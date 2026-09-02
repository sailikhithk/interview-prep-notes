# Payment Validation & Duplicate Prevention

**Difficulty:** MEDIUM · **Context:** Capital One GPN · Senior Lead SWE
**Pattern:** HashSet + Rule Chain · **Time:** O(n) · **Space:** O(n) · **Language:** Java / Python

You are joining the Global Payment Network team as a Senior Lead Software Engineer. The platform processes payment transactions from multiple merchants, card networks, and internal services. Build a transaction validation component that detects invalid transactions, prevents duplicate processing, and produces auditable validation results.

## 1. Problem Statement

Approve a transaction only if ALL of:
1. Transaction ID is not duplicated
2. Amount is greater than zero
3. Currency is supported
4. Merchant is active
5. Account/card is active
6. Timestamp is present
7. Required fields are not missing

**Sample Input:**
```
Supported currencies: USD, CAD
Active merchants: M100, M200
Active accounts: A100, A200, A300

1. T001, A100, M100, 120.50, USD
2. T002, A200, M100, 0.00, USD
3. T003, A300, M999, 75.00, USD
4. T001, A100, M100, 120.50, USD  (duplicate)
5. T004, A999, M200, 20.00, CAD
6. T005, A100, M200, 10.00, EUR
```

**Expected Output:**
```
T001 -> APPROVED, VALID
T002 -> DECLINED, INVALID_AMOUNT
T003 -> DECLINED, INACTIVE_MERCHANT
T001 -> DECLINED, DUPLICATE_TRANSACTION
T004 -> DECLINED, INACTIVE_ACCOUNT
T005 -> DECLINED, UNSUPPORTED_CURRENCY
```

## 2. Pattern Recognition

**Why signals:**
- Need to detect duplicates across a stream of items
- Multiple independent validation rules applied in sequence
- Each item gets a pass/fail with a reason code
- Single pass through the list is sufficient

**Core pattern:** HashSet for duplicate detection + sequential rule chain for validation. O(n) single pass, O(n) space for the dedup set.

## 3. Pattern Blueprint

5-step template for HashSet + Rule Chain:
1. Initialize a HashSet to track seen transaction IDs
2. For each transaction, check null/missing fields first (fail fast)
3. Attempt to add transaction ID to set; if add returns false, it is a duplicate
4. Apply remaining validation rules in order (amount, currency, merchant, account, timestamp)
5. Return APPROVED only if all rules pass; otherwise return DECLINED with the first failing reason code

## 4. How to Think About It

**Q1: What data do I need to track across transactions?**
Only the transaction IDs I have already seen. That is a Set. HashSet gives O(1) add and contains.

**Q2: What is the validation order?**
Fail fast. Check missing fields first (cheapest), then duplicate, then business rules. The order matters for reason code clarity.

**Q3: Should I return all failure reasons or just the first?**
Clarify with the interviewer. Default: first failure. Production: may want all reasons for audit. State both options.

**Q4: → How does this scale to production?**
In-memory HashSet only works for a single instance. Production needs a shared idempotency store (Redis SETNX or DB unique constraint) so multiple pods do not double-process.

## 5. Real-World Analogy

Think of a **bouncer at a club with a guest list**. Each person (transaction) walks up. The bouncer checks:
1. Is the person on the guest list? (missing fields check)
2. Have I already let this person in? (duplicate check, HashSet is the stamp on the hand)
3. Are they old enough? (amount > 0)
4. Is this club open tonight? (currency supported)
5. Is this person banned? (merchant/account active)

The bouncer stamps your hand the first time. If you come back with the same name, the stamp is already there, you get turned away as a duplicate. The stamp book is the HashSet. In production, there are multiple bouncers at multiple doors, so the stamp book needs to be shared (Redis).

## 6. Build Your Intuition

**Q: Why HashSet and not a List?**
List.contains() is O(n). HashSet.contains() and add() are O(1) average. For 1M transactions, that is the difference between 1M and 1 trillion operations.

**Q: Why check duplicate before other business rules?**
If the same transaction ID arrives twice, the second one is a duplicate regardless of whether the first was approved or declined. The duplicate check is about idempotency, not business validity.

