#!/usr/bin/env python3
"""
AgentCall — Voice Bridge for AI Coding Agents

This script bridges a meeting's audio I/O with an AI agent framework
(Claude Code, Cursor, Codex, Gemini CLI, etc.) via stdin/stdout.

It is NOT a standalone agent. It has NO LLM. The agent framework that
spawns this script IS the LLM. This script is a thin communication layer:

  stdout → agent framework: meeting events (transcripts, chat, participants)
  stdin  ← agent framework: commands (tts.speak, send chat, leave, raise hand)

The agent framework processes transcripts as instructions (same as text input)
using its existing session context — no separate context loading needed.

KEY FEATURES:
  - VAD gap buffering: accumulates transcript.final events and waits for a
    configurable silence gap before emitting to the agent. This handles slow
    speakers whose sentences are split by STT into multiple finals.
  - Chat I/O: agent can send and receive meeting chat messages (useful for
    sharing URLs, code snippets, or text that's hard to speak).
  - Raise hand: agent can raise the bot's hand before speaking.
  - Graceful exit: agent can leave the call, or the bridge exits when the
    call ends externally.

PROTOCOL (one JSON object per line, newline-delimited):

  stdout events (bridge → agent):
    {"event": "call.bot_ready", "call_id": "..."}
    {"event": "participant.joined", "name": "Alice"}
    {"event": "participant.left", "name": "Bob"}
    {"event": "user.message", "speaker": "Alice", "text": "check the endpoint"}
    {"event": "chat.received", "sender": "Alice", "message": "here's the link: ..."}
    {"event": "tts.done"}
    {"event": "call.ended", "reason": "left"}

  stdin commands (agent → bridge):
    {"command": "tts.speak", "text": "Health check returned OK", "voice": "af_heart"}
    {"command": "send_chat", "message": "Here's the URL: https://..."}
    {"command": "raise_hand"}
    {"command": "leave"}

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"
    python bridge.py "https://meet.google.com/abc-def-ghi"

    # Custom bot name, voice, and VAD timeout
    python bridge.py "https://meet.google.com/abc" --name "Claude" --voice af_bella --vad-timeout 3.0

Dependencies:
    pip install aiohttp websockets
"""

import argparse
import asyncio
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import aiohttp
import websockets


# ──────────────────────────────────────────────────────────────────────────────
# EMIT HELPERS
#
# All output goes to stdout as single-line JSON objects.
# The agent framework reads these as events.
# stderr is used for debug logging (not visible to agent).
# ──────────────────────────────────────────────────────────────────────────────

def emit(event: dict):
    """Send an event to the agent framework via stdout."""
    print(json.dumps(event), flush=True)


def emit_err(msg: str):
    """Log to stderr (visible in terminal, not to agent framework)."""
    print(f"[bridge] {msg}", file=sys.stderr, flush=True)


# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

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
    emit_err("API key not found. Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# VAD GAP BUFFER
#
# Problem: FirstCall's STT splits long utterances into multiple transcript.final
# events. A speaker who pauses mid-sentence gets split:
#   final: "Can you check the"      (1s gap)
#   final: "health endpoint"         (1s gap)
#   final: "and also the database"
#
# If we emit each final separately, the agent sees 3 separate instructions
# instead of one: "Can you check the health endpoint and also the database"
#
# Solution: Buffer finals and wait for a silence gap (configurable, default 2s).
# If a transcript.partial arrives during the gap, the user is still speaking —
# reset the timer. Only emit the combined text when silence confirms the user
# is done speaking.
#
# This is especially important for:
# - Slow speakers who pause between phrases
# - Complex instructions with natural pauses
# - Non-native speakers who think between words
# ──────────────────────────────────────────────────────────────────────────────

class VADBuffer:
    """Accumulates transcript finals and emits after a silence gap."""

    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self.pending: List[str] = []
        self.speaker: str = "User"
        self.timer_task: Optional[asyncio.Task] = None
        self.on_complete = None  # callback: async fn(speaker, text)

    def on_transcript_final(self, speaker: str, text: str):
        """Add a final transcript. Start/reset the silence timer."""
        text = text.strip()
        if not text:
            return

        self.pending.append(text)
        self.speaker = speaker
        self._reset_timer()

    def on_transcript_partial(self, speaker: str, text: str):
        """
        A partial transcript arrived — user is still speaking.
        Reset the timer if we have pending finals.
        """
        if self.pending:
            self._reset_timer()

    def _reset_timer(self):
        """Cancel existing timer and start a new one."""
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self._wait_and_emit())

    async def _wait_and_emit(self):
        """Wait for silence, then emit combined text."""
        try:
            await asyncio.sleep(self.timeout)
            if self.pending and self.on_complete:
                combined = " ".join(self.pending)
                speaker = self.speaker
                self.pending.clear()
                await self.on_complete(speaker, combined)
        except asyncio.CancelledError:
            pass  # Timer was reset — user is still speaking

    async def flush(self):
        """Force-emit any pending text (e.g., on call end)."""
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
        if self.pending and self.on_complete:
            combined = " ".join(self.pending)
            speaker = self.speaker
            self.pending.clear()
            await self.on_complete(speaker, combined)


# ──────────────────────────────────────────────────────────────────────────────
# API CLIENT (minimal, inline — no external dependency beyond aiohttp)
# ──────────────────────────────────────────────────────────────────────────────

