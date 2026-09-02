# Credit Card Application Service

**Type:** SYSTEM DESIGN · **Context:** Capital One GPN · Senior Round
**Scale:** 100K apps/day · **Latency:** instant decision < 5s · **Compliance:** FCRA, ECOA, OCC · **Integration:** Experian, Equifax, TransUnion

Design Capital One's credit card application system. A customer applies for a credit card online or in-app. The system pulls credit bureau data, scores the application, makes an instant decision (approve/deny/pending), and if approved, issues a card. The system must comply with FCRA, ECOA, and OCC regulations, and integrate with three credit bureaus.

## 1. Problem Statement

**Functional Requirements:**
- **Submit application:** Personal info, income, employment, desired card product.
- **Credit pull:** Soft pull (pre-qual) or hard pull (formal application) from bureaus.
- **Risk scoring:** Internal model + bureau score (FICO). Decision: approve/deny/pending.
- **Card issuance:** Generate card number, manufacture physical card, ship to customer.
- **Adverse action notice:** If denied, generate FCRA-compliant notice with reasons.
- **Application status:** Customer can check status online or via app.

**Non-Functional Requirements:**
- **Scale:** 100K applications/day, 1K/sec peak (marketing campaigns)
- **Latency:** Instant decision < 5 seconds (customer is waiting)
- **Availability:** 99.9% (not 99.99% like payments, this is not real-time POS)
- **Compliance:** FCRA (credit reporting), ECOA (fair lending), OCC (banking), PCI-DSS (card data)
- **Data retention:** 7 years (regulatory), adverse action notices 25 months
- **Fairness:** No discriminatory decisions. Regular fair lending audits.

## 2. Pattern Recognition

**Why signals:**
- Multi-step workflow with external calls → orchestration engine / saga
- Instant decision → pre-compute what you can, parallel calls to bureaus
- External dependency (3 bureaus) → circuit breakers, fallback, retry
- Regulatory compliance → audit trail, adverse action generation, data retention
- Risk scoring → ML model + rules, model versioning, explainability
- Card issuance → async manufacturing and shipping, not instant

**Core pattern:** Orchestrated workflow with parallel external calls (3 bureaus simultaneously), ML risk scoring, and async card issuance. Event-driven for the slow path (manufacturing, shipping). Synchronous for the fast path (decision in < 5s).

## 3. High-Level Architecture

```
Customer App / Website
     |
     v
[API Gateway] --- auth, rate limit, TLS
     |
     v
[Application Service] --- orchestrates the flow
     |
     +---> [Bureau Service] (parallel calls, 2s timeout each)
     |       +---> Experian API
     |       +---> Equifax API
     |       +---> TransUnion API
     |       returns: 3 bureau reports + FICO scores
     |
     +---> [Risk Scoring Service] (ML model + rules)
     |       inputs: app data, bureau data, internal history
     |       returns: score, decision (approve/deny/pending), reasons
     |
     +---> [Decision Service] --- combines bureau + risk + policy
     |       returns: final decision, credit limit, APR
     |
     v
[Kafka] --- application.decided event
     |
     +---> [Card Issuance Service] (async: generate number, manufacture, ship)
     +---> [Adverse Action Service] (if denied: generate FCRA notice, mail)
     +---> [Notification Service] (SMS/email: "You're approved!")
     +---> [CRM Service] (update customer record)
     +---> [Analytics Service] (conversion funnel, approval rate)

  Stores:
  - Application DB (PostgreSQL, sharded by app_id)
  - Bureau Cache (Redis, 24h TTL, soft pull reuse)
  - Risk Model Registry (MLflow)
  - Card Vault (HSM-protected, PCI-DSS)
  - Document Store (S3, adverse action notices, 25-month retention)
```

## 4. How to Think About It

**Q1: What is the critical path?**
Customer is waiting for a decision. The 5-second budget: bureau pulls (2s parallel), risk scoring (1s), decision logic (0.5s), DB write (0.5s), notification (0.5s). Bureau calls are the bottleneck, so call all 3 in parallel.

**Q2: Soft pull vs hard pull?**
Soft pull (pre-qualification): does not affect credit score, cached for 24h. Hard pull (formal application): affects credit score, fresh data. Pre-qual uses soft pull to show "you're pre-approved." Formal app uses hard pull for the actual decision.

**Q3: What if a bureau is down?**
If one bureau is down, use the other two. If all three are down, either: (a) pending decision (defer until bureaus recover), or (b) use cached data if available. Hard pull cannot be skipped (regulatory). Circuit breaker per bureau. Fallback to pending.

