#!/usr/bin/env node

import { randomUUID } from 'node:crypto';
import { mkdir, mkdtemp, readFile, realpath, rm, unlink } from 'node:fs/promises';
import { homedir, tmpdir } from 'node:os';
import { join, resolve, relative, isAbsolute } from 'node:path';
import { pathToFileURL } from 'node:url';
import { atomicWrite, fail, MAX_BYTES, readResponseBytes } from './common.mjs';
import { publicMediaUrl } from './download.mjs';
import { imageInfo, validateImage } from './image.mjs';
import { saveMedia } from './delivery.mjs';
import { resumeWorkflow, structured } from './workflow.mjs';

const VERSION = '1.0.8';
const ORIGIN = 'https://inkroom.ai';
const STATE_DIR = process.env.INKROOM_STATE_DIR || join(homedir(), '.inkroom-workbuddy');
const TOKEN_FILE = join(STATE_DIR, 'mcp-token');

function output(value, exitCode = 0) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
  process.exitCode = exitCode;
}

function argsOf(values) {
  const result = { _: [] };
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith('--')) {
      result._.push(value);
      continue;
    }
    const key = value.slice(2);
    const next = values[index + 1];
    if (!next || next.startsWith('--')) fail('invalid_arguments', `--${key} requires a value`);
    result[key] = next;
    index += 1;
  }
  return result;
}

function allowedInkRoomUrl(raw) {
  let url;
  try {
    if (typeof raw !== 'string' || /[\u0000-\u0020\u007f]/.test(raw)) throw new Error('Invalid endpoint');
    url = new URL(raw);
  } catch { fail('unsafe_endpoint', 'Only credential-free HTTPS endpoints owned by inkroom.ai are accepted'); }
  const host = url.hostname.toLowerCase();
  if (url.protocol !== 'https:' || url.username || url.password || url.port || url.hash || (host !== 'inkroom.ai' && !host.endsWith('.inkroom.ai'))) {
    fail('unsafe_endpoint', 'Only credential-free HTTPS endpoints owned by inkroom.ai are accepted');
  }
  return url;
}

async function fetchBytes(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    redirect: 'error',
    credentials: 'omit',
    signal: AbortSignal.timeout(options.timeoutMs || 660000),
  });
  const bytes = await readResponseBytes(response);
  return { response, bytes };
}

async function discover() {
  const { response, bytes } = await fetchBytes(`${ORIGIN}/api/settings`, { timeoutMs: 30000 });
  if (!response.ok) fail('endpoint_discovery_failed', `Settings returned HTTP ${response.status}`);
  const envelope = JSON.parse(bytes.toString('utf8'));
  const candidate = envelope?.data?.endpoints?.mcpUrl || `${ORIGIN}/api/mcp`;
  return allowedInkRoomUrl(candidate).toString();
}

async function readToken() {
  const fromEnvironment = process.env.INKROOM_MCP_TOKEN?.trim();
  if (fromEnvironment) return fromEnvironment;
  try {
    return (await readFile(TOKEN_FILE, 'utf8')).trim();
  } catch {
    return '';
  }
}

function parseMcp(bytes) {
  const raw = bytes.toString('utf8').replaceAll('\r\n', '\n').trim();
  try {
    return JSON.parse(raw);
  } catch {}
  for (const event of raw.split('\n\n')) {
    const data = event.split('\n').filter((line) => line.startsWith('data:')).map((line) => line.slice(5).trim()).join('\n');
    if (!data) continue;
    try {
      const parsed = JSON.parse(data);
      if (parsed?.result || parsed?.error) return parsed;
    } catch {}
  }
  fail('invalid_mcp_response', 'No JSON-RPC result found in the saved response');
}

async function mcpRequest(endpoint, token, payload) {
  const { response, bytes } = await fetchBytes(endpoint, {
    method: 'POST',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      'Content-Type': 'application/json',
      Accept: 'application/json, text/event-stream',
      'MCP-Protocol-Version': '2025-03-26',
    },
    body: JSON.stringify(payload),
  });
  if (response.status === 401) fail('invalid_token', 'InkRoom Key is invalid or revoked', { httpStatus: 401, response: bytes });
  if (response.status === 403) fail('forbidden', 'This InkRoom Key does not have the required permission', { httpStatus: 403, response: bytes });
  if (!response.ok) fail('mcp_http_error', `InkRoom returned HTTP ${response.status}`, { httpStatus: response.status, response: bytes });
  return bytes;
}

