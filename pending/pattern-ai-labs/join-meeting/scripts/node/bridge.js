#!/usr/bin/env node
/**
 * AgentCall — Voice Bridge for AI Coding Agents (Node.js)
 *
 * This script bridges a meeting's audio I/O with an AI agent framework
 * (Claude Code, Cursor, Codex, Gemini CLI, etc.) via stdin/stdout.
 *
 * It is NOT a standalone agent. It has NO LLM. The agent framework that
 * spawns this script IS the LLM. This script is a thin communication layer:
 *
 *   stdout → agent framework: meeting events (transcripts, chat, participants)
 *   stdin  ← agent framework: commands (tts.speak, send chat, leave, raise hand)
 *
 * KEY FEATURES:
 *   - VAD coalescing: accumulates transcript.final events and emits a single
 *     user.message after a short cooldown anchored to the most recent final.
 *   - Barge-in prevention: tts.speak waits for silence before sending.
 *   - Chat I/O: agent can send and receive meeting chat messages.
 *   - Screenshot: agent can take a screenshot of the meeting view.
 *   - Raise hand: agent can raise the bot's hand before speaking.
 *   - Graceful exit: agent can leave the call.
 *
 * Usage:
 *     export AGENTCALL_API_KEY="ak_ac_your_key"
 *     node bridge.js "https://meet.google.com/abc-def-ghi"
 *
 *     # Custom bot name, voice, and VAD cooldown
 *     node bridge.js "https://meet.google.com/abc" --name "Claude" --voice af_bella --vad-timeout 2.0
 *
 * Dependencies:
 *     npm install ws
 */

import { readFileSync, existsSync, appendFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { createInterface } from 'readline';
import WebSocket from 'ws';

// ──────────────────────────────────────────────────────────────────────────────
// CONFIG
// ──────────────────────────────────────────────────────────────────────────────

const CONFIG_PATH = join(homedir(), '.agentcall', 'config.json');
let _cfg = {};
if (existsSync(CONFIG_PATH)) {
  try { _cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8')); } catch {}
}

const API_BASE = process.env.AGENTCALL_API_URL || _cfg.api_url || 'https://api.agentcall.dev';
const API_KEY = process.env.AGENTCALL_API_KEY || _cfg.api_key || '';

if (!API_KEY) {
  console.error('[bridge] API key not found. Set AGENTCALL_API_KEY env var or save to ~/.agentcall/config.json');
  process.exit(1);
}

// Normalize em/en dashes to commas — Kokoro mispronounces them
// (reads U+2014 as "circumflex something" on some text paths).
// Pure replacement, no stripping; everything else passes through.
function sanitizeTtsText(text) {
  return (text || '').replace(/—/g, ', ').replace(/–/g, ', ');
}

// Split text on sentence terminators (.!?) followed by whitespace, OR on
// newlines. Used by the bridge to break multi-sentence tts.speak into
// per-sentence backend dispatches: first audio reaches the meeting in <1s
// regardless of paragraph length, played/not_played boundaries stay exact,
// and the agent still receives one tts.done per tts.speak. Single-sentence
// text returns a 1-element array (passthrough).
function splitSentences(text) {
  if (!text) return [];
  return text
    .split(/(?<=[.!?])\s+|\n+/)
    .map(s => s.trim())
    .filter(s => s.length > 0);
}

// ──────────────────────────────────────────────────────────────────────────────
// ARGS
// ──────────────────────────────────────────────────────────────────────────────

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    meetURL: '',
    name: 'Agent',
    voice: 'af_heart',
    vadTimeout: 1.25,
    output: '',
    maxDuration: 0,
    aloneTimeout: 0,
    silenceTimeout: 0,
  };

  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (!a.startsWith('--') && !opts.meetURL) { opts.meetURL = a; }
    else if (a === '--name') opts.name = args[++i];
    else if (a === '--voice') opts.voice = args[++i];
    else if (a === '--vad-timeout') opts.vadTimeout = parseFloat(args[++i]);
    else if (a === '--output') opts.output = args[++i];
    else if (a === '--max-duration') opts.maxDuration = parseInt(args[++i]);
    else if (a === '--alone-timeout') opts.aloneTimeout = parseInt(args[++i]);
    else if (a === '--silence-timeout') opts.silenceTimeout = parseInt(args[++i]);
  }

  if (!opts.meetURL) {
    console.error('Usage: bridge.js <meet-url> [--name Agent] [--voice af_heart] [--vad-timeout 1.25]');
    process.exit(1);
  }
  return opts;
}

