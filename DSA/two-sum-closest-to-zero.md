# Two Sum Closest to Zero

**Difficulty:** EASY-MEDIUM · **Context:** Capital One GPN · DSA Round
**Pattern:** Sort + Two Pointer · **Time:** O(n log n) · **Space:** O(1) or O(n) · **Language:** Java / Python

Given an array of integers (positive and negative), find two elements whose sum is closest to zero. Return the sum of that pair. If multiple pairs have the same absolute distance from zero, return the positive sum (the one with the larger value).

## 1. Problem Statement

**Examples:**
```
Input:  [1, 60, -10, 70, -80, 85]
Output: 5  (pair: -80 + 85 = 5)

Input:  [1, 2, -2, 4, -4]
Output: 0  (pair: 2 + -2 = 0)

Input:  [1, 2, 3, 4, 5]
Output: 3  (pair: 1 + 2 = 3, closest to zero)

Input:  [-5, -4, -3, -2, -1]
Output: -3  (pair: -2 + -1 = -3, closest to zero)
```

## 2. Pattern Recognition

**Why signals:**
- Find a pair with a target property → two pointer or hash map
- "Closest to zero" → minimize absolute value of sum
- Array has both positive and negative → sorting helps
- No exact target → two pointer on sorted array, track minimum
- Tie-break (prefer positive) → comparison logic update

**Core pattern:** Sort the array, then use two pointers (left at start, right at end). Compute sum. If sum < 0, move left rightward (increase sum). If sum > 0, move right leftward (decrease sum). Track the closest sum seen. O(n log n) time, O(1) space.

## 3. Pattern Blueprint

5-step template:
1. Sort the array in ascending order
2. Initialize left = 0, right = n-1, minSum = infinity, result = 0
3. Loop while left < right: compute sum = arr[left] + arr[right]
4. If |sum| < |minSum|, update minSum = sum. If |sum| == |minSum| and sum > minSum, update (prefer positive). Move pointers: if sum < 0, left++. If sum > 0, right--. If sum == 0, break (found exact).
5. Return minSum (the closest sum)

## 4. How to Think About It

**Q1: Why does sorting help?**
After sorting, the smallest (most negative) is at the left, the largest (most positive) is at the right. Their sum is somewhere in the middle. By moving pointers inward based on the sign of the sum, we systematically explore all candidate pairs.

**Q2: Why not check all pairs?**
Brute force is O(n²). For n = 1M, that is 1 trillion pairs. Sort + two pointer is O(n log n) = 20M operations. 50,000x faster.

**Q3: Why does the two-pointer movement work?**
If sum < 0, we need a larger sum to get closer to zero. Moving left rightward increases the sum (since the array is sorted). If sum > 0, we need a smaller sum. Moving right leftward decreases the sum. This greedily converges toward zero.

**Q4: → What about the tie-break?**
If two sums have the same absolute value (e.g., -3 and 3), prefer the positive one (3). Update the result when |sum| < |minSum| OR (|sum| == |minSum| AND sum > minSum).

## 5. Real-World Analogy

Think of a **balance scale with weights on both sides**. You have a set of weights, some positive (right side) and some negative (left side, which is really a counterweight). You want to find two weights that, when placed on the same side, make the scale as balanced as possible (closest to zero).

Sort the weights from lightest to heaviest. Put one finger on the lightest (most negative) and one on the heaviest (most positive). If the combined weight tilts left (negative), move the left finger right to a heavier weight. If it tilts right (positive), move the right finger left to a lighter weight. Keep going until your fingers meet.

At each step, note how close the scale is to balanced. The closest you ever got is your answer. If you ever hit perfect balance (sum = 0), stop immediately.

## 6. Build Your Intuition

**Q: Why not use a HashMap like classic Two Sum?**
Classic Two Sum has an exact target (e.g., target = 9). You check if (target - num) exists in the map. Here, the target is "closest to zero," which is not a fixed value. You cannot look up "closest to zero" in a HashMap. Sort + two pointer handles the fuzzy target.

