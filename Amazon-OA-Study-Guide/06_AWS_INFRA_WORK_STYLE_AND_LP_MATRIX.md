# AWS Infrastructure SDE: Work Style & Leadership Principles Matrix (2026)

> **Context:** Tailored specifically for **AWS Workshop Studio / AWS Platform Infrastructure SDE (Job ID: 10503637)**.  
> **Candidate Profile:** Sai Likhith Kanuparthi (Senior Systems & AI Infrastructure Engineer, AWS SAP-C02, Bedrock/AgentCore, Southwest/Airbnb Distributed Platforms).  
> **Purpose:** Map every forced-choice pair in the **Amazon Work Style Survey** and every situational dilemma in the **Work Simulation** to Amazon's **16 Leadership Principles** through the lens of **AWS cloud infrastructure, distributed fleets, and multi-account platform engineering**.

---

## 1. The AWS Infrastructure SDE Persona (Your Core Anchor)

In AWS engineering, especially for platform teams like **Workshop Studio (Content Catalog, Events Service, Account Management Service)**, you are evaluated through a distinct archetype:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AWS INFRASTRUCTURE SDE PERSONA (ARCHETYPE)                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • HIGH AGENCY & FLEET-WIDE OWNERSHIP:                                                  │
│   You view 100,000+ isolated AWS accounts as your personal blast radius responsibility.│
│ • RADICAL AUTOMATION OVER MANUAL TOIL:                                                 │
│   If an action must be repeated twice, it belongs in an idempotent CDK construct or   │
│   automated Step Functions state machine.                                              │
│ • ZERO-BLAST-RADIUS DEFENSE:                                                           │
│   Strict IAM boundaries, VPC isolation, KMS key rotation, and automated resource       │
│   sweeping to eliminate stranded cloud costs and security leaks.                       │
│ • METRIC-FIRST & TELEMETRY OBSESSED:                                                   │
│   No architectural assertions without CloudWatch percentiles (p99 < 200ms),            │
│   dead-letter queues (DLQ), and synthetic canaries.                                    │
│ • TWO-WAY DOOR AGILITY VS ONE-WAY DOOR RIGOR:                                          │
│   Fast experimentation on API iterations; relentless, uncompromising rigor on data     │
│   isolation, multi-tenant security, and 24/7 fleet resilience.                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

When taking the **Work Style Survey** and **Work Simulation**, your answers must consistently reflect this Senior AWS Infrastructure Engineer persona.

---

## 2. The 16 Leadership Principles Mapped to AWS Infrastructure & Fleet Ops

