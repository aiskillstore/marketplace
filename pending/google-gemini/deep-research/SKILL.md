---
name: deep-research
description: Conduct deep, multi-agent research on complex topics by spawning parallel subagents that independently search, analyze, and synthesize information. Use for broad surveys, multi-angle investigations, or exhaustive comparisons. Do not use for simple factual lookups.
license: Apache-2.0
metadata:
  author: Google Gemini
  origin: gemini-original
  version: "1.0.0"
---

# Deep Research

Act as a lead researcher orchestrating parallel subagents to investigate a complex topic, then synthesize a grounded report.

## Workflow

1. Orient first: clarify scope only if genuinely ambiguous. If the topic is unfamiliar, run one quick search to map the landscape. For narrow or single-fact lookups, answer directly or use at most 2 subagents; for broad topics, decompose into 3 to 5 non-overlapping sub-questions (cap at 2 to 3 on slow or high-thinking models).
2. Gather in parallel: spawn concurrent `research` subagents (use `browser` when a sub-question needs full-page reads of live or authenticated pages). If subagent tools are unavailable, execute the search tracks directly. Give each subagent a distinct angle, time frame, source scope, and a budget of at most 8 to 12 web searches or tool steps.
3. Keep evidence primary: tell subagents to verify claims against primary sources rather than search snippets, include exact quotes or raw outputs for key numbers, and return partial verified findings plus remaining gaps when they hit their search budget instead of looping.
4. Resolve gaps and avoid straggler stalls: read findings as they arrive. If most subagents finish and one track stalls, cancel the stalled worker and move on. Run one targeted follow-up pass only if important gaps remain, and spawn a fresh verification subagent only for high-stakes or data-heavy reports.
5. Synthesize: write the final report to the session Artifact Directory Path when available, or reply directly in headless runs, using Simplified Technical English, inline clickable citations, a 2-sentence top-line summary, and a brief Unresolved section whenever sources conflict or data is missing. When writing an artifact, keep chat output to a short pointer and key decisions.
