import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  inspectWorkflowRunEvent,
  persistCancellationRecovery,
  prepareCancellationRecovery,
} from '../pack-production-cancellation-recovery.mjs';

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const WORKFLOW_FILE = join(REPO_ROOT, '.github/workflows/recover-cancelled-pack-production.yml');
const WORKFLOW = readFileSync(WORKFLOW_FILE, 'utf8');
const RECOVERY_HELPER = readFileSync(join(REPO_ROOT, 'scripts/pack-production-cancellation-recovery.mjs'), 'utf8');
const GENERATION_ID = '11111111-1111-4111-8111-111111111111';
const SOURCE_SHA = 'a'.repeat(40);
const CURRENT_SHA = 'b'.repeat(40);
const CLI_SHA = 'c'.repeat(64);

function json(file, value) {
  writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function event(overrides = {}) {
  return {
    action: 'completed',
    repository: { full_name: 'aiskillstore/marketplace' },
    workflow_run: {
      id: 12345,
      run_attempt: 2,
      workflow_id: 678,
      name: 'Generate Pack',
      path: '.github/workflows/generate-packs.yml',
      status: 'completed',
      conclusion: 'cancelled',
      event: 'schedule',
      head_branch: 'main',
      head_sha: SOURCE_SHA,
      run_started_at: '2026-07-16T01:00:00.000Z',
      updated_at: '2026-07-16T01:05:00.000Z',
      head_repository: { full_name: 'aiskillstore/marketplace' },
      ...overrides,
    },
  };
}

function source() {
  return inspectWorkflowRunEvent(event());
}

function metadata() {
  const frozen = source();
  return {
    source: frozen,
    attempt: {
      id: frozen.runId,
      run_attempt: frozen.runAttempt,
      workflow_id: frozen.workflowId,
      name: frozen.workflowName,
      path: frozen.workflowPath,
      event: frozen.event,
      status: 'completed',
      conclusion: 'cancelled',
      head_branch: frozen.branch,
      head_sha: frozen.commitSha,
      run_started_at: frozen.startedAt,
      updated_at: frozen.completedAt,
    },
    workflow: {
      id: frozen.workflowId,
      name: frozen.workflowName,
      path: frozen.workflowPath,
      state: 'active',
    },
    comparison: {
      status: 'ahead',
      base_commit: { sha: frozen.commitSha },
      merge_base_commit: { sha: frozen.commitSha },
      head_commit: { sha: CURRENT_SHA },
    },
    workflowSource: `name: Generate Pack
env:
  PACK_PRODUCTION_CLI_VERSION: '2.14.1'
jobs:
  evaluate:
    steps:
      - run: |
          command --model sonnet \\
            --judge-model gpt-5.5 \\
          GENERATION_ID=$(node -e "process.stdout.write(require('node:crypto').randomUUID())")
          jq '.scenarios[0].generationId = $generationId | .workflowBinding = {' plan.json
`,
  };
}

function artifact(name, id, size = 1024) {
  return {
    id,
    name,
    size_in_bytes: size,
    expired: false,
    created_at: '2026-07-16T01:01:00.000Z',
    updated_at: '2026-07-16T01:01:01.000Z',
    workflow_run: {
      id: 12345,
      head_sha: SOURCE_SHA,
      head_branch: 'main',
    },
  };
}

function artifactIndex(names = ['pack-production-plan']) {
  const artifacts = names.map((name, index) => artifact(name, index + 100));
  return { total_count: artifacts.length, artifacts };
}

function scenario(generationId = GENERATION_ID) {
  return {
    id: 'spreadsheet-audit',
    version: '1.0.0',
    task: 'Produce and verify a spreadsheet audit artifact.',
    slug: 'spreadsheet-audit-pack',
    name: 'Spreadsheet Audit Pack',
    tags: ['spreadsheet', 'audit'],
    capabilitySlots: [{ id: 'workbook', required: true, keywords: ['xlsx'] }],
    requiredArtifacts: [{ id: 'workbook', kind: 'xlsx' }],
    ...(generationId ? { generationId } : {}),
  };
}

function createInput({ generationId = GENERATION_ID, artifacts, diagnostics = null } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'pack-cancellation-recovery-'));
  const planDir = join(root, 'plan');
  const diagnosticsDir = join(root, 'diagnostics');
  const outputDir = join(root, 'result');
  mkdirSync(planDir, { recursive: true });
  mkdirSync(diagnosticsDir, { recursive: true });
  mkdirSync(outputDir, { recursive: true });
  const frozen = source();
  json(join(planDir, 'plan.json'), {
    schemaVersion: 'pack-production-queue/v1',
    source: 'signals',
    scenarios: [scenario(generationId)],
    workflowBinding: {
      repository: frozen.repository,
      workflow: frozen.workflowName,
      runId: String(frozen.runId),
      runAttempt: frozen.runAttempt,
      commitSha: frozen.commitSha,
      scenarioId: 'spreadsheet-audit',
    },
  });
  json(join(planDir, 'cli-identity.json'), { version: '2.14.1', sha256: CLI_SHA });
  if (diagnostics) {
    for (const [name, value] of Object.entries(diagnostics)) {
      if (typeof value === 'string') writeFileSync(join(diagnosticsDir, name), value);
      else json(join(diagnosticsDir, name), value);
    }
  }
  return {
    ...metadata(),
    artifactIndex: artifactIndex(artifacts ?? (diagnostics
      ? ['pack-production-plan', 'pack-production-diagnostics']
      : ['pack-production-plan'])),
    planDir,
    diagnosticsDir,
    outputDir,
  };
}

