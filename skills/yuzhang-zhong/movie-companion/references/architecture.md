# Movie Companion Architecture

## Goal

Provide a watch-along workflow that feels live while preserving a hard no-spoiler boundary.

## Components

0. Screening mode state machine
   - Idle: no session is running.
   - Screening: user has said "开始观看" or equivalent; a session file stores wall-clock start time and movie timestamp.
   - Paused: user says playback is paused; do not estimate forward until resynced.
   - Closed: user exits screening mode; future `ask` calls must require a fresh start or resync.
   - Resync: user provides a new visible movie timestamp after pause, rewind, skip, or drift.
   - Every in-screening question must call the sync helper first, then answer from the returned safe bundle.

1. Subtitle indexer
   - Parse `.srt` and `.vtt` files into normalized cue objects.
   - Store start/end times in seconds and original text.
   - Accept multiple text tracks: dialogue subtitles, SDH captions, descriptive subtitles, audio-description transcripts, or manually prepared scene-note tracks.
   - Use these text tracks as the primary timeline source.

2. Watch session tracker
   - Record the wall-clock time when the user says playback starts.
   - Record the movie timestamp visible at that moment.
   - Estimate current movie time as `start_movie_seconds + elapsed_wall_seconds * playback_rate`.
   - Subtract a safety lag before retrieval.

3. Safe context retriever
   - Return only cues ending before the safe time.
   - Include a configurable lookback window.
   - Default to no future window.
   - The `ask` command bundles fresh time calculation plus safe context retrieval for active viewing.
   - Closed sessions are rejected by `ask` so the companion cannot accidentally keep estimating after the user ended screening mode.

4. Scene context without screenshots
   - Do not request screenshots from the user.
   - Prefer descriptive subtitles, SDH captions, closed captions with non-dialogue cues, audio-description transcripts, or manually prepared scene-note tracks.
   - If visual context is unavailable, answer from dialogue only and explicitly state the limitation.

5. External metadata
   - Use only for facts that cannot spoil plot: title disambiguation, release year, director, cast, runtime, language, ratings, or content warnings.
   - Avoid plot pages, recaps, reviews, ending explainers, and wiki sections during active viewing.

## Future App Shape

A fuller implementation can expose a local web UI:

- File picker for subtitles and optional local video.
- File picker for dialogue subtitles plus optional descriptive subtitle or audio-description tracks.
- Start/pause/resync controls.
- Current safe time display.
- "Ask Codex" text box that always includes the safe context bundle.

For streaming services with DRM, do not attempt to bypass protections. Use subtitles or descriptive tracks supplied by the user and their own timestamp.

## Failure Modes

- Playback paused or buffered: ask for current timestamp and resync.
- Subtitle drift: ask for visible timestamp and offset, then rebuild or adjust index.
- Missing descriptive tracks: rely on dialogue subtitles and user text descriptions only; keep answers cautious about visual claims.
- User requests spoilers: refuse during no-spoiler mode unless they explicitly end the session and opt into spoilers.
