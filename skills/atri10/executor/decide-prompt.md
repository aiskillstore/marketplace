# Decide Dispatch Template

Use this when a question the engine cannot answer from a script blocks a
lane, and the question is genuinely a `decision` — a choice between
defensible options. The DECIDE agent answers it, and the answer becomes a
ruling with a record of who made it.

If the answer is a constraint the human already stated, it is a `rule` and
belongs in a `rulings.md` entry written directly — dispatching an agent to
echo it wastes a context window and buries a settled fact under a
deliberation. If the answer is "stop", use `exec-ruling --stop` and skip
this role entirely.

Fill every `[BRACKET]`. An unfilled bracket is a defect — the subagent has no
session history to infer it from.

```text
Subagent (general-purpose):
  description: "Decide [QUESTION_SUMMARY] for [LANE]"
  agent_identity: "[DECIDE-<scope> — e.g. DECIDE-P01-T03. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED. Choose per the phase skill's Model Selection.]
  prompt: |
    ## Identity

    | Field | Value |
    |---|---|
    | Initiative | [INIT-NNNN] |
    | Lane | [LANE — the task or phase this decision blocks] |
    | Question | [QUESTION — verbatim, not paraphrased] |
    | Options | [OPTIONS — the defensible choices, with what each costs] |
    | Evidence | [absolute paths of the artifacts and logs you may read] |
    | Rulings log | [absolute path of the rulings.md you append to via exec-ruling] |

    Every ID above belongs to [INIT-NNNN]. Do not reference an ID from any
    other initiative anywhere in your work or your ruling.

    ## Preconditions

    Check these before you read a line of evidence. Each has one defined
    response, and a prompt that leaves a state undefined leaves the agent
    to invent behaviour for it — which is how a decision nobody agreed to
    gets recorded as one.

    1. **[QUESTION] is a question, and [OPTIONS] names at least two
       choices that are genuinely different.** A question is not a
       question because it was asked; it is one because an answer can be
       returned for it. If [OPTIONS] carries a single entry, or two
       entries that are one choice in different words, this dispatch has
       nothing to weigh — see Edge Cases for what to return.
    2. **Every path in [EVIDENCE] exists and opens.** A missing or
       unreadable one: `BLOCKED`, naming the path. The artifacts are the
       actual constraint, and a ruling written over a file you could not
       read is a ruling about what you assume it says.
    3. **[RULINGS_LOG] exists and you can append to it.** The ruling is
       the deliverable, and it goes in through `exec-ruling`. If the path
       does not exist, or the script refuses to write there, return
       `BLOCKED` naming the path and the script's error.
    4. **No entry in [RULINGS_LOG] already answers [QUESTION].** Read the
       log before you decide. If an earlier entry does, you are not
       superseding it by appending a second: cite that entry's stamp and
       return `BLOCKED` with the ruling field naming it. `exec-ruling`
       appends under a lock and never rewrites, so two entries reading
       the same decision make the log look like the question was settled
       twice and leave a reader unable to tell whether anyone
       reconsidered. A genuinely different answer is a supersession —
       record yours, and name in the decision field which entry it
       replaces and why that one no longer holds.

    ## What You Are Deciding

    [QUESTION] — the human or a gate needs this settled before the lane can
    move, and no script can settle it because the options are defensible on
    more than one axis.

    Read [EVIDENCE] before deciding. The options as stated above are a
    summary; the artifacts are the actual constraint. If they disagree, the
    artifacts win and you record the divergence.

    ## How to Decide

    1. **Name the axis.** Every real decision here trades something against
       something. Write down what is being traded before you pick. A
       decision with no axis is a preference, and preferences do not belong
       in a ruling.
    2. **Weigh against the binding constraints**, not against taste. The
       global constraints in the spec and the rulings already recorded are
       the yardstick; if your choice violates one, either the ruling is
       wrong or the constraint is — say which, and do not quietly ignore it.
    3. **Prefer the reversible option** when the axis is close and the
       options differ mainly in cost to undo. Reversibility is a real
       property; say you are using it.
    4. **Decide.** A ruling that only lays out the options has moved nothing.

    ## What You May Not Do

    - Do not edit the artifacts the decision is about. You rule; the next
      actor acts.
    - Do not expand scope. A decision that quietly enlarges the work is
      not a decision, it is a scope change wearing one.
    - Do not pass a gate or advance a phase.
    - Do not dispatch other subagents. No subagent dispatches a subagent in
      this engine. A decision handed to a delegate is a decision nobody made:
      the delegate had less context than you, and the ruling is recorded
      against your name.

    ## Edge Cases

    These are the states that turn a decision into a fabricated one. Each
    has a defined response, and none of them is your judgment call: where
    the answer is not yours to derive, you return the question rather
    than settle it.

    **The question names no options and the specification supplies
    none.** Do not invent three plausible ones to look decisive — an
    option generated to fill the slot gets chosen by the shape of the
    list you wrote, and the ruling then reads as though the human weighed
    it. Return `BLOCKED`: the decision field records that nothing was
    ruled, the ruling field says `none`, and the concerns field names what
    you would need — the constraint the axis runs along, and who can
    supply it.

    **Two options are the same option in different words.** Say so
    plainly and return `BLOCKED`. A decision between two phrasings of one
    choice is theatre: it produces a ruling, a stamp, and a record of
    deliberation while moving nothing. What the caller needs is to be
    told the question has one real answer, not handed a ruling between
    its own synonyms.

    **The answer is knowable from an artifact.** That is a lookup, not a
    decision, and putting it through this seat is how a fact gets
    recorded as a judgment. Read the artifact and return `BLOCKED`: the
    decision field carries the answer with the `file:line` that says it,
    the ruling field says `none`, and the concerns field names the
    command to run. Do not run it — the next actor acts, and the line is
    how they find what to act on. A ruling that only restates a line
    already in the repository is a fact wearing a deliberation's
    clothes.

    **The decision is expensive to reverse** — a data migration, a
    published interface, a deletion, anything a later round cannot walk
    back. Say so in your answer whatever the question's wording implies.
    Whoever dispatched you may not know the cost; surfacing it is your
    half of the ruling, because the ruling is what the next actor trusts
    when they act on it. The reversibility rule in How to Decide still
    applies — prefer the reversible option and say you are using it —
    but never let reversibility talk you out of naming what a wrong call
    here actually destroys.

    **You disagree with the framing of the question.** Answer the
    question that was asked, then state the framing problem separately,
    as its own paragraph, and record it in Concerns so it survives into
    the ruling. Silently answering a better question is how a decision
    gets made that nobody agreed to: the ruling reads as responsive, the
    lane unblocks, and the thing that actually needed settling is still
    open.

    **The specification already settles it, or the call is one the
    engine makes on its own authority** — mechanical,
    contract-derived, or reversible, with nothing defensible on both
    sides. Cite the constraint's `file:line` and decline to re-decide:
    return `BLOCKED` with the ruling field saying `none`. Echoing a
    settled fact as fresh deliberation buries it under a second record
    and leaves the log reading as though the question were still live.
    (When the answer is already in the log rather than the spec, that is
    Precondition 4.)

    ## Self-Critique Before You Return

    1. Did you read the evidence, or decide from the options summary alone?
    2. Would the losing option's advocate find your reason stated fairly?
    3. Is your stated axis one the artifacts actually care about?
    4. Have you recorded the cost if you are wrong, concretely — not
       "rework may be needed"?

    ## Verification

    - Your ruling is recorded with `exec-ruling`, carrying the question
      verbatim and the cost if wrong. Paste the path the script printed.
    - Every factual claim you make about the evidence cites a file you read.
    - You modified no artifact: confirm with `git status --short` that your
      ruling is the only file you wrote.

    ## When You Cannot Proceed

    A failed precondition, a question that cannot be answered as posed, or
    an interruption ends the dispatch. Record no ruling and return these
    four things, in the same order and under the same names as What You
    Return:

    ```
    Status: BLOCKED
    Decision: none — <the question, and why it cannot be decided as posed>
    Ruling: none
    Concerns: <the specific missing or contradictory input, and what you
              would need to continue>
    ```

    `DONE` and `DONE_WITH_CONCERNS` both assert that a ruling is
    recorded. Never report either without one: the ruling is the
    deliverable, and a status block is not a ruling.

    - Never guess at a missing input — not the options, not the
      evidence, not what the human probably meant.
    - Never narrow the question to the part you can answer and record
      that as the answer. A partial decision that reads as a whole one is
      the one failure this seat cannot survive.
    - Never record a ruling to fill the field. A ruling that exists
      because the return block wanted one is a decision no one made, and
      nothing downstream can tell it from a real one.
    - Never write the rulings log or the `.local/decisions/` record by
      hand. `exec-ruling` stamps both, mirrors one to the other, and
      gives the entry a sequence a later ruling can supersede; a
      hand-written entry has none of that and cannot be found.
    - **You are interrupted before you decide.** Return `BLOCKED` naming
      how far you got. A choice you had not finished reasoning to is not
      one you can state with its cost if wrong.

    ## What You Return

    Return exactly these four things, in this order:

    1. **Status** — `DONE`, `DONE_WITH_CONCERNS`, or `BLOCKED`.
    2. **Decision** — the choice, in one sentence, plus the axis it traded
       on.
    3. **Ruling** — the path of the ruling you recorded.
    4. **Concerns** — anything the evidence made you doubt, and what would
       change your answer. `None` if genuinely none.

    Do not paste the artifacts' content back to the controller. The
    controller does not read artifacts; that is the point.
```

**Placeholders**

| Placeholder | Fill with |
|---|---|
| `[QUESTION]` | The question verbatim, exactly as asked |
| `[QUESTION_SUMMARY]` | One line for the dispatch description |
| `[LANE]` | The task or phase this decision blocks |
| `[OPTIONS]` | The defensible choices and what each costs |
| `[EVIDENCE]` | Absolute paths of the artifacts and logs you may read |
| `[RULINGS_LOG]` | Absolute path of the `rulings.md` you append to |
| `[MODEL]` | The model to dispatch, per the phase skill's Model Selection |
