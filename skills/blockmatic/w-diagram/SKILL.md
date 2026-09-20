---
name: w-diagram
description: Produce a Mermaid diagram of the requested code, architecture, or data flow.
disable-model-invocation: true
---

Visualize relationships, flow, or structure. Chat output unless the user gave a file path. Do not invent architecture that is not in the sources. Do not invent PRODUCT.md.

1. If the request is product, journey, or architecture docs, read `PRODUCT.md` and named MDX and emit at most two Mermaid diagrams from those sources. Flag contradictions between docs and code without proposing a new methodology.
2. Otherwise inspect the named code or docs. Choose flowchart, sequence, class, er, state, or journey only when it matches the question.
3. Keep labels short. Split oversized graphs. Wrap output in a mermaid fence.
4. Explain what the diagram shows in a few sentences. Nodes and edges must map to inspected sources.