function compact(value) {
  if (Array.isArray(value)) return value.filter((item) => item?.type !== 'image').map(compact);
  if (!value || typeof value !== 'object') return value;
  const result = {};
  for (const [key, child] of Object.entries(value)) {
    if (key === 'data' || key === 'b64_json' || key.toLowerCase().includes('token')) continue;
    if (key === 'text' && value.type === 'text' && typeof child === 'string') {
      try { result[key] = compact(JSON.parse(child)); continue; } catch {}
    }
    result[key] = compact(child);
  }
  return result;
}

async function commandDoctor() {
  const major = Number(process.versions.node.split('.')[0]);
  if (major < 18 || typeof fetch !== 'function') fail('unsupported_runtime', 'Node.js 18 or newer is required');
  await mkdir(STATE_DIR, { recursive: true, mode: 0o700 });
  const probe = join(STATE_DIR, `.doctor-${process.pid}`);
  await atomicWrite(probe, 'ok');
  await unlink(probe);
  const endpoint = await discover();
  output({ ok: true, version: VERSION, node: process.versions.node, platform: `${process.platform}-${process.arch}`, endpointHost: new URL(endpoint).hostname, generationSubmitted: false, creditsCharged: false });
}

async function commandSelfTest() {
  const major = Number(process.versions.node.split('.')[0]);
  if (major < 18 || typeof fetch !== 'function') fail('unsupported_runtime', 'Node.js 18 or newer is required');

  const temporaryDirectory = !process.env.INKROOM_SELF_TEST_DIR;
  const stateDirectory = temporaryDirectory
    ? await mkdtemp(join(tmpdir(), 'inkroom-self-test-'))
    : resolve(process.env.INKROOM_SELF_TEST_DIR);
  const probe = join(stateDirectory, `probe-${process.pid}.json`);
  await atomicWrite(probe, JSON.stringify({ ok: true }));
  const written = JSON.parse(await readFile(probe, 'utf8'));
  await unlink(probe);

  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=', 'base64');
  const parsedJson = parseMcp(Buffer.from(JSON.stringify({ jsonrpc: '2.0', id: 1, result: { ok: true } })));
  const parsedSse = parseMcp(Buffer.from('event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"ok":true}}\n\n'));
  const image = validateImage(png);
  const endpoint = allowedInkRoomUrl('https://mcp.inkroom.ai/mcp');
  let unsafeUrlRejected = false;
  try { publicMediaUrl('http://127.0.0.1/image.png'); } catch { unsafeUrlRejected = true; }

  if (!written.ok || !parsedJson.result?.ok || !parsedSse.result?.ok || image.width !== 1 || image.height !== 1 || endpoint.hostname !== 'mcp.inkroom.ai' || !unsafeUrlRejected) {
    fail('self_test_failed', 'One or more deterministic checks failed');
  }
  if (temporaryDirectory) await rm(stateDirectory, { recursive: true, force: true });
  output({
    ok: true,
    version: VERSION,
    runtime: `node-${process.versions.node}`,
    platform: `${process.platform}-${process.arch}`,
    checks: ['atomic_write', 'json_rpc_json', 'json_rpc_sse', 'png_chunks_and_inflated_rows', 'endpoint_allowlist', 'private_url_rejection'],
    networkUsed: false,
    authorizationRead: false,
    generationSubmitted: false,
    creditsCharged: false,
  });
}

async function commandAuthorize() {
  let token = '';
  for await (const chunk of process.stdin) token += chunk;
  token = token.trim();
  if (!token || token.length > 16384) fail('invalid_token_input', 'Key is empty or too large');
  const endpoint = await discover();
  const payload = { jsonrpc: '2.0', id: randomUUID(), method: 'tools/list' };
  const bytes = await mcpRequest(endpoint, token, payload);
  const parsed = parseMcp(bytes);
  if (parsed.error || !parsed.result) fail('invalid_token', 'Key validation failed; authorization was not saved');
  await atomicWrite(TOKEN_FILE, token);
  output({ ok: true, authorizationStored: true, generationSubmitted: false, creditsCharged: false });
}

