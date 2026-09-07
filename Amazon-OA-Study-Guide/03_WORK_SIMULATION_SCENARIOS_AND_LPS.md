# Amazon OA: Work Simulation Scenarios & Leadership Principles (2026)

> **Section:** Work Simulation Assessment  
> **Duration:** ~15–20 minutes (Self-paced, un-timed or generous buffer)  
> **Core Objective:** Simulate a day in the life of an Amazon SDE making high-impact decisions across ambiguous workplace situations.

---

## 1. What is the Amazon Work Simulation?

The Work Simulation presents an interactive interface replicating an Amazon internal workstation (Amazon Chime messenger, internal wiki, CloudWatch operational graphs, and simulated emails from Product Managers, Senior Engineers, and Engineering Managers).

You are given a scenario (e.g., a pending product launch, a sudden spike in latency, conflicting feature requests, or a code review dispute) and asked to evaluate 4–5 potential courses of action by rating them or picking the best option.

Every single decision is calibrated against the **Amazon Leadership Principles (LPs)**.

---

## 2. The 16 Leadership Principles & OA Interpretation

| Leadership Principle | What it Means in the Work Simulation | The "Amazonian" Choice |
| :--- | :--- | :--- |
| **Customer Obsession** | Leaders start with the customer and work backwards. | Always prioritize customer reliability, data privacy, and usability over internal team convenience or arbitrary deadlines. |
| **Ownership** | Leaders are owners. They think long term and don't sacrifice long-term value for short-term results. | Never say *"that's not my job"* or *"let another team deal with it."* Own operational quality and technical debt. |
| **Invent and Simplify** | Leaders expect innovation and always find ways to simplify. | Choose clean, automated, reusable solutions over complex, brittle manual workarounds. |
| **Are Right, A Lot** | Leaders have strong judgment and good instincts. They seek diverse perspectives. | Back up technical choices with telemetry, benchmarks, and data rather than hunches. |
| **Learn and Be Curious** | Leaders are never done learning and seek to improve themselves. | Investigate root causes, read documentation, and explore new architectural approaches when existing tools fail. |
| **Hire and Develop the Best** | Leaders raise the performance bar with every hire and promotion. | In peer feedback scenarios, give actionable, constructive coaching that elevates engineering standards. |
| **Insist on the Highest Standards** | Leaders have relentlessly high standards. | Refuse to ship buggy code or bypass security reviews just to meet a launch date. |
| **Think Big** | Thinking small is a self-fulfilling prophecy. | Design architectures that scale for 10x growth, not just next month's traffic. |
| **Bias for Action** | Speed matters in business. Many decisions are two-way doors (reversible). | When an issue is easily reversible, act quickly with calculated risk instead of waiting weeks for excessive analysis. |
| **Frugality** | Accomplish more with less. Constraints breed resourcefulness. | Optimize existing infrastructure and query efficiency before proposing expensive hardware or server fleet expansions. |
| **Earn Trust** | Leaders listen attentively, speak candidly, and treat others respectfully. | Be transparent about delays or errors; admit mistakes early and provide a clear remediation plan. |
| **Dive Deep** | Leaders operate at all levels, stay connected to the details, and audit frequently. | When an alert fires, don't just restart the server; dig into thread dumps, logs, and query plans to find root causes. |
| **Have Backbone; Disagree and Commit** | Leaders are obligated to respectfully challenge decisions when they disagree, then commit fully once decided. | Speak up if a proposed plan harms system reliability or customer trust; don't stay silent out of politeness. |
| **Deliver Results** | Leaders focus on key inputs and deliver them with quality and timeliness. | Balance technical perfection with pragmatic delivery; ship working increments that move metrics. |
| **Strive to be Earth's Best Employer** | Leaders create a safe, productive, and diverse work environment. | Ensure work distribution is sustainable and team members are supported. |
| **Success and Scale Bring Broad Responsibility** | We must be humble and thoughtful about the secondary effects of our actions. | Consider downstream security, privacy, and systemic ecosystem impacts of your code. |

---

## 3. High-Frequency Work Simulation Dilemmas & Solutions

