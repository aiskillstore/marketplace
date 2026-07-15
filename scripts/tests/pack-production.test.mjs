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
  allocateScenarioBudgetMs,
  buildApiEvaluation,
  buildPublicReadbackExpectation,
  buildSloResult,
  canonicalJson,
  isSafeEvaluatorProgressLine,
  normalizeEvaluatorProgressLine,
  readExactPublicPack,
  runEvaluatorProcess,
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
    usedSkills: ['spreadsheet-skill', 'workbook-validator'],
    minimumDistinctSkillsUsed: 2,
    distinctSkillUseRate: 1,
    minimumScore: 8,
    minimumRunScore: 7,
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
      capabilitySlots: [{ id: 'workbook', required: true }, { id: 'validation', required: true }],
      requiredArtifacts: [{ id: 'workbook', extensions: ['.xlsx'], minimumCount: 1 }],
    },
    slotEvaluations: [],
    manifest: {
      name: 'Monthly Sales Excel Dashboard',
      slug: 'monthly-sales-excel-workbook',
      description: 'A verified real workbook.',
      scenario_tags: ['excel', 'dashboard'],
      risk_flags: [],
      skills: ['spreadsheet-skill', 'workbook-validator'],
      slot_assignments: { workbook: ['spreadsheet-skill'], validation: ['workbook-validator'] },
      rationale: 'One Skill created the workbook and another validated it.',
    },
    composition: { attempts: 1, fallbackUsed: false, errors: [] },
    packVerification: {
      summary,
      verdicts: [
        { used_skill: true, used_skills: ['spreadsheet-skill', 'workbook-validator'], task_completed: true, artifact_requirements_met: true, env_blocked: false, score: 8, reason: 'complete', issues: [] },
        { used_skill: true, used_skills: ['spreadsheet-skill', 'workbook-validator'], task_completed: true, artifact_requirements_met: true, env_blocked: false, score: 8, reason: 'complete', issues: [] },
        { used_skill: true, used_skills: ['spreadsheet-skill', 'workbook-validator'], task_completed: true, artifact_requirements_met: true, env_blocked: false, score: 9, reason: 'excellent', issues: [] },
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
  cliVersion: '2.10.0',
  cliSha256: 'b'.repeat(64),
  model: 'sonnet',
  judgeModel: 'gpt-5.5',
};

function verificationFixture() {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-verify-'));
  const cli = join(directory, 'skillstore-cli');
  writeFileSync(cli, '#!/bin/sh\necho "skillstore-cli 2.10.0"\n');
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
    cliVersion: '2.10.0',
    cliSha256,
    attempts: [{
      planIndex: 0,
      scenarioId: report.scenario.id,
      generationId: report.generationId,
      status: 'completed',
      outcome: report.outcome,
      durationMs: 1,
    }],
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
    '--expected-cli-version', '2.10.0',
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

test('async evaluator streams only allowlisted progress and persists heartbeat evidence', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-progress-'));
  const stdoutFile = join(directory, 'stdout.json');
  const stderrFile = join(directory, 'run.log');
  const progressFile = join(directory, 'progress.ndjson');
  const messages = [];
  const childScript = [
    "process.stderr.write('[1/5] scenario excel-dashboard@1.1.0: Excel dashboard\\n')",
    "process.stderr.write('run 1/1: executing task...\\n')",
    "process.stderr.write('do-not-forward arbitrary child output\\n')",
    "setTimeout(() => process.stdout.write('{\\\"outcome\\\":\\\"quality_rejected\\\"}\\n'), 35)",
  ].join(';');
  const result = await runEvaluatorProcess(process.execPath, ['-e', childScript], {
    cwd: directory,
    env: process.env,
    stdoutFile,
    stderrFile,
    progressFile,
    checkpointFile: join(directory, 'checkpoint.json'),
    label: 'excel-dashboard',
    generationId: context.generationId,
    scenarioIndex: 1,
    scenarioCount: 1,
    heartbeatMs: 10,
    timeoutMs: 1_000,
    killGraceMs: 100,
    onProgress: (message) => messages.push(message),
  });

  assert.equal(result.status, 0);
  assert.equal(result.timedOut, false);
  assert.match(readFileSync(stdoutFile, 'utf8'), /quality_rejected/);
  assert.match(readFileSync(stderrFile, 'utf8'), /\[1\/5\] scenario/);
  assert.doesNotMatch(readFileSync(stderrFile, 'utf8'), /do-not-forward arbitrary child output/);
  assert.ok(messages.some((message) => message.includes('[1/5] scenario')));
  assert.ok(messages.some((message) => message.includes('heartbeat')));
  assert.ok(messages.every((message) => !message.includes('do-not-forward')));
  const events = readFileSync(progressFile, 'utf8').trim().split('\n').map(JSON.parse);
  assert.deepEqual(events.map((event) => event.seq), events.map((_, index) => index + 1));
  assert.ok(events.some((event) => event.event === 'scenario.started'));
  assert.ok(events.some((event) => event.event === 'scenario.progress'));
  assert.ok(events.some((event) => event.event === 'scenario.heartbeat'));
  assert.ok(events.some((event) => event.event === 'scenario.process_exited'));
  assert.equal(
    JSON.parse(readFileSync(join(directory, 'checkpoint.json'), 'utf8')).event,
    'scenario.process_exited',
  );
  assert.equal(isSafeEvaluatorProgressLine('arbitrary child output'), false);
  assert.equal(
    normalizeEvaluatorProgressLine(
      '[1/5] scenario excel-dashboard@1.1.0: deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
    ),
    '[1/5] scenario excel-dashboard@1.1.0',
  );
});

test('async evaluator bounds a hung child and records the timeout terminal signal', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-timeout-'));
  const progressFile = join(directory, 'progress.ndjson');
  const result = await runEvaluatorProcess(
    process.execPath,
    ['-e', 'setInterval(() => {}, 1000)'],
    {
      cwd: directory,
      env: process.env,
      stdoutFile: join(directory, 'stdout.json'),
      stderrFile: join(directory, 'run.log'),
      progressFile,
      label: 'excel-dashboard',
      heartbeatMs: 10,
      timeoutMs: 30,
      killGraceMs: 100,
      onProgress: () => {},
    },
  );

  assert.equal(result.timedOut, true);
  assert.equal(result.signal, 'SIGTERM');
  const events = readFileSync(progressFile, 'utf8').trim().split('\n').map(JSON.parse);
  assert.ok(events.some((event) => event.event === 'scenario.timeout'));
  assert.ok(events.some((event) => event.event === 'scenario.process_exited' && event.timedOut));
});