async function recordedRequest(endpoint, token, payload, directory) {
  const stamp = `${Date.now()}-${randomUUID()}`;
  const requestPath = join(directory, `${stamp}.request.json`);
  const responsePath = join(directory, `${stamp}.response`);
  await atomicWrite(requestPath, JSON.stringify(payload, null, 2));
  let bytes;
  try { bytes = await mcpRequest(endpoint, token, payload); }
  catch (error) {
    if (error.details?.response) await atomicWrite(responsePath, error.details.response);
    error.details = { ...error.details, requestPath, ...(error.details?.response ? { responsePath } : {}) };
    throw error;
  }
  await atomicWrite(responsePath, bytes);
  return { value: parseMcp(bytes), record: responsePath, requestPath };
}
function defaultDelivery(tool, input) {
  // Preserve the requirements frozen by an existing preview.
  if (tool !== 'wait_images' && ('requestId' in input || 'batchId' in input)) return;
  if (['generate_image', 'derive_image', 'upscale_image', 'batch_generate', 'wait_images'].includes(tool) && input.deliveryMode === undefined) input.deliveryMode = 'links';
}
async function reviewFailedMedia(media, endpoint, token, directory) {
  const seen = new Map();
  for (const item of media) {
    if (item.saved || item.source !== 'original_link' || !item.resultId || !item.taskId || !Number.isInteger(item.imageIndex)) continue;
    if (![403, 404, 410].includes(item.httpStatus) && !['missing_original_link', 'download_empty', 'download_incomplete', 'download_range_invalid', 'download_timeout', 'download_transport', 'invalid_image'].includes(item.errorCode)) continue;
    try {
      let review = seen.get(item.resultId);
      if (!review) {
        review = await recordedRequest(endpoint, token, { jsonrpc: '2.0', id: randomUUID(), method: 'tools/call', params: {
          name: 'report_image_delivery', arguments: { taskId: item.taskId, imageIndex: item.imageIndex, resultId: item.resultId },
        } }, directory);
        seen.set(item.resultId, review);
      }
      item.reviewResponse = review.record;
      item.reviewStatus = review.value.error || review.value.result?.isError ? 'unconfirmed' : structured(review.value).status || 'unconfirmed';
      item.deliveryReview = compact(review.value);
      const recovered = await saveMedia(review.value, directory);
      const match = recovered.find((saved) => saved.saved && saved.source === 'original_link' && saved.resultId === item.resultId);
      if (match) Object.assign(item, match, { recovered: true });
    } catch { item.reviewStatus = 'unconfirmed'; }
  }
}
async function executeMcp(command, args) {
  const token = await readToken();
  let payload = { jsonrpc: '2.0', id: randomUUID(), method: 'tools/list' };
  if (command === 'models' || command === 'capabilities') {
    payload = { jsonrpc: '2.0', id: randomUUID(), method: 'tools/call', params: {
      name: command === 'models' ? 'list_models' : 'help', arguments: command === 'capabilities' ? { topic: args.topic || 'quickstart' } : {},
    } };
  } else if (command === 'call') {
    if (!args.tool || !args.arguments) fail('invalid_arguments', 'call requires --tool and --arguments');
    const input = JSON.parse(await readFile(resolve(args.arguments), 'utf8'));
    if (!input || Array.isArray(input) || typeof input !== 'object') fail('invalid_arguments', 'Arguments file must contain a JSON object');
    defaultDelivery(args.tool, input);
    payload = { jsonrpc: '2.0', id: randomUUID(), method: 'tools/call', params: { name: args.tool, arguments: input } };
  }
  const publicRead = publicSkillPayload(payload);
  if (!token && !publicRead) fail('authorization_required', 'Sign in to InkRoom and authorize your own Key through standard input');
  const endpoint = await discover();
  const directory = resolve(args.output || 'inkroom-output');
  await mkdir(directory, { recursive: true, mode: 0o700 });
  const { value, record, requestPath } = await recordedRequest(endpoint, token, payload, directory);
  const media = publicRead ? [] : await saveMedia(value, directory);
  if (!publicRead) await reviewFailedMedia(media, endpoint, token, directory);
  const manifestPath = `${record}.manifest.json`;
  await atomicWrite(manifestPath, JSON.stringify(media, null, 2));
  const ok = !value.error && !value.result?.isError && !media.some((item) => item.source === 'original_link' && !item.saved);
  output({ ok, requestPath, responsePath: record, manifestPath, summary: compact(value), media,
    allOriginalsSaved: false, generationAutomaticallyRetried: false }, ok ? 0 : 1);
}

