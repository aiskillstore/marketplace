#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const CLI_SCHEMA = 'pack-generation-evaluation/v2';
const API_SCHEMA = 'skillstore.pack-evaluation/v2';
const STATUS_SCHEMA = 'skillstore.pack-production-status/v1';
const READBACK_SCHEMA = 'skillstore.pack-production-readback/v1';
const SLO_SCHEMA = 'marketplace.pack-production-slo/v1';
const VERIFICATION_SCHEMA = 'marketplace.pack-production-evaluation-verification/v1';
const KNOWN_CLI_EXIT = new Map([
  ['candidate_ready', 0],
  ['quality_rejected', 10],
  ['evaluation_inconclusive', 20],
  ['infrastructure_failed', 30],
]);

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const args = { command };
  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (!token.startsWith('--')) fail(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    const value = rest[index + 1];
    if (!value || value.startsWith('--')) fail(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function required(args, name) {
  const value = args[name];
  if (!value) fail(`--${name} is required`);
  return value;
}

function positiveInteger(value, name, fallback) {
  if (value == null) return fallback;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) fail(`--${name} must be a positive integer`);
  return parsed;
}

function normalizeJson(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(normalizeJson);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, entry]) => entry !== undefined)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, entry]) => [key, normalizeJson(entry)]),
    );
  }
  fail('Value is not canonical JSON');
}

export function canonicalJson(value) {
  return JSON.stringify(normalizeJson(value));
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

async function sha256File(file) {
  return sha256(await readFile(file));
}

async function readJson(file) {
  return JSON.parse(await readFile(file, 'utf8'));
}

async function writeJson(file, value) {
  await writeFile(file, `${JSON.stringify(value, null, 2)}\n`);
}

function cliVersion(cli) {
  const result = spawnSync(cli, ['--version'], { encoding: 'utf8' });
  if (result.status !== 0) fail(`Cannot read CLI version: ${result.stderr || result.stdout}`);
  const version = `${result.stdout}\n${result.stderr}`.match(/[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z._-]+)?/)?.[0];
  if (!version) fail('CLI version output is not parseable');
  return version;
}

function artifactReferences(raw) {
  const evidence = raw.packVerification?.artifactEvidence ?? [];
  return [...new Set(evidence.flatMap((run) => {
    const required = (run.requirements ?? []).flatMap((requirement) => requirement.validMatches ?? []);
    if (required.length > 0) return required;
    return (run.artifacts ?? [])
      .filter((artifact) => artifact.valid)
      .map((artifact) => artifact.relativePath);
  }))].slice(0, 20);
}

function apiVerdicts(raw) {
  return (raw.packVerification?.verdicts ?? []).map((verdict) => ({
    usedSkill: Boolean(verdict.used_skill),
    taskCompleted: Boolean(verdict.task_completed),
    envBlocked: Boolean(verdict.env_blocked),
    score: Number(verdict.score),
    reason: String(verdict.reason || 'No grader reason supplied'),
    issues: Array.isArray(verdict.issues) ? verdict.issues.map(String) : [],
  }));
}

