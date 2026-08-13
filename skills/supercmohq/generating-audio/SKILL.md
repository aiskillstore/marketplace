---
name: generating-audio
description: ALWAYS read this skill before generating spoken audio or calling audio_generate — a voiceover, narration, an ad read, a character line, or any script read aloud. Turns a script into speech — picks the model and voice, prepares the text for reading, and splits a long script into clips. Use whenever the user asks for text-to-speech, a voiceover, narration, or to have something read or spoken aloud.
license: Apache-2.0
metadata:
  version: "0.1.0"
  category: creative
  summary: "Converts scripts into audio. Lets you preview voice candidates from top models before generating. It then formats your script's numbers, dates, and URLs so the chosen AI model pronounces them accurately."
---

# Audio Generation

Turn a script into spoken audio via the `audio_generate` tool. Two decisions drive quality: **which
voice** reads it, and **how the script is written for the ear**.

**Scope.** Speech — a voice reading written words, delivered as its own audio file. Nothing here makes
non-speech sound, alters audio that already exists, or combines two tracks into one.

Lip-synced dialogue spoken by a character *inside* a video clip belongs to `generating-videos`.

## Workflow

### Step 1: Settle the script

Generate only from the exact words that will be spoken.

- **Supplied** → use them verbatim.
- **Enough to write them** — the product, audience, platform, and length are known → draft the script
  and show it before generating.
- **Not enough** → ask. Never invent a tagline, product claim, or brand name to fill the gap.

**Write to a duration.** Speech runs about two to three words a second, so a fifteen-second read is
thirty to forty-five words. Set the word count before writing, and trim words rather than speeding up
the delivery.

### Step 2: Pick the model

**`eleven-v3` is the default** — the most expressive read, and right for anything heard as a
performance. Reach for another only on a clear signal:

| Reach for another model when the script… | Model |
| --- | --- |
| Is a long, even read — an explainer, documentary narration, an audiobook chapter — where the voice must not drift | `eleven-multilingual-v2` |
| Is high-volume, a throwaway draft, or cost-sensitive, and expressiveness doesn't matter | `eleven-flash-v2.5` |

When the user names a model, use it. Per-request character limits differ sharply between models, and
an over-limit script is rejected rather than truncated — `list_audio_models` carries each ceiling.

### Step 3: Pick the voice

Call `list_voices`, filtered by what the brief demands — `gender`, `accent`, `age`, `use_case`,
`language`, or free-text `search`. Each row carries a `preview_url`. 
**There is no default voice**: every request needs a `voice_id` chosen here, passed as `voice`. 
Display names are not accepted.

- A stated **gender, accent, or age is a hard filter** — apply it, don't trade it away on tone.
  Read the attribute back from the row's own fields; **never infer it from the voice's name**. 
- **Let the user hear the options.** Unless they named a voice, offer two or three candidates with
  their `preview_url`s and let them pick.
- **Choose on tone**: what is the listener doing (half-watching a social clip wants attack and
  momentum; following an explainer wants a voice that stays out of the way), and whose voice is it
  meant to be (a brand narrator should stay neutral enough to reuse; a character should match the
  age and register of the writing).
- **Non-English script** → check the row's `language`, and that the model of Step 2 covers it.
- A `voice_id` the user pastes themselves is taken as given.
- Reuse the chosen `voice_id` for every clip in the job.
- **Nothing matched** → a normal result, not a dead end. Drop the narrowest facet — `use_case`
  first, then `age` — and search again. Only when gender and accent alone come back empty is the
  account genuinely short of voices; then relay the tool's hint verbatim, since the cause and the fix
  differ by provider and by whose key is in use.

### Step 4: Prepare the text

`text` is read out word for word, so write it the way it should sound.

- **Strip anything unspoken** — stage directions, speaker labels, bracketed cues, markdown.
- **Spell out** numbers, dates, currency, acronyms, and URLs as a person would say them.
- **Punctuate for pacing** — commas and full stops become pauses, and are the main lever on rhythm.

Direct the delivery with `stability` and `style` (`references/directing-the-read.md`), never with instructions
written into the text.

### Step 5: Generate

Speech comes **only** from `audio_generate`. If it errors, or no voice fits, say so and stop — never
substitute another text-to-speech tool the host happens to expose. A different engine means a
different voice, no access to the account's voices, and output outside the media directory.

Call `audio_generate` with a `requests` list — one object per clip, up to ten per call.

- Per object: `text` and `voice` (both required — the `voice_id` from Step 3); `model` only when
  Step 2 chose a non-default; `speed`, `stability`, `style`, `similarity_boost`, `format` as needed.
- **Split only where the audio will actually be cut** — per scene, or per section placed separately.
  Objects generate independently, so a continuous read split across two of them seams audibly.
- **Hold one `voice` and `model` across every object**, for the same reason. In a dialogue, one voice
  per character, consistent across that character's lines.
- **Repeat a line to get alternate takes** — different voices when the choice is unclear, or the same
  voice twice at low `stability`. Worth it on one short line, not a whole script.

### Step 6: Return

Share the audio file path(s). When the script was split, label each with the section it covers.

## Edge cases

- **Something other than speech is asked for** (music, sound effects, ambience, re-voicing, dubbing,
  cloning a voice from a sample) → say so plainly rather than substituting something else. In
  particular, do not generate a clip through `generating-videos` to get music or effects out of its
  native audio: that bakes the sound into the picture, so it can never serve as a track the user
  mixes. An already-cloned voice still works by its `voice_id`, and another language works by
  translating the script and generating it fresh.
- **Tracks need mixing or timing** ("the voiceover under the music", "a swoosh on the logo") → deliver
  clean speech and let the user assemble it in their editor.
- **Part of the brief is speech and part isn't** → state the limits in one message up front, then
  deliver the speech. Never generate first and disclose the gaps after.
- **Script over the model's character limit** → split it at a natural break, or switch to a
  higher-ceiling model.
- **`error: "no_voices_available"`** → relay the hint; it distinguishes an empty account from a key
  lacking permission to read voices, and the fixes differ.
- **Part of a batch fails** → keep the takes that worked and resend only the failed lines.
- **The read itself came out wrong** (flat, erratic, mispronounced, stress on the wrong word) →
  `references/directing-the-read.md` diagnoses it symptom by symptom.
- **Safety rejection** → remove the sensitive wording and retry once.
- **Generic failure** → retry once as-is, then report the error.
- **`error: "no_provider_configured"`** → relay the tool's `hint` (the user must set their key).

## Reference

- `references/directing-the-read.md` — tuning the delivery with `stability`, `style`,
  `similarity_boost` and `speed`, and diagnosing a read that isn't working.
