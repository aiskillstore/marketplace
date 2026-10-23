# Voice and performance

Read this when deciding what performance carries a passage, how a recurring person keeps one voice,
or whether an off-screen passage continues an A-roll performance or uses independent speech.
[Voice direction](voice-direction.md) owns casting an appealing voice and writing its direction.

## Let the Segment reveal the A-roll

A Segment is one authored passage in the Script. Before production it has identity and meaning but no
seconds. A-roll names the performance carrying that passage. Its prepared media supplies duration;
spoken words can acquire local timing through semantic preparation when the composition needs their
positions. Visible performance can carry
picture and sound together; audio-only performance carries the passage while other contributions
supply its picture.

Timeline construction uses the prepared media's Extent to create an absolute Window within the
complete work, ordinarily after the previous passage, or at an authored position.
The work can also contain graphics-only passages before, between or after those performances.
[Timeline authoring](../../production/timeline.md) owns the exact temporal DAG;
[semantic projection](../../production/timing.md) maps separate NarrativeAlignment evidence through
its complete local domain and equal-length Window.

For spoken work, ask **who is speaking this Segment?** The selected visible performance carries
words, mouth movement, gesture, gaze, delivery, picture, and sound together.
In a multi-person exchange, the speaking performance can include listeners, several turns, or camera
cuts while still carrying one Segment. The number of people visible in the frame does not determine
how many semantic clocks exist.

A recurring presenter, podcast speaker, interview participant, or dramatic character continues to
own their own lines even while another picture covers them. Visual handoffs, coverage, Caption, MG,
and Effects are authored against the time that performance established. If an edit changes the
performance's actual length, prepare the edited media before assembly and realign it when those
dependent layers use semantic timing.

A wordless Segment can identify a real performed passage, such as a dance or reaction. Its prepared
media supplies a local domain without spoken words. A graphics-only interval can instead contribute
an authored Span to Timeline with no media. Choose from the content the passage actually uses.

## Keep the performance role separate from the picture

A-roll identifies a performance's role in the work. Its accepted material, Script relationship and
Timeline Window persist while the author changes its visual use. The picture can lead the frame,
share space, appear more than once, become part of a diagram or leave the picture entirely. A large
app recording can lead attention while a small presenter supplies the passage's words and timing.
Several such changes can happen within one source Window; a visual treatment can also continue
across several sources.

The covering B-roll may even show the same person doing a silent lifestyle action. Seeing a person
while hearing words does not by itself make that picture the speaking source or create a new speech
source. An Audio Clip plays the explicitly declared performance audio, while a Visual Clip
chooses what to show. The same source clip can also serve as an independently timed replay or example elsewhere.
Its role follows that use; size, crop, transparency and the presence of a face do not establish it.

Follow the relationship the picture needs: a [Visual Clip](../../production/visual-clips.md) places
one source occurrence, while a project scene can coordinate several materials and events. A change
of emphasis can be a direct
cut, a held arrangement or a continuous motion. Decide from the idea and viewing rhythm. For a
continuous move, retain the source playback position while directing the viewport's motion; for a
direct cut, make the two intended states meet at the chosen event. Speech remains independently
connected through an [Audio Clip](../../production/audio-clips.md).

The [presenter-led explainer guide](../formats/presenter-led-explainer.md) develops the whole-work
relationship among performance, demonstration and graphics. [Graphic composition](graphic-compositions.md) owns
their visual hierarchy, and [Spatial layout](../../production/spatial.md) owns geometry and fitting.

## Let neighboring A-roll performances keep their time

The usual A-roll assembly places Segment performances one after another without consuming either
side of their duration. This fits how the work is authored: `hypit estimate` helps size each request so
its words, delivery and action belong naturally in that generated passage, and speaking video models
normally use the requested clip to perform the line. Asking one generated clip to remain silent for a synthetic
half-second handle at its beginning or end works against both that sizing and the model's performance.

