#!/usr/bin/env node
/**
 * AgentCall — Visual Voice Bridge with Screenshare (Node.js)
 *
 * Like bridge.js but with visual presence + screenshare capability.
 * The bot joins with an animated avatar (voice states visible to participants)
 * and can screenshare any URL into the meeting.
 *
 * Uses webpage-av-screenshare mode. By default starts a local avatar template
 * server and tunnels it to the cloud — no manual setup needed.
 *
 * Everything from bridge.js is included:
 *   - VAD coalescing (state machine), chat I/O, raise hand, screenshots, graceful exit
 *
 * Additional features:
 *   - Bot has a visual avatar (7 voice states: listening, speaking, etc.)
 *   - Agent can screenshare public URLs or local ports into the meeting
 *   - Screenshare can be started/stopped dynamically during the call
 *   - Tunnel client runs automatically for local UI and screenshare
 *
 * Additional stdin commands:
 *   {"command": "screenshare.start", "url": "https://slides.google.com/..."}
 *   {"command": "screenshare.start", "port": 3001}
 *   {"command": "screenshare.swap", "port": 3002}            // atomic stop+start
 *   {"command": "screenshare.swap", "url": "https://..."}    // atomic stop+start
 *   {"command": "screenshare.stop"}
 *   {"command": "set_state", "state": "thinking"}
 *
 * Usage:
 *     export AGENTCALL_API_KEY="ak_ac_your_key"
 *     node bridge-visual.js "https://meet.google.com/abc" --name "Claude"
 *     node bridge-visual.js "https://meet.google.com/abc" --webpage-url "https://your-site.com/avatar"
 *     node bridge-visual.js "https://meet.google.com/abc" --ui-port 3000
 *
 * Dependencies:
 *     npm install ws
 */

import { readFileSync, existsSync, appendFileSync, readdirSync, statSync } from 'fs';
import { join, dirname, resolve as resolvePath } from 'path';
import { homedir } from 'os';
import { createInterface } from 'readline';
import { createServer, request as httpRequest } from 'http';
import { createConnection } from 'net';
import { fileURLToPath } from 'url';
import WebSocket from 'ws';

// ──────────────────────────────────────────────────────────────────────────────
// SCREENSHARE HELPERS
//
// FirstCall's headless browser caches the screenshare URL aggressively — a swap
// from one local port to another keeps showing the OLD content because the URL
// (https://tunnel/screenshare/) doesn't change.
//
// Cache-buster: append ?_acv=<ms> so every start is a fresh URL.
// Pre-flight: TCP-probe the local port before sending start, so a dead port
//             produces a clear screenshare.error instead of a silent white page.
// ScreenshareState: lets screenshare.swap wait for FirstCall to confirm the
//             previous screenshare has stopped before issuing the new start.
// ──────────────────────────────────────────────────────────────────────────────

function isPortReachable(port, timeoutMs = 500) {
  return new Promise((resolve) => {
    const socket = createConnection({ host: '127.0.0.1', port });
    const cleanup = () => { try { socket.destroy(); } catch {} };
    const timer = setTimeout(() => { cleanup(); resolve(false); }, timeoutMs);
    socket.once('connect', () => { clearTimeout(timer); cleanup(); resolve(true); });
    socket.once('error', () => { clearTimeout(timer); cleanup(); resolve(false); });
  });
}

function cacheBustedUrl(base) {
  // Per RFC 3986, query must precede fragment. Split off any #frag, append
  // the cache-buster to the query, then reattach the fragment.
  // Only used for the local tunnel URL — never for external URLs (would break
  // signed URLs like S3/CloudFront/Vimeo where the signature includes the query).
  const hashIdx = base.indexOf('#');
  let fragment = '';
  if (hashIdx !== -1) {
    fragment = base.substring(hashIdx);
    base = base.substring(0, hashIdx);
  }
  const sep = base.includes('?') ? '&' : '?';
  return `${base}${sep}_acv=${Date.now()}${fragment}`;
}