test('scenario budgets reserve real execution time for the fallback queue', () => {
  assert.equal(allocateScenarioBudgetMs({
    remainingBudgetMs: 13_800_000,
    remainingScenarios: 3,
    maxScenarioMs: 7_200_000,
    minimumFallbackMs: 2_700_000,
  }), 7_200_000);
  assert.equal(allocateScenarioBudgetMs({
    remainingBudgetMs: 6_600_000,
    remainingScenarios: 2,
    maxScenarioMs: 7_200_000,
    minimumFallbackMs: 2_700_000,
  }), 3_900_000);
  assert.equal(allocateScenarioBudgetMs({
    remainingBudgetMs: 2_700_000,
    remainingScenarios: 1,
    maxScenarioMs: 7_200_000,
    minimumFallbackMs: 2_700_000,
  }), 2_700_000);
});

test('a timed-out scenario keeps later evidence diagnostic-only and blocks workflow success', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-fallback-'));
  const cli = join(directory, 'fake-skillstore-cli');
  const scenarios = {
    slow: {
      id: 'slow', version: '1.0.0', slug: 'slow-pack', name: 'Slow Pack',
      task: 'Create a slow artifact.', tags: ['slow'], keywords: ['slow'],
      capabilitySlots: [{ id: 'artifact', required: true }],
      requiredArtifacts: [{ id: 'artifact', extensions: ['.txt'], minimumCount: 1 }],
    },
    fast: {
      id: 'fast', version: '1.0.0', slug: 'fast-pack', name: 'Fast Pack',
      task: 'Create a fast artifact.', tags: ['fast'], keywords: ['fast'],
      capabilitySlots: [{ id: 'artifact', required: true }],
      requiredArtifacts: [{ id: 'artifact', extensions: ['.txt'], minimumCount: 1 }],
    },
  };
  const script = `#!/usr/bin/env node
const args = process.argv.slice(2);
if (args.includes('--version')) { console.log('skillstore-cli 2.10.0'); process.exit(0); }
const value = (name) => args[args.indexOf(name) + 1];
const scenarioId = value('--scenario');
if (scenarioId === 'slow') {
  setInterval(() => {}, 1000);
} else {
  const scenarios = ${JSON.stringify(scenarios)};
  const now = new Date().toISOString();
  process.stdout.write(JSON.stringify({
    schemaVersion: 'pack-generation-evaluation/v2',
    generationId: value('--generation-id'),
    evaluationStartedAt: now,
    evaluationCompletedAt: now,
    outcome: 'quality_rejected',
    outcomeReason: 'fixture rejection',
    autoPublishEligible: false,
    scenario: scenarios[scenarioId],
    slotEvaluations: [],
    manifest: null,
    composition: null,
    packVerification: null,
    baselineVerification: null,
    baselineScoreDelta: null,
    errors: [],
  }));
  process.exit(10);
}
`;
  writeFileSync(cli, script);
  chmodSync(cli, 0o755);
  const planFile = join(directory, 'plan.json');
  const resultsDir = join(directory, 'results');
  writeFileSync(planFile, `${JSON.stringify({
    schemaVersion: 'pack-production-queue/v1',
    scenarios: [scenarios.slow, scenarios.fast],
  })}\n`);

  const common = [
    '--plan', planFile,
    '--results-dir', resultsDir,
    '--cli', cli,
    '--expected-cli-version', '2.10.0',
    '--skills-dir', directory,
    '--run-id', context.runId,
    '--run-attempt', String(context.runAttempt),
    '--commit-sha', context.commitSha,
    '--model', context.model,
    '--judge-model', context.judgeModel,
  ];
  const evaluation = spawnSync(process.execPath, [
    PACK_PRODUCTION, 'evaluate', ...common,
    '--evaluation-budget-ms', '2000',
    '--scenario-timeout-ms', '500',
    '--minimum-fallback-ms', '500',
  ], { encoding: 'utf8', timeout: 5_000 });
  assert.equal(evaluation.status, 1);
  assert.match(evaluation.stderr, /operationally incomplete attempts: slow:timed_out/);

  const summary = JSON.parse(readFileSync(join(resultsDir, 'evaluate-summary.json'), 'utf8'));
  assert.deepEqual(summary.attempts.map((attempt) => attempt.status), ['timed_out', 'completed']);
  assert.equal(summary.reports[0].planIndex, 1);
  assert.equal(summary.reports[0].scenarioId, 'fast');
  assert.equal(readFileSync(join(resultsDir, '01-slow.run.log'), 'utf8'), '');
  assert.throws(() => readFileSync(join(resultsDir, '01-slow.evaluation.json')));

  const verification = spawnSync(process.execPath, [PACK_PRODUCTION, 'verify', ...common], {
    encoding: 'utf8',
    timeout: 5_000,
  });
  assert.notEqual(verification.status, 0);
  assert.match(verification.stderr, /operationally incomplete attempts: slow:timed_out/);
  assert.throws(() => readFileSync(join(resultsDir, 'evaluation-verification.json')));
});

