#!/usr/bin/env node

import { createHash, createPublicKey, verify as verifySignature } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
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
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SHA256_RE = /^[0-9a-f]{64}$/;
const SHA1_RE = /^[0-9a-f]{40}$/;
const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?$/;
const MAX_PUBLIC_ARTIFACT_FILES = 512;
const MAX_PUBLIC_ARTIFACT_BYTES = 256 * 1024 * 1024;
const MAX_SINGLE_FILE_BYTES = 32 * 1024 * 1024;
const MAX_JSON_BYTES = 16 * 1024 * 1024;
const ARTIFACT_DOWNLOAD_CONCURRENCY = 4;
const TRUSTED_SIGNING_KEY = Object.freeze({
  keyId: 'EP0Myk7rTk_J0RdG1fvpkP',
  publicKeyX: '2tbC6eNY4T9sx4Pvuo_NwHlXGyWWz95WAtHyHUTqzs8',
});
const RETRYABLE_PUBLIC_STATUSES = new Set([404, 409, 425, 429]);

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
    || !['schedule', 'workflow_dispatch'].includes(sourceRun.event)
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
      || !Array.isArray(binding?.slotIds)
      || binding.slotIds.length === 0
    ) fail(`Candidate Skill binding ${index + 1} is incomplete or out of order`);
    return {
      canonicalId: binding.canonicalId,
      version: binding.version,
      contentHash: binding.contentHash,
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
  return { selected, evaluation, dag, skills, score };
}