class ScreenshareState {
  constructor() {
    this.active = false;
    this._waiters = [];
  }
  markStarting() { this.active = true; }
  markStopped() {
    this.active = false;
    const ws = this._waiters;
    this._waiters = [];
    ws.forEach((resolve) => resolve(true));
  }
  // Returns Promise<boolean>: true if FirstCall confirmed stop, false on timeout.
  waitStopped(timeoutMs = 5000) {
    return new Promise((resolve) => {
      const timer = setTimeout(() => {
        this._waiters = this._waiters.filter((w) => w !== resolver);
        resolve(false);
      }, timeoutMs);
      const resolver = (ok) => { clearTimeout(timer); resolve(ok); };
      this._waiters.push(resolver);
    });
  }
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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
    webpageURL: '',
    screenshareURL: '',
    template: 'pattern',
    uiPort: 0,
    screensharePort: 0,
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
    else if (a === '--webpage-url') opts.webpageURL = args[++i];
    else if (a === '--screenshare-url') opts.screenshareURL = args[++i];
    else if (a === '--template') opts.template = args[++i];
    else if (a === '--ui-port') opts.uiPort = parseInt(args[++i]);
    else if (a === '--screenshare-port') opts.screensharePort = parseInt(args[++i]);
    else if (a === '--max-duration') opts.maxDuration = parseInt(args[++i]);
    else if (a === '--alone-timeout') opts.aloneTimeout = parseInt(args[++i]);
    else if (a === '--silence-timeout') opts.silenceTimeout = parseInt(args[++i]);
  }

  if (!opts.meetURL) {
    console.error('Usage: bridge-visual.js <meet-url> [--name Agent] [--template pattern] [--ui-port 3000]');
    process.exit(1);
  }

  // If using local port or public URL, don't use template
  if (opts.uiPort || opts.webpageURL) opts.template = '';

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
    this._cancelCooldown();
    this.isIdle = false;
    this.cooldownTimer = setTimeout(() => this._cooldownFire(), this.cooldownMs);
    if (wasEmpty) {
      this.emitTask = this._waitAndEmit();
    }
  }

  onTranscriptPartial(speaker, text) {
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
    this.isIdle = true;
    const resolvers = this.idleResolvers;
    this.idleResolvers = [];
    resolvers.forEach(r => r());
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// BARGE-IN STATE MACHINE — see bridge.js source for full rationale.
// Three states (IDLE / WAITING_FOR_FINAL / COOLDOWN) anchored to
// transcript.final from FirstCall STT (fires after ~600ms of silence).
// Replaces the earlier partial-arrival-timing approach which was sensitive
// to network jitter and STT batching.
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
// AUTO-THINKING — broadcasts voice.state=thinking on every user.message so the
// avatar shows visible feedback during agent processing. Cleared by the
// agent's next activity or by a 10s fallback. See bridge-visual.py for the
// full design rationale.
//
// Clear semantics:
//   tts.speak / set_state → cancel timer silently (their own visual takes over)
//   send_chat / screenshare.* / webpage.* / mic / raise_hand / leave →
//                cancel timer + broadcast voice.state=listening
//   screenshot   → leave thinking active (data-gathering input)
//   10s timeout  → broadcast voice.state=listening
// ──────────────────────────────────────────────────────────────────────────────

class AutoThinking {
  constructor(send) {
    // send = async (payload) => sends a JSON object over the WS to backend
    this.send = send;
    this.timeoutMs = 10000;
    this.timer = null;
    this.active = false;
  }

  async trigger() {
    this._cancelTimer();
    this.active = true;
    await this.send({ type: 'voice.state_update', state: 'thinking' });
    this.timer = setTimeout(() => this._fireTimeout(), this.timeoutMs);
  }

  async _fireTimeout() {
    this.timer = null;
    if (this.active) {
      this.active = false;
      await this.send({ type: 'voice.state_update', state: 'listening' });
    }
  }

  cancelSilent() {
    this._cancelTimer();
    this.active = false;
  }

  async cancelAndClear() {
    const wasActive = this.active;
    this._cancelTimer();
    this.active = false;
    if (wasActive) {
      await this.send({ type: 'voice.state_update', state: 'listening' });
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
// GATE RAISE-HAND — see bridge.py source for the full design rationale.
// If a gated tts.speak waits >10s for the human to stop talking, politely
// raise the bot's hand. In bridge-visual mode (withAvatarState=true), also
// flip the avatar to "waiting_to_speak". Last-write-wins on the avatar
// state — subsequent agent set_state or backend auto-state overrides.
//
// Lock-based dedupe via ttsChain: only the chain head awaits the gate,
// so at most one timer is armed at a time → at most one raise_hand per
// locked window. A new locked window (user starts a fresh monologue
// after the bot speaks) gets a fresh timer.
// ──────────────────────────────────────────────────────────────────────────────

class GateRaiseHand {
  constructor(send, withAvatarState = false) {
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
// TEMPLATE SERVER
// ──────────────────────────────────────────────────────────────────────────────

const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
};

function startTemplateServer(templateName) {
  return new Promise((resolve, reject) => {
    const templatesBase = join(__dirname, '..', '..', 'ui-templates');
    const templateDir = join(templatesBase, templateName);
    const sharedJsPath = join(templatesBase, 'agentcall-audio.js');

    if (!existsSync(templateDir)) {
      reject(new Error(`Template '${templateName}' not found at ${templateDir}`));
      return;
    }

    // Agent's current task list (max 3 strings, 30 chars each — validated in
    // the tasks.set command handler before write). Polled by templates via
    // GET /tasks.json (relative path, served through the tunnel as
    // /ui/tasks.json from the cloud's perspective).
    const state = { currentTasks: [] };

    const server = createServer((req, res) => {
      let urlPath = req.url.split('?')[0];

      // Serve shared JS
      if (urlPath === '/agentcall-audio.js' || urlPath === '/../agentcall-audio.js') {
        if (existsSync(sharedJsPath)) {
          res.writeHead(200, { 'Content-Type': 'application/javascript' });
          res.end(readFileSync(sharedJsPath, 'utf-8'));
          return;
        }
        res.writeHead(404);
        res.end('Not found');
        return;
      }

      // Serve agent's current task list (polled by templates every 2s for
      // live work-in-progress display).
      if (urlPath === '/tasks.json') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ tasks: state.currentTasks }));
        return;
      }

      // Serve index
      if (urlPath === '/' || urlPath === '') urlPath = '/index.html';

      const filePath = resolvePath(join(templateDir, urlPath));
      // Prevent path traversal — file must be inside template directory
      if (!filePath.startsWith(resolvePath(templateDir))) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
      }
      if (!existsSync(filePath) || !statSync(filePath).isFile()) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }

      const ext = '.' + filePath.split('.').pop();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(readFileSync(filePath));
    });

    // Port 0 = random available port
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      resolve({ server, port, state });
    });
    server.on('error', reject);
  });
}

