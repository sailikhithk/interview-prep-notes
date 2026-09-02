# Git at Scale: Cursor Origin & Continuity

**Type:** SYSTEM DESIGN · **Domain:** Distributed Storage, VCS, Monorepos & AI Agent Workloads  
**Scale:** 300+ pushes/sec (S3 Express), 100+ read replicas linear scaling, millions of ephemeral repositories  
**Key Paradigms:** S3 Write-Ahead Log (WAL), Stateless NVMe Warm Caches, Rendezvous Hashing, Single-Leader Compaction

---

## 1. Problem Statement

Modern software development has fundamentally outgrown traditional Git hosting architectures:
1. **Massive Monorepos:** Heavy write contention, hundreds of CI runners cloning/fetching simultaneously.
2. **AI Coding Agents:** High-frequency, machine-speed automated pushes and millions of ephemeral throwaway repositories.
3. **Strict Consistency Requirements:** Git clients break under eventual consistency (e.g. push a commit then fail immediate fetch).

### Why Naive Approaches Fail
- **Git over Distributed Key-Value Store:** Every Git operation requires traversing the commit/tree DAG. Querying each object over the network causes $O(\text{DAG Depth})$ sequential round trips (100ms+ per operation).
- **Git over Distributed Filesystem (NFS/GFS/DRBD):** Git packfiles use sliding-window delta compression. Objects are scattered randomly across binary packfiles on disk. Seeking through packfiles over a networked filesystem causes severe random seek I/O and page fault thrashing.

---

## 2. Generational Evolution

```
Generation 1 (2008-2012): Dedicated RPC Fileservers
- Monolith talks via RPC to single fileservers.
- Bottleneck: 1 server per repo. Single Point of Failure (SPOF).

Generation 2 (2013-2025): GitHub Spokes (3-Phase Commit)
- Repositories stored on local NVMe disks across 3+ replicas.
- Packfiles fanned out; reference updates synchronized via 3PC.
- Bottleneck: Write latency bound by slowest replica (tail at scale).
- High operational complexity: Repos are "Pets" (stateful routing DB, corruption repairs, CPU compaction storms).

Generation 3 (2026+): Cursor Continuity & Origin (S3 WAL + Cattle)
- Source of truth moved to S3-compatible Object Storage (WAL).
- NVMe workers are stateless "Cattle" (warm caches).
- Zero-DB routing via Rendezvous Hashing (HRW).
- Linearizable pushes via S3 Atomic Compare-And-Swap (CAS).
- Sub-10ms strongly consistent reads via S3 Conditional GET (HTTP 304).
- Single-leader compaction: Primary repacks; replicas stream pre-compacted packs.
```

---

## 3. High-Level Architecture (HLD)

```
                    ┌─────────────────────────┐
                    │ Git CLI / AI Agents /   │
                    │ Web UI / CI Runners     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     API / Git Gateway   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Rendezvous Hash Router │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┴───────────────────┐
             │ (Rank #1: Primary)                    │ (Rank #2..K: Replicas)
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
             │ Upload Pack + Atomic CAS Index        │ Conditional GET (If-None-Match)
             ▼                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│             S3-Compatible Object Store (Source of Truth)         │
│  - repos/{repo_id}/wal/index.json (Single CAS Pointer)           │
│  - repos/{repo_id}/packs/{sha256}.pack (Immutable Blobs)         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Request Lifecycles

### 4.1 Push Flow (Write Path)
1. **Ingress:** Router routes push to the #1 ranked primary node using **Rendezvous Hashing**.
2. **Concurrent Ingestion:** Primary writes incoming packfile to local NVMe and uploads to S3 as an immutable blob (`repos/{id}/packs/{hash}.pack`).
3. **Local Lock:** Primary acquires an in-memory lock on the reference and verifies fast-forward invariants.
4. **S3 Atomic CAS:** Primary prepares an updated `WAL Index` JSON (incremented `epoch` and `sequence_number`) and executes an atomic S3 PUT with `If-Match: <current_etag>`.
5. **ACK:** Once S3 confirms CAS, local NVMe reference is updated and push success is returned to client.
6. **UDP Gossip:** Primary broadcasts UDP datagram `{repo_id, epoch, new_etag}` to replicas.

### 4.2 Fetch / Clone Flow (Read Path)
1. Request routed to any healthy replica.
2. Replica validates cache with S3 via conditional GET: `If-None-Match: <cached_etag>`.
3. S3 returns **HTTP 304 Not Modified** in <10ms.
4. Replica immediately streams objects from local NVMe cache.

### 4.3 Compaction Flow
- Only primary runs `git repack`.
- Uploads merged packfile to S3 and updates WAL index via CAS.
- Replicas download the pre-compacted packfile from S3 without burning CPU.

---

## 5. Low-Level Design & Data Structures (LLD / DSA)

### 5.1 Rendezvous Hashing (Highest Random Weight / HRW)
```python
import hashlib

def get_node(repo_id: str, active_nodes: list[str]) -> str:
    """
    Rendezvous Hashing: Computes node with highest weight.
    Deterministic, O(N) time, zero routing table database required.
    """
    def weight(node: str) -> int:
        return int(hashlib.sha256(f"{repo_id}:{node}".encode()).hexdigest(), 16)
    return max(active_nodes, key=weight)
```

### 5.2 Directed Acyclic Graph (DAG) & Lowest Common Ancestor (LCA)
- Commit history forms a DAG. Three-way merge requires finding the **Merge Base** (Lowest Common Ancestor).
- Calculated via Multi-Source Breadth-First Search (BFS) and topological generation numbers.

### 5.3 Sliding-Window Delta Compression (xdelta)
- Base objects are chunked into 16-byte blocks and indexed with a **Rabin-Karp rolling hash**.
- Target objects are scanned with a sliding window, generating `COPY(offset, len)` and `INSERT(bytes)` instructions.

### 5.4 Multi-Pack Index (MIDX) & Roaring Bitmaps
- Unifies multiple `.pack` indexes into a single $O(\log N)$ lookup table.
- Reachability queries (`git rev-list main ^origin/main`) executed via compressed bitwise boolean operations:
  $$\text{Reachable} = \text{Bitmap}(\text{main}) \ \mathbf{AND\ NOT}\ \text{Bitmap}(\text{origin/main})$$

---

## 6. Interview FAQ & Trade-Offs

| Question | Core Takeaway |
|---|---|
| **Why not Raft/Paxos?** | Delegating durable consensus to S3 atomic CAS makes storage workers 100% stateless cattle, removing complex leader elections. |
| **How to scale S3 PUTs?** | Batching multiple pushes arriving within a 5ms window into a single S3 WAL write; using S3 Express One Zone for sub-millisecond PUTs. |
| **Why UDP Gossip + S3 304?** | UDP is optimistic; S3 conditional GET `If-None-Match` guarantees linearizable reads with <10ms metadata check even if UDP packets drop. |
| **How is split-brain avoided?** | S3 atomic CAS ensures exactly one worker succeeds on concurrent writes; the loser receives HTTP 412 and retries. |