function publicSkillPayload(payload) {
  if (payload.method === 'tools/list') return true;
  if (payload.method !== 'tools/call') return false;
  if (['list_models', 'help'].includes(payload.params?.name)) return true;
  const input = payload.params?.arguments;
  return payload.params?.name === 'prompts' && input &&
    (input.action === undefined || ['search', 'get'].includes(input.action)) &&
    (input.scope === undefined || input.scope === 'recommended');
}
async function loadResponse(args) {
  if (!args.response) fail('invalid_arguments', 'recover/resume requires --response');
  let responsePath = resolve(args.response);
  const directory = resolve(args.output || 'inkroom-output');
  await mkdir(directory, { recursive: true, mode: 0o700 });
  let bytes = await readFile(responsePath);
  let prior = [], checkpoint;
  try {
    const saved = JSON.parse(bytes);
    if (saved.version === 1 && saved.latestResponse && Array.isArray(saved.media)) {
      checkpoint = responsePath;
      responsePath = resolve(saved.latestResponse);
      const rel = relative(directory, responsePath);
      if (!rel || rel.startsWith('..') || isAbsolute(rel)) fail('invalid_checkpoint', 'Checkpoint response must belong to the selected output directory');
      bytes = await readFile(responsePath); prior = saved.media;
    }
  } catch (error) { if (error.code === 'invalid_checkpoint' || error.code === 'ENOENT') throw error; }
  return { value: parseMcp(bytes), record: responsePath, directory, prior, checkpoint };
}
async function commandRecover(args) {
  const { value, record, directory } = await loadResponse(args);
  const media = await saveMedia(value, directory);
  const manifestPath = `${record}.manifest.json`;
  await atomicWrite(manifestPath, JSON.stringify(media, null, 2));
  const ok = !value.error && !value.result?.isError && !media.some((item) => item.source === 'original_link' && !item.saved);
  output({ ok, responsePath: record, manifestPath, generationSubmitted: false, summary: compact(value), media, allOriginalsSaved: false }, ok ? 0 : 1);
}
async function commandResume(args) {
  const loaded = await loadResponse(args);
  const token = await readToken();
  if (!token) fail('authorization_required', 'Receipt recovery requires your existing InkRoom Key');
  const endpoint = await discover();
  const result = await resumeWorkflow({ ...loaded, maxPolls: args['max-polls'] === undefined ? 32 : Number(args['max-polls']),
    compact, saveMedia,
    review: (media) => reviewFailedMedia(media, endpoint, token, loaded.directory),
    request: (next) => recordedRequest(endpoint, token, { jsonrpc: '2.0', id: randomUUID(), method: 'tools/call', params: next }, loaded.directory),
  });
  output(result, result.ok && !result.continuationPending ? 0 : 1);
}

async function main() {
  const [command = 'help', ...rest] = process.argv.slice(2);
  const args = argsOf(rest);
  if (command === 'help' || command === '--help') {
    output({ name: 'InkRoom 图片创作', version: VERSION, commands: ['self-test', 'doctor', 'models', 'capabilities', 'authorize', 'tools', 'call', 'recover', 'resume'], publicCommands: ['self-test', 'doctor', 'models', 'capabilities', 'tools'], dependencies: 'Node.js built-ins only' });
  } else if (command === 'self-test') await commandSelfTest();
  else if (command === 'doctor') await commandDoctor();
  else if (command === 'authorize') await commandAuthorize();
  else if (['tools', 'models', 'capabilities', 'call'].includes(command)) await executeMcp(command, args);
  else if (command === 'recover') await commandRecover(args);
  else if (command === 'resume') await commandResume(args);
  else fail('unknown_command', `Unknown command: ${command}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(await realpath(resolve(process.argv[1]))).href) main().catch((error) => {
  const details = { ...(error.details || {}) };
  delete details.response;
  output({ ok: false, error: error.code || 'runtime_error', message: error.message, ...details, generationAutomaticallyRetried: false }, 1);
});

export { parseMcp, defaultDelivery, compact };
