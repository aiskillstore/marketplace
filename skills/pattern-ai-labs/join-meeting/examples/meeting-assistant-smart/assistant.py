#!/usr/bin/env python3
"""
AgentCall — Smart Meeting Assistant with Background Task Execution

A meeting assistant that can execute tasks in the background while the meeting
continues. Uses collaborative mode — GetSun (collaborative voice intelligence)
handles conversation naturally while the agent executes tools in parallel.

The key pattern:
  1. GetSun's context describes available capabilities (tools)
  2. When someone asks for a task, GetSun acknowledges INSTANTLY
     ("Sure, I'll look that up") — because the context says it can
  3. The agent detects the task, executes the tool in the background
  4. When results are ready, the agent:
     - Updates GetSun's context with the full data (so follow-up questions work)
     - Announces with a SHORT inject.natural: "I've got the results ready."
  5. GetSun speaks the short announcement at the next natural pause
  6. User asks follow-up → GetSun answers from context instantly

WHY THIS PATTERN IS POWERFUL:
  - Instant feedback: participants hear "I'll do that" immediately
  - No dead air: meeting continues while the agent works in background
  - Natural delivery: results are spoken conversationally, not robotically
  - Follow-up capable: data is in context, so "tell me more about X" works
  - Parallel tasks: multiple tasks can run simultaneously

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python assistant.py "https://meet.google.com/abc-def-ghi"

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

from tools import TOOLS, get_capabilities_text

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

# Maximum context size for GetSun (collaborative voice intelligence).
# Context holds capabilities + accumulated task results.
MAX_CONTEXT_CHARS = 4000


# ──────────────────────────────────────────────────────────────────────────────
# CONTEXT MANAGER
#
# WHY: GetSun (collaborative voice intelligence) uses the context to answer
# questions. By keeping task results in the context, GetSun can answer
# follow-up questions about results without the agent doing anything.
#
# The context has two parts:
#   1. Capabilities (static) — what tools the assistant can use
#   2. Task results (dynamic) — accumulated data from completed tasks
#
# When context exceeds 4000 chars, oldest results are trimmed first.
# Capabilities always stay — GetSun always needs to know what it can do.
# ──────────────────────────────────────────────────────────────────────────────

class ContextManager:
    """Manages the two-layer context for GetSun (collaborative voice intelligence)."""

    def __init__(self, persona: str, capabilities: str):
        self.persona = persona
        self.capabilities = capabilities
        self.task_results: List[dict] = []

    def add_result(self, summary: str, data: str):
        """Add a task result. Oldest results trimmed if over limit."""
        self.task_results.append({"summary": summary, "data": data})
        # Trim oldest results if total context exceeds limit
        while len(self.build()) > MAX_CONTEXT_CHARS and len(self.task_results) > 1:
            self.task_results.pop(0)

    def build(self) -> str:
        """
        Build the combined context string.

        WHY we combine persona + capabilities + results into one context:
        - GetSun sees this as its "knowledge" for answering questions
        - Capabilities tell it what to promise ("I can look that up")
        - Results give it data to answer follow-ups ("The revenue was $2.4M")
        - Persona shapes how it communicates (concise, helpful, etc.)
        """
        parts = [self.persona, "", self.capabilities]

        if self.task_results:
            parts.append("")
            parts.append("Data available for answering questions:")
            for r in self.task_results:
                parts.append(f"\n{r['summary']}:")
                parts.append(r["data"])

        return "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# TASK DETECTOR (LLM)
#
# WHY: Not every transcript is a task. "What did Alice say?" is answerable
# from meeting memory — no tool needed. But "Look up Q3 revenue" requires
# a database query. The LLM distinguishes between these.
#
# The LLM returns:
#   {"is_task": false}                          — no action needed
#   {"is_task": true, "tool": "database_lookup",
#    "query": "Q3 revenue by region",
#    "summary": "Q3 regional revenue"}          — execute this tool
# ──────────────────────────────────────────────────────────────────────────────

TASK_DETECT_PROMPT = """You detect tasks in meeting transcripts. The assistant "{bot_name}" has these tools:

{tool_descriptions}

Given the latest transcript, determine:
- Is the speaker asking {bot_name} to perform a task that requires one of these tools?
- Normal conversation or questions answerable from meeting memory do NOT need tools.
- Only flag as a task if it requires fetching external data, computing, or creating something.