export function buildApiEvaluation(raw, context) {
  if (raw.schemaVersion !== CLI_SCHEMA) fail(`Unsupported CLI report schema: ${raw.schemaVersion}`);
  if (!KNOWN_CLI_EXIT.has(raw.outcome)) fail(`Unsupported CLI outcome: ${raw.outcome}`);
  if (raw.generationId !== context.generationId) fail('CLI report generationId changed during evaluation');
  if (raw.scenario?.id !== context.scenarioId) fail('CLI report scenario differs from the queue plan');

  let candidate = null;
  if (raw.outcome === 'candidate_ready') {
    const summary = raw.packVerification?.summary;
    const baseline = raw.baselineVerification?.summary;
    const verdicts = apiVerdicts(raw);
    if (!raw.manifest || !summary || !baseline || verdicts.length === 0) {
      fail('candidate_ready report lacks manifest, pack verification, baseline, or verdicts');
    }
    const references = artifactReferences(raw);
    const artifactKind = raw.scenario.requiredArtifacts?.length > 0 ? 'file' : 'text';
    const produced = artifactKind === 'file' ? references.length > 0 : summary.taskCompletedRate === 1;
    candidate = {
      manifest: {
        name: raw.manifest.name,
        slug: raw.manifest.slug,
        description: raw.manifest.description,
        scenarioTags: raw.manifest.scenario_tags,
        riskFlags: raw.manifest.risk_flags,
        skills: raw.manifest.skills,
        rationale: raw.manifest.rationale,
      },
      fitness: {
        score: summary.medianScore,
        passed: Boolean(summary.passed && summary.usedSkillEver),
        runs: verdicts.length,
        usedSkillRate: summary.usedSkillRate,
        taskCompletionRate: summary.taskCompletedRate,
        envBlockedRate: summary.envBlockedRate,
        artifact: {
          kind: artifactKind,
          produced,
          verified: Boolean(produced && summary.artifactsPassed),
          references,
        },
        baseline: {
          score: baseline.medianScore,
          improvement: summary.medianScore - baseline.medianScore,
        },
        verdicts,
        errors: [
          ...(raw.packVerification?.errors ?? []).map((error) => `pack: ${error}`),
          ...(raw.baselineVerification?.errors ?? []).map((error) => `baseline: ${error}`),
        ],
      },
    };
  }

  const unsigned = {
    schemaVersion: API_SCHEMA,
    generationId: context.generationId,
    workflow: {
      repository: 'aiskillstore/marketplace',
      runId: context.runId,
      runAttempt: context.runAttempt,
      runUrl: `https://github.com/aiskillstore/marketplace/actions/runs/${context.runId}`,
      commitSha: context.commitSha,
    },
    scenario: {
      id: raw.scenario.id,
      version: String(raw.scenario.version),
      task: raw.scenario.task,
      slug: raw.scenario.slug,
      name: raw.scenario.name,
      tags: raw.scenario.tags,
    },
    evaluator: {
      cliVersion: context.cliVersion,
      cliSha256: context.cliSha256,
      model: context.model,
      judgeModel: context.judgeModel,
      startedAt: raw.evaluationStartedAt,
      completedAt: raw.evaluationCompletedAt,
    },
    outcome: raw.outcome,
    candidate,
    evidence: { cliReport: raw },
  };
  return { ...unsigned, evidenceDigest: sha256(canonicalJson(unsigned)) };
}

function workflowContext(args, generationId, scenarioId, cli, version, checksum) {
  const runId = required(args, 'run-id');
  if (!/^[1-9][0-9]*$/.test(runId)) fail('--run-id must be a GitHub Actions numeric run id');
  const runAttempt = positiveInteger(args['run-attempt'], 'run-attempt', 1);
  const commitSha = required(args, 'commit-sha');
  if (!/^[0-9a-f]{40}$/.test(commitSha)) fail('--commit-sha must be a 40-character lowercase SHA');
  return {
    generationId,
    scenarioId,
    runId,
    runAttempt,
    commitSha,
    cli,
    cliVersion: version,
    cliSha256: checksum,
    model: args.model ?? 'sonnet',
    judgeModel: args['judge-model'] ?? 'gpt-5.5',
  };
}

