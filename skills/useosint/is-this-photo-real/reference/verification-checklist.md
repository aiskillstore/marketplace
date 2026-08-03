# Verification checklist, ordered by cost

Ordered cheapest-first, where cost means your time plus the risk of misreading the
result. Work down it and stop when the question is answered — which, for most cases, is
in tier 1 or 2. Record every step including the ones that found nothing; a documented
null is evidence, an undocumented one is nothing.

Tier 5 is the tier people start with. That is the whole problem.

## Tier 0 — Before you touch anything (minutes)

- [ ] Write down the **exact claim** being tested: who, what, where, when. Verification
      without a stated claim has no stopping condition.
- [ ] Write down what you would expect to see **if the claim were true**. Check for those
      things specifically later.
- [ ] Obtain the best available copy. Original file over platform rendition, platform
      rendition over screenshot. For platform video use `yt-dlp` rather than a screen
      recording.
- [ ] Hash it. `sha256sum` the file, record the hash, and work only on copies.
- [ ] Record the **processing history you know**: where you got it, whether it was
      re-encoded, whether it is a crop or screenshot. This determines which tiers below
      are valid at all.

## Tier 1 — Provenance (minutes, highest yield)

- [ ] Reverse image search: full frame across at least three engines. For video, extract
      keyframes and search several.
- [ ] Crop the distinctive elements and re-search each. Mirror and re-search.
- [ ] Sort for the **oldest** copy where the engine allows.
- [ ] Open every match page. Harvest: caption, date, photographer credit, agency, named
      people, image filename.
- [ ] Corroborate the earliest page's date against an independent archive capture.
- [ ] Search the caption text and any distinctive on-image text as a string, in the
      original language.

**Stop here if:** you found the same media published earlier with a different,
better-sourced caption. That is a confirmed recontextualisation and no further analysis
is needed to report it.

## Tier 2 — Metadata and internal consistency (tens of minutes)

- [ ] Full metadata dump: `exiftool -G1 -a -u -g1`.
- [ ] Extract and compare the embedded thumbnail and preview against the main image —
      aspect ratio and content.
- [ ] Check the three timestamps against each other, and against UTC GPS time if present.
- [ ] Check the software/editing chain and XMP media-management history.
- [ ] Check whether MakerNotes exist and are consistent with the claimed device.
- [ ] Check for C2PA Content Credentials. Absence is uninformative; a valid manifest is
      strong.
- [ ] For video: `ffprobe -show_format -show_streams` and MediaInfo. Is this an original
      capture or a platform re-encode? **Record the answer — it governs tiers 4 and 5.**
- [ ] Internal consistency sweep: signage language and script, licence plates, currency,
      uniforms and insignia, vehicle models, road markings, season, weather, clothing.
      Does everything agree with the claimed place and date?

**Stop here if:** an internal detail contradicts the claim outright — wrong script,
wrong driving side, wrong season. One hard contradiction disproves a claim; you do not
need to prove what the media actually is.

## Tier 3 — Geolocation and chronolocation (hours)

- [ ] Run the clue inventory and ranking from `geolocate-from-pixels`.
- [ ] Establish country from tier-one and tier-two indicators.
- [ ] Narrow to a site and confirm against satellite and street-level imagery, on at
      least three independent non-transient features.
- [ ] Check imagery capture dates before rejecting any candidate.
- [ ] Shadow azimuth and elevation, solved against a sun-position calculator for the
      confirmed location.
- [ ] Break the two-date ambiguity with foliage, snow, crops or a dated object in frame.
- [ ] Corroborate against a weather archive for the nearest station; note the station and
      its distance.

**Stop here if:** the location or date is established and contradicts or confirms the
claim. Most cases end here with a defensible answer.

## Tier 4 — Physical and geometric consistency (hours, high defensibility)

Valid on any copy, including re-encodes. This is the best value in the whole checklist
after tier 1.

- [ ] Shadow convergence construction on three or more objects on one ground plane. Do
      the lines meet at a single point?
