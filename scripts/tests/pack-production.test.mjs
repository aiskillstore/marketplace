import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  chmodSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildApiEvaluation,
  buildPublicReadbackExpectation,
  buildSloResult,
  canonicalJson,
  readExactPublicPack,
  validatePublicPackReadback,
} from '../pack-production.mjs';

const PACK_PRODUCTION = fileURLToPath(new URL('../pack-production.mjs', import.meta.url));

function cliReport() {
  const summary = {
    runs: 3,
    scores: [8, 8, 9],
    medianScore: 8,
    usedSkillRate: 1,
    passed: true,
    envBlockedRate: 0,
    envBlocked: false,
    usedSkillEver: true,
    taskCompletedRate: 1,
    taskCompletedEver: true,
    taskCompletedThreshold: 1,
    artifactPassRate: 1,
    artifactThreshold: 1,
    artifactsRequired: true,
    artifactsPassed: true,
  };
  return {
    schemaVersion: 'pack-generation-evaluation/v2',
    generationId: 'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0',
    evaluationStartedAt: '2026-07-15T10:00:00.000Z',
    evaluationCompletedAt: '2026-07-15T10:30:00.000Z',
    outcome: 'candidate_ready',
    outcomeReason: 'passed',
    autoPublishEligible: true,
    scenario: {
      id: 'excel-dashboard',
      slug: 'monthly-sales-excel-workbook',
      name: 'Monthly Sales Excel Dashboard',
      version: '1.0.0',
      tags: ['excel', 'dashboard'],
      keywords: ['xlsx'],
      task: 'Create a real workbook.',
      capabilitySlots: [{ id: 'workbook', required: true }],
      requiredArtifacts: [{ id: 'workbook', extensions: ['.xlsx'], minimumCount: 1 }],
    },
    slotEvaluations: [],
    manifest: {
      name: 'Monthly Sales Excel Dashboard',
      slug: 'monthly-sales-excel-workbook',
      description: 'A verified real workbook.',
      scenario_tags: ['excel', 'dashboard'],
      risk_flags: [],
      skills: ['spreadsheet-skill'],
      slot_assignments: { workbook: ['spreadsheet-skill'] },
      rationale: 'The skill created and validated the workbook.',
    },
    composition: { attempts: 1, fallbackUsed: false, errors: [] },
    packVerification: {
      summary,
      verdicts: [
        { used_skill: true, task_completed: true, score: 8, reason: 'complete', issues: [] },
        { used_skill: true, task_completed: true, score: 8, reason: 'complete', issues: [] },
        { used_skill: true, task_completed: true, score: 9, reason: 'excellent', issues: [] },
      ],
      artifactEvidence: [{
        run: 1,
        passed: true,
        requirements: [{ validMatches: ['sales.xlsx'] }],
        artifacts: [],
      }],
      errors: [],
    },
    baselineVerification: {
      summary: { ...summary, scores: [4, 4, 5], medianScore: 4, passed: false, usedSkillRate: 0, usedSkillEver: false, artifactPassRate: 0, artifactsPassed: false },
      verdicts: [],
      artifactEvidence: [],
      errors: [],
    },
    baselineScoreDelta: 4,
    errors: [],
  };
}

const context = {
  generationId: 'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0',
  scenarioId: 'excel-dashboard',
  runId: '123456789',
  runAttempt: 1,
  commitSha: 'a'.repeat(40),
  cliVersion: '2.9.0',
  cliSha256: 'b'.repeat(64),
  model: 'sonnet',
  judgeModel: 'gpt-5.5',
};

