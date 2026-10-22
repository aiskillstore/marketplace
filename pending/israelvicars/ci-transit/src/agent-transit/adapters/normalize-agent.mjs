// Tolerant, privacy-first adapters for local coding-agent session JSONL.
// Deliberately extracts timing and tool identity only; payloads are never copied.
import { basename } from 'node:path';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validate, parseJsonSafe } from '../../request-transit/adapters/normalize.mjs';

const FAMILIES = new Map([
  ['read', 'read'], ['readfile', 'read'], ['glob', 'read'], ['grep', 'read'], ['ls', 'read'], ['view', 'read'], ['view_image', 'read'],
  ['edit', 'edit'], ['write', 'edit'], ['multiedit', 'edit'], ['apply_patch', 'edit'],
  ['bash', 'shell'], ['shell', 'shell'], ['exec_command', 'shell'], ['local_shell', 'shell'], ['write_stdin', 'shell'], ['wait', 'shell'],
  ['webfetch', 'web'], ['websearch', 'web'], ['web_fetch', 'web'], ['web_search', 'web'], ['web__run', 'web'], ['web.run', 'web'],
  ['task', 'subagent'], ['agent', 'subagent'],
  ['skill', 'skill'], ['todowrite', 'plan'], ['update_plan', 'plan'], ['notebookedit', 'edit'],
  ['strreplace', 'edit'], ['delete', 'edit'], ['editnotebook', 'edit'],
  ['semanticsearch', 'read'], ['readlints', 'read'],
  // Cursor IDE composer tool names (toolFormerData.name in state.vscdb)
  ['read_file', 'read'], ['list_dir', 'read'], ['grep_search', 'read'], ['ripgrep', 'read'], ['file_search', 'read'], ['glob_file_search', 'read'],
  ['codebase_search', 'read'], ['read_lints', 'read'], ['search_replace', 'edit'], ['edit_file', 'edit'], ['edit_file_v2_apply_patch', 'edit'],
  ['delete_file', 'edit'], ['run_terminal_cmd', 'shell'], ['todo_write', 'plan'], ['update_memory', 'plan'], ['fetch_pull_request', 'web'],
]);
const isoMs = (x) => {
  if (x == null) return null;
  if (typeof x === 'number') return x < 1e12 ? x * 1000 : x;
  const n = Number(x); if (Number.isFinite(n)) return n < 1e12 ? n * 1000 : n;
  const t = Date.parse(String(x)); return Number.isFinite(t) ? t : null;
};
const key = (name) => String(name || '').toLowerCase();
const family = (name) => {
  const n = key(name);
  if (FAMILIES.has(n)) return FAMILIES.get(n);
  return n.startsWith('mcp__') || n.startsWith('mcp_') || n.includes('.') ? 'mcp' : 'other';
};
const contentText = (x) => Array.isArray(x) ? x.map((b) => typeof b === 'string' ? b : b && (b.text || b.content || '')).join(' ') : String(x ?? '');
const denied = (x) => /\b(denied|permission denied|not allowed|rejected|approval required)\b/i.test(contentText(x));
const errorText = (x) => /\b(error|failed|failure|exception)\b/i.test(contentText(x));
const basenameTarget = (name, args) => {
  const a = args && typeof args === 'object' ? args : {};
  const path = a.file_path || a.filePath || a.path || a.filename || a.target_file || a.relativeWorkspacePath || a.relative_workspace_path || a.targetFile
    || a.directoryPath || a.targetDirectory || a.target_directory || a.globPattern || a.glob_pattern;
  if (path) return basename(String(path));
  const command = typeof args === 'string' ? args : a.command || a.cmd || a.script;
  if (command) return String(command).trim().split(/\s+/)[0].slice(0, 40);
  const query = a.pattern || a.query || a.url || a.searchTerm || a.search_term;
  return query ? String(query).trim().split(/\s+/)[0].slice(0, 40) : '';
};
const shortName = (name, args) => `${String(name || 'tool')}${basenameTarget(name, args) ? ` · ${basenameTarget(name, args)}` : ''}`.slice(0, 40);
const safeArgs = (args) => {
  let s = typeof args === 'string' ? args : JSON.stringify(args ?? '', (k, v) => /^(content|output|result|prompt|text)$/i.test(k) ? '[REDACTED]' : v);
  s = s.replace(/("?(?:password|passwd|token|secret|authorization|cookie)"?\s*[:=]\s*")([^"\\]{0,200})(")/ig, '$1[REDACTED]$3');
  return s.slice(0, 120);
};
const isMarker = (x) => x && typeof x === 'object' && (x._agentFormat || x.meta && x.meta.agentFormat);
const linesOf = (doc) => Array.isArray(doc) ? doc : String(doc).split(/\r?\n/).filter(Boolean).map((x) => JSON.parse(x));

export function isAgentLog(doc) {
  const lines = Array.isArray(doc) ? doc : [];
  return !!lines.length && (isMarker(lines[0]) || lines.some((x) => x && (x.type === 'session_meta' || x.type === 'response_item' || x.role === 'assistant' || x.role === 'user')) || lines.slice(0, 5).some(isBubble));
}

function claudeEvents(lines, format, warnings) {
  const calls = new Map(), results = new Map(), times = [];
  for (const line of lines) {
    if (isMarker(line)) continue;
    if (['queue-operation', 'attachment', 'ai-title', 'last-prompt', 'summary', 'system', 'file-history-snapshot'].includes(line.type)) continue;
    const t = isoMs(line.timestamp); if (t != null) times.push(t);
    const blocks = line.message && Array.isArray(line.message.content) ? line.message.content : [];
    for (const b of blocks) {
      if (line.type === 'assistant' && b && b.type === 'tool_use' && b.id) calls.set(String(b.id), { id: String(b.id), name: b.name, args: b.input, start: t, sidechain: !!line.isSidechain });
      if (line.type === 'user' && b && b.type === 'tool_result' && b.tool_use_id) results.set(String(b.tool_use_id), { end: t, error: !!b.is_error, denied: !!b.is_error && denied(contentText(b.content).slice(0, 200)) });
    }
  }
  return [...calls.values()].map((c) => ({ ...c, result: results.get(c.id) })).filter((c) => c.start != null);
}

// Codex outputs: judge only the head of the output (first line / exit metadata). Scanning the whole body for
// words like "error" or "denied" flags any call whose output merely mentions them (seen on real sessions).
function codexStatus(p) {
  const text = contentText(p.output);
  const head = text.trimStart().split(/\r?\n/)[0].slice(0, 120);
  let exit = null;
  if (typeof p.output === 'string' && p.output.trim().startsWith('{')) { try { const o = JSON.parse(p.output); exit = o && o.metadata && o.metadata.exit_code; } catch {} }
  const isDenied = /^(permission denied|denied|rejected|not allowed|aborted by user)/i.test(head);
  return { error: !!p.is_error || isDenied || /^script failed\b/i.test(head) || (exit != null && Number(exit) !== 0), denied: isDenied };
}

function codexEvents(lines, warnings) {
  const calls = new Map(), results = new Map(), times = [], unknown = new Map();
  const warnUnknown = (type) => unknown.set(type, (unknown.get(type) || 0) + 1);
  for (const line of lines) {
    if (isMarker(line)) continue;
    const t = isoMs(line.timestamp); if (t != null) times.push(t);
    if (['session_meta', 'turn_context', 'event_msg', 'world_state', 'token_usage_record', 'compacted'].includes(line.type)) continue;
    if (line.type !== 'response_item') { warnUnknown(line.type || 'missing type'); continue; }
    const p = line.payload || {};
    const kind = p.type || line.type;
    if (kind === 'message' || kind === 'reasoning' || kind === 'agent_message' || String(kind).startsWith('compaction') || kind === 'ghost_snapshot') continue;
    if (kind === 'web_search_call') {
      const id = String(p.call_id || p.id || `web-${calls.size + 1}`);
      calls.set(id, { id, name: 'web_search', args: {}, start: t });
    } else if (kind === 'function_call' || kind === 'custom_tool_call' || kind === 'local_shell_call') {
      const id = String(p.call_id || p.id || `${kind}-${calls.size + 1}`);
      let args = p.arguments ?? p.input ?? p.command ?? p;
      let name = p.namespace && p.name ? `${p.namespace}.${p.name}` : p.name || (kind === 'local_shell_call' ? 'local_shell' : kind);
      let wrapper;
      if (kind === 'custom_tool_call' && name === 'exec') {
        const match = typeof p.input === 'string' && [...p.input.matchAll(/\btools\.(\w+)\s*\(/g)].find((m) => !/^(forEach|map|filter|find|some|every|reduce|includes|keys|values|entries)$/.test(m[1]));
        name = match ? match[1] : 'exec';
        args = {};
        wrapper = 'exec';
      }
      if (typeof args === 'string' && p.arguments && (args.trim().startsWith('{') || args.trim().startsWith('['))) { try { args = JSON.parse(args); } catch {} }
      calls.set(id, { id, name, args, start: t, wrapper });
    } else if (kind === 'function_call_output' || kind === 'custom_tool_call_output' || kind === 'local_shell_call_output') {
      const id = String(p.call_id || p.id || ''); if (id) { const st = codexStatus(p); results.set(id, { end: t, error: st.error, denied: st.denied }); }
    } else warnUnknown(kind || 'missing payload type');
  }
  for (const [type, count] of unknown) warnings.push(`ignored ${count} Codex line(s) of type ${type}`);
  return [...calls.values()].map((c) => ({ ...c, result: results.get(c.id) })).filter((c) => c.start != null);
}

// Cursor IDE composer bubbles (exported by scripts/export-cursor.mjs, or any dump of state.vscdb bubble records):
// {bubbleId, type: 1 user | 2 assistant, createdAt ISO, timingInfo {clientRpcSendTime, clientEndTime}, toolFormerData {name, status, params}}.
// A tool call starts at its bubble's createdAt. Cursor stores no tool end time, so it ends at the next bubble's
// createdAt, capped by the turn's clientEndTime: an upper bound that includes the model's next step.
// Bubbles from Cursor builds before ~Sep 2025 have no createdAt: order only, uniform durations.
const isBubble = (l) => l && typeof l === 'object' && typeof l.bubbleId === 'string' && typeof l.type === 'number';
const parseObj = (x) => { if (x && typeof x === 'object') return x; try { const o = JSON.parse(x); return o && typeof o === 'object' ? o : {}; } catch { return {}; } };
function cursorBubbleEvents(lines, warnings) {
  const bubbles = lines.filter(isBubble);
  const t = bubbles.map((b) => isoMs(b.createdAt));
  const tools = bubbles.map((b, i) => [b, i]).filter(([b]) => b.toolFormerData && b.toolFormerData.name);
  const timed = tools.length > 0 && tools.every(([, i]) => t[i] != null);
  const events = []; let turnEnd = null;
  // Bubbles created within a few ms of each other belong to one model step: parallel tool calls, and the empty
  // assistant placeholder Cursor creates right after each call (seen on every call in real sessions). A call ends at
  // the first bubble after that burst.
  const BURST_MS = 300;
  const endOf = (i) => {   // next later timestamp after the burst, capped by the turn end
    let j = i + 1;
    while (j < bubbles.length && bubbles[j].type !== 1 && t[j] != null && t[j - 1] != null && t[j] - t[j - 1] < BURST_MS) j++;
    for (; j < bubbles.length; j++) if (t[j] != null && t[j] >= t[i]) return turnEnd != null && turnEnd >= t[i] ? Math.min(t[j], turnEnd) : t[j];
    return turnEnd != null && turnEnd >= t[i] ? turnEnd : t[i];
  };
  bubbles.forEach((b, i) => {
    if (b.type === 1) turnEnd = null;
    const te = b.timingInfo && isoMs(b.timingInfo.clientEndTime);
    if (te != null && te > 1e12) turnEnd = te;
    const tf = b.toolFormerData;
    if (!tf || !tf.name) return;
    const n = events.length, start = timed ? t[i] : n * 1250, end = timed ? endOf(i) : start + 1000;
    const st = String(tf.status || '').toLowerCase();
    events.push({ id: `cursor-${n + 1}`, name: tf.name, args: { ...parseObj(tf.rawArgs), ...parseObj(tf.params) }, start, cursor: true,
      result: { end, error: st === 'error', denied: st === 'cancelled' || st === 'rejected', cancelled: st === 'cancelled' } });
  });
  warnings.push(timed ? 'Cursor session: tool calls start at their bubble createdAt; Cursor stores no tool end time, so each ends at the next message (an upper bound)'
    : 'Cursor session without bubble timestamps (Cursor builds before ~Sep 2025): order only, durations are uniform');
  return events;
}

function cursorEvents(lines, warnings) {
  if (lines.some(isBubble)) return cursorBubbleEvents(lines, warnings);
  const calls = [], turnCalls = [];
  for (const line of lines) {
    if (line.type === 'turn_ended') {
      if (line.status === 'error' && turnCalls.length) turnCalls[turnCalls.length - 1].turnError = true;
      turnCalls.length = 0;
      continue;
    }
    const blocks = line.message && Array.isArray(line.message.content) ? line.message.content : [];
    for (const b of blocks) if (line.role === 'assistant' && b && b.type === 'tool_use') {
      const e = { id: `cursor-${calls.length + 1}`, name: b.name, args: b.input, start: calls.length * 1250, cursor: true };
      calls.push(e); turnCalls.push(e);
    }
  }
  warnings.push('Cursor transcripts have no timestamps or results: order only, durations are uniform');
  return calls.map((e) => ({ ...e, result: e.turnError ? { end: e.start + 1000, error: true, denied: false } : { end: e.start + 1000, error: false, denied: false } }));
}

export function normalizeAgent(doc, options = {}) {
  const lines = linesOf(doc), format = options.format || (lines[0] && lines[0]._agentFormat) || 'claude-code';
  const warnings = [], events = format === 'codex' ? codexEvents(lines, warnings) : format === 'cursor' ? cursorEvents(lines, warnings) : claudeEvents(lines, format, warnings);
  const allTimes = format === 'cursor' ? events.flatMap((e) => [e.start, e.result.end]) : lines.map((l) => isoMs(l.timestamp)).filter((x) => x != null);
  for (const e of events) if (e.result && e.result.end != null) allTimes.push(e.result.end);
  const startMs = allTimes.length ? Math.min(...allTimes) : 0, endMs = Math.max(...allTimes, startMs);
  const rootId = `session-${format}`;
  const raw = [{ spanId: rootId, parentId: null, service: 'agent', name: `${format} session`, start: 0, duration: endMs - startMs, status: 'ok', kind: 'server', attrs: { 'agent.source': format } }];
  for (const e of events) {
    const end = e.result && e.result.end != null ? e.result.end : e.start;
    const result = e.result;
    const status = result && (result.error || result.denied) ? 'error' : 'ok';
    const attrs = { 'agent.source': format };
    if (e.wrapper) attrs['agent.wrapper'] = e.wrapper;
    if (e.sidechain) attrs['agent.sidechain'] = true;
    const s = { spanId: `tool-${e.id}`, parentId: rootId, service: e.wrapper === 'exec' ? family(e.name) : family(e.name), name: shortName(e.name, e.args), start: Math.max(0, e.start - startMs), duration: Math.max(0, end - e.start), status, kind: 'internal', attrs };
    if (status === 'error') s.statusMessage = result.cancelled ? 'cancelled' : result.denied ? 'denied' : 'tool error';
    if (options.showArgs) s.attrs['agent.args'] = safeArgs(e.args);
    raw.push(s);
  }
  const synthetic = options.synthetic === true || lines.some((l) => /synthetic/i.test(String(l._comment || l.meta?.synthetic || '')));
  return validate({ traceId: `agent-${format}`, meta: { format, source: `agent.${format}`, synthetic, startUnixNs: String(Math.round(startMs * 1e6)), warnings }, spans: raw });
}

export function normalize(doc, options = {}) { return normalizeAgent(doc, options); }

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const file = process.argv[2], format = process.argv.find((x) => ['claude-code', 'codex', 'cursor'].includes(x));
  if (!file) throw new Error('usage: node normalize-agent.mjs <session.jsonl> [claude-code|codex|cursor]');
  const t = normalizeAgent(readFileSync(file, 'utf8'), { format }); console.log(JSON.stringify(t, null, 2));
}
