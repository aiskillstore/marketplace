import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  chmodSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const PACK_PRODUCTION = fileURLToPath(new URL('../pack-production.mjs', import.meta.url));
const PLAN_MODULE = new URL('../pack-production-plan.mjs', import.meta.url);
const GENERATION_ID = 'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0';
const HEAD_SHA = 'a'.repeat(40);
const CLI_ASSET = 'skillstore-cli-linux-x64';

function normalizeJson(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(normalizeJson);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, entry]) => [key, normalizeJson(entry)]),
    );
  }
  throw new Error('fixture value is not JSON');
}

function canonicalJson(value) {
  return JSON.stringify(normalizeJson(value));
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function scenario() {
  return {
    capabilitySlots: [
      { id: 'workbook', required: true },
      { id: 'validation', required: true },
    ],
    generationId: GENERATION_ID,
    id: 'excel-dashboard',
    name: 'Monthly Sales Excel Dashboard',
    requiredArtifacts: [
      { extensions: ['.xlsx'], id: 'workbook', minimumCount: 1 },
    ],
    slug: 'monthly-sales-excel-workbook',
    tags: ['excel', 'dashboard'],
    task: 'Create a real workbook.',
    version: '1.0.0',
  };
}

function parameters(slotCount = 2) {
  const maxCandidates = 2;
  const hiddenVariants = 3;
  const maxPackSkills = 4;
  const maxBestSingleCompetitors = slotCount * maxCandidates;
  const estimatedRequests = 2
    + 4
    + (3 * slotCount * maxCandidates)
    + 3
    + (hiddenVariants * (maxPackSkills + 2))
    + (2 * hiddenVariants)
    + (3 * hiddenVariants * maxBestSingleCompetitors)
    + (hiddenVariants * maxPackSkills * (maxPackSkills + 1));
  return {
    generation: {
      autoPublishThreshold: 8,
      baselineDelta: 1,
      finalRuns: 3,
      maxCandidates,
      pick: 4,
      runs: 1,
      threshold: 7,
    },
    proxy: {
      allowedModels: ['claude-sonnet-5', 'gpt-5.5'],
      contractProbes: 2,
      estimatedRequests,
      hiddenVariants,
      maxBestSingleCompetitors,
      maxCliPreflightRequests: 4,
      maxConcurrent: 4,
      maxPackSkills,
      maxRequests: 256,
      port: 18765,
      reservedRequests: estimatedRequests + 64,
      toolLoopHeadroom: 64,
      upstreamUrl: 'https://helm.easymeta.au',
    },
    resources: {
      addressSpaceBytes: 6_442_450_944,
      evaluatorOutputBytes: 16_777_216,
      maxProcesses: 256,
      proxyActivityBytes: 1_048_576,
      resultBytes: 268_435_456,
      resultFiles: 1000,
    },
    retries: {
      agentMaxRetries: 1,
      contractMaxRetries: 0,
      executorPreflightMaxAttempts: 2,
    },
    runtime: {
      claudeCodeVersion: '2.1.210',
      codexVersion: '0.139.0',
    },
    timeoutsMs: {
      agent: 360_000,
      contract: 30_000,
      evaluationBudget: 13_800_000,
      evaluatorHeartbeat: 60_000,
      executorPreflight: 360_000,
      executorPreflightAgent: 180_000,
      executorPreflightHeartbeat: 30_000,
      executorPreflightIdle: 240_000,
      executorPreflightOuterKillGrace: 5_000,
      executorPreflightOuter: 420_000,
      executorPreflightRetryDelay: 5_000,
      minimumFallback: 2_700_000,
      outerEvaluation: 14_400_000,
      outerEvaluationKillGrace: 30_000,
      processKillGrace: 3_000,
      proxyRequest: 600_000,
      proxyTtl: 14_400_000,
      scenario: 7_200_000,
      scenarioIdle: 1_200_000,
    },
    tokens: {
      contractProbeOutput: 16,
      maxOutput: 16_384,
    },
  };
}

function executionPlan() {
  const plannedScenario = scenario();
  const models = {
    judge: {
      identity: 'gpt-5.5',
      pinType: 'workflow-pinned alias',
      revision: 'workflow-pinned alias',
    },
    runner: {
      identity: 'claude-sonnet-5',
      pinType: 'workflow-pinned alias',
      revision: 'workflow-pinned alias',
    },
  };
  const cli = {
    assetName: CLI_ASSET,
    releaseAssetSha256: '21b1967e134622a40ae4d312278fa10d136103f0148887252f61e4e3b4536674',
    version: '2.14.2',
  };
  const boundParameters = parameters(plannedScenario.capabilitySlots.length);
  const unsigned = {
    executionBinding: {
      cli,
      evaluatorInputs: {
        configSha256: sha256(canonicalJson({ cli, models, parameters: boundParameters })),
        promptSha256: sha256(plannedScenario.task),
        rulesSha256: sha256(canonicalJson({
          capabilitySlots: plannedScenario.capabilitySlots,
          requiredArtifacts: plannedScenario.requiredArtifacts,
        })),
        scenarioSha256: sha256(canonicalJson(plannedScenario)),
      },
      executorPreflight: {
        generationId: '00000000-0000-4000-8000-000000000001',
        skillA: {
          canonicalId: 'pack-executor-preflight-a',
          contentSha256: 'b'.repeat(64),
          version: '1.0.0',
        },
        skillB: {
          canonicalId: 'pack-executor-preflight-b',
          contentSha256: 'c'.repeat(64),
          version: '1.0.0',
        },
        task: 'Invoke Skill pack-executor-preflight-a first and Skill pack-executor-preflight-b second. After both Skills load successfully, reply with exactly PACK_EVALUATOR_READY and nothing else.',
      },
      models,
      parameters: boundParameters,
      source: {
        files: [
          {
            gitBlobSha: '1'.repeat(40),
            path: '.github/workflows/generate-packs.yml',
            sha256: '1'.repeat(64),
          },
          {
            gitBlobSha: '2'.repeat(40),
            path: 'scripts/pack-evaluator-contract-smoke.mjs',
            sha256: '2'.repeat(64),
          },
          {
            gitBlobSha: '3'.repeat(40),
            path: 'scripts/pack-evaluator-preflight.sh',
            sha256: '3'.repeat(64),
          },
          {
            gitBlobSha: '4'.repeat(40),
            path: 'scripts/pack-evaluator-proxy.mjs',
            sha256: '4'.repeat(64),
          },
          {
            gitBlobSha: '5'.repeat(40),
            path: 'scripts/pack-production-plan.mjs',
            sha256: '5'.repeat(64),
          },
          {
            gitBlobSha: '6'.repeat(40),
            path: 'scripts/pack-production.mjs',
            sha256: '6'.repeat(64),
          },
        ],
        repositoryTreeSha: 'd'.repeat(40),
        skillsManifest: {
          fileCount: 1,
          sha256: 'f'.repeat(64),
          totalBytes: 1,
        },
        skillsTreeSha: 'e'.repeat(40),
      },
    },
    scenario: plannedScenario,
    schemaVersion: 'marketplace.pack-production-execution-plan/v1',
    workflowBinding: {
      generationId: GENERATION_ID,
      headSha: HEAD_SHA,
      repository: 'aiskillstore/marketplace',
      runAttempt: 1,
      runId: '123456789',
      scenarioId: plannedScenario.id,
      workflow: 'Generate Pack',
    },
  };
  return { ...unsigned, digest: sha256(canonicalJson(unsigned)) };
}

function writeCanonical(file, value) {
  writeFileSync(file, canonicalJson(value));
}

function mutatePlan(plan, mutate) {
  const changed = structuredClone(plan);
  mutate(changed);
  return changed;
}

function evaluateResult(plan) {
  const directory = mkdtempSync(join(tmpdir(), 'pack-execution-plan-evaluate-'));
  const cli = join(directory, CLI_ASSET);
  writeFileSync(cli, '#!/bin/sh\necho "skillstore-cli 2.14.2"\n');
  chmodSync(cli, 0o755);
  const planFile = join(directory, 'plan.json');
  writeCanonical(planFile, plan);
  return spawnSync(process.execPath, [
    PACK_PRODUCTION,
    'evaluate',
    '--plan', planFile,
    '--results-dir', join(directory, 'results'),
    '--cli', cli,
    '--skills-dir', directory,
  ], { encoding: 'utf8' });
}

function downstreamResult(command, plan) {
  const directory = mkdtempSync(join(tmpdir(), `pack-${command}-execution-plan-`));
  const planFile = join(directory, 'plan.json');
  writeCanonical(planFile, plan);
  return spawnSync(process.execPath, [
    PACK_PRODUCTION,
    command,
    '--plan', planFile,
    '--results-dir', directory,
  ], { encoding: 'utf8' });
}

for (const command of ['evaluate', 'verify']) {
  test(`${command} rejects deprecated model, CLI, and execution overrides before runtime`, () => {
    const directory = mkdtempSync(join(tmpdir(), `pack-${command}-deprecated-overrides-`));
    const planFile = join(directory, 'plan.json');
    writeCanonical(planFile, executionPlan());
    const result = spawnSync(process.execPath, [
      PACK_PRODUCTION,
      command,
      '--plan', planFile,
      '--model', 'changed-runner',
      '--judge-model', 'changed-judge',
      '--expected-cli-version', '0.0.0',
      '--max-candidates', '99',
    ], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, new RegExp(`${command} rejects deprecated execution override flag`));
    assert.match(result.stderr, /--model/);
    assert.match(result.stderr, /--judge-model/);
    assert.match(result.stderr, /--expected-cli-version/);
    assert.match(result.stderr, /--max-candidates/);
    assert.doesNotMatch(result.stderr, /--artifact-gate is required|--cli is required/);
  });
}

test('canonical execution Plan round-trips atomically and rejects non-canonical bytes', async () => {
  const {
    readExecutionPlan,
    writeExecutionPlanAtomic,
  } = await import(PLAN_MODULE);
  const directory = mkdtempSync(join(tmpdir(), 'pack-execution-plan-canonical-'));
  const planFile = join(directory, 'plan.json');
  const plan = executionPlan();

  await writeExecutionPlanAtomic(planFile, plan);
  assert.equal(readFileSync(planFile, 'utf8'), canonicalJson(plan));
  assert.deepEqual(await readExecutionPlan(planFile), plan);
  assert.equal(existsSync(`${planFile}.tmp`), false);

  writeFileSync(planFile, `${canonicalJson(plan)}\n`);
  await assert.rejects(readExecutionPlan(planFile), /canonical JSON bytes/);

  const duplicate = canonicalJson(plan).replace(
    '"schemaVersion":"marketplace.pack-production-execution-plan/v1"',
    '"schemaVersion":"marketplace.pack-production-execution-plan/v1","schemaVersion":"marketplace.pack-production-execution-plan/v1"',
  );
  writeFileSync(planFile, duplicate);
  await assert.rejects(readExecutionPlan(planFile), /canonical JSON bytes/);
});

const planMutations = [
  ['runId', (plan) => { plan.workflowBinding.runId = '987654321'; }],
  ['runAttempt', (plan) => { plan.workflowBinding.runAttempt = 2; }],
  ['headSha', (plan) => { plan.workflowBinding.headSha = 'f'.repeat(40); }],
  ['scenarioId', (plan) => { plan.workflowBinding.scenarioId = 'changed-scenario'; }],
  ['generationId', (plan) => {
    plan.workflowBinding.generationId = '22222222-2222-4222-8222-222222222222';
  }],
  ['runner identity', (plan) => { plan.executionBinding.models.runner.identity = 'claude-other'; }],
  ['runner revision', (plan) => { plan.executionBinding.models.runner.revision = 'claude-other'; }],
  ['judge identity', (plan) => { plan.executionBinding.models.judge.identity = 'gpt-other'; }],
  ['judge revision', (plan) => { plan.executionBinding.models.judge.revision = 'gpt-other'; }],
  ['CLI version', (plan) => { plan.executionBinding.cli.version = '2.14.1'; }],
  ['CLI asset name', (plan) => { plan.executionBinding.cli.assetName = 'other-cli'; }],
  ['CLI asset SHA', (plan) => { plan.executionBinding.cli.releaseAssetSha256 = '0'.repeat(64); }],
  ['evaluator prompt digest', (plan) => {
    plan.executionBinding.evaluatorInputs.promptSha256 = '0'.repeat(64);
  }],
  ['evaluator rules digest', (plan) => {
    plan.executionBinding.evaluatorInputs.rulesSha256 = '0'.repeat(64);
  }],
  ['evaluator config digest', (plan) => {
    plan.executionBinding.evaluatorInputs.configSha256 = '0'.repeat(64);
  }],
  ['script digest', (plan) => { plan.executionBinding.source.files[0].sha256 = '0'.repeat(64); }],
  ['Skills bytes manifest', (plan) => {
    plan.executionBinding.source.skillsManifest.sha256 = '0'.repeat(64);
  }],
  ['skills tree', (plan) => { plan.executionBinding.source.skillsTreeSha = '0'.repeat(40); }],
  ['repository tree', (plan) => {
    plan.executionBinding.source.repositoryTreeSha = '0'.repeat(40);
  }],
  ['scenario digest', (plan) => {
    plan.executionBinding.evaluatorInputs.scenarioSha256 = '0'.repeat(64);
  }],
  ['scenario bytes', (plan) => { plan.scenario.task = 'Changed task bytes.'; }],
  ['threshold', (plan) => { plan.executionBinding.parameters.generation.threshold = 6; }],
  ['timeout', (plan) => { plan.executionBinding.parameters.timeoutsMs.scenario = 1; }],
  ['budget', (plan) => { plan.executionBinding.parameters.proxy.maxRequests = 255; }],
  ['output cap', (plan) => { plan.executionBinding.parameters.tokens.maxOutput = 8192; }],
  ['resource limit', (plan) => {
    plan.executionBinding.parameters.resources.maxProcesses = 255;
  }],
];

for (const [name, mutate] of planMutations) {
  for (const command of ['evaluate', 'persist', 'finalize']) {
    test(`${command} rejects a changed ${name} from an old Plan`, () => {
      const changed = mutatePlan(executionPlan(), mutate);
      const result = command === 'evaluate'
        ? evaluateResult(changed)
        : downstreamResult(command, changed);
      assert.notEqual(result.status, 0);
      assert.match(result.stderr, /execution Plan digest mismatch/);
      assert.doesNotMatch(result.stderr, /--token is required|--api-url is required/);
    });
  }
}

function artifactState(plan, producerStatus = 'success', artifactStatus = 'downloaded') {
  return {
    artifact: {
      name: 'pack-production-evaluation',
      planDigest: plan.digest,
      status: artifactStatus,
    },
    producer: {
      name: 'evaluate',
      status: producerStatus,
    },
    schemaVersion: 'marketplace.pack-production-artifact-state/v1',
    workflowBinding: plan.workflowBinding,
  };
}

function artifactGateResult(state, plan = executionPlan()) {
  const directory = mkdtempSync(join(tmpdir(), 'pack-artifact-gate-'));
  const planFile = join(directory, 'plan.json');
  const stateFile = join(directory, 'state.json');
  const outputFile = join(directory, 'gate.json');
  writeCanonical(planFile, plan);
  writeCanonical(stateFile, state);
  const result = spawnSync(process.execPath, [
    PACK_PRODUCTION,
    'artifact-gate',
    '--plan', planFile,
    '--state', stateFile,
    '--output', outputFile,
  ], { encoding: 'utf8' });
  return { directory, outputFile, result };
}

test('same-Plan producer and downloaded artifact pass the runtime artifact gate', () => {
  const plan = executionPlan();
  const { outputFile, result } = artifactGateResult(artifactState(plan), plan);
  assert.equal(result.status, 0, result.stderr);
  const gate = JSON.parse(readFileSync(outputFile, 'utf8'));
  assert.equal(gate.planDigest, plan.digest);
  assert.equal(gate.producer.status, 'success');
  assert.equal(gate.artifact.status, 'downloaded');
  assert.match(gate.digest, /^[0-9a-f]{64}$/);
});

for (const status of ['missing', 'failed', 'cancelled', 'skipped']) {
  test(`artifact gate fails closed for ${status} producer state`, () => {
    const plan = executionPlan();
    const { result } = artifactGateResult(artifactState(plan, status), plan);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /producer status must be success/);
  });

  test(`artifact gate fails closed for ${status} artifact state`, () => {
    const plan = executionPlan();
    const { result } = artifactGateResult(artifactState(plan, 'success', status), plan);
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /artifact status must be downloaded/);
  });
}

