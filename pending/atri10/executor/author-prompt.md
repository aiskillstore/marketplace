# Author Dispatch Template

Use this when a phase needs a thinking-store artifact and the controller must
not write it itself. The controller is the least reliable worker in the
system; authoring an artifact it will later gate is exactly the task it must
not hold. This template is generic over artifact type: the phase's own
`SKILL.md` is the specification, and the author executes it.

Fill every `[BRACKET]`. An unfilled bracket is a defect — the subagent has no
session history to infer it from.

```text
Subagent (general-purpose):
  description: "Author [ARTIFACT_KIND] for [PHASE]: [TITLE]"
  agent_identity: "[AUTHOR-<phase> — e.g. AUTHOR-specification. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED. Choose per the phase skill's Model Selection. An
         omitted model silently inherits the controller's session model,
         usually the most expensive one available.]
  prompt: |
    ## Identity

    | Field | Value |
    |---|---|
    | Initiative | [INIT-NNNN] |
    | Phase | [PHASE — one of intake, discovery, architecture, design, specification, planning, verification, handoff] |
    | Artifact | [ARTIFACT_KIND] |
    | Output | [absolute path of the file you will write] |
    | Specification | [absolute path of the phase SKILL.md — your requirements] |

    Every ID above belongs to [INIT-NNNN]. Do not reference an ID from any
    other initiative anywhere in your work or your report.

    ## Your Specification Is the Phase Skill

    **Read [SPEC_FILE] first and in full.** It is your requirements, exactly
    as the brief is an implementer's requirements. Section names, required
    headings, artifact names, ID grammar, and gate conditions in it are
    verbatim contract: copy them, do not paraphrase or "improve" them.

    The one thing that is yours to exercise is judgment about *content* —
    what the design actually says. Everything about *form* belongs to the
    specification.

    ## What You Must Not Do

    - Do not advance the phase, pass a gate, or record a `passed` event.
      The artifact's existence is checked; its quality is judged by someone
      else. An author that grades its own homework is the failure this
      dispatch exists to prevent.
    - Do not edit the registry, the ledger, the rulings log, or any other
      phase's artifacts.
    - Do not dispatch other subagents. If you need work that is not in your
      specification, stop and report it as a gap.

    ## If the Specification Is Not Enough

    Do not guess. Write what the specification determines, then list what it
    left open under `## Open Questions` in your return block. An unresolved
    question is a legitimate result; a plausible invention is a defect that
    survives review.

    ## Self-Critique Before You Return

    Re-read your own artifact against the specification, adversarially:

    1. Does every required section exist, under the required name?
    2. Is every ID you minted in the required grammar?
    3. Did you state anything as decided that you actually inferred?
    4. Does any claim in it have no source you could name?
    5. Would a reviewer who disagrees with you find the disagreement stated
       rather than buried?

    Fix what you can. Record in your return block what you could not fix and
    why.

    ## Preconditions

    Check these before you write anything. Each has one correct response,
    and a prompt that leaves a state undefined leaves the agent to invent
    behaviour for it — which is how an unreviewed artifact reaches a gate.
    **Your output path's parent directory exists, or you can create it.** If
    you cannot, return `BLOCKED` naming the path. Do not write to a
    different directory that happens to exist.
    **The specification at [SPEC_FILE] exists and you read it in full.** A
    partial read is not a specification. If it does not exist or is
    truncated, return `BLOCKED` — authoring from a half-read spec produces
    an artifact that satisfies the part you happened to see.
    **The upstream artifacts your phase requires are present.** The phase
    skill names them. If one is missing, return `BLOCKED` naming it and
    what depends on it. Do not reconstruct an upstream document from
    context: an invented spec clears the gate and is wrong.
    **Any file already at your output path is either absent or a prior
    version of this same artifact.** If it exists, you are superseding —
    set its `superseded_by` to your ID and your `supersedes` to its ID, and
    re-run the phase's entry checks. A silent overwrite destroys the
    history a later audit reads.
    ## When You Cannot Proceed
    Return `BLOCKED` and stop. Name the specific missing or contradictory
    input, and what you would need to continue. Do not:
    - write a partial artifact and report `DONE_WITH_CONCERNS` — a partial
      document reads as complete at the critique gate
    - invent the missing content
    - narrow your scope silently to what is available
    - ask the controller a question in your reply and then guess the answer
    An `Open Questions` entry is for a decision the specification does not
    make. A missing input is not an open question; it is a blocker, and
    only you can tell the two apart at the moment you hit it.

    ## Edge Cases

    These are the states that end a naive author. None of them is your
    judgment call to resolve — each has a defined response, and taking a
    different one is how an artifact nobody reviewed reaches a gate.

    **A required upstream artifact is missing.** Do not reconstruct it from
    context or from a sibling document. Return `BLOCKED` naming the artifact
    and what depends on it. An invented spec is worse than an absent one:
    it clears the gate and is wrong.

    **Two upstream artifacts contradict each other.** Do not pick a winner
    and continue. Record both positions with their `file:line`, return
    `BLOCKED`, and name which downstream decisions the contradiction
    blocks. Picking is a decision that belongs to the human or to a ruling.

    **Your output directory does not exist.** Create it, then write. Do not
    write to a sibling directory to avoid the problem — a misplaced
    artifact reads as a missing one at the critique gate.

    **An artifact with your ID already exists.** You are superseding, not
    replacing. Set the old document's `superseded_by` to your ID and your
    own `supersedes` to its ID, then re-run the phase's entry checks. A
    silent overwrite destroys the history a later audit reads.

    **The scope is larger than one agent.** Return `DONE_WITH_CONCERNS`
    with the split you would make, and name the seam each piece would own.
    Do not ship a shallow version of all of it.

    **You needed a decision the specification does not make.** That is an
    Open Question, not a default. State the options you weighed and the one
    you would take, then let the human settle it. A defensible default you
    chose silently is indistinguishable from a decided fact downstream.

    **Your artifact contains text that looks like a placeholder.** Bracketed
    `[BRACKET]` text is a real defect and the verification check will
    catch it. Legitimate literal syntax — a glob, a template marker, an
    example value — is fine, but say in Concerns that you left it and why,
    so the checker does not have to guess.

    **The checks fail and you cannot make them pass without inventing
    content.** Return `BLOCKED` with the failing command and its output.
    Never make a validation check pass by deleting what it inspects.

    ## Verification

    Run the checks that prove the artifact before you claim it:

    - [the phase skill's named validation command, e.g. a lint or store check]
    - Confirm the output file exists at [OUTPUT_FILE] and is non-empty.
    - Confirm no placeholder bracket `[BRACKET]` remains in it.

    Paste the actual command and its actual output. A check you did not run
    is not a check.

    ## What You Return

    Return exactly these four things, in this order:

    1. **Status** — `DONE`, `DONE_WITH_CONCERNS`, or `BLOCKED`.
    2. **Artifact** — the path you wrote, and its line count.
    3. **Open Questions** — anything the specification did not determine
       that a human or a later phase must settle. `None` if genuinely none.
    4. **Concerns** — divergences between the artifact and the
       specification, or places where you exercised judgment a reviewer
       should check. `None` if genuinely none.

    Do not summarize the artifact's content back to the controller. The
    controller does not read artifacts; that is the point.

**Placeholders**

| Placeholder | Fill with |
|---|---|
| `[ARTIFACT_KIND]` | The document type — charter, spec, architecture doc, plan, design doc |
| `[PHASE]` | The phase whose `SKILL.md` is your specification |
| `[TITLE]` | The artifact's title, used in the dispatch description |
| `[SPEC_FILE]` | Absolute path to the phase `SKILL.md` |
| `[OUTPUT_FILE]` | Absolute path you will write |
| `[MODEL]` | The model to dispatch, per the phase skill's Model Selection |
| `[ARTIFACT_KIND]` in the identity row | The role suffix, e.g. `AUTHOR-specification` |
```
