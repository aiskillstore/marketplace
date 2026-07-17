import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:http';
import {
  accessSync,
  constants,
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  allocateScenarioBudgetMs,
  buildApiEvaluation,
  buildHardDisabledReviewPendingResult,
  buildInfrastructureCliReport,
  buildPublicReadbackExpectation,
  buildSafeCliEvidence,
  buildSloResult,
  canonicalJson,
  deterministicHttpFailureFromActivity,
  exactExecutorPreflightClosure,
  isSafeEvaluatorProgressLine,
  normalizeEvaluatorProgressLine,
  normalizeInfrastructureFailure,
  planTrustedPersistence,
  prepareScenarioRuntime,
  projectExecutorPreflightEvidence,
  readExactPublicPack,
  runEvaluatorProcess,
  validateCandidateNullPersistResponse,
  validateCurrentContentDispatchNonce,
  validateImmutableProductionPlan,
  validatePublicPackReadback,
} from '../pack-production.mjs';

const PACK_PRODUCTION = fileURLToPath(new URL('../pack-production.mjs', import.meta.url));
const PACK_PRODUCTION_URL = new URL('../pack-production.mjs', import.meta.url).href;
const V4_GOLDEN = fileURLToPath(new URL('./fixtures/pack-production-evaluation-v4.golden.json', import.meta.url));

test('automatic publication is hard-disabled even when explicitly requested', () => {
  const selected = {
    generationId: 'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0',
    pack: { id: 'pack-123', slug: 'staging-pack' },
  };
  assert.deepEqual(buildHardDisabledReviewPendingResult(selected, true), {
    outcome: 'review_pending',
    generationId: selected.generationId,
    pack: selected.pack,
    reason: 'automatic publish was disabled for this run',
    autoPublishRequested: true,
    publicationMode: 'manual_only',
  });
  assert.equal(buildHardDisabledReviewPendingResult(selected, false).autoPublishRequested, false);
});

export function cliReport() {
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
  const nodes = [
    { id: 'workbook', instruction: 'Create the workbook.', depends_on: [], artifact_ids: ['workbook'] },
    { id: 'validation', instruction: 'Validate the workbook.', depends_on: ['workbook'], artifact_ids: ['validation-report'] },
  ];
  const handoffs = [{
    from: 'workbook',
    to: 'validation',
    artifact_ids: ['workbook'],
    contract: 'validated-artifacts-only',
  }];
  const workflowDigest = createHash('sha256').update(canonicalJson({
    schema_version: 'skillstore.pack-execution-dag/v1',
    nodes,
    handoffs,
  })).digest('hex');
  const skillBindings = [
    { canonical_id: 'spreadsheet-skill', content_hash: '1'.repeat(64), version: '1.0.0', slot_ids: ['workbook'] },
    { canonical_id: 'workbook-validator', content_hash: '2'.repeat(64), version: '2.0.0', slot_ids: ['validation'] },
  ];
  const bindingDigest = createHash('sha256').update(canonicalJson({
    workflow_digest: workflowDigest,
    skill_bindings: skillBindings,
  })).digest('hex');
  const variants = ['public-variant', 'hidden-variant-a', 'hidden-variant-b'];
  const deterministicValidations = variants.map((variantId, index) => ({
    variantId,
    visibility: index === 0 ? 'public' : 'hidden',
    passed: true,
    slotPasses: { workbook: true, validation: true },
    taskDigest: '3'.repeat(64),
    fixtureDigest: String(6 + index).repeat(64),
    validatorDigest: '9'.repeat(64),
  }));
  const usageTraces = variants.map((variantId) => ({
    variantId,
    events: skillBindings.map((binding, index) => ({
      canonicalId: binding.canonical_id,
      contentHash: binding.content_hash,
      version: binding.version,
      sequence: index + 1,
    })),
  }));
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
      requiredArtifacts: [
        { id: 'workbook', extensions: ['.xlsx'], minimumCount: 1 },
        { id: 'validation-report', extensions: ['.json'], minimumCount: 1 },
      ],
    },
    slotEvaluations: [
      {
        slot: { id: 'workbook', required: true },
        candidates: [{ slug: 'spreadsheet-skill', summary, verdicts: [], errors: [] }],
        eligible: [{ slug: 'spreadsheet-skill' }],
        winner: { slug: 'spreadsheet-skill' },
      },
      {
        slot: { id: 'validation', required: true },
        candidates: [{ slug: 'workbook-validator', summary, verdicts: [], errors: [] }],
        eligible: [{ slug: 'workbook-validator' }],
        winner: { slug: 'workbook-validator' },
      },
    ],
    manifest: {
      name: 'Monthly Sales Excel Dashboard',
      slug: 'monthly-sales-excel-workbook',
      description: 'A verified real workbook.',
      scenario_tags: ['excel', 'dashboard'],
      risk_flags: [],
      skills: ['spreadsheet-skill', 'workbook-validator'],
      slot_assignments: { workbook: ['spreadsheet-skill'], validation: ['workbook-validator'] },
      execution_dag: {
        schema_version: 'skillstore.pack-execution-dag/v1',
        workflow_digest: workflowDigest,
        binding_digest: bindingDigest,
        nodes,
        handoffs,
        skill_bindings: skillBindings,
        usage_guide_marker: `<!-- skillstore-execution-binding:${bindingDigest} -->`,
      },
      rationale: 'One Skill created the workbook and another validated it.',
    },
    composition: { attempts: 1, fallbackUsed: false, errors: [] },
    packVerification: {
      workflowDigest,
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
      deterministicValidations,
      errors: [],
    },
    baselineVerification: {
      workflowDigest,
      summary: { ...summary, scores: [4, 4, 5], medianScore: 4, passed: false, usedSkillRate: 0, usedSkillEver: false, artifactPassRate: 0, artifactsPassed: false },
      verdicts: [],
      artifactEvidence: [],
      errors: [],
    },
    baselineScoreDelta: 4,
    bestSingleEvidence: {
      eligibleCandidateSkills: ['spreadsheet-skill', 'workbook-validator'],
      competitors: [
        {
          skill: 'spreadsheet-skill',
          contentHash: '1'.repeat(64),
          version: '1.0.0',
          workflowDigest,
          verification: {
            summary: { ...summary, scores: [6, 6, 7], medianScore: 6, minimumScore: 6 },
            artifactEvidence: [true, false, false].map((passed) => ({ passed })),
            deterministicValidations,
            errors: [],
          },
          deterministicPassCount: 3,
          artifactPassCount: 1,
        },
        {
          skill: 'workbook-validator',
          contentHash: '2'.repeat(64),
          version: '2.0.0',
          workflowDigest,
          verification: {
            summary: { ...summary, scores: [5, 5, 6], medianScore: 5, minimumScore: 5 },
            artifactEvidence: [false, false, false].map((passed) => ({ passed })),
            deterministicValidations: deterministicValidations.map((validation, index) => ({
              ...validation,
              passed: index < 2,
            })),
            errors: [],
          },
          deterministicPassCount: 2,
          artifactPassCount: 0,
        },
      ],
      winnerSkill: 'spreadsheet-skill',
      complete: true,
    },
    bestSingleScoreDelta: 2,
    treatmentWorkflowDigests: {
      fullPack: workflowDigest,
      planOnly: workflowDigest,
      bestSingle: [
        { skill: 'spreadsheet-skill', workflowDigest },
        { skill: 'workbook-validator', workflowDigest },
      ],
      leaveOneOut: [
        { removedSkill: 'spreadsheet-skill', workflowDigest },
        { removedSkill: 'workbook-validator', workflowDigest },
      ],
    },
    ablationVerification: [
      {
        removedSkill: 'spreadsheet-skill',
        workflowDigest,
        remainingSkills: ['workbook-validator'],
        boundSlotIds: ['workbook'],
        boundArtifactIds: ['workbook'],
        fullSlotPasses: [true, true, true],
        ablatedSlotPasses: [false, false, false],
        fullArtifactPasses: [true, true, true],
        ablatedArtifactPasses: [false, false, false],
        deterministicMarginalContribution: true,
        verification: { workflowDigest },
      },
      {
        removedSkill: 'workbook-validator',
        workflowDigest,
        remainingSkills: ['spreadsheet-skill'],
        boundSlotIds: ['validation'],
        boundArtifactIds: ['validation-report'],
        fullSlotPasses: [true, true, true],
        ablatedSlotPasses: [false, false, false],
        fullArtifactPasses: [true, true, true],
        ablatedArtifactPasses: [false, false, false],
        deterministicMarginalContribution: true,
        verification: { workflowDigest },
      },
    ],
    deterministicMarginalSkills: ['spreadsheet-skill', 'workbook-validator'],
    evaluationSuiteEvidence: {
      schemaVersion: 'skillstore.pack-evaluation-suite/v1',
      executed: true,
      variantIds: variants,
      hiddenVariantCount: 2,
      taskDigests: ['3'.repeat(64), '3'.repeat(64), '3'.repeat(64)],
      fixtureDigests: ['6'.repeat(64), '7'.repeat(64), '8'.repeat(64)],
      validatorDigests: ['9'.repeat(64), '9'.repeat(64), '9'.repeat(64)],
    },
    usageProvenance: {
      deterministic: true,
      source: 'runner-trace-v1',
      traces: usageTraces,
    },
    errors: [],
  };
}

