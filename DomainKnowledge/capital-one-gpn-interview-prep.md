# Capital One GPN — Senior Lead Software Engineer Interview Prep

> **Role**: Senior Lead Software Engineer, Full Stack — Global Payment Network (GPN)
> **Req ID**: R242981
> **Recruiter**: Jeffrey Jackson (jeffrey.jackson1@capitalone.com, 224-619-4398)
> **Stack**: Java, Spring Boot, Microservices, Kafka, AWS, Docker, Kubernetes, React/Angular, SQL, Oracle, AI tools
> **SLA**: Five-nines (99.999%) availability — ~5 min downtime/year
> **Domain**: Money movement, payments, banking compliance (OCC, PCI-DSS, SOX)
> **Foundation**: Builds on `dms-developer-interview-guide.md` (DMS = your pharma analog, 21 CFR Part 11)

---

## How to use this file

The DMS guide (`dms-developer-interview-guide.md`) is your **foundation** — every question there is one you can answer from muscle memory because you built DMS. This file adds:

1. **DMS → GPN translation layer** — which DMS questions transfer directly, which need rewording for payments
2. **Capital One-specific gaps** — Kafka depth, payments domain, five-nines, banking compliance, microservices at scale, Oracle DB, distributed systems
3. **Your answer anchors** — mapped to your real experience (Lilly, Southwest, Airbnb, Oracle, NYU)

**Study order:** DMS guide Tier 1 (must-pass) → this file Section 1 (transfers) → Section 2 (GPN-specific) → Section 3 (payments domain) → Section 4 (system design).

---

## 1. DMS Guide → GPN Translation

### Transfers directly (swap "FDA" → "OCC/PCI-DSS")

| DMS Q | Topic | GPN framing |
|---|---|---|
| Q1 | Constructor injection | Same — Spring Boot is Spring Boot |
| Q2 | Layered architecture | Same — Controller→Service→Repository, DTOs not entities |
| Q3 | LAZY vs EAGER, `@EntityGraph` | Same — JPA is JPA |
| Q4 | `@Transactional` boundaries | Same — **even more critical for payments** (double-spend risk) |
| Q5 | Compare-before-mutate audit bug | Same pattern — **payments: idempotency key check before debit** |
| Q6 | Optimistic locking `@Version` | Same — **critical for payments** (concurrent updates to same account) |
| Q7 | Error response contract | Same — **never expose stack traces in banking APIs** |
| Q8 | Audit columns NULL on INSERT | Same — **PCI-DSS/SOX audit trails are non-negotiable** |
| Q9 | Soft delete | Same — **payments records are never hard-deleted (Reg E disputes)** |
| Q10 | Flyway idempotency | Same — **schema migrations on 24/7 payments systems need zero-downtime** |
| Q11 | NOT NULL column on 500K rows | Same — **but GPN tables are 100M+ rows, batch backfill is mandatory** |
| Q12 | `clear()+addAll()` reconciliation | Same — in-place reconciliation, never bulk replace |
| Q17 | Frontend route guards ≠ security | Same — **backend must enforce every payment authorization** |
| Q22 | Security mindset | Same — **IDOR in payments = someone sees your transactions** |
| Q33-38 | JPA lazy loading deep dive | Same — **but N+1 at GPN scale = connection pool exhaustion in seconds** |
| Q57 | IDOR vulnerability | Same — **payments IDOR = account takeover** |
| Q60 | Hardcoded "SYSTEM" | Same — **banking audit trails need real user IDs for SOX** |
| Q61 | Conditional audit stamps | Same — **every payment state change must be auditable** |
| Q64 | UTC datetime contract | Same — **settlement times are timezone-critical (T+0, T+1)** |
| Q65 | Stale closure | Same — React is React |
| Q66 | System-wide sibling audit | Same — **a payments bug pattern likely exists in 10 services, not 1** |
| Q67 | 6-layer field completeness | Same — DB→Entity→DTO→Mapper→TS→UI |
| Q68 | `@Enumerated(STRING)` | Same — **ordinal corruption in payments = silent data loss** |
| Q73-76 | DB performance anti-patterns | Same — **but 100x more expensive at GPN scale** |

