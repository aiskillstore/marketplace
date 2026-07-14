import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const INVALIDATOR = join(REPO_ROOT, 'scripts', 'invalidate-cache.sh');
const SYNC_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const SECRET = 'never-print-this-bearer-secret';

const FAKE_CURL = `#!/usr/bin/env bash
set -u

count_file="$FAKE_CURL_LOG_DIR/count"
count=0
if [ -f "$count_file" ]; then
  count=$(cat "$count_file")
fi
count=$((count + 1))
printf '%s' "$count" > "$count_file"

response_file=""
payload_arg=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -o)
      response_file="$2"
      shift 2
      ;;
    --data-binary|-d)
      payload_arg="$2"
      shift 2
      ;;
    -H|-X|-w|--connect-timeout|--max-time)
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

payload_file="\${payload_arg#@}"
cp "$payload_file" "$FAKE_CURL_LOG_DIR/payload-$count.json"

IFS=',' read -r -a results <<< "$FAKE_CURL_RESULTS"
result_index=$((count - 1))
if [ "$result_index" -ge "\${#results[@]}" ]; then
  result_index=$(("\${#results[@]}" - 1))
fi
result="\${results[$result_index]}"

case "$result" in
  transport:*)
    printf '000'
    exit "\${result#transport:}"
    ;;
  http:*)
    response="\${result#http:}"
    status="\${response%%:*}"
    curl_exit=0
    if [ "$response" != "$status" ]; then
      curl_exit="\${response#*:}"
    fi
    printf '{"ok":true}' > "$response_file"
    printf '%s' "$status"
    exit "$curl_exit"
    ;;
  *)
    echo "unknown fake curl result: $result" >&2
    exit 99
    ;;
esac
`;

const FAKE_SLEEP = `#!/usr/bin/env bash
printf '%s\n' "$1" >> "$FAKE_SLEEP_LOG"
`;

function runInvalidator({
  slugs = '',
  slugsFile = '',
  secret = SECRET,
  batchSize = 2,
  maxAttempts = 3,
  maxItems = 100,
  retryBaseSeconds = 1,
  results = 'http:200',
  contentType = 'skills',
  mktempFails = false,
} = {}) {
  const tmp = mkdtempSync(join(tmpdir(), 'invalidate-cache-test-'));
  const bin = join(tmp, 'bin');
  const curlLogDir = join(tmp, 'curl-log');
  const sleepLog = join(tmp, 'sleep.log');
  const githubOutput = join(tmp, 'github-output');
  mkdirSync(bin);
  mkdirSync(curlLogDir);
  writeFileSync(join(bin, 'curl'), FAKE_CURL, { mode: 0o755 });
  writeFileSync(join(bin, 'sleep'), FAKE_SLEEP, { mode: 0o755 });
  if (mktempFails) {
    writeFileSync(join(bin, 'mktemp'), '#!/usr/bin/env bash\nexit 1\n', { mode: 0o755 });
  }

  const result = spawnSync('/bin/bash', [INVALIDATOR], {
    encoding: 'utf8',
    timeout: 10_000,
    env: {
      ...process.env,
      PATH: `${bin}:${process.env.PATH}`,
      CACHE_SECRET: secret,
      SITE_URL: 'https://offline.invalid',
      CONTENT_TYPE: contentType,
      SLUGS_STR: slugs,
      SLUGS_FILE: slugsFile,
      BATCH_SIZE: String(batchSize),
      MAX_ATTEMPTS: String(maxAttempts),
      MAX_ITEMS: String(maxItems),
      RETRY_BASE_SECONDS: String(retryBaseSeconds),
      CURL_CONNECT_TIMEOUT: '1',
      CURL_MAX_TIME: '2',
      GITHUB_OUTPUT: githubOutput,
      FAKE_CURL_LOG_DIR: curlLogDir,
      FAKE_CURL_RESULTS: results,
      FAKE_SLEEP_LOG: sleepLog,
    },
  });

  const payloads = readdirSync(curlLogDir)
    .filter((name) => /^payload-\d+\.json$/.test(name))
    .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]))
    .map((name) => JSON.parse(readFileSync(join(curlLogDir, name), 'utf8')));
  const sleeps = readdirSync(tmp).includes('sleep.log')
    ? readFileSync(sleepLog, 'utf8').trim().split('\n').filter(Boolean)
    : [];
  const outputs = {};
  if (readdirSync(tmp).includes('github-output')) {
    for (const line of readFileSync(githubOutput, 'utf8').trim().split('\n').filter(Boolean)) {
      const separator = line.indexOf('=');
      assert.notEqual(separator, -1, `Invalid GITHUB_OUTPUT line: ${line}`);
      outputs[line.slice(0, separator)] = Number(line.slice(separator + 1));
    }
  }

  assert.doesNotMatch(`${result.stdout}${result.stderr}`, new RegExp(SECRET));
  return { result, payloads, sleeps, outputs };
}

