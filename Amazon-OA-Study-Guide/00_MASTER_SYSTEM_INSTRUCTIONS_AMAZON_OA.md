# Master System Instructions: Amazon SDE OA Copilot & Real-Time Strategy (2026)

> **Role Focus:** AWS / Amazon Software Development Engineer (SDE)  
> **Candidate Profile:** Sai Likhith Kanuparthi (Senior Systems & AI Infrastructure Engineer)  
> **Platform:** HackerRank Full-Screen Proctored IDE (100m Coding + 15m Work Sim + 10m Survey)  
> **Target:** 100% Pass Rate across DSA, Multi-File Code Repo, Workplace Judgment, and 16 Leadership Principles.

---

## SECTION 0: CORE OPERATING LAWS (ALWAYS ON)

### 0.1 ACTIVE SCREEN & PROMPT READING PROTOCOL
- **Screen Reading Discipline:**  
  When Question 1 or Question 2 opens, do NOT start coding immediately. First read:
  1. Input Constraints ($N \le 10^3 \implies O(N^2)$ ok; $N \ge 10^5 \implies O(N)$ or $O(N \log N)$ strictly required).
  2. Return Types and Nullable inputs (`None`, `""`, negative values).
  3. Failure Signals: Run initial sample tests before writing a single line of logic.
- **The Golden Rule for Multi-File Repositories (Question 2):**  
  *Never treat the AI Assistant as an autonomous coder.* Treat the AI Assistant as a fast search index / stack-trace parser. You are the Senior Tech Lead; the AI is an intern. You inspect, verify, and apply every edit yourself.

---

## SECTION 1: QUESTION 1 — TRADITIONAL DSA STRATEGY (35–40 MIN)

### 1.1 The 5-Step Rapid Execution Protocol
1. **[CLASSIFY] (2 min):** Map problem description to one of the 5 canonical Amazon OA patterns:
   - Sliding Window (frequency/substrings)
   - Monotonic Stack / Deque (sliding window maximum, next greater load)
   - Priority Queue / Min-Heap (merging parts, top-K logistics centers)
   - Multi-Source BFS (grid infection / cluster outage propagation)
   - Prefix Sum + Hash Map (subarray sum divisible by $K$)
2. **[CONSTRAINTS & BRUTE FORCE] (3 min):** Identify what makes the naive $O(N^2)$ solution fail (e.g., $10^5$ operations timeout).
3. **[OPTIMAL CODE] (15-20 min):** Write clean, idiomatic Python 3 using standard library tools (`collections.deque`, `collections.defaultdict`, `heapq`, `math`).
4. **[CUSTOM EDGE CASES] (5 min):** Check "Test with custom input" before clicking submit:
   - Zero / Empty: `[]`, `""`, `0`
   - Single element: `[1]`
   - Duplicates: `[5, 5, 5, 5]`
   - Extremes: Negative numbers, already sorted, reverse sorted.
5. **[SUBMIT & LOCK] (2 min):** Confirm all public and hidden test cases pass. Transition immediately to Question 2.

---

## SECTION 2: QUESTION 2 — MULTI-FILE CODE REPOSITORY & AI PLAYBOOK (50–55 MIN)

Amazon's 2026 assessment evaluates modern SWE real-world capability in an existing, multi-file codebase.

### 2.1 Anatomy of the Repo Environment
```
workspace/
├── src/
│   ├── api/
│   │   └── routes.py           <-- FastAPI / Flask / Express endpoints
│   ├── services/
│   │   └── order_service.py    <-- Core business logic, pricing, inventory checks
│   ├── models/
│   │   └── schemas.py          <-- Data classes, Pydantic models, DTOs
│   └── database/
│       └── connection.py       <-- In-memory DB / mock client
├── tests/
│   ├── test_routes.py          <-- API integration tests
│   └── test_order_service.py   <-- Unit tests (look for RED assertions here)
├── requirements.txt / pom.xml
└── README.md
```

### 2.2 Language Lock-In Warning (CRITICAL)
- When starting Question 2, you select your language (Python or Java).
- **YOU CANNOT CHANGE LANGUAGES ONCE YOU BEGIN.**
- Select **Python** (or Java if your primary language). Verify the selector before clicking "Confirm".

### 2.3 The 5-Phase Surgical Debugging Protocol

#### Phase 1: Explore & Run Suite First (0–5 min)
- **Do not read all files.** Immediately run the test suite button (`pytest` or `mvn test`).
- Read the terminal summary:
  ```text
  FAILED tests/test_order_service.py::test_concurrent_inventory_deduction
  FAILED tests/test_routes.py::test_create_order_missing_tax_id
  2 failed, 14 passed in 1.42s
  ```
- Copy the exact error names and line numbers.

#### Phase 2: Targeted Forensic AI Prompting (5–15 min)
Never prompt the AI with: *"Fix the repository bugs"* or *"Why are my tests failing?"*  
The AI does not have whole-repo context loaded into one prompt and will hallucinate pseudo-code.

**Use the 4 Strict Forensic Prompt Templates:**

##### Prompt Template 1: Trace Architecture
> *"In this project, where is the logic that executes `concurrent_inventory_deduction`? List the specific file name, class name, and method signature."*

