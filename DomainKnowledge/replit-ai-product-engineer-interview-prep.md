# Replit — Sr/Staff AI Product Engineer Interview Prep

> **Role**: Sr/Staff AI Product Engineer — Product Foundry
> **Company**: Replit ($9B Series D, 550M+ ARR, 2.5M→550M in <17 months)
> **Recruiter**: Mike Hauschild (ex-Founding Recruiter @ ASAPP, 500+ hires)
> **Location**: Foster City, CA — **hybrid 3 days/week (BLOCKER — you're in Houston)**
> **Team**: Product Foundry — internal startup within Replit, 0→1 product building
> **Foundation**: Primary anchor is **Airbnb GenAI** (BPI VA, Redpen, FacadeDriver, Loki evals), NOT DMS

---

## CRITICAL: Location mismatch — resolve first

**Foster City hybrid 3 days/week. You're in Houston.** This is the first question for Mike:

> "I'm based in Houston. The role is hybrid in Foster City, 3 days/week. Is there any flexibility on remote, or is relocation required? I'm open to discussing relocation if the fit is right, but I want to understand the constraint before we go deeper."

**Possible outcomes:**
1. **Hard no on remote** → you decide: relocate to Bay Area or pass. Replit at $9B + Product Foundry is worth considering relocation for.
2. **Negotiable** → some Product Foundry teams are distributed. Push gently.
3. **Relocation package** → Replit is well-funded, ask if they cover it.

**Do not skip this.** It's Tier 1. If you can't relocate and they can't flex, the rest of the prep is moot.

---

## How to use this file

Unlike Capital One (where DMS is your foundation), **Replit is an AI product role**. Your primary anchor is **Airbnb GenAI** — BPI Virtual Analyst, Redpen, FacadeDriver (30+ LLMs), Loki eval harness. Secondary anchors: Lilly (full-stack regulated), Southwest (Angular + streaming), portfolio sites (Next.js/React production).

The DMS guide transfers for **full-stack depth** (Spring Boot, JPA, React) but the core of this interview is **AI product engineering**: building AI-powered products from 0→1, LLM orchestration, eval harnesses, agent architecture, shipping customer-facing AI.

**Study order:** Section 1 (is this role right for you) → Section 2 (AI product engineering) → Section 3 (Replit-specific) → Section 4 (your 0→1 stories) → Section 5 (questions for Mike).

---

## 1. Is this role right for you? (honest fit check)

### What Replit Product Foundry wants
- Engineers who **build products, not just infrastructure**
- Thrive in **ambiguity**, move quickly
- **0→1 ownership**: concept → launch
- **Customer-facing products** from idea to production
- **AI-native product development** — work on the frontier of how software gets created

### Your fit (honest assessment)

| Signal | You have it? | Evidence |
|---|---|---|
| Build products, not just infra | ✅ YES | BPI VA (sole owner, customer-facing Python co-pilot for 55+ analysts), Redpen UI (sole owner) |
| Thrive in ambiguity | ✅ YES | Airbnb GenAI platform — 30+ LLMs, no playbook, you built the orchestration |
| 0→1 ownership | ✅ YES | BPI VA was 0→1 — you built it from concept to production serving 55+ analysts |
| Customer-facing products | ✅ YES | BPI VA is customer-facing (analysts are internal customers), Redpen is customer-facing |
| AI-native product development | ✅ YES | LLM orchestration, eval harnesses, agentic workflows at Airbnb |
| Full-stack (product, not just infra) | ✅ YES | Lilly (Spring Boot + React/TS), Southwest (Flask/Django + Angular), portfolio (Next.js 16) |
| Ship at startup speed | ⚠️ PARTIAL | Airbnb is big-company pace. Lilly was contract. You've shipped fast at Southwest (95% coverage in 12 months). Frame as "I've shipped at both speeds." |

### Level check: Sr/Staff
- Replit "Sr/Staff" — you're L9 Senior (7+ YOE). Staff is L10 stretch.
- Per memory: L9 is green, L10 is yellow stretch. This is a **stretch role but legitimate**.
- Frame as: "I'm senior-level, owned apps end-to-end, built 0→1 products. Staff scope is where I'm heading, and Product Foundry is the kind of environment where I'd grow into it fast."

### Honest gap
- **No prior AI coding agent experience** — you haven't built a coding agent (Replit Agent). But you've built AI products (BPI VA co-pilot for analysts) and you understand the agent space (agentic workflows, tool use, eval harnesses at Airbnb).
- **Foster City location** — see critical flag above.

---

## 2. AI Product Engineering (core of this interview)

### 2.1 LLM Orchestration (your strongest card — lead with this)

**Q-R1: How do you orchestrate 30+ LLMs behind a unified interface?**

> **Your anchor (Airbnb)**: "At Airbnb I built the FacadeDriver — a unified abstraction layer over 30+ LLMs across Azure, Bedrock, Vertex, and vLLM. The pattern is: a common interface (`generate(prompt, params)`) with provider-specific adapters underneath. The FacadeDriver handles routing (which model for which task), fallbacks (if Azure is down, fail to Bedrock), retries (idempotency keys + circuit breakers), and cost tracking. BPI Virtual Analyst uses this to serve 55+ analysts with the right model for each task — cheap models for triage, expensive models for complex reasoning."

**Follow-ups to expect:**
- **Model routing**: "How do you decide which model for which task?" → Eval harness scores per task, route by cost/latency/quality tradeoff. Cheap models (Haiku/Mini) for classification, expensive (Opus/Sonnet) for reasoning.
- **Fallback strategy**: "What if a provider is down?" → Circuit breaker (Resilience4j), fail to next provider, log the fallback for post-mortem.
- **Cost control**: "How do you manage spend?" → Per-request cost tracking, monthly budgets per app, alerting on anomalies, cache common prompts.

### 2.2 Eval Harnesses (your second strongest card)

**Q-R2: How do you evaluate LLM output quality at scale?**

> **Your anchor (Airbnb)**: "I operated Loki — Airbnb's eval harness for LLM outputs. The pattern is: (1) golden dataset per use case (human-labeled examples), (2) automated evals (LLM-as-judge for reasoning tasks, exact match for extraction, BLEU/ROUGE for generation), (3) regression suite — every model change runs against the golden set before shipping, (4) human review for edge cases. At Airbnb I ran evals before every model upgrade — if the new model scored lower on the golden set, we didn't ship it. This is the same discipline as unit tests, but for non-deterministic outputs."

**Follow-ups:**
- **LLM-as-judge bias**: "How do you handle judge bias?" → Rotate judges, cross-check with human labels, track agreement rate.
- **Golden dataset drift**: "What if the golden set is stale?" → Refresh quarterly, sample production traffic, human-label new patterns.
- **Production monitoring**: "How do you catch regressions in production?" → Sample 1% of outputs, score with eval harness, alert if quality drops below threshold.

### 2.3 AI Coding Agents (Replit's domain — study this)

**Q-R3: How would you build an AI coding agent that can autonomously complete development tasks?**

> **Expected**: An AI coding agent is an LLM with:
> 1. **Tools** — file read/write, shell execution, search, test runner, browser
> 2. **Planning** — break the task into steps (ReAct, plan-then-execute, or tree-of-thought)
> 3. **Memory** — context window + retrieval (codebase search, conversation history)
> 4. **Verification** — run tests, compile, lint, iterate on failures
> 5. **Safety** — sandbox execution, human approval for destructive ops, rollback
>
> **Your anchor**: "At Airbnb I build AI co-pilots for analysts — BPI VA is an agent that reads, reasons, and acts on analyst workflows. The patterns transfer to coding agents: tool use (function calling), planning (ReAct loops), verification (run tests, check output), and safety (sandbox, human-in-the-loop for destructive actions). The difference is the domain — analysts vs developers — but the agent architecture is the same. Replit Agent is the most ambitious version of this, and I'd want to work on pushing the frontier of what coding agents can do."

**Study up on (if you don't know these, learn before the interview):**
- **ReAct** (Reasoning + Acting) — the dominant agent loop pattern
- **Tool use / function calling** — OpenAI/Anthropic function calling API
- **SWE-bench** — the benchmark for coding agents (know what it is)
- **Cursor / Copilot / Devin / Claude Code** — the competitive landscape
- **Replit Agent** — try it before the interview, know what it does

### 2.4 0→1 Product Building (Product Foundry's core)

**Q-R4: Walk me through a product you built from 0→1.

> **Your anchor (BPI VA)**: "BPI Virtual Analyst was 0→1. Analysts were spending 40% of their day on repetitive triage. I identified the pain point by shadowing analysts, prototyped a Python co-pilot orchestrating 30+ LLMs behind a FacadeDriver, shipped it to 55+ analysts, and iterated based on feedback. The key decisions: (1) start with the highest-pain workflow (triage), not the coolest AI feature, (2) ship a working version in weeks, not months, (3) measure impact (analyst triage time cut by X%), (4) iterate based on what users actually did, not what they said they wanted. That's the Product Foundry playbook — identify, prototype, launch, iterate."

**Q-R5: How do you decide what to build when the idea is ambiguous?**

> **Your anchor**: "At Airbnb the mandate was 'build an AI co-pilot for analysts' — that's ambiguous. I resolved it by: (1) shadowing 5 analysts for a week to find the highest-pain workflow, (2) prototyping 3 different approaches in a week each, (3) picking the one that analysts actually used, not the one that was technically impressive. The lesson: ambiguity is resolved by user contact, not more thinking. Ship something, watch users, iterate. Product Foundry's 'turn ambiguous ideas into products' is exactly this — the ambiguity is a feature, not a bug, because it means you get to define the product."

### 2.5 Agentic Workflows (hot topic — know this cold)

**Q-R6: How do you build a reliable agentic workflow? LLMs are non-deterministic.**

> **Expected**: 
> 1. **Structured output** — JSON schema, function calling, not free-text parsing
> 2. **Tool use with validation** — agent proposes an action, system validates before executing
> 3. **Human-in-the-loop** for destructive or irreversible actions
> 4. **Idempotency** — agent retries are safe (same action twice = same result)
> 5. **Observability** — log every step, every tool call, every LLM response
> 6. **Eval harness** — regression test the agent on a golden dataset
> 7. **Cost + latency budgets** — agents can loop forever; set hard limits
>
> **Your anchor**: "At Airbnb I build agentic workflows for BPI VA. The reliability stack is: structured output (function calling, not parsing), tool validation (agent proposes, system validates), human-in-the-loop for destructive ops, idempotency for retries, and an eval harness for regressions. The non-determinism is managed, not eliminated — you constrain the agent's action space, verify outputs, and have a human checkpoint for anything irreversible. This is the same pattern as DMS Q66 — system-wide safety, not point fixes."

---

## 3. Replit-Specific Questions

### Q-R7: Why Replit?

> **Your anchor**: "Replit is defining a new category — software creation through natural language. The Agent is the most ambitious coding agent in production, and Product Foundry is where new AI-powered experiences get built from 0→1. I've spent the last 20 months at Airbnb building AI co-pilots for analysts — BPI VA, Redpen, LLM orchestration for 30+ models, eval harnesses. Product Foundry is the team where that experience compounds: 0→1 ownership, ship to tens of millions of developers, startup speed with $9B backing. I want to build the future of how software gets created, not just maintain existing systems."

**Don't say**: "I'm passionate about AI" (cliché). **Don't say**: "Replit is a great company" (flattery). **Do say**: the 0→1 + AI coding agent + your Airbnb GenAI experience mapping.

### Q-R8: Why Product Foundry specifically?

> **Your anchor**: "Product Foundry is an internal startup within a startup — lean team, direct access to leadership, 0→1 ownership, ship to millions. That's the environment where I do my best work. At Airbnb I owned BPI VA end-to-end, from shadowing analysts to find the pain point, to prototyping, to shipping to 55+ analysts, to iterating. I didn't own a piece of a large system — I owned the whole thing. Product Foundry is that model at Replit scale. The 'turn ambiguous ideas into products used by millions' framing is exactly what I've been doing, just at a smaller scale. I want to do it at Replit scale."

### Q-R9: What's your experience with AI coding tools?

> **Your anchor (honest)**: "I use AI coding tools daily — Claude Code, Cursor, Copilot. At Airbnb I build AI co-pilots for analysts, not for developers, but the patterns are the same: LLM orchestration, tool use, eval harnesses, agentic workflows. I've also studied the coding agent space — SWE-bench, ReAct, tool use patterns. I tried Replit Agent before this call — [share one specific observation about what it did well or where it struggled]. The gap between my Airbnb work and Replit Agent is the domain (analysts vs developers), not the AI engineering. I'd ramp on the coding-agent-specific patterns in weeks."

**Before the interview**: try Replit Agent on a real task. Note one thing it did well, one thing it struggled with. That's your specific observation.

### Q-R10: How do you handle the non-determinism of LLMs in production?

> **Your anchor**: "Constrain, verify, observe. (1) Constrain — structured output via function calling, not free-text. (2) Verify — validate outputs against a schema before acting. (3) Observe — log every LLM call, every tool use, every outcome. (4) Eval — regression test on a golden dataset before every model change. (5) Human-in-the-loop for irreversible actions. At Airbnb I apply this to BPI VA — the agent can't take destructive actions without a human checkpoint. The non-determinism is a managed risk, not a blocker."

---

## 4. Your 0→1 Stories (rehearse these aloud)

### Story 1: BPI Virtual Analyst (0→1 AI product)

> **Setup**: Analysts at Airbnb were spending 40% of their day on repetitive triage.
> **Action**: I shadowed 5 analysts for a week, identified triage as the highest-pain workflow, prototyped a Python co-pilot orchestrating 30+ LLMs behind a FacadeDriver, shipped to 55+ analysts.
> **Result**: Cut analyst triage time by X%. [Fill in real number before interview.]
> **Lesson**: Ambiguity is resolved by user contact, not more thinking. Ship something, watch users, iterate.

### Story 2: Redpen UI (0→1 full-stack ownership)

> **Setup**: [Context — what pain did Redpen solve?]
> **Action**: I owned the UI end-to-end — design, React/TypeScript implementation, integration with the backend Alex owned.
> **Result**: [What did Redpen achieve?]
> **Lesson**: 0→1 ownership means you own the whole thing, not a piece.

### Story 3: Lilly DMS (0→1 regulated full-stack)

> **Setup**: Lilly needed a radiopharmaceutical dose-management system under FDA compliance, 21 CFR Part 11, with a 10-hour isotope-decay window.
> **Action**: I built it full-stack — Java/Spring Boot backend, React/TypeScript frontend, PostgreSQL, OpenShift/K8s deployment, 8-level RBAC for 14 personas.
> **Result**: 99.9% uptime for 6 months, 21 CFR Part 11 compliant.
> **Lesson**: 0→1 in a regulated environment — the constraints make you a better engineer, not a slower one.

### Story 4: Portfolio sites (0→1 production-grade)

> **Setup**: I wanted to demonstrate full-stack production skills, not just backend.
> **Action**: Built sailikhith.me (Next.js 16, React 19, TypeScript 5, Tailwind 4) and airbnb.sailikhith.me (MUI v9, case-study subpages, 3D Spline, GSAP, react-globe.gl SGP4 satellite propagation).
> **Result**: Production-grade sites, not toy projects.
> **Lesson**: I can ship 0→1 on my own — backend, frontend, design, deploy.

---

## 5. Questions to Ask Mike

### Tier 1 (must ask — in order)

1. **Location**: "I'm based in Houston. The role is hybrid in Foster City, 3 days/week. Is there any flexibility on remote, or is relocation required? I'm open to relocation if the fit is right, but I want to understand the constraint."
2. **Level**: "Sr/Staff — how does Replit level this? Is it IC with technical leadership, or people management? What's the scope expectation?"
3. **Product Foundry structure**: "How big is the Product Foundry team? Who does it report to? How are products prioritized — top-down from leadership, or bottom-up from the team?"
4. **What's shipped so far**: "What has Product Foundry shipped so far? What's in the pipeline? What's the biggest win and the biggest lesson?"
5. **Interview process**: "What does the interview process look like? Timeline from here to offer?"

### Tier 2 (ask if time allows)

6. **AI coding agent direction**: "Where is Replit Agent heading? What are the hardest unsolved problems — long-context, multi-file reasoning, verification, safety?"
7. **Eval harness**: "How does Replit evaluate agent quality? SWE-bench? Internal benchmarks? Human review?"
8. **Tech stack**: "What's the Product Foundry stack? Python? TypeScript? What models do you use — frontier only, or fine-tuned?"
9. **Comp**: "What's the comp range for Sr/Staff? Base, equity, sign-on?" (Ask LAST. Replit at $9B — equity is the big variable.)
10. **Relocation**: "If relocation is required, does Replit cover it?"

---

## 6. Red Flags to Avoid

- "I'm passionate about AI" (cliché — every candidate says this)
- "I want to work with cutting-edge technology" (vague)
- Can't name a specific Replit Agent experience (try it before the interview)
- Can't explain LLM orchestration beyond "I call the API"
- No 0→1 story — only talks about maintaining existing systems
- Says "I'm a backend person" (this is a product role — full-stack or product-first)
- Over-claims: "I built Replit Agent" or "I authored Loki" (you operated Loki, didn't author it)
- Under-claims: "I only do backend" (you're full-stack — Lilly, Southwest, portfolio prove it)

---

## 7. Green Flags to Trigger

- Names a **specific Replit Agent experience** you tried before the call
- Mentions **SWE-bench** or coding agent benchmarks unprompted
- Talks about **eval harnesses** for non-deterministic outputs unprompted
- Says **"ambiguity is resolved by user contact, not more thinking"**
- Has a **0→1 story** with a specific pain point → prototype → ship → iterate arc
- Mentions **function calling / structured output** for agent reliability
- Frames **BPI VA as a coding agent for analysts** (domain transfer, not gap)
- Asks about **Product Foundry's shipped products** (shows you researched)
- Mentions **cost/latency budgets** for agents (production awareness)

---

## 8. Study Checklist

### Before the call with Mike (recruiter screen)
- [ ] Try Replit Agent on a real task — note one thing it did well, one struggle
- [ ] Re-read your Airbnb GenAI evidence (`about_me/resume_airbnb.md`)
- [ ] Practice Story 1 (BPI VA 0→1) aloud — 90 seconds
- [ ] Prepare the location question (Tier 1, #1)
- [ ] Know the Replit ARR story: 2.5M→550M in <17 months, $9B Series D

### Before a technical interview (if you pass the screen)
- [ ] Study ReAct pattern, function calling, SWE-bench
- [ ] Study the competitive landscape: Cursor, Copilot, Devin, Claude Code, Replit Agent
- [ ] Re-read this file Sections 2-3
- [ ] Practice Q-R1 (LLM orchestration), Q-R2 (eval harness), Q-R3 (coding agent) aloud
- [ ] Have a specific Replit Agent observation ready

### 1 hour before
- [ ] Re-read green flags (Section 7) + red flags (Section 6)
- [ ] Warm up with your BPI VA 0→1 story
- [ ] Have the location question ready as your first question

---

## 9. The Framing That Wins

> "I've spent the last 20 months at Airbnb building AI co-pilots for analysts — BPI Virtual Analyst, a 0→1 product serving 55+ analysts with 30+ LLMs behind a FacadeDriver, plus eval harnesses for non-deterministic outputs. Before that I built full-stack regulated systems at Lilly and streaming pipelines at Southwest. Product Foundry is where all of that compounds — 0→1 ownership, AI-native product development, ship to tens of millions of developers. I want to build the future of how software gets created. The location is the one constraint I need to understand — I'm in Houston, the role is Foster City hybrid, and I want to know if there's flexibility or if relocation is the path."

**Why this works**: leads with 0→1 AI product (BPI VA), names the specific skills (FacadeDriver, 30+ LLMs, eval harnesses), maps to Product Foundry's mandate, addresses the location constraint honestly upfront, ends with a question (not a demand).
