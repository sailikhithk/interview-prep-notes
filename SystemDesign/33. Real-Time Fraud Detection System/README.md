# Real-Time Fraud Detection System (Billion-Scale Fintech)

> High-throughput stream processing, feature store engineering, ML inference pipelines, and sub-50ms decision engines for real-time financial transaction scoring.

🔗 **Interactive Study Workbook:** [Open index.html](index.html) | [Capital One Case Study](fraud-detection-capital-one.html)

---

## Architecture Overview

```
[ Card Swipe / Payment Request ]
               │ (Synchronous Auth Hold, SLA < 50ms)
               ▼
   [ Edge Payment Gateway ]
               │
   ┌───────────┴─────────────────────────────┐
   ▼                                         ▼
[ Rule Engine (Stateless) ]        [ Real-Time Feature Store ]
 (Hard velocity & blacklist)        (Redis / Feast / Rockset)
   │                                         │
   └───────────┬─────────────────────────────┘
               ▼
  [ ML Model Scoring Engine ] (ONNX / Triton GPU Cluster)
               │ (Risk Score: 0 - 1000)
               ▼
    [ Decision Orchestrator ] ──► [ Approve / Step-up MFA / Decline ]
               │ (Async Event Ingestion)
               ▼
    [ Kafka Event Stream ] ──► [ Flink Aggregations ] ──► [ Offline Graph DB ]
```

---

## Core SLAs and Trade-Offs

- **Hard Latency Budget:** $< 50\text{ms}$ end-to-end at the 99.9th percentile. If ML scoring exceeds 40ms, fallback to rule-based baseline to prevent payment timeout.
- **Feature Aggregation:** Sliding windows (e.g., *Transactions in last 5 mins*, *Distance between current POS and last swipe*) computed in real-time using Redis sliding-window counters and Apache Flink stateful streams.
- **Graph Clustering:** Heterogeneous Graph Neural Networks (GNNs) analyzing money-mule rings and synthetic identities offline, projecting risk embeddings back to Redis.