**Q: Why use BigDecimal instead of double for amount?**
double has floating-point precision errors. 0.1 + 0.2 != 0.3 in double. BigDecimal gives exact decimal representation, critical for payment/ledger/settlement systems.

## 7. How It Works (Step by Step)

- **Step 1:** Create empty HashSet `processedTransactionIds`. Create empty results list.
- **Step 2:** For each transaction in input list, call `validateTransaction`.
- **Step 3:** Check null or blank fields (transactionId, accountId, merchantId, currency). If any blank, return MISSING_REQUIRED_FIELD.
- **Step 4:** Try `processedTransactionIds.add(transactionId)`. If returns false, return DUPLICATE_TRANSACTION.
- **Step 5:** Check amount null or ≤ 0. If so, return INVALID_AMOUNT.
- **Step 6:** Check currency not in supportedCurrencies set. If not, return UNSUPPORTED_CURRENCY.
- **Step 7:** Check merchant not in activeMerchants. If not, return INACTIVE_MERCHANT.
- **Step 8:** Check account not in activeAccounts. If not, return INACTIVE_ACCOUNT.
- **Step 9:** Check timestamp null. If so, return MISSING_TIMESTAMP.
- **Step 10:** All checks passed. Return APPROVED, VALID. Add result to results list.

## 8. Dry Run Table

| Txn | ID | Acct | Merch | Amt | Curr | Set state | Result |
|-----|----|----|-------|-----|------|-----------|--------|
| 1 | T001 | A100 | M100 | 120.50 | USD | {T001} | APPROVED |
| 2 | T002 | A200 | M100 | 0.00 | USD | {T001,T002} | INVALID_AMOUNT |
| 3 | T003 | A300 | M999 | 75.00 | USD | {T001,T002,T003} | INACTIVE_MERCHANT |
| 4 | T001 | A100 | M100 | 120.50 | USD | add returns false | DUPLICATE |
| 5 | T004 | A999 | M200 | 20.00 | CAD | {..T004} | INACTIVE_ACCOUNT |
| 6 | T005 | A100 | M200 | 10.00 | EUR | {..T005} | UNSUPPORTED_CURRENCY |

## 9. Complexity Deep Dive

**Time: O(n)** — Single pass through n transactions. Each transaction does O(1) work: HashSet.add() is O(1) average, Set.contains() for currency/merchant/account is O(1). Worst case: HashSet degenerates to O(log n) per operation if many hash collisions (Java 8+ uses balanced tree in buckets with >8 collisions). Still O(n log n) worst case, but extremely rare with good hash distribution.

**Space: O(n)** — The HashSet stores up to n unique transaction IDs. The results list stores n ValidationResult objects. Reference data sets are O(k), typically small and constant. Production: the idempotency store grows unbounded. Add TTL or time-windowed eviction (e.g., keep 24h of transaction IDs, archive older to cold storage for audit).

## 10. From Brute Force to Optimal

**Naive: Nested Loop Dedup** — O(n²) time, O(1) extra space. For 1M transactions, 1 trillion comparisons. Unusable at payment scale.

**Optimal: HashSet Dedup** — O(n) time, O(n) space. For 1M transactions, 1M O(1) operations. **1 million times faster** at scale.

## 11. Edge Cases & Gotchas

- **Duplicate ID with different amount:** Suspicious. Same ID but different amount or merchant could indicate a bug or fraud. Compare incoming with original. If mismatch, route to exception queue or fraud review.
- **Lowercase currency "usd" vs "USD":** Normalize to uppercase before set lookup. `currency.toUpperCase()`.
- **Null timestamp vs future timestamp:** Null is MISSING_TIMESTAMP. Future timestamp may be valid (pre-authorization) or invalid. Default: reject future timestamps beyond a small clock-skew tolerance (e.g., 5 minutes).
- **Concurrent processing across instances:** In-memory HashSet is not shared across pods. Two pods can both add the same ID and both approve. Production: use Redis SETNX or DB unique constraint with atomic insert.

## 12. Flashcards

**Q1: What is the time and space complexity?**
Time O(n), Space O(n). Single pass with HashSet for dedup. The HashSet stores up to n unique IDs.

**Q2: Why does HashSet.add() return false for duplicates?**
Set semantics reject duplicates. add() returns true if the element was added (not already present), false if it was already in the set. This is a single atomic O(1) check-and-add.

