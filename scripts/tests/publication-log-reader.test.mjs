import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const moduleUrl = new URL('../publication-prepush-recovery.mjs', import.meta.url).href;

test('reads colored GitHub job logs as plain reconciliation evidence', () => {
  const dir = mkdtempSync(join(tmpdir(), 'publication-log-'));
  try {
    writeFileSync(join(dir, 'gh'), `#!${process.execPath}\n
      const fs = require('node:fs');
      fs.writeFileSync(process.env.CAPTURE_ARGS, JSON.stringify(process.argv.slice(2)));
      if (!process.argv.includes('--allow-escape-sequences')) process.exit(2);
      process.stdout.write('2026-11-06T17:28:35.189Z \\u001b[31mMain advanced; re-preflight required\\u001b[0m\\n');
    `, { mode: 0o700 });
    const output = execFileSync(process.execPath, ['--input-type=module', '-e',
      `import { readPublicationJobLog } from ${JSON.stringify(moduleUrl)}; process.stdout.write(readPublicationJobLog(128043381793));`],
      { encoding: 'utf8', env: { ...process.env, PATH: `${dir}:${process.env.PATH}`, CAPTURE_ARGS: join(dir, 'args.json') } });
    assert.equal(output, '2026-11-06T17:28:35.189Z Main advanced; re-preflight required\n');
    assert.deepEqual(JSON.parse(readFileSync(join(dir, 'args.json'), 'utf8')),
      ['api', 'repos/aiskillstore/marketplace/actions/jobs/128043381793/logs', '--allow-escape-sequences']);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('never treats a failed job-log fetch as empty successful evidence', () => {
  const dir = mkdtempSync(join(tmpdir(), 'publication-log-failed-'));
  try {
    writeFileSync(join(dir, 'gh'), `#!${process.execPath}\nprocess.exit(1);\n`, { mode: 0o700 });
    assert.throws(() => execFileSync(process.execPath, ['--input-type=module', '-e',
      `import { readPublicationJobLog } from ${JSON.stringify(moduleUrl)}; readPublicationJobLog(128043381793);`],
      { stdio: 'pipe', env: { ...process.env, PATH: `${dir}:${process.env.PATH}` } }));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('keeps the installed older gh reader working when the new flag is unsupported', () => {
  const dir = mkdtempSync(join(tmpdir(), 'publication-log-old-gh-'));
  try {
    writeFileSync(join(dir, 'gh'), `#!${process.execPath}\n
      if (process.argv.includes('--allow-escape-sequences')) {
        process.stderr.write('unknown flag: --allow-escape-sequences\\n'); process.exit(1);
      }
      process.stdout.write('\\u001b[32mverified log\\u001b[0m\\n');
    `, { mode: 0o700 });
    const output = execFileSync(process.execPath, ['--input-type=module', '-e',
      `import { readPublicationJobLog } from ${JSON.stringify(moduleUrl)}; process.stdout.write(readPublicationJobLog(128043381793));`],
      { encoding: 'utf8', stdio: 'pipe', env: { ...process.env, PATH: `${dir}:${process.env.PATH}` } });
    assert.equal(output, 'verified log\n');
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
