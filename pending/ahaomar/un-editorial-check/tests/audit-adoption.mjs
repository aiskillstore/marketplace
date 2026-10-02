// Phase 5A adoption pack (Agent D) — plain node:assert, run with:
// node tests/audit-adoption.mjs
//
// Locks every user-facing claim the adoption features make:
//   * --baseline: snapshot on first use, exit 1 only for findings NOT in the
//     snapshot, fail-closed exit 2 for an unreadable snapshot, deterministic
//     keys that survive line shifts,
//   * --init: writes exactly what the existing --config loader accepts, is
//     inert until edited, refuses to overwrite without --init-overwrite, and
//     prints the snippet for the detected host,
//   * --self-test: exact corpus findings, exit 0 verified / exit 1 with a
//     readable diff / exit 2 when the corpus cannot be read, isolated from
//     any working-directory config,
//   * action.yml structure and the action entry point's exit behaviour,
//   * the four agent command templates and the pre-commit hook,
//   * the per-platform truncation preview with its documented assumptions.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { run } from '../bin/check.mjs';
import {
  BASELINE_VERSION, BaselineError, findingKey, buildSnapshot, serialiseSnapshot,
  parseSnapshot, readSnapshot, compareSnapshot, evaluateBaseline,
} from '../lib/baseline.mjs';
import {
  detectHosts, starterConfig, writeStarterConfig, formatInitReport, InitError,
  PRE_COMMIT_HOOK,
} from '../lib/init.mjs';
import { CORPUS, CORPUS_DIR, SelfTestError, runSelfTest } from '../lib/selftest.mjs';
import { PLATFORMS, previewTruncate, formatPreview } from '../lib/truncate.mjs';
import {
  loadCatalogue, loadBaselineProfile, validateConfig, parseJsonStrict, makeContext,
} from '../lib/config.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'check.mjs');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'un-editorial-adoption-'));

const capture = (args, opts = {}) => {
  const result = spawnSync(process.execPath, [cli, ...args], { encoding: 'utf8', ...opts });
  assert(result.status !== null, `the CLI did not exit: ${result.error}`);
  return { code: result.status, stdout: result.stdout, stderr: result.stderr };
};
const inProcess = (args) => {
  const out = [];
  const err = [];
  const code = run(args, { log: line => out.push(String(line)), error: line => err.push(String(line)) });
  return { code, stdout: out.join('\n'), stderr: err.join('\n') };
};
const mkdir = (name) => {
  const dir = path.join(tmp, name);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
};
const sortMarks = list => [...list].sort((a, b) =>
  a.ruleId.localeCompare(b.ruleId) || a.line - b.line || a.column - b.column);

// --- baseline: keys, snapshots, comparison (pure units) ----------------------

