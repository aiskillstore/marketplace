import assert from 'node:assert/strict';
import { chmod, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';

const wrapper = new URL('../run-source-monitor-with-retry.sh', import.meta.url).pathname;
const workflow = new URL('../../.github/workflows/monitor-skill-sources.yml', import.meta.url);

async function fixture(mode) {
  const dir = await mkdtemp(join(tmpdir(), 'source-monitor-retry-'));
  const counter = join(dir, 'count');
  const output = join(dir, 'output.log');
  const fake = join(dir, 'fake-monitor.sh');
  await writeFile(fake, `#!/usr/bin/env bash
set -u
count=0
[ ! -f "$COUNTER_FILE" ] || count=$(cat "$COUNTER_FILE")
count=$((count + 1))
printf '%s' "$count" > "$COUNTER_FILE"
case "$FAKE_MODE" in
  cert-once)
    if [ "$count" -eq 1 ]; then
      echo 'fatal: unknown certificate verification error'
      exit 1
    fi
    echo 'monitor completed'
    ;;
  cert-always)
    echo 'fatal: unknown certificate verification error'
    exit 1
    ;;
  generic)
    echo 'fatal: repository contract failed'
    exit 42
    ;;
esac
`, 'utf8');
  await chmod(fake, 0o755);
  return { dir, counter, output, fake, mode };
}

async function run(mode) {
  const files = await fixture(mode);
  const result = spawnSync('/bin/bash', [wrapper, '--', files.fake], {
    encoding: 'utf8',
    env: {
      ...process.env,
      COUNTER_FILE: files.counter,
      FAKE_MODE: mode,
      MONITOR_OUTPUT_FILE: files.output,
      MONITOR_MAX_ATTEMPTS: '2',
      MONITOR_RETRY_DELAY_SECONDS: '0',
    },
  });
  const count = Number(await readFile(files.counter, 'utf8').catch(() => '0'));
  const output = await readFile(files.output, 'utf8').catch(() => '');
  await rm(files.dir, { recursive: true, force: true });
  return { result, count, output };
}

test('retries the exact transient certificate error once and then succeeds', async () => {
  const { result, count, output } = await run('cert-once');
  assert.equal(result.status, 0, result.stderr);
  assert.equal(count, 2);
  assert.match(output, /unknown certificate verification error/);
  assert.match(output, /monitor completed/);
});

test('does not retry unrelated monitor failures', async () => {
  const { result, count } = await run('generic');
  assert.equal(result.status, 42);
  assert.equal(count, 1);
});

test('stops after the bounded certificate retry', async () => {
  const { result, count } = await run('cert-always');
  assert.notEqual(result.status, 0);
  assert.equal(count, 2);
});

test('workflow keeps the 24 hour job budget and uses the bounded retry wrapper', async () => {
  const content = await readFile(workflow, 'utf8');
  const scanJob = content.match(/  scan:[\s\S]*?(?=\n  [a-zA-Z0-9_-]+:|$)/)?.[0] ?? '';
  assert.match(scanJob, /timeout-minutes: 1440/);
  assert.match(scanJob, /run-source-monitor-with-retry\.sh/);
  assert.match(scanJob, /MONITOR_MAX_ATTEMPTS: ['"]2['"]/);
  assert.match(scanJob, /MONITOR_RETRY_DELAY_SECONDS: ['"]15['"]/);
});