### Needs rewording (same concept, payments vocabulary)

| DMS Q | DMS context | GPN rewording |
|---|---|---|
| Q9 | "Pharma regulatory audit trail (FDA/GxP)" | "Banking regulatory audit trail (OCC, PCI-DSS, SOX, Reg E) — every transaction must be reconstructable for auditors and dispute resolution" |
| Q22 | "External user calls internal API" | "A merchant calls a cardholder-only endpoint — backend must enforce role + tenancy" |
| Q46 | "Hard delete destroys pharma audit trail" | "Hard delete destroys SOX audit trail + Reg E dispute records — illegal in banking" |
| Q54 | "Dose order approval workflow" | "Payment authorization workflow: fraud check → balance check → limit check → ledger post → settlement queue" |

### New for GPN (not in DMS guide — study these hard)

| Topic | Why GPN needs it | Section |
|---|---|---|
| Kafka depth (exactly-once, partitions, consumer groups) | Payments event sourcing, no duplicate charges | §2.1 |
| Idempotency keys | Double-spend prevention, retry safety | §2.2 |
| Saga pattern | Distributed transactions across microservices | §2.3 |
| Outbox pattern | Reliable event publishing (DB + Kafka atomicity) | §2.4 |
| Five-nines architecture | 99.999% vs 99.9% — 10x stricter | §2.5 |
| Payments domain (double-spend, settlement, clearing) | Core domain knowledge | §3 |
| Banking compliance (OCC, PCI-DSS, SOX, Reg E/Z) | Regulatory framing | §3.4 |
| Microservices at scale | GPN is not a monolith — service boundaries, network failure | §4 |
| Oracle DB specifics | JD lists Oracle explicitly | §2.6 |
| Concurrency at scale | Concurrent updates to same account | §2.7 |

---

## 2. GPN-Specific Technical Questions

### 2.1 Kafka Depth (Capital One will grill this — JD must-have)

**Q-G1: Exactly-once semantics** — A payment event is published to Kafka. A consumer debits the account and commits the offset. The consumer crashes after the debit but before the offset commit. What happens on restart? How do you prevent double-charging?

> **Expected**: Message redelivered → debit happens again → **double charge**. Fixes:
> 1. **Idempotency key** — store `paymentId + eventId` in dedup table; check before processing.
> 2. **Transactional consumer** — debit + offset commit in one transaction (Kafka 0.11+ EOS).
> 3. **Outbox pattern** — write to DB + outbox table in one transaction; separate poller publishes.
>
> **Your anchor**: "At Southwest I ran Kafka and RabbitMQ for flight-tracking. At Airbnb it's SNS/SQS/EventBridge, but the patterns transfer — idempotency keys, dead-letter queues, replay. For exactly-once in payments, I'd use the outbox pattern on the producer side and an idempotency-key table on the consumer side. Exactly-once is a two-sided problem — producer and consumer both need guarantees."

**Q-G2: Partition strategy** — You're designing Kafka topics for GPN payment events. How do you partition?

> **Expected**: Partition by **account ID** (or card ID) to guarantee ordering per account. Concurrent debits to the same account must be ordered to prevent balance corruption. Anti-pattern: partition by timestamp or round-robin. Partition count = max parallelism for consumers — size for peak throughput × 3-4x headroom.
>
> **Your anchor**: "Partition by account ID for ordering. At Southwest we partitioned flight events by flight number for the same reason — ordering matters for state machines. At Airbnb I partition by analyst ID for BPI VA event streams."

**Q-G3: Consumer group rebalance** — A consumer in your group crashes mid-rebalance. Some partitions are unassigned for 30 seconds. Payments are delayed. How do you handle this?

> **Expected**: 
> 1. **Sticky assignment** — `CooperativeStickyAssignor` minimizes partition movement.
> 2. **Static membership** — `group.instance.id` makes consumers sticky across restarts.
> 3. **Heartbeat + session timeout tuning** — balance fast failure detection vs false positives.
> 4. **Multi-region deployment** — failover to another region's consumers.

**Q-G4: Kafka vs SQS** — When would you pick Kafka over SQS for GPN?

