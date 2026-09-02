# 29. Git at Scale: Architecture of Cursor Origin & Continuity

**Type:** SYSTEM DESIGN & DISTRIBUTED STORAGE · **Domain:** Distributed Version Control Systems (VCS), Monorepos & AI Agent Workloads  
**Core Innovation:** Decoupled Compute/Storage with Object Store (S3) Write-Ahead Log (WAL), Stateless Warm-Cache NVMe Replicas, Rendezvous Hashing Routing, and Single-Leader Compaction  
**Scale Target:** 300+ pushes/sec (S3 Express One Zone), 100+ read replicas linear scaling, millions of ephemeral AI-agent repositories with zero idle storage overhead.

---

## 1. Executive Summary & Problem Framing

Hosting Git repositories at global enterprise scale has historically been one of the most notoriously difficult problems in distributed systems engineering. As Linus Torvalds famously stated in the initial commit, Git is *"the information manager from hell"*. Git was architected for the decentralized Linux kernel development model where every peer maintains an identical, authoritative local copy of the repository.

However, modern software engineering is strictly **centralized** (GitHub, GitLab, Cursor Origin). When centralization meets **massive enterprise monorepos** (tens of GBs, hundreds of CI runners fetching per minute) and **autonomous AI coding agents** (generating millions of ephemeral repositories, branches, and machine-speed commits), conventional Git hosting architectures fail catastrophically.

This study guide deconstructs the evolution of distributed Git architectures—from naive distributed filesystems, to GitHub's industry-standard **Spokes (3-Phase Commit)**, to Cursor's state-of-the-art **Origin & Continuity (S3 Write-Ahead Log + Disposable NVMe Cattle)**. We analyze the complete engineering spectrum from **High-Level Design (HLD)** to **Low-Level Design (LLD)** and the exact **Data Structures & Algorithms (DSA)** tested in top-tier Senior/Staff infrastructure interviews.

---

## 2. The Fundamental Hardness of Scaling Git

To ace a System Design interview on Git or version control systems, you must understand why standard distributed database patterns cannot be blindly applied to Git.

### Why Not a Distributed Key-Value Store? (Git Without Packfiles)
Git is inherently a **content-addressable store**: every object (blob, tree, commit, tag) is keyed by its SHA-1 / SHA-256 hash. Intuitively, one might propose sharding objects across Cassandra, DynamoDB, or FoundationDB where `Key = Object_SHA` and `Value = Object_Bytes`.

**Why this fails:**
1. **DAG Traversal Network Amplification:** A Git repository is a Directed Acyclic Graph (DAG). To inspect a tree, diff two commits, or clone a repository, Git cannot execute a bulk SQL `JOIN`. It must traverse the graph node-by-node (Commit $\to$ Root Tree $\to$ Sub-trees $\to$ Blobs).
2. If every node is an RPC lookup to a remote KV store, traversing a repository with depth $D=50$ and thousands of trees requires hundreds of sequential round trips:
$$\text{Latency} \approx \sum_{i=1}^{D} \text{RTT}_i \approx 50 \times 2\text{ms} = 100\text{ms}$$
This turns even a simple `git log` or `git status` into an unacceptably slow operation.

### Why Not a Distributed Networked Filesystem? (NFS, GFS, DRBD)
Early GitHub attempted to run Git on NFS, GFS, and DRBD block-level replication.

**Why this fails:**
1. **Packfile Mechanics:** Git compresses objects into `.pack` files using **sliding-window delta compression** (`xdelta`). Objects are stored not as whole files, but as delta chains referencing base objects located arbitrarily across multi-gigabyte packfiles.
2. **Random I/O Explosion:** Resolving an object requires jumping to arbitrary byte offsets across several packfiles to reconstruct the delta chain. Over a networked filesystem (NFS/block storage), this triggers random page faults and cache thrashing across thousands of concurrent repositories.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Why Naive Approaches Fail                                              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Distributed KV Store: $O(\text{DAG Depth})$ network round-trip hops.│
│ 2. Distributed Filesystem (NFS): Random delta-chain seek I/O latency.  │
│ 3. Plain Git on Single Server: Single Point of Failure (SPOF), No Scale│
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Generational Evolution of Git Storage Architecture

