#!/usr/bin/env python3
"""
AgentCall — Visual Voice Bridge with Screenshare

Like bridge.py but with visual presence + screenshare capability.
The bot joins with an animated avatar (voice states visible to participants)
and can screenshare any URL into the meeting.

Uses webpage-av-screenshare mode. By default starts a local avatar template
server and tunnels it to the cloud — no manual setup needed.

Everything from bridge.py is included:
  - VAD coalescing (state machine), chat I/O, raise hand, screenshots, graceful exit

Additional features:
  - Bot has a visual avatar (7 voice states: listening, speaking, etc.)
  - Agent can screenshare public URLs or local ports into the meeting
  - Screenshare can be started/stopped dynamically during the call
  - Tunnel client runs automatically for local UI and screenshare

PROTOCOL (extends bridge.py):

  Additional stdout events:
    {"event": "screenshare.started", "url": "https://..."}
    {"event": "screenshare.stopped"}
    {"event": "screenshare.error", "message": "Failed to load URL"}

  Additional stdin commands:
    {"command": "screenshare.start", "url": "https://slides.google.com/..."}
    {"command": "screenshare.start", "port": 3001}
    {"command": "screenshare.swap", "port": 3002}             — atomic stop+start
    {"command": "screenshare.swap", "url": "https://..."}    — atomic stop+start
    {"command": "screenshare.stop"}

Usage:
    export AGENTCALL_API_KEY="ak_ac_your_key"

    # With built-in avatar template (starts local server + tunnel automatically)
    python bridge-visual.py "https://meet.google.com/abc" --name "Claude"

    # With public webpage as bot's video feed (no tunnel needed)
    python bridge-visual.py "https://meet.google.com/abc" --webpage-url "https://your-site.com/avatar"

    # With custom local UI on port 3000 (tunnel auto-started)
    python bridge-visual.py "https://meet.google.com/abc" --ui-port 3000

Dependencies:
    pip install aiohttp websockets
"""

import argparse
import asyncio
import json
import os
import socket
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
# SCREENSHARE HELPERS
#
# These exist because FirstCall's headless browser caches the screenshare URL
# aggressively — a swap from one local port to another keeps showing the OLD
# content because the URL (https://tunnel/screenshare/) doesn't change.
#
# Cache-buster: append ?_acv=<ms> so every start is a fresh URL.
# Pre-flight: TCP-probe the local port before sending start, so a dead port
#             produces a clear screenshare.error instead of a silent white page.
# State tracking: lets screenshare.swap wait for FirstCall to confirm the
#                 previous screenshare has stopped before issuing the new start
#                 (eliminates race where start arrives before stop is processed).
# ──────────────────────────────────────────────────────────────────────────────

