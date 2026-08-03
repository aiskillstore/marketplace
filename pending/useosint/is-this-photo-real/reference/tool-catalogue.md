# Verification tool catalogue

Each entry: what it does, what it is actually good for, and how it fails. Read the
failure mode before you read the capability. Most bad verification comes from using
a good tool on the wrong input.

Before anything: check whether a tool **publishes** your submission. Some forensic
services maintain public galleries of uploads. For anything sensitive, prefer local
tools.

## Provenance and search

### Reverse image engines

See `find-the-original-image` for the engine-by-engine treatment. In verification
terms they are the highest-value tools in this list and belong first in every
workflow.

**Failure mode:** absence of results is uninformative, and visual-similarity results
masquerade as matches.

### Web archives

Archived captures date a page independently of what the page claims about itself. See
`read-deleted-pages`.

**Failure mode:** no capture means no evidence either way; robots-directive
retroactivity and takedowns can remove captures that existed.

### InVID/WeVerify verification plugin

Browser extension aimed at exactly this workflow: keyframe extraction from video URLs,
one-click reverse search across engines, metadata reading, a magnifier, and a set of
forensic filters. The single biggest time-saver for video verification.

**Failure mode:** the forensic filters it bundles carry all the interpretive hazards
of the standalone tools, presented in a UI that makes them look authoritative.
Keyframe extraction depends on the platform still serving the video.

### yt-dlp

Downloads the best available rendition of a platform video plus a sidecar JSON with
upload time, uploader and description. Always prefer this to a screen recording.

**Failure mode:** the platform's rendition is already a re-encode; you are getting the
best available copy, not an original.

## Metadata

### exiftool

See `secrets-in-file-metadata`. In verification, its jobs are: reveal the editing
chain, extract the embedded thumbnail for comparison against the main image, expose
timestamp inconsistencies, and show whether MakerNotes are consistent with the claimed
device.

**Failure mode:** every value is a writable claim. Absence proves nothing.

### ffprobe and MediaInfo

Container and stream inspection for video: encoder strings, frame rate, rotation
matrices, per-track metadata, frame types and timestamps.

```bash
ffprobe -v error -show_format -show_streams video.mp4
ffprobe -v error -select_streams v -show_frames -show_entries frame=pict_type,pkt_pts_time video.mp4
mediainfo video.mp4
```

Good for: determining whether you have an original capture or a platform re-encode,
which decides whether any signal-level test is worth running. Detecting duplicated
frames, unexpected keyframes and telecine.

**Failure mode:** encoder strings can be edited, and remuxing changes container
metadata without touching the video. A "clean" encoder string is weak evidence.

### C2PA / Content Credentials verification

Where a manifest exists, verification is cryptographic rather than interpretive: it
tells you the file is unchanged since signing and who signed it. Public verification
pages exist for inspecting a file's credentials.

**Failure mode:** absence is the default state and means almost nothing. A valid
manifest attests to the chain, not to the truth of the depicted scene. A manifest can
also be valid and *incomplete* — signed after an unrecorded edit.

## Signal-level image forensics

### FotoForensics

Hosted suite built around ELA, plus JPEG quality estimation, last-save quality,
metadata, embedded thumbnail extraction, and hidden-pixel and string checks. The
non-ELA parts are the useful parts.

**Failure mode:** ELA is the headline feature and the most misread analysis in the
field — see the parent skill. The service also retains and may display submissions;
do not upload sensitive material.

### Forensically (browser-based)

Free in-browser toolkit: clone detection, ELA, noise analysis, level sweep, luminance
gradient, principal-component analysis, a strong magnifier, metadata and string
extraction. Runs locally in the page, which makes it the better choice for sensitive
files.

Good for: **clone detection** on suspected copy-move edits, **noise analysis** to spot
a region with a different noise character, and the **magnifier** for careful manual
inspection, which is underrated.

**Failure mode:** clone detection flags legitimately repeated texture — brickwork,
foliage, crowds, fabric — constantly. Noise analysis is destroyed by re-compression
and by aggressive in-camera noise reduction. Level sweep and luminance gradient are
visualisation aids, not detectors, and will show "structure" in any image.

### JPEG quantisation-table analysis

A JPEG's quantisation tables reflect the encoder that wrote it. Camera manufacturers
use characteristic tables; editors and libraries use different ones. Tools that read
tables and compare them against signature databases can tell you whether a file
plausibly came straight from a camera.

Good for: testing "this is the original camera file" claims. A file whose tables match
a common editor's while being presented as camera-original is a real contradiction.