**Q: Can we do better than O(n log n)?**
Sorting is the bottleneck. If the array is already sorted, the two-pointer part is O(n). There is no known O(n) solution for unsorted input because finding the closest-to-zero pair requires comparing elements in a way that sorting enables.

**Q: What if the array has fewer than 2 elements?**
Edge case. If n < 2, there is no pair. Return an error or a sentinel value. Clarify with the interviewer.

**Q: Why prefer positive on tie?**
Convention. In a financial context, a net gain of $3 is preferred over a net loss of $3. The positive sum is the "better" outcome. State this rule explicitly.

## 7. How It Works (Step by Step)

- **Step 1:** Input: [1, 60, -10, 70, -80, 85]. Sort: [-80, -10, 1, 60, 70, 85].
- **Step 2:** left=0 (-80), right=5 (85). sum = 5. |5| < inf, minSum = 5. sum > 0, right--. right=4.
- **Step 3:** left=0 (-80), right=4 (70). sum = -10. |-10| > |5|, no update. sum < 0, left++. left=1.
- **Step 4:** left=1 (-10), right=4 (70). sum = 60. |60| > |5|, no update. sum > 0, right--. right=3.
- **Step 5:** left=1 (-10), right=3 (60). sum = 50. |50| > |5|, no update. sum > 0, right--. right=2.
- **Step 6:** left=1 (-10), right=2 (1). sum = -9. |-9| > |5|, no update. sum < 0, left++. left=2. left == right, stop.
- **Step 7:** Return minSum = 5. Pair: -80 and 85.

## 8. Dry Run Table

| Step | left | arr[left] | right | arr[right] | sum | minSum | Action |
|------|------|-----------|-------|------------|-----|--------|--------|
| 0 | 0 | -80 | 5 | 85 | 5 | 5 | sum>0, right-- |
| 1 | 0 | -80 | 4 | 70 | -10 | 5 | \|-10\|>\|5\|, sum<0, left++ |
| 2 | 1 | -10 | 4 | 70 | 60 | 5 | \|60\|>\|5\|, sum>0, right-- |
| 3 | 1 | -10 | 3 | 60 | 50 | 5 | \|50\|>\|5\|, sum>0, right-- |
| 4 | 1 | -10 | 2 | 1 | -9 | 5 | \|-9\|>\|5\|, sum<0, left++ |
| 5 | 2 | 1 | 2 | 1 | - | 5 | left==right, STOP |

Result: 5 (pair -80, 85)

## 9. Complexity Deep Dive

**Time: O(n log n)** — Sort: O(n log n). Two pointer scan: O(n). The sort dominates. For n = 1M: sort ~20M ops, scan ~1M ops. Total ~21M ops vs brute force 1 trillion.

**Space: O(1)** if sorting in place (modifies input). O(n) if you copy the array to avoid mutation. Java's Arrays.sort() on primitives is in-place. Python's sorted() creates a new list.

## 10. From Brute Force to Optimal

**Naive: Check All Pairs** — O(n²) time, O(1) space. For n=1M, 500 billion pairs. Too slow.

**Optimal: Sort + Two Pointer** — O(n log n) time, O(1) space. **50,000x faster** at n=1M.

## 11. Edge Cases & Gotchas

- **Array with fewer than 2 elements:** n < 2: no pair exists. Return error or throw.
- **All positive numbers:** [1, 2, 3, 4, 5]. Closest sum is the two smallest: 1+2=3. Algorithm handles this: sum always positive, right moves left until adjacent.
- **All negative numbers:** [-5, -4, -3, -2, -1]. Closest sum is the two largest: -2 + -1 = -3. Algorithm: sum always negative, left moves right until adjacent.
- **Exact zero pair exists:** [1, -1, 2, 3]. Sum = 0 is the best possible. Break early when sum == 0.
- **Tie between positive and negative:** [-3, 3] both have |sum| = 3. Prefer 3 (positive).
- **Duplicate elements:** [2, 2, -2, -2]. Multiple pairs sum to 0. Duplicates do not break the two-pointer approach.

## 12. Flashcards

**Q1: What is the time complexity?**
O(n log n). Sorting is O(n log n), the two-pointer scan is O(n). The sort dominates.