export const context = {
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

function immutableProductionPlan(scenario, generationId = context.generationId) {
  return {
    schemaVersion: 'pack-production-queue/v1',
    source: 'signals',
    scenarios: [{ ...scenario, generationId }],
    workflowBinding: {
      repository: 'aiskillstore/marketplace',
      workflow: 'Generate Pack',
      runId: context.runId,
      runAttempt: context.runAttempt,
      commitSha: context.commitSha,
      scenarioId: scenario.id,
    },
  };
}

const workflowArgs = {
  'run-id': context.runId,
  'run-attempt': String(context.runAttempt),
  'commit-sha': context.commitSha,
};

function verificationFixture(report = cliReport()) {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-verify-'));
  const cli = join(directory, 'skillstore-cli');
  writeFileSync(cli, '#!/bin/sh\necho "skillstore-cli 2.10.0"\n');
  chmodSync(cli, 0o755);
  const cliSha256 = createHash('sha256').update(readFileSync(cli)).digest('hex');
  const fixtureContext = { ...context, cliSha256 };
  const evaluation = buildApiEvaluation(report, fixtureContext);
  const prefix = '01-excel-dashboard';
  writeFileSync(join(directory, 'plan.json'), `${JSON.stringify(
    immutableProductionPlan(report.scenario, report.generationId),
  )}\n`);
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
      planIndex: 0,
      scenarioId: report.scenario.id,
      generationId: report.generationId,
      outcome: report.outcome,
      outcomeCategory: 'passed',
      outcomeReasonSha256: createHash('sha256').update(report.outcomeReason).digest('hex'),
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

test('immutable production plan binds one generation id to the exact workflow invocation', () => {
  const report = cliReport();
  const plan = immutableProductionPlan(report.scenario, report.generationId);
  assert.equal(validateImmutableProductionPlan(plan, workflowArgs).generationId, report.generationId);
  assert.throws(
    () => validateImmutableProductionPlan({
      ...plan,
      scenarios: [{ ...plan.scenarios[0], generationId: undefined }],
    }, workflowArgs),
    /generation id is invalid/,
  );
  assert.throws(
    () => validateImmutableProductionPlan({
      ...plan,
      workflowBinding: { ...plan.workflowBinding, runAttempt: 2 },
    }, workflowArgs),
    /differs from this workflow invocation/,
  );
  assert.throws(
    () => validateImmutableProductionPlan({
      ...plan,
      workflowBinding: { ...plan.workflowBinding, injected: true },
    }, workflowArgs),
    /unexpected fields/,
  );
});

test('v4 causal stages are allowlisted as bounded evaluator progress', () => {
  assert.equal(
    normalizeEvaluatorProgressLine('[5/6] running 3-run plan-only baseline with the identical DAG'),
    '[5/6] running 3-run plan-only baseline',
  );
  assert.equal(
    normalizeEvaluatorProgressLine('[6/7] running every viable unique finalist end-to-end for the true best-single baseline'),
    '[6/7] running true best-single tournament',
  );
  assert.equal(
    normalizeEvaluatorProgressLine('[7/7] running one leave-one-out comparison for each of 4 members'),
    '[7/7] running 4 leave-one-out comparisons',
  );
  assert.equal(
    normalizeEvaluatorProgressLine('      slot workbook: winner spreadsheet-skill after evaluating all 2 bounded candidates'),
    'slot workbook: winner spreadsheet-skill after 2 candidates',
  );
});

test('deterministic HTTP activity is scoped to exact inference paths', () => {
  const retryable = [408, 425, 429, 500, 503]
    .map((status) => JSON.stringify({ phase: 'response', path: '/v1/messages', status }))
    .join('\n');
  assert.equal(deterministicHttpFailureFromActivity(retryable), null);
  assert.equal(deterministicHttpFailureFromActivity([
    { phase: 'response', path: 'not_allowed', status: 401 },
    { phase: 'response', path: '/v1/messages/count_tokens', status: 403 },
    { phase: 'circuit_open', path: '/v1/responses/compact', status: 422 },
    { phase: 'response', status: 400 },
  ].map((activity) => JSON.stringify(activity)).join('\n')), null);
  assert.equal(deterministicHttpFailureFromActivity(JSON.stringify({
    phase: 'response', path: '/v1/responses', status: 401,
  }))?.path, '/v1/responses');
  const failure = deterministicHttpFailureFromActivity([
    retryable,
    JSON.stringify({
      phase: 'response',
      status: 422,
      path: '/v1/messages',
      model: 'sonnet',
      requestNumber: 4,
      errorType: 'invalid_request_error',
      errorCode: 'model_not_allowed',
      errorParam: 'model',
      errorCategory: 'unknown_model_or_lane',
      errorMessageSha256: 'a'.repeat(64),
      ignoredSecret: 'must not escape',
    }),
  ].join('\n'));
  assert.deepEqual(failure, {
    status: 422,
    path: '/v1/messages',
    model: 'sonnet',
    requestNumber: 4,
    errorType: 'invalid_request_error',
    errorCode: 'model_not_allowed',
    errorParam: 'model',
    errorCategory: 'unknown_model_or_lane',
    errorMessageSha256: 'a'.repeat(64),
  });
});

test('infrastructure audit reports retain only bounded operational evidence', () => {
  const report = buildInfrastructureCliReport({
    scenario: cliReport().scenario,
    context,
    failure: {
      stage: 'evaluation',
      reason: 'deterministic_http',
      status: 400,
      path: '/v1/messages',
      model: 'sonnet',
      errorCategory: 'unsupported_parameter',
      diagnosticSha256: 'a'.repeat(64),
      rawError: 'must never escape',
    },
    startedAt: '2026-07-16T01:00:00.000Z',
    completedAt: '2026-07-16T01:00:01.000Z',
  });
  assert.equal(report.outcome, 'infrastructure_failed');
  assert.equal(report.manifest, null);
  assert.equal(report.infrastructureFailure.status, 400);
  assert.equal(report.infrastructureFailure.rawError, undefined);
  const evaluation = buildApiEvaluation(report, context);
  assert.equal(evaluation.candidate, null);
  assert.equal(evaluation.outcome, 'infrastructure_failed');
  assert.match(evaluation.evidenceDigest, /^[0-9a-f]{64}$/);
  for (const errorCategory of [
    'request_body_too_large',
    'model_not_allowed',
    'invalid_output_token_limit',
  ]) {
    assert.equal(normalizeInfrastructureFailure({
      schemaVersion: 'marketplace.pack-production-infrastructure-failure/v1',
      stage: 'agent_preflight',
      reason: 'deterministic_http',
      status: 400,
      errorCategory,
    }).errorCategory, errorCategory);
  }
  assert.throws(() => normalizeInfrastructureFailure({
    schemaVersion: 'marketplace.pack-production-infrastructure-failure/v1',
    stage: 'evaluation',
    reason: 'invented',
  }), /Unsupported infrastructure failure reason/);
  for (const diagnosticSha256 of ['a'.repeat(65), `${'a'.repeat(63)} `, 42]) {
    assert.throws(() => normalizeInfrastructureFailure({
      schemaVersion: 'marketplace.pack-production-infrastructure-failure/v1',
      stage: 'agent_preflight',
      reason: 'preflight_failed',
      diagnosticSha256,
    }), /Infrastructure diagnostic hash is invalid/);
  }
});

test('safe CLI evidence hard-caps error digests per category and in total', () => {
  const report = cliReport();
  const errors = (category) => Array.from(
    { length: 40 },
    (_, index) => `secret-${category}-${index}`,
  );
  report.errors = errors('evaluation');
  report.composition.errors = errors('composition');
  report.packVerification.errors = errors('pack');
  report.baselineVerification.errors = errors('baseline');
  report.slotEvaluations = [{ errors: errors('slot') }];
  report.bestSingleEvidence = { errors: errors('single') };
  report.ablationVerification = [{ errors: errors('ablation') }];

  const evidence = buildSafeCliEvidence(report, context);
  assert.equal(evidence.errorEvidence.length, 7);
  assert.ok(evidence.errorEvidence.every((entry) => entry.sha256.length <= 16));
  assert.equal(
    evidence.errorEvidence.reduce((count, entry) => count + entry.sha256.length, 0),
    64,
  );
  assert.equal(evidence.counts.errors, 280);
  assert.equal(evidence.counts.errorDigestsCaptured, 64);
  assert.equal(evidence.counts.errorDigestsTruncated, true);
  assert.ok(evidence.errorEvidence.every((entry) => entry.truncated));
  assert.doesNotMatch(JSON.stringify(evidence), /secret-/);
});

test('safe CLI evidence retains only bounded failed Agent process metadata', () => {
  const report = cliReport();
  report.slotEvaluations = [{
    agentExecutionEvidence: [{
      phase: 'run',
      run: 1,
      succeeded: false,
      privateInvocation: 'private prompt',
      attempts: [{
        schemaVersion: 'skillstore.agent-execution-evidence/v1',
        agent: 'claude',
        attempt: 1,
        sandboxed: true,
        outcome: 'failed',
        failureCategory: 'spawn_error',
        spawnErrorCode: 'EAGAIN',
        exitCode: null,
        signal: null,
        durationMs: 42,
        stdoutBytes: 0,
        stderrBytes: 0,
        stdoutSha256: 'a'.repeat(64),
        stderrSha256: 'b'.repeat(64),
        rawStderr: 'secret child path',
      }],
    }],
    errors: [],
  }];

  const evidence = buildSafeCliEvidence(report, context).agentExecutionEvidence;
  assert.deepEqual(evidence, {
    schemaVersion: 'marketplace.pack-production-agent-execution-evidence/v1',
    invocations: 1,
    attempts: 1,
    failedInvocations: 1,
    failedAttempts: 1,
    recoveredFailedAttempts: 0,
    capturedFailures: 1,
    truncated: false,
    failures: [{
      phase: 'run',
      run: 1,
      recovered: false,
      agent: 'claude',
      attempt: 1,
      sandboxed: true,
      outcome: 'failed',
      failureCategory: 'spawn_error',
      spawnErrorCode: 'EAGAIN',
      exitCode: null,
      signal: null,
      durationMs: 42,
      stdoutBytes: 0,
      stderrBytes: 0,
      stdoutSha256: 'a'.repeat(64),
      stderrSha256: 'b'.repeat(64),
    }],
  });
  assert.doesNotMatch(JSON.stringify(evidence), /private|secret|rawStderr/);
});

test('safe CLI evidence retains a failed attempt recovered by a later retry', () => {
  const report = cliReport();
  const attempt = (number, outcome, category, code) => ({
    schemaVersion: 'skillstore.agent-execution-evidence/v1',
    agent: 'claude',
    attempt: number,
    sandboxed: true,
    outcome,
    failureCategory: category,
    spawnErrorCode: code,
    exitCode: outcome === 'succeeded' ? 0 : null,
    signal: null,
    durationMs: 10,
    stdoutBytes: outcome === 'succeeded' ? 5 : 0,
    stderrBytes: 0,
    stdoutSha256: 'a'.repeat(64),
    stderrSha256: 'b'.repeat(64),
  });
  report.slotEvaluations = [{
    agentExecutionEvidence: [{
      phase: 'run',
      run: 1,
      succeeded: true,
      attempts: [
        attempt(1, 'failed', 'spawn_error', 'EAGAIN'),
        attempt(2, 'succeeded', 'none', null),
      ],
    }],
    errors: [],
  }];

  const evidence = buildSafeCliEvidence(report, context).agentExecutionEvidence;
  assert.equal(evidence.failedInvocations, 0);
  assert.equal(evidence.failedAttempts, 1);
  assert.equal(evidence.recoveredFailedAttempts, 1);
  const { schemaVersion: _schemaVersion, ...failedAttempt } = attempt(
    1,
    'failed',
    'spawn_error',
    'EAGAIN',
  );
  assert.deepEqual(evidence.failures[0], {
    phase: 'run',
    run: 1,
    recovered: true,
    ...failedAttempt,
  });
});

test('Agent evidence traversal fails before descending past its depth budget', () => {
  const report = cliReport();
  let nested = {};
  for (let depth = 0; depth < 40; depth += 1) nested = { nested };
  report.extra = nested;
  assert.throws(
    () => buildSafeCliEvidence(report, context),
    /traversal depth budget/,
  );
});

test('executor preflight preserves the validated attempt schema for the shell projector', () => {
  const bindings = [
    { canonicalId: 'pack-executor-preflight-a', contentHash: '1'.repeat(64), version: '1.0.0' },
    { canonicalId: 'pack-executor-preflight-b', contentHash: '2'.repeat(64), version: '1.0.0' },
  ];
  const attempt = (agent) => ({
    schemaVersion: 'skillstore.agent-execution-evidence/v1',
    agent,
    attempt: 1,
    sandboxed: true,
    outcome: 'succeeded',
    failureCategory: 'none',
    spawnErrorCode: null,
    exitCode: 0,
    signal: null,
    durationMs: 10,
    stdoutBytes: 5,
    stderrBytes: 0,
    stdoutSha256: 'a'.repeat(64),
    stderrSha256: 'b'.repeat(64),
  });
  const report = {
    schemaVersion: 'skillstore.pack-executor-preflight/v1',
    outcome: 'passed',
    bindings,
    verification: {
      passed: true,
      runs: 1,
      medianScore: 10,
      taskCompletedRate: 1,
      verdictCount: 1,
      errorCount: 0,
      usedSkill: true,
      usedSkills: bindings.map((binding) => binding.canonicalId),
      taskCompleted: true,
      envBlocked: false,
      score: 10,
    },
    runnerUsageTraces: [{
      schemaVersion: 'skillstore.runner-skill-trace/v1',
      agent: 'claude',
      source: 'claude-stream-json-v1',
      deterministic: true,
      events: bindings.map((binding, index) => ({ sequence: index + 1, ...binding })),
    }],
    agentExecutionEvidence: [
      { phase: 'run', run: 1, succeeded: true, attempts: [attempt('claude')] },
      { phase: 'judge', run: 1, succeeded: true, attempts: [attempt('codex')] },
    ],
  };
  const closure = exactExecutorPreflightClosure(report, bindings);

  assert.deepEqual(
    closure.agentExecutionEvidence.map((invocation) => invocation.attempts[0].schemaVersion),
    [
      'skillstore.agent-execution-evidence/v1',
      'skillstore.agent-execution-evidence/v1',
    ],
  );
  assert.deepEqual(closure.runnerTraceEvidence, {
    schemaVersion: 'marketplace.pack-executor-trace-evidence/v1',
    deterministic: true,
    traceCount: 1,
    eventCount: 2,
    bindingDigest: createHash('sha256').update(canonicalJson(bindings)).digest('hex'),
  });

  const wrongJudge = structuredClone(report);
  wrongJudge.verification.usedSkills = [bindings[0].canonicalId];
  assert.equal(exactExecutorPreflightClosure(wrongJudge, bindings), null);

  const wrongTrace = structuredClone(report);
  wrongTrace.runnerUsageTraces[0].events[1].contentHash = 'f'.repeat(64);
  assert.equal(exactExecutorPreflightClosure(wrongTrace, bindings), null);
});

test('executor preflight retains bounded failed Agent evidence outside the pass closure', () => {
  const report = {
    errors: ['private failure text'],
    verdicts: [],
    agentExecutionEvidence: [{
      phase: 'run',
      run: 1,
      succeeded: false,
      privateInvocation: 'private prompt',
      attempts: [{
        schemaVersion: 'skillstore.agent-execution-evidence/v1',
        agent: 'claude',
        attempt: 1,
        sandboxed: true,
        outcome: 'failed',
        failureCategory: 'spawn_error',
        spawnErrorCode: 'EAGAIN',
        exitCode: null,
        signal: null,
        durationMs: 10,
        stdoutBytes: 0,
        stderrBytes: 0,
        stdoutSha256: 'a'.repeat(64),
        stderrSha256: 'b'.repeat(64),
        rawStderr: 'private process detail',
      }],
    }],
  };

  assert.equal(exactExecutorPreflightClosure(report, [
    { canonicalId: 'pack-executor-preflight-a', contentHash: '1'.repeat(64), version: '1.0.0' },
    { canonicalId: 'pack-executor-preflight-b', contentHash: '2'.repeat(64), version: '1.0.0' },
  ]), null);
  const evidence = projectExecutorPreflightEvidence(report);
  assert.equal(evidence[0].attempts[0].spawnErrorCode, 'EAGAIN');
  assert.equal(evidence[0].attempts[0].schemaVersion, 'skillstore.agent-execution-evidence/v1');
  assert.doesNotMatch(JSON.stringify(evidence), /private|rawStderr|errors|verdicts/);
});

test('isolated scenario Codex home permits ephemeral state without weakening config', async (t) => {
  if (typeof process.getuid !== 'function' || typeof process.getgid !== 'function') {
    t.skip('POSIX ownership is required');
    return;
  }
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-runtime-'));
  const sourceCodexHome = join(directory, 'source-codex-home');
  const runtimeRoot = join(directory, 'generations');
  mkdirSync(sourceCodexHome, { recursive: true });
  writeFileSync(join(sourceCodexHome, 'config.toml'), 'model_provider = "fixture"\n');

  const runtime = await prepareScenarioRuntime(
    runtimeRoot,
    'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0',
    process.getuid(),
    process.getgid(),
    { CODEX_HOME: sourceCodexHome },
  );
  const codexHome = runtime.env.CODEX_HOME;
  assert.equal(statSync(codexHome).mode & 0o7777, 0o1777);
  assert.doesNotThrow(() => accessSync(codexHome, constants.W_OK));
  assert.equal(statSync(join(codexHome, 'config.toml')).mode & 0o777, 0o444);
  assert.equal(statSync(join(codexHome, 'log')).mode & 0o777, 0o700);
  assert.equal(statSync(join(codexHome, 'sessions')).mode & 0o777, 0o700);
  assert.equal(statSync(join(codexHome, 'log')).uid, process.getuid());
  assert.equal(statSync(join(codexHome, 'sessions')).uid, process.getuid());
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

test('async evaluator stalls despite continuous untrusted stdout and stderr noise', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-stall-'));
  const progressFile = join(directory, 'progress.ndjson');
  const result = await runEvaluatorProcess(
    process.execPath,
    ['-e', `setInterval(() => {
      process.stdout.write('untrusted-noise');
      process.stderr.write('not allowlisted evaluator progress\\n');
    }, 5)`],
    {
      cwd: directory,
      env: process.env,
      stdoutFile: join(directory, 'stdout.json'),
      stderrFile: join(directory, 'run.log'),
      progressFile,
      label: 'excel-dashboard',
      heartbeatMs: 10,
      idleTimeoutMs: 40,
      timeoutMs: 1_000,
      killGraceMs: 100,
      onProgress: () => {},
    },
  );

  assert.equal(result.stalled, true);
  assert.equal(result.timedOut, false);
  const events = readFileSync(progressFile, 'utf8').trim().split('\n').map(JSON.parse);
  assert.ok(events.some((event) => event.event === 'scenario.heartbeat'));
  assert.ok(events.some((event) => event.event === 'scenario.stalled'));
  assert.ok(events.some((event) => event.event === 'scenario.process_exited' && event.stalled));
});

test('external proxy activity extends the idle deadline without exposing request data', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-proxy-activity-'));
  const activityFile = join(directory, 'proxy.activity');
  writeFileSync(activityFile, '');
  const activityTimer = setInterval(() => writeFileSync(activityFile, `${Date.now()}\n`), 20);
  let result;
  try {
    result = await runEvaluatorProcess(
      process.execPath,
      ['-e', 'setTimeout(() => process.exit(0), 180)'],
      {
        cwd: directory,
        env: process.env,
        stdoutFile: join(directory, 'stdout.json'),
        stderrFile: join(directory, 'run.log'),
        progressFile: join(directory, 'progress.ndjson'),
        externalActivityFile: activityFile,
        label: 'excel-dashboard',
        heartbeatMs: 10,
        idleTimeoutMs: 50,
        timeoutMs: 1_000,
        killGraceMs: 100,
        onProgress: () => {},
      },
    );
  } finally {
    clearInterval(activityTimer);
  }

  assert.equal(result.status, 0);
  assert.equal(result.stalled, false);
  assert.equal(result.timedOut, false);
});

test('auxiliary proxy rejection does not terminate in-flight inference', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-auxiliary-activity-'));
  const activityFile = join(directory, 'proxy.activity');
  const progressFile = join(directory, 'progress.ndjson');
  writeFileSync(activityFile, [
    { phase: 'response', requestNumber: 1, path: 'not_allowed', status: 401 },
    { phase: 'started', requestNumber: 2, path: '/v1/messages', model: 'claude-sonnet-5' },
    { phase: 'started', requestNumber: 3, path: '/v1/messages', model: 'claude-sonnet-5' },
  ].map((activity) => JSON.stringify(activity)).join('\n'));
  const result = await runEvaluatorProcess(
    process.execPath,
    ['-e', 'setTimeout(() => process.exit(0), 180)'],
    {
      cwd: directory,
      env: process.env,
      stdoutFile: join(directory, 'stdout.json'),
      stderrFile: join(directory, 'run.log'),
      progressFile,
      externalActivityFile: activityFile,
      label: 'executor-preflight',
      heartbeatMs: 20,
      idleTimeoutMs: 5_000,
      timeoutMs: 1_000,
      killGraceMs: 100,
      onProgress: () => {},
    },
  );

  assert.equal(result.status, 0);
  assert.equal(result.signal, null);
  assert.equal(result.deterministicHttpFailure, null);
  assert.doesNotMatch(readFileSync(progressFile, 'utf8'), /scenario\.deterministic_http_failure/);
});

test('mid-evaluation deterministic 4xx opens the circuit and terminates the scenario', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-http-circuit-'));
  const activityFile = join(directory, 'proxy.activity');
  const progressFile = join(directory, 'progress.ndjson');
  writeFileSync(activityFile, '');
  const activityTimer = setTimeout(() => writeFileSync(activityFile, `${JSON.stringify({
    phase: 'response',
    status: 403,
    path: '/v1/messages',
    model: 'sonnet',
    requestNumber: 1,
    errorType: 'permission_error',
    errorMessageSha256: 'b'.repeat(64),
  })}\n`), 25);
  let result;
  try {
    result = await runEvaluatorProcess(
      process.execPath,
      ['-e', 'setInterval(() => {}, 1000)'],
      {
        cwd: directory,
        env: process.env,
        stdoutFile: join(directory, 'stdout.json'),
        stderrFile: join(directory, 'run.log'),
        progressFile,
        externalActivityFile: activityFile,
        label: 'excel-dashboard',
        heartbeatMs: 20,
        idleTimeoutMs: 5_000,
        timeoutMs: 5_000,
        killGraceMs: 100,
        onProgress: () => {},
      },
    );
  } finally {
    clearTimeout(activityTimer);
  }
  assert.equal(result.deterministicHttpFailure.status, 403);
  assert.equal(result.timedOut, false);
  const progress = readFileSync(progressFile, 'utf8');
  assert.match(progress, /scenario\.deterministic_http_failure/);
  assert.match(progress, /scenario\.http_circuit_opened/);
  assert.doesNotMatch(progress, /must not escape/);
});

