#!/usr/bin/env python3
"""
AgentCall — Smart Note-Taker with LLM Summarization

Joins a meeting in audio mode, collects transcripts, then uses an LLM
to generate a structured summary with key decisions and action items.

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python notetaker.py "https://meet.google.com/abc-def-ghi"

    # Optional: customize bot name and output
    python notetaker.py "https://meet.google.com/abc-def-ghi" --name "Scribe" --output summary.md
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


# ──────────────────────────────────────────────────────────────────────────────
# LLM SUMMARIZATION PROMPT
# This prompt asks the LLM to produce a structured meeting summary.
# It works with any LLM — OpenAI, Anthropic, Google Gemini, or local models.
# ──────────────────────────────────────────────────────────────────────────────

SUMMARY_PROMPT = """You are a meeting summarizer. Given the transcript below, produce a structured summary.

## Instructions
- Write a concise summary (2-4 sentences) of what was discussed
- List key decisions that were made (if any)
- Extract action items with the responsible person and deadline (if mentioned)
- Note any unresolved questions or topics that need follow-up
- Be factual — only include what was actually said, do not infer or assume

## Output Format (use exactly this markdown structure)

## Summary
<2-4 sentence overview>

## Key Decisions
- <decision 1>
- <decision 2>
(or "No explicit decisions were made." if none)

## Action Items
- [ ] <person>: <task> <deadline if mentioned>
- [ ] <person>: <task>
(or "No action items were identified." if none)

## Follow-Up Needed
- <unresolved question or topic>
(or "No follow-ups needed." if none)

## Transcript

