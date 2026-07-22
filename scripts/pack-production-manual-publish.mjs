#!/usr/bin/env node

import { createHash, createPublicKey, verify as verifySignature } from 'node:crypto';
import { lstat, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const APPROVAL_SCHEMA = 'marketplace.pack-production-manual-approval/v1';
const PUBLIC_READBACK_SCHEMA = 'marketplace.pack-production-public-readback/v1';
const RELEASE_SCHEMA = 'marketplace.pack-production-manual-release/v1';
const API_READBACK_SCHEMA = 'skillstore.pack-production-readback/v1';
const API_READBACK_EVIDENCE_SCHEMA = 'skillstore.pack-production-readback-evidence/v1';
const REPOSITORY = 'aiskillstore/marketplace';
const WORKFLOW_NAME = 'Generate Pack';
const WORKFLOW_PATH = '.github/workflows/generate-packs.yml';
const SOURCE_ARTIFACT_NAME = 'pack-production-final';
// Release sequencing gate: replace only after this exact npm package is public.
const CLI_PACKAGE = 'skillstore@__SET_AFTER_MARKETPLACE_CLI_RELEASE__';
const CLI_VERSION = CLI_PACKAGE.slice('skillstore@'.length);
const INSTALL_READBACK_SCHEMA = 'marketplace.pack-production-install-readback/v1';
const RUNTIME_READBACK_SCHEMA = 'marketplace.pack-production-runtime-readback/v1';
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SHA256_RE = /^[0-9a-f]{64}$/;
const SHA1_RE = /^[0-9a-f]{40}$/;
const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?$/;
const MAX_PUBLIC_ARTIFACT_FILES = 512;
const MAX_PUBLIC_ARTIFACT_BYTES = 256 * 1024 * 1024;
const MAX_SINGLE_FILE_BYTES = 32 * 1024 * 1024;
const MAX_JSON_BYTES = 16 * 1024 * 1024;
const ARTIFACT_DOWNLOAD_CONCURRENCY = 4;
// Installer-owned receipt: verified separately, excluded from the Pack source tree.
const PACK_ORCHESTRATION_MANAGED_METADATA_PATHS = new Set(['skillstore-pack-orchestration.json']);
const TRUSTED_SIGNING_KEY = Object.freeze({
  keyId: 'EP0Myk7rTk_J0RdG1fvpkP',
  publicKeyX: '2tbC6eNY4T9sx4Pvuo_NwHlXGyWWz95WAtHyHUTqzs8',
});
const RETRYABLE_PUBLIC_STATUSES = new Set([404, 409, 425, 429]);
const OPPORTUNITY_BINDING_KEYS = [
  'opportunityId', 'briefDigest', 'sourceRunId', 'sourceRunAttempt',
  'sourceCreatedAt', 'sourceHeadSha', 'sourceWorkflowPath', 'evaluationTemplateId', 'candidateSkills',
];
const OPPORTUNITY_CANDIDATE_SKILL_KEYS = [
  'canonicalId', 'contentHash', 'treeHash', 'version', 'sourceCommit',
  'canonicalPath', 'slotIds', 'safeToPublish', 'license',
];

function isSafeArtifactSourcePath(path) {
  return typeof path === 'string'
    && /^[A-Za-z0-9][A-Za-z0-9._/-]*$/.test(path)
    && path.split('/').every((segment) => segment && segment !== '.' && segment !== '..');
}

export class RetryablePublicReadbackError extends Error {}

function isRetryablePublicStatus(status) {
  return RETRYABLE_PUBLIC_STATUSES.has(status) || (status >= 500 && status <= 599);
}

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
    if (value == null || value.startsWith('--')) fail(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function required(args, key) {
  const value = args[key];
  if (typeof value !== 'string' || value.length === 0) fail(`Missing --${key}`);
  return value;
}

function normalizeForJson(value) {
  if (Array.isArray(value)) return value.map(normalizeForJson);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value)
      .filter(([, entry]) => entry !== undefined)
      .sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0))
      .map(([key, entry]) => [key, normalizeForJson(entry)]));
  }
  return value;
}