| # | Leadership Principle | AWS Platform / Fleet Meaning | Candidate Real-World Proof Point | "Most Like Me" Winning Behavioral Stance |
|---|---|---|---|---|
| **1** | **Customer Obsession** | Customer = AWS workshop participants & event organizers. Zero failed account provisions, zero leaked credentials, sub-second event setup. | Scaled BPI VA from 600 to 10K rows/run, serving 55+ internal operations analysts across customer trust/safety. | *"I prioritize eliminating customer-facing friction and API errors over internal team convenience or arbitrary feature milestones."* |
| **2** | **Ownership** | You own the fleet lifecycle from account vending to teardown. No "stranded resources" or "orphaned EC2 instances." | Owned failing IAT token expiration system built by another team; fixed root cause in 2 hrs, zero mid-run drops. | *"I take full end-to-end responsibility for upstream and downstream service health, never dismissing an operational issue as 'someone else's service'."* |
| **3** | **Invent and Simplify** | Automating multi-account infrastructure deployment and content review via agentic pipelines instead of manual reviews. | Architected Bedrock/AgentCore runtime unifying 30+ LLMs; built KC-to-Flowchart tool slashing authoring from days to minutes. | *"I actively eliminate complex manual procedures by designing simple, self-healing automated workflows."* |
| **4** | **Are Right, A Lot** | Validating distributed architectures with empirical benchmarks, traffic profiles, and chaos game days. | Benchmarked 23 prompt/model versions across 1,690 ground-truth samples with counterfactual flip analysis. | *"I rely on data, metrics, and empirical testing to make technical decisions, welcoming alternative data that disproves my hypothesis."* |
| **5** | **Learn and Be Curious** | Diving deep into emerging AWS primitives (Bedrock Agents, Guardrails, Karpenter, Graviton) to optimize platform economics. | Author of Cambridge book chapter on State Space Models; upstream contributor to LiveKit Agents, Ragas, and LiteLLM. | *"I continuously explore new technologies and architectural paradigms to uncover non-obvious optimizations."* |
| **6** | **Hire and Develop the Best** | Raising the team's engineering bar through rigorous code reviews, automated CI gates, and mentorship. | Instituted 6-lens code review checklist and 80/10/10 test methodology; authored on-call runbooks. | *"I invest time in giving constructive, actionable technical feedback that elevates code quality across the team."* |
| **7** | **Insist on the Highest Standards** | Never bypassing multi-tenant security boundaries, VPC isolation, or unit/integration test coverage for speed. | Maintained 99.9% uptime on FDA 21 CFR Part 11 platform; enforced zero regression release gating. | *"I refuse to compromise on security boundaries, automated test coverage, or operational monitoring to rush a deployment."* |
| **8** | **Think Big** | Architecting account provisioning fleets to scale 10x (from 10K to 100K concurrent event participants). | Designed Southwest event-streaming platform sustaining 4M req/min sub-second throughput. | *"I design systems with future orders-of-magnitude scale and modular extensibility in mind from day one."* |
| **9** | **Bias for Action** | Recognizing two-way door decisions (API schema tweaks, caching parameters) and shipping calculated iterations quickly. | Deployed transformer model at Shell with feature-flag rollback in 2 weeks, reclaiming 20 hrs/week. | *"I prefer making calculated, reversible decisions quickly to test hypotheses in production rather than waiting for exhaustive certainty."* |
| **10** | **Frugality** | Minimizing AWS account idle spend, aggressive resource recycling, DynamoDB on-demand vs provisioned optimization. | Optimized Bedrock inference token caching and query compaction, eliminating redundant model calls. | *"I look for ways to optimize compute and resource utilization before requesting expanded infrastructure budgets."* |
| **11** | **Earn Trust** | Transparent communication during outages; blameless post-mortems (Correction of Errors - CoE) with permanent remediation. | Resolved cross-team boundary conflict with Alex via a formal validation response contract rather than political escalation. | *"I am transparent about technical trade-offs, admit mistakes openly, and communicate proactively with stakeholders."* |
| **12** | **Dive Deep** | Not just restarting failed Lambda workers, but analyzing memory profiles, thread contention, and CloudWatch traces. | Root-caused Sandcastle daemon thread token leak under 2 hours by inspecting low-level session lifetimes. | *"I inspect low-level system metrics, query execution plans, and logs myself to uncover true root causes."* |
| **13** | **Have Backbone; Disagree and Commit** | Voicing architectural objections when a partner team requests unvetted direct database access; committing fully once resolved. | Defended API isolation over direct DB coupling, delivering a custom REST contract that satisfied partner requirements. | *"I challenge technical proposals that jeopardize system reliability or security, but execute with full commitment once a decision is finalized."* |
| **14** | **Deliver Results** | Delivering resilient services on schedule despite operational ambiguity, on-call spikes, and shifting requirements. | Resolved 191 JIRA tickets across 6 weeks on Lilly 1.2 release, shipping on time with 99.9% uptime. | *"I stay focused on core business deliverables, breaking complex initiatives into working, iterative increments."* |
| **15** | **Strive to be Earth's Best Employer** | Ensuring on-call rotations are sustainable by automating alerts, eliminating false alarms, and preventing burnout. | Reduced on-call MTTR by 73% at Southwest via automated Dead Letter Queue (DLQ) replay scripts. | *"I prioritize building sustainable operational tooling so my teammates are not overwhelmed by repetitive operational toil."* |
| **16** | **Success and Scale Bring Broad Responsibility** | Designing ethical AI agents, enforcing data privacy (Presidio PII redaction), and protecting multi-tenant account boundaries. | Integrated Microsoft Presidio across 12 PII entity types, ensuring zero raw data leakage to foundation models. | *"I carefully assess the downstream privacy, security, and ethical impacts of the infrastructure and models we deploy."* |

