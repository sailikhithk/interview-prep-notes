# System Design Mastery Curriculum: 27-Topic Deep-Dive & Failure Mode Matrix

> A senior/staff-level guide turning 27 core system design topics into concrete architectural trade-offs, edge-case failure modes, and real-world implementation patterns.

---

## The 4-Pillar Architectural Framework

Rather than memorizing isolated components, every system design problem maps into 4 interdependent pillars:

```
                  SYSTEM DESIGN MASTERY (4 PILLARS)
 ┌───────────────────────────┬───────────────────────────┐
 │   1. DATA & CONSISTENCY   │     2. ACCESS & TRAFFIC   │
 │ • Storage Engines (B-Tree │ • API Gateway & mTLS      │
 │   vs. LSM-Tree)           │ • Distributed Rate Limit  │
 │ • Sharding & Consistent   │ • Load Balancing (L4/L7)  │
 │   Hashing                 │ • Cache Invalidation &    │
 │ • Outbox Pattern & CDC    │   Thundering Herd         │
 │ • Distributed Locks &     │ • Pagination & Cursor     │
 │   Fencing Tokens          │   Strategies              │
 ├───────────────────────────┼───────────────────────────┤
 │   3. EVENT & ASYNC FLOW   │     4. RESILIENCE & SCALE │
 │ • Kafka Partitioning &    │ • Circuit Breakers &      │
 │   Consumer Lag            │   Jittered Backoff        │
 │ • Idempotency Keys        │ • Split-Brain & Consensus │
 │ • Dead Letter Queues      │ • Observability & SLOs    │
 │ • Backpressure Handling   │ • Cascading Failure       │
 │ • Sagas & Compensation    │   Isolation / Bulkheads   │
 └───────────────────────────┴───────────────────────────┘
```

---

## Complete 27-Topic Mastery Matrix & Trade-Off Blueprint