A duration-consuming crossfade between neighboring A-roll clips can eat into the word windows that
each performance established. The result may contain simultaneous speech at a boundary and weaken
the listening rhythm. For ordinary creator speech, podcast turns, interviews and short drama, this
makes a direct join between the prepared Segment performances a practical starting point. Visual coverage
and effects can still cross that seam without changing the underlying speech time.

Deliberate interruption, overlapping dialogue or musical phrasing can use explicit Window positions.
[Timeline authoring](../../production/timeline.md) supports gaps and overlaps directly.
The sources retain their local timing; a crossfade or other coordinated picture treatment belongs
to the visual component owning that behavior. Sequential Window construction remains the concise ordinary
choice for creator speech.

## Give a recurring person one accepted voice

When the intended work retains a person's recorded delivery, prepare that passage and align its
actual sound to Script when downstream relationships need word or boundary positions; its picture,
if retained, is available to Visual Clip. A supplied recording
may instead guide a new performance or provide a short Voice Reference. Voice Design can make such
a reference when a new performance needs one and none was supplied; Voice Clone can then perform
independently narrated lines from Script. The intended use of the recording, not its mere presence,
decides which relationship holds.

A **Voice Reference** is an ordinary accepted audio Resource that establishes a person's vocal
identity. Reusing that Resource wherever the same person performs is what carries the relationship
through the production.

For newly generated performances, give each recurring speaker their own Voice Reference. A silent
listener does not acquire a voice merely by appearing in the picture; when that character speaks
elsewhere, their reference follows them into the new performance.

When the user supplies the exact private voice they want, prepare a clean representative excerpt as
the Voice Reference. Otherwise use [Voice direction](voice-direction.md) to cast the character through
Voice Design and choose its sample line. A public character type or an imagined voice can be designed
directly.

For a newly cast person, a short designed sample is a strong starting point: it establishes a usable
voice at modest generation cost and stays easy to carry into speaking-video requests. About five
seconds of clear, natural speech usually gives the model enough vocal identity without spending
reference duration on a finished passage. Choose words that exercise the delivery the work needs;
keep the sample free of other speakers, music, clipping, heavy room echo, and long silence. When one
video request includes several speakers, give each a compact reference and keep their combined
duration within the selected model's reference-audio limit. The selected model's documentation owns
exact count, duration and format limits.

Once accepted, reuse that same Resource wherever the same person must sound like themselves.

## Let one reference support different performances

The useful dependency is shallow:

```text
Voice Design or supplied audio
             ↓
     accepted Voice Reference
          ↙             ↘
visible A-roll      audio-only A-roll
```

An A-roll-capable video model receives the short reference and the actual Script while generating
the person's visible speaking clip. Voice Clone receives the same reference and the passage's Script
when the work needs independent speech; it generates that passage's audio, whose length follows the
passage and the selected speech model's request limits rather than the short reference's duration.
These are two uses of one ordinary Resource, not two voice identities.

A work may combine them. A host can perform visible A-roll and later narrate a passage that has no
underlying on-camera performance; using the same Voice Reference makes both sound like the same
person. Another passage covered by B-roll may still be audio from the A-roll performance beneath it. Decide
from the passage's expressive construction, not from whether the face happens to be visible at that
instant.

## Choose between visible and audio-only A-roll

For visible A-roll, the video request receives the character's camera image, Voice Reference and
exact Script dialogue, then returns the picture and sound of that person actually performing. Voice
Design casts the person; its short sample line exists to establish voice identity and need not repeat
any line from the finished Script.

Audio-only A-roll is useful when a Segment is constructed without an on-camera speaking
performance: a desktop point-of-view demonstration, a narration-led montage, a pure MG explanation,
or a product-explanation passage inside an otherwise presenter-led work. Voice Clone
uses the person's existing Voice Reference and the Segment's actual Script to produce that passage.
The resulting audio is normalized like any other performed media and aligned when Caption or another
semantic consumer needs positions inside it. An Audio Clip
Source pairs that ordinary media with its exact Window while Visual Clips, Typography, MG, or another visual Track supplies what the
viewer sees; no compound audio-only semantic object is required.