{
  const cwd = path.join(tmp, 'unit');
  const marks = file => ({ file: path.join(cwd, file), ruleId: 'UE-SP001', line: 1, column: 5, severity: 'error', current: 'color' });

  assert.equal(findingKey(marks('page.txt'), cwd), 'page.txt|UE-SP001|color',
    'a key must be working-directory relative, pipe-delimited');
  assert.equal(findingKey({ ...marks('page.txt'), file: `.${path.sep}page.txt` }, cwd),
    'page.txt|UE-SP001|color', 'a leading ./ must not change the key');
  assert.equal(findingKey({ ...marks('page.txt'), current: '  The   color\nof\tthe cover ' }, cwd),
    'page.txt|UE-SP001|The color of the cover',
    'the excerpt must be whitespace-normalised so reflow cannot change the key');
  assert.equal(findingKey({ ...marks('page.txt'), current: 'e\u0301' }, cwd),
    findingKey({ ...marks('page.txt'), current: '\u00e9' }, cwd),
    'composed and decomposed forms of the same characters must share a key');
  assert.notEqual(findingKey(marks('page.txt'), cwd),
    findingKey({ ...marks('page.txt'), current: 'colour' }, cwd),
    'a changed excerpt must produce a new key (fail closed)');
  assert.notEqual(findingKey(marks('page.txt'), cwd),
    findingKey({ ...marks('page.txt'), ruleId: 'UE-RE005' }, cwd), 'the rule is part of the key');
  assert.equal(findingKey({ ...marks('page.txt'), file: 'outside.txt' }, cwd),
    'outside.txt|UE-SP001|color', 'a relative finding path is kept as written');

  const a = marks('a.txt');
  const b = { ...marks('b.txt'), ruleId: 'UE-RE005', current: 'record level!' };
  const forward = buildSnapshot([a, b], '0.9.0');
  const backward = buildSnapshot([b, a], '0.9.0');
  assert.equal(serialiseSnapshot(forward), serialiseSnapshot(backward),
    'the snapshot must be byte-identical regardless of finding order');
  assert.equal(forward.baselineVersion, BASELINE_VERSION);
  assert.equal(forward.toolVersion, '0.9.0');
  assert(!/created|timestamp|date/i.test(serialiseSnapshot(forward)),
    'the snapshot must carry no timestamp: identical findings must produce identical bytes');

  const roundTrip = parseSnapshot(serialiseSnapshot(forward), 'unit');
  assert.deepEqual(roundTrip, forward, 'parse must be the exact inverse of serialise');
  assert.equal(readSnapshot(path.join(tmp, 'no-such-baseline.json')), null,
    'a missing snapshot reads as null (first use)');
  assert.throws(() => parseSnapshot('[]', 'bad.json'), BaselineError,
    'a non-object snapshot must be rejected');
  assert.throws(() => parseSnapshot('{"baselineVersion":99,"findings":[]}', 'bad.json'),
    BaselineError, 'an unknown baselineVersion must be rejected');
  assert.throws(() => parseSnapshot('{"baselineVersion":1,"findings":[{"line":1}]}', 'bad.json'),
    BaselineError, 'an entry without a key must be rejected');
  assert.throws(() => readSnapshot(path.join(tmp)), BaselineError,
    'a directory in place of the snapshot must be rejected');

  const cmp = compareSnapshot(forward, [a, b, { ...marks('c.txt') }], { cwd });
  assert.equal(cmp.known, 2, 'both snapshotted findings are known');
  assert.equal(cmp.newFindings.length, 1, 'the third finding is new');
  assert.equal(cmp.stale, 0);
  const shifted = { ...a, line: 9, column: 3 };
  const cmpShifted = compareSnapshot(forward, [shifted, b], { cwd });
  assert.equal(cmpShifted.known, 2, 'line and column shifts must not make a finding new');
  assert.equal(cmpShifted.stale, 0);
  const cmpGone = compareSnapshot(forward, [a], { cwd });
  assert.equal(cmpGone.stale, 1, 'a snapshot entry absent from this run is stale, never failing');

  // evaluateBaseline wires read-or-write, comparison and exit code together.
  const evalDir = path.join(tmp, 'unit-eval');
  fs.mkdirSync(evalDir, { recursive: true });
  const evalFile = path.join(evalDir, 'page.txt');
  const finding = { file: evalFile, ruleId: 'UE-SP001', line: 1, column: 5, severity: 'error', current: 'color' };
  const evalSnap = path.join(evalDir, 'b.json');
  const written = evaluateBaseline({
    file: evalSnap, findings: [finding], errors: [finding], toolVersion: '0.9.0', cwd: evalDir,
  });
  assert.equal(written.mode, 'written');
  assert.equal(written.exitCode, 0, 'first use records the snapshot and exits 0');
  assert.match(written.status, /Baseline written: .*1 finding recorded/);
  const compared = evaluateBaseline({
    file: evalSnap, findings: [finding], errors: [finding], toolVersion: '1.0.0', cwd: evalDir,
  });
  assert.equal(compared.mode, 'compared');
  assert.equal(compared.exitCode, 0);
  assert.match(compared.status, /1 known, 0 new, 0 stale, 0 new error-severity/);
  assert.match(compared.status, /snapshot from 0\.9\.0/,
    'a snapshot written by another version is named in the status, not rejected');
  const fresh = {
    file: path.join(evalDir, 'other.txt'), ruleId: 'UE-RE005',
    line: 1, column: 1, severity: 'error', current: 'record level!',
  };
  const grownRun = evaluateBaseline({
    file: evalSnap, findings: [finding, fresh], errors: [fresh], toolVersion: '1.0.0', cwd: evalDir,
  });
  assert.equal(grownRun.exitCode, 1, 'a new error-severity finding fails the run');
  assert.match(grownRun.status, /1 new error-severity/);
}

// --- baseline: CLI behaviour -------------------------------------------------