```
+-------------------------------------------------------------------------------+
| GENERATION 1 (2008-2012): Dedicated RPC Fileservers                           |
| - Monolithic app talks via RPC to dedicated storage nodes.                   |
| - Bottleneck: 1 node per repo. Single Point of Failure. No read scaling.     |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| GENERATION 2 (2013-2025): GitHub Spokes (3-Phase Commit Consensus)            |
| - Repositories stored on local NVMe disks on 3+ replicas.                     |
| - Packfiles fanned out; Reference Transactions synchronized via 3PC.          |
| - Bottleneck: 3PC write throughput bound by slowest replica (tail at scale).  |
| - Operational pain: Repositories are "Pets" (stateful routing DB, corruption) |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
| GENERATION 3 (2026+): Cursor Continuity & Origin (S3 WAL + Disposable Cattle) |
| - Source of truth moved to S3-compatible Write-Ahead Log (WAL).               |
| - NVMe storage nodes are stateless "Cattle" (Warm Caches).                    |
| - Rendezvous Hashing routes requests without centralized routing databases.   |
| - Linearizable pushes via S3 Atomic Compare-And-Swap (CAS).                   |
| - Replication via UDP Gossip + Sub-10ms Conditional S3 GETs (HTTP 304).       |
| - Single-Leader Compaction: Only primary repacks; replicas download packs.   |
+-------------------------------------------------------------------------------+
```

---

## 4. GitHub Spokes vs. Cursor Continuity: Architectural Deep Dive

### GitHub Spokes (3PC Consensus over Local Storage)

Spokes uses an application-level consensus protocol to replicate Git repositories across $N$ storage nodes (typically $N=3$):

```
Developer Push
     │
     ▼
[Spokes Proxy Router] ── (Routes via Central Routing DB)
     │
     ├── 1. Fan-out Packfile ───────────► [Node 1 (NVMe)] [Node 2 (NVMe)] [Node 3 (NVMe)]
     │
     └── 2. Three-Phase Commit (3PC) ───► 1. Voting (Can-Commit?)
                                           2. Pre-Commit (Lock ref & ACK)
                                           3. Do-Commit (Update ref to commit OID)
```

#### Why Spokes Broke Under Modern Monorepo & AI Workloads:
1. **The 3PC Latency Bottleneck (Tail at Scale):** In 3PC, every push requires 3 round trips across all $N$ replicas. The write latency is determined by the slowest replica:
$$T_{\text{push}} = \max(T_{\text{node}_1}, T_{\text{node}_2}, \dots, T_{\text{node}_N})$$
Adding more replicas to scale CI read traffic severely degrades push throughput.
2. **"Pets, Not Cattle":** Disk copies are the authoritative source of truth. If 2 of 3 replicas suffer file corruption or disk failure, quorum is lost and the repo goes read-only.
3. **Fragile State Management:** Requires a massive relational database to store routing tables mapping every repo to specific host servers, plus continuous background checksum repair daemons.
4. **Compaction Storms:** Every replica must independently execute CPU-intensive Git packfile repacking (`git gc` / `git repack`). If multiple replicas repack simultaneously, CPU saturation triggers cascading failovers.

---

### Cursor Continuity: The WAL-over-Object-Storage Paradigm

Continuity shifts the single source of truth entirely to an **S3-compatible Object Store**, treating all local NVMe repositories as disposable warm caches.

```
                              ┌──────────────────────────────────────┐
                              │     S3 Object Storage (WAL Truth)    │
                              │ ┌───────────────┐  ┌───────────────┐ │
                              │ │  WAL Index    │  │  Packfiles    │ │
                              │ │ (CAS Pointer) │  │  (Immutable)  │ │
                              │ └───────▲───────┘  └───────▲───────┘ │
                              └─────────┼──────────────────┼─────────┘
                                        │ Atomic CAS PUT   │ Simultaneous PUT
                                        │ (If-Match ETag)  │
                                        │                  │
   Git Client ──Push──► [Ingress Router] ───► [Primary Worker (NVMe)]
                             │                      │
                  Rendezvous │                      │ UDP Gossip Broadcast
                     Hashing │                      ▼
                             ▼             [Replica Worker (NVMe)]
                   [Replica Worker (NVMe)]          │
                             │                      │ Conditional GET (If-None-Match)
                             └──────────────────────┴────────► Returns HTTP 304 / New Manifest
```