> **Expected**: Kafka for: (1) event sourcing/replay (re-process last 7 days after a bug fix), (2) multiple consumers of same stream (fraud + ledger + notification all read the same payment event), (3) high throughput (100K+ events/sec), (4) strict ordering per partition. SQS for: (1) fire-and-forget notifications, (2) per-message visibility timeout, (3) simple work queues.
>
> **GPN reality**: Payment authorization needs Kafka (replay, multiple consumers). Notification emails can use SQS.
>
> **Your anchor**: "At Airbnb notifications go through SNS/SQS — fire-and-forget. At Southwest flight events went through Kafka because we needed replay and multiple consumers. GPN payments need Kafka for the same reasons — replay for bug recovery, multiple consumers for fraud + ledger + settlement."

### 2.2 Idempotency (the payments holy grail)

**Q-G5: Idempotency key design** — A user clicks "Pay" twice in 500ms. Two requests hit your API. How do you prevent double-charge?

> **Expected**: 
> 1. **Client-generated idempotency key** (UUID) in `Idempotency-Key` header.
> 2. **Server stores key + response** in dedup table (TTL 24h+).
> 3. First request: process payment, store `{key, response, status}`.
> 4. Second request (same key): return cached response, do NOT process again.
> 5. **Race condition**: two requests arrive simultaneously → `SELECT FOR UPDATE` on the key row, or unique constraint causing one to fail with 409.
>
> **Critical**: The idempotency check must happen **before** any side effect (debit, email, Kafka publish).
>
> **Your anchor**: "This is the compare-before-mutate pattern from DMS Q5, applied to payments. At Lilly I enforced audit-stamp-before-save. At GPN I'd enforce idempotency-key-check-before-debit. The pattern is the same — guard before the side effect, not after."

**Q-G6: Retry storms** — A downstream settlement service is slow. Your retry logic fires 3 retries with exponential backoff. The first call eventually succeeds at 8 seconds. But retries 2 and 3 already fired. The settlement service processes all 3. Triple settlement. How do you prevent this?

> **Expected**: 
> 1. **Idempotency key on the downstream call** — settlement service dedupes on `paymentId`.
> 2. **Retry only on transient errors** — 5xx, timeouts. Never retry on 4xx.
> 3. **Circuit breaker** — after N failures, stop retrying, fail fast. Async reconciler handles it.
> 4. **Saga with compensating transactions** — if retry causes double-settlement, a reversal saga fixes it.
>
> **Your anchor**: "At Airbnb I deal with LLM API retries — 30+ providers, each with different retry semantics. The pattern is idempotency key + circuit breaker + dead-letter queue. For payments it's the same but the stakes are higher — a duplicate LLM call is wasted money, a duplicate settlement is a regulatory incident."

### 2.3 Saga Pattern (distributed transactions)

**Q-G7: Distributed payment transaction** — A payment touches 3 services: Auth (fraud check), Ledger (debit/credit), Settlement (bank transfer). Separate databases. How do you ensure all 3 succeed or all 3 roll back?

> **Expected**: **Saga pattern** — two types:
> 1. **Choreography**: Each service publishes an event. Auth → `AuthApproved` → Ledger consumes → `LedgerPosted` → Settlement consumes. Compensating events on failure.
> 2. **Orchestration**: Central orchestrator calls each service in order. On failure, calls compensating actions in reverse. Easier to reason about, single source of truth.
>
> **For payments**: Orchestration is safer — clear audit trail of "who called whom and when." Choreography is harder to debug in a regulatory incident.
>
> **Critical**: Sagas are **not ACID** — they're eventually consistent. There's a window where the ledger is debited but settlement hasn't happened. Must have a **reconciliation job** that detects stuck sagas.
>
> **Your anchor**: "At Lilly the dose-order approval workflow was a saga across clinical supply, clinical ops, and manufacturer — sequential then parallel approval. I orchestrated it in one service with compensating actions. For GPN payments I'd use orchestration over choreography because the audit trail is cleaner for OCC examiners."

### 2.4 Outbox Pattern (reliable event publishing)

