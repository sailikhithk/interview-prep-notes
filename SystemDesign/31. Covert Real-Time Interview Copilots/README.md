# Covert Real-Time Interview Copilots Architecture

> System design, low-latency audio capture pipelines, visual stealth rendering, and dual-LLM streaming orchestration behind desktop interview assistant tools (FinalRound AI, Cluely, MindWhisper).

🔗 **Interactive Study Workbook:** [Open index.html (Explainer)](index.html) | [Open interactive.html (Architecture Lab)](interactive.html)

---

## High-Level Architecture

```
[ System Audio / Loopback ] ──► [ Local VAD & Whisper Chunking ] ──► [ LLM Streaming Gateway ]
[ Screen / OCR Ingestion ]   ──► [ Text Diff & Context Extractor ] ──► [ Prompt Routing Engine ]
                                                                                │
                                                                   [ Stealth Transparent Overlay ]
                                                                     (Electron / macOS Metal)
```

### Core Engineering Challenges & Solutions

1. **Low-Latency Loopback Audio Capture:**
   - Intercepts system audio output (interviewer's voice) via CoreAudio / virtual audio cable without echo-feedback into the candidate's microphone.
   - Chunks audio into 1.5s sliding windows using WebRTC Voice Activity Detection (VAD) before sending to streaming Speech-to-Text (STT / Deepgram / Whisper).

2. **Dual-Model Streaming Orchestration:**
   - **Fast Tier (Groq / Gemini Flash):** Generates instant bullet points & code templates in <400ms.
   - **Deep Tier (Claude Sonnet / GPT-4o):** Re-ranks and produces rigorous mathematical proofs and deep trade-off analyses in parallel.

3. **Stealth Overlay & Process Masking:**
   - Electron window configuration: `alwaysOnTop: true`, `transparent: true`, `hasShadow: false`, `hiddenInMissionControl: true`.
   - Native macOS Window Sharing API protection: `CGWindowSetSharingState(kCGWindowSharingNone)` to ensure screen-sharing tools (Zoom, Google Meet, Teams) cannot capture the overlay.
