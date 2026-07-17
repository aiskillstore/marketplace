import assert from 'node:assert/strict';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  rmSync,
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
const refreshHelperSource = readFileSync(
  resolve(repoRoot, 'scripts/refresh-security-research-stats.sh'),
  'utf8',
);
const monitorWorkflow = readFileSync(
  resolve(repoRoot, '.github/workflows/monitor-skill-sources.yml'),
  'utf8',
);

const validUsage = '{"object":"usage_stats","totals":{"total_tokens":7,"cost_usd":1.25}}';
const successfulResponse = {
  curlExit: 0,
  httpStatus: '200',
  body: validUsage,
  headers: 'HTTP/2 200\r\ncontent-type: application/json\r\n\r\n',
};

function shellEnvironment(overrides = {}) {
  const env = { ...process.env, ...overrides };
  delete env.BASH_ENV;
  delete env.CD_PATH;
  delete env.ENV;
  return env;
}

function extractLiteralRunBody(workflow, stepName) {
  const lines = workflow.split(/\r?\n/);
  const stepMarker = `      - name: ${stepName}`;
  const stepIndex = lines.indexOf(stepMarker);
  assert.notEqual(stepIndex, -1, `missing workflow step: ${stepName}`);

  let runIndex = stepIndex + 1;
  while (runIndex < lines.length && !/^      - name: /.test(lines[runIndex])) {
    if (lines[runIndex] === '        run: |') {
      break;
    }
    runIndex += 1;
  }
  assert.equal(lines[runIndex], '        run: |', `missing literal run body: ${stepName}`);

  let endIndex = runIndex + 1;
  while (endIndex < lines.length && !/^      - name: /.test(lines[endIndex])) {
    endIndex += 1;
  }

  return `${lines
    .slice(runIndex + 1, endIndex)
    .map((line, index) => {
      if (line === '') {
        return '';
      }
      assert.ok(
        line.startsWith('          '),
        `unexpected indentation in ${stepName} run body at line ${runIndex + index + 2}`,
      );
      return line.slice(10);
    })
    .join('\n')}\n`;
}

const syncComputeRunBody = extractLiteralRunBody(
  computeWorkflow,
  'Sync audit compute snapshot',
);

function writeExecutable(path, source) {
  writeFileSync(path, source);
  chmodSync(path, 0o755);
}

function writeMaliciousCurlConfig(root) {
  const curlHome = join(root, 'curl-home');
  mkdirSync(curlHome, { recursive: true });
  writeFileSync(
    join(curlHome, '.curlrc'),
    [
      'insecure',
      'retry = 3',
      'retry-all-errors',
      'retry-delay = 0',
      '',
    ].join('\n'),
  );
  return curlHome;
}