**Q-G8: DB write + Kafka publish atomicity** — Your service writes a payment to PostgreSQL, then publishes an event to Kafka. The DB commit succeeds, the Kafka publish fails. The payment is recorded but no downstream service knows. How do you fix this?

> **Expected**: **Transactional outbox pattern**:
> 1. Write payment + outbox row in **one DB transaction**.
> 2. Separate poller (or CDC like Debezium) reads outbox table and publishes to Kafka.
> 3. On publish success, mark outbox row as `published`.
> 4. On publish failure, retry with exponential backoff.
> 5. **Idempotency on consumer side** — Kafka may redeliver, consumers must dedupe.
>
> **Your anchor**: "This is the same problem as DMS audit trails — you need the side effect (audit row / Kafka event) to be atomic with the primary write. At Lilly I used DB triggers for audit. At GPN I'd use the outbox pattern for Kafka events — same principle, different transport."

### 2.5 Five-Nines Architecture (99.999% availability)

**Q-G9: 99.999% vs 99.9%** — You've shipped 99.9% uptime at Lilly. GPN requires 99.999%. What's different?

> **Expected**: 
> - **99.9%** = ~43 minutes/month downtime (Lilly — scheduled maintenance windows OK)
> - **99.999%** = ~5 minutes/year downtime (GPN — **no scheduled maintenance windows**, zero-downtime deploys mandatory)
> - **10x stricter** — requires:
>   1. **Multi-region active-active** — both regions serve traffic
>   2. **Zero-downtime deploys** — blue-green or canary, instant rollback
>   3. **Circuit breakers everywhere** — downstream failure must not cascade
>   4. **Graceful degradation** — if fraud check is slow, default to manual review
>   5. **Chaos engineering** — regular failure injection
>   6. **No single points of failure**
>
> **Your anchor**: "At Lilly 99.9% meant we could take a 30-min maintenance window monthly. GPN's 99.999% means zero-downtime deploys are mandatory — blue-green, canary, instant rollback. I'd push for multi-region active-active, circuit breakers on every downstream call, and a chaos engineering practice. The jump from 99.9% to 99.999% is not about better code — it's about architecture for failure."

**Q-G10: Zero-downtime deployment** — You need to deploy a schema change to GPN's payment service without taking it down. Walk me through it.

> **Expected**: **Expand-contract pattern**:
> 1. **Expand**: new code reads both old + new schema, writes both. Deploy first.
> 2. **Migrate**: backfill data, run Flyway migration (additive only).
> 3. **Contract**: new code reads + writes only new schema. Deploy.
> 4. **Cleanup**: remove old columns (after weeks, not days).
> 5. **Throughout**: blue-green or canary deploy, instant rollback if error rate spikes.
>
> **Never**: `ALTER TABLE DROP COLUMN` in the same deploy as the code that removes the column.
>
> **Your anchor**: "At Lilly we used Flyway with additive-only migrations — never drop in the same release. At Airbnb I do canary deploys with instant rollback. For GPN I'd use the expand-contract pattern — add column, backfill, switch code, drop old column weeks later."

### 2.6 Oracle DB (JD lists it explicitly)

**Q-G11: Oracle vs PostgreSQL** — You've used PostgreSQL at Lilly. GPN uses Oracle. What's different?

> **Expected**: 
> - **Oracle**: commercial, ACID-strong, RAC (Real Application Clusters) for active-active, PL/SQL stored procedures, materialized views, table partitioning built-in.
> - **PostgreSQL**: open-source, ACID-strong, no built-in active-active (need Patroni/Bucardo), PL/pgSQL, partitioning since v10.
> - **Key syntax differences**: Oracle `SEQUENCE` vs PG `SERIAL`, Oracle `NVL` vs PG `COALESCE`, Oracle `DUAL` table, Oracle `CONNECT BY` for hierarchies vs PG recursive CTEs.
>
> **Your anchor**: "I worked at Oracle the company on Oracle DB — P2P + O2C ERP analytics for 13 business units. I know PL/SQL, sequences, materialized views, partitioning. At Lilly I used PostgreSQL. The SQL patterns transfer; the main adjustment is Oracle-specific syntax and RAC for active-active clustering."

