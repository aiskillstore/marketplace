import assert from 'node:assert/strict';
import { chmodSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const repoRoot = process.cwd();
const syncWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/sync-to-supabase.yml'),
  'utf8',
);
const computeWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/sync-audit-compute.yml'),
  'utf8',
);
const safetyWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/refresh-security-research-stats.yml'),
  'utf8',
);
const testWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/test-recalculate-scores.yml'),
  'utf8',
);
const refreshScript = resolve(repoRoot, 'scripts/refresh-security-research-stats.sh');
const refreshScriptSource = readFileSync(refreshScript, 'utf8');

function section(source, start, end) {
  const startIndex = source.indexOf(start);
  assert.notEqual(startIndex, -1, `missing section: ${start}`);
  const endIndex = end ? source.indexOf(end, startIndex + start.length) : source.length;
  assert.notEqual(endIndex, -1, `missing section boundary: ${end}`);
  return source.slice(startIndex, endIndex);
}

function assertDedicatedRefreshContract(source) {
  assert.match(
    source,
    /SECURITY_RESEARCH_AUTOMATION_KEY: \$\{\{ secrets\.SECURITY_RESEARCH_AUTOMATION_KEY \}\}/,
  );
  assert.doesNotMatch(source, /SECURITY_ATTESTATION_AUTOMATION_KEY|SKILLSTORE_CALLBACK_TOKEN/);
  assert.match(source, /run: \.\/scripts\/refresh-security-research-stats\.sh/);
}

test('Skill sync refreshes after every successful audit write without rolling back the sync', () => {
  const refresh = section(
    syncWorkflow,
    '      - name: Refresh security research snapshot',
    '      - name: Save synced slugs to artifact',
  );

  assert.ok(
    syncWorkflow.indexOf('      - name: Remove generated report evidence from synced audits')
      < syncWorkflow.indexOf('      - name: Refresh security research snapshot'),
    'research refresh must run after the final audit mutation in the sync job',
  );
  assert.match(
    refresh,
    /if: steps\.changes\.outputs\.skip_sync != 'true' && steps\.sync\.outputs\.synced_count != '0'/,
  );
  assert.match(refresh, /continue-on-error: true/);
  assertDedicatedRefreshContract(refresh);
  assert.match(refresh, /Skill sync succeeded, but the security research snapshot refresh failed/);
  assert.match(refresh, /stale-only safety-net workflow will retry/);
});

test('audit compute writer refreshes only after its RPC succeeds and keeps that write committed', () => {
  const refresh = section(
    computeWorkflow,
    '      - name: Refresh security research snapshot',
  );

  assert.ok(
    computeWorkflow.indexOf('record_audit_compute_snapshot')
      < computeWorkflow.indexOf('      - name: Refresh security research snapshot'),
    'research refresh must follow the cumulative snapshot RPC',
  );
  assert.match(computeWorkflow, /id: sync-compute/);
  assert.match(refresh, /continue-on-error: true/);
  assertDedicatedRefreshContract(refresh);
  assert.match(
    refresh,
    /if: steps\.sync-compute\.outcome == 'success' && steps\.security-research-refresh\.outcome == 'failure'/,
  );
  assert.match(refresh, /audit-compute snapshot remains committed/);
});

test('the low-frequency safety net probes first and refreshes stale snapshots only', () => {
  assert.match(safetyWorkflow, /cron: '43 \*\/6 \* \* \*'/);
  assert.match(safetyWorkflow, /timeout-minutes: 10/);
  assertDedicatedRefreshContract(safetyWorkflow);
  assert.match(
    safetyWorkflow,
    /run: \.\/scripts\/refresh-security-research-stats\.sh --stale-only/,
  );
  assert.doesNotMatch(safetyWorkflow, /continue-on-error: true/);

  assert.ok(
    refreshScriptSource.indexOf('"$public_url"')
      < refreshScriptSource.indexOf('"$refresh_url"'),
    'stale-only mode must probe the public snapshot before calling the private refresh endpoint',
  );
  assert.match(
    refreshScriptSource,
    /current\)[\s\S]*stale-only refresh skipped[\s\S]*exit 0[\s\S]*stale\)/,
  );
  assert.match(refreshScriptSource, /data\.snapshot_state/);
  assert.match(refreshScriptSource, /snapshot_state" != "current"/);
});