test('empty input succeeds without validating a secret or making an HTTP request', () => {
  const { result, payloads, outputs } = runInvalidator({ slugs: '', secret: '' });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads, []);
  assert.deepEqual(outputs, { total_count: 0, success_count: 0, failed_count: 0 });
});

test('single and 96-item inputs use deterministic bounded JSON batches', () => {
  const single = runInvalidator({ slugs: 'only-one', batchSize: 30 });
  assert.equal(single.result.status, 0);
  assert.deepEqual(single.payloads, [
    { type: 'skills', slugs: ['only-one'], invalidateApi: true },
  ]);

  const slugs = [
    'alpha',
    'quote"slug',
    String.raw`slash\slug`,
    ...Array.from({ length: 93 }, (_, index) => `skill-${String(index).padStart(2, '0')}`),
  ];
  const larger = runInvalidator({ slugs: slugs.join(','), batchSize: 10 });

  assert.equal(
    larger.result.status,
    0,
    `STDOUT:\n${larger.result.stdout}\nSTDERR:\n${larger.result.stderr}`,
  );
  assert.deepEqual(
    larger.payloads.map((payload) => payload.slugs.length),
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 6],
  );
  assert.ok(larger.payloads.every((payload) => payload.type === 'skills'));
  assert.ok(larger.payloads.every((payload) => payload.invalidateApi === true));
  assert.deepEqual(larger.payloads.flatMap((payload) => payload.slugs), slugs);
  assert.deepEqual(larger.outputs, {
    total_count: 96,
    success_count: 96,
    failed_count: 0,
  });

  const unbounded = runInvalidator({ slugs: 'alpha,beta', batchSize: 31 });
  assert.notEqual(unbounded.result.status, 0);
  assert.deepEqual(unbounded.payloads, []);
});

test('inputs above the explicit 100-item budget fail before making an HTTP request', () => {
  const slugs = Array.from({ length: 101 }, (_, index) => `skill-${index}`);
  const { result, payloads, sleeps } = runInvalidator({
    slugs: slugs.join(','),
    batchSize: 10,
    maxItems: 100,
  });

  assert.notEqual(result.status, 0);
  assert.deepEqual(payloads, []);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /item count 101 exceeds MAX_ITEMS 100/);
});

test('temporary workspace failure fails closed before making an HTTP request', () => {
  const { result, payloads, outputs } = runInvalidator({
    slugs: 'alpha',
    mktempFails: true,
  });

  assert.notEqual(result.status, 0);
  assert.deepEqual(payloads, []);
  assert.deepEqual(outputs, {});
  assert.match(result.stderr, /Failed to create temporary workspace/);
});

