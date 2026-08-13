---
name: writing-video-prompts
description: Writes the motion prompt for a video clip — what moves, how the camera behaves, the physics and the audio, in the shape the chosen model wants. Works from a brief alone, from a start frame, from a source video, or from a storyboard sheet where each panel becomes a cut. Handles one clip or a whole set, returning one prompt per clip. Nothing is generated here. Use when a clip's model, duration and content are settled and it needs the prompt written.
license: Apache-2.0
metadata:
  version: "0.5.0"
  category: creative
  summary: "Translates your scenes into the highly specific, detailed instructions that different video models require. It times the camera motion and steers around known AI rendering limits to match your exact visual brief."
---

# Clip prompts

Turn a clip into a prompt its video model will honour. **Text only — nothing is generated here.**

**A video may be one clip or several.** Write a prompt for every clip in it, then hand them all back
together. Clips in one video share a model, an aspect ratio and a look.

Write only what the clip actually has. No person on camera means no performance direction, no product
means no product rules, no speech means no dialogue.

## Workflow

### Step 1: Read what the clip has

Ask only for what would change the prompt and can't be defaulted.

- **The model and the duration.** Where no model was named, use `seedance-2.0-fast` and say so. The
  aspect ratio is a call parameter rather than prompt text — carry it if it was given, don't ask.
- **What happens in the clip** — as beats, or as a single action.
- **The media, and what each one is for** — a storyboard sheet, a start frame, an end frame,
  reference images, a source video, an audio track. **Any of them may be absent**, and they differ from
  clip to clip.
- **The dialog segment**, where anyone speaks, and whether they are on camera or heard over the
  picture.

### Step 2: Pick the clip's form

**With a storyboard sheet, one cut per panel** — panel 1 is the first cut, panel 2 the second, hard
cut between them. 

Without a sheet, cut only where the brief asks for one.

**Where a beat's opening frame is fixed** — by a panel or by a start frame — the hands, the grip, the
product, the props and the positions are already there when it opens. Write what happens next, not
how it starts.
Write "a hand reaches in" or "she brings it into frame" only when the frame genuinely has no such
element. Introduce something that is already there and the model renders a second one — an extra
hand, a duplicate arm, a doubled person.

### Step 3: Read the chosen model's guide

| Model | Guide |
| --- | --- |
| `seedance-2.0` | `references/prompt-seedance.md` |
| `veo-3.1` | `references/prompt-veo.md` |
| `gemini-omni` | `references/prompt-gemini-omni.md` |
| `kling-3.0-pro` | `references/prompt-kling.md` |
| `grok-imagine-video` | `references/prompt-grok.md` |
| `wan-2.7` | `references/prompt-wan.md` |

The `-fast` / `-lite` / `-turbo` / `-standard` / `-mini` variants share their family's guide.

**The guide owns how the prompt is laid out** — the order the elements go in, how references are
labelled, how speech and sound are marked, and how to keep something out of frame. Follow it on all
of those, over anything the steps below imply about layout.

**It does not decide whether the clip cuts.** Step 2 already did, from the media. A guide showing how
to write a sequence of shots is giving you the layout to use *if* the clip has one — not a reason to
add cuts to a clip that doesn't.

### Step 4: Label the media

Where more than one piece of media goes on the call, name each one in the prompt, in the order it
will be passed, and say once what each is. Unlabelled, the model picks its own subject out of the
set. **The labelling convention comes from the model's guide** — a numbered slot, a tag, or plain
words. A clip carrying a single start frame and nothing else has nothing to label — just say what it
opens on.

- **A storyboard sheet** — labelled once at the top as the storyboard for this clip. Don't contradict
  it and don't caption it: a sentence that would work as a caption for the panel is a description of
  a still, so write that panel's beat in motion instead.
- **A start or end frame** — named as the frame the clip opens or closes on.
- **The person** — labelled on first mention in a beat, then the plain noun. Repeat the label later
  in the same beat and the render snaps back to the reference, breaking continuity.
- **The product** — label it where it is shown intact: first introduction, a hero close-up, a label
  point-out. Drop the label during any verb that changes it — opening, tearing, pouring, scooping,
  applying, drinking, mixing, putting on — because carrying it through forces the product back to its
  reference state mid-beat, so an opened jar snaps shut. Pick the label up again once it is shown
  intact.
- **Several product images** — point at whichever shows the angle that beat needs.

**Never put a label inside quoted speech.** Quoted text is read aloud as written, so the label gets
spoken.

### Step 5: Read the storyboard

Skip this where the clip has no sheet.

Run `image_analysis` on the sheet before writing anything, and take these from each panel as it
actually rendered:

- the camera position — held at arm's length, locked off, over the shoulder
- the framing distance
- the action
- which hand is doing what
- where the product is — held, set down, worn, hidden, absent
- the expression

**Where the sheet and the plan disagree, the sheet is what the model will see, so the sheet wins.**
Write the cut to the panel, and say which panel disagreed and how.

### Step 6: Write the clip

Write 6a to 6d, laid out in the order the model's guide sets out.

**6a — The look.** One line: the light, and how the camera behaves across the clip. Add the delivery
register where anyone speaks.

**6b — The beats**, in order.

- **Each cut is one or two sentences, carrying one verb that moves something.** A second moving
  verb is a second cut.
- **With cuts**, head each with its number and its span — `Cut 2 (3.5-7s):` — and end every cut but
  the last with a hard-cut instruction on its own line. Both go in whatever the guide says about
  timings: the spans are what make the cuts add up to the clip's length, and without the hard-cut
  line the model runs the beats together as one continuous move.