**Failure mode:** any platform upload re-encodes and overwrites the tables, so this
only works on files you believe are first-generation. Signature databases are
incomplete, so an unmatched table is not evidence of anything.

### Double-compression detection

Looks for the periodic artifacts left in DCT coefficient distributions when an image
is compressed, edited and compressed again.

**Failure mode:** most images on the internet have been compressed many times
legitimately. Detecting double compression tells you the file was re-saved, which is
almost always true and almost never interesting on its own. It becomes meaningful only
when *part* of the image shows a different compression history from the rest.

### Colour-filter-array and demosaicing analysis

A digital sensor captures one colour per photosite and interpolates the rest, leaving a
periodic pattern. Regions that have been synthesised, heavily resampled or pasted from
another source disturb it.

Good for: distinguishing camera-originated pixels from generated or resampled ones on
a first-generation file.

**Failure mode:** any resize, re-encode or platform processing destroys the pattern.
Effectively unusable on anything downloaded from a social platform.

### PRNU sensor-noise matching

Every sensor has a fixed pattern of pixel-response non-uniformity, which acts as a
sensor fingerprint and can tie an image to a specific camera.

**Failure mode:** requires a set of reference images from the **physical camera**, so
it is a tool for cases where you have or can obtain the device — law enforcement and
formal forensic engagements. Not an open-source-investigation technique. Also defeated
by strong compression and by cropping.

### Amped Authenticate and comparable commercial suites

Commercial forensic platforms bundling the above with case management, reporting and
validated methodology. The reason they exist is court admissibility and defensible
process, not better algorithms.

**Failure mode:** cost and licensing; and the underlying methods have the same limits
as the free implementations. A commercial tool's confident output on a
platform-processed file is just as wrong, and harder to argue with.

## AI-generation detection

### Automated detectors

Classifier services returning a probability that an image or video is synthetic.

Good for: a weak additional signal, and for triaging large volumes when you accept the
error rate.

**Failure mode:** the important entry in this file. They produce **false positives on
real images** that have been compressed, resized, upscaled, denoised, heavily edited,
or shot in low light — the exact condition of most images you will receive. They
produce **false negatives** against generators newer than their training data. They
give no auditable reasoning, so you cannot inspect why. They are adversarially fragile:
a mild recompression can flip a score. Never publish a conclusion resting on a detector
output, and be sceptical when one confirms what you already suspected.

### Invisible watermark detection

Some generators embed a watermark detectable with the vendor's own tooling.

**Failure mode:** only covers that vendor's models, only where the tooling is available
to you, and can be degraded by editing and re-encoding. A positive is strong; a
negative says nothing.

### Manual structural inspection

Your own eyes at high magnification, looking for the durable tells in the parent skill.

Good for: everything. This is the most reliable AI detection available and the least
automatable.

**Failure mode:** you get better at it and generators get better faster; and it is
subject to your own bias about what "looks AI".

## Geometry and reconstruction

### Shadow and vanishing-point construction

Draw lines. Any image editor with a line tool, or a printout and a ruler.

Good for: the most defensible manipulation finding available, because the reasoning is
visible and checkable by anyone.

**Failure mode:** requires level ground and vertical objects, both of which you must
verify rather than assume. Wide-angle lens distortion bends lines that should be
straight — correct for it or choose objects near the frame centre.

### Sun-position calculators

SunCalc and the NOAA Solar Calculator compute solar azimuth and elevation for a given
place and time. Used in reverse, they test whether the shadows in an image are
consistent with the claimed date, time and place.

**Failure mode:** you need the location first, and shadow measurement error propagates
badly. See the chronolocation reference in `geolocate-from-pixels`.

### Mapping and street-level imagery

See `geolocate-from-pixels`. In verification these settle the "where" half of most
claims, and settling the "where" usually settles the claim.

**Failure mode:** imagery is dated, so differences between image and reference may be
time, not deception.

## Video-specific

### FFmpeg for frame extraction and comparison

Keyframe and scene-change extraction for reverse search; exact-timestamp frame pulls
for close inspection; side-by-side comparison of two versions of the same footage.
Commands are in the preprocessing reference of `find-the-original-image`.

**Failure mode:** none in the tool; the hazard is treating an extracted frame as
first-generation evidence when the video itself is a re-encode.

### Audio inspection

A spectrogram view in any audio editor reveals splices as discontinuities in the noise
floor, abrupt band-limiting, and mismatched room tone between segments.

Good for: catching added or substituted audio, which is common and rarely checked.

**Failure mode:** platform audio re-encoding introduces band-limiting of its own, so
compare only within one file rather than against an expectation of what "unprocessed"
looks like.