**Q4: → What about adverse action?**
If denied, FCRA requires an adverse action notice within 30 days. It must state the reasons and the bureau data used. The system generates the notice automatically, stores it for 25 months, and mails it (physical or electronic). This is a regulatory requirement, not optional.

## 5. Real-World Analogy

Think of a **loan officer at a bank branch**. You walk in, fill out an application. The officer calls three references (credit bureaus) in parallel to get your history. While waiting, they check their own records (internal history). When the references come back, the officer scores you (risk model) and makes a decision.

If approved, the officer says "congratulations" and starts the card manufacturing process (which takes days). If denied, they hand you a letter explaining why (adverse action notice). The letter is a legal requirement.

The 5-second budget is like the customer standing at the counter. They will not wait 30 seconds. The officer must be fast: parallel calls, pre-computed scores, instant decision. The slow stuff (manufacturing, mailing) happens in the back office after the customer leaves.

## 6. Build Your Intuition

**Q: Why call all 3 bureaus in parallel?**
Each bureau call takes 1-2 seconds. Sequential: 6 seconds (too slow). Parallel: 2 seconds (within budget). Different bureaus have different data, so you need all 3 for an accurate score. The slowest bureau determines the total time.

**Q: Why not cache bureau data permanently?**
Credit data changes daily. A hard pull must be fresh (regulatory). Soft pulls can be cached for 24h (pre-qualification). Caching a hard pull would violate FCRA. The cache is only for soft pulls and pre-qualification flows.

**Q: How does the risk model work?**
Inputs: application data (income, employment), bureau data (FICO, utilization, inquiries, delinquencies), internal history (existing Capital One accounts). Model: gradient boosted trees (XGBoost). Output: probability of default. Threshold: below X% = approve, above Y% = deny, between = pending (manual review).

**Q: What is adverse action and why does it matter?**
FCRA requires that if you deny credit based on bureau data, you must tell the customer: (1) that bureau data was used, (2) which bureau, (3) the main reasons for denial. This is the adverse action notice. Non-compliance is a regulatory violation with fines. The system generates it automatically.

## 7. How It Works (Step by Step)

- **Step 1:** Customer submits application via app/website. API Gateway authenticates, rate-limits, routes to Application Service.
- **Step 2:** Application Service validates input (SSN format, income > 0, etc.). Creates application record with status=RECEIVED.
- **Step 3:** Bureau Service calls Experian, Equifax, TransUnion in parallel (2s timeout each). Returns 3 bureau reports with FICO scores. If one fails, use the other two.
- **Step 4:** Risk Scoring Service fetches internal history (existing accounts, past delinquencies). Runs ML model with all features. Returns risk score and top factors.
- **Step 5:** Decision Service applies policy rules: if score < X and FICO > 680, APPROVE with limit $Y. If score > Z, DENY. Else, PENDING (manual review).
- **Step 6:** Application Service writes decision to DB. Publishes application.decided event to Kafka. Returns decision to customer. Total: 3-5 seconds.
- **Step 7:** Async (APPROVED): Card Issuance Service generates card number (HSM), creates card record, orders physical card manufacturing. Ships in 7-10 days.
- **Step 8:** Async (DENIED): Adverse Action Service generates FCRA notice with reasons and bureau info. Mails to customer within 30 days. Stores for 25 months.
- **Step 9:** Async (all): Notification Service sends SMS/email. CRM updates customer record. Analytics tracks conversion funnel.

## 8. Data Model

**Application (PostgreSQL, sharded by app_id):**
```
applications:
  app_id          UUID PK
  customer_id     VARCHAR
  product_id      VARCHAR  -- which card product (Quicksilver, Venture, etc.)
  status          ENUM(received, pending, approved, denied, cancelled)
  personal_info   JSONB  -- name, DOB, SSN (encrypted), address
  financial_info  JSONB  -- income, employment, housing
  bureau_reports  JSONB  -- 3 bureau responses
  risk_score      DECIMAL
  risk_factors    JSONB  -- top SHAP features
  decision        VARCHAR
  credit_limit    DECIMAL NULL
  apr             DECIMAL NULL
  created_at      TIMESTAMP
  decided_at      TIMESTAMP NULL
```

**Bureau Cache (Redis, 24h TTL, soft pulls only):**
```
bureau_cache:soft:{customer_id} = {
  experian: JSON,
  equifax: JSON,
  transunion: JSON,
  pulled_at: TIMESTAMP
}
TTL: 24 hours
```