**Q2: Why does the two-pointer approach work?**
After sorting, moving left rightward increases the sum, moving right leftward decreases it. If sum < 0, we need a larger sum, so left++. If sum > 0, we need smaller, so right--. This greedily converges toward zero.

**Q3: How do you handle the tie-break (prefer positive)?**
Update minSum when |sum| < |minSum| OR (|sum| == |minSum| AND sum > minSum). This ensures the positive sum wins on ties.

**Q4: Can you break early?**
Yes. If sum == 0, that is the best possible. Break immediately. Common optimization.

**Q5: Why not use a HashMap?**
HashMap works for exact target Two Sum. Here the target is "closest to zero," which is fuzzy. You cannot hash-search for a fuzzy target. Sort + two pointer handles it.

## 13. Where It Is Used (Real World)

- **Portfolio Hedging (Finance):** Find two positions whose combined risk is closest to zero. Long and short positions offset. Minimizing net exposure is literally "two sum closest to zero."
- **Transaction Reconciliation (Capital One):** Match debits and credits that sum closest to zero to find near-balanced pairs. Useful when exact matches fail.
- **Charge-Balance Optimization:** In battery systems or chemical reactions, find two charges that neutralize each other closest to zero.
- **Sensor Calibration:** Two sensors with offset errors. Find the pair whose combined error is closest to zero for calibration pairing.

## 14. Common Mistakes

- Not sorting first. Two pointer only works on sorted arrays.
- Moving the wrong pointer. If sum < 0, move LEFT rightward (to increase sum). If sum > 0, move RIGHT leftward (to decrease). Reversing this diverges from zero.
- Forgetting the tie-break. |sum| == |minSum| but sum > minSum: update. Otherwise you return -3 instead of 3.
- Using left <= right instead of left < right. You need two distinct elements.
- Not handling n < 2. Array of 0 or 1 elements has no pair.
- Initializing minSum to 0. 0 is a valid sum. Use Integer.MAX_VALUE or infinity.
- Not breaking on sum == 0. 0 is the optimal. Continuing wastes iterations.

## 15. Interview Tips

- Start with brute force. "I can check all pairs in O(n²). But I can do better by sorting first."
- Explain why sorting enables two-pointer. Sorted array lets you greedily move pointers based on the sign of the sum.
- State the tie-break rule. "If two sums have the same absolute value, I prefer the positive one."
- Walk through the example. Trace the sorted array and pointer movements.
- Mention the early break. "If sum == 0, I break immediately since 0 is optimal."
- State complexity. O(n log n) time, O(1) space (or O(n) if copying).
- Handle edge cases. n < 2, all positive, all negative, duplicates.
- Pivot to production. For Capital One: reconciliation, hedging, risk offset. Connect to finance domain.

## 16. Similar Problems to Practice

- **Two Sum** (LeetCode 1) — the classic, HashMap approach — EASY
- **Two Sum II** (LeetCode 167) — sorted array, two pointer — MEDIUM
- **3Sum Closest** (LeetCode 16) — three elements closest to target — MEDIUM
- **3Sum** (LeetCode 15) — all triplets summing to zero — MEDIUM
- **Container With Most Water** (LeetCode 11) — two pointer on sorted — EASY

## 17. Related Algorithms

- **Two Pointer** — left and right converging on sorted array
- **Sorting** — enables the two-pointer greedy approach
- **Greedy** — move the pointer that improves the current best
- **HashMap** — alternative for exact-target Two Sum
- **Binary Search** — alternative: for each num, binary search for -num
- **k-Sum Problem** — generalization to k elements
- **Subset Sum** — related NP-complete problem
- **Knapsack** — optimization with constraints

## 18. Where This Pattern Meets System Design

