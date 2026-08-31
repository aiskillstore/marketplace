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
count_lock="$FAKE_CURL_LOG_DIR/count.lock"
while ! mkdir "$count_lock" 2>/dev/null; do
  :
done
count=0
if [ -f "$count_file" ]; then
  count=$(cat "$count_file")
fi
count=$((count + 1))
printf '%s' "$count" > "$count_file"
rmdir "$count_lock"

response_file=""
payload_arg=""
max_time=""
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
    --max-time)
      max_time="$2"
      shift 2
      ;;
    -H|-X|-w|--connect-timeout)
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

payload_file="\${payload_arg#@}"
cp "$payload_file" "$FAKE_CURL_LOG_DIR/payload-$count.json"
printf '%s' "$max_time" > "$FAKE_CURL_LOG_DIR/max-time-$count"

IFS=',' read -r -a results <<< "$FAKE_CURL_RESULTS"
result_index=$((count - 1))
if [ "$result_index" -ge "\${#results[@]}" ]; then
  result_index=$((\${#results[@]} - 1))
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
    jq '{
      preflight: false,
      type: (if .type == "plugins" then "packs" else .type end),
      slugs,
      invalidated: {
        total: (.slugs | length),
        page: (.slugs | length),
        api: 0,
        artifacts: 0,
        listVersionBumped: (if (.type == "skills" or .type == "packs" or .type == "plugins") then true else false end),
        listMaxStaleSeconds: 0
      }
    }' "$payload_file" > "$response_file"
    printf '%s' "$status"
    exit "$curl_exit"
    ;;
  contract:malformed)
    printf '{' > "$response_file"
    printf '200'
    ;;
  contract:preflight)
    jq '{preflight: true, type, slugs, invalidated: {total: 1, page: 1, api: 0, artifacts: 0, listVersionBumped: true, listMaxStaleSeconds: 0}}' "$payload_file" > "$response_file"
    printf '200'
    ;;
  contract:wrong-slugs)
    jq '{preflight: false, type, slugs: ["unexpected"], invalidated: {total: 1, page: 1, api: 0, artifacts: 0, listVersionBumped: true, listMaxStaleSeconds: 0}}' "$payload_file" > "$response_file"
    printf '200'
    ;;
  contract:missing-invalidated)
    jq '{preflight: false, type, slugs}' "$payload_file" > "$response_file"
    printf '200'
    ;;
  contract:zero-invalidated)
    jq '{preflight: false, type, slugs, invalidated: {total: 0, page: 0, api: 0, artifacts: 0, listVersionBumped: false, listMaxStaleSeconds: 0}}' "$payload_file" > "$response_file"
    printf '200'
    ;;
  contract:no-list-bump)
    jq '{preflight: false, type, slugs, invalidated: {total: 1, page: 1, api: 0, artifacts: 0, listVersionBumped: false, listMaxStaleSeconds: 0}}' "$payload_file" > "$response_file"
    printf '200'
    ;;
  closure-overflow)
    printf '{"message":"Dependent pack closure exceeds the 100-pack cap"}' > "$response_file"
    printf '409'
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

const FAKE_DATE = `#!/usr/bin/env bash
count=0
if [ -f "$FAKE_DATE_COUNT" ]; then
  count=$(cat "$FAKE_DATE_COUNT")
fi
count=$((count + 1))
printf '%s' "$count" > "$FAKE_DATE_COUNT"
IFS=',' read -r -a epochs <<< "$FAKE_DATE_EPOCHS"
index=$((count - 1))
if [ "$index" -ge "\${#epochs[@]}" ]; then
  index=$((\${#epochs[@]} - 1))
fi
printf '%s\n' "\${epochs[$index]}"
`;