test('workflow_run inspection accepts only exact cancelled main schedule/dispatch runs', () => {
  const inspected = inspectWorkflowRunEvent(event());
  assert.equal(inspected.runId, 12345);
  assert.equal(inspected.runAttempt, 2);
  assert.equal(inspected.commitSha, SOURCE_SHA);
  assert.equal(inspectWorkflowRunEvent(event({ event: 'workflow_dispatch' })).event, 'workflow_dispatch');
  assert.throws(() => inspectWorkflowRunEvent(event({ conclusion: 'failure' })), /only cancelled/);
  assert.throws(() => inspectWorkflowRunEvent(event({ event: 'pull_request' })), /schedule or workflow_dispatch/);
  assert.throws(() => inspectWorkflowRunEvent(event({ head_branch: 'feature' })), /must run on main/);
  assert.throws(() => inspectWorkflowRunEvent({
    ...event(),
    repository: { full_name: 'attacker/fork' },
  }), /trusted Marketplace repository/);
});

test('immutable plan generation id produces a sanitized v4 candidate-null recovery', async () => {
  const input = createInput();
  const result = await prepareCancellationRecovery(input);
  assert.equal(result.outcome, 'candidate_null_prepared');
  assert.equal(result.generationId, GENERATION_ID);
  assert.equal(result.evidence.recoveryBinding.generationSource, 'immutable-plan');
  assert.match(result.evidence.recoveryBinding.planSha256, /^[0-9a-f]{64}$/);
  assert.match(result.evidence.recoveryBinding.cliIdentitySha256, /^[0-9a-f]{64}$/);
  assert.equal(result.evidence.recoveryBinding.diagnosticsBindingSha256, null);
  const evaluation = JSON.parse(readFileSync(join(input.outputDir, 'candidate-null.evaluation.json')));
  assert.equal(evaluation.schemaVersion, 'skillstore.pack-evaluation/v4');
  assert.equal(evaluation.outcome, 'infrastructure_failed');
  assert.equal(evaluation.candidate, null);
  assert.equal(evaluation.evidence.cliReport.schemaVersion, 'marketplace.pack-production-cli-evidence/v1');
  assert.equal(evaluation.evidence.cliReport.source, 'cancelled-run-recovery');
  assert.equal(
    evaluation.evidence.cliReport.sourceSchemaVersion,
    'marketplace.pack-production-cancellation-recovery/v1',
  );
  assert.equal(evaluation.evidence.cliReport.sourceEvidenceSha256, result.evidence.diagnosticSha256);
  assert.equal(evaluation.evidence.cliReport.infrastructureFailure.reason, 'terminal_report_missing');
  assert.equal(evaluation.evidence.cliReport.infrastructureFailure.errorCategory, null);
  assert.match(evaluation.evidence.cliReport.infrastructureFailure.diagnosticSha256, /^[0-9a-f]{64}$/);
  assert.equal(evaluation.evidence.cliReport.rawReport, undefined);
  assert.equal(evaluation.evidence.cliReport.rawReportSha256, undefined);
  assert.doesNotMatch(JSON.stringify(evaluation), /Bearer|helm_live_|PACK_EVALUATOR|rawError/);
});