export function canonicalJson(value) {
  return JSON.stringify(normalizeForJson(value));
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

async function calculateCanonicalInstalledSkillHashes(directory, excludedPaths = new Set()) {
  const root = resolve(directory);
  const entries = [];
  async function walk(current) {
    const children = await readdir(current, { withFileTypes: true });
    children.sort((left, right) => left.name.localeCompare(right.name, 'en', { sensitivity: 'variant' }));
    for (const child of children) {
      const fullPath = join(current, child.name);
      const path = relative(root, fullPath).split('\\').join('/');
      const stat = await lstat(fullPath);
      if (child.isSymbolicLink() || (!child.isDirectory() && !child.isFile())) {
        fail(`Unsupported installed Skill entry: ${path}`);
      }
      if (child.isDirectory()) {
        await walk(fullPath);
		} else if (path !== 'skill-report.json' && !excludedPaths.has(path)) {
        const bytes = await readFile(fullPath);
        entries.push({
          path,
          mode: (stat.mode & 0o111) === 0 ? '100644' : '100755',
          sha256: sha256(bytes),
          size: bytes.byteLength,
        });
      }
    }
  }
  await walk(root);
  entries.sort((left, right) => left.path.localeCompare(right.path, 'en', { sensitivity: 'variant' }));
  const skillMd = await readFile(join(root, 'SKILL.md'));
  return {
    contentHash: sha256(skillMd),
    treeHash: sha256(entries.map((entry) => JSON.stringify(entry)).join('\n')),
  };
}

async function readJson(path) {
  let raw;
  try {
    raw = await readFile(path);
  } catch (cause) {
    fail(`Unable to read ${path}: ${cause.message}`);
  }
  if (raw.length > MAX_JSON_BYTES) fail(`${path} exceeds the JSON size limit`);
  try {
    return { raw, value: JSON.parse(raw.toString('utf8')) };
  } catch {
    fail(`${path} is not valid JSON`);
  }
}

async function writeJson(path, value) {
  await mkdir(resolve(path, '..'), { recursive: true });
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
}

function exactString(value, name, pattern) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${name} is invalid`);
  return value;
}

function exactInteger(value, name) {
  if (!Number.isSafeInteger(value) || value < 1) fail(`${name} is invalid`);
  return value;
}

function exactOpportunityBinding(value) {
  if (
    !value
    || typeof value !== 'object'
    || Array.isArray(value)
    || canonicalJson(Object.keys(value).sort()) !== canonicalJson([...OPPORTUNITY_BINDING_KEYS].sort())
    || !SLUG_RE.test(value.opportunityId)
    || !SHA256_RE.test(value.briefDigest)
    || typeof value.sourceRunId !== 'string'
    || !/^[1-9][0-9]*$/.test(value.sourceRunId)
    || !Number.isSafeInteger(value.sourceRunAttempt)
    || value.sourceRunAttempt < 1
    || typeof value.sourceCreatedAt !== 'string'
    || !Number.isFinite(Date.parse(value.sourceCreatedAt))
    || new Date(value.sourceCreatedAt).toISOString() !== value.sourceCreatedAt
    || !SHA1_RE.test(value.sourceHeadSha)
    || !/^\.github\/workflows\/[A-Za-z0-9._-]+\.ya?ml$/.test(value.sourceWorkflowPath)
    || !SLUG_RE.test(value.evaluationTemplateId)
  ) fail('Evaluation opportunity binding is invalid');
  if (!Array.isArray(value.candidateSkills) || value.candidateSkills.length < 2 || value.candidateSkills.length > 3) {
    fail('Evaluation opportunity binding must contain two to three candidate Skills');
  }
  const candidateSkills = value.candidateSkills.map((skill, index) => {
    if (
      !skill || typeof skill !== 'object' || Array.isArray(skill)
      || canonicalJson(Object.keys(skill).sort()) !== canonicalJson([...OPPORTUNITY_CANDIDATE_SKILL_KEYS].sort())
      || !SLUG_RE.test(skill.canonicalId ?? '')
      || !SHA256_RE.test(skill.contentHash ?? '')
      || !SHA256_RE.test(skill.treeHash ?? '')
      || typeof skill.version !== 'string' || !skill.version
      || !SHA1_RE.test(skill.sourceCommit ?? '')
      || !isSafeArtifactSourcePath(skill.canonicalPath)
      || !Array.isArray(skill.slotIds) || skill.slotIds.length === 0
      || new Set(skill.slotIds).size !== skill.slotIds.length
      || skill.slotIds.some((slotId) => !SLUG_RE.test(slotId))
      || skill.safeToPublish !== true
      || typeof skill.license !== 'string' || !skill.license.trim() || skill.license.length > 200
    ) fail(`Evaluation opportunity candidate Skill ${index + 1} is invalid`);
    return {
      canonicalId: skill.canonicalId,
      contentHash: skill.contentHash,
      treeHash: skill.treeHash,
      version: skill.version,
      sourceCommit: skill.sourceCommit,
      canonicalPath: skill.canonicalPath,
      slotIds: [...skill.slotIds],
      safeToPublish: skill.safeToPublish,
      license: skill.license,
    };
  });
  if (new Set(candidateSkills.map((skill) => skill.canonicalId)).size !== candidateSkills.length) {
    fail('Evaluation opportunity candidate Skills must have distinct canonical ids');
  }
  return { ...Object.fromEntries(OPPORTUNITY_BINDING_KEYS.map((key) => [key, value[key]])), candidateSkills };
}

function assertOpportunityCandidateSkillsMatchDag(candidateSkills, skills) {
  if (candidateSkills.length !== skills.length || canonicalJson(
    candidateSkills.map(({ canonicalId, contentHash, treeHash, version, slotIds }) => ({
      canonicalId, contentHash, treeHash, version, slotIds,
    })),
  ) !== canonicalJson(skills.map(({ canonicalId, contentHash, treeHash, version, slotIds }) => ({
    canonicalId, contentHash, treeHash, version, slotIds,
  })))) fail('Evaluation opportunity candidate Skills differ from the ordered execution DAG bindings');
}

function exactRuntimeContract(evaluation, skills) {
  const suite = evaluation?.candidate?.fitness?.evaluationSuite;
  const provenance = evaluation?.candidate?.fitness?.usageProvenance;
  const variantId = suite?.variantIds?.[0];
  const expectedTrace = provenance?.traces?.[0];
  if (
    typeof evaluation?.scenario?.task !== 'string'
    || !evaluation.scenario.task.trim()
    || evaluation.scenario.task.length > 20_000
    || !Array.isArray(evaluation.scenario.requiredCapabilitySlots)
    || evaluation.scenario.requiredCapabilitySlots.length < 1
    || !Array.isArray(suite?.variantIds)
    || suite.variantIds.length !== 3
    || !Array.isArray(suite.taskDigests)
    || !Array.isArray(suite.fixtureDigests)
    || !Array.isArray(suite.validatorDigests)
    || !SLUG_RE.test(variantId ?? '')
    || !SHA256_RE.test(suite.taskDigests[0] ?? '')
    || !SHA256_RE.test(suite.fixtureDigests[0] ?? '')
    || !SHA256_RE.test(suite.validatorDigests[0] ?? '')
    || expectedTrace?.variantId !== variantId
    || canonicalJson(expectedTrace?.events) !== canonicalJson(skills.map((skill, index) => ({
      canonicalId: skill.canonicalId,
      contentHash: skill.contentHash,
      treeHash: skill.treeHash,
      version: skill.version,
      sequence: index + 1,
    })))
  ) fail('Selected evaluation lacks an exact public runtime acceptance contract');
  return {
    scenarioId: evaluation.scenario.id,
    task: evaluation.scenario.task,
    requiredCapabilitySlots: [...evaluation.scenario.requiredCapabilitySlots],
    variantId,
    taskDigest: suite.taskDigests[0],
    fixtureDigest: suite.fixtureDigests[0],
    validatorDigest: suite.validatorDigests[0],
    expectedMemberTrace: expectedTrace.events,
    // The exact Opportunity Brief plus content-addressed Skillstore CLI contain
    // the public fixture generator and evaluator-only deterministic validator.
    executableFixtureIncluded: true,
    executableValidatorIncluded: true,
  };
}

function exactSourceRun(sourceRun, workflow, artifact, requestedRunId) {
  const runId = exactInteger(sourceRun?.id, 'source run id');
  if (String(runId) !== requestedRunId) fail('Source run id differs from workflow_dispatch input');
  if (
    sourceRun.name !== WORKFLOW_NAME
    || sourceRun.path !== WORKFLOW_PATH
    || sourceRun.repository?.full_name !== REPOSITORY
    || sourceRun.status !== 'completed'
    || sourceRun.conclusion !== 'success'
    || sourceRun.head_branch !== 'main'
    || !['workflow_run', 'workflow_dispatch'].includes(sourceRun.event)
  ) fail('Source run is not a successful main Generate Pack execution');
  const headSha = exactString(sourceRun.head_sha, 'source run head SHA', SHA1_RE);
  const runAttempt = exactInteger(sourceRun.run_attempt, 'source run attempt');
  if (
    workflow?.name !== WORKFLOW_NAME
    || workflow?.path !== WORKFLOW_PATH
    || workflow?.state !== 'active'
    || exactInteger(workflow?.id, 'workflow id') !== sourceRun.workflow_id
  ) fail('Generate Pack workflow identity is not exact and active');
  if (
    artifact?.name !== SOURCE_ARTIFACT_NAME
    || artifact?.expired !== false
    || !Number.isSafeInteger(artifact?.size_in_bytes)
    || artifact.size_in_bytes < 1
    || artifact.size_in_bytes > 32 * 1024 * 1024
    || artifact?.workflow_run?.id !== runId
    || artifact?.workflow_run?.head_sha !== headSha
  ) fail('Source artifact is not bound to the exact Generate Pack run');
  const digest = exactString(artifact.digest, 'source artifact digest', /^sha256:[0-9a-f]{64}$/);
  return {
    repository: REPOSITORY,
    runId: String(runId),
    runAttempt,
    runUrl: sourceRun.html_url,
    event: sourceRun.event,
    headSha,
    workflowId: workflow.id,
    workflowPath: WORKFLOW_PATH,
    artifactId: exactInteger(artifact.id, 'source artifact id'),
    artifactName: SOURCE_ARTIFACT_NAME,
    artifactDigest: digest,
  };
}

function exactSkillBindings(evaluation) {
  const manifest = evaluation?.candidate?.manifest;
  const dag = manifest?.executionDag;
  if (
    !dag
    || dag.schemaVersion !== 'skillstore.pack-execution-dag/v1'
    || !SHA256_RE.test(dag.workflowDigest ?? '')
    || !SHA256_RE.test(dag.bindingDigest ?? '')
    || dag.usageGuideMarker !== `<!-- skillstore-execution-binding:${dag.bindingDigest} -->`
    || !Array.isArray(manifest.skills)
    || !Array.isArray(dag.skillBindings)
    || manifest.skills.length < 2
    || dag.skillBindings.length !== manifest.skills.length
  ) fail('Candidate execution DAG or ordered Skill binding is incomplete');
  const skills = dag.skillBindings.map((binding, index) => {
    if (
      binding?.canonicalId !== manifest.skills[index]
      || !SLUG_RE.test(binding?.canonicalId ?? '')
      || typeof binding?.version !== 'string'
      || binding.version.length === 0
      || !SHA256_RE.test(binding?.contentHash ?? '')
      || !SHA256_RE.test(binding?.treeHash ?? '')
      || !Array.isArray(binding?.slotIds)
      || binding.slotIds.length === 0
    ) fail(`Candidate Skill binding ${index + 1} is incomplete or out of order`);
    return {
      canonicalId: binding.canonicalId,
      version: binding.version,
      contentHash: binding.contentHash,
      treeHash: binding.treeHash,
      slotIds: [...binding.slotIds],
    };
  });
  return { manifest, dag, skills };
}

function exactCandidate(persisted, finalResult, source) {
  const selected = persisted?.selected;
  if (!selected || !UUID_RE.test(selected.generationId ?? '')) {
    fail('Persist summary did not select a valid generation');
  }
  if (
    !selected.pack?.id
    || !SLUG_RE.test(selected.pack?.slug ?? '')
    || selected.autoPublishEligible !== true
    || selected.comparisonOf != null
    || selected.enrichment?.content !== 'dispatched'
    || !UUID_RE.test(selected.enrichment?.contentDispatchNonce ?? '')
  ) fail('Selected candidate is not eligible for non-override manual publication');
  const candidates = (persisted.persisted ?? []).filter(
    (item) => item?.request?.generationId === selected.generationId && item?.auditOnly === false,
  );
  if (candidates.length !== 1) fail('Persist summary does not contain one exact selected candidate');
  const persistedCandidate = candidates[0];
  const evaluation = persistedCandidate.request;
  if (
    evaluation?.schemaVersion !== 'skillstore.pack-evaluation/v4'
    || evaluation?.outcome !== 'candidate_ready'
    || evaluation.generationId !== selected.generationId
    || evaluation.workflow?.repository !== REPOSITORY
    || evaluation.workflow?.runId !== source.runId
    || evaluation.workflow?.runAttempt !== source.runAttempt
    || evaluation.workflow?.commitSha !== source.headSha
    || !SHA256_RE.test(evaluation.evidenceDigest ?? '')
    || !SLUG_RE.test(evaluation.scenario?.slug ?? '')
    || persistedCandidate.response?.data?.generationId !== selected.generationId
    || persistedCandidate.response?.data?.pack?.id !== selected.pack.id
    || persistedCandidate.response?.data?.pack?.slug !== selected.pack.slug
    || persistedCandidate.response?.data?.enrichment?.contentDispatchNonce
      !== selected.enrichment.contentDispatchNonce
  ) fail('Selected v4 evaluation differs from persisted source run evidence');
  const { evidenceDigest: _evidenceDigest, ...unsignedEvaluation } = evaluation;
  if (sha256(canonicalJson(unsignedEvaluation)) !== evaluation.evidenceDigest) {
    fail('Selected v4 evaluation evidence digest is invalid');
  }
  const { manifest, dag, skills } = exactSkillBindings(evaluation);
  const opportunityBinding = exactOpportunityBinding(evaluation.opportunityBinding);
  if (opportunityBinding.opportunityId !== evaluation.scenario.id) {
    fail('Evaluation opportunity binding differs from the dynamic scenario');
  }
  assertOpportunityCandidateSkillsMatchDag(opportunityBinding.candidateSkills, skills);
  const fitness = evaluation.candidate?.fitness;
  const score = Number(fitness?.score);
  if (
    fitness?.passed !== true
    || !Number.isFinite(score)
    || score < 8
    || !Array.isArray(manifest.riskFlags)
    || manifest.riskFlags.length !== 0
    || !fitness?.bestSingle
    || !Array.isArray(fitness.bestSingle.competitors)
    || !Array.isArray(fitness?.ablation)
    || fitness?.evaluationSuite?.executed !== true
    || fitness?.usageProvenance?.deterministic !== true
    || !Array.isArray(fitness?.errors)
    || fitness.errors.length !== 0
  ) fail('Manual publication cannot override v4 quality, risk, or evaluation gates');
  if (
    finalResult?.outcome !== 'review_pending'
    || finalResult?.generationId !== selected.generationId
    || finalResult?.pack?.id !== selected.pack.id
    || finalResult?.pack?.slug !== selected.pack.slug
    || finalResult?.reason !== 'automatic publish was disabled for this run'
    || finalResult?.publicationMode !== 'manual_only'
  ) fail('Final artifact is not an auto-publish-disabled review_pending generation');
  const runtimeAcceptance = exactRuntimeContract(evaluation, skills);
  return { selected, evaluation, dag, skills, score, opportunityBinding, runtimeAcceptance };
}

function exactRuntimeInputs(opportunity, cliIdentity, runtimeAcceptance, candidate) {
  const expectedOpportunityKeys = [
    'schemaVersion', 'opportunityId', 'briefDigest', 'evaluationTemplateId', 'task',
    'name', 'slug', 'keywords', 'capabilitySlots', 'requiredArtifacts', 'candidateSkills',
  ];
  if (!opportunity || typeof opportunity !== 'object' || Array.isArray(opportunity)
    || canonicalJson(Object.keys(opportunity).sort()) !== canonicalJson(expectedOpportunityKeys.sort())) {
    fail('Exact runtime Opportunity Brief is invalid');
  }
  const { briefDigest, ...unsignedBrief } = opportunity;
  if (
    opportunity.schemaVersion !== 'skillstore.pack-opportunity-brief/v1'
    || opportunity.opportunityId !== candidate.opportunityBinding.opportunityId
    || opportunity.evaluationTemplateId !== candidate.opportunityBinding.evaluationTemplateId
    || briefDigest !== candidate.opportunityBinding.briefDigest
    || sha256(canonicalJson(unsignedBrief)) !== briefDigest
    || opportunity.task !== candidate.evaluation.scenario.task
    || opportunity.slug !== candidate.evaluation.scenario.slug
    || canonicalJson(opportunity.candidateSkills) !== canonicalJson(candidate.opportunityBinding.candidateSkills)
  ) fail('Exact runtime Opportunity Brief differs from the approved evaluation');
  if (
    !cliIdentity || typeof cliIdentity !== 'object' || Array.isArray(cliIdentity)
    || canonicalJson(Object.keys(cliIdentity).sort()) !== canonicalJson(['sha256', 'version'])
    || cliIdentity.version !== candidate.evaluation.evaluator.cliVersion
    || cliIdentity.sha256 !== candidate.evaluation.evaluator.cliSha256
    || !SHA256_RE.test(cliIdentity.sha256 ?? '')
  ) fail('Runtime CLI identity differs from the evaluated CLI');
  const { evidenceDigest, ...runtimeUnsigned } = runtimeAcceptance ?? {};
  const expectedMembers = candidate.runtimeAcceptance.expectedMemberTrace.map((event, index) => ({
    ...event,
    sequence: index + 2,
  }));
  if (
    runtimeAcceptance?.schemaVersion !== 'skillstore.pack-runtime-acceptance/v1'
    || !SHA256_RE.test(evidenceDigest ?? '')
    || sha256(canonicalJson(runtimeUnsigned)) !== evidenceDigest
    || runtimeAcceptance.opportunityId !== opportunity.opportunityId
    || runtimeAcceptance.briefDigest !== opportunity.briefDigest
    || runtimeAcceptance.evaluationTemplateId !== opportunity.evaluationTemplateId
    || runtimeAcceptance.passed !== true
    || runtimeAcceptance.artifactPassed !== true
    || !Array.isArray(runtimeAcceptance.errors)
    || runtimeAcceptance.errors.length !== 0
    || runtimeAcceptance.trace?.agent !== 'claude'
    || runtimeAcceptance.trace?.source !== 'claude-stream-json-v1'
    || runtimeAcceptance.trace?.deterministic !== true
    || !Array.isArray(runtimeAcceptance.trace?.events)
    || runtimeAcceptance.trace.events.length !== expectedMembers.length + 1
    || !SLUG_RE.test(runtimeAcceptance.trace.events[0]?.canonicalId ?? '')
    || !runtimeAcceptance.trace.events[0].canonicalId.startsWith('skillstore-pack-')
    || !SHA256_RE.test(runtimeAcceptance.trace.events[0]?.contentHash ?? '')
    || !SHA256_RE.test(runtimeAcceptance.trace.events[0]?.treeHash ?? '')
		|| typeof runtimeAcceptance.trace.events[0]?.version !== 'string'
		|| runtimeAcceptance.trace.events[0].version !== candidate.evaluation.scenario.version
    || runtimeAcceptance.trace.events[0]?.sequence !== 1
    || canonicalJson(runtimeAcceptance.trace.events.slice(1)) !== canonicalJson(expectedMembers)
    || runtimeAcceptance.validation?.variantId !== candidate.runtimeAcceptance.variantId
    || runtimeAcceptance.validation?.passed !== true
    || runtimeAcceptance.validation?.taskDigest !== candidate.runtimeAcceptance.taskDigest
    || runtimeAcceptance.validation?.fixtureDigest !== candidate.runtimeAcceptance.fixtureDigest
    || runtimeAcceptance.validation?.validatorDigest !== candidate.runtimeAcceptance.validatorDigest
	) fail('Pre-publication runtime acceptance differs from the approved evaluation');
  return {
    runtimeCli: { version: cliIdentity.version, sha256: cliIdentity.sha256 },
    runtimeEvidenceDigest: evidenceDigest,
		orchestration: (({ canonicalId, contentHash, treeHash, version }) => ({
			canonicalId, contentHash, treeHash, version,
		}))(runtimeAcceptance.trace.events[0]),
  };
}

export function buildManualApproval({
  sourceRun, workflow, artifact, persisted, finalResult, opportunity, cliIdentity,
  runtimeAcceptance, requestedRunId, hashes,
}) {
  const source = exactSourceRun(sourceRun, workflow, artifact, requestedRunId);
  const candidate = exactCandidate(persisted, finalResult, source);
  const runtimeInputs = exactRuntimeInputs(opportunity, cliIdentity, runtimeAcceptance, candidate);
  const unsigned = {
    schemaVersion: APPROVAL_SCHEMA,
    preparedAt: new Date().toISOString(),
    source,
    generationId: candidate.selected.generationId,
    contentDispatchNonce: candidate.selected.enrichment.contentDispatchNonce,
    pack: {
      id: candidate.selected.pack.id,
      stagingSlug: candidate.selected.pack.slug,
      publicSlug: candidate.evaluation.scenario.slug,
		version: candidate.evaluation.scenario.version,
    },
    evaluation: {
      schemaVersion: candidate.evaluation.schemaVersion,
      evidenceDigest: candidate.evaluation.evidenceDigest,
      sha256: sha256(canonicalJson(candidate.evaluation)),
      score: candidate.score,
    },
    opportunityBinding: candidate.opportunityBinding,
    runtimeCli: runtimeInputs.runtimeCli,
    runtimeAcceptance: {
      ...candidate.runtimeAcceptance,
		orchestration: runtimeInputs.orchestration,
      prepublishEvidenceDigest: runtimeInputs.runtimeEvidenceDigest,
    },
    executionBinding: {
      schemaVersion: 'skillstore.pack-execution-binding/v1',
      generationId: candidate.evaluation.generationId,
      evidenceDigest: candidate.evaluation.evidenceDigest,
      executionDag: candidate.dag,
      workflowDigest: candidate.dag.workflowDigest,
      bindingDigest: candidate.dag.bindingDigest,
      usageGuideMarker: candidate.dag.usageGuideMarker,
      marketplaceCommitSha: candidate.evaluation.workflow.commitSha,
      opportunityBinding: candidate.opportunityBinding,
      skills: candidate.skills,
    },
    skills: candidate.skills.map((skill) => ({
      slug: skill.canonicalId,
      version: skill.version,
      contentHash: skill.contentHash,
      treeHash: skill.treeHash,
    })),
    sourceFiles: hashes,
  };
  return { ...unsigned, handoffDigest: sha256(canonicalJson(unsigned)) };
}

export function validateManualApproval(approval) {
  if (!approval || approval.schemaVersion !== APPROVAL_SCHEMA) fail('Manual approval schema is invalid');
  const { handoffDigest, ...unsigned } = approval;
  if (!SHA256_RE.test(handoffDigest ?? '') || sha256(canonicalJson(unsigned)) !== handoffDigest) {
    fail('Manual approval handoff digest is invalid');
  }
  if (
    approval.source?.repository !== REPOSITORY
    || approval.source?.workflowPath !== WORKFLOW_PATH
    || approval.source?.artifactName !== SOURCE_ARTIFACT_NAME
    || !/^sha256:[0-9a-f]{64}$/.test(approval.source?.artifactDigest ?? '')
    || !SHA256_RE.test(approval.sourceFiles?.persistSummarySha256 ?? '')
    || !SHA256_RE.test(approval.sourceFiles?.finalResultSha256 ?? '')
    || !SHA256_RE.test(approval.sourceFiles?.opportunitySha256 ?? '')
    || !SHA256_RE.test(approval.sourceFiles?.cliIdentitySha256 ?? '')
    || !SHA256_RE.test(approval.sourceFiles?.runtimeAcceptanceSha256 ?? '')
    || approval.runtimeCli?.version == null
    || !SHA256_RE.test(approval.runtimeCli?.sha256 ?? '')
    || !Number.isFinite(approval.evaluation?.score)
    || approval.evaluation.score < 8
    || !UUID_RE.test(approval.generationId ?? '')
    || !UUID_RE.test(approval.contentDispatchNonce ?? '')
    || !SLUG_RE.test(approval.pack?.stagingSlug ?? '')
    || !SLUG_RE.test(approval.pack?.publicSlug ?? '')
		|| typeof approval.pack?.version !== 'string'
		|| !approval.pack.version
    || approval.executionBinding?.generationId !== approval.generationId
    || approval.executionBinding?.bindingDigest
      !== approval.executionBinding?.executionDag?.bindingDigest
    || canonicalJson(approval.opportunityBinding) !== canonicalJson(
      approval.executionBinding?.opportunityBinding
    )
    || canonicalJson(approval.runtimeAcceptance?.expectedMemberTrace) !== canonicalJson(
      approval.skills?.map((skill, index) => ({
        canonicalId: skill.slug,
        contentHash: skill.contentHash,
        treeHash: skill.treeHash,
        version: skill.version,
        sequence: index + 1,
      }))
    )
    || approval.runtimeAcceptance?.executableFixtureIncluded !== true
    || approval.runtimeAcceptance?.executableValidatorIncluded !== true
    || !SHA256_RE.test(approval.runtimeAcceptance?.taskDigest ?? '')
    || !SHA256_RE.test(approval.runtimeAcceptance?.fixtureDigest ?? '')
    || !SHA256_RE.test(approval.runtimeAcceptance?.validatorDigest ?? '')
    || !SHA256_RE.test(approval.runtimeAcceptance?.prepublishEvidenceDigest ?? '')
		|| !SLUG_RE.test(approval.runtimeAcceptance?.orchestration?.canonicalId ?? '')
		|| !approval.runtimeAcceptance.orchestration.canonicalId.startsWith('skillstore-pack-')
		|| !SHA256_RE.test(approval.runtimeAcceptance?.orchestration?.contentHash ?? '')
		|| !SHA256_RE.test(approval.runtimeAcceptance?.orchestration?.treeHash ?? '')
		|| approval.runtimeAcceptance?.orchestration?.version !== approval.pack.version
    || !Array.isArray(approval.skills)
    || approval.skills.length < 2
    || canonicalJson(approval.skills) !== canonicalJson(
      approval.executionBinding?.skills?.map((skill) => ({
        slug: skill.canonicalId,
        version: skill.version,
        contentHash: skill.contentHash,
        treeHash: skill.treeHash,
      })),
    )
  ) fail('Manual approval binding is internally inconsistent');
  return approval;
}

async function prepare(args) {
  const sourceDir = resolve(required(args, 'source-dir'));
  const output = resolve(required(args, 'output'));
  const requestedRunId = required(args, 'source-run-id');
  if (!/^[1-9][0-9]{5,19}$/.test(requestedRunId)) fail('Invalid --source-run-id');
  const [
    sourceRunFile, workflowFile, artifactFile, persistedFile, finalFile,
    opportunityFile, cliIdentityFile, runtimeAcceptanceFile,
  ] = await Promise.all([
    readJson(resolve(required(args, 'source-run-file'))),
    readJson(resolve(required(args, 'workflow-file'))),
    readJson(resolve(required(args, 'artifact-file'))),
    readJson(resolve(sourceDir, 'persist-summary.json')),
    readJson(resolve(sourceDir, 'final-result.json')),
    readJson(resolve(sourceDir, 'opportunity.json')),
    readJson(resolve(sourceDir, 'cli-identity.json')),
    readJson(resolve(sourceDir, 'runtime-acceptance.json')),
  ]);
  const approval = buildManualApproval({
    sourceRun: sourceRunFile.value,
    workflow: workflowFile.value,
    artifact: artifactFile.value,
    persisted: persistedFile.value,
    finalResult: finalFile.value,
    opportunity: opportunityFile.value,
    cliIdentity: cliIdentityFile.value,
    runtimeAcceptance: runtimeAcceptanceFile.value,
    requestedRunId,
    hashes: {
      persistSummarySha256: sha256(persistedFile.raw),
      finalResultSha256: sha256(finalFile.raw),
      opportunitySha256: sha256(opportunityFile.raw),
      cliIdentitySha256: sha256(cliIdentityFile.raw),
      runtimeAcceptanceSha256: sha256(runtimeAcceptanceFile.raw),
    },
  });
  await writeJson(output, approval);
  process.stdout.write(`${JSON.stringify({
    generationId: approval.generationId,
    packSlug: approval.pack.publicSlug,
    stagingSlug: approval.pack.stagingSlug,
    sourceRunId: approval.source.runId,
    sourceSha: approval.source.headSha,
    bindingDigest: approval.executionBinding.bindingDigest,
    score: approval.evaluation.score,
    handoffDigest: approval.handoffDigest,
  })}\n`);
}

async function requestJson(url, options = {}, fetchImpl = fetch) {
  const { retryPublicStatus = false, ...fetchOptions } = options;
  const response = await fetchImpl(url, {
    ...fetchOptions,
    signal: fetchOptions.signal ?? AbortSignal.timeout(30_000),
    headers: { Accept: 'application/json', ...(fetchOptions.headers ?? {}) },
  });
  if (!response.ok && retryPublicStatus === true && isRetryablePublicStatus(response.status)) {
    throw new RetryablePublicReadbackError(`${url} returned HTTP ${response.status}`);
  }
  const raw = Buffer.from(await response.arrayBuffer());
  if (raw.length > MAX_JSON_BYTES) fail(`${url} returned oversized JSON`);
  const text = raw.toString('utf8');
  if (!response.ok) {
    const message = `${url} returned HTTP ${response.status}: ${text.slice(0, 500)}`;
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  let body = null;
  if (text) {
    try { body = JSON.parse(text); } catch { fail(`${url} returned invalid JSON`); }
  }
  return body;
}

function apiBase(value, name, { credentialed = false } = {}) {
  let url;
  try { url = new URL(value); } catch { fail(`${name} is invalid`); }
  if (
    url.protocol !== 'https:'
    || url.username
    || url.password
    || url.pathname !== '/'
    || url.search
    || url.hash
  ) {
    fail(`${name} must be a credential-free HTTPS origin`);
  }
  if (credentialed && url.origin !== 'https://skillstore.io') {
    fail(`${name} must be the exact production origin https://skillstore.io`);
  }
  return url.origin;
}

