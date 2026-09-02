# Find Negative Balance Accounts

**Difficulty:** EASY · **Context:** Capital One GPN · DSA Round
**Pattern:** Filter + Sort · **Time:** O(n log n) · **Space:** O(k) · **Language:** Java / Python

Given a list of accounts where each account has an ID and a balance, find all accounts with a negative balance. Return the account IDs sorted by balance in ascending order (most negative first). If no accounts have negative balance, return an empty list.

## Input / Output

```
accounts = [
  {id: "A", balance: 1000},
  {id: "B", balance: -500},
  {id: "C", balance: -200},
  {id: "D", balance: 300},
  {id: "E", balance: -50}
]

Output: ["B", "C", "E"]  // sorted by balance: -500, -200, -50
```

**Edge cases:**
- No negative balances → return empty list
- All negative → return all IDs sorted
- Empty input → return empty list
- Tie in balances → sort by ID alphabetically

## 2. Pattern Recognition

**Why signals:**
- Filter elements by a condition → linear scan
- Return sorted by a field → sort after filter
- Simple comparison (balance < 0) → no complex logic
- Tie-break by ID → secondary sort key
- Capital One banking domain → overdraft detection

**Core pattern:** Filter (O(n)) + Sort (O(k log k) where k is the number of negatives). Total O(n + k log k). This is a warm-up question that tests basic data processing and sorting.

## 3. Pattern Blueprint

4-step template:
1. Handle edge case: empty input → return empty list
2. Filter: iterate through accounts, collect those with balance < 0
3. Sort: order by balance ascending (most negative first), tie-break by ID alphabetically
4. Extract and return the IDs

## 4. How to Think About It

**Q1: Is this too simple for an interview?**
It is a warm-up. The interviewer uses it to see if you can write clean, correct code quickly. The follow-up questions are where the senior signal comes: scale, concurrency, alerting, production handling.

**Q2: Filter first or sort first?**
Filter first. Sorting only the negatives (k elements) is O(k log k), which is cheaper than sorting all n then filtering O(n log n). If k is small (few negatives), this is much faster.

**Q3: What about the tie-break?**
If two accounts have the same balance, sort by ID alphabetically. This makes the output deterministic. Use a comparator: `(a, b) -> a.balance != b.balance ? a.balance - b.balance : a.id.compareTo(b.id)`.

**Q4: → What is the production context?**
This is overdraft detection. In production, negative balances trigger alerts, overdraft fees, or fraud investigation. The "find negative accounts" query runs continuously or on a schedule. Think about streaming, alerting, and escalation.

## 5. Real-World Analogy

Think of a **bouncer at a club checking IDs**. The bouncer goes through the line, checks each person's age (balance), and lets in only those who are underage (negative). Then the underage people line up by height (sort by balance).

The filter is the bouncer's check. The sort is the lineup. You do not sort the entire crowd first, you filter first because the bouncer only cares about the underage ones.

In banking, this is the overdraft monitor. Every night, the system scans all accounts, flags the negative ones, sorts them by how far underwater they are, and sends the list to the collections team. The most negative accounts get attention first.

## 6. Build Your Intuition

**Q: Why filter before sorting?**
If you have 10M accounts and only 100 are negative, filtering first gives you 100 elements to sort (O(100 log 100)). Sorting all 10M first is O(10M log 10M). Filter-first is 100,000x less work.

**Q: Is this a streaming or batch problem?**
Both. Batch: run nightly on all accounts. Streaming: maintain a set of negative accounts updated on each transaction. The streaming version uses a min-heap or sorted set for real-time queries.

**Q: What if balances change frequently?**
If balances update every second, re-scanning all accounts is wasteful. Maintain a TreeSet of negative accounts. On each balance update, add or remove from the set. Query is O(1) to get the sorted list.

**Q: Why is this question asked at Capital One?**
Overdraft management is a core banking function. Capital One needs engineers who understand that "find negative accounts" is not just a coding exercise, it is the foundation of overdraft fees, alerts, and regulatory reporting.

## 7. How It Works (Step by Step)

- **Step 1:** Input: [(A, 1000), (B, -500), (C, -200), (D, 300), (E, -50)].
- **Step 2:** Filter: A: 1000 ≥ 0 skip. B: -500 < 0 keep. C: -200 < 0 keep. D: 300 ≥ 0 skip. E: -50 < 0 keep. Filtered: [(B, -500), (C, -200), (E, -50)].
- **Step 3:** Sort by balance ascending: [(B, -500), (C, -200), (E, -50)]. Already sorted (most negative first).
- **Step 4:** Extract IDs: ["B", "C", "E"]. Return.