test('recovery retries for one workflow_run produce byte-identical evaluation evidence', async () => {
  const first = createInput();
  const second = createInput();
  const firstResult = await prepareCancellationRecovery(first);
  const secondResult = await prepareCancellationRecovery(second);
  const firstBytes = readFileSync(join(first.outputDir, 'candidate-null.evaluation.json'));
  const secondBytes = readFileSync(join(second.outputDir, 'candidate-null.evaluation.json'));
  assert.deepEqual(secondBytes, firstBytes);
  assert.equal(secondResult.evaluationSha256, firstResult.evaluationSha256);
  assert.deepEqual(secondResult.evidence.recoveryBinding, firstResult.evidence.recoveryBinding);
  assert.doesNotMatch(RECOVERY_HELPER, /buildInfrastructureCliReport|buildApiEvaluation\(/);
});

test('bounded diagnostics may confirm but never replace the immutable plan generation binding', async () => {
  const progress = [
    {
      schemaVersion: 'marketplace.pack-production-progress/v1',
      seq: 1,
      at: '2026-07-16T01:02:00.000Z',
      event: 'scenario.started',
      scenarioId: 'spreadsheet-audit',
      generationId: GENERATION_ID,
    },
    {
      schemaVersion: 'marketplace.pack-production-progress/v1',
      seq: 2,
      at: '2026-07-16T01:03:00.000Z',
      event: 'scenario.signal_received',
      scenarioId: 'spreadsheet-audit',
      signal: 'SIGTERM',
    },
  ].map((item) => JSON.stringify(item)).join('\n') + '\n';
  const input = createInput({ diagnostics: { 'evaluate-progress.ndjson': progress } });
  const result = await prepareCancellationRecovery(input);
  assert.equal(result.outcome, 'candidate_null_prepared');
  assert.equal(result.generationId, GENERATION_ID);
  assert.equal(result.evidence.recoveryBinding.generationSource, 'immutable-plan');
});

test('missing or conflicting immutable generation provenance never invents an id', async () => {
  const missing = createInput({ generationId: null });
  const missingResult = await prepareCancellationRecovery(missing);
  assert.equal(missingResult.outcome, 'unrecoverable');
  assert.equal(missingResult.reason, 'immutable_plan_generation_id_invalid');
  assert.equal(missingResult.generationId, null);

  const progress = [GENERATION_ID, '22222222-2222-4222-8222-222222222222']
    .map((generationId, index) => JSON.stringify({
      schemaVersion: 'marketplace.pack-production-progress/v1',
      seq: index + 1,
      event: 'scenario.started',
      scenarioId: 'spreadsheet-audit',
      generationId,
    })).join('\n') + '\n';
  const conflicting = createInput({
    diagnostics: { 'evaluate-progress.ndjson': progress },
  });
  const conflictingResult = await prepareCancellationRecovery(conflicting);
  assert.equal(conflictingResult.outcome, 'unrecoverable');
  assert.equal(conflictingResult.reason, 'diagnostics_binding_invalid');
});

test('source attempt and artifact provenance are bound to the exact cancelled attempt window', async () => {
  const wrongAttempt = createInput();
  wrongAttempt.attempt.run_started_at = '2026-07-16T00:59:59.000Z';
  await assert.rejects(
    prepareCancellationRecovery(wrongAttempt),
    /Source attempt API response differs from the workflow_run event/,
  );

  const afterCompletion = createInput();
  afterCompletion.artifactIndex.artifacts[0].created_at = '2026-07-16T01:06:00.000Z';
  afterCompletion.artifactIndex.artifacts[0].updated_at = '2026-07-16T01:06:01.000Z';
  const result = await prepareCancellationRecovery(afterCompletion);
  assert.equal(result.outcome, 'unrecoverable');
  assert.equal(result.reason, 'immutable_plan_artifact_missing_or_ambiguous');

  const wrongRun = createInput();
  wrongRun.artifactIndex.artifacts[0].workflow_run.id = 99999;
  await assert.rejects(prepareCancellationRecovery(wrongRun), /not bound to the source run/);

  const legacySourceWorkflow = createInput();
  legacySourceWorkflow.workflowSource = legacySourceWorkflow.workflowSource.replace('randomUUID()', 'legacyId()');
  await assert.rejects(
    prepareCancellationRecovery(legacySourceWorkflow),
    /lacks immutable generation and workflow binding/,
  );
});

test('existing evaluator or downstream evidence blocks candidate-null synthesis', async () => {
  for (const existing of [
    'pack-production-evaluation',
    'pack-production-persisted',
    'pack-production-final',
  ]) {
    const input = createInput({ artifacts: ['pack-production-plan', existing] });
    const result = await prepareCancellationRecovery(input);
    assert.equal(result.outcome, 'unrecoverable');
    assert.equal(result.reason, 'trusted_evaluation_or_downstream_artifact_exists');
  }
});

test('a declared diagnostics artifact must actually download before recovery', async () => {
  const input = createInput({ artifacts: ['pack-production-plan', 'pack-production-diagnostics'] });
  const result = await prepareCancellationRecovery(input);
  assert.equal(result.outcome, 'unrecoverable');
  assert.equal(result.reason, 'diagnostics_download_missing_or_invalid');
});

test('an evaluator summary with a recorded report is never overwritten by recovery', async () => {
  const input = createInput({
    diagnostics: {
      'evaluate-summary.json': {
        schemaVersion: 'marketplace.pack-production-evaluate/v1',
        cliVersion: '2.14.1',
        cliSha256: CLI_SHA,
        attempts: [{ scenarioId: 'spreadsheet-audit', generationId: GENERATION_ID, status: 'completed' }],
        reports: [{ scenarioId: 'spreadsheet-audit', generationId: GENERATION_ID }],
        selectedGenerationId: null,
      },
    },
  });
  const result = await prepareCancellationRecovery(input);
  assert.equal(result.outcome, 'unrecoverable');
  assert.equal(result.reason, 'evaluator_report_recorded_before_cancellation');
});

test('persistence performs one narrow POST and requires no Pack or enrichment', async () => {
  const input = createInput();
  await prepareCancellationRecovery(input);
  const calls = [];
  const outputFile = join(input.outputDir, 'persist-result.json');
  const persisted = await persistCancellationRecovery({
    resultFile: join(input.outputDir, 'recovery-result.json'),
    evaluationFile: join(input.outputDir, 'candidate-null.evaluation.json'),
    apiUrl: 'https://skillstore.example',
    token: 'narrow-test-token',
    outputFile,
    fetchImpl: async (url, init) => {
      calls.push({ url: String(url), init });
      const request = JSON.parse(init.body.toString('utf8'));
      return new Response(JSON.stringify({
        data: {
          generationId: request.generationId,
          evaluationOutcome: 'infrastructure_failed',
          outcome: 'infrastructure_failed',
          replayed: true,
          pack: null,
          comparisonOf: null,
          autoPublishEligible: false,
          enrichment: {
            content: 'not_applicable',
            translation: 'not_applicable',
            contentDispatchNonce: null,
          },
        },
      }), { status: 200, headers: { 'content-type': 'application/json' } });
    },
  });
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, 'https://skillstore.example/api/automation/packs/production');
  assert.equal(calls[0].init.headers.Authorization, 'Bearer narrow-test-token');
  assert.equal(persisted.outcome, 'candidate_null_persisted');
  assert.equal(persisted.replayed, true);
  assert.equal(persisted.response.pack, null);
  assert.doesNotMatch(readFileSync(outputFile, 'utf8'), /narrow-test-token/);
});

