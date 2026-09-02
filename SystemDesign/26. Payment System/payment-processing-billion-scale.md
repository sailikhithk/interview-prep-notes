# Payment Processing at Billion-Transaction Scale

**Type:** SYSTEM DESIGN · **Context:** Capital One GPN · Senior Round
**Scale:** 1B tx/day, 12K tx/sec peak · **Latency:** p99 < 200ms · **Availability:** 99.99% · **Compliance:** PCI-DSS, OCC

Design Capital One's payment processing system that handles card transactions (auth, capture, settlement) at scale. The system must process 1B+ transactions per day, integrate with card networks (Visa, Mastercard), ensure exactly-once processing, detect fraud in real time, and comply with PCI-DSS and OCC regulations.

## 1. Problem Statement

**Functional Requirements:**
- **Authorization:** Verify card is valid and funds are available. Hold the amount.
- **Capture:** Complete the transaction. Move held funds to merchant.
- **Settlement:** Batch process at end of day. Transfer funds via ACH/Fedwire.
- **Refund:** Reverse a captured transaction.
- **Void:** Cancel an authorization before capture.

**Non-Functional Requirements:**
- **Scale:** 1B transactions/day, 12K tx/sec peak (Black Friday)
- **Latency:** p99 < 200ms for authorization (customer is waiting at POS)
- **Availability:** 99.99% (4 min downtime/month). Payment failures lose customers.
- **Consistency:** Exactly-once processing. No double charges, no missed charges.
- **Durability:** No transaction ever lost. Audit trail for 7 years (regulatory).
- **Compliance:** PCI-DSS Level 1, OCC regulation, SOX audit

## 2. Pattern Recognition

**Why signals:**
- High write throughput + low latency → partition by transaction ID, shard the database
- Exactly-once processing → idempotency keys, dedup at ingestion
- Real-time fraud check → sync call to fraud service with timeout + circuit breaker
- Batch settlement → Kafka + batch processor, not real-time
- Regulatory audit → append-only ledger, event sourcing
- External dependency (Visa/Mastercard) → saga pattern, compensating transactions

**Core pattern:** Event-driven microservices with Kafka as the backbone. Idempotent ingestion, synchronous auth path (fraud + ledger), asynchronous settlement path. Event-sourced ledger for audit. Saga for cross-service transactions.

## 3. High-Level Architecture

```
Merchant POS / App
       |
       v
  [API Gateway] --- rate limit, auth, TLS
       |
       v
  [Payment Service] --- orchestrates auth flow
       |
       +---> [Fraud Service] (sync, 50ms timeout, circuit breaker)
       +---> [Ledger Service] (sync, double-entry write)
       +---> [Card Network Adapter] (sync to Visa/MC, 100ms timeout)
       |
       v
  [Kafka] --- transaction events
       |
       +---> [Settlement Service] (batch, end of day)
       +---> [Notification Service] (SMS/email to customer)
       +---> [Analytics Service] (streaming aggregations)
       +---> [Compliance Service] (regulatory reports)

  Databases:
  - Ledger DB (Cassandra, partitioned by account_id)
  - Transaction DB (PostgreSQL sharded by tx_id)
  - Idempotency Store (Redis, 24h TTL)
  - Audit Store (S3 + Glacier, 7-year retention)
```

## 4. How to Think About It

**Q1: What is the critical path?**
Authorization: customer is waiting at the POS terminal. Every millisecond counts. Fraud check + ledger write + card network call must all complete in < 200ms. This drives the architecture: sync calls with tight timeouts, circuit breakers, and fallbacks.

**Q2: What can be asynchronous?**
Settlement (end-of-day batch), notifications, analytics, compliance reporting. These do not block the customer. Push to Kafka, process later. This separates the fast path (auth) from the slow path (everything else).

**Q3: How do you ensure exactly-once?**
Idempotency key on every request (client-generated UUID). Store in Redis with 24h TTL. If a duplicate arrives, return the cached result. At the ledger level, use a transaction ID as the primary key. Duplicate writes are rejected by the database.

**Q4: → What fails and how?**
Fraud service down: fail open (approve) or fail closed (decline)? For customer experience, fail open with a post-transaction fraud review. For security, fail closed. This is a business decision. Card network down: queue the transaction, retry with exponential backoff. Ledger write fails: fail the transaction, no money moves.

## 5. Real-World Analogy

