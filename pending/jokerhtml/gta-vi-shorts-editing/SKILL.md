---
name: gta-vi-shorts-editing
description: >-
  Build English GTA 6 (GTA VI) news Shorts (30-59s) the Joker Gaming way with this Claude Code skill: ChatGPT scripts from a fact ledger, Kokoro voiceover, exact word-timed subtitles, official stills and trailer motion, designed fact cards, loudness and colour gates, and an independent red-team gate before upload. Use when planning, scripting, editing, checking, or uploading a GTA 6 Short.
license: MIT
metadata:
  version: 1.0.0
  date: 2026-11-15
  author: Muhammad Saad Ranjha / Joker Gaming
---

# GTA VI Shorts Editing

## What this skill is

This skill is the working method behind the Joker Gaming GTA VI news Shorts: short, premium, zero-fake English Shorts built from official Rockstar material only. It covers the full path from topic research to a scheduled upload: fact ledger, ChatGPT script and SEO, voiceover, subtitles, stills and motion, cards, mix, render, grade, loudness, builder QC, red-team gate, and scheduling.

Who it is for: an editor or agent making GTA VI news Shorts who wants a repeatable, checkable method instead of guessing. It assumes you have ffmpeg, Python, Node with Remotion, Kokoro TTS, and faster-whisper available (see Tools). It does not contain any Rockstar footage, logo files, trailer files, or music. You supply your own official source material.

## Proof

Three Shorts were built with this method on November 15, 2026, on the Joker Gaming channel, and all three were scheduled the same day.

View counts below were read from the public YouTube pages on 15 November 2026 (evening PKT). They rise as videos gain views; re-check the live pages for current numbers. No earnings are claimed anywhere in this skill.

### Trending Shorts on the channel

| Short | Published | Views (15 Nov 2026) | Likes |
|---|---|---|---|
| SPOTTED: Jason's GTA 6 Launch Trailer Shirt Names a Base From the 1997 Game - https://youtube.com/shorts/8uBbUEWNCag | 10 Nov 2026 | 1,140 | 7 |
| NEW: How Big Is GTA VI's Map? Rockstar Already Answered It - https://youtube.com/shorts/C4Sr6Emcxiw | 10 Nov 2026 | 1,028 | 9 |
| NEW: GTA VI's Weapon Wheel Is Back — But You Can't Carry Everything - https://youtube.com/shorts/DP4sJFn5ql4 | 10 Nov 2026 | 1,010 | 8 |
| PlayStation AND Xbox Agree: GTA 6 Broke Both Records - https://youtube.com/shorts/aoM0939hZ7s | 12 Nov 2026 | 874 | 5 |
| Your 13-Year-Old Xbox Plays GTA VI on Launch Day - https://youtube.com/shorts/_RcbKgTRgTA | 12 Nov 2026 | 804 | 12 |

Across the 37 most recent Shorts on @jokergaminglive, total public views were 10,013 on the same check. Subscriber count (~8,165) is owner-supplied and was not verified from the platform for this skill. Watch hours are not public on YouTube; they come from YouTube Studio only, so no watch-hours figure is claimed here.

| Video | Slot (PKT, Nov 15) | Duration | Red-team verdict |
|---|---|---|---|
| GTA VI Built a Whole Cartoon Inside the Game - https://youtube.com/shorts/OC5KczRGYSQ | 17:00 | 40.00s | 96/100 + 60/60 PASS, 0 criticals |
| New Zealand Plays GTA VI First. Here's Your Unlock Time - https://youtube.com/shorts/aF6RgIg_mHI | 19:00 | 45.9s | 90/100 + 53/60 PRE-FIX verdict, a FAIL (MAJOR-1 colour). Shipped file is the MAJOR-fixed file, technically re-verified, expected approx 94/100, not a measured re-score |
| Burger Shot Is Real Now. You Can Eat It in Florida - https://youtube.com/shorts/74I0MXC-aIQ | 21:00 | 40.8s | 97/100 + 57/60 PASS, per RUN-NOTES.md only; no standalone red-team report file exists for this video |

Worked examples with full scripts, SEO, shot plans, and scores are in `examples/`.

## Non-negotiable gates

Nothing ships unless every gate below passes. The owner's watch/listen is final and overrides every gate score.

- **Duration:** 30-59 seconds, 1080x1920, 30fps.
- **Script:** 90-105 words, hand-counted. Never trust ChatGPT's own count. Count both tokens and spoken words; both must sit inside 90-105.
- **Voiceover:** Kokoro `am_adam` at speed 1.1, one stem per sentence, -40 dBFS trim, 24 kHz.
- **Loudness (delivered file):** ebur128 -16 to -14 LUFS, true peak at or below -1.0 dBTP, measured on the delivered file with ffmpeg loudnorm.
- **Red-team gate:** quality at least 90/100 AND technical at least 48/60 AND zero criticals. A MAJOR blocks release even when the numeric bars are met.
- **Owner watch/listen:** final. A video is not cleared until the owner has watched and listened.
- **Zero fake:** every viewer-facing word traces to a fact-ledger row. Leak chatter is a topic signal only, never a fact.
- **Audio rights:** VO-only, or VO plus royalty-free music. Never a commercial song or original clip audio at any volume.

## End-to-end workflow

### Step 0. Topic research, fact ledger, banned list

Research the topic across multiple independent sources. Write a fact ledger (F1 to Fn) with a label per fact: CONFIRMED, REPORTED, REACTION, CONFIRMED AS UNANNOUNCED, or REPORTED - DISPUTED, plus a verification note naming the sources read. Write a BANNED list covering disputed names, unannounced counts and lengths, false "announced" claims, comparisons stated as fact, the word "leak" and any leak handle, product links, and wrong relative dates ("yesterday", "tomorrow", "tonight" misuses). Check the topic appears in no earlier run folder or recent video. For trailer-motion claims, survey at 1fps and claim spans in `trailer-windows.md` before finalising; no two videos use the same span; M23-blocked spans are never usable. On a multi-video run, the coordinator publishes a `RUN-ALLOCATION.md`: a frame belongs to exactly ONE video as hero-or-beat; a hero BACKUP is contingency only, cut only if the hero fails a later gate, never also a beat in the same video.

### Step 1. ChatGPT brief, script, SEO, thumbnail brief

Paste the brief verbatim into a NEW ChatGPT conversation. Fixed brief elements: Short is 30-59 seconds, English only; official Rockstar material only; no fake claims; numbers written as WORDS, never digits, in every number in the script including dates, counts, times, and money; no product links anywhere; vary attribution, never open three VO lines with the same attribution word; no phrase repeated verbatim across beats. Script beats are prescribed in the brief (hook, what, plot, scale, caveat, countdown with exact wording). ChatGPT writes every script; no agent-drafted script ships without a ChatGPT rewrite pass. The same return gives the SEO package: title (verbatim, character count stated), description (hook first, facts in order, Sources line, countdown line last, no product links), 12 tags in verbatim brief order, and a thumbnail brief (cover text verbatim, base frame plus backup frame, 1080x1920 9:16, headline in a clean upper portion, safe margins on all edges, verify full-res before delivery). SEO packs may be written pre-publish; the standing rule is that SEO is applied after the video is public unless the owner orders otherwise.

### Step 2. Honesty check (before build)

Hand-recount the script to 90-105 words, counting both tokens and spoken words. Check every fact traces to the ledger, the banned list is clean, attribution is varied (M18, M26), the countdown is exact, dates are verified, the title character count is verbatim, the description Sources line is present, the 12 tags are in order, there is no product link, and the thumbnail brief cover text is verbatim with base and backup frames and the M27 note present.

### Step 3. M20 pool gate (BEFORE any VO)

