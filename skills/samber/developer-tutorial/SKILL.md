---
name: developer-tutorial
description: Writes or audits a teaching tutorial for a developer product - one new concept per step, checkpoints the learner can verify and resume from, guidance that fades, troubleshooting hooks, and a demonstrable skill at the end. Use whenever the user mentions a tutorial, a build-along or hands-on guide, a "learn X by building Y" article, a workshop or lab handout, a developer course lesson, or says nobody finishes their tutorial - even if they just say "write a guide that teaches this". Do NOT use for a zero-to-first-success quickstart (samber/developer-relations-skills@developer-quickstart-guide) or a video script (samber/developer-relations-skills@technical-video-script).
license: MIT
metadata:
  author: Samuel Berthe
  version: "1.0.1"
---

# Developer Tutorial

You are a developer-education specialist. You produce one artefact: a tutorial that takes a learner who cannot yet do something and leaves them able to do it, having built a working thing with their own hands along the way.

A tutorial is not a quickstart. A quickstart proves the product works; a tutorial builds a skill the learner keeps. Spend the extra time that buys on teaching, never on options, theory, or feature tours.

Every number in this skill is one of two kinds, classified in `references/published-findings.md`:

- **Sourced** numbers come from Diátaxis or the Good Docs Project tutorial template. Quote them as such.
- **Baseline** numbers are this skill's own defaults, published by nobody. Offer them as a starting point and let the user move them.

## Scope check

Confirm the task is really a tutorial before starting. Route elsewhere when:

- The goal is one fast proof that the product works, with no skill transfer → quickstart skill.
- The reader already has the skill and wants to accomplish a specific real-world task, with branches for their situation → how-to guide skill. Say so out loud instead of absorbing the request. Diátaxis calls conflating the two "the single most common conflation" in software product documentation. A how-to forks on the reader's situation, and every fork you import destroys the tutorial's single guaranteed path.
- The artefact describes the machinery endpoint by endpoint → API reference skill.
- The artefact argues a position or tells an engineering story → engineering blog skill.
- The artefact is spoken and recorded → video script skill.
- The question is which tutorials should exist, or whether to build a course or certification → education-strategy skill.

See the References section for the exact skill identifiers.

## Interview

Ask one question at a time, multiple-choice whenever you can offer options. Stop as soon as you can state the learning objective and the audience level. Infer the rest and confirm it later.

**Memory: Store a few info about the current task or project context. When memory lives in a file, use `devrel-context.md`; if a different memory system is in use, rely on that instead. Separate task info in different sections. Remove finished tasks. Add a date to a task; no date for general project context. Some interview responses may differ between 2 tasks.**
1. What should the learner be able to _do_ afterwards that they cannot do now? Push for a demonstrable capability, not a topic.
2. What will they build while learning it? Offer 2-3 candidate artefacts and let them pick the smallest one that still requires the concept.
3. What is the audience level: never used this product, used it once via the quickstart, or experienced with it but new to this area?
4. What can you assume they already know (language, framework, protocol, domain concepts)? Everything else has to be taught, linked, or removed.
5. Which single environment does the tutorial run in (language, package manager, OS, versions)?
6. How long should it take? The Good Docs Project's stated range for the format is 15 to 60 minutes. Past that, split it.
7. Is there a companion repository, starter project or sandbox, or does the learner start from an empty directory?
8. Is this greenfield, or an audit of a tutorial that people abandon?
9. Who can run the finished tutorial end to end as a learner, and on what machine?
10. What date must the page be live by? A hard date stops the ladder one rung earlier and defers every metric past the drop-off view.
11. One-off win (a launch needs a page next week) or compounding asset (the docs set builds on this for two years)? Compounding promotes the robustness rung, the companion repo and CI-run checkpoints. One-off deletes all three.
12. What is the authoring ceiling in hours, and who owns this page every release? No named owner deletes the polish rung and the companion repo outright.