**Q3: Why use BigDecimal instead of double for amount?**
double has floating-point precision errors (0.1 + 0.2 != 0.3). BigDecimal gives exact decimal representation, critical for payment/ledger/settlement. Never use double or float for money.

**Q4: How do you make this thread-safe for production?**
In-memory HashSet is not shared across pods. Use Redis SETNX (atomic set-if-not-exists) or a DB unique constraint on transaction_id. The check-and-add must be a single atomic operation.

**Q5: What happens if audit write fails after approval?**
For payment systems, audit failure is serious. Keep validation result and audit write in the same transaction boundary. If not possible, use the outbox pattern so the audit event is reliably persisted and published later.

## 13. Where It Is Used (Real World)

- **Payment Gateways (Stripe, Adyen, Square):** Every payment API accepts an idempotency key. The gateway stores it in a dedup store. Retried requests with the same key return the original result, never double-charge.
- **Bank Transaction Processing (Capital One GPN, JPMorgan):** Transaction validation pipelines check account status, merchant status, currency support, and duplicate detection before authorizing. Audit trail for every decision including declines.
- **Order Management Systems (Amazon, Shopify):** Order ID dedup prevents double-fulfillment when buyers retry checkout.
- **Kafka Consumer Idempotency:** Kafka provides at-least-once delivery. Consumers must be idempotent. Dedup store keyed by topic+partition+offset or by business-level idempotency key.

## 14. Common Mistakes

- Using double for amount. Use BigDecimal in Java, Decimal in Python, or integer cents.
- Checking duplicate after business rules. If the first transaction was declined for INVALID_AMOUNT, the duplicate check never fires. Always check duplicate first (after missing fields).
- Not normalizing currency. "usd" vs "USD" vs "Usd" all fail set lookup.
- Using List.contains() for dedup. O(n) per check, O(n²) total. Use HashSet for O(1).
- Not handling null transaction. Null check must be first.
- Returning all failure reasons instead of first. Clarify with interviewer.
- Not discussing production hardening. Senior interview expects idempotency, thread safety, audit, reconciliation discussion after the coding solution.

## 15. Interview Tips

- Open with clarification. "Before I code, I want to clarify the validation rules and edge cases. Since this is a payment system, I will also consider idempotency, auditability, retry behavior, and reconciliation."
- State the pattern before coding. "I will use a HashSet for O(1) duplicate detection and a sequential rule chain for validation. This gives O(n) time and O(n) space."
- Code brute force first if optimal is not immediately clear. Then optimize.
- Use helper functions. `isBlank()`, `decline()` keep the main loop clean.
- Walk through the example. After coding, trace through the sample input/output to verify.
- State complexity explicitly. "Time O(n), space O(n)."
- Pivot to production. After the coding solution, proactively discuss: idempotency store (Redis SETNX), audit table, Kafka topics, DLQ, reconciliation. This is the senior-level signal.
- Use BigDecimal, not double. If the interviewer asks why, explain floating-point precision. This is a payments domain signal.

## 16. Similar Problems to Practice

- **Contains Duplicate** (LeetCode 217) — EASY
- **Contains Duplicate II** (LeetCode 219) — HashSet + sliding window — EASY
- **Design a Bank System** (LeetCode 2043) — OOP, state validation — MEDIUM
- **Validate Credit Card Number** (Luhn algorithm) — MEDIUM
- **Design Transaction Limit System** — rate limiting + dedup — HARD

## 17. Related Algorithms

- **HashSet / HashMap** — O(1) lookup and insertion for dedup and counting
- **Bloom Filter** — probabilistic dedup for massive scale, false positives but no false negatives
- **Rule Chain / Chain of Responsibility** — sequential validation pattern
- **Idempotency Key Pattern** — distributed dedup using Redis SETNX or DB unique constraint
- **Outbox Pattern** — reliable event publishing with DB transaction
- **Luhn Algorithm** — credit card number validation checksum

## 18. Where This Pattern Meets System Design