function runInvalidator({
  slugs = '',
  slugsFile = '',
  secret = SECRET,
  batchSize = 2,
  maxAttempts = 3,
  maxItems = 100,
  retryBaseSeconds = 1,
  fallbackMaxAttempts = 2,
  fallbackRetryBaseSeconds = 1,
  fallbackCurlMaxTime = 9,
  fallbackConcurrency = 1,
  results = 'http:200',
  contentType = 'skills',
  mktempFails = false,
  fakeDateEpochs = '',
} = {}) {
  const tmp = mkdtempSync(join(tmpdir(), 'invalidate-cache-test-'));
  const bin = join(tmp, 'bin');
  const curlLogDir = join(tmp, 'curl-log');
  const sleepLog = join(tmp, 'sleep.log');
  const githubOutput = join(tmp, 'github-output');
  const fakeDateCount = join(tmp, 'date-count');
  mkdirSync(bin);
  mkdirSync(curlLogDir);
  writeFileSync(join(bin, 'curl'), FAKE_CURL, { mode: 0o755 });
  writeFileSync(join(bin, 'sleep'), FAKE_SLEEP, { mode: 0o755 });
  if (fakeDateEpochs) {
    writeFileSync(join(bin, 'date'), FAKE_DATE, { mode: 0o755 });
  }
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
      FALLBACK_MAX_ATTEMPTS: String(fallbackMaxAttempts),
      FALLBACK_RETRY_BASE_SECONDS: String(fallbackRetryBaseSeconds),
      FALLBACK_CURL_MAX_TIME: String(fallbackCurlMaxTime),
      FALLBACK_CONCURRENCY: String(fallbackConcurrency),
      CURL_CONNECT_TIMEOUT: '1',
      CURL_MAX_TIME: '2',
      GITHUB_OUTPUT: githubOutput,
      FAKE_CURL_LOG_DIR: curlLogDir,
      FAKE_CURL_RESULTS: results,
      FAKE_SLEEP_LOG: sleepLog,
      FAKE_DATE_COUNT: fakeDateCount,
      FAKE_DATE_EPOCHS: fakeDateEpochs,
    },
  });

  const payloads = readdirSync(curlLogDir)
    .filter((name) => /^payload-\d+\.json$/.test(name))
    .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]))
    .map((name) => JSON.parse(readFileSync(join(curlLogDir, name), 'utf8')));
  const sleeps = readdirSync(tmp).includes('sleep.log')
    ? readFileSync(sleepLog, 'utf8').trim().split('\n').filter(Boolean)
    : [];
  const maxTimes = readdirSync(curlLogDir)
    .filter((name) => /^max-time-\d+$/.test(name))
    .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]))
    .map((name) => Number(readFileSync(join(curlLogDir, name), 'utf8')));
  const outputs = {};
  if (readdirSync(tmp).includes('github-output')) {
    for (const line of readFileSync(githubOutput, 'utf8').trim().split('\n').filter(Boolean)) {
      const separator = line.indexOf('=');
      assert.notEqual(separator, -1, `Invalid GITHUB_OUTPUT line: ${line}`);
      outputs[line.slice(0, separator)] = Number(line.slice(separator + 1));
    }
  }

  assert.doesNotMatch(`${result.stdout}${result.stderr}`, new RegExp(SECRET));
  return { result, payloads, sleeps, maxTimes, outputs };
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

test('plugin and release responses obey their canonical list-version contracts', () => {
  const plugin = runInvalidator({ slugs: 'alpha', contentType: 'plugins' });
  assert.equal(plugin.result.status, 0);
  assert.equal(plugin.payloads[0].type, 'plugins');

  const release = runInvalidator({ slugs: 'alpha', contentType: 'releases' });
  assert.equal(release.result.status, 0);
  assert.equal(release.payloads[0].type, 'releases');
});

test('inputs above the explicit 100-item budget fail before making an HTTP request', () => {
  const slugs = Array.from({ length: 101 }, (_, index) => `skill-${index}`);
  const { result, payloads, sleeps } = runInvalidator({
    slugs: slugs.join(','),
    batchSize: 10,
    maxItems: 100,
  });

  assert.notEqual(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads, []);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /item count 101 exceeds MAX_ITEMS 100/);
});

test('temporary workspace failure fails closed before making an HTTP request', () => {
  const { result, payloads, outputs } = runInvalidator({
    slugs: 'alpha',
    mktempFails: true,
  });

  assert.notEqual(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads, []);
  assert.deepEqual(outputs, {});
  assert.match(result.stderr, /Failed to create temporary workspace/);
});

test('retryable non-timeout curl transport failures retry the same idempotent batch', () => {
  for (const exitCode of [5, 6, 7, 16, 18, 35, 52, 55, 56, 92]) {
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

test('the exact pre-mutation closure overflow 409 safely splits into single requests', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta',
    results: 'closure-overflow,http:200,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads.map((payload) => payload.slugs), [
    ['alpha', 'beta'],
    ['alpha'],
    ['beta'],
  ]);
  assert.deepEqual(sleeps, []);
  assert.deepEqual(outputs, { total_count: 2, success_count: 2, failed_count: 0 });
});