// ──────────────────────────────────────────────────────────────────────────────
// EMIT
// ──────────────────────────────────────────────────────────────────────────────

let outputFile = '';

function emit(event) {
  const line = JSON.stringify(event);
  console.log(line);
  if (outputFile) {
    try { appendFileSync(outputFile, line + '\n'); } catch {}
  }
}

function emitErr(msg) {
  console.error(`[bridge] ${msg}`);
}

// ──────────────────────────────────────────────────────────────────────────────
// VAD STATE MACHINE — coalesces fragmented transcript.final into user.message.
// Structurally parallel to BargeInState below, kept as a separate instance
// with its own cooldown so the two timers can be tuned independently.
//
//   IDLE              — pending=[], no timer
//   WAITING_FOR_FINAL — partial seen (or partial cancelled an earlier
//                       cooldown); awaiting next final
//   COOLDOWN          — final received, cooldown timer ticking. New final
//                       restarts; new partial cancels and returns to
//                       WAITING_FOR_FINAL; expiry emits user.message.
//
// Anchoring on transcript.final (not "any STT event") removes partial-jitter
// noise. Trade-off: a truly silent mid-utterance pause longer than the
// cooldown splits the utterance — most speakers produce filler audio that
// triggers partials, so coalescing still works in practice.
//
// Failure mode: partial without a follow-up final leaves buffered text
// stuck until the next utterance's final (which would then merge them) or
// flush() on call end. Same shape as BargeInState's "stuck silent" trade-off.
// ──────────────────────────────────────────────────────────────────────────────

class VADBuffer {
  constructor(cooldown = 1.25, onComplete = null) {
    this.cooldownMs = cooldown * 1000;
    this.pending = [];
    this.speaker = 'User';
    this.cooldownTimer = null;
    this.idleResolvers = [];
    this.isIdle = true;
    this.emitTask = null;
    this.onComplete = onComplete;
  }

  onTranscriptFinal(speaker, text) {
    text = text.trim();
    if (!text) return;
    const wasEmpty = this.pending.length === 0;
    this.pending.push(text);
    this.speaker = speaker;
    // → COOLDOWN: restart the cooldown; an earlier emit task (if any) keeps
    // waiting on the same idle latch and will pick up the longer pending
    // list when the cooldown finally fires.
    this._cancelCooldown();
    this.isIdle = false;
    this.cooldownTimer = setTimeout(() => this._cooldownFire(), this.cooldownMs);
    if (wasEmpty) {
      this.emitTask = this._waitAndEmit();
    }
  }

  onTranscriptPartial(speaker, text) {
    // → WAITING_FOR_FINAL: any cooldown is invalidated because the user
    // started speaking again. The buffered pending list is preserved.
    this._cancelCooldown();
    this.isIdle = false;
  }

  _cancelCooldown() {
    if (this.cooldownTimer) {
      clearTimeout(this.cooldownTimer);
      this.cooldownTimer = null;
    }
  }

  _cooldownFire() {
    this.cooldownTimer = null;
    this.isIdle = true;
    const resolvers = this.idleResolvers;
    this.idleResolvers = [];
    resolvers.forEach(r => r());
  }

  _waitUntilIdle() {
    if (this.isIdle) return Promise.resolve();
    return new Promise(r => this.idleResolvers.push(r));
  }

  async _waitAndEmit() {
    await this._waitUntilIdle();
    if (this.pending.length > 0 && this.onComplete) {
      const combined = this.pending.join(' ');
      const speaker = this.speaker;
      this.pending = [];
      await this.onComplete(speaker, combined);
    }
  }