{
  const dir = mkdir('baseline');
  const page = path.join(dir, 'page.txt');
  fs.writeFileSync(page, 'The color of the cover was noted in the file.\n');
  const snap = path.join(dir, '.ue-baseline.json');
  const scan = (...extra) => capture(['page.txt', '--baseline', '.ue-baseline.json', ...extra], { cwd: dir });

  const first = scan();
  assert.equal(first.code, 0,
    'the first run writes the snapshot and exits 0, because every finding it just recorded is in it');
  assert.match(first.stdout, /UE-SP001/, 'the report must still list the findings on the first run');
  assert.match(first.stderr, new RegExp(`Baseline written: \\.ue-baseline\\.json \\(1 finding recorded; commit this file so later runs fail only on new findings\\)`),
    `first-run status: ${first.stderr}`);
  const bytes1 = fs.readFileSync(snap, 'utf8');

  const second = scan();
  assert.equal(second.code, 0, 'an unchanged run exits 0');
  assert.match(second.stderr, /Baseline \.ue-baseline\.json: 1 known, 0 new, 0 stale, 0 new error-severity/);

  fs.writeFileSync(page, 'The draft was long, and then a line was added above it.\nThe color of the cover was noted in the file.\n');
  const shifted = scan();
  assert.equal(shifted.code, 0, 'a line shift must not turn a baselined finding into a new one');
  assert.match(shifted.stderr, /1 known, 0 new, 0 stale, 0 new error-severity/);

  fs.appendFileSync(page, 'Coverage reached a record level!\n');
  const grown = scan();
  assert.equal(grown.code, 1, 'only the NEW error-severity finding fails');
  assert.match(grown.stderr, /1 known, 1 new, 0 stale, 1 new error-severity/);
  assert.match(grown.stdout, /UE-RE005/, 'the new finding must be named in the report');

  const withoutFlag = capture(['page.txt'], { cwd: dir });
  assert.equal(withoutFlag.code, 1, 'without --baseline the exit code contract is unchanged');

  // The snapshot is deterministic: re-running without changes never rewrites it.
  fs.writeFileSync(snap, bytes1);
  const again = scan();
  assert.equal(again.code, 1, 'the appended finding is still new after the snapshot is restored');
  assert.equal(fs.readFileSync(snap, 'utf8'), bytes1, 'a comparison run must not rewrite the snapshot');

  // Fail-closed exits (exit 2) for unreadable snapshots.
  fs.writeFileSync(snap, 'not json at all');
  const corrupt = scan();
  assert.equal(corrupt.code, 2, 'a corrupt snapshot must fail closed with exit 2');
  assert.match(corrupt.stderr, /baseline .* is not valid JSON/);

  fs.writeFileSync(snap, JSON.stringify({ baselineVersion: 99, findings: [] }));
  const future = scan();
  assert.equal(future.code, 2, 'an unknown baselineVersion must fail closed');
  assert.match(future.stderr, /unsupported baselineVersion 99/);

  const asDir = path.join(dir, 'snap-dir');
  fs.mkdirSync(asDir);
  const dirSnap = capture(['page.txt', '--baseline', 'snap-dir'], { cwd: dir });
  assert.equal(dirSnap.code, 2, 'a directory used as the snapshot must fail closed');
  assert.match(dirSnap.stderr, /cannot read baseline/);

  const unwritable = capture(['page.txt', '--baseline', path.join(dir, 'no-such-dir', 'b.json')], { cwd: dir });
  assert.equal(unwritable.code, 2, 'an unwritable snapshot path must refuse with exit 2');
  assert.match(unwritable.stderr, /cannot write baseline/);

  // Machine-readable stdout stays valid JSON: the status goes to stderr.
  fs.writeFileSync(snap, JSON.stringify({ baselineVersion: BASELINE_VERSION, toolVersion: '0.9.0', findings: [] }));
  const asJson = scan('--format', 'json');
  assert.equal(asJson.code, 1, 'JSON mode keeps the same exit semantics');
  const parsed = JSON.parse(asJson.stdout);
  assert.equal(parsed.findings.length, 2, 'stdout must still be the full JSON report');
  assert.match(asJson.stderr, /Baseline \.ue-baseline\.json/);

  // Stale entries: a snapshot finding no longer present is reported, never failing.
  const two = mkdir('baseline-stale');
  fs.writeFileSync(path.join(two, 'a.txt'), 'The color of the cover was noted.\n');
  fs.writeFileSync(path.join(two, 'b.txt'), 'Coverage reached a record level!\n');
  const both = capture(['.', '--baseline', 'snap.json'], { cwd: two });
  assert.equal(both.code, 0, 'first run over two files writes the snapshot and exits 0');
  fs.rmSync(path.join(two, 'b.txt'));
  const stale = capture(['.', '--baseline', 'snap.json'], { cwd: two });
  assert.equal(stale.code, 0, 'stale snapshot entries never fail a run');
  assert.match(stale.stderr, /1 known, 0 new, 1 stale, 0 new error-severity/);

  // Flag grammar.
  const emptyValue = inProcess(['--baseline=']);
  assert.equal(emptyValue.code, 2, '--baseline requires a value');
  assert.match(emptyValue.stderr, /--baseline requires a value/);
  const clash = capture(['--init', '--baseline', 'x.json'], { cwd: tmp });
  assert.equal(clash.code, 2, '--init and --baseline cannot be combined');
  assert.match(clash.stderr, /cannot be combined/);
}

// --- --init ------------------------------------------------------------------

