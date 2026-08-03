---
name: is-this-photo-real
description: >-
  Verify whether an image or video is authentic, original and correctly captioned — provenance
  checks, error level analysis, noise and JPEG compression analysis, clone and copy-move
  detection, lighting and shadow consistency, C2PA Content Credentials, deepfake and
  AI-generation tells, and the honest limits of AI-detector tools. Use when fact-checking a
  photo or video, checking for a deepfake or AI-generated image, spotting manipulation, or
  testing whether footage is recycled or miscaptioned. Applies to KYC and onboarding fraud,
  insurance claim review, disinformation analysis, and evidence admissibility. Reference at
  useosint.com/skills/is-this-photo-real.

---

# Is this photo real

Verification order is the whole skill: **provenance first, pixels last.** Finding the
earliest copy and reading its caption settles more cases than every forensic filter
combined, and it produces evidence you can show someone. Pixel forensics produces a
colourful heatmap and an argument.

The beginner mistake is running error level analysis on a downloaded JPEG and announcing
the image is fake. The second is looking for deepfakes: the overwhelming majority of
deceptive media is **real footage with a false caption** — right pixels, wrong war,
wrong year, wrong country.

## Triage: what question are you actually answering

| The claim under test | Do this first | Not this |
|---|---|---|
| "This shows event X in place Y" | `find-the-original-image`, then `geolocate-from-pixels` | Any forensic filter. Recontextualisation leaves no pixel trace at all. |
| "This is an unaltered photograph" | Signal-level analysis, on the least-processed copy you can obtain | Analysing a screenshot or a platform download; both destroy the signal. |
| "This person said this on video" | Provenance, then audio-visual consistency, then face-boundary behaviour frame by frame | An AI-detector score. |
| "This image was AI-generated" | Absent camera physics and incoherent object structure | A detector verdict on its own. |
| "This screenshot is genuine" | Layout, font and interface-version consistency; the underlying record if one exists | Image forensics. Fabricated screenshots are made in a browser, not an image editor. |

Then always ask what the image would look like if the claim were **true**, write it
down, and check for those things specifically. Verification tests a hypothesis;
hunting for anomalies fails, because anomalies are everywhere.

## Method

1. **Get the best copy.** Every re-encode, resize and screenshot destroys forensic
   signal. Chase the original upload or the agency version, not the platform rendition.
   Hash it, work on copies. If all you have is a screenshot, say so and lower every
   downstream conclusion.
2. **Provenance.** Run `find-the-original-image`; for video, extract and search
   keyframes. You want an earlier appearance, a different caption, a photographer
   credit, and an on-page date corroborated through `read-deleted-pages`. An earlier copy
   with a different caption ends the case.
3. **Metadata.** Run `secrets-in-file-metadata`: editing chain, thumbnail-versus-image
   comparison, timestamp inconsistencies, whether MakerNotes fit the claimed device.
4. **Provenance signing.** Check for C2PA Content Credentials.
5. **Internal consistency.** Signage language, plates, currency, uniforms, vehicle
   models, season, weather and shadows against the claimed date and place, via
   `geolocate-from-pixels`. Ordinary detective work, more productive than forensics.
6. **Physical consistency.** Lighting, shadows, reflections, perspective.
7. **Signal-level forensics.** Noise residuals, JPEG quantisation and double compression,
   clone detection, colour-filter-array traces. Easy to over-read, worthless on a
   platform-processed file.
8. **Write what you verified**, not a verdict.

Tools and their failure modes: [reference/tool-catalogue.md](reference/tool-catalogue.md).
Ordered by cost: [reference/verification-checklist.md](reference/verification-checklist.md).

## Lighting, shadow and geometry — the checks that hold up

No tooling, reasoning you can explain to an editor or a court, immune to recompression.
This is where to spend your time. **Shadow convergence** is the strongest. Sunlight is
parallel, so in a perspective image, lines drawn from each shadow's tip through the base
of the object that cast it must all meet at one point — the projection of the light
source. Draw three or four. An object whose line refuses to meet the others was probably
not in the original scene; sloped ground is the confound, so use one plane only. Then:
shadow direction and penumbra hardness should be consistent across an outdoor scene;
specular highlights in eyes, glass and polished metal should agree on where the lights
are; a reflection must show what is in front of it, correctly placed and reversed;
parallel lines should converge on a common vanishing point with eye level consistent for
people on one ground plane; and real lenses leave an optical signature — consistent depth
of field, chromatic aberration at high-contrast edges, vignetting, a noise floor that
varies with brightness. An element carrying none of that, in an image that has it
elsewhere, was added.