test('retryable curl transport failures retry the same idempotent batch', () => {
  for (const exitCode of [5, 6, 7, 16, 18, 28, 35, 52, 55, 56, 92]) {
    const { result, payloads, sleeps } = runInvalidator({
      slugs: 'alpha,beta',
      results: `transport:${exitCode},http:200`,
    });

    assert.equal(
      result.status,
      0,
      `curl exit ${exitCode}\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`,
    );
    assert.equal(payloads.length, 2);
    assert.deepEqual(payloads[0], payloads[1]);
    assert.equal(sleeps.length, 1);
  }
});

test('HTTP 408, 429, and 5xx responses are transient and use finite retries', () => {
  for (const status of [408, 429, 503]) {
    const { result, payloads, sleeps } = runInvalidator({
      slugs: 'alpha',
      results: `http:${status},http:200`,
    });

    assert.equal(
      result.status,
      0,
      `HTTP ${status}\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`,
    );
    assert.equal(payloads.length, 2);
    assert.equal(sleeps.length, 1);
    assert.deepEqual(payloads[0], payloads[1]);
  }
});

test('HTTP 401 takes precedence over curl exit 18 and fails after one request', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    results: 'http:401:18,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /Non-transient HTTP 401/);
});

test('HTTP 403 takes precedence over curl exit 28 and fails after one request', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    results: 'http:403:28,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /Non-transient HTTP 403/);
});

test('HTTP 503 takes precedence over curl exit 18 and retries within the finite budget', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    maxAttempts: 3,
    results: 'http:503:18,http:503:18,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 3);
  assert.ok(payloads.every((payload) => JSON.stringify(payload) === JSON.stringify(payloads[0])));
  assert.deepEqual(sleeps, ['1', '2']);
  assert.match(result.stderr, /Transient HTTP 503/);
  assert.doesNotMatch(result.stderr, /curl transport failure/);
});

test('status 000 with curl exit 28 uses transport retries within the finite budget', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    maxAttempts: 3,
    results: 'http:000:28,http:000:28,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 3);
  assert.ok(payloads.every((payload) => JSON.stringify(payload) === JSON.stringify(payloads[0])));
  assert.deepEqual(sleeps, ['1', '2']);
  assert.match(result.stderr, /Transient curl transport failure \(exit 28\)/);
});

test('non-transient curl failures fail closed without retrying', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha,beta,gamma',
    results: 'transport:3,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.deepEqual(sleeps, []);
});

test('non-transient HTTP failures fail closed without retrying', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha,beta,gamma',
    results: 'http:400,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.deepEqual(sleeps, []);
});

test('an exhausted batch fails immediately without sending later batches', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma,delta,epsilon',
    maxAttempts: 3,
    results: 'http:200,http:503',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 4);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.ok(
    payloads.slice(1).every(
      (payload) => JSON.stringify(payload.slugs) === '["gamma","delta"]',
    ),
  );
  assert.equal(sleeps.length, 2);
  assert.deepEqual(outputs, {
    total_count: 5,
    success_count: 2,
    failed_count: 3,
  });
  assert.equal(outputs.total_count, outputs.success_count + outputs.failed_count);
});