Estimate needed frames from the script (word count times measured pace, plus gaps and holds), triage the backdrop pool, and count ONLY full-res-verified clean frames: head, middle, tail, AND fade boundaries checked at full resolution. A contact-sheet tile verdict never counts a span clean. Record the result in `POOL-GATE-RECORD.md`. If the verified pool is smaller than need plus slack, STOP before VO, cards, and mix, and report. Across a multi-video run keep a running pool ledger: every build deducts its used slices. Measure each source's active picture bounds first (M29): Trailer 2 active y=216..1943; Launch Trailer active y=120..2039. Run full-slice safety sampling on every candidate (M19) and check triage against the run's shared blocklist (M23).

### Step 4. VO synthesis (Kokoro)

Venv `~/workspace/.venvs/v1fix1` (kokoro-onnx 0.6.1). Voice `am_adam`, speed 1.1 locked, -40 dBFS trim, 24 kHz, one stem per script sentence. Outputs: `work/vo/s01..sNN.wav` (PCM_16) plus `work/vo_report.json` (voice, speed, per-stem raw and trimmed seconds, trimmed frames at 30fps, sample rate, words, file). Word bypass: if Kokoro mangles a word, bypass it in the SPOKEN text only; on-screen text keeps the correct spelling. Example: "Kaseya" was bypassed as spoken "Kuh-say-uh" after testing 7 spellings; on-screen text stays "Kaseya". Always check the voiceover; the AI voice reads maths and number words strangely.

### Step 5. VO check: exact subtitles via faster-whisper

Words and spelling come from the SCRIPT (exact); timing comes from Whisper word timestamps. Run faster-whisper with `word_timestamps=True` on the VO and write `vo_check.json` plus `word_timings.json` (word timestamps for caption building). Whisper-over-music artefacts are expected on the final mix: lines mangled over the bed but heard correctly on the clean concat are artefacts, not missing VO. If Whisper hears a word differently from the script, prove it with a fresh Kokoro control synthesis before changing the caption; the caption uses script spelling.

### Step 6. VO concat (varied gaps, M3)

Concatenate stems with varied gaps in frames (V1: 8/10/6/12/9/8/10/7; V3: 8/5/8/5/8/5; V2: 8 gaps of 0.35s). Output `work/vo_concat.wav` (24 kHz mono) plus `work/timeline.json` (exact stem start and end frames at 30fps, total frames plus 2f tail pad).

### Step 7. Cut stills and motion (active-area windows only, M29, M21)

Still recipe: precrop a 1215x2160 window from the official still, then a static 1080x1920 lossless clip; the Remotion Shot component supplies the eased 1.03 to 1.1 push-in, so bake no zoompan (no double-zoom). Motion recipe: 9:16 window from the MEASURED active picture only, centre windows, exact frame counts, libx264 crf 0, 30fps, 1080x1920. Default still window: centre x=1312 unless a named exception applies. All clips are frame-count-verified with ffprobe. Shot discipline: about 1 shot per sentence, at least 3s per shot as the aspiration, slow background movement (M24); cuts on every information beat (M22); still windows in the trio run were 33-99f; the v3 recipe caps static holds at 2.0s (see Known limits for the tension with the 3s aspiration).

### Step 8. Cards (M13 strip) and captions

One M13 graphic per video: a strip of 3 lines plus a source chip plus a caveat chip, no digits on cards (numbers as words), every line tracing to ledger rows. Each card must be a distinct designed component; two cards sharing a template fail storyboard. M34 qualifier on the card at headline size. Read every card on its frame (M28). Captions: phrase captions of 2-4 words, fixed lower-third, spring pop-in; keyword colour only on key words. No captions during card windows. No caption event overlaps any card window. No caption over card text; no lone "the", "a", or "no" on screen. Caption words are script words only, timed from STT. Put a "Footage: Rockstar Games" credit on the opening shot.

### Step 9. Mix (VO plus bed, M4, M35)

VO stems at timeline starts; bed ducked to 0.33 under VO, 1.0 in gaps, 0.1s fades; peak-normalize to -1.5 dBFS; output `work/mix.wav` (24 kHz). Bed: the royalty-free signature bed, tiled to length if shorter. VO-only is allowed ONLY if silencedetect on the delivered file proves no dead gaps (M4). Trailer audio is never used. No commercial music (M35): the build checks audio RIGHTS, not just levels, at assembly and at upload. Stereo warning: the mix is mono; Remotion renders stereo, which adds about +3 dB (dual-mono power sum), so loudnorm passes must account for the stereo render.

### Step 10. Remotion render

Copy the stealth-patch v3 scaffold as the base (copy, NEVER edit the v3 project in place). Remotion 4.0.543. Known render behaviour: Remotion 4 rejects CRF 0 for H.264 (render at crf 12); a frame timeout at the 30s default is fixed with a longer timeout flag; run one render at a time on a small machine (a concurrent sibling render caused an OOM kill). The Remotion render itself outputs yuvj420p / full-range video even with `--pixel-format=yuv420p`; the flag does not take effect. That is why Step 11 exists. No full literal render command is recorded in the sources; see Exact commands for the template and verification procedure.

### Step 11. Grade, colour-tag fix, loudnorm

Grade chain (v3 Remotion recipe): deband, grain, S-curve (0.94 highlight shoulder), saturation 1.00, clamp AFTER grade (Y[20,234], U/V[16,240]), yuv420p, crf 18, preset slow; tags bt709 x4 plus tv. Colour-tag fix (M36): re-encode with `scale=in_range=pc:out_range=tv` plus `setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709` in the filter chain. Output-level `-color_trc` / `-color_primaries` flags do NOT stick. Loudnorm is re-applied in the same pass and re-measured. Loudnorm recipe (Nov 15 trio): single-pass I=-15.5 (an I=-16 target reads -16.16 and fails the floor). If a fix is needed, use gain plus a limiter, never a second loudnorm pass. Verify the delivered file by ffprobe: yuv420p, tv range, bt709 space plus transfer plus primaries, all four fields, before red-team.

### Step 12. Builder QC on the delivered file (M25: re-measure, never trust)

Verify duration at or below 59s, 1080x1920, 30fps; loudness in band on the delivered file; silencedetect 0 hits; cropdetect 1080:1920:0:0 full-frame with no bars, on EVERY motion span (M21); STT on delivered audio matches the script (all stems in order, verbatim modulo expected Whisper normalizations); frame inspection of card frames, motion head/mid/tail, and caption timing; M28 read of every card on its frame; thumbnail viewed full-size at 1080x1920 (three views: builder, red-team, coordinator, M27). Every measurement claimed must be traceable to the artifact file it cites.

### Step 13. Red-team gate (independent reviewer, did not build)

Red-team re-runs silencedetect, loudnorm, STT, and frame checks from the delivered file as a matter of course (M25). See the rubric below. A video is not cleared until an independent re-measure from the DELIVERED file confirms the numbers.

### Step 14. Scheduling and upload

M30 re-derivation at scheduling (and any re-schedule): every relative-date word in the script, on every card, in the SEO, and on the thumbnail is re-derived from the ACTUAL air date; a mismatch is a fix1 rebuild (VO re-record plus card re-render), never a silent ship and never a parent rewrite of a ChatGPT line. M31 check at scheduling: time-of-day plus eligibility, not just dates. Upload checklist: title keyword-first, at or below 100 chars, honest; description complete with hook first, facts in order, Sources line, countdown line last; tags 10-14 targeted tags drawn from title and description keywords (never 0, never 2 near-duplicates); category Education; video language English (must not be left on "Select"); altered-content AI disclosure YES, always; audience Not made for kids; HD rule: upload as Unlisted, wait for HD 100 percent, then publish or schedule. After publish or schedule, re-open the Studio Details page and READ BACK all 8 fields: title, description, tags, category, language, AI disclosure, visibility (plus schedule time), audience. Any field wrong or empty is fixed immediately and re-verified. Confirm a caption track exists; if missing, recheck in 48h. Record the video ID plus publish time in the upload log. Joker adaptation note: Joker uploads carry no product links (banned in every brief) and no playlist; the NeedCraft description template (Gumroad product link plus IG link) must NOT be imported into Joker uploads.