---

## 5. High-Level Design (HLD)

### 5.1 System Architecture

```
                    ┌─────────────────────────┐
                    │ Git CLI / AI Agents /   │
                    │ Web UI / CI Runners     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     API / Git Gateway   │
                    │   (Auth, TLS, Rate Lim) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Rendezvous Hash Router │
                    │   HRW(RepoID, Nodes)    │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┴───────────────────┐
             │ (Rank 1: Primary)                     │ (Rank 2..K: Replicas)
             ▼                                       ▼
┌──────────────────────────┐            ┌──────────────────────────┐
│  Primary Storage Worker  │            │  Replica Storage Worker  │
│  ┌────────────────────┐  │            │  ┌────────────────────┐  │
│  │ Local NVMe Cache   │  │   Gossip   │  │ Local NVMe Cache   │  │
│  │ (Standard Git Repo)│  │───(UDP)───►│  │ (Standard Git Repo)│  │
│  └────────────────────┘  │            │  └────────────────────┘  │
│  │ Compaction Engine  │  │            │  │ Fast Ingester      │  │
│  └────────────────────┘  │            │  └────────────────────┘  │
└────────────┬─────────────┘            └────────────┬─────────────┘
             │                                       │
             │ Upload Packfile + Atomic CAS Index    │ Conditional Fetch (ETag)
             ▼                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│             S3-Compatible Object Store (Source of Truth)         │
│  - repos/{repo_id}/wal/index.json (Single CAS Pointer)           │
│  - repos/{repo_id}/packs/{sha256}.pack (Immutable Blobs)         │
│  - repos/{repo_id}/packs/{sha256}.idx (Packfile Index)           │
└──────────────────────────────────────────────────────────────────┘
```

---

### 5.2 Core Workflows

#### 1. Push Workflow (Write Path - Linearizable)
1. **Client Ingress:** Client initiates `git push origin main`.
2. **Routing:** Router hashes `RepoID` against active nodes using **Rendezvous Hashing** and routes to the ranked #1 node (Primary).
3. **Parallel Ingestion:**
   - Worker streams incoming packfile to local NVMe disk.
   - Concurrently uploads the packfile as an immutable object to S3: `repos/{id}/packs/{pack_hash}.pack`.
4. **Local Ref Transaction:** Worker acquires an in-memory lock on the target reference (`refs/heads/main`), verifies the old commit OID (fast-forward check), and prepares the transaction locally using `libgit2`.
5. **Atomic S3 CAS:** Worker prepares a new `WAL Index` JSON containing the incremented `epoch`, `sequence_number`, new `ref_map`, and appended packfile reference. Worker performs an atomic S3 PUT with `If-Match: <current_index_etag>`.
6. **Commit Local & ACK:** Once S3 confirms the CAS write:
   - Local Git reference is committed to NVMe disk.
   - Lock is released.
   - HTTP/SSH 200 OK is returned to the Git client.
7. **Async Gossip:** Primary broadcasts a lightweight UDP datagram to the cluster with `{repo_id, new_epoch, new_etag}`.

#### 2. Fetch / Clone Workflow (Read Path - Strongly Consistent)
1. **Routing:** Read request arrives for `RepoID`. Router forwards to any healthy replica for that repository.
2. **Sub-10ms Linearizability Check:**
   - Replica performs an S3 Conditional GET on `repos/{id}/wal/index.json` with header `If-None-Match: <local_cached_etag>`.
   - **Case A (Up to date):** S3 returns **HTTP 304 Not Modified** (metadata-only, ~5-10ms). Replica immediately serves the clone/fetch from local NVMe using standard `git-upload-pack`.
   - **Case B (Stale / Cache Miss):** S3 returns **HTTP 200 OK** with the latest `WAL Index`. Replica downloads the missing packfiles from S3, updates local refs, and then serves the read.

