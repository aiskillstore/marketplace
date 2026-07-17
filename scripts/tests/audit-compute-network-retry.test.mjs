import assert from 'node:assert/strict';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const repoRoot = process.cwd();
const helper = resolve(repoRoot, 'scripts/fetch-audit-compute-usage.sh');
const computeWorkflowPath = resolve(repoRoot, '.github/workflows/sync-audit-compute.yml');
const computeWorkflow = readFileSync(computeWorkflowPath, 'utf8');
const monitorWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/monitor-skill-sources.yml'),
  'utf8',
);

function installFakeNetwork(sequence) {
  const root = mkdtempSync(join(tmpdir(), 'audit-compute-network-'));
  const bin = join(root, 'bin');
  mkdirSync(bin, { recursive: true });

  const state = join(root, 'attempt-count');
  const curlLog = join(root, 'curl.log');
  const sleepLog = join(root, 'sleep.log');
  const fakeCurl = join(bin, 'curl');
  const fakeSleep = join(bin, 'sleep');

  writeFileSync(
    fakeCurl,
    `#!/usr/bin/env bash
set -euo pipefail
count=0
[[ ! -f '${state}' ]] || count=$(cat '${state}')
count=$((count + 1))
printf '%s' "$count" > '${state}'
printf '%s\\n' "$*" >> '${curlLog}'
case "$count" in
${sequence
  .map(
    ({ status, stderr = '', stdout = '' }, index) => `  ${index + 1})
    printf '%s' '${stdout.replaceAll("'", "'\\''")}'
    printf '%s' '${stderr.replaceAll("'", "'\\''")}' >&2
    exit ${status}
    ;;`,
  )
  .join('\n')}
  *)
    echo 'unexpected extra curl attempt' >&2
    exit 99
    ;;
esac
`,
  );
  writeFileSync(fakeSleep, `#!/usr/bin/env bash\nprintf '%s\\n' "$1" >> '${sleepLog}'\n`);
  chmodSync(fakeCurl, 0o755);
  chmodSync(fakeSleep, 0o755);

  return { root, bin, state, curlLog, sleepLog };
}

function runHelper(sequence, extraEnv = {}) {
  const fixture = installFakeNetwork(sequence);
  const result = spawnSync(helper, ['https://helm.example/v1/usage/stats'], {
    encoding: 'utf8',
    env: {
      ...process.env,
      ...extraEnv,
      PATH: `${fixture.bin}:${process.env.PATH}`,
      HELM_API_KEY: 'test-helm-key',
      AUDIT_READ_MAX_ATTEMPTS: '3',
      AUDIT_READ_RETRY_BASE_SECONDS: '2',
    },
  });
  const attempts = existsSync(fixture.state) ? Number(readFileSync(fixture.state, 'utf8')) : 0;
  const curlCalls = existsSync(fixture.curlLog)
    ? readFileSync(fixture.curlLog, 'utf8').trim().split(/\r?\n/).filter(Boolean)
    : [];
  const sleeps = existsSync(fixture.sleepLog)
    ? readFileSync(fixture.sleepLog, 'utf8').trim().split(/\r?\n/).filter(Boolean)
    : [];
  return { ...result, attempts, curlCalls, sleeps };
}

test('initial idempotent GET recovers SSL timeout then reset with bounded backoff', () => {
  const result = runHelper([
    { status: 28, stderr: 'curl: (28) SSL connection timeout\n' },
    { status: 35, stderr: 'curl: (35) Recv failure: Connection reset by peer\n' },
    { status: 0, stdout: '{"object":"usage_stats","totals":{"total_tokens":7}}' },
  ]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, '{"object":"usage_stats","totals":{"total_tokens":7}}');
  assert.equal(result.attempts, 3);
  assert.deepEqual(result.sleeps, ['2', '4']);
  assert.match(result.stderr, /attempt 1\/3 failed with curl exit 28; retrying in 2s/);
  assert.match(result.stderr, /attempt 2\/3 failed with curl exit 35; retrying in 4s/);
  for (const call of result.curlCalls) {
    assert.match(call, /--proto =https/);
    assert.match(call, /--request GET/);
    assert.match(call, /--header @-/);
    assert.doesNotMatch(call, /test-helm-key/);
    assert.doesNotMatch(call, /(?:^|\s)(?:-k|--insecure)(?:\s|$)/);
  }
});