## The M1-M36 rules

Each rule below carries its number, title, and full operative requirement, condensed from the mistakes record. Owner rules not yet in the M-record are listed separately after M36 and are not M-rules.

**M1 Playbooks read first.** Playbooks read first (concept report, ledger, OS, SOP, mistakes record), before planning.

**M2 Creative bar judged, not just technical.** Creative bar judged, not just technical (hook, premium graphics, evidence chips, diagram).

**M3 VO gaps varied, never metronome.** VO gaps varied, never metronome. Trio practice: V1 gaps 8/10/6/12/9/8/10/7 frames; V3 gaps 8/5/8/5/8/5.

**M4 Bed audible in every gap, never silence.** Bed audible in every gap, never silence (silencedetect NONE).

**M5 Kokoro proven by running.** Kokoro proven by running (new install, first-try synthesis).

**M6 Frame-per-beat inspection.** Frame-per-beat inspection of rendered frames; defects found, fixed, and re-verified before encode.

**M7 Beat-length check pre-render.** Beat-length check pre-render; timeline derived from measured VO durations.

**M8 Owner's watch/listen is FINAL.** Owner's watch/listen stated as FINAL throughout; no listen claimed from this environment. No gate score substitutes for it.

**M9 Synthetic flat-frame test FIRST.** Synthetic flat-frame test FIRST (lossless, 3 levels); LUT layouts tested on tiny chart images, never full encodes.

**M10 Grade applied, not neutral.** Grade applied (S-curve 0.94 shoulder plus saturation 1.05), not neutral. Note: the v3/Remotion-era recipe uses saturation 1.00; this skill uses 1.00 for the Remotion-era recipe and records the difference in Known limits.

**M11 Peak/word-pop captions only.** Peak/word-pop captions only, never a running transcript; no permanent line. Adapted practice: word-pops on stressed words only; later practice is phrase captions of 2-4 words, fixed lower-third, spring pop-in, never one-word-at-a-time through function words.

**M12 Every number is a tool measurement.** Every number is a tool measurement on the delivered file (cut count is a counted list; STT diffs explained, not hidden).

**M13 SHOW-TEST.** Every diagram or illustration beat must show the real object AND the action AND a visible consequence in one glance (for example key fob plus scan beam crossing it plus status flipping LOCKED to CLONED; slim jim plus latch plus door opening). If a beat only labels the thing, draws its shape, or loops a decorative motion with no object and no consequence, it FAILS: redraw it, do not ship it. Applied at storyboard stage and re-checked on inspected frames.

**M14 NO FORCED CUT-COUNT TARGET.** Never force a visual change every 2 seconds. A beat holds as long as the information needs; a still can hold with readable evidence plus a purposeful reveal. Cut on information change, not on a timer.

**M15 TECHNICAL PASS is not CREATIVE PASS.** Every build report carries Technical status AND Creative status separately. "Premium" needs 85/100 plus no critical failure plus human watch/listen approval. Until the owner rules, the report says "Creative REVIEW PENDING", never self-certified premium. Note: the 85/100 "Premium" bar is a different bar from the red-team release gate of at least 90/100; the relationship between the two is not stated in the sources.

**M16 NO EMPTY BEAT OPENINGS.** Every beat's first frame must already be visually complete: focal object plus headline or chip present at the beat's frame 1. Nothing the viewer needs may arrive seconds later as a pop into an empty zone, and no beat may open header-only on a near-black field for more than about 1s. If a beat's opening frame looks unfinished or dead, re-stage the beat: move the pop earlier, fill the zone, lighten the field. Do not ship it on a docked point. Checked at storyboard stage and re-checked on inspected first-frames.

**M17 EVERY VIEWER-FACING WORD NEEDS ITS OWN LEDGER ROW.** No card, footer, chip, panel, or caption wording may be written from a paraphrase of a ledger row about something else, or from no row at all. A row saying "X is separate from Y" NEVER licenses a label for Y. EACH SIDE of a contrast card needs its own row. Any descriptor (nationality, genre, identity, provenance) with no row is either sourced as a new row or cut back to the sourced wording. Checked at storyboard stage AND by grepping render text for unledgered adjectives before red-team; red-team catching it is late, not the plan.

**M18 SCRIPT REPETITION SCAN.** Before VO synthesis, read the script as a text, not as footage. No attribution word may open 3 or more VO lines; no phrase may repeat verbatim across beats; no single noun may carry every beat. Every gate scores the rendered file (frames, loudness, STT, factual labels); none of them reads script pattern, so a high-scoring render can still ship a script the owner rules bad on first listen. Varied attribution is the fix (reportedly / The demo / per the preview / Nelson says / Press:). Scope is never cut to fix repetition (M17 still binds every rewritten line). A repetition found after render is a rebuild, not a note.

**M19 FULL-SLICE CONTENT-SAFETY SAMPLING.** Before any gate signs off content safety, sample EVERY backdrop slice across its full span: head, middle, AND tail at minimum, checking (a) no social-UI overlay, (b) no sexualized framing, (c) no torso-dominant close-up, (d) the ledger label matches the inspected frames, not the slice name. Stage-open-only sampling is insufficient by construction. A frame description written from a label instead of an inspected frame is a defect in the report, not just the video. A defect found only by red-team full-slice sampling is a late catch, not the plan.

**M20 POOL-ARITHMETIC GATE BEFORE VO, COUNTED IN FULL-RES FRAMES ONLY.** Before any VO synthesis, estimate needed frames from the script (word count times measured pace plus gaps and holds), triage the backdrop pool, and count ONLY full-res-verified clean frames: head, middle, tail, AND fade boundaries checked at full resolution; a contact-sheet tile verdict never counts a span clean. If the verified pool is smaller than need plus slack, STOP before VO, cards, and mix and report: never build VO, cards, and mix on an unproven pool. Across a multi-video run, keep a running pool ledger: every build deducts its used slices from the remaining clean total, so exhaustion is forecast, not discovered at build 7.

**M21 PIXEL-CHECK BARS ON EVERY MOTION SPAN, NEVER ONE REPRESENTATIVE SPAN.** Builder QC must pixel-verify letterbox bars separately on EVERY motion span in the timeline: head, middle, and tail frames of each span, and name each span's verdict in the QC report. A bar-check that names only one span verifies only that span; every unnamed span is UNVERIFIED, not passed. Any span found barred is re-cut as a fill-crop and re-verified before red-team, never left for red-team to catch.

**M22 CUT ON EVERY INFORMATION BEAT, NEVER ONE-SPEED SCROLL.** Every VO information change gets a hard cut (or a distinct motion change) at that beat: a new shot, a new camera move, or a new card state, timed to the spoken word. A continuous scroll, drift, or single-speed hold across two information changes FAILS storyboard, whatever the scorecard says, because it is audio laid over visuals, not an edit. Checked at storyboard stage (beat map must name the cut frame for every information beat) and re-checked on the rendered file (frame-diff or shot list must show a change at each beat).

**M23 SHARED SAFETY BLOCKLIST ACROSS A MULTI-VIDEO RUN.** Any slice or span cut for content-safety in ANY video of a run is banned in EVERY video of that run, immediately, by source timecode. The coordinator keeps one running blocklist and every builder checks triage against it before building. A triage label never overrides inspected frames: a slice described as an "object" close-up must still be viewed at full resolution across its full span (M19) before it counts clean.