test('linux SIGTERM writes diagnostics and kills a TERM-ignoring grandchild process tree', {
  skip: process.platform !== 'linux',
}, async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-sigterm-'));
  const grandchildPidFile = join(directory, 'grandchild.pid');
  const progressFile = join(directory, 'progress.ndjson');
  const checkpointFile = join(directory, 'checkpoint.json');
  const resultFile = join(directory, 'result.json');
  const grandchildScript = [
    "const { writeFileSync } = require('node:fs')",
    `writeFileSync(${JSON.stringify(grandchildPidFile)}, String(process.pid))`,
    "process.on('SIGTERM', () => {})",
    'setInterval(() => {}, 1000)',
  ].join(';');
  const childScript = [
    "const { spawn } = require('node:child_process')",
    `spawn(process.execPath, ['-e', ${JSON.stringify(grandchildScript)}], { stdio: 'inherit' })`,
    'setInterval(() => {}, 1000)',
  ].join(';');
  const helperScript = `
    import { writeFileSync } from 'node:fs';
    import { runEvaluatorProcess } from ${JSON.stringify(PACK_PRODUCTION_URL)};
    const result = await runEvaluatorProcess(process.execPath, ['-e', ${JSON.stringify(childScript)}], {
      cwd: ${JSON.stringify(directory)},
      env: process.env,
      stdoutFile: ${JSON.stringify(join(directory, 'stdout.json'))},
      stderrFile: ${JSON.stringify(join(directory, 'run.log'))},
      progressFile: ${JSON.stringify(progressFile)},
      checkpointFile: ${JSON.stringify(checkpointFile)},
      label: 'excel-dashboard',
      heartbeatMs: 20,
      idleTimeoutMs: 2_000,
      timeoutMs: 5_000,
      killGraceMs: 100,
      onProgress: () => {},
    });
    writeFileSync(${JSON.stringify(resultFile)}, JSON.stringify(result));
  `;
  const helper = spawn(process.execPath, ['--input-type=module', '-e', helperScript], {
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  for (let attempt = 0; attempt < 100 && !existsSync(grandchildPidFile); attempt += 1) {
    await new Promise((resolveWait) => setTimeout(resolveWait, 10));
  }
  assert.equal(existsSync(grandchildPidFile), true);
  const grandchildPid = Number(readFileSync(grandchildPidFile, 'utf8'));
  helper.kill('SIGTERM');
  const [helperStatus] = await once(helper, 'close');
  assert.equal(helperStatus, 0);
  const result = JSON.parse(readFileSync(resultFile, 'utf8'));

  assert.equal(result.interruptedSignal, 'SIGTERM');
  assert.ok(readFileSync(progressFile, 'utf8').length > 0);
  assert.ok(readFileSync(checkpointFile, 'utf8').length > 0);
  assert.match(readFileSync(progressFile, 'utf8'), /scenario\.signal_received/);
  let grandchildAlive = true;
  for (let attempt = 0; attempt < 100 && grandchildAlive; attempt += 1) {
    try {
      process.kill(grandchildPid, 0);
      await new Promise((resolveWait) => setTimeout(resolveWait, 10));
    } catch (error) {
      if (error?.code !== 'ESRCH') throw error;
      grandchildAlive = false;
    }
  }
  assert.equal(grandchildAlive, false);
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

test('a timed-out admitted scenario becomes a verifiable candidate-null infrastructure audit', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-fallback-'));
  const cli = join(directory, 'fake-skillstore-cli');
  const cliArgsFile = join(directory, 'cli-args.json');
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
require('node:fs').writeFileSync(${JSON.stringify(cliArgsFile)}, JSON.stringify(args));
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
  writeFileSync(planFile, `${JSON.stringify(immutableProductionPlan(scenarios.slow))}\n`);

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
    '--agent-timeout-ms', '1234',
    '--agent-max-retries', '2',
  ], { encoding: 'utf8', timeout: 5_000 });
  assert.equal(evaluation.status, 0, evaluation.stderr);

  const summary = JSON.parse(readFileSync(join(resultsDir, 'evaluate-summary.json'), 'utf8'));
  assert.deepEqual(summary.attempts.map((attempt) => attempt.status), ['completed']);
  assert.equal(summary.attempts[0].outcome, 'infrastructure_failed');
  assert.equal(summary.attempts[0].generationId, context.generationId);
  assert.equal(summary.attempts[0].infrastructureAudit, true);
  assert.equal(summary.reports[0].outcome, 'infrastructure_failed');
  assert.equal(readFileSync(join(resultsDir, '01-slow.run.log'), 'utf8'), '');
  const forwardedArgs = JSON.parse(readFileSync(cliArgsFile, 'utf8'));
  assert.equal(forwardedArgs[forwardedArgs.indexOf('--generation-id') + 1], context.generationId);
  assert.equal(forwardedArgs[forwardedArgs.indexOf('--agent-timeout-ms') + 1], '1234');
  assert.equal(forwardedArgs[forwardedArgs.indexOf('--agent-max-retries') + 1], '2');
  const audit = JSON.parse(readFileSync(join(resultsDir, '01-slow.evaluation.json'), 'utf8'));
  assert.equal(audit.outcome, 'infrastructure_failed');
  assert.equal(audit.candidate, null);
  assert.equal(audit.evidence.cliReport.infrastructureFailure.reason, 'timeout');
  assert.throws(() => readFileSync(join(resultsDir, '02-fast.run.log')));

  const verification = spawnSync(process.execPath, [PACK_PRODUCTION, 'verify', ...common], {
    encoding: 'utf8',
    timeout: 5_000,
  });
  assert.equal(verification.status, 0, verification.stderr);
  assert.equal(
    JSON.parse(readFileSync(join(resultsDir, 'evaluation-verification.json'), 'utf8')).selectedGenerationId,
    null,
  );
});

