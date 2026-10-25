# Recording brief

The page the recorder reads before shooting. It ships with the script; the script is not finished without it.

- [Starting states](#starting-states)
- [Machine hygiene](#machine-hygiene)
- [Music](#music)
- [AI voiceover](#ai-voiceover)
- [Off-limits list](#off-limits-list)
- [Take plan](#take-plan)
- [After the shoot](#after-the-shoot)
- [Description and CTA](#description-and-cta)
- [Captions and translations](#captions-and-translations)
- [Publication checks](#publication-checks)

## Starting states

One row per beat, copied from the script's Starting state column and made executable.

| Beat | Enter this state with                               | Verified |
| ---- | --------------------------------------------------- | -------- |
| 1    | `git checkout v2.3.0 && ./scripts/seed.sh && clear` | yes      |
| 5    | `git checkout step-2 && code handler.ts:12`         | yes      |

Every state must be reachable by one command from a cold machine, and rehearsed from a machine that has _not_ already run the demo - that is where hidden caches, warm containers and leftover env vars hide. A beat whose state cannot be re-entered forces a full re-shoot when take 4 fails.

## Machine hygiene

- Notifications, calendar alerts, chat badges: off at the OS level, not minimized.
- A recording profile for the browser and the editor: no personal bookmarks, no autofill history, no unrelated tabs, no signed-in personal accounts.
- Terminal 24pt or larger, editor 20pt or larger, high-contrast theme, window sized to 16:9.
- Shell prompt shortened; no directory paths containing customer or employer names.
- Secrets: use throwaway keys that will be rotated after recording. Assume every frame is a screenshot someone keeps.
- Everything slow happens before recording: installs, builds, image pulls, index builds, account verification.

## Music

- Take every track from an open-source or Creative Commons-licensed music library, and read that track's license: some variants forbid commercial use or derivatives, and a product video is commercial.
- Never use commercial or copyrighted music without written clearance: a rights claim can mute or block the video long after it ships.
- Cut music to the beats the script flags with a music cue or transition, and keep it under the narration, never competing with it.
- An AI music generator is a third option alongside a licensed library or a composer: check its output license before using the track commercially, since generated-music terms vary by tool and by plan.

## AI voiceover

Applies only when the interview answer to voiceover is AI-synthesized, not a human recorder.

- Generate the opening beat through 2-3 candidate voices before the full narration pass, and pick by ear. A synthesis engine's default voice rarely fits the video's tone.
- Favor a plain, confident, conversational reading over an expressive or performative one. A technical viewer trusts a steady presenter, not a narrator selling something.
- Tune the delivery, not just the voice: a setting that maximizes consistency reads flat and robotic, one that maximizes expressiveness can drift staged or uneven - dial between the two by ear, not by default.
- Prefer a model built for narration and long-form consistency over one optimized for real-time latency. A pre-rendered voiceover has no latency constraint to trade naturalness against.
- Check the voice's commercial-use license before publishing, same as any licensed asset (see Music above).

Optional integration note: ElevenLabs' `eleven_multilingual_v2` model is a common narration-grade choice, tuned via `stability`, `similarity_boost` and `style` - moderate stability and a low style value read closest to a steady presenter.

## Off-limits list

Copy the script's `Off-limits` header line here and make it concrete per surface:

- Customer names
- Tenant IDs
- Internal hostnames
- Unreleased features
- Pricing
- Ticket numbers
- Colleague avatars in a chat sidebar

For a B2B or enterprise audience this is not politeness - a recording is forwardable and durable, and it will be replayed in a security or procurement review long after the release it described.

## Take plan

- Record segment by segment, not in one pass. Segment boundaries are the natural cut points and the re-shoot unit.
- Between takes, re-enter the beat's starting state rather than continuing from wherever the failed take left the machine.
- Mark a fluffed take out loud ("cut, again from beat 6") so the edit finds it without scrubbing.
- Audio quality outranks video quality: a viewer forgives a soft image and leaves over a hissy room.
- Record 3-5 seconds of room tone once - the edit needs it to patch gaps.

## After the shoot

The script already contains everything below; this list exists so nothing gets re-derived from the video.

| Artefact            | Source in the script                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| Chapter list        | Segment titles + final timecodes (first `00:00`, three or more, each ≥10s, ascending)          |
| Description         | Opening beat's problem statement, promise, prerequisites, chapters, links, one CTA - see below |
| Captions            | Auto-generate, then correct against the narration column - never re-transcribe. For another language, see below |
| Caption fix list    | The identifiers, flags and package names flagged in the metadata block                         |
| Short-form clips    | Beats marked clip-able                                                                         |
| Link overlays       | Same one CTA as the description - see below                                                    |
| Companion page      | Beats in order, rewritten as a how-to                                                          |
| Claims to re-verify | Version numbers, benchmark figures, pricing statements                                         |

## Description and CTA

```text
<hook: the opening beat's problem statement, in the viewer's words>
<promise: one line, what the viewer has working or decided by the end>

Prerequisites: <versions, accounts, prior knowledge>

Chapters:
00:00 <task-shaped title>
<mm:ss> <next title>

Links:
- <every link named in the narration, in the order it is named>

Music: <track, author, license, credited exactly as the license asks>

<one call to action: the next step, with its link>
```

- Put the hook first. The platform shows only the opening lines above the "more" fold, and the problem statement is what the searching viewer recognizes.
- Take the call to action from the destination the interview already set: try the product, read the docs, star the repository. State it as one plain instruction.
- Keep exactly one primary call to action. Other links sit in the Links list as references, never phrased as asks, so the next step stays unambiguous.
- Point any on-screen link overlay at the same one CTA, timed to a beat where the narration has already earned it - not the opening beat. A second, different destination splits a decision the description already resolved.
- Reuse the chapter list from the row above verbatim. A second, edited copy drifts from the video's real timecodes.
- For a short-form clip, drop the chapters block entirely. Most short-form surfaces truncate or hide the description behind a tap, and few viewers read it before swiping on - keep the description to the hook line and the call to action, nothing else survives the fold.

## Captions and translations

Correct the primary-language captions against the narration column first, the same pass already described above - the script already fixed every deictic sentence and every pronunciation, so this pass is verification, not authoring.

Pick target languages from the channel's own viewer-language breakdown (the video platform and the docs site both report one), never from a generic list of world languages - a devtools audience skews toward whichever languages its actual developer base reads, which a global ranking does not predict.

To add another language, translate the corrected transcript, never the raw audio and never the source material. Machine-translate a first pass, then have a fluent or native speaker in that language check every identifier, flag and package name - translation engines mangle these the same way a raw auto-caption does, just in a language nobody else on the team can catch by ear. Upload each language as its own caption track; never rely on a platform's live auto-translate, which the viewer cannot correct and the team cannot review before it ships.

## Publication checks

1. Captions present and corrected - required for prerecorded audio under WCAG Level A, and the only way most viewers read technical terms.
2. Chapter list satisfies the platform's minimums.
3. Every link named in narration is actually in the description.
4. The video plays intelligibly with the screen off (the audio-only pass, re-run on the real recording).
5. Code on screen is readable at phone size.
6. No off-limits item appears in any frame - scrub at 4x with the off-limits list open.
7. The description opens with the problem statement above the fold and carries exactly one primary call to action.
8. Every published caption language is a reviewed translation of the corrected transcript, not a raw machine translation of the audio or an unreviewed auto-translated track.
