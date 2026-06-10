# PM Agent Brief

Use this before assigning work to Claude Code, Codex, OpenClaw, or another coding agent.

## 1. Outcome

Write the concrete shipped result in one sentence.

Example:
> Add a Gumroad free-product draft flow that creates the product, attaches a ZIP, and leaves it unpublished for final review.

## 2. Scope

In scope:
- Files or modules the agent may change
- User-facing behavior to deliver
- Tests or validation required

Out of scope:
- Refactors not needed for the requested behavior
- Visual redesigns unless explicitly requested
- Any destructive action such as deleting data, resetting git state, or overwriting user changes

## 3. Context

Give the agent:
- Project purpose
- Existing conventions to follow
- Relevant files
- Known constraints
- Anything already attempted

Keep this factual. Do not make the agent infer business context from scattered notes.

## 4. Acceptance Criteria

The work is done when:
- The requested behavior exists
- Existing important behavior still works
- Tests or manual checks pass
- The final response names changed files and remaining risks

## 5. Review Questions

Ask these before accepting the result:
- Did the agent change files outside the expected scope?
- Did it invent a new abstraction when a local pattern already existed?
- Did it leave a manual step that should have been automated?
- Did it claim verification without showing the command or result?
- Did it expose secrets, tokens, private data, or account identifiers unnecessarily?