test('preflight failure evidence skips Pack generation and closes as an infrastructure audit', () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-preflight-audit-'));
  const cli = join(directory, 'fake-skillstore-cli');
  const invoked = join(directory, 'pack-generate-invoked');
  writeFileSync(cli, `#!/bin/sh
if [ "$1" = "--version" ]; then echo "skillstore-cli 2.10.0"; exit 0; fi
touch ${JSON.stringify(invoked)}
exit 99
`);
  chmodSync(cli, 0o755);
  const report = cliReport();
  const planFile = join(directory, 'plan.json');
  const resultsDir = join(directory, 'results');
  const failureFile = join(directory, 'infrastructure-failure.json');
  writeFileSync(planFile, `${JSON.stringify(immutableProductionPlan(report.scenario))}\n`);
  writeFileSync(failureFile, `${JSON.stringify({
    schemaVersion: 'marketplace.pack-production-infrastructure-failure/v1',
    stage: 'agent_preflight',
    reason: 'deterministic_http',
    status: 400,
    errorCategory: 'invalid_output_token_limit',
    diagnosticSha256: 'a'.repeat(64),
  })}\n`);
  const result = spawnSync(process.execPath, [
    PACK_PRODUCTION,
    'evaluate',
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
    '--infrastructure-failure-file', failureFile,
  ], { encoding: 'utf8' });

  assert.equal(result.status, 0, result.stderr);
  assert.equal(existsSync(invoked), false);
  const audit = JSON.parse(readFileSync(join(resultsDir, '01-excel-dashboard.evaluation.json'), 'utf8'));
  assert.equal(audit.generationId, context.generationId);
  assert.equal(audit.outcome, 'infrastructure_failed');
  assert.equal(audit.candidate, null);
  assert.deepEqual(audit.evidence.cliReport.infrastructureFailure, {
    schemaVersion: 'marketplace.pack-production-infrastructure-failure/v1',
    stage: 'agent_preflight',
    reason: 'deterministic_http',
    status: 400,
    errorCategory: 'invalid_output_token_limit',
    diagnosticSha256: 'a'.repeat(64),
    pathSha256: null,
    modelSha256: null,
  });

  const replayResultsDir = join(directory, 'replay-results');
  const replay = spawnSync(process.execPath, [
    PACK_PRODUCTION,
    'evaluate',
    '--plan', planFile,
    '--results-dir', replayResultsDir,
    '--cli', cli,
    '--expected-cli-version', '2.10.0',
    '--skills-dir', directory,
    '--run-id', context.runId,
    '--run-attempt', String(context.runAttempt),
    '--commit-sha', context.commitSha,
    '--model', context.model,
    '--judge-model', context.judgeModel,
    '--infrastructure-failure-file', failureFile,
  ], { encoding: 'utf8' });
  assert.equal(replay.status, 0, replay.stderr);
  assert.equal(
    JSON.parse(readFileSync(join(replayResultsDir, '01-excel-dashboard.evaluation.json'), 'utf8')).generationId,
    context.generationId,
  );
});