function installFakeNetwork(sequence, { maliciousCurlConfig = false } = {}) {
  assert.ok(sequence.length > 0, 'fake curl requires at least one response');

  const root = mkdtempSync(join(tmpdir(), 'audit-compute-network-'));
  const bin = join(root, 'bin');
  const responses = join(root, 'responses');
  mkdirSync(bin, { recursive: true });
  mkdirSync(responses, { recursive: true });

  for (const [index, response] of sequence.entries()) {
    const request = index + 1;
    writeFileSync(join(responses, `${request}.curl-exit`), String(response.curlExit));
    writeFileSync(join(responses, `${request}.http-status`), response.httpStatus ?? '000');
    writeFileSync(join(responses, `${request}.body`), response.body ?? '');
    writeFileSync(join(responses, `${request}.headers`), response.headers ?? '');
    writeFileSync(join(responses, `${request}.stderr`), response.stderr ?? '');
    if (response.insecureResponse) {
      const insecure = response.insecureResponse;
      writeFileSync(
        join(responses, `${request}.insecure.curl-exit`),
        String(insecure.curlExit),
      );
      writeFileSync(
        join(responses, `${request}.insecure.http-status`),
        insecure.httpStatus ?? '000',
      );
      writeFileSync(join(responses, `${request}.insecure.body`), insecure.body ?? '');
      writeFileSync(
        join(responses, `${request}.insecure.headers`),
        insecure.headers ?? '',
      );
      writeFileSync(
        join(responses, `${request}.insecure.stderr`),
        insecure.stderr ?? '',
      );
    }
  }
  writeFileSync(join(root, 'response-count'), String(sequence.length));

  writeExecutable(
    join(bin, 'curl'),
    `#!/usr/bin/env bash
set -euo pipefail

root="\${FAKE_CURL_ROOT:?FAKE_CURL_ROOT is required}"
invocation_count=0
[[ ! -f "$root/invocation-count" ]] || invocation_count="$(cat "$root/invocation-count")"
invocation_count=$((invocation_count + 1))
printf '%s' "$invocation_count" > "$root/invocation-count"
invocation_dir="$root/invocation-$invocation_count"
mkdir -p "$invocation_dir"

arg_number=0
for arg in "$@"; do
  arg_number=$((arg_number + 1))
  printf '%s' "$arg" > "$invocation_dir/arg-$arg_number"
done
printf '%s' "$arg_number" > "$invocation_dir/arg-count"

config_enabled=true
if [[ "\${1:-}" == "--disable" ]]; then
  config_enabled=false
fi

retry_count=0
retry_all_errors=false
effective_insecure=false
if [[ "$config_enabled" == true && -f "\${CURL_HOME:-$HOME}/.curlrc" ]]; then
  while IFS= read -r config_line || [[ -n "$config_line" ]]; do
    normalized="\${config_line//[[:space:]]/}"
    case "$normalized" in
      insecure) effective_insecure=true ;;
      retry=*) retry_count="\${normalized#retry=}" ;;
      retry-all-errors) retry_all_errors=true ;;
    esac
  done < "\${CURL_HOME:-$HOME}/.curlrc"
fi

method=GET
output_file=''
header_file=''
write_out=''
read_headers=false
args=("$@")
index=0
while ((index < \${#args[@]})); do
  argument="\${args[$index]}"
  case "$argument" in
    --request|-X)
      index=$((index + 1))
      method="\${args[$index]}"
      ;;
    --output|-o)
      index=$((index + 1))
      output_file="\${args[$index]}"
      ;;
    --dump-header|-D)
      index=$((index + 1))
      header_file="\${args[$index]}"
      ;;
    --write-out|-w)
      index=$((index + 1))
      write_out="\${args[$index]}"
      ;;
    --retry)
      index=$((index + 1))
      retry_count="\${args[$index]}"
      ;;
    --retry=*)
      retry_count="\${argument#--retry=}"
      ;;
    --retry-all-errors)
      retry_all_errors=true
      ;;
    --insecure|-k)
      effective_insecure=true
      ;;
    --header|-H)
      index=$((index + 1))
      [[ "\${args[$index]}" != "@-" ]] || read_headers=true
      ;;
    --connect-timeout|--max-time|--proto|--retry-delay|--data|--data-raw|--data-binary)
      index=$((index + 1))
      ;;
    --)
      break
      ;;
  esac
  index=$((index + 1))
done

if [[ "$read_headers" == true ]]; then
  cat > "$invocation_dir/stdin"
fi
if [[ "$effective_insecure" == true ]]; then
  printf '%s\n' "$invocation_count" >> "$root/insecure-invocations"
fi
printf '%s' "$method" > "$invocation_dir/method"

internal_attempt=0
while true; do
  request_count=0
  [[ ! -f "$root/request-count" ]] || request_count="$(cat "$root/request-count")"
  request_count=$((request_count + 1))
  printf '%s' "$request_count" > "$root/request-count"
  printf '%s\n' "$method" >> "$root/request-methods"

  response_count="$(cat "$root/response-count")"
  if ((request_count > response_count)); then
    echo "unexpected extra curl request $request_count" >&2
    curl_exit=99
    http_status=000
    : > "$root/unexpected-request"
    if [[ -n "$output_file" ]]; then : > "$output_file"; fi
    if [[ -n "$header_file" ]]; then : > "$header_file"; fi
  else
    response="$root/responses/$request_count"
    if [[ "$effective_insecure" == true && -f "$response.insecure.curl-exit" ]]; then
      response="$response.insecure"
    fi
    curl_exit="$(cat "$response.curl-exit")"
    http_status="$(cat "$response.http-status")"
    cat "$response.stderr" >&2
    if [[ -n "$output_file" ]]; then
      cat "$response.body" > "$output_file"
    else
      cat "$response.body"
    fi
    if [[ -n "$header_file" ]]; then
      cat "$response.headers" > "$header_file"
    fi
  fi

  if [[ "$curl_exit" -eq 0 ]]; then
    break
  fi
  if ((internal_attempt < retry_count)) && [[ "$retry_all_errors" == true ]]; then
    internal_attempt=$((internal_attempt + 1))
    continue
  fi
  break
done

if [[ -n "$write_out" ]]; then
  if [[ "$write_out" != '%{http_code}' ]]; then
    echo "unsupported fake curl --write-out format: $write_out" >&2
    exit 98
  fi
  printf '%s' "$http_status"
fi
exit "$curl_exit"
`,
  );

  writeExecutable(
    join(bin, 'sleep'),
    `#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$1" >> "\${FAKE_CURL_ROOT:?}/sleep.log"
`,
  );

  const curlHome = maliciousCurlConfig
    ? writeMaliciousCurlConfig(root)
    : join(root, 'empty-curl-home');
  mkdirSync(curlHome, { recursive: true });
  return { root, bin, curlHome };
}

