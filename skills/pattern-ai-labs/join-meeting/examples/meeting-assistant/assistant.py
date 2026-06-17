#!/usr/bin/env python3
"""
AgentCall — Simple Meeting Assistant (Collaborative Mode)

An AI meeting assistant that joins with an animated avatar, listens to the
conversation, and answers when addressed by name. Uses collaborative voice
strategy — GetSun (collaborative voice intelligence) handles everything
autonomously: trigger word detection, barge-in prevention, natural timing,
and interruption handling.

The agent's job is minimal: create the call, stay connected, and log events.
GetSun hears the meeting transcript automatically and responds when triggered.

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python assistant.py "https://meet.google.com/abc-def-ghi"

    # Custom bot name and trigger words
    python assistant.py "https://meet.google.com/abc" --name "Juno" --triggers "juno,zuno,assistant"

Dependencies:
    pip install requests websockets
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


def create_call(meet_url: str, bot_name: str, trigger_words: List[str], context: str, voice: str) -> dict:
    """Create a collaborative mode call with avatar UI."""
    resp = requests.post(
        f"{API_BASE}/v1/calls",
        headers=HEADERS,
        json={
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "webpage-av",
            "voice_strategy": "collaborative",
            "transcription": True,
            "ui_template": "avatar",
            "collaborative": {
                "trigger_words": trigger_words,
                "barge_in_prevention": True,
                "interruption_use_full_text": True,
                "context": context,
                "voice": voice,
            },
        },
    )
    resp.raise_for_status()
    return resp.json()


def save_meeting_log(call_id: str, participants: List[str], transcript: List[dict], voice_events: List[dict], end_reason: str, output_file: Optional[str]):
    """Save meeting log to markdown."""
    now = datetime.now()
    filename = output_file or f"meeting-log-{now.strftime('%Y-%m-%d-%H%M')}.md"

    with open(filename, "w") as f:
        f.write(f"# Meeting Log — {now.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Call ID:** {call_id}  \n")
        f.write(f"**End reason:** {end_reason}  \n\n")

        f.write("## Participants\n")
        for p in sorted(participants):
            f.write(f"- {p}\n")
        f.write("\n")

        f.write("## Transcript\n")
        for line in transcript:
            ts = line.get("timestamp", "")
            time_str = ts[11:19] if len(ts) >= 19 else ""
            f.write(f"[{time_str}] **{line['speaker']}**: {line['text']}  \n")
        f.write("\n")

        if voice_events:
            f.write("## Voice State Timeline\n")
            for ve in voice_events:
                f.write(f"- [{ve['time']}] {ve['state']}")
                if ve.get("text"):
                    f.write(f" — \"{ve['text']}\"")
                f.write("\n")
            f.write("\n")

    print(f"\nMeeting log saved to: {filename}")


async def run_assistant(call: dict, output_file: Optional[str]):
    """Connect to WebSocket and log events. GetSun handles everything else."""
    call_id = call["call_id"]
    ws_url = call["ws_url"]
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")

    transcript = []
    participants = set()
    voice_events = []
    end_reason = "unknown"

    print(f"Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as ws:
            print("Connected. Waiting for bot to join...\n")

            async for msg in ws:
                event = json.loads(msg)
                event_type = event.get("event", event.get("type", ""))
                now_str = datetime.now().strftime("%H:%M:%S")

                # ── Bot joined the meeting ──
                if event_type == "call.bot_ready":
                    print("Bot is in the meeting with avatar visible.")
                    print("Say the trigger word to ask a question.\n")

                # ── Participants ──
                elif event_type == "participant.joined":
                    name = event.get("name", "Unknown")
                    participants.add(name)
                    print(f"  + {name} joined")

                elif event_type == "participant.left":
                    print(f"  - {event.get('name', 'Unknown')} left")

                # ── Transcripts (agent sees finals only in collaborative mode) ──
                elif event_type == "transcript.final":
                    speaker = event.get("speaker", "Unknown")
                    text = event.get("text", "")
                    timestamp = event.get("timestamp", "")
                    participants.add(speaker)
                    transcript.append({"speaker": speaker, "text": text, "timestamp": timestamp})
                    print(f"  [{speaker}] {text}")

                # ── Voice state changes (from GetSun) ──
                elif event_type == "voice.state":
                    state = event.get("state", "")
                    voice_events.append({"time": now_str, "state": state})
                    icon = {
                        "listening": "👂",
                        "actively_listening": "🎯",
                        "thinking": "🧠",
                        "waiting_to_speak": "⏳",
                        "speaking": "🗣️",
                        "interrupted": "🛑",
                        "contextually_aware": "💡",
                    }.get(state, "❓")
                    print(f"  {icon} Voice state: {state}")

                # ── Voice text (what GetSun decided to say) ──
                elif event_type == "voice.text":
                    text = event.get("text", "")
                    if voice_events:
                        voice_events[-1]["text"] = text
                    print(f"  💬 Bot says: \"{text}\"")

                # ── TTS events ──
                elif event_type == "tts.started":
                    print(f"  🔊 TTS started")

                elif event_type == "tts.done":
                    print(f"  🔇 TTS done")

                elif event_type == "tts.interrupted":
                    print(f"  ⚡ TTS interrupted")

                # ── Call ended ──
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

    # Save log
    save_meeting_log(call_id, sorted(participants), transcript, voice_events, end_reason, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Simple Meeting Assistant (Collaborative Mode)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: bot named "Juno", responds to "juno", "zuno", "assistant"
  python assistant.py "https://meet.google.com/abc-def-ghi"

  # Custom name and triggers
  python assistant.py "https://meet.google.com/abc" --name "Aria" --triggers "aria,hey aria"

  # Custom voice
  python assistant.py "https://meet.google.com/abc" --voice voice.bella
        """,
    )
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Juno", help="Bot name (default: Juno)")
    parser.add_argument("--triggers", default="juno,zuno,assistant", help="Comma-separated trigger words (default: juno,zuno,assistant)")
    parser.add_argument("--voice", default="voice.heart", help="Voice ID (default: voice.heart)")
    parser.add_argument("--context", default=None, help="Custom context/persona for the assistant")
    parser.add_argument("--output", default=None, help="Output filename (default: meeting-log-DATE.md)")
    args = parser.parse_args()

    trigger_words = [t.strip() for t in args.triggers.split(",")]
    context = args.context or (
        f"You are {args.name}, a helpful meeting assistant. "
        f"Answer questions based on what has been discussed in this meeting. "
        f"Be concise — keep answers to 1-2 sentences. "
        f"If you don't know something, say so honestly."
    )

    print(f"Creating meeting assistant:")
    print(f"  Bot name: {args.name}")
    print(f"  Trigger words: {trigger_words}")
    print(f"  Voice: {args.voice}")
    print(f"  Mode: webpage-av (avatar visible)")
    print(f"  Strategy: collaborative (autonomous voice intelligence)\n")

    call = create_call(args.meet_url, args.name, trigger_words, context, args.voice)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    try:
        asyncio.run(run_assistant(call, args.output))
    except KeyboardInterrupt:
        print("\nInterrupted — cleaning up...")
        requests.delete(f"{API_BASE}/v1/calls/{call['call_id']}", headers=HEADERS)
        print("Call ended (cleanup)")


if __name__ == "__main__":
    main()