**Adverse Action Notice (S3 + PostgreSQL index):**
```
adverse_actions:
  notice_id       UUID PK
  app_id          UUID
  customer_id     VARCHAR
  reasons         JSONB  -- ["high_utilization", "recent_inquiries"]
  bureaus_used    JSONB  -- ["Experian", "Equifax"]
  document_url    VARCHAR  -- S3 URL to PDF
  mailed_at       TIMESTAMP NULL
  retention_until TIMESTAMP  -- created_at + 25 months
```

**Card (HSM Vault + PostgreSQL metadata):**
```
cards:
  card_id         UUID PK
  app_id          UUID
  customer_id     VARCHAR
  card_token      VARCHAR  -- tokenized PAN
  last4           CHAR(4)
  product_id      VARCHAR
  credit_limit    DECIMAL
  apr             DECIMAL
  status          ENUM(issued, activated, closed)
  manufactured_at TIMESTAMP NULL
  shipped_at      TIMESTAMP NULL
  activated_at    TIMESTAMP NULL
```

## 9. Scalability Deep Dive

**Throughput:** 100K apps/day, 1K/sec peak. Application Service: stateless, 20 pods. Bureau Service: 15 pods (I/O bound, waiting on bureau APIs). Risk Scoring: 10 pods with model in memory. Kafka: 3 brokers, 12 partitions.

**Latency:** p99 < 5s. Gateway 100ms, validation 200ms, bureau pull 2000ms (parallel), risk scoring 1000ms, decision 500ms, DB write 500ms, Kafka publish 100ms. Total: 4.4s. Buffer for tail latency.

**Bureau API Rate Limits:** Bureaus enforce rate limits (e.g., 100 req/sec per client). Bureau Service manages a token bucket per bureau. Queue excess requests. For peak campaigns, pre-negotiate higher limits. Cache soft pulls to reduce volume.

**Card Vault (HSM):** Card numbers generated in Hardware Security Module (HSM). Never exposed outside HSM. Tokenized immediately. HSM throughput: 100 cards/sec. Sufficient for 100K/day. For spikes, queue card generation.

## 10. Failure Modes & Resilience

- **One Bureau Down:** If Experian is down, use Equifax and TransUnion. The risk model works with 2 bureaus (slightly less accurate). Circuit breaker per bureau. Log the missing bureau for compliance. If all 3 are down, defer to PENDING.
- **All Bureaus Down:** Cannot make a credit decision without bureau data (FCRA). Set application to PENDING. Queue for retry when bureaus recover. Notify customer: "We need more time to review your application." Do not deny without bureau data.
- **Risk Scoring Service Down:** Fall back to rules-based decision: FICO > 720 and income > $50K = APPROVE. FICO < 600 = DENY. Else PENDING. Less accurate but functional. Circuit breaker on ML service.
- **HSM (Card Vault) Down:** Cannot generate card numbers. APPROVED applications queue for card issuance. When HSM recovers, drain the queue. Customer is notified of delay. No application is lost.
- **Kafka Down:** Decision still works (sync path). Async consumers (card issuance, notification, adverse action) are blocked. Buffer events in Application Service. When Kafka recovers, flush. Critical async jobs (adverse action) have a fallback queue.

## 11. Edge Cases & Gotchas

- **Duplicate application:** Customer submits twice (double-click) or applies for multiple cards. Check for existing application with same SSN in last 30 days. If found, return the existing decision. Do not pull bureau twice (FCRA: one hard pull per application).
- **Fraudulent application (identity theft):** Someone applies using stolen SSN. Fraud detection on applications: velocity (multiple apps from same IP), device fingerprinting, address mismatch. If flagged, PENDING for manual review. Do not deny automatically.
- **Existing customer applying for second card:** Customer already has a Capital One card. Internal history is rich: payment behavior, utilization, account age. The risk model weights internal data heavily. May approve with better terms. Or deny if existing account is delinquent.
- **Thin file (no credit history):** Young adult or new immigrant with no bureau data. FICO cannot be computed. Use alternative data: utility payments, rent history, employment. Capital One's CreditWise program handles this. May require manual review or secured card product.
- **Fair lending (ECOA) compliance:** Cannot discriminate on protected classes (race, gender, age, marital status). Model must not use these features or proxies (zip code can proxy for race). Regular fair lending audits. Adverse action reasons must be specific and actionable.

## 12. Flashcards

**Q1: Why call bureaus in parallel?**
Each bureau call takes 1-2s. Sequential: 6s (exceeds 5s budget). Parallel: 2s (within budget). The slowest bureau determines total time. All 3 are needed for an accurate score.

