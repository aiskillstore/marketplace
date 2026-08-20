import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const scripts = new URL('.', import.meta.url);

function run(script, statePath, ...args) {
  return spawnSync(process.execPath, [fileURLToPath(new URL(script, scripts)), '--state', statePath, ...args], { encoding: 'utf8' });
}

test('retries pending messages until successful delivery is recorded', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'me-featured-events-'));
  const statePath = join(directory, 'state.json');
  const oldCursor = 'old-cursor';
  const nextCursor = 'next-cursor';
  await writeFile(statePath, JSON.stringify({
    version: 2,
    cursor: oldCursor,
    recent_ids: ['activity:1'],
    pending_delivery: {
      message: '新增会议\n\n测试活动',
      next_cursor: nextCursor,
      recent_ids: ['activity:1', 'activity:2'],
      attempt_count: 1,
    },
  }));

  try {
    const firstRetry = run('poll-new-events.mjs', statePath);
    assert.equal(firstRetry.status, 0);
    assert.equal(firstRetry.stdout, '新增会议\n\n测试活动\n');

    const failed = run('record-delivery.mjs', statePath, '--status', 'failed', '--error', 'Telegram unavailable');
    assert.equal(failed.status, 0);
    let state = JSON.parse(await readFile(statePath, 'utf8'));
    assert.equal(state.cursor, oldCursor);
    assert.equal(state.pending_delivery.failure_count, 1);

    const secondRetry = run('poll-new-events.mjs', statePath);
    assert.equal(secondRetry.stdout, firstRetry.stdout);

    const succeeded = run('record-delivery.mjs', statePath, '--status', 'success');
    assert.equal(succeeded.status, 0);
    state = JSON.parse(await readFile(statePath, 'utf8'));
    assert.equal(state.cursor, nextCursor);
    assert.deepEqual(state.recent_ids, ['activity:1', 'activity:2']);
    assert.equal(state.pending_delivery, undefined);
    assert.equal(state.last_delivery_status, 'success');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