class APIClient:
    """Minimal AgentCall API client."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
        return self.session

    async def create_call(self, meet_url: str, bot_name: str) -> dict:
        session = await self._get_session()
        async with session.post(f"{API_BASE}/v1/calls", json={
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "audio",
            "voice_strategy": "direct",
            "transcription": True,
        }) as resp:
            if resp.status != 201:
                body = await resp.text()
                raise Exception(f"Create call failed ({resp.status}): {body}")
            return await resp.json()

    async def connect_ws(self, call_id: str):
        ws_url = API_BASE.replace("https://", "wss://").replace("http://", "ws://")
        uri = f"{ws_url}/v1/calls/{call_id}/ws?api_key={API_KEY}"
        self.ws = await websockets.connect(uri)
        return self.ws

    async def send(self, command: dict):
        if self.ws:
            await self.ws.send(json.dumps(command))

    async def close(self):
        if self.ws:
            await self.ws.close()
        if self.session and not self.session.closed:
            await self.session.close()


# ──────────────────────────────────────────────────────────────────────────────
# STDIN READER
#
# Reads commands from the agent framework via stdin.
# Each command is a single-line JSON object.
#
# Supported commands:
#   tts.speak  — speak text in the meeting via TTS
#   send_chat  — send a text message in the meeting chat
#   raise_hand — raise the bot's hand in the meeting
#   leave      — gracefully leave the meeting
# ──────────────────────────────────────────────────────────────────────────────

async def read_stdin(client: APIClient, done_event: asyncio.Event):
    """Read commands from agent framework and forward to AgentCall.

    Uses a daemon thread with blocking sys.stdin.readline() + asyncio.Queue for
    cross-platform compatibility (asyncio.connect_read_pipe is broken on Windows
    per CPython issue #71019).
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def reader_thread():
        while not done_event.is_set():
            try:
                line = sys.stdin.readline()
            except Exception:
                break
            if not line:
                loop.call_soon_threadsafe(queue.put_nowait, None)
                break
            loop.call_soon_threadsafe(queue.put_nowait, line)

    threading.Thread(target=reader_thread, daemon=True).start()

    try:
        while not done_event.is_set():
            try:
                line = await asyncio.wait_for(queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            if line is None:
                break

            try:
                cmd = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            command = cmd.get("command", "")

            if command == "tts.speak":
                # Speak text in the meeting via TTS.
                # The agent decides what to say — this just delivers it.
                await client.send({
                    "type": "tts.speak",
                    "text": cmd.get("text", ""),
                    "voice": cmd.get("voice", "af_heart"),
                    "speed": cmd.get("speed", 1.0),
                })

            elif command == "send_chat":
                # Send a text message in the meeting chat.
                # Useful for: URLs, code snippets, emails, anything hard to speak.
                await client.send({
                    "type": "meeting.send_chat",
                    "message": cmd.get("message", ""),
                })

            elif command == "raise_hand":
                # Raise the bot's hand in the meeting.
                # Useful to signal the agent wants to speak in group meetings.
                await client.send({
                    "type": "meeting.raise_hand",
                })

            elif command == "screenshot":
                # Take a screenshot of the meeting view.
                # Captures what the bot sees: participant grid, shared screen, presentation.
                await client.send({
                    "type": "screenshot.take",
                    "request_id": cmd.get("request_id", "screenshot"),
                })

            elif command == "leave":
                # Gracefully leave the meeting.
                await client.send({
                    "type": "meeting.leave",
                })
                done_event.set()

    except asyncio.CancelledError:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# EVENT LOOP
#
# Connects to the meeting WebSocket and processes events.
# Events are translated to a simplified protocol for the agent framework.
#
# The agent framework receives clean, simple events:
#   user.message  — user finished speaking (VAD-buffered, complete utterance)
#   chat.received — user sent a chat message
#   participant.joined/left — people entering/leaving
#   tts.done — bot finished speaking (agent can speak again)
#   call.ended — meeting is over
# ──────────────────────────────────────────────────────────────────────────────

async def run_bridge(meet_url: str, bot_name: str, voice: str, vad_timeout: float):
    """Main bridge loop."""
    client = APIClient()
    done = asyncio.Event()

    # ── Create call ──
    emit_err(f"Creating call for: {meet_url}")
    try:
        call = await client.create_call(meet_url, bot_name)
    except Exception as e:
        emit({"event": "error", "message": str(e)})
        await client.close()
        return

    call_id = call["call_id"]
    emit_err(f"Call created: {call_id}")
    emit({"event": "call.created", "call_id": call_id, "status": call.get("status", "")})

    # ── Set up VAD buffer ──
    vad = VADBuffer(timeout=vad_timeout)

    async def on_user_complete(speaker: str, text: str):
        """Called when VAD confirms user is done speaking."""
        emit({"event": "user.message", "speaker": speaker, "text": text})

    vad.on_complete = on_user_complete

    # ── Connect WebSocket ──
    try:
        ws = await client.connect_ws(call_id)
    except Exception as e:
        emit({"event": "error", "message": f"WebSocket connection failed: {e}"})
        await client.close()
        return

    emit_err("WebSocket connected")

    # ── Start stdin reader ──
    stdin_task = asyncio.create_task(read_stdin(client, done))

    # ── Track state ──
    bot_name_lower = bot_name.lower()
    is_speaking = False
    greeted = False
    participants = set()

    # ── Process events ──
    try:
        async for msg in ws:
            if done.is_set():
                break

            event = json.loads(msg)
            event_type = event.get("event", event.get("type", ""))

            # ── Bot is in the meeting ──
            if event_type == "call.bot_ready":
                emit({"event": "call.bot_ready", "call_id": call_id})
                emit_err("Bot joined the meeting")

            # ── Participant joined ──
            elif event_type == "participant.joined":
                participant = event.get("participant", {})
                name = participant.get("name", event.get("name", "Unknown"))
                participants.add(name)
                emit({"event": "participant.joined", "name": name})
                emit_err(f"Participant joined: {name}")

                # Greet when first non-bot participant joins.
                # The agent SHOULD greet unless explicitly told not to.
                if not greeted and name.lower() != bot_name_lower:
                    greeted = True
                    emit({
                        "event": "greeting.prompt",
                        "participant": name,
                        "hint": f"{name} joined. Introduce yourself and greet them via tts.speak. Active participation is the default — do not stay silent.",
                    })

            # ── Participant left ──
            elif event_type == "participant.left":
                participant = event.get("participant", {})
                name = participant.get("name", event.get("name", "Unknown"))
                participants.discard(name)
                emit({"event": "participant.left", "name": name})

            # ── Transcript final ──
            elif event_type == "transcript.final":
                speaker_obj = event.get("speaker", {})
                if isinstance(speaker_obj, dict):
                    speaker = speaker_obj.get("name", "Unknown")
                else:
                    speaker = str(speaker_obj)
                text = event.get("text", "").strip()

                # Skip the bot's own speech being transcribed back
                if speaker.lower() == bot_name_lower:
                    continue
                if is_speaking:
                    continue
                if not text:
                    continue

                # Feed to VAD buffer — will emit user.message after silence gap
                vad.on_transcript_final(speaker, text)

            # ── Transcript partial ──
            elif event_type == "transcript.partial":
                speaker_obj = event.get("speaker", {})
                if isinstance(speaker_obj, dict):
                    speaker = speaker_obj.get("name", "Unknown")
                else:
                    speaker = str(speaker_obj)

                # Skip bot's own partials
                if speaker.lower() == bot_name_lower:
                    continue

                # Tell VAD buffer the user is still speaking
                vad.on_transcript_partial(speaker, event.get("text", ""))

            # ── Chat message received ──
            elif event_type == "chat.message":
                sender = event.get("sender", "Unknown")
                message = event.get("message", "")
                if sender.lower() != bot_name_lower and message:
                    emit({
                        "event": "chat.received",
                        "sender": sender,
                        "message": message,
                    })

            # ── Screenshot result ──
            elif event_type == "screenshot.result":
                emit({
                    "event": "screenshot.result",
                    "data": event.get("data", ""),
                    "width": event.get("width", 0),
                    "height": event.get("height", 0),
                    "request_id": event.get("request_id", ""),
                })

            # ── TTS lifecycle ──
            elif event_type == "tts.started":
                is_speaking = True

            elif event_type == "tts.done":
                is_speaking = False
                emit({"event": "tts.done"})

            elif event_type == "tts.error":
                is_speaking = False
                emit({"event": "tts.error", "reason": event.get("reason", "unknown")})

            # ── Call ended ──
            elif event_type == "call.ended":
                reason = event.get("reason", "unknown")
                emit({"event": "call.ended", "reason": reason})
                emit_err(f"Call ended: {reason}")
                done.set()
                break

    except websockets.exceptions.ConnectionClosed:
        emit({"event": "call.ended", "reason": "connection_lost"})
        emit_err("WebSocket connection closed")
    except Exception as e:
        emit({"event": "error", "message": str(e)})
        emit_err(f"Error: {e}")
    finally:
        # Flush any remaining VAD buffer
        await vad.flush()
        stdin_task.cancel()
        await client.close()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Voice Bridge — connects an AI coding agent to a meeting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script is spawned by an AI agent framework (Claude Code, Cursor, etc.)
as a subprocess. It bridges meeting audio I/O with the agent via stdin/stdout.

The agent framework's existing session context is used — no separate LLM needed.
Transcripts arrive as instructions; tts.speak sends voice responses.

Protocol:
  stdout: {"event": "user.message", "speaker": "Alice", "text": "..."} (meeting → agent)
  stdin:  {"command": "tts.speak", "text": "...", "voice": "af_heart"}  (agent → meeting)
        """,
    )
    parser.add_argument("meet_url", help="Meeting URL (Google Meet, Zoom, or Teams)")
    parser.add_argument("--name", default="Agent", help="Bot name in participant list (default: Agent)")
    parser.add_argument("--voice", default="af_heart", help="TTS voice ID (default: af_heart)")
    parser.add_argument(
        "--vad-timeout", type=float, default=2.0,
        help="Seconds to wait after last transcript.final before treating utterance as complete. "
             "Increase for slow speakers, decrease for fast speakers. (default: 2.0)"
    )
    args = parser.parse_args()

    asyncio.run(run_bridge(args.meet_url, args.name, args.voice, args.vad_timeout))


if __name__ == "__main__":
    main()
