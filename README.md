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
- [10 Production Systems Deconstructed](SystemDesign/30.%2010%20Production%20Systems%20Deconstructed/index.html): Interactive deep-dives into 10 flagship production architectures (Notion Postgres Sharding, Quora 100k+ MySQL QPS, Shopify GraphQL & Wasm Checkout Sandboxing, YouTube Video DAG Transcoding, Google GFS, Slack Flannel Caching, URL Shortener Sequencers) with live failure simulators.
- [System Design Mastery & Failure Mode Interactive Workbook](SystemDesign/00.%20System%20Design%20Mastery%20Curriculum/index.html): Master 27 system design topics with real-time simulators (Distributed Locks & GC pauses, Dual-Write vs Outbox CDC, Cache Stampede Singleflight, Rate Limiting), dynamic Scale Calculator, and Senior/Staff interview drills.
- [Consistent Hashing Ring](SystemDesign/05.%20Consistent%20Hashing/index.html): Design a decentralized request routing and partition key redistribution ring with virtual nodes.
- [Database Sharding](SystemDesign/01.%20Scaling/index.html): Detailed partitioning strategies, routing layers, re-sharding, and cross-shard queries.
- [Gang of Four (GoF) Design Patterns (Python)](SystemDesign/35.%20Gang%20of%20Four%20Design%20Patterns%20%28LLD%29/index.html): Interactive LLD workbook for structural, creational, and behavioral patterns.
- [Personal Brain Architecture](SystemDesign/34.%20Personal%20Brain%20Knowledge%20Graph/index.html): Complete System Design & DSA breakdown of the local knowledge graph (FastMCP, Hebbian learning, BFS/DFS, KNN similarity, exponential decay).
- [Git at Scale — Cursor Origin & Continuity](SystemDesign/29.%20Git%20at%20Scale%20-%20Cursor%20Origin%20%26%20Continuity/index.html): Interactive visual study guide on S3 Write-Ahead Logs (WAL), stateless warm NVMe caches, Rendezvous Hashing, and 3PC vs CAS consensus.

## System Design Reference Guides & Interactive Workbooks

Every single system design module is fully self-contained with its dedicated **Markdown Documentation (`README.md`)** and **Interactive Visual Workbook (`index.html`)**.