## 8. Dry Run Table

| Account | Balance | Negative? | Action |
|---------|---------|-----------|--------|
| A | 1000 | No | Skip |
| B | -500 | Yes | Keep |
| C | -200 | Yes | Keep |
| D | 300 | No | Skip |
| E | -50 | Yes | Keep |

Filtered: [B(-500), C(-200), E(-50)]. Sorted: same. Result: `["B", "C", "E"]`

## 9. Complexity Deep Dive

**Time Complexity:** Filter O(n) + Sort O(k log k). Total O(n + k log k). If k is small, nearly O(n). If k ≈ n, O(n log n).

**Space Complexity:** O(k) for the filtered list of negative accounts. The output list also has k elements.

## 10. From Brute Force to Optimal

**Naive: Sort All Then Filter** — O(n log n) time. Sorts all n accounts even if only k are negative. Wasteful when k is small.

**Optimal: Filter Then Sort** — O(n + k log k) time. Filter first, sort only the negatives. **100,000x faster** when k is small.

## 11. Edge Cases & Gotchas

- **Empty input:** No accounts. Return empty list. Do not throw.
- **No negative accounts:** All balances ≥ 0. Return empty list.
- **All negative accounts:** Every account is overdrawn. Return all IDs sorted.
- **Tie in balances:** Two accounts with -500. Sort by ID alphabetically for deterministic output.
- **Zero balance:** Balance == 0 is NOT negative. Use balance < 0, not ≤ 0.
- **Null accounts or null balances:** Handle null. Either filter out nulls or throw. In production, null balance is a data integrity issue.

## 12. Flashcards

**Q1: What is the time complexity?**
O(n + k log k) where n is total accounts and k is negative accounts. Filter is O(n), sort is O(k log k).

**Q2: Why filter before sort?**
Sorting only k elements is O(k log k) vs sorting all n is O(n log n). When k is small, filter-first is much faster.

**Q3: How do you handle ties in balance?**
Sort by balance ascending, then by ID alphabetically. Comparator: `(a, b) -> a.balance != b.balance ? a.balance - b.balance : a.id.compareTo(b.id)`.

**Q4: Is zero balance negative?**
No. Zero is not negative. Use balance < 0, not ≤ 0. Common off-by-one trap.

**Q5: How would you make this real-time?**
Maintain a TreeSet of negative accounts. On each balance update, add or remove from the set. Query returns the sorted list in O(k) iteration.

## 13. Where It Is Used (Real World)

- **Overdraft Detection (Capital One, Chase, Bank of America):** Every bank runs this query nightly or continuously. Negative accounts trigger overdraft fees, alerts, and escalation to collections.
- **Margin Call Detection (Brokerage):** Negative margin balance triggers a margin call.
- **Fraud Flagging:** Sudden negative balance on a credit card may indicate fraud.
- **Regulatory Reporting:** Banks must report overdraft statistics to regulators (OCC, FDIC).

## 14. Common Mistakes

- Using ≤ 0 instead of < 0. Zero is not negative.
- Sorting before filtering. O(n log n) instead of O(n + k log k).
- Not handling ties. Define a tiebreaker (by ID) for deterministic output.
- Returning balances instead of IDs. Read the problem.
- Not handling null or empty input. Return empty list, do not throw.
- Using double for balance. Use BigDecimal for money. Precision errors cause false negatives.
- Not mentioning the production context. Senior engineers connect the coding problem to the business function.

## 15. Interview Tips

- Code it quickly and correctly. This is a warm-up. Filter, sort, extract IDs.
- Use streams (Java) or list comprehension (Python). Shows language fluency.
- State the complexity. O(n + k log k). Explain why filter-first is better.
- Handle edge cases. Empty input, no negatives, ties, zero balance.
- Use BigDecimal. If asked why, explain floating-point precision for money.
- Pivot to production immediately. "This is overdraft detection. In production I would maintain a sorted set of negative accounts updated on each transaction, trigger alerts, and feed the compliance reporting pipeline." This is the senior signal.
- Mention the business impact. Overdraft fees are a revenue stream. Fraud detection. Regulatory compliance.

## 16. Similar Problems to Practice

- **Filter Elements by Condition** — generic pattern (EASY)
- **Top K Frequent Elements** (LeetCode 347) — filter + sort (EASY)
- **Kth Largest Element** (LeetCode 215) — partial sort (MEDIUM)
- **Move Zeroes** (LeetCode 283) — in-place filter (EASY)
- **Design a Leaderboard** (LeetCode 1244) — sorted set maintenance (MEDIUM)

## 17. Related Algorithms