| # | Topic Area | Core Mechanism & Architecture | Key Trade-Offs & Gotchas | Failure Mode & Edge Case to Defend |
|---|---|---|---|---|
| **1** | **Requirements & Scale Math** | DAU, Peak QPS ($QPS_{peak} = \frac{DAU \times R}{86400} \times \text{Multiplier}$), Storage ($QPS \times \text{size} \times 5\text{ yrs}$), Read:Write ratio. | Accuracy vs. speed: Don't get stuck on exact arithmetic; orders of magnitude matter for storage tiering and memory sizing. | **Under-provisioning cache memory:** Calculating average QPS instead of 99.9th percentile peak traffic during flash events. |
| **2** | **APIs & Contracts** | REST (HTTP/1.1 or 2), GraphQL (flexible field selection), gRPC (HTTP/2 binary protobuf multiplexing). | Network overhead vs. payload flexibility. gRPC gives ~5-10x throughput over REST but lacks native browser-friendly tooling without Envoy gRPC-Web. | **Pagination drift / duplicate reads:** Offset-based pagination (`OFFSET 10000 LIMIT 20`) causes severe DB table scans and skips items when rows insert concurrently. **Fix:** Keyset/cursor pagination (`WHERE id > last_seen_id LIMIT 20`). |
| **3** | **Load Balancing** | L4 (TCP/UDP, IP+Port hashing via Maglev/IPVS) vs. L7 (HTTP headers, path routing, TLS termination). | Throughput vs. application intelligence: L4 handles millions of packets with low CPU; L7 allows header inspection and sticky sessions at higher CPU/memory cost. | **Sticky session node death:** If a server with 10k sticky WebSocket connections dies, a blind failover thundering-herd crushes the backup node. **Fix:** Consistent hash routing + distributed session backplane. |
| **4** | **Caching Layers** | Cache-Aside, Write-Through, Write-Behind, Refresh-Ahead, Redis Cluster, Multi-tier CDN. | Latency vs. consistency: Caches hide DB bottlenecks but introduce stale reads and invalidation complexity. | **Cache Stampede / Thundering Herd:** Cache key expires on a hot key with 50k QPS; all 50k requests hit Postgres simultaneously. **Fix:** Mutex lock on cache miss (Singleflight), probabilistic early expiration (XFetch), or background refresh. |
| **5** | **Databases & Storage Internals** | B-Trees (in-place updates, page random I/O) vs. LSM-Trees (WAL + MemTable + SSTable compaction, sequential append I/O). | Read latency vs. write throughput: B-Tree (Postgres/MySQL) minimizes read amplification; LSM-Tree (RocksDB/Cassandra) gives massive write throughput at the cost of background compaction I/O. | **N+1 queries & index bloat:** Over-indexing degrades write performance; missing composite indexes forces sequential table scans. |
| **6** | **Data Partitioning & Sharding** | Range-based vs. Hash-based vs. Directory-based sharding. | Range queries vs. uniform key distribution. Range allows easy scans (`WHERE date BETWEEN...`) but creates write hotspots on latest date. | **Celebrity / Hotspot Partition:** Elon Musk writes a tweet; writing to user shard 42 causes partition saturation. **Fix:** Compound keys (`user_id + post_id`), salt partition keys, or read cache replication. |
| **7** | **Replication & Consensus** | Single-leader, Multi-leader, Leaderless (Dynamo-style quorum: $R + W > N$). | Replication lag vs. write latency: Synchronous replication guarantees zero data loss (RPO=0) but blocks writes on slow replicas; async allows read-after-write anomalies. | **Replication Lag Inconsistency:** User posts a comment, page reloads, user reads from replica with 300ms lag and doesn't see their own comment. **Fix:** Read-your-own-writes (route reads to leader for 5s after write). |
| **8** | **Consistency Models** | Strict Serializability > Linearizability > Sequential > Causal > Eventual Consistency. | CAP/PACELC trade-off: Strong consistency requires inter-node synchronization latency; eventual consistency scales horizontally but requires conflict resolution (CRDTs, LWW). | **Last-Write-Wins (LWW) Data Loss:** Two concurrent updates overwrite each other based on unsynchronized NTP server clocks. **Fix:** Vector clocks or CRDTs for collaborative state. |
| **9** | **CAP & PACELC** | If Partition (P), choose Availability (A) or Consistency (C). Else (E), choose Latency (L) or Consistency (C). | DynamoDB/Cassandra: PA/EL (low latency, high availability). CockroachDB/Spanner: PC/EC (serializable transactions, higher latency). | **Network Partition Split-Brain:** Subnet partition causes two nodes to both believe they are leader and accept conflicting writes. **Fix:** Raft/Paxos majority quorum ($N/2 + 1$). |
| **10** | **Messaging & Event Streaming** | Kafka (partitioned append-only log, pull-based, consumer group offset tracking) vs. RabbitMQ (AMQP, broker queue, push-based). | Message retention & replayability (Kafka) vs. complex routing and per-message ack/nack (RabbitMQ). | **Poison Pill Message & Consumer Lag:** Malformed payload causes worker crash; consumer restarts and reads the same message in an infinite loop, stalling the partition. **Fix:** Dead Letter Queue (DLQ) with max retry counter. |
| **11** | **Async Processing & Workflows** | Background workers (Celery, Temporal workflows), Job queues, Backpressure (token-based or channel drop). | Immediate HTTP response vs. eventual completion; requires status polling or WebSocket callback. | **Worker OOM / Queue Flooding:** Upstream producer produces 100k tasks/sec; workers consume 10k/sec; unconstrained in-memory queue crashes workers. **Fix:** Backpressure (drop tail, reject with 429/503), bounded Redis streams. |
| **12** | **Distributed Rate Limiting** | Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log, Sliding Window Counter. | Accuracy vs. memory footprint: Sliding window log stores timestamps for every request ($O(N)$ memory); sliding window counter approximates within 0.05% error using 2 counters. | **Redis Race Condition on Sliding Window:** Concurrent requests read count 99, both increment to 100, exceeding limit 100. **Fix:** Atomic Redis Lua script or Redis Cell module. |
| **13** | **Reliability & Fault Isolation** | Circuit Breaker (Closed $\to$ Open $\to$ Half-Open), Exponential Backoff with Full Jitter, Bulkhead pattern. | Availability vs. resource protection: Circuit breakers shed load early to prevent cascading collapse of downstream dependencies. | **Retry Storm:** Downstream service slows down; 1,000 upstream clients retry simultaneously every 1s, tripling the load and ensuring the service never recovers. **Fix:** Full Jitter ($t = \text{random}(0, \min(M, B \times 2^i))$). |
| **14** | **Idempotency & Replay Safety** | Idempotency Keys stored in Redis/DB with unique constraints, Deduplication window. | Storage overhead of deduplication keys vs. double-spend / duplicate charge risk. | **Duplicate Payment Processing:** Client timeout on checkout; user clicks "Pay" twice. Two requests hit parallel servers. **Fix:** Insert `(idempotency_key, user_id, status='IN_PROGRESS')` in DB with unique constraint before processing charge. |
| **15** | **Distributed Locks & Leases** | Redis Redlock, ZooKeeper ephemeral nodes, etcd leases with Raft, Postgres advisory locks. | Safety vs. complexity: Distributed locks are notoriously vulnerable to network partitions and GC pauses without fencing tokens. | **GC Pause Lock Invalidation:** Worker 1 gets lock with 5s lease, hits 7s Java GC pause. Lock expires, Worker 2 gets lock. Worker 1 wakes up and writes to DB. **Fix:** Monotonically increasing fencing tokens passed to and verified by DB. |
| **16** | **Observability & Reliability Math** | OpenTelemetry, Prometheus (pull metrics), Jaeger (distributed tracing with trace/span IDs), SLO/SLA/Error budgets. | Storage cost & CPU overhead of 100% trace sampling vs. missing 1-in-a-million tail latency bugs. | **Missing Trace Context:** HTTP boundary drops `traceparent` header; cross-service latency spike becomes invisible in telemetry. **Fix:** Automatic Envoy/service mesh sidecar header propagation. |
| **17** | **Storage Systems (Blob/Object/Block)** | Object storage (S3, Ceph, MinIO), Block storage (EBS), Metadata database separation. | High throughput & durability (Erasure coding $8+4$) vs. no in-place byte mutation (immutable objects). | **Small File Metadata Explosion:** Storing 100M 1KB files in S3 wastes massive inode/metadata indexing. **Fix:** Haystack/SeaweedFS needle-in-haystack bundling into large aggregate data files. |
| **18** | **Search & Indexing Engines** | Inverted Index (Elasticsearch/Lucene), TF-IDF, BM25, Vector Embeddings (HNSW index). | Ingestion write latency (segment merging) vs. sub-50ms search query speed. | **Dual-Write Inconsistency between DB and Search:** App writes to Postgres and then Elasticsearch; Elasticsearch write fails. **Fix:** Transactional Outbox + Debezium CDC streaming to ES. |
| **19** | **Real-Time Systems** | WebSockets (full duplex, persistent TCP), Server-Sent Events (SSE - unidirectional HTTP), Long Polling. | Connection density (file descriptors per server, memory per socket) vs. real-time sub-100ms push. | **Connection Thundering Herd on Deploy:** Rolling restart of 10 gateway servers drops 1M WebSockets; 1M clients immediately reconnect, crashing new nodes. **Fix:** Connection jitter + backoff on client reconnect. |
| **20** | **High-Scale File Uploads** | Direct S3 presigned URLs, Multipart chunked upload, Client-side MD5 hashing, Resume capability. | Bypassing app server CPU/bandwidth by uploading directly to S3 vs. verifying auth tokens prior to upload. | **Orphaned Chunk Storage:** User starts 10GB multipart upload, uploads 8GB, and closes browser. Unassembled parts bill storage indefinitely. **Fix:** S3 Lifecycle rule to abort incomplete multipart uploads after 3 days. |
| **21** | **Feed Systems** | Fan-out on Write (push to followers' inbox caches) vs. Fan-out on Read (pull and merge dynamically). | Write amplification ($O(\text{followers})$ on write) vs. Read latency ($O(\text{following})$ queries on feed load). | **Celebrity Problem (Fan-out Write Explosion):** User with 50M followers posts; writing 50M cache entries takes 45 seconds. **Fix:** Hybrid fan-out (regular users fan-out on write; celebrities fan-out on read). |
| **22** | **URL Shortener** | Base62 encoding ($[0-9a-zA-Z]$), 7 characters ($62^7 \approx 3.5 \text{ trillion}$ URLs), Distributed Snowflake ID vs Hash truncation. | MD5/SHA256 hash collision resolution vs. pre-allocated ID ranges via distributed sequencer. | **MD5 Hash Collision Loops:** Hashing long URL and taking first 7 chars causes collisions; recursive salt-and-rehash causes latency spikes. **Fix:** Auto-incrementing distributed 64-bit ID $\to$ Base62 encode. |
| **23** | **Chat Systems** | Message sequencing, WebSocket gateways, Redis Pub/Sub for local connection routing, Cassandra message archive. | Message delivery guarantees (At-least-once vs. Exactly-once) and offline queue storage. | **Out-of-Order Message Display:** Channel messages arrive over different network routes with skewed timestamps. **Fix:** Per-channel monotonic sequence IDs generated by a sequencer service. |
| **24** | **Video Streaming Platforms** | Video chunking (HLS / MPEG-DASH), Transcoding pipeline (Bitrate ladders: 1080p, 720p, 480p), CDN Edge Caching. | Compute cost of multi-resolution transcoding vs. edge delivery bandwidth savings. | **CDN Cache Miss on Viral Upload:** First 100k users request newly uploaded video chunks simultaneously before CDN edge caches populate. **Fix:** Origin Shield caching + byte-range request coalescing. |
| **25** | **Geospatial & Ride Matching** | Geohash (Base32 space-filling curve), Google S2, Uber H3 (Hexagonal hierarchical spatial index). | Index update frequency for moving objects vs. spatial query speed ($O(1)$ cell lookup). | **Driver Location Ping Saturation:** 500k drivers sending GPS pings every 3s = 166k write QPS to geospatial index. **Fix:** Ephemeral in-memory Redis geospatial buffer (no disk write on raw GPS); persist only trip milestones. |
| **26** | **Financial Ledgers & Payments** | Double-Entry Bookkeeping (immutable debits/credits where $\sum \text{debits} = \sum \text{credits}$), Idempotency state machine, Reconciliation worker. | Eventual consistency is STRICTLY FORBIDDEN in balance transfers; requires ACID serializable transactions or deterministic state machine. | **Transient Payment Timeout:** Bank gateway returns 504. Did the user get charged? **Fix:** Payment state = `PENDING_RECONCILIATION`; asynchronous reconciliation worker polls bank API before refunding or confirming. |
| **27** | **Large-Scale Multi-Tier Architecture** | Tiered storage (NVMe warm $\to$ S3 cold), Edge routing, Global multi-region active-active vs active-passive. | Cross-region replication latency ($100\text{ms}+$ speed of light) vs. disaster recovery RTO/RPO. | **Split-Brain Database Split in Active-Active:** Both US-East and EU-Central accept conflicting writes during transatlantic fiber cut. **Fix:** Partition single master per tenant / user account (geosharding). |

---

## The 4-Step System Design Interview Framework

When walking into any 45-minute interview, execute this exact timeline:

```
[00:00 - 05:00] Step 1: Clarify Scope & Calculate Scale
├── Functional Requirements (top 3 user stories only)
├── Non-Functional Requirements (Latency, High Availability vs Consistency, Durability)
└── Back-of-the-envelope math (QPS peak, Storage/yr, Network bandwidth)

[05:00 - 15:00] Step 2: High-Level Architecture & API Contracts
├── REST / gRPC API definitions (inputs, outputs, error codes)
├── Data Model schema (Primary keys, Partition keys, Indexes)
└── End-to-end component diagram (Client -> LB -> Gateway -> Service -> Storage)

[15:00 - 35:00] Step 3: Deep Dive & Bottleneck Resolution
├── Solve the core hard problem (e.g., matching engine, fan-out, sharding key)
├── Trade-off analysis (Explain WHY you chose Cassandra over PostgreSQL)
└── Scaling bottlenecks (Hot keys, caching strategies, replication lag)

[35:00 - 45:00] Step 4: Reliability, Failure Modes & Wrap-Up
├── Component failure scenarios (What if Redis dies? What if network partitions?)
├── Observability (P99 latency metrics, Distributed Tracing, Error budgets)
└── Future enhancements (Multi-region active-active, cold storage tiering)
```

---

## The 3-Step Daily Mastery Workflow

Mastering system design is not about memorizing static block diagrams. Follow this daily 3-step loop:

1. **Pick One Topic Daily:** Focus on one of the 27 building blocks above. Understand *why* it exists in distributed computing and dissect the exact trade-offs (e.g., Latency vs. Consistency, Read throughput vs. Write amplification).
2. **Design on Paper & Explain Out Loud:** Sketch a real-world system leveraging that component on a blank sheet or whiteboard. Articulate every design decision, edge case, and failure mode out loud as if explaining to a Principal Engineer.
3. **Connect Requirements to Components:** Do not memorize fixed architectures (like "Uber architecture" or "Twitter architecture"). Instead, practice extracting non-functional constraints (e.g., 50k write QPS, 99.99% availability, strict linearizability) and deducing the necessary components from first principles.

---

## AI Tutor & Voice Chat Simulation Protocol

Use voice-enabled AI tutors or conversational agents to run live interactive mock system design sessions:

### Prompt Template for System Design Voice Sparring:
> *"Act as a Principal Infrastructure Architect at a Tier-1 tech company conducting a 45-minute System Design interview for a Senior/Staff role. We will design [System Name, e.g., Distributed Payment Ledger / Real-time Geospatial Matching]. Interrupt me to challenge my assumptions, probe edge cases (e.g., network partitions, GC pauses, thundering herds), demand quantitative calculations, and enforce trade-off evaluations. Do not give away answers; push back when my design lacks depth."*

### Integrated Preparation Roadmap:
* **AI Engineering & LLMOps:** Multi-model routing (FacadeDriver), dynamic context budget chunking, Presidio PII sanitization pipelines, RAG with hybrid search + rerankers, and LLM-as-Judge eval gates.
* **High-Level Design (HLD):** Sharding, consensus (Raft/Paxos), distributed streaming (Kafka), multi-region active-active databases, and CDN edge caching.
* **Low-Level Design (LLD) & Clean Architecture:** Gang of Four design patterns, concurrency primitives (locks, semaphores, atomic CAS), thread pools, and domain-driven design.
* **Data Structures & Algorithms (DSA):** Monotonic queues, Tries, Skip Lists, Segment Trees, Bloom Filters, and Graph traversals (BFS/DFS/Dijkstra).

---

## Topic-to-Chapter Directory Index

Each of the 27 building blocks maps directly to the in-depth reference chapters in this repository:

| # | Topic | Deep-Dive Directory Guide |
|---|---|---|
| **1** | Requirements & Scale | [01. Scaling](../01.%20Scaling/README.md) · [02. Back Of the Envelope Estimation](../02.%20Back%20Of%20the%20Envelope%20Estimation/README.md) · [03. System Design Framework](../03.%20System%20Design%20Framework/README.md) |
| **2** | APIs & Contracts | [03. System Design Framework](../03.%20System%20Design%20Framework/README.md) |
| **3** | Load Balancing | [01. Scaling](../01.%20Scaling/README.md) |
| **4** | Caching | [01. Scaling](../01.%20Scaling/README.md) · [system-design-mastery-interactive.html](../system-design-mastery-interactive.html) |
| **5** | Databases & Storage | [06. Key-Value Store](../06.%20Key-Value%20Store/README.md) · [database-sharding.html](../database-sharding.html) |
| **6** | Data Partitioning & Sharding | [05. Consistent Hashing](../05.%20Consistent%20Hashing/README.md) · [consistent-hashing.html](../consistent-hashing.html) · [database-sharding.html](../database-sharding.html) |
| **7** | Replication & Consensus | [06. Key-Value Store](../06.%20Key-Value%20Store/README.md) · [29. Git at Scale](../29.%20Git%20at%20Scale%20-%20Cursor%20Origin%20&%20Continuity/README.md) |
| **8** | Consistency Models | [06. Key-Value Store](../06.%20Key-Value%20Store/README.md) · [system-design-mastery-interactive.html](../system-design-mastery-interactive.html) |
| **9** | CAP & PACELC | [06. Key-Value Store](../06.%20Key-Value%20Store/README.md) |
| **10** | Messaging & Queues | [19. Distributed Message Queue](../19.%20Distributed%20Message%20Queue/README.md) |
| **11** | Async Processing | [10. Notification System](../10.%20Notification%20System/README.md) · [21. Ad Click Aggregation](../21.%20Ad%20Click%20Event%20Aggregation/README.md) |
| **12** | Rate Limiting | [04. Rate Limiter](../04.%20Rate%20Limiter/README.md) · [distributed-rate-limiter.html](../distributed-rate-limiter.html) |
| **13** | Reliability & Fault Isolation | [00. Curriculum](README.md) · [system-design-mastery-interactive.html](../system-design-mastery-interactive.html) |
| **14** | Idempotency & Safety | [26. Payment System](../26.%20Payment%20System/README.md) · [payment-processing-billion-scale.md](../payment-processing-billion-scale.md) |
| **15** | Distributed Locks & Leases | [00. Curriculum](README.md) · [system-design-mastery-interactive.html](../system-design-mastery-interactive.html) |
| **16** | Observability & SLOs | [20. Metrics Monitoring & Alerting](../20.%20Metrics%20Monitoring%20and%20Alerting%20System/README.md) |
| **17** | Storage Systems | [24. S3-like Object Storage](../24.%20S3-like%20Object%20Storage/README.md) · [15. Google Drive](../15.%20Google%20Drive/README.md) |
| **18** | Search Systems | [13. Search Autocomplete](../13.%20Search%20Autocomplete/README.md) · [09. Web Crawler](../09.%20Web%20Crawler/README.md) |
| **19** | Real-Time Systems | [12. Chat System](../12.%20Chat%20System/README.md) · [17. Nearby Friends](../17.%20Nearby%20Friends/README.md) |
| **20** | High-Scale File Uploads | [15. Google Drive](../15.%20Google%20Drive/README.md) · [24. S3-like Object Storage](../24.%20S3-like%20Object%20Storage/README.md) |
| **21** | Feed Systems | [11. News Feed System](../11.%20News%20Feed%20System/README.md) |
| **22** | URL Shortener | [08. URL Shortener](../08.%20URL%20Shortener/README.md) · [07. Unique-Id Generator](../07.%20Unique-Id%20Generator/README.md) |
| **23** | Chat Systems | [12. Chat System](../12.%20Chat%20System/README.md) |
| **24** | Video Streaming | [14. Youtube](../14.%20Youtube/README.md) |
| **25** | Geospatial & Ride Matching | [16. Proximity Service](../16.%20Proximity%20Service/README.md) · [18. Google Maps](../18.%20Google%20Maps/README.md) · [17. Nearby Friends](../17.%20Nearby%20Friends/README.md) |
| **26** | Financial Ledgers & Payments | [26. Payment System](../26.%20Payment%20System/README.md) · [27. Digital Wallet](../27.%20%20Digital%20Wallet/README.md) · [payment-processing-billion-scale.md](../payment-processing-billion-scale.md) |
| **27** | Large-Scale Multi-Tier Architecture | [28. Stock Exchange](../28.%20Stock%20Exchange/README.md) · [29. Git at Scale](../29.%20Git%20at%20Scale%20-%20Cursor%20Origin%20&%20Continuity/README.md) |
| **28** | Production Loops & Scenarios | [36. Netflix 8-Round Interview Loop Mastery](../36.%20Netflix%208-Round%20Interview%20Loop%20Mastery/README.md) |
| **29** | The 7 Layers of Production System Design | [37. The 7 Layers of Production System Design](../37.%20The%207%20Layers%20of%20Production%20System%20Design/README.md) |
| **30** | Product & Engineering Metrics Rubric | [38. The Product & Engineering Metrics Rubric](../38.%20The%20Product%20%26%20Engineering%20Metrics%20Rubric/README.md) |

---

## 🎯 The 26 Canonical System Design Problems: Fundamental Revision Blueprint

To crack Senior/Staff interviews at **Meta, Google, Microsoft, and Netflix**, revise your fundamentals across these **26 canonical system design problems** divided into **6 functional categories**. Every production interview problem is an architectural composite of these 26 foundations:

### Category 1: Foundations & Distributed Systems
1. **Scale From Zero To Millions Of Users:** [01. Scaling](../01.%20Scaling/README.md) — Multi-tier caching, stateless microservices, read-replica replication, geosharding.
2. **Back-of-the-envelope Estimation:** [02. Back Of the Envelope Estimation](../02.%20Back%20Of%20the%20Envelope%20Estimation/README.md) — QPS calculations, latency numbers every programmer should know, memory vs disk IOPS sizing.
3. **A Framework For System Design Interviews:** [03. System Design Framework](../03.%20System%20Design%20Framework/README.md) — The 4-step 45m interview loop pacing, 7-layer production mental model.
4. **Design A Rate Limiter:** [04. Rate Limiter](../04.%20Rate%20Limiter/README.md) — Token bucket, sliding window logs, Redis atomic Lua scripts, multi-region rate synchronization.
5. **Design Consistent Hashing:** [05. Consistent Hashing](../05.%20Consistent%20Hashing/README.md) — Ketama hash ring, virtual nodes for hotspot prevention, zero-downtime cluster rebalancing.
6. **Design A Unique ID Generator In Distributed Systems:** [07. Unique-Id Generator](../07.%20Unique-Id%20Generator/README.md) — Twitter Snowflake, clock drift mitigation, 64-bit sequence partitioning.

### Category 2: Storage & Data Systems
7. **Design A Key-Value Store:** [06. Key-Value Store](../06.%20Key-Value%20Store/README.md) — LSM-Tree (MemTable, WAL, SSTable, Compaction) vs B+ Tree, Quorum consensus ($R+W>N$).
8. **Design Google Drive:** [15. Google Drive](../15.%20Google%20Drive/README.md) — 4MB block chunking, SHA-256 content deduplication, delta sync, S3 + metadata SQL database.
9. **S3-like Object Storage:** [24. S3-like Object Storage](../24.%20S3-like%20Object%20Storage/README.md) — Blob storage nodes, metadata service, Reed-Solomon erasure coding, garbage collection.
10. **Distributed Message Queue:** [19. Distributed Message Queue](../19.%20Distributed%20Message%20Queue/README.md) — Partitioned commit logs, zero-copy `sendfile()`, consumer group offset rebalancing.
11. **Metrics Monitoring and Alerting System:** [20. Metrics Monitoring and Alerting System](../20.%20Metrics%20Monitoring%20and%20Alerting%20System/README.md) — Timeseries DB (Gorilla compression), pull vs push telemetry, anomaly detection.
12. **Ad Click Event Aggregation:** [21. Ad Click Event Aggregation](../21.%20Ad%20Click%20Event%20Aggregation/README.md) — Lambda/Kappa stream architecture, Flink tumbling/sliding windows, watermark handling, idempotent aggregation.

### Category 3: Search & Discovery Systems
13. **Design A URL Shortener:** [08. URL Shortener](../08.%20URL%20Shortener/README.md) — Base62 encoding, pre-generated sequence ranges, 99:1 read:write caching.
14. **Design A Web Crawler:** [09. Web Crawler](../09.%20Web%20Crawler/README.md) — Frontier priority/politeness queues, robots.txt caching, Bloom filter duplicate URL checks.
15. **Design A Search Autocomplete System:** [13. Search Autocomplete](../13.%20Search%20Autocomplete/README.md) — In-memory Trie structure, cached top-K query nodes, offline MapReduce build pipelines.

### Category 4: Communication & Social Systems
16. **Design A Notification System:** [10. Notification System](../10.%20Notification%20System/README.md) — Multi-channel fan-out (APNS, FCM, SES), user opt-out/rate limits, priority queues.
17. **Design A News Feed System:** [11. News Feed System](../11.%20News%20Feed%20System/README.md) — Push (fan-out on write) vs Pull (fan-out on read) for celebrities, timeline Redis caches.
18. **Design A Chat System:** [12. Chat System](../12.%20Chat%20System/README.md) — WebSocket connection managers, presence servers, Cassandra message history, Raft/ZK synchronization.
19. **Distributed Email Service:** [23. Distributed Email Service](../23.%20Distributed%20Email%20Service/README.md) — SMTP/IMAP protocol gateways, distributed maildir storage, spam classification DAGs.

### Category 5: Geo-Spatial Systems
20. **Proximity Service:** [16. Proximity Service](../16.%20Proximity%20Service/README.md) — Geohash vs Quadtree vs Google S2 spatial indexing, 2D geospatial search.
21. **Nearby Friends:** [17. Nearby Friends](../17.%20Nearby%20Friends/README.md) — Ephemeral location updates, Redis Pub/Sub, geohash grid channel multiplexing.
22. **Design Google Maps:** [18. Google Maps](../18.%20Google%20Maps/README.md) — Map tile slicing by zoom level, road graph partitioning, Dijkstra/A* routing engine.

### Category 6: Large-Scale Applications & Financial Systems
23. **Design YouTube:** [14. Youtube](../14.%20Youtube/README.md) — Video chunk ingestion, asynchronous transcoding DAGs (H.264/AV1), CDN edge caches, adaptive bitrate (DASH/HLS).
24. **Hotel Reservation System:** [22. Hotel Reservation System](../22.%20Hotel%20Reservation%20System/README.md) — Relational ACID booking transactions, optimistic locking with version checks, 2-phase room hold.
25. **Real-time Gaming Leaderboard:** [25. Real-time Gaming Leaderboard](../25.%20Real-time%20Gaming%20Leaderboard/README.md) — Redis Sorted Sets (`ZADD`, `ZRANK`), distributed sharding by score ranges.
26. **Payment System & Stock Exchange:** [26. Payment System](../26.%20Payment%20System/README.md) · [27. Digital Wallet](../27.%20%20Digital%20Wallet/README.md) · [28. Stock Exchange](../28.%20Stock%20Exchange/README.md) — Idempotency keys, double-entry ledgers, 2PC/Sagas, LMAX Disruptor order matching engine.