#### 3. Materialization / Cold-Start Workflow (Cattle Recovery)
- If a server crashes or a new node joins the cluster, it has **zero local state**.
- On first request for `RepoID`:
  1. Node fetches `wal/index.json` from S3.
  2. Downloads referenced packfiles and indexes from S3 in parallel.
  3. Initializes a standard bare Git repository on NVMe (`git init --bare`).
  4. Writes refs from the WAL index into `.git/packed-refs`.
  5. The node is now fully warm and ready to serve reads or writes in seconds.

#### 4. Compaction Workflow (Single-Leader)
- Git creates a new `.pack` file on every push. Having 1,000 packfiles causes linear search degradation across `.idx` files.
- In Continuity, **only the primary worker** runs background compaction (`git repack -ad` / geometric repacking).
- The resulting merged packfile is uploaded to S3.
- Primary updates the `WAL Index` via S3 CAS to replace the individual pack references with the single compacted pack reference.
- **Replicas do not execute `git repack`!** They simply receive the WAL update, download the already-compacted packfile from S3, and delete obsolete packfiles from local NVMe. **CPU cost is amortized across the entire cluster.**

---

## 6. Low-Level Design (LLD)

### 6.1 Data Model & Schemas

#### S3 WAL Index Schema (`repos/{repo_id}/wal/index.json`)
```json
{
  "version": 1,
  "repo_id": "org-42/monorepo",
  "epoch": 1042,
  "sequence_number": 88419,
  "timestamp_ns": 1724000000000000000,
  "head_commit": "c8f3a9e4b71234567890abcdef1234567890abcd",
  "refs": {
    "refs/heads/main": "c8f3a9e4b71234567890abcdef1234567890abcd",
    "refs/heads/feature-ai": "87ab3211c4000000000000000000000000000000",
    "refs/tags/v1.0.0": "4b70123456789000000000000000000000000000"
  },
  "packfiles": [
    {
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 104857600,
      "object_count": 45000,
      "is_compacted": true
    },
    {
      "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
      "size_bytes": 40960,
      "object_count": 12,
      "is_compacted": false
    }
  ]
}
```

---

### 6.2 Object-Oriented Component Design (Python / Type System)