export function buildManualApproval({ sourceRun, workflow, artifact, persisted, finalResult, requestedRunId, hashes }) {
  const source = exactSourceRun(sourceRun, workflow, artifact, requestedRunId);
  const candidate = exactCandidate(persisted, finalResult, source);
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
    },
    evaluation: {
      schemaVersion: candidate.evaluation.schemaVersion,
      evidenceDigest: candidate.evaluation.evidenceDigest,
      sha256: sha256(canonicalJson(candidate.evaluation)),
      score: candidate.score,
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
      skills: candidate.skills,
    },
    skills: candidate.skills.map((skill) => ({
      slug: skill.canonicalId,
      version: skill.version,
      contentHash: skill.contentHash,
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
    || !Number.isFinite(approval.evaluation?.score)
    || approval.evaluation.score < 8
    || !UUID_RE.test(approval.generationId ?? '')
    || !UUID_RE.test(approval.contentDispatchNonce ?? '')
    || !SLUG_RE.test(approval.pack?.stagingSlug ?? '')
    || !SLUG_RE.test(approval.pack?.publicSlug ?? '')
    || approval.executionBinding?.generationId !== approval.generationId
    || approval.executionBinding?.bindingDigest
      !== approval.executionBinding?.executionDag?.bindingDigest
    || !Array.isArray(approval.skills)
    || approval.skills.length < 2
    || canonicalJson(approval.skills) !== canonicalJson(
      approval.executionBinding?.skills?.map((skill) => ({
        slug: skill.canonicalId,
        version: skill.version,
        contentHash: skill.contentHash,
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
  const [sourceRunFile, workflowFile, artifactFile, persistedFile, finalFile] = await Promise.all([
    readJson(resolve(required(args, 'source-run-file'))),
    readJson(resolve(required(args, 'workflow-file'))),
    readJson(resolve(required(args, 'artifact-file'))),
    readJson(resolve(sourceDir, 'persist-summary.json')),
    readJson(resolve(sourceDir, 'final-result.json')),
  ]);
  const approval = buildManualApproval({
    sourceRun: sourceRunFile.value,
    workflow: workflowFile.value,
    artifact: artifactFile.value,
    persisted: persistedFile.value,
    finalResult: finalFile.value,
    requestedRunId,
    hashes: {
      persistSummarySha256: sha256(persistedFile.raw),
      finalResultSha256: sha256(finalFile.raw),
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
    fail(message);
  }
  let body = null;
  if (text) {
    try { body = JSON.parse(text); } catch { fail(`${url} returned invalid JSON`); }
  }
  return body;
}

function apiBase(value, name) {
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
  const base = apiBase(apiUrl, 'Skillstore API URL');
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
  }));
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
    || canonicalJson(manifest.signed.executionBinding) !== canonicalJson(approval.executionBinding)
    || canonicalJson(installSkillProjection(manifest.signed.skills)) !== canonicalJson(approval.skills)
    || canonicalJson(installSkillProjection(manifest.signed.lockfile?.skills)) !== canonicalJson(approval.skills)
    || canonicalJson(manifest.signed.lockfile?.executionBinding) !== canonicalJson(approval.executionBinding)
    || manifest.signed.lockfile?.source?.manifestUrl !== expectedManifestUrl
  ) fail('Signed Pack manifest differs from the approved execution binding');
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
      || !Array.isArray(artifact?.files)
      || artifact.files.length === 0
    ) fail(`Signed artifact for ${skill?.slug ?? 'unknown Skill'} is invalid`);
    const seen = new Set();
    const files = artifact.files.map((file) => {
      if (
        typeof file?.path !== 'string'
        || file.path.length === 0
        || file.path.startsWith('/')
        || file.path.split('/').includes('..')
        || seen.has(file.path)
        || typeof file?.url !== 'string'
        || !file.url.startsWith('https://')
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

async function verifyArtifactFiles(files, fetchImpl) {
  if (files.length > MAX_PUBLIC_ARTIFACT_FILES) fail('Signed Pack exceeds the public artifact file limit');
  const expectedBytes = files.reduce((total, file) => total + file.bytes, 0);
  if (expectedBytes > MAX_PUBLIC_ARTIFACT_BYTES) fail('Signed Pack exceeds the public artifact byte limit');
  const results = new Array(files.length);
  let cursor = 0;
  const worker = async () => {
    while (cursor < files.length) {
      const index = cursor;
      cursor += 1;
      const file = files[index];
      const response = await fetchResponse(file.url, { headers: { Accept: 'application/octet-stream' } }, fetchImpl);
      if (!response.ok) fail(`Artifact download returned HTTP ${response.status}: ${file.skill}/${file.path}`);
      const bytes = Buffer.from(await response.arrayBuffer());
      const digest = sha256(bytes);
      if (bytes.length !== file.bytes || digest !== file.sha256) {
        fail(`Artifact download hash/size mismatch: ${file.skill}/${file.path}`);
      }
      results[index] = { skill: file.skill, path: file.path, bytes: bytes.length, sha256: digest, url: file.url };
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

export async function recordReadback(
  base,
  token,
  approval,
  status,
  errorMessage,
  evidence,
  fetchImpl = fetch,
) {
  const response = await requestJson(`${base}/api/automation/packs/production/${encodeURIComponent(approval.generationId)}`, {
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
  const attempt = response?.data;
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
}

async function complete(args) {
  const approval = validateManualApproval((await readJson(resolve(required(args, 'approval')))).value);
  const token = required(args, 'token');
  const base = apiBase(required(args, 'api-url'), 'Skillstore API URL');
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
    const cliCheck = (await readJson(resolve(required(args, 'cli-check')))).value;
    validateCliCheck(cliCheck, approval);
    const readbackEvidence = {
      schemaVersion: API_READBACK_EVIDENCE_SCHEMA,
      sourceRunId: approval.source.runId,
      generationId: approval.generationId,
      contentDispatchNonce: approval.contentDispatchNonce,
      bindingDigest: approval.executionBinding.bindingDigest,
      manifestDigest: publicReadback.manifest.sha256,
      lockfileDigest: publicReadback.lockfile.sha256,
      fileCount: publicReadback.downloads.length,
      cliPackage: 'skillstore@0.1.9',
      cliCheck: 'passed',
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
    cliPackage: 'skillstore@0.1.9',
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
    case 'complete': return complete(args);
    default:
      fail('Usage: pack-production-manual-publish.mjs <prepare|publish|public-readback|complete> [options]');
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
