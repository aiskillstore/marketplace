import { createHash } from 'node:crypto';
import { lookup } from 'node:dns';
import https from 'node:https';
import { isIP } from 'node:net';
import { mkdir, open, readFile, stat } from 'node:fs/promises';
import { join, resolve, relative, isAbsolute } from 'node:path';
import { atomicWrite, fail, MAX_BYTES } from './common.mjs';

const mediaAgent = new https.Agent({ keepAlive: true, maxSockets: 2 });
const sha = (value) => createHash('sha256').update(value).digest('hex');
export function publicMediaUrl(raw) {
  const url = new URL(raw);
  const host = url.hostname.toLowerCase();
  if (url.protocol !== 'https:' || url.username || url.password ||
      host === 'localhost' || host.endsWith('.localhost') || host.endsWith('.local') || isIP(host)) {
    fail('unsafe_media_url', 'Media must use a public HTTPS hostname');
  }
  return url;
}
export function publicAddress(address) {
  if (isIP(address) === 4) {
    const [a, b] = address.split('.').map(Number);
    return !(a === 0 || a === 10 || a === 127 || a >= 224 || (a === 100 && b >= 64 && b <= 127) ||
      (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && [0, 168].includes(b)) || (a === 198 && [18, 19, 51].includes(b)) ||
      (a === 203 && b === 0));
  }
  // Only globally routed IPv6; refuse mapped, loopback, ULA and link-local.
  return isIP(address) === 6 && /^[23][0-9a-f]{3}:/i.test(address) && !/^2001:db8:/i.test(address);
}
export function publicHttpsGet(url, headers) {
  return new Promise((accept, reject) => {
    const request = https.get(publicMediaUrl(url), {
      agent: mediaAgent, headers,
      lookup(hostname, options, callback) {
        lookup(hostname, { ...options, all: true }, (error, answers) => {
          if (error) return callback(error);
          if (!answers.length || answers.some((item) => !publicAddress(item.address))) {
            return callback(Object.assign(new Error('Media DNS resolved to a non-public address'), { code: 'unsafe_media_url' }));
          }
          const selected = answers[0];
          callback(null, options.all ? answers : selected.address, selected.family);
        });
      },
    }, accept);
    // Covers DNS, connection and the complete body, independent of socket activity.
    const timer = setTimeout(() => request.destroy(Object.assign(new Error('Download timed out'), { code: 'download_timeout' })), 120000);
    request.on('error', reject);
    request.on('close', () => clearTimeout(timer));
  });
}
export function originalKey(identity, url) {
  return identity.resultId || url;
}
function checkpointPaths(directory, identity, url) {
  const prefix = join(directory, '.downloads', sha(originalKey(identity, url)));
  return { part: `${prefix}.part`, state: `${prefix}.json` };
}
function inside(path, directory) {
  const rel = relative(resolve(directory), resolve(path));
  return rel !== '' && !rel.startsWith('..') && !isAbsolute(rel);
}
export async function checkpointOriginal(directory, identity, url, path, digest) {
  const { state } = checkpointPaths(directory, identity, url);
  await atomicWrite(state, JSON.stringify({ resultId: identity.resultId, urlHash: sha(url), path, sha256: digest }));
}
export async function downloadOriginal(url, directory, identity = {}, get = publicHttpsGet) {
  publicMediaUrl(url);
  const paths = checkpointPaths(directory, identity, url);
  await mkdir(join(directory, '.downloads'), { recursive: true, mode: 0o700 });
  let prior = {};
  try { prior = JSON.parse(await readFile(paths.state, 'utf8')); } catch {}
  if (prior.path && inside(prior.path, directory)) {
    try {
      const info = await stat(prior.path);
      if (info.size > 0 && info.size <= MAX_BYTES) {
        const bytes = await readFile(prior.path);
        if (sha(bytes) === prior.sha256 && (!identity.expectedBytes || bytes.length === identity.expectedBytes)) return bytes;
      }
    } catch {}
  }
  if (prior.urlHash !== sha(url)) prior = {};
  let last;
  for (let attempt = 0; attempt < 3; attempt++) {
    let size = 0;
    try { size = (await stat(paths.part)).size; } catch {}
    const resume = size > 0 && size < MAX_BYTES && typeof prior.etag === 'string' && /^"[^"\r\n]+"$/.test(prior.etag);
    const headers = { 'Accept-Encoding': 'identity' };
    if (resume) Object.assign(headers, { Range: `bytes=${size}-`, 'If-Range': prior.etag });
    let response;
    let file;
    try {
      response = await get(url, headers);
      const status = response.statusCode;
      if (status === 416) {
        response.destroy();
        await atomicWrite(paths.part, Buffer.alloc(0));
        prior = {};
        last = Object.assign(new Error('Range must restart'), { code: 'download_range_invalid' });
        continue;
      }
      if (status !== 200 && status !== 206) {
        fail('media_http_error', `Media returned HTTP ${status}`, { httpStatus: status });
      }
      const header = response.headers;
      const rawLength = header['content-length'];
      const length = rawLength === undefined ? null : Number(rawLength);
      if (length !== null && (!Number.isSafeInteger(length) || length < 0 || length > MAX_BYTES)) fail('download_incomplete', 'Invalid content length');
      let total = null;
      if (status === 206) {
        const match = /^bytes (\d+)-(\d+)\/(\d+)$/.exec(header['content-range'] || '');
        if (!resume || !match) fail('download_range_invalid', 'Unexpected partial response');
        const [start, end, count] = match.slice(1).map(Number);
        if (start !== size || end < start || end !== count - 1 || count > MAX_BYTES ||
            (length !== null && length !== end - start + 1) || header.etag !== prior.etag) {
          fail('download_range_invalid', 'Partial response does not match the original');
        }
        total = count;
      } else {
        size = 0;
        total = length;
      }
      if (header['content-encoding'] && header['content-encoding'] !== 'identity') fail('download_incomplete', 'Unexpected media encoding');
      prior = { etag: header.etag, urlHash: sha(url), total };
      await atomicWrite(paths.state, JSON.stringify(prior));
      file = await open(paths.part, status === 206 ? 'a' : 'w', 0o600);
      let received = 0;
      for await (const chunk of response) {
        received += chunk.length;
        if (size + received > MAX_BYTES) fail('response_too_large', 'Image exceeds 100 MiB');
        await file.writeFile(chunk);
      }
      await file.sync();
      await file.close(); file = null;
      const actual = size + received;
      if (actual === 0) fail('download_empty', 'Image response is empty');
      if ((length !== null && received !== length) || (total !== null && actual !== total) ||
          (identity.expectedBytes && actual !== identity.expectedBytes)) fail('download_incomplete', 'Image byte count does not match');
      return await readFile(paths.part);
    } catch (error) {
      last = error;
      const status = error.details?.httpStatus;
      if (status && status !== 429 && status < 500) break;
      if (['unsafe_media_url', 'response_too_large'].includes(error.code)) break;
      if (error.code === 'download_range_invalid') {
        await atomicWrite(paths.part, Buffer.alloc(0)); prior = {};
      }
    } finally {
      await file?.close().catch(() => {});
      response?.destroy();
    }
  }
  if (!last?.code || !['download_timeout', 'download_empty', 'download_incomplete', 'download_range_invalid', 'media_http_error', 'unsafe_media_url', 'response_too_large'].includes(last.code)) {
    fail('download_transport', 'Original download was interrupted');
  }
  throw last;
}
