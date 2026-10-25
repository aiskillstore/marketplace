# Published findings and self-set baselines

Every number and named rule this skill uses, split by whether someone published it or this skill set it. Read this before defending a threshold to a docs team, and before changing one.

## Contents

- Sourced rules - published by a named framework, template or study
- Self-set baselines - this skill's own defaults, safe to renegotiate
- Named frameworks and why each one fits
- Deliberately excluded

## Sourced rules

| Rule used in this skill                                                                                                                                                                                                  | Source                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| A tutorial is learning-oriented and serves the user _at study_; a how-to serves the user _at work_. Conflating them is "the single most common conflation made in software product documentation"                        | Diátaxis, diataxis.fr/tutorials-how-to                                                                                       |
| "The first rule of teaching is simply: don't try to teach."                                                                                                                                                              | Diátaxis, diataxis.fr/tutorials                                                                                              |
| "A tutorial is not the place for explanation." Explanation "distracts their attention from that, and blocks their learning."                                                                                             | same                                                                                                                         |
| "A tutorial must inspire confidence." "Your tutorial ought to be so well constructed that things can't go wrong, that your tutorial works for every user, every time."                                                   | same                                                                                                                         |
| "Repetition is not the best teacher - sometimes it's the only teacher."                                                                                                                                                  | same                                                                                                                         |
| Don't: abstraction and generalisation, explanation, choices, excess information                                                                                                                                          | same, verbatim don't-list                                                                                                    |
| Language patterns: "In this tutorial, we will…", "First, do x. Now, do y.", "The output should look something like…", "Notice that…", "You have built…"                                                                  | same                                                                                                                         |
| 15-60 minutes end to end                                                                                                                                                                                                 | Good Docs Project, `tutorial/tutorial-template-guide.md`: "Ideally, your tutorial should take 15 to 60 minutes to complete." |
| At most seven primary steps                                                                                                                                                                                              | same: "Avoid writing procedures that are more than seven primary steps long."                                                |
| At most four substeps per primary step                                                                                                                                                                                   | same: "Aim for no more than four substeps in any primary step."                                                              |
| Objectives phrased "By the end of this tutorial, you'll be able to…" + a verb, written before the content and used to decide scope                                                                                       | same; it points authors at Arizona State University's Learning Objectives Builder                                            |
| Overview declares learning objectives, intended audience, prerequisite knowledge                                                                                                                                         | same                                                                                                                         |
| Imperative verb headings expressed as a complete thought; no -ing form (harder to translate)                                                                                                                             | same                                                                                                                         |
| Orient the reader before the action - name the file or dialog first                                                                                                                                                      | same                                                                                                                         |
| Code samples carry required `import`/`using` statements and explanatory comments, and are verified to work                                                                                                               | same                                                                                                                         |
| Summary lists skills gained, worded differently from the objectives                                                                                                                                                      | same                                                                                                                         |
| The reader has ideally already completed a quickstart                                                                                                                                                                    | same                                                                                                                         |
| "What I explain or say is almost irrelevant, and the only thing that matters is what I get people to do, in order that they learn." Explanation and demonstration are "packaging for the lesson," not the lesson itself. | Daniele Procida (Diátaxis's creator), writing outside the framework itself, vurt.org/articles/on-teaching/                   |

## Learning-science sources

These justify the ladder and the fading table; none of them prescribes a number.

| Effect                    | Finding                                                                                                | Origin                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------------- |
| Worked-example effect     | For a novice, studying a complete worked example beats solving unaided                                 | Sweller & Cooper, 1985            |
| Completion-problem effect | Partially completed problems perform as well as full solutions                                         | Paas, 1992                        |
| Guidance-fading effect    | Remove solution steps progressively as competence builds, continuously rather than in fixed stages     | Renkl and Atkinson                |
| Expertise-reversal effect | The example that helps a novice becomes redundant, then harmful, for an expert                         | Kalyuga et al., 2000-2001         |
| Split-attention effect    | Keep the explanation adjacent to the code it explains                                                  | cognitive load theory             |
| Desirable difficulty      | Difficulty that slows acquisition can raise long-term retention; retrieval strength ≠ storage strength | Robert A. Bjork, term coined 1994 |

Cite these effects as the origin of a principle, never as a measured effect size for documentation.

## Self-set baselines

These are this skill's own defaults - reasonable, untested, and meant to be agreed with the user rather than quoted as an industry bar.

| Baseline                    | Value                                                                      | Where it came from                                                                                                                               |
| --------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Checkpoint spacing          | Every 3-5 steps                                                            | A prescription in the `technical-tutorials` open-source skill, adopted because it divides a seven-step maximum sensibly. Self-set, not measured. |
| Pass threshold              | All six criteria hold on one cold run                                      | Assembled from the sourced rules above; the gate itself is self-set.                                                                             |
| Fading schedule             | Full example, then diff, then requirement, across early/middle/late thirds | Guidance fading is sourced; this particular three-stage split is not.                                                                            |
| Companion-branch CI cadence | Weekly, plus on commit                                                     | Chosen to catch product drift between releases. Pick the cadence that matches your release train instead.                                        |
| "Split it" trigger          | Measured runtime over 60 minutes                                           | The 60-minute ceiling is sourced; splitting rather than trimming is a judgement call.                                                            |
| Transfer-test delay         | Ten minutes after the last checkpoint                                      | Long enough that the last code block is not on screen. Arbitrary otherwise.                                                                      |

When you state one of these to a user, say it is a starting default. Presenting a self-set number as a standard is how a docs team ends up defending a figure nobody can source.

## What real organizations do at the same three points

None of the three baselines above matches a published practice at its stated granularity, but each sits near a real, citable one a team can compare itself against instead:

- **Checkpoint spacing.** Diátaxis argues for a checkpoint at every single step ("every step the learner follows should produce a comprehensible result"), tighter than this baseline. Google Codelabs, its own tutorial-authoring format, constrains total length rather than checkpoint interval: five to ten steps per codelab, split into two above that. freeCodeCamp's two-minute rule forces a passing-test checkpoint after nearly every step. None of the three publishes an "every 3-5 steps" rule.
- **Pass threshold.** No org publishes a tutorial-specific six-item gate, but each criterion has a named individual source outside this skill: output matching documented output is task success, a core usability-testing metric; a checkpoint passing without help echoes the unassisted-completion condition in historical software acceptance-test designs; zero prerequisites discovered after step 1 is the Good Docs Project's own "before you begin" promise, worded as avoiding a reader "getting halfway through a tutorial and discovering they don't have something needed"; and the unaided repeat on an untaught variation is far-transfer testing, a standard instructional-design evaluation method distinct from the near-transfer worked-example studies cited above.
- **Fading schedule.** Renkl and Atkinson's own experimental designs fade continuously rather than in three fixed stages: a complete example, then one solution step blanked, then more blanks added incrementally, until only the bare problem remains. The three-stage shape here is a coarser, more authorable version of a continuous effect, not the effect's own documented shape.

## Named frameworks and why each fits

- **Diátaxis** - the only framework that defines the tutorial _as an artefact type_ and separates it from the how-to. It supplies the reliability constraint the whole skill rests on.
- **The Good Docs Project tutorial template** - the only widely used template with hard structural limits, and the only source for the size numbers.
- **Backward design** (Wiggins & McTighe, _Understanding by Design_, 1998): three stages, in order - identify desired results, determine acceptable evidence, plan learning activities, matching this skill's own order of objective, then checkpoints and the transfer test, then steps. Naming it stops the common inversion, where the author writes the feature walkthrough first and reverse-engineers an objective. Documented criticism to respect: pre-set goals can underestimate learners, so treat the objective list as a floor.
- **Kirkpatrick's four levels** (1954; popularised 1959/1994) - reaction, learning, behaviour, results. The documented failure mode is the one tutorial authors have: teams get stuck at levels 1-2 and never measure behaviour. Completion rate maps to level 1, the transfer test to level 2, and downstream product use to level 3.
- **Cognitive load theory** - see the table above.

Frameworks deliberately _not_ invoked:

- Gagné's Nine Events - built for instructor-led sequences, not a page.
- ADDIE - a program lifecycle, so it belongs to a curriculum skill.
- The Socratic method - Diátaxis is explicit that a tutorial gives actions rather than interrogating the learner.

## Deliberately excluded

- Any completion-rate benchmark. The activation bands quoted in developer-marketing material are self-reported vendor numbers about signup funnels, not tutorials. Compare a tutorial against its own baseline instead.
- Any claim about how long a learner will tolerate a tutorial beyond the sourced 15-60 minute band.
