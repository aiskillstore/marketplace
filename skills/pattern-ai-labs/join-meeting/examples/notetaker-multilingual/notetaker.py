#!/usr/bin/env python3
"""
AgentCall — Multilingual Note-Taker with Gemini Audio Understanding

Joins a meeting in audio mode, collects raw audio chunks, and after the
meeting ends sends the full audio to Google Gemini for multilingual
transcription, translation, and summarization.

This is useful when meeting participants speak different languages.
AgentCall's built-in STT is English-focused, so for multilingual meetings
we skip it and use Gemini's native audio understanding instead.

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    export GOOGLE_API_KEY="your_gemini_api_key"
    python notetaker.py "https://meet.google.com/abc-def-ghi"

    # Save raw audio file for archival
    python notetaker.py "https://meet.google.com/abc" --save-audio

    # Custom output file
    python notetaker.py "https://meet.google.com/abc" --output standup.md

Dependencies:
    pip install requests websockets google-generativeai

NOTE: This is demo code showing the multilingual capability.
Agents can easily modify this to:
  - Translate everything to a single target language (e.g. --language spanish)
  - Change the output format (JSON, DOCX, etc.)
  - Stream the transcript to a different service
  - Add real-time translation during the meeting (using audio chunks as they arrive)
"""

import argparse
import asyncio
import base64
import io
import json
import os
import struct
import sys
import wave
from datetime import datetime
from typing import List, Optional

import requests
import websockets

_cfg = {}
_cfg_path = os.path.join(os.path.expanduser("~"), ".agentcall", "config.json")
if os.path.exists(_cfg_path):
    try:
        _cfg = json.loads(open(_cfg_path).read())
    except (json.JSONDecodeError, OSError):
        pass