test('adapter binds the complete v4 causal evidence and immutable DAG identities', () => {
  const evaluation = buildApiEvaluation(cliReport(), context);
  assert.equal(evaluation.schemaVersion, 'skillstore.pack-evaluation/v4');
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
    workflowDigest: evaluation.candidate.manifest.executionDag.workflowDigest,
    runs: 3,
    scores: [4, 4, 5],
    score: 4,
    improvement: 4,
    errors: [],
  });
  assert.match(evaluation.candidate.manifest.executionDag.workflowDigest, /^[0-9a-f]{64}$/);
  assert.match(evaluation.candidate.manifest.executionDag.bindingDigest, /^[0-9a-f]{64}$/);
  assert.equal(evaluation.candidate.fitness.bestSingle.winnerSkill, 'spreadsheet-skill');
  assert.equal(evaluation.candidate.fitness.bestSingle.competitors.length, 2);
  assert.deepEqual(evaluation.candidate.fitness.deterministicMarginalSkills, [
    'spreadsheet-skill',
    'workbook-validator',
  ]);
  assert.equal(evaluation.candidate.fitness.ablation.length, 2);
  assert.equal(
    evaluation.candidate.fitness.treatmentWorkflowDigests.fullPack,
    evaluation.candidate.manifest.executionDag.workflowDigest,
  );
  assert.equal(evaluation.candidate.fitness.evaluationSuite.hiddenVariantCount, 2);
  assert.equal(evaluation.candidate.fitness.usageProvenance.source, 'runner-trace-v1');
  assert.deepEqual(evaluation.candidate.fitness.verdicts[0].usedSkills, ['spreadsheet-skill', 'workbook-validator']);
  assert.equal(evaluation.candidate.fitness.verdicts[0].artifactVerified, true);
  assert.match(evaluation.evidenceDigest, /^[0-9a-f]{64}$/);
  assert.equal(evaluation.evidence.cliReport.schemaVersion, 'marketplace.pack-production-cli-evidence/v1');
  assert.equal(evaluation.evidence.cliReport.sourceSchemaVersion, 'pack-generation-evaluation/v2');
});