```python
import hashlib
import json
import time
from typing import List, Dict, Optional, Tuple

class RendezvousHashRouter:
    """
    Implements Highest Random Weight (HRW) / Rendezvous Hashing.
    Maps repo_id to a deterministic ranked list of storage nodes.
    Time Complexity: O(N) where N is number of active nodes.
    Space Complexity: O(1).
    """
    def __init__(self, nodes: List[str]):
        self.nodes = sorted(nodes)

    def _hash_weight(self, repo_id: str, node_id: str) -> int:
        # MurmurHash3 or SHA256(repo_id + node_id)
        key = f"{repo_id}:{node_id}".encode('utf-8')
        return int(hashlib.sha256(key).hexdigest(), 16)

    def get_ranked_nodes(self, repo_id: str) -> List[str]:
        # Returns nodes sorted by highest weight descending
        ranked = sorted(
            self.nodes,
            key=lambda node: self._hash_weight(repo_id, node),
            reverse=True
        )
        return ranked

    def get_primary(self, repo_id: str) -> str:
        return self.get_ranked_nodes(repo_id)[0]


class WALIndex:
    def __init__(self, repo_id: str, epoch: int, seq: int, refs: Dict[str, str], packfiles: List[Dict]):
        self.repo_id = repo_id
        self.epoch = epoch
        self.seq = seq
        self.refs = refs
        self.packfiles = packfiles

    def to_json(self) -> str:
        return json.dumps({
            "repo_id": self.repo_id,
            "epoch": self.epoch,
            "sequence_number": self.seq,
            "refs": self.refs,
            "packfiles": self.packfiles
        }, sort_keys=True)


class S3StorageClient:
    """Mock interface representing S3 with conditional CAS semantics."""
    def get_object(self, key: str, if_none_match: Optional[str] = None) -> Tuple[int, Optional[str], Optional[str]]:
        """Returns (status_code, body, etag). HTTP 304 if etag matches."""
        pass

    def put_object_cas(self, key: str, data: str, expected_etag: str) -> Tuple[bool, str]:
        """
        Atomic Compare-And-Swap.
        Succeeds only if S3 object's current ETag matches expected_etag.
        Returns (success_boolean, new_etag).
        """
        pass

    def put_blob(self, key: str, payload_bytes: bytes) -> str:
        """Uploads immutable packfile blob, returns SHA256/ETag."""
        pass


class ContinuityWorker:
    """
    Storage Worker handling local NVMe Git operations & WAL synchronization.
    """
    def __init__(self, node_id: str, s3: S3StorageClient):
        self.node_id = node_id
        self.s3 = s3
        self.local_cache: Dict[str, WALIndex] = {}
        self.local_etags: Dict[str, str] = {}

    def push(self, repo_id: str, ref_name: str, old_oid: str, new_oid: str, packfile_bytes: bytes) -> bool:
        """
        Executes Linearizable Push Protocol.
        """
        # 1. Upload immutable packfile to S3
        pack_sha = hashlib.sha256(packfile_bytes).hexdigest()
        self.s3.put_blob(f"repos/{repo_id}/packs/{pack_sha}.pack", packfile_bytes)

        max_retries = 3
        for attempt in range(max_retries):
            # 2. Fetch current WAL Index & ETag
            wal_key = f"repos/{repo_id}/wal/index.json"
            status, wal_data, current_etag = self.s3.get_object(wal_key)
            
            if status == 200 and wal_data:
                current_wal = json.loads(wal_data)
                epoch = current_wal["epoch"]
                seq = current_wal["sequence_number"] + 1
                refs = current_wal["refs"].copy()
                packs = current_wal["packfiles"].copy()
            else:
                epoch = 1
                seq = 1
                refs = {}
                packs = []
                current_etag = ""

            # 3. Verify reference fast-forward / consistency
            if refs.get(ref_name) != old_oid and old_oid != "0000000000000000000000000000000000000000":
                raise ValueError(f"Non-fast-forward push rejected on {ref_name}")

            # 4. Prepare updated WAL index
            refs[ref_name] = new_oid
            packs.append({"sha256": pack_sha, "size_bytes": len(packfile_bytes), "is_compacted": False})
            new_wal = WALIndex(repo_id, epoch, seq, refs, packs)

            # 5. Atomic S3 CAS write
            success, new_etag = self.s3.put_object_cas(wal_key, new_wal.to_json(), expected_etag=current_etag)
            if success:
                # 6. Apply to local NVMe and update cache
                self.local_cache[repo_id] = new_wal
                self.local_etags[repo_id] = new_etag
                self._broadcast_udp_gossip(repo_id, epoch, new_etag)
                return True
            
            # Exponential backoff + jitter on CAS collision
            time.sleep(0.05 * (2 ** attempt))

        return False

    def sync_for_read(self, repo_id: str) -> WALIndex:
        """
        Executes sub-10ms conditional sync for linearizable reads.
        """
        wal_key = f"repos/{repo_id}/wal/index.json"
        cached_etag = self.local_etags.get(repo_id, "")
        
        status, wal_data, new_etag = self.s3.get_object(wal_key, if_none_match=cached_etag)
        if status == 304:
            # Fully up to date! Serve immediately from NVMe
            return self.local_cache[repo_id]
        
        # 200 OK: Cache is stale; update local NVMe state
        latest_wal = json.loads(wal_data)
        self.local_cache[repo_id] = WALIndex(
            latest_wal["repo_id"], latest_wal["epoch"], latest_wal["sequence_number"],
            latest_wal["refs"], latest_wal["packfiles"]
        )
        self.local_etags[repo_id] = new_etag
        self._hydrate_missing_packs(repo_id, latest_wal["packfiles"])
        return self.local_cache[repo_id]

    def _hydrate_missing_packs(self, repo_id: str, packfiles: List[Dict]):
        # Download missing packfiles from S3 in parallel to local NVMe
        pass

    def _broadcast_udp_gossip(self, repo_id: str, epoch: int, etag: str):
        # Fire-and-forget UDP packet to peer cluster nodes
        pass
```

