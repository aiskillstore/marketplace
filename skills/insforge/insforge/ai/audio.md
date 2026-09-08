# Audio

Use OpenRouter audio APIs for speech-to-text (STT) and text-to-speech (TTS).
Keep OpenRouter request details in the official docs; use this guide for how to
wire audio features into InsForge Storage, database rows, and server-side app
flows.

Official OpenRouter references:

- [Speech-to-Text](https://openrouter.ai/docs/guides/overview/multimodal/stt)
- [Text-to-Speech](https://openrouter.ai/docs/guides/overview/multimodal/tts)
- [Audio input/output with chat completions](https://openrouter.ai/docs/guides/overview/multimodal/audio)
- [Create transcription](https://openrouter.ai/docs/api/api-reference/transcriptions/create-audio-transcriptions)
- [Models API](https://openrouter.ai/docs/api-reference/models/get-models)

## Naming

Use OpenRouter's terms in user-facing docs and code comments:

| Capability | OpenRouter term | Endpoint |
|------------|-----------------|----------|
| Audio to text | Speech-to-Text (STT), transcription | `/api/v1/audio/transcriptions` |
| Text to audio | Text-to-Speech (TTS), speech | `/api/v1/audio/speech` |
| Audio reasoning | Audio input via chat completions | `/api/v1/chat/completions` |

Name the InsForge guide `audio.md` because it covers both STT and TTS.
Use "transcription" only for STT-specific tables, jobs, or UI.

## Speech-to-Text

For STT, upload the original audio file to InsForge Storage first, then
transcribe from server-side code. Store the transcript and OpenRouter metadata
in the database:

- `audio_url` and `audio_key` for the source file
- transcript text
- model ID and audio format
- duration/cost/usage when returned
- OpenRouter generation ID when available
- owner/session/tenant fields needed for RLS

OpenRouter STT expects base64-encoded raw audio bytes, not a data URI. For long
recordings, split audio into smaller segments before sending them to
OpenRouter; the official docs call out upstream timeout risk for large files.

## Text-to-Speech

For TTS, generate speech from server-side code and treat the OpenRouter response
as audio bytes. Upload the result to InsForge Storage and save:

- `audio_url` and `audio_key`
- input text or a reference to the source message
- model ID, voice, response format, and speed when used
- owner/session/tenant fields needed for RLS

Prefer `mp3` for stored playback. Use raw PCM only for realtime audio pipelines.
Do not store generated audio bytes or base64 audio in Postgres.

## Audio Input via Chat

Use the dedicated STT endpoint when the product needs a transcript. Use audio
input via chat completions when the model should reason about the audio, answer
questions about it, or combine audio with other modalities.

## Best Practices

1. Keep `OPENROUTER_API_KEY` server-side; browsers upload/listen through your
   app, not directly through OpenRouter.
2. Store audio files in InsForge Storage and database rows with `url` plus `key`.
3. Store transcripts, model IDs, usage/cost, and generation IDs for auditing and
   debugging.
4. Use RLS on transcript and audio-asset tables so users cannot read each
   other's recordings or generated speech.
5. Use [models-list.md](models-list.md) to discover models with
   `output_modalities=transcription` or `output_modalities=speech`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling STT/TTS directly from the browser | Route through server-side code so the key stays private |
| Storing raw audio/base64 in Postgres | Store files in Storage; save `url` and `key` in the database |
| Calling the chat audio endpoint when a transcript is needed | Use `/api/v1/audio/transcriptions` for STT |
| Treating TTS responses as JSON | TTS returns an audio byte stream |
| Sending long recordings as one STT request | Split long audio into smaller segments |