export function validateGenerationReadback(readback, approval) {
  const attempt = readback?.attempt ?? readback;
  const pack = readback?.pack ?? null;
  const evidence = attempt?.evidence;
  if (
    attempt?.generation_id !== approval.generationId
    || attempt?.pack_id !== approval.pack.id
    || attempt?.content_dispatch_nonce !== approval.contentDispatchNonce
    || attempt?.evidence_digest !== approval.evaluation.evidenceDigest
    || attempt?.workflow_repository !== REPOSITORY
    || String(attempt?.workflow_run_id) !== approval.source.runId
    || attempt?.workflow_run_attempt !== approval.source.runAttempt
    || evidence?.generationId !== approval.generationId
    || evidence?.evidenceDigest !== approval.evaluation.evidenceDigest
    || evidence?.workflow?.commitSha !== approval.source.headSha
    || canonicalJson(evidence?.candidate?.manifest?.executionDag)
      !== canonicalJson(approval.executionBinding.executionDag)
  ) fail('Authenticated generation readback differs from the immutable approval');
  if (attempt.outcome === 'review_pending') {
    if (
      attempt.pack_slug !== approval.pack.stagingSlug
      || pack?.id !== approval.pack.id
      || pack?.slug !== approval.pack.stagingSlug
      || !['generated', 'pending_review'].includes(pack?.review_status)
    ) fail('review_pending generation no longer points at the approved staging Pack');
    return { outcome: 'review_pending', publicSlug: null };
  }
  if (attempt.outcome === 'published') {
    if (
      attempt.pack_slug !== approval.pack.publicSlug
      || pack?.id !== approval.pack.id
      || pack?.slug !== approval.pack.publicSlug
      || pack?.review_status !== 'approved'
    ) fail('Published generation no longer points at the approved public Pack');
    return { outcome: 'published', publicSlug: pack.slug };
  }
  fail(`Generation outcome ${String(attempt?.outcome)} cannot be manually published`);
}