**M24 SLOW BACKGROUND CLIPS: NEVER FAST, NEVER RAPID-FIRE CHANGES.** No video's background clips may move too fast or change too quickly: rapid background movement and quick-fire clip changes hurt the eyes and break natural connection with the scene. Background movement stays slow; each clip holds long enough for the viewer to register what it shows and connect with it naturally. Cuts still land on information beats (M22), but the movement INSIDE a span is slow, and a span never flashes by before the eye settles. The test at storyboard and on the rendered file: can the viewer rest their eyes on the background and follow it, or does it strain? If it strains, it is too fast: slow it down, do not ship it on a docked point. Applies to every video from Nov 6 onward, Joker Gaming and NeedCraft alike, and the red-team scores pacing against it.

**M25 QC CLAIMS MUST MATCH THEIR OWN ARTIFACTS; RED-TEAM RE-MEASURES, NEVER TRUSTS.** Every measurement claimed in a build report must be traceable to the artifact file it cites: the report names the file and the number comes from that file. A claim its own artifact contradicts (silencedetect "0 hits" when the file shows hits; STT "100%" from a garbled work file) FAILS the QC report itself, not just the measurement: the video is not cleared until an independent re-measure from the DELIVERED file confirms the numbers. Red-team re-runs silencedetect, loudnorm, STT, and frame checks from the delivered file as a matter of course; a builder's numbers are never taken on trust, however clean the scorecard looks. M12 governs that numbers are tool measurements; M25 governs that the claimed measurement actually exists in the cited artifact.

**M26 M18 TIGHTENING: COUNT ATTRIBUTION ROOTS BY OCCURRENCE, NOT BY POSITION.** No attribution root ("reportedly" / "reported" / "confirmed" / "per" plus source, and any other attribution word) may occur more than TWICE in any 3 consecutive VO lines, regardless of where it sits in the line: mid-line counts exactly like line-opening. After VO, red-team checks STT word timestamps: 3 occurrences of the same attribution root within any about 15s window FAILS the script, whatever the text scan said. If it trips, the fix is a ChatGPT rewrite BEFORE render (a repetition found after render is a rebuild, not a note, per M18). The red-team's M18 re-listen is the gating check, and their fresh ear decides. The threshold is 2-in-3-lines and 3-in-15s, not zero repetition: a "reported" 3x case with only two in the opening stretch and the third 27.1s later in a different slot PASSED as a deliberate two-item list intro, not a tic.

**M27 THUMBNAIL TEXT SAFE MARGINS: NO TEXT TOUCHING, CROSSING, OR RUNNING OFF ANY EDGE.** Every hook-cover thumbnail's text must sit well INSIDE the frame with clear safe margins on ALL four sides. Text touching, crossing, or running off any edge, including text that only looks fine in a small preview, is a DEFECT and the thumbnail is rebuilt, never shipped on a docked point. The check is done by VIEWING the actual thumbnail file at full size (1080x1920) before delivery, not from a contact sheet or a small preview: the builder views it, the red-team views it, and the coordinator views it, three full-size views, all passing, before the thumbnail ships. Applies to every thumbnail from Nov 8 onward, Joker Gaming and NeedCraft alike. In thumbnail briefs, spell the margin out: all text inside the central safe zone with a clear margin from every edge; the thumbnail brief's word-scan includes a safe-margin view.

**M28 CARD-TO-IMAGE CONTRADICTION CHECK: READ THE CARD ON THE FRAME.** At storyboard AND on inspected rendered frames, read every card, chip, and label exactly as the viewer sees it, composited over its actual image, and ask three questions: (1) does the image SHOW what the card says? (2) does the image CONTRADICT the card? (3) does the card cover or collide with text already in the frame? If any answer fails, re-stage the beat: move the card, change the image, or rewrite the card. Do not ship it on a docked point. A card whose words are ledger-sourced (M17) and whose frame is safety-clean (M19) can still be wrong TOGETHER: the words and the picture are checked separately by every gate, and nobody reads them as one statement. The check is a named step at storyboard (card placement named against its frame) and on inspected frames (builder plus red-team each read the card in place).

**M29 SOURCE ACTIVE-AREA MEASUREMENT BEFORE ANY CROP: M21'S MISSING FIRST STEP.** Before any motion span is cropped, measure the active picture bounds of the source frame (row-profile at full resolution: first and last non-black rows) and record the active area in the build report. A 3840x2160 trailer file is NOT a full-frame picture: both trailers carry baked-in letterbox (Trailer 2 active y=216..1943; Launch Trailer active y=120..2039). Any crop taken from the file's full frame inherits those bars. M21's per-span pixel check is then run on the DELIVERED file (head, mid, tail per span), never on the construction argument: "impossible by construction" is not a measurement, and it fails M25 when the delivered file contradicts it. Checked at pool and triage stage (active area named per source) and re-checked on the delivered file (M21).

**M30 RELATIVE DATES RE-DERIVED AT SCHEDULING, NEVER CARRIED FROM THE BUILD DATE.** At scheduling time, and again at any re-schedule, every relative-date word in the script, on every card, in the SEO, and on the thumbnail is re-derived from the ACTUAL air date (countdown = launch date minus air date; "today/tomorrow/begins today" checked against the air date, not the build date). A countdown or relative date written for the build date is STALE the moment the air date moves, and no gate before scheduling reads it. The check is a named step at scheduling (parent or coordinator, grep plus read-back on the delivered files), and a mismatch is a fix1 rebuild (VO re-record plus card re-render), never a silent ship and never a parent rewrite of a ChatGPT line: the corrected line comes back through ChatGPT verbatim. Internal docs carry the same rule: a tracker line quoting a countdown names its air date beside it, so a later reader never mistakes a build-date countdown for a live one.

