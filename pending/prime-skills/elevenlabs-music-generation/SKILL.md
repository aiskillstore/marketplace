---
name: elevenlabs-music-generation
displayName: "ElevenLabs AI Music Generation — Pro Pack on RunComfy"
allowed-tools: Bash(runcomfy *)
description: >
  Generate full songs and instrumental tracks with ElevenLabs Music on
  RunComfy via the `runcomfy` CLI. ElevenLabs Music turns a style
  description plus structured lyrics into studio-quality 44.1 kHz
  stereo audio — 5 seconds to 5 minutes — with section-level control
  (Intro / Verse / Chorus / Bridge), multilingual vocals, and
  commercial-friendly output. Generate a backing track, a full vocal
  song, a jingle, a podcast intro, a game loop, or an instrumental
  bed. Calls `runcomfy run elevenlabs/elevenlabs/music-generation`
  through the local RunComfy CLI. Triggers on "generate music",
  "make a song", "AI music", "background music", "instrumental
  track", "ElevenLabs Music", "soundtrack", "jingle", "theme music",
  "royalty-free music", "compose", or any explicit ask to generate
  music or a song from a text description.
homepage: https://www.runcomfy.com
license: MIT
---

# ElevenLabs AI Music Generation — Pro Pack on RunComfy

Generate full songs and instrumental tracks from a text description — studio-quality 44.1 kHz stereo, 5 seconds to 5 minutes, with section-level structure control. ElevenLabs Music on the **RunComfy Model API**, called through the `runcomfy` CLI.

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) · [ElevenLabs Music model](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) · [CLI docs](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation)

## Install this skill

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill elevenlabs-music-generation -g
```

## Powered by the RunComfy CLI

```bash
# 1. Install (one of — see runcomfy-cli skill for details)
npm i -g @runcomfy/cli                              # global install
npx -y @runcomfy/cli --version                      # zero-install

# 2. Sign in
runcomfy login                                      # or in CI: export RUNCOMFY_TOKEN=<token>

# 3. Generate music
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{"prompt": "..."}' \
  --output-dir ./out
```

CLI deep dive: [`runcomfy-cli`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/runcomfy-cli) skill.

## When to use ElevenLabs Music

ElevenLabs Music's strength is **structured songs with real vocals** — it takes a style brief plus lyrics with section markers and returns a coherent, mixed track. Pick it for:

- **Full vocal songs** — verse/chorus structure, multilingual lyrics, consistent meter
- **Instrumental beds** — `force_instrumental: true` for background music, podcast intros, game loops
- **Short brand assets** — jingles, stingers, theme music (5–30 s)
- **Long-form tracks** — up to 5 minutes in a single call
- **Commercial work** — output is commercial-friendly

If the user just wants ambient sound or a one-off SFX (thunder, footsteps), that's a sound-effects task, not music — ElevenLabs Music is for *songs and tracks*.

## Endpoint + input schema

**Model**: `elevenlabs/elevenlabs/music-generation`

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `prompt` | string | yes | — | Style description **and** lyrics with section markers. See prompting tips |
| `music_length_ms` | int | no | `40000` | Output duration in ms. **5000–300000** (5 s – 5 min) |
| `force_instrumental` | bool | no | `false` | `true` = instrumental only, no vocals |
| `output_format` | string | no | `mp3_standard` | `mp3_standard` (default), or WAV — see the [model page](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) API tab for the full format list |

Output: 44.1 kHz stereo audio. The result JSON contains the generated audio URL — the CLI downloads it into `--output-dir`.

**Pricing**: ~$0.0083 per second of generated audio (30 s ≈ $0.25, 60 s ≈ $0.50, 5 min ≈ $2.49). Cost scales with `music_length_ms`, so draft short and finalize long.

## How to invoke

**Full vocal song with structure:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "Upbeat indie-pop anthem, bright electric guitars, driving drums, 120 BPM, female lead vocal. [Intro 8 bars] instrumental build. [Verse] Chalk on the palms, laces double-knotted, morning on the ridge. [Chorus] We rise, we strike, we never fade out. [Bridge] soft breakdown, just piano and voice. [Outro] full band, fade.",
    "music_length_ms": 60000
  }' \
  --output-dir ./out
```

**Instrumental background bed:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "Calm lo-fi hip-hop instrumental for a study playlist. Warm Rhodes piano, soft vinyl crackle, mellow boom-bap drums, 75 BPM. No vocals. Consistent loop-friendly groove throughout.",
    "music_length_ms": 90000,
    "force_instrumental": true
  }' \
  --output-dir ./out
```

**Short brand jingle:**

```bash
runcomfy run elevenlabs/elevenlabs/music-generation \
  --input '{
    "prompt": "5-second cheerful brand stinger, bright marimba and a single uplifting chord resolve, no vocals.",
    "music_length_ms": 5000,
    "force_instrumental": true
  }' \
  --output-dir ./out
