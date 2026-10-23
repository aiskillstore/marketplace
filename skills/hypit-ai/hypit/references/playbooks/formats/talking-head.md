# UGC and talking-head performance

A compelling person speaks to the viewer. Their attitude carries the piece; Caption, evidence and MG
help the viewer follow it. A ranking board is one possible companion, not a requirement of UGC.
For that relationship, combine this page with [Ranking](ranking-listicle.md).
When evolving demonstrations and MG carry much of the argument, use
[Presenter-led visual explainers](presenter-led-explainer.md) for their relationship to that performance.
This relationship follows the speaking performance, whether its footage is newly made or retained
from a recording.

## One useful image can carry the whole performance

Make a character-and-scene image with the presence, camera distance, posture and available graphic
space the video needs. For a performance expected to stay mostly full-frame, its final aspect ratio
is a useful starting point. Preserve the body and gesture room needed across its later uses;
destination viewports can change around the same footage. [Image direction](../craft/image-direction.md)
owns that craft. A person placed slightly right can leave room for an icon on the left; the image
prompt describes the person and visible setting, while the icon belongs to its component. A table
or the direction of their seated body can make that placement feel inhabited. Choose it for this work.

For a reusable frontal speaking image, explicitly keep the face toward the lens, with no head tilt
or rotation. A vivid attitude and an easy speaking gesture give this settled view life. The
[idle principle](../craft/image-direction.md#choose-an-idle-state-for-the-encounter) relates that pose
to addressing the viewer; the generated performance can move and react within the encounter.

Cast the person's vocal appeal with [Voice direction](../craft/voice-direction.md).
Use that same image and the person's recurring voice reference for every ordinary talking clip.
Each clip can return to the same useful visual premise and contribute another piece of the edited
performance.

Natural cuts are part of the desired result. A small change in pose between passages can make the
video feel like a creator's edited recording. Stable character-and-scene references can support each
clip independently because this work wants edited speech rather than an unbroken simulated recording.

## Use the tested Speaker Kit when its shape fits

For a single presenter returning to one useful camera image through natural edited cuts, `speaker-v1`
from `@hypit/seedance-kits` is a tested fit. It combines that character-and-scene image, one voice
reference, Script dialogue, a Recipe for recurring direction, and optional action Text for the passage.
The installed Kit package owns its exact assembly, reference order and Recipe choices.
[Generated video direction](../craft/video-direction.md) explains what the image, voice, dialogue and
passage direction each contribute. A work whose camera, cast, or performance relationship differs can
use another Kit or ordinary authored direction.

For this edited talking-head form, start with the Speaker Recipe's
`edit-rhythm: pause-trim-jump-cuts`. The camera can stay fixed while the performer remains expressive.
[Video direction](../craft/video-direction.md#direct-camera-and-cuts-as-part-of-the-passage) explains
choosing the rhythm for the passage; the installed Kit documents the wording this option supplies.

Action supplies what the scene means to this person. For a teasing ranking host, amused disbelief,
a knowing look and a compact dismissive gesture are more useful than a limb-by-limb animation plan.
Give a few actions a reason: a shrug dismisses an argument; a quick lean makes a punchline personal.
Let speech, Caption or MG carry exact numbers while the hand makes a readable emphatic gesture.

One useful action direction, alongside Script dialogue, is:

```text
Play this as an affectionate roast from someone who knows the subject well. Start with amused
certainty, let the comparison earn a brief disbelieving look, and land the last line with a small
knowing shrug. The free hand makes relaxed emphatic gestures; keep the microphone easy and steady.
```

This illustrates attitude and a few visible beats; it does not prescribe every creator's personality.
See [Generated video direction](../craft/video-direction.md) for listeners, gestures and cuts.

## Let speech and graphics do different work

Write natural stages in Script. For newly generated clips, estimate each Segment before choosing a
literal generation duration. When the work retains recorded speech, its edited delivery supplies
the actual duration; [media preparation](../../production/media.md) explains how to prepare and
align it. A Segment can contain several edited shots, Caption Cue separators, graphic changes and
speaking turns. Choose its boundaries from the performance it carries.

Normalize the produced speaking media, align its own audio to its Segment, construct its equal-length
Timeline Window, and project that alignment through the local domain/Window relation. Keep that performance's sound
when B-roll covers its picture. Place evidence on
Selections and reveals on the component's declared timing inputs. A persistent board can continue
through a cut while the current portrait, evidence image and Caption change.

Watch whether the person feels engaged and whether the visual layers support that engagement.
Stable identity and a coherent setting matter; identical pose at every seam does not. A static
expression, mechanically repeated gestures or relentless intensity can undermine the result even
when every requested word is present.
