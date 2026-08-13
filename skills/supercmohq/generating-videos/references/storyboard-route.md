# The storyboard route

The video is planned as a story split across clips, each clip becomes a storyboard sheet, and each
sheet becomes a clip.

**This route runs on `seedance-2.0-fast` unless the user named a model.**

## Steps

### Step 1: Ask for anything still missing

Ask only for what would change the result and can't be sensibly defaulted:

- **How long the whole video runs.** Everything below depends on it.
- **The aspect ratio**, where the brief doesn't say and the destination decides the crop.
- **Whether anyone speaks**, and whether they are on camera or heard as a voiceover.

Put them in one message rather than asking one at a time. If the user has said they don't want to be
asked, pick sensible values, say what you picked in one line, and carry on.

### Step 2: Plan the concept

Follow the brief exactly wherever it is specific — a scenario, a shot list, a named place, a mood.
The rest is yours to decide.

**1. Decide who is in it, and where.**

- A brief that names them settles it. Where it doesn't, pick whoever the video is most believable
  coming from, and put them where it would actually happen.
- Anything that shows up in more than one clip is decided here too — a product, a prop, an animal.
  Say what it is and what it looks like.
- Where nobody is on camera, skip this.

**2. Split the length into clips.**

- `list_video_models` gives the model's shortest and longest clip.
- Make each clip as long as the model allows. Put whatever is left over in the last one. If that
  leftover is shorter than the model's minimum, make the last clip the minimum and let the video run
  a little long.

**3. Give each clip its share of the story.**

- One clip is one storyboard. What happens in it is settled here; how it divides into panels is
  worked out when the sheet is built.
- A **primary action** is one continuous motion at one object, and each one needs two to four
  seconds. The clip's length is therefore how many it can carry — write its share of the story to
  that number.
- Nothing finer than a whole hand movement, and no state change shown on screen: where the thing has
  to be open, worn or empty, the clip arrives with it already that way.
- State only moves forward. Opened, worn or emptied, it stays that way — nothing later in the video
  closes it, takes it off, or puts it back.

**4. Spread one story across the clips.**

- Clip 1 covers the opening of the story. Clip 2 picks up where clip 1 ended. And so on.
- Each clip covers only its own stretch — never the whole story again.
- Each clip opens on whatever state the one before it ended in.
- Hold the same story arc, colours, lighting and setting across the whole video.

**5. Write it down.** Every step after this reads it instead of deciding again:

- who is in it and where, and anything else that shows up in more than one clip
- how many clips, and how many seconds each
- what happens in each clip
- where anyone speaks: one line per clip on what is said, and the most words that clip can carry.
  Two words a second is the target and three is the ceiling, so a 15-second clip runs about 30 to 40 words.

### Step 3: Write the script

Skip this when nobody speaks.

Otherwise trigger the `writing-video-scripts` skill workflow with the concept from Step 2: the clip
durations, what happens in each clip, and the word budget.

### Step 4: Show the concept and wait

Nothing has been generated yet, and everything after this step costs money. Get the concept approved first.

Show, written out, in one brief, to the point message:

- **The person, if anyone is on camera, who shows up in more than 1 clip** — their age, how they look, what they're wearing, where they are, etc. 
- **Anything else that shows up in more than one clip** — a product, a prop, an animal, etc. Say what it
  is and what it looks like.
- **What happens in each clip** — the setting, what happens, where the subject is. Keep this brief and focus on the high level concept rather than stating all small technical details. 
- **What's said in each clip** — the script from Step 3, word for word. Leave this out if nobody
  speaks.

Then ask whether it's right, and say they can change any of it — the person, the setting, what
happens in a clip, a line. **Expect edits.** Rewrite what they change, show it again, and repeat until they approve.

Wait for an answer. Don't cast, don't generate a still, don't build a sheet, don't generate a clip.

If the user has said they don't want to be asked, say in one line what you're going with and carry
on.

### Step 5: Cast anyone or anything that recurs

**Each thing that shows up in more than one clip gets its own image, made once, reused everywhere.**
Clips are generated separately, so writing *"the same woman"* or *"that sneaker again"* in a later
clip returns a different-looking woman or sneaker. Make one image per subject — the person, the
product, the prop — and pass every image a clip needs into that clip as references, describing each
in the same words each time.

Skip this if nobody is on camera, if a person appears in only one clip, or if the user supplied a
photo of them.

Otherwise trigger the `generating-ai-actors` skill workflow with the person from the approved concept
— the same age, clothes and setting, not a new invention — and the look the video is going for.

**Anything else in more than one clip works the same way** — a product, a prop, an animal. One clean
image of it on a plain white background, made once with a single `image_generate` call.

Skip if the user already supplied a photo of it. **If it's a real product and no photo was supplied,
ask for one instead of inventing it** — an invented product held consistently across every clip is
worse than stopping to ask.

### Step 6: Build the storyboards

Trigger the `generating-storyboards` skill workflow with: one sheet per clip, what happens in that
clip and how many seconds it runs, which sheet this is and how many there are, the images from Step 5
as references, and its script segment if there is one. How the clip divides into panels is worked out
there, not here. The sheet's own shape is not yours to set — it is always `16:9` with
vertical panels, whatever ratio the video is delivered in.

### Step 7: Write the prompts

Trigger the `writing-video-prompts` skill workflow with: one prompt per clip, the chosen model, that
clip's duration from the concept and the panels of its sheet, its script segment if there is one, and
the media that go with it — the sheet from Step 6, the images from Step 5, and any video or audio
track the user supplied.

It returns the prompts as text, and the order it labelled the media in. Nothing is generated there.

### Step 8: Generate

Call `video_generate` with a `requests` list, one object per clip, all in the same call so they render
at once.

- Per object: the `prompt` from Step 7; the media it labelled, passed as `reference_images`,
  `reference_videos` and `reference_audios` **in the order Step 7 labelled them**; `duration`,
  `resolution`, `aspect_ratio` and `generate_audio`. Omit `model` to use the default; set it only if
  one was chosen.
- Every clip uses the same aspect ratio and resolution.
- A clip can come back as `{status: "pending", …}` — a job handle, not a failure. Pass that exact
  handle to `job_status`, and again if it is still pending. **Never re-run a pending clip**; that
  starts a second billed job.

### Step 9: Stitch and return

Wait until every clip has finished, collecting any `pending` ones with `job_status` first. Then pass
them in order to `video_stitch`, which joins them with a hard cut between each and keeps each clip's
audio. Don't join them by hand.

A single clip needs no stitching. Return the finished video's URL and local file path, and
the individual clips if the user asks for them.

## Edge cases

**Never regenerate a clip without the user asking for it.** Every re-run is billed again. Hand back
what came out, say what looks wrong, and wait — including in the cases below.

- **A sheet comes back wrong** — remake it, then remake every sheet after it. Each sheet is built
  from the one before, so they all copy the mistake. Sheets are cheap; a clip made from a wrong sheet
  is not.
- **One clip in the batch fails while the others succeed** — send a new call with only that request.
  Re-running the whole list bills every clip again.
- **A clip doesn't match its sheet** — hand it over and say what looks off. Whether it's close enough
  is the user's call. Don't re-run it unless they ask.
- **The user changes something after approving the concept** — redo from the earliest step the change
  touches. A different setting means new sheets and new clips; a different line means only the script
  and that clip's prompt.
- **`video_stitch` isn't available** — return the clips in order and say they aren't joined.
