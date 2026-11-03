import { readFile, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { relative, resolve, isAbsolute, join } from 'node:path';
import { atomicWrite, fail, MAX_BYTES } from './common.mjs';
import { mediaEntryKey } from './delivery.mjs';

export function structured(value) {
  if (value.result?.structuredContent) return value.result.structuredContent;
  for (const block of value.result?.content || []) {
    if (block.type !== 'text') continue;
    try { return JSON.parse(block.text); } catch {}
  }
  return {};
}
export function continuation(value) {
  const next = structured(value).nextAction;
  if (next?.tool !== 'wait_images' || !next.arguments || Array.isArray(next.arguments) || typeof next.arguments !== 'object') return null;
  return { name: 'wait_images', arguments: next.arguments };
}
export function responseComplete(value) {
  const content = structured(value);
  return content.complete === true || content.status === 'completed';
}
export async function verifiedPrior(entries, directory) {
  const result = [];
  for (const entry of entries || []) {
    if (!entry.saved) { result.push(entry); continue; }
    const rel = entry.path ? relative(resolve(directory), resolve(entry.path)) : '..';
    try {
      if (!rel || rel.startsWith('..') || isAbsolute(rel)) throw new Error();
      const size = (await stat(entry.path)).size;
      if (!size || size > MAX_BYTES || size !== entry.bytes) throw new Error();
      const hash = createHash('sha256').update(await readFile(entry.path)).digest('hex');
      if (hash !== entry.sha256) throw new Error();
      result.push(entry);
    } catch {
      result.push({ ...entry, saved: false, errorCode: 'local_file_unverified', error: 'Prior file is missing or changed' });
    }
  }
  return result;
}
export async function resumeWorkflow({ value, record, directory, checkpoint, prior = [], maxPolls = 32, request, saveMedia, review, compact }) {
  if (!Number.isInteger(maxPolls) || maxPolls < 1 || maxPolls > 256) fail('invalid_arguments', 'max-polls must be 1..256');
  checkpoint ||= join(directory, `${Date.now()}.resume.json`);
  const entries = new Map((await verifiedPrior(prior, directory)).map((item) => [mediaEntryKey(item), item]));
  for (let poll = 0; ; poll++) {
    const media = await saveMedia(value, directory);
    if (review) await review(media.filter((item) => !entries.get(mediaEntryKey(item))?.saved), record);
    for (const item of media) {
      const key = mediaEntryKey(item), previous = entries.get(key);
      if (!previous?.saved || item.saved) entries.set(key, item);
    }
    await atomicWrite(`${record}.manifest.json`, JSON.stringify(media, null, 2));
    const nextAction = continuation(value);
    const complete = responseComplete(value) && !structured(value).nextAction;
    const all = [...entries.values()];
    await atomicWrite(checkpoint, JSON.stringify({ version: 1, latestResponse: record, media: all, nextAction, complete }, null, 2));
    const toolError = Boolean(value.error || value.result?.isError);
    if (toolError || !nextAction || poll >= maxPolls) {
      const unsaved = all.filter((item) => item.source === 'original_link' && !item.saved);
      const content = structured(value);
      const requested = content.resultManifest?.requestedImages || content.requestedImages;
      const originals = all.filter((item) => item.source === 'original_link' && item.saved);
      const failures = (content.resultManifest?.results || []).filter((item) => item.status === 'failed').length;
      const allOriginalsSaved = Boolean(complete && Number.isInteger(requested) && requested > 0 && originals.length === requested && !failures && !unsaved.length);
      const deliveryAccounted = Number.isInteger(requested) && requested > 0 && originals.length + failures === requested;
      return { ok: !toolError && complete && deliveryAccounted && !unsaved.length, complete, allOriginalsSaved,
        originalsSaved: originals.length, requestedImages: requested, failedImages: failures,
        checkpoint, responsePath: record, media: all, summary: compact(value), continuationPending: Boolean(nextAction),
        generationSubmitted: false, generationAutomaticallyRetried: false };
    }
    // Only wait_images is accepted above. No automatic paid submission or retry.
    const next = await request(nextAction);
    value = next.value; record = next.record;
  }
}
