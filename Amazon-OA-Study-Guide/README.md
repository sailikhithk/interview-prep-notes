# Amazon Online Assessment (OA) — Master Strategy & Execution Guide (2026)

> **Role Focus:** AWS / Amazon Software Development Engineer (SDE)  
> **Platform:** HackerRank Full-Screen IDE + Proctored Environment  
> **Total Time:** ~125–150 minutes (100 min Coding + ~15 min Work Simulation + ~10 min Work Style Survey)  
> **Delivery Window:** Within 7 calendar days of invitation  

---

## 1. Executive Assessment Breakdown

Amazon's 2026 SDE Online Assessment consists of three core components executed sequentially in one sitting.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               AMAZON SDE OA ARCHITECTURE                               │
├────────────────────────────────┬──────────────────────────┬────────────────────────────┤
│ 1. CODING CHALLENGE (100 min)  │ 2. WORK SIMULATION (15 m)│ 3. WORK STYLE SURVEY (10 m)│
├────────────────────────────────┼──────────────────────────┼────────────────────────────┤
│ • Part A: Traditional DSA (1Q) │ • Interactive Workplace  │ • 2 Personality Surveys   │
│   Arrays/Strings, Slid. Window,│   Email, Slack, Metrics  │ • Ipsative Forced-Choice   │
│   Hash Maps, Two Pointers, DP  │ • Architectural Decisions│   ("Most Like Me" vs       │
│ • Part B: Code Repository (1Q) │ • Ambiguity & Trade-offs │    "Least Like Me")        │
│   Multi-file project with AI   │ • 16 Amazon Leadership   │ • 100% Alignment with     │
│   assistant; bug fixing & tests│   Principles (LPs)       │   Amazon Leadership Ethics │
└────────────────────────────────┴──────────────────────────┴────────────────────────────┘
```

---

## 2. Component Specifications & Time Budget

| Section | Time Allocated | Question Count | Format & Tech Environment | Evaluation Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Section 1: Traditional DSA** | ~40–45 mins | 1 Question | HackerRank standard editor; Python 3, Java, C++, Go, etc. | Time/Space complexity, boundary conditions, all hidden test cases passed |
| **Section 2: Code Repository + AI** | ~50–55 mins | 1 Question | Full-stack project directory, file tree, test runner, embedded AI helper | Code navigation, diagnostic speed, regression avoidance, test pass rate |
| **Section 3: Work Simulation** | ~15–20 mins | 4–6 Scenarios | Simulated AWS internal work environment (Chime/Slack, emails, logs, metrics charts) | Prioritization, long-term architectural stability, customer focus vs speed |
| **Section 4: Work Style Survey** | ~10–15 mins | 2 Surveys (~30-50 pairs) | Forced-choice paired statements ("Most like me" / "Least like me") | Consistency, High Agency, Customer Obsession, Ownership, Bias for Action |

---

## 3. Section-by-Section Battle Plan

### Part 1: Traditional Code Writing (DSA)
*   **Dominant Question Patterns:**
    1.  **Sliding Window & Two Pointers:** Substrings with character frequency constraints, maximum profit / window sum.
    2.  **Monotonic Stack / Deque:** Next greater element, histogram areas, stock price spans, sliding window maximum.
    3.  **Hash Table & Prefix Sums:** Subarray sums divisible by $k$, frequency balance, anagram groups.
    4.  **Graph BFS / DFS & Grid Traversal:** Shortest delivery routes, connected server clusters, rotten oranges / virus spread variants.
    5.  **Greedy & Priority Queue (Min/Max Heap):** Warehouse package consolidation, server task scheduling, minimum cost to connect ropes.
*   **Execution Protocol:**
    - Read input constraints first: $N \le 10^5 \implies O(N)$ or $O(N \log N)$ required; $O(N^2)$ will TLE.
    - Write out edge cases before coding: empty arrays, 1-element arrays, all duplicates, negative numbers, large numbers causing overflow.
    - Run custom test cases covering zero, extremes, and off-by-one indices before hitting "Submit".

---

### Part 2: Code Repository + AI Coding Assistant (2026 Format)
Amazon's 2026 assessment evaluates modern SWE productivity inside a multi-file project repository.

```
project_root/
├── src/
│   ├── api/routes.py
│   ├── services/order_service.py
│   └── models/order.py
├── tests/
│   ├── test_order_service.py
│   └── test_api.py
├── requirements.txt / pom.xml / package.json
└── README.md
```

*   **How the AI Assistant Works:**
    - A specialized internal conversational assistant is embedded inside the HackerRank IDE.
    - It can answer questions about the codebase structure, explain stack traces, or suggest edits.
*   **The Traps to Avoid:**
    - **Prompt Dumping:** Asking the AI to "fix all bugs" will result in generic hallucinations or broken imports.
    - **Language Lock-in:** You choose your language at the start of Question 2 and **cannot switch**. Pick Python or Java based on what you are fastest at reading and testing.
    - **Blind Copy-Pasting:** The AI might introduce subtle regressions that break existing unit tests. Always inspect diffs.
*   **Step-by-Step AI Workflow:**
    1. Run the test suite first (`pytest` or `mvn test` button) to see which tests fail and capture the stack traces.
    2. Ask the AI targeted questions: *"In `order_service.py`, what causes `test_concurrent_checkout` to raise `StaleObjectException`?"*
    3. Review the AI's diagnosis, examine the line in the file, and make the surgical fix.
    4. Re-run tests locally and verify 100% green before submitting.

---

### Part 3: Work Simulation (AWS Workplace Scenario)
*   **Interface Simulation:** You play an SDE at Amazon. You receive incoming tickets, emails from Product Managers (PMs), alerts from CloudWatch, and requests from teammates.
*   **Core Decision Matrix:**
    - **Customer Impact > Internal Convenience:** Never choose an option that compromises customer uptime or data privacy to meet a team deadline.
    - **Root Cause Fix > Band-Aid:** Choose the root-cause bugfix with automated regression tests over a quick monkey-patch, unless an active production P0 outage requires an immediate rollback first.
    - **Data-Driven > Intuition:** When choosing between two designs, choose the option that involves running an A/B test, profiling telemetry, or checking metrics over "what feels right."
    - **Ownership & Long-Term Scalability:** Never say *"That's not my service / team, I will ignore it."* Instead, coordinate with the owner service, log an issue, or offer assistance.

---

### Part 4: Work Style Survey (Ipsative Forced-Choice)
*   **The Structure:**
    - Two statements are presented (e.g., Statement A vs. Statement B).
    - You must mark one as **"Most Like Me"** and the other as **"Least Like Me"** (or a 5-point spectrum between them).
*   **The Scoring Mechanism:**
    - Measures alignment with the **16 Amazon Leadership Principles**.
    - It tests **Consistency**: Similar questions are repeated in reverse phrasing 30 questions later. Contradicting yourself docks authenticity points.
    - Extreme neutrality (picking the middle ground) is scored negatively; Amazon looks for decisive engineers with high conviction.

---

## 4. Test-Day Checklist & Proctoring Guardrails

1. **Hardware & Environment Setup:**
   - **Strict Single Monitor Only:** HackerRank detects external displays. Disconnect secondary monitors or close your laptop lid if using an external monitor.
   - **Full-Screen Browser IDE:** No switching tabs, minimizing windows, or opening external developer tools. Doing so triggers focus-loss proctoring flags.
   - **Webcam/ID Verification:** Have a government photo ID ready if prompted. Ensure lighting is front-facing.
2. **Timing Protocol (Total 100 min for Coding):**
   - **Minute 0–40:** Traditional DSA question. Aim to solve, optimize, and submit within 35–40 minutes.
   - **Minute 40–95:** Code Repository question. Spend 5 min exploring the file tree and running tests, 30 min fixing bugs with AI, 15 min edge-case testing and verifying.
   - **Minute 95–100:** Buffer to review submissions.
3. **Follow-on Sections (Work Sim + Survey):**
   - Do not rush through the simulation. Read the simulated charts and emails carefully.
   - Maintain consistent Amazon persona through the final survey.

---

## 5. Study Guide Artifacts in this Repository

| [00_MASTER_SYSTEM_INSTRUCTIONS_AMAZON_OA.md](00_MASTER_SYSTEM_INSTRUCTIONS_AMAZON_OA.md) | **Master Operating Instructions & Real-Time Strategy** | Complete Copilot Architecture, Repo Protocol & Rules of Engagement |
| [01_AMAZON_CODING_PATTERNS_AND_ALGORITHMS.md](01_AMAZON_CODING_PATTERNS_AND_ALGORITHMS.md) | Top Amazon OA DSA patterns with clean Python 3 templates | Section 1 (DSA) |
| [02_CODE_REPOSITORY_AND_AI_ASSISTANT_PLAYBOOK.md](02_CODE_REPOSITORY_AND_AI_ASSISTANT_PLAYBOOK.md) | How to navigate multi-file codebases & prompt the AI assistant | Section 2 (Code Repo) |
| [03_WORK_SIMULATION_SCENARIOS_AND_LPS.md](03_WORK_SIMULATION_SCENARIOS_AND_LPS.md) | Real scenario questions, email decisions, and trade-off formulas | Section 3 (Work Sim) |
| [04_WORK_STYLE_SURVEY_FORCED_CHOICE_STRATEGY.md](04_WORK_STYLE_SURVEY_FORCED_CHOICE_STRATEGY.md) | Ipsative survey pair breakdown & consistency matrices | Section 4 (Survey) |
| [05_HACKERRANK_ENVIRONMENT_AND_PROCTORING_FAQ.md](05_HACKERRANK_ENVIRONMENT_AND_PROCTORING_FAQ.md) | Environment gotchas, single-monitor setup, language rules | Test Day Rules |
| [06_AWS_INFRA_WORK_STYLE_AND_LP_MATRIX.md](06_AWS_INFRA_WORK_STYLE_AND_LP_MATRIX.md) | **AWS Infrastructure SDE / Workshop Studio LP Matrix** | Section 3 & 4 (Customized to AWS Multi-Account Fleet, AI Agents & Distributed Platforms) |