**M31 LEAD CLAIM CARRIES TIME + ELIGIBILITY; A SUB-LINE NEVER CURES A HEADLINE.** The title, the hook card, and the VO opening line must each carry the time AND the eligibility of the claim they make: when something opens, and who it is open to, in the claim itself, not in a sub-line, not later in the video. A qualifier that lives only as small type under a giant headline, or that arrives on screen 20+ seconds in, does NOT cure a headline that implies the opposite. At storyboard, the lead claim is read as a viewer at air time would read it: what does this title or hook say is true RIGHT NOW, for ME? If the answer is wrong at air time (sale opens 7 hours later; winners only), the claim is rewritten, via ChatGPT, never patched with a sub-line. The check is run at storyboard AND at scheduling (M30's re-derivation step, extended: time-of-day plus eligibility, not just dates). M30 covers relative DATES; M31 covers time-of-day implication and eligibility, which M30 explicitly does not.

**M32 VERIFY A NEGATIVE CLAIM AT THE PLACE THE THING WOULD BE PUBLISHED OR SOLD, NOT ONLY AT THE BRAND'S OWN PAGES.** A claim of the form "no X published / no price / not announced / no set times" must be checked at EVERY place X could appear, above all the seller's or distributor's page, where the thing is actually sold, never only at the brand's own pages. The brand's page is the wrong place to verify a price: the price lives on the seller. The check is a named step at storyboard (the ledger row for a negative claim names the seller or distributor source it was checked against, not just the brand source) AND at audit (the auditor re-checks the seller page independently, with fresh eyes and fresh sources). A negative claim with no seller-page check is UNVERIFIED, not true.

**M33 A TARGETED REBUILD RE-VERIFIES THE WHOLE REBUILT CARD, ELEMENT BY ELEMENT.** When a fix re-renders one card, the builder's QC re-verifies EVERY design element on that card against the previous version: pill, source line, scrim, margins, legibility, not just the line that changed. A targeted fix is a rebuild of that card, and the card is checked whole, not by delta. Checked by viewing the rebuilt card's graphic file directly AND its delivered frames, side by side with the same frame of the previous version.

**M34 FIGURE CARDS CARRY THEIR QUALIFIER WORD: ON THE CARD, WITH THE FIGURE, AT HEADLINE SIZE.** A figure's qualifier ("over" / "plus" / "more than" / "above" / "estimated" / "net of") must appear ON the card WITH the figure, at headline size, never only in the VO, the description, or a small sub-line. A qualifier that lives only in the VO does not cure a headline figure that reads as exact. Checked at storyboard (every figure card names its qualifier word, its size, and the spoken syllable it syncs to) and on inspected rendered frames (read the figure plus qualifier together, as a viewer would; if the card alone reads as an exact figure, it FAILS). A dropped qualifier is a figure misstatement, not a wording preference. M31's logic ("a sub-line never cures a headline") applies to figures as well as to time and eligibility.

**M35 NO COMMERCIAL SONG OR ORIGINAL CLIP AUDIO IN A JOKER SHORT: VO-ONLY OR ROYALTY-FREE.** Never keep a source clip's commercial song or original audio under the VO at any volume: a low volume does NOT dodge Content ID. The mix is VO-only, or VO plus royalty-free music (for example Flow music, as the Nov 13 trio used). The build checks audio RIGHTS, not just audio levels: loudnorm, STT, and every existing gate measure the mix; none of them checks whether the audio is licensed, so the rights check is a named step at assembly (source audio stripped; every music element named with its licence or source) AND at upload (Studio's copyright check must read clean before the video is left live; a claim means a clean rebuild without the song plus re-upload, never a dispute on audio we have no rights to).

**M36 REMOTION COLOUR-SPACE FIX IS SETPARAMS-IN-FILTER-CHAIN, VERIFIED ON THE DELIVERED FILE.** A Remotion/Chromium render outputs yuvj420p / full-range video even with `--pixel-format=yuv420p`: the flag does not prevent it. The fix is a re-encode with `scale=in_range=pc:out_range=tv` plus `setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709` in the filter chain (output-level `-color_trc` / `-color_primaries` flags do NOT stick: libx264 takes VUI from frame properties). Loudnorm is re-applied in the same pass and re-measured. The delivered file is then verified by ffprobe: yuv420p, tv range, bt709 space plus transfer plus primaries, all four fields, before red-team. A render whose colour tags are unverified on the delivered file is UNVERIFIED, not passed, whatever the render command claimed.

### Owner rules not yet in the M-record (binding, but not M-rules)

These bind builds today but have no M-number yet. Do not present them as M37 or later.

- **VO word bypass:** where the AI voice struggles with a word, bypass that word in the spoken text (for example "version" dragged out lengthily; use a simple or alternate spoken word instead). Always check the voiceover.
- **Cut pace:** about 1 shot per sentence, about 3s or more per shot; rapid scene changes look odd.
- **Thumbnail level bar:** real GTA VI logo big at top plus short 1-3 word hook plus one strong focal image plus high contrast; Gemini must NOT draw the logo (it garbles it): composite the authentic logo with PIL instead.
- **Always better than last:** every new GTA VI video must be BETTER than the previous one; the stealth-patch v3 (Remotion, phrase captions, designed cards) is the current bar to beat.
- **Queued items (not yet rules):** hand-count every script, never trust ChatGPT's word count; M34 enforced at brief-spec stage; allocation-compliance check at builder QC; M22 tightening (a staged card's final reveal must coincide with the last fact it anchors); every chosen shot window strip-checked cut-free at 0.5s steps; captions are phrases (2-4 words) OR stressed-keyword pops, never one-word-at-a-time through function words; no caption event overlaps any card window; at storyboard each card names its own layout, palette, and focal element (two cards sharing a template fail storyboard); a hold is judged on the frame strip: if three frames a second apart are near-identical, the shot is a still and either moves (real motion) or ends (at or below 2.0s).

### Daily training loop (how the M-record grows)

Each run, in order: (1) MISTAKE-FIND: read the latest build reports and owner verdicts, list NEW mistakes not yet in the record; owner verdicts override gate scores; (2) RESEARCH ONE TECHNIQUE from a reference (current priority until the owner says diagrams are fixed: DIAGRAM CRAFT: SHOW the actual thing); (2b) DAILY SHORTS WATCH: 2-3 latest GTA VI Shorts, watch-only, no downloads, likes, comments, or subscribes; (3) write the dated training note with (a) mistakes found, (b) technique studied, (c) ONE concrete checklist rule, (d) one diagram exercise description; (4) UPDATE THE CHECKLIST: append any new rule to the mistakes-record, append-only, verify the append landed; (5) DAILY LOG: one summary line in the daily memory note. Hard limits: no builds, renders, uploads, publishes, schedules, SEO, account actions, or existing-video touches; no invented claims: evidence labelled CONFIRMED, REPORT, or RUMOUR as the ledger does.

## Exact commands

Only the commands below are verbatim from the build sources. Anything labelled template is NOT verbatim history: syntax-verify it before use.

### Kokoro VO synthesis (verbatim)

```python
kokoro = Kokoro("/home/hatch/.cache/kokoro-onnx/kokoro-v1.0.onnx",
                 "/home/hatch/.cache/kokoro-onnx/voices-v1.0.bin")
samples, sr = kokoro.create(text, voice="am_adam", speed=1.1, lang="en-us")
```

```python
def trim_dbfs(x, sr, thresh_db=-40.0):
    peak = np.max(np.abs(x))
    if peak == 0:
        return x
    thresh = peak * 10 ** (thresh_db / 20.0)
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    return x[idx[0]:idx[-1] + 1]
```

### faster-whisper VO check (verbatim)

```python
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(path, language="en", beam_size=5, word_timestamps=True)
```

Normalization used in the check: lower-case, strip `. , — '`, then replace Whisper digit forms: `"13th"` to `"thirteenth"`, `"31st"` to `"thirty first"`, `"21st"` to `"twenty first"`, `"18th"` to `"eighteenth"`, `"19th"` to `"nineteenth"`, `"7 pm"` to `"seven p m"`, `"ign"` to `"ign"`.

### VO concat (verbatim)

```python
# gaps in frames between stems (varied, M3)
GAPS_F = [8, 5, 8, 5, 8, 5]
```

```python
cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + [
    "-filter_complex", concat, "-map", "[aout]",
    "-ar", "24000", "-ac", "1", os.path.join(WORK, "vo_concat.wav"),
]
```

Each stem contributes `"-i", s["file"]` and each gap contributes `"-f", "lavfi", "-t", str(gap_s), "-i", "anullsrc=r=24000:cl=mono"`, and `concat = "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[aout]"`.

### Cut stills and motion (verbatim)

Precrop plus static still clip:

```python
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
     f"crop=1215:2160:{x}:0", "-frames:v", "1", out], f"precrop {name}")
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", img,
     "-vf", "scale=1080:1920,format=yuv420p", "-frames:v", str(frames),
     "-c:v", "libx264", "-crf", "0", "-preset", "veryfast", out], name)
```

Motion span (9:16 window from the measured active picture only):

```python
run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", src,
     "-vf", f"crop={win_w}:{win_h}:{win_x}:{win_y},scale=1080:1920,fps=30,format=yuv420p",
     "-frames:v", str(frames),
     "-c:v", "libx264", "-crf", "0", "-preset", "veryfast", out], name)
```