{
  const allowed = new Set([
    'ignoredPaths', 'allowlist', 'severities', 'rules', 'spellingReview',
    'baseOrigin', 'renderTargets',
  ]);
  const dir = mkdir('init-generic');
  const init = capture(['--init'], { cwd: dir });
  assert.equal(init.code, 0, init.stderr);
  const configFile = path.join(dir, '.un-editorial.json');
  assert(fs.existsSync(configFile), '--init must write .un-editorial.json in the working directory');
  assert.match(init.stdout, /Wrote \.un-editorial\.json \(starter configuration; it changes no behaviour until you edit it\)\./);
  assert.match(init.stdout, /npx un-editorial-check --config \.un-editorial\.json <paths>/);
  assert.match(init.stdout, /No CI or git host detected in this directory\./);
  assert.match(init.stdout, /npx un-editorial-check --self-test/,
    '--init must print the one-command verification snippet');

  const written = JSON.parse(fs.readFileSync(configFile, 'utf8'));
  assert.deepEqual(Object.keys(written).filter(key => !allowed.has(key)), [],
    'the starter config may only use fields the --config loader accepts');
  assert.equal(written.baseOrigin, null);
  assert(Array.isArray(written.ignoredPaths) && Array.isArray(written.allowlist.claims));

  // The file the loader actually accepts: an explicit --config run must not be
  // a usage error, and the scan still reports its findings.
  const shared = path.join(tmp, 'shared-page.txt');
  fs.writeFileSync(shared, 'The color of the cover was noted in the file.\n');
  const explicit = capture([shared, '--config', configFile, '--format', 'json'], { cwd: tmp });
  assert.notEqual(explicit.code, 2, `the written config must load through --config: ${explicit.stderr}`);
  assert(JSON.parse(explicit.stdout).findings.length >= 1, 'the shared fixture must carry a finding');

  // The starter is inert: the same scan from a directory without the config is identical.
  const plain = mkdir('init-plain');
  const withConfig = capture([shared, '--format', 'json'], { cwd: dir });
  const withoutConfig = capture([shared, '--format', 'json'], { cwd: plain });
  assert.equal(withConfig.code, withoutConfig.code);
  assert.deepEqual(JSON.parse(withConfig.stdout).findings, JSON.parse(withoutConfig.stdout).findings,
    'the starter config must change nothing until it is edited');

  // Refusal without a flag; replacement with --init-overwrite.
  const again = capture(['--init'], { cwd: dir });
  assert.equal(again.code, 2, 'a second --init must refuse to overwrite');
  assert.match(again.stderr, /config already exists: .*\.un-editorial\.json \(use --init-overwrite to replace it\)/);
  fs.writeFileSync(configFile, '{ this is broken');
  const overwrite = capture(['--init', '--init-overwrite'], { cwd: dir });
  assert.equal(overwrite.code, 0, overwrite.stderr);
  assert.doesNotThrow(() => JSON.parse(fs.readFileSync(configFile, 'utf8')),
    '--init-overwrite must leave a valid config behind');

  // Usage exclusivity.
  const withPath = capture(['--init', 'somewhere.txt'], { cwd: tmp });
  assert.equal(withPath.code, 2);
  assert.match(withPath.stderr, /--init cannot be combined with scan paths/);
  const withFix = capture(['--init', '--fix'], { cwd: tmp });
  assert.equal(withFix.code, 2);
  assert.match(withFix.stderr, /--init cannot be combined with --fix/);
  const withQuiet = capture(['--init', '--quiet'], { cwd: tmp });
  assert.equal(withQuiet.code, 2);
  assert.match(withQuiet.stderr, /--init cannot be combined with --quiet/);
  const overwriteAlone = capture(['--init-overwrite'], { cwd: tmp });
  assert.equal(overwriteAlone.code, 2);
  assert.match(overwriteAlone.stderr, /--init-overwrite requires --init/);

  // Host detection and the exact snippets (deterministic, offline). --init
  // inspects the working directory itself, so each fixture is scanned from its
  // own root: markers live at <root>/<marker>, never one level deeper.
  const ghRoot = mkdir('init-gh');
  fs.mkdirSync(path.join(ghRoot, '.github', 'workflows'), { recursive: true });
  const ghRun = capture(['--init'], { cwd: ghRoot });
  assert.equal(ghRun.code, 0, ghRun.stderr);
  assert.match(ghRun.stdout, /Detected: GitHub Actions \(\.github\/workflows\)/);
  assert.match(ghRun.stdout, /- uses: ahaomar\/un-editorial-check@main/,
    'the GitHub Actions snippet must reference this repository action');
  assert.match(ghRun.stdout, /Paste the GitHub Actions snippet:/);

  const gl = mkdir('init-gl');
  fs.writeFileSync(path.join(gl, '.gitlab-ci.yml'), 'editorial-check:\n  image: node:20\n');
  assert.match(capture(['--init'], { cwd: gl }).stdout, /npx --yes un-editorial-check \./);

  const ccRoot = mkdir('init-cc');
  fs.mkdirSync(path.join(ccRoot, '.circleci'), { recursive: true });
  fs.writeFileSync(path.join(ccRoot, '.circleci', 'config.yml'), 'version: 2.1\n');
  assert.match(capture(['--init'], { cwd: ccRoot }).stdout, /cimg\/node:current/);

  const jk = mkdir('init-jk');
  fs.writeFileSync(path.join(jk, 'Jenkinsfile'), 'pipeline { agent any }\n');
  assert.match(capture(['--init'], { cwd: jk }).stdout, /sh 'npx --yes un-editorial-check \.'/);

  const pc = mkdir('init-pc');
  fs.writeFileSync(path.join(pc, '.pre-commit-config.yaml'), 'repos: []\n');
  assert.match(capture(['--init'], { cwd: pc }).stdout, /entry: npx --no-install un-editorial-check/);

  const gt = mkdir('init-git/.git');
  const gtRun = capture(['--init'], { cwd: path.dirname(gt) });
  assert.match(gtRun.stdout, /git diff --cached --name-only --diff-filter=ACM/,
    'the printed git hook must contain the staged-files line the pre-commit template pins');
  assert.match(gtRun.stdout, /Detected: git \(\.git\)/);

  // Priority: with both GitHub Actions and git, the Actions snippet wins and
  // both are still listed. The markers live at the fixture root, because
  // --init inspects the working directory it is run in and walks no parents.
  const prio = mkdir('init-prio');
  fs.mkdirSync(path.join(prio, '.github', 'workflows'), { recursive: true });
  fs.writeFileSync(path.join(prio, '.github', 'workflows', 'ci.yml'), 'on: push\n');
  fs.mkdirSync(path.join(prio, '.git'), { recursive: true });
  fs.writeFileSync(path.join(prio, '.git', 'HEAD'), 'ref: refs/heads/main\n');
  const prioRun = capture(['--init'], { cwd: prio });
  assert.match(prioRun.stdout, /Detected: GitHub Actions \(\.github\/workflows\), git \(\.git\)/);
  assert.match(prioRun.stdout, /Paste the GitHub Actions snippet:/);

  // The detector itself is a pure function of the directory contents, in the
  // documented priority order: GitHub Actions, GitLab CI, CircleCI, Jenkins,
  // pre-commit, git.
  const everyHost = mkdir('init-hosts');
  fs.mkdirSync(path.join(everyHost, '.github', 'workflows'), { recursive: true });
  fs.writeFileSync(path.join(everyHost, '.github', 'workflows', 'ci.yml'), 'on: push\n');
  fs.writeFileSync(path.join(everyHost, '.gitlab-ci.yml'), 'stages: []\n');
  fs.mkdirSync(path.join(everyHost, '.circleci'), { recursive: true });
  fs.writeFileSync(path.join(everyHost, '.circleci', 'config.yml'), 'version: 2.1\n');
  fs.writeFileSync(path.join(everyHost, 'Jenkinsfile'), 'pipeline { agent any }\n');
  fs.writeFileSync(path.join(everyHost, '.pre-commit-config.yaml'), 'repos: []\n');
  fs.mkdirSync(path.join(everyHost, '.git'), { recursive: true });
  fs.writeFileSync(path.join(everyHost, '.git', 'HEAD'), 'ref: refs/heads/main\n');
  assert.deepEqual(detectHosts(everyHost).map(host => host.id),
    ['GitHub Actions', 'gitlab-ci', 'circleci', 'jenkins', 'pre-commit', 'git'],
    'detection order is the documented priority order');
  assert.deepEqual(detectHosts(path.join(tmp, 'init-generic')).map(host => host.id), []);

  // formatInitReport keeps the same guarantees when called directly.
  const report = formatInitReport({ relative: '.un-editorial.json', hosts: detectHosts(path.dirname(gt)) });
  assert.match(report, /Wrote \.un-editorial\.json/);
  assert.match(report, /npx un-editorial-check --self-test/);

  // starterConfig is a pure value: calling it twice yields equal fields.
  assert.deepEqual(starterConfig(), starterConfig());
  assert.throws(() => writeStarterConfig(configFile, { overwrite: false }), InitError,
    'writeStarterConfig without overwrite must refuse an existing file');
}