test('sync workflow uses the local bounded invalidator and preserves downstream success gates', () => {
  const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
  const invalidationJob = workflow.slice(
    workflow.indexOf('  cache-invalidate:'),
    workflow.indexOf('  # ENGLISH CACHE FINALIZER'),
  );
  const finalizerJob = workflow.slice(
    workflow.indexOf('  finalize-english-cache:'),
    workflow.indexOf('  # TRIGGER TRANSLATION'),
  );
  const triggerJob = workflow.slice(workflow.indexOf('  trigger-translate:'));

  assert.notEqual(
    statSync(INVALIDATOR).mode & 0o111,
    0,
    'workflow invokes the invalidator directly, so it must be committed executable',
  );
  assert.match(invalidationJob, /sparse-checkout: scripts\/invalidate-cache\.sh/);
  assert.match(invalidationJob, /sparse-checkout-cone-mode: false/);
  assert.match(invalidationJob, /BATCH_SIZE: ['"]10['"]/);
  assert.match(invalidationJob, /CONTENT_TYPE: skills/);
  assert.match(invalidationJob, /CURL_MAX_TIME: ['"]30['"]/);
  assert.match(invalidationJob, /MAX_ATTEMPTS: ['"]3['"]/);
  assert.match(invalidationJob, /run: \.\/scripts\/invalidate-cache\.sh/);
  assert.doesNotMatch(invalidationJob, /uses: \.\/\.github\/actions\/invalidate-cache/);
  assert.doesNotMatch(invalidationJob, /curl .*api\/cache\/invalidate/);
  assert.match(
    invalidationJob,
    /Report cache invalidation failure[\s\S]*if: failure\(\) && steps\.invalidate\.outcome == 'failure'/,
  );
  assert.match(finalizerJob, /needs: \[sync, calculate-scores, cache-invalidate\]/);
  assert.match(finalizerJob, /needs\.cache-invalidate\.result == 'success'/);
  assert.match(triggerJob, /needs: \[sync, cache-invalidate, finalize-english-cache\]/);
  assert.match(
    triggerJob,
    /if: always\(\) && needs\.sync\.result == 'success' && needs\.cache-invalidate\.result == 'success'/,
  );
});

test('sync cache invalidation has a fixed 10-batch budget below its job timeout', () => {
  const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
  const invalidationJob = workflow.slice(
    workflow.indexOf('  cache-invalidate:'),
    workflow.indexOf('  # ENGLISH CACHE FINALIZER'),
  );
  const readInteger = (name) => {
    const match = invalidationJob.match(
      new RegExp(`^\\s+${name}:\\s*['"]?(\\d+)['"]?\\s*$`, 'm'),
    );
    return match ? Number(match[1]) : undefined;
  };

  const timeoutMinutes = readInteger('timeout-minutes');
  const settings = {
    BATCH_SIZE: readInteger('BATCH_SIZE'),
    MAX_ATTEMPTS: readInteger('MAX_ATTEMPTS'),
    CURL_MAX_TIME: readInteger('CURL_MAX_TIME'),
    RETRY_BASE_SECONDS: readInteger('RETRY_BASE_SECONDS'),
    MAX_ITEMS: readInteger('MAX_ITEMS'),
  };
  const expectedSettings = {
    BATCH_SIZE: 10,
    MAX_ATTEMPTS: 3,
    CURL_MAX_TIME: 30,
    RETRY_BASE_SECONDS: 5,
    MAX_ITEMS: 100,
  };
  const violations = [];

  if (timeoutMinutes === undefined || timeoutMinutes < 25) {
    violations.push(
      `cache-invalidate timeout-minutes must be at least 25 (found ${timeoutMinutes ?? 'missing'})`,
    );
  }
  for (const [name, expected] of Object.entries(expectedSettings)) {
    if (settings[name] !== expected) {
      violations.push(
        `cache-invalidate must fix ${name}=${expected} (found ${settings[name] ?? 'missing'})`,
      );
    }
  }
  assert.deepEqual(violations, []);

  const maxBatches = Math.ceil(settings.MAX_ITEMS / settings.BATCH_SIZE);
  const retrySleepSeconds = settings.RETRY_BASE_SECONDS
    * ((settings.MAX_ATTEMPTS - 1) * settings.MAX_ATTEMPTS / 2);
  const worstSecondsPerBatch = settings.MAX_ATTEMPTS * settings.CURL_MAX_TIME
    + retrySleepSeconds;
  const worstCaseSeconds = maxBatches * worstSecondsPerBatch;

  assert.equal(maxBatches, 10);
  assert.equal(worstSecondsPerBatch, 105);
  assert.equal(worstCaseSeconds, 1050);
  assert.ok(worstCaseSeconds < timeoutMinutes * 60);
});
