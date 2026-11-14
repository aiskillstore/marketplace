import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createHash } from 'node:crypto';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';

const action = readFileSync('.github/actions/download-skillstore-cli/action.yml', 'utf8');
const step = action.split('    - name: Verify release checksum before execution\n')[1]
  .split('\n    - name: Verify CLI\n')[0];
const script = step.split('      run: |\n')[1].split('\n').map(l => l.slice(8)).join('\n');
const payload = 'untrusted cached executable bytes';
const digest = createHash('sha256').update(payload).digest('hex');

function runCase(mode, expectedSha = '') {
  const dir = mkdtempSync(resolve('.cli-checksum-test-'));
  try {
    const bin = join(dir, 'bin'); mkdirSync(bin);
    const output = join(dir, 'output'); writeFileSync(output, '');
    writeFileSync(join(dir, 'skillstore-cli'), payload);
    writeFileSync(join(bin, 'gh'), `#!/bin/bash
set -eu
n=0; [ ! -f "$FIXTURE/count" ] || n=$(cat "$FIXTURE/count")
n=$((n+1)); echo "$n" > "$FIXTURE/count"
dest=''; while [ "$#" -gt 0 ]; do
  if [ "$1" = '--dir' ]; then shift; dest="$1"; fi
  shift
done
if [ "$MODE" = permanent ] || { [ "$MODE" = transient ] && [ "$n" -lt 3 ]; }; then
  printf partial > "$dest/checksums.txt"
  echo 'net/http: TLS handshake timeout' >&2
  exit 1
fi
[ ! -e "$dest/checksums.txt" ] || { echo 'stale partial download' >&2; exit 1; }
case "$MODE" in
 invalid) printf 'invalid skillstore-cli-linux-x64\\n' > "$dest/checksums.txt" ;;
 mismatch) printf '%064d  skillstore-cli-linux-x64\\n' 0 > "$dest/checksums.txt" ;;
 *) printf '%s  skillstore-cli-linux-x64\\n' "$DIGEST" > "$dest/checksums.txt" ;;
esac
`, { mode: 0o755 });
    writeFileSync(join(bin, 'sleep'), '#!/bin/bash\nexit 0\n', { mode: 0o755 });
    const result = spawnSync('bash', ['-e', '-o', 'pipefail', '-c', script], {
      encoding: 'utf8', env: { ...process.env, PATH: `${bin}:${process.env.PATH}`,
        TMPDIR: dir, FIXTURE: dir, MODE: mode, DIGEST: digest,
        GITHUB_WORKSPACE: dir, GITHUB_OUTPUT: output,
        CLI_REPO: 'aiskillstore/skillstore', RELEASE_TAG: 'cli-v2.18.3', EXPECTED_SHA256: expectedSha },
    });
    return { ...result, calls: Number(readFileSync(join(dir, 'count'), 'utf8')), output: readFileSync(output, 'utf8') };
  } finally { rmSync(dir, { recursive: true, force: true }); }
}

test('checksum download retries transient transport errors, removes partial files, verifies bytes', () => {
  const r = runCase('transient');
  assert.equal(r.status, 0, r.stderr); assert.equal(r.calls, 3);
  assert.match(r.output, new RegExp(`cli-sha256=${digest}`));
});
test('transport failure stops after three attempts without claiming verification', () => {
  const r = runCase('permanent');
  assert.notEqual(r.status, 0); assert.equal(r.calls, 3); assert.equal(r.output, '');
});
for (const mode of ['invalid', 'mismatch']) {
  test(`${mode} checksum fails closed, without retrying integrity failures`, () => {
    const r = runCase(mode); assert.notEqual(r.status, 0); assert.equal(r.calls, 1); assert.equal(r.output, '');
  });
}
test('independently recorded digest mismatch still fails closed', () => {
  const r = runCase('success', '0'.repeat(64));
  assert.notEqual(r.status, 0); assert.equal(r.calls, 1); assert.equal(r.output, '');
});
test('first-attempt success verifies cached executable bytes normally', () => {
  const r = runCase('success', digest); assert.equal(r.status, 0, r.stderr); assert.equal(r.calls, 1);
});