// --- --self-test -------------------------------------------------------------

{
  // The built-in corpus is two in-package cases with exact expectations.
  assert.equal(CORPUS.length, 2, 'the self-test corpus has exactly two cases');
  assert.equal(CORPUS[0].file, 'clean.txt');
  assert.deepEqual(CORPUS[0].expected, [], 'the clean case must expect zero findings');
  assert.equal(CORPUS[1].file, 'violations.txt');
  const expected = CORPUS[1].expected;
  assert(expected.length >= 5, `the violation case must stay substantial, found ${expected.length}`);
  assert(new Set(expected.map(f => f.ruleId)).size >= 3,
    'the violation case must cover at least three distinct rules');
  for (const entry of CORPUS) {
    assert(fs.existsSync(path.join(CORPUS_DIR, entry.file)), `corpus file missing: ${entry.file}`);
  }

  // Cross-check: the real CLI scan of the same corpus files must produce
  // exactly the expectations the self-test asserts (independent code path).
  const corpusPaths = CORPUS.map(entry => path.join(CORPUS_DIR, entry.file));
  const scanned = inProcess([...corpusPaths, '--format', 'json', '--self-scan']);
  assert.equal(scanned.code, 1, `the corpus must contain error-severity findings: ${scanned.stderr}`);
  const actual = JSON.parse(scanned.stdout).findings.map(f => ({
    ruleId: f.ruleId, line: f.line, column: f.column, file: f.file,
  }));
  const fromClean = actual.filter(f => f.file === corpusPaths[0]);
  assert.deepEqual(fromClean, [], 'clean.txt must produce no findings under the default configuration');
  const fromViolations = actual.filter(f => f.file === corpusPaths[1]).map(({ file, ...rest }) => rest);
  assert.deepEqual(sortMarks(fromViolations), sortMarks(expected),
    'the self-test expectations must equal the live scan of the corpus');

  // The success line states the case count and the asserted finding count.
  const ok = capture(['--self-test'], { cwd: tmp });
  assert.equal(ok.code, 0, `self-test must verify a fresh install: ${ok.stderr}`);
  const okMatch = ok.stdout.match(/^ok — self-test: (\d+) corpus cases, (\d+) findings asserted exactly$/m);
  assert(okMatch, `unexpected self-test output: ${ok.stdout}`);
  assert.equal(Number(okMatch[1]), CORPUS.length, 'the case count in the success line must be exact');
  assert.equal(Number(okMatch[2]), expected.length, 'the finding count in the success line must be exact');

  const quiet = capture(['--self-test', '--quiet'], { cwd: tmp });
  assert.equal(quiet.code, 0, quiet.stderr);
  assert.equal(quiet.stdout, '', '--quiet suppresses the success line');

  // Isolation: a broken .un-editorial.json in the working directory cannot
  // influence the self-test — it runs on the bundled defaults only.
  const poisoned = mkdir('selftest-poisoned');
  fs.writeFileSync(path.join(poisoned, '.un-editorial.json'), '{ not json');
  const isolated = capture(['--self-test'], { cwd: poisoned });
  assert.equal(isolated.code, 0, 'the self-test must not read the working-directory config');

  // Usage exclusivity.
  const withPath = capture(['--self-test', 'some.txt'], { cwd: tmp });
  assert.equal(withPath.code, 2);
  assert.match(withPath.stderr, /--self-test cannot be combined with scan paths/);
  const withProfile = capture(['--self-test', '--profile', 'security'], { cwd: tmp });
  assert.equal(withProfile.code, 2);
  assert.match(withProfile.stderr, /--self-test cannot be combined with --profile/);

  // Mismatch: a tampered copy of the corpus must fail with a readable diff.
  const ctxRoot = loadCatalogue(root);
  const defaults = parseJsonStrict(
    fs.readFileSync(path.join(root, 'config', 'default.json'), 'utf8'), 'config/default.json');
  const cfg = validateConfig(defaults, { knownIds: ctxRoot.ids });
  const profile = loadBaselineProfile(root, ctxRoot.ids);
  const ctx = makeContext({ cfg, baseline: profile, meta: ctxRoot.meta });

  const cleanRun = runSelfTest({ ctx });
  assert.equal(cleanRun.ok, true, `the shipped corpus must match its expectations: ${cleanRun.diff.join('\n')}`);
  assert.equal(cleanRun.cases, CORPUS.length);
  assert.equal(cleanRun.findings, expected.length);

  const tampered = path.join(tmp, 'selftest-tampered');
  fs.mkdirSync(tampered, { recursive: true });
  for (const entry of CORPUS) {
    fs.copyFileSync(path.join(CORPUS_DIR, entry.file), path.join(tampered, entry.file));
  }
  fs.appendFileSync(path.join(tampered, 'violations.txt'), 'The color of the cover was noted.\n');
  const extra = runSelfTest({ ctx, corpusDir: tampered });
  assert.equal(extra.ok, false, 'an extra violation must break the exact assertion');
  assert.match(extra.diff.join('\n'), /unexpected UE-/,
    `the diff must name the unexpected finding:\n${extra.diff.join('\n')}`);
  assert.match(extra.diff.join('\n'), /violations\.txt/);

  const emptied = path.join(tmp, 'selftest-emptied');
  fs.mkdirSync(emptied, { recursive: true });
  for (const entry of CORPUS) fs.rmSync(path.join(emptied, entry.file), { force: true });
  assert.throws(() => runSelfTest({ ctx, corpusDir: emptied }), SelfTestError,
    'an unreadable corpus must raise, never pass silently');
}

