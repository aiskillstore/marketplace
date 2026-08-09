import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  renameSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { gzipSync } from 'node:zlib';
import { calculateCanonicalTreeHash } from '../resolve-approved-submission.mjs';

const reusable = readFileSync('.github/workflows/reusable-process-skills.yml', 'utf8');
const approval = readFileSync('.github/workflows/on-pr-merge.yml', 'utf8');
const processSubmission = readFileSync('.github/workflows/process-submission.yml', 'utf8');
const approveSubmission = readFileSync('.github/workflows/approve-submission.yml', 'utf8');
const processShardScript = 'scripts/process-submission-shard.mjs';
const aggregateShardsScript = 'scripts/aggregate-submission-shards.mjs';
const shardContractScript = 'scripts/submission-shard-contract.mjs';

function withTempDirectory(fn) {
  const root = mkdtempSync(join(tmpdir(), 'submission-shards-'));
  try {
    return fn(root);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

function runNode(script, args, options = {}) {
  return spawnSync(process.execPath, [script, ...args], {
    cwd: process.cwd(),
    encoding: 'utf8',
    env: { ...process.env, ...(options.env ?? {}) },
  });
}

function writeSelectionPlan(root, skills, { scope = 'skills' } = {}) {
  const path = join(root, 'selection-plan.json');
  writeFileSync(path, `${JSON.stringify({
    schemaVersion: 1,
    repository: 'example/source',
    sourceCommit: 'a'.repeat(40),
    scope: { path: scope, reason: scope === '.' ? 'explicit_path' : 'conventional_skills' },
    skills,
  })}\n`);
  return path;
}

function selectionPlanFor(skills) {
  return {
    schemaVersion: 1,
    repository: 'example/source',
    sourceCommit: 'a'.repeat(40),
    scope: { path: 'skills', reason: 'conventional_skills' },
    skills: skills.map((slug) => ({ slug, path: `skills/${slug}` })),
  };
}

function writePendingSkill(root, slug, extraFiles = []) {
  const pendingDir = `pending/${slug}`;
  const absoluteDir = join(root, pendingDir);
  mkdirSync(absoluteDir, { recursive: true });
  const skillBytes = `---\nname: ${slug}\ndescription: fixture\n---\n`;
  writeFileSync(join(absoluteDir, 'SKILL.md'), skillBytes);
  for (const [relativePath, content] of extraFiles) {
    const destination = join(absoluteDir, relativePath);
    mkdirSync(dirname(destination), { recursive: true });
    writeFileSync(destination, content);
  }
  const contentHash = createHash('sha256').update(skillBytes).digest('hex');
  const treeHash = calculateCanonicalTreeHash(root, pendingDir);
  writeFileSync(join(absoluteDir, 'skill-report.json'), `${JSON.stringify({
    meta: {
      source_type: 'official',
      slug,
      content_hash: contentHash,
      tree_hash: treeHash,
    },
    security_audit: { is_blocked: false, safe_to_publish: true, risk_level: 'safe' },
  })}\n`);
}

function successfulManifest(index, planned, { reasonCode = 'processed_all_planned' } = {}) {
  const noOp = planned.length === 0;
  return {
    schemaVersion: 1,
    shardIndex: index,
    status: 'succeeded',
    reasonCode: noOp ? 'no_skills_planned' : reasonCode,
    selectionPlan: selectionPlanFor(planned),
    planned,
    succeeded: planned,
    failed: [],
    failureCategories: [],
    attempts: [{
      number: 1,
      phase: 'first',
      status: noOp ? 'skipped' : 'succeeded',
      exitCode: noOp ? null : 0,
      requested: planned,
      succeeded: planned,
      failed: [],
    }],
  };
}

function failedManifest(index, planned, status = 'failed') {
  return {
    schemaVersion: 1,
    shardIndex: index,
    status,
    reasonCode: status === 'failed' ? 'processing_failed' : `processing_${status}`,
    selectionPlan: selectionPlanFor(planned),
    planned,
    succeeded: [],
    failed: planned,
    failureCategories: [status === 'failed' ? 'cli_nonzero' : status],
    attempts: [{
      number: 1,
      phase: 'first',
      status,
      exitCode: status === 'failed' ? 23 : null,
      requested: planned,
      succeeded: [],
      failed: planned,
    }],
  };
}

function createShardArchive(artifactsDir, {
  rawIndex,
  manifest,
  selectionPlan = manifest?.selectionPlan,
  slugs = manifest?.succeeded ?? [],
  nested = '',
  omitManifest = false,
  extraFiles = {},
}) {
  const fixtureRoot = mkdtempSync(join(tmpdir(), 'submission-archive-root-'));
  try {
    mkdirSync(join(fixtureRoot, 'pending'), { recursive: true });
    for (const slug of slugs) writePendingSkill(fixtureRoot, slug, extraFiles[slug] ?? []);
    if (!omitManifest) {
      writeFileSync(join(fixtureRoot, 'shard-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
    }
    writeFileSync(join(fixtureRoot, 'selection-plan.json'), `${JSON.stringify(selectionPlan)}\n`);
    const archiveDir = join(artifactsDir, nested);
    mkdirSync(archiveDir, { recursive: true });
    const archive = join(archiveDir, `process-shard-1-${rawIndex}.tar.gz`);
    const entries = ['pending', 'selection-plan.json'];
    if (!omitManifest) entries.push('shard-manifest.json');
    const tar = spawnSync('tar', ['-C', fixtureRoot, '-czf', archive, ...entries], { encoding: 'utf8' });
    assert.equal(tar.status, 0, tar.stderr);
    return archive;
  } finally {
    rmSync(fixtureRoot, { recursive: true, force: true });
  }
}

function createRawEntryArchive(artifactsDir, entryName) {
  const name = Buffer.from(entryName, 'utf8');
  assert.ok(name.length > 0 && name.length <= 100, 'raw tar fixture name must fit in the header');
  const header = Buffer.alloc(512);
  name.copy(header, 0);
  Buffer.from('0000644\0').copy(header, 100);
  Buffer.from('0000000\0').copy(header, 108);
  Buffer.from('0000000\0').copy(header, 116);
  Buffer.from('00000000000\0').copy(header, 124);
  Buffer.from('00000000000\0').copy(header, 136);
  header.fill(0x20, 148, 156);
  header[156] = '0'.charCodeAt(0);
  Buffer.from('ustar\0').copy(header, 257);
  Buffer.from('00').copy(header, 263);
  const checksum = header.reduce((sum, byte) => sum + byte, 0);
  Buffer.from(`${checksum.toString(8).padStart(6, '0')}\0 `).copy(header, 148);
  const archive = join(artifactsDir, 'process-shard-1-0.tar.gz');
  writeFileSync(archive, gzipSync(Buffer.concat([header, Buffer.alloc(1024)])));
  return archive;
}

function matrixWithSelectionPlans(matrix) {
  return {
    include: matrix.include.map((entry) => entry.selection_plan ? entry : {
      shard: entry.shard,
      selection_plan: selectionPlanFor(entry.slugs === '' ? [] : entry.slugs.split(',')),
    }),
  };
}

function runAggregate(root, matrix, expectedCount = matrix.include.length, { normalizeLegacyMatrix = true } = {}) {
  const approvalPlan = join(root, 'approval-plan.json');
  const mergedResults = join(root, 'merged');
  const summary = join(root, 'summary.json');
  const result = runNode(aggregateShardsScript, [
    '--artifacts-dir', join(root, 'artifacts'),
    '--run-attempt', '1',
    '--matrix-json', JSON.stringify(normalizeLegacyMatrix ? matrixWithSelectionPlans(matrix) : matrix),
    '--expected-count', String(expectedCount),
    '--approval-plan', approvalPlan,
    '--merged-results', mergedResults,
    '--summary', summary,
  ]);
  return { result, approvalPlan, mergedResults, summary };
}

test('submission processing isolates every shard and stages only its frozen plan', () => {
  assert.match(reusable, /RESULT_DIR="\/tmp\/submission-shard-/);
  assert.match(reusable, /process-shard-\$\{\{ github\.run_attempt \}\}-\$\{\{ matrix\.shard \}\}/);
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/process-submission-shard\.mjs"/);
  assert.match(reusable, /node "\$GITHUB_WORKSPACE\/scripts\/aggregate-submission-shards\.mjs"/);
  assert.match(reusable, /--slug-aliases-file "\$GITHUB_WORKSPACE\/governance\/submission-slug-aliases\.json"/);
  assert.match(reusable, /--selection-plan "\$INPUT_PLAN"/);
  assert.match(reusable, /PLAN_EVIDENCE=\(\)/);
  assert.match(reusable, /selection-plan\.invalid\.json/);
  assert.match(reusable, /git add -f -- "\$\{SUBMISSION_PATHS\[@\]\}"/);
  assert.doesNotMatch(reusable, /continue-on-error:\s*true/);
  assert.doesNotMatch(reusable, /skill process[\s\S]{0,500}\|\| true/);
  assert.match(reusable, /Enforce shard terminal status/);
  assert.match(reusable, /Frozen update target is missing or unsafe/);
  assert.match(reusable, /Unexpected published target collision/);
});

test('submission staging preserves frozen tracked files hidden by a copied .gitignore', () => withTempDirectory((root) => {
  const pendingDir = 'pending/owner/skill';
  mkdirSync(join(root, pendingDir, 'dist'), { recursive: true });
  writeFileSync(join(root, pendingDir, '.gitignore'), 'dist/\n');
  writeFileSync(join(root, pendingDir, 'SKILL.md'), '# Skill\n');
  writeFileSync(join(root, pendingDir, 'dist/cli.js'), 'export default true;\n');
  for (const args of [
    ['init', '-q'],
    ['add', '-f', '--', pendingDir],
  ]) {
    const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  }
  const staged = spawnSync('git', ['diff', '--cached', '--name-only'], { cwd: root, encoding: 'utf8' });
  assert.equal(staged.status, 0, staged.stderr);
  assert.match(staged.stdout, /pending\/owner\/skill\/dist\/cli\.js/);
}));

test('approval staging preserves reviewed files hidden by the packaged .gitignore', () => withTempDirectory((root) => {
  const pending = join(root, 'pending', 'owner', 'skill');
  const published = join(root, 'skills', 'owner', 'skill');
  mkdirSync(join(pending, 'dist'), { recursive: true });
  writeFileSync(join(root, '.gitignore'), 'dist/\n');
  writeFileSync(join(pending, 'SKILL.md'), '# Skill\n');
  writeFileSync(join(pending, 'dist', 'runtime.js'), 'export const ready = true;\n');

  for (const args of [
    ['init'],
    ['config', 'user.email', 'test@example.com'],
    ['config', 'user.name', 'Test'],
    ['add', '-A', '-f'],
    ['commit', '-m', 'fixture'],
  ]) {
    const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  }

  mkdirSync(dirname(published), { recursive: true });
  renameSync(pending, published);
  const stage = spawnSync('git', [
    'add', '-A', '-f', '--', 'pending/owner/skill', 'skills/owner/skill',
  ], { cwd: root, encoding: 'utf8' });
  assert.equal(stage.status, 0, stage.stderr);

  const staged = spawnSync('git', ['diff', '--cached', '--name-status'], {
    cwd: root,
    encoding: 'utf8',
  });
  assert.equal(staged.status, 0, staged.stderr);
  assert.match(staged.stdout, /skills\/owner\/skill\/dist\/runtime\.js/);
}));

test('real CLI two-round failure produces a failed manifest and cannot aggregate as no-op', () => withTempDirectory((root) => {
  const fakeCli = join(root, 'fake-cli.sh');
  const state = join(root, 'calls.txt');
  const argsLog = join(root, 'args.txt');
  const aliases = join(root, 'aliases.json');
  const resultDir = join(root, 'result');
  const selectionPlan = writeSelectionPlan(root, [{ slug: 'broken-skill', path: 'skills/broken-skill' }]);
  writeFileSync(aliases, '{"schemaVersion":1,"aliases":[]}\n');
  writeFileSync(fakeCli, `#!/usr/bin/env bash\nset -eu\ncount=0\n[ ! -f "$FAKE_STATE" ] || count=$(cat "$FAKE_STATE")\ncount=$((count + 1))\nprintf '%s\\n' "$count" > "$FAKE_STATE"\nprintf '%s\\n' "$*" >> "$FAKE_ARGS"\necho "fixture CLI failure $count" >&2\nexit 23\n`);
  chmodSync(fakeCli, 0o755);

  const processing = runNode(processShardScript, [
    '--cli', fakeCli,
    '--github-url', 'https://github.com/example/source',
    '--selection-plan', selectionPlan,
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--slug-aliases-file', aliases,
    '--retry-delay-ms', '0',
  ], { env: { FAKE_STATE: state, FAKE_ARGS: argsLog } });
  assert.equal(processing.status, 0, processing.stderr);
  assert.equal(readFileSync(state, 'utf8').trim(), '2');
  const attempts = readFileSync(argsLog, 'utf8').trim().split('\n');
  assert.equal(attempts.length, 2);
  for (const args of attempts) {
    assert.match(args, new RegExp(`--slug-aliases-file ${aliases.replaceAll('/', '\\/')}`));
    assert.match(args, /--selection-plan .*selection-plan\.json/);
    assert.match(args, /--slugs broken-skill/);
  }
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.deepEqual(JSON.parse(readFileSync(join(resultDir, 'selection-plan.json'), 'utf8')), JSON.parse(readFileSync(selectionPlan, 'utf8')));
  assert.equal(manifest.status, 'failed');
  assert.deepEqual(manifest.planned, ['broken-skill']);
  assert.deepEqual(manifest.succeeded, []);
  assert.deepEqual(manifest.failed, ['broken-skill']);
  assert.deepEqual(manifest.attempts.map(({ status }) => status), ['failed', 'failed']);

  const terminal = runNode(shardContractScript, [
    '--manifest', join(resultDir, 'shard-manifest.json'),
    '--expected-index', '0',
    '--expected-slugs', 'broken-skill',
    '--expected-selection-plan', selectionPlan,
    '--pending-root', join(resultDir, 'pending'),
    '--require-success',
  ]);
  assert.notEqual(terminal.status, 0, 'failed manifest must fail the post-upload terminal gate');

  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  const archive = join(artifacts, 'process-shard-1-0.tar.gz');
  const tar = spawnSync('tar', [
    '-C', resultDir,
    '-czf', archive,
    'pending',
    'shard-manifest.json',
  ], { encoding: 'utf8' });
  assert.equal(tar.status, 0, tar.stderr);
  const aggregate = runAggregate(root, { include: [{ shard: 0, slugs: 'broken-skill' }] });
  assert.notEqual(aggregate.result.status, 0, 'failed shard archive must not become a successful no-op');
}));

test('a successful retry closes the manifest only after every planned result exists', () => withTempDirectory((root) => {
  const fakeCli = join(root, 'fake-cli.sh');
  const state = join(root, 'calls.txt');
  const sourceFixture = join(root, 'source-fixture');
  const resultDir = join(root, 'result');
  const selectionPlan = writeSelectionPlan(root, [{ slug: 'recoverable', path: 'skills/recoverable' }]);
  mkdirSync(join(sourceFixture, 'pending'), { recursive: true });
  writePendingSkill(sourceFixture, 'recoverable');
  writeFileSync(fakeCli, `#!/usr/bin/env bash\nset -eu\ncount=0\n[ ! -f "$FAKE_STATE" ] || count=$(cat "$FAKE_STATE")\ncount=$((count + 1))\nprintf '%s\\n' "$count" > "$FAKE_STATE"\nif [ "$count" -eq 1 ]; then\n  echo 'first attempt fails' >&2\n  exit 23\nfi\noutput=''\nwhile [ "$#" -gt 0 ]; do\n  if [ "$1" = '--output' ]; then output="$2"; break; fi\n  shift\ndone\ntest -n "$output"\nmkdir -p "$output/pending"\ncp -R "$FIXTURE_PENDING/recoverable" "$output/pending/recoverable"\n`);
  chmodSync(fakeCli, 0o755);

  const processing = runNode(processShardScript, [
    '--cli', fakeCli,
    '--github-url', 'https://github.com/example/source',
    '--selection-plan', selectionPlan,
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--retry-delay-ms', '0',
  ], { env: { FAKE_STATE: state, FIXTURE_PENDING: join(sourceFixture, 'pending') } });
  assert.equal(processing.status, 0, processing.stderr);
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.deepEqual(JSON.parse(readFileSync(join(resultDir, 'selection-plan.json'), 'utf8')), JSON.parse(readFileSync(selectionPlan, 'utf8')));
  assert.equal(manifest.status, 'succeeded');
  assert.equal(manifest.reasonCode, 'processed_all_planned');
  assert.deepEqual(manifest.succeeded, ['recoverable']);
  assert.deepEqual(manifest.failed, []);
  assert.deepEqual(manifest.attempts.map(({ status }) => status), ['failed', 'succeeded']);

  const terminal = runNode(shardContractScript, [
    '--manifest', join(resultDir, 'shard-manifest.json'),
    '--expected-index', '0',
    '--expected-slugs', 'recoverable',
    '--expected-selection-plan', selectionPlan,
    '--pending-root', join(resultDir, 'pending'),
    '--require-success',
  ]);
  assert.equal(terminal.status, 0, terminal.stderr);
}));

test('the shard contract rejects a serialized selection plan whose paths do not match the shard slugs', () => withTempDirectory((root) => {
  const manifest = successfulManifest(0, ['alpha']);
  manifest.selectionPlan = {
    schemaVersion: 1,
    repository: 'example/source',
    sourceCommit: 'a'.repeat(40),
    scope: { path: 'skills', reason: 'conventional_skills' },
    skills: [{ slug: 'beta', path: 'skills/beta' }],
  };
  const manifestPath = join(root, 'shard-manifest.json');
  const expectedPlan = writeSelectionPlan(root, [{ slug: 'alpha', path: 'skills/alpha' }]);
  writeFileSync(manifestPath, `${JSON.stringify(manifest)}\n`);
  mkdirSync(join(root, 'pending'));
  const result = runNode(shardContractScript, [
    '--manifest', manifestPath,
    '--expected-index', '0',
    '--expected-slugs', 'alpha',
    '--expected-selection-plan', expectedPlan,
    '--pending-root', join(root, 'pending'),
  ]);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /selection plan does not match planned slugs/);
}));

test('an invalid selection plan still produces an uploadable diagnostic manifest and raw-plan evidence', () => withTempDirectory((root) => {
  const plan = join(root, 'tampered-plan.json');
  const resultDir = join(root, 'result');
  writeFileSync(plan, '{not-json\n');
  const result = runNode(processShardScript, [
    '--cli', join(root, 'not-invoked'),
    '--github-url', 'https://github.com/example/source',
    '--selection-plan', plan,
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--retry-delay-ms', '0',
  ]);
  assert.equal(result.status, 0, result.stderr);
  assert.equal(readFileSync(join(resultDir, 'selection-plan.invalid.json'), 'utf8'), '{not-json\n');
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.equal(manifest.reasonCode, 'process_step_failed');
  assert.equal(manifest.selectionPlan, null);
}));

test('overlapping skill paths fail before the submission CLI is invoked', () => withTempDirectory((root) => {
  const fakeCli = join(root, 'fake-cli.sh');
  const invoked = join(root, 'cli-invoked');
  const resultDir = join(root, 'result');
  const selectionPlan = writeSelectionPlan(root, [
    { slug: 'monad', path: 'skills/monad' },
    { slug: 'addresses', path: 'skills/monad/addresses' },
  ]);
  writeFileSync(fakeCli, '#!/usr/bin/env bash\nset -eu\ntouch "$CLI_INVOKED"\nexit 23\n');
  chmodSync(fakeCli, 0o755);

  const result = runNode(processShardScript, [
    '--cli', fakeCli,
    '--github-url', 'https://github.com/starchild-ai-agent/official-skills',
    '--selection-plan', selectionPlan,
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--retry-delay-ms', '0',
  ], { env: { CLI_INVOKED: invoked } });

  assert.equal(result.status, 0, result.stderr);
  assert.equal(existsSync(invoked), false, 'invalid overlapping plan must not invoke the CLI');
  assert.match(
    readFileSync(join(resultDir, 'process-output-0.log'), 'utf8'),
    /selection plan skill paths overlap: skills\/monad and skills\/monad\/addresses/,
  );
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.equal(manifest.reasonCode, 'process_step_failed');
  assert.equal(manifest.selectionPlan, null);
}));

test('aggregation accepts root and nested archives only when manifests and pending results agree', () => withTempDirectory((root) => {
  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  createShardArchive(artifacts, {
    rawIndex: '0',
    manifest: successfulManifest(0, ['alpha']),
    slugs: ['alpha'],
  });
  createShardArchive(artifacts, {
    rawIndex: '1',
    manifest: successfulManifest(1, ['beta']),
    slugs: ['beta'],
    nested: 'process-shard-1-1',
  });

  const aggregate = runAggregate(root, {
    include: [
      { shard: 0, slugs: 'alpha' },
      { shard: 1, slugs: 'beta' },
    ],
  });
  assert.equal(aggregate.result.status, 0, aggregate.result.stderr);
  const plan = JSON.parse(readFileSync(aggregate.approvalPlan, 'utf8'));
  assert.deepEqual(plan.skills.map(({ pendingDir }) => pendingDir), ['pending/alpha', 'pending/beta']);
  assert.equal(JSON.parse(readFileSync(aggregate.summary, 'utf8')).status, 'has_results');
}));

test('aggregation rejects legacy slug-only matrix entries and path-bound plan drift', () => withTempDirectory((root) => {
  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  const manifest = successfulManifest(0, ['alpha']);
  manifest.selectionPlan.skills[0].path = 'skills/other-alpha';
  createShardArchive(artifacts, {
    rawIndex: '0',
    manifest,
    selectionPlan: selectionPlanFor(['alpha']),
    slugs: ['alpha'],
  });
  const matrix = { include: [{ shard: 0, slugs: 'alpha' }] };
  const legacy = runAggregate(root, matrix, 1, { normalizeLegacyMatrix: false });
  assert.notEqual(legacy.result.status, 0);
  assert.match(legacy.result.stderr, /selection_plan/);
  const drift = runAggregate(root, matrix);
  assert.notEqual(drift.result.status, 0);
  assert.match(drift.result.stderr, /selection plan does not match matrix selection plan/);
}));

test('aggregation requires archive selection-plan evidence to exactly match the matrix plan', () => withTempDirectory((root) => {
  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  const tamperedPlan = { ...selectionPlanFor(['alpha']), skills: [{ slug: 'alpha', path: 'skills/tampered-alpha' }] };
  createShardArchive(artifacts, {
    rawIndex: '0',
    manifest: successfulManifest(0, ['alpha']),
    selectionPlan: tamperedPlan,
    slugs: ['alpha'],
  });
  const matrix = { include: [{ shard: 0, selection_plan: selectionPlanFor(['alpha']) }] };
  const aggregate = runAggregate(root, matrix);
  assert.notEqual(aggregate.result.status, 0);
  assert.match(aggregate.result.stderr, /archive selection plan does not match matrix selection plan/);
}));

for (const fixture of [
  {
    name: 'mixed source commits',
    plans: [selectionPlanFor(['alpha']), { ...selectionPlanFor(['beta']), sourceCommit: 'b'.repeat(40) }],
    expected: /identity does not match/,
  },
  {
    name: 'mixed scopes',
    plans: [selectionPlanFor(['alpha']), { ...selectionPlanFor(['beta']), scope: { path: '.', reason: 'explicit_path' }, skills: [{ slug: 'beta', path: 'beta' }] }],
    expected: /identity does not match/,
  },
  {
    name: 'duplicate slugs',
    plans: [selectionPlanFor(['alpha']), selectionPlanFor(['alpha'])],
    expected: /duplicate slug/,
  },
  {
    name: 'duplicate paths',
    plans: [selectionPlanFor(['alpha']), { ...selectionPlanFor(['beta']), skills: [{ slug: 'beta', path: 'skills/alpha' }] }],
    expected: /duplicate path/,
  },
]) {
  test(`aggregation rejects matrix selection plans with ${fixture.name}`, () => withTempDirectory((root) => {
    mkdirSync(join(root, 'artifacts'));
    const matrix = { include: fixture.plans.map((selection_plan, shard) => ({ shard, selection_plan })) };
    const aggregate = runAggregate(root, matrix);
    assert.notEqual(aggregate.result.status, 0);
    assert.match(aggregate.result.stderr, fixture.expected);
  }));
}

test('aggregation preserves printable UTF-8 archive paths without weakening path validation', () => withTempDirectory((root) => {
  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  createShardArchive(artifacts, {
    rawIndex: '0',
    manifest: successfulManifest(0, ['alpha']),
    slugs: ['alpha'],
    extraFiles: { alpha: [['references/水电与渗漏问题.md', 'fixture\n']] },
  });
  const aggregate = runAggregate(root, { include: [{ shard: 0, slugs: 'alpha' }] });
  assert.equal(aggregate.result.status, 0, aggregate.result.stderr);
  assert.equal(readFileSync(join(aggregate.mergedResults, 'pending/alpha/references/水电与渗漏问题.md'), 'utf8'), 'fixture\n');
}));

for (const entryName of [
  '/absolute.md',
  '../traversal.md',
  'pending/alpha/back\\slash.md',
  'pending/alpha/control\ncharacter.md',
]) {
  test(`aggregation rejects unsafe raw archive path ${JSON.stringify(entryName)}`, () => withTempDirectory((root) => {
    const artifacts = join(root, 'artifacts');
    mkdirSync(artifacts);
    createRawEntryArchive(artifacts, entryName);
    const aggregate = runAggregate(root, { include: [{ shard: 0, slugs: 'alpha' }] });
    assert.notEqual(aggregate.result.status, 0, `${entryName} unexpectedly passed`);
    assert.match(aggregate.result.stderr, /contains unsafe path/);
  }));
}

test('legal no-op requires an explicit successful no_skills_planned manifest', () => withTempDirectory((root) => {
  const artifacts = join(root, 'artifacts');
  mkdirSync(artifacts);
  createShardArchive(artifacts, {
    rawIndex: '0',
    manifest: successfulManifest(0, []),
    slugs: [],
  });
  const aggregate = runAggregate(root, { include: [{ shard: 0, slugs: '' }] });
  assert.equal(aggregate.result.status, 0, aggregate.result.stderr);
  assert.deepEqual(JSON.parse(readFileSync(aggregate.approvalPlan, 'utf8')), { schemaVersion: 1, skills: [] });
  assert.deepEqual(JSON.parse(readFileSync(aggregate.summary, 'utf8')), {
    schemaVersion: 1,
    status: 'no_op',
    reasonCode: 'no_skills_planned',
    shardIndices: [0],
  });
}));

const rejectedFixtures = [
  {
    name: 'failed manifest',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: failedManifest(0, ['alpha']) }],
  },
  {
    name: 'cancelled manifest',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: failedManifest(0, ['alpha'], 'cancelled') }],
  },
  {
    name: 'skipped manifest',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: failedManifest(0, ['alpha'], 'skipped') }],
  },
  {
    name: 'missing manifest',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'], omitManifest: true }],
  },
  {
    name: '0 and 00 leading-zero alias',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }, { shard: 1, slugs: 'beta' }] },
    archives: [
      { rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] },
      { rawIndex: '00', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'], nested: 'alias' },
    ],
  },
  {
    name: '01 leading-zero index',
    matrix: { include: [{ shard: 1, slugs: 'alpha' }] },
    archives: [{ rawIndex: '01', manifest: successfulManifest(1, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: '+0 signed index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '+0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'negative index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '-1', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'non-decimal index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0x0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'unknown shard index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '2', manifest: successfulManifest(2, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'duplicate canonical index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [
      { rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] },
      { rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'], nested: 'duplicate' },
    ],
  },
  {
    name: 'missing expected shard',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }, { shard: 1, slugs: 'beta' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'matrix slug mismatch',
    matrix: { include: [{ shard: 0, slugs: 'beta' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'manifest outcome partition mismatch',
    matrix: { include: [{ shard: 0, slugs: 'alpha,beta' }] },
    archives: [{
      rawIndex: '0',
      manifest: {
        ...successfulManifest(0, ['alpha', 'beta']),
        succeeded: ['alpha'],
        failed: [],
      },
      slugs: ['alpha'],
    }],
  },
  {
    name: 'successful manifest with empty pending output',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: [] }],
  },
  {
    name: 'noncanonical matrix index',
    matrix: { include: [{ shard: '0', slugs: 'alpha' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
  {
    name: 'duplicate matrix index',
    matrix: { include: [{ shard: 0, slugs: 'alpha' }, { shard: 0, slugs: 'beta' }] },
    archives: [{ rawIndex: '0', manifest: successfulManifest(0, ['alpha']), slugs: ['alpha'] }],
  },
];

for (const fixture of rejectedFixtures) {
  test(`aggregation rejects ${fixture.name}`, () => withTempDirectory((root) => {
    const artifacts = join(root, 'artifacts');
    mkdirSync(artifacts);
    for (const archive of fixture.archives) createShardArchive(artifacts, archive);
    const aggregate = runAggregate(root, fixture.matrix);
    assert.notEqual(aggregate.result.status, 0, `${fixture.name} unexpectedly passed\n${aggregate.result.stdout}`);
  }));
}

test('submission callers emit distinct terminal callbacks for legal no-op, rejection, and failure', () => {
  for (const workflow of [processSubmission, approveSubmission]) {
    assert.match(workflow, /needs\.process-skills\.result == 'failure'/);
    assert.match(workflow, /needs\.process-skills\.outputs\.outcome == 'no_op'/);
    assert.match(workflow, /"event": "completed"/);
    assert.match(workflow, /"reason_code":/);
    assert.match(workflow, /needs\.process-skills\.outputs\.outcome == 'rejected'/);
    assert.match(workflow, /event: "rejected"/);
    assert.match(workflow, /outcome: "rejected"/);
    assert.match(workflow, /reason_code: \$reason_code/);
    assert.match(workflow, /reason: \$reason/);
    assert.match(workflow, /processed_count: 0/);
    assert.match(workflow, /curl --fail-with-body/);
    assert.match(workflow, /--retry 3/);
  }
});

test('merged approval scope comes only from immutable PR changed files', () => {
  assert.match(approval, /Verify trusted submission PR provenance/);
  assert.match(approval, /\.user\.id == 254047988/);
  assert.match(approval, /\.user\.login == "ai-skill-store\[bot\]"/);
  assert.match(approval, /\.head\.repo\.full_name == \$repository/);
  assert.match(approval, /\.head\.ref \| startswith\("submission\/"\)/);
  assert.match(approval, /pulls\/\$PR_NUMBER\/files\?per_page=100/);
  assert.match(approval, /for CLONE_ATTEMPT in 1 2 3/);
  assert.match(approval, /git clone --depth 1 --filter=blob:none --no-checkout/);
  assert.match(approval, /sparse-checkout set --no-cone --stdin/);
  assert.match(approval, /ls-tree HEAD/);
  assert.match(approval, /symlink or non-directory path component/);
  assert.match(approval, /node scripts\/resolve-approved-submission\.mjs/);
  assert.match(approval, /mapfile -t SKILL_PATHS/);
  assert.match(approval, /diff -qr --exclude=skill-report\.json "\$PENDING_DIR" "\$TARGET_DIR"/);
  assert.match(approval, /rm -rf -- "\$PENDING_DIR"/);
  assert.match(approval, /Reviewed update target is missing or unsafe/);
  assert.match(approval, /git diff --quiet "\$MERGE_COMMIT_SHA" HEAD -- "\$PENDING_DIR"/);
  assert.match(approval, /Published update target changed after the reviewed merge/);
  assert.match(approval, /verify_update_parent/);
  assert.match(approval, /--tree-hash-at-commit/);
  assert.match(approval, /\[ "\$parent_tree" = "\$expected_tree" \]/);
  assert.match(approval, /Published update target changed before push/);
  assert.match(approval, /git add -A -f -- "\$\{SKILL_PATHS\[@\]\}" "\$\{TARGET_PATHS\[@\]\}"/);
  assert.match(approval, /PUSHED=false/);
  assert.match(approval, /test "\$PUSHED" = true/);
  assert.match(approval, /for i in \{1\.\.12\}; do/);
  assert.match(approval, /RANDOM % 3/);
  assert.doesNotMatch(approval, /cherry-pick HEAD@\{1\} \|\| true/);
  assert.doesNotMatch(approval, /find pending/);
  assert.match(approval, /rm -rf -- "\$TARGET_DIR"/);
});