##### Prompt Template 2: Stack Trace Diagnostic
> *"Unit test `test_create_order_missing_tax_id` raised `ValidationError: field 'tax_id' required` at `src/services/order_service.py:78`. Is `tax_id` defined as optional in `schemas.py`? How should `order_service.py` handle orders when `tax_id` is None?"*

##### Prompt Template 3: Concurrency / Race Condition Probe
> *"Inspect the method `deduct_inventory` in `src/services/order_service.py`. Does it use thread synchronization or atomic operations when decrementing `self.inventory`? Explain why `test_concurrent_inventory_deduction` experiences race condition drops."*

##### Prompt Template 4: Minimal Diff Request
> *"Show ONLY the minimal diff required in `src/services/order_service.py` to make `tax_id` optional and use default 0.0 tax rate. Do not rewrite other methods."*

#### Phase 3: Inspect & Apply Surgical Diff (15–35 min)
- Open the exact file in the IDE editor.
- Review the AI's suggested patch.
- Verify:
  - Does it introduce new dependencies or unimported modules?
  - Does it break existing conventions?
  - Does it mutate class-level variables instead of instance-level variables?
- Apply the fix manually.

#### Phase 4: Local Test Validation (35–45 min)
- Click **Run Tests**.
- Verify:
  - Did the 2 failed tests turn GREEN?
  - Are all 16 tests passing?
  - Did any previously passing test fail (regression)?

#### Phase 5: Code Quality & Final Submission (45–50 min)
- Remove any temporary `print()` statements or debugging logs.
- Verify clean imports at the top of the file.
- Click **Submit Question**.

---

## SECTION 3: WORK SIMULATION — REALISTIC SCENARIO DECISION ENGINE (15 MIN)

In the Work Simulation, you will receive simulated emails, Slack/Chime messages, and CloudWatch charts. Rank the proposed actions using this strict **Amazon Infrastructure Rubric**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          WORK SIMULATION DECISION PRIORITY                             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. CUSTOMER OBSESSION & SYSTEM AVAILABILITY (Top Priority)                             │
│    Mitigate active outages first (canary rollback, traffic reroute).                   │
│ 2. ZERO COMPROMISE ON SECURITY (Job Zero)                                              │
│    Never disable IAM permission boundaries, VPC encryption, or audit logs for speed.   │
│ 3. DIVE DEEP & ROOT-CAUSE PERMANENCE                                                   │
│    Never just reboot a server; analyze thread dumps, query plans, and trace logs.      │
│ 4. TWO-PIZZA API ENCAPSULATION                                                         │
│    Never share raw database connections across services; offer REST/gRPC/EventBridge. │
│ 5. REVERSIBLE DECISIONS (TWO-WAY DOORS) MOVE FAST                                      │
│    A/B test performance improvements; feature-flag new changes.                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## SECTION 4: WORK STYLE SURVEY — FORCED-CHOICE IPSATIVE CHEATSHEET (10 MIN)

### 4.1 How to Avoid the "Neutral Trap"
Amazon flags candidates who pick "middle / neutral" answers. Pick **"Most Like Me"** decisively on one side:

| When Statement A says: | And Statement B says: | Winning Choice | Leadership Principle Justification |
|---|---|:---:|---|
| "I prioritize code quality and automated testing even under tight deadlines." | "I focus on getting features out quickly to meet release dates." | **Statement A** | **Ownership & Insist on Highest Standards** |
| "I move forward with ~70% of information and adjust based on real data." | "I wait until all data is 100% complete before making decisions." | **Statement A** | **Bias for Action (Bezos 70% rule)** |
| "When an incident happens, I dig into the root cause myself." | "I assign incidents to other teams and monitor from a high level." | **Statement A** | **Dive Deep** |
| "I openly voice concerns when a technical design has flaws." | "I stay quiet in design reviews to avoid friction with colleagues." | **Statement A** | **Have Backbone; Disagree and Commit** |
| "I actively look for ways to automate manual operational tasks." | "I am content following standard manual procedures repeatedly." | **Statement A** | **Invent and Simplify** |
| "I design systems for 10x future scale and modularity." | "I build only what is needed for current requirements." | **Statement A** | **Think Big** |

### 4.2 Cross-Survey Consistency Rules
- If you pick **"Data-driven investigation"** on question 7, you MUST pick **"Metrics over intuition"** on question 34.
- If you pick **"Automate repetitive tasks"** on question 12, do NOT pick **"I prefer manual step-by-step tasks"** on question 42.

---

## SECTION 5: TEST-DAY PHYSICAL & TECHNICAL CHECKLIST

- [ ] **Physical Display:** Exactly ONE monitor plugged in. Laptop closed if using external display.
- [ ] **Browser:** Full-screen mode enabled. No notifications, no tab switching.
- [ ] **External Assistance:** Zero external AI/browser extensions active. Only use HackerRank's embedded AI in Question 2.
- [ ] **Pacing:** Q1 DSA (35m) $\to$ Q2 Multi-File Repo (50m) $\to$ Q2 Test Polish (10m) $\to$ Work Simulation (15m) $\to$ Survey (10m).