test('unrecognized 409 responses fail closed without split fallback', () => {
  const { result, payloads, outputs } = runInvalidator({
    slugs: 'alpha,beta',
    results: 'http:409',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(outputs, { total_count: 2, success_count: 0, failed_count: 2 });
});

test('HTTP 401 takes precedence over curl exit 18 and fails after one request', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    results: 'http:401:18,http:200',
  });

  assert.notEqual(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 1);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /Non-transient HTTP 401/);
});

test('HTTP 403 takes precedence over curl exit 28 and fails after one request', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    results: 'http:403:28,http:200',
  });

  assert.notEqual(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
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

test('HTTP 200 takes precedence over curl exit 18 and succeeds without retrying', () => {
  const { result, payloads, sleeps } = runInvalidator({
    slugs: 'alpha',
    results: 'http:200:18,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 1);
  assert.deepEqual(sleeps, []);
  assert.doesNotMatch(result.stderr, /curl transport failure|retrying/);
});

test('2xx responses fail closed when the cache response contract is invalid', () => {
  for (const scenario of [
    'contract:malformed',
    'contract:preflight',
    'contract:wrong-slugs',
    'contract:missing-invalidated',
    'contract:zero-invalidated',
    'contract:no-list-bump',
  ]) {
    const { result, payloads, sleeps, outputs } = runInvalidator({
      slugs: 'alpha',
      results: scenario,
    });

    assert.notEqual(result.status, 0, scenario);
    assert.equal(payloads.length, 1, scenario);
    assert.deepEqual(sleeps, [], scenario);
    assert.deepEqual(outputs, {
      total_count: 1,
      success_count: 0,
      failed_count: 1,
    });
    assert.match(result.stderr, /response violated the requested contract/);
  }
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
  assert.match(result.stderr, /Transient curl timeout \(exit 28\)/);
});

test('a multi-item timeout skips batch retries and latches item fallback for later batches', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma,delta,epsilon,zeta',
    batchSize: 2,
    maxAttempts: 3,
    fallbackConcurrency: 1,
    results: 'transport:28,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads.map((payload) => payload.slugs), [
    ['alpha', 'beta'],
    ['alpha'],
    ['beta'],
    ['gamma'],
    ['delta'],
    ['epsilon'],
    ['zeta'],
  ]);
  assert.deepEqual(sleeps, []);
  assert.match(result.stderr, /without another batch retry/);
  assert.equal(
    (result.stderr.match(/Skipping multi-item request/g) || []).length,
    2,
  );
  assert.deepEqual(outputs, {
    total_count: 6,
    success_count: 6,
    failed_count: 0,
  });
});

test('parallel item fallback preserves one completion result for every requested item', () => {
  const { result, payloads, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma,delta',
    batchSize: 4,
    fallbackConcurrency: 2,
    results: 'transport:28,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta', 'gamma', 'delta']);
  assert.deepEqual(
    payloads.slice(1).map((payload) => payload.slugs[0]).sort(),
    ['alpha', 'beta', 'delta', 'gamma'],
  );
  assert.equal((result.stdout.match(/completed for item:/g) || []).length, 4);
  assert.deepEqual(outputs, {
    total_count: 4,
    success_count: 4,
    failed_count: 0,
  });
  assert.equal(outputs.total_count, outputs.success_count + outputs.failed_count);
});

test('the 78-item timeout shape completes through one batch probe and item evidence only', () => {
  const slugs = Array.from({ length: 78 }, (_, index) => `sync-item-${index}`);
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: slugs.join(','),
    batchSize: 10,
    fallbackConcurrency: 2,
    results: 'transport:28,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 79);
  assert.deepEqual(payloads[0].slugs, slugs.slice(0, 10));
  assert.ok(payloads.slice(1).every((payload) => payload.slugs.length === 1));
  assert.deepEqual(
    payloads.slice(1).map((payload) => payload.slugs[0]).sort(),
    [...slugs].sort(),
  );
  assert.deepEqual(sleeps, []);
  assert.equal((result.stdout.match(/completed for item:/g) || []).length, 78);
  assert.deepEqual(outputs, {
    total_count: 78,
    success_count: 78,
    failed_count: 0,
  });
});

test('non-transient curl failures fail closed without retrying the failed batch', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma',
    results: 'transport:3,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 2);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.deepEqual(payloads[1].slugs, ['gamma']);
  assert.deepEqual(sleeps, []);
  assert.deepEqual(outputs, { total_count: 3, success_count: 1, failed_count: 2 });
});

