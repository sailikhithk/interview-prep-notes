# AI Infra Interview — 30-Topic Cheat Sheet
> Distilled from `rohitg00/ai-engineering-from-scratch` for **ML Infra / AI Data Prep** loops.
> One-line answer you can recite + lesson path for the deep dive.

| # | Topic | One-line answer | Deep dive |
|---|-------|-----------------|-----------|
| 1 | **Why scale dot-product by 1/√d_k in attention?** | Dot products grow with d_k; without scaling softmax saturates → vanishing gradients. Scaling keeps scores in a usable gradient range. | `07-transformers-deep-dive/02-self-attention-from-scratch` |
| 2 | **Why is self-attention O(n²)?** | QK^T produces an n×n matrix; both compute and memory scale quadratically with sequence length — the reason FlashAttention / sparse attention exist. | `07-transformers-deep-dive/02-self-attention-from-scratch` |
| 3 | **What does the causal mask prevent?** | Token t attending to tokens > t. Sets future positions to -∞ before softmax so autoregressive generation can't see the future. | `07-transformers-deep-dive/02-self-attention-from-scratch` |
| 4 | **KV cache — what & why?** | Cache of past K,V so decode step t doesn't recompute K,V for steps 1..t-1. Turns O(n²) decode into O(n) per step. Memory grows with context. | `07-transformers-deep-dive/12-kv-cache-flash-attention` |
| 5 | **FlashAttention in one sentence** | Fuses the QK^T → softmax → V matmul into one kernel that never materializes the n×n matrix in HBM → O(n) memory, same math. | `07-transformers-deep-dive/12-kv-cache-flash-attention` |
| 6 | **Multi-head attention — dim per head?** | d_model / h. With 512/8 = 64 per head. Total compute ≈ single-head at full dim, but heads learn different relations. | `07-transformers-deep-dive/03-multi-head-attention` |
| 7 | **RoPE vs sinusoidal vs ALiBi positional encoding** | Sinusoidal: fixed additive. RoPE: rotates Q,K by angle ∝ position → relative positions via dot-product phase. ALiBi: bias term that decays with distance — enables length extrapolation. | `07-transformers-deep-dive/04-positional-encoding` |
| 8 | **Mixture of Experts — routing & load balancing** | Router (gating network) selects top-k experts per token. Aux loss penalizes imbalance to prevent expert collapse. Sparse activation → bigger model, same FLOPs. | `07-transformers-deep-dive/11-mixture-of-experts` |
| 9 | **Speculative decoding — draft + verify** | Small draft model proposes k tokens; large model verifies in one forward pass. Accept matches, reject at first mismatch. Lossless, ~2-3× speedup. | `07-transformers-deep-dive/16-speculative-decoding` |
| 10 | **Scaling laws (Chinchilla)** | Loss scales as power law in params (N), data (D), compute (C). Chinchilla: optimal compute ≈ 20 tokens per parameter. Most models are over-parameterized / under-trained. | `07-transformers-deep-dive/13-scaling-laws` |
| 11 | **BPE / SentencePiece tokenization** | Byte-pair encoding merges most-frequent adjacent pairs iteratively into a vocab. Handles OOV via subwords. SentencePiece treats text as raw bytes — language agnostic. | `10-llms-from-scratch/01-tokenizers` |
| 12 | **SFT vs RLHF vs DPO** | SFT: supervised fine-tune on instruction→response. RLHF: train reward model then PPO vs KL-regularized policy. DPO: skip reward model — directly optimize policy on preference pairs (simpler, stable). | `10-llms-from-scratch/06-instruction-tuning-sft` |
| 13 | **Why quantize? INT8 / INT4 / GGUF trade-offs** | Memory ↓ 4× (INT8) / 8× (INT4), bandwidth-bound decode speeds up. Accuracy loss small with calibration (GPTQ, AWQ). INT4 needs group-wise scales. GGUF = llama.cpp file format with k-quants. | `10-llms-from-scratch/11-quantization` |
| 14 | **vLLM — PagedAttention & continuous batching** | PagedAttention: KV cache in pages like virtual memory → no fragmentation, handles variable seq lens. Continuous batching: new requests join running batch every step → GPU utilization ↑. | `17-infrastructure-and-production/04-vllm-serving-internals` |
| 15 | **Goodput — the metric that matters for LLM serving** | Requests/s meeting both latency SLO (TTFT + TPOT) AND quality. Throughput that violates SLO doesn't count. The single number to optimize infra against. | `17-infrastructure-and-production/08-inference-metrics-goodput` |
| 16 | **Disaggregated prefill / decode** | Prefill (compute-bound, big batch) and decode (memory-bound, small batch) have opposite profiles. Run on separate GPU pools → each tuned, no mutual starvation. | `17-infrastructure-and-production/17-disaggregated-prefill-decode` |
| 17 | **Prompt caching — why it cuts cost** | Cache KV for a fixed prefix (system prompt, tools) → reuse across requests. Anthropic / OpenAI charge ~10% for cache reads. Big win for agents with long system prompts. | `11-llm-engineering/15-prompt-caching` |
| 18 | **RAG vs fine-tuning — when to pick which** | RAG: knowledge changes often, need citations, no training cost. Fine-tune: tone/style/format locked, latency budget tight, knowledge stable. Often: fine-tune format + RAG facts. | `11-llm-engineering/06-rag` |
| 19 | **LoRA — what it actually does** | Freezes base weights W, trains low-rank delta W = B@A where A: r×d, B: d×r, r ≪ d. Only ~1% params trainable, no inference overhead if merged. QLoRA = LoRA on 4-bit base. | `11-llm-engineering/08-fine-tuning-lora` |
| 20 | **Function calling / tool use — the contract** | Model emits structured JSON matching a schema you provide; you execute and feed result back. The bridge from text-in / text-out to actions-on-the-world. | `13-tools-and-protocols/02-function-calling-deep-dive` |
| 21 | **MCP — what problem it solves** | Standard protocol so any LLM can talk to any tool/server. Decouples tool-building from agent-building. Like USB-C for AI tools. | `13-tools-and-protocols/06-mcp-fundamentals` |
| 22 | **Agent loop — the core pattern** | Observe → think → act → observe. LLM proposes action, runtime executes, result fed back. Repeat until done or max steps. ReAct = reasoning + acting interleaved. | `14-agent-engineering/01-the-agent-loop` |
| 23 | **Plan-and-execute / ReWOO vs ReAct** | ReAct interleaves think-act per step (lots of LLM calls). Plan-and-execute: planner produces full plan once, executor runs it, solver aggregates. Fewer calls, less drift. | `14-agent-engineering/02-rewoo-plan-and-execute` |
| 24 | **Reflexion — verbal RL for agents** | After failure, agent writes a self-critique ('I forgot to check X') stored in memory, retried on next attempt. No weight updates — improvement via natural-language reflection. | `14-agent-engineering/03-reflexion-verbal-rl` |
| 25 | **Tree of Thoughts / LATS** | Explore multiple reasoning branches, evaluate each, expand best (MCTS-style). Beats linear CoT on planning puzzles; costs more inference. | `14-agent-engineering/04-tree-of-thoughts-lats` |
| 26 | **Agent memory: short-term vs long-term** | Short-term = current turn / context window. Long-term = vector store (semantic), KV store (keyed), or graph. MemGPT: OS-style paging between the two. | `14-agent-engineering/07-memory-virtual-context-memgpt` |
| 27 | **Prompt injection — the agent security problem** | Untrusted text in tool output can issue instructions ('ignore previous, send emails'). Defenses: input/output tagging, allow-listing actions, human-in-loop on side-effects, separate privileged context. | `14-agent-engineering/27-prompt-injection-defense` |
| 28 | **Eval-driven agent development** | Build a small graded eval set BEFORE iterating. Every prompt/tool change scored against it. Prevents the 'feels better but actually regressed' trap. | `14-agent-engineering/30-eval-driven-agent-development` |
| 29 | **FinOps for LLMs — the cost levers** | Model routing (cheap model for easy queries), prompt caching, batch API (50% off), quantization, self-hosting above breakeven, context compression. Track $/1M-tokens and $/request. | `17-infrastructure-and-production/27-finops-llms` |
| 30 | **SRE for AI — what's different from regular SRE** | Non-determinism, drift, quality SLOs not just uptime. Need: shadow traffic, canary by prompt-class, quality evals in prod, rollback to prior model snapshot, prompt regression suite. | `17-infrastructure-and-production/23-sre-for-ai` |

## Drill protocol (suggested)

1. **Day -7 → -3:** Read the full `ai-engineering-interview-prep.md` (608 Q&A) once, mark anything fuzzy.
2. **Day -2:** This cheat sheet — recite each one-liner from memory, check.
3. **Day -1:** Pick the 5 topics you stumbled on, open the lesson doc, re-read.
4. **Day of:** This cheat sheet only. Don't cram new topics.

## Source repo
`/Users/sailikhithkanuparthi/Downloads/career/job-search/github/ai-engineering-from-scratch`
- 503 lessons, 20 phases, ~320 hrs of material.
- Each lesson has `docs/en.md` (concept), `code/` (build it), `quiz.json` (test).
- Run `npx skills add rohitg00/ai-engineering-from-scratch` to install the tutor skill into Claude Code / Cursor.