Think of a **restaurant with a front-of-house and a back-of-house**. The front-of-house (waiter, POS terminal) is the auth path: customer is waiting, everything must be fast. The waiter checks with the kitchen (fraud service: is this order suspicious?), checks inventory (ledger: do we have the ingredients?), and confirms with the customer (card network: is the card valid?). All in under 2 minutes.

The back-of-house (settlement, reporting) happens after the customer leaves. The chef reconciles the day's orders, sends the receipts to accounting, orders more ingredients for tomorrow. No customer is waiting, so it can be batch and slow.

The idempotency key is the order number. If the waiter accidentally submits the same order twice, the kitchen sees the same order number and does not cook it twice. The ledger is the recipe book: every dish has a double-entry (debit ingredients, credit the plate).

## 6. Build Your Intuition

**Q: Why Kafka instead of direct service-to-service calls?**
Decoupling. The auth service publishes a transaction event. Settlement, notification, analytics, and compliance all subscribe independently. Adding a new consumer (e.g., rewards points) does not touch the auth service. Kafka also provides replay (reprocess if a consumer has a bug) and buffering (handle traffic spikes).

**Q: Why Cassandra for the ledger and PostgreSQL for transactions?**
Ledger is write-heavy, append-only, partitioned by account_id. Cassandra is optimized for this: high write throughput, linearizable writes within a partition. Transactions need ACID (auth, capture, refund are stateful). PostgreSQL gives transactions, foreign keys, and rich queries. Polyglot persistence: use the right tool for each workload.

**Q: Why not use 2PC (two-phase commit) for the saga?**
2PC blocks until all participants agree. If the card network is slow (100ms), the entire transaction is blocked. At 12K tx/sec, this creates cascading timeouts. Saga with compensating actions is preferred: each step commits locally, failures trigger compensating transactions. Higher availability, lower latency, but requires idempotency and careful ordering.

**Q: How do you handle Black Friday traffic spikes (10x normal)?**
Auto-scaling: Kubernetes HPA based on CPU and queue depth. Pre-provision for known events (Black Friday). Kafka buffers the spike: consumers scale up to drain the queue. The idempotency store (Redis) is scaled by cluster mode. The ledger (Cassandra) handles spikes naturally due to its write-optimized design.

## 7. How It Works (Step by Step)

- **Step 1:** Merchant sends auth request with idempotency key, card token, amount, merchant ID.
- **Step 2:** API Gateway authenticates, rate-limits, routes to Payment Service.
- **Step 3:** Payment Service checks idempotency store (Redis). If duplicate, return cached result. If new, proceed.
- **Step 4:** Payment Service calls Fraud Service (sync, 50ms timeout). Fraud returns approve/decline/review. If timeout, fail open (approve) with post-transaction review.
- **Step 5:** Payment Service calls Ledger Service (sync). Ledger writes double-entry: debit customer account, credit merchant hold account. Atomic within a Cassandra partition.
- **Step 6:** Payment Service calls Card Network Adapter (sync, 100ms timeout). Visa/MC returns auth code. If timeout, mark as pending, retry async.
- **Step 7:** Payment Service publishes "transaction.authorized" event to Kafka. Returns auth code to merchant.
- **Step 8:** Async consumers: Notification Service sends SMS. Analytics Service updates dashboards. Settlement Service queues for end-of-day batch.
- **Step 9:** End of day: Settlement Service batches transactions, sends to ACH/Fedwire. publishes "transaction.settled" event.

## 8. Data Model

**Transaction (PostgreSQL, sharded by tx_id):**
```
transactions:
  tx_id          UUID PK
  idempotency_key VARCHAR(64) UNIQUE
  type           ENUM(auth, capture, refund, void)
  status         ENUM(pending, approved, declined, settled, failed)
  amount         DECIMAL(12,2)
  currency       CHAR(3)
  card_token     VARCHAR(128)  -- PCI tokenized
  merchant_id    VARCHAR(64)
  customer_id    VARCHAR(64)
  auth_code      VARCHAR(32)
  created_at     TIMESTAMP
  settled_at     TIMESTAMP NULL
  fraud_score    INT
  fraud_decision ENUM(approve, review, decline)
```

**Ledger Entry (Cassandra, partitioned by account_id):**
```
ledger_entries:
  account_id     VARCHAR PARTITION KEY
  tx_id          UUID CLUSTERING KEY
  entry_type     ENUM(debit, credit)
  amount         DECIMAL(12,2)
  balance_after  DECIMAL(12,2)
  created_at     TIMESTAMP
  -- Append-only, never updated or deleted
```