def _is_port_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    """Quick TCP probe — is something listening on host:port?"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def _cache_busted_url(base: str) -> str:
    """Append a millisecond timestamp as ?_acv= so FirstCall's browser reloads.
    Handles hash fragments correctly: per RFC 3986, query must precede fragment.
    Only used for the local tunnel URL — never for external URLs (would break
    signed URLs like S3/CloudFront/Vimeo where the signature includes the query)."""
    fragment = ""
    if "#" in base:
        base, frag = base.split("#", 1)
        fragment = "#" + frag
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}_acv={int(time.time() * 1000)}{fragment}"


class ScreenshareState:
    """Tracks screenshare lifecycle so screenshare.swap can wait for stop confirmation."""

    def __init__(self):
        self.active = False
        self._stopped_event = asyncio.Event()
        self._stopped_event.set()  # initially stopped → wait_stopped() returns immediately

    def mark_starting(self):
        """Bridge issued screenshare.start — active until FirstCall confirms stop."""
        self.active = True
        self._stopped_event.clear()

    def mark_stopped(self):
        """FirstCall confirmed screenshare.stopped (or error) — wake any swap waiters."""
        self.active = False
        self._stopped_event.set()

    async def wait_stopped(self, timeout: float = 5.0) -> bool:
        """Block until FirstCall confirms stop, or timeout. Returns True if confirmed."""
        try:
            await asyncio.wait_for(self._stopped_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False


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
# AUTO-THINKING — broadcasts voice.state=thinking on every user.message so the
# avatar shows visible feedback during the gap between "user finished" and
# "bot starts answering." Without this, the avatar sits at "listening" the
# whole time the agent is processing and the user thinks the bot is dead.
#
# Three triggers clear the thinking state:
#   - tts.speak from agent → cancel timer silently. The backend's auto
#     voice.state=speaking on tts.speak start will overwrite the visual.
#   - set_state from agent → cancel timer silently. The agent took explicit
#     control; their state is already going through.
#   - any other agent command (send_chat / screenshare.* / webpage.* /
#     mic / raise_hand / leave) → cancel timer + broadcast voice.state=
#     listening. The command has no own visual, so we explicitly clear.
#   - 10s timeout → broadcast voice.state=listening. Catches the silent-
#     observer / notetaker case and stuck-agent recovery.
#
# screenshot is intentionally NOT a clear trigger — it's a data-gathering
# input, often part of the agent's thinking process.
# ──────────────────────────────────────────────────────────────────────────────

class AutoThinking:
    """Auto-broadcasts voice.state=thinking on user.message; clears on next
    agent activity or after a fallback timeout."""

    TIMEOUT_SECONDS = 10.0

    def __init__(self, client: "APIClient"):
        self._client = client
        self._task: Optional[asyncio.Task] = None
        self._active = False  # True iff thinking has been set and not yet cleared

    async def trigger(self):
        """Broadcast thinking + (re)start the 10s clear timer."""
        self._cancel_task()
        self._active = True
        await self._client.send({"type": "voice.state_update", "state": "thinking"})
        self._task = asyncio.create_task(self._clear_after_timeout())

    async def _clear_after_timeout(self):
        try:
            await asyncio.sleep(self.TIMEOUT_SECONDS)
        except asyncio.CancelledError:
            return
        self._task = None
        if self._active:
            self._active = False
            await self._client.send({"type": "voice.state_update", "state": "listening"})

    def cancel_silent(self):
        """Caller will set its own visual (tts.speak via backend, or set_state)."""
        self._cancel_task()
        self._active = False

    async def cancel_and_clear(self):
        """Caller has no own visual; broadcast listening if we set thinking."""
        was_active = self._active
        self._cancel_task()
        self._active = False
        if was_active:
            await self._client.send({"type": "voice.state_update", "state": "listening"})

    def _cancel_task(self):
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None


# ──────────────────────────────────────────────────────────────────────────────
# GATE RAISE-HAND — see bridge.py source for the full block-comment design
# rationale. If a gated tts.speak waits >10s for the human to stop talking,
# politely raise the bot's hand. In bridge-visual mode (with_avatar_state=
# True), also flip the avatar to "waiting_to_speak". Last-write-wins:
# subsequent agent set_state or backend auto-state overrides the avatar
# state; the raised hand stays raised (no lower_hand command exists).
#
# The lock around forward_tts_with_gate naturally limits this to one
# raise per locked window — only the tts.speak holding the lock awaits
# the gate; queued tts.speaks find the gate IDLE when their turn comes.
# ──────────────────────────────────────────────────────────────────────────────

class GateRaiseHand:
    """Raises the bot's hand (and optionally flips avatar to waiting_to_speak)
    if the barge-in gate stays locked >DELAY_SECONDS."""

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
                          webpage_url: str = "", screenshare_url: str = "",
                          ui_port: int = 0, screenshare_port: int = 0,
                          max_duration: int = 0, alone_timeout: int = 0,
                          silence_timeout: int = 0) -> dict:
        params = {
            "meet_url": meet_url,
            "bot_name": bot_name,
            "mode": "webpage-av-screenshare",
            "voice_strategy": "direct",
            "transcription": True,
        }
        if webpage_url:
            params["webpage_url"] = webpage_url
        if screenshare_url:
            params["screenshare_url"] = screenshare_url
        if max_duration > 0:
            params["max_duration"] = max_duration
        if alone_timeout > 0:
            params["alone_timeout"] = alone_timeout
        if silence_timeout > 0:
            params["silence_timeout"] = silence_timeout
        if ui_port:
            params["ui_port"] = ui_port
        if screenshare_port:
            params["screenshare_port"] = screenshare_port

        session = await self._get_session()
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
# TEMPLATE SERVER
#
# Starts a local HTTP server to serve built-in UI templates.
# The template page is injected with query params (ws, name) so it can
# connect back to AgentCall's WebSocket for voice state + audio events.
# ──────────────────────────────────────────────────────────────────────────────

class TemplateServer:
    """Local HTTP server that serves a UI template with dynamic WS config.
    Also exposes /tasks.json — the in-memory list of work-in-progress tasks
    set by the agent via tasks.set, polled by the avatar template every 2s."""

    def __init__(self, template_dir: str, shared_js_path: str):
        self.template_dir = template_dir
        self.shared_js_path = shared_js_path
        self.ws_url = ""
        self.bot_name = "Agent"
        # Agent's current task list (max 3 strings, 30 chars each — validated
        # in read_stdin's tasks.set handler before write). Polled by templates
        # via GET /tasks.json (relative path, served through the tunnel as
        # /ui/tasks.json from the cloud's perspective).
        self.current_tasks: list[str] = []

    def set_ws_url(self, url: str):
        self.ws_url = url

    def set_bot_name(self, name: str):
        self.bot_name = name

    async def handle_index(self, request):
        """Serve index.html. The backend appends ?ws= and &name= to the URL
        that FirstCall loads, so the template reads them from window.location.search."""
        from aiohttp import web
        index_path = os.path.join(self.template_dir, "index.html")
        if not os.path.exists(index_path):
            return web.Response(status=404, text="Template not found")
        with open(index_path, "r") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")

    async def handle_shared_js(self, request):
        """Serve the shared agentcall-audio.js file."""
        from aiohttp import web
        if os.path.exists(self.shared_js_path):
            with open(self.shared_js_path, "r") as f:
                return web.Response(text=f.read(), content_type="application/javascript")
        return web.Response(status=404)

    async def handle_tasks(self, request):
        """Serve the agent's current task list as JSON."""
        from aiohttp import web
        return web.json_response({"tasks": self.current_tasks})

    async def handle_static(self, request):
        """Serve other static files from the template directory."""
        from aiohttp import web
        filename = request.match_info.get("filename", "")
        filepath = os.path.realpath(os.path.join(self.template_dir, filename))
        # Prevent path traversal — file must be inside template directory
        if not filepath.startswith(os.path.realpath(self.template_dir)):
            return web.Response(status=403, text="Forbidden")
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return web.FileResponse(filepath)
        return web.Response(status=404)