export async function publishManualApproval(approval, { apiUrl, token, fetchImpl = fetch }) {
  validateManualApproval(approval);
  if (typeof token !== 'string' || token.length < 16) fail('Manual publish token is missing');
  const base = apiBase(apiUrl, 'Skillstore API URL', { credentialed: true });
  const body = {
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    publishMode: 'manual',
    sourceRunId: approval.source.runId,
  };
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  const readGeneration = async () => {
    const response = await requestJson(
      `${base}/api/automation/packs/production/${encodeURIComponent(approval.generationId)}`,
      { headers },
      fetchImpl,
    );
    return validateGenerationReadback(response?.data, approval);
  };
  const before = await readGeneration();
  let data;
  let replayed = false;
  if (before.outcome === 'published') {
    data = {
      slug: before.publicSlug,
      reviewStatus: 'approved',
      generationId: approval.generationId,
      contentDispatchNonce: approval.contentDispatchNonce,
      sourceRunId: approval.source.runId,
    };
    replayed = true;
  } else {
    let response;
    try {
      response = await requestJson(
        `${base}/api/automation/packs/${encodeURIComponent(approval.pack.stagingSlug)}/publish`,
        { method: 'POST', headers, body: JSON.stringify(body) },
        fetchImpl,
      );
    } catch (cause) {
      // A publish can commit while its HTTP response is lost. Re-read the exact
      // generation before deciding whether a rerun is safe.
      const recovered = await readGeneration().catch(() => null);
      if (recovered?.outcome !== 'published') throw cause;
      response = { data: {
        slug: recovered.publicSlug,
        reviewStatus: 'approved',
        generationId: approval.generationId,
        contentDispatchNonce: approval.contentDispatchNonce,
        sourceRunId: approval.source.runId,
      } };
      replayed = true;
    }
    data = response?.data;
  }
  if (
    data?.slug !== approval.pack.publicSlug
    || (data.reviewStatus ?? data.review_status) !== 'approved'
    || data?.generationId !== approval.generationId
    || data?.contentDispatchNonce !== approval.contentDispatchNonce
    || String(data?.sourceRunId) !== approval.source.runId
  ) fail('Manual publish response did not echo the exact generation, nonce, run, and Pack binding');
  const after = await readGeneration();
  if (after.outcome !== 'published' || after.publicSlug !== data.slug) {
    fail('Generation did not become exactly published after the manual publish request');
  }
  return {
    schemaVersion: 'marketplace.pack-production-manual-publish/v1',
    publishedAt: new Date().toISOString(),
    approvalDigest: approval.handoffDigest,
    generationId: approval.generationId,
    sourceRunId: approval.source.runId,
    packSlug: data.slug,
    reviewStatus: 'approved',
    replayed,
  };
}