- **Filter (Linear Scan)** — O(n) pass to select elements by condition
- **Sort** — O(k log k) ordering of filtered elements
- **Comparator** — multi-key sort (balance, then ID)
- **TreeSet** — maintained sorted set for real-time queries
- **Stream API** — filter + sorted + map + collect pipeline
- **BigDecimal** — exact decimal for financial balances
- **Quickselect** — if only top-k negatives needed, O(n) average
- **Counting Sort** — if balances are bounded integers, O(n)

## 18. Where This Pattern Meets System Design

- **In-memory list → Database query on sharded accounts:** Production has millions of accounts across shards. Run the query per shard in parallel, merge results. Or maintain a materialized view of negative accounts updated by triggers.
- **Batch query → Streaming overdraft monitor:** Each transaction publishes an event to Kafka. A stream processor (Flink) tracks balances and emits "account went negative" events. The alerting service subscribes and triggers notifications in real time.
- **Simple list → Alerting and escalation pipeline:** Negative accounts feed an alerting pipeline: SMS/email to customer, assess overdraft fee, flag for fraud review, escalate to collections after N days.
- **One-time query → Compliance reporting:** Regulators require daily/weekly overdraft statistics. The negative accounts list feeds a reporting job aggregated by region, customer type, and severity.
- **Single currency → Multi-currency balances:** "Negative" must consider the converted total. Use real-time FX rates. Filter becomes: `sum(balance_i * fx_rate_i) < 0`.

## 19. Code Solutions

### Java

```java
import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

class Account {
    final String id;
    final BigDecimal balance;
    Account(String id, BigDecimal balance) { this.id = id; this.balance = balance; }
}

public class NegativeBalanceFinder {
    public static List<String> findNegativeAccounts(List<Account> accounts) {
        if (accounts == null || accounts.isEmpty()) {
            return Collections.emptyList();
        }
        return accounts.stream()
            .filter(a -> a.balance.compareTo(BigDecimal.ZERO) < 0)
            .sorted((a, b) -> {
                int cmp = a.balance.compareTo(b.balance);
                return cmp != 0 ? cmp : a.id.compareTo(b.id);
            })
            .map(a -> a.id)
            .collect(Collectors.toList());
    }
}
```

### Python

```python
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class Account:
    id: str
    balance: Decimal

def find_negative_accounts(accounts: list[Account]) -> list[str]:
    if not accounts:
        return []
    negatives = [a for a in accounts if a.balance < Decimal("0")]
    negatives.sort(key=lambda a: (a.balance, a.id))
    return [a.id for a in negatives]
```

## 20. Follow-Up Questions

**Q: How would you handle 100M accounts across multiple shards?**
Run the query per shard in parallel. Each shard returns its negative accounts. Merge the sorted lists using a k-way merge. Or maintain a materialized view updated by transaction triggers.

**Q: How would you make this real-time?**
Maintain a TreeSet of negative accounts. On each transaction, update the balance. If balance crosses zero, add or remove from the set. Query returns the sorted set in O(k). Updates are O(log n).

**Q: What if you only need the top N most negative?**
Use a min-heap of size N. Iterate accounts, if balance < 0 and heap size < N, add. If heap full and balance < heap root, replace. O(n log N) time, O(N) space.

**Q: How do you alert on new negative accounts?**
Stream processor (Flink) watches the transaction event stream. When an account balance crosses from positive to negative, emit an alert event. The alerting service sends SMS/email and creates a ticket.

**Q: How do you handle multi-currency accounts?**
Convert all balances to a base currency using real-time FX rates. The filter checks the converted total. Cache FX rates with a TTL. Precompute the converted balance on each transaction.

## 21. Quick Reference

| Aspect | Value |
|--------|-------|
| **Pattern** | Filter + Sort (filter-first) |
| **Complexity** | O(n + k log k) time, O(k) space |
| **Filter Condition** | balance < 0 (strictly, zero is NOT negative) |
| **Sort Order** | Balance ascending (most negative first), tie-break by ID |
| **Edge Cases** | Empty input, no negatives, all negative, ties, zero balance, null |
| **Senior Signal** | Overdraft detection: streaming, alerting, compliance, multi-currency |

**Core code shape:**
```java
List<String> findNegativeAccounts(List<Account> accounts) {
  if (accounts == null || accounts.isEmpty()) return emptyList();
  return accounts.stream()
    .filter(a -> a.balance.compareTo(ZERO) < 0)
    .sorted((a, b) -> a.balance != b.balance
      ? a.balance.compareTo(b.balance)
      : a.id.compareTo(b.id))
    .map(a -> a.id)
    .collect(toList());
}
```