// ──────────────────────────────────────────────────────────────────────────────
// TUNNEL CLIENT (inline, with path routing for UI + screenshare)
// ──────────────────────────────────────────────────────────────────────────────

class BridgeTunnelClient {
  constructor(tunnelWSURL, tunnelId, accessKey, uiPort, screensharePort = 0) {
    this.tunnelWSURL = tunnelWSURL;
    this.tunnelId = tunnelId;
    this.accessKey = accessKey;
    this.uiPort = uiPort;
    this.screensharePort = screensharePort;
    this.webpagePort = 0;
    this.ws = null;
    this.running = false;
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.running = true;
      this.ws = new WebSocket(this.tunnelWSURL);

      this.ws.on('open', () => {
        this.ws.send(JSON.stringify({
          type: 'tunnel.register',
          payload: {
            tunnel_id: this.tunnelId,
            tunnel_access_key: this.accessKey,
          },
        }));
        emitErr(`Tunnel client connected (tunnel_id=${this.tunnelId.substring(0, 8)}...)`);
        resolve();
      });

      this.ws.on('error', reject);
      this.ws.on('message', (data) => {
        try {
          const msg = JSON.parse(data.toString());
          if (msg.type === 'http.request') {
            this._handleHTTP(msg);
          } else if (msg.type === 'tunnel.error') {
            emitErr(`TUNNEL ERROR: ${msg.message || 'unknown'}`);
            emit({ event: 'error', message: `Tunnel: ${msg.message || 'unknown'}` });
          }
        } catch {}
      });

      this.ws.on('close', () => {
        if (this.running) emitErr('Tunnel connection lost');
      });

      // Heartbeat
      this._heartbeat = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) this.ws.ping();
      }, 30000);
    });
  }

  _resolvePort(path) {
    if (path.startsWith('/screenshare') && this.screensharePort) {
      return { port: this.screensharePort, localPath: path.substring('/screenshare'.length) || '/' };
    }
    if (path.startsWith('/webpage') && this.webpagePort) {
      return { port: this.webpagePort, localPath: path.substring('/webpage'.length) || '/' };
    }
    if (path.startsWith('/ui')) {
      return { port: this.uiPort, localPath: path.substring('/ui'.length) || '/' };
    }
    return { port: this.uiPort, localPath: path };
  }

  _handleHTTP(msg) {
    const payload = msg.payload || msg;
    const requestId = payload.request_id || msg.request_id || '';
    const method = payload.method || 'GET';
    const path = payload.path || '/';
    const headers = payload.headers || {};
    const reqBody = payload.body || '';

    const { port, localPath } = this._resolvePort(path);

    const options = { hostname: 'localhost', port, path: localPath, method, headers };
    const req = httpRequest(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        const respHeaders = {};
        for (const [k, v] of Object.entries(res.headers)) {
          respHeaders[k] = Array.isArray(v) ? v[0] : v;
        }
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({
            type: 'http.response',
            request_id: requestId,
            payload: { request_id: requestId, status: res.statusCode, headers: respHeaders, body },
          }));
        }
      });
    });

    req.on('error', (err) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'http.response',
          request_id: requestId,
          payload: { request_id: requestId, status: 502, headers: { 'Content-Type': 'text/plain' }, body: `Local server error: ${err.message}` },
        }));
      }
    });

    if (reqBody) req.write(reqBody);
    req.end();
  }

  close() {
    this.running = false;
    clearInterval(this._heartbeat);
    if (this.ws) this.ws.close();
  }
}