async function publish(args) {
  const approval = validateManualApproval((await readJson(resolve(required(args, 'approval')))).value);
  const result = await publishManualApproval(approval, {
    apiUrl: required(args, 'api-url'),
    token: required(args, 'token'),
  });
  await writeJson(resolve(required(args, 'output')), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

function validatePublicPack(pack, approval) {
  const mismatches = [];
  if (pack?.id !== approval.pack.id) mismatches.push('Pack id differs from approval');
  if (pack?.slug !== approval.pack.publicSlug) mismatches.push('Pack slug differs from approval');
  if (pack?.reviewStatus !== 'approved') mismatches.push('Pack is not publicly approved');
	if (pack?.version !== approval.pack.version) mismatches.push('Pack version differs from approval');
  if (canonicalJson(pack?.executionBinding) !== canonicalJson(approval.executionBinding)) {
    mismatches.push('Pack execution binding differs from approval');
  }
  if (typeof pack?.usageGuide !== 'string' || !pack.usageGuide.includes(approval.executionBinding.usageGuideMarker)) {
    mismatches.push('Pack usage guide lost the DAG binding marker');
  }
  const skills = Array.isArray(pack?.skills) ? pack.skills.map((skill) => ({
    slug: skill?.slug,
    version: skill?.version,
    contentHash: skill?.contentHash,
    treeHash: skill?.treeHash,
  })) : [];
  if (canonicalJson(skills) !== canonicalJson(approval.skills)) {
    mismatches.push('Pack ordered Skill identities differ from approval');
  }
  if (mismatches.length > 0) fail(mismatches.join('; '));
}

function decodeBase64Url(value) {
  if (typeof value !== 'string' || !/^[A-Za-z0-9_-]+$/.test(value)) fail('Signature is not base64url');
  return Buffer.from(value, 'base64url');
}

export function verifyCanonicalEd25519(signed, signature, trustedSigningKey = TRUSTED_SIGNING_KEY) {
  if (
    signature?.algorithm !== 'Ed25519'
    || typeof signature?.keyId !== 'string'
    || signature.keyId.length === 0
    || signature?.publicKeyJwk?.kty !== 'OKP'
    || signature?.publicKeyJwk?.crv !== 'Ed25519'
    || typeof signature.publicKeyJwk.x !== 'string'
  ) fail('Ed25519 signature metadata is invalid');
  if (
    signature.keyId !== trustedSigningKey?.keyId
    || signature.publicKeyJwk.x !== trustedSigningKey?.publicKeyX
  ) fail('Ed25519 signature key is not the trusted production key');
  let verified = false;
  try {
    verified = verifySignature(
      null,
      Buffer.from(canonicalJson(signed)),
      createPublicKey({ key: signature.publicKeyJwk, format: 'jwk' }),
      decodeBase64Url(signature.value),
    );
  } catch {
    verified = false;
  }
  if (!verified) fail('Ed25519 signature verification failed');
  return true;
}

function installSkillProjection(skills) {
  return (skills ?? []).map((skill) => ({
    slug: skill?.slug,
    version: skill?.version,
    contentHash: skill?.contentHash,
    treeHash: skill?.treeHash,
  }));
}

function assertApprovedArtifactProvenance(skills, candidateSkills, label) {
  if (!Array.isArray(skills) || !Array.isArray(candidateSkills) || skills.length !== candidateSkills.length) {
    fail(`${label} artifact provenance has an unexpected Skill count`);
  }
  skills.forEach((skill, index) => {
    const candidate = candidateSkills[index];
    const source = skill?.artifact?.source;
    if (
      skill?.slug !== candidate?.canonicalId
      || skill?.artifact?.type !== 'skill-files'
      || source?.type !== 'github'
      || source?.owner !== 'aiskillstore'
      || source?.repo !== 'marketplace'
      || source?.commit !== candidate.sourceCommit
      || source?.path !== candidate.canonicalPath
      || !isSafeArtifactSourcePath(source?.path)
    ) fail(`${label} artifact provenance differs from the approved candidate Skill`);
  });
}

export function validateSignedInstallContracts(
  manifest,
  lockfile,
  approval,
  publicBase,
  trustedSigningKey = TRUSTED_SIGNING_KEY,
) {
  const expectedManifestUrl = `${publicBase}/api/packs/${encodeURIComponent(approval.pack.publicSlug)}/manifest`;
  if (manifest?.schemaVersion !== '2.0' || manifest?.signed?.kind !== 'pack') {
    fail('Signed Pack manifest envelope is invalid');
  }
  verifyCanonicalEd25519(manifest.signed, manifest.signature, trustedSigningKey);
  for (const field of ['kind', 'version', 'generatedAt', 'pack', 'executionBinding', 'skills', 'lockfile']) {
    if (canonicalJson(manifest[field]) !== canonicalJson(manifest.signed[field])) {
      fail(`Manifest flattened ${field} differs from its signed payload`);
    }
  }
  if (
    manifest.signed.pack?.slug !== approval.pack.publicSlug
    || manifest.signed.pack?.visibility !== 'public'
		|| manifest.signed.pack?.version !== approval.pack.version
    || canonicalJson(manifest.signed.executionBinding) !== canonicalJson(approval.executionBinding)
    || canonicalJson(installSkillProjection(manifest.signed.skills)) !== canonicalJson(approval.skills)
    || canonicalJson(installSkillProjection(manifest.signed.lockfile?.skills)) !== canonicalJson(approval.skills)
    || canonicalJson(manifest.signed.lockfile?.executionBinding) !== canonicalJson(approval.executionBinding)
    || manifest.signed.lockfile?.source?.manifestUrl !== expectedManifestUrl
  ) fail('Signed Pack manifest differs from the approved execution binding');
  assertApprovedArtifactProvenance(
    manifest.signed.skills,
    approval.opportunityBinding.candidateSkills,
    'Signed Pack manifest',
  );
  assertApprovedArtifactProvenance(
    manifest.signed.lockfile?.skills,
    approval.opportunityBinding.candidateSkills,
    'Signed Pack manifest lockfile',
  );
  manifest.signed.skills.forEach((skill, index) => {
    const manifestLockSkill = manifest.signed.lockfile.skills[index];
    if (
      canonicalJson(skill.artifact) !== canonicalJson(manifestLockSkill?.artifact)
      || skill.contentHash !== manifestLockSkill?.contentHash
    ) fail(`Manifest lockfile artifact differs for ${skill.slug}`);
  });
  const { signature, ...lockfileBody } = lockfile ?? {};
  verifyCanonicalEd25519(lockfileBody, signature, trustedSigningKey);
  if (
    lockfileBody.manifestUrl !== expectedManifestUrl
    || lockfileBody.source?.manifestUrl !== expectedManifestUrl
    || canonicalJson(lockfileBody.executionBinding) !== canonicalJson(approval.executionBinding)
    || canonicalJson(installSkillProjection(lockfileBody.skills)) !== canonicalJson(approval.skills)
  ) fail('Independently signed Pack lockfile differs from the approved execution binding');
  assertApprovedArtifactProvenance(
    lockfileBody.skills,
    approval.opportunityBinding.candidateSkills,
    'Independently signed Pack lockfile',
  );
  manifest.signed.lockfile.skills.forEach((skill, index) => {
    if (canonicalJson(skill.artifact) !== canonicalJson(lockfileBody.skills[index]?.artifact)) {
      fail(`Standalone lockfile artifact differs for ${skill.slug}`);
    }
  });
  if (
    signature.keyId !== manifest.signature.keyId
    || canonicalJson(signature.publicKeyJwk) !== canonicalJson(manifest.signature.publicKeyJwk)
  ) fail('Manifest and lockfile were signed by different keys');
  return manifest.signed.skills.flatMap((skill) => {
    const artifact = skill?.artifact;
    if (
      artifact?.type !== 'skill-files'
      || artifact?.source?.type !== 'github'
      || artifact?.source?.owner !== 'aiskillstore'
      || artifact?.source?.repo !== 'marketplace'
      || !SHA1_RE.test(artifact?.source?.commit ?? '')
      || !isSafeArtifactSourcePath(artifact?.source?.path)
      || !Array.isArray(artifact?.files)
      || artifact.files.length === 0
    ) fail(`Signed artifact for ${skill?.slug ?? 'unknown Skill'} is invalid`);
    const seen = new Set();
    const files = artifact.files.map((file) => {
      let artifactUrl;
      try { artifactUrl = new URL(file?.url); } catch { fail(`Signed artifact file for ${skill.slug} is invalid`); }
      if (
        typeof file?.path !== 'string'
        || file.path.length === 0
        || file.path.startsWith('/')
        || file.path.split('/').includes('..')
        || seen.has(file.path)
        || typeof file?.url !== 'string'
        || artifactUrl.protocol !== 'https:'
        || artifactUrl.origin !== publicBase
        || artifactUrl.username
        || artifactUrl.password
        || artifactUrl.hash
        || !SHA256_RE.test(file?.sha256 ?? '')
        || !Number.isSafeInteger(file?.bytes)
        || file.bytes < 0
        || file.bytes > MAX_SINGLE_FILE_BYTES
      ) fail(`Signed artifact file for ${skill.slug} is invalid`);
      seen.add(file.path);
      return { skill: skill.slug, ...file };
    });
    const skillMd = artifact.files.find((file) => file.path === 'SKILL.md') ?? artifact.files[0];
    if (skill.contentHash !== skillMd.sha256) fail(`Signed contentHash differs for ${skill.slug}`);
    if (skill.downloadUrl !== skillMd.url) fail(`Signed downloadUrl differs for ${skill.slug}`);
    const aggregate = sha256(canonicalJson(artifact.files.map(({ path, sha256: fileSha256 }) => ({
      path,
      sha256: fileSha256,
    }))));
    if (artifact.sha256 !== aggregate) fail(`Signed artifact aggregate differs for ${skill.slug}`);
    return files;
  });
}

async function fetchResponse(url, options, fetchImpl) {
  return fetchImpl(url, { ...options, signal: options?.signal ?? AbortSignal.timeout(30_000) });
}

function contentLength(response, file) {
  const value = response.headers.get('content-length');
  if (value == null) return null;
  if (!/^(?:0|[1-9][0-9]*)$/.test(value)) {
    fail(`Artifact download has an invalid Content-Length: ${file.skill}/${file.path}`);
  }
  const length = Number(value);
  if (!Number.isSafeInteger(length) || length !== file.bytes || length > MAX_SINGLE_FILE_BYTES) {
    fail(`Artifact download Content-Length mismatch: ${file.skill}/${file.path}`);
  }
  return length;
}

async function readArtifactFile(response, file, budget, abort) {
  const advertisedBytes = contentLength(response, file);
  if (advertisedBytes != null && budget.bytes + advertisedBytes > MAX_PUBLIC_ARTIFACT_BYTES) {
    abort.abort();
    fail('Artifact downloads exceed the public artifact byte limit');
  }
  const hash = createHash('sha256');
  const reader = response.body?.getReader();
  if (!reader) {
    if (file.bytes !== 0) fail(`Artifact download has no body: ${file.skill}/${file.path}`);
    return { bytes: 0, sha256: hash.digest('hex') };
  }
  let bytes = 0;
  let complete = false;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        complete = true;
        break;
      }
      const chunk = Buffer.from(value);
      if (
        bytes + chunk.length > file.bytes
        || bytes + chunk.length > MAX_SINGLE_FILE_BYTES
        || budget.bytes + chunk.length > MAX_PUBLIC_ARTIFACT_BYTES
      ) {
        abort.abort();
        fail(`Artifact download exceeds its signed byte limit: ${file.skill}/${file.path}`);
      }
      bytes += chunk.length;
      budget.bytes += chunk.length;
      hash.update(chunk);
    }
  } finally {
    if (!complete) await reader.cancel().catch(() => {});
  }
  const digest = hash.digest('hex');
  if (bytes !== file.bytes || digest !== file.sha256) {
    fail(`Artifact download hash/size mismatch: ${file.skill}/${file.path}`);
  }
  return { bytes, sha256: digest };
}