async def start_template_server(template_name: str):
    """Start a local HTTP server for a built-in template. Returns (server, port)."""
    from aiohttp import web

    # Find templates relative to this script: ../../ui-templates/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    templates_base = os.path.join(script_dir, "..", "..", "ui-templates")
    template_dir = os.path.join(templates_base, template_name)
    shared_js = os.path.join(templates_base, "agentcall-audio.js")

    if not os.path.isdir(template_dir):
        emit_err(f"Template '{template_name}' not found at {template_dir}")
        return None, 0

    server = TemplateServer(template_dir, shared_js)
    app = web.Application()
    app.router.add_get("/", server.handle_index)
    # Serve agentcall-audio.js at the path the templates expect (../agentcall-audio.js)
    app.router.add_get("/../agentcall-audio.js", server.handle_shared_js)
    app.router.add_get("/agentcall-audio.js", server.handle_shared_js)
    # Tasks endpoint — polled by the avatar template every 2s for live work-
    # in-progress display. Registered BEFORE the catch-all /{filename} route.
    app.router.add_get("/tasks.json", server.handle_tasks)
    app.router.add_get("/{filename:.+}", server.handle_static)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    # Use port 0 to get a random available port.
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    return server, port


# ──────────────────────────────────────────────────────────────────────────────
# TUNNEL CLIENT
#
# Connects to AgentCall's tunnel server via WebSocket and proxies HTTP requests
# from FirstCall's browser back to the local template/UI server.
# ──────────────────────────────────────────────────────────────────────────────