test('Marketplace reconstruction exactly matches the Skillstore v4 golden JSON update point', () => {
  const expected = JSON.parse(readFileSync(V4_GOLDEN, 'utf8'));
  const evaluation = buildApiEvaluation(cliReport(), context);
  evaluation.evidence = expected.evidence;
  const { evidenceDigest: _oldDigest, ...unsigned } = evaluation;
  evaluation.evidenceDigest = createHash('sha256').update(canonicalJson(unsigned)).digest('hex');
  assert.deepEqual(evaluation, expected);
});

test('adapter rejects one-Skill or incomplete candidate_ready evidence before persistence', () => {
  const oneSkill = cliReport();
  oneSkill.manifest.skills = ['spreadsheet-skill'];
  assert.throws(() => buildApiEvaluation(oneSkill, context), /two to four distinct manifest Skills/);

  const fiveSkills = cliReport();
  fiveSkills.manifest.skills = ['one', 'two', 'three', 'four', 'five'];
  assert.throws(() => buildApiEvaluation(fiveSkills, context), /two to four distinct manifest Skills/);

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

  const missingDag = cliReport();
  delete missingDag.manifest.execution_dag;
  assert.throws(() => buildApiEvaluation(missingDag, context), /execution DAG/);

  const missingBestSingle = cliReport();
  delete missingBestSingle.bestSingleEvidence;
  assert.throws(() => buildApiEvaluation(missingBestSingle, context), /best-single verification/);

  const incompleteAblation = cliReport();
  incompleteAblation.ablationVerification.pop();
  assert.throws(() => buildApiEvaluation(incompleteAblation, context), /exactly one treatment/);

  const suiteNotExecuted = cliReport();
  suiteNotExecuted.evaluationSuiteEvidence.executed = false;
  assert.throws(() => buildApiEvaluation(suiteNotExecuted, context), /execute the v1 paired evaluation suite/);

  const judgeOnlyUsage = cliReport();
  judgeOnlyUsage.usageProvenance = { deterministic: false, source: 'judge-only', traces: [] };
  assert.throws(() => buildApiEvaluation(judgeOnlyUsage, context), /deterministic runner Skill usage provenance/);

  const malformedRootErrors = cliReport();
  malformedRootErrors.errors = { secret: 'must not be stringified' };
  assert.throws(
    () => buildApiEvaluation(malformedRootErrors, context),
    /candidate_ready evaluation errors must be an array of error strings/,
  );

  const malformedCompositionErrors = cliReport();
  malformedCompositionErrors.composition.errors = ['retry', { secret: 'must not be stringified' }];
  assert.throws(
    () => buildApiEvaluation(malformedCompositionErrors, context),
    /candidate_ready composition errors\[1\] must be a bounded non-empty error string/,
  );
});

