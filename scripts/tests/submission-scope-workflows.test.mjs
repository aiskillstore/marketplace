import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  chmodSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
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

function writePendingSkill(root, slug) {
  const pendingDir = `pending/${slug}`;
  const absoluteDir = join(root, pendingDir);
  mkdirSync(absoluteDir, { recursive: true });
  const skillBytes = `---\nname: ${slug}\ndescription: fixture\n---\n`;
  writeFileSync(join(absoluteDir, 'SKILL.md'), skillBytes);
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
  slugs = manifest?.succeeded ?? [],
  nested = '',
  omitManifest = false,
}) {
  const fixtureRoot = mkdtempSync(join(tmpdir(), 'submission-archive-root-'));
  try {
    mkdirSync(join(fixtureRoot, 'pending'), { recursive: true });
    for (const slug of slugs) writePendingSkill(fixtureRoot, slug);
    if (!omitManifest) {
      writeFileSync(join(fixtureRoot, 'shard-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
    }
    const archiveDir = join(artifactsDir, nested);
    mkdirSync(archiveDir, { recursive: true });
    const archive = join(archiveDir, `process-shard-1-${rawIndex}.tar.gz`);
    const entries = ['pending'];
    if (!omitManifest) entries.push('shard-manifest.json');
    const tar = spawnSync('tar', ['-C', fixtureRoot, '-czf', archive, ...entries], { encoding: 'utf8' });
    assert.equal(tar.status, 0, tar.stderr);
    return archive;
  } finally {
    rmSync(fixtureRoot, { recursive: true, force: true });
  }
}

function runAggregate(root, matrix, expectedCount = matrix.include.length) {
  const approvalPlan = join(root, 'approval-plan.json');
  const mergedResults = join(root, 'merged');
  const summary = join(root, 'summary.json');
  const result = runNode(aggregateShardsScript, [
    '--artifacts-dir', join(root, 'artifacts'),
    '--run-attempt', '1',
    '--matrix-json', JSON.stringify(matrix),
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
  assert.match(reusable, /git add -- "\$\{SUBMISSION_PATHS\[@\]\}"/);
  assert.doesNotMatch(reusable, /continue-on-error:\s*true/);
  assert.doesNotMatch(reusable, /skill process[\s\S]{0,500}\|\| true/);
  assert.match(reusable, /Enforce shard terminal status/);
  assert.match(reusable, /Published target already exists; use the explicit update workflow/);
});

test('real CLI two-round failure produces a failed manifest and cannot aggregate as no-op', () => withTempDirectory((root) => {
  const fakeCli = join(root, 'fake-cli.sh');
  const state = join(root, 'calls.txt');
  const resultDir = join(root, 'result');
  writeFileSync(fakeCli, `#!/usr/bin/env bash\nset -eu\ncount=0\n[ ! -f "$FAKE_STATE" ] || count=$(cat "$FAKE_STATE")\ncount=$((count + 1))\nprintf '%s\\n' "$count" > "$FAKE_STATE"\necho "fixture CLI failure $count" >&2\nexit 23\n`);
  chmodSync(fakeCli, 0o755);

  const processing = runNode(processShardScript, [
    '--cli', fakeCli,
    '--github-url', 'https://github.com/example/source',
    '--slugs', 'broken-skill',
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--retry-delay-ms', '0',
  ], { env: { FAKE_STATE: state } });
  assert.equal(processing.status, 0, processing.stderr);
  assert.equal(readFileSync(state, 'utf8').trim(), '2');
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.equal(manifest.status, 'failed');
  assert.deepEqual(manifest.planned, ['broken-skill']);
  assert.deepEqual(manifest.succeeded, []);
  assert.deepEqual(manifest.failed, ['broken-skill']);
  assert.deepEqual(manifest.attempts.map(({ status }) => status), ['failed', 'failed']);

  const terminal = runNode(shardContractScript, [
    '--manifest', join(resultDir, 'shard-manifest.json'),
    '--expected-index', '0',
    '--expected-slugs', 'broken-skill',
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
  mkdirSync(join(sourceFixture, 'pending'), { recursive: true });
  writePendingSkill(sourceFixture, 'recoverable');
  writeFileSync(fakeCli, `#!/usr/bin/env bash\nset -eu\ncount=0\n[ ! -f "$FAKE_STATE" ] || count=$(cat "$FAKE_STATE")\ncount=$((count + 1))\nprintf '%s\\n' "$count" > "$FAKE_STATE"\nif [ "$count" -eq 1 ]; then\n  echo 'first attempt fails' >&2\n  exit 23\nfi\noutput=''\nwhile [ "$#" -gt 0 ]; do\n  if [ "$1" = '--output' ]; then output="$2"; break; fi\n  shift\ndone\ntest -n "$output"\nmkdir -p "$output/pending"\ncp -R "$FIXTURE_PENDING/recoverable" "$output/pending/recoverable"\n`);
  chmodSync(fakeCli, 0o755);

  const processing = runNode(processShardScript, [
    '--cli', fakeCli,
    '--github-url', 'https://github.com/example/source',
    '--slugs', 'recoverable',
    '--result-dir', resultDir,
    '--marketplace-repo', 'aiskillstore/marketplace',
    '--shard-index', '0',
    '--retry-delay-ms', '0',
  ], { env: { FAKE_STATE: state, FIXTURE_PENDING: join(sourceFixture, 'pending') } });
  assert.equal(processing.status, 0, processing.stderr);
  const manifest = JSON.parse(readFileSync(join(resultDir, 'shard-manifest.json'), 'utf8'));
  assert.equal(manifest.status, 'succeeded');
  assert.equal(manifest.reasonCode, 'processed_all_planned');
  assert.deepEqual(manifest.succeeded, ['recoverable']);
  assert.deepEqual(manifest.failed, []);
  assert.deepEqual(manifest.attempts.map(({ status }) => status), ['failed', 'succeeded']);

  const terminal = runNode(shardContractScript, [
    '--manifest', join(resultDir, 'shard-manifest.json'),
    '--expected-index', '0',
    '--expected-slugs', 'recoverable',
    '--pending-root', join(resultDir, 'pending'),
    '--require-success',
  ]);
  assert.equal(terminal.status, 0, terminal.stderr);
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

test('submission callers emit a terminal callback for explicit legal no-op and failure', () => {
  for (const workflow of [processSubmission, approveSubmission]) {
    assert.match(workflow, /needs\.process-skills\.result == 'failure'/);
    assert.match(workflow, /needs\.process-skills\.outputs\.outcome == 'no_op'/);
    assert.match(workflow, /"event": "completed"/);
    assert.match(workflow, /"reason_code":/);
  }
});

test('merged approval scope comes only from immutable PR changed files', () => {
  assert.match(approval, /pulls\/\$PR_NUMBER\/files\?per_page=100/);
  assert.match(approval, /node scripts\/resolve-approved-submission\.mjs/);
  assert.match(approval, /mapfile -t SKILL_PATHS/);
  assert.match(approval, /Refusing to overwrite existing published target/);
  assert.match(approval, /git diff --quiet "\$MERGE_COMMIT_SHA" HEAD -- "\$PENDING_DIR"/);
  assert.match(approval, /PUSHED=false/);
  assert.match(approval, /test "\$PUSHED" = true/);
  assert.doesNotMatch(approval, /cherry-pick HEAD@\{1\} \|\| true/);
  assert.doesNotMatch(approval, /find pending/);
  assert.doesNotMatch(approval, /rm -rf "\$TARGET_DIR"/);
});