**Q2: What is an adverse action notice?**
FCRA-required notice sent to denied applicants. Must state: bureau data was used, which bureaus, and the main reasons for denial. Generated automatically. Mailed within 30 days. Retained for 25 months. Non-compliance = fines.

**Q3: Soft pull vs hard pull?**
Soft pull: pre-qualification, does not affect credit score, cached 24h. Hard pull: formal application, affects credit score, must be fresh. FCRA regulates both. Hard pull cannot be cached or skipped.

**Q4: How do you ensure fair lending?**
No protected class features (race, gender, age). No proxies (zip code). Regular fair lending audits. Monitor approval rates by demographic. Explainable model (SHAP). ECOA compliance. Adverse action reasons must be specific.

**Q5: How do you handle card issuance?**
HSM generates card number. Tokenized immediately. Physical card manufactured (1-2 days), shipped (7-10 days). Customer activates via app or phone. Virtual card number available instantly in app for online use while waiting for physical card.

## 13. Where It Is Used (Real World)

- **Capital One:** Processes millions of credit card applications per year. Pre-qualification (soft pull) on their website. Instant decision on formal application.
- **Chase, Amex, Discover:** All major card issuers use a similar architecture. Bureau integration, risk scoring, instant decision, card issuance.
- **Fintech Card Issuers (Mercury, Brex, Ramp):** Modern fintech card issuers use similar patterns but with modern stack: Kafka, Kubernetes, MLflow. They often use card-issuing-as-a-service (Marqeta, Stripe Issuing) for the HSM and manufacturing.
- **Mortgage and Auto Loan Applications:** Same pattern: application, bureau pull, risk scoring, decision. Different: larger amounts, longer terms, more documentation. The architecture is reusable across credit products.

## 14. Common Mistakes

- Sequential bureau calls. 6 seconds, exceeds budget. Always parallel.
- No adverse action automation. Manual generation is non-compliant. Must be automatic and within 30 days.
- Caching hard pulls. FCRA violation. Hard pulls must be fresh. Only soft pulls can be cached.
- No duplicate application check. Double hard pull from double-click. Check existing applications first.
- Storing raw SSN. Encrypt at rest. Tokenize. PCI-DSS and FCRA compliance.
- No fair lending audit. Model bias can lead to regulatory action. Monitor approval rates by demographic.
- Synchronous card manufacturing. Takes days. Must be async. Customer gets instant decision, card arrives later.
- No bureau rate limit handling. Bureaus enforce limits. Token bucket per bureau. Queue excess.

## 15. Interview Tips

- Start with the 5-second budget. "Customer is waiting. Bureau calls are 2s, scoring 1s, decision 0.5s. I will parallelize bureau calls."
- Discuss soft vs hard pull. Shows FCRA knowledge. Pre-qual uses soft, formal uses hard. Cache soft, never cache hard.
- Mention adverse action early. FCRA requirement. Automatic generation. 30-day window. 25-month retention. Regulatory knowledge.
- Discuss bureau failure handling. One down: use other two. All down: PENDING. Circuit breakers. Never deny without bureau data.
- Mention fair lending (ECOA). No protected classes. No proxies. Regular audits. Shows regulatory depth.
- Separate sync (decision) from async (issuance). Customer gets instant decision. Card manufacturing is async. This is the key architectural split.
- Discuss HSM for card numbers. PCI-DSS. Tokenization. Never expose PAN. Shows security knowledge.
- Mention duplicate application check. Prevents double hard pull. FCRA compliance. Customer experience.

## 16. Related System Design Problems

- **Loan Application System** — same pattern for mortgages, auto loans — CORE
- **Multi-Step Workflow with External APIs** — orchestration pattern — CORE
- **Identity Verification System** — KYC/AML, bureau integration — SIMILAR
- **Insurance Underwriting** — risk scoring, external data, decision — SIMILAR
- **Account Opening (KYC/AML)** — compliance-heavy onboarding — ADVANCED

## 17. Key Technologies

- **PostgreSQL** — application data, ACID, JSONB for bureau reports
- **Redis** — soft pull cache, rate limiting tokens
- **Kafka** — event backbone for async consumers
- **XGBoost** — risk scoring model
- **MLflow** — model registry, versioning
- **HSM (Thales/Gemalto)** — card number generation, PCI-DSS
- **S3** — adverse action notices, document storage
- **Bureau APIs** — Experian, Equifax, TransUnion integration

## 18. Trade-Offs

