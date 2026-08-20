import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const initScript = fileURLToPath(new URL('init-subscription.mjs', import.meta.url));

test('persists and reuses the original baseline when initialization resumes', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'me-featured-events-init-'));
  const statePath = join(directory, 'state.json');
  const mockPath = join(directory, 'mock-fetch.mjs');
  await writeFile(mockPath, `
globalThis.fetch = async (url) => {
  const path = new URL(url).pathname;
  if (path.endsWith('/options')) return response({ types: [{ value: 'ai' }], regions: [{ value: 'hong-kong' }] });
  if (path.endsWith('/changes')) {
    if (process.env.FAIL_ON_CHANGES === '1') throw new Error('baseline must not be requested again');
    return response({ items: [], next_cursor: 'original-cursor', has_more: false });
  }
  if (path.endsWith('/upcoming')) {
    if (process.env.FAIL_UPCOMING === '1') throw new Error('simulated upcoming failure');
    return response({ items: [] });
  }
  throw new Error('unexpected request: ' + path);
};
function response(data) {
  return { ok: true, json: async () => ({ code: 200, data }) };
}
`);

  const run = (extraEnv) => spawnSync(process.execPath, [
    '--import', mockPath,
    initScript,
    '--state', statePath,
    '--types', 'ai',
    '--regions', 'hong-kong',
  ], { encoding: 'utf8', env: { ...process.env, ...extraEnv } });

  try {
    const failed = run({ FAIL_UPCOMING: '1' });
    assert.equal(failed.status, 1);
    assert.match(failed.stderr, /simulated upcoming failure/);
    let state = JSON.parse(await readFile(statePath, 'utf8'));
    assert.equal(state.cursor, 'original-cursor');
    assert.equal(state.initialization_status, 'pending');

    const resumed = run({ FAIL_ON_CHANGES: '1' });
    assert.equal(resumed.status, 0, resumed.stderr);
    state = JSON.parse(await readFile(statePath, 'utf8'));
    assert.equal(state.cursor, 'original-cursor');
    assert.equal(state.initialization_status, 'complete');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
