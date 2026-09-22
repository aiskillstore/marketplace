import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const map = path.join(root, 'examples/architecture.json');

test('CLI main guards still run when the installation is reached through a symlink', t => {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-main-module-test-'));
  const link = path.join(fixture, 'birdview');
  t.after(() => {
    try { fs.unlinkSync(link); } catch { try { fs.rmdirSync(link); } catch { /* already gone */ } }
    fs.rmSync(fixture, { recursive: true, force: true });
  });
  try {
    fs.symlinkSync(path.resolve(root), link, 'junction');
  } catch (error) {
    t.skip(`Linked directories unavailable: ${error instanceof Error ? error.message : String(error)}`);
    return;
  }
  const run = (nodeArgs: string[], ...args: string[]) =>
    spawnSync(process.execPath, [...nodeArgs, ...args], { cwd: fixture, encoding: 'utf8' });

  const validated = run([], path.join(link, 'scripts/validate.mjs'), map);
  assert.equal(validated.status, 0, validated.stdout + validated.stderr);
  assert.match(validated.stdout, /"ok": true/);

  const output = path.join(fixture, 'map.html');
  const rendered = run([], path.join(link, 'scripts/render.mjs'), map, output);
  assert.equal(rendered.status, 0, rendered.stdout + rendered.stderr);
  assert.equal(fs.existsSync(output), true);

  // import.meta.url keeps the linked path under this flag, so resolving only process.argv[1] would
  // move the silent failure here instead of removing it.
  const preserved = run(['--preserve-symlinks-main'], path.join(link, 'scripts/validate.mjs'), map);
  assert.equal(preserved.status, 0, preserved.stdout + preserved.stderr);
  assert.match(preserved.stdout, /"ok": true/);
  for (const flags of [[], ['--preserve-symlinks-main']]) {
    const doctor = run(flags, path.join(link, 'scripts/birdview.mjs'), 'doctor');
    assert.equal(doctor.status, 0, doctor.stdout + doctor.stderr);
    assert.match(doctor.stdout, /through installed CLI/);
  }
});

test('main guards stay inert and silent without a resolvable entry path', () => {
  const cli = pathToFileURL(path.join(root, 'scripts/validate.mjs')).href;
  const load = (...args: string[]) =>
    spawnSync(process.execPath, ['-e', `import(${JSON.stringify(cli)})`, ...args], { cwd: root, encoding: 'utf8' });

  const imported = load();
  assert.equal(imported.status, 0, imported.stdout + imported.stderr);
  assert.equal(imported.stdout, '');

  // A synthetic or already deleted process.argv[1] must leave the guard false rather than throw.
  const missing = load(path.join(root, 'no-such-entry.mjs'));
  assert.equal(missing.status, 0, missing.stdout + missing.stderr);
  assert.equal(missing.stdout, '');
});