// --- action.yml and its entry point ------------------------------------------

{
  const actionFile = path.join(root, 'action.yml');
  assert(fs.existsSync(actionFile), 'action.yml must exist at the repository root');
  const text = fs.readFileSync(actionFile, 'utf8');
  assert.match(text, /^name: .+$/m, 'action.yml must declare a name');
  const description = text.match(/^description: (.+)$/m);
  assert(description, 'action.yml must declare a description');
  assert(description[1].length <= 125,
    `the action description must stay within GitHub's 125-character limit (got ${description[1].length})`);
  assert.match(text, /^runs:$/m, 'action.yml must declare runs');
  assert.match(text, /^\s{2}using: node20$/m, 'the action must run on node20');
  assert.match(text, /^\s{2}main: action\/main\.mjs$/m, 'the action must point at its entry script');
  assert(!/\buses:/.test(text), 'a node action must not declare composite uses steps');
  assert(!/npm (install|ci)|curl /.test(text), 'the action must stay dependency-free');
  for (const input of ['path', 'config', 'baseline']) {
    assert(new RegExp(`^\\s{2}${input}:$`, 'm').test(text), `action.yml must declare the ${input} input`);
    assert(new RegExp(`^\\s{4}default:`, 'm').test(text), `input ${input} must carry a default`);
  }
  const entry = path.join(root, 'action', 'main.mjs');
  assert(fs.existsSync(entry), 'action/main.mjs must exist');
  const syntax = spawnSync(process.execPath, ['--check', entry], { encoding: 'utf8' });
  assert.equal(syntax.status, 0, `action/main.mjs must parse: ${syntax.stderr}`);
  const entryText = fs.readFileSync(entry, 'utf8');
  assert(entryText.includes("from '../lib/cli.mjs'"), 'the entry must reuse the CLI');
  assert(entryText.includes('GITHUB_WORKSPACE'), 'the entry must run inside the checked-out workspace');
  assert(entryText.includes('process.exitCode = run('),
    'the entry must map the CLI exit code onto the action result');

  const workspace = mkdir('action-workspace');
  fs.writeFileSync(path.join(workspace, 'page.txt'), 'Coverage reached a record level!\n');
  const failing = spawnSync(process.execPath, [entry], {
    cwd: tmp, encoding: 'utf8',
    env: { ...process.env, GITHUB_WORKSPACE: workspace, INPUT_PATH: 'page.txt' },
  });
  assert.equal(failing.status, 1, `the action must fail on error-severity findings: ${failing.stderr}`);
  assert.match(failing.stdout, /UE-RE005/, 'the action must print the report');
  assert.match(failing.stdout, /un-editorial-check/, 'the action must print the checker banner');

  fs.writeFileSync(path.join(workspace, 'page.txt'), 'The delegation noted the date.\n');
  const passing = spawnSync(process.execPath, [entry], {
    cwd: tmp, encoding: 'utf8',
    env: { ...process.env, GITHUB_WORKSPACE: workspace, INPUT_PATH: 'page.txt' },
  });
  assert.equal(passing.status, 0, `a clean workspace must pass: ${passing.stderr}`);

  const missing = spawnSync(process.execPath, [entry], {
    cwd: tmp, encoding: 'utf8',
    env: { ...process.env, GITHUB_WORKSPACE: workspace, INPUT_PATH: 'no-such-file.txt' },
  });
  assert.equal(missing.status, 2, 'a usage failure must fail the action with exit 2');
}

// --- agent command templates and the pre-commit hook -------------------------