async function evaluate(args) {
  const cli = resolve(required(args, 'cli'));
  const plan = await readJson(resolve(required(args, 'plan')));
  const resultsDir = resolve(required(args, 'results-dir'));
  const skillsDir = resolve(required(args, 'skills-dir'));
  if (plan.schemaVersion !== 'pack-production-queue/v1') fail(`Unsupported plan schema: ${plan.schemaVersion}`);
  if (!Array.isArray(plan.scenarios) || plan.scenarios.length < 1 || plan.scenarios.length > 3) {
    fail('Plan must contain one to three scenarios');
  }
  await mkdir(resultsDir, { recursive: true });

  const version = cliVersion(cli);
  const expectedVersion = required(args, 'expected-cli-version');
  if (version !== expectedVersion) fail(`CLI version mismatch: expected ${expectedVersion}, got ${version}`);
  const checksum = await sha256File(cli);
  const reports = [];
  const hasEvaluatorIdentity = args['evaluator-uid'] != null || args['evaluator-gid'] != null;
  if (hasEvaluatorIdentity && (args['evaluator-uid'] == null || args['evaluator-gid'] == null)) {
    fail('--evaluator-uid and --evaluator-gid must be supplied together');
  }
  const evaluatorUid = hasEvaluatorIdentity
    ? positiveInteger(args['evaluator-uid'], 'evaluator-uid')
    : undefined;
  const evaluatorGid = hasEvaluatorIdentity
    ? positiveInteger(args['evaluator-gid'], 'evaluator-gid')
    : undefined;
  const evaluatorCwd = hasEvaluatorIdentity
    ? resolve(required(args, 'evaluator-cwd'))
    : process.cwd();
  if (hasEvaluatorIdentity && typeof process.getuid === 'function' && process.getuid() !== 0) {
    fail('Evaluator identity separation requires a root orchestrator');
  }

  for (const scenario of plan.scenarios) {
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id || '')) fail(`Unsafe scenario id: ${scenario.id}`);
    const ordinal = String(reports.length + 1).padStart(2, '0');
    const generationId = randomUUID();
    const context = workflowContext(args, generationId, scenario.id, cli, version, checksum);
    const commandArgs = [
      'pack', 'generate',
      '--scenario', scenario.id,
      '--generation-id', generationId,
      '--skills-dir', skillsDir,
      '--max-candidates', args['max-candidates'] ?? '3',
      '--pick', args.pick ?? '4',
      '--model', context.model,
      '--judge-model', context.judgeModel,
      '--runs', args.runs ?? '1',
      '--final-runs', args['final-runs'] ?? '3',
      '--threshold', args.threshold ?? '7',
      '--baseline-delta', args['baseline-delta'] ?? '1',
      '--auto-publish-threshold', args['auto-publish-threshold'] ?? '8',
      '--json',
    ];
    const result = spawnSync(cli, commandArgs, {
      cwd: evaluatorCwd,
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
      ...(hasEvaluatorIdentity ? { uid: evaluatorUid, gid: evaluatorGid } : {}),
      env: {
        ...process.env,
        SKILLSTORE_AGENT_ENV_MODE: 'strict',
      },
    });
    if (result.error) fail(`Evaluator process failed for ${scenario.id}: ${result.error.message}`);
    await writeFile(resolve(resultsDir, `${ordinal}-${scenario.id}.stdout.json`), result.stdout || '');
    await writeFile(resolve(resultsDir, `${ordinal}-${scenario.id}.run.log`), result.stderr || '');
    let raw;
    try {
      raw = JSON.parse(result.stdout);
    } catch {
      fail(`Evaluator returned invalid JSON for ${scenario.id} (exit ${result.status}): ${result.stderr}`);
    }
    const expectedExit = KNOWN_CLI_EXIT.get(raw.outcome);
    if (result.status !== expectedExit) {
      fail(`Evaluator exit/outcome mismatch for ${scenario.id}: exit ${result.status}, outcome ${raw.outcome}`);
    }
    const evaluation = buildApiEvaluation(raw, context);
    const file = resolve(resultsDir, `${ordinal}-${scenario.id}.evaluation.json`);
    await writeJson(file, evaluation);
    reports.push({
      scenarioId: scenario.id,
      generationId,
      outcome: raw.outcome,
      outcomeReason: raw.outcomeReason,
      file,
    });
    if (raw.outcome === 'candidate_ready') break;
  }

  const summary = {
    schemaVersion: 'marketplace.pack-production-evaluate/v1',
    cliVersion: version,
    cliSha256: checksum,
    reports,
    selectedGenerationId: reports.find((report) => report.outcome === 'candidate_ready')?.generationId ?? null,
  };
  await writeJson(resolve(resultsDir, 'evaluate-summary.json'), summary);
  process.stdout.write(`${JSON.stringify(summary)}\n`);
}