```

## Prompting tips

ElevenLabs Music reads **one `prompt` field** that carries both the style brief and the lyrics. Structure it well:

- **Lead with the style brief**: genre, mood, tempo (BPM), key instruments, vocal type. `"Upbeat indie-pop anthem, bright electric guitars, 120 BPM, female lead vocal."`
- **Then the lyrics with section markers**: `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`. Add approximate durations or bar counts — `[Intro 8 bars]`, `[Verse 16 bars]`.
- **Keep lyrical meter consistent** — even syllable counts per line, clear rhyme scheme. The model follows meter; sloppy meter produces awkward phrasing.
- **Name lead instruments and mix priorities** — `"electric guitar carries the chorus, drums sit back in the verse."`
- **For instrumental**, set `force_instrumental: true` AND say "no vocals" in the prompt — belt and suspenders.
- **Multilingual**: write the lyrics in the target language; annotate accent/language inline if needed (`[Verse] (sung in Brazilian Portuguese) ...`).
- **Avoid contradictory style instructions** — "aggressive metal" + "soft lullaby" in one prompt confuses the model. One coherent direction per call.
- **Draft short, finalize long**: validate the direction with a 30–45 s draft (`music_length_ms: 35000`) before paying for a 5-minute render.

## Common patterns

### Theme song for a video
- Full brief + lyrics + `[Intro]/[Verse]/[Chorus]` structure, `music_length_ms` matched to the video length

### Podcast intro / outro
- `force_instrumental: true`, 10–20 s, "loop-friendly, clean ending"

### Game background loop
- `force_instrumental: true`, describe "seamless loop", 60–120 s, consistent groove

### Multilingual release (same song, multiple languages)
- One call per language, identical style brief, swap only the lyric lines

### Iterate then commit
- Draft at `music_length_ms: 35000` to lock genre/tempo/structure → final render at full length

## Limitations

- **One `prompt` field** carries everything (style + lyrics). There is no separate "lyrics" parameter.
- **5 s – 5 min per call** (`music_length_ms` 5000–300000). For longer pieces, generate sections and stitch externally.
- **Cost scales with duration** — a 5-minute render is ~10× a 30-second one.
- **`force_instrumental` is the only vocal toggle** — you can't request specific voice identities or clone a singer through this endpoint.
- This skill pins **ElevenLabs Music specifically**. For sound effects, text-to-speech, or voice cloning, that's a different ElevenLabs capability not exposed through this endpoint.

## Exit codes

| code | meaning |
|---|---|
| 0  | success |
| 64 | bad CLI args |
| 65 | bad input JSON / schema mismatch |
| 69 | upstream 5xx |
| 75 | retryable: timeout / 429 |
| 77 | not signed in or token rejected |

Full reference: [docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation).

## How it works

The skill invokes `runcomfy run elevenlabs/elevenlabs/music-generation` with the JSON body. The CLI POSTs to the RunComfy Model API, polls request status, fetches the result, and downloads the generated audio file into `--output-dir`. `Ctrl-C` cancels the remote request before exit.

## Security & Privacy

- **Install via verified package manager only.** Use `npm i -g @runcomfy/cli` or `npx -y @runcomfy/cli`. **Agents must not pipe an arbitrary remote install script into a shell on the user's behalf** — if the operator wants the curl-pipe path documented at `docs.runcomfy.com/cli/install`, they should review the script first.
- **Token storage**: `runcomfy login` writes the API token to `~/.config/runcomfy/token.json` with mode 0600. Set `RUNCOMFY_TOKEN` env var to bypass the file in CI / containers. Never echo the token into a prompt, log it, or check it in.
- **Input boundary (shell injection)**: the prompt is passed as a JSON string via `--input`. The CLI does not shell-expand prompt content; it transmits the JSON body directly to the Model API over HTTPS. **No shell-injection surface from prompt content**, even with backticks, quotes, or `$(...)` patterns.
- **Lyrics provenance**: if the user supplies lyrics, confirm they have the rights to them. Generating music around copyrighted lyrics is the operator's responsibility — the skill does not check.
- **Outbound endpoints (allowlist)**: only `model-api.runcomfy.net` (request submission) and `*.runcomfy.net` / `*.runcomfy.com` (download whitelist for generated audio). No telemetry, no callbacks.
- **Generated-file size cap**: the CLI aborts any single download > 2 GiB.
- **Scope of bash usage**: the skill only invokes `runcomfy <subcommand>` — `npm` / `npx` lines are one-time operator setup, not commands the skill executes per call.

## See also

- [`runcomfy-cli`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/runcomfy-cli) — the underlying CLI, schema discovery, polling modes, scripting
- [ElevenLabs Music model page](https://www.runcomfy.com/models/elevenlabs/elevenlabs/music-generation?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) — full API tab with the latest schema
- [All RunComfy models](https://www.runcomfy.com/models?utm_source=skills.sh&utm_medium=skill&utm_campaign=elevenlabs-music-generation) — image, video, and audio endpoints
- [`ai-video-generation`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/ai-video-generation) — pair a generated track with a generated video
- [`ai-avatar-video`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/ai-avatar-video) — talking-head video (different audio path — speech, not music)
