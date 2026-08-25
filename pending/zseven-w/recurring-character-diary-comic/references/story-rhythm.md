# Story rhythm

Use this reference to turn an anecdote, conversation, observation, or viewpoint into a short recurring-character diary comic. Preserve the source viewpoint; do not invent a different lesson or inflate a small moment into a grand moral.

## Contents

- [Pass the topic gate](#pass-the-topic-gate)
- [Build one self-contained unit](#build-one-self-contained-unit)
- [Choose 4–8 panels by rhythm](#choose-48-panels-by-rhythm)
- [Lock dialogue before image generation](#lock-dialogue-before-image-generation)
- [Give supporting characters a job](#give-supporting-characters-a-job)
- [Produce a story contract](#produce-a-story-contract)
- [Review the rhythm](#review-the-rhythm)

## Pass the topic gate

Proceed only when the material contains all three layers:

1. **Concrete behavior:** an action, object, choice, or exchange that can be drawn.
2. **Unspoken psychology:** a recognizable want, hesitation, contradiction, or self-protective thought beneath that behavior.
3. **Light reveal:** a final observation or reversal that exposes the gap between the behavior and the psychology without humiliating the character.

Summarize the spine in one sentence:

> While doing **[observable behavior]**, the character is really trying to **[unspoken intention]**, until **[small reveal or reversal]** makes the contradiction visible.

Reject or reframe material when it is only an abstract opinion, requires extensive backstory, has no drawable change, or depends on a forced inspirational conclusion. Prefer a modest, immediately recognizable truth over a manufactured joke.

## Build one self-contained unit

Make each comic understandable without knowledge of earlier episodes. Preserve recurring character identity, but introduce the current situation, relationship, and stakes on the page.

Extract five possible beats before choosing the panel count:

| Beat | Narrative job | Visual evidence |
| --- | --- | --- |
| Situation | Establish where the character is and what is happening | A readable action, place, object, or exchange |
| Pursuit | Show what the character is doing next | Progress, repetition, avoidance, comparison, or a choice |
| Inner pressure | Let the unspoken psychology become inferable | Pause, gaze, posture, object detail, environment, or contrast |
| Reaction | Change the timing or expose another interpretation | A supporting character, interruption, silence, or consequence |
| Final beat | Reveal the contradiction or land the exact viewpoint | The clearest image and the fewest necessary words |

Merge beats when the material is compact. Split a reaction or repeated action only when the extra panel improves timing. Do not add events merely to reach a target count.

## Choose 4–8 panels by rhythm

- Use **4 panels** for one setup, one development, one turn, and one final beat.
- Use **5–6 panels** when the action needs an anchor image plus one or two distinct reactions.
- Use **7–8 panels** only when escalation, elapsed time, or multiple viewpoints genuinely add information.
- Use a large scenic or emotional panel as the anchor, then use smaller reaction or object panels to accelerate time.
- Reserve the strongest visual emphasis for the turn or final beat. A final panel may be large, quiet, or unusually simple.
- Vary panel width, height, inset angle, or border treatment when it serves timing. Do not default to equal rectangles or a rigid grid.
- Unequal rectangles are not automatically irregular rhythm. If every beat still sits inside the same rounded card, row stack, border weight, and rectangular family, redesign the page hierarchy rather than calling the size differences sufficient.
- Treat reaction insets as punctuation: keep the expression or object legible, attach the inset to a clear transition, and reject a floating strip that looks accidentally cropped.
- Give every large empty region one declared job—lettering reserve, pause, subject isolation, environmental scale, or reading-path transition. Remove or reshape leftover packing space.
- Keep the reading path unmistakable. Rhythm is not an excuse for ambiguous order.
- Let rooms, objects, screens, empty space, or another character carry a beat when they communicate more clearly than another view of the protagonist.

## Lock dialogue before image generation

Write a dialogue manifest before composing or generating the page:

| Panel | Speaker | Exact text | Bubble order |
| --- | --- | --- | --- |
| 1 | Character or narrator | Approved Simplified Chinese string | 1 |

Treat every approved string as immutable. Preserve characters, punctuation, wording, speaker attribution, and order exactly. Do not let an image model paraphrase, translate, expand, or add text.

Keep dialogue shorter than the action it accompanies. Remove any line that merely describes what the image already proves. Allow silent panels, especially before or after the reveal. If the source has a distinctive colloquial phrase, preserve it instead of polishing away the voice.

## Give supporting characters a job

Assign each supporting character exactly one primary narrative function:

- **Trigger:** starts the action or poses the question.
- **Contrast:** reveals another attitude or behavior.
- **Witness:** makes the protagonist's contradiction legible through a reaction.
- **Interruption:** changes the timing or prevents a predictable outcome.

Remove a supporting character who does not alter the story, timing, or interpretation. Do not use extras as decoration, and do not make the protagonist speak every side of a conversation. Keep supporting designs distinct enough to follow across panels without competing with the recurring lead.

## Produce a story contract

Record the following before visual production:

```text
Observable behavior:
Unspoken psychology:
Light reveal or reversal:
Exact final viewpoint:
Panel count and reading order:
Beat assigned to each panel:
Dialogue manifest:
Supporting-character roles:
Required props and continuity facts:
Panel visual weights and page anchor:
Border or inset treatment by beat:
Purpose of each large negative-space region:
```

Use this contract as the source of truth during generation, editing, and review. Change it only when the user approves a story change.

Lock story semantics before render implementation. After the semantic contract is stable, draft one or more low-cost evidence views for high-risk actions and directional objects. Choose a view that makes the required relation inspectable, then lock the render contract before final generation. A declared S2 camera, crop, panel proportion, or bubble anchor may vary within its pre-approved alternatives; do not rewrite an S0 action, relation, prop state, identity rule, or dialogue after seeing generated art.

## Review the rhythm

Before approving the storyboard or page, verify that:

- the first beat is concrete rather than explanatory;
- every panel contributes new evidence, timing, or interpretation;
- the hidden psychology can be inferred without a paragraph of narration;
- the reveal grows from the established behavior rather than arriving as an unrelated joke;
- the tone remains observant and lightly self-aware rather than cruel or preachy;
- the final beat preserves the source viewpoint and does not become an advertisement;
- the exact dialogue fits the intended bubbles and remains readable in order;
- the page silhouette does not collapse into an accidental card grid when viewed at normal reading or thumbnail size;
- the anchor, reaction, and final beat remain distinguishable through scale, placement, border language, or stillness rather than only through their written labels;
- the page works as a self-contained story while leaving the recurring character recognizable.

This rhythm review is a planning preflight, not final evidence. Apply the
structured editorial-layout gate to the rendered final page before calling it a
showcase example.
