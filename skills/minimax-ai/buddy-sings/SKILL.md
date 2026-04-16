---
name: buddy-sings
description: >
  Use when user wants their Claude Code pet (/buddy) to sing a song. Triggers on any
  request that combines the concept of their Claude Code buddy, pet, or companion with
  singing or music. Supports multilingual triggers — match equivalent phrases in any
  language.
license: MIT
metadata:
  version: "1.1"
  category: creative
---

# Buddy Sings — Let Your Claude Code Pet Sing

Turn your Claude Code pet into a singer. Each pet gets a unique vocal identity
based on its name and personality — the same pet always sounds the same.

## Prerequisites

- **mmx CLI** (required for music generation):

  **Install:**
  ```bash
  npm install -g mmx-cli
  ```

  **Authenticate (first time only):**
  ```bash
  mmx auth login --api-key <your-minimax-api-key>
  ```
  Get your API key from [MiniMax Platform](https://platform.minimaxi.com/).

- **Audio player** (for playback — at least one of):
  - `mpv` (recommended — interactive controls: space = pause, q = quit)
  - `ffplay` (from FFmpeg)
  - `afplay` (macOS built-in)

---

## Workflow Overview

```
Check pet → Build vocal identity → Gather context → Generate music → Play & feedback
```

---

## Language & Interaction

Detect the user's language from their first message. Respond in the same language
throughout the entire session. All examples below are in English — translate them
naturally when responding in other languages.

**User-facing text localization rule**:
- ALL text shown to the user — including pet info, voice description, lyrics preview,
  prompt preview, playback info, and feedback prompts — MUST be fully translated into
  the user's language.
- The **API prompt** sent to the model should always be written in English for best
  generation quality. However, when previewing the prompt to the user, show a localized
  description in the user's language instead of the raw English prompt. The English prompt
  is an internal implementation detail — the user does not need to see it.
- The templates below are written in English as reference. At runtime, translate every
  label and message into the user's detected language.

The pet sings in the user's language by default. Embed the singing language
naturally in the vocal description (e.g., "singing in Japanese" or "singing in
Mandarin Chinese") rather than appending a separate language tag. If the user
explicitly requests a different language for the lyrics, honor that request.

---

## Step 1: Check for Pet

Read `~/.claude.json` and look for the `companion` field.

If no companion is found or the field is empty, tell the user:

```
You don't have a pet yet! Type /buddy to adopt one, then come back to let it sing.
```

Stop here and wait for the user to adopt a pet. Do not proceed without a pet.

If a companion exists, extract its profile:
- `name` — the pet's name
- `personality` — the pet's personality description

Present the pet to the user:

```
Found your pet!
   Name: <name>
   Personality: <personality>
```

---

## Step 2: Build Vocal Identity

Based on the pet's **name** and **personality** text, creatively design a unique
vocal identity. No template lookups — interpret the personality freely.

### How to interpret personality into voice

Read the personality text and craft vocal attributes:

- **Timbre**: What does this personality sound like? e.g., "few words" →
  low, warm, deliberate; "energetic" → bright, punchy; "mysterious" → breathy,
  dark; "legendary chonk" → thick, warm, cozy
- **Singing style**: How would they deliver a song? e.g., "of few words" →
  sparse, dramatic pauses; "playful" → bouncy, rhythmic; "poetic" → flowing, legato
- **Mood**: What emotional tone fits? e.g., "chill" → relaxed, laid-back;
  "fierce" → intense, powerful

Construct a `prompt_fragment` that describes the vocal style in English, embedding
the singing language naturally. For example:

```
Vocal: warm low female voice singing in Mandarin Chinese with cozy thick timbre,
sparse minimalist delivery with dramatic pauses giving each word weight, relaxed
laid-back mood.
```

### Voice caching

The vocal identity must be **cached** so the pet always sounds the same.

- Cache file: `~/.claude/skills/buddy-sings/voices/<name>.json`
- Cache format:
  ```json
  {
    "name": "Moth",
    "personality": "A legendary chonk of few words.",
    "prompt_fragment": "Vocal: warm low female voice singing in Mandarin Chinese...",
    "cached_at": "2026-04-07T19:52:15"
  }
  ```

**First time**: No cache exists → interpret personality → save to cache file.

**Subsequent calls**: Read cache → use the saved `prompt_fragment` directly.
Do NOT re-interpret — consistency matters.

**Cache invalidation**: If the `personality` in `~/.claude.json` differs from what's
cached, the pet has changed — regenerate and save a new cache.

**Manual regeneration**: If the user says "change the voice" or "regenerate voice":
delete the cache file and re-interpret from scratch.

### Present the voice to the user

```
<name>'s unique voice:

Timbre: <timbre description>
Style: <style description>
Mood: <mood description>

Let's pick what <name> should sing about!
```

---

## Step 3: Understand Intent & Gather Context

**Do NOT always present a mode menu.** Instead, analyze the user's request to
determine what context is needed, and auto-gather it.

### Auto-context detection

When the user's request implies personal context, **automatically** scan for
relevant information without asking. Triggers include:

- **Time-based references**: "today", "this week", "recently", "yesterday" → scan
  current conversation history and memory files for what happened in that period
- **Personal references**: "my work", "my day", "what I did" → scan memory
  and conversation for the user's activities
- **Relationship references**: "our story", "what we did together" → scan memory for
  shared experiences between user and pet/Claude

### Context gathering (auto, not mode-gated)

When context is needed, scan these sources in order:

1. **Current conversation context**: Look at what the user has been doing in
   this Claude Code session — files edited, commands run, topics discussed.
   This is the richest source for "today" type requests.

2. **Memory files**: Scan for relevant memories:
   ```bash
   find ~/.claude/projects/*/memory/ -name "*.md" 2>/dev/null | head -20
   ```
   Also check `~/.claude/memory/` if it exists.
   Read found files and extract themes relevant to the user's request.

3. **Git history** (if in a repo): For work-related songs, check recent commits:
   ```bash
   git log --oneline --since="today" 2>/dev/null | head -10
   ```

Use gathered context to enrich the lyrics prompt — make the song personal and
specific to what actually happened, not generic.

### When NO context is needed

If the user's request is a clear standalone scene (e.g., "sing a rainy day song",
"sing a lullaby"), skip context gathering and proceed directly to music generation.

### When context is ambiguous

Only ask for clarification when you genuinely can't determine what the user wants.
Don't present a mode menu — ask a specific question:

```
What should <name> sing about?

For example:
  - "Today's work" — I'll check what you've been up to
  - "My pet waiting by the window for me to come home"
  - Or let me pick a random theme?
```

### Fallback to random

If context gathering finds nothing useful (no memory files, no conversation
history, no git log), fall back to random theme generation based on the pet's
personality:
- Quiet/reserved personality → midnight lullaby, gentle sunset, quiet morning
- Energetic personality → party jam, adventure song, victory march
- Mysterious personality → moonlit serenade, secret whisper, dream journey

Tell the user what theme was picked.

---

## Step 4: Generate Music

Combine the vocal identity with the chosen theme.

1. **Construct the full prompt**: The prompt has two parts that MUST both be present:

   **Part A — Vocal identity (MUST come first)**: Always start the prompt with the
   cached `prompt_fragment`. This is the most important part — it defines who is
   singing. Place it at the beginning of the prompt so the API prioritizes it.

   **Part B — Genre/style/mood tags**: Choose tags that **match the theme**, NOT
   a default set. Vary the genre deliberately based on what the song is about.

   Write prompts as **vivid English sentences**, not comma-separated tags.
   Follow this pattern: `A [mood] [genre] song, featuring [vocal description],
   about [narrative/theme], [atmosphere], [key instruments and production].`
   Describe vocals as a character ("sultry baritone with jazz inflections"),
   not just a gender. Include a scene or vibe to anchor the generation.

   **Genre matching guidelines** — pick a genre that fits the theme's energy:

   | Theme energy | Suggested genres | Avoid |
   |-------------|-----------------|-------|
   | Encouragement / motivation / cheer | Indie rock, synth-pop, funk, rap | Indie folk, healing |
   | Daily life / warmth / companionship | Mandopop, city pop, bossa nova | Same as last time |
   | Missing someone / waiting | Folk, R&B, lo-fi | Rock, EDM |
   | Humor / roasting / complaining | Funk, rap, ska, electro-pop | Classical, ballad |
   | Late night / quiet | Ambient, piano piece, lo-fi, neoclassical | Upbeat, EDM |
   | Celebration / achievement | EDM, future bass, funk, K-pop | Slow tempo, melancholy |
   | Work routine | City pop, synth-pop, lo-fi hip-hop, indie rock | Same genre every time |

   **Anti-monotony rule**: NEVER use the same genre combination twice in a row.
   Before constructing the prompt, recall what genre was used in the previous
   generation (if any in this session) and pick something different.

   **Prompt structure** — write as vivid English sentences, not comma-separated tags:
   ```
   <vocal prompt_fragment>. A <genre> song with <mood> mood, featuring <instruments>,
   at a <tempo> tempo, evoking <scene>.
   ```

   **Diverse examples**:
   ```
   # Encouragement for the workday
   A deep warm androgynous voice with cozy delivery. An energetic synth-pop track
   with a fiery, uplifting mood, driven by pulsing synthesizers and electronic drums
   at a fast tempo, capturing the rush of a morning commute.

   # Waiting for the owner to come home
   A deep warm androgynous voice with cozy delivery. A warm city pop song with sweet,
   tender feelings, featuring electric piano and groovy bass at a mid-tempo pace,
   set on a sunny afternoon windowsill waiting for someone to come home.

   # Complaining about overtime
   A deep warm androgynous voice with cozy delivery. A playful funk track with a
   humorous, laid-back vibe, featuring slap bass and brass at a groovy mid-tempo,
   capturing the absurdity of working late in a dim office.

   # Late-night companionship
   A deep warm androgynous voice with cozy delivery. A calm lo-fi hip-hop piece with
   a healing, dreamy atmosphere, featuring sampled piano and soft electronic drums
   at a slow tempo, evoking a quiet late-night desk with warm lamp light.
   ```

2. **Generate lyrics**: Use `--lyrics-optimizer` to auto-generate lyrics, or write lyrics
   yourself when you need to control the perspective.

   **Important — perspective & personality-driven lyrics**:

   The pet is the singer, so lyrics MUST be written from the **pet's first-person
   perspective** ("I" = the pet, "you" = the owner/user). The pet is singing TO
   the owner. For example:
   - "I sit by the door waiting for you to come home" (pet's perspective)
   - "Wake up now, my dear human" (pet singing to owner)
   - NOT "I rub my sleepy eyes" (owner's perspective — wrong)
   - NOT "Then you woke up, my little Moth" (owner talking about pet — wrong)

   The pet's personality should shape the lyrics' tone and word choice:
   - "of few words" → short, impactful lines, minimal filler
   - "playful" → rhyming, bouncy phrasing, fun wordplay
   - "poetic" → metaphor-rich, flowing imagery
   - "fierce" → direct, powerful declarations

   The pet's name may appear in the lyrics (e.g., in a chorus hook) but the
   narrative voice is always the pet speaking/singing.

   **When perspective matters**: Write the lyrics yourself and pass via `--lyrics`.
   **When perspective is not critical**: Use `--lyrics-optimizer` for convenience.

3. **Preview (MUST show full content)**: Before generating, show the user the
   **complete lyrics** and **full prompt** — no abbreviation, no `...`, no summary.
   This is part of the fun — the user wants to read and enjoy the lyrics before
   hearing them sung.

   The API prompt is always constructed in English (for best generation quality).
   When responding in a non-English language, show a **localized description** of
   the prompt in the user's language for readability. The English prompt is an
   internal implementation detail — do not show it to the user. Translate all
   labels (Singer, Theme, Description, Confirm, etc.) into the user's language.

   Template (English reference — localize all labels at runtime):

   ```
   About to generate:
   Singer: <name>
   Theme: <theme>

   Lyrics:
   [verse]
   <full verse lyrics here>

   [chorus]
   <full chorus lyrics here>

   ... (show ALL sections in full)

   Description: <localized description of the song style and mood>

   Confirm? (press enter to confirm, or tell me what to change)
   ```

   **Never truncate or abbreviate** the lyrics or prompt in the preview.
   The user should see exactly what will be sent to the API.

4. **Call music generation**:

   **With auto-generated lyrics (perspective not critical):**
   ```bash
   mmx music generate \
     --prompt "<full combined prompt>" \
     --lyrics-optimizer \
     --out ~/Music/minimax-gen/<name>_sings_<YYYYMMDD_HHMMSS>.mp3 \
     --quiet --non-interactive
   ```

   **With self-written lyrics (perspective-controlled):**
   ```bash
   mmx music generate \
     --prompt "<full combined prompt>" \
     --lyrics "<lyrics with correct pet perspective>" \
     --out ~/Music/minimax-gen/<name>_sings_<YYYYMMDD_HHMMSS>.mp3 \
     --quiet --non-interactive
   ```

---

## Step 5: Play & Feedback

### Cross-platform playback

Detect the available audio player and play the generated file:

```bash
if command -v mpv >/dev/null 2>&1; then
  mpv --no-video ~/Music/minimax-gen/<filename>.mp3
elif command -v ffplay >/dev/null 2>&1; then
  ffplay -nodisp -autoexit ~/Music/minimax-gen/<filename>.mp3
elif command -v afplay >/dev/null 2>&1; then
  afplay ~/Music/minimax-gen/<filename>.mp3
else
  echo "No audio player found. Your song is saved at: ~/Music/minimax-gen/<filename>.mp3"
fi
```

After starting playback, tell the user the file is playing and where it's saved.
Do NOT show playback controls (e.g. keyboard shortcuts) — they don't work in this
environment since the player runs in the background.

If no player is found, show the file path and suggest installing mpv.

### Feedback

After playback, ask for feedback (localize all text):

```
How was <name>'s performance?

1. Amazing! Keep it!
2. Try a different theme / style
3. Fine-tune the lyrics and regenerate
4. Try another random one
```

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| No `~/.claude.json` | Tell user to run `/buddy` first |
| Companion field is empty | Same — guide to `/buddy` |
| mmx CLI not installed | Print: "You need to install mmx CLI: `npm install -g mmx-cli && mmx auth login`" |
| No audio player found | Show file path and suggest installing mpv |
| No memory files found | Suggest a custom theme or random mode |
| User wants to change the pet's voice | Delete cache, re-interpret personality |
| User wants a specific genre | Let them override — append their genre to the prompt |

---

## Notes

- The vocal identity is based on **name + personality** only. No species/rarity
  template mapping.
- Voice is cached and consistent across sessions. Same pet = same voice.
- Lyrics should always be **original** — never reproduce copyrighted lyrics.
- The pet's personality shapes both the **voice** (how they sound) and the
  **lyrics** (what they say and how they say it).
- All generated files go to `~/Music/minimax-gen/` with the pet name in the
  filename.