Choose audio-only A-roll because the passage itself is independently narrated, not merely because
B-roll or graphics happen to hide a visible performance. Use Voice Design to establish the person's
reusable voice and Voice Clone to perform the actual Segment; the casting sample and the finished
delivery have different jobs.

Each vendor's speech models are one package with its own Source import: `@hypit/mimo-speech`
(Xiaomi MiMo Voice Design and Voice Clone), `@hypit/fishaudio-speech` (Fish Audio Voice Design and
Voice Clone) and `@hypit/elevenlabs-speech` (ElevenLabs Voice Design). Use `hypit vocabulary` with a
package name for its author Surfaces. A voice reference designed by one package is an ordinary audio
Resource that another package's Voice Clone accepts. The Source chooses those model semantics; the
Runtime Profile independently chooses the Endpoint that can perform them.

## Treat narration as a sound-picture relationship

Narration means the audience hears speech while the speaker is not the primary visible action. That
description does not reveal how the speech was produced.

- In a visible-performance-led passage, coverage changes the picture while the accepted visible
  A-roll remains the performance and timing authority.
- In an independent-narration-led passage, audio-only A-roll supplies the performance while the
  picture is designed separately around it.
- In a mixed work, each passage can use the relationship that serves it, while recurring people keep
  their accepted Voice References.

Keep three questions distinct:

| Question | What it establishes |
| --- | --- |
| Is the speaker off screen at this instant? | A viewing relationship: speech is heard while its performer is not the primary visible action. |
| Does the sound come from covered visible A-roll or from audio-only A-roll? | The production source and owner of the performed audio. |
| Is this passage visible-performance-led or independent-narration-led? | The Segment's higher-level expressive construction. |

The same visual language can answer these questions differently. Consider a notebook-paper field
with animated steps, labels and panels:

- When that field persists as the place where a product process is explained, its changing graphic
  relationships carry the passage. Independent speech can establish the Segment's semantic time
  while the paper composition supplies its picture. This is an independent-narration-led module.
- When a ranking host says a brief “Top one: the product” over a paper reveal and then appears on
  camera to continue the same judgment, the host's performance normally owns the whole passage. The
  paper reveal is MG coverage over that A-roll, and the sound remains the host performance's sound.

Duration can support the reading but does not decide it. Ask what carries the argument, attitude and
progression, and whether an on-camera performance exists whose words naturally continue through the
coverage. A sustained graphic explanation and a brief graphic reveal can look alike in one frame
while belonging to different constructions.

Segment boundaries express the work's useful modules without acting as source labels. One
independent-narration-led Segment can contain many MG steps through Selections and Moments. One
visible-performance-led Segment can begin under a graphic and later reveal the speaker. Splitting a
generation into two Segments also does not make either one audio-only A-roll by itself; each
Segment's actual performance relationship remains the deciding fact.

Use `../formats/narration-led-demo.md` when independent narration actually organizes a work or
substantial passage. `../index.md` routes to available Format and Craft knowledge for the work's
other relationships.

## Give real performance real semantic time

`../../creation/script-and-time.md` owns duration estimation, literal duration, and alignment. When
the accepted performance has semantic timing, its dependent layers follow the delivery that really
happened.

## Carry the character through the performance

[Voice direction](voice-direction.md#let-one-voice-express-different-thoughts) connects recurring vocal
identity with changing delivery; [Video direction](video-direction.md#direct-the-reason-for-an-action)
connects each passage's meaning with expression, gesture and interaction.

Use [Sound and mix](sound-mix.md) for music, effects, ambience, gain, and the completed mix.
[Transformations](../../creation/transformations.md) connects casting and reference choices to the
target's argument, relationships and presentation.