- [ ] Shadow direction and penumbra hardness consistent across the scene?
- [ ] Specular highlights in eyes, glass and metal consistent with one light arrangement?
- [ ] Reflections in mirrors, windows and water geometrically correct and correctly
      reversed?
- [ ] Vanishing points consistent; horizon line consistent; eye level consistent for
      people on one ground plane?
- [ ] Scale of each person and object plausible for their distance?
- [ ] Optical signature consistent across the frame: depth of field, chromatic
      aberration at edges, vignetting, noise floor varying with brightness?
- [ ] Edges around any suspected inserted element: warping, halos, a mismatched blur
      radius, a cut that follows an object's outline too precisely?
- [ ] For AI suspicion: the durable structural tells — background object coherence,
      small and peripheral text, contact and occlusion, absent camera physics.

Correct for lens distortion before drawing lines, or use objects near the frame centre.

## Tier 5 — Signal-level forensics (hours, easily misread)

**Precondition:** you established in tier 2 that you hold a first-generation or
near-first-generation file. If the file is a platform re-encode or a screenshot, most of
this tier is invalid and the honest report says so rather than reporting a
meaningless result.

- [ ] Clone/copy-move detection. Expect false positives on brickwork, foliage, crowds and
      fabric; look for a duplicated region that is *semantically* implausible, not merely
      repeated texture.
- [ ] Noise residual analysis. Is there a region whose noise character differs from its
      surroundings?
- [ ] JPEG quantisation-table comparison. Do the tables match a camera or an editor?
- [ ] Double-compression analysis. Does *part* of the image show a different compression
      history from the rest? Whole-image double compression is normal and uninteresting.
- [ ] Colour-filter-array / demosaicing consistency, if the file is genuinely
      first-generation.
- [ ] ELA, last and least. Read the parent skill's section on it first. Treat any result
      as a pointer to inspect a region manually, never as a finding.
- [ ] AI detectors, plural, understood as a weak signal. Record the scores and the fact
      that you did not rely on them.

## Tier 6 — Out of reach without special access

Know these exist so you can say what you could not do, rather than implying it was done.

- [ ] PRNU sensor-noise matching to a specific camera body — requires the physical device
      or a corpus of its images.
- [ ] Electric-network-frequency matching of a recording's mains hum against grid records
      — requires reference recordings that are not publicly available for most grids.
- [ ] Platform-side upload records, server logs and original un-stripped uploads —
      requires legal process.
- [ ] Interviewing the photographer or uploader. Often the fastest route of all, and
      routinely forgotten in favour of pixel analysis.

## Video additions, inserted at the matching tier

| Tier | Check |
|---|---|
| 1 | Extract keyframes and scene-change frames; reverse search several, not one. |
| 2 | Container and encoder inspection; frame-type listing; duplicated-frame detection; rotation matrix. |
| 2 | Audio: spectrogram for splices, room-tone changes, band-limiting discontinuities, noise-floor jumps at cuts. |
| 3 | Sun position across the clip — shadows should rotate in the correct direction for the hemisphere and at the correct rate. |
| 4 | Face-boundary behaviour frame by frame: hairline and jaw flicker, lighting not tracking head motion, teeth and tongue during speech, behaviour on profile turns and hand occlusion. |
| 4 | Temporal coherence of background objects and of any on-screen text. |
| 5 | Compression-generation assessment; per-frame ELA is even less reliable than single-image ELA. |

## Output template

Write these five things. If you cannot fill one in, say so explicitly.

1. **The claim tested**, stated as who/what/where/when.
2. **The file examined**: source, hash, and processing history — original, re-encode, or
   screenshot.
3. **Findings, graded individually**: origin, caption accuracy, location, date,
   manipulation, synthesis. Each with the evidence it rests on.
4. **Tests run that found nothing**, and tests that were **invalid** on this copy and why.
5. **Assumptions and open questions** — what would change the conclusion, and what you
   would need to close it.

Then hand it to `write-the-intel-brief`.
