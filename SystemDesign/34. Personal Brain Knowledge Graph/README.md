# Personal Brain Knowledge Graph Architecture

> Complete system design and algorithmic breakdown of a local, privacy-first knowledge graph memory system with FastMCP, Hebbian learning, semantic KNN search, and exponential forgetting.

🔗 **Interactive Study Workbook:** [Open index.html](index.html)

---

## Architectural Data Flow

```
[ AI Agent / IDE Prompt ] ──► [ FastMCP Server Interface ]
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                               ▼
            [ SQLite Graph Store ]          [ Vector Embedding Index ]
            (Nodes, Edges, Co-activations)     (FastEmbed / HNSW ANN)
                       │                               │
                       └───────────────┬───────────────┘
                                       ▼
                       [ Hebbian Weight Engine ]
                   (Weight Decay & Reinforcement)
```

---

## Core Algorithms
1. **Hebbian Learning & Co-activation:** "Concepts that fire together, wire together." Weight $W_{ij} \leftarrow W_{ij} + \eta$, with exponential temporal decay $W_{ij}(t) = W_{ij}(0) \cdot e^{-\lambda t}$.
2. **Hybrid Retrieval:** Multi-hop Graph Traversal (BFS/DFS with depth 2) + Cosine Vector Similarity ($K=5$ nearest neighbors).