- **In-memory HashSet → Distributed Idempotency Store:** Production uses Redis SETNX or a DB unique constraint. The check-and-add must be atomic across all instances.
- **Rule Chain → Microservice Validation Pipeline:** Each validation rule can be a separate service: fraud check, account service, merchant service, currency service. Orchestrate via synchronous calls or a streaming pipeline with Kafka.
- **Results List → Audit Table + Kafka Topics:** Every validation result (approved and declined) writes to an immutable audit table. Approved and declined events publish to separate Kafka topics for downstream authorization, ledger, and reconciliation.
- **Single Pass → Streaming Consumer:** The for-loop becomes a Kafka consumer. Partition by account_id or transaction_id for ordering. Commit offset only after validation result and audit write succeed (at-least-once + idempotent consumer = effectively once).
- **Reason Codes → Observability + Reconciliation:** Reason codes feed dashboards (decline rate by reason), alerts (spike in INACTIVE_MERCHANT), and reconciliation (compare internal decisions to external network settlement files).

## 19. Code Solutions

### Java

```java
import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

public record Transaction(
    String transactionId, String accountId, String merchantId,
    BigDecimal amount, String currency, Instant timestamp
) {}

public enum TransactionStatus { APPROVED, DECLINED }
public enum ReasonCode {
    VALID, MISSING_REQUIRED_FIELD, DUPLICATE_TRANSACTION, INVALID_AMOUNT,
    UNSUPPORTED_CURRENCY, INACTIVE_MERCHANT, INACTIVE_ACCOUNT, MISSING_TIMESTAMP
}
public record ValidationResult(String transactionId, TransactionStatus status, ReasonCode reasonCode) {}

public class PaymentValidationService {
    public List<ValidationResult> validateTransactions(
        List<Transaction> transactions,
        Set<String> activeAccounts,
        Set<String> activeMerchants,
        Set<String> supportedCurrencies
    ) {
        List<ValidationResult> results = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        for (Transaction t : transactions) {
            results.add(validate(t, seen, activeAccounts, activeMerchants, supportedCurrencies));
        }
        return results;
    }

    private ValidationResult validate(Transaction t, Set<String> seen,
            Set<String> accounts, Set<String> merchants, Set<String> currencies) {
        if (t == null) return decline(null, ReasonCode.MISSING_REQUIRED_FIELD);
        if (isBlank(t.transactionId()) || isBlank(t.accountId())
            || isBlank(t.merchantId()) || isBlank(t.currency()))
            return decline(t.transactionId(), ReasonCode.MISSING_REQUIRED_FIELD);
        if (!seen.add(t.transactionId()))
            return decline(t.transactionId(), ReasonCode.DUPLICATE_TRANSACTION);
        if (t.amount() == null || t.amount().compareTo(BigDecimal.ZERO) <= 0)
            return decline(t.transactionId(), ReasonCode.INVALID_AMOUNT);
        if (!currencies.contains(t.currency().toUpperCase()))
            return decline(t.transactionId(), ReasonCode.UNSUPPORTED_CURRENCY);
        if (!merchants.contains(t.merchantId()))
            return decline(t.transactionId(), ReasonCode.INACTIVE_MERCHANT);
        if (!accounts.contains(t.accountId()))
            return decline(t.transactionId(), ReasonCode.INACTIVE_ACCOUNT);
        if (t.timestamp() == null)
            return decline(t.transactionId(), ReasonCode.MISSING_TIMESTAMP);
        return new ValidationResult(t.transactionId(), TransactionStatus.APPROVED, ReasonCode.VALID);
    }

    private ValidationResult decline(String id, ReasonCode rc) {
        return new ValidationResult(id, TransactionStatus.DECLINED, rc);
    }
    private boolean isBlank(String s) { return s == null || s.trim().isEmpty(); }
}
```

### Python