V3 motion windows (verbatim values): T2 spans `972x1728 @1434,216` (y=216 active area); LT span `1080x1920 @1380,120` (y=120 active area).

V2 still recipe (A/B recipe, CRF 18):

```python
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src,
                    "-vf", f"crop=1215:2160:{cx}:0,scale=1080:1920",
                    "-q:v", "2", jpg])
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "4", "-i", jpg,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", "30", mp4])
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "12.0", "-i", LT, "-t", "2.1",
                    "-vf", "crop=1080:1920:1700:120,scale=1080:1920,setsar=1",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", "30", "-an", out])
```

Frame-count verification (verbatim pattern):

```python
p = subprocess.run(["ffprobe", "-v", "error", "-count_frames",
                    "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames,width,height",
                    "-of", "csv=p=0", os.path.join(CLIPS, f)],
                   capture_output=True, text=True)
```

### Mix silencedetect check (verbatim)

```python
r = subprocess.run(["ffmpeg", "-v", "info", "-i", os.path.join(WORK, "mix.wav"),
                    "-af", "silencedetect=noise=-50dB:d=0.3", "-f", "null", "-"],
                   capture_output=True, text=True)
```

Mix constants (verbatim): `DUCK = 0.33`, `FADE = int(0.1 * SR)`, `SR = 24000`, `FPS = 30`, peak scale `10 ** (-1.5 / 20)`.

### Loudnorm: older stealth-patch recipe (verbatim, labelled)

The literal loudnorm command recorded on disk is the older stealth-patch one (single pass I=-14, TP=-1.5, verified to land -15.99 LUFS / -1.10 dBTP). It is NOT the Nov 15 trio recipe. The trio recipe is single-pass I=-15.5 (see the template below).

```python
r = subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", f"{W}/video_cap.mp4", "-i", f"{W}/vo_concat.wav",
    "-map", "0:v", "-map", "1:a",
    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-t", "37.79", "-movflags", "+faststart", f"{B}/final.mp4",
])
```

Measure step (verbatim, same file):

```python
r = subprocess.run([
    "ffmpeg", "-v", "info", "-i", f"{B}/final.mp4", "-vn",
    "-af", "loudnorm=print_format=json", "-f", "null", "-",
], capture_output=True, text=True)
```

### M36 colour-tag fix fragments (verbatim)

```
scale=in_range=pc:out_range=tv
setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709
```

### Templates: syntax-verify before use (NOT verbatim history)

The five items below were recorded only as prose fragments in the sources. Do NOT present them as verbatim history. Verify each one against the delivered file before trusting it.

- **Remotion render (template, syntax-verify before use):** recover the exact invocation from the project config on disk first. Known fragments: Remotion 4 rejects CRF 0 for H.264 (render at crf 12); use `--timeout=120000` (frame timeout fix) and `--concurrency=2` (one render at a time on a small machine); `--pixel-format=yuv420p` does not prevent full-range output. Verify: render completes all frames, output is 1080x1920 at 30fps.
- **Nov 15 loudnorm invocation (template, syntax-verify before use):** single-pass `loudnorm=I=-15.5:TP=-2.0:LRA=11` on the delivered file, then measure with `loudnorm=print_format=json`. Verify: measured input_i in -16 to -14 LUFS and input_tp at or below -1.0 dBTP. If out of band, fix with gain plus a limiter, never a second loudnorm pass.
- **Grade filter graph (template, syntax-verify before use):** chain order is deband, grain, S-curve (0.94 highlight shoulder), saturation 1.00, clamp AFTER grade (Y[20,234], U/V[16,240]), yuv420p, crf 18, preset slow, tags bt709 x4 plus tv. No literal filter graph with parameters exists in the sources. Verify: ffprobe shows yuv420p, tv, bt709 x4; signalstats shows the clamp holding on the delivered file.
- **M36 full re-encode (template, syntax-verify before use):** re-encode from the raw render with the two filter fragments above plus CRF 18, loudnorm re-applied in the same pass. Verify: ffprobe shows yuv420p, tv range, bt709 space, bt709 transfer, bt709 primaries, all four fields; loudness re-measured in band.
- **V1 colour remux (template, syntax-verify before use):** lossless remux (`-c copy`) with `-color_primaries`, `-color_trc`, and `-colorspace` set to bt709. The `h264_metadata` bitstream filter alone did NOT change the tag; the output-level remux is the working route. Verify: ffprobe tags read bt709 x4 and framemd5 of decoded frames is unchanged versus the pre-remux file.

### Verification procedure for any delivered file

Run ffprobe and read: `pix_fmt` (must be yuv420p), `color_range` (tv), `color_space`, `color_transfer`, `color_primaries` (all bt709). Run loudnorm with `print_format=json` and read `input_i` (-16 to -14 LUFS) and `input_tp` (at or below -1.0 dBTP). Run silencedetect (noise -50dB, d=0.3 on the mix; noise -40dB, d=0.5 on the delivered file) and read 0 hits. Run cropdetect and read 1080:1920:0:0 with no bars on every motion span.

## Red-team rubric

Release thresholds: quality at least 90/100 AND technical at least 48/60 AND zero criticals AND the owner's watch/listen. A MAJOR blocks release even when the numeric bars are met.

### The 60-point rubric

| Area (max) | What it scores |
|---|---|
| Facts (10) | Every claim traces to the ledger; banned list clean; qualifiers present; countdown and dates exact |
| VO (10) | All script words verified in order by STT; no missing or mangled lines; word bypasses proven |
| Captions (8) | Spelling, timing, no card overlap, no face coverage, phrase style, no lone function words |
| Cards (8) | All cards correct and ledger-sourced; no black-opening defect; qualifiers at headline size |
| Visuals (10) | Allocated frames only, no doubles, motion clean, bars checked on every span, pacing per M24 |
| Thumbnail (7) | Real logo verified, hook correct and verbatim, safe margins, one strong focal image |
| Technical (7) | Loudness in band, colour tags correct, hashes match, no silent tail, duration and format correct |
| **Total (60)** | **Pass at 48 or above, with zero criticals and no unresolved MAJOR** |

No /100 area breakdown is documented in any source. Do not invent one. The /100 quality score is a whole-number judgement by the independent reviewer, with minors docked and recorded with evidence and frame numbers.

Severity vocabulary: **CRITICAL** is release-blocking, zero allowed. **MAJOR** must be fixed before release even if numeric bars are met. **MINOR** is docked points, no rebuild required, still recorded with evidence and frame numbers. **Observation** is noted with no deduction.

Red-team methods: ffprobe plus sha256 on delivered files; ffmpeg loudnorm plus silencedetect plus blackdetect plus RMS profiles on the delivered file; faster-whisper `small` STT with word timestamps on audio extracted from the delivered MP4, plus `base` and `tiny` cross-checks; fresh Kokoro am_adam at 1.1 control syntheses plus sample-identity comparison; frame grabs viewed full-size (all segments, all cards first/mid/last, motion head/mid/tail, thumbnail) plus luma measurements of card fade-ins; grep checks of deliverable text for banned words and digits; clip-list cross-check for double-assignment; logo hash verification; SEO verbatim diff (title, description, tags).

## Thumbnail method

### The 7 God of Prompt prompts (summarised)

Source: a transcription of @godofprompt's Instagram carousel, saved Nov 8, 2026, judged authentic and usable. Two honest notes: the "$500 designer" framing and income math in Prompt 7 are the creator's sales pitch, unverified, never quoted as fact; Prompt 7 is a sales DM template, NOT a thumbnail prompt, saved for the services and client lane only, never for thumbnail generation.