test('refresh helper keeps the dedicated secret out of curl argv and bounds retries', () => {
  assert.match(refreshScriptSource, /printf 'Authorization: Bearer %s\\n'/);
  assert.match(refreshScriptSource, /--header @-/);
  assert.doesNotMatch(refreshScriptSource, /--header ['"]Authorization: Bearer \$SECURITY_RESEARCH_AUTOMATION_KEY/);
  assert.doesNotMatch(
    refreshScriptSource,
    /SECURITY_ATTESTATION_AUTOMATION_KEY|AUTOMATION_API_KEY|SKILLSTORE_CALLBACK_TOKEN/,
  );
  assert.match(refreshScriptSource, /for attempt in 1 2 3/);
  assert.match(refreshScriptSource, /\^\(429\|500\|502\|503\|504\)\$/);
  assert.match(refreshScriptSource, /--max-time 120/);
});

test('CI tracks and syntax-checks every refresh contract input', () => {
  for (const path of [
    'scripts/refresh-security-research-stats.sh',
    '.github/workflows/refresh-security-research-stats.yml',
    '.github/workflows/sync-audit-compute.yml',
    '.github/workflows/sync-to-supabase.yml',
  ]) {
    assert.match(testWorkflow, new RegExp(path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
  assert.match(testWorkflow, /bash -n scripts\/refresh-security-research-stats\.sh/);
  assert.match(testWorkflow, /node --test scripts\/tests\/\*\.test\.mjs/);
});

function installFakeCurl(probeState) {
  const root = mkdtempSync(join(tmpdir(), 'security-research-refresh-'));
  const bin = join(root, 'bin');
  const mkdir = spawnSync('mkdir', ['-p', bin]);
  assert.equal(mkdir.status, 0, mkdir.stderr?.toString());
  const log = join(root, 'curl.log');
  const fakeCurl = join(bin, 'curl');
  writeFileSync(fakeCurl, `#!/usr/bin/env bash
set -euo pipefail
method=GET
output=''
read_header=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --request) method="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --header)
      [[ "$2" == '@-' ]] && read_header=true
      shift 2
      ;;
    *) shift ;;
  esac
done
if [[ "$read_header" == true ]]; then
  IFS= read -r authorization
  [[ "$authorization" == 'Authorization: Bearer test-research-secret' ]]
fi
echo "$method" >> '${log}'
if [[ "$method" == GET ]]; then
  printf '%s' '{"snapshot_state":"${probeState}"}' > "$output"
else
  printf '%s' '{"data":{"snapshot_state":"current","captured_at":"2026-07-15T00:00:00Z","source":{"version":"0123456789abcdef0123456789abcdef"}}}' > "$output"
fi
printf '200'
`);
  chmodSync(fakeCurl, 0o755);
  return { root, bin, log };
}

function runStaleOnly(probeState) {
  const fixture = installFakeCurl(probeState);
  const summary = join(fixture.root, 'summary.md');
  const result = spawnSync(refreshScript, ['--stale-only'], {
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: `${fixture.bin}:${process.env.PATH}`,
      GITHUB_STEP_SUMMARY: summary,
      SECURITY_RESEARCH_AUTOMATION_KEY: 'test-research-secret',
      SKILLSTORE_API_URL: 'https://skillstore.example',
    },
  });
  return {
    ...result,
    calls: readFileSync(fixture.log, 'utf8').trim().split(/\r?\n/),
    summary: readFileSync(summary, 'utf8'),
  };
}

test('stale-only runtime skips current snapshots without sending the credential', () => {
  const result = runStaleOnly('current');
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.deepEqual(result.calls, ['GET']);
  assert.match(result.stdout, /stale-only refresh skipped/);
  assert.match(result.summary, /Snapshot is current/);
});

test('stale-only runtime performs one authenticated POST for a stale snapshot', () => {
  const result = runStaleOnly('stale');
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
  assert.deepEqual(result.calls, ['GET', 'POST']);
  assert.match(result.stdout, /snapshot refreshed/);
  assert.match(result.summary, /source_version=`0123456789abcdef0123456789abcdef`/);
});