### 2.7 Concurrency at Scale

**Q-G12: Concurrent debits to same account** — Two transactions hit the same account simultaneously. Balance is $100. Transaction A is $60, Transaction B is $50. Both pass the balance check. Both debit. Final balance is -$10. How do you prevent this?

> **Expected**: 
> 1. **Pessimistic locking** — `SELECT ... FOR UPDATE` on the account row. First transaction locks, second waits. Slow but safe.
> 2. **Optimistic locking** — `@Version` field. Both read version=1. Both try to write. One gets `OptimisticLockException`, retries, re-reads balance ($40), fails the check.
> 3. **Conditional update** — `UPDATE accounts SET balance = balance - 60 WHERE id = ? AND balance >= 60`. Returns 0 rows if balance changed → retry or fail.
> 4. **Event sourcing** — all debits are events, single-writer per account, serialized.
>
> **For GPN**: Optimistic locking or conditional update for throughput. Pessimistic locking only for hot accounts.
>
> **Your anchor**: "This is DMS Q6 on steroids. At Lilly I used `@Version` for dose-order conflicts. For GPN I'd use conditional updates — `UPDATE ... WHERE balance >= amount` — because it's atomic at the DB level and doesn't require a separate version column."

---

## 3. Payments Domain Primer

### 3.1 The payment lifecycle (know this cold)

```
Authorization → Fraud Check → Balance Check → Ledger Post → Clearing → Settlement
     ↓              ↓              ↓              ↓           ↓           ↓
  100ms SLA     50ms SLA      20ms SLA       100ms       T+0/T+1     T+1/T+2
```

- **Authorization**: real-time yes/no — card swipe → issuer approves/declines
- **Fraud check**: ML model scores transaction, block if high-risk
- **Balance check**: sufficient funds?
- **Ledger post**: debit cardholder, credit merchant (internal ledger)
- **Clearing**: banks reconcile the transaction (batch, end of day)
- **Settlement**: actual money moves between banks (T+1 or T+2)

**GPN's role**: Capital One is both issuer (your Capital One card) and acquirer (merchant's bank). GPN handles the full lifecycle.

### 3.2 Payments-specific concerns

| Concern | What it means | Your answer anchor |
|---|---|---|
| **Double-spend** | Same payment processed twice | Idempotency key (Q-G5) |
| **Lost transaction** | Payment written to DB but not published | Outbox pattern (Q-G8) |
| **Ordering** | Debits must process before credits for same account | Kafka partition by account ID (Q-G2) |
| **Replay** | Re-process last 7 days after a bug fix | Kafka retention + idempotent consumers |
| **Reconciliation** | Internal ledger vs bank statement match | Batch job, T+1, flag mismatches |
| **Dispute (Reg E)** | Cardholder disputes a charge | Soft delete + audit trail (DMS Q9) |
| **Chargeback** | Merchant disputes a dispute | State machine: charge → dispute → chargeback → arbitration |

### 3.3 Payments vocabulary (use these words on the call)

| Term | Definition |
|---|---|
| **Issuer** | The bank that issued your card (Capital One) |
| **Acquirer** | The merchant's bank |
| **ISO 8583** | The message format for card transactions (think: HTTP for payments) |
| **Authorization code** | The "yes" from the issuer — 6-digit code |
| **Capture** | Merchant claims the authorized amount (separate from auth) |
| **Void** | Cancel an authorization before capture |
| **Refund** | Return money after capture |
| **Chargeback** | Cardholder disputes a charge, bank reverses it |
| **PCI-DSS** | Payment Card Industry Data Security Standard — card data handling |
| **Tokenization** | Replace card number with a token (Apple Pay, Google Pay) |
| **EMV** | Chip card standard (Europay/Mastercard/Visa) |
| **NOC** | Notification of Change (ACH — bank says "routing number changed") |
| **RTP** | Real-Time Payments (FedNow, same-day settlement) |

### 3.4 Banking compliance (know the acronyms)

