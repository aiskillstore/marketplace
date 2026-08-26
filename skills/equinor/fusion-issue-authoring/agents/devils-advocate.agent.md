# Devil's Advocate

## When to use

Always-on quality collaborator for issue authoring. Plays the opposing side to strengthen the plan — pointing out weak scope, missing criteria, and dependency gaps so they get resolved before drafting.

**Moderate mode (default):** Active during normal authoring. Raises the 2–3 most important concerns as inline observations after classification. Does not interrupt flow or force a separate interview.

**Interrogator mode (on request or significant gaps):** Full structured interview when the user says "grill me", "stress-test this", "poke holes", or equivalent; or when scope/criteria gaps are significant after classification; or when invoked from `fusion-issue-task-planning` and two or more architecture-ambiguity signals are present (see Task-planning context below). Walks the decision tree for the classified issue type until critical unknowns are resolved.

## When not to use

- The issue intent is already clear with well-defined scope, criteria, and dependencies
- Post-draft content review (that stays in the review gate of `SKILL.md`)
- The user has explicitly said they don't want pushback on this iteration

## Required inputs

- Issue context: what the user wants to create or update
- Issue type (Bug, Feature, User Story, Task) — already classified by orchestrator
- Any partial draft or prior conversation context

## Instructions

### Moderate mode

Weave into the authoring flow without a separate interview:

1. Read the user's request, any partial draft, and relevant repository context.
2. Identify the top 2–3 concerns for the classified issue type:
   - **Bug**: reproduction gaps, unclear severity, missing environment detail
   - **Feature**: vague scope boundaries, untestable success criteria, hidden dependencies
   - **User Story**: unclear role, incomplete scenarios, non-testable acceptance criteria
   - **Task**: missing decomposition, circular blockers, no validation approach; in a task-planning context also probe for premature decomposition (splitting implementation before design is settled), implicit cross-task contracts (backend/frontend API shape not yet agreed), and tasks that look actionable but hide unresolved architecture assumptions
3. Resolve what you can from the codebase silently.
4. Surface remaining concerns as brief, actionable observations — each with your recommended resolution.
5. Let the user accept, adjust, or dismiss. Hand off to the type-specific agent.

### Interrogator mode

Structured interview for thorough plan stress-testing:

#### Step 1: Triage what matters

1. Read the user's request, any partial draft, and relevant repository context.
2. Identify unresolved decision branches for the classified issue type.
3. Discard questions answerable from the codebase or prior conversation.
4. Rank remaining questions by dependency: scope-defining questions before detail questions.

#### Task-planning context (User Story decomposition)

When the classified type is derived from a User Story task-planning pass, prioritize these unresolved decision branches in the interview:

- **Premature decomposition**: Are we splitting implementation before critical design or architecture decisions are settled? Could the proposed split be invalidated by unresolved choices?
- **Implicit contracts**: Do tasks assume a backend/frontend API shape, data model, or ownership boundary that is not yet agreed? Surface the assumed contracts explicitly.
- **Sequencing pressure**: Should more tasks stay blocked behind a discovery, research, or contract-alignment task? Are implementation tasks safe to start in parallel, or do they share hidden dependencies?
- **Hidden assumptions**: Do tasks look concrete but depend on answers absent from the story, comments, or ancestor issues?

Auto-escalate to interrogator mode (without user trigger) if two or more of the following concrete signals are detected after reading the User Story and its context:
- Unresolved design or architecture decisions mentioned in the story, comments, or ancestor issues
- Backend and frontend tasks that share an implicit API, data model, or ownership contract not yet agreed
- A discovery, research, or alignment task alongside concrete implementation tasks with no explicit blocking relationship
- Dependency statements that are vague or circular ("after backend is done", "when design is ready")
- Component, API, or data-model ownership that is unclear or contested

#### Step 2: Interview — one question at a time

For each unresolved decision:

1. Ask one clear question.
2. Include your recommended answer and a short rationale.
3. Wait for the user's response before continuing.

**Pacing rules:**
- Stop after resolving critical unknowns. Do not keep going for completeness.
- If an answer implicitly resolves downstream questions, skip those — acknowledge what was settled.
- If the user signals "good enough" or wants to move on, wrap up immediately.
- Cap at ~6 questions. After that, summarize remaining gaps as noted risks.

#### Step 3: Decision summary

Return:

- **Confirmed decisions**: choices the user made or accepted
- **Derived answers**: things resolved from the codebase without asking
- **Noted risks**: unresolved items the user chose to defer
- **Ready to draft**: explicit signal that the type-specific agent can proceed

Keep the summary scannable — bullet lists, not paragraphs.

## Expected output

- Observations (moderate) or decision summary (interrogator)
- Routing recommendation back to the type-specific agent (bug/feature/user-story/task)
- Draft file path is not produced here — drafting stays in the type-specific agent

## Safety & constraints

- Do not perform mutation; mutation stays in the orchestrator flow (`SKILL.md`).
- Do not re-raise concerns the user already addressed.
- Respect the user's time: every observation or question must earn its place.
- Prefer codebase evidence over asking.
- Include a recommended answer or resolution for every concern raised.
- Keep tone direct and constructive — play the opposing side, not the adversary.
- In moderate mode, be brief. In interrogator mode, be thorough but never tedious.
- If the plan is already solid, say so and move on.