  async flush() {
    this._cancelCooldown();
    if (this.pending.length > 0 && this.onComplete) {
      const combined = this.pending.join(' ');
      const speaker = this.speaker;
      this.pending = [];
      await this.onComplete(speaker, combined);
    }
    // Reset to IDLE and unblock any stuck waiters defensively.
    this.isIdle = true;
    const resolvers = this.idleResolvers;
    this.idleResolvers = [];
    resolvers.forEach(r => r());
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// BARGE-IN STATE MACHINE
//
// Drives whether tts.speak is allowed to forward. Three states:
//
//   IDLE              — STT believes everyone is quiet; gate is open.
//   WAITING_FOR_FINAL — a transcript.partial fired and STT hasn't yet
//                       emitted a transcript.final for the utterance.
//                       Gate is locked until the final arrives.
//   COOLDOWN          — transcript.final fired; we wait COOLDOWN_MS to
//                       catch the user resuming. Any transcript.partial
//                       during cooldown cancels the timer and returns
//                       to WAITING_FOR_FINAL.
//
// Anchored to transcript.final (FirstCall STT's authoritative end-of-
// utterance signal, fires after ~600ms of silence) instead of partial-
// arrival timing, which was sensitive to network jitter and STT batching.
// ──────────────────────────────────────────────────────────────────────────────

class BargeInState {
  constructor() {
    this.cooldownMs = 1500;
    this.cooldownTimer = null;
    this.isIdle = true;          // start IDLE — first tts.speak fires immediately
    this.idleResolvers = [];
  }

  onPartial() {
    this._cancelCooldown();
    this.isIdle = false;
  }

  onFinal() {
    this._cancelCooldown();
    this.isIdle = false;
    this.cooldownTimer = setTimeout(() => {
      this.cooldownTimer = null;
      this.isIdle = true;
      const resolvers = this.idleResolvers;
      this.idleResolvers = [];
      resolvers.forEach(r => r());
    }, this.cooldownMs);
  }

  _cancelCooldown() {
    if (this.cooldownTimer) {
      clearTimeout(this.cooldownTimer);
      this.cooldownTimer = null;
    }
  }

  waitUntilIdle() {
    if (this.isIdle) return Promise.resolve();
    return new Promise(r => this.idleResolvers.push(r));
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// GATE RAISE-HAND — see bridge.py source for the full design rationale.
// If a gated tts.speak waits >10s for the human to stop talking, politely
// raise the bot's hand. The lock around the tts dispatcher (ttsChain in
// JS) naturally limits this to one raise per locked window — only the
// chain head awaits the gate; queued tts.speaks find the gate IDLE
// when their turn comes (if the user has stopped). withAvatarState
// is false here (audio mode has no avatar to flip).
// ──────────────────────────────────────────────────────────────────────────────

class GateRaiseHand {
  constructor(send, withAvatarState = false) {
    // send = async (payload) => sends a JSON object over the WS to backend
    this.send = send;
    this.withAvatarState = withAvatarState;
    this.delayMs = 10000;
    this.timer = null;
  }

  arm() {
    this._cancelTimer();
    this.timer = setTimeout(() => this._fire(), this.delayMs);
  }

  cancel() {
    this._cancelTimer();
  }

  async _fire() {
    this.timer = null;
    await this.send({ type: 'meeting.raise_hand' });
    if (this.withAvatarState) {
      await this.send({ type: 'voice.state_update', state: 'waiting_to_speak' });
    }
  }

  _cancelTimer() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// API CLIENT
// ──────────────────────────────────────────────────────────────────────────────

async function apiCall(method, path, body) {
  const url = `${API_BASE}${path}`;
  const opts = {
    method,
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
  };
  if (body) opts.body = JSON.stringify(body);
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
  }
  return resp.json();
}

async function checkCallActive(callId) {
  try {
    const data = await apiCall('GET', `/v1/calls/${callId}`);
    if (data.status === 'ended' || data.status === 'error') {
      return { active: false, reason: data.end_reason || data.status };
    }
    return { active: true, reason: '' };
  } catch {
    return { active: false, reason: 'api_unreachable' };
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function reconnectWS(callId) {
  const delays = [1, 5, 10, 30];
  const wsURL = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
  const wsURI = `${wsURL}/v1/calls/${callId}/ws?api_key=${API_KEY}`;
  for (let i = 0; i < delays.length; i++) {
    emitErr(`WebSocket reconnecting in ${delays[i]}s (attempt ${i + 1}/${delays.length})...`);
    await sleep(delays[i] * 1000);
    const { active, reason } = await checkCallActive(callId);
    if (!active) {
      emitErr(`Call no longer active: ${reason}`);
      return null;
    }
    try {
      const newWs = new WebSocket(wsURI);
      await new Promise((resolve, reject) => {
        newWs.on('open', resolve);
        newWs.on('error', reject);
      });
      emitErr('WebSocket reconnected successfully');
      return newWs;
    } catch (e) {
      emitErr(`Reconnect attempt ${i + 1} failed: ${e.message}`);
    }
  }
  return null;
}

// ──────────────────────────────────────────────────────────────────────────────
// MAIN
// ──────────────────────────────────────────────────────────────────────────────

async function main() {
  const opts = parseArgs();
  outputFile = opts.output;
  if (outputFile) emitErr(`Events also writing to: ${outputFile}`);

  // ── Create call ──
  emitErr(`Creating call for: ${opts.meetURL}`);
  let call;
  try {
    const params = {
      meet_url: opts.meetURL,
      bot_name: opts.name,
      mode: 'audio',
      voice_strategy: 'direct',
      transcription: true,
    };
    if (opts.maxDuration > 0) params.max_duration = opts.maxDuration * 60000;
    if (opts.aloneTimeout > 0) params.alone_timeout = opts.aloneTimeout * 1000;
    if (opts.silenceTimeout > 0) params.silence_timeout = opts.silenceTimeout * 1000;
    call = await apiCall('POST', '/v1/calls', params);
  } catch (e) {
    emit({ event: 'error', message: e.message });
    process.exit(1);
  }

  const callId = call.call_id;
  emitErr(`Call created: ${callId}`);
  emit({ event: 'call.created', call_id: callId, status: call.status || '' });

  // ── VAD buffer ──
  const vad = new VADBuffer(opts.vadTimeout, (speaker, text) => {
    emit({ event: 'user.message', speaker, text });
  });

  // ── Connect WebSocket ──
  const wsURL = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
  const wsURI = `${wsURL}/v1/calls/${callId}/ws?api_key=${API_KEY}`;
  let ws;
  try {
    ws = new WebSocket(wsURI);
  } catch (e) {
    emit({ event: 'error', message: `WebSocket connection failed: ${e.message}` });
    process.exit(1);
  }

  // ── State ──
  const botNameLower = opts.name.toLowerCase();
  let isSpeaking = false;
  let greeted = false;
  const participants = new Set();
  let done = false;
  const bargeIn = new BargeInState();

  // ── Echo suppression for outbound chat ──
  // FirstCall echoes our own chat back as chat.message events. Without this,
  // the agent would see its own send_chat replayed as chat.received. Filtering
  // by sender == bot_name alone is wrong — it drops legit human chat from
  // participants who happen to share the bot's display name. We instead match
  // on (sender == bot AND text equals something we just sent), with pop-on-
  // match so each outbound chat consumes exactly one echo. maxlen=5 is plenty:
  // FirstCall echoes within ~2-3s; entries don't need to live longer.
  const sentChats = []; // ring buffer, manually capped at 5
  const SENT_CHATS_MAX = 5;

  // sleep helper used by safeSend's retry backoff.
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ── Non-blocking TTS dispatcher ──
  // ttsChain serializes tts.speak forwards so the agent's ordering survives
  // (Node's rl.on('line', ...) handlers run in parallel — without the chain,
  // two rapid tts.speak commands would race through the gate independently
  // and could land at the backend out of order). Other commands fire from
  // their own line handlers immediately without joining this chain.
  // ── Gate raise-hand ──
  // Audio mode — no avatar; only sends meeting.raise_hand if gate stays
  // locked >10s. Lock-based dedupe via ttsChain: only the chain head
  // awaits the gate, so at most one timer is armed at any time.
  const gateRaiseHand = new GateRaiseHand((payload) => safeSend(payload), false);

  let ttsChain = Promise.resolve();

  // ── Sentence-batch queue ──
  // Multi-sentence tts.speak from the agent is split into N backend tts.speaks
  // for pipelined Kokoro synthesis. Each batch entry tracks the expected vs.
  // received count of backend tts.done events; when balanced, ONE aggregated
  // tts.done is forwarded to the agent (matching the agent's 1:1 mental model
  // of tts.speak → tts.done). FIFO since the backend ttsQueue + ttsWorker is
  // FIFO. Cleared on tts.interrupted / tts.error. Single-sentence tts.speaks
  // bypass this queue entirely (passthrough). See tts.speak handler below.
  const batchQueue = [];

  function enqueueTts(payload) {
    ttsChain = ttsChain
      .then(async () => {
        // Barge-in gate via state machine — blocks until BargeInState
        // transitions back to IDLE (transcript.final + cooldown elapsed).
        gateRaiseHand.arm();
        try {
          await bargeIn.waitUntilIdle();
        } finally {
          gateRaiseHand.cancel();
        }
        if (done) return;
        await safeSend(payload);
      })
      .catch(e => emitErr(`tts task: ${e.message || e}`));
  }

  // ── Safe send with retry (handles WS reconnect windows) ──
  async function safeSend(payload) {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(payload));
          return true;
        }
        throw new Error('ws not open');
      } catch (e) {
        emitErr(`send failed (attempt ${attempt + 1}/3): ${e.message || e}`);
        await sleep(500 * (attempt + 1));
      }
    }
    emitErr(`dropped command after 3 failures: ${payload.type || '?'}`);
    return false;
  }

  // ── Stdin reader ──
  const rl = createInterface({ input: process.stdin });
  rl.on('line', async (line) => {
    let cmd;
    try { cmd = JSON.parse(line.trim()); } catch { return; }
    const command = cmd.command || '';

    if (command === 'tts.speak') {
      // Sanitize + sentence-split. Multi-sentence text becomes N backend
      // tts.speaks for pipelined Kokoro synthesis; the event loop aggregates
      // the N backend tts.done events into ONE tts.done back to the agent
      // (see batchQueue handling in the WS event loop below).
      // Single-sentence text bypasses the queue and forwards as today.
      const text = sanitizeTtsText(cmd.text);
      const sentences = splitSentences(text);
      const voice = cmd.voice || opts.voice;
      const speed = cmd.speed || 1.0;
      if (sentences.length === 0) {
        // Empty after sanitize — emit synthetic done so agent isn't stuck.
        emit({ event: 'tts.done' });
      } else if (sentences.length === 1) {
        enqueueTts({ type: 'tts.speak', text: sentences[0], voice, speed });
      } else {
        batchQueue.push({ expected: sentences.length, received: 0, createdAt: Date.now() });
        for (const sentence of sentences) {
          enqueueTts({ type: 'tts.speak', text: sentence, voice, speed });
        }
      }
    } else if (command === 'send_chat') {
      const msgText = cmd.message || '';
      // Track sent chat so we can suppress its echo when it bounces back via
      // FirstCall as a chat.message event. ADD before forward so the echo
      // always finds an entry to consume — see chat.message handler below.
      if (msgText) {
        sentChats.push(msgText);
        if (sentChats.length > SENT_CHATS_MAX) sentChats.shift();
      }
      await safeSend({ type: 'meeting.send_chat', message: msgText });
    } else if (command === 'raise_hand') {
      await safeSend({ type: 'meeting.raise_hand' });
    } else if (command === 'mic') {
      await safeSend({ type: 'meeting.mic', action: cmd.action || 'on' });
    } else if (command === 'screenshot') {
      await safeSend({ type: 'screenshot.take', request_id: cmd.request_id || 'screenshot' });
    } else if (command === 'leave') {
      await safeSend({ type: 'meeting.leave' });
      done = true;
    }
  });

  // ── Wire up WebSocket event handlers ──
  function wireWS(socket) {
    socket.on('open', () => emitErr('WebSocket connected'));

    socket.on('message', (data) => {
      if (done) return;
      let event;
      try { event = JSON.parse(data.toString()); } catch { return; }
      const eventType = event.event || event.type || '';

      if (eventType === 'call.bot_joining_meeting') {
        emit({ event: 'call.bot_joining_meeting', call_id: callId, detail: event.detail || '' });
        emitErr(`Bot joining meeting (${event.detail || ''})`);
      } else if (eventType === 'call.bot_waiting_room') {
        emit({ event: 'call.bot_waiting_room', call_id: callId });
        emitErr('Bot is in the waiting room — waiting to be admitted');
      } else if (eventType === 'call.bot_ready') {
        emit({ event: 'call.bot_ready', call_id: callId });
        emitErr('Bot joined the meeting');
      } else if (eventType === 'participant.joined') {
        const p = event.participant || {};
        const name = p.name || event.name || 'Unknown';
        participants.add(name);
        emit({ event: 'participant.joined', name });
        emitErr(`Participant joined: ${name}`);
        if (!greeted && name.toLowerCase() !== botNameLower) {
          greeted = true;
          emit({
            event: 'greeting.prompt', participant: name,
            hint: `${name} joined. Introduce yourself and greet them via tts.speak. Active participation is the default — do not stay silent.`,
          });
        }
      } else if (eventType === 'participant.left') {
        const p = event.participant || {};
        const name = p.name || event.name || 'Unknown';
        participants.delete(name);
        emit({ event: 'participant.left', name });
      } else if (eventType === 'transcript.final') {
        // Drive the barge-in state machine: STT just decided utterance ended.
        bargeIn.onFinal();

        const speakerObj = event.speaker || {};
        const speaker = typeof speakerObj === 'object' ? (speakerObj.name || 'Unknown') : String(speakerObj);
        const text = (event.text || '').trim();
        // FirstCall does not transcribe bot audio — every transcript event is
        // from a human. We deliberately do NOT filter by speaker.name ==
        // botName: a participant who shares the bot's display name is still
        // a real human and the agent must hear them.
        if (!text) return;
        vad.onTranscriptFinal(speaker, text);
      } else if (eventType === 'transcript.partial') {
        // Drive the barge-in state machine: STT detected speech.
        bargeIn.onPartial();

        const speakerObj = event.speaker || {};
        const speaker = typeof speakerObj === 'object' ? (speakerObj.name || 'Unknown') : String(speakerObj);
        vad.onTranscriptPartial(speaker, event.text || '');
      } else if (eventType === 'chat.message') {
        const sender = event.sender || 'Unknown';
        const message = event.message || '';
        if (!message) {
          // nothing to emit
        } else if (sender.toLowerCase() === botNameLower) {
          // Possible echo of our own outbound chat. Match by exact text + pop
          // on match so the next entry survives for a subsequent legit human
          // chat with the same text from a name-collision participant.
          const idx = sentChats.indexOf(message);
          if (idx !== -1) {
            sentChats.splice(idx, 1);
            // suppress (echo)
          } else {
            // bot-named participant sent a NEW chat — forward
            emit({ event: 'chat.received', sender, message });
          }
        } else {
          emit({ event: 'chat.received', sender, message });
        }
      } else if (eventType === 'screenshot.result') {
        emit({ event: 'screenshot.result', data: event.data || '', width: event.width || 0, height: event.height || 0, request_id: event.request_id || '' });
      } else if (eventType === 'tts.started') {
        isSpeaking = true;
      } else if (eventType === 'tts.done') {
        isSpeaking = false;
        // Multi-sentence batch aggregation: decrement the head batch's
        // received count; emit ONE tts.done to agent only when received ==
        // expected. If batchQueue is empty, this is a single-sentence
        // passthrough (or a stray done after a cleared batch — accepted
        // noise per design).
        if (batchQueue.length > 0) {
          const entry = batchQueue[0];
          entry.received++;
          if (entry.received >= entry.expected) {
            batchQueue.shift();
            emit({ event: 'tts.done' });
          }
        } else {
          emit({ event: 'tts.done' });
        }
      } else if (eventType === 'tts.error') {
        isSpeaking = false;
        emit({ event: 'tts.error', reason: event.reason || 'unknown' });
        batchQueue.length = 0;  // tts.error terminates all pending batches
      } else if (eventType === 'tts.interrupted') {
        isSpeaking = false;
        emit({ event: 'tts.interrupted', reason: event.reason || 'user_speaking', sentence_index: event.sentence_index ?? -1, elapsed_ms: event.elapsed_ms || 0 });
        batchQueue.length = 0;  // tts.interrupted terminates all pending batches
      } else if (eventType === 'call.max_duration_warning') {
        emit({ event: 'call.max_duration_warning', minutes_remaining: event.minutes_remaining || 5 });
        emitErr(`Warning: call will end in ${event.minutes_remaining || 5} minutes (max duration)`);
      } else if (eventType === 'call.credits_low') {
        emit({ event: 'call.credits_low', balance_microcents: event.balance_microcents || 0, estimated_minutes_remaining: event.estimated_minutes_remaining || 0 });
        emitErr(`Warning: credits low — estimated ${event.estimated_minutes_remaining || 0} minutes remaining`);
      } else if (eventType === 'call.ended') {
        const reason = event.reason || 'unknown';
        emit({ event: 'call.ended', reason });
        emitErr(`Call ended: ${reason}`);
        done = true;
        cleanup();
      }
    });

    socket.on('close', async () => {
      if (done) return;
      emitErr('WebSocket disconnected, checking call status...');
      const newWs = await reconnectWS(callId);
      if (newWs) {
        ws = newWs;
        wireWS(ws);
        emitErr('Resuming event stream');
      } else {
        emit({ event: 'call.ended', reason: 'connection_lost' });
        emitErr('WebSocket reconnection failed — call ended');
        done = true;
        cleanup();
      }
    });

    socket.on('error', (err) => {
      if (!done) {
        emitErr(`WebSocket error: ${err.message}`);
      }
    });
  }

  wireWS(ws);

  // ── Periodic batch timeout (safety net) ──
  // If a multi-sentence batch hasn't completed in 60s — e.g., backend's
  // ttsQueue dropped a sentence silently on overflow — emit tts.error for
  // all pending batches and clear the queue. Prevents permanent deadlock.
  // Stale backend tts.done events arriving after a timed-out batch flow
  // through the single-sentence passthrough; accepted minor noise.
  const batchTimeoutInterval = setInterval(() => {
    if (batchQueue.length === 0) return;
    const now = Date.now();
    if (now - batchQueue[0].createdAt > 60000) {
      const count = batchQueue.length;
      emitErr(`tts batch timeout after 60s — aborting ${count} pending batches`);
      for (let i = 0; i < count; i++) {
        emit({ event: 'tts.error', reason: 'tts_timeout' });
      }
      batchQueue.length = 0;
    }
  }, 5000);

  function cleanup() {
    clearInterval(batchTimeoutInterval);
    vad.flush();
    rl.close();
    if (ws.readyState === WebSocket.OPEN) ws.close();
    setTimeout(() => process.exit(0), 500);
  }

  process.on('SIGINT', () => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'meeting.leave' }));
    }
    done = true;
    cleanup();
  });
  process.on('SIGTERM', () => {
    done = true;
    cleanup();
  });
}

main();