{
  const templates = ['claude-code', 'codex', 'opencode', 'cursor'];
  const P1 = 'Never modify a file before the user has explicitly approved the corrections.';
  const P2 = 'npx un-editorial-check <paths> --report un-editorial-review.pdf';
  const P3 = 'Apply these corrections?';
  const P4 = '--fix --apply';
  const P5 = 'If `proposed` is null, do not improvise — ask the user what should be written instead.';
  const P6 = 'Never claim the copy is clean unless the exit code is 0.';
  const paste = { 'claude-code': 'CLAUDE.md', codex: 'AGENTS.md', opencode: 'AGENTS.md', cursor: '.cursor/rules' };

  for (const name of templates) {
    const file = path.join(root, 'templates', 'agent-commands', `${name}.md`);
    assert(fs.existsSync(file), `template missing: ${file}`);
    const source = fs.readFileSync(file, 'utf8');
    for (const [id, pinned] of [['P1', P1], ['P2', P2], ['P3', P3], ['P4', P4], ['P5', P5], ['P6', P6]]) {
      assert(source.includes(pinned), `${name}.md must carry ${id} verbatim`);
    }
    const idx = pin => source.indexOf(pin);
    assert(idx(P1) < idx(P2) && idx(P2) < idx(P3) && idx(P3) < idx(P4),
      `${name}.md must keep the order: law, scan, approval question, apply`);
    assert(source.includes(paste[name]), `${name}.md must name its paste location (${paste[name]})`);
    assert(source.includes('--baseline .ue-baseline.json'),
      `${name}.md must document the baseline ratchet`);
  }

  const hook = path.join(root, 'templates', 'pre-commit');
  assert(fs.existsSync(hook), 'templates/pre-commit must exist');
  const hookText = fs.readFileSync(hook, 'utf8');
  assert(hookText.startsWith('#!/bin/sh'), 'the hook must be a POSIX sh script');
  assert.equal(hookText, PRE_COMMIT_HOOK,
    'templates/pre-commit must be byte-identical to the PRE_COMMIT_HOOK --init prints');
  const hookSyntax = spawnSync('/bin/sh', ['-n', hook], { encoding: 'utf8' });
  assert.equal(hookSyntax.status, 0, `templates/pre-commit must parse under sh -n: ${hookSyntax.stderr}`);
  const shared = 'git diff --cached --name-only --diff-filter=ACM';
  assert(hookText.includes(shared), 'the hook must collect staged files with the pinned command');
  assert(hookText.includes('un-editorial-check'), 'the hook must invoke the checker');

  // The git snippet printed by --init shares the pinned staged-files line, so
  // the two surfaces cannot drift apart.
  const gitHost = detectHosts(path.join(tmp, 'init-git'));
  const printed = formatInitReport({ relative: '.un-editorial.json', hosts: gitHost });
  assert(printed.includes(shared), '--init must print the same staged-files line as templates/pre-commit');
  assert(printed.includes(hookText.split('\n').find(line => line.includes(shared))),
    'the printed hook and the template must contain the identical line');
}

// --- truncation preview ------------------------------------------------------

