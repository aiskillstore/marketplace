# Phase 0 Brainstorming Playbook

Turn the user's idea into an agreed `.agents-cli-spec.md` through a collaborative dialogue —
*before* any sample study, scaffolding, or code. Adapt the depth to the agent's complexity.

## HARD-GATE

Do NOT clone a sample, scaffold, run `agents-cli create`, or write any code until the user has
approved the spec. **Reading the recipe index is exempt** — it is not "studying a sample". Scan it
before your first reply and name any matching recipe there, even when that reply is only a
clarifying question. This applies even to "obvious" agents — unexamined assumptions cause the most
wasted work.

## Scale to complexity

- **Trivial agent** — single tool or none, fixed persona, no external auth, no RAG, no multi-agent.
  → A couple of adaptive questions, a 2–3 sentence spec, one approval. Don't force the full process.
- **Complex agent** — multi-agent / orchestration, RAG, external APIs with auth, or safety-critical.
  → Full treatment below: adaptive Q&A across all topics, 2–3 approaches, sectioned design with
  approval per section, self-review, and a user-review gate.

When unsure, start light and escalate as complexity surfaces.

## One question at a time

- Ask a single question per message; let the answer shape the next. **Even two questions in one
  message is a batch** — ask the one that most shapes the design first (usually problem/scope before
  integrations), and let the answer pick the next.
- **Ask at least one clarifying question before proposing approaches, and never present a full spec in
  your first reply.** Jumping straight to a finished spec is the most common failure — it skips the
  dialogue this phase exists for. (Exceptions: a trivial agent, or a genuinely non-interactive run.)
- Prefer multiple-choice questions — they are easier to answer than open-ended ones.
- Cover the Phase 0 topics (problem, tools/APIs + auth, safety, deployment, plus the context-based
  ones in `SKILL.md`), but follow the user's lead rather than a fixed script.
- YAGNI: prune features that don't serve the stated purpose.

## When you can't ask (non-interactive, sparse, or deferred input)

Asking is always the default. But when you genuinely can't get an answer — a non-interactive run, a
one-liner "just build it", **or the user defers a choice to you ("whatever's standard", "you pick",
"the simplest")** — make a concrete choice and **list it in the spec under an `## Assumptions`
heading**, each as a one-line decision the user can correct (e.g. "Assumed the public icanhazdadjoke
API; no auth"). A deferred or vague answer is an assumption to surface, **not a fact to state in the
spec body**. Always check the axes users most often leave implicit: **data sources, auth method,
schedule/cadence, and which model.**

Non-interactive ≠ skip the thinking. For non-trivial agents you must still record the approaches you
weighed and the one you chose, flag oversized scope, and route any capability the scaffold doesn't
ship to its recipe (`/google-agents-cli-adk-code` → `references/samples.md`) — then commit to a design. The user-review gate is how they catch a wrong assumption.

## Propose 2–3 approaches (non-trivial agents)

Once you understand the goal, present 2–3 *agent architecture* options with trade-offs. **End with one
explicit recommendation — "I recommend Option X because Y" — before asking the user to choose.** Never
present a neutral menu and leave the decision unframed; a default-with-reasoning is faster to confirm
or override. Typical axes:

- **Single-agent vs multi-agent / orchestration** — one agent with tools, or a coordinator delegating
  to sub-agents.
- **Tool / integration choices** — which APIs or data sources, and how auth is handled.
- **Capabilities the scaffold doesn't ship** — retrieval ("search / look up over our docs, incidents,
  tickets, or knowledge base"), sandboxed shell or code execution, memory across sessions, approval
  gates before risky actions, OAuth consent, safety guardrails, event-driven or scheduled runs. Each
  is a **clone-and-study recipe, never a scaffold flag**: look the need up in the topic index in
  `/google-agents-cli-adk-code` → `references/samples.md` and list every matching recipe in the spec's
  Reference Samples, to study in Phase 1. Don't silently downgrade a stated need to a plain tool
  call, and flag it even when it's deferred to a later phase.
- **Deployment shape** — prototype-first (recommended) vs a deployment target.

## Present the design in sections

For complex agents, present the design in sections and get approval after each — scale each section to
its complexity (a sentence if straightforward, a short paragraph if nuanced):

- **Architecture** — single vs multi-agent, sub-agents and their roles.
- **Tools** — each tool's purpose, API, and auth.
- **Data flow** — inputs, retrieval, state/memory.
- **Safety** — concrete guardrails, not generic statements.
- **Success criteria** — measurable outcomes for evaluation.

Be ready to revisit earlier sections when something doesn't fit.

## Right-size the scope first

If the request spans multiple sub-systems — **3+ specialist/sub-agents, several integrations, or
distinct data/team domains** — stop and flag it *before* designing. Over-scoped agents are the biggest
cause of wasted work. Recommend the smallest end-to-end slice that proves the architecture (often one
coordinator + one specialist), and defer the rest under a `## Future Phases` heading in the spec. This
holds even non-interactively: name the full scope, recommend a first slice, defer the remainder —
never silently spec the whole thing as one build.

## Write the spec

Once the design is agreed, write `.agents-cli-spec.md` using `references/spec-template.md`. Write it to
the **project's working directory** (the cwd where the user is building), not a temporary/scratch
location — Phase 0 resumes by reading `./.agents-cli-spec.md`, so a spec saved elsewhere is lost next
session. Name the path in your approval message.

**Self-review before showing the user:**

1. **Placeholders** — any "TBD"/"TODO"/vague requirement? Fill them in.
2. **Consistency** — do sections contradict each other? Does the architecture match the tools/use cases?
3. **Scope** — 3+ sub-agents/integrations? If so, did you flag it and carve out a first slice, with the
   rest under `## Future Phases`? A spec that builds everything at once is a red flag.
4. **Measurable success criteria** — each criterion is a number, threshold, or pass/fail eval, not
   "works well" / "comprehensive".
5. **Ambiguity** — could a requirement be read two ways? Pick one and make it explicit.

Fix issues inline, then continue.

## User-review gate

Ask the user to review `.agents-cli-spec.md` before moving on:

> "Spec written to `.agents-cli-spec.md`. Please review it and tell me if you want changes before we
> look at reference samples and scaffold."

If they request changes, make them and re-run the self-review. Only once they approve do you proceed
to **Phase 1 (study samples)** → **Phase 2 (scaffold)**.