### Scenario 1: The Looming Product Deadline vs. Test Coverage
*   **The Context:** Marketing has promised a major customer that a new API feature will launch on Friday. On Thursday afternoon, you discover an edge-case bug that will require 2 days to refactor cleanly, or you can ship a temporary bypass with minimal testing.
*   **Options Presented:**
    1. Ship the temporary bypass without tests to hit Friday's deadline; write tests next week. *(WRONG - Violates Insist on Highest Standards & Customer Obsession)*
    2. Tell the PM to cancel the feature entirely. *(WRONG - Violates Deliver Results & Earn Trust)*
    3. Meet with the PM, present the data on customer impact and risk of data corruption, recommend delaying launch by 2 days to implement the verified root-cause fix, and explore if a partial beta launch is safe. *(CORRECT - Highest Standards, Ownership, Customer Obsession)*
*   **Principle Applied:** **Insist on the Highest Standards** + **Customer Obsession**. Never ship untested code that puts customer data at risk for an internal calendar date.

---

### Scenario 2: Production Incident & Conflicting Fixes
*   **The Context:** An alert fires showing p99 latency spiked from 50ms to 2.4s. A junior engineer suggests restarting the service fleet. A senior engineer suggests rolling back the latest deployment from 3 hours ago.
*   **Options Presented:**
    1. Immediately restart the entire production fleet without checking logs. *(WRONG - Destroys volatile debugging data and may not fix root cause)*
    2. Roll back the deployment immediately to restore customer service (mitigate immediate customer impact), while simultaneously archiving log telemetry to investigate root cause in a staging environment. *(CORRECT - Customer Obsession, Bias for Action, Dive Deep)*
    3. Spend 4 hours analyzing metrics while customers experience timeouts. *(WRONG - Violates Customer Obsession & Bias for Action)*
*   **Principle Applied:** **Customer Obsession** (restore service first) followed by **Dive Deep** (find the true root cause, don't just treat the symptom).

---

### Scenario 3: Inter-Team Architectural Disagreement
*   **The Context:** Another AWS team wants to integrate with your service, but their proposed architecture requires opening a direct database connection to your MySQL cluster, bypassing your service API.
*   **Options Presented:**
    1. Allow them direct DB access to maintain a good working relationship and speed up their launch. *(WRONG - Violates Ownership & Highest Standards; creates tight coupling and security risks)*
    2. Flatly reject their request and refuse to speak with them further. *(WRONG - Violates Earn Trust)*
    3. Deny direct database access explaining security, encapsulation, and schema evolution risks; propose extending your REST/gRPC API with the specific endpoints they need to achieve their business goal. *(CORRECT - Ownership, Invent & Simplify, Earn Trust)*
*   **Principle Applied:** **Ownership** + **Earn Trust**. Protect service boundaries and long-term maintainability while helping partner teams succeed.

---

### Scenario 4: Resource Constraints & Scaling
*   **The Context:** Your service is projected to handle 5x more requests during Prime Day. The current server fleet CPU utilization is 60%.
*   **Options Presented:**
    1. 5x the server fleet size immediately by purchasing more EC2 instances. *(WRONG - Violates Frugality and Invent & Simplify)*
    2. Do nothing and hope auto-scaling handles it. *(WRONG - Violates Ownership)*
    3. Profile the application endpoints to identify bottlenecks (e.g., unindexed queries, redundant API calls, lack of caching); implement Redis caching on the read-heavy path and benchmark before sizing the fleet. *(CORRECT - Frugality, Dive Deep, Think Big)*
*   **Principle Applied:** **Frugality** + **Dive Deep**. Profile and optimize software architecture before throwing expensive compute at unoptimized code.

---

## 4. The Decision Filter: Rank Your Priorities

Whenever you are presented with multiple choices in the Work Simulation, use this strict hierarchy:

```
1. Customer Data Safety & Availability (Absolute Priority)
   └── 2. Long-term Code Quality & Maintainability (Ownership)
       └── 3. Data-Driven Root Cause Investigation (Dive Deep)
           └── 4. Transparent Stakeholder Communication (Earn Trust)
               └── 5. Internal Timelines / Feature Deadlines (Reversible)
```