test('non-transient HTTP failures fail closed without retrying the failed batch', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma',
    results: 'http:400,http:200',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 2);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.deepEqual(payloads[1].slugs, ['gamma']);
  assert.deepEqual(sleeps, []);
  assert.deepEqual(outputs, { total_count: 3, success_count: 1, failed_count: 2 });
});

test('an exhausted multi-item batch falls back to bounded single-item requests', () => {
  const { result, payloads, sleeps, maxTimes, outputs } = runInvalidator({
    slugs: 'alpha,beta,gamma,delta,epsilon',
    maxAttempts: 2,
    fallbackMaxAttempts: 2,
    results: 'http:200,http:503,http:503,http:200,http:200,http:200',
  });

  assert.equal(result.status, 0, `STDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  assert.equal(payloads.length, 6);
  assert.deepEqual(payloads[0].slugs, ['alpha', 'beta']);
  assert.deepEqual(payloads.slice(1).map((payload) => payload.slugs), [
    ['gamma', 'delta'],
    ['gamma', 'delta'],
    ['gamma'],
    ['delta'],
    ['epsilon'],
  ]);
  assert.deepEqual(sleeps, ['1']);
  assert.deepEqual(maxTimes, [2, 2, 2, 9, 9, 2]);
  assert.deepEqual(outputs, {
    total_count: 5,
    success_count: 5,
    failed_count: 0,
  });
  assert.equal(outputs.total_count, outputs.success_count + outputs.failed_count);
});

test('single-item fallback failures preserve exact counts and fail closed', () => {
  const { result, payloads, outputs } = runInvalidator({
    slugs: 'alpha,beta',
    maxAttempts: 2,
    fallbackMaxAttempts: 2,
    results: 'http:503,http:503,http:200,http:503,http:503',
  });

  assert.notEqual(result.status, 0);
  assert.deepEqual(payloads.map((payload) => payload.slugs), [
    ['alpha', 'beta'],
    ['alpha', 'beta'],
    ['alpha'],
    ['beta'],
    ['beta'],
  ]);
  assert.deepEqual(outputs, {
    total_count: 2,
    success_count: 1,
    failed_count: 1,
  });
  assert.equal(outputs.total_count, outputs.success_count + outputs.failed_count);
});

test('the global deadline stops retries and fallback before the workflow timeout', () => {
  const { result, payloads, sleeps, outputs } = runInvalidator({
    slugs: 'alpha,beta',
    maxAttempts: 3,
    results: 'http:503',
    fakeDateEpochs: '100,100,1300',
  });

  assert.notEqual(result.status, 0);
  assert.equal(payloads.length, 1);
  assert.deepEqual(sleeps, []);
  assert.deepEqual(outputs, { total_count: 2, success_count: 0, failed_count: 2 });
  assert.match(result.stderr, /runtime budget exhausted/);
});

test('sync workflow uses an artifact-backed bounded invalidator and preserves downstream success gates', () => {
  const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
  const invalidationJob = workflow.slice(
    workflow.indexOf('  cache-invalidate-shard:'),
    workflow.indexOf('  cache-invalidate:'),
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
  assert.match(invalidationJob, /scripts\/invalidate-cache\.sh/);
  assert.match(invalidationJob, /name: synced-slugs/);
  assert.match(invalidationJob, /BATCH_SIZE: ['"]1['"]/);
  assert.match(invalidationJob, /CONTENT_TYPE: skills/);
  assert.match(invalidationJob, /CURL_MAX_TIME: ['"]30['"]/);
  assert.match(invalidationJob, /FALLBACK_CONCURRENCY: ['"]1['"]/);
  assert.match(invalidationJob, /FALLBACK_CURL_MAX_TIME: ['"]30['"]/);
  assert.match(invalidationJob, /FALLBACK_MAX_ATTEMPTS: ['"]1['"]/);
  assert.match(invalidationJob, /MAX_ATTEMPTS: ['"]2['"]/);
  assert.match(invalidationJob, /MAX_ITEMS: ['"]1['"]/);
  assert.match(invalidationJob, /MAX_RUNTIME_SECONDS: ['"]240['"]/);
  assert.match(invalidationJob, /run: \.\/scripts\/invalidate-cache\.sh/);
  assert.doesNotMatch(invalidationJob, /uses: \.\/\.github\/actions\/invalidate-cache/);
  assert.doesNotMatch(invalidationJob, /curl .*api\/cache\/invalidate/);
  assert.doesNotMatch(invalidationJob, /needs\.sync\.outputs\.synced_slugs/);
  assert.match(finalizerJob, /needs: \[sync, calculate-scores, cache-invalidate\]/);
  assert.match(finalizerJob, /needs\.cache-invalidate\.result == 'success'/);
  assert.match(workflow, /runs\?status=completed&event=push&per_page=100/);
  assert.match(workflow, /actions\/runs\/\$run_id\/jobs\?per_page=100/);
  assert.match(workflow, /Previous provider sync run .* unknown partial effect/);
  assert.match(triggerJob, /needs: \[sync, cache-invalidate, finalize-english-cache\]/);
  assert.match(
    triggerJob,
    /if: always\(\) && vars\.CACHE_FINALIZER_AUTOMATION_ENABLED == 'true' && needs\.sync\.result == 'success' && needs\.cache-invalidate\.result == 'success'/,
  );
});

test('each cache invalidation shard has a hard runtime deadline below its own timeout', () => {
  const workflow = readFileSync(SYNC_WORKFLOW, 'utf8');
  const invalidator = readFileSync(INVALIDATOR, 'utf8');
  const invalidationJob = workflow.slice(
    workflow.indexOf('  cache-invalidate-shard:'),
    workflow.indexOf('  cache-invalidate:'),
  );
  const readInteger = (name) => {
    const match = invalidationJob.match(
      new RegExp(`^\\s+${name}:\\s*['"]?(\\d+)['"]?\\s*$`, 'm'),
    );
    return match ? Number(match[1]) : undefined;
  };

  const timeoutMinutes = readInteger('timeout-minutes');
  const settings = {
    MAX_PARALLEL: readInteger('max-parallel'),
    BATCH_SIZE: readInteger('BATCH_SIZE'),
    MAX_ATTEMPTS: readInteger('MAX_ATTEMPTS'),
    CURL_MAX_TIME: readInteger('CURL_MAX_TIME'),
    RETRY_BASE_SECONDS: readInteger('RETRY_BASE_SECONDS'),
    FALLBACK_CONCURRENCY: readInteger('FALLBACK_CONCURRENCY'),
    FALLBACK_MAX_ATTEMPTS: readInteger('FALLBACK_MAX_ATTEMPTS'),
    FALLBACK_CURL_MAX_TIME: readInteger('FALLBACK_CURL_MAX_TIME'),
    FALLBACK_RETRY_BASE_SECONDS: readInteger('FALLBACK_RETRY_BASE_SECONDS'),
    MAX_ITEMS: readInteger('MAX_ITEMS'),
    MAX_RUNTIME_SECONDS: readInteger('MAX_RUNTIME_SECONDS'),
  };
  const expectedSettings = {
    MAX_PARALLEL: 1,
    BATCH_SIZE: 1,
    MAX_ATTEMPTS: 2,
    CURL_MAX_TIME: 30,
    RETRY_BASE_SECONDS: 5,
    FALLBACK_CONCURRENCY: 1,
    FALLBACK_MAX_ATTEMPTS: 1,
    FALLBACK_CURL_MAX_TIME: 30,
    FALLBACK_RETRY_BASE_SECONDS: 2,
    MAX_ITEMS: 1,
    MAX_RUNTIME_SECONDS: 240,
  };
  const violations = [];

  if (timeoutMinutes === undefined || timeoutMinutes < 5) {
    violations.push(
      `cache-invalidate-shard timeout-minutes must be at least 5 (found ${timeoutMinutes ?? 'missing'})`,
    );
  }
  for (const [name, expected] of Object.entries(expectedSettings)) {
    if (settings[name] !== expected) {
      violations.push(
        `cache-invalidate-shard must fix ${name}=${expected} (found ${settings[name] ?? 'missing'})`,
      );
    }
  }
  assert.deepEqual(violations, []);

  const runtimeMatch = invalidator.match(
    /^MAX_RUNTIME_SECONDS="\$\{MAX_RUNTIME_SECONDS:-([0-9]+)\}"$/m,
  );
  assert.ok(runtimeMatch, 'invalidator must declare a fixed default runtime deadline');
  const defaultMaxRuntimeSeconds = Number(runtimeMatch[1]);
  assert.ok(
    settings.MAX_RUNTIME_SECONDS <= defaultMaxRuntimeSeconds,
    'workflow runtime override must not exceed the script default',
  );
  assert.ok(
    settings.MAX_RUNTIME_SECONDS <= timeoutMinutes * 60 - 60,
    'script deadline must leave one minute for setup and teardown',
  );
  assert.equal(
    settings.MAX_PARALLEL * settings.FALLBACK_CONCURRENCY,
    1,
    'matrix-wide fallback pressure must remain strictly serial',
  );
});