**Idempotency Record (Redis, 24h TTL):**
```
idempotency:{key} = {
  tx_id: UUID,
  status: approved/declined,
  auth_code: VARCHAR,
  response_payload: JSON
}
TTL: 24 hours
```

## 9. Scalability Deep Dive

**Throughput:** 12K tx/sec peak. Payment Service: stateless, scale to 100 pods. Cassandra: 30 nodes, 3 replicas, 10 shards. Kafka: 6 brokers, 30 partitions. Redis: 6-node cluster.

**Latency:** p99 < 200ms. Breakdown: gateway 5ms, idempotency 2ms, fraud 50ms, ledger 20ms, card network 100ms, Kafka publish 5ms. Total ~182ms. Buffer for tail latency.

**Sharding Strategy:** Transactions: hash(tx_id) mod N. Ledger: hash(account_id) mod N (all entries for an account on one partition). Kafka: partition by merchant_id for settlement ordering.

**Caching:** Redis for idempotency (24h TTL), card token to account mapping (1h TTL), merchant config (1h TTL). Hot accounts cached in Payment Service L1 cache (Caffeine, 10K entries, 5min TTL).

## 10. Failure Modes & Resilience

- **Fraud Service Timeout:** Fail open for low-risk (approve, post-review). Fail closed for high-risk (decline). Circuit breaker: after 5 consecutive timeouts, stop calling for 30s. Post-transaction review queue for fail-open cases.
- **Ledger Write Failure:** Fail the transaction. No money moves without a ledger entry. Cassandra quorum write retries internally. If quorum cannot be reached, return error to merchant. Retry by merchant with same idempotency key.
- **Card Network Timeout:** Mark transaction as pending. Retry with exponential backoff (1s, 2s, 4s, 8s). After 3 retries, mark as failed and notify merchant. If Visa confirms later, reconcile. Idempotency key prevents double-auth on retry.
- **Kafka Unavailable:** Auth path still works (sync). Async consumers blocked. Buffer events in Payment Service memory (bounded queue, 10K). When Kafka recovers, flush. If buffer overflows, drop analytics events (lowest priority), keep settlement and notification.
- **Redis (Idempotency) Down:** Fall back to PostgreSQL lookup by idempotency_key. Slower (20ms vs 2ms) but correct. Circuit breaker on Redis. When Redis recovers, warm cache from recent transactions.
- **Network Partition (Split Brain):** Cassandra uses quorum (2 of 3 replicas). The partition with quorum continues. The minority partition rejects writes. When healed, Cassandra repairs via read-repair and hinted handoff. No data loss, no split-brain.

## 11. Edge Cases & Gotchas

- **Double spend (concurrent auths on same card):** Two auths arrive simultaneously for the same card. Both check balance, both see sufficient funds, both approve. Fix: serialize by card_id. Use a Redis lock or Cassandra lightweight transaction (IF NOT EXISTS) on the ledger.
- **Refund before settlement:** Merchant tries to refund a transaction that has not settled yet. Either block (return error) or allow (creates a negative entry, netted at settlement). Clarify business rule.
- **Currency conversion rounding:** Customer in EUR, merchant in USD. Convert at auth time, hold the converted amount. At settlement, reconvert. Rounding differences (sub-cent) accumulate. Use BigDecimal and a rounding policy. Reconciliation job catches discrepancies.
- **Partial auth (Visa Partial Authorization):** Customer has $50, transaction is $100. Visa supports partial auth: approve $50, decline $50. The system must handle this: split the transaction, return partial auth code.
- **Time skew across services:** Different services have slightly different clocks. Use NTP and a central time service. For ordering, use the Kafka offset, not wall clock.

## 12. Flashcards

**Q1: How do you ensure exactly-once processing?**
Client-generated idempotency key on every request. Redis cache (24h TTL) for fast dedup. Transaction DB unique constraint on idempotency_key as the source of truth. Ledger uses tx_id as primary key, duplicates rejected by Cassandra.

**Q2: Why saga instead of 2PC?**
2PC blocks on all participants. At 12K tx/sec, a slow card network (100ms) creates cascading timeouts. Saga commits each step locally, failures trigger compensating actions. Higher availability, lower latency, requires idempotency.