test('read helper rejects method or body arguments before curl can run', () => {
  const fixture = installFakeNetwork([{ status: 0, stdout: '{}' }]);
  const result = spawnSync(helper, ['--request', 'POST'], {
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: `${fixture.bin}:${process.env.PATH}`,
      HELM_API_KEY: 'test-helm-key',
    },
  });

  assert.equal(result.status, 64);
  assert.match(result.stderr, /usage:/);
  assert.equal(existsSync(fixture.state), false, 'curl must not run for mutation-capable arguments');
});

test('configuration cannot raise the read budget above three total attempts', () => {
  const fixture = installFakeNetwork([{ status: 0, stdout: '{}' }]);
  const result = spawnSync(helper, ['https://helm.example/v1/usage/stats'], {
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: `${fixture.bin}:${process.env.PATH}`,
      HELM_API_KEY: 'test-helm-key',
      AUDIT_READ_MAX_ATTEMPTS: '4',
    },
  });

  assert.equal(result.status, 64);
  assert.match(result.stderr, /integer from 1 to 3/);
  assert.equal(existsSync(fixture.state), false, 'invalid budget must fail before curl');
});

test('terminal certificate verification failure never retries or disables verification', () => {
  const result = runHelper([
    { status: 60, stderr: 'curl: (60) SSL certificate problem: unable to get local issuer certificate\n' },
  ]);

  assert.equal(result.status, 60);
  assert.equal(result.attempts, 1);
  assert.deepEqual(result.sleeps, []);
  assert.match(result.stderr, /non-retryable curl exit 60/);
  assert.doesNotMatch(result.curlCalls[0], /(?:^|\s)(?:-k|--insecure)(?:\s|$)/);
});

test('a mixed transient then terminal error stops immediately at the terminal result', () => {
  const result = runHelper([
    { status: 28, stderr: 'curl: (28) SSL connection timeout\n' },
    { status: 60, stderr: 'curl: (60) SSL certificate problem\n' },
  ]);

  assert.equal(result.status, 60);
  assert.equal(result.attempts, 2);
  assert.deepEqual(result.sleeps, ['2']);
  assert.match(result.stderr, /non-retryable curl exit 60/);
});

test('transient failures stop after three total attempts and two bounded sleeps', () => {
  const result = runHelper([
    { status: 28, stderr: 'curl: (28) SSL connection timeout\n' },
    { status: 35, stderr: 'curl: (35) Connection reset by peer\n' },
    { status: 56, stderr: 'curl: (56) Recv failure\n' },
  ]);

  assert.equal(result.status, 56);
  assert.equal(result.attempts, 3);
  assert.deepEqual(result.sleeps, ['2', '4']);
  assert.match(result.stderr, /exhausted 3 attempts; final curl exit 56/);
});

test('workflow retries only the Helm GET and never retries the snapshot POST', () => {
  assert.match(computeWorkflow, /sparse-checkout:[\s\S]*scripts\/fetch-audit-compute-usage\.sh/);
  assert.match(
    computeWorkflow,
    /helm_usage_json="\$\(\.\/scripts\/fetch-audit-compute-usage\.sh "\$helm_usage_url"\)"/,
  );
  assert.match(computeWorkflow, /AUDIT_READ_MAX_ATTEMPTS: ['"]3['"]/);
  assert.match(computeWorkflow, /AUDIT_READ_RETRY_BASE_SECONDS: ['"]2['"]/);

  const post = computeWorkflow.match(
    /response="\$\([\s\S]*?record_audit_compute_snapshot[\s\S]*?\n\s*\)"/,
  )?.[0] ?? '';
  assert.notEqual(post, '', 'missing audit snapshot POST section');
  assert.match(post, /curl --fail --silent --show-error/);
  assert.doesNotMatch(post, /--retry|fetch-audit-compute-usage/);
});

test('the read helper cannot wrap scan, persist, local mutation, or any other workflow', () => {
  assert.doesNotMatch(monitorWorkflow, /fetch-audit-compute-usage|run-source-monitor-with-retry/);

  const workflowUsers = readdirSync(resolve(repoRoot, '.github/workflows'))
    .filter((name) => name.endsWith('.yml') || name.endsWith('.yaml'))
    .filter((name) =>
      readFileSync(resolve(repoRoot, '.github/workflows', name), 'utf8').includes(
        './scripts/fetch-audit-compute-usage.sh "$helm_usage_url"',
      ),
    )
    .map((name) => basename(name));
  assert.deepEqual(workflowUsers, ['sync-audit-compute.yml']);
});