function readCount(path) {
  return existsSync(path) ? Number(readFileSync(path, 'utf8')) : 0;
}

function readLines(path) {
  if (!existsSync(path)) {
    return [];
  }
  return readFileSync(path, 'utf8').trim().split(/\r?\n/).filter(Boolean);
}

function readCurlInvocations(fixture) {
  const count = readCount(join(fixture.root, 'invocation-count'));
  return Array.from({ length: count }, (_, invocationIndex) => {
    const directory = join(fixture.root, `invocation-${invocationIndex + 1}`);
    const argCount = readCount(join(directory, 'arg-count'));
    return Array.from({ length: argCount }, (_, argIndex) =>
      readFileSync(join(directory, `arg-${argIndex + 1}`), 'utf8'));
  });
}

function collectNetworkResult(fixture) {
  return {
    invocations: readCurlInvocations(fixture),
    requests: readCount(join(fixture.root, 'request-count')),
    requestMethods: readLines(join(fixture.root, 'request-methods')),
    sleeps: readLines(join(fixture.root, 'sleep.log')),
    insecureInvocations: readLines(join(fixture.root, 'insecure-invocations')),
    unexpectedRequest: existsSync(join(fixture.root, 'unexpected-request')),
  };
}

function runHelper(sequence, { maliciousCurlConfig = false, extraEnv = {} } = {}) {
  const fixture = installFakeNetwork(sequence, { maliciousCurlConfig });
  try {
    const result = spawnSync(helper, ['https://helm.example/v1/usage/stats'], {
      encoding: 'utf8',
      timeout: 10_000,
      env: shellEnvironment({
        ...extraEnv,
        PATH: `${fixture.bin}:${process.env.PATH}`,
        CURL_HOME: fixture.curlHome,
        FAKE_CURL_ROOT: fixture.root,
        HELM_API_KEY: 'test-helm-key',
        AUDIT_READ_MAX_ATTEMPTS: '3',
        AUDIT_READ_RETRY_BASE_SECONDS: '2',
      }),
    });
    return { ...result, ...collectNetworkResult(fixture) };
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
}

function optionValue(argv, name) {
  const index = argv.indexOf(name);
  assert.notEqual(index, -1, `missing curl option ${name}: ${argv.join(' ')}`);
  assert.ok(index + 1 < argv.length, `missing value for curl option ${name}`);
  return argv[index + 1];
}

function runHelperWithArguments(args, extraEnv = {}) {
  const fixture = installFakeNetwork([successfulResponse]);
  try {
    const result = spawnSync(helper, args, {
      encoding: 'utf8',
      timeout: 10_000,
      env: shellEnvironment({
        ...extraEnv,
        PATH: `${fixture.bin}:${process.env.PATH}`,
        CURL_HOME: fixture.curlHome,
        FAKE_CURL_ROOT: fixture.root,
        HELM_API_KEY: 'test-helm-key',
      }),
    });
    return { ...result, ...collectNetworkResult(fixture) };
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
}

function runWorkflow(
  helmUsageJson,
  postSequence = [{
    curlExit: 0,
    httpStatus: '200',
    body: '{"snapshot_id":1}',
    headers: 'HTTP/2 200\r\ncontent-type: application/json\r\n\r\n',
  }],
) {
  const fixture = installFakeNetwork(postSequence, { maliciousCurlConfig: true });
  const scriptsDirectory = join(fixture.root, 'scripts');
  const usageFile = join(fixture.root, 'helm-usage.json');
  const helperLog = join(fixture.root, 'helper.log');
  const summary = join(fixture.root, 'summary.md');
  mkdirSync(scriptsDirectory, { recursive: true });
  writeFileSync(usageFile, helmUsageJson);

  writeExecutable(
    join(scriptsDirectory, 'fetch-audit-compute-usage.sh'),
    `#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$*" >> "\${FAKE_WORKFLOW_HELPER_LOG:?}"
cat "\${FAKE_HELM_USAGE_FILE:?}"
`,
  );
  writeExecutable(
    join(fixture.bin, 'date'),
    `#!/usr/bin/env bash
set -euo pipefail
[[ "$*" == '-u +%F' ]]
printf '%s\n' '2026-07-17'
`,
  );

  try {
    const result = spawnSync('bash', ['-c', syncComputeRunBody], {
      cwd: fixture.root,
      encoding: 'utf8',
      timeout: 10_000,
      env: shellEnvironment({
        PATH: `${fixture.bin}:${process.env.PATH}`,
        CURL_HOME: fixture.curlHome,
        FAKE_CURL_ROOT: fixture.root,
        FAKE_HELM_USAGE_FILE: usageFile,
        FAKE_WORKFLOW_HELPER_LOG: helperLog,
        HELM_BASE_URL: 'https://helm.example/v1',
        HELM_API_KEY: 'test-helm-key',
        SUPABASE_URL: 'https://supabase.example',
        SUPABASE_SERVICE_KEY: 'test-supabase-key',
        LEGACY_TOKENS: '1308077250',
        LEGACY_COST_USD: '2568.41704016099988706',
        AUDIT_READ_MAX_ATTEMPTS: '3',
        AUDIT_READ_RETRY_BASE_SECONDS: '2',
        GITHUB_STEP_SUMMARY: summary,
      }),
    });
    return {
      ...result,
      ...collectNetworkResult(fixture),
      helperCalls: readLines(helperLog),
      summary: existsSync(summary) ? readFileSync(summary, 'utf8') : '',
    };
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
}

test('helper retries HTTP 000 empty allowlisted failures and returns only an exact HTTP 200 body', () => {
  const result = runHelper([
    {
      curlExit: 28,
      httpStatus: '000',
      stderr: 'curl: (28) SSL connection timeout\n',
    },
    {
      curlExit: 35,
      httpStatus: '000',
      stderr: 'curl: (35) Connection reset by peer\n',
    },
    successfulResponse,
  ]);

  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, validUsage);
  assert.equal(result.requests, 3);
  assert.deepEqual(result.requestMethods, ['GET', 'GET', 'GET']);
  assert.deepEqual(result.sleeps, ['2', '4']);
  assert.match(result.stderr, /attempt 1\/3 failed with curl exit 28; retrying in 2s/);
  assert.match(result.stderr, /attempt 2\/3 failed with curl exit 35; retrying in 4s/);
  assert.equal(result.unexpectedRequest, false);

  const capturePaths = [];
  for (const invocation of result.invocations) {
    assert.equal(invocation[0], '--disable', `curl --disable must be first: ${invocation.join(' ')}`);
    assert.equal(optionValue(invocation, '--proto'), '=https');
    assert.equal(optionValue(invocation, '--proto-redir'), '=https');
    assert.equal(optionValue(invocation, '--request'), 'GET');
    assert.equal(optionValue(invocation, '--header'), '@-');
    const bodyPath = optionValue(invocation, '--output');
    const headerPath = optionValue(invocation, '--dump-header');
    assert.notEqual(bodyPath, headerPath, 'body and headers must use separate capture files');
    capturePaths.push(bodyPath, headerPath);
    assert.equal(optionValue(invocation, '--write-out'), '%{http_code}');
    assert.equal(invocation.includes('test-helm-key'), false, 'secret must not appear in argv');
  }
  assert.equal(
    new Set(capturePaths).size,
    capturePaths.length,
    'every attempt must use new body and header capture paths',
  );
  for (const capturePath of capturePaths) {
    assert.equal(existsSync(capturePath), false, `temp capture was not cleaned: ${capturePath}`);
  }
});

test('helper disables ambient curl config before every invocation and never exceeds three requests', () => {
  const failures = Array.from({ length: 12 }, () => ({
    curlExit: 28,
    httpStatus: '000',
    stderr: 'curl: (28) timeout\n',
  }));
  const result = runHelper(failures, { maliciousCurlConfig: true });

  assert.equal(result.status, 28);
  assert.equal(result.requests, 3, 'ambient curl retry must not multiply helper attempts');
  assert.equal(result.invocations.length, 3);
  assert.deepEqual(result.sleeps, ['2', '4']);
  assert.deepEqual(result.insecureInvocations, [], 'ambient insecure must not disable TLS checks');
  for (const invocation of result.invocations) {
    assert.equal(invocation[0], '--disable', `curl --disable must be first: ${invocation.join(' ')}`);
  }
});

test('helper ignores malicious ambient insecure for a certificate failure', () => {
  const result = runHelper([
    {
      curlExit: 60,
      httpStatus: '000',
      stderr: 'curl: (60) SSL certificate problem\n',
      insecureResponse: successfulResponse,
    },
    successfulResponse,
  ], { maliciousCurlConfig: true });

  assert.equal(result.status, 60);
  assert.equal(result.requests, 1, 'certificate failure must not become an insecure success');
  assert.equal(result.invocations.length, 1);
  assert.deepEqual(result.insecureInvocations, []);
  assert.equal(result.stdout, '');
});

for (const curlExit of [28, 35, 52, 55, 56]) {
  test(`helper permits retryable curl exit ${curlExit} only for an empty HTTP 000 response`, () => {
    const result = runHelper([
      { curlExit, httpStatus: '000' },
      successfulResponse,
    ]);

    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.requests, 2);
    assert.deepEqual(result.sleeps, ['2']);
  });
}

test('helper does not retry an empty HTTP 000 response for a non-allowlisted curl exit', () => {
  const result = runHelper([
    {
      curlExit: 60,
      httpStatus: '000',
      stderr: 'curl: (60) SSL certificate problem\n',
    },
    successfulResponse,
  ]);

  assert.equal(result.status, 60);
  assert.equal(result.requests, 1);
  assert.deepEqual(result.sleeps, []);
  assert.match(result.stderr, /non-retryable curl exit 60/);
});

const terminalTransportResponses = [
  {
    name: 'HTTP 401 plus a transport error',
    response: {
      curlExit: 28,
      httpStatus: '401',
      headers: 'HTTP/2 401\r\n\r\n',
      stderr: 'curl: (28) timeout after response\n',
    },
  },
  {
    name: 'HTTP 000 plus a partial body',
    response: {
      curlExit: 28,
      httpStatus: '000',
      body: '{"object":"usage_',
      stderr: 'curl: (28) partial body\n',
    },
  },
  {
    name: 'HTTP 000 plus partial headers',
    response: {
      curlExit: 35,
      httpStatus: '000',
      headers: 'HTTP/1.1 200',
      stderr: 'curl: (35) partial headers\n',
    },
  },
  {
    name: 'HTTP 503 plus partial body and headers',
    response: {
      curlExit: 56,
      httpStatus: '503',
      body: '{"error":"upstream',
      headers: 'HTTP/2 503\r\ncontent-type: application/json\r\n',
      stderr: 'curl: (56) receive failure\n',
    },
  },
];

for (const { name, response } of terminalTransportResponses) {
  test(`helper does not retry ${name}`, () => {
    const result = runHelper([response, successfulResponse]);

    assert.equal(result.status, response.curlExit);
    assert.equal(result.requests, 1);
    assert.deepEqual(result.sleeps, []);
  });
}

for (const response of [
  {
    name: 'HTTP 302',
    httpStatus: '302',
    headers: 'HTTP/2 302\r\nlocation: https://other.example/usage\r\n\r\n',
  },
  {
    name: 'HTTP 204',
    httpStatus: '204',
    headers: 'HTTP/2 204\r\n\r\n',
  },
]) {
  test(`helper maps curl-zero ${response.name} to exit 22 without retrying`, () => {
    const result = runHelper([
      {
        curlExit: 0,
        httpStatus: response.httpStatus,
        body: validUsage,
        headers: response.headers,
      },
      successfulResponse,
    ]);

    assert.equal(result.status, 22);
    assert.equal(result.requests, 1);
    assert.deepEqual(result.sleeps, []);
    assert.equal(result.stdout, '');
  });
}

test('helper rejects HTTP 503 with curl exit 18 without retrying', () => {
  const result = runHelper([
    {
      curlExit: 18,
      httpStatus: '503',
      body: '{"error":"partial response"}',
      headers: 'HTTP/2 503\r\n\r\n',
      stderr: 'curl: (18) end of response with bytes missing\n',
    },
    successfulResponse,
  ]);

  assert.equal(result.status, 18);
  assert.equal(result.requests, 1);
  assert.deepEqual(result.sleeps, []);
});

test('helper requires curl exit zero even when the captured HTTP status is 200', () => {
  const result = runHelper([
    {
      curlExit: 28,
      httpStatus: '200',
      body: validUsage,
      headers: 'HTTP/2 200\r\ncontent-type: application/json\r\n\r\n',
      stderr: 'curl: (28) timeout after response\n',
    },
    successfulResponse,
  ]);

  assert.equal(result.status, 28);
  assert.equal(result.requests, 1);
  assert.equal(result.stdout, '');
  assert.deepEqual(result.sleeps, []);
});

test('read helper rejects method or body arguments before curl can run', () => {
  for (const args of [
    ['--request', 'POST'],
    ['--data', '{}'],
  ]) {
    const result = runHelperWithArguments(args);
    assert.equal(result.status, 64);
    assert.match(result.stderr, /usage:/);
    assert.equal(result.requests, 0, 'curl must not run for mutation-capable arguments');
  }
});

test('configuration cannot raise the read budget above three total attempts', () => {
  const result = runHelperWithArguments(
    ['https://helm.example/v1/usage/stats'],
    { AUDIT_READ_MAX_ATTEMPTS: '4' },
  );

  assert.equal(result.status, 64);
  assert.match(result.stderr, /integer from 1 to 3/);
  assert.equal(result.requests, 0, 'invalid budget must fail before curl');
});

const invalidUsageFixtures = [
  {
    name: 'non-object response root',
    json: '[]',
  },
  {
    name: 'unexpected object discriminator',
    json: '{"object":"other","totals":{"total_tokens":7,"cost_usd":1.25}}',
  },
  {
    name: 'missing totals',
    json: '{"object":"usage_stats"}',
  },
  {
    name: 'non-object totals',
    json: '{"object":"usage_stats","totals":[]}',
  },
];

for (const field of ['total_tokens', 'cost_usd']) {
  const otherField = field === 'total_tokens'
    ? '"cost_usd":1.25'
    : '"total_tokens":7';
  const invalidValues = [
    ['missing', null],
    ['null', 'null'],
    ['string', '"7"'],
    ['boolean', 'true'],
    ['negative', '-1'],
    ...(field === 'total_tokens' ? [['non-integer number', '7.5']] : []),
    ['NaN', 'NaN'],
    ['Infinity', 'Infinity'],
    [
      'overflow',
      field === 'total_tokens' ? '9223372036854775808' : '1e309',
    ],
  ];

  for (const [kind, value] of invalidValues) {
    const members = value === null
      ? otherField
      : `"${field}":${value},${otherField}`;
    invalidUsageFixtures.push({
      name: `${kind} ${field}`,
      json: `{"object":"usage_stats","totals":{${members}}}`,
    });
  }
}

for (const fixture of invalidUsageFixtures) {
  test(`workflow rejects ${fixture.name} before the snapshot POST`, () => {
    const result = runWorkflow(fixture.json);

    assert.notEqual(result.status, 0, 'invalid Helm totals must fail the workflow');
    assert.deepEqual(result.helperCalls, ['https://helm.example/v1/usage/stats']);
    assert.equal(result.requests, 0, 'invalid Helm totals must fail before POST');
    assert.equal(result.invocations.length, 0);
  });
}

for (const fixture of [
  {
    name: 'explicit zero totals',
    json: '{"object":"usage_stats","totals":{"total_tokens":0,"cost_usd":0}}',
    tokens: 0,
    cost: 0,
  },
  {
    name: 'ordinary nonnegative totals',
    json: validUsage,
    tokens: 7,
    cost: 1.25,
  },
]) {
  test(`workflow accepts ${fixture.name} under the existing nonnegative contract`, () => {
    const result = runWorkflow(fixture.json);

    assert.equal(result.status, 0, result.stderr);
    assert.equal(result.requests, 1);
    assert.deepEqual(result.requestMethods, ['POST']);
    assert.equal(result.invocations.length, 1);
    const payload = JSON.parse(optionValue(result.invocations[0], '--data'));
    assert.equal(payload.p_helm_tokens, fixture.tokens);
    assert.equal(payload.p_helm_cost_usd, fixture.cost);
    assert.match(result.summary, /## Audit Compute Snapshot/);
  });
}

test('workflow POST starts with curl --disable, forces retry zero, and cannot be replayed by .curlrc', () => {
  const postFailures = Array.from({ length: 4 }, () => ({
    curlExit: 28,
    httpStatus: '000',
    stderr: 'curl: (28) POST timeout\n',
  }));
  const result = runWorkflow(validUsage, postFailures);

  assert.notEqual(result.status, 0, 'failed POST must fail the workflow');
  assert.equal(result.requests, 1, 'a failed POST must issue exactly one network request');
  assert.deepEqual(result.requestMethods, ['POST']);
  assert.equal(result.invocations.length, 1);
  const post = result.invocations[0];
  assert.equal(post[0], '--disable', `curl --disable must be first: ${post.join(' ')}`);
  assert.equal(optionValue(post, '--proto'), '=https');
  assert.equal(optionValue(post, '--proto-redir'), '=https');
  assert.equal(optionValue(post, '--retry'), '0');
  assert.deepEqual(result.insecureInvocations, [], 'ambient insecure must not affect POST TLS');
});

function requiredMatch(source, pattern, label) {
  const match = source.match(pattern);
  assert.ok(match, `could not derive ${label} from production source`);
  return match;
}

test('job timeout covers GET, POST, and ancillary refresh worst cases plus explicit margin', () => {
  const timeoutMinutes = Number(requiredMatch(
    computeWorkflow,
    /^\s{4}timeout-minutes:\s*(\d+)\s*$/m,
    'job timeout',
  )[1]);
  const getAttempts = Number(requiredMatch(
    computeWorkflow,
    /^\s{6}AUDIT_READ_MAX_ATTEMPTS:\s*['"](\d+)['"]\s*$/m,
    'GET attempts',
  )[1]);
  const getBackoffBase = Number(requiredMatch(
    computeWorkflow,
    /^\s{6}AUDIT_READ_RETRY_BASE_SECONDS:\s*['"](\d+)['"]\s*$/m,
    'GET backoff base',
  )[1]);
  const getMaxTime = Number(requiredMatch(
    readFileSync(helper, 'utf8'),
    /--max-time\s+(\d+)/,
    'GET max time',
  )[1]);
  const postMaxTime = Number(requiredMatch(
    syncComputeRunBody,
    /--max-time\s+(\d+)[\s\S]*?--request POST/,
    'POST max time',
  )[1]);

  const refreshLoop = requiredMatch(
    refreshHelperSource,
    /for attempt in ((?:\d+\s+)+\d+); do([\s\S]*?)\ndone/,
    'ancillary refresh retry loop',
  );
  const refreshAttempts = refreshLoop[1].trim().split(/\s+/).map(Number);
  const refreshMaxTime = Number(requiredMatch(
    refreshLoop[2],
    /--max-time\s+(\d+)/,
    'ancillary refresh max time',
  )[1]);
  const refreshSleepMultiplier = Number(requiredMatch(
    refreshLoop[2],
    /sleep\s+\$\(\(attempt \* (\d+)\)\)/,
    'ancillary refresh sleep multiplier',
  )[1]);

  const getBackoffSeconds = Array.from(
    { length: getAttempts - 1 },
    (_, index) => getBackoffBase * (2 ** index),
  ).reduce((total, delay) => total + delay, 0);
  const getWorstCaseSeconds = (getAttempts * getMaxTime) + getBackoffSeconds;
  const refreshSleepSeconds = refreshAttempts
    .slice(0, -1)
    .reduce((total, attempt) => total + (attempt * refreshSleepMultiplier), 0);
  const refreshWorstCaseSeconds =
    (refreshAttempts.length * refreshMaxTime) + refreshSleepSeconds;
  const totalWorstCaseSeconds =
    getWorstCaseSeconds + postMaxTime + refreshWorstCaseSeconds;
  const explicitMarginSeconds = 159;
  const timeoutSeconds = timeoutMinutes * 60;

  assert.equal(getWorstCaseSeconds, 366);
  assert.equal(postMaxTime, 120);
  assert.equal(refreshWorstCaseSeconds, 375);
  assert.equal(totalWorstCaseSeconds, 861);
  assert.ok(
    timeoutSeconds >= totalWorstCaseSeconds + explicitMarginSeconds,
    `job timeout ${timeoutSeconds}s must cover ${totalWorstCaseSeconds}s plus ${explicitMarginSeconds}s margin`,
  );
});

test('the read helper cannot wrap scan, persist, local mutation, or any other workflow', () => {
  assert.doesNotMatch(monitorWorkflow, /fetch-audit-compute-usage|run-source-monitor-with-retry/);

  const workflowUsers = readdirSync(resolve(repoRoot, '.github/workflows'))
    .filter((name) => name.endsWith('.yml') || name.endsWith('.yaml'))
    .filter((name) =>
      readFileSync(resolve(repoRoot, '.github/workflows', name), 'utf8').includes(
        './scripts/fetch-audit-compute-usage.sh "$helm_usage_url"',
      ))
    .map((name) => basename(name));
  assert.deepEqual(workflowUsers, ['sync-audit-compute.yml']);
});