async function verifyArtifactFiles(files, fetchImpl) {
  if (files.length > MAX_PUBLIC_ARTIFACT_FILES) fail('Signed Pack exceeds the public artifact file limit');
  const expectedBytes = files.reduce((total, file) => total + file.bytes, 0);
  if (expectedBytes > MAX_PUBLIC_ARTIFACT_BYTES) fail('Signed Pack exceeds the public artifact byte limit');
  const results = new Array(files.length);
  const budget = { bytes: 0 };
  const abort = new AbortController();
  let cursor = 0;
  const worker = async () => {
    try {
      while (cursor < files.length) {
        const index = cursor;
        cursor += 1;
        const file = files[index];
        const response = await fetchResponse(file.url, {
          headers: { Accept: 'application/octet-stream' },
          redirect: 'error',
          signal: AbortSignal.any([abort.signal, AbortSignal.timeout(30_000)]),
        }, fetchImpl);
        if (!response.ok) fail(`Artifact download returned HTTP ${response.status}: ${file.skill}/${file.path}`);
        const downloaded = await readArtifactFile(response, file, budget, abort);
        results[index] = { skill: file.skill, path: file.path, ...downloaded, url: file.url };
      }
    } catch (cause) {
      abort.abort();
      throw cause;
    }
  };
  await Promise.all(Array.from(
    { length: Math.min(ARTIFACT_DOWNLOAD_CONCURRENCY, files.length) },
    () => worker(),
  ));
  return results;
}

export async function verifyPublicProduction(approval, {
  publicUrl,
  fetchImpl = fetch,
  trustedSigningKey = TRUSTED_SIGNING_KEY,
}) {
  validateManualApproval(approval);
  const base = apiBase(publicUrl, 'public Skillstore URL');
  const slug = encodeURIComponent(approval.pack.publicSlug);
  const packBody = await requestJson(`${base}/api/packs/${slug}?lang=en`, {
    headers: { 'Cache-Control': 'no-cache' },
    retryPublicStatus: true,
  }, fetchImpl);
  validatePublicPack(packBody?.data, approval);
  const page = await fetchResponse(`${base}/packs/${slug}`, {
    headers: { Accept: 'text/html', 'Cache-Control': 'no-cache' },
  }, fetchImpl);
  if (!page.ok) {
    const message = `Public Pack page returned HTTP ${page.status}`;
    if (isRetryablePublicStatus(page.status)) throw new RetryablePublicReadbackError(message);
    fail(message);
  }
  const manifest = await requestJson(`${base}/api/packs/${slug}/manifest`, {
    headers: { 'Cache-Control': 'no-cache' },
    retryPublicStatus: true,
  }, fetchImpl);
  const lockfile = await requestJson(`${base}/api/packs/${slug}/lockfile`, {
    headers: { 'Cache-Control': 'no-cache' },
    retryPublicStatus: true,
  }, fetchImpl);
  const files = validateSignedInstallContracts(manifest, lockfile, approval, base, trustedSigningKey);
  const downloads = await verifyArtifactFiles(files, fetchImpl);
  const unsigned = {
    schemaVersion: PUBLIC_READBACK_SCHEMA,
    checkedAt: new Date().toISOString(),
    approvalDigest: approval.handoffDigest,
    generationId: approval.generationId,
    packSlug: approval.pack.publicSlug,
    publicBase: base,
    pageStatus: page.status,
    manifest: {
      keyId: manifest.signature.keyId,
      bindingDigest: manifest.signed.executionBinding.bindingDigest,
      skillCount: manifest.signed.skills.length,
      sha256: sha256(canonicalJson(manifest)),
    },
    lockfile: {
      keyId: lockfile.signature.keyId,
      skillCount: lockfile.skills.length,
      sha256: sha256(canonicalJson(lockfile)),
    },
    downloads,
  };
  return { ...unsigned, readbackDigest: sha256(canonicalJson(unsigned)) };
}

async function publicReadback(args) {
  const approval = validateManualApproval((await readJson(resolve(required(args, 'approval')))).value);
  const publishResult = (await readJson(resolve(required(args, 'publish-result')))).value;
  if (
    publishResult?.approvalDigest !== approval.handoffDigest
    || publishResult?.generationId !== approval.generationId
    || publishResult?.packSlug !== approval.pack.publicSlug
    || publishResult?.reviewStatus !== 'approved'
  ) fail('Publish result differs from the approved handoff');
  const attempts = Number(args.attempts ?? '10');
  const pollSeconds = Number(args['poll-seconds'] ?? '30');
  if (!Number.isSafeInteger(attempts) || attempts < 1 || attempts > 10) fail('Invalid --attempts');
  if (!Number.isSafeInteger(pollSeconds) || pollSeconds < 1 || pollSeconds > 60) fail('Invalid --poll-seconds');
  let result;
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      result = await verifyPublicProduction(approval, { publicUrl: required(args, 'public-url') });
      break;
    } catch (cause) {
      if (!(cause instanceof RetryablePublicReadbackError)) throw cause;
      lastError = cause;
      if (attempt < attempts) await new Promise((resolveWait) => setTimeout(resolveWait, pollSeconds * 1000));
    }
  }
  if (!result) throw lastError;
  await writeJson(resolve(required(args, 'output')), result);
  process.stdout.write(`${JSON.stringify({
    generationId: result.generationId,
    packSlug: result.packSlug,
    pageStatus: result.pageStatus,
    skillCount: result.manifest.skillCount,
    fileCount: result.downloads.length,
    readbackDigest: result.readbackDigest,
  })}\n`);
}

export function validateCliCheck(report, approval) {
  if (!Array.isArray(report?.errors) || report.errors.length !== 0) fail('skillstore check reported errors');
  if (!Array.isArray(report?.updates) || report.updates.length !== 0) fail('skillstore check reported unexpected updates');
  if (!Array.isArray(report?.upToDate)) fail('skillstore check omitted upToDate');
  for (const skill of approval.skills) {
    if (!report.upToDate.includes(skill.slug)) fail(`skillstore check omitted ${skill.slug}`);
  }
  return true;
}

export function validateRegistryProof(metadata, packageLock, signatureAudit) {
  const install = packageLock?.packages?.['node_modules/skillstore'];
  const expectedAttestationsUrl = `https://registry.npmjs.org/-/npm/v1/attestations/${CLI_PACKAGE}`;
  if (
    metadata?.name !== 'skillstore'
    || metadata?.version !== CLI_VERSION
    || metadata?.repository?.url !== 'git+https://github.com/aiskillstore/marketplace.git'
    || metadata?.repository?.directory !== 'packages/skillstore'
    || !/^sha512-[A-Za-z0-9+/]+={0,2}$/.test(metadata?.dist?.integrity ?? '')
    || !SHA1_RE.test(metadata?.dist?.shasum ?? '')
    || metadata?.dist?.tarball !== `https://registry.npmjs.org/skillstore/-/skillstore-${CLI_VERSION}.tgz`
    || metadata?.dist?.attestations?.url !== expectedAttestationsUrl
    || metadata?.dist?.attestations?.provenance?.predicateType !== 'https://slsa.dev/provenance/v1'
    || !Array.isArray(metadata?.dist?.signatures)
    || metadata.dist.signatures.length < 1
    || install?.version !== metadata.version
    || install?.integrity !== metadata.dist.integrity
    || install?.resolved !== metadata.dist.tarball
    || !Array.isArray(signatureAudit?.invalid)
    || signatureAudit.invalid.length !== 0
    || !Array.isArray(signatureAudit?.missing)
    || signatureAudit.missing.length !== 0
  ) fail(`Registry integrity or provenance proof for ${CLI_PACKAGE} is invalid`);
  return {
    package: CLI_PACKAGE,
    integrity: metadata.dist.integrity,
    shasum: metadata.dist.shasum,
    tarball: metadata.dist.tarball,
    attestationsUrl: metadata.dist.attestations.url,
    registrySignaturesVerified: true,
  };
}