---

## 7. Data Structures & Algorithms (DSA) Involved

Infrastructure interviews frequently drill down into the algorithmic foundations underpinning distributed version control systems.

### 7.1 Directed Acyclic Graphs (DAG) & Lowest Common Ancestor (LCA)
- **Git Commit Graph as a DAG:** Commits are vertices $V$, parent pointers are directed edges $E$.
- **Merge Base Calculation:** To perform a `git merge` or three-way diff between branch $A$ and branch $B$, Git must find the **Lowest Common Ancestor (LCA)** in the DAG.
- **Algorithm:** Multi-source Breadth-First Search (BFS) or Tarjan's Off-line LCA algorithm using commit topological generation numbers (`commit-graph` binary format) to bound graph traversal depth in $O(|V| + |E|)$.

```
      A (Commit 1)
     / \
    B   C
    │   │
    D   E
     \ /
      F (Merge Base / LCA of D and E)
```

---

### 7.2 Rendezvous Hashing (Highest Random Weight / HRW)
Unlike the standard Chord / Ketama Consistent Hashing Ring which uses $O(\log N)$ binary search on virtual tokens:
- **HRW Formula:** For a given object key $K$ and set of $N$ nodes $\{S_1, S_2, \dots, S_N\}$:
$$\text{Node}^*(K) = \arg\max_{i=1}^N h(K \parallel S_i)$$
- **Properties:**
  1. **Zero Central Routing State:** Any proxy or client with the list of healthy nodes computes identical ranking locally in $O(N)$ hash operations.
  2. **Ranked Fallback List:** If the primary node $S_1$ fails, the cluster instantly fails over to $S_2$ without rebalancing or consensus renegotiation.
  3. **Minimal Disruption:** When a node joins or leaves, exactly $\frac{1}{N}$ keys are remapped with optimal load uniformity.

---

### 7.3 Byte-Level Sliding-Window Delta Compression (xdelta)
- **Packfile Generation:** Packfiles compress similar files (e.g. revisions of `app.py`) by emitting copy/insert instructions.
- **Algorithm:**
  1. Base object is indexed using a **Rabin-Karp rolling hash** on fixed chunk boundaries (e.g., 16-byte blocks) stored in a hash lookup table.
  2. Target object is scanned with a sliding window. Matches in the hash table trigger maximal substring expansion (copy instruction `COPY(offset, length)`).
  3. Non-matching bytes are emitted as `INSERT(bytes)`.
- **Delta Chains:** Git limits delta chain depth (default $D=50$) and prevents directed cycles using cycle detection algorithms (DFS with coloring).

---

### 7.4 Multi-Pack Index (MIDX) & Roaring Bitmaps
- When a repository accumulates hundreds of `.pack` files, searching for an object SHA requires scanning each `.idx` fan-out table in $O(P \log K)$ time (where $P$ is packfile count).
- **Multi-Pack Index (MIDX):** Unifies all packfiles into a single binary search table mapping `SHA-256` $\to$ `(packfile_id, byte_offset)` in $O(\log (\sum K))$.
- **Roaring Bitmaps:** Used for reachability bitmap indexes (`.bitmap`). A commit's entire reachable tree/blob set is represented as compressed bitmaps. Answering `git rev-list --count main ^origin/main` is reduced to hardware-accelerated bitwise operations:
$$\text{Reachable Objects} = \text{Bitmap}(\text{main}) \ \mathbf{AND\ NOT}\ \text{Bitmap}(\text{origin/main})$$

---

## 8. Interview Preparation: Q&A, Trade-offs & Deep Questions