- **In-memory pair search → Streaming reconciliation:** Production reconciliation processes millions of transactions streaming from Kafka. Use windowed aggregation: collect transactions in a time window, sort, run two-pointer, emit matched pairs.
- **Single array → Sharded datasets:** If debits and credits are in different databases, partition by a hash key, run the algorithm per partition, then merge results. Or use a distributed sort (MapReduce).
- **O(n log n) batch → Real-time matching engine:** For real-time hedging, maintain a sorted structure (balanced BST or skip list) of live positions. On each new position, binary search for the closest offset. O(log n) per insertion and query.
- **Closest to zero → Multi-objective optimization:** Production systems optimize multiple objectives: minimize risk, maximize return, respect constraints. Linear programming or ML-based optimizers replace the simple two-pointer.

## 19. Code Solutions

### Java

```java
import java.util.Arrays;

public class TwoSumClosestToZero {
    public static int closestSumToZero(int[] arr) {
        if (arr == null || arr.length < 2) {
            throw new IllegalArgumentException("Array must have at least 2 elements");
        }
        Arrays.sort(arr);
        int left = 0, right = arr.length - 1;
        int minSum = Integer.MAX_VALUE;
        while (left < right) {
            int sum = arr[left] + arr[right];
            if (Math.abs(sum) < Math.abs(minSum)) {
                minSum = sum;
            } else if (Math.abs(sum) == Math.abs(minSum) && sum > minSum) {
                minSum = sum;
            }
            if (sum < 0) {
                left++;
            } else if (sum > 0) {
                right--;
            } else {
                break; // sum == 0 is optimal
            }
        }
        return minSum;
    }
}
```

### Python

```python
def closest_sum_to_zero(arr: list[int]) -> int:
    if not arr or len(arr) < 2:
        raise ValueError("Array must have at least 2 elements")

    sorted_arr = sorted(arr)
    left, right = 0, len(sorted_arr) - 1
    min_sum = float('inf')

    while left < right:
        s = sorted_arr[left] + sorted_arr[right]
        if abs(s) < abs(min_sum):
            min_sum = s
        elif abs(s) == abs(min_sum) and s > min_sum:
            min_sum = s
        if s < 0:
            left += 1
        elif s > 0:
            right -= 1
        else:
            break  # s == 0 is optimal

    return min_sum
```

## 20. Follow-Up Questions

**Q: What if you need to return the pair, not just the sum?**
Track minLeft and minRight alongside minSum. When you update minSum, also update the indices. Return (arr[minLeft], arr[minRight]).

**Q: What if there are multiple pairs with the same closest sum?**
Return all of them. Collect pairs in a list whenever |sum| == |minSum|. Reset the list when a closer sum is found.

**Q: What about 3Sum Closest to Zero?**
Sort, then for each element i, run two-pointer on the subarray i+1 to n-1 looking for the pair closest to -arr[i]. O(n²) time, O(1) space.

**Q: How would you handle streaming data?**
Maintain a sorted structure (balanced BST). On each new element, binary search for the element closest to its negation. Update the closest sum. O(log n) per element, O(n log n) total.

**Q: Can you do it without sorting?**
Binary search approach: for each element, binary search for its negation in a sorted copy. Still O(n log n). No known O(n) solution for closest-to-zero pair finding on unsorted input.

## 21. Quick Reference

| Aspect | Value |
|--------|-------|
| **Pattern** | Sort + Two Pointer (convergent) |
| **Complexity** | O(n log n) time, O(1) space (in-place sort) |
| **Pointer Movement** | sum < 0 → left++, sum > 0 → right--, sum == 0 → break |
| **Tie-Break** | \|sum\| == \|minSum\| AND sum > minSum → update (prefer positive) |
| **Edge Cases** | n < 2, all positive, all negative, duplicates, exact zero |
| **Senior Signal** | Pivot to finance: reconciliation, hedging, risk offset |

**Core code shape:**
```java
int closestSum(int[] arr) {
  Arrays.sort(arr);
  int left = 0, right = arr.length - 1;
  int minSum = MAX_VALUE;
  while (left < right) {
    int sum = arr[left] + arr[right];
    if (|sum| < |minSum|) minSum = sum;
    else if (|sum| == |minSum| && sum > minSum) minSum = sum;
    if (sum < 0) left++;
    else if (sum > 0) right--;
    else break;  // sum == 0 is optimal
  }
  return minSum;
}
```
