import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const cli = path.join(root, 'scripts/render.mjs');

test('render CLI preserves existing output on invalid input and runs outside the repository', t => {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-render-test-'));
  t.after(() => fs.rmSync(fixture, { recursive: true, force: true }));
  const run = (...args: string[]) => spawnSync(process.execPath, [cli, ...args], { cwd: fixture, encoding: 'utf8' });
  const map = path.join(root, 'examples/architecture.json');
  const output = path.join(fixture, 'map.html');
  fs.writeFileSync(output, 'keep previous output');
  const invalid = path.join(fixture, 'invalid.json');
  fs.writeFileSync(invalid, 'null');
  assert.equal(run(invalid, output).status, 1);
  assert.equal(fs.readFileSync(output, 'utf8'), 'keep previous output');
  const activity = path.join(fixture, 'invalid.jsonl');
  fs.writeFileSync(activity, '{broken}\n');
  const failed = run(map, output, activity);
  assert.equal(failed.status, 1);
  assert.match(failed.stderr, /Invalid JSON in activity record 1/);
  assert.equal(fs.readFileSync(output, 'utf8'), 'keep previous output');

  const sameFile = path.join(fixture, 'source.html');
  fs.copyFileSync(map, sameFile);
  const saved = fs.readFileSync(sameFile, 'utf8');
  assert.equal(run(sameFile, sameFile).status, 1);
  assert.equal(fs.readFileSync(sameFile, 'utf8'), saved);
  assert.equal(run(map, output, output).status, 1);
  assert.equal(fs.readFileSync(output, 'utf8'), 'keep previous output');
  const badExtension = path.join(fixture, 'map.json');
  assert.equal(run(map, badExtension).status, 1);
  assert.equal(fs.existsSync(badExtension), false);

  const nested = path.join(fixture, 'nested/map.html');
  const valid = run(map, nested, '--simulation');
  assert.equal(valid.status, 0, valid.stdout + valid.stderr);
  const html = fs.readFileSync(nested, 'utf8');
  assert.match(html, /"simulation":true/);
  assert.match(html, /data:image\/png;base64,/);
  assert.doesNotMatch(html, /\/\* BIRDVIEW_[A-Z_]+ \*\//);
  assert.equal(run().status, 1);
});