test('persistence rejects any response that creates a Pack or dispatches enrichment', async () => {
  const input = createInput();
  await prepareCancellationRecovery(input);
  await assert.rejects(persistCancellationRecovery({
    resultFile: join(input.outputDir, 'recovery-result.json'),
    evaluationFile: join(input.outputDir, 'candidate-null.evaluation.json'),
    apiUrl: 'https://skillstore.example',
    token: 'narrow-test-token',
    outputFile: join(input.outputDir, 'bad-persist-result.json'),
    fetchImpl: async () => new Response(JSON.stringify({
      data: {
        generationId: GENERATION_ID,
        evaluationOutcome: 'infrastructure_failed',
        outcome: 'infrastructure_failed',
        pack: { id: 'forbidden' },
        comparisonOf: null,
        autoPublishEligible: false,
        enrichment: { content: 'dispatched', translation: 'not_applicable', contentDispatchNonce: null },
      },
    }), { status: 200 }),
  }), /no-Pack, no-enrichment/);
});

test('recovery workflow is secret-minimal, bounded, and retains evidence for 90 days', () => {
  assert.match(WORKFLOW, /workflow_run:[\s\S]*workflows: \[Generate Pack\][\s\S]*types: \[completed\][\s\S]*branches: \[main\]/);
  assert.match(WORKFLOW, /permissions:\n  actions: read\n  contents: read/);
  assert.match(WORKFLOW, /github\.event\.workflow_run\.conclusion == 'cancelled'/);
  assert.match(WORKFLOW, /workflow_run\.event == 'schedule'.*workflow_run\.event == 'workflow_dispatch'/s);
  assert.match(WORKFLOW, /runs-on: ubuntu-latest/);
  assert.match(WORKFLOW, /persist-credentials: false/);
  assert.equal((WORKFLOW.match(/run-id: \$\{\{ steps\.source\.outputs\.run_id \}\}/g) ?? []).length, 2);
  assert.match(WORKFLOW, /artifacts\?per_page=100/);
  assert.match(WORKFLOW, /actions\/runs\/\$RUN_ID\/attempts\/\$RUN_ATTEMPT/);
  assert.match(WORKFLOW, /compare\/\$SOURCE_SHA\.\.\.\$GITHUB_SHA/);
  assert.match(WORKFLOW, /contents\/\.github\/workflows\/generate-packs\.yml\?ref=\$SOURCE_SHA/);
  assert.match(WORKFLOW, /continue-on-error: true[\s\S]*name: pack-production-plan/);
  assert.match(WORKFLOW, /continue-on-error: true[\s\S]*name: pack-production-diagnostics/);
  assert.match(WORKFLOW, /if: steps\.prepare\.outputs\.outcome == 'candidate_null_prepared'/);
  assert.match(WORKFLOW, /PACK_PRODUCTION_AUTOMATION_KEY: \$\{\{ secrets\.PACK_PRODUCTION_AUTOMATION_KEY \}\}/);
  assert.doesNotMatch(WORKFLOW, /PACK_EVALUATOR_HELM_API_KEY|HELM_API_KEY|SUPABASE_SERVICE_ROLE|APP_PRIVATE_KEY/);
  assert.match(WORKFLOW, /retention-days: 90/);
  const secretIndex = WORKFLOW.indexOf('PACK_PRODUCTION_AUTOMATION_KEY:');
  const persistIndex = WORKFLOW.indexOf('Persist the exact candidate-null cancellation audit');
  assert.ok(secretIndex > persistIndex, 'write token must exist only inside the final persistence step');
});