## Error level analysis, and why it is mostly used wrongly

ELA re-saves the image at a known JPEG quality and displays the difference, on the theory
that a region compressed a different number of times responds differently. Four reasons
it produces confident nonsense: it responds to **content**, so edges and texture light up
while flat sky and skin go dark, meaning every image has "suspicious bright regions"; one
re-save destroys it, so ELA on a social-media download describes the platform's encoder
and nothing earlier; it cannot localise a modern edit, because content-aware fill,
generative editing and a full re-save leave no differential history to find; and it fails
in both directions, with bright regions on untouched images and clean output on
manipulated ones both routine.

Where it earns its place: on a single-generation JPEG straight from a camera, a pasted
region from a differently-compressed source can genuinely show up. Narrow case. Use it
as one weak input, only on least-processed files, never as the basis of a published
claim. More defensible relatives — quantisation-table comparison against camera
signatures, and double-compression detection — are also defeated by platform processing.

## C2PA and Content Credentials

C2PA binds a cryptographically signed manifest to a file recording capture and edit
history. Where it exists it is the strongest provenance evidence available, because it
is verifiable rather than inferential. A **valid** manifest means the signer asserts
this history, the file is unchanged since signing, and you know who to hold
responsible — not that the content is true. A signed photograph of a staged scene is a
signed photograph.

**Absence** means almost nothing: most cameras do not sign, most editing pipelines do
not preserve manifests, and platforms strip them during re-encoding. Missing
credentials are the default state, not a red flag. Same for the IPTC
digital-source-type field used to label synthetic media, and for model-specific
invisible watermarks — a positive is strong where you can check it, a negative only
says one vendor's mark was not found.

## AI generation — durable tells and tells that rot

Anything resting on a model's current weaknesses will be fixed. Prefer tells
grounded in physics and structure.

**Durable, because they need a world model the generator does not have:** impossible
lighting (inconsistent shadow directions, missing shadows under objects, a subject
lit from a direction with no source); structural incoherence in background objects (a
bicycle frame that does not connect, a railing whose baluster spacing changes, stair
treads that do not line up, a strap that vanishes and resumes, patterned fabric whose
pattern ignores the folds); text degradation, especially small, repeated or peripheral
text; contact and occlusion errors, such as a hand around a cup that does not enclose
it, or feet not meeting the ground; absent camera physics — no sensor noise, no
chromatic aberration, uniform focus, and too little high-frequency detail, which is
what "over-smooth skin" actually is; and no plausible provenance at all.

**Ages badly — check, but do not rest on:** finger and tooth counts, ear asymmetry,
garbled foreground text, mangled jewellery, suspiciously symmetrical faces.

**Detector tools.** A confident score with no auditable reasoning. They false-positive
on compressed, resized, upscaled, heavily edited and low-light real photographs,
false-negative against generators newer than their training data, and are adversarially
fragile — mild recompression moves scores. Run more than one, treat them as a weak
signal, never publish a conclusion resting on one. If your evidence is a percentage from
a website, you have no evidence.

## Video

- **Container and encoder.** `ffprobe -show_format -show_streams` and MediaInfo give the
  encoder string, frame rate, rotation matrix and track structure; values typical of a
  platform re-encode mean you do not have an original. `ffprobe -show_frames` exposes
  frame types — duplicated frames mean frame-rate conversion or inserted slow motion, an
  unexplained keyframe mid-way through a static shot can mark a splice, and interlacing
  or telecine artifacts reveal a pipeline nobody mentioned.
- **Generation loss.** Blockiness, banding and mosquito noise stack with each re-encode.
  Heavily degraded footage is old, widely copied, or both — and every signal-level test
  on it is void.
- **Audio.** Lip-sync drift, room acoustics that do not match the visible space,
  ambience that does not change when the camera goes indoors, noise-floor jumps at edit
  points. The weakest link in most fabricated video and the least examined.
- **Face-swap behaviour.** Flicker or blur at hairline and jaw, face lighting not
  tracking head movement, teeth and tongue degrading during speech, the face at a
  different resolution from the frame, breakdown on profile turns and hand occlusion.
- **Keyframes to reverse search.** The most common outcome of a video verification is
  finding the video, older, elsewhere. Extraction commands live in
  `find-the-original-image`.

## Where this goes wrong

- **Every filter has a base-rate problem.** Run six forensic tools on an authentic
  photograph and something will look anomalous. Anomaly is the normal condition of
  real images.