async function readJsonValue(path) {
  return (await readJson(path)).value;
}

export async function buildInstallReadback(approval, {
  home,
  registryMetadata,
  packageLock,
  signatureAudit,
  cliCheck,
}) {
  validateManualApproval(approval);
  const registry = validateRegistryProof(registryMetadata, packageLock, signatureAudit);
  validateCliCheck(cliCheck, approval);
  const skillsRoot = resolve(home, '.agents', 'skills');
  const entries = await readdir(skillsRoot, { withFileTypes: true });
  const receipts = [];
  for (const entry of entries) {
    if (!entry.isDirectory() && !entry.isSymbolicLink()) continue;
    const directory = resolve(skillsRoot, entry.name);
    try {
      const receipt = await readJsonValue(resolve(directory, 'skillstore-pack-orchestration.json'));
      if (receipt?.managedBy === 'skillstore-cli') receipts.push({ directory, receipt });
    } catch {
      // Pack members do not carry an orchestration ownership receipt.
    }
  }
  if (receipts.length !== 1) fail('Fresh install did not contain one exact Pack orchestration identity');
  const { directory: orchestrationDirectory, receipt } = receipts[0];
  const orchestrationContent = await readFile(resolve(orchestrationDirectory, 'SKILL.md'));
	const orchestrationHashes = await calculateCanonicalInstalledSkillHashes(
		orchestrationDirectory,
		PACK_ORCHESTRATION_MANAGED_METADATA_PATHS,
	);
  if (
    receipt?.schemaVersion !== 'skillstore.pack-orchestration-install/v1'
    || !SLUG_RE.test(receipt?.slug ?? '')
    || receipt.packSlug !== approval.pack.publicSlug
    || typeof receipt.packVersion !== 'string'
    || !receipt.packVersion
    || receipt.packVersion !== approval.pack.version
    || receipt.orchestrationVersion !== receipt.packVersion
		|| receipt.orchestrationVersion !== approval.runtimeAcceptance.orchestration.version
    || !SHA256_RE.test(receipt.contentHash ?? '')
		|| receipt.contentHash !== approval.runtimeAcceptance.orchestration.contentHash
		|| receipt.treeHash !== approval.runtimeAcceptance.orchestration.treeHash
    || sha256(orchestrationContent) !== receipt.contentHash
    || orchestrationHashes.contentHash !== receipt.contentHash
		|| orchestrationHashes.treeHash !== receipt.treeHash
    || receipt.bindingDigest !== approval.executionBinding.bindingDigest
    || !orchestrationContent.toString('utf8').includes(approval.executionBinding.usageGuideMarker)
  ) fail('Installed Pack orchestration identity differs from the approved binding');

  const lock = await readJsonValue(resolve(home, '.agents', '.skill-lock.json'));
  const members = [];
  for (const expected of approval.skills) {
    const memberDirectory = resolve(skillsRoot, expected.slug);
    const content = await readFile(resolve(memberDirectory, 'SKILL.md'));
    const installedHashes = await calculateCanonicalInstalledSkillHashes(memberDirectory);
    const locked = lock?.skills?.[expected.slug];
    if (
      sha256(content) !== expected.contentHash
      || installedHashes.contentHash !== expected.contentHash
      || installedHashes.treeHash !== expected.treeHash
      || locked?.slug !== expected.slug
      || locked?.version !== expected.version
      || locked?.treeHash !== expected.treeHash
      || locked?.source !== 'skillstore'
      || !SHA256_RE.test(locked?.zipHash ?? '')
    ) fail(`Installed member identity differs from approval: ${expected.slug}`);
    members.push({
      canonicalId: expected.slug,
      contentHash: expected.contentHash,
      treeHash: installedHashes.treeHash,
      version: expected.version,
    });
  }
  const unsigned = {
    schemaVersion: INSTALL_READBACK_SCHEMA,
    checkedAt: new Date().toISOString(),
    approvalDigest: approval.handoffDigest,
    generationId: approval.generationId,
    packSlug: approval.pack.publicSlug,
    bindingDigest: approval.executionBinding.bindingDigest,
    registry,
    orchestration: {
      canonicalId: receipt.slug,
      contentHash: receipt.contentHash,
      treeHash: orchestrationHashes.treeHash,
      version: receipt.orchestrationVersion,
      bindingDigest: receipt.bindingDigest,
    },
    members,
    cliCheck: 'passed',
  };
  return { ...unsigned, readbackDigest: sha256(canonicalJson(unsigned)) };
}

function validateDigestedEvidence(value, schemaVersion, approval, label) {
  const unsigned = { ...value };
  const digest = unsigned.readbackDigest;
  delete unsigned.readbackDigest;
  if (
    value?.schemaVersion !== schemaVersion
    || value?.approvalDigest !== approval.handoffDigest
    || value?.generationId !== approval.generationId
    || !SHA256_RE.test(digest ?? '')
    || sha256(canonicalJson(unsigned)) !== digest
  ) fail(`${label} evidence is invalid`);
  return value;
}

export function validateInstallReadback(readback, approval) {
  validateDigestedEvidence(readback, INSTALL_READBACK_SCHEMA, approval, 'Install readback');
  if (
    readback.packSlug !== approval.pack.publicSlug
	|| readback.bindingDigest !== approval.executionBinding.bindingDigest
		|| canonicalJson(readback.orchestration) !== canonicalJson({
			...approval.runtimeAcceptance.orchestration,
			bindingDigest: approval.executionBinding.bindingDigest,
		})
    || readback.registry?.package !== CLI_PACKAGE
    || readback.registry?.registrySignaturesVerified !== true
    || readback.cliCheck !== 'passed'
    || canonicalJson(readback.members) !== canonicalJson(approval.runtimeAcceptance.expectedMemberTrace.map(
      ({ sequence: _sequence, ...identity }) => identity,
    ))
  ) fail('Install readback differs from the approved runtime identities');
  return readback;
}

export async function buildInstalledRuntimeIdentities(approval, installReadback, home) {
  validateManualApproval(approval);
  validateInstallReadback(installReadback, approval);
  const skillsRoot = resolve(home, '.agents', 'skills');
  const dag = approval.executionBinding.executionDag;
  const members = dag.skillBindings.map((binding) => {
    const installed = installReadback.members.find((member) => member.canonicalId === binding.canonicalId);
    if (!installed || installed.contentHash !== binding.contentHash
      || installed.treeHash !== binding.treeHash || installed.version !== binding.version) {
      fail(`Installed runtime member differs from the approved DAG: ${binding.canonicalId}`);
    }
    return {
      canonicalId: installed.canonicalId,
      contentHash: installed.contentHash,
      treeHash: installed.treeHash,
      version: installed.version,
      path: resolve(skillsRoot, installed.canonicalId),
      slotIds: binding.slotIds,
    };
  });
  return {
    schemaVersion: 'skillstore.pack-runtime-identities/v1',
    orchestration: {
      canonicalId: installReadback.orchestration.canonicalId,
      contentHash: installReadback.orchestration.contentHash,
      treeHash: installReadback.orchestration.treeHash,
      version: installReadback.orchestration.version,
      path: resolve(skillsRoot, installReadback.orchestration.canonicalId),
      slotIds: [],
    },
    members,
    executionDag: {
      schema_version: dag.schemaVersion,
      workflow_digest: dag.workflowDigest,
      binding_digest: dag.bindingDigest,
      nodes: dag.nodes.map((node) => ({
        id: node.id,
        instruction: node.instruction,
        depends_on: node.dependsOn,
        artifact_ids: node.artifactIds,
      })),
      handoffs: dag.handoffs.map((handoff) => ({
        from: handoff.from,
        to: handoff.to,
        artifact_ids: handoff.artifactIds,
        contract: handoff.contract,
      })),
      skill_bindings: dag.skillBindings.map((binding) => ({
        canonical_id: binding.canonicalId,
        content_hash: binding.contentHash,
        tree_hash: binding.treeHash,
        version: binding.version,
        slot_ids: binding.slotIds,
      })),
      usage_guide_marker: dag.usageGuideMarker,
    },
  };
}

export function validateRuntimeReadback(readback, approval, installReadback) {
  if (
    approval.runtimeAcceptance.executableFixtureIncluded !== true
    || approval.runtimeAcceptance.executableValidatorIncluded !== true
  ) {
    fail('Runtime acceptance blocked: the approved source artifact has only fixture/validator digests, not the executable public fixture and evaluator validator');
  }
  validateInstallReadback(installReadback, approval);
  validateDigestedEvidence(readback, RUNTIME_READBACK_SCHEMA, approval, 'Runtime readback');
  if (
    readback.installReadbackDigest !== installReadback.readbackDigest
    || readback.orchestration?.canonicalId !== installReadback.orchestration.canonicalId
    || readback.orchestration?.contentHash !== installReadback.orchestration.contentHash
		|| readback.orchestration?.treeHash !== installReadback.orchestration.treeHash
    || readback.orchestration?.version !== installReadback.orchestration.version
    || readback.orchestration?.bindingDigest !== approval.executionBinding.bindingDigest
    || readback.trace?.schemaVersion !== 'skillstore.runner-skill-trace/v1'
    || readback.trace?.agent !== 'claude'
    || readback.trace?.source !== 'claude-stream-json-v1'
    || readback.trace?.deterministic !== true
    || !Array.isArray(readback.trace?.events)
    || readback.trace.events.length !== approval.runtimeAcceptance.expectedMemberTrace.length + 1
    || readback.trace.events[0]?.canonicalId !== installReadback.orchestration.canonicalId
    || readback.trace.events[0]?.contentHash !== installReadback.orchestration.contentHash
    || readback.trace.events[0]?.version !== installReadback.orchestration.version
    || readback.trace.events[0]?.treeHash !== installReadback.orchestration.treeHash
    || readback.trace.events[0]?.sequence !== 1
    || canonicalJson(readback.trace.events.slice(1)) !== canonicalJson(
      approval.runtimeAcceptance.expectedMemberTrace.map((event, index) => ({
        ...event,
        sequence: index + 2,
      }))
    )
    || readback.validation?.schemaVersion !== 'skillstore.deterministic-validation/v1'
    || readback.validation?.variantId !== approval.runtimeAcceptance.variantId
    || readback.validation?.passed !== true
    || readback.validation?.taskDigest !== approval.runtimeAcceptance.taskDigest
    || readback.validation?.fixtureDigest !== approval.runtimeAcceptance.fixtureDigest
    || readback.validation?.validatorDigest !== approval.runtimeAcceptance.validatorDigest
    || approval.runtimeAcceptance.requiredCapabilitySlots.some(
      (slot) => readback.validation?.slotPasses?.[slot] !== true,
    )
  ) fail('Runtime orchestration trace or deterministic artifact validator did not PASS exactly');
  return readback;
}

