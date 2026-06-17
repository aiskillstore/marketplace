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
  - VAD coalescing: accumulates transcript.final events and emits a single
    user.message after a short cooldown anchored to the most recent final.
    Handles slow speakers whose sentences are split by STT into multiple finals.
  - Chat I/O: agent can send and receive meeting chat messages (useful for
    sharing URLs, code snippets, or text that's hard to speak).
  - Raise hand: agent can raise the bot's hand before speaking.
  - Graceful exit: agent can leave the call, or the bridge exits when the
    call ends externally.

PROTOCOL (one JSON object per line, newline-delimited):

  stdout events (bridge → agent):
    {"event": "call.bot_joining_meeting", "call_id": "...", "detail": "joining"}
    {"event": "call.bot_waiting_room", "call_id": "..."}
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

    # Custom bot name, voice, and VAD cooldown
    python bridge.py "https://meet.google.com/abc" --name "Claude" --voice af_bella --vad-timeout 2.0

Dependencies:
    pip install aiohttp websockets
"""

import argparse
import asyncio
import json
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiohttp
import websockets


# ──────────────────────────────────────────────────────────────────────────────
# EMIT HELPERS
#
# All output goes to stdout as single-line JSON objects.
# The agent framework reads these as events.
# stderr is used for debug logging (not visible to agent).
# ──────────────────────────────────────────────────────────────────────────────

_output_file = None  # set by --output flag

def emit(event: dict):
    """Send an event to the agent framework via stdout (and optionally to a file)."""
    line = json.dumps(event)
    print(line, flush=True)
    if _output_file:
        try:
            with open(_output_file, "a") as f:
                f.write(line + "\n")
        except Exception:
            pass


def emit_err(msg: str):
    """Log to stderr (visible in terminal, not to agent framework)."""
    print(f"[bridge] {msg}", file=sys.stderr, flush=True)


def _sanitize_tts_text(text: str) -> str:
    """Normalize em/en dashes to commas — Kokoro mispronounces them
    (reads U+2014 as "circumflex something" on some text paths).
    Pure replacement, no stripping; everything else passes through."""
    return text.replace("—", ", ").replace("–", ", ")


import re as _re

def _split_sentences(text: str) -> list:
    """Split text on sentence terminators (.!?) followed by whitespace,
    OR on newlines. Used by the bridge to break multi-sentence tts.speak
    into per-sentence backend dispatches: first audio reaches the meeting
    in <1s regardless of paragraph length, played/not_played boundaries
    stay exact, and the agent still receives one tts.done per tts.speak.
    Single-sentence text returns a 1-element list (passthrough)."""
    parts = _re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in parts if s.strip()]


# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

_config_path = Path.home() / ".agentcall" / "config.json"
_config = {}
if _config_path.exists():
    try:
        _config = json.loads(_config_path.read_text())
    except (json.JSONDecodeError, OSError):
        pass

API_BASE = os.environ.get("AGENTCALL_API_URL", "") or _config.get("api_url", "") or "https://api.agentcall.dev"
API_KEY = os.environ.get("AGENTCALL_API_KEY", "") or _config.get("api_key", "")

if not API_KEY:
    emit_err("API key not found. Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────────────────────
# VAD STATE MACHINE — coalesces fragmented transcript.final into user.message
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
# Solution: a 3-state machine, structurally parallel to BargeInState below
# but kept as a separate instance with its own cooldown so the two timers
# can be tuned independently.
#
#   IDLE              — pending=[], no timer running
#   WAITING_FOR_FINAL — partial seen (or partial cancelled an earlier
#                       cooldown); no timer running, awaiting the next final
#   COOLDOWN          — final received, cooldown timer ticking. A new final
#                       restarts the cooldown (still buffering this utterance).
#                       A new partial cancels the cooldown and returns to
#                       WAITING_FOR_FINAL (user resumed). Cooldown expiry
#                       emits the buffered text as user.message.
#
# Why anchor the cooldown to transcript.final and not "any STT event":
#   - partials are noisy timing signals (mid-sentence batching, network jitter)
#   - transcript.final is FirstCall STT's authoritative end-of-utterance
#     signal (fires after ~600ms of detected silence)
#   - anchoring to final removes the partial-jitter noise from the gate
#
# Trade-off: a truly silent mid-utterance pause longer than the cooldown
# splits the utterance into two user.message events (no partial arrives
# during the pause to extend the cooldown). In practice most speakers
# produce filler noise / breath that triggers partials, so coalescing
# still works. If this turns out to bite, raise the cooldown.
#
# Failure mode: if a partial arrives without a follow-up final (STT bug,
# audio cut, network drop), the buffered text stays unemitted until either
# (a) the next genuine utterance's final + cooldown flushes everything
# together, or (b) flush() runs on call end. Same shape of "stuck waiting"
# trade-off as BargeInState; recovery is the same.
# ──────────────────────────────────────────────────────────────────────────────

class VADBuffer:
    """Accumulates transcript.final events and emits user.message after a
    cooldown anchored to the most recent final. See block comment above."""

    def __init__(self, cooldown: float = 1.25):
        self.cooldown = cooldown
        self.pending: list[str] = []
        self.speaker: str = "User"
        self._cooldown_task: Optional[asyncio.Task] = None
        self._emit_task: Optional[asyncio.Task] = None
        # _idle is set when state == IDLE (cooldown elapsed). The emit task
        # awaits this; flipping it to set wakes the emit and delivers the
        # buffered utterance.
        self._idle = asyncio.Event()
        self._idle.set()
        self.on_complete = None  # callback: async fn(speaker, text)

    def on_transcript_final(self, speaker: str, text: str):
        """STT emitted end-of-utterance — append text and (re)start cooldown."""
        text = text.strip()
        if not text:
            return
        was_empty = not self.pending
        self.pending.append(text)
        self.speaker = speaker
        # → COOLDOWN: restart the timer; an earlier emit task (if any) keeps
        # waiting on the same _idle Event and will pick up the longer pending
        # list when the cooldown finally fires.
        self._cancel_cooldown()
        self._idle.clear()
        self._cooldown_task = asyncio.create_task(self._cooldown_timer())
        if was_empty:
            self._emit_task = asyncio.create_task(self._wait_and_emit())

    def on_transcript_partial(self, speaker: str, text: str):
        """STT detected speech — cancel any running cooldown; await next final."""
        # → WAITING_FOR_FINAL: any cooldown is invalidated because the user
        # started speaking again. The buffered pending list is preserved.
        self._cancel_cooldown()
        self._idle.clear()

    def _cancel_cooldown(self):
        if self._cooldown_task and not self._cooldown_task.done():
            self._cooldown_task.cancel()
        self._cooldown_task = None

    async def _cooldown_timer(self):
        try:
            await asyncio.sleep(self.cooldown)
        except asyncio.CancelledError:
            return
        self._idle.set()  # → IDLE: wake the emit task

    async def _wait_and_emit(self):
        try:
            await self._idle.wait()
            if self.pending and self.on_complete:
                combined = " ".join(self.pending)
                speaker = self.speaker
                self.pending.clear()
                await self.on_complete(speaker, combined)
        except asyncio.CancelledError:
            pass

    async def flush(self):
        """Force-emit any pending text (e.g., on call end)."""
        self._cancel_cooldown()
        if self._emit_task and not self._emit_task.done():
            self._emit_task.cancel()
        self._emit_task = None
        if self.pending and self.on_complete:
            combined = " ".join(self.pending)
            speaker = self.speaker
            self.pending.clear()
            await self.on_complete(speaker, combined)
        # Reset to IDLE so a post-flush final (defensive) would behave sanely.
        self._idle.set()


# ──────────────────────────────────────────────────────────────────────────────
# BARGE-IN STATE MACHINE
#
# Drives whether tts.speak is allowed to forward. Three states:
#
#   IDLE              — STT believes everyone is quiet; gate is open.
#   WAITING_FOR_FINAL — a transcript.partial fired and STT hasn't yet
#                       emitted a transcript.final for the utterance.
#                       Gate is locked until the final arrives.
#   COOLDOWN          — transcript.final fired; we wait COOLDOWN_SECONDS
#                       to catch the user resuming. Gate is locked. Any
#                       transcript.partial during cooldown cancels the
#                       timer and returns to WAITING_FOR_FINAL.
#
# Why the explicit final signal beats partial-arrival timing:
#   - partial events can fire mid-sentence; their cadence is noisy
#   - network jitter delays partials, making time-since-last-partial
#     a poor proxy for "is the human still speaking right now"
#   - transcript.final is FirstCall STT's authoritative end-of-utterance
#     signal (fires after ~600ms of silence). Anchoring to final removes
#     the noise from the gate.
#
# The 30s SPEAKING fallback that earlier designs included is intentionally
# omitted — if the bot stays silent because state is stuck, the human will
# inevitably speak again, producing a final that transitions COOLDOWN → IDLE.
# Self-healing on any future final.
# ──────────────────────────────────────────────────────────────────────────────

class BargeInState:
    """STT-derived speaking-state machine. Gate is open iff state is IDLE."""

    COOLDOWN_SECONDS = 1.5

    def __init__(self):
        # Use an asyncio.Event for event-driven waits — wait_until_idle()
        # blocks with zero polling and resolves the moment the cooldown
        # timer flips state back to IDLE.
        self._idle = asyncio.Event()
        self._idle.set()  # start IDLE — first tts.speak fires immediately
        self._cooldown_task: Optional[asyncio.Task] = None

    def on_partial(self) -> None:
        """transcript.partial arrived — STT detected speech, lock the gate."""
        self._cancel_cooldown()
        self._idle.clear()

    def on_final(self) -> None:
        """transcript.final arrived — start the cooldown timer."""
        self._cancel_cooldown()
        self._idle.clear()
        self._cooldown_task = asyncio.create_task(self._cooldown_timer())

    async def _cooldown_timer(self):
        try:
            await asyncio.sleep(self.COOLDOWN_SECONDS)
        except asyncio.CancelledError:
            return
        self._idle.set()

    def _cancel_cooldown(self):
        if self._cooldown_task and not self._cooldown_task.done():
            self._cooldown_task.cancel()
        self._cooldown_task = None

    async def wait_until_idle(self):
        """Block until the gate is open. Returns immediately if already IDLE."""
        await self._idle.wait()


# ──────────────────────────────────────────────────────────────────────────────
# GATE RAISE-HAND — if a gated tts.speak waits >10s for the human to stop
# talking, politely raise the bot's hand to signal "I have something to say."
#
# Armed by forward_tts_with_gate before awaiting the BargeInState; cancelled
# in the finally when the gate opens. The lock around forward_tts_with_gate
# naturally limits this to one raise per locked window — only the tts.speak
# holding the lock awaits the gate; subsequent queued tts.speaks wait on
# the lock and find the gate IDLE when their turn comes (if the user has
# stopped). So a "batch" of queued tts.speaks during one user-talking
# window produces at most one raise_hand. If the user starts a NEW
# monologue later, the next queued tts.speak's timer arms fresh —
# allowing one more raise_hand for that new locked window.
#
# In bridge-visual (with_avatar_state=True), the timer also flips the
# avatar to "waiting_to_speak" so the visual matches. Last-write-wins:
# any subsequent agent set_state or backend auto-state overrides this.
# In bridge.py audio mode (no avatar), only the raise_hand is sent.
# ──────────────────────────────────────────────────────────────────────────────

class GateRaiseHand:
    """Raises the bot's hand if the barge-in gate stays locked >DELAY_SECONDS."""

    DELAY_SECONDS = 10.0

    def __init__(self, client: "APIClient", with_avatar_state: bool = False):
        self._client = client
        self._with_avatar_state = with_avatar_state
        self._task: Optional[asyncio.Task] = None

    def arm(self):
        """Start the timer. Cancels any prior timer (defensive)."""
        self._cancel_task()
        self._task = asyncio.create_task(self._fire_after_delay())

    def cancel(self):
        """Gate opened (or call ended) before timer fired — don't raise."""
        self._cancel_task()

    async def _fire_after_delay(self):
        try:
            await asyncio.sleep(self.DELAY_SECONDS)
        except asyncio.CancelledError:
            return
        await self._client.send({"type": "meeting.raise_hand"})
        if self._with_avatar_state:
            await self._client.send(
                {"type": "voice.state_update", "state": "waiting_to_speak"}
            )

    def _cancel_task(self):
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None


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

    async def create_call(self, meet_url: str, bot_name: str,
                          max_duration: int = 0, alone_timeout: int = 0,
                          silence_timeout: int = 0) -> dict:
        session = await self._get_session()
        params = {
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "audio",
            "voice_strategy": "direct",
            "transcription": True,
        }
        if max_duration > 0:
            params["max_duration"] = max_duration
        if alone_timeout > 0:
            params["alone_timeout"] = alone_timeout
        if silence_timeout > 0:
            params["silence_timeout"] = silence_timeout
        async with session.post(f"{API_BASE}/v1/calls", json=params) as resp:
            if resp.status != 201:
                body = await resp.text()
                raise Exception(f"Create call failed ({resp.status}): {body}")
            return await resp.json()

    async def connect_ws(self, call_id: str):
        ws_url = API_BASE.replace("https://", "wss://").replace("http://", "ws://")
        uri = f"{ws_url}/v1/calls/{call_id}/ws?api_key={API_KEY}"
        self.ws = await websockets.connect(uri)
        return self.ws

    async def check_call_active(self, call_id: str) -> tuple:
        """Check if call is still active via HTTP API. Returns (active, reason)."""
        try:
            session = await self._get_session()
            async with session.get(f"{API_BASE}/v1/calls/{call_id}") as resp:
                if resp.status != 200:
                    return False, "call_not_found"
                data = await resp.json()
                status = data.get("status", "")
                if status in ("ended", "error"):
                    return False, data.get("end_reason", status)
                return True, ""
        except Exception:
            return False, "api_unreachable"

    async def reconnect_ws(self, call_id: str) -> bool:
        """Reconnect WebSocket with exponential backoff. Returns True on success."""
        delays = [1, 5, 10, 30]
        for i, delay in enumerate(delays):
            emit_err(f"WebSocket reconnecting in {delay}s (attempt {i + 1}/{len(delays)})...")
            await asyncio.sleep(delay)
            # Check if call is still active before reconnecting
            active, reason = await self.check_call_active(call_id)
            if not active:
                emit_err(f"Call no longer active: {reason}")
                return False
            try:
                await self.connect_ws(call_id)
                emit_err("WebSocket reconnected successfully")
                return True
            except Exception as e:
                emit_err(f"Reconnect attempt {i + 1} failed: {e}")
        return False

    async def send(self, command: dict):
        """Send with automatic retry on transient errors (e.g. WS reconnect window).
        Retries up to 3 times with exponential backoff. Logs drop to stderr if all fail."""
        for attempt in range(3):
            try:
                if self.ws:
                    await self.ws.send(json.dumps(command))
                    return True
            except Exception as e:
                emit_err(f"send failed (attempt {attempt + 1}/3): {e}")
                await asyncio.sleep(0.5 * (attempt + 1))
        emit_err(f"dropped command after 3 failures: {command.get('type', '?')}")
        return False

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

async def read_stdin(client: APIClient, done_event: asyncio.Event,
                     batch_queue: deque,
                     barge_in: "BargeInState" = None,
                     sent_chats: deque = None,
                     gate_raise_hand: "GateRaiseHand" = None):
    """Read commands from agent framework and forward to AgentCall.

    Includes barge-in prevention: tts.speak waits for the BargeInState to
    return to IDLE before sending. The gate is non-blocking with respect to
    OTHER commands — every tts.speak is dispatched as a background task that
    acquires a TTS-only lock, waits on the state machine, then forwards.
    Meanwhile send_chat / raise_hand / mic / screenshot / leave continue to
    be processed inline. Multiple tts.speak commands stay in the order the
    agent sent them (the lock serializes them) so the agent's mental model
    is preserved.

    Uses a daemon thread with blocking sys.stdin.readline() + asyncio.Queue for
    cross-platform compatibility (asyncio.connect_read_pipe is broken on Windows
    per CPython issue #71019). Latency is sub-millisecond on all platforms.
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    # ── TTS dispatcher (non-blocking gate) ──
    # tts_lock serializes tts.speak forwards so the agent's ordering survives.
    # pending_tts holds task refs so they aren't GC'd before completion (per
    # asyncio.create_task docs — tasks weakly referenced by the event loop
    # can otherwise be collected mid-flight).
    tts_lock = asyncio.Lock()
    pending_tts: set = set()

    async def forward_tts_with_gate(payload: dict):
        async with tts_lock:
            # Barge-in gate via state machine (see BargeInState above). We
            # block on the IDLE event — zero polling — and the event flips
            # the moment STT fires a final + the cooldown elapses.
            if barge_in is not None:
                if gate_raise_hand is not None:
                    gate_raise_hand.arm()
                try:
                    await barge_in.wait_until_idle()
                finally:
                    if gate_raise_hand is not None:
                        gate_raise_hand.cancel()
            if done_event.is_set():
                return
            await client.send(payload)

    def schedule_tts(payload: dict):
        task = asyncio.create_task(forward_tts_with_gate(payload))
        pending_tts.add(task)
        task.add_done_callback(pending_tts.discard)

    def reader_thread():
        while not done_event.is_set():
            try:
                line = sys.stdin.readline()
            except Exception:
                break
            if not line:
                # EOF — signal the consumer by pushing a sentinel.
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
                break  # EOF

            try:
                cmd = json.loads(line.strip())
            except json.JSONDecodeError:
                continue

            command = cmd.get("command", "")

            if command == "tts.speak":
                # Sanitize + sentence-split. Multi-sentence text becomes N
                # backend tts.speaks for pipelined Kokoro synthesis; the run_bridge
                # event loop aggregates the N backend tts.done events into ONE
                # tts.done back to the agent (see batch_queue handling below).
                # Single-sentence text bypasses the queue and forwards as today.
                text = _sanitize_tts_text(cmd.get("text", ""))
                sentences = _split_sentences(text)
                voice = cmd.get("voice", "af_heart")
                speed = cmd.get("speed", 1.0)
                if not sentences:
                    # Empty after sanitize — emit synthetic done so the agent
                    # isn't stuck waiting for a terminal event.
                    emit({"event": "tts.done"})
                elif len(sentences) == 1:
                    schedule_tts({
                        "type": "tts.speak",
                        "text": sentences[0],
                        "voice": voice,
                        "speed": speed,
                    })
                else:
                    batch_queue.append({
                        "expected": len(sentences),
                        "received": 0,
                        "created_at": time.time(),
                    })
                    for sentence in sentences:
                        schedule_tts({
                            "type": "tts.speak",
                            "text": sentence,
                            "voice": voice,
                            "speed": speed,
                        })

            elif command == "send_chat":
                # Send a text message in the meeting chat.
                # Useful for: URLs, code snippets, emails, anything hard to speak.
                msg_text = cmd.get("message", "")
                # Track sent chat so we can suppress its echo when it bounces
                # back via FirstCall as a chat.message event. ADD before forward
                # so the echo always finds an entry to consume — see chat.message
                # handler below for the matching pop-on-match logic.
                if sent_chats is not None and msg_text:
                    sent_chats.append(msg_text)
                await client.send({
                    "type": "meeting.send_chat",
                    "message": msg_text,
                })

            elif command == "raise_hand":
                # Raise the bot's hand in the meeting.
                # Useful to signal the agent wants to speak in group meetings.
                await client.send({
                    "type": "meeting.raise_hand",
                })

            elif command == "mic":
                # Mute/unmute/toggle the bot's microphone.
                # Useful when the bot joins muted in a large group meeting.
                # Action: "on" (unmute, default), "off" (mute), "toggle" (flip state).
                action = cmd.get("action", "on")
                await client.send({
                    "type": "meeting.mic",
                    "action": action,
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

async def run_bridge(meet_url: str, bot_name: str, voice: str, vad_timeout: float,
                     max_duration: int = 0, alone_timeout: int = 0, silence_timeout: int = 0):
    """Main bridge loop."""
    client = APIClient()
    done = asyncio.Event()

    # ── Create call ──
    emit_err(f"Creating call for: {meet_url}")
    try:
        call = await client.create_call(meet_url, bot_name,
                                        max_duration=max_duration,
                                        alone_timeout=alone_timeout,
                                        silence_timeout=silence_timeout)
    except Exception as e:
        emit({"event": "error", "message": str(e)})
        await client.close()
        return

    call_id = call["call_id"]
    emit_err(f"Call created: {call_id}")
    emit({"event": "call.created", "call_id": call_id, "status": call.get("status", "")})

    # ── Set up VAD buffer ──
    vad = VADBuffer(cooldown=vad_timeout)

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

    # ── Barge-in state machine ──
    # Three states (IDLE / WAITING_FOR_FINAL / COOLDOWN) driven by
    # transcript.partial and transcript.final events from FirstCall. Gate
    # is open only in IDLE. read_stdin's TTS dispatcher awaits this.
    barge_in = BargeInState()

    # ── Echo suppression for outbound chat ──
    # FirstCall echoes our own chat back as chat.message events. Without this,
    # the agent would see its own send_chat replayed as chat.received. Filtering
    # by sender == bot_name alone is wrong — it drops legit human chat from
    # participants who happen to share the bot's display name. We instead match
    # on (sender == bot AND text equals something we just sent), with pop-on-
    # match so each outbound chat consumes exactly one echo. maxlen=5 is
    # plenty: FirstCall echoes within ~2-3s; entries don't need to live longer.
    sent_chats: deque = deque(maxlen=5)

    # ── Gate raise-hand ──
    # Audio mode has no avatar — only raise_hand fires (no voice.state_update).
    gate_raise_hand = GateRaiseHand(client, with_avatar_state=False)

    # ── Sentence-batch queue ──
    # Multi-sentence tts.speak from the agent is split into N backend tts.speaks
    # for pipelined Kokoro synthesis. Each batch entry tracks the expected vs.
    # received count of backend tts.done events; when balanced, ONE aggregated
    # tts.done is forwarded to the agent (matching the agent's 1:1 mental model
    # of tts.speak → tts.done). FIFO since the backend ttsQueue + ttsWorker is
    # FIFO. Cleared on tts.interrupted / tts.error. Single-sentence tts.speaks
    # bypass this queue entirely (passthrough). See read_stdin tts.speak handler.
    batch_queue: deque = deque()

    # ── Start stdin reader ──
    stdin_task = asyncio.create_task(read_stdin(
        client, done, batch_queue, barge_in, sent_chats, gate_raise_hand))

    # ── Periodic batch timeout (safety net) ──
    # If a multi-sentence batch hasn't completed in 60s — e.g., backend's
    # ttsQueue dropped a sentence silently on overflow — emit tts.error for
    # all pending batches and clear the queue. Prevents permanent deadlock.
    # Stale backend tts.done events arriving after a timed-out batch are
    # cleared then flow through the single-sentence passthrough; this is an
    # accepted minor noise artifact (no functional impact).
    async def _batch_timeout_check():
        while not done.is_set():
            try:
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                return
            if not batch_queue:
                continue
            now = time.time()
            if now - batch_queue[0]["created_at"] > 60:
                count = len(batch_queue)
                emit_err(f"tts batch timeout after 60s — aborting {count} pending batches")
                for _ in range(count):
                    emit({"event": "tts.error", "reason": "tts_timeout"})
                batch_queue.clear()
    batch_timeout_task = asyncio.create_task(_batch_timeout_check())

    # ── Track state ──
    bot_name_lower = bot_name.lower()
    is_speaking = False
    greeted = False
    participants = set()

    # ── Process events (with reconnection) ──
    while not done.is_set():
        try:
            async for msg in ws:
                if done.is_set():
                    break

                event = json.loads(msg)
                event_type = event.get("event", event.get("type", ""))

                # ── Bot lifecycle ──
                if event_type == "call.bot_joining_meeting":
                    detail = event.get("detail", "")
                    emit({"event": "call.bot_joining_meeting", "call_id": call_id, "detail": detail})
                    emit_err(f"Bot joining meeting ({detail})")

                elif event_type == "call.bot_waiting_room":
                    emit({"event": "call.bot_waiting_room", "call_id": call_id})
                    emit_err("Bot is in the waiting room — waiting to be admitted")

                elif event_type == "call.bot_ready":
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

                    # Drive the barge-in state machine: STT just decided the
                    # utterance ended → start cooldown timer.
                    barge_in.on_final()

                    # FirstCall does not transcribe bot audio — every transcript
                    # event is from a human. We deliberately do NOT filter by
                    # speaker.name == bot_name here: a participant who happens
                    # to share the bot's display name is still a real human and
                    # the agent must hear them.
                    if not text:
                        continue

                    # Feed to VAD state machine — emits user.message after the cooldown
                    vad.on_transcript_final(speaker, text)

                # ── Transcript partial ──
                elif event_type == "transcript.partial":
                    speaker_obj = event.get("speaker", {})
                    if isinstance(speaker_obj, dict):
                        speaker = speaker_obj.get("name", "Unknown")
                    else:
                        speaker = str(speaker_obj)

                    # Drive the barge-in state machine: STT detected speech
                    # → lock the gate, cancel any pending cooldown.
                    barge_in.on_partial()

                    # Tell VAD buffer the user is still speaking
                    vad.on_transcript_partial(speaker, event.get("text", ""))

                # ── Chat message received ──
                elif event_type == "chat.message":
                    sender = event.get("sender", "Unknown")
                    message = event.get("message", "")
                    if not message:
                        pass  # nothing to emit
                    elif sender.lower() == bot_name_lower and message in sent_chats:
                        # Echo of our own outbound chat — suppress and consume one
                        # entry so a subsequent legit human chat with the same
                        # text passes through correctly.
                        sent_chats.remove(message)
                    else:
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
                    # Multi-sentence batch aggregation: decrement the head batch's
                    # received count; emit ONE tts.done to agent only when
                    # received == expected. If batch_queue is empty, this is a
                    # single-sentence passthrough (or a stray done after a cleared
                    # batch — accepted noise per design).
                    if batch_queue:
                        entry = batch_queue[0]
                        entry["received"] += 1
                        if entry["received"] >= entry["expected"]:
                            batch_queue.popleft()
                            emit({"event": "tts.done"})
                    else:
                        emit({"event": "tts.done"})

                elif event_type == "tts.error":
                    is_speaking = False
                    emit({"event": "tts.error", "reason": event.get("reason", "unknown")})
                    batch_queue.clear()  # tts.error terminates all pending batches

                elif event_type == "tts.interrupted":
                    is_speaking = False
                    emit({
                        "event": "tts.interrupted",
                        "reason": event.get("reason", "user_speaking"),
                        "sentence_index": event.get("sentence_index", -1),
                        "elapsed_ms": event.get("elapsed_ms", 0),
                    })
                    batch_queue.clear()  # tts.interrupted terminates all pending batches

                # ── Warnings ──
                elif event_type == "call.max_duration_warning":
                    emit({
                        "event": "call.max_duration_warning",
                        "minutes_remaining": event.get("minutes_remaining", 5),
                    })
                    emit_err(f"Warning: call will end in {event.get('minutes_remaining', 5)} minutes (max duration)")

                elif event_type == "call.credits_low":
                    emit({
                        "event": "call.credits_low",
                        "balance_microcents": event.get("balance_microcents", 0),
                        "estimated_minutes_remaining": event.get("estimated_minutes_remaining", 0),
                    })
                    emit_err(f"Warning: credits low — estimated {event.get('estimated_minutes_remaining', 0)} minutes remaining")

                # ── Call ended ──
                elif event_type == "call.ended":
                    reason = event.get("reason", "unknown")
                    emit({"event": "call.ended", "reason": reason})
                    emit_err(f"Call ended: {reason}")
                    done.set()
                    break

            # If we exited the for loop without done being set, WS closed gracefully
            if not done.is_set():
                raise websockets.exceptions.ConnectionClosed(None, None)

        except websockets.exceptions.ConnectionClosed:
            if done.is_set():
                break
            emit_err("WebSocket disconnected, checking call status...")
            if await client.reconnect_ws(call_id):
                ws = client.ws
                emit_err("Resuming event stream")
                continue
            else:
                emit({"event": "call.ended", "reason": "connection_lost"})
                emit_err("WebSocket reconnection failed — call ended")
                break
        except Exception as e:
            emit({"event": "error", "message": str(e)})
            emit_err(f"Error: {e}")
            break

    # ── Cleanup ──
    await vad.flush()
    stdin_task.cancel()
    batch_timeout_task.cancel()
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
        "--vad-timeout", type=float, default=1.25,
        help="Cooldown seconds after the most recent transcript.final before emitting "
             "the buffered utterance. A new partial cancels the cooldown (user resumed). "
             "Raise for slow speakers, lower for fast back-and-forth. (default: 1.25)"
    )
    parser.add_argument("--output", default="",
        help="Also write events to this file (for file-based polling). "
             "Events go to both stdout AND this file."
    )
    parser.add_argument("--max-duration", type=int, default=0,
        help="Max call duration in minutes (default: plan limit). Cannot exceed plan limit."
    )
    parser.add_argument("--alone-timeout", type=int, default=0,
        help="Leave if alone for N seconds (default: 120). Set 0 for plan default."
    )
    parser.add_argument("--silence-timeout", type=int, default=0,
        help="Leave if silent for N seconds (default: 300). Set 0 for plan default."
    )
    args = parser.parse_args()

    global _output_file
    if args.output:
        _output_file = args.output
        emit_err(f"Events also writing to: {_output_file}")

    asyncio.run(run_bridge(
        args.meet_url, args.name, args.voice, args.vad_timeout,
        max_duration=args.max_duration * 60000 if args.max_duration > 0 else 0,
        alone_timeout=args.alone_timeout * 1000 if args.alone_timeout > 0 else 0,
        silence_timeout=args.silence_timeout * 1000 if args.silence_timeout > 0 else 0,
    ))


if __name__ == "__main__":
    main()