**Q3: How do you handle the auth vs settlement timing gap?**
Auth holds funds immediately (ledger entry with status=held). Settlement batches at end of day, converts held to settled. If auth expires (typically 7 days), release the hold. Reconciliation job detects orphaned holds.

**Q4: How do you achieve PCI-DSS compliance?**
Never store raw card numbers. Tokenize at ingress. Encrypt at rest (AES-256). Network segmentation: card data zone isolated. Audit all access. Annual penetration testing. QSA audit. The system never sees raw PAN after tokenization.

**Q5: How do you handle 10x traffic spikes (Black Friday)?**
K8s HPA auto-scales Payment Service. Kafka buffers the spike. Cassandra handles write spikes naturally. Pre-provision for known events. Rate limit at gateway to protect downstream. Shed non-critical traffic (analytics) if needed.

## 13. Where It Is Used (Real World)

- **Stripe:** Processes hundreds of millions of transactions per day. Uses a similar architecture: API gateway, idempotent ingestion, Kafka backbone, double-entry ledger.
- **Capital One:** Processes 1B+ card transactions per day. Uses Kafka extensively, event sourcing for the ledger, and a microservices architecture.
- **PayPal:** Handles 4B+ payment transactions per year. Uses a mix of synchronous (auth) and asynchronous (settlement) paths.
- **Square:** Processes card payments for merchants. Their engineering blog describes a ledger service very similar to this design: append-only, double-entry, Cassandra-backed, with Kafka for event distribution.

## 14. Common Mistakes

- No idempotency key. Network retries cause double charges.
- Using double for money. Precision errors. Use BigDecimal or integer cents.
- Single-entry ledger. No audit trail. Double-entry is mandatory for financial systems.
- Synchronous settlement. Settlement is batch, not real-time. Doing it synchronously blocks the auth path.
- No circuit breaker on fraud. Fraud service timeout blocks the entire auth.
- Storing raw card numbers. PCI-DSS violation. Tokenize at ingress, never store PAN.
- Not handling concurrent auths on same card. Double spend. Serialize by card_id.
- No reconciliation job. Silent failures accumulate. Daily reconciliation catches discrepancies.

## 15. Interview Tips

- Start with requirements. "Let me clarify the scale, latency, and consistency requirements." Write them down.
- Separate sync (auth) from async (settlement). The customer is waiting for auth. Settlement can wait. This is the key architectural decision.
- Draw the diagram. API Gateway, Payment Service, Fraud, Ledger, Card Network, Kafka, Settlement. Show the flow.
- Discuss idempotency early. It is the foundation. Every request has a key. Redis for fast dedup, DB for source of truth.
- Use double-entry ledger. This is a financial system. Mention it proactively. Shows domain understanding.
- Discuss failure modes. For each component: what if it fails? Circuit breakers, fallbacks, compensating transactions. This is the senior signal.
- Mention compliance. PCI-DSS, OCC, SOX. Tokenization, encryption, audit trail.
- Quantify everything. 12K tx/sec, p99 < 200ms, 99.99% availability. Numbers show you think about production.

## 16. Related System Design Problems

- **Distributed Ledger / Double-Entry Bookkeeping** — the core of any financial system — CORE
- **Idempotency at Scale** — dedup patterns for distributed systems — CORE
- **Design a Payment Gateway** (Stripe-like) — similar but merchant-focused — SIMILAR
- **Design a Wallet System** (PayPal/Venmo) — account-to-account transfers — SIMILAR
- **Design a Stock Trading System** — order matching, settlement — ADVANCED

## 17. Key Technologies

- **Kafka** — event backbone, durable, replayable
- **Cassandra** — write-optimized ledger, partitioned by account
- **PostgreSQL** — transaction state, ACID
- **Redis** — idempotency cache, distributed locks
- **Kubernetes** — container orchestration, HPA auto-scaling
- **Envoy / Istio** — service mesh, circuit breakers, mTLS
- **Flink** — stream processing for real-time analytics
- **Vault / KMS** — encryption key management, tokenization

## 18. Trade-Offs