// ──────────────────────────────────────────────────────────────────────────────
// API
// ──────────────────────────────────────────────────────────────────────────────

async function apiCall(method, path, body) {
  const url = `${API_BASE}${path}`;
  const opts = {
    method,
    headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
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

function sleepMs(ms) { return new Promise(r => setTimeout(r, ms)); }

async function reconnectWS(callId) {
  const delays = [1, 5, 10, 30];
  const wsURL = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
  const wsURI = `${wsURL}/v1/calls/${callId}/ws?api_key=${API_KEY}`;
  for (let i = 0; i < delays.length; i++) {
    emitErr(`WebSocket reconnecting in ${delays[i]}s (attempt ${i + 1}/${delays.length})...`);
    await sleepMs(delays[i] * 1000);
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

  let uiPort = opts.uiPort;
  let templateServer = null;
  let templateState = null;

  // ── Start template server if needed ──
  if (opts.template && !opts.webpageURL && !uiPort) {
    try {
      const result = await startTemplateServer(opts.template);
      templateServer = result.server;
      templateState = result.state;
      uiPort = result.port;
      emitErr(`Template '${opts.template}' serving on port ${uiPort}`);
    } catch (e) {
      emit({ event: 'error', message: `Failed to start template: ${e.message}` });
      process.exit(1);
    }
  }

  // ── Create call ──
  emitErr(`Creating visual call for: ${opts.meetURL}`);
  let call;
  try {
    const params = {
      meet_url: opts.meetURL,
      bot_name: opts.name,
      mode: 'webpage-av-screenshare',
      voice_strategy: 'direct',
      transcription: true,
    };
    if (opts.webpageURL) params.webpage_url = opts.webpageURL;
    if (opts.screenshareURL) params.screenshare_url = opts.screenshareURL;
    if (uiPort) params.ui_port = uiPort;
    if (opts.screensharePort) params.screenshare_port = opts.screensharePort;
    if (opts.maxDuration > 0) params.max_duration = opts.maxDuration * 60000;
    if (opts.aloneTimeout > 0) params.alone_timeout = opts.aloneTimeout * 1000;
    if (opts.silenceTimeout > 0) params.silence_timeout = opts.silenceTimeout * 1000;
    call = await apiCall('POST', '/v1/calls', params);
  } catch (e) {
    emit({ event: 'error', message: e.message });
    process.exit(1);
  }

  const callId = call.call_id;
  const tunnelId = call.tunnel_id || '';
  const tunnelAccessKey = call.tunnel_access_key || '';
  const tunnelUrl = call.tunnel_url || '';
  emitErr(`Call created: ${callId}`);
  emit({ event: 'call.created', call_id: callId, status: call.status || '' });

  // ── Start tunnel client if using local port ──
  let tunnelClient = null;
  let tunnelBaseUrl = '';
  if (tunnelId && tunnelAccessKey && uiPort) {
    const tunnelWS = API_BASE.replace('https://', 'wss://').replace('http://', 'ws://');
    tunnelClient = new BridgeTunnelClient(
      `${tunnelWS}/internal/tunnel/connect`,
      tunnelId, tunnelAccessKey, uiPort, opts.screensharePort
    );
    try {
      await tunnelClient.connect();
      if (tunnelUrl.endsWith('/ui/')) tunnelBaseUrl = tunnelUrl.slice(0, -4);
      else if (tunnelUrl.endsWith('/ui')) tunnelBaseUrl = tunnelUrl.slice(0, -3);
      emitErr('Tunnel client connected — waiting for bot to join');
    } catch (e) {
      emit({ event: 'error', message: `Tunnel connection failed: ${e.message}` });
      process.exit(1);
    }
  }

  // ── Screenshare state (tracks active/stopped for screenshare.swap) ──
  const screenshareState = new ScreenshareState();

  // ── Auto-thinking + VAD buffer ──
  // auto_thinking flips the avatar to "thinking" on every user.message so the
  // user sees visible feedback during agent processing. Cleared by the agent's
  // next activity (see stdin dispatch) or by a 10s fallback. See AutoThinking
  // class above. `send` is bound to safeSend, defined below — the closure
  // resolves at call time (after safeSend is in scope).
  const autoThinking = new AutoThinking((payload) => safeSend(payload));
  const vad = new VADBuffer(opts.vadTimeout, async (speaker, text) => {
    emit({ event: 'user.message', speaker, text });
    await autoThinking.trigger();
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
  // Webpage mode — flips avatar to "waiting_to_speak" alongside the
  // meeting.raise_hand when the gate stays locked >10s.
  const gateRaiseHand = new GateRaiseHand((payload) => safeSend(payload), true);

  let ttsChain = Promise.resolve();
  // Incremented on tts.interrupted; any pending ttsChain task that captured
  // a lower seq at enqueue time will short-circuit instead of sending its
  // (now-stale) tts.speak. JS Promise chains can't be cancelled mid-chain,
  // so this seq pattern is the equivalent of Python's pending_tts.cancel().
  let interruptSeq = 0;

  // ── Sentence-batch queue ──
  // Multi-sentence tts.speak from the agent is split into N backend tts.speaks
  // for pipelined Kokoro synthesis. Each batch entry tracks the expected vs.
  // received count of backend tts.done events; when balanced, ONE aggregated
  // tts.done is forwarded to the agent (matching the agent's 1:1 mental model
  // of tts.speak → tts.done). FIFO since the backend ttsQueue + ttsWorker is
  // FIFO. Cleared on tts.interrupted / tts.error. Single-sentence tts.speaks
  // bypass this queue entirely (passthrough).
  const batchQueue = [];
  function enqueueTts(payload) {
    const mySeq = interruptSeq;
    ttsChain = ttsChain
      .then(async () => {
        // Short-circuit if an interrupt happened since this task was scheduled.
        if (mySeq !== interruptSeq) return;
        // Barge-in gate via state machine — blocks until BargeInState
        // transitions back to IDLE (transcript.final + cooldown elapsed).
        gateRaiseHand.arm();
        try {
          await bargeIn.waitUntilIdle();
        } finally {
          gateRaiseHand.cancel();
        }
        if (done) return;
        // Re-check after gate wait: a long-parked task may have been
        // bypassed by an interrupt that fired while we waited.
        if (mySeq !== interruptSeq) return;
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

    // Auto-thinking cleanup: any agent activity ends the thinking state set
    // by the VAD callback. tts.speak / set_state cancel silently (their own
    // visual takes over); other commands cancel AND broadcast listening (no
    // own visual). screenshot is a data-gathering input — leave thinking.
    if (command === 'tts.speak' || command === 'set_state') {
      autoThinking.cancelSilent();
    } else if (command === 'send_chat' || command === 'screenshare.start' ||
               command === 'screenshare.stop' || command === 'screenshare.swap' ||
               command === 'webpage.open' || command === 'webpage.close' ||
               command === 'raise_hand' || command === 'mic' || command === 'leave') {
      await autoThinking.cancelAndClear();
    }

    if (command === 'tts.speak') {
      // Sanitize + sentence-split. Multi-sentence text becomes N backend
      // tts.speaks for pipelined Kokoro synthesis; the event loop aggregates
      // the N backend tts.done events into ONE tts.done back to the agent.
      // Single-sentence text bypasses the queue and forwards as today.
      const text = sanitizeTtsText(cmd.text);
      const sentences = splitSentences(text);
      const voice = cmd.voice || opts.voice;
      const speed = cmd.speed || 1.0;
      if (sentences.length === 0) {
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

    } else if (command === 'screenshare.start') {
      let url = cmd.url || '';
      const port = cmd.port || 0;
      if (port && tunnelClient && tunnelBaseUrl) {
        // Pre-flight: confirm something is actually listening locally.
        // Catches the "white screen" failure mode where the agent forgot
        // to start its HTTP server, or killed it before sending start.
        const reachable = await isPortReachable(port);
        if (!reachable) {
          emit({ event: 'screenshare.error',
                 message: `localhost:${port} is not reachable. Is your local server running?` });
          return;
        }
        tunnelClient.screensharePort = port;
        url = cacheBustedUrl(tunnelBaseUrl + '/screenshare/');
        emitErr(`Screenshare tunneling localhost:${port}`);
      }
      // External URLs pass through unchanged. Cache-busting is applied only to
      // the local tunnel URL because that URL is byte-identical across swaps;
      // appending ?_acv would break signed URLs (S3 pre-signed, Vimeo private,
      // Power BI secure embed, etc.) where the signature covers the query.
      if (url) {
        screenshareState.markStarting();
        await safeSend({ type: 'screenshare.start', url });
      } else {
        emit({ event: 'screenshare.error', message: "screenshare.start requires 'url' or 'port'" });
      }

    } else if (command === 'screenshare.stop') {
      // NOTE: do NOT clear tunnelClient.screensharePort here — FirstCall's
      // browser may have in-flight /screenshare/* fetches, and clearing the
      // port would route them to uiPort (avatar template), producing garbage.
      // Cleared in the screenshare.stopped event handler instead.
      await safeSend({ type: 'screenshare.stop' });

    } else if (command === 'screenshare.swap') {
      // Atomic swap: stop the current screenshare, wait for FirstCall to confirm
      // stop, then start the new one with a cache-busted URL.
      const newUrl = cmd.url || '';
      const newPort = cmd.port || 0;
      if (!newUrl && !newPort) {
        emit({ event: 'screenshare.error',
               message: "screenshare.swap requires 'url' or 'port'" });
        return;
      }
      if (newPort && tunnelClient && tunnelBaseUrl) {
        const reachable = await isPortReachable(newPort);
        if (!reachable) {
          emit({ event: 'screenshare.error',
                 message: `localhost:${newPort} is not reachable. Is your local server running?` });
          return;
        }
      }
      if (screenshareState.active) {
        await safeSend({ type: 'screenshare.stop' });
        const confirmed = await screenshareState.waitStopped(5000);
        if (!confirmed) {
          emitErr('screenshare.swap: stop timeout (5s) — proceeding anyway');
        }
      }
      let finalUrl;
      if (newPort && tunnelClient && tunnelBaseUrl) {
        tunnelClient.screensharePort = newPort;
        finalUrl = cacheBustedUrl(tunnelBaseUrl + '/screenshare/');
        emitErr(`Screenshare swapped to localhost:${newPort}`);
      } else {
        // External URL — pass through unchanged. See comment in screenshare.start.
        finalUrl = newUrl;
      }
      screenshareState.markStarting();
      await safeSend({ type: 'screenshare.start', url: finalUrl });

    } else if (command === 'webpage.open') {
      const port = cmd.port || 0;
      if (port && tunnelClient && tunnelBaseUrl) {
        tunnelClient.webpagePort = port;
        const webpageUrl = tunnelBaseUrl + '/webpage/';
        emitErr(`Webpage tunneling localhost:${port}`);
        emit({ event: 'webpage.opened', url: webpageUrl });
      } else {
        emit({ event: 'webpage.error', message: "webpage.open requires 'port' and an active tunnel" });
      }

    } else if (command === 'webpage.close') {
      if (tunnelClient) tunnelClient.webpagePort = 0;
      emit({ event: 'webpage.closed' });

    } else if (command === 'set_state') {
      await safeSend({ type: 'voice.state_update', state: cmd.state || 'listening' });

    } else if (command === 'tasks.set') {
      // Update the work-in-progress task list. Avatar template polls
      // /tasks.json every 2s and renders below the status. Independent of
      // all state machines — separate UI layer for "what the bot is working
      // on" alongside the voice state. Cap at 3 items, 30 chars each.
      const rawTasks = Array.isArray(cmd.tasks) ? cmd.tasks : [];
      const tasks = rawTasks.slice(0, 3).map(t => String(t).slice(0, 30));
      if (templateState) {
        templateState.currentTasks = tasks;
      }

    } else if (command === 'leave') {
      await safeSend({ type: 'meeting.leave' });
      done = true;
    }
  });

  // ── Wire up WebSocket event handlers ──
  function wireWS(socket) {
    socket.on('open', () => emitErr('WebSocket connected'));

    socket.on('message', async (data) => {
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
      } else if (eventType === 'screenshare.started') {
        screenshareState.markStarting();  // idempotent confirmation
        emit({ event: 'screenshare.started', url: event.url || '' });
        emitErr('Screenshare started');
      } else if (eventType === 'screenshare.stopped') {
        screenshareState.markStopped();  // unblocks any swap waiters
        if (tunnelClient) {
          // Now safe to clear — no more in-flight /screenshare/* fetches.
          tunnelClient.screensharePort = 0;
        }
        emit({ event: 'screenshare.stopped' });
        emitErr('Screenshare stopped');
      } else if (eventType === 'screenshare.error') {
        screenshareState.markStopped();  // unblock waiters from a failed start/stop
        emit({ event: 'screenshare.error', message: event.message || 'unknown' });
        emitErr(`Screenshare error: ${event.message || ''}`);
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
        // Bump interruptSeq so any pending ttsChain task with a lower seq
        // short-circuits instead of sending its (now-stale) tts.speak.
        // See enqueueTts above for the seq-check pattern.
        interruptSeq++;
        batchQueue.length = 0;  // tts.interrupted terminates all pending batches
        // Forward played / not_played sentence lists; agent decides what
        // to do next based on what the participant heard vs. what was cut.
        emit({
          event: 'tts.interrupted',
          reason: event.reason || 'user_speaking',
          played: event.played || [],
          not_played: event.not_played || [],
        });
        // Flip the avatar to "interrupted" (red). No auto-clear: the next
        // event takes over (auto-thinking on user.message, backend auto-
        // speaking on next tts.speak, or agent set_state). Last-write-wins.
        await safeSend({ type: 'voice.state_update', state: 'interrupted' });
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
      if (!done) emitErr(`WebSocket error: ${err.message}`);
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
    // Defensive clear — a final in-flight /tasks.json poll then returns empty.
    if (templateState) templateState.currentTasks = [];
    if (tunnelClient) tunnelClient.close();
    if (templateServer) templateServer.close();
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
