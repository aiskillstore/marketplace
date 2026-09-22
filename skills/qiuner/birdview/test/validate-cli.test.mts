import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const cli = path.join(root, 'scripts/validate.mjs');
const map = path.join(root, 'examples/architecture.json');

test('validator CLI validates outside the repository and reports malformed input as JSON', t => {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-validator-test-'));
  t.after(() => fs.rmSync(fixture, { recursive: true, force: true }));
  const run = (...args: string[]) => spawnSync(process.execPath, [cli, ...args], { cwd: fixture, encoding: 'utf8' });
  const valid = run(map, path.join(root, 'examples/activity.jsonl'));
  assert.equal(valid.status, 0, valid.stdout + valid.stderr);
  assert.match(valid.stdout, /"ok": true/);
  assert.equal(valid.stderr, '');

  const activity = path.join(fixture, 'invalid.jsonl');
  fs.writeFileSync(activity, '\n{broken}\n');
  const malformed = run(map, activity);
  assert.equal(malformed.status, 1);
  assert.deepEqual(JSON.parse(malformed.stdout), {
    ok: false, errors: [{ code: 'input/read', message: 'Invalid JSON in event record 1.' }],
  });
  fs.writeFileSync(activity, 'null\n');
  const schema = run(map, activity);
  assert.equal(schema.status, 1);
  assert.match(schema.stdout, /"code": "schema\/activity"/);
  assert.match(schema.stdout, /"location": "\/events\/0"/);
  const invalidMap = path.join(fixture, 'invalid-map.json');
  fs.writeFileSync(invalidMap, 'null');
  const rejected = run(invalidMap);
  assert.equal(rejected.status, 1);
  assert.match(rejected.stdout, /"code": "schema\/architecture"/);
  const usage = run();
  assert.equal(usage.status, 1);
  assert.match(usage.stdout, /"code": "input\/read"/);
  assert.match(usage.stdout, /Usage: node scripts\/validate.mjs/);
});