test('adapter binds workflow identity, artifact evidence, baseline, and digest', () => {
  const evaluation = buildApiEvaluation(cliReport(), context);
  assert.equal(evaluation.schemaVersion, 'skillstore.pack-evaluation/v3');
  assert.equal(evaluation.workflow.runId, '123456789');
  assert.equal(evaluation.scenario.version, '1.0.0');
  assert.deepEqual(evaluation.scenario.requiredCapabilitySlots, ['workbook', 'validation']);
  assert.deepEqual(evaluation.candidate.manifest.slotAssignments, {
    workbook: ['spreadsheet-skill'],
    validation: ['workbook-validator'],
  });
  assert.deepEqual(evaluation.candidate.fitness.artifact.references, ['sales.xlsx']);
  assert.deepEqual(evaluation.candidate.fitness.usedSkills, ['spreadsheet-skill', 'workbook-validator']);
  assert.equal(evaluation.candidate.fitness.minimumDistinctSkillsUsed, 2);
  assert.equal(evaluation.candidate.fitness.distinctSkillUseRate, 1);
  assert.equal(evaluation.candidate.fitness.minimumScore, 8);
  assert.equal(evaluation.candidate.fitness.minimumRunScore, 7);
  assert.deepEqual(evaluation.candidate.fitness.baseline, {
    runs: 3,
    scores: [4, 4, 5],
    score: 4,
    improvement: 4,
    errors: [],
  });
  assert.deepEqual(evaluation.candidate.fitness.verdicts[0].usedSkills, ['spreadsheet-skill', 'workbook-validator']);
  assert.equal(evaluation.candidate.fitness.verdicts[0].artifactVerified, true);
  assert.match(evaluation.evidenceDigest, /^[0-9a-f]{64}$/);
  assert.equal(evaluation.evidence.cliReport.schemaVersion, 'pack-generation-evaluation/v2');
});

test('adapter rejects one-Skill or incomplete candidate_ready evidence before persistence', () => {
  const oneSkill = cliReport();
  oneSkill.manifest.skills = ['spreadsheet-skill'];
  assert.throws(() => buildApiEvaluation(oneSkill, context), /at least two distinct manifest Skills/);

  const incomplete = cliReport();
  incomplete.packVerification.verdicts[1].artifact_requirements_met = false;
  assert.throws(() => buildApiEvaluation(incomplete, context), /did not pass the task, artifact, environment, and score gates/);

  const invented = cliReport();
  invented.packVerification.verdicts[1].used_skills = ['spreadsheet-skill', 'invented-skill'];
  assert.throws(() => buildApiEvaluation(invented, context), /outside the manifest/);

  const missingSlot = cliReport();
  delete missingSlot.manifest.slot_assignments.validation;
  assert.throws(() => buildApiEvaluation(missingSlot, context), /required slot validation is not assigned/);

  const extraSlot = cliReport();
  extraSlot.manifest.slot_assignments.unplanned = ['spreadsheet-skill'];
  assert.throws(() => buildApiEvaluation(extraSlot, context), /non-required capability slot assignments/);

  const inconsistentSummary = cliReport();
  inconsistentSummary.packVerification.summary.usedSkills = ['spreadsheet-skill'];
  assert.throws(() => buildApiEvaluation(inconsistentSummary, context), /summary usedSkills differs/);

  const incompleteBaseline = cliReport();
  incompleteBaseline.baselineVerification.summary.runs = 2;
  incompleteBaseline.baselineVerification.summary.scores = [4, 5];
  assert.throws(() => buildApiEvaluation(incompleteBaseline, context), /baseline lacks exactly three valid run scores/);
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
    skillSlugs: ['spreadsheet-skill', 'workbook-validator'],
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
