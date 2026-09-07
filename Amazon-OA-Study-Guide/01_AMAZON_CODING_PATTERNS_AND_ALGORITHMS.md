# Amazon OA: Top Algorithmic Patterns & Python 3 Blueprints (2026)

> **Section:** Coding Challenge — Problem 1 (Traditional DSA)  
> **Target Time:** 35–40 minutes  
> **Evaluation:** 100% correct outputs, $O(N)$ or $O(N \log N)$ complexity, zero memory limit/timeout errors.

---

## Pattern 1: Sliding Window with Frequency Constraints

### Typical Amazon Variants:
- Find the longest/shortest substring of warehouse order codes containing at most $k$ distinct categories.
- Minimum size package shipment window where all required items are present.
- Maximum customer engagement score over a variable sliding interval.

### Production-Ready Template (Dynamic Window):
```python
from collections import defaultdict


def min_window_substring(s: str, target: str) -> str:
    """Find the minimum window in s which contains all characters of target.

    Time Complexity: O(N) where N is len(s)
    Space Complexity: O(K) where K is unique chars in target
    """
    if not s or not target:
        return ""

    target_counts = defaultdict(int)
    for char in target:
        target_counts[char] += 1

    required_unique = len(target_counts)
    window_counts = defaultdict(int)

    formed = 0
    left = 0
    min_len = float("inf")
    result_window = (0, 0)

    for right, char in enumerate(s):
        window_counts[char] += 1

        if (
            char in target_counts
            and window_counts[char] == target_counts[char]
        ):
            formed += 1

        # Shrink the window from the left as long as it satisfies constraints
        while left <= right and formed == required_unique:
            current_len = right - left + 1
            if current_len < min_len:
                min_len = current_len
                result_window = (left, right)

            # Character at left leaves the window
            leaving_char = s[left]
            window_counts[leaving_char] -= 1
            if (
                leaving_char in target_counts
                and window_counts[leaving_char] < target_counts[leaving_char]
            ):
                formed -= 1

            left += 1

    if min_len == float("inf"):
        return ""
    return s[result_window[0] : result_window[1] + 1]
```

---

## Pattern 2: Priority Queue / Greedy Optimization

### Typical Amazon Variants:
- **Optimal Package Consolidation:** Connecting cables or packaging items with minimum cumulative cost (Huffman coding principle).
- **K-Closest Logistics Centers:** Finding the $K$ closest fulfillment centers to a delivery point.
- **Task Scheduler with Cooldown:** Scheduling AWS Lambda functions or worker tasks with cooling intervals.

### Production-Ready Template (Minimum Cost to Merge Parts):
```python
import heapq
from typing import List


def minimum_cost_to_combine_packages(package_sizes: List[int]) -> int:
    """Consolidate packages by always combining the two smallest packages first.

    Time Complexity: O(N log N)
    Space Complexity: O(N)
    """
    if not package_sizes or len(package_sizes) <= 1:
        return 0

    heapq.heapify(package_sizes)
    total_cost = 0

    while len(package_sizes) > 1:
        first = heapq.heappop(package_sizes)
        second = heapq.heappop(package_sizes)

        merge_cost = first + second
        total_cost += merge_cost

        heapq.heappush(package_sizes, merge_cost)

    return total_cost
```

---

## Pattern 3: Monotonic Stack & Deque

### Typical Amazon Variants:
- **Server Health Histogram:** Largest rectangle area of healthy adjacent server racks.
- **Stock Price Spans / Next Greater Server Load:** Days until a higher resource spike occurs.
- **Sliding Window Max Throughput:** Maximum request load in every continuous $k$-second window.

### Production-Ready Template (Sliding Window Maximum):
```python
from collections import deque
from typing import List


def max_sliding_window(nums: List[int], k: int) -> List[int]:
    """Find maximum throughput in each sliding window of size k using Monotonic Deque.

    Time Complexity: O(N) - each element is pushed/popped at most once
    Space Complexity: O(k) - deque stores at most k indices
    """
    if not nums or k <= 0:
        return []

    dq = deque()  # stores indices of candidate maximums in decreasing order
    result = []

    for i, num in enumerate(nums):
        # 1. Remove indices that are outside the current window
        while dq and dq[0] < i - k + 1:
            dq.popleft()

        # 2. Maintain decreasing monotonicity: remove elements smaller than current
        while dq and nums[dq[-1]] <= num:
            dq.pop()

        # 3. Add current element index
        dq.append(i)

        # 4. Once we have populated the first full window, record the front
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result
```

---

## Pattern 4: Graph Traversal (BFS/DFS) & Grid Pathfinding

### Typical Amazon Variants:
- **Rotten Oranges / Defective Server Outage Propagation:** Time taken for an infected node in an AWS data center cluster to corrupt all connected nodes.
- **Number of Fulfillment Islands / Delivery Zones:** Connected components in a 2D grid matrix.
- **Shortest Delivery Route with Obstacles:** BFS for unweighted minimum steps.

### Production-Ready Template (Outage Propagation - Multi-Source BFS):
```python
from collections import deque
from typing import List


def time_to_infect_cluster(grid: List[List[int]]) -> int:
    """Calculates minutes elapsed until all operational servers (1) are corrupted by defective servers (2).

    0 = empty rack, 1 = healthy server, 2 = defective server.
    Time Complexity: O(M * N)
    Space Complexity: O(M * N)
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    queue = deque()
    healthy_servers = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                queue.append((r, c, 0))  # (row, col, minute)
            elif grid[r][c] == 1:
                healthy_servers += 1

    if healthy_servers == 0:
        return 0

    minutes_elapsed = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        r, c, mins = queue.popleft()
        minutes_elapsed = mins

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2  # Infect
                healthy_servers -= 1
                queue.append((nr, nc, mins + 1))

    return minutes_elapsed if healthy_servers == 0 else -1
```

---

## Pattern 5: Prefix Sums & Hash Map Remainder Lookups

### Typical Amazon Variants:
- **Subarrays with Target Sum / Even Category Distribution:** Number of sub-sequences whose total payload matches $K$.
- **Subarray Sum Divisible by K:** Grouping transactions or logs into batches of size $K$.

### Production-Ready Template (Subarray Sum Equals K):
```python
from collections import defaultdict
from typing import List


def subarray_sum(nums: List[int], k: int) -> int:
    """Counts number of continuous subarrays whose sum equals target k.

    Time Complexity: O(N)
    Space Complexity: O(N)
    """
    prefix_counts = defaultdict(int)
    prefix_counts[0] = 1  # Base case: sum of 0 appears once initially

    current_sum = 0
    valid_subarrays = 0

    for num in nums:
        current_sum += num
        needed_prefix = current_sum - k

        if needed_prefix in prefix_counts:
            valid_subarrays += prefix_counts[needed_prefix]

        prefix_counts[current_sum] += 1

    return valid_subarrays
```

---

## 6. Amazon OA Edge Case & Test Verification Checklist

Before hitting **Submit Code** on HackerRank, manually trace your code against:
- [ ] **Empty / Single Input:** `nums = []`, `nums = [1]`, `s = ""`
- [ ] **All Elements Identical:** `nums = [7, 7, 7, 7]`
- [ ] **Negative Values / Zeroes:** `nums = [-5, 0, 5, -2, 2]`
- [ ] **Extreme Scale Constraints:** $N = 10^5 \implies$ Is there any nested loop that yields $O(N^2)$?
- [ ] **Integer Overflow (Python auto-handles, but watch recursion depth):** If using DFS, set `sys.setrecursionlimit(200000)` or convert to iterative stack.