{transcript}"""


def summarize_with_llm(transcript_text: str) -> str:
    """
    Send the transcript to an LLM for summarization.
    Uncomment ONE of the options below and add your API key.

    If no LLM is configured, returns the raw transcript.
    """

    prompt = SUMMARY_PROMPT.format(transcript=transcript_text)

    # ──────────────────────────────────────────────────────────────────────
    # OPTION A: Anthropic (Claude)
    #
    # pip install anthropic
    # export ANTHROPIC_API_KEY="sk-ant-..."
    # ──────────────────────────────────────────────────────────────────────
    # from anthropic import Anthropic
    #
    # client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=2048,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.content[0].text

    # ──────────────────────────────────────────────────────────────────────
    # OPTION B: OpenAI (GPT-4o)
    #
    # pip install openai
    # export OPENAI_API_KEY="sk-..."
    # ──────────────────────────────────────────────────────────────────────
    # from openai import OpenAI
    #
    # client = OpenAI()  # reads OPENAI_API_KEY from env
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.choices[0].message.content

    # ──────────────────────────────────────────────────────────────────────
    # OPTION C: Google Gemini
    #
    # pip install google-generativeai
    # export GOOGLE_API_KEY="..."
    # ──────────────────────────────────────────────────────────────────────
    # import google.generativeai as genai
    #
    # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # model = genai.GenerativeModel("gemini-2.0-flash")
    # response = model.generate_content(prompt)
    # return response.text

    # ──────────────────────────────────────────────────────────────────────
    # OPTION D: Any OpenAI-compatible API (Ollama, Together, Groq, etc.)
    #
    # pip install openai
    # ──────────────────────────────────────────────────────────────────────
    # from openai import OpenAI
    #
    # client = OpenAI(
    #     base_url="http://localhost:11434/v1",  # Ollama
    #     api_key="ollama",
    # )
    # response = client.chat.completions.create(
    #     model="llama3",
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # return response.choices[0].message.content

    # ──────────────────────────────────────────────────────────────────────
    # NO LLM CONFIGURED — return raw transcript with a note
    # ──────────────────────────────────────────────────────────────────────
    print("\n  [!] No LLM configured. Uncomment one of the options in summarize_with_llm().")
    print("  [!] Saving raw transcript without summary.\n")
    return None


def create_call(meet_url: str, bot_name: str) -> dict:
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
    resp = requests.get(f"{API_BASE}/v1/calls/{call_id}/transcript?format=json", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return None


def format_transcript(lines: List[dict]) -> str:
    """Format transcript lines into readable text for the LLM."""
    parts = []
    for line in lines:
        ts = line.get("timestamp", "")
        time_str = ts[11:19] if len(ts) >= 19 else ""
        parts.append(f"[{time_str}] {line['speaker']}: {line['text']}")
    return "\n".join(parts)


def save_summary(
    call_id: str,
    participants: List[str],
    transcript_lines: List[dict],
    duration: str,
    end_reason: str,
    summary: Optional[str],
    output_file: Optional[str],
):
    now = datetime.now()
    filename = output_file or f"meeting-summary-{now.strftime('%Y-%m-%d-%H%M')}.md"

    with open(filename, "w") as f:
        f.write(f"# Meeting Summary — {now.strftime('%Y-%m-%d %H:%M')}\n\n")

        # Meeting info header
        f.write(f"**Call ID:** {call_id}  \n")
        f.write(f"**Duration:** {duration}  \n")
        f.write(f"**Participants:** {', '.join(participants)}  \n")
        f.write(f"**End reason:** {end_reason}  \n\n")

        f.write("---\n\n")

        # LLM-generated summary (or placeholder)
        if summary:
            f.write(summary)
            f.write("\n\n")
        else:
            f.write("## Summary\n")
            f.write("*LLM summarization not configured. See the raw transcript below.*\n\n")
            f.write("## Key Decisions\n*Not available*\n\n")
            f.write("## Action Items\n*Not available*\n\n")

        f.write("---\n\n")

        # Full transcript
        f.write("## Full Transcript\n\n")
        for line in transcript_lines:
            ts = line.get("timestamp", "")
            time_str = ts[11:19] if len(ts) >= 19 else ""
            f.write(f"[{time_str}] **{line['speaker']}**: {line['text']}  \n")

    print(f"\nSummary saved to: {filename}")
    return filename


async def listen(call: dict, output_file: Optional[str]):
    call_id = call["call_id"]
    ws_url = call["ws_url"]
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
                    print(f"  - {event.get('name', 'Unknown')} left")

                elif event_type == "transcript.final":
                    speaker = event.get("speaker", "Unknown")
                    text = event.get("text", "")
                    timestamp = event.get("timestamp", "")
                    participants.add(speaker)
                    transcript_lines.append({"speaker": speaker, "text": text, "timestamp": timestamp})
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

    # Fetch full transcript
    print("\nFetching full transcript from API...")
    full = fetch_transcript(call_id)
    if full and full.get("entries"):
        transcript_lines = [
            {
                "speaker": e["speaker"].get("name", "Unknown") if isinstance(e.get("speaker"), dict) else str(e.get("speaker", "Unknown")),
                "text": e.get("text", ""),
                "timestamp": e.get("timestamp", ""),
            }
            for e in full["entries"]
        ]
        duration = f"{full.get('duration_minutes', 0)} minutes"
        print(f"  Got {len(transcript_lines)} entries ({duration})")
    else:
        duration = f"{len(transcript_lines)} utterances captured"
        print("  Full transcript not available yet, using real-time captures")

    # Summarize with LLM
    print("\nGenerating summary with LLM...")
    transcript_text = format_transcript(transcript_lines)
    summary = summarize_with_llm(transcript_text)

    # Save
    save_summary(call_id, sorted(participants), transcript_lines, duration, end_reason, summary, output_file)


def main():
    parser = argparse.ArgumentParser(description="AgentCall Smart Note-Taker with LLM Summary")
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Notetaker", help="Bot name (default: Notetaker)")
    parser.add_argument("--output", default=None, help="Output filename (default: meeting-summary-DATE.md)")
    args = parser.parse_args()

    print(f"Creating call for: {args.meet_url}")
    print(f"Bot name: {args.name}\n")

    call = create_call(args.meet_url, args.name)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    try:
        asyncio.run(listen(call, args.output))
    except KeyboardInterrupt:
        print("\nInterrupted — cleaning up...")
        requests.delete(f"{API_BASE}/v1/calls/{call['call_id']}", headers=HEADERS)
        print("Call ended (cleanup)")


if __name__ == "__main__":
    main()