| Regulation | What it covers | Your DMS analog |
|---|---|---|
| **OCC** | Office of the Comptroller of the Currency — regulates national banks | FDA of banking |
| **PCI-DSS** | Card data security (store, transmit, process) | 21 CFR Part 11 (data integrity) |
| **SOX** | Sarbanes-Oxley — financial reporting controls, audit trails | GxP audit trails |
| **Reg E** | Electronic Fund Transfer Act — consumer dispute rights | Pharma patient data rights |
| **Reg Z** | Truth in Lending — credit card disclosure | Informed consent |
| **BSA/AML** | Bank Secrecy Act / Anti-Money Laundering | Pharmacovigilance |

**Your framing**: "I haven't worked in banking compliance specifically — I've worked in FDA compliance (21 CFR Part 11 at Lilly). The muscle is the same: audit trails, data integrity, access control, regulated state changes, five-nines availability. Banking compliance is the same muscle, different regulator."

---

## 4. System Design — GPN Scenarios

### Q-G13: Design a payment authorization service

> **Requirements**: 10K auth requests/sec, 100ms p99 latency, 99.999% availability, fraud check + balance check + ledger post.
>
> **Approach**:
> 1. **API gateway** → rate limiting, auth, TLS termination
> 2. **Auth service** (Java/Spring Boot) → orchestrates fraud + balance + ledger
> 3. **Fraud service** (ML model) → async, 50ms SLA, circuit breaker (default to manual review if slow)
> 4. **Balance service** → reads from cache (Redis) backed by DB, conditional update for debit
> 5. **Ledger service** → writes to DB + outbox, publishes Kafka event
> 6. **Kafka** → partition by account ID, consumers for settlement + notification + reconciliation
> 7. **Multi-region active-active** → both regions serve, DB replication
> 8. **Circuit breakers** on every downstream call (Resilience4j)
> 9. **Idempotency** on every external-facing endpoint
>
> **Your anchor**: "At Lilly I built a real-time decision engine with 14 personas and 8-level RBAC under 21 CFR Part 11. At Airbnb I orchestrate 30+ LLMs behind a FacadeDriver with circuit breakers and fallbacks. For GPN auth, I'd use the same orchestration pattern — fraud + balance + ledger as downstream calls with circuit breakers, idempotency keys, and the outbox pattern for Kafka events."

### Q-G14: Design a reconciliation system

> **Requirements**: Match internal ledger against bank statements daily, flag mismatches, auto-resolve where possible.
>
> **Approach**:
> 1. **Batch job** (Airflow/Temporal) — runs T+1, pulls bank statement file (SFTP/EDI 823)
> 2. **Parser** — normalizes bank statement to internal format
> 3. **Matcher** — joins on transaction ID, amount, date; fuzzy match on timestamp ±5min
> 4. **Discrepancy classification**: missing in ledger (lost transaction), missing in bank (settlement failure), amount mismatch (fee error), duplicate
> 5. **Auto-resolve**: small fee mismatches (<$1) auto-accept; everything else → manual review queue
> 6. **Audit**: every reconciliation action logged for SOX
>
> **Your anchor**: "At Oracle I built ERP analytics across P2P + O2C for 13 business units — reconciliation between purchase orders, invoices, and payments was a core use case. At Shell I ran batch NLP pipelines on 17M pageviews/month. The reconciliation pattern is the same — normalize, join, classify discrepancies, auto-resolve the easy ones, queue the hard ones."

### Q-G15: Design for failure — payment service is down