API_BASE = os.environ.get("AGENTCALL_API_URL", "") or _cfg.get("api_url", "") or "https://api.agentcall.dev"
API_KEY = os.environ.get("AGENTCALL_API_KEY", "") or _cfg.get("api_key", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

if not API_KEY:
    print("Error: Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json")
    sys.exit(1)

if not GOOGLE_API_KEY:
    print("Error: Set GOOGLE_API_KEY environment variable (Gemini API key)")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Audio format: AgentCall sends 16kHz, 16-bit mono PCM
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # 16-bit = 2 bytes
CHANNELS = 1


# ──────────────────────────────────────────────────────────────────────────────
# GEMINI PROMPT
#
# This prompt instructs Gemini to:
# 1. Transcribe in original languages
# 2. Provide English translations for non-English utterances
# 3. Map speakers using the participant list (if provided)
# 4. Generate a structured summary in English
#
# Agents can modify this prompt to:
# - Translate everything to a single language: "Translate all speech to Spanish"
# - Skip translations: "Only transcribe, no translations needed"
# - Different format: "Output as JSON with speaker, language, original, translated fields"
# ──────────────────────────────────────────────────────────────────────────────

GEMINI_PROMPT_TEMPLATE = """You are a multilingual meeting transcriber and summarizer.

You will receive the audio recording of a meeting. Participants may speak in different languages.

{speaker_hint}

## Instructions
1. Transcribe the meeting in the ORIGINAL language each person spoke
2. After each non-English utterance, provide an English translation in [brackets]
3. English utterances do not need translation
4. Identify speakers by name if possible (using the participant list and voice matching), otherwise use Speaker 1, Speaker 2, etc.
5. Include timestamps relative to the start of the recording
6. After the transcript, provide a complete summary in English

## Output Format (use exactly this markdown structure)

## Languages Detected
- <list each language detected>

## Transcript

[MM:SS] Speaker Name (Language): <original text>
  [English translation if not English]

## Summary (English)
<2-4 sentence overview of what was discussed>

## Key Decisions
- <decision 1>
- <decision 2>
(or "No explicit decisions were made." if none)

## Action Items
- [ ] <person>: <task> <deadline if mentioned>
(or "No action items were identified." if none)

## Follow-Up Needed
- <unresolved question or topic>
(or "No follow-ups needed." if none)"""


def build_prompt(participants: List[str], english_transcript: Optional[List[dict]]) -> str:
    """Build the Gemini prompt with optional speaker hints."""
    hints = []

    if participants:
        hints.append(f"**Participants in the meeting:** {', '.join(participants)}")
        hints.append("Use these names to identify speakers in the transcript when possible.")

    if english_transcript:
        hints.append("\n**English STT transcript (for speaker diarization reference — may be inaccurate for non-English speech):**")
        for line in english_transcript[:50]:  # Limit to first 50 lines to save tokens
            ts = line.get("timestamp", "")
            time_str = ts[11:19] if len(ts) >= 19 else ""
            hints.append(f"  [{time_str}] {line['speaker']}: {line['text']}")
        if len(english_transcript) > 50:
            hints.append(f"  ... ({len(english_transcript) - 50} more lines)")

    speaker_hint = "\n".join(hints) if hints else "No participant information available."
    return GEMINI_PROMPT_TEMPLATE.format(speaker_hint=speaker_hint)


def pcm_to_wav_bytes(pcm_data: bytes) -> bytes:
    """Convert raw PCM bytes to WAV format in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def save_wav(pcm_data: bytes, filename: str):
    """Save raw PCM data as a WAV file."""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    duration_sec = len(pcm_data) / (SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS)
    print(f"  Audio saved: {filename} ({duration_sec:.0f}s, {len(pcm_data) / 1024 / 1024:.1f} MB)")


def summarize_with_gemini(wav_bytes: bytes, prompt: str) -> str:
    """Send audio to Gemini for multilingual transcription and summarization."""
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Upload audio as inline data
    audio_part = {
        "inline_data": {
            "mime_type": "audio/wav",
            "data": base64.b64encode(wav_bytes).decode("utf-8"),
        }
    }

    response = model.generate_content([prompt, audio_part])
    return response.text


def create_call(meet_url: str, bot_name: str, enable_english_stt: bool) -> dict:
    """Create a call with audio streaming enabled."""
    resp = requests.post(
        f"{API_BASE}/v1/calls",
        headers=HEADERS,
        json={
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "audio",
            "voice_strategy": "direct",
            "transcription": enable_english_stt,  # Optional: English STT for speaker hints
            "audio_streaming": True,              # Get raw audio chunks
        },
    )
    resp.raise_for_status()
    return resp.json()


def save_summary(
    call_id: str,
    participants: List[str],
    duration_sec: float,
    end_reason: str,
    gemini_output: str,
    output_file: Optional[str],
):
    """Save the Gemini-generated summary to a markdown file."""
    now = datetime.now()
    filename = output_file or f"meeting-multilingual-{now.strftime('%Y-%m-%d-%H%M')}.md"

    with open(filename, "w") as f:
        f.write(f"# Multilingual Meeting Notes — {now.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Call ID:** {call_id}  \n")
        f.write(f"**Duration:** {duration_sec / 60:.0f} minutes  \n")
        f.write(f"**Participants:** {', '.join(participants) if participants else 'Unknown'}  \n")
        f.write(f"**End reason:** {end_reason}  \n")
        f.write(f"**Transcribed by:** Google Gemini (audio understanding)  \n\n")
        f.write("---\n\n")
        f.write(gemini_output)
        f.write("\n")

    print(f"\nSummary saved to: {filename}")
    return filename


async def listen(call: dict, save_audio: bool, enable_english_stt: bool, output_file: Optional[str]):
    """Connect to WebSocket, collect audio chunks and optional English transcripts."""
    call_id = call["call_id"]
    ws_url = call["ws_url"]
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")

    audio_buffer = bytearray()
    participants = set()
    english_transcript = []  # Optional: English STT for speaker hints
    end_reason = "unknown"
    chunk_count = 0

    print(f"Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as ws:
            print("Connected. Collecting audio...\n")

            async for msg in ws:
                event = json.loads(msg)
                event_type = event.get("event", event.get("type", ""))

                if event_type == "call.bot_ready":
                    print("Bot is in the meeting. Recording audio...\n")

                elif event_type == "participant.joined":
                    name = event.get("name", "Unknown")
                    participants.add(name)
                    print(f"  + {name} joined")

                elif event_type == "participant.left":
                    print(f"  - {event.get('name', 'Unknown')} left")

                elif event_type == "audio.chunk":
                    # Raw PCM audio data (base64-encoded, 16kHz 16-bit mono)
                    audio_b64 = event.get("data", "")
                    if audio_b64:
                        pcm_bytes = base64.b64decode(audio_b64)
                        audio_buffer.extend(pcm_bytes)
                        chunk_count += 1
                        # Progress indicator every 500 chunks (~10 seconds)
                        if chunk_count % 500 == 0:
                            duration_so_far = len(audio_buffer) / (SAMPLE_RATE * SAMPLE_WIDTH)
                            print(f"  Recording... {duration_so_far:.0f}s collected ({len(audio_buffer) / 1024 / 1024:.1f} MB)")

                elif event_type == "transcript.final" and enable_english_stt:
                    # Collect English STT transcripts for speaker diarization hints
                    speaker = event.get("speaker", "Unknown")
                    text = event.get("text", "")
                    timestamp = event.get("timestamp", "")
                    participants.add(speaker)
                    english_transcript.append({"speaker": speaker, "text": text, "timestamp": timestamp})
                    print(f"  [STT] [{speaker}] {text}")

                elif event_type == "call.ended":
                    end_reason = event.get("reason", "unknown")
                    print(f"\nCall ended: {end_reason}")
                    break
    finally:
        # Always end the call to stop billing
        print("Ending call...")
        try:
            requests.delete(f"{API_BASE}/v1/calls/{call_id}", headers=HEADERS)
            print("Call ended (cleanup)")
        except Exception as e:
            print(f"Cleanup failed: {e}")

    duration_sec = len(audio_buffer) / (SAMPLE_RATE * SAMPLE_WIDTH * CHANNELS)
    print(f"\nTotal audio: {duration_sec:.0f} seconds ({len(audio_buffer) / 1024 / 1024:.1f} MB)")
    print(f"Chunks received: {chunk_count}")

    if len(audio_buffer) == 0:
        print("No audio collected. Exiting.")
        return

    # Convert PCM to WAV
    wav_bytes = pcm_to_wav_bytes(bytes(audio_buffer))

    # Optionally save raw audio
    if save_audio:
        now = datetime.now().strftime("%Y-%m-%d-%H%M")
        save_wav(bytes(audio_buffer), f"meeting-audio-{now}.wav")

    # Send to Gemini
    print("\nSending audio to Gemini for multilingual transcription...")
    print("  (this may take a minute for longer meetings)\n")

    prompt = build_prompt(
        sorted(participants),
        english_transcript if enable_english_stt and english_transcript else None,
    )
    gemini_output = summarize_with_gemini(wav_bytes, prompt)

    print("Gemini response received.\n")
    print("─" * 60)
    print(gemini_output)
    print("─" * 60)

    # Save to file
    save_summary(call_id, sorted(participants), duration_sec, end_reason, gemini_output, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Multilingual Note-Taker (Gemini Audio)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python notetaker.py "https://meet.google.com/abc-def-ghi"

  # Save the raw audio file
  python notetaker.py "https://meet.google.com/abc" --save-audio

  # Enable English STT for better speaker identification
  python notetaker.py "https://meet.google.com/abc" --with-english-stt

  # Custom bot name and output
  python notetaker.py "https://meet.google.com/abc" --name "Translator" --output standup.md
        """,
    )
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Scribe", help="Bot name (default: Scribe)")
    parser.add_argument("--output", default=None, help="Output filename (default: meeting-multilingual-DATE.md)")
    parser.add_argument("--save-audio", action="store_true", help="Save raw audio as .wav file")
    parser.add_argument(
        "--with-english-stt",
        action="store_true",
        help="Also enable English STT — provides speaker names as hints to Gemini for better diarization (adds STT billing)",
    )
    args = parser.parse_args()

    print(f"Creating call for: {args.meet_url}")
    print(f"Bot name: {args.name}")
    print(f"Audio streaming: enabled")
    print(f"English STT: {'enabled (for speaker hints)' if args.with_english_stt else 'disabled (audio-only, cheapest)'}")
    print(f"Save audio: {'yes' if args.save_audio else 'no'}\n")

    call = create_call(args.meet_url, args.name, args.with_english_stt)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    try:
        asyncio.run(listen(call, args.save_audio, args.with_english_stt, args.output))
    except KeyboardInterrupt:
        print("\nInterrupted — cleaning up...")
        requests.delete(f"{API_BASE}/v1/calls/{call['call_id']}", headers=HEADERS)
        print("Call ended (cleanup)")


if __name__ == "__main__":
    main()
