# V2: New Zealand Plays GTA VI First. Here's Your Unlock Time

- **Video:** https://youtube.com/shorts/aF6RgIg_mHI
- **Slot:** Sunday, November 15, 2026, 19:00 PKT
- **Duration:** 45.9s (1377 frames at 30fps, 1080x1920). A parent verification line says "46.0s"; that is rounding, and 45.9s is the ffprobe and red-team value.
- **Scores:** 90/100 + 53/60 is the PRE-FIX verdict and a FAIL. MAJOR-1 (colour / pixel-format) blocked release even though the numeric bars were met. The shipped file is the MAJOR-fixed file, technically re-verified (loudness re-measured -15.62 / -1.87, luma shift at or below 0.1, fixed f1000 viewed identical). Expected post-fix score approx 94/100. That is an expectation, NOT a measured re-score. Never present 90/53 as the shipped score, and never present 94 as measured. Source: `v2-unlock-times/work/red-team-report.md`, about 02:00 PKT, and `RUN-NOTES.md`.
- **Title:** 55 characters, verbatim: "New Zealand Plays GTA VI First. Here's Your Unlock Time"

## Script (verbatim, corrected version)

ChatGPT follow-up 2, 2026-11-15 00:35 PKT. The original first return was 115 words and is superseded; never build from it. Count: 102 tokens / 104 spoken, PASS (90-105 gate).

> There is no single GTA VI launch moment; each country has a midnight. Rockstar Support confirms midnight local time November nineteenth, on PlayStation Five and Xbox Series X and S. The listings put New Zealand first: midnight NZDT Thursday, November nineteenth; eleven a.m. UTC Wednesday, November eighteenth. Mexico and Central America last: store listings show six a.m. UTC Thursday, nineteen hours later. Store listings show midnight Eastern, nine p.m. Pacific Wednesday, November eighteenth. Pre-loading leaves files locked until your unlock time. Your store account region—not location—determines it. Rockstar has announced no global unlock hour; store times can change. Four days to launch.

## Description (verbatim)

> There is no single GTA VI launch moment — your country has its own midnight. Rockstar Support confirms GTA VI unlocks at midnight local time on November nineteenth in every region, on both consoles. The store listings show New Zealand unlocks first at midnight NZDT on Thursday, November nineteenth — eleven a.m. UTC on Wednesday, November eighteenth. Mexico and Central America unlock last at six a.m. UTC on Thursday, November nineteenth, about nineteen hours after New Zealand. The store listings show the United States unlocks at midnight Eastern, which is nine p.m. Pacific on Wednesday, November eighteenth, because the stores keep one time per country. Pre-loading does not unlock the game early. Pre-loaded files stay locked until your region's unlock time. Your unlock follows your store account region, not where you are. Rockstar has not announced one single global unlock hour. The per-country times come from store listings and can change. Sources: Rockstar Support — regional pre-load and release times; PlayStation Blog — rolling midnight launch; PlayStation and Xbox store listings (Nov 14, 2026). Four days to launch.

## Tags (12, verbatim order)

1. GTA VI unlock time
2. GTA VI release time
3. GTA VI New Zealand
4. GTA VI midnight launch
5. Grand Theft Auto VI
6. GTA 6
7. GTA VI launch
8. GTA VI November 19
9. GTA VI PS5
10. GTA VI Xbox
11. GTA VI countdown
12. Joker Gaming

## Shot-plan summary

| Item | Detail |
|---|---|
| Segments | 20: 16 still windows (max 68f) plus 1 motion span plus 4 cards |
| Motion span | Launch Trailer 12.0-14.1 (63f, phone call; head/mid/tail viewed full-res, one continuous take, active rows 120..2039; crop 1080x1920 @1700:120) |
| Cards | C1 "MIDNIGHT LOCAL TIME" (78f, navy/cyan); C2a "NEW ZEALAND FIRST" (191f, green/teal, row 2 staggers in at card frame about 81 with the spoken "eleven a.m. UTC"); C2b "MEXICO LAST" (146f, plum/amber, "ABOUT NINETEEN HOURS LATER" at headline size, M34); C3 "FOUR DAYS TO LAUNCH." (79f). Cards are 36% of the video |
| Captions | 20 phrases, 88px Anton plus gradient rail, bottom 150 (A/B recipe); no captions during card windows |
| VO | 9 stems, 41.61s speech, 102 words; concat 44.41s = 1332f; 8 gaps of 0.35s |
| Hero | Vice_City_11 (true dusk/night skyline; suggested window x=1312; also the thumbnail base) |
| Mix | VO-only (see minors: MINOR-1). No tail chime |
| Grade | Grade chain NOT executed (v3-as-executed also skipped it) |
| Credit | "Footage: Rockstar Games" present at f000/f100 |