The assistant's voice intelligence can answer questions from what it heard in the meeting.
It can also do realtime web search on its own. Only use tools for things that need
database lookups, document searches, calculations, or ticket creation.

Respond with ONLY a JSON object:
If NOT a task: {{"is_task": false}}
If IS a task: {{"is_task": true, "tool": "<tool_name>", "query": "<what to look up>", "summary": "<short label for this data>"}}"""


def detect_task(transcript_text: str, speaker: str, bot_name: str) -> dict:
    """
    Ask an LLM if this transcript requires a tool execution.
    Uncomment ONE LLM option below.

    Returns: {"is_task": false} or {"is_task": true, "tool": "...", "query": "...", "summary": "..."}
    """
    tool_descriptions = "\n".join(
        f"  - {name}: {t['description']} (e.g., {t['examples']})"
        for name, t in TOOLS.items()
    )
    system = TASK_DETECT_PROMPT.format(
        bot_name=bot_name,
        tool_descriptions=tool_descriptions,
    )
    user_msg = f"[{speaker}]: {transcript_text}"

    # ──────────────────────────────────────────────────────────────────
    # OPTION A: Anthropic (Claude)
    #
    # pip install anthropic
    # export ANTHROPIC_API_KEY="sk-ant-..."
    # ──────────────────────────────────────────────────────────────────
    # from anthropic import Anthropic
    # client = Anthropic()
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=128,
    #     system=system,
    #     messages=[{"role": "user", "content": user_msg}],
    # )
    # return json.loads(response.content[0].text)

    # ──────────────────────────────────────────────────────────────────
    # OPTION B: OpenAI (GPT-4o)
    #
    # pip install openai
    # export OPENAI_API_KEY="sk-..."
    # ──────────────────────────────────────────────────────────────────
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": system},
    #         {"role": "user", "content": user_msg},
    #     ],
    #     response_format={"type": "json_object"},
    # )
    # return json.loads(response.choices[0].message.content)

    # ──────────────────────────────────────────────────────────────────
    # OPTION C: Google Gemini
    # ──────────────────────────────────────────────────────────────────
    # import google.generativeai as genai
    # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    # model = genai.GenerativeModel("gemini-2.0-flash")
    # response = model.generate_content(system + "\n\n" + user_msg)
    # return json.loads(response.text)

    # ──────────────────────────────────────────────────────────────────
    # NO LLM CONFIGURED — never detect tasks (assistant works as simple version)
    # ──────────────────────────────────────────────────────────────────
    return {"is_task": False}


# ──────────────────────────────────────────────────────────────────────────────
# TASK EXECUTOR
#
# WHY async + create_task:
#   The task runs in the background while the event loop continues to
#   receive meeting events. The meeting never pauses. Multiple tasks
#   can run simultaneously (e.g., "look up revenue AND create a ticket").
#
# WHY voice.context_update + inject.natural together:
#   - voice.context_update: adds data to GetSun's knowledge so follow-up
#     questions work ("tell me more about the revenue breakdown")
#   - inject.natural: tells GetSun to speak the results NOW at the next
#     natural pause. Without inject, GetSun has the data but won't
#     volunteer it — it waits to be asked.
#   Together they provide: immediate delivery + persistent knowledge.
# ──────────────────────────────────────────────────────────────────────────────

async def execute_task(ws, task: dict, context_mgr: ContextManager):
    """
    Execute a tool in the background and inject results into the meeting.

    This runs as a separate coroutine — the main event loop keeps processing
    meeting events while this runs. When results are ready:
      1. Context is updated (so GetSun can answer follow-ups)
      2. Results are injected naturally (so GetSun speaks them at next pause)
    """
    tool_name = task["tool"]
    query = task["query"]
    summary = task["summary"]

    tool = TOOLS.get(tool_name)
    if not tool:
        print(f"  [!] Unknown tool: {tool_name}")
        return

    print(f"  ⚙️  Executing: {tool_name}(\"{query}\")")

    try:
        # Run the tool (async — doesn't block event loop)
        result = await tool["fn"](query)

        # ── Step 1: Update context ──
        # WHY: GetSun (collaborative voice intelligence) keeps this data in memory.
        # If someone asks a follow-up question ("break that down by quarter"),
        # GetSun can answer from the context without the agent doing anything.
        context_mgr.add_result(summary, result)
        await ws.send(json.dumps({
            "command": "voice.context_update",
            "text": context_mgr.build(),
        }))
        print(f"  📝 Context updated with: {summary}")

        # ── Step 2: Announce results with SHORT inject ──
        # WHY: inject.natural has high reliability — if interrupted, GetSun retries
        # until fully spoken. Keep it SHORT (1 sentence) to avoid retry loops.
        # The full data is already in context (step 1) — user can ask follow-ups
        # and GetSun answers from context instantly.
        # DO NOT dump full results into inject — that's an anti-pattern.
        await ws.send(json.dumps({
            "command": "inject.natural",
            "text": f"I've got the {summary} results ready.",
            "priority": "normal",
        }))
        print(f"  💉 Announced results for: {summary}")

    except Exception as e:
        # ── Graceful failure ──
        # WHY: If a tool fails, we don't want silence. The meeting participants
        # asked for something — they should know it didn't work.
        error_msg = f"I wasn't able to complete the {summary} lookup. Could you give me more details?"
        await ws.send(json.dumps({
            "command": "inject.natural",
            "text": error_msg,
            "priority": "normal",
        }))
        print(f"  ❌ Task failed: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# AGENTCALL API
# ──────────────────────────────────────────────────────────────────────────────

def create_call(meet_url: str, bot_name: str, trigger_words: List[str], context: str, voice: str) -> dict:
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


def save_meeting_log(
    call_id: str,
    participants: List[str],
    transcript: List[dict],
    tasks_completed: List[dict],
    voice_events: List[dict],
    end_reason: str,
    output_file: Optional[str],
):
    now = datetime.now()
    filename = output_file or f"smart-meeting-log-{now.strftime('%Y-%m-%d-%H%M')}.md"

    with open(filename, "w") as f:
        f.write(f"# Smart Meeting Log — {now.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Call ID:** {call_id}  \n")
        f.write(f"**End reason:** {end_reason}  \n\n")

        f.write("## Participants\n")
        for p in sorted(participants):
            f.write(f"- {p}\n")
        f.write("\n")

        if tasks_completed:
            f.write("## Tasks Executed\n")
            for t in tasks_completed:
                f.write(f"- **{t['summary']}** ({t['tool']}) — {t['time']}  \n")
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

    print(f"\nMeeting log saved to: {filename}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN EVENT LOOP
# ──────────────────────────────────────────────────────────────────────────────

async def run_assistant(call: dict, bot_name: str, output_file: Optional[str]):
    """
    Main loop: listen to events, detect tasks, execute in background.

    WHY this architecture:
      The event loop runs continuously, receiving meeting events from the
      WebSocket. When a task is detected, it's spawned as a background
      coroutine via asyncio.create_task() — the loop keeps running.
      Multiple tasks can execute simultaneously. Results are injected
      as each task completes, in whatever order they finish.
    """
    call_id = call["call_id"]
    ws_url = call["ws_url"]
    if ws_url.startswith("https://"):
        ws_url = ws_url.replace("https://", "wss://")

    # Initialize context manager with persona + tool capabilities
    capabilities = get_capabilities_text()
    persona = (
        f"You are {bot_name}, a smart meeting assistant. "
        f"Answer questions from what has been discussed in this meeting. "
        f"Be concise — 1-2 sentences. If you don't know, say so.\n\n"
        f"When someone asks you to perform a task from your capabilities below, "
        f"acknowledge immediately — say you'll do it and share results shortly. "
        f"When results arrive in your context, they're available for follow-up questions.\n\n"
        f"Note: You can also search the web in realtime for general questions. "
        f"The capabilities below are for tasks that need specific company data, "
        f"documents, calculations, or creating action items."
    )
    context_mgr = ContextManager(persona, capabilities)

    transcript = []
    participants = set()
    voice_events = []
    tasks_completed = []
    pending_tasks = set()
    end_reason = "unknown"

    print(f"Connecting to WebSocket: {ws_url}")

    try:
        async with websockets.connect(ws_url) as ws:
            print("Connected. Waiting for bot to join...\n")

            async for msg in ws:
                event = json.loads(msg)
                event_type = event.get("event", event.get("type", ""))
                now_str = datetime.now().strftime("%H:%M:%S")

                # ── Bot joined ──
                if event_type == "call.bot_ready":
                    print(f"Bot is in the meeting with avatar visible.")
                    print(f"Tools available: {', '.join(TOOLS.keys())}")
                    print(f"Say trigger word to ask a question or request a task.\n")

                # ── Participants ──
                elif event_type == "participant.joined":
                    name = event.get("name", "Unknown")
                    participants.add(name)
                    print(f"  + {name} joined")

                elif event_type == "participant.left":
                    print(f"  - {event.get('name', 'Unknown')} left")

                # ── Transcript (agent sees finals in collaborative mode) ──
                elif event_type == "transcript.final":
                    speaker = event.get("speaker", "Unknown")
                    text = event.get("text", "").strip()
                    if not text:
                        continue

                    timestamp = event.get("timestamp", "")
                    participants.add(speaker)
                    transcript.append({"speaker": speaker, "text": text, "timestamp": timestamp})
                    print(f"  [{speaker}] {text}")

                    # ── Task detection ──
                    # WHY: We check every transcript to see if someone is asking
                    # the assistant to do something that requires a tool.
                    # GetSun handles conversational questions on its own —
                    # we only intervene when external data/action is needed.
                    task = detect_task(text, speaker, bot_name)
                    if task.get("is_task"):
                        tool_name = task["tool"]
                        summary = task["summary"]
                        print(f"  🎯 Task detected: {tool_name} — {summary}")
                        tasks_completed.append({"tool": tool_name, "summary": summary, "time": now_str})
                        pending_tasks.add(summary)

                        # ── Spawn background execution ──
                        # WHY create_task: the tool runs asynchronously while this
                        # loop continues receiving meeting events. The meeting
                        # never pauses. GetSun already acknowledged the request
                        # (because context described the capability).
                        asyncio.create_task(execute_task(ws, task, context_mgr))

                # ── Voice state (from GetSun) ──
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

                # ── Voice text (what GetSun said) ──
                elif event_type == "voice.text":
                    text = event.get("text", "")
                    if voice_events:
                        voice_events[-1]["text"] = text
                    print(f"  💬 {bot_name} said: \"{text}\"")

                # ── TTS lifecycle ──
                elif event_type == "tts.started":
                    print(f"  🔊 Speaking...")
                elif event_type == "tts.done":
                    print(f"  🔇 Done speaking")
                elif event_type == "tts.interrupted":
                    print(f"  ⚡ Interrupted")

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

    save_meeting_log(call_id, sorted(participants), transcript, tasks_completed, voice_events, end_reason, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Smart Meeting Assistant (Collaborative + Background Tasks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python assistant.py "https://meet.google.com/abc-def-ghi"
  python assistant.py "https://meet.google.com/abc" --name "Aria" --triggers "aria,hey aria"
  python assistant.py "https://meet.google.com/abc" --voice voice.bella
        """,
    )
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Juno", help="Bot name (default: Juno)")
    parser.add_argument("--triggers", default="juno,zuno,assistant", help="Comma-separated trigger words")
    parser.add_argument("--voice", default="voice.heart", help="Voice ID (default: voice.heart)")
    parser.add_argument("--output", default=None, help="Output filename")
    args = parser.parse_args()

    trigger_words = [t.strip() for t in args.triggers.split(",")]

    print(f"Creating smart meeting assistant:")
    print(f"  Bot name: {args.name}")
    print(f"  Trigger words: {trigger_words}")
    print(f"  Voice: {args.voice}")
    print(f"  Tools: {', '.join(TOOLS.keys())}")
    print(f"  Mode: webpage-av (avatar) + collaborative\n")

    # Build initial context: persona + capabilities
    capabilities = get_capabilities_text()
    initial_context = (
        f"You are {args.name}, a smart meeting assistant. "
        f"Answer questions from what has been discussed in this meeting. "
        f"Be concise — 1-2 sentences. If you don't know, say so.\n\n"
        f"When someone asks you to perform a task from your capabilities below, "
        f"acknowledge immediately — say you'll do it and share results shortly. "
        f"When results arrive in your context, they're available for follow-up questions.\n\n"
        f"Note: You can also search the web in realtime for general questions. "
        f"The capabilities below are for tasks that need specific company data, "
        f"documents, calculations, or creating action items.\n\n"
        f"{capabilities}"
    )

    call = create_call(args.meet_url, args.name, trigger_words, initial_context, args.voice)
    print(f"Call created: {call['call_id']}")
    print(f"Status: {call['status']}\n")

    try:
        asyncio.run(run_assistant(call, args.name, args.output))
    except KeyboardInterrupt:
        print("\nInterrupted — cleaning up...")
        requests.delete(f"{API_BASE}/v1/calls/{call['call_id']}", headers=HEADERS)
        print("Call ended (cleanup)")


if __name__ == "__main__":
    main()