function verificationFixture() {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-verify-'));
  const cli = join(directory, 'skillstore-cli');
  writeFileSync(cli, '#!/bin/sh\necho "skillstore-cli 2.9.0"\n');
  chmodSync(cli, 0o755);
  const cliSha256 = createHash('sha256').update(readFileSync(cli)).digest('hex');
  const report = cliReport();
  const fixtureContext = { ...context, cliSha256 };
  const evaluation = buildApiEvaluation(report, fixtureContext);
  const prefix = '01-excel-dashboard';
  writeFileSync(join(directory, 'plan.json'), `${JSON.stringify({
    schemaVersion: 'pack-production-queue/v1',
    scenarios: [report.scenario],
  })}\n`);
  writeFileSync(join(directory, `${prefix}.stdout.json`), `${JSON.stringify(report)}\n`);
  writeFileSync(join(directory, `${prefix}.evaluation.json`), `${JSON.stringify(evaluation)}\n`);
  writeFileSync(join(directory, 'evaluate-summary.json'), `${JSON.stringify({
    schemaVersion: 'marketplace.pack-production-evaluate/v1',
    cliVersion: '2.9.0',
    cliSha256,
    reports: [{
      scenarioId: report.scenario.id,
      generationId: report.generationId,
      outcome: report.outcome,
      outcomeReason: report.outcomeReason,
      file: `/var/lib/pack-evaluator/results/${prefix}.evaluation.json`,
    }],
    selectedGenerationId: report.generationId,
  })}\n`);
  return { directory, cli, evaluationFile: join(directory, `${prefix}.evaluation.json`) };
}

function runVerification(fixture) {
  return spawnSync(process.execPath, [
    PACK_PRODUCTION,
    'verify',
    '--plan', join(fixture.directory, 'plan.json'),
    '--results-dir', fixture.directory,
    '--cli', fixture.cli,
    '--expected-cli-version', '2.9.0',
    '--run-id', context.runId,
    '--run-attempt', String(context.runAttempt),
    '--commit-sha', context.commitSha,
    '--model', context.model,
    '--judge-model', context.judgeModel,
  ], { encoding: 'utf8' });
}

test('canonical JSON is stable across object key order', () => {
  assert.equal(canonicalJson({ z: 1, a: { y: 2, x: 3 } }), canonicalJson({ a: { x: 3, y: 2 }, z: 1 }));
});

test('adapter binds workflow identity, artifact evidence, baseline, and digest', () => {
  const evaluation = buildApiEvaluation(cliReport(), context);
  assert.equal(evaluation.schemaVersion, 'skillstore.pack-evaluation/v2');
  assert.equal(evaluation.workflow.runId, '123456789');
  assert.equal(evaluation.scenario.version, '1.0.0');
  assert.deepEqual(evaluation.candidate.fitness.artifact.references, ['sales.xlsx']);
  assert.equal(evaluation.candidate.fitness.baseline.improvement, 4);
  assert.match(evaluation.evidenceDigest, /^[0-9a-f]{64}$/);
  assert.equal(evaluation.evidence.cliReport.schemaVersion, 'pack-generation-evaluation/v2');
});

test('adapter rejects an exit artifact whose scenario differs from the immutable plan', () => {
  const report = cliReport();
  report.scenario.id = 'different-scenario';
  assert.throws(() => buildApiEvaluation(report, context), /scenario differs/);
});

test('quality rejections persist without a candidate object', () => {
  const report = cliReport();
  report.outcome = 'quality_rejected';
  report.manifest = null;
  report.packVerification = null;
  report.baselineVerification = null;
  const evaluation = buildApiEvaluation(report, context);
  assert.equal(evaluation.outcome, 'quality_rejected');
  assert.equal(evaluation.candidate, null);
});

test('finalize binds public readback to the selected Pack and candidate Skill order', () => {
  const request = buildApiEvaluation(cliReport(), context);
  const selected = {
    generationId: request.generationId,
    pack: { id: 'pack-123', slug: request.scenario.slug },
  };
  const expectation = buildPublicReadbackExpectation({
    persisted: [{ request }],
  }, selected, 'monthly-sales-excel-workbook');

  assert.deepEqual(expectation, {
    generationId: request.generationId,
    packId: 'pack-123',
    publicSlug: 'monthly-sales-excel-workbook',
    skillSlugs: ['spreadsheet-skill'],
  });
});

