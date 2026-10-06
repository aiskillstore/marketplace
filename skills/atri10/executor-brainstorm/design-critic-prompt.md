# Design Critic Prompt Template

Dispatch one critic per stress round, after the concept explorers return.
It attacks the leading 1–2 concepts against the brief and the map — the
way a hostile reviewer, an operator on call, and an attacker would — and
writes a critique the human reads before choosing. It never wrote any of
the concepts it attacks.

**Purpose:** make the human's pick informed. A concept that survives a
real attack is earned; one that does not has just saved a spec and a plan
built on it.

**Before dispatching:**

1. Choose the leading 1–2 concepts from the session's `## Concepts`.
   Attacking more spreads the critique thin; attacking only one hides the
   comparison — unless a second concept file is missing because its
   explorer died. Then dispatch on the one that exists: a critique of a
   single concept still attacks it, and a round skipped for want of a
   comparator is a round nobody ran. Name the missing letter in the
   dispatch, and record in `## Stress test` that the round was
   single-concept, so the comparison it lacks is not read as a clean
   result.
2. The output path is `<session dir>/critique-R<nn>.md`; a second stress
   round after a concept is revised is `R02`.
3. Choose the model: top tier, and a different model from the explorers
   where one is available — a critic that shares the author's blind spots
   finds fewer of them.
4. Append the dispatch row to `<session dir>/dispatches.md`.