export function buildRuntimeReadback(approval, installReadback, runtimeAcceptance) {
  validateManualApproval(approval);
  validateInstallReadback(installReadback, approval);
  const { evidenceDigest, ...runtimeUnsigned } = runtimeAcceptance ?? {};
  if (
    runtimeAcceptance?.schemaVersion !== 'skillstore.pack-runtime-acceptance/v1'
    || !SHA256_RE.test(evidenceDigest ?? '')
    || sha256(canonicalJson(runtimeUnsigned)) !== evidenceDigest
    || runtimeAcceptance.opportunityId !== approval.opportunityBinding.opportunityId
    || runtimeAcceptance.briefDigest !== approval.opportunityBinding.briefDigest
    || runtimeAcceptance.evaluationTemplateId !== approval.opportunityBinding.evaluationTemplateId
    || runtimeAcceptance.passed !== true
    || runtimeAcceptance.artifactPassed !== true
    || !Array.isArray(runtimeAcceptance.errors)
    || runtimeAcceptance.errors.length !== 0
  ) fail('Skillstore runtime acceptance evidence is invalid');
  const unsigned = {
    schemaVersion: RUNTIME_READBACK_SCHEMA,
    checkedAt: new Date().toISOString(),
    approvalDigest: approval.handoffDigest,
    generationId: approval.generationId,
    installReadbackDigest: installReadback.readbackDigest,
    orchestration: installReadback.orchestration,
    trace: runtimeAcceptance.trace,
    validation: runtimeAcceptance.validation,
    artifactPassed: true,
    prepublishRuntimeEvidenceDigest: approval.runtimeAcceptance.prepublishEvidenceDigest,
    runtimeEvidenceDigest: evidenceDigest,
  };
  const readback = { ...unsigned, readbackDigest: sha256(canonicalJson(unsigned)) };
  return validateRuntimeReadback(readback, approval, installReadback);
}

async function installReadback(args) {
  const approval = validateManualApproval(await readJsonValue(resolve(required(args, 'approval'))));
  const result = await buildInstallReadback(approval, {
    home: resolve(required(args, 'home')),
    registryMetadata: await readJsonValue(resolve(required(args, 'registry-metadata'))),
    packageLock: await readJsonValue(resolve(required(args, 'package-lock'))),
    signatureAudit: await readJsonValue(resolve(required(args, 'signature-audit'))),
    cliCheck: await readJsonValue(resolve(required(args, 'cli-check'))),
  });
  await writeJson(resolve(required(args, 'output')), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function runtimeReadback(args) {
  const approval = validateManualApproval(await readJsonValue(resolve(required(args, 'approval'))));
  const install = await readJsonValue(resolve(required(args, 'install-readback')));
  const runtime = await readJsonValue(resolve(required(args, 'runtime-evidence')));
  const result = buildRuntimeReadback(approval, install, runtime);
  await writeJson(resolve(required(args, 'output')), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function installedRuntimeIdentities(args) {
  const approval = validateManualApproval(await readJsonValue(resolve(required(args, 'approval'))));
  const install = await readJsonValue(resolve(required(args, 'install-readback')));
  const result = await buildInstalledRuntimeIdentities(
    approval,
    install,
    resolve(required(args, 'home')),
  );
  await writeJson(resolve(required(args, 'output')), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

export async function recordReadback(
  base,
  token,
  approval,
  status,
  errorMessage,
  evidence,
  fetchImpl = fetch,
) {
  base = apiBase(base, 'Skillstore API URL', { credentialed: true });
  const url = `${base}/api/automation/packs/production/${encodeURIComponent(approval.generationId)}`;
  const validateRecordedAttempt = (attempt) => {
    if (
      attempt?.generation_id !== approval.generationId
      || attempt?.pack_id !== approval.pack.id
      || attempt?.pack_slug !== approval.pack.publicSlug
      || attempt?.content_dispatch_nonce !== approval.contentDispatchNonce
      || attempt?.outcome !== 'published'
      || attempt?.production_readback_status !== status
      || (status === 'succeeded' && attempt?.production_readback_error != null)
      || (status === 'failed' && attempt?.production_readback_error !== errorMessage)
      || canonicalJson(attempt?.production_readback_evidence ?? null) !== canonicalJson(evidence)
    ) fail('Production readback record did not preserve the exact published generation');
    return attempt;
  };
  let response;
  try {
    response = await requestJson(url, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        schemaVersion: API_READBACK_SCHEMA,
        status,
        packSlug: approval.pack.publicSlug,
        checkedAt: new Date().toISOString(),
        error: errorMessage,
        evidence,
      }),
    }, fetchImpl);
  } catch (postError) {
    if (status !== 'succeeded' || (postError?.status >= 400 && postError.status < 500)) throw postError;
    try {
      return validateRecordedAttempt((await requestJson(url, {
        headers: { Authorization: `Bearer ${token}` },
      }, fetchImpl))?.data);
    } catch {
      throw postError;
    }
  }
  return validateRecordedAttempt(response?.data);
}

async function complete(args) {
  const approval = validateManualApproval((await readJson(resolve(required(args, 'approval')))).value);
  const token = required(args, 'token');
  const base = apiBase(required(args, 'api-url'), 'Skillstore API URL', { credentialed: true });
  const status = required(args, 'status');
  const output = resolve(required(args, 'output'));
  if (!['succeeded', 'failed'].includes(status)) fail('Invalid --status');
  if (status === 'failed') {
    const message = required(args, 'error').slice(0, 500);
    await recordReadback(base, token, approval, 'failed', message, null);
    const result = {
      schemaVersion: RELEASE_SCHEMA,
      outcome: 'readback_failed',
      generationId: approval.generationId,
      packSlug: approval.pack.publicSlug,
      error: message,
    };
    await writeJson(output, result);
    fail(message);
  }
  let readbackDigest;
  try {
    const publicReadback = (await readJson(resolve(required(args, 'public-readback')))).value;
    const readbackUnsigned = { ...publicReadback };
    readbackDigest = readbackUnsigned.readbackDigest;
    delete readbackUnsigned.readbackDigest;
    if (
      publicReadback?.schemaVersion !== PUBLIC_READBACK_SCHEMA
      || publicReadback?.approvalDigest !== approval.handoffDigest
      || publicReadback?.generationId !== approval.generationId
      || publicReadback?.packSlug !== approval.pack.publicSlug
      || !SHA256_RE.test(readbackDigest ?? '')
      || sha256(canonicalJson(readbackUnsigned)) !== readbackDigest
    ) fail('Public production readback evidence is invalid');
    const install = await readJsonValue(resolve(required(args, 'install-readback')));
    validateInstallReadback(install, approval);
    const runtime = await readJsonValue(resolve(required(args, 'runtime-readback')));
    validateRuntimeReadback(runtime, approval, install);
    const readbackEvidence = {
      schemaVersion: API_READBACK_EVIDENCE_SCHEMA,
      sourceRunId: approval.source.runId,
      generationId: approval.generationId,
      contentDispatchNonce: approval.contentDispatchNonce,
      bindingDigest: approval.executionBinding.bindingDigest,
      manifestDigest: publicReadback.manifest.sha256,
      lockfileDigest: publicReadback.lockfile.sha256,
      fileCount: publicReadback.downloads.length,
      cliPackage: CLI_PACKAGE,
      cliCheck: 'passed',
      registryIntegrity: install.registry.integrity,
      installReadbackDigest: install.readbackDigest,
      runtimeReadbackDigest: runtime.readbackDigest,
      orchestration: install.orchestration,
      memberTrace: runtime.trace.events,
      artifactValidation: runtime.validation,
    };
    await recordReadback(base, token, approval, 'succeeded', null, readbackEvidence);
  } catch (cause) {
    const message = `completion validation failed: ${cause instanceof Error ? cause.message : String(cause)}`.slice(0, 500);
    await recordReadback(base, token, approval, 'failed', message, null).catch(() => {});
    await writeJson(output, {
      schemaVersion: RELEASE_SCHEMA,
      outcome: 'readback_failed',
      generationId: approval.generationId,
      packSlug: approval.pack.publicSlug,
      error: message,
    });
    throw cause;
  }
  const result = {
    schemaVersion: RELEASE_SCHEMA,
    outcome: 'published',
    generationId: approval.generationId,
    sourceRunId: approval.source.runId,
    packSlug: approval.pack.publicSlug,
    bindingDigest: approval.executionBinding.bindingDigest,
    publicReadbackDigest: readbackDigest,
    cliPackage: CLI_PACKAGE,
    cliAgent: 'codex',
    readbackPassed: true,
  };
  await writeJson(output, result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  switch (args.command) {
    case 'prepare': return prepare(args);
    case 'publish': return publish(args);
    case 'public-readback': return publicReadback(args);
    case 'install-readback': return installReadback(args);
    case 'runtime-readback': return runtimeReadback(args);
    case 'installed-runtime-identities': return installedRuntimeIdentities(args);
    case 'complete': return complete(args);
    default:
      fail('Usage: pack-production-manual-publish.mjs <prepare|publish|public-readback|install-readback|installed-runtime-identities|runtime-readback|complete> [options]');
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