## Thumbnail

- Cover text: "NEW ZEALAND FIRST" (two lines, 150px: the 18-char single line would not fit at v3's 168px within safe margins)
- File: `thumbnail-v2.png` (1080x1920, Remotion still, real GTA VI logo, clean solid Anton hook)
- Base frame: Vice_City_11 (dusk skyline, ferris wheel)
- Real logo verified: `remotion-v2/public/logo.png` hashes to sha256 `18ad6092...`, identical to the verified gradient logo file (md5 `116fe9fe...`)
- In-world "MEGAMUNDO" building sign cut at the left edge: official-frame signage, not a defect

## Loudness result

Single-pass I=-15.5, TP=-2.0, LRA=11, measured on the delivered file: I=-15.62 LUFS (band -16 to -14, pass), TP=-1.87 dBTP (at or below -1.0, pass), LRA=2.00. Independently re-measured by red-team with identical values.

## MAJOR-1 (fixed, release-blocking)

The delivered file was yuvj420p / pc (full) / bt470bg / transfer plus primaries unknown, against the required yuv420p plus bt709 x4 plus tv. The Remotion render itself produces yuvj420p despite `--pixel-format=yuv420p`. Fix: re-encode from the raw render with `scale=in_range=pc:out_range=tv` plus `setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709` plus CRF 18, loudnorm re-applied in the same pass. A first attempt with output-level `-color_trc` / `-color_primaries` flags did NOT stick. Final file: yuv420p, tv, bt709 space, bt709 transfer, bt709 primaries, all four bt709 fields. This is the origin of M36. Final file sha256: `816b06768fdd3d8a1b21a97bf8be6d154214e7f2303b98e6c37cf60900f98030` (21,188,200 B). Pre-fix file sha256: `a10371d7d2d7521c061d02d86a68ad0cbb8a70c0fc6253fe292cd650eb0c43c5` (26,322,390 B).

## Red-team minors (6, no change)

1. MINOR-1: silent gaps plus 1.3s silent tail under C3 (accepted by design: 0.35s gaps are the A/B stem recipe; end hold is standard end-card read time). Note: the VO-only mix was still docked here under M4.
2. MINOR-2: cards open on black field about 4 frames (v3 precedent, spring-stagger entry)
3. MINOR-3: VO s04 "nineteen hours later" without "about" (qualifier IS on screen at the moment the words are spoken, C2b, M34, and in the description; script parent-approved)
4. MINOR-4: "The United States" never named in VO or cards (script as approved; description names the US)
5. MINOR-5: motion head about 0.7s soft empty marina (wide establishing beat, per allocation note)
6. MINOR-6: thumbnail hook less dominant than the Nov 13 V1 bar, logo top margin about 30px, MEGAMUNDO sign clipped (same logo placement as v3's passing thumbnail; sign is in-world signage)

## The s06 "unlocked" note

Whisper hears "unlocked" reproducibly in s06, but fresh Kokoro control syntheses prove the artifact, and decisively the freshly synthesised sentence from "...until your unlock time." is sample-identical to the delivered `s06.wav` (max diff 0.0, 68,065 samples). The caption uses script spelling "unlock time." Saad's listen remains final.

## What to learn

- **M36:** a Remotion render outputs yuvj420p / full-range even with `--pixel-format=yuv420p`. Verify colour tags on the delivered file with ffprobe (M25); a render whose tags are unverified is UNVERIFIED, not passed. This video is the case that created M36.
- **M34:** C2b "ABOUT NINETEEN HOURS LATER" at headline size is the passing example of a qualifier carried on the card with the figure. Compare with V1, where the card dropped "ABOUT".
- **M4:** VO-only is allowed only if silencedetect proves no dead gaps. This VO-only mix still earned MINOR-1 for digital silence in every 0.35s gap plus a 1.3s silent tail. Prefer the bed mix unless the delivered file proves VO-only clean.
- **M26:** attribution roots are counted by occurrence, not by position. The script was checked for repeated attribution before VO, and the red-team STT timestamp check is the gating check.
- **M25:** red-team re-measures everything from the delivered file. The MAJOR-1 colour defect was caught by independent re-measurement, not by trusting the build report.