> **Scenario**: Primary payment service is down in us-east-1. What happens?
>
> **Approach**:
> 1. **Health checks** — Kubernetes liveness/readiness probes detect failure
> 2. **Auto-failover** — traffic routes to us-west-2 (active-active, not cold standby)
> 3. **DB replication** — reads from replica, writes queue if primary unavailable
> 4. **Circuit breakers** — downstream services stop calling the failed region
> 5. **Graceful degradation** — if fraud check is down, default to manual review (don't block payments)
> 6. **Recovery** — when us-east-1 returns, replay queued writes, reconcile
> 7. **Communication** — status page, internal Slack, customer notification if visible
>
> **Your anchor**: "At Airbnb I deal with multi-provider LLM failover — if Azure is down, fail to Bedrock, then Vertex. The pattern is circuit breaker + fallback + replay. For GPN I'd apply the same pattern at the region level — active-active, circuit breakers between regions, replay for missed writes during the failover window."

---

## 5. Behavioral / Leadership Questions

### Q-G16: "Tell me about a time you led a technical decision"

> **Anchor (Lilly)**: "At Lilly I chose OpenShift on AWS over raw EKS for the DMS deployment. The trade-off was GitOps rollbacks vs raw Kubernetes control. OpenShift gave us ArgoCD GitOps, automated rollbacks, and a managed control plane — critical under 21 CFR Part 11 where every deployment had to be auditable. The decision paid off when we had a bad deploy in month 3 and rolled back in 90 seconds via ArgoCD, no manual kubectl, full audit trail."

### Q-G17: "Tell me about a production incident you owned"

> **Anchor (Lilly)**: "I owned on-call for DMS. We had a radiopharmaceutical dose-order stuck in PENDING_CO_MFG state for 4 hours — the parallel approval workflow had a race condition where the manufacturer approval was overwritten by the clinical ops approval. I traced it DB→BE→FE: the DB showed both approvals, the backend service was overwriting one with the other due to a `clear()+addAll()` bug (CMCDOS-3150). I fixed it with in-place reconciliation, wrote a regression test, and did a system-wide sibling audit — found the same pattern in 3 other services. That audit prevented 6 future bugs."

### Q-G18: "How do you handle tech debt?"

> **Anchor (Lilly/Airbnb)**: "At Lilly we had ~1200 ESLint warnings and ~187 TS errors inherited from R1. I tackled it incrementally — every PR that touched a file had to leave it cleaner than it found it (boy scout rule). I also did a system-wide audit for the `clear()+addAll()` anti-pattern and fixed all 4 instances in one PR. At Airbnb I do the same with LLM eval harnesses — every new model gets an eval before it ships, and I backfill evals for existing models when I touch them."

### Q-G19: "Why Capital One?"

> **Anchor**: "Capital One calls itself a tech company that happens to be a bank, and GPN is where that identity gets tested at five-nines scale. That's the exact problem shape I've shipped under, just in a different regulated industry. At Lilly I held 99.9% uptime under FDA compliance, 21 CFR Part 11. At Southwest I ran streaming pipelines for flight operations. Payments under banking compliance is the same muscle, whether the regulator is the FDA or the OCC. The post-Discover acquisition means GPN's scope just expanded significantly, and that's the kind of scale-and-modernization problem I want to own."

### Q-G20: "What's your weakness / honest gap?"

> **Anchor (honest, not under-claiming)**: "I haven't worked in banking payments specifically — OCC-regulated money movement. But I have built payments-adjacent systems at Oracle (order-to-cash cycle: invoicing, accounts receivable, payment collection, cash application, reconciliation across 13 business units) and NYU (credit-card fraud detection + billing pipeline on Kafka), plus regulated enterprise systems at scale with the same constraints: idempotency, ordering, audit trails, five-nines availability. Banking compliance is the same muscle, different regulator. The gap is banking-specific regulation (OCC, Reg E), not payments broadly."

---

## 6. Questions to Ask the Interviewer

### Tier 1 (must ask)

1. **Exact level**: "Senior Lead Software Engineer — does that map to Staff, Principal, or Senior in Capital One's leveling?"
2. **Location / remote**: "I'm based in Houston, no Capital One hub. What's the remote or hybrid policy?"
3. **IC vs people manager**: "Is this IC with technical leadership, or people management?"
4. **Why the role is open**: "Growth role or backfill? You mentioned ASAP."
5. **Interview process**: "What's the process and timeline from here to offer?"

### Tier 2 (ask if time allows)

6. **What "AI tools" means in GPN**: "GenAI for payments? ML for fraud/risk? Internal dev tooling?"
7. **Kafka expectation**: "Direct Kafka a hard requirement, or is event-driven architecture experience sufficient?"
8. **On-call**: "Five-nines is ~5 min/year. What's the on-call rotation? How many engineers?"
9. **Team size**: "How big is the GPN team? Sub-teams owning different parts of the payment flow?"
10. **Comp**: "Base, bonus, equity, sign-on?" (Ask LAST, never first.)

---

## 7. Red Flags to Avoid (Auto-Reject)

- "Route guards are sufficient for security" (DMS Q17)
- "Use `FetchType.EAGER` to fix lazy loading" (DMS Q3)
- "`SYSTEM` is fine for automated processes" (DMS Q60)
- "Just delete the row from `flyway_schema_history`" (DMS Q10)
- Puts business logic in controllers (DMS Q2)
- Can't explain `@Transactional` (DMS Q4)
- Says "I've worked in payments" when they haven't (over-claiming)
- Says "I have no payments experience" when they have O2C (under-claiming)
- Can't explain idempotency (Q-G5)
- Suggests direct push to `main` or skipping validation cycles (DMS Q21c)
- Uses `@Enumerated(EnumType.ORDINAL)` (DMS Q68)

---

## 8. Green Flags to Trigger (Bonus Points)

- Mentions **outbox pattern** for event-driven reliability unprompted (Q-G8)
- Says **"I'd check if the same pattern exists elsewhere"** before fixing a bug (DMS Q66)
- Mentions **idempotency keys** when discussing retries (Q-G5, Q-G6)
- Knows **saga pattern** for distributed transactions (Q-G7)
- Mentions **expand-contract** for zero-downtime schema changes (Q-G10)
- Asks about **on-call rotation and SLA** unprompted
- Mentions **OCC, PCI-DSS, SOX** without prompting
- Frames regulated enterprise as "same muscle, different regulator"
- Mentions **Kafka partition by account ID** for ordering (Q-G2)
- Spots the compare-before-mutate bug immediately (DMS Q5)

---

## 9. Study Checklist (T-minus before interview)

### 3 days before
- [ ] Re-read DMS guide Tier 1 (Q5, Q8, Q17, Q33-35, Q60, Q61, Q64, Q65, Q66, Q67, Q68, Q70, Q71, Q73-76, Q78)
- [ ] Read this file Sections 1-4
- [ ] Practice Q-G1 (exactly-once), Q-G5 (idempotency), Q-G7 (saga), Q-G8 (outbox) aloud

### 1 day before
- [ ] Re-read payments domain primer (Section 3)
- [ ] Practice behavioral answers (Section 5) aloud — 90 seconds each
- [ ] Review your resume bullets for Lilly, Southwest, Airbnb, Oracle — be ready to go deep on any
- [ ] Prepare 3 questions for the interviewer (Section 6)

### 1 hour before
- [ ] Read red flags (Section 7) + green flags (Section 8)
- [ ] Warm up with Q5 (audit bug) — spot it in <10 seconds
- [ ] Warm up with Q-G5 (idempotency) — the payments equivalent

### During the interview
- **Lead with Lilly** for regulated enterprise questions (21 CFR Part 11 → OCC)
- **Lead with Southwest** for Kafka/streaming questions
- **Lead with Airbnb** for AI tools + eval harness questions
- **Lead with Oracle** for payments-adjacent (O2C) + Oracle DB questions
- **Say "I'd check if the same pattern exists elsewhere"** when discussing any bug fix
- **Say "same muscle, different regulator"** when asked about banking vs pharma
- **Be honest about Kafka**: "ran Kafka at Southwest, AWS-native event-driven at Airbnb, patterns transfer"
- **Be honest about banking**: "no OCC experience, but Oracle O2C + NYU fraud + Lilly FDA-regulated = same constraints"

---

## 10. Your Asymmetric Advantage

This is your interview to lose. Every DMS question is one you can answer from muscle memory — you built the system, you fixed the bugs, you wrote the audit patterns. The GPN-specific questions (Kafka depth, payments domain, five-nines) are the gap, but they're closeable in days, not weeks.

**The framing that wins**: "I've shipped regulated enterprise systems at scale under FDA compliance. Payments under banking compliance is the same muscle — idempotency, ordering, audit trails, five-nines. The regulator is different, the constraints are the same. I built DMS at Lilly, I ran Kafka at Southwest, I orchestrate AI at Airbnb, I built ERP analytics at Oracle. GPN is where all of that comes together."