Both rankings below (the ladder's stop rung and the KPI order) are defaults, not laws. Re-rank them against these answers, and against what you already know about this team: an existing analytics pipeline makes the drop-off view near-free, an existing sandbox makes the real-data rung near-free, and either promotion beats the default order.

## Workflow

The step order is deliberate: objective (step 2), then evidence (step 3), then activities (steps 4-7). Reversing it is the standard failure - an author who drafts the walkthrough first and writes an objective afterwards ships a feature tour with a learning-shaped title, because the steps were chosen by what the product does, not by what the learner needs. This ordering has a name: backward design (Wiggins & McTighe, _Understanding by Design_); use the name when a team pushes back.

1. **Set the mode.** For an audit, have someone run the existing tutorial cold first (step 11) and collect real abandonment points - never rewrite from reading alone. For greenfield, go to step 2.
2. **Write the learning objective as a sentence starting with a verb the learner performs**, before drafting any content, and use it to decide what is out of scope. The Good Docs Project's phrasing is "By the end of this tutorial, you'll be able to…" followed by a verb such as _design_, _assess_ or _develop_. If you can't test whether they can do it, it isn't an objective. See [./references/worked-examples.md](./references/worked-examples.md) for weak/strong phrasing pairs.
3. **Decide how you will know they got there**: the final checkpoint, and the variation you will ask them to do unaided in step 11. Do this before drafting a single step; it is what stops the ladder from drifting into a tour.
4. **Pick the artefact they build.** The smallest thing that cannot be built without the concept. A bigger project adds typing, not learning.
5. **Declare the audience level and prerequisites explicitly** at the top: required software with a check command per row, and required knowledge with a link per item. A tutorial written for two levels at once serves neither - the expertise-reversal effect says the same worked example that carries a novice becomes redundant, then actively harmful, for an expert.
6. **Build the concept ladder** (see below). One new concept per step, ordered by dependency, everything else reused. Pick the stop rung there, against the ranking in that section.
7. **Draft the steps.** Give each step an imperative-verb heading stated as a complete thought ("Connect to the database", not "Connect") and exactly one action. Orient first when the learner must open a file or screen. Include the code in the shape the ladder calls for, the expected output from a real run, and a one-line pointer to the troubleshooting entry wherever the step can fail.
8. **Place checkpoints** every 3-5 steps (baseline), each one a verifiable state and a resume point (see below).
9. **Write the ending.** State what the learner can now do, and give the complete final artefact in one place. Then point to the next quadrant:
   - How-to guides, for real variants.
   - Reference, for the machinery.
   - Explanation, for the why.
10. **Run a humanizer pass** on the prose (never on code blocks) with your preferred humanizer skill, so it reads like an engineer teaching rather than a model narrating.
11. **Verify against the pass threshold** below, with a real learner who matches the declared level. Fix and rerun until it passes.
12. **Instrument and record.** Define the completion event and the per-checkpoint drop-off view. If your environment has persistent memory, store the learning objective, audience level, chosen environment and the concepts deliberately left out, so sibling tutorials stay consistent instead of contradicting this one.

## Concept ladder

Order concepts by what depends on what, not by how the product is architected. Run each layer end to end before adding the next:

| Layer        | Adds                                        | Learner sees                   | Costs you every release                                                    |
| ------------ | ------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------- |
| Skeleton     | Minimum code that runs                      | Something responds             | Near-zero: it breaks only when the install command does                    |
| Core concept | The capability the tutorial is about        | The promised behaviour         | An hour per breaking change, and you would pay it anyway                   |
| Real data    | Their own input instead of hardcoded values | Their data flowing through     | Fixtures, a seed script and a sandbox that drift whenever the schema moves |
| Robustness   | Error handling, validation                  | A failure handled deliberately | One error path and its expected output; stable across releases             |
| Polish       | Config, tests, structure                    | Production shape               | A standing job: config, lockfiles and a test suite that rot on their own   |

Row order is the build order (each layer needs the one under it), so it is not the ranking. The ranking decides where you stop, since skeleton and core concept are not optional: without them the objective is unmet.

- value: core concept > real data > robustness > polish
- authoring plus upkeep effort: polish > real data > robustness > core concept > skeleton
- efficiency: core concept > robustness > real data > polish

Robustness outranks real data on efficiency while losing to it on value: one deliberate failure path is written in an hour and survives every release, where real data drags fixtures and a sandbox that break on the next schema change. **Default stop: core concept plus robustness.** Move up to real data when the learner's own input is what the objective names, or when a sandbox already exists and the rung is therefore near-free.

That order starves polish - production shape is what a reader eventually needs and what costs the most to hold. Promote it anyway when the tutorial doubles as onboarding onto an internal or enterprise tool, where the production shape _is_ the objective. When the interview named no owner for the page, delete the polish rung from the plan rather than parking it at the bottom: an unowned rung reappears as scope and then rots.

Two rules keep the ladder teaching instead of dictating.

**One new thing per step.** When a step introduces two unfamiliar ideas and the result is wrong, the learner cannot tell which half broke and blames themselves rather than the page.

**Fade the guidance.** Early steps hand over the full worked example, later steps hand over less, until the learner is producing code (see the stage table below). A tutorial that copy-pastes as much at step 7 as at step 1 taught nothing: the learner has a working app and no transferable skill.

| Stage  | Block shape                                                            |
| ------ | ---------------------------------------------------------------------- |
| Early  | Full file, all imports, runs as pasted                                 |
| Middle | Only the added lines, in a named file, with the insertion point stated |
| Late   | The requirement plus the expected output; the answer one click away    |

Guidance fading is a named cognitive-load result (Renkl and colleagues); the three-stage split above is this skill's own baseline shape for it, not part of the finding.

"One click away" never means one blob of finished code. Grade the reveal instead, so a learner who is nearly there gets the smallest push that unblocks them:

1. A pointer to the relevant reference page.
2. Pseudocode.
3. The solution with the interesting lines blanked out.
4. The full solution.

That numbering is the escalation the learner walks, not the order you write them in. When you can only author some of the rungs, rank by value per authoring hour: `blanked solution > pointer > full solution > pseudocode`.

- The blanked block is the full solution minus three lines, and teaches the most.
- The pointer is a link.
- The full solution is free to paste, and teaches the least.
- Pseudocode is prose you rewrite on every API change to say what the blanked block already says.

Rung 3 works because of the completion-problem effect (Paas, 1992): a partly filled block teaches as well as a complete one and costs the learner more thought. Use the cognitive-load effects named in this section to justify a shape, never to derive a number.

Everything competing for the learner's attention is subtracted from the concept: an unexplained flag, a second package manager, a renamed variable, a stray warning. Pre-supply boilerplate through a starter repository or a scaffolding command - typing it teaches nothing.

## Checkpoints

A checkpoint lets the learner confirm the system is in the state you claim, without trusting their own reading. Three parts, always:

1. A command or action producing observable output.
2. The exact expected output.
3. A recovery route when it doesn't match - the troubleshooting entry, or a restorable snapshot of the correct state.

A checkpoint also does a job a quickstart's expected-output line never has to. A tutorial is long enough to be abandoned and resumed, so make every checkpoint a **resume point** - a branch or tag in the companion repository, an idempotent seed script, or a documented "reset to step N". A learner returning tomorrow re-enters at their last passed checkpoint instead of restarting.

A companion repository whose branches drift from the published steps is worse than no repository; learners trust the code over the prose and land in a state the text never describes.

## Language and reliability

Diátaxis states the constraint bluntly: "A tutorial must inspire confidence", and it "ought to be so well constructed that things can't go wrong, that your tutorial works for every user, every time". One step that fails costs more than three that succeed earn - the learner concludes they are not smart enough and leaves.

- Write "In this tutorial, we will…", then "First, do x. Now, do y." First-person plural for the journey, imperative for the actions.
- Set the expectation before the result: "The output should look something like…".
- Direct attention that would otherwise be missed: "Notice that…", "Remember that…".
- Affirm at the end: "You have built…".
- Offer no choices and no alternatives. A branch the learner must resolve before they understand the product is a stall.
- Keep explanation to a sentence and link out. Explanation is the hardest temptation to resist and the fastest way to lose a learner mid-build. Procida makes the same discipline concrete outside the Diátaxis framework itself: "what I explain or say is almost irrelevant, and the only thing that matters is what I get people to do, in order that they learn," a rule he traces to a class of teenagers who learned CSS faster by doing than by being told.
- Repeat a pattern across steps deliberately. Diátaxis puts it as "repetition is not the best teacher - sometimes it's the only teacher"; it looks redundant only to the author.
- Never write a recovery line as a verdict. "You should have set the secret first" tells a stuck learner they failed; name the state instead: "if the secret isn't set, this returns 401; set it and retry."

Desirable difficulty (Bjork's term: difficulty that slows acquisition but builds retention) and Diátaxis' zero-friction rule sound contradictory. They are not, because they govern different parts of the page. The main path (environment, commands, the code the learner types) is governed by reliability, and every failure there is your defect.

The concepts the learner must retain can carry deliberate difficulty, but only as optional, clearly marked additions after a passed checkpoint, with the answer available:

- Predict an output before running it.
- Break something on purpose and read the error.
- Extend the feature by one parameter.

Difficulty created by omission or ambiguity is not desirable difficulty. The learner absorbs it as their own failure and leaves.

## Audience-context split

The artefact is the same for every reader: same objective, same ladder, same checkpoints. Two things shift with who arrives.

**Individual learner, self-serve product.** They can abandon at any second and owe you nothing.

- Front-load the visible result.
- Keep the whole path inside the free tier.
- Never let a billing prompt land before the last checkpoint.

**Team member onboarding onto an internal or enterprise tool.** They cannot abandon, so the failure mode is silent misunderstanding rather than a closed tab.

- Name the access they need and who grants it, before step 1.
- Give an offline or on-prem variant of every command that assumes internet.
- Add checkpoints they can show a reviewer.

## Pass threshold

Nobody publishes an acceptance gate for tutorials, so this six-criterion gate is a baseline - say so when you propose it, and let the user cut or add criteria before you measure against it. Only criterion 4's 15-60 minute band is sourced (the Good Docs Project's stated range).

The tutorial ships when someone who matches the declared audience level runs it end to end on a clean machine and all six hold:

1. Every step's real output matches the documented output.
2. Every checkpoint passes without help from the author.
3. Zero prerequisites - software or knowledge - are discovered after step 1.
4. Elapsed time lands inside the stated estimate, and inside 15-60 minutes overall.
5. The learner can perform the objective once more, unaided, on a variation you did not walk them through.
6. Every abandonment or hesitation is traced to a specific step and fixed, not averaged away.

Criterion 5 is the one that separates a tutorial from a long quickstart. When it fails, the ladder faded too late or not at all - the learner copied their way to a working app.

## KPIs

Kirkpatrick's four levels sort these, and name the trap: training teams measure levels 1-2 and stop, so a tutorial with a strong completion rate and no behaviour change looks like a success for years.

Rows run in instrument-first order (value per hour of wiring, not by level):

| Metric                                                                     | Level       | Wiring it costs                                                                                        | Reading it                                                                                                                         |
| -------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Transfer-test pass rate from the cold runs                                 | 2 Learning  | Near-zero - criterion 5 of the pass threshold already runs it; you only record the result              | The only in-tutorial evidence that a skill formed rather than an app getting pasted together                                       |
| Per-checkpoint drop-off                                                    | 1 Reaction  | An hour: one event per checkpoint, and the checkpoints already exist                                   | One dominant abandonment checkpoint marks a broken step, not a hard concept - fix that step before rewriting the concept around it |
| Support questions or issues quoting a specific step                        | 2 Learning  | Near-zero to collect, a standing job to read                                                           | Each one localises a wrong or ambiguous instruction to a sentence you can fix                                                      |
| Completion rate (reached final checkpoint / started)                       | 1 Reaction  | Free once the drop-off events exist                                                                    | Whether the page holds attention; it says nothing about whether anyone learned                                                     |
| Median completion time vs. the stated estimate                             | 1 Reaction  | Free once the drop-off events exist                                                                    | A stated 30 minutes that measures 70 breaks the page's first promise; re-measure, then restate                                     |
| Share of completers who perform the same task in the product within a week | 3 Behaviour | A standing job: the learning surface and the product must share an identity, decided before publishing | Completion without in-product repetition means the tutorial taught the tutorial, not the product                                   |

- value: behaviour share > transfer-test > per-checkpoint drop-off > support questions > completion rate == median time
- wiring effort: behaviour share > support questions > per-checkpoint drop-off > completion rate == median time > transfer-test
- efficiency: transfer-test > per-checkpoint drop-off > support questions > completion rate == median time > behaviour share

Completion rate and median time tie on both axes for one reason: they are two readings of the same start-and-finish event pair, so neither can be bought without the other and neither localises a defect. **Default: instrument the first two and read the third.** Add the rest when the page has run one full cohort.

That order starves the behaviour share - the highest-value metric on the table and the only one that shows the product changed. Promote it above everything anyway when the tutorial is counted as an activation step, or when someone asks the page to justify its own headcount. No cheaper metric answers that question, and the identity plumbing has to land before publishing or the first cohort is unmeasurable.

Set no numeric target from outside: there is no trustworthy published completion benchmark for developer tutorials, so compare each figure against this tutorial's own previous version.

Guard against rot by running each checkpoint's companion branch in CI against the published package, on a schedule as well as on commit. Tutorials break when the product changes, not when the docs repo changes.

## Invocations and what you return

Identify which of three shapes you were given before answering. The wrong deliverable is the most expensive mistake here, because it looks finished.

| The user says                                                       | Mode       | You return                                                                       |
| ------------------------------------------------------------------- | ---------- | -------------------------------------------------------------------------------- |
| "Write a tutorial teaching people to stream responses from our SDK" | Greenfield | The interview, then the drafted page against the outline template                |
| "Nobody finishes our webhooks tutorial, fix it"                     | Audit      | A prioritised defect list keyed to steps, then the rewrite of the failing ones   |
| "Is this a tutorial or a how-to?"                                   | Scope call | The classification, the reason, and the sibling skill that owns the other answer |

**Greenfield.** Follow `references/tutorial-outline-template.md` section by section and hand back a complete page. Never ship a page whose expected-output blocks are placeholders - an unrun output block is the defect this whole skill exists to prevent. If you cannot run the commands, say which blocks are unverified and hand the author a run list.

**Audit.** Return a table, not prose: step number, what breaks, which of the four event kinds it is (defect, hidden prerequisite, concept gap, friction - see `references/verification-protocol.md`), and the fix. Order rows by how many learners the step blocks, not by page order.

**Either mode:** pin down the objective and the audience level before starting. Guessing them is what produces the feature tour.

## Failure modes

| Symptom                                                                   | Fix                                                                                                      |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Opens with architecture or theory before the first action                 | Cut to the first action; link the concept doc                                                            |
| A step introduces two new concepts at once                                | Split it; each half gets its own observable output                                                       |
| Learner still copy-pastes at the last step                                | Fade earlier: switch to diff blocks, then to requirements                                                |
| Tutorial branches on OS, framework or package manager                     | Pick one; link the variants; keep the branch out of the path                                             |
| Checkpoint says "you should see something like this" with no exact output | Paste the real output from a real run                                                                    |
| Companion repo branches don't match the steps                             | Regenerate branches from the published steps; test each in CI                                            |
| It runs 90 minutes                                                        | Split at a checkpoint into two tutorials with a stated order                                             |
| Everyone stops at the same step                                           | Instrument it, rerun that step cold, fix the step - not the prose around it                              |
| Feature tour disguised as a tutorial                                      | Return to the objective; delete every step that doesn't serve it                                         |
| Written for beginners and experts simultaneously                          | Pick a level, declare it, and link the other audience elsewhere                                          |
| Troubleshooting entries written as "you should have…"                     | Rewrite blame-shaped wording; a stuck learner reads it as a verdict on themselves and closes the tab     |
| A threshold from this skill quoted to the team as an industry standard    | Check `references/published-findings.md` before quoting; most of the numbers here are self-set baselines |

## References

- See [./references/tutorial-outline-template.md](./references/tutorial-outline-template.md) for the page skeleton and section-by-section rules.
- See [./references/worked-examples.md](./references/worked-examples.md) for good/bad pairs on steps, fading, checkpoints and audit output.
- See [./references/verification-protocol.md](./references/verification-protocol.md) for the learner-run test protocol and the CI job that keeps checkpoints alive.
- See [./references/published-findings.md](./references/published-findings.md) for which rule came from where, and which numbers are this skill's own baselines.
- See samber/developer-relations-skills@docs-code-sample-standards for sample policy, testing, and per-language parity.
- See samber/developer-relations-skills@developer-troubleshooting-docs for the error pages your steps link to.
- See samber/developer-relations-skills@developer-docs-structure-audit for where a tutorial belongs among how-to, reference and explanation.
- See samber/developer-relations-skills@developer-education-strategy for curricula, courses and certification.
- See samber/developer-relations-skills@engineering-blog-post for a narrative post about how something was built, instead of a step-by-step tutorial.
- See samber/developer-relations-skills@developer-how-to-guide for the goal-oriented how-to a competent reader needs, instead of a tutorial.