class BridgeTunnelClient:
    """Inline tunnel client for bridge-visual — proxies HTTP via WS."""

    def __init__(self, tunnel_ws_url: str, tunnel_id: str, access_key: str,
                 ui_port: int, screenshare_port: int = 0):
        self.tunnel_ws_url = tunnel_ws_url
        self.tunnel_id = tunnel_id
        self.access_key = access_key
        self.ui_port = ui_port
        self.screenshare_port = screenshare_port
        self.webpage_port = 0
        self._ws = None
        self._running = False

    async def connect(self):
        """Connect to tunnel server and register."""
        import base64 as b64
        self._running = True
        self._ws = await websockets.connect(self.tunnel_ws_url)
        # Send registration with tunnel_access_key (NOT the API key).
        await self._ws.send(json.dumps({
            "type": "tunnel.register",
            "payload": {
                "tunnel_id": self.tunnel_id,
                "tunnel_access_key": self.access_key,
            },
        }))
        emit_err(f"Tunnel client connected (tunnel_id={self.tunnel_id[:8]}...)")
        asyncio.create_task(self._read_loop())
        asyncio.create_task(self._heartbeat())

    def _resolve_local_url(self, path: str) -> str:
        """Route to correct local port based on path prefix."""
        if path.startswith("/screenshare") and self.screenshare_port:
            local_path = path[len("/screenshare"):] or "/"
            return f"http://localhost:{self.screenshare_port}{local_path}"
        if path.startswith("/webpage") and self.webpage_port:
            local_path = path[len("/webpage"):] or "/"
            return f"http://localhost:{self.webpage_port}{local_path}"
        if path.startswith("/ui"):
            local_path = path[len("/ui"):] or "/"
            return f"http://localhost:{self.ui_port}{local_path}"
        return f"http://localhost:{self.ui_port}{path}"

    async def _read_loop(self):
        try:
            async for message in self._ws:
                msg = json.loads(message)
                msg_type = msg.get("type", "")
                if msg_type == "http.request":
                    asyncio.create_task(self._handle_http(msg))
                elif msg_type == "tunnel.error":
                    error_msg = msg.get("message", "unknown tunnel error")
                    emit_err(f"TUNNEL ERROR: {error_msg}")
                    emit({"event": "error", "message": f"Tunnel: {error_msg}"})
        except websockets.ConnectionClosed:
            if self._running:
                emit_err("Tunnel connection lost")

    async def _handle_http(self, msg: dict):
        payload = msg.get("payload", msg)
        request_id = payload.get("request_id", msg.get("request_id", ""))
        method = payload.get("method", "GET")
        path = payload.get("path", "/")
        headers = payload.get("headers", {})
        body = payload.get("body", "")

        local_url = self._resolve_local_url(path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, local_url, headers=headers,
                                           data=body if body else None) as resp:
                    resp_body = await resp.text()
                    resp_headers = {k: v for k, v in resp.headers.items()}
                    response = {
                        "type": "http.response",
                        "request_id": request_id,
                        "payload": {
                            "request_id": request_id,
                            "status": resp.status,
                            "headers": resp_headers,
                            "body": resp_body,
                        },
                    }
                    await self._ws.send(json.dumps(response))
        except Exception as e:
            response = {
                "type": "http.response",
                "request_id": request_id,
                "payload": {
                    "request_id": request_id,
                    "status": 502,
                    "headers": {"Content-Type": "text/plain"},
                    "body": f"Local server error: {e}",
                },
            }
            await self._ws.send(json.dumps(response))

    async def _heartbeat(self):
        while self._running and self._ws and not self._ws.closed:
            try:
                await asyncio.sleep(30)
                if self._ws and not self._ws.closed:
                    await self._ws.ping()
            except Exception:
                break

    async def close(self):
        self._running = False
        if self._ws:
            await self._ws.close()


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
                     pending_tts: set,
                     batch_queue: deque,
                     tunnel_client: BridgeTunnelClient = None, tunnel_base_url: str = "",
                     barge_in: "BargeInState" = None,
                     screenshare_state: ScreenshareState = None,
                     sent_chats: deque = None,
                     auto_thinking: "AutoThinking" = None,
                     gate_raise_hand: "GateRaiseHand" = None,
                     template_server: "TemplateServer" = None):
    """Read commands from agent framework and forward to AgentCall.

    Includes barge-in prevention: tts.speak waits for the BargeInState to
    return to IDLE before sending. The gate is non-blocking with respect to
    OTHER commands — every tts.speak is dispatched as a background task that
    acquires a TTS-only lock, waits on the state machine, then forwards.
    Meanwhile send_chat / screenshare.* / webpage.* / set_state / mic / etc.
    continue to be processed inline. Multiple tts.speak commands stay in the
    order the agent sent them (the lock serializes them) so the agent's
    mental model is preserved.

    Uses a daemon thread with blocking sys.stdin.readline() + asyncio.Queue for
    cross-platform compatibility (asyncio.connect_read_pipe is broken on Windows
    per CPython issue #71019). Latency is sub-millisecond on all platforms.
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    # ── TTS dispatcher (non-blocking gate) ──
    # tts_lock serializes tts.speak forwards so the agent's ordering survives.
    # pending_tts (passed in by run_bridge) holds task refs so they aren't
    # GC'd before completion (per asyncio.create_task docs — tasks weakly
    # referenced by the event loop can otherwise be collected mid-flight).
    # Shared with run_bridge so its tts.interrupted handler can cancel
    # queued tasks when the user confirms an interrupt.
    tts_lock = asyncio.Lock()

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

            # Auto-thinking cleanup: any agent activity ends the thinking
            # state set by on_user_complete. tts.speak / set_state cancel
            # silently (their own visual takes over); other commands cancel
            # AND broadcast listening (no own visual). screenshot is a data-
            # gathering input — leave thinking active.
            if auto_thinking is not None:
                if command in ("tts.speak", "set_state"):
                    auto_thinking.cancel_silent()
                elif command in ("send_chat", "screenshare.start", "screenshare.stop",
                                 "screenshare.swap", "webpage.open", "webpage.close",
                                 "raise_hand", "mic", "leave"):
                    await auto_thinking.cancel_and_clear()

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
                await client.send({
                    "type": "screenshot.take",
                    "request_id": cmd.get("request_id", "screenshot"),
                })

            elif command == "screenshare.start":
                # Start screensharing. Accepts either:
                #   {"command": "screenshare.start", "url": "https://..."}  — public URL
                #   {"command": "screenshare.start", "port": 3001}          — local port via tunnel
                url = cmd.get("url", "")
                port = cmd.get("port", 0)
                if port and tunnel_client and tunnel_base_url:
                    # Pre-flight: confirm something is actually listening locally.
                    # Catches the "white screen" failure mode where the agent forgot
                    # to start its HTTP server, or killed it before sending start.
                    if not _is_port_reachable("127.0.0.1", port):
                        emit({"event": "screenshare.error",
                              "message": f"localhost:{port} is not reachable. Is your local server running?"})
                        continue
                    tunnel_client.screenshare_port = port
                    url = _cache_busted_url(tunnel_base_url + "/screenshare/")
                    emit_err(f"Screenshare tunneling localhost:{port}")
                # External URLs are passed through as-is. Cache-busting is applied
                # only to the local tunnel URL because that URL is byte-identical
                # across swaps (FirstCall's browser would otherwise see "same URL —
                # don't reload" and keep showing the old content). Two different
                # external URLs in a swap are already different, so the browser
                # reloads naturally. Appending ?_acv would also break signed URLs
                # (S3 pre-signed, Vimeo private, Power BI secure embed, etc.).
                if url:
                    if screenshare_state:
                        screenshare_state.mark_starting()
                    await client.send({
                        "type": "screenshare.start",
                        "url": url,
                    })
                else:
                    emit({"event": "screenshare.error", "message": "screenshare.start requires 'url' or 'port'"})

            elif command == "screenshare.stop":
                # Stop screensharing. NOTE: we intentionally do NOT clear
                # tunnel_client.screenshare_port here — FirstCall's browser may have
                # in-flight /screenshare/* fetches, and clearing the port would route
                # them to ui_port (the avatar template), producing garbage on screen.
                # Cleared in the screenshare.stopped event handler instead.
                await client.send({
                    "type": "screenshare.stop",
                })

            elif command == "screenshare.swap":
                # Atomic swap: stop the current screenshare, wait for FirstCall to
                # confirm stop, then start the new one with a cache-busted URL.
                # Eliminates race conditions and cache reuse from naive stop+start.
                new_url = cmd.get("url", "")
                new_port = cmd.get("port", 0)
                if not new_url and not new_port:
                    emit({"event": "screenshare.error",
                          "message": "screenshare.swap requires 'url' or 'port'"})
                    continue
                # Pre-flight check on new local port
                if new_port and tunnel_client and tunnel_base_url:
                    if not _is_port_reachable("127.0.0.1", new_port):
                        emit({"event": "screenshare.error",
                              "message": f"localhost:{new_port} is not reachable. Is your local server running?"})
                        continue
                # Stop current if active, wait for FirstCall to confirm
                if screenshare_state and screenshare_state.active:
                    await client.send({"type": "screenshare.stop"})
                    confirmed = await screenshare_state.wait_stopped(timeout=5.0)
                    if not confirmed:
                        emit_err("screenshare.swap: stop timeout (5s) — proceeding anyway")
                # Build new URL. Cache-bust ONLY the local tunnel URL — external
                # URLs pass through unchanged (signed URLs would break, and a swap
                # to a different external URL already triggers a fresh load).
                if new_port and tunnel_client and tunnel_base_url:
                    tunnel_client.screenshare_port = new_port
                    final_url = _cache_busted_url(tunnel_base_url + "/screenshare/")
                    emit_err(f"Screenshare swapped to localhost:{new_port}")
                else:
                    final_url = new_url
                if screenshare_state:
                    screenshare_state.mark_starting()
                await client.send({
                    "type": "screenshare.start",
                    "url": final_url,
                })

            elif command == "webpage.open":
                # Open a shareable webpage from a local port.
                # Participants open the URL in their own browser (interactive, clickable).
                port = cmd.get("port", 0)
                if port and tunnel_client and tunnel_base_url:
                    tunnel_client.webpage_port = port
                    webpage_url = tunnel_base_url + "/webpage/"
                    emit_err(f"Webpage tunneling localhost:{port}")
                    emit({"event": "webpage.opened", "url": webpage_url})
                else:
                    emit({"event": "webpage.error", "message": "webpage.open requires 'port' and an active tunnel"})

            elif command == "webpage.close":
                # Close the shareable webpage.
                if tunnel_client:
                    tunnel_client.webpage_port = 0
                emit({"event": "webpage.closed"})

            elif command == "set_state":
                # Manually set the avatar's voice state.
                # States: listening, actively_listening, thinking,
                #         waiting_to_speak, speaking, interrupted, contextually_aware
                # This is broadcast to all WS clients (including the avatar template).
                state = cmd.get("state", "listening")
                await client.send({
                    "type": "voice.state_update",
                    "state": state,
                })

            elif command == "tasks.set":
                # Set the agent's current work-in-progress task list. Avatar
                # template polls /tasks.json every 2s and renders the list
                # below the status. Independent of all state machines —
                # this is a separate UI layer for "what the bot is working
                # on" alongside the voice state ("what it's doing right now").
                # Cap at 3 items, truncate each to 30 chars (defensive).
                # Empty list clears the list; tasks.set with no list also clears.
                raw_tasks = cmd.get("tasks", [])
                if not isinstance(raw_tasks, list):
                    raw_tasks = []
                tasks = [str(t)[:30] for t in raw_tasks[:3]]
                if template_server is not None:
                    template_server.current_tasks = tasks

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
                     webpage_url: str = "", screenshare_url: str = "",
                     template: str = "", ui_port: int = 0,
                     screenshare_port: int = 0,
                     max_duration: int = 0, alone_timeout: int = 0,
                     silence_timeout: int = 0):
    """Main bridge loop."""
    client = APIClient()
    done = asyncio.Event()
    template_server = None

    # ── Start local template server if needed ──
    if template and not webpage_url and not ui_port:
        template_server, ui_port = await start_template_server(template)
        if template_server is None:
            emit({"event": "error", "message": f"Failed to start template server for '{template}'"})
            await client.close()
            return
        emit_err(f"Template '{template}' serving on port {ui_port}")

    # ── Create call ──
    emit_err(f"Creating visual call for: {meet_url}")
    try:
        call = await client.create_call(
            meet_url, bot_name,
            webpage_url=webpage_url,
            ui_port=ui_port,
            screenshare_url=screenshare_url,
            screenshare_port=screenshare_port,
            max_duration=max_duration,
            alone_timeout=alone_timeout,
            silence_timeout=silence_timeout,
        )
    except Exception as e:
        emit({"event": "error", "message": str(e)})
        await client.close()
        return

    call_id = call["call_id"]
    call_token = call.get("call_token", "")
    tunnel_id = call.get("tunnel_id", "")
    tunnel_access_key = call.get("tunnel_access_key", "")
    tunnel_url = call.get("tunnel_url", "")
    emit_err(f"Call created: {call_id}")
    emit({"event": "call.created", "call_id": call_id, "status": call.get("status", "")})

    # Note: the backend appends ?ws= and &name= to the tunnel URL when creating
    # the FirstCall bot. The template page reads these from window.location.search.
    # No client-side injection needed.

    # ── Start tunnel client if using local port (template or --ui-port) ──
    tunnel_client = None
    tunnel_base_url = ""
    if tunnel_id and tunnel_access_key and ui_port:
        tunnel_ws = API_BASE.replace("https://", "wss://").replace("http://", "ws://")
        tunnel_ws_url = f"{tunnel_ws}/internal/tunnel/connect"
        tunnel_client = BridgeTunnelClient(
            tunnel_ws_url, tunnel_id, tunnel_access_key,
            ui_port=ui_port, screenshare_port=screenshare_port,
        )
        try:
            await tunnel_client.connect()
            # Extract base URL for screenshare (tunnel_url is like .../k/{key}/ui/)
            if tunnel_url.endswith("/ui/"):
                tunnel_base_url = tunnel_url[:-4]  # strip /ui/
            elif tunnel_url.endswith("/ui"):
                tunnel_base_url = tunnel_url[:-3]  # strip /ui
            emit_err("Tunnel client connected — waiting for bot to join")
        except Exception as e:
            emit({"event": "error", "message": f"Tunnel connection failed: {e}"})
            await client.close()
            return

    # ── Set up screenshare state (tracks active/stopped for screenshare.swap) ──
    screenshare_state = ScreenshareState()

    # ── Set up VAD buffer (handler wired below, after auto_thinking exists) ──
    vad = VADBuffer(cooldown=vad_timeout)

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

    # ── Auto-thinking ──
    # On every user.message, the bridge flips the avatar to "thinking" so the
    # user sees visible feedback during agent processing. Cleared on the
    # agent's next activity or after a 10s fallback. See AutoThinking above.
    auto_thinking = AutoThinking(client)

    async def on_user_complete(speaker: str, text: str):
        """Called when VAD confirms user is done speaking."""
        emit({"event": "user.message", "speaker": speaker, "text": text})
        await auto_thinking.trigger()

    vad.on_complete = on_user_complete

    # ── Gate raise-hand ──
    # Webpage mode has an avatar — flip to "waiting_to_speak" alongside
    # the meeting.raise_hand when the gate stays locked >10s.
    gate_raise_hand = GateRaiseHand(client, with_avatar_state=True)

    # ── TTS state shared between read_stdin (which adds tasks) and this
    # function's tts.interrupted handler (which cancels them). Created here
    # so both functions can reference it. ──
    pending_tts: set = set()

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
        client, done, pending_tts, batch_queue, tunnel_client, tunnel_base_url,
        barge_in, screenshare_state, sent_chats, auto_thinking, gate_raise_hand,
        template_server))

    # ── Periodic batch timeout (safety net) ──
    # If a multi-sentence batch hasn't completed in 60s — e.g., backend's
    # ttsQueue dropped a sentence silently on overflow — emit tts.error for
    # all pending batches and clear the queue. Prevents permanent deadlock.
    # Stale backend tts.done events arriving after a timed-out batch flow
    # through the single-sentence passthrough; this is accepted minor noise.
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
                    # speaker.name == bot_name: a participant who happens to
                    # share the bot's display name is still a real human and
                    # the agent must hear them.
                    if not text:
                        continue

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
                        emit({"event": "chat.received", "sender": sender, "message": message})

                # ── Screenshare events ──
                elif event_type == "screenshare.started":
                    screenshare_state.mark_starting()  # idempotent confirmation
                    emit({"event": "screenshare.started", "url": event.get("url", "")})
                    emit_err("Screenshare started")

                elif event_type == "screenshare.stopped":
                    screenshare_state.mark_stopped()  # unblocks any swap waiters
                    if tunnel_client:
                        # Now safe to clear — no more in-flight /screenshare/* fetches.
                        tunnel_client.screenshare_port = 0
                    emit({"event": "screenshare.stopped"})
                    emit_err("Screenshare stopped")

                elif event_type == "screenshare.error":
                    screenshare_state.mark_stopped()  # unblock waiters from a failed start/stop
                    emit({"event": "screenshare.error", "message": event.get("message", "unknown")})
                    emit_err(f"Screenshare error: {event.get('message', '')}")

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
                    # Cancel any queued/parked forward_tts_with_gate tasks so
                    # pre-interrupt tts.speak commands don't fire after the
                    # user confirmed an interrupt. Tasks awaiting on the
                    # barge-in gate get CancelledError injected at the next
                    # await; their `async with tts_lock` releases the lock
                    # cleanly via __aexit__. websockets handles mid-send
                    # cancellation cleanly (no connection corruption).
                    for task in list(pending_tts):
                        task.cancel()
                    pending_tts.clear()
                    batch_queue.clear()  # tts.interrupted terminates all pending batches
                    # Forward the played / not_played sentence lists to the
                    # agent. The agent decides what to do next based on what
                    # the participant heard vs. what was cut.
                    emit({
                        "event": "tts.interrupted",
                        "reason": event.get("reason", "user_speaking"),
                        "played": event.get("played", []),
                        "not_played": event.get("not_played", []),
                    })
                    # Flip the avatar to "interrupted" (red). No auto-clear:
                    # the next event takes over (auto-thinking on user.message,
                    # backend auto-speaking on next tts.speak, or agent
                    # set_state). Last-write-wins per the project convention.
                    await client.send({"type": "voice.state_update", "state": "interrupted"})

                # ── Warnings ──
                elif event_type == "call.max_duration_warning":
                    emit({"event": "call.max_duration_warning", "minutes_remaining": event.get("minutes_remaining", 5)})
                    emit_err(f"Warning: call will end in {event.get('minutes_remaining', 5)} minutes (max duration)")

                elif event_type == "call.credits_low":
                    emit({"event": "call.credits_low", "balance_microcents": event.get("balance_microcents", 0), "estimated_minutes_remaining": event.get("estimated_minutes_remaining", 0)})
                    emit_err(f"Warning: credits low — estimated {event.get('estimated_minutes_remaining', 0)} minutes remaining")

                # ── Call ended ──
                elif event_type == "call.ended":
                    reason = event.get("reason", "unknown")
                    emit({"event": "call.ended", "reason": reason})
                    emit_err(f"Call ended: {reason}")
                    done.set()
                    break

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
    # Defensive clear — a final in-flight /tasks.json poll then returns empty.
    if template_server is not None:
        template_server.current_tasks = []
    if tunnel_client:
        await tunnel_client.close()
    await client.close()


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AgentCall Visual Voice Bridge — avatar + screenshare in meetings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Like bridge.py but with visual presence + screenshare. The bot joins with
an animated avatar and can screenshare URLs into the meeting.

Protocol (extends bridge.py):
  stdout: {"event": "user.message", ...}, {"event": "screenshare.started", ...}
  stdin:  {"command": "tts.speak", ...}, {"command": "screenshare.start", "url": "..."}

Examples:
  # Avatar template (no local server needed)
  python bridge-visual.py "https://meet.google.com/abc" --name Claude

  # Public webpage as avatar
  python bridge-visual.py "https://meet.google.com/abc" --webpage-url "https://your-site.com/avatar"

  # Local screenshare (agent runs local server on port 3001)
  python bridge-visual.py "https://meet.google.com/abc" --screenshare-port 3001

  # Share a URL during the call
  stdin: {"command": "screenshare.start", "url": "https://slides.google.com/..."}
  stdin: {"command": "screenshare.stop"}
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
    parser.add_argument("--webpage-url", default="", help="Public URL for bot's video feed (avatar page)")
    parser.add_argument("--screenshare-url", default="", help="Public URL for initial screenshare content")
    parser.add_argument("--template", default="pattern", help="Built-in UI template (default: pattern). Options: pattern, ring, orb, avatar, dashboard, blank, voice-agent.")
    parser.add_argument("--ui-port", type=int, default=0, help="Local port for bot's video feed (instead of --template or --webpage-url)")
    parser.add_argument("--screenshare-port", type=int, default=0, help="Local port for screenshare content")
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

    # If using local port or public URL, don't use template
    template = args.template
    if args.ui_port or args.webpage_url:
        template = ""

    asyncio.run(run_bridge(
        args.meet_url, args.name, args.voice, args.vad_timeout,
        webpage_url=args.webpage_url,
        screenshare_url=args.screenshare_url,
        template=template,
        ui_port=args.ui_port,
        screenshare_port=args.screenshare_port,
        max_duration=args.max_duration * 60000 if args.max_duration > 0 else 0,
        alone_timeout=args.alone_timeout * 1000 if args.alone_timeout > 0 else 0,
        silence_timeout=args.silence_timeout * 1000 if args.silence_timeout > 0 else 0,
    ))


if __name__ == "__main__":
    main()