async function verifyEvaluation(args) {
  const cli = resolve(required(args, 'cli'));
  const plan = await readJson(resolve(required(args, 'plan')));
  const resultsDir = resolve(required(args, 'results-dir'));
  const summary = await readJson(resolve(resultsDir, 'evaluate-summary.json'));
  if (plan.schemaVersion !== 'pack-production-queue/v1') fail(`Unsupported plan schema: ${plan.schemaVersion}`);
  if (!Array.isArray(plan.scenarios) || plan.scenarios.length < 1 || plan.scenarios.length > 3) {
    fail('Plan must contain one to three scenarios');
  }
  if (summary.schemaVersion !== 'marketplace.pack-production-evaluate/v1') {
    fail(`Unsupported evaluate summary schema: ${summary.schemaVersion}`);
  }
  if (!Array.isArray(summary.reports) || summary.reports.length < 1 || summary.reports.length > plan.scenarios.length) {
    fail('Evaluate summary report count is outside the immutable plan');
  }

  const version = cliVersion(cli);
  const expectedVersion = required(args, 'expected-cli-version');
  if (version !== expectedVersion || summary.cliVersion !== version) {
    fail(`Evaluation CLI version mismatch: expected ${expectedVersion}, got ${version}/${summary.cliVersion}`);
  }
  const checksum = await sha256File(cli);
  if (summary.cliSha256 !== checksum) fail('Evaluation CLI checksum differs from the trusted CLI');

  const expectedFiles = [];
  const verifiedFiles = [];
  let selectedGenerationId = null;
  let candidateSeen = false;
  for (const [index, report] of summary.reports.entries()) {
    const scenario = plan.scenarios[index];
    if (!scenario || report.scenarioId !== scenario.id) fail('Evaluate summary scenario order differs from the plan');
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id)) fail(`Unsafe scenario id: ${scenario.id}`);
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(report.generationId || '')) {
      fail(`Invalid generation id for ${scenario.id}`);
    }
    if (candidateSeen) fail('Evaluate summary contains reports after a ready candidate');

    const ordinal = String(index + 1).padStart(2, '0');
    const prefix = `${ordinal}-${scenario.id}`;
    const stdoutFile = `${prefix}.stdout.json`;
    const evaluationFile = `${prefix}.evaluation.json`;
    if (basename(String(report.file || '')) !== evaluationFile) {
      fail(`Evaluate summary file differs from the deterministic path for ${scenario.id}`);
    }
    const raw = await readJson(resolve(resultsDir, stdoutFile));
    if (raw.outcome !== report.outcome || raw.outcomeReason !== report.outcomeReason) {
      fail(`Evaluate summary outcome differs from stdout for ${scenario.id}`);
    }
    const context = workflowContext(args, report.generationId, scenario.id, cli, version, checksum);
    const rebuilt = buildApiEvaluation(raw, context);
    const recorded = await readJson(resolve(resultsDir, evaluationFile));
    if (canonicalJson(recorded) !== canonicalJson(rebuilt)) {
      fail(`Evaluation artifact differs from trusted reconstruction for ${scenario.id}`);
    }
    expectedFiles.push(evaluationFile);
    verifiedFiles.push({ file: evaluationFile, sha256: await sha256File(resolve(resultsDir, evaluationFile)) });
    if (raw.outcome === 'candidate_ready') {
      candidateSeen = true;
      selectedGenerationId = report.generationId;
    }
  }

  if ((summary.selectedGenerationId ?? null) !== selectedGenerationId) {
    fail('Evaluate summary selected generation is inconsistent with verified outcomes');
  }
  const actualFiles = (await readdir(resultsDir)).filter((file) => file.endsWith('.evaluation.json')).sort();
  if (canonicalJson(actualFiles) !== canonicalJson([...expectedFiles].sort())) {
    fail('Evaluation artifact set is not the exact trusted closure');
  }
  const verification = {
    schemaVersion: VERIFICATION_SCHEMA,
    cliVersion: version,
    cliSha256: checksum,
    selectedGenerationId,
    files: verifiedFiles.sort((left, right) => left.file.localeCompare(right.file)),
  };
  await writeJson(resolve(resultsDir, 'evaluation-verification.json'), verification);
  process.stdout.write(`${JSON.stringify(verification)}\n`);
}