### Q1: Why does Continuity use S3 Atomic CAS instead of Raft or Paxos?
**Answer:**
Raft/Paxos requires maintaining a long-running quorum of stateful server processes with heartbeat leases, leader elections, and log compaction state machines. If a minority of Raft nodes lag or experience network partitions, write availability halts.
By using S3's managed object store as the WAL with conditional PUTs (`If-Match` / `If-None-Match`), the storage layer delegates physical consensus to AWS/GCP (who already solve petabyte-scale Paxos/Quorum replication across Availability Zones). The application nodes become **100% stateless**. Any worker can process writes or reads, eliminating complex leader election logic.

---

### Q2: How does Continuity avoid the S3 PUT latency bottleneck on high-throughput pushes?
**Answer:**
A single S3 Standard PUT takes 20-50ms, which would theoretically cap a single repository at ~20-50 pushes/second if done naively. Continuity solves this via three optimizations:
1. **Push Batching & Pipelining:** The primary worker pipelines incoming pushes. Multiple client reference updates arriving within a 5ms window are coalesced into a single atomic S3 WAL index update.
2. **S3 Express One Zone:** Sub-millisecond PUT latencies allow single-repo throughput to scale to **300+ pushes/second**.
3. **Decoupled Packfile Uploads:** Packfile blobs are uploaded concurrently and asynchronously with local NVMe caching; only the tiny WAL metadata pointer requires serialized CAS.

---

### Q3: Why is UDP Gossip combined with HTTP 304 Conditional GETs instead of pure TCP streaming?
**Answer:**
In a distributed system, network links and node topologies are inherently unreliable. If a primary relied on synchronous TCP pushes to notify 100 replicas, a single slow replica or broken TCP socket would cause head-of-line blocking or dropped notifications.
Continuity treats UDP gossip as an **optimistic accelerator** (best-effort fast notification). The hard consistency guarantee is enforced by the replica doing a **conditional S3 GET with `If-None-Match: <cached_etag>`**. Because S3 answers this metadata check in <10ms with HTTP 304 (0 body bytes), reads are guaranteed to be linearizable even if UDP datagrams are completely dropped.

---

### Q4: How does this architecture handle a Network Partition (Split-Brain)?
**Answer:**
Because the source of truth is the S3 WAL, a network partition between storage workers **cannot cause split-brain data divergence**.
- If two workers both believe they are primary and attempt to commit concurrent pushes, both will execute `put_object_cas("wal/index.json", ..., expected_etag=E_prev)`.
- S3's atomic consistency guarantees that **exactly one** CAS will succeed and transition the ETag to `E_new`.
- The losing worker receives HTTP 412 Precondition Failed, fetches the updated WAL index, checks for fast-forward conflicts, and re-executes the transaction or notifies the client to `git pull --rebase`.

---

## 9. Summary Comparison Matrix for System Design Interviews

| Architectural Dimension | Naive Git (Single Host) | GitHub Spokes (Gen 2) | Cursor Continuity / Origin (Gen 3) |
|---|---|---|---|
| **Source of Truth** | Local Disk (SPOF) | Quorum of NVMe Replicas | S3-Compatible Object Store (WAL) |
| **Consensus Mechanism** | None (OS File Locks) | 3-Phase Commit (3PC) | Optimistic CAS on S3 Objects |
| **Node State Category** | Single Pet | Stateful Pets (Needs Routing DB) | Stateless Cattle (Warm Cache) |
| **Routing Discovery** | Static IP / DNS | Centralized Relational DB | Rendezvous Hashing (HRW, Zero DB) |
| **Horizontal Read Scaling** | None ($1\times$) | Constrained by 3PC write tail | Linear ($100\times$+ Replicas via S3 304) |
| **Push Throughput Cap** | Bound by local NVMe | Bound by slowest 3PC replica | Up to 300+ pushes/s (S3 Express) |
| **Compaction Strategy** | Manual / Local `git gc` | Every replica repacks (CPU spikes) | Single-Leader: Primary repacks $\to$ S3 |
| **Ephemeral Repo Cost** | Fixed disk allocation | 3 idle replicas min (High waste) | \$0 idle cost (Pure object metadata) |

---
*Created as part of the Advanced System Design & VCS Infrastructure Interview Preparation Series.*
