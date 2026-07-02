# Interview Preparation Notes

This repository contains structured, high-density study guides, code blueprints, and interactive system design/DSA workbooks compiled to prepare for SDE interviews.

## Directory Structure

| Path | Topic | Focus Areas |
|---|---|---|
| [README.md](README.md) | Hub & Study Index | Navigation, study plans, core checklist |
| [DomainKnowledge/dms-developer-interview-guide.md](DomainKnowledge/dms-developer-interview-guide.md) | Original DMS Guide | Reference guide from Dose Management System |
| [DomainKnowledge/Java/java-spring-boot.md](DomainKnowledge/Java/java-spring-boot.md) | Spring Boot & Java Depth | DI, JPA/Hibernate LAZY vs EAGER, Transactions, AOP, custom annotations |
| [DomainKnowledge/PostgreSQL/database-postgres.md](DomainKnowledge/PostgreSQL/database-postgres.md) | Database, Indexing & Migrations | PostgreSQL, Flyway safety, triggers, auditing patterns |

## Interactive HTML Study Workbooks

These are premium, self-contained, light-themed interactive study workbooks that can be opened directly in any web browser. They feature step-by-step algorithms, visual animations, capacity estimation calculators, and low-level design patterns.

### Data Structures & Algorithms (DSA)
- [Sliding Window Maximum (Hard)](DSA/sliding-window-maximum.html): Uses Monotonic Deque. Covers problem intuition, boundary checks, and walk-through tracing.
- [Regular Expression Matching (Hard)](DSA/regular-expression-matching.html): Interactive execution state and recursion/dynamic programming trace.

### System Design & Low-Level Design (LLD)
- [Consistent Hashing Ring](SystemDesign/consistent-hashing.html): Design a decentralized request routing and partition key redistribution ring with virtual nodes.
- [Database Sharding](SystemDesign/database-sharding.html): Detailed partitioning strategies, routing layers, re-sharding, and cross-shard queries.
- [Gang of Four (GoF) Design Patterns (Python)](SystemDesign/design-patterns-python-lld.html): Interactive LLD workbook for structural, creational, and behavioral patterns.
- [Personal Brain Architecture](SystemDesign/personal-brain.html): Complete System Design & DSA breakdown of the local knowledge graph (FastMCP, Hebbian learning, BFS/DFS, KNN similarity, exponential decay).

## System Design Reference Guides

Detailed breakdowns of architectural foundations, scale estimation, core system components, and real-world system design case studies.

### Foundation & Building Blocks
- [01. Scaling](SystemDesign/01.%20Scaling/README.md) — Single server setup, replication, sharding, caching, CDN, multi-DC.
- [02. Back Of the Envelope Estimation](SystemDesign/02.%20Back%20Of%20the%20Envelope%20Estimation/README.md) — Power of two, latency numbers, QPS, storage, and bandwidth math.
- [03. System Design Framework](SystemDesign/03.%20System%20Design%20Framework/README.md) — 4-step framework for system design interviews.
- [04. Rate Limiter](SystemDesign/04.%20Rate%20Limiter/README.md) — Token bucket, leaking bucket, fixed window, sliding window log/counter.
- [05. Consistent Hashing](SystemDesign/05.%20Consistent%20Hashing/README.md) — Dynamic partition key routing, virtual nodes, hot spots mitigation.
- [06. Key-Value Store](SystemDesign/06.%20Key-Value%20Store/README.md) — CAP theorem, replication, consistency models, SSTables, LSM-trees.
- [07. Unique-Id Generator](SystemDesign/07.%20Unique-Id%20Generator/README.md) — Multi-master, UUIDs, Ticket Server, Twitter Snowflake ID.

### Core Systems & Infrastructure
- [08. URL Shortener](SystemDesign/08.%20URL%20Shortener/README.md) — API design, base 62 encoding, hashing, redirect flows.
- [09. Web Crawler](SystemDesign/09.%20Web%20Crawler/README.md) — DFS vs BFS, URL frontier, politeness, DNS resolver, duplicate detection.
- [10. Notification System](SystemDesign/10.%20Notification%20System/README.md) — Push, SMS, Email, rate-limiting, retry mechanism, templates.
- [19. Distributed Message Queue](SystemDesign/19.%20Distributed%20Message%20Queue/README.md) — Topic partitions, WAL, consumer groups, pull/push model, coordinate with Zookeeper.
- [20. Metrics Monitoring and Alerting System](SystemDesign/20.%20Metrics%20Monitoring%20and%20Alerting%20System/README.md) — Data collection, TSDB (Time Series DB), pull vs push, alerting pipeline.
- [24. S3-like Object Storage](SystemDesign/24.%20S3-like%20Object%20Storage/README.md) — Metadata store, data store, upload/download paths, erasure coding.

### High-Scale Web Applications
- [11. News Feed System](SystemDesign/11.%20News%20Feed%20System/README.md) — Fan-out on write vs fan-out on read, cache structures, retrieval.
- [12. Chat System](SystemDesign/12.%20Chat%20System/README.md) — WebSocket, keep-alive, message sync, push notifications, status.
- [13. Search Autocomplete](SystemDesign/13.%20Search%20Autocomplete/README.md) — Trie data structure, serialization, query service, prefix matching.
- [14. Youtube](SystemDesign/14.%20Youtube/README.md) — Video transcoding, CDN streaming, metadata DB, upload pipeline.
- [15. Google Drive](SystemDesign/15.%20Google%20Drive/README.md) — Block servers, delta sync, metadata sync, conflict resolution.