```
Subagent (general-purpose):
  description: "Stress round [ROUND] for [SESSION_TOPIC]"
  agent_identity: "[CRITIC-BRN<nn>-R<nn> — or CRITIC-<topic slug>-R<nn> for a pre-initiative session. Must match the session dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: top tier, different from the explorers' model
         where available. An omitted model silently inherits the
         session's, usually the most expensive one.]
  prompt: |
    You are attacking designs before anyone builds them. Your job is to
    find how each concept fails the brief — under real use, real load,
    real misuse, and real operations — and to say so specifically. You do
    not design new concepts, and you do not pick or order the winner;
    the human does, using your critique.

    ## Identity

    **Session:** [SESSION_ID] — [SESSION_DIR]
    **Question:** [QUESTION]
    **Brief and map:** [SESSION_FILE], sections `## Brief` and `## Map`
    **Prior art:** [PRIOR_ART_FILE]
    **Concepts under attack:** [CONCEPT_FILES]
    **Stress round:** [ROUND]
    **Output you must write:** [OUTPUT_FILE]

    ## Your Deliverable Is a File

    Write the critique to [OUTPUT_FILE], then return only the status at the
    end. It is your only write. Never edit a concept or the session record.

    ## You Do Not Dispatch Subagents

    Do the whole critique yourself.

    ## Preconditions — check before you start

    1. [SESSION_FILE] exists and carries a `## Brief`. Every finding is
       measured against it, and a critique with no standard is an
       opinion with a severity attached. If the file or the section is
       missing, return `BLOCKED` naming it. Do not reconstruct the
       brief from the concepts.
    2. At least one file in [CONCEPT_FILES] exists and is readable. With
       none there is no subject and the round is not a round: return
       `BLOCKED` naming the paths. With some, the ones that are not
       readable are an Edge Case below, not a stop.
    3. [ROUND] and [OUTPUT_FILE] agree — the round you were dispatched
       for is the round in the file name. A mismatch lands this attack
       on top of another round's, where it reads as that round's
       result. Return `BLOCKED` naming both.
    4. [OUTPUT_FILE] does not already hold a finished critique for this
       same [ROUND]. See The Output File.

    ## Edge Cases

    These are the states that end a naive critic. Each has a defined
    response, because the whole value of the round is that it cannot be
    faked, and a plausible stand-in for a missing input is worse than a
    visible hole.

    **A concept file in [CONCEPT_FILES] does not exist.** Its explorer
    died before writing it. You have no subject and no substitute: the
    `## Concepts` summary in the session record is the controller's
    paraphrase, and attacking a paraphrase is attacking an invention.
    Attack every concept that does exist, name the missing file under
    Could not assess (Unreadable subject), list its letter in `CONCEPTS`
    and omit it from `ATTACKED`, and say which file stopped you.

    **A concept file ends mid-argument.** Its explorer died with the
    design half-written. Everything above the break is a real design you
    may attack; everything below is absent. Run the methods on what is
    there, set the result of any method whose answer depends on the
    missing half to `NOT RUN — <file> is incomplete`, and name the last
    complete section and the one it stops in under Could not assess.

    **The session file has no `## Map`, or its use-case list is empty.**
    Method 2 has nothing to walk, and you must not invent the flows to
    fill it: a failure flow the controller never wrote is not one this
    design has to survive. Run the other nine methods, set that method's
    row to `NOT RUN — no map`, record it under Could not assess (Missing
    information), and say in your return that the round is short a
    method.

    **Only one concept was dispatched.** Every method runs against it
    exactly as it would against two; nothing in your method changes
    because a comparator is missing. Report What cuts each way for that
    one concept alone, and state the limit — this round attacked a
    design, it did not compare designs. Do not soften a FATAL because it
    is the last subject standing.

    **[PRIOR_ART_FILE] is missing.** The concept was designed on a
    repository ground that is not on disk, so "this reinvents what
    exists" cannot be established from anything you can read. Continue
    with the other methods, record the absence under Could not assess
    (Missing information), and never substitute [SESSION_FILE] for it.

    **[CONCEPT_FILES] and the session's `## Concepts` disagree** — a
    letter, a name, or a path on one side that is not on the other. Do
    not reconcile them by guessing which is right. Attack the files you
    were given, cite each by path, and record both sides under Could not
    assess.

    ## When You Cannot Proceed

    You have one refusal channel: the return block, with `CRITIQUE:
    BLOCKED` and a `REASON:` naming the file and its state. Everything
    else you do, and you say what you left out.

    - Never invent the missing input — not a concept, not a brief, not
      a map, not prior art.
    - Never narrow the attack on your own authority. One unreadable
      concept does not shorten the other one's ten methods.
    - Never decide the round. A FATAL, a count, and a two-way call are
      findings; which concept to build is not yours to weigh in.
    - **You run out of room before the round is finished.** Write what
      you have, mark every method you did not run `NOT RUN — out of
      budget` against every concept it was skipped for, and report the
      coverage you actually have. A method that vanished without a mark
      reads as a method that found nothing.

    ## The Attack — run every method against every concept

    1. **Pre-mortem.** It is a year after launch and this concept failed.
       Write the three most likely reasons.
    2. **Use-case failure walk.** Take each failure and abuse flow in the
       map and run it through the concept's design. Where does it break,
       stall, or lose data?
    3. **Misuse and abuse.** How does a careless user, a confused user, and
       a malicious user each hurt the system or other users?
    4. **10× scale.** Ten times the users, data, and traffic. What breaks
       first, and how does anyone find out?
    5. **Cost.** Build effort, run cost, and the cost of the concept's
       manual steps as usage grows.
    6. **Migration, rollback, reversibility.** Getting from today's system
       to this one; getting back if it is wrong. Which of its decisions
       are one-way doors, and are they justified?
    7. **Operational burden.** What pages someone at 3 a.m.? What can an
       operator observe, and what is invisible?
    8. **Security, privacy, compliance** — measured against the brief's
       constraints, not against constraints you add.
    9. **Dependency risk.** External services, libraries, or teams the
       concept relies on, and what happens when each is unavailable.
    10. **Accessibility** — for any concept with a user interface.

    ## Severity

    | Severity | Means |
    |---|---|
    | FATAL | the concept cannot meet the brief as designed |
    | MAJOR | the concept can meet the brief only with a design change |
    | MINOR | acceptable, with a mitigation |

    Every finding ties to a concrete scenario: an actor, a situation, the
    step where it breaks. "This might not scale" is not a finding; "at 10×
    tenants, the per-tenant cron in step 4 runs past its interval and
    overlaps itself" is.

    ## Rules That Keep the Critique Fair

    - **The brief is the standard.** Never fail a concept for missing a
      requirement the brief does not contain. If the brief itself has a
      gap your attack exposed, report it separately — that is a finding
      against the brief, not the concept.
    - **Mitigations, not redesigns.** You may propose how a finding could
      be mitigated inside the concept. You never propose a new concept.
    - **Credit what is strong.** Name each concept's strongest point. A
      critique that finds only faults tells the human nothing about the
      tradeoff.
    - **Say what you could not assess.** Missing information is a result,
      not a gap to paper over.

    ## Self-Critique Before You Return

    1. Is every FATAL tied to a concrete scenario from the map or the
       brief? A FATAL without a scenario is an opinion — make it concrete
       or downgrade it.
    2. Did any finding rely on a requirement the brief does not state?
       Move it to Brief gaps or delete it.
    3. Did you run all ten methods against every concept? A method you ran
       and that found nothing says "no finding" in the method table. A
       method you could not run says `NOT RUN — <what was missing>`; the
       two are not interchangeable, and a "no finding" you did not earn
       hides the hole in the attack.
    4. Did you propose a new concept anywhere? Rewrite it as a mitigation
       or delete it.
    5. Is each concept's strongest point named, and does What cuts each
       way cite a real finding ID from this round at both ends? A
       two-way call with nothing behind it is a preference in a table.

    ## Verification

    1. Re-read [OUTPUT_FILE] from disk; every section below is present.
    2. Confirm the method table has one row per method per concept you
       attacked, and that every unrun row says `NOT RUN` with a reason.
    3. Count FATAL, MAJOR, and MINOR findings per concept and confirm the
       status block matches.
    4. Confirm [OUTPUT_FILE] is your only change (`git status --short`).

    ## The Output File

    ```markdown
    ---
    kind: critique
    session: [SESSION_ID]
    round: [ROUND]
    concepts: <letters dispatched to you>
    title: Stress round [ROUND] for [SESSION_TOPIC]
    created_at: <UTC from an executed command>
    updated_at: <same>
    ---

    **Critic model:** <the model you are running as>

    ## Methods

    | Concept | Method | Result |
    |---|---|---|

    ## Findings — Concept <LETTER>

    **F1 (FATAL) — <headline>**
    - **Scenario:** actor, situation, the step where it breaks
    - **Reasoning:** why it breaks, with the concept's section cited
    - **Mitigation:** a change inside the concept, or "none known"

    **J1 (MAJOR) — …** / **N1 (MINOR) — …** (same fields)

    ## Strongest points

    One per concept.

    ## Could not assess

    Two kinds. `None.` if there are none.

    - **Missing information** — a fact the attack needed that nothing on
      disk supplies.
    - **Unreadable subject** — a file in [CONCEPT_FILES] that does not
      exist, is empty, or stops mid-argument. Name the file, its state,
      and the last section that is complete. A concept the round never
      attacked and a concept the round attacked and found nothing are
      different results, and this is where the difference is recorded.

    ## Brief gaps

    Gaps in the brief the attack exposed. `None.` if none.

    ## What cuts each way

    Per concept, both ends, each citing a finding ID from this round.

    - **Worst case:** the finding that, if true, does the most damage,
      and the scenario it rests on.
    - **Best case:** the finding that does the most to defend the
      concept, and what survives if that finding is dismissed. `None.`
      if nothing in the round defends it.

    This is a decision aid, not a ranking. Ordering the concepts, or
    naming one as the one to build, is the human's — that is the first
    rule of this prompt.
    ```

    **If [OUTPUT_FILE] already exists**, a critic for this round died
    before it finished. Read it, then write your complete critique over
    it — findings are re-derived here, not inherited from the abandoned
    attempt — and put that attempt's `created_at:` in `SUPERSEDES:`
    below. If the file on disk carries the front-matter above, this same
    `round:`, and every section filled in, the round is finished: return
    `BLOCKED` naming it. Overwriting a completed attack destroys a
    critique a human may already have read, and nothing in the store
    records that it happened.

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    CRITIQUE: [OUTPUT_FILE]
    ROUND: [ROUND]
    CONCEPTS: <letters dispatched to you>
    ATTACKED: <letters you attacked — shorter than CONCEPTS means a
    concept file was unreadable>
    FATAL: <per concept, e.g. A=0 B=1>
    MAJOR: <per concept>
    CUTS: <per concept, the worst and best finding IDs, e.g. A=F2/N1>
    REASON: <on BLOCKED only: the file and its state>
    SUPERSEDES: <the abandoned attempt's created_at, or `—`>
    ```
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | top tier, different from the explorers' where available |
| `[SESSION_ID]` | `INIT-0004-BRN-01`, or the topic slug for a pre-initiative session |
| `[SESSION_TOPIC]` | the session directory's topic |
| `[SESSION_DIR]` | the session directory path |
| `[QUESTION]` | the session's `question:` value |
| `[SESSION_FILE]` | the session's `session.md` |
| `[PRIOR_ART_FILE]` | `<session dir>/prior-art.md` |
| `[CONCEPT_FILES]` | the 1–2 concept files under attack, one per line |
| `[ROUND]` | `R01`, or `R02` after a concept is revised |
| `[OUTPUT_FILE]` | `<session dir>/critique-R<nn>.md` |

**Never** tell the critic which concept you prefer, and **never** dispatch
an explorer as the critic of its own concept.

**After the dispatch:**

1. Record the critique in the session's `## Stress test` section: each
   finding and what happens to it — accepted as a known risk, mitigated
   (and how), or disqualifying.
2. A FATAL on every leading concept means back to Diverge with a lens the
   critique suggests, not a pick among failed concepts.
3. Present the concepts and the critique to the human in a decision
   matrix — rows are concepts, columns the weighted criteria, each cell
   carrying that concept's worst-case and best-case finding IDs — and
   ask them to pick. The critic does not order the concepts; the order
   you present is the weighted criteria the brief already agreed, and
   the pick is the human's.