test('candidate technical errors persist only as fixed codes and hashed evidence', () => {
  const report = cliReport();
  report.errors = ['raw evaluation secret'];
  report.packVerification.errors = ['raw Pack secret'];
  report.baselineVerification.errors = ['raw baseline secret'];
  const evaluation = buildApiEvaluation(report, context);

  assert.deepEqual(evaluation.candidate.fitness.errors, [
    'evaluation_reported_error',
    'pack_verification_reported_error',
    'baseline_verification_reported_error',
  ]);
  assert.deepEqual(evaluation.candidate.fitness.baseline.errors, [
    'baseline_verification_reported_error',
  ]);
  assert.doesNotMatch(JSON.stringify(evaluation), /raw (?:evaluation|Pack|baseline) secret/);
});

test('a recovered composer retry stays in hashed evidence without poisoning passed fitness', () => {
  const report = cliReport();
  report.composition = { attempts: 2, fallbackUsed: false, errors: ['attempt 1: invalid JSON'] };
  report.errors = ['attempt 1: invalid JSON'];
  const evaluation = buildApiEvaluation(report, context);
  assert.deepEqual(evaluation.candidate.fitness.errors, []);
  const compositionEvidence = evaluation.evidence.cliReport.errorEvidence.find(
    (entry) => entry.category === 'composition',
  );
  assert.deepEqual(compositionEvidence, {
    category: 'composition',
    count: 1,
    capturedCount: 1,
    truncated: false,
    sha256: [createHash('sha256').update('attempt 1: invalid JSON').digest('hex')],
  });
  assert.doesNotMatch(JSON.stringify(evaluation), /attempt 1: invalid JSON/);
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

test('complete v4 non-candidates reach only the candidate-null POST plan', () => {
  const rejectedReport = cliReport();
  rejectedReport.outcome = 'quality_rejected';
  rejectedReport.manifest = null;
  rejectedReport.packVerification = null;
  rejectedReport.baselineVerification = null;
  const rejected = buildApiEvaluation(rejectedReport, context);
  const auditPlan = planTrustedPersistence([
    { file: '01-excel-dashboard.evaluation.json', evaluation: rejected },
  ], null);
  assert.equal(auditPlan.candidate, null);
  assert.equal(auditPlan.candidateNullPosts.length, 1);
  assert.equal(auditPlan.auditOnly.length, 0);

  const response = {
    data: {
      generationId: rejected.generationId,
      outcome: rejected.outcome,
      evaluationOutcome: rejected.outcome,
      pack: null,
      enrichment: { content: 'not_applicable', translation: 'not_applicable', contentDispatchNonce: null },
    },
  };
  assert.equal(validateCandidateNullPersistResponse(response, rejected).generationId, rejected.generationId);
  assert.throws(() => validateCandidateNullPersistResponse({
    data: { ...response.data, pack: { id: 'forbidden' } },
  }, rejected), /exact candidate-null v4 audit outcome/);

  const candidate = buildApiEvaluation(cliReport(), context);
  delete candidate.candidate.fitness.bestSingle.competitors;
  assert.throws(() => planTrustedPersistence([
    { file: '01-excel-dashboard.evaluation.json', evaluation: candidate },
  ], candidate.generationId), /persistence and enrichment are forbidden/);
});

test('finalize fails closed when a newer content dispatch supersedes its nonce', () => {
  const expected = '22222222-2222-4222-8222-222222222222';
  assert.equal(validateCurrentContentDispatchNonce({ content_dispatch_nonce: expected }, expected, 'generation-1'), expected);
  assert.throws(() => validateCurrentContentDispatchNonce({
    content_dispatch_nonce: '33333333-3333-4333-8333-333333333333',
  }, expected, 'generation-1'), /was superseded/);
});

test('persist POSTs every verified v4 candidate-null outcome and creates no Pack', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-persist-audits-'));
  const makeRejected = (generationId, outcome) => {
    const report = cliReport();
    report.generationId = generationId;
    report.outcome = outcome;
    report.outcomeReason = `${outcome} fixture`;
    report.manifest = null;
    report.packVerification = null;
    report.baselineVerification = null;
    return buildApiEvaluation(report, { ...context, generationId });
  };
  const evaluations = [
    ['01-quality.evaluation.json', makeRejected('11111111-1111-4111-8111-111111111111', 'quality_rejected')],
    ['02-infrastructure.evaluation.json', makeRejected('22222222-2222-4222-8222-222222222222', 'infrastructure_failed')],
  ];
  for (const [file, evaluation] of evaluations) {
    writeFileSync(join(directory, file), `${JSON.stringify(evaluation, null, 2)}\n`);
  }
  writeFileSync(join(directory, 'evaluation-verification.json'), `${JSON.stringify({
    schemaVersion: 'marketplace.pack-production-evaluation-verification/v1',
    selectedGenerationId: null,
    files: evaluations.map(([file]) => ({
      file,
      sha256: createHash('sha256').update(readFileSync(join(directory, file))).digest('hex'),
    })),
  })}\n`);

  const observed = [];
  const server = createServer((request, response) => {
    const chunks = [];
    request.on('data', (chunk) => chunks.push(chunk));
    request.on('end', () => {
      const evaluation = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      observed.push({
        method: request.method,
        url: request.url,
        authorization: request.headers.authorization,
        evaluation,
      });
      response.writeHead(200, { 'content-type': 'application/json' });
      response.end(JSON.stringify({
        data: {
          generationId: evaluation.generationId,
          outcome: evaluation.outcome,
          evaluationOutcome: evaluation.outcome,
          replayed: false,
          pack: null,
          comparisonOf: null,
          autoPublishEligible: false,
          enrichment: { content: 'not_applicable', translation: 'not_applicable', contentDispatchNonce: null },
        },
      }));
    });
  });
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const address = server.address();
  const child = spawn(process.execPath, [
    PACK_PRODUCTION,
    'persist',
    '--results-dir', directory,
    '--api-url', `http://127.0.0.1:${address.port}`,
    '--token', 'test-token',
  ], { stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '';
  let stderr = '';
  child.stdout.on('data', (chunk) => { stdout += chunk; });
  child.stderr.on('data', (chunk) => { stderr += chunk; });
  const [status] = await once(child, 'close');
  server.close();
  await once(server, 'close');

  assert.equal(status, 0, stderr);
  assert.equal(observed.length, 2);
  assert.deepEqual(observed.map((item) => item.evaluation.outcome), [
    'quality_rejected',
    'infrastructure_failed',
  ]);
  assert.ok(observed.every((item) => (
    item.method === 'POST'
    && item.url === '/api/automation/packs/production'
    && item.authorization === 'Bearer test-token'
    && item.evaluation.candidate === null
  )));
  const summary = JSON.parse(stdout);
  assert.equal(summary.selected, null);
  assert.equal(summary.persisted.length, 2);
  assert.ok(summary.persisted.every((item) => (
    item.auditOnly === true
    && item.persistedRemotely === true
    && item.response.data.pack === null
  )));
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
    skillBindings: [
      { slug: 'spreadsheet-skill', version: '1.0.0', contentHash: '1'.repeat(64) },
      { slug: 'workbook-validator', version: '2.0.0', contentHash: '2'.repeat(64) },
    ],
    executionDag: request.candidate.manifest.executionDag,
    workflowDigest: request.candidate.manifest.executionDag.workflowDigest,
    bindingDigest: request.candidate.manifest.executionDag.bindingDigest,
    usageGuideMarker: request.candidate.manifest.executionDag.usageGuideMarker,
    executionBinding: {
      schemaVersion: 'skillstore.pack-execution-binding/v1',
      generationId: request.generationId,
      evidenceDigest: request.evidenceDigest,
      workflowDigest: request.candidate.manifest.executionDag.workflowDigest,
      bindingDigest: request.candidate.manifest.executionDag.bindingDigest,
      usageGuideMarker: request.candidate.manifest.executionDag.usageGuideMarker,
      marketplaceCommitSha: request.workflow.commitSha,
      skills: request.candidate.manifest.executionDag.skillBindings,
      executionDag: request.candidate.manifest.executionDag,
    },
  });
});

test('exact public readback proves DAG/digest and exact Skill versions/hashes', async () => {
  const request = buildApiEvaluation(cliReport(), context);
  const expected = buildPublicReadbackExpectation({ persisted: [{ request }] }, {
    generationId: request.generationId,
    pack: { id: 'pack-123', slug: request.scenario.slug },
  }, 'monthly-sales-excel-workbook');
  let observed;
  const result = await readExactPublicPack('https://skillstore.example', expected, async (url, options) => {
    observed = { url, options };
    return new Response(JSON.stringify({
      data: {
        id: 'pack-123',
        slug: 'monthly-sales-excel-workbook',
        reviewStatus: 'approved',
        executionBinding: expected.executionBinding,
        usageGuide: `# Guide\n${expected.usageGuideMarker}`,
        skills: expected.skillBindings,
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
  const request = buildApiEvaluation(cliReport(), context);
  const expected = buildPublicReadbackExpectation({ persisted: [{ request }] }, {
    generationId: request.generationId,
    pack: { id: 'pack-123', slug: request.scenario.slug },
  }, 'monthly-sales-excel-workbook');
  const result = validatePublicPackReadback({
    id: 'other-pack',
    slug: 'other-slug',
    review_status: 'approved',
    skills: [{ slug: 'artifact-validator' }, { slug: 'spreadsheet-skill' }],
  }, expected);

  assert.equal(result.matched, false);
  assert.match(result.mismatches.join('\n'), /Pack id mismatch/);
  assert.match(result.mismatches.join('\n'), /Pack slug mismatch/);
  assert.match(result.mismatches.join('\n'), /reviewStatus is missing/);
  assert.match(result.mismatches.join('\n'), /Pack Skill slugs mismatch/);
  assert.match(result.mismatches.join('\n'), /executionDag differs/);
  assert.match(result.mismatches.join('\n'), /version\/contentHash/);
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

test('trusted verification removes raw secrets from evaluation, rewritten stdout, and summary', () => {
  const secret = 'super-secret-provider-detail-7f9a';
  const report = cliReport();
  report.outcomeReason = secret;
  report.composition.errors = [secret];
  report.errors = [secret];
  const fixture = verificationFixture(report);
  const stdoutFile = join(fixture.directory, '01-excel-dashboard.stdout.json');
  const summaryFile = join(fixture.directory, 'evaluate-summary.json');

  assert.doesNotMatch(readFileSync(fixture.evaluationFile, 'utf8'), new RegExp(secret));
  assert.doesNotMatch(readFileSync(summaryFile, 'utf8'), new RegExp(secret));
  assert.match(readFileSync(stdoutFile, 'utf8'), new RegExp(secret));

  const result = runVerification(fixture);
  assert.equal(result.status, 0, result.stderr);
  assert.doesNotMatch(readFileSync(fixture.evaluationFile, 'utf8'), new RegExp(secret));
  assert.doesNotMatch(readFileSync(stdoutFile, 'utf8'), new RegExp(secret));
  assert.doesNotMatch(readFileSync(summaryFile, 'utf8'), new RegExp(secret));
  assert.equal(
    JSON.parse(readFileSync(stdoutFile, 'utf8')).schemaVersion,
    'marketplace.pack-production-cli-evidence/v1',
  );
});

test('internal SIGTERM becomes a verified candidate-null infrastructure closure', {
  skip: process.platform === 'win32',
}, async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-production-sigterm-closure-'));
  const cli = join(directory, 'fake-skillstore-cli');
  const marker = join(directory, 'evaluator-started');
  const planFile = join(directory, 'plan.json');
  const resultsDir = join(directory, 'results');
  writeFileSync(cli, `#!/bin/sh
if [ "$1" = "--version" ]; then echo "skillstore-cli 2.10.0"; exit 0; fi
touch ${JSON.stringify(marker)}
while :; do sleep 1; done
`);
  chmodSync(cli, 0o755);
  writeFileSync(planFile, `${JSON.stringify(immutableProductionPlan(cliReport().scenario))}\n`);
  const common = [
    '--plan', planFile,
    '--results-dir', resultsDir,
    '--cli', cli,
    '--expected-cli-version', '2.10.0',
    '--run-id', context.runId,
    '--run-attempt', String(context.runAttempt),
    '--commit-sha', context.commitSha,
    '--model', context.model,
    '--judge-model', context.judgeModel,
  ];
  const child = spawn(process.execPath, [
    PACK_PRODUCTION,
    'evaluate',
    ...common,
    '--skills-dir', directory,
    '--evaluation-budget-ms', '10000',
    '--scenario-timeout-ms', '10000',
    '--scenario-idle-timeout-ms', '10000',
    '--minimum-fallback-ms', '1',
  ], { stdio: ['ignore', 'pipe', 'pipe'] });
  let stdout = '';
  let stderr = '';
  child.stdout.on('data', (chunk) => { stdout += chunk; });
  child.stderr.on('data', (chunk) => { stderr += chunk; });
  for (let attempt = 0; attempt < 200 && !existsSync(marker); attempt += 1) {
    await new Promise((resolveWait) => setTimeout(resolveWait, 10));
  }
  assert.equal(existsSync(marker), true, stderr);
  await new Promise((resolveWait) => setTimeout(resolveWait, 50));
  child.kill('SIGTERM');
  const [status, signal] = await once(child, 'close');
  assert.equal(status, 0, `${stderr}\n${stdout}`);
  assert.equal(signal, null);

  const evaluation = JSON.parse(readFileSync(
    join(resultsDir, '01-excel-dashboard.evaluation.json'),
    'utf8',
  ));
  assert.equal(evaluation.outcome, 'infrastructure_failed');
  assert.equal(evaluation.candidate, null);
  assert.equal(evaluation.evidence.cliReport.infrastructureFailure.reason, 'cancelled');
  assert.equal(evaluation.evidence.cliReport.infrastructureFailure.signal, 'SIGTERM');
  const summary = JSON.parse(readFileSync(join(resultsDir, 'evaluate-summary.json'), 'utf8'));
  assert.equal(summary.reports[0].outcomeCategory, 'infrastructure');
  assert.match(summary.reports[0].outcomeReasonSha256, /^[0-9a-f]{64}$/);
  assert.equal(summary.reports[0].outcomeReason, undefined);

  const verification = spawnSync(process.execPath, [PACK_PRODUCTION, 'verify', ...common], {
    encoding: 'utf8',
  });
  assert.equal(verification.status, 0, verification.stderr);
  assert.equal(
    JSON.parse(readFileSync(join(resultsDir, 'evaluation-verification.json'), 'utf8')).selectedGenerationId,
    null,
  );
  const rewrittenStdout = JSON.parse(readFileSync(
    join(resultsDir, '01-excel-dashboard.stdout.json'),
    'utf8',
  ));
  assert.equal(rewrittenStdout.schemaVersion, 'marketplace.pack-production-cli-evidence/v1');
  assert.equal(rewrittenStdout.infrastructureFailure.signal, 'SIGTERM');
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

test('trusted verification rejects summary provenance that changes the immutable generation id', () => {
  const fixture = verificationFixture();
  const summaryFile = join(fixture.directory, 'evaluate-summary.json');
  const summary = JSON.parse(readFileSync(summaryFile, 'utf8'));
  summary.attempts[0].generationId = '22222222-2222-4222-8222-222222222222';
  summary.reports[0].generationId = '22222222-2222-4222-8222-222222222222';
  summary.selectedGenerationId = '22222222-2222-4222-8222-222222222222';
  writeFileSync(summaryFile, `${JSON.stringify(summary)}\n`);
  const result = runVerification(fixture);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /attempt differs from the immutable plan generation binding/);
});
