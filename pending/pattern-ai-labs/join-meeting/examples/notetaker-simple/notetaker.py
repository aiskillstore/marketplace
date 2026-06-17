#!/usr/bin/env python3
"""
AgentCall — Simple Note-Taker Bot

Joins a meeting in audio mode, collects transcripts in real-time,
and saves the full transcript to a markdown file when the meeting ends.

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python notetaker.py "https://meet.google.com/abc-def-ghi"

    # Optional: customize bot name
    python notetaker.py "https://meet.google.com/abc-def-ghi" --name "Scribe"
"""

import argparse
import asyncio
import json
import os
import sys
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

if not API_KEY:
    print("Error: Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def create_call(meet_url: str, bot_name: str) -> dict:
    """Create a call via REST API — audio mode, transcription on, direct strategy (listen only)."""
    resp = requests.post(
        f"{API_BASE}/v1/calls",
        headers=HEADERS,
        json={
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "audio",
            "voice_strategy": "direct",
            "transcription": True,
        },
    )
    resp.raise_for_status()
    return resp.json()


def fetch_transcript(call_id: str) -> Optional[dict]:
    """Fetch the full transcript after the call ends."""
    resp = requests.get(
        f"{API_BASE}/v1/calls/{call_id}/transcript?format=json",
        headers=HEADERS,
    )
    if resp.status_code == 200:
        return resp.json()
    return None


def save_notes(call_id: str, participants: List[str], transcript_lines: List[dict], duration: str, end_reason: str):
    """Save transcript to a markdown file."""
    now = datetime.now().strftime("%Y-%m-%d-%H%M")
    filename = f"meeting-notes-{now}.md"

    with open(filename, "w") as f:
        f.write(f"# Meeting Notes — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

        f.write("## Participants\n")
        for p in participants:
            f.write(f"- {p}\n")
        f.write("\n")

        f.write("## Transcript\n")
        for line in transcript_lines:
            ts = line.get("timestamp", "")
            # Extract time portion (HH:MM:SS) from ISO timestamp
            time_str = ts[11:19] if len(ts) >= 19 else ts
            f.write(f"[{time_str}] {line['speaker']}: {line['text']}\n")
        f.write("\n")

        f.write("## Meeting Info\n")
        f.write(f"- Call ID: {call_id}\n")
        f.write(f"- Duration: {duration}\n")
        f.write(f"- End reason: {end_reason}\n")
        f.write(f"- Total utterances: {len(transcript_lines)}\n")

    print(f"\nNotes saved to: {filename}")
    return filename


async def listen(call: dict):
    """Connect to WebSocket and collect transcript events."""
    call_id = call["call_id"]
    ws_url = call["ws_url"]

    # Replace https:// with wss:// if needed
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")

    transcript_lines = []
    participants = set()
    end_reason = "unknown"

    print(f"Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as ws:
            print("Connected. Waiting for events...\n")

            async for msg in ws:
                event = json.loads(msg)
                event_type = event.get("event", event.get("type", ""))

                if event_type == "call.bot_ready":
                    print("Bot is in the meeting. Listening for transcripts...\n")

                elif event_type == "participant.joined":
                    name = event.get("name", "Unknown")
                    participants.add(name)
                    print(f"  + {name} joined")

                elif event_type == "participant.left":
                    name = event.get("name", "Unknown")
                    print(f"  - {name} left")

                elif event_type == "transcript.final":
                    speaker = event.get("speaker", "Unknown")
                    text = event.get("text", "")
                    timestamp = event.get("timestamp", "")
                    participants.add(speaker)
                    transcript_lines.append({
                        "speaker": speaker,
                        "text": text,
                        "timestamp": timestamp,
                    })
                    print(f"  [{speaker}] {text}")

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

    # Calculate duration
    created = call.get("created_at", "")
    duration = f"{len(transcript_lines)} utterances captured"

    # Try fetching the full transcript from the API (more complete than WS events)
    print("\nFetching full transcript from API...")
    full_transcript = fetch_transcript(call_id)
    if full_transcript and full_transcript.get("entries"):
        transcript_lines = [
            {
                "speaker": e["speaker"].get("name", "Unknown") if isinstance(e.get("speaker"), dict) else str(e.get("speaker", "Unknown")),
                "text": e.get("text", ""),
                "timestamp": e.get("timestamp", ""),
            }
            for e in full_transcript["entries"]
        ]
        minutes = full_transcript.get("duration_minutes", 0)
        duration = f"{minutes} minutes"
        print(f"  Got {len(transcript_lines)} entries ({duration})")
    else:
        print("  Full transcript not available yet, using real-time captures")

    # Save to file
    save_notes(call_id, sorted(participants), transcript_lines, duration, end_reason)


def main():
    parser = argparse.ArgumentParser(description="AgentCall Simple Note-Taker")
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Notetaker", help="Bot name (default: Notetaker)")
    args = parser.parse_args()

    print(f"Creating call for: {args.meet_url}")
    print(f"Bot name: {args.name}\n")

    call = create_call(args.meet_url, args.name)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    try:
        asyncio.run(listen(call))
    except KeyboardInterrupt:
        print("\nInterrupted — cleaning up...")
        requests.delete(f"{API_BASE}/v1/calls/{call['call_id']}", headers=HEADERS)
        print("Call ended (cleanup)")


if __name__ == "__main__":
    main()
