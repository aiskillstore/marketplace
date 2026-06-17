# Multilingual Note-Taker with Gemini Audio Understanding

Joins a meeting, collects raw audio, and sends it to Google Gemini for multilingual transcription, translation, and summarization. Handles meetings where participants speak different languages.

## Why This Approach

AgentCall's built-in speech-to-text is English-focused. For multilingual meetings, the English transcript misses or garbles non-English speech. Instead:

1. **Skip built-in STT** — set `transcription: false` (cheapest option)
2. **Collect raw audio** — set `audio_streaming: true` to get PCM chunks via WebSocket
3. **Send to Gemini** — Gemini natively understands 100+ languages from audio
4. **Get everything** — original language transcript + English translations + summary

## What It Does

1. Creates a call in **audio mode** with `audio_streaming: true`
2. Collects `audio.chunk` events (base64 PCM, 16kHz 16-bit mono)
3. Optionally collects English STT transcripts for speaker diarization hints
4. Optionally collects participant join events for speaker name mapping
5. On `call.ended`, stitches audio into a WAV file
6. Sends audio + participant list + optional English transcript to Gemini
7. Saves multilingual transcript + English summary to markdown

## Setup

```bash
pip install requests websockets google-generativeai

export AGENTCALL_API_KEY="ak_ac_your_key"
export GOOGLE_API_KEY="your_gemini_api_key"
```

## Usage

```bash
# Basic — audio only, cheapest (only base rate charged)
python notetaker.py "https://meet.google.com/abc-def-ghi"

# With English STT for better speaker identification
# (adds STT billing but Gemini can match speaker names to voices)
python notetaker.py "https://meet.google.com/abc" --with-english-stt

# Save the raw audio file for records
python notetaker.py "https://meet.google.com/abc" --save-audio

# Custom bot name and output
python notetaker.py "https://meet.google.com/abc" --name "Translator" --output standup.md

# All options
python notetaker.py "https://meet.google.com/abc" --name "Scribe" --save-audio --with-english-stt --output weekly.md
```

## Billing

### Without `--with-english-stt` (default, cheapest)

| Component | Charged? | Notes |
|-----------|----------|-------|
| Meeting bot (base) | Yes | Per minute of call |
| Speech-to-text | **No** | Skipped (`transcription: false`) |
| Voice intelligence | No | Direct mode |
| TTS | No | Bot doesn't speak |
| Gemini | Yes | Billed by Google (~$0.10/min audio) |

### With `--with-english-stt`

Same as above, plus:
- **Speech-to-text** — charged per minute (provides speaker names as hints to Gemini)

## Output

```markdown
# Multilingual Meeting Notes — 2026-04-03 14:30

**Call ID:** call-550e8400...
**Duration:** 32 minutes
**Participants:** Alice, Hiroshi, Priya
**Transcribed by:** Google Gemini (audio understanding)

---

## Languages Detected
- English, Japanese, Hindi

## Transcript

[00:12] Alice (English): Let's go around and share updates from each region.
[00:25] Hiroshi (Japanese): 東京チームは新しいAPIの統合を完了しました。テストは来週開始予定です。
  [The Tokyo team has completed the new API integration. Testing is scheduled to start next week.]
[00:48] Priya (Hindi): हमारी मुंबई टीम ने मोबाइल ऐप का बीटा वर्शन लॉन्च कर दिया है।
  [Our Mumbai team has launched the beta version of the mobile app.]
[01:10] Alice (English): Great progress. Any blockers?
...

## Summary (English)
Regional teams shared updates: Tokyo completed API integration with testing next week,
Mumbai launched mobile app beta. Alice asked about blockers — Hiroshi mentioned a
dependency on the auth service migration.

## Key Decisions
- API integration testing to begin next week
- Mumbai beta to be extended to 500 users

## Action Items
- [ ] Hiroshi: Share test plan with Alice by Thursday
- [ ] Priya: Send beta metrics report by Friday
- [ ] Alice: Schedule auth service migration review

## Follow-Up Needed
- Auth service dependency blocking Tokyo's full deployment
```

## How Speaker Diarization Works

Gemini identifies speakers from audio alone (different voices). To improve accuracy:

### Participant list (always collected)
When people join the meeting, AgentCall sends `participant.joined` events with names. These names are passed to Gemini so it can label speakers as "Alice" instead of "Speaker 1".

### English STT hints (optional, `--with-english-stt`)
If enabled, AgentCall's built-in STT provides an English transcript with speaker names already assigned. Even though the English transcript may be inaccurate for non-English speech, the speaker labels are useful. This is passed to Gemini as a reference for matching voices to names.

## Audio Data Size

| Meeting Duration | PCM Size | WAV Size | Within Gemini Limit? |
|-----------------|----------|----------|---------------------|
| 15 minutes | ~29 MB | ~29 MB | Yes (9.5 hr max) |
| 30 minutes | ~57 MB | ~57 MB | Yes |
| 1 hour | ~115 MB | ~115 MB | Yes |
| 4 hours | ~460 MB | ~460 MB | Yes |

## Customization Ideas

This is demo code. Agents and developers can modify it to:

- **Single language output** — change the prompt to "Translate all speech to Spanish" or any target language
- **Real-time translation** — process audio chunks as they arrive instead of waiting for call end
- **Multiple LLMs** — use OpenAI Whisper for transcription + GPT-4o for summarization
- **Subtitle generation** — output as VTT/SRT format for video playback
- **Language detection alerts** — notify when a new language is detected mid-meeting
- **Custom vocabulary** — add domain-specific terms to the prompt for better accuracy
- **Streaming summary** — send partial audio every 5 minutes for incremental summaries