```python
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionStatus(Enum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"

class ReasonCode(Enum):
    VALID = "VALID"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    UNSUPPORTED_CURRENCY = "UNSUPPORTED_CURRENCY"
    INACTIVE_MERCHANT = "INACTIVE_MERCHANT"
    INACTIVE_ACCOUNT = "INACTIVE_ACCOUNT"
    MISSING_TIMESTAMP = "MISSING_TIMESTAMP"

@dataclass
class Transaction:
    transaction_id: str
    account_id: str
    merchant_id: str
    amount: Decimal
    currency: str
    timestamp: Optional[datetime] = None

@dataclass
class ValidationResult:
    transaction_id: str
    status: TransactionStatus
    reason_code: ReasonCode

def validate_transactions(transactions, active_accounts, active_merchants, supported_currencies):
    results = []
    seen = set()
    for t in transactions:
        results.append(_validate(t, seen, active_accounts, active_merchants, supported_currencies))
    return results

def _validate(t, seen, accounts, merchants, currencies):
    if t is None:
        return ValidationResult(None, TransactionStatus.DECLINED, ReasonCode.MISSING_REQUIRED_FIELD)
    if not all([t.transaction_id, t.account_id, t.merchant_id, t.currency]):
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.MISSING_REQUIRED_FIELD)
    if t.transaction_id in seen:
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.DUPLICATE_TRANSACTION)
    seen.add(t.transaction_id)
    if t.amount is None or t.amount <= Decimal("0"):
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.INVALID_AMOUNT)
    if t.currency.upper() not in currencies:
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.UNSUPPORTED_CURRENCY)
    if t.merchant_id not in merchants:
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.INACTIVE_MERCHANT)
    if t.account_id not in accounts:
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.INACTIVE_ACCOUNT)
    if t.timestamp is None:
        return ValidationResult(t.transaction_id, TransactionStatus.DECLINED, ReasonCode.MISSING_TIMESTAMP)
    return ValidationResult(t.transaction_id, TransactionStatus.APPROVED, ReasonCode.VALID)
```

## 20. Follow-Up Questions

**Q: How would you handle duplicate transaction IDs with different amounts?**
Suspicious. Compare incoming with original. If ID same but amount or merchant differs, mark as integrity issue, send to exception queue or fraud/risk review. Do not silently treat as normal duplicate.

**Q: What happens if the audit write fails after approval?**
For payment systems, audit failure is serious. Keep validation result and audit write in the same transaction boundary. If not possible, use the outbox pattern so the audit event is reliably persisted and published later.

**Q: How would you make this scalable to 10K TPS?**
Stateless validation service, horizontally scalable. Shared state (idempotency, merchant/account status, audit) stored externally in Redis or DB. Kafka partitions keyed by transaction ID or account ID for ordering. Metrics and tracing for visibility.

**Q: How do you reconcile internal records with external network settlement files?**
Daily batch job compares internal ledger to external settlement file. Check: internal but not external, external but not internal, amount mismatch, currency mismatch, status mismatch, settlement date mismatch. Exceptions go to a reconciliation queue for ops review.

**Q: How do you handle Kafka redelivery?**
Kafka provides at-least-once delivery. The consumer must be idempotent. Commit the Kafka offset only after the validation result and audit record are successfully written. The idempotency store ensures redelivered messages do not double-process.

## 21. Quick Reference

| Aspect | Value |
|--------|-------|
| **Pattern** | HashSet + Rule Chain |
| **Complexity** | Time O(n), Space O(n) |
| **Key Data Structures** | HashSet (dedup), Set (reference data), BigDecimal (amount) |
| **Validation Order** | null → missing fields → duplicate → amount → currency → merchant → account → timestamp |
| **Production Hardening** | Redis SETNX, audit table, Kafka topics, DLQ, reconciliation |
| **Senior Signal** | Pivot from coding to production: idempotency, thread safety, audit, reconciliation |

**Core code shape:**
```
Set seen = new HashSet()
for (Transaction t : transactions) {
  if (isBlank(t.id) || isBlank(t.acct) || isBlank(t.merch))
    -> DECLINED, MISSING_REQUIRED_FIELD
  if (!seen.add(t.id))
    -> DECLINED, DUPLICATE_TRANSACTION
  if (t.amount <= 0)
    -> DECLINED, INVALID_AMOUNT
  if (!currencies.contains(t.currency.toUpperCase()))
    -> DECLINED, UNSUPPORTED_CURRENCY
  if (!merchants.contains(t.merchant))
    -> DECLINED, INACTIVE_MERCHANT
  if (!accounts.contains(t.account))
    -> DECLINED, INACTIVE_ACCOUNT
  if (t.timestamp == null)
    -> DECLINED, MISSING_TIMESTAMP
  -> APPROVED, VALID
}
```