### Geospatial & Real-time Tracking
- [16. Proximity Service](SystemDesign/16.%20Proximity%20Service/README.md) — Geospatial indexes, Geohash, Quadtree, SQL spatial extension.
- [17. Nearby Friends](SystemDesign/17.%20Nearby%20Friends/README.md) — Redis Pub/Sub, geohash-based message routing, location updates.
- [18. Google Maps](SystemDesign/18.%20Google%20Maps/README.md) — Map tiles, routing tiles, Dijkstra/A* pathfinding, ETA service.

### Advanced Enterprise Systems
- [21. Ad Click Event Aggregation](SystemDesign/21.%20Ad%20Click%20Event%20Aggregation/README.md) — MapReduce, stream processing, windowing (tumbling/sliding), fault tolerance.
- [22. Hotel Reservation System](SystemDesign/22.%20Hotel%20Reservation%20System/README.md) — Concurrency control (optimistic/pessimistic locking), inventory management, DB constraints.
- [23. Distributed Email Service](SystemDesign/23.%20Distributed%20Email%20Service/README.md) — SMTP, IMAP/POP3, email storage engine, search indexing.
- [25. Real-time Gaming Leaderboard](SystemDesign/25.%20Real-time%20Gaming%20Leaderboard/README.md) — Redis Sorted Sets (ZADD/ZRANGE), skip lists, scaling read QPS.
- [26. Payment System](SystemDesign/26.%20Payment%20System/README.md) — Ledger, double-entry bookkeeping, payment gateways, reconciliation.
- [27.  Digital Wallet](SystemDesign/27.%20%20Digital%20Wallet/README.md) — 2-phase commit (2PC), event sourcing, CQRS, transactional state machine.
- [28. Stock Exchange](SystemDesign/28.%20Stock%20Exchange/README.md) — Order matching engine, order book, sequencer, L1/L2/L3 market data.

## DSA Reference Library

A comprehensive collection of Python solutions and code structures for standard data structures and algorithmic paradigms.

### Linear & Hierarchical Structures
- [AVL Tree](DSA/AVL%20Tree)
- [Array](DSA/Array)
- [LinkList](DSA/LinkList)
- [Queue](DSA/Queue)
- [Stack](DSA/Stack)
- [Tree](DSA/Tree)
- [Tries](DSA/Tries)

### Advanced Algorithms & Paradigms
- [Back Tracking](DSA/Back_Tracking)
- [Binary Search](DSA/Binary_Search)
- [Bitwise Manipulation](DSA/Bitwise_Manipulation)
- [Dynamic Programming](DSA/Dynamic%20Programming)
- [Graph](DSA/Graph)
- [Greedy](DSA/Greedy)
- [Hashing](DSA/Hashing)
- [Heap](DSA/Heap)
- [Line Sweep Algorithm](DSA/Line%20Sweep%20Algorithm)
- [Prefix Sum](DSA/Prefix%20Sum)
- [Segment Tree](DSA/Segment%20Tree)
- [Sliding Window](DSA/Sliding%20%20Window)
- [Sorting](DSA/Sorting)
- [Two Pointer](DSA/Two%20Pointer)
- [Recursion](DSA/recursion)

### Math, Systems & Misc
- [Basic Math](DSA/Basic%20Math)
- [Maths and Geometry](DSA/Maths%20and%20Geometry)
- [Concurrency & Multithreading](DSA/Concurrency%20%26%20Multithreading)
- [Designing Questions](DSA/Designing%20Questions)
- [Disjoint Set Union](DSA/Disjoint%20Set%20Union)
- [Probability and Statistics](DSA/Probability%20and%20Statistics)
- [Recursion and String](DSA/Recursion_and_String)

## Domain Knowledge Study Index

### 1. Java / Spring Boot Core
- **Dependency Injection**: Preference for `@RequiredArgsConstructor` (constructor injection) over field `@Autowired` for testability, final field immutability, and startup fail-fast.
- **Entity State Lifecycle**: FetchType.LAZY by default. Use `@EntityGraph` or custom JPQL joins to avoid N+1 select problems.
- **Transactions**: Intercepted via Spring AOP proxies. Must be `public` and invoked from outside the class boundary to apply rollback behavior.

### 2. Databases & Migrations
- **Flyway Migrations**: SQL migration versioning (`V###__desc.sql`). Rules for non-destructive, idempotent changes (`IF NOT EXISTS` / `IF EXISTS`).
- **Database Auditing**: Master-data triggers writing JSON payloads (`OLD`/`NEW` representation) to `audit_logs` table.
- **Business Triggers**: Enforcing business constraints at the database level to ensure consistency (e.g., protocol site uniqueness).

### 3. Frontend & State Management
- **React 18 + Jotai**: State management using atomic Jotai stores. Component separation between state containers and presentation.
- **TypeScript**: Enforcing strict typings for API request/response payloads to match backend DTOs.