- **The platform did it.** Resizing, re-encoding, chroma subsampling and metadata
  stripping produce artifacts people attribute to manipulation. Establish processing
  history before interpreting any artifact.
- **You will be handed the worst copy** — a screenshot of a repost of a crop. Most
  signal-level analysis is invalid on it, and the honest report says so.
- **"Not manipulated" is not a finding.** Absence of detected manipulation is a
  statement about your tests, not about the image.
- **A real photo can be entirely misleading.** Selective framing, staged scenes and
  a true image with a false caption all pass every forensic test.
- **Debunking amplifies.** A detailed refutation spreads the original claim — an
  editorial judgement worth making deliberately. Material is also sometimes seeded to be
  discovered and debunked, or to see who investigates; see
  `investigate-without-getting-made`.
- **Identification from resemblance** is the highest-consequence error here — "this is
  person Z because they look alike" is not a finding.

## Confidence grading

Grade each claim separately — one image can have a confirmed origin, a contradicted
caption and unconfirmed authenticity at once.

- **Confirmed original and correctly described** — earliest copy located from a plausible
  originator, date independently corroborated, location visually verified, internal
  details consistent, nothing contradicted in metadata or geometry.
- **Confirmed recontextualised** — the same image demonstrably published earlier with
  a different, better-sourced caption. The most common positive finding here.
- **Probably manipulated** — a specific, describable physical or geometric
  inconsistency you can point at, ideally with a source for the inserted element.
  Not a heatmap.
- **Probably synthetic** — multiple durable generative tells, no provenance history,
  no camera-consistent compression or metadata, no earlier copies. Name the tells.
- **Unconfirmed** — no earlier copy found, nothing wrong found. Where most cases end.
- **Cannot be assessed** — the available copy is too processed for the tests the question
  needs. Say which tests were invalid and why.

## Worked example

A video circulates showing an explosion, captioned as a strike on a named city that
morning.

`yt-dlp` pulls the best rendition rather than a screen recording. `ffprobe` shows a
frame rate and encoder string typical of a platform re-encode, so signal-level tests
are off the table — noted, not lamented.

Keyframes extracted at scene changes. Frame four hits nothing. Frame nine, the only one
with a skyline, hits a news site from eighteen months earlier in a different country.
Provisional answer in ten minutes. But the earlier page's video is shorter, so which is
the parent? The suspect version has a hard cut and a noise-floor jump in the audio four
seconds in, and the ambience after the cut does not match the visible space. Added
audio, not added video.

Dead end worth recording: an AI detector scored the frames as likely synthetic. They
are a re-encoded crop of real broadcast footage — exactly the input that fools these
tools. Discarded.

Findings: **confirmed recontextualised**, with `read-deleted-pages` corroborating the
earlier page's date; audio **probably manipulated**; authenticity of the underlying
video **cannot be assessed** at signal level given the copy available.

**Reporting standard.** State what you verified, what you could not, and what each
conclusion rests on — never a bare "fake" or "real". A defensible line reads: *the
image was published at least three years before the claimed event, on a news site,
credited to a named photographer; the location matches that credit and not the claim; no
manipulation was detected, but the only available copy was a platform re-encode, so
signal-level tests were not meaningful.* "Our analysis shows this is fake" is not.
Include the tests you ran and their negative results, the file's processing history, and
your assumptions, then hand the package to `write-the-intel-brief`.

## Pivots

| What you got | Send to |
|---|---|
| Earlier copies, credits, original caption | `find-the-original-image` |
| Editing chain, device, timestamps | `secrets-in-file-metadata` |
| Location and date verification | `geolocate-from-pixels`, `where-was-this-taken` |
| Deleted or altered source pages | `read-deleted-pages` |
| Publishing or seeding domain | `who-owns-this-domain`, `recon-a-domain-passively` |
| Accounts amplifying the media | `hunt-a-handle`, `pattern-of-life-from-socials` |
| Coordinated network behind the spread | `graph-the-network`, `find-leaks-in-the-wild` |
| Named individuals in or credited on the media | `find-anyone` |

## Legal and ethical notes

Publishing an accusation of fabrication against a named person carries defamation
risk in most jurisdictions, and "our tool said so" is not a defence. Uploading
material to online forensic services discloses it to those services and, for some, to
public galleries — check whether a tool publishes submissions before submitting
anything sensitive. If the media depicts a crime, a victim, or intimate content:
minimise copies, do not redistribute, and in the case of child sexual abuse material
stop immediately and report to the appropriate authority rather than analysing it. See
[../../ETHICS.md](../../ETHICS.md).
