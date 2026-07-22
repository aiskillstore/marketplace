# deslop-the-copy

A portable Agent Skill for Claude Code, Codex, OpenClaw, Cursor, Gemini CLI, GitHub Copilot, and other compatible agents. It removes AI-generated patterns without replacing the writer's voice with a generic "human" one.

It can edit a draft or detect named slop patterns without rewriting. Every edit is checked against a repeatable evaluation, and em dashes are never allowed in the output.

## Why this exists

Wikipedia's [WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup) maintains a detailed guide called [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), cataloging patterns observed across thousands of AI-generated texts. NPR, TechCrunch, and FlowingData have all covered it as the best reference for spotting machine-written prose.

Existing tools use these patterns to detect and strip AI tells from text: banned phrases, structural cliches, and sentence-level habits. Detection and removal are useful, but an aggressive rewrite can erase the person along with the slop.

deslop-the-copy preserves the writer's vocabulary, cadence, bluntness, humor, uncertainty, digressions, and formality. It makes the minimum effective edit, leaves strong human sentences alone, and never invents facts or opinions to sound more alive.

## Installation

This repository follows the open [Agent Skills](https://agentskills.io) format.

**Cross-agent installer:**

```bash
npx skills add skyzer/deslop-the-copy
```

The installer lets you choose from its supported agents, including Claude Code, Codex, OpenClaw, Cursor, Gemini CLI, and GitHub Copilot.

**OpenClaw:**

```bash
openclaw skills install @skyzer/deslop-the-copy
```

**Manual installation:**

Clone or copy the entire repository into your agent's skills directory. Keep `SKILL.md` and `references/eval.md` together.

```bash
git clone https://github.com/skyzer/deslop-the-copy.git
```

## Usage

Ask your agent to clean up any AI-sounding text:

- "Deslop this paragraph"
- "Make this not sound like AI"
- "Clean up this copy"
- "This reads like slop, fix it"

Or audit a draft without rewriting it:

- "Scan this for AI slop"
- "Which AI-writing patterns are in this copy?"
- "Flag the slop, but don't rewrite it"

## What it does

AI text has a recognizable smell. This skill handles it through three passes and a final evaluation.

### Pass 1: Read before editing

Find the draft's core point, audience, existing voice signals, and lines that already sound human. This keeps the edit anchored to the writer instead of a universal casual voice.

### Pass 2: Remove slop

Targets AI tells including:

**Content patterns** like significance inflation ("stands as a testament"), standalone filler sentences ("that distinction matters", "the practical mental model is simple"), promotional language ("groundbreaking", "nestled in the heart of"), vague attributions ("experts argue"), and generic "challenges and future" wrap-ups.

**Language patterns** like AI vocabulary (robust, leverage, navigate, landscape, paradigm, delve, foster, synergy), copula avoidance ("serves as" instead of "is"), binary contrasts ("it's not just about X, it's about Y"), rule-of-three overuse, synonym cycling, false ranges, filler phrases, and empty hedging.

**Copy patterns** like throat-clearing openers, faux-insight hooks, colon reveals, negative lists, dramatic fragments, rhetorical setups, robotic rhythm, fake-profound endings, and redundant recaps.

**Style patterns** like em dash use (zero tolerance), decorative bold, inline-header lists, Title Case headings, emoji headers, and unnecessary micro-sections.

**Communication artifacts** like chatbot language ("I hope this helps!"), knowledge-cutoff disclaimers, sycophancy, and meta-signposting ("let's explore", "here's the thing").

### Pass 3: Preserve the person

After removing the patterns, it checks that the edit still belongs to the writer:

- Keeps recognizable vocabulary, cadence, humor, bluntness, and uncertainty
- Preserves strong opinions already in the draft without inventing new ones
- Uses contractions only when they fit the writer and context
- Keeps useful rough edges instead of manufacturing them
- Changes rhythm only where the original drones or repeats itself

### Final evaluation

The skill runs every result against [references/eval.md](references/eval.md). Failed checks trigger another revision before the text is returned. The first hard check requires zero Unicode em-dash characters in the full response, including quoted evidence in detection mode.

## Before and after

**Before:**
> In today's rapidly evolving digital landscape, artificial intelligence stands as a transformative force that is fundamentally reshaping how businesses navigate the complexities of modern commerce. From small startups to large enterprises, organizations are leveraging robust AI solutions to enhance their operational efficiency, foster innovation, and drive sustainable growth. It's not just about automation. It's about reimagining what's possible.

**After:**
> AI is changing how businesses operate. Companies of all sizes use it to automate work, run more efficiently, and test new ideas.

## License

MIT