async function apiRequest(url, token, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  });
  const text = await response.text();
  let body = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = { message: text };
  }
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status} from ${url}: ${text.slice(0, 2000)}`);
    error.status = response.status;
    error.body = body;
    throw error;
  }
  return body;
}

function apiBase(args) {
  return required(args, 'api-url').replace(/\/$/, '');
}

export function buildPublicReadbackExpectation(persisted, selected, publicSlug) {
  const generationId = selected?.generationId;
  const packId = selected?.pack?.id;
  if (typeof generationId !== 'string' || !generationId) {
    fail('Persist response did not bind the selected generation');
  }
  if (typeof packId !== 'string' || !packId) {
    fail('Persist response did not bind the selected Pack id');
  }
  if (typeof publicSlug !== 'string' || !publicSlug) {
    fail('Publish response did not bind the public Pack slug');
  }
  const persistedAttempt = persisted?.persisted?.find(
    (item) => item?.request?.generationId === generationId,
  );
  const skillSlugs = persistedAttempt?.request?.candidate?.manifest?.skills;
  if (!Array.isArray(skillSlugs) || skillSlugs.length < 1 || skillSlugs.some(
    (slug) => typeof slug !== 'string' || !slug,
  )) {
    fail('Persisted candidate evidence did not contain exact Skill slugs');
  }
  return { generationId, packId, publicSlug, skillSlugs: [...skillSlugs] };
}

export function validatePublicPackReadback(pack, expected) {
  const mismatches = [];
  if (!pack || typeof pack !== 'object') {
    return { matched: false, mismatches: ['response data is not a Pack object'], actualSkillSlugs: [] };
  }
  if (pack.id !== expected.packId) {
    mismatches.push(`Pack id mismatch: expected ${expected.packId}, got ${String(pack.id ?? 'missing')}`);
  }
  if (pack.slug !== expected.publicSlug) {
    mismatches.push(`Pack slug mismatch: expected ${expected.publicSlug}, got ${String(pack.slug ?? 'missing')}`);
  }
  // The public Pack detail contract is camelCase even though the database field
  // is review_status.
  if (pack.reviewStatus !== 'approved') {
    mismatches.push(`Pack reviewStatus is ${String(pack.reviewStatus ?? 'missing')}, expected approved`);
  }
  const actualSkillSlugs = Array.isArray(pack.skills)
    ? pack.skills.map((skill) => skill?.slug)
    : [];
  if (actualSkillSlugs.some((slug) => typeof slug !== 'string')) {
    mismatches.push('Pack skills contain a missing or invalid slug');
  } else if (
    actualSkillSlugs.length !== expected.skillSlugs.length ||
    actualSkillSlugs.some((slug, index) => slug !== expected.skillSlugs[index])
  ) {
    mismatches.push(
      `Pack Skill slugs mismatch: expected ${expected.skillSlugs.join(',')}, got ${actualSkillSlugs.join(',')}`,
    );
  }
  return { matched: mismatches.length === 0, mismatches, actualSkillSlugs };
}

export async function readExactPublicPack(base, expected, fetchImpl = fetch) {
  const response = await fetchImpl(
    `${base}/api/packs/${encodeURIComponent(expected.publicSlug)}?lang=en`,
    { headers: { Accept: 'application/json', 'Cache-Control': 'no-cache' } },
  );
  if (!response.ok) {
    return { pack: null, mismatches: [`public Pack API returned HTTP ${response.status}`] };
  }
  let body;
  try {
    body = await response.json();
  } catch {
    return { pack: null, mismatches: ['public Pack API returned invalid JSON'] };
  }
  const pack = body?.data;
  const validation = validatePublicPackReadback(pack, expected);
  return {
    pack: validation.matched ? pack : null,
    mismatches: validation.mismatches,
  };
}

async function persist(args) {
  const resultsDir = resolve(required(args, 'results-dir'));
  const token = required(args, 'token');
  const base = apiBase(args);
  const verification = await readJson(resolve(resultsDir, 'evaluation-verification.json'));
  if (verification.schemaVersion !== VERIFICATION_SCHEMA || !Array.isArray(verification.files)) {
    fail('Trusted evaluation verification is missing or invalid');
  }
  const files = (await readdir(resultsDir))
    .filter((file) => file.endsWith('.evaluation.json'))
    .sort();
  if (files.length === 0) fail('No evaluation artifacts found to persist');
  const verifiedFiles = verification.files.map((entry) => entry?.file).sort();
  if (canonicalJson(files) !== canonicalJson(verifiedFiles)) {
    fail('Persist artifact set differs from the trusted evaluation closure');
  }
  for (const entry of verification.files) {
    if (typeof entry?.file !== 'string' || !/^\d{2}-[a-z0-9][a-z0-9-]{0,79}\.evaluation\.json$/.test(entry.file)) {
      fail(`Invalid verification filename: ${entry?.file}`);
    }
    if (!/^[0-9a-f]{64}$/.test(entry?.sha256 || '')) fail(`Invalid verification hash for ${entry?.file}`);
    if (await sha256File(resolve(resultsDir, entry.file)) !== entry.sha256) {
      fail(`Persist artifact hash differs from trusted verification: ${entry.file}`);
    }
  }

  const persisted = [];
  for (const file of files) {
    const evaluation = await readJson(resolve(resultsDir, file));
    const response = await apiRequest(`${base}/api/automation/packs/production`, token, {
      method: 'POST',
      body: JSON.stringify(evaluation),
    });
    persisted.push({ file, request: evaluation, response });
  }
  const summary = {
    schemaVersion: 'marketplace.pack-production-persist/v1',
    persisted,
    selected: persisted.find((item) => item.request.outcome === 'candidate_ready')?.response?.data ?? null,
  };
  await writeJson(resolve(resultsDir, 'persist-summary.json'), summary);
  process.stdout.write(`${JSON.stringify(summary)}\n`);
}

function readiness(attempt) {
  const state = attempt.packReadiness ?? attempt.readiness ?? null;
  if (!state) return null;
  if (typeof state.contentReady === 'boolean' && typeof state.translationReady === 'boolean') {
    return {
      contentReady: state.contentReady,
      translationReady: state.translationReady,
      blockers: state.blockers ?? [],
    };
  }
  const cover = state.coverImageUrl ?? state.cover_image_url;
  const guide = state.usageGuideStatus ?? state.usage_guide_status;
  const translation = state.translationStatus ?? state.translation_status;
  return {
    contentReady: Boolean(cover) && guide === 'completed',
    translationReady: translation === 'completed',
    cover,
    guide,
    translation,
  };
}

export function buildSloResult(value, checkedAt = new Date().toISOString()) {
  if (!value || typeof value !== 'object') fail('Pack production SLO response is missing');
  const windowDays = Number(value.windowDays);
  const target = Number(value.target);
  const publishedReadbackPassed = Number(value.publishedReadbackPassed);
  if (windowDays !== 7) fail(`Pack production SLO window must be 7 days, got ${value.windowDays}`);
  if (target !== 2) fail(`Pack production SLO target must be 2, got ${value.target}`);
  if (!Number.isSafeInteger(publishedReadbackPassed) || publishedReadbackPassed < 0) {
    fail('Pack production SLO published count is invalid');
  }
  if (typeof value.met !== 'boolean' || value.met !== (publishedReadbackPassed >= target)) {
    fail('Pack production SLO met flag is inconsistent with its count and target');
  }
  if (typeof value.windowStartedAt !== 'string' || !Number.isFinite(Date.parse(value.windowStartedAt))) {
    fail('Pack production SLO window start is invalid');
  }
  return {
    schemaVersion: SLO_SCHEMA,
    checkedAt,
    windowDays,
    windowStartedAt: value.windowStartedAt,
    target,
    publishedReadbackPassed,
    met: value.met,
  };
}

async function patchStatus(base, token, generationId, body) {
  return apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
    method: 'PATCH',
    body: JSON.stringify({ schemaVersion: STATUS_SCHEMA, ...body }),
  });
}

function wait(milliseconds) {
  return new Promise((resolveWait) => setTimeout(resolveWait, milliseconds));
}

async function finalize(args) {
  const resultsDir = resolve(required(args, 'results-dir'));
  const persisted = await readJson(resolve(resultsDir, 'persist-summary.json'));
  const selected = persisted.selected;
  const rawOutcomes = persisted.persisted.map((item) => item.request.outcome);
  if (!selected) {
    if (rawOutcomes.some((outcome) => outcome === 'infrastructure_failed' || outcome === 'evaluation_inconclusive')) {
      fail(`No candidate was produced because evaluation was not conclusive: ${rawOutcomes.join(', ')}`);
    }
    const result = { outcome: 'quality_rejected', attempts: rawOutcomes.length };
    await writeJson(resolve(resultsDir, 'final-result.json'), result);
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  const token = required(args, 'token');
  const base = apiBase(args);
  const generationId = selected.generationId;
  const maxWaitSeconds = positiveInteger(args['max-wait-seconds'], 'max-wait-seconds', 1800);
  const pollSeconds = positiveInteger(args['poll-seconds'], 'poll-seconds', 30);
  const deadline = Date.now() + maxWaitSeconds * 1000;
  let attempt;
  let ready;
  while (Date.now() < deadline) {
    const response = await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token);
    const readback = response?.data;
    attempt = readback?.attempt ?? readback;
    ready = readiness(readback);
    if (ready?.contentReady && ready.translationReady) break;
    if (attempt?.outcome === 'enrichment_failed') {
      fail(`Enrichment failed for ${generationId}: ${attempt.last_error ?? 'unknown error'}`);
    }
    await wait(pollSeconds * 1000);
  }
  if (!ready?.contentReady || !ready.translationReady) {
    await patchStatus(base, token, generationId, {
      outcome: 'enrichment_failed',
      contentStatus: ready?.contentReady ? 'succeeded' : 'failed',
      translationStatus: ready?.translationReady ? 'succeeded' : 'failed',
      error: `enrichment readiness timed out after ${maxWaitSeconds}s`,
    });
    fail(`Enrichment timed out for ${generationId}`);
  }

  await patchStatus(base, token, generationId, {
    outcome: 'review_pending',
    contentStatus: 'succeeded',
    translationStatus: 'succeeded',
    error: null,
  });
  const autoPublishEnabled = (args['auto-publish'] ?? 'true') === 'true';
  if (!autoPublishEnabled || !selected.autoPublishEligible || selected.comparisonOf) {
    const result = {
      outcome: 'review_pending',
      generationId,
      pack: selected.pack,
      reason: selected.comparisonOf
        ? 'comparison candidates require human review'
        : !autoPublishEnabled
          ? 'automatic publish was disabled for this run'
          : 'candidate did not meet the automatic publish gate',
    };
    await writeJson(resolve(resultsDir, 'final-result.json'), result);
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  const publish = await apiRequest(
    `${base}/api/automation/packs/${encodeURIComponent(selected.pack.slug)}/publish`,
    token,
    { method: 'POST', body: JSON.stringify({ generationId }) },
  );
  const publicSlug = publish?.data?.slug;
  if (!publicSlug) fail('Publish response did not include the public slug');
  const expectedPublicPack = buildPublicReadbackExpectation(persisted, selected, publicSlug);

  let publicPack = null;
  let readbackMismatches = [];
  for (let attemptNumber = 1; attemptNumber <= 20; attemptNumber += 1) {
    try {
      const readback = await readExactPublicPack(base, expectedPublicPack);
      publicPack = readback.pack;
      readbackMismatches = readback.mismatches;
      if (publicPack) break;
    } catch (cause) {
      // Production cache/readback may lag; retry within the bounded window.
      readbackMismatches = [cause instanceof Error ? cause.message : String(cause)];
    }
    await wait(15_000);
  }
  const checkedAt = new Date().toISOString();
  if (!publicPack) {
    const readbackError = `exact public Pack readback failed: ${readbackMismatches.join('; ') || 'no matching Pack returned'}`;
    await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
      method: 'POST',
      body: JSON.stringify({
        schemaVersion: READBACK_SCHEMA,
        status: 'failed',
        packSlug: publicSlug,
        checkedAt,
        error: readbackError,
      }),
    }).catch(() => {});
    fail(`Published pack ${publicSlug} failed production readback: ${readbackError}`);
  }

  await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
    method: 'POST',
    body: JSON.stringify({
      schemaVersion: READBACK_SCHEMA,
      status: 'succeeded',
      packSlug: publicSlug,
      checkedAt,
      error: null,
    }),
  });
  const slo = (await apiRequest(`${base}/api/automation/packs/production?windowDays=7`, token))?.data;
  if (slo && !slo.met) {
    process.stderr.write(`::error::Rolling 7-day Pack production SLO is below target: ${slo.publishedReadbackPassed}/${slo.target}\n`);
  }

  const result = {
    outcome: 'published',
    generationId,
    pack: { id: publicPack.id, slug: publicSlug, skillCount: publicPack.skills.length },
    readbackPassed: true,
    rollingSevenDaySlo: slo ?? null,
  };
  await writeJson(resolve(resultsDir, 'final-result.json'), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function reportSlo(args) {
  const resultsDir = resolve(required(args, 'results-dir'));
  const token = required(args, 'token');
  const base = apiBase(args);
  await mkdir(resultsDir, { recursive: true });
  const response = await apiRequest(`${base}/api/automation/packs/production?windowDays=7`, token);
  const result = buildSloResult(response?.data);
  await writeJson(resolve(resultsDir, 'slo-result.json'), result);
  if (!result.met) {
    process.stderr.write(
      `::error::Rolling 7-day Pack production SLO is below target: ${result.publishedReadbackPassed}/${result.target}\n`,
    );
  }
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  switch (args.command) {
    case 'evaluate':
      return evaluate(args);
    case 'verify':
      return verifyEvaluation(args);
    case 'persist':
      return persist(args);
    case 'finalize':
      return finalize(args);
    case 'slo':
      return reportSlo(args);
    default:
      fail('Usage: pack-production.mjs <evaluate|verify|persist|finalize|slo> [options]');
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