| # | Topic / Module | Markdown Guide | Interactive Workbook (HTML) |
|---|---|---|---|
| **00** | **System Design Mastery Curriculum** | [README.md](SystemDesign/00.%20System%20Design%20Mastery%20Curriculum/README.md) | [index.html](SystemDesign/00.%20System%20Design%20Mastery%20Curriculum/index.html) |
| **01** | **Scaling & Database Sharding** | [README.md](SystemDesign/01.%20Scaling/README.md) | [index.html](SystemDesign/01.%20Scaling/index.html) |
| **02** | **Back Of the Envelope Estimation** | [README.md](SystemDesign/02.%20Back%20Of%20the%20Envelope%20Estimation/README.md) | [index.html](SystemDesign/02.%20Back%20Of%20the%20Envelope%20Estimation/index.html) |
| **03** | **System Design Framework (4-Step)** | [README.md](SystemDesign/03.%20System%20Design%20Framework/README.md) | [index.html](SystemDesign/03.%20System%20Design%20Framework/index.html) |
| **04** | **Rate Limiter (Distributed Token Bucket)** | [README.md](SystemDesign/04.%20Rate%20Limiter/README.md) | [index.html](SystemDesign/04.%20Rate%20Limiter/index.html) |
| **05** | **Consistent Hashing Ring** | [README.md](SystemDesign/05.%20Consistent%20Hashing/README.md) | [index.html](SystemDesign/05.%20Consistent%20Hashing/index.html) |
| **06** | **Key-Value Store (SSTables & LSM-Tree)** | [README.md](SystemDesign/06.%20Key-Value%20Store/README.md) | [index.html](SystemDesign/06.%20Key-Value%20Store/index.html) |
| **07** | **Unique-Id Generator (Snowflake)** | [README.md](SystemDesign/07.%20Unique-Id%20Generator/README.md) | [index.html](SystemDesign/07.%20Unique-Id%20Generator/index.html) |
| **08** | **URL Shortener at Scale** | [README.md](SystemDesign/08.%20URL%20Shortener/README.md) | [index.html](SystemDesign/08.%20URL%20Shortener/index.html) |
| **09** | **Distributed Web Crawler** | [README.md](SystemDesign/09.%20Web%20Crawler/README.md) | [index.html](SystemDesign/09.%20Web%20Crawler/index.html) |
| **10** | **Notification System** | [README.md](SystemDesign/10.%20Notification%20System/README.md) | [index.html](SystemDesign/10.%20Notification%20System/index.html) |
| **11** | **News Feed System (Fan-out on Write/Read)** | [README.md](SystemDesign/11.%20News%20Feed%20System/README.md) | [index.html](SystemDesign/11.%20News%20Feed%20System/index.html) |
| **12** | **Chat System (WebSockets & Sequencing)** | [README.md](SystemDesign/12.%20Chat%20System/README.md) | [index.html](SystemDesign/12.%20Chat%20System/index.html) |
| **13** | **Search Autocomplete (Trie & Cache)** | [README.md](SystemDesign/13.%20Search%20Autocomplete/README.md) | [index.html](SystemDesign/13.%20Search%20Autocomplete/index.html) |
| **14** | **YouTube Video Transcoding Pipeline** | [README.md](SystemDesign/14.%20Youtube/README.md) | [index.html](SystemDesign/14.%20Youtube/index.html) |
| **15** | **Google Drive (Block Sync & Conflict)** | [README.md](SystemDesign/15.%20Google%20Drive/README.md) | [index.html](SystemDesign/15.%20Google%20Drive/index.html) |
| **16** | **Proximity Service (Geohash & Quadtree)** | [README.md](SystemDesign/16.%20Proximity%20Service/README.md) | [index.html](SystemDesign/16.%20Proximity%20Service/index.html) |
| **17** | **Nearby Friends (Redis Pub/Sub)** | [README.md](SystemDesign/17.%20Nearby%20Friends/README.md) | [index.html](SystemDesign/17.%20Nearby%20Friends/index.html) |
| **18** | **Google Maps (Tiles & Dijkstra/A*)** | [README.md](SystemDesign/18.%20Google%20Maps/README.md) | [index.html](SystemDesign/18.%20Google%20Maps/index.html) |
| **19** | **Distributed Message Queue (Kafka WAL)** | [README.md](SystemDesign/19.%20Distributed%20Message%20Queue/README.md) | [index.html](SystemDesign/19.%20Distributed%20Message%20Queue/index.html) |
| **20** | **Metrics Monitoring & Alerting (TSDB)** | [README.md](SystemDesign/20.%20Metrics%20Monitoring%20and%20Alerting%20System/README.md) | [index.html](SystemDesign/20.%20Metrics%20Monitoring%20and%20Alerting%20System/index.html) |
| **21** | **Ad Click Event Aggregation (Streaming)** | [README.md](SystemDesign/21.%20Ad%20Click%20Event%20Aggregation/README.md) | [index.html](SystemDesign/21.%20Ad%20Click%20Event%20Aggregation/index.html) |
| **22** | **Hotel Reservation (Pessimistic/Optimistic)** | [README.md](SystemDesign/22.%20Hotel%20Reservation%20System/README.md) | [index.html](SystemDesign/22.%20Hotel%20Reservation%20System/index.html) |
| **23** | **Distributed Email Service** | [README.md](SystemDesign/23.%20Distributed%20Email%20Service/README.md) | [index.html](SystemDesign/23.%20Distributed%20Email%20Service/index.html) |
| **24** | **S3-like Object Storage (Erasure Coding)** | [README.md](SystemDesign/24.%20S3-like%20Object%20Storage/README.md) | [index.html](SystemDesign/24.%20S3-like%20Object%20Storage/index.html) |
| **25** | **Real-Time Gaming Leaderboard (Skip List)** | [README.md](SystemDesign/25.%20Real-time%20Gaming%20Leaderboard/README.md) | [index.html](SystemDesign/25.%20Real-time%20Gaming%20Leaderboard/index.html) |
| **26** | **Payment System (Double-Entry & Sagas)** | [README.md](SystemDesign/26.%20Payment%20System/README.md) | [index.html](SystemDesign/26.%20Payment%20System/index.html) |
| **27** | **Digital Wallet (CQRS & Event Sourcing)** | [README.md](SystemDesign/27.%20%20Digital%20Wallet/README.md) | [index.html](SystemDesign/27.%20%20Digital%20Wallet/index.html) |
| **28** | **Stock Exchange (Order Matching Engine)** | [README.md](SystemDesign/28.%20Stock%20Exchange/README.md) | [index.html](SystemDesign/28.%20Stock%20Exchange/index.html) |
| **29** | **Git at Scale (Cursor Origin & Continuity)** | [README.md](SystemDesign/29.%20Git%20at%20Scale%20-%20Cursor%20Origin%20%26%20Continuity/README.md) | [index.html](SystemDesign/29.%20Git%20at%20Scale%20-%20Cursor%20Origin%20%26%20Continuity/index.html) |
| **30** | **10 Production Systems Deconstructed** | [README.md](SystemDesign/30.%2010%20Production%20Systems%20Deconstructed/README.md) | [index.html](SystemDesign/30.%2010%20Production%20Systems%20Deconstructed/index.html) |
| **31** | **Covert Real-Time Interview Copilots** | [README.md](SystemDesign/31.%20Covert%20Real-Time%20Interview%20Copilots/README.md) | [index.html](SystemDesign/31.%20Covert%20Real-Time%20Interview%20Copilots/index.html) |
| **32** | **Credit Card Application Service** | [README.md](SystemDesign/32.%20Credit%20Card%20Application%20Service/README.md) | [index.html](SystemDesign/32.%20Credit%20Card%20Application%20Service/index.html) |
| **33** | **Real-Time Fraud Detection System** | [README.md](SystemDesign/33.%20Real-Time%20Fraud%20Detection%20System/README.md) | [index.html](SystemDesign/33.%20Real-Time%20Fraud%20Detection%20System/index.html) |
| **34** | **Personal Brain Knowledge Graph** | [README.md](SystemDesign/34.%20Personal%20Brain%20Knowledge%20Graph/README.md) | [index.html](SystemDesign/34.%20Personal%20Brain%20Knowledge%20Graph/index.html) |
| **35** | **Gang of Four Design Patterns (LLD)** | [README.md](SystemDesign/35.%20Gang%20of%20Four%20Design%20Patterns%20%28LLD%29/README.md) | [index.html](SystemDesign/35.%20Gang%20of%20Four%20Design%20Patterns%20%28LLD%29/index.html) |
| **36** | **Netflix 8-Round Interview Loop Mastery** | [README.md](SystemDesign/36.%20Netflix%208-Round%20Interview%20Loop%20Mastery/README.md) | [index.html](SystemDesign/36.%20Netflix%208-Round%20Interview%20Loop%20Mastery/index.html) |
| **37** | **The 7 Layers of Production System Design** | [README.md](SystemDesign/37.%20The%207%20Layers%20of%20Production%20System%20Design/README.md) | [index.html](SystemDesign/37.%20The%207%20Layers%20of%20Production%20System%20Design/index.html) |
| **38** | **The Product & Engineering Metrics Rubric** | [README.md](SystemDesign/38.%20The%20Product%20%26%20Engineering%20Metrics%20Rubric/README.md) | [index.html](SystemDesign/38.%20The%20Product%20%26%20Engineering%20Metrics%20Rubric/index.html) |

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