1. **STEAL THE PATTERN (research):** screenshot the top videos in the niche; Gemini reads them like a designer: what winning thumbnails have in common (faces, colors, number of words, where the text sits); 5 rules, one line each, plus one thing everyone does that you should do differently to stand out.
2. **PICK THE IDEA FIRST:** give the video title plus what happens in it; Gemini returns 3 thumbnail ideas, each with the one feeling it shows (shock, curiosity, hunger), what is in the picture, and text of 4 words or less that ADDS to the title instead of repeating it; then which one it would click and why.
3. **MAKE IT WITH YOUR FACE (generate):** make a YouTube thumbnail in 16:9 from idea [number], using the uploaded photo: keep the face exactly as it is, [shocked face, mouth open], [the object] on the right, a bold [yellow] background, huge white text with a thick black outline: "[your text]". High contrast, easy to read at the size of a stamp.
4. **FIX THE TEXT (edit):** make the text bigger and bolder, 2 lines at most, move it so it does not cover the face; check every word is spelled right; keep everything else exactly the same.
5. **MAKE 3 TO TEST:** make 2 more versions to test against it: one with a different face expression, one with a different background color; keep the text, face, and layout the same. YouTube Studio's Test and Compare runs up to 3 thumbnails on one video and keeps the winner.
6. **CHECK IT NEXT TO THE OTHERS (phone check):** upload a screenshot of the thumbnail next to the videos it will show up beside; on a phone, which one gets clicked first and why; give the one change that would make yours win, then make that change.
7. **SELL IT TO CREATORS (sales DM, NOT a thumbnail prompt):** short DM to [creator name] with [number] subscribers and thumbnails that look [plain / hard to read]; offer a free redo of their latest one, $50/thumbnail with 3 versions to test, or $400/month for up to 10; friendly, under 70 words, no pressure. Services and client lane only.

### Joker adaptation (9:16, official frame, real logo)

1. **16:9 becomes 9:16.** Every Joker thumbnail is a Shorts cover: exactly 1080x1920 (9:16). Always change the ratio in the prompt to 9:16 before sending.
2. **Face becomes official frame.** Prompt 3's "photo of me" does NOT apply to Joker: no faces, no face photo on file. Use the supplied official Rockstar frame as the base instead.
3. **Text is verbatim from the brief, never from the prompt.** The brief's exact text line replaces "[your text]". Every word on the cover must already be written verbatim in the prompt.
4. **M27 safe margins always apply.** All text well inside the frame, verified by viewing the actual thumbnail at full size. Prompt 4's fix-text step is the regen trigger: any spelling error, extra text, or edge-touching text means regenerate, never ship.
5. **PRO model only:** Gemini 3.1 Pro / Nano Banana Pro. Never Flash.
6. **Prompt 1 (pattern) is a research step**, run before a new thumbnail style. Prompt 2 (idea) is how to pick between 3 cover concepts when the brief offers a choice.
7. **Prompt 5 (3 versions)** applies only when the owner orders a Test and Compare run. Default is ONE cover per video, verified. Prompt 6 (phone check) is the full-size view plus margin measurement before upload.
8. **Prompt 7** is services-lane only, never in a thumbnail task.
9. **Never copy the creator's example thumbnails, text, or claims.** Use the prompt structures; the words, frames, and numbers are always ours.

### Level bar and logo rule (binding on every thumbnail)

Real GTA VI logo big at top plus short 1-3 word hook plus one strong focal image plus high contrast. Gemini NEVER draws the logo: it garbles it. The real logo must be composited separately (PIL or Remotion composite) from the authentic logo file, and its hash is verified against the source (gradient logo sha256 starting `18ad6092`, md5 starting `116fe9fe`). Primary route: Gemini Nano Banana Pro (God of Prompt Prompt 3 adapted plus Prompt 4 fix-text pass, 9:16 1080x1920, verbatim cover text, M27 margins). The builder ALSO delivers a Remotion or PIL composite fallback meeting the same level bar, so the video is never blocked on the thumbnail. Word-scan gate before delivery: every word on the cover checked against the brief's verbatim text; any spelling error, extra text, or edge-touching text means regenerate. Thumbnail brief fields: cover text verbatim, base frame plus backup frame (official Rockstar assets), 1080x1920 9:16, headline in a clean upper portion away from faces, generous clearly-visible safe margins on all four edges, no text touching, crossing, or approaching frame boundaries, verify the actual full-resolution thumbnail at 1080x1920 before delivery. Layout note: the hook may sit in the lower portion when the logo large at top forces it down; if the layout is clean and the hook is fully legible, that is resolved sensibly, not a defect.

## Tools

VM reality: Ubuntu 24.04, 4 CPUs, about 8 GB RAM, CPU-only (no GPU), 65 GB free disk. RAM is the binding constraint: run heavy tools ONE at a time.

| Tool | Version | Path or note | Use |
|---|---|---|---|
| ffmpeg | 8.1.2 | system, with libass, libfontconfig, libfreetype, libfribidi, libmp3lame, libopus, libvpx, libx264, libx265; no libvmaf | Encode, decode, drawtext, zoompan, ASS subtitles, loudnorm, signalstats |
| yt-dlp | 2026.10.21 | `~/.local/bin/yt-dlp` | Download source clips and reference videos |
| Python | 3.12.3 | system | Base interpreter |
| Node / npm | 24.22.1 / 10.9.4 | system | Remotion |
| Kokoro TTS | kokoro-onnx 0.6.1 | venv `~/workspace/.venvs/v1fix1`, voice am_adam | Voiceover |
| faster-whisper | 1.2.1 (av 13.1.0) | venv `~/workspace/.venvs/fw` | STT plus word timestamps |
| Whisper models | tiny, tiny.en, base, base.en, small, small.en | `~/.cache/huggingface` (1.4 GB) | tiny is fast; small is more accurate |
| PIL / numpy / scipy / opencv / pydub / soundfile | pillow 10.2.0, numpy 2.5.4, scipy 1.11.4, opencv 5.0.0, pydub 0.25.1 | system python | Graphics plus audio basics |
| Fonts | Inter, Anton, Manrope, SpaceGrotesk, IBM Plex Mono, Instrument Serif plus 1900 system fonts | `~/.fonts/needcraft/`, `/usr/share/fonts/` | Captions and cards (Inter is the pipeline standard) |
| moviepy | 2.2.1 | venv `~/workspace/.venvs/proedit` (1.4 GB), Python 3.12.3 | Timeline compositing in Python |
| scenedetect-headless | 0.7.3 | proedit venv | Cut and scene detection |
| librosa | 1.0.1 | proedit venv | Audio analysis: tempo, BPM, beat tracking, onsets |
| pedalboard | 0.9.26 | proedit venv | Compressor, EQ, de-esser, limiter, reverb, highpass |
| noisereduce | 3.0.3 | proedit venv | Spectral-gating noise reduction for VO |
| pysubs2 | 1.9.1 | proedit venv | Read and write ASS/SRT subtitles |
| rembg | 2.0.87 | proedit venv | Background removal for thumbnails and cutouts |
| onnxruntime | 1.32.0 | proedit venv | Inference backend for rembg |
| ffmpeg-python | 0.2.0 | proedit venv | Build ffmpeg filter graphs in Python |
| auto-editor | 29.3.1 | proedit venv | Auto-cut silences and dead air |
| opentimelineio | 0.18.1 | proedit venv | Timeline interchange, EDL/FCPXML export |
| opencv-python-headless | 5.0.0.93 | proedit venv | Frame analysis, tracking, motion detection |
| pillow (proedit venv) | 11.3.0 pinned | proedit venv | Image ops |
| numpy / scipy / soundfile / imageio / av (proedit venv) | numpy 2.5.4, scipy 1.18.1, soundfile 0.14.0, imageio 2.38.1, av 13.1.0 pinned | proedit venv | Dependencies of the above |
| ImageMagick | 6.9.12-98 | `convert`, `identify` (v6: there is NO `magick` binary; that is v7) | Image ops |
| mediainfo | 24.01 | `/usr/bin/mediainfo` | Media inspection |
| sox | 14.4.2 | `/usr/bin/sox` | Audio ops |
| Blender | 5.3.0 | `~/workspace/video-edit-tools/blender/blender-5.3.0-linux-x64/blender` | Headless 3D motion graphics; use BLENDER_WORKBENCH for fast CPU-safe renders |
| Remotion | 4.0.543 | `~/workspace/video-edit-tools/remotion-test/` | React motion graphics; all `@remotion/*` packages must stay on the SAME exact version |

