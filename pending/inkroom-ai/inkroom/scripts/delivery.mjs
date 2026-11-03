import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { atomicWrite, fail, MAX_BYTES } from './common.mjs';
import { checkpointOriginal, downloadOriginal, originalKey } from './download.mjs';
import { validateImage } from './image.mjs';

const sha = (value) => createHash('sha256').update(value).digest('hex');
const identityFields = ['taskId', 'resultId', 'inputIndex', 'imageIndex', 'index', 'expectedBytes', 'retainedUntil', 'linkExpiresAt', 'expiresAt'];
function identityOf(node) {
  const meta = node._meta?.['inkroom/image'] || {};
  const result = {};
  for (const key of identityFields) if (meta[key] !== undefined) result[key] = meta[key];
  if (result.index !== undefined) result.imageIndex = result.index;
  if (node.type === 'resource_link' && Number.isSafeInteger(node.size) && node.size > 0) result.expectedBytes = node.size;
  return result;
}
function walk(value, visit) {
  if (Array.isArray(value)) { value.forEach((item) => walk(item, visit)); return; }
  if (!value || typeof value !== 'object') return;
  visit(value);
  if (value.type === 'text' && typeof value.text === 'string') {
    let parsed;
    try { parsed = JSON.parse(value.text); } catch {}
    if (parsed) walk(parsed, visit);
  }
  for (const [key, child] of Object.entries(value)) {
    if (!['data', 'b64_json', 'text', 'nextAction', 'arguments', 'generation', 'referenceImages'].includes(key)) walk(child, visit);
  }
}
export function mediaCandidates(value) {
  const identities = new Map(), manifest = new Map(), tasks = new Map();
  let more = false;
  walk(value, (node) => {
    if (node.nextAction?.tool === 'wait_images') more = true;
    if (node.type === 'resource_link' && node.uri) {
      const identity = identityOf(node);
      if (identity.resultId) identities.set(node.uri, identity);
    }
    if (node.resultManifest) {
      for (const input of node.resultManifest.inputs || []) tasks.set(input.index, input.taskId);
      for (const item of node.resultManifest.results || []) manifest.set(item.resultId, item);
    }
  });
  const candidates = [], seen = new Set();
  walk(value, (node) => {
    let data = node.b64_json;
    if (node.type === 'image') data = node.data;
    const url = node.type === 'resource_link' ? node.uri : (node.url && (node.mimeType || node.width || node.revised_prompt) ? node.url : '');
    if (!url && !data) return;
    const source = data ? 'inline' : 'original_link';
    const identity = { ...(identities.get(url) || {}), ...identityOf(node) };
    const item = manifest.get(identity.resultId);
    if (item) {
      for (const key of identityFields) if (item[key] !== undefined && identity[key] === undefined) identity[key] = item[key];
      if (!identity.expectedBytes && item.bytes > 0) identity.expectedBytes = item.bytes;
      if (!identity.taskId) identity.taskId = tasks.get(item.inputIndex);
    }
    const key = data ? `inline:${identity.resultId || sha(data)}` : `original_link:${originalKey(identity, url)}`;
    if (seen.has(key)) return;
    seen.add(key); candidates.push({ source, data, url, identity });
  });
  for (const item of manifest.values()) {
    if (more || item.status !== 'ready' || seen.has(`original_link:${item.resultId}`)) continue;
    // Even an empty media response cannot turn a ready manifest into saved files.
    candidates.push({ source: 'original_link', missing: true, identity: {
      resultId: item.resultId, taskId: tasks.get(item.inputIndex), inputIndex: item.inputIndex,
      imageIndex: item.imageIndex, index: item.imageIndex, retainedUntil: item.retainedUntil,
      linkExpiresAt: item.linkExpiresAt,
    } });
  }
  return candidates;
}
export async function saveMedia(value, directory, options = {}) {
  const candidates = mediaCandidates(value);
  const entries = new Array(candidates.length);
  let position = 0;
  async function worker() {
    while (position < candidates.length) {
      const index = position++;
      const candidate = candidates[index];
      const base = { source: candidate.source, mediaKind: candidate.source === 'original_link' ? 'original' : 'preview', ...candidate.identity };
      try {
        if (candidate.missing) fail('missing_original_link', 'Ready image has no original link in this response');
        let bytes;
        if (candidate.data) {
          if (candidate.data.length > Math.ceil(MAX_BYTES * 4 / 3) + 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(candidate.data)) fail('invalid_image', 'Invalid inline image');
          bytes = Buffer.from(candidate.data, 'base64');
        } else bytes = await downloadOriginal(candidate.url, directory, candidate.identity, options.get);
        if (!bytes.length) fail('download_empty', 'Image is empty');
        if (candidate.source === 'original_link' && candidate.identity.expectedBytes && bytes.length !== candidate.identity.expectedBytes) fail('download_incomplete', 'Original byte count does not match');
        const info = validateImage(bytes);
        const sha256 = sha(bytes);
        const path = join(directory, `${sha256}.${info.format}`);
        await atomicWrite(path, bytes);
        entries[index] = { ...base, saved: true, path, sha256, bytes: bytes.length, ...info };
        if (candidate.source === 'original_link') {
          await checkpointOriginal(directory, candidate.identity, candidate.url, path, sha256).catch(() => {
            entries[index].checkpointStatus = 'failed';
          });
        }
      } catch (error) {
        entries[index] = { ...base, saved: false, errorCode: error.code || 'local_write_failed',
          error: error.code ? error.message : 'Image save failed', ...(error.details?.httpStatus ? { httpStatus: error.details.httpStatus } : {}) };
      }
    }
  }
  await Promise.all(Array.from({ length: Math.min(2, candidates.length) }, worker));
  return entries;
}
export function mediaEntryKey(item) {
  return `${item.source}:${item.resultId || item.path || item.sha256 || 'unknown'}`;
}
