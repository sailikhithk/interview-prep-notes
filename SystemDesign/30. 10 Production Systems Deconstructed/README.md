# 10 Production Systems Deconstructed

> Battle-tested architectural breakdowns of 10 real-world systems operating under extreme production scale.

🔗 **Interactive Study Workbook:** [Open index.html](index.html)

---

## The 10 Flagship Case Studies

1. **Notion:** Sharding a monolithic PostgreSQL database into 32 AWS RDS shards by Workspace ID, eliminating RDS storage exhaustion at the cost of cross-shard foreign keys.
2. **Quora:** Scaling MySQL to 100k+ QPS using Memcached consistent hash clusters, read replicas, and replica-lag-aware routing proxies.
3. **Shopify APIs:** GraphQL multi-tenant scaling with AST query complexity cost limits to prevent nested connection denial-of-service attacks.
4. **Shopify Checkout:** WebAssembly (Wasm) isolated micro-runtimes (5ms CPU / 10MB RAM limits) inside independent Pod/Cell architectures to isolate custom merchant scripts during Black Friday flash sales.
5. **System Design Interview Pitfalls:** The 7 fatal candidate mistakes (silent whiteboard drawing, premature micro-optimization, ignoring dual-write divergence, hand-waving auth).
6. **YouTube:** Video ingestion DAG transcoding across 8 bitrate ladders (HLS/MPEG-DASH chunks) with Origin Shield caching and byte-range request coalescing.
7. **Google File System (GFS):** Decoupled control and data planes with a single in-memory Master and 64MB chunkservers designed to withstand commodity hardware failure.
8. **Back of the Envelope Math:** Capacity estimation constants every engineer must memorize (L1 cache 0.5ns, RAM 100ns, NVMe 10µs, Cross-DC 100ms, 80/20 Pareto cache sizing).
9. **Slack:** Real-time messaging across 10M+ WebSockets using the Flannel in-memory channel cache proxy, Delta Sync tokens, and reconnect jitter.
10. **Billion-Scale URL Shortener:** Auto-incrementing distributed 64-bit Snowflake sequencers with Base62 encoding ($62^7 \approx 3.52\text{T}$ keys) and 301 vs 302 redirect analytics.

---

## Architectural Comparison Matrix

| System | Primary Architectural Focus | What They Sacrificed | Core Failure Mode Defended |
| :--- | :--- | :--- | :--- |
| **Notion** | Workspace-level RDS Sharding | Foreign keys & cross-shard transactions | Storage & connection pool exhaustion on AWS RDS |
| **Slack** | Real-time edge caching (Flannel) | Total global ordering across teams | Gateway connection storms & fan-out latency |
| **Shopify** | Cell architecture & Wasm sandboxes | Shared global cache efficiency | Untrusted merchant code crashing checkout pods |
| **GFS** | Decoupled metadata/data plane | Low-latency random small-file I/O | Frequent commodity hardware & drive crashes |