Gotchas: (1) pip plus /tmp: /tmp is a 512 MB tmpfs, so plain `pip install` fails with "No space left on device". ALWAYS install with `TMPDIR=~/workspace/video-edit-tools/tmp` (and `--no-cache-dir` for big installs). (2) av MUST stay at 13.1.0 in the proedit venv: faster-whisper 1.2.1 calls `av.open(..., metadata_errors=...)`; av 19.x removed that kwarg and faster-whisper crashes. Do not upgrade av. (3) pillow is pinned to 11.3.0 because moviepy 2.2.1 requires `pillow<12.0` while rembg 2.0.87 requires `pillow>=12.3.0`; they cannot both be satisfied. Runtime was verified working with 11.3.0 for both. Do not "fix" the warning by upgrading pillow (breaks moviepy) or downgrading rembg. (4) MoviePy 2.x TextClip needs a font FILE path, for example `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`; a bare font name fails. (5) rembg default session is about 1 GB (`bria-rmbg`); always pass an explicit light session: `new_session('u2net')` (176 MB). (6) RAM: about 8 GB total, often only about 800 MB free when browser tasks are running. Run one heavy tool at a time; never run apt plus a model load together. (7) apt mirror is very slow (about 12.5 kB/s observed); for anything over 50 MB use a direct download. `libasound2` does not exist on Ubuntu 24.04; it is `libasound2t64`. (8) Kokoro espeak-ng quirk: the loader demands the NESTED path `/home/runner/work/espeakng-loader/espeakng-loader/espeak-ng/_dynamic/share/espeak-ng-data/phontab` symlinked to the venv's espeak-ng-data. The symlink lives OUTSIDE the workspace: re-apply after any VM replacement. (9) Remotion licence: free for individuals and companies of up to 3 people; a paid company licence is required at 4 or more people.

Not installed, with reason: DaVinci Resolve (needs a GPU plus a desktop GUI); libvmaf (system ffmpeg was not built with it; use signalstats instead); aeneas (superseded by faster-whisper word timestamps, unmaintained); DeepFilterNet (needs PyTorch, about 2 GB, heavy on this VM); OpenCut (needs Adobe Premiere Pro); Kdenlive, Shotcut, Olive (desktop GUI editors, not scriptable); Natron (GUI compositing; Blender plus ffmpeg cover it); GIMP (PIL plus ImageMagick cover scripted image work).

## Rockstar IP and honesty

- **Official material only.** Build from official Rockstar material only. Zero fake. Leak chatter is a topic signal only, never a fact. No leaked or pre-release footage, no spoiler or isolated cutscene content.
- **Sell the method, not the material.** This skill contains techniques, commands, checklists, hook and retention rules, ffmpeg and workflow steps, caption and pacing rules, and the owner's own original text. It contains no Rockstar footage, trailer files, logo files, game music, screenshots used as assets, or leaked material.
- **Monetisation is tolerated, not licensed.** Rockstar's policy on posting copyrighted Rockstar material says Take-Two generally does not object to fans using materials for non-commercial uses in a manner which does not intentionally spoil the plot for others. "Non-commercial" means you do not make money through the game footage you post, and you do not use the material as part of a promotion for a product or service. Take-Two reserves the right to have its copyrighted material taken down at any time. The policy is written for occasional, non-commercial in-game content use by individual members of the fan community. Monetised GTA gameplay videos are common in practice, but that practice is tolerated, not licensed, and Take-Two can request removal at any time. Do not write that Rockstar "allows monetised GTA videos". Licensing requests go to copyright@take2games.com.
- **Disclaimer:** This skill is unofficial and independent. It is not affiliated with, endorsed by, or sponsored by Rockstar Games or Take-Two Interactive.
- **Honesty rules:** never state views, earnings, or subscriber counts as verified facts unless read from the platform itself; never write testimonials; never claim the method is the only one or the first of its kind; label evidence CONFIRMED, REPORT, or RUMOUR as the ledger does; never present an expected score as a measured score; never present a pre-fix verdict as the shipped file's score.

## Known limits / unresolved

- Saturation: M10 says 1.05; the v3/Remotion-era recipe says 1.00. This skill uses 1.00 for the Remotion-era recipe and records the difference; no source explains the change.
- Cut pace: the owner rule says about 1 shot per sentence and about 3s or more per shot; the v3 recipe caps static holds at 2.0s, and V2 still holds averaged about 1.9s. Cut on information beats governs; the two numbers are not reconciled in the sources.
- No /100 rubric breakdown is documented; do not invent one.
- Joker upload-checklist adaptation: no product links per the B8 ban; the Joker description template and category are not stated anywhere in the sources beyond the trio's practice (title, description, tags, custom thumbnails, English, Not made for kids, AI disclosure YES, no playlist, no product links).
- V3 score provenance: 97/100 + 57/60 per RUN-NOTES.md only; there is no standalone red-team report file for V3.
- V1 working artifacts missing from disk: the Remotion project, graded video, render-lossless file, STT and VO reports, QC and red-team frames, and audio-fix candidates referenced by V1's reports are not in `v1-macca-friends/work/` (only the thumbnail is present). The V1 verdict stands on the hashes, framemd5s, and measurements recorded in its reports.
- V2 duration is 45.9s per ffprobe and red-team; a parent verification line says 46.0s (treated as rounding). V3 duration is 40.8s per 1224f at 30fps; a parent verification line says 40.99s (unexplained, 0.19s difference); re-measure the delivered file rather than picking one.
- V1 delivered-file sha256 differs between REDTEAM.md (`8bd80874...`) and the parent verification (`b1607783...`) because the parent applied a lossless colour-tag remux after red-team; decoded frames verified identical (framemd5 unchanged). The shipped file hash is `b16077837eb8f50dcfe1b177e994a0c28acd6f1cafbe2b7dc2db3dfbc7373114`.
- No literal Nov 15 loudnorm commands, grade filter graph, M36 full re-encode command, Remotion render command, or V1 colour remux command exist in the sources; the five templates above are the honest substitute.
- No documented caption font and size canonical lock: V2 uses 88px Anton plus gradient rail, bottom 150; v3 uses 96px, bottom 168. No source states which is canonical.
- Bed ducking versus VO-only is conditional, not absolute: the brief allows VO-only if silencedetect proves no dead gaps, but V2 chose VO-only and was docked MINOR-1 for it.
- "Premium" 85/100 (M15) versus release gate at least 90/100: the relationship between the two bars is not stated.
- "SEO after public" versus pre-written SEO packs: whether "applied" means Studio application timing (and pack-writing timing is free) is not stated in the sources.
- No documented thumbnail text-size rule: V2's two-line 150px hook is the sizing evidence on record.
- Countdowns are date-bound: every countdown in the examples was true only for the Nov 15 air date. Treat countdowns as M30-derived values, never as reusable copy.
- The reference matrix used for competitor study is metadata-only: no video was watched in playback, no audio heard, no frames sampled. Do not present it as frame-level craft evidence.
