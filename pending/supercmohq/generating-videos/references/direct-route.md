# The direct route

One clip. Everything the video needs fits inside the model's longest clip, in one continuous shot.

## Steps

### Step 1: Pick the mode

The mode is what goes on the call beside the prompt. `list_video_models` says which ones the chosen
model accepts.

| The brief is… | Mode | What you pass |
| --- | --- | --- |
| A scene described in words, no image | **text-to-video** | `prompt` only |
| A still to bring to life — "animate this", "make this move" | **image-to-video** | `prompt` + `start_frame_image` |
| A move from one held frame to another | **start→end transition** | `prompt` + `start_frame_image` + `end_frame_image` |
| A subject or style to carry into a new scene, not tied to a specific frame | **reference image** | `prompt` + `reference_images` |
| Motion or style taken from existing footage | **video-to-video** | `prompt` + `reference_videos` |
| Timed to an existing track — a beat, a read to lip-sync to | **audio-guided** | `prompt` + `reference_audios` |

**A start frame cannot be sent with any `reference_*` input.** A clip carrying a start frame carries
nothing else — no reference images, no reference video, no audio track, and including one fails the
call. Where a person, a product or a style has to match an image that isn't the start frame, pass
that image as a reference and drop the start frame.

The other modes combine freely, within what `list_video_models` says the model accepts.

### Step 2: Ask for anything still missing

Ask only for what would change the result and can't be sensibly defaulted:

- **How long the clip runs** — `list_video_models` gives the model's shortest and longest.
- **The aspect ratio**, where the brief doesn't say and the destination decides the crop.
- **Whether the clip carries sound.**
- **Whether a second image is an end frame** — one the clip finishes on — when the user supplied more
  than one and hasn't said what each is for.
- **Whether a supplied image is the start frame or a reference**, when the brief doesn't say. The two
  cannot be combined, so this decides what the clip can carry.
- **What to keep from a supplied video and what to change** — the motion, the camera move, the style
  — when the brief only says to use it.
- **What a supplied audio track is for** — words to lip-sync to, or a beat to cut the motion against.

Put them in one message rather than asking one at a time. If the user has said they don't want to be
asked, pick sensible values, say what you picked in one line, and carry on.

### Step 3: Decide what happens in the clip

One line per beat, in order, saying what moves.

**Fit the beats to the seconds.** Each beat runs two to four seconds of the clip, so its length
decides how many it has. Fewer, longer beats render; more, shorter ones get dropped or mangled. If
anyone speaks, the words have to fit too, at about two to three words a second.

**It is one continuous shot.** The beats run through it without a cut. There is no storyboard sheet
here to fix the frame on the far side of one, so a cut lands on whatever the model invents.

**With a start frame**, the first beat opens on that image exactly as it is — nothing enters, nothing
moves position, nothing changes state before the motion starts. If there is an end frame, the last
beat finishes on it.

**With a source video**, the motion comes from it. Say what changes — the subject, the setting, the
style — and leave the movement alone.

**With an audio track**, the beats land with the track. Say what happens on it, and where anyone
speaks, that the words come from the track rather than being written again in the prompt.

### Step 4: Write the prompt

Trigger the `writing-video-prompts` skill workflow with the beats from Step 3, the clip's duration,
the model and aspect ratio, a script segment if anyone speaks, and the supplied media with what each
one is for.

It returns the prompt as text, and the order it labelled the media in. Nothing is generated there.

### Step 5: Generate

Call `video_generate` with one request:

- `prompt` — the one from Step 4.
- The media for this clip, in the mode Step 1 picked: `start_frame_image` and `end_frame_image`, or
  `reference_images`, `reference_videos` and `reference_audios` **in the order Step 4 labelled them**.
- **A start frame cannot be sent with any `reference_*` input.** Including one fails the call.
- `duration`, `resolution`, `aspect_ratio`, `generate_audio`. Omit `model` to use the default; set it
  only if one was chosen.

To give the user several takes of the same idea, put the same request object in the list more than
once. To give them different ideas, write a different prompt for each and add one object per idea.

The clip can come back as `{status: "pending", …}` — a job handle, not a failure. Pass that exact
handle to `job_status`, and again if it is still pending. Never re-run a pending clip; that starts a
second billed job.

### Step 6: Return

One clip is the whole video. Return its URL and local file path.

## Edge cases

- **The video needs more than one clip** — the length asked for is longer than the model's longest
  clip, or the brief covers more than fits in one. Switch to the storyboard route and hand the
  supplied media over as references, so the person, place or product they show carries into every
  sheet and every clip. A start frame pins only the clip it is attached to; as a reference it holds
  across all of them.
- **A start frame doesn't show something the brief needs** — a person who has to match an actor
  image, or a product that has to match its own photo. Say so, then either pass that image as a
  reference instead of the start frame, or switch to the storyboard route. A start frame cannot be
  sent alongside either.
- **`end_frame_image` rejected** — not every model supports it. Check `list_video_models`, then either
  switch to a model that does or use the start frame alone.
- **`reference_audios` rejected** — not every model takes a driving track. Check `list_video_models`;
  where none of the accepted models does, generate the clip with its own audio and say the supplied
  track wasn't used.
- **The model refuses the frame on content grounds** → say which element is blocked instead of
  retrying. You can't reword your way around a supplied image.