- **Without cuts, time the beats only where the model's guide uses timings.** Some models read a
  written span; others are made unstable by one and want the beats in order with the pacing following
  the action.
- **How long each beat is.** Each one runs two to four seconds of the clip, and they add up to its
  length exactly.
- **The first beat opens already underway** rather than on a held pose. Where a frame is fixed, it
  opens exactly on what that shows — nothing enters and nothing changes state before the motion
  starts. Where a person is on camera, that means hands already moving or a reaction already on the
  face, and the first words landing at the top of the beat rather than after a pause.

**6c — The camera, in every beat.** Where a sheet or a start frame already fixes what is in frame and
where the camera sits, only how it moves is yours — a push in, a pull back, a tilt, a pan, a rack
focus, a handheld sway. Without one, write the framing and the position too. Locked off means the
frame doesn't move and everything moves inside it, so keep any word suggesting an unsteady grip or a
travelling lens out of those beats. At arm's length the camera is the phone and carries a small
natural unsteadiness; nothing showing a handset, a screen, or either reflected belongs in shot.

**6d — The person, where one is on camera.**

- **Hands, counted at every moment.** A phone held at arm's length takes up one hand, so a single hand
  is free to act; a locked-off shot leaves both. Describe a third job — hold one thing, work a second,
  point at a third — and a third hand appears. Where hands don't matter to the beat, leave them out.
  When an arm's-length beat calls for two working hands, it can't be shot as framed — send it back to
  the storyboard to re-frame that beat rather than working around it in the prompt.
- **Performance.** Several small movements within each beat, and at least one thing that changes —
  weight moving forward, a breath landing, a grin breaking after a pause. A beat with no change inside
  it reads as a frozen frame. Pitch each one higher than the level you want on screen, since the model
  plays performance back flatter than it is written. Vary the expression from beat to beat. Where they
  speak, let the delivery slip and recover once somewhere in the clip.

**Every beat is bounded by these:**

- **One action per beat** — one continuous motion at one object. Chained verbs get dropped or mangled.
- **Nothing below limb scale.** Moving, holding, tilting, lifting, gesturing and walking render.
  Unscrewing a cap, pulling a drawstring, pumping a pump head, working a zip or a clasp do not. Where
  a beat needs the thing in a new state, open it with the thing already in that state.
- **Interactions respect the physical chain.** Nobody drinks from a sealed bottle. Where the whole
  chain won't fit, open the clip further along it.
- **Positions hold through a beat.** Where something is, how it's held, how it's worn stays put unless
  a visible movement changes it. An unstated change renders as a teleport, and once changed it stays
  changed.
- **Describe only what the media show.** Texture, back panels, interiors and hidden mechanisms
  outside the frame come back invented.
- **Nothing can be written as absent.** A thing named is a thing rendered, whether object, action or
  sound.

Every piece of media also goes to the model on the call, so don't restate what it shows — the same
instruction twice renders a slideshow. But write the prompt full: written thin, the image wins and
the clip comes back as held poses with pauses between them.

### Step 7: Write the audio

Skip this where the clip carries no sound.

Where anyone speaks, split the clip's script segment across the beats at natural phrase breaks,
roughly in proportion to their lengths. The words themselves are exact — no rewording, no insertions,
no deletions — and the pieces must reassemble into the whole segment with nothing heard twice.
**Mark the speech the way the model's guide marks it**; that marking is what drives lip movement.

The audio line says how the speech is produced and what else is heard. On camera: the person speaking
in their own accent, lip-synced to the segments above. As voiceover: spoken off-screen, no mouth
moving. Say what the recording sounds like, following the look the plan named — a phone-shot piece
means phone-microphone audio and room tone.

Where anyone speaks on camera, give each beat a moment with the mouth closed while the hands work. Lip
movement is the weakest thing the model renders, and continuous speech across a clip smears it.

Ambience is room tone plus what the beat's action actually makes. Name the source and the surface it
happens on, keep it to two or three sounds at once, and never write a sound as absent — a sound named
in a beat whose action doesn't produce it makes the model add the action to match. Don't repeat spoken
words in the ambience line, and don't name or imply music unless the user asked for it.

### Step 8: Hand the prompts back

Write every clip's prompt before any of them is generated. They don't depend on each other, and a
prompt is far cheaper to fix on paper than after it has rendered.

Hand back one prompt per clip, in order, each tied to its clip, along with the media that go with it
and the order they were labelled in.

## Edge cases

- **No beats were supplied, only a brief** → write the clip as one continuous shot and split it into
  beats yourself, to the seconds in Step 6.
- **The beats need more time than the clip has** → say so and hand back the beats that fit. Don't
  compress them into fewer seconds; the extra ones get dropped or mangled in the render.
- **A start frame arrives alongside reference images** → they cannot be sent on one call. Say which
  the clip should keep, and write the prompt for that form.
- **The model is one with no guide here** → call `list_video_models` for its accepted inputs, and
  write to the guide of the family it most resembles.

## Reference

**Model prompt guides — read the one for the chosen model:**

- `references/prompt-seedance.md` — native audio markers, one-move-per-shot, storyboards.
- `references/prompt-veo.md` — cinematography-first order, `SFX:` / `Ambient noise:` markers, timecodes.
- `references/prompt-gemini-omni.md` — conversational editing of an existing clip; edits, not extends.
- `references/prompt-kling.md` — director-script style, `@Element` references, per-speaker dialogue labels.
- `references/prompt-grok.md` — tight front-loaded briefs, positive-only exclusions, one action per clip.
- `references/prompt-wan.md` — front-loaded prose, multi-shot timestamps, driving-audio sync.