{
  assert.deepEqual(Object.keys(PLATFORMS), ['x', 'linkedin', 'bluesky', 'mastodon'],
    'the documented platform order is part of the interface');
  assert.equal(PLATFORMS.x.limit, 280);
  assert.equal(PLATFORMS.x.linkCost, 23, 'on X every link is counted as 23 characters');
  assert.equal(PLATFORMS.linkedin.limit, 3000);
  assert.equal(PLATFORMS.linkedin.linkCost, null, 'LinkedIn counts a link as written');
  assert.equal(PLATFORMS.bluesky.limit, 300);
  assert.equal(PLATFORMS.mastodon.limit, 500);

  const fits = previewTruncate('The delegation noted the date.', 'x');
  assert.equal(fits.counted, 30);
  assert.equal(fits.fits, true);
  assert.equal(fits.preview, 'The delegation noted the date.');
  assert.equal(fits.links, 0);

  const withLink = previewTruncate('ab https://xy.example/z cd', 'x');
  assert.equal(withLink.counted, 29, 'a link costs 23 characters on X regardless of its length');
  assert.equal(withLink.links, 1);
  assert.equal(withLink.linkCharacters, 20, 'linkCharacters records the URL as written');
  assert.equal(withLink.fits, true);

  const over = previewTruncate('a'.repeat(300), 'x');
  assert.equal(over.counted, 300);
  assert.equal(over.overBy, 20);
  assert.equal(over.fits, false);
  assert.equal(over.preview, 'a'.repeat(280), 'the cut is exact, code point by code point');

  const midLink = previewTruncate(`${'a'.repeat(279)} https://example.com/very/long`, 'x');
  assert.equal(midLink.counted, 303);
  assert.equal(midLink.overBy, 23);
  assert.equal(midLink.preview, `${'a'.repeat(279)} `,
    'a link is never cut in half: the budget stops before it');

  const linkedIn = previewTruncate(`https://example.co/1 ${'b'.repeat(3000)}`, 'linkedin');
  assert.equal(linkedIn.counted, 3021, 'on LinkedIn a link is counted as the characters written');
  assert.equal(linkedIn.overBy, 21);
  assert.equal(linkedIn.preview, `https://example.co/1 ${'b'.repeat(2979)}`);

  assert.equal(previewTruncate('e\u0301', 'x').counted, previewTruncate('\u00e9', 'x').counted,
    'counting must be normalisation-stable');
  assert.equal(previewTruncate('two\nlines', 'x').counted, 9, 'line breaks count as one character each');
  assert.equal(previewTruncate('', 'x').counted, 0, 'an empty file costs nothing');

  const fitsText = formatPreview(fits, 'note.txt');
  assert.equal(fitsText, [
    'X preview: note.txt — limit 280 characters',
    'counted 30, fits; links: 0',
    'Preview only: this is not an editorial scan; exit code 0 means the preview was produced.',
  ].join('\n'), 'the fits output is pinned so the docs stay true');
  const overText = formatPreview(over, 'long.txt');
  assert.equal(overText, [
    'X preview: long.txt — limit 280 characters',
    'counted 300, over budget by 20; links: 0',
    '--- cut to the budget ---',
    'a'.repeat(280),
    'Preview only: this is not an editorial scan; exit code 0 means the preview was produced.',
  ].join('\n'));
  assert.match(formatPreview(withLink, 'note.txt'), /links: 1 at 23 characters/);
  assert.match(formatPreview(linkedIn, 'post.txt'), /LinkedIn preview: post\.txt — limit 3000 characters/);
  assert.match(formatPreview(linkedIn, 'post.txt'), /links: 1 counted as written/);

  // CLI behaviour: exit 0 when the preview is produced; usage failures exit 2.
  const pre = mkdir('preview');
  fs.writeFileSync(path.join(pre, 'note.txt'), 'The delegation noted the date.');
  const preview = capture(['--preview', 'x', 'note.txt'], { cwd: pre });
  assert.equal(preview.code, 0, preview.stderr);
  assert.equal(preview.stdout.trim(), fitsText.replace('note.txt', 'note.txt'),
    'the CLI prints exactly the pinned preview');
  assert.match(preview.stdout, /Preview only: this is not an editorial scan/);

  fs.writeFileSync(path.join(pre, 'long.txt'), 'a'.repeat(300));
  const longRun = capture(['--preview', 'x', 'long.txt'], { cwd: pre });
  assert.equal(longRun.code, 0, 'over budget is stated in the output, not in the exit code');
  assert.match(longRun.stdout, /over budget by 20/);

  const quietRun = capture(['--preview', 'x', 'note.txt', '--quiet'], { cwd: pre });
  assert.equal(quietRun.code, 0);
  assert.equal(quietRun.stdout, '', '--quiet suppresses the preview output');

  const unknown = capture(['--preview', 'nope', 'note.txt'], { cwd: pre });
  assert.equal(unknown.code, 2, 'an unknown platform is a usage error');
  assert.match(unknown.stderr, /unknown preview platform "nope" \(expected x, linkedin, bluesky, mastodon\)/);

  const noPath = capture(['--preview', 'x'], { cwd: pre });
  assert.equal(noPath.code, 2);
  assert.match(noPath.stderr, /--preview takes exactly one file path/);
  const twoPaths = capture(['--preview', 'x', 'note.txt', 'long.txt'], { cwd: pre });
  assert.equal(twoPaths.code, 2);
  assert.match(twoPaths.stderr, /--preview takes exactly one file path/);
  const missingFile = capture(['--preview', 'x', 'no-such.txt'], { cwd: pre });
  assert.equal(missingFile.code, 2);
  assert.match(missingFile.stderr, /path not found/);
  const withFix = capture(['--preview', 'x', 'note.txt', '--fix'], { cwd: pre });
  assert.equal(withFix.code, 2, 'the preview never fixes');
  assert.match(withFix.stderr, /--preview cannot be combined with --fix/);
  const withJson = capture(['--preview', 'x', 'note.txt', '--json'], { cwd: pre });
  assert.equal(withJson.code, 2, 'the preview has no JSON form');
  assert.match(withJson.stderr, /--preview cannot be combined with --format/);
}

// --- existing behaviour is untouched, docs and script wiring -----------------

{
  const version = capture(['--version'], { cwd: tmp });
  assert.equal(version.code, 0);
  assert.match(version.stdout, /^un-editorial-check \d+\.\d+\.\d+$/m);

  const unknownFlag = capture(['--definitely-not-a-flag'], { cwd: tmp });
  assert.equal(unknownFlag.code, 2, 'unknown options must still be usage errors');
  assert.match(unknownFlag.stderr, /unknown option --definitely-not-a-flag/);

  const help = capture(['--help'], { cwd: tmp });
  assert.equal(help.code, 0);
  for (const flag of ['--baseline <file>', '--init', '--self-test', '--preview']) {
    assert(help.stdout.includes(flag), `HELP must document ${flag}`);
  }
  assert.match(help.stdout, /snapshot/, 'HELP must explain what the baseline snapshot means');

  const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  assert(readme.includes('Phase 5A adoption pack'),
    'the README additions must stay marked for the documentation merge');
  for (const token of ['--baseline', '--init', '--self-test', '--preview', 'action.yml', 'templates/pre-commit']) {
    assert(readme.includes(token), `README must document ${token}`);
  }

  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  const suites = pkg.scripts.test.split('&&').map(part => part.trim());
  // The PDF-extraction suite joined the gate after this lock was written; the
  // two final suites keep their relative order: adoption, then the PDF locks.
  assert.deepEqual(suites.slice(-2),
    ['node tests/audit-adoption.mjs', 'node tests/audit-pdf-extraction.mjs'],
    'the final gate suites must keep their order: adoption, then PDF extraction');
}

fs.rmSync(tmp, { recursive: true, force: true });
console.log('ok — adoption: baseline keys/snapshot/compare, baseline CLI, init, self-test, action.yml, templates, preview, docs locks');
