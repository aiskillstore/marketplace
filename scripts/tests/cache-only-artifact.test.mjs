import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { verifiedWarmArtifact } from '../cache-only-reconciliation.mjs';

const make = entries => execFileSync('python3', ['-c', `import io,sys,json,zipfile
b=io.BytesIO()
with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,text in json.load(sys.stdin):z.writestr(name,text)
sys.stdout.buffer.write(b.getvalue())`], { input: JSON.stringify(entries), maxBuffer: 3 * 1024 * 1024 });
const metadata = bytes => ({ size_in_bytes: bytes.length, expired: false, digest: 'sha256:' + createHash('sha256').update(bytes).digest('hex') });
const entries = [['warm-cache-summary.json', '{"success":true}'], ['warm-cache-report.jsonl', '{"ok":true}\n']];
test('warm evidence binds exact archive bytes and regular named files', () => {
  const zip = make(entries);
  assert.deepEqual(verifiedWarmArtifact(zip, metadata(zip)), { summary: { success: true }, records: [{ ok: true }] });
  for (const change of [{ expired: true }, { size_in_bytes: zip.length + 1 }, { digest: 'sha256:' + '0'.repeat(64) }]) {
    assert.throws(() => verifiedWarmArtifact(zip, { ...metadata(zip), ...change }));
  }
  for (const wrong of [entries.slice(0, 1), [...entries, ['extra', 'x']], [entries[0], entries[0]],
    [['../warm-cache-summary.json', '{}'], entries[1]], [entries[0], ['warm-cache-report.jsonl', 'not json']],
    [['warm-cache-summary.json', 'x'.repeat(2097153)], entries[1]]]) {
    const bytes = make(wrong);
    assert.throws(() => verifiedWarmArtifact(bytes, metadata(bytes)));
  }
});
