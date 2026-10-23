# Street interview

An interviewer encounters someone with their own life, asks something, and receives an answer worth
watching. The guest usually carries the story; the interviewer helps the viewer discover it.

## Establish the encounter, then derive attention

For the three-view method, generate a shared image containing both people and their real spatial
relationship. Derive the guest close view and interviewer close view directly from it. In the
interviewer view, retaining part of the guest at the opposite edge keeps the exchange legible.
The guest looks toward the interviewer, and the interviewer looks back across the same screen axis.
That attention and a comfortable microphone position give the reusable views their
[idle state](../craft/image-direction.md#choose-an-idle-state-for-the-encounter). Opening, reaction
and departure actions can then develop from this encounter in their respective video passages.

```text
shared street scene ──> guest close view
                    └─> interviewer close view, retaining part of guest
```

The [worked image directions](../craft/examples/conversation-images.md#street-interview-views)
show how little the derived prompts need to add once the shared image is doing its job.

`street-interview-v1` uses this supplied set: interviewer A, guest B, shared view, then the two voices
in A/B order. All ordinary generated clips reuse it. Its three-view limit is the design of this Kit, not a
restriction on every street interview or on Hypit. The interviewer keeps the microphone and moves
it toward whoever speaks; extending it to the guest is not handing over ownership.

## Cut toward the person who matters now

Guest answers can favor the guest close view. A brief neutral interviewer question
can stay in the shared view; disbelief or an emotionally important challenge earns the interviewer
close view. This directs attention rather than alternating cameras on a timer.

Action can specify cuts between the Kit's supplied setups. Several questions and answers fit in one
Segment and one generated clip. Keep the chosen framing behavior within each setup and let the cut
move directly to the next; an invented travel shot between cameras changes the scene's grammar.

## Give the encounter a before and an after

At the opening, the guest is occupied with something plausible: looking into a bag, checking an
object, or looking down. The interviewer takes a small step forward and asks; the guest looks up
or turns toward them in response. Begin the exchange naturally rather than imposing a fixed silent
delay before every line.

At the end, return attention to the guest and let them begin to turn away after the final thought.
These small actions imply life outside the clip. They work because of their cause, not because
every interview must contain the same bag check and exit direction.

For example, action alongside the Script can make an opening's causal sequence concrete:

```text
BOY is interviewer A; WIFE is guest B. Open in the shared reference setup. She is looking into her
bag as he takes a small step toward her and begins the question. She looks up toward him in response.
Cut directly to her supplied close view for her answer. Use the shared view for his brief follow-up,
and his supplied close view when the surprising answer earns his disbelief. Keep the reaction
interested and spontaneous rather than theatrical; he continues to hold and position the microphone.
```

On the final passage, a short additional direction can return to her close view and let her begin
turning away after the punchline. The opening and ending actions belong to those actual passages;
intermediate clips carry the behavior of their own exchange.

For the middle, give a few readable gestures a purpose: amused certainty, a compact shrug, a glance
that registers a surprising answer. Avoid exaggerated emotion, constant motion and exact numerical
finger poses. The performer should seem to respond, not execute an animation checklist.

## Make a reveal one event across several layers

A single answer Moment can update one slot in an emoji strip, start a short sound and trigger
a colored flash. Earlier answers remain visible; future answers remain question marks. Reuse the
same Script Moment for these consumers so a changed delivery still makes the reveal land together.

Design Caption colors, placeholder and answer icons, flash colors and sound character as one visual
and rhythmic treatment. An icon's role can supply an accent color; not every layer needs the same
color. Use actual image assets when matching icon shape and color matters.

This answer strip is a normal project component. Its outer Window owns visibility; child Moments
own reveals; its implementation owns the resulting persistent state. See
[Track authoring](../../production/track-authoring.md) for that distinction and other Track roles.

## Caption can follow the guest's head

When tracked placement serves the work, produce the speaking footage with ordinary Caption placement
available first. Face detection on that footage can then supply boxes; expand the chosen person's
boxes to head regions and render again with Caption anchored above them, reusing the paid media.

Use [Caption tracking](../craft/caption-tracking.md) when this placement serves the piece. It is a
specific production loop with an external measurement step, not a required first step for interviews.
Fixed interviewer Caption and tracked guest Caption can coexist. Fine styles handle these examples;
a new structural Caption treatment can be a project Caption family using the shared Script,
Caption data and semantic timing.
