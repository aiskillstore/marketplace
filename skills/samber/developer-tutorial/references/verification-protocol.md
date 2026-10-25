# Verification protocol

A tutorial is verified by watching a learner run it, not by reading it. The author's machine and the author's head both lie: one has the dependencies, the other has the answers.

## Choosing the runner

- Match the declared audience level. A senior engineer breezing through a beginner tutorial proves nothing - they patch the gaps unconsciously and report success.
- Never the author, and ideally not the author's team.
- Two runners beat one: a first-time evaluator and someone already fluent in the ecosystem hit different walls.
- Where the tutorial has an enterprise or internal-tooling audience, one runner must go through the real access request, not a pre-provisioned account.

## Environment

- Clean machine or fresh container: no cached credentials, no globally installed toolchain, no leftover project directory.
- The exact OS and runtime versions the tutorial declares - and one version newer, to see how loudly it breaks.
- Install from the published artefact (registry package, released image), not from the working tree. That is what the learner will have.

## Running it

1. Hand over the tutorial link and nothing else. No verbal setup, no "oh you'll also need…".
2. The runner narrates aloud; the observer stays silent and takes notes. Answering a question destroys the data point you came for.
3. Timestamp the start of each step and each checkpoint. The gap between two timestamps is the friction.
4. Record every hesitation, re-read, scroll-back and tab-switch away from the page - each one marks a place the text failed to carry the learner.
5. Let failures play out. The recovery path is part of the artefact under test.

## Log every event as one of four kinds

| Kind                | Meaning                                                         | Action                                                                 |
| ------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Defect              | A command failed, or output differed from the documented output | Fix before shipping. Non-negotiable.                                   |
| Hidden prerequisite | Something needed that wasn't in "Before you begin"              | Move it up; add a check command.                                       |
| Concept gap         | The learner did the step but couldn't say what it did           | The step introduced more than one idea, or explained none. Split it.   |
| Friction            | Hesitation, re-read, wrong guess that self-corrected            | Rewrite the sentence; usually an ambiguous pronoun or an unnamed file. |

Anything the runner "figured out" is a defect, not a success.

## The transfer test

Ten minutes after the last checkpoint, ask the runner to perform the objective once more on a variation you never demonstrated - a different field, a second endpoint, another event type. Give them the reference docs and no help.

- They do it → the skill transferred; the fading worked.
- They do it by scrolling back and adapting the last code block → partial; move the fade one or two steps earlier.
- They can't start → the tutorial was a long quickstart. Add a produce-it-yourself step before the final checkpoint.

This is the only check that distinguishes a tutorial from a page of copy-paste, and it is the one authors skip.

## Keeping it verified

Tutorials rot faster than quickstarts: more steps, more surface, more product drift.

- Keep a companion repository with one branch or tag per checkpoint, generated from the published steps rather than maintained by hand.
- Run a CI job per checkpoint branch: install the published package, run that checkpoint's command, assert the documented output.
- Schedule it (weekly is enough) as well as running it on commit. Tutorials break when the _product_ ships, not when the docs repo changes.
- Fail the docs build, not an advisory job - a red mark nobody owns gets muted within a month.
- Track the age of the last successful run per checkpoint, not the last edit date. An untouched tutorial that still passes is healthy; a recently edited one that hasn't run is not.

## Instrumentation to add before publishing

- A completion event fired at the final checkpoint, plus an event per checkpoint, so drop-off is per step rather than per page.
- Copy-button clicks per block: blocks nobody copies are usually blocks nobody reaches.
- Search and support queries quoting a step verbatim - the fastest signal that a sentence is ambiguous.
- Downstream: whether completers go on to perform the same task in the product within a week. Completion without downstream use means the tutorial taught the tutorial, not the product.