test('artifact gate rejects an artifact made under a different complete Plan', () => {
  const plan = executionPlan();
  const changed = structuredClone(plan);
  changed.workflowBinding.runAttempt = 2;
  const { digest: _digest, ...unsigned } = changed;
  changed.digest = sha256(canonicalJson(unsigned));
  const { result } = artifactGateResult(artifactState(plan), changed);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /artifact state differs from the execution Plan/);
});

for (const command of ['persist', 'finalize']) {
  test(`${command} rejects a changed Plan before any downstream write or publish action`, () => {
    const original = executionPlan();
    const { outputFile, result: gateResult } = artifactGateResult(artifactState(original), original);
    assert.equal(gateResult.status, 0, gateResult.stderr);
    const changed = mutatePlan(original, (plan) => {
      plan.workflowBinding.headSha = 'f'.repeat(40);
    });
    const directory = mkdtempSync(join(tmpdir(), `pack-${command}-plan-gate-`));
    const planFile = join(directory, 'plan.json');
    writeCanonical(planFile, changed);
    const result = spawnSync(process.execPath, [
      PACK_PRODUCTION,
      command,
      '--plan', planFile,
      '--artifact-gate', outputFile,
      '--results-dir', directory,
    ], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /execution Plan digest mismatch/);
    assert.doesNotMatch(result.stderr, /--token is required|--api-url is required/);
  });
}