---

## 3. Work Simulation: High-Frequency Infrastructure Scenarios & The Amazonian Choice

### Scenario A: The Account Vending Fleet Bottleneck
*   **The Dilemma:** AWS GameDay starts in 3 hours with 5,000 participants. The Account Management Service queue is backing up because account provisioning takes 4 minutes per account. The PM asks if you can disable the VPC security scan and IAM permission boundary checks to speed up provisioning to 30 seconds.
*   **Analysis:**
    - *Option 1 (Disable Security):* Unacceptable. In AWS, security is Job Zero. Bypassing IAM boundaries violates **Insist on the Highest Standards** and can allow participant privilege escalation into production AWS assets.
    - *Option 2 (Cancel Event):* Violates **Customer Obsession** and **Deliver Results**.
    - *Option 3 (The Amazonian Choice):* Reject disabling security controls (**Insist on the Highest Standards**). Implement a hot-pool pre-warming strategy: immediately batch-provision a pool of pre-warmed accounts using a temporary burst limit increase in AWS Service Quotas, parallelize the deployment across multiple regions, and communicate the exact regional allocation to the PM (**Bias for Action**, **Customer Obsession**, **Invent and Simplify**).

---

### Scenario B: CloudWatch Alarms & Noisy On-Call Pagers
*   **The Dilemma:** You take over the on-call pager for Workshop Studio's Events Service. A high-severity alarm (`AccountRecycleTimeoutAlarm`) fires 14 times a night, but 90% of the time, the account simply takes 30 seconds longer to delete S3 buckets and eventually resolves itself. A teammate suggests muting the alarm.
*   **Analysis:**
    - *Option 1 (Mute Alarm):* Violates **Ownership** and **Dive Deep**. Muting alarms hides silent failures.
    - *Option 2 (The Amazonian Choice):* Do NOT mute the alarm. **Dive Deep** into CloudWatch metrics: why are S3 bucket deletions taking longer? Discover that versioned S3 buckets require multi-threaded batch deletions. Adjust the alarm threshold to reflect the true failure boundary ($> 10$ min) to protect team sustainability (**Earth's Best Employer**), while opening an operational ticket to implement asynchronous parallel batch deletion in the cleanup worker (**Ownership**, **Frugality**).

---

### Scenario C: Cross-Service API Contract vs. Direct Data Access
*   **The Dilemma:** The AWS Content Catalog service needs to know if a workshop's infrastructure template has ever failed deployment in the Events Service. The Content Catalog engineer asks for direct read access to your PostgreSQL database tables so they can join the tables directly in their query.
*   **Analysis:**
    - *Option 1 (Grant DB Access):* Violates **Ownership** and the Two-Pizza Team API contract rule. Direct database sharing couples schemas, leaks connection pools, and breaks service isolation.
    - *Option 2 (Refuse without alternative):* Violates **Earn Trust** and **Deliver Results**.
    - *Option 3 (The Amazonian Choice):* Respectfully decline direct database access (**Have Backbone**). Explain the encapsulation, connection exhaustion, and schema migration risks. Propose a lightweight gRPC/REST endpoint or emit an Amazon EventBridge event (`TemplateDeploymentResult`) that the Content Catalog service can subscribe to and cache locally (**Invent and Simplify**, **Earn Trust**).

---

### Scenario D: AI Agent Hallucination in Workshop Content Review
*   **The Dilemma:** The team is rolling out an AI agent to automatically review community-submitted workshop CDK code. During beta testing, the agent hallucinated and approved a CDK template that opened security group port 22 (SSH) to `0.0.0.0/0`.
*   **Analysis:**
    - *Option 1 (Shut down AI project):* Violates **Think Big** and **Invent and Simplify**.
    - *Option 2 (Ship anyway and rely on user reporting):* Violates **Customer Obsession** and **Insist on Highest Standards**.
    - *Option 3 (The Amazonian Choice):* Implement deterministic defense-in-depth (**Insist on Highest Standards**, **Success and Scale Bring Broad Responsibility**). The AI agent should propose reviews, but deterministic AST / cdk-nag security guardrails must execute as an unbypassable policy gate. Log the failure in the evaluation dataset to retrain the prompt harness (**Dive Deep**, **Learn and Be Curious**).

---

## 4. Work Style Survey: Infrastructure-Calibrated Forced-Choice Pairs

In the **Work Style Survey**, you will encounter forced-choice pairs. Use these calibrations to select the **"Most Like Me"** option:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        INFRASTRUCTURE FORCED-CHOICE MATRIX                             │
├───────────────────────────────────────┬────────────────────────────────────────────────┤
│ CHOICE A                              │ CHOICE B                                       │
├───────────────────────────────────────┼────────────────────────────────────────────────┤
│ "I prioritize long-term system        │ "I prioritize delivering immediate feature     │
│  reliability and automated tests even │  requests to meet short-term deadlines."       │
│  if it requires extra upfront effort."│                                                │
│  >>> WINNER: CHOICE A (Ownership)     │                                                │
├───────────────────────────────────────┼────────────────────────────────────────────────┤
│ "I am comfortable taking calculated   │ "I prefer to wait until all operational        │
│  risks and rolling out reversible     │  uncertainties are 100% resolved before        │
│  changes to learn quickly."           │  shipping anything to production."             │
│  >>> WINNER: CHOICE A (Bias for Action│                                                │
├───────────────────────────────────────┼────────────────────────────────────────────────┤
│ "When an operational incident occurs, │ "When an operational incident occurs,          │
│  I inspect metrics and trace the root │  I focus on restarting the service and         │
│  cause to ensure it never recurs."    │  defer root-cause investigation to backlog."   │
│  >>> WINNER: CHOICE A (Dive Deep)     │                                                │
├───────────────────────────────────────┼────────────────────────────────────────────────┤
│ "I openly voice concerns when a plan  │ "I avoid conflict in architecture reviews to   │
│  could jeopardize data security or    │  maintain harmony among team members."         │
│  system scalability."                 │                                                │
│  >>> WINNER: CHOICE A (Have Backbone) │                                                │
├───────────────────────────────────────┼────────────────────────────────────────────────┤
│ "I seek to simplify complex systems   │ "I prefer to maintain existing procedures      │
│  by replacing manual maintenance with │  because they are already familiar to the      │
│  automated, self-healing code."       │  team."                                        │
│  >>> WINNER: CHOICE A (Invent/Simplify│                                                │
└───────────────────────────────────────┴────────────────────────────────────────────────┘
```

---

## 5. Summary: The Golden Rules for Your Test Day

1. **Be Decisive:** Choose strong statements (**"Most Like Me"**). Avoid the weak middle ground.
2. **Be Consistent:** If you favor automated root-cause fixes over band-aids on question 3, choose that same philosophy when rephrased on question 41.
3. **Security is Job Zero:** Never pick any option in the Work Simulation that compromises IAM roles, customer data, encryption, or security scans.
4. **Data Over Opinion:** Whenever a scenario offers a choice between *"discussing what people think"* vs. *"analyzing CloudWatch logs / running a canary"*, **choose the canary and data analysis**.
