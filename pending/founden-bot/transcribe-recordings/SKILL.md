---
name: transcribe-recordings
description: Turn local voice memos, meeting, interview, lecture or podcast recordings into transcripts, notes, summaries or action items, privately on the user's computer, using the Yap MCP tools (transcribe_audio, search_dictations). Use when the user mentions an audio or video file, a recording, a voice memo, or something they dictated earlier.
---

# Transcribe recordings with Yap

Yap MCP transcribes audio on the user's own computer (NVIDIA Parakeet, 25 European languages, detected automatically). Nothing is uploaded. These steps assume the `yap` MCP server is connected (`npx -y github:founden-bot/yap-mcp`).

## When the user points at a recording

1. Get the file's absolute path. If they only describe it ("the memo on my desktop"), ask for the path or file name; a leading `~` is fine.
2. Call `transcribe_audio` with `path`. Pass `timestamps: true` for anything longer than a few minutes or when they want to find moments again.
3. If the answer says the speech model is still downloading (first use only, about 670 MB), tell the user it is a one-time download and call the tool again a minute later. Do not switch to a cloud service.
4. Do what they asked with the text: a clean transcript, a summary, meeting notes with decisions and action items (owner, task, date when said), quotes with their timestamps, or a translation.
5. Quote the transcript faithfully. Mark words you are unsure about rather than guessing names or numbers.

## When the user refers to something they said or dictated

Call `search_dictations` with a few distinctive words (`query`) and a time window (`days`). It reads the history of the Yap dictation app on this computer, read-only. If nothing matches, widen `days` or try other words before saying it is not there.

## Good defaults

- Several files: transcribe them one by one and keep each result under the file's name.
- Long recordings: summarize per timestamped section first, then overall.
- Keep the user's language: answer in the language of the recording unless they ask otherwise.