- **Consistency vs Availability (CAP):** Ledger: choose consistency (quorum writes). Auth path: choose availability (fail open on fraud timeout). Different parts make different tradeoffs.
- **Latency vs Fraud Accuracy:** A more complex ML model gives better fraud detection but takes longer. 50ms budget for fraud. Fast rules engine (10ms) first pass, slower ML model (40ms) for borderline cases.
- **2PC vs Saga:** 2PC gives atomicity but blocks. Saga gives availability but requires compensating actions and idempotency. At scale, saga wins.
- **Cassandra vs Spanner vs PostgreSQL:** Cassandra: high write throughput, tunable consistency. Spanner: global strong consistency, expensive. PostgreSQL: ACID, but sharding is manual. For ledger, Cassandra with quorum is the sweet spot.
- **Event Sourcing vs CRUD:** Event sourcing (append-only ledger) gives perfect audit trail and replay. CRUD is simpler but loses history. For financial systems, event sourcing is worth the complexity. Regulatory requirement.

## 19. Monitoring & Observability

- **Metrics (Prometheus + Grafana):** Tx rate, p99 latency, error rate, fraud decline rate, auth success rate, settlement batch status, Kafka consumer lag, Cassandra write latency, Redis hit rate. Alert on SLO breaches.
- **Distributed Tracing (Jaeger/Zipkin):** Trace every transaction across services: gateway, payment, fraud, ledger, network. See where the 200ms is spent. Essential for debugging p99 issues.
- **Structured Logging (ELK / Splunk):** Every log line includes tx_id, idempotency_key, customer_id, merchant_id. Search by tx_id to see the full journey. No PII (card numbers) in logs. PCI compliance.
- **Reconciliation Jobs:** Daily: compare ledger totals vs card network reports vs bank account balances. Discrepancies trigger alerts. This is the safety net that catches silent failures.
- **Alerting (PagerDuty):** Page on: auth success rate < 99%, p99 latency > 200ms, ledger write failures > 0.1%, settlement batch failure, Kafka consumer lag > 10K. Runbooks for each alert.

## 20. Follow-Up Questions

**Q: How would you handle international payments (multi-currency)?**
FX rate service with real-time rates. At auth, convert and hold in customer currency. At settlement, convert to merchant currency. Cache FX rates with 1min TTL. Rounding policy: banker's rounding to nearest cent. Reconciliation handles sub-cent discrepancies.

**Q: How would you add support for recurring payments (subscriptions)?**
Tokenize the card at first auth. Store token with a subscription schedule. A scheduler triggers auth on the schedule. If auth fails (card expired), notify customer, retry with backoff. Use the same idempotency pattern with a subscription-specific key.

**Q: How would you handle chargebacks (customer disputes a transaction)?**
Chargeback is a separate flow. Customer initiates dispute. Dispute Service creates a chargeback record, debits the merchant account, credits the customer. Merchant can contest. If contested, arbitration via card network. The ledger tracks all of this.

**Q: How would you migrate from a monolith to this architecture without downtime?**
Strangler fig pattern. New features go to microservices. Old features migrated one at a time. Dual-write during migration: write to monolith and new service, compare results. Cut over when confident. Keep monolith as fallback for 30 days.

**Q: How would you handle a regulatory audit (OCC, PCI)?**
Event-sourced ledger provides the full audit trail. Every transaction has a complete history. Compliance Service generates reports on demand. Access logs show who accessed what. Encryption keys are rotated and audited. QSA audits annually.

## 21. Quick Reference

| Aspect | Value |
|--------|-------|
| **Architecture** | Event-driven microservices, Kafka backbone, sync auth + async settlement |
| **Scale** | 1B tx/day, 12K tx/sec peak, p99 < 200ms, 99.99% availability |
| **Key Patterns** | Idempotency keys, double-entry ledger, saga, circuit breakers, event sourcing |
| **Data Stores** | Cassandra (ledger), PostgreSQL (tx state), Redis (idempotency), S3 (audit) |
| **Compliance** | PCI-DSS (tokenization, encryption), OCC (audit trail), SOX (controls) |
| **Senior Signal** | Failure modes, tradeoffs, reconciliation, observability, compliance |

**Key decisions:**
```
1. Sync auth (customer waiting) vs async settlement (batch)
2. Idempotency key on every request (Redis + DB)
3. Double-entry ledger (Cassandra, append-only)
4. Saga over 2PC (availability over atomicity)
5. Kafka for decoupling (auth does not block on async consumers)
6. Circuit breakers on external calls (fraud, card network)
7. Event sourcing for audit (regulatory requirement)
8. Polyglot persistence (right tool for each workload)
```