test('exact public readback uses the camelCase API contract and no-cache request', async () => {
  const expected = {
    generationId: context.generationId,
    packId: 'pack-123',
    publicSlug: 'monthly-sales-excel-workbook',
    skillSlugs: ['spreadsheet-skill', 'artifact-validator'],
  };
  let observed;
  const result = await readExactPublicPack('https://skillstore.example', expected, async (url, options) => {
    observed = { url, options };
    return new Response(JSON.stringify({
      data: {
        id: 'pack-123',
        slug: 'monthly-sales-excel-workbook',
        reviewStatus: 'approved',
        skills: [{ slug: 'spreadsheet-skill' }, { slug: 'artifact-validator' }],
      },
    }), { status: 200, headers: { 'content-type': 'application/json' } });
  });

  assert.equal(
    observed.url,
    'https://skillstore.example/api/packs/monthly-sales-excel-workbook?lang=en',
  );
  assert.equal(observed.options.headers['Cache-Control'], 'no-cache');
  assert.equal(result.pack.id, 'pack-123');
  assert.deepEqual(result.mismatches, []);
});

test('exact public readback rejects wrong identity, snake_case status, and changed Skills', () => {
  const result = validatePublicPackReadback({
    id: 'other-pack',
    slug: 'other-slug',
    review_status: 'approved',
    skills: [{ slug: 'artifact-validator' }, { slug: 'spreadsheet-skill' }],
  }, {
    packId: 'pack-123',
    publicSlug: 'monthly-sales-excel-workbook',
    skillSlugs: ['spreadsheet-skill', 'artifact-validator'],
  });

  assert.equal(result.matched, false);
  assert.match(result.mismatches.join('\n'), /Pack id mismatch/);
  assert.match(result.mismatches.join('\n'), /Pack slug mismatch/);
  assert.match(result.mismatches.join('\n'), /reviewStatus is missing/);
  assert.match(result.mismatches.join('\n'), /Pack Skill slugs mismatch/);
});

test('terminal SLO evidence is fixed to seven days and internally consistent', () => {
  const result = buildSloResult({
    windowDays: 7,
    windowStartedAt: '2026-07-09T00:00:00.000Z',
    target: 2,
    publishedReadbackPassed: 1,
    met: false,
  }, '2026-07-16T00:00:00.000Z');

  assert.deepEqual(result, {
    schemaVersion: 'marketplace.pack-production-slo/v1',
    checkedAt: '2026-07-16T00:00:00.000Z',
    windowDays: 7,
    windowStartedAt: '2026-07-09T00:00:00.000Z',
    target: 2,
    publishedReadbackPassed: 1,
    met: false,
  });
  assert.throws(() => buildSloResult({ ...result, met: true }), /met flag is inconsistent/);
  assert.throws(() => buildSloResult({ ...result, windowDays: 30 }), /must be 7 days/);
  assert.throws(() => buildSloResult({ ...result, target: 1, met: true }), /target must be 2/);
});

test('trusted verification accepts only the exact reconstructed evaluation closure', () => {
  const fixture = verificationFixture();
  const result = runVerification(fixture);
  assert.equal(result.status, 0, result.stderr);
  const verification = JSON.parse(readFileSync(join(fixture.directory, 'evaluation-verification.json'), 'utf8'));
  assert.equal(verification.schemaVersion, 'marketplace.pack-production-evaluation-verification/v1');
  assert.deepEqual(verification.files.map((entry) => entry.file), ['01-excel-dashboard.evaluation.json']);
});

test('trusted verification rejects an injected evaluation file', () => {
  const fixture = verificationFixture();
  writeFileSync(join(fixture.directory, '00-injected.evaluation.json'), '{}\n');
  const result = runVerification(fixture);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /not the exact trusted closure/);
});

test('trusted verification rejects a tampered otherwise-valid evaluation', () => {
  const fixture = verificationFixture();
  const evaluation = JSON.parse(readFileSync(fixture.evaluationFile, 'utf8'));
  evaluation.candidate.fitness.score = 10;
  writeFileSync(fixture.evaluationFile, `${JSON.stringify(evaluation)}\n`);
  const result = runVerification(fixture);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /differs from trusted reconstruction/);
});
