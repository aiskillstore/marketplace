import test from 'node:test';
import assert from 'node:assert/strict';
import { createGithubEvidenceReader } from '../reconcile-submission-sync.mjs';

const artifact = 'repos/aiskillstore/marketplace/actions/artifacts/12/zip';
const log = 'repos/aiskillstore/marketplace/actions/jobs/34/logs';
const json = 'repos/aiskillstore/marketplace/actions/runs/56';
const bytes = Buffer.from([0x50, 0x4b, 0, 0xff, 0x1b, 0x5b, 0x33, 0x31, 0x6d]);
function fixture(help) {
  const calls = [];
  const read = createGithubEvidenceReader((program, args, options) => {
    calls.push({ program, args, options });
    assert.equal(program, 'gh');
    assert.deepEqual(options.stdio, ['ignore', 'pipe', 'pipe']);
    assert.equal(options.encoding, undefined, 'never re-encode binary evidence');
    assert.ok(options.timeout > 0 && options.timeout <= 30000);
    assert.ok(options.maxBuffer > 0 && options.maxBuffer <= 2 * 1024 * 1024);
    if (args.includes('--help')) return Buffer.from(help);
    assert.equal(args.includes('--allow-escape-sequences'), help.includes('--allow-escape-sequences') && args[1] !== json);
    return args[1] === json ? Buffer.from('{"ok":true}') : bytes;
  });
  return { read, calls };
}
test('new gh captures exact ZIP/log bytes with its documented option, but leaves JSON guarded', () => {
  const f = fixture('      --allow-escape-sequences   Allow printing terminal escape sequences\n');
  assert.deepEqual(f.read(json), Buffer.from('{"ok":true}'));
  assert.equal(f.calls.length, 1, 'JSON needs no capability probe');
  assert.deepEqual(f.read(artifact), bytes);
  assert.deepEqual(f.read(log), bytes);
  assert.equal(f.calls.filter(c => c.args.includes('--help')).length, 1, 'cache only the local CLI capability');
  assert.equal(f.calls.filter(c => c.args[1] === artifact).length, 1, 'never retry a partial response');
});
test('old gh remains compatible without an unsupported output flag', () => {
  const f = fixture('USAGE\n gh api <endpoint>\nFLAGS\n --silent\n');
  assert.deepEqual(f.read(artifact), bytes);
  assert.deepEqual(f.read(log), bytes);
  assert.ok(f.calls.every(c => !c.args.includes('--allow-escape-sequences')));
});
test('help failure and response failure, timeout or buffer overflow stay failures without fallback', () => {
  const failures = ['nonzero exit', 'ETIMEDOUT', 'ENOBUFS'];
  for (const failure of failures) {
    for (const onHelp of [true, false]) {
      let reads = 0;
      const error = Object.assign(new Error(failure), { stdout: Buffer.from('partial'), stderr: Buffer.from('untrusted') });
      const read = createGithubEvidenceReader((_program, args) => {
        if (args.includes('--help') && !onHelp) return Buffer.from('--allow-escape-sequences\n');
        reads++;
        throw error;
      });
      assert.throws(() => read(artifact), e => e === error);
      assert.equal(reads, 1);
    }
  }
});
test('similarly named option is not capability evidence', () => {
  let args;
  const read = createGithubEvidenceReader((_p, a) => {
    if (a.includes('--help')) return Buffer.from('--allow-escape-sequences-extra\n');
    args = a;
    return bytes;
  });
  assert.deepEqual(read(artifact), bytes);
  assert.ok(!args.includes('--allow-escape-sequences'));
});