- **Speed vs Accuracy:** A more complex model is more accurate but slower. 5s budget. Use XGBoost (1s) instead of a deep neural network (3s). The accuracy difference is small for this use case.
- **2 Bureaus vs 3 Bureaus:** If one bureau is slow, do you wait or proceed with 2? Proceeding is faster but less accurate. Compromise: 2s timeout per bureau. If one times out, proceed with the other two.
- **Instant vs Pending:** Instant decision is better UX but riskier. Pending is safer but slower. Use instant for clear Approve/Deny, pending for borderline. Manual review for pending cases within 24h.
- **Physical vs Virtual Card:** Physical card takes 7-10 days. Virtual card is instant. Offer both: virtual for immediate use, physical for in-store.
- **Model Explainability vs Accuracy:** A complex model is more accurate but harder to explain (adverse action reasons). XGBoost with SHAP gives both. Deep learning would be more accurate but less explainable. Regulatory requirement for explainability.

## 19. Monitoring & Compliance

- **Business Metrics:** Approval rate, denial rate, pending rate, conversion funnel, average credit limit, average APR, time-to-decision. Dashboard for product team.
- **System Metrics:** Application latency p99, bureau API latency, bureau error rate, risk scoring time, DB write time, Kafka lag. Alert on SLO breaches.
- **Fair Lending Monitoring:** Approval rate by demographic (inferred from address, not explicitly collected). If one group has significantly lower approval rate, investigate. Regular fair lending audits by compliance team. ECOA compliance.
- **Regulatory Reporting:** Monthly: application statistics to OCC. Adverse action notice audit (all denied apps have notices within 30 days). FCRA compliance audit. Data retention check (25 months for adverse action, 7 years for applications).
- **Model Monitoring:** Model performance: approval rate drift, default rate of approved customers, feature drift. If model approves riskier customers over time, retrain. A/B test new models. SR 11-7 model risk management compliance.

## 20. Follow-Up Questions

**Q: How would you handle pre-qualification (soft pull) at scale?**
Marketing campaigns drive millions of pre-qual checks. Soft pull, cached 24h. If a customer pre-quals, show "you're pre-approved for Venture X." When they apply formally, the hard pull confirms. The cache reduces bureau volume by 80% during campaigns.

**Q: How would you handle instant virtual card issuance?**
On approval, HSM generates a virtual card number instantly. Push to customer's app. They can use it online immediately. Physical card arrives in 7-10 days. This reduces drop-off and is a competitive feature.

**Q: How would you handle A/B testing of risk models?**
Route 5% of applications to the challenger model. Compare approval rate, default rate (over 6 months), and revenue. If challenger is better, promote to 100%. MLflow for model versioning. Shadow mode: run both models, compare decisions without using the challenger's decision.

**Q: How would you handle applications from existing customers?**
Rich internal data: payment history, utilization, account age. Skip bureau pull if internal data is sufficient (saves cost and time). Pre-fill application from existing profile. Offer better terms for loyal customers. Deny if existing account is delinquent.

**Q: How would you handle a marketing campaign that drives 10x traffic?**
Pre-negotiate higher bureau rate limits. Pre-provision Application Service pods. Kafka buffers the spike. For soft pulls, the 24h cache absorbs most of the load. For hard pulls, queue if bureau rate limit is hit. Customer sees "processing" and gets decision in minutes instead of seconds.

## 21. Quick Reference

| Aspect | Value |
|--------|-------|
| **Architecture** | Orchestrated workflow, parallel bureau calls, sync decision + async issuance |
| **Scale** | 100K apps/day, 1K/sec peak, p99 < 5s, 99.9% availability |
| **Key Patterns** | Parallel external calls, ML risk scoring, adverse action automation, HSM card issuance |
| **Compliance** | FCRA (adverse action), ECOA (fair lending), OCC (banking), PCI-DSS (card data) |
| **Data Stores** | PostgreSQL (apps), Redis (soft pull cache), HSM (cards), S3 (notices) |
| **Senior Signal** | Soft vs hard pull, adverse action, fair lending, HSM, bureau failure handling |

**Key decisions:**
```
1. Parallel bureau calls (2s vs 6s sequential)
2. Soft pull cache (24h) vs hard pull (fresh, no cache)
3. Sync decision (5s) + async card issuance (7-10 days)
4. Adverse action automation (FCRA, 30 days, 25-month retention)
5. HSM for card numbers (PCI-DSS, tokenization)
6. ML risk scoring + rules fallback
7. Fair lending monitoring (ECOA, no proxies)
8. Bureau failure: 2 of 3 is OK, all 3 down = PENDING
```
