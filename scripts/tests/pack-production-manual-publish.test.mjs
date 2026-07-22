import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash, generateKeyPairSync, sign } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  buildManualApproval,
  buildInstallReadback,
  buildInstalledRuntimeIdentities,
  buildRuntimeReadback,
  canonicalJson,
  publishManualApproval,
  recordReadback,
  RetryablePublicReadbackError,
  validateCliCheck,
  validateGenerationReadback,
  validateInstallReadback,
  validateManualApproval,
  validateRegistryProof,
  validateRuntimeReadback,
  validateSignedInstallContracts,
  verifyCanonicalEd25519,
  verifyPublicProduction,
} from '../pack-production-manual-publish.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const GENERATION_ID = 'a43f792e-92ac-4b9d-b0fe-eafe4855d3a0';
const NONCE = '11111111-1111-4111-8111-111111111111';
const RUN_ID = '123456789';
const SOURCE_SHA = 'a'.repeat(40);
const ARTIFACT_DIGEST = `sha256:${'b'.repeat(64)}`;
const SKILL_CONTENTS = [Buffer.from('# Skill one\n'), Buffer.from('# Skill two\n')];
const CLI_VERSION = '__SET_AFTER_MARKETPLACE_CLI_RELEASE__';
const CLI_PACKAGE = `skillstore@${CLI_VERSION}`;

function registryProofFixture() {
  const metadata = {
    name: 'skillstore',
    version: CLI_VERSION,
    repository: {
      type: 'git',
      url: 'git+https://github.com/aiskillstore/marketplace.git',
      directory: 'packages/skillstore',
    },
    dist: {
      integrity: `sha512-${Buffer.from('registry-integrity').toString('base64')}`,
      shasum: 'e'.repeat(40),
      tarball: `https://registry.npmjs.org/skillstore/-/skillstore-${CLI_VERSION}.tgz`,
      attestations: {
        url: `https://registry.npmjs.org/-/npm/v1/attestations/${CLI_PACKAGE}`,
        provenance: { predicateType: 'https://slsa.dev/provenance/v1' },
      },
      signatures: [{ keyid: 'test', sig: 'test' }],
    },
  };
  return {
    metadata,
    packageLock: { packages: { 'node_modules/skillstore': {
      version: metadata.version,
      integrity: metadata.dist.integrity,
      resolved: metadata.dist.tarball,
    } } },
    signatureAudit: { invalid: [], missing: [] },
  };
}

function hash(value) {
  return createHash('sha256').update(value).digest('hex');
}

function singleFileTreeHash(content) {
  return hash(JSON.stringify({
    path: 'SKILL.md',
    mode: '100644',
    sha256: hash(content),
    size: content.byteLength,
  }));
}

function fixture() {
  const evaluation = JSON.parse(readFileSync(
    join(REPO_ROOT, 'scripts/tests/fixtures/pack-production-evaluation-v4.golden.json'),
    'utf8',
  ));
  evaluation.workflow.runId = RUN_ID;
  evaluation.workflow.runAttempt = 1;
  evaluation.workflow.commitSha = SOURCE_SHA;
  evaluation.candidate.manifest.executionDag.skillBindings.forEach((binding, index) => {
    binding.contentHash = hash(SKILL_CONTENTS[index]);
    binding.treeHash = singleFileTreeHash(SKILL_CONTENTS[index]);
  });
  const dag = evaluation.candidate.manifest.executionDag;
  dag.bindingDigest = hash(canonicalJson({
    workflow_digest: dag.workflowDigest,
    skill_bindings: dag.skillBindings.map((binding) => ({
      canonical_id: binding.canonicalId,
      content_hash: binding.contentHash,
      tree_hash: binding.treeHash,
      version: binding.version,
      slot_ids: binding.slotIds,
    })),
  }));
  dag.usageGuideMarker = `<!-- skillstore-execution-binding:${dag.bindingDigest} -->`;
  evaluation.candidate.fitness.usageProvenance.traces.forEach((trace) => {
    trace.events.forEach((event, index) => {
      event.contentHash = hash(SKILL_CONTENTS[index]);
      event.treeHash = singleFileTreeHash(SKILL_CONTENTS[index]);
    });
  });
  evaluation.opportunityBinding.candidateSkills = evaluation.opportunityBinding.candidateSkills.map((skill, index) => ({
    ...skill,
    contentHash: dag.skillBindings[index].contentHash,
    treeHash: dag.skillBindings[index].treeHash,
    version: dag.skillBindings[index].version,
    slotIds: dag.skillBindings[index].slotIds,
  }));
  const opportunity = {
    schemaVersion: 'skillstore.pack-opportunity-brief/v1',
    opportunityId: evaluation.opportunityBinding.opportunityId,
    briefDigest: '',
    evaluationTemplateId: evaluation.opportunityBinding.evaluationTemplateId,
    task: evaluation.scenario.task,
    name: evaluation.scenario.name,
    slug: evaluation.scenario.slug,
    keywords: ['xlsx'],
    capabilitySlots: evaluation.scenario.requiredCapabilitySlots.map((id) => ({ id })),
    requiredArtifacts: [{ id: 'workbook', extensions: ['.xlsx'], minimumCount: 1 }],
    candidateSkills: dag.skillBindings.map((binding, index) => ({
      canonicalId: binding.canonicalId,
      canonicalPath: evaluation.opportunityBinding.candidateSkills[index].canonicalPath,
      contentHash: binding.contentHash,
      treeHash: binding.treeHash,
      version: binding.version,
      sourceCommit: evaluation.opportunityBinding.candidateSkills[index].sourceCommit,
      slotIds: binding.slotIds,
      safeToPublish: evaluation.opportunityBinding.candidateSkills[index].safeToPublish,
      license: evaluation.opportunityBinding.candidateSkills[index].license,
    })),
  };
  const { briefDigest: _briefDigest, ...unsignedOpportunity } = opportunity;
  opportunity.briefDigest = hash(canonicalJson(unsignedOpportunity));
  evaluation.opportunityBinding.briefDigest = opportunity.briefDigest;
	const orchestrationContent = `# Runtime\n${dag.usageGuideMarker}\n`;
	const orchestration = {
		canonicalId: `skillstore-pack-${evaluation.scenario.slug}`,
		contentHash: hash(orchestrationContent),
		treeHash: singleFileTreeHash(Buffer.from(orchestrationContent)),
		version: evaluation.scenario.version,
	};
  const runtimeAcceptance = {
    schemaVersion: 'skillstore.pack-runtime-acceptance/v1',
    opportunityId: opportunity.opportunityId,
    briefDigest: opportunity.briefDigest,
    evaluationTemplateId: opportunity.evaluationTemplateId,
    passed: true,
    artifactPassed: true,
    errors: [],
    trace: {
      schemaVersion: 'skillstore.runner-skill-trace/v1',
      agent: 'claude',
      source: 'claude-stream-json-v1',
      deterministic: true,
      events: [
        {
			...orchestration,
          sequence: 1,
        },
        ...dag.skillBindings.map((binding, index) => ({
          canonicalId: binding.canonicalId,
          contentHash: binding.contentHash,
          treeHash: binding.treeHash,
          version: binding.version,
          sequence: index + 2,
        })),
      ],
    },
    validation: {
      schemaVersion: 'skillstore.deterministic-validation/v1',
      variantId: evaluation.candidate.fitness.evaluationSuite.variantIds[0],
      passed: true,
      taskDigest: evaluation.candidate.fitness.evaluationSuite.taskDigests[0],
      fixtureDigest: evaluation.candidate.fitness.evaluationSuite.fixtureDigests[0],
      validatorDigest: evaluation.candidate.fitness.evaluationSuite.validatorDigests[0],
      slotPasses: Object.fromEntries(evaluation.scenario.requiredCapabilitySlots.map((slot) => [slot, true])),
    },
  };
  runtimeAcceptance.evidenceDigest = hash(canonicalJson(runtimeAcceptance));
  const { evidenceDigest: _evidenceDigest, ...unsignedEvaluation } = evaluation;
  evaluation.evidenceDigest = hash(canonicalJson(unsignedEvaluation));
  const stagingSlug = 'monthly-sales-excel-workbook-staging';
  const selected = {
    generationId: GENERATION_ID,
    pack: { id: 'pack-123', slug: stagingSlug },
    enrichment: { content: 'dispatched', translation: 'not_applicable', contentDispatchNonce: NONCE },
    autoPublishEligible: true,
    comparisonOf: null,
  };
  const persisted = {
    schemaVersion: 'marketplace.pack-production-persist/v1',
    selected,
    persisted: [{
      file: '01-excel-dashboard.evaluation.json',
      request: evaluation,
      response: {
        data: {
          generationId: GENERATION_ID,
          pack: selected.pack,
          enrichment: { contentDispatchNonce: NONCE },
        },
      },
      auditOnly: false,
      persistedRemotely: true,
    }],
  };
  const finalResult = {
    outcome: 'review_pending',
    generationId: GENERATION_ID,
    pack: selected.pack,
    reason: 'automatic publish was disabled for this run',
    autoPublishRequested: false,
    publicationMode: 'manual_only',
  };
  const sourceRun = {
    id: Number(RUN_ID),
    workflow_id: 303407323,
    name: 'Generate Pack',
    path: '.github/workflows/generate-packs.yml',
    repository: { full_name: 'aiskillstore/marketplace' },
    status: 'completed',
    conclusion: 'success',
    head_branch: 'main',
    head_sha: SOURCE_SHA,
    event: 'workflow_dispatch',
    run_attempt: 1,
    html_url: `https://github.com/aiskillstore/marketplace/actions/runs/${RUN_ID}`,
  };
  const workflow = {
    id: 303407323,
    name: 'Generate Pack',
    path: '.github/workflows/generate-packs.yml',
    state: 'active',
  };
  const artifact = {
    id: 987654321,
    name: 'pack-production-final',
    expired: false,
    size_in_bytes: 4096,
    digest: ARTIFACT_DIGEST,
    workflow_run: { id: Number(RUN_ID), head_sha: SOURCE_SHA },
  };
  const approval = buildManualApproval({
    sourceRun,
    workflow,
    artifact,
    persisted,
    finalResult,
    opportunity,
    cliIdentity: { version: evaluation.evaluator.cliVersion, sha256: evaluation.evaluator.cliSha256 },
    runtimeAcceptance,
    requestedRunId: RUN_ID,
    hashes: {
      persistSummarySha256: 'c'.repeat(64),
      finalResultSha256: 'd'.repeat(64),
      opportunitySha256: 'e'.repeat(64),
      cliIdentitySha256: 'f'.repeat(64),
      runtimeAcceptanceSha256: '1'.repeat(64),
    },
  });
  return { evaluation, selected, persisted, finalResult, opportunity, orchestrationContent, runtimeAcceptance, sourceRun, workflow, artifact, approval };
}

function generationReadback(approval, outcome) {
  const published = outcome === 'published';
  return {
    attempt: {
      generation_id: approval.generationId,
      pack_id: approval.pack.id,
      pack_slug: published ? approval.pack.publicSlug : approval.pack.stagingSlug,
      content_dispatch_nonce: approval.contentDispatchNonce,
      evidence_digest: approval.evaluation.evidenceDigest,
      workflow_repository: 'aiskillstore/marketplace',
      workflow_run_id: Number(approval.source.runId),
      workflow_run_attempt: approval.source.runAttempt,
      outcome,
      evidence: {
        generationId: approval.generationId,
        evidenceDigest: approval.evaluation.evidenceDigest,
        workflow: { commitSha: approval.source.headSha },
        candidate: { manifest: { executionDag: approval.executionBinding.executionDag } },
      },
    },
    pack: {
      id: approval.pack.id,
      slug: published ? approval.pack.publicSlug : approval.pack.stagingSlug,
      review_status: published ? 'approved' : 'generated',
    },
  };
}

function jsonResponse(value, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

function signatureFor(value, privateKey, publicJwk) {
  return {
    algorithm: 'Ed25519',
    keyId: 'test-key',
    publicKeyJwk: publicJwk,
    signedAt: '2026-07-16T00:00:00.000Z',
    value: sign(null, Buffer.from(canonicalJson(value)), privateKey).toString('base64url'),
  };
}

function installContracts(approval) {
  const { privateKey, publicKey } = generateKeyPairSync('ed25519');
  const publicJwk = publicKey.export({ format: 'jwk' });
  const contents = SKILL_CONTENTS;
  const skills = approval.skills.map((skill, index) => {
    const digest = hash(contents[index]);
    const artifactFiles = [{
      path: 'SKILL.md',
      url: `https://skillstore.io/downloads/${skill.slug}/SKILL.md`,
      sha256: digest,
      bytes: contents[index].length,
    }];
    return {
      slug: skill.slug,
      name: skill.slug,
      version: skill.version,
      authorVersion: skill.version,
      skillstoreRevision: 1,
      versionStatus: 'valid',
      treeHash: skill.treeHash,
      downloadUrl: artifactFiles[0].url,
      contentHash: skill.contentHash,
      artifact: {
        type: 'skill-files',
        source: {
          type: 'github',
          owner: 'aiskillstore',
          repo: 'marketplace',
          ref: approval.opportunityBinding.candidateSkills[index].sourceCommit,
          commit: approval.opportunityBinding.candidateSkills[index].sourceCommit,
          path: approval.opportunityBinding.candidateSkills[index].canonicalPath,
        },
        files: artifactFiles,
        sha256: hash(canonicalJson(artifactFiles.map(({ path, sha256 }) => ({ path, sha256 })))),
      },
    };
  });
  const lockfileBody = {
    schemaVersion: '1.0',
    generatedAt: '2026-07-16T00:00:00.000Z',
    source: { manifestUrl: `https://skillstore.io/api/packs/${approval.pack.publicSlug}/manifest` },
    executionBinding: approval.executionBinding,
    skills: skills.map(({ downloadUrl: _downloadUrl, ...skill }) => skill),
  };
  const signed = {
    kind: 'pack',
    version: '1.0',
    generatedAt: lockfileBody.generatedAt,
		pack: { slug: approval.pack.publicSlug, name: 'Pack', version: approval.pack.version, visibility: 'public' },
    executionBinding: approval.executionBinding,
    skills,
    lockfile: lockfileBody,
  };
  const manifest = {
    ...signed,
    schemaVersion: '2.0',
    signed,
    signature: signatureFor(signed, privateKey, publicJwk),
  };
  const standaloneBody = {
    ...lockfileBody,
    manifestUrl: `https://skillstore.io/api/packs/${approval.pack.publicSlug}/manifest`,
  };
  const lockfile = {
    ...standaloneBody,
    signature: signatureFor(standaloneBody, privateKey, publicJwk),
  };
  return {
    manifest,
    lockfile,
    contents,
    privateKey,
    publicJwk,
    trustedSigningKey: { keyId: 'test-key', publicKeyX: publicJwk.x },
  };
}

function resignInstallContracts({ manifest, lockfile, privateKey, publicJwk }) {
  manifest.signature = signatureFor(manifest.signed, privateKey, publicJwk);
  const { signature: _signature, ...lockfileBody } = lockfile;
  lockfile.signature = signatureFor(lockfileBody, privateKey, publicJwk);
}

function publicRoutes(approval, manifest, lockfile, artifactResponse) {
  const routes = new Map([
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}?lang=en`, jsonResponse({ data: {
      id: approval.pack.id,
      slug: approval.pack.publicSlug,
      reviewStatus: 'approved',
      version: approval.pack.version,
      executionBinding: approval.executionBinding,
      usageGuide: `# Guide\n${approval.executionBinding.usageGuideMarker}`,
      skills: approval.skills,
    } })],
    [`https://skillstore.io/packs/${approval.pack.publicSlug}`, new Response('<html></html>', { status: 200 })],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/manifest`, jsonResponse(manifest)],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/lockfile`, jsonResponse(lockfile)],
  ]);
  manifest.signed.skills.forEach((skill, index) => {
    routes.set(skill.artifact.files[0].url, artifactResponse(index));
  });
  return routes;
}

test('prepare binds the exact successful run, nonce, staging/public slugs, quality, and DAG', () => {
  const { approval } = fixture();
  assert.equal(validateManualApproval(approval), approval);
  assert.equal(approval.pack.stagingSlug, 'monthly-sales-excel-workbook-staging');
  assert.equal(approval.pack.publicSlug, 'monthly-sales-excel-workbook');
  assert.equal(approval.source.artifactDigest, ARTIFACT_DIGEST);
  assert.equal(approval.evaluation.score, 8);
  assert.equal(approval.skills.length, 2);
  assert.equal(approval.executionBinding.bindingDigest, approval.executionBinding.executionDag.bindingDigest);
  assert.deepEqual(approval.executionBinding.opportunityBinding, approval.opportunityBinding);
  assert.equal(approval.runtimeAcceptance.task, 'Create a real workbook.');
  assert.deepEqual(
    approval.runtimeAcceptance.expectedMemberTrace.map(({ canonicalId }) => canonicalId),
    approval.skills.map(({ slug }) => slug),
  );
});

test('prepare rejects quality override, comparison, stale nonce, and source SHA drift', () => {
  for (const mutate of [
    (value) => { value.persisted.selected.autoPublishEligible = false; },
    (value) => { value.persisted.selected.comparisonOf = 'other-pack'; },
    (value) => { value.persisted.persisted[0].response.data.enrichment.contentDispatchNonce = '22222222-2222-4222-8222-222222222222'; },
    (value) => { value.sourceRun.head_sha = 'f'.repeat(40); value.artifact.workflow_run.head_sha = 'f'.repeat(40); },
    (value) => { value.artifact.size_in_bytes = 32 * 1024 * 1024 + 1; },
    (value) => { value.persisted.persisted[0].request.candidate.fitness.score = 9; },
    (value) => { delete value.finalResult.publicationMode; },
    (value) => { value.persisted.persisted[0].request.opportunityBinding.sourceRunAttempt = 0; },
  ]) {
    const value = fixture();
    mutate(value);
    assert.throws(() => buildManualApproval({
      ...value,
      requestedRunId: RUN_ID,
      hashes: { persistSummarySha256: 'c'.repeat(64), finalResultSha256: 'd'.repeat(64) },
    }));
  }
  const value = fixture();
  value.persisted.persisted[0].request.opportunityBinding.candidateSkills[0].license = '';
  const { evidenceDigest: _evidenceDigest, ...unsigned } = value.persisted.persisted[0].request;
  value.persisted.persisted[0].request.evidenceDigest = hash(canonicalJson(unsigned));
  assert.throws(() => buildManualApproval({
    ...value,
    requestedRunId: RUN_ID,
    hashes: { persistSummarySha256: 'c'.repeat(64), finalResultSha256: 'd'.repeat(64) },
  }), /candidate Skill 1 is invalid/);
});

test('manual publish pre-reads the exact generation and sends only artifact-bound authority', async () => {
  const { approval } = fixture();
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, options });
    if (calls.length === 1) return jsonResponse({ data: generationReadback(approval, 'review_pending') });
    if (calls.length === 2) return jsonResponse({ data: {
      slug: approval.pack.publicSlug,
      reviewStatus: 'approved',
		version: approval.pack.version,
      generationId: approval.generationId,
      contentDispatchNonce: approval.contentDispatchNonce,
      sourceRunId: approval.source.runId,
    } });
    return jsonResponse({ data: generationReadback(approval, 'published') });
  };
  const result = await publishManualApproval(approval, {
    apiUrl: 'https://skillstore.io', token: 'manual-key-1234567890', fetchImpl,
  });
  assert.equal(result.replayed, false);
  assert.equal(calls[0].options.method, undefined);
  assert.match(calls[1].url, new RegExp(`/packs/${approval.pack.stagingSlug}/publish$`));
  assert.deepEqual(JSON.parse(calls[1].options.body), {
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    publishMode: 'manual',
    sourceRunId: approval.source.runId,
  });
  assert.equal(calls.length, 3);
});

test('manual publish safely replays an already-published exact generation without POST', async () => {
  const { approval } = fixture();
  const calls = [];
  const result = await publishManualApproval(approval, {
    apiUrl: 'https://skillstore.io',
    token: 'manual-key-1234567890',
    fetchImpl: async (url, options) => {
      calls.push({ url, options });
      return jsonResponse({ data: generationReadback(approval, 'published') });
    },
  });
  assert.equal(result.replayed, true);
  assert.equal(calls.length, 2);
  assert.ok(calls.every((call) => call.options.method == null));
});

test('generation readback rejects evidence or nonce drift before publication', () => {
  const { approval } = fixture();
  const readback = generationReadback(approval, 'review_pending');
  assert.equal(validateGenerationReadback(readback, approval).outcome, 'review_pending');
  readback.attempt.content_dispatch_nonce = '22222222-2222-4222-8222-222222222222';
  assert.throws(() => validateGenerationReadback(readback, approval), /immutable approval/);
});

test('production readback record must echo the exact published generation and status', async () => {
  const { approval } = fixture();
  const evidence = {
    schemaVersion: 'skillstore.pack-production-readback-evidence/v1',
    sourceRunId: approval.source.runId,
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    bindingDigest: approval.executionBinding.bindingDigest,
    manifestDigest: '1'.repeat(64),
    lockfileDigest: '2'.repeat(64),
    fileCount: 2,
    cliPackage: CLI_PACKAGE,
    cliCheck: 'passed',
  };
  const attempt = {
    ...generationReadback(approval, 'published').attempt,
    production_readback_status: 'succeeded',
    production_readback_error: null,
    production_readback_evidence: evidence,
  };
  const recorded = await recordReadback(
    'https://skillstore.io',
    'manual-key-1234567890',
    approval,
    'succeeded',
    null,
    evidence,
    async () => jsonResponse({ data: attempt }),
  );
  assert.equal(recorded.generation_id, approval.generationId);
  await assert.rejects(
    recordReadback(
      'https://skillstore.io',
      'manual-key-1234567890',
      approval,
      'succeeded',
      null,
      evidence,
      async () => jsonResponse({ data: { ...attempt, pack_slug: 'wrong-pack' } }),
    ),
    /exact published generation/,
  );
});

test('production readback reconciles a lost succeeded POST only against the exact committed attempt', async () => {
  const { approval } = fixture();
  const evidence = {
    schemaVersion: 'skillstore.pack-production-readback-evidence/v1',
    sourceRunId: approval.source.runId,
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    bindingDigest: approval.executionBinding.bindingDigest,
    manifestDigest: '1'.repeat(64),
    lockfileDigest: '2'.repeat(64),
    fileCount: 2,
    cliPackage: CLI_PACKAGE,
    cliCheck: 'passed',
  };
  const attempt = {
    ...generationReadback(approval, 'published').attempt,
    production_readback_status: 'succeeded',
    production_readback_error: null,
    production_readback_evidence: evidence,
  };
  const calls = [];
  const recorded = await recordReadback(
    'https://skillstore.io',
    'manual-key-1234567890',
    approval,
    'succeeded',
    null,
    evidence,
    async (url, options) => {
      calls.push({ url, options });
      if (options.method === 'POST') throw new TypeError('response lost');
      return jsonResponse({ data: attempt });
    },
  );
  assert.equal(recorded.production_readback_status, 'succeeded');
  assert.deepEqual(calls.map((call) => call.options.method ?? 'GET'), ['POST', 'GET']);
});

test('production readback keeps the original POST error when reconciliation is unavailable', async () => {
  const { approval } = fixture();
  const evidence = {
    schemaVersion: 'skillstore.pack-production-readback-evidence/v1',
    sourceRunId: approval.source.runId,
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    bindingDigest: approval.executionBinding.bindingDigest,
    manifestDigest: '1'.repeat(64),
    lockfileDigest: '2'.repeat(64),
    fileCount: 2,
    cliPackage: CLI_PACKAGE,
    cliCheck: 'passed',
  };
  const calls = [];
  await assert.rejects(
    recordReadback(
      'https://skillstore.io', 'manual-key-1234567890', approval, 'succeeded', null, evidence,
      async (url, options) => {
        calls.push({ url, options });
        if (options.method === 'POST') throw new TypeError('response lost');
        return jsonResponse({ data: { generation_id: approval.generationId } });
      },
    ),
    /response lost/,
  );
  assert.deepEqual(calls.map((call) => call.options.method ?? 'GET'), ['POST', 'GET']);
});

test('production readback does not reconcile a succeeded POST 4xx', async () => {
  const { approval } = fixture();
  const evidence = {
    schemaVersion: 'skillstore.pack-production-readback-evidence/v1',
    sourceRunId: approval.source.runId,
    generationId: approval.generationId,
    contentDispatchNonce: approval.contentDispatchNonce,
    bindingDigest: approval.executionBinding.bindingDigest,
    manifestDigest: '1'.repeat(64),
    lockfileDigest: '2'.repeat(64),
    fileCount: 2,
    cliPackage: CLI_PACKAGE,
    cliCheck: 'passed',
  };
  let calls = 0;
  await assert.rejects(
    recordReadback(
      'https://skillstore.io', 'manual-key-1234567890', approval, 'succeeded', null, evidence,
      async () => {
        calls += 1;
        return jsonResponse({ message: 'bad request' }, 422);
      },
    ),
    /HTTP 422/,
  );
  assert.equal(calls, 1);
});

test('public proof verifies independent signatures, exact binding, every file hash, and CLI closure', async () => {
  const { approval } = fixture();
  const { manifest, lockfile, contents, trustedSigningKey } = installContracts(approval);
  assert.equal(validateSignedInstallContracts(
    manifest,
    lockfile,
    approval,
    'https://skillstore.io',
    trustedSigningKey,
  ).length, 2);
  const routes = new Map([
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}?lang=en`, jsonResponse({ data: {
      id: approval.pack.id,
      slug: approval.pack.publicSlug,
      reviewStatus: 'approved',
			version: approval.pack.version,
      executionBinding: approval.executionBinding,
      usageGuide: `# Guide\n${approval.executionBinding.usageGuideMarker}`,
      skills: approval.skills,
    } })],
    [`https://skillstore.io/packs/${approval.pack.publicSlug}`, new Response('<html></html>', { status: 200 })],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/manifest`, jsonResponse(manifest)],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/lockfile`, jsonResponse(lockfile)],
    [`https://skillstore.io/downloads/${approval.skills[0].slug}/SKILL.md`, new Response(contents[0])],
    [`https://skillstore.io/downloads/${approval.skills[1].slug}/SKILL.md`, new Response(contents[1])],
  ]);
  const result = await verifyPublicProduction(approval, {
    publicUrl: 'https://skillstore.io',
    trustedSigningKey,
    fetchImpl: async (url) => routes.get(url) ?? new Response('missing', { status: 404 }),
  });
  assert.equal(result.pageStatus, 200);
  assert.equal(result.downloads.length, 2);
  assert.equal(validateCliCheck({ errors: [], updates: [], upToDate: approval.skills.map((skill) => skill.slug) }, approval), true);
  assert.throws(() => validateCliCheck({ errors: [], updates: [], upToDate: [] }, approval), /omitted/);
});

test('public artifact URLs are pinned to the approved Skillstore origin', () => {
  const { approval } = fixture();
  const contracts = installContracts(approval);
  const file = contracts.manifest.signed.skills[0].artifact.files[0];
  file.url = 'https://127.0.0.1/internal/SKILL.md';
  contracts.manifest.signed.skills[0].downloadUrl = file.url;
  resignInstallContracts(contracts);
  assert.throws(
    () => validateSignedInstallContracts(
      contracts.manifest,
      contracts.lockfile,
      approval,
      'https://skillstore.io',
      contracts.trustedSigningKey,
    ),
    /Signed artifact file.*invalid/,
  );
});

test('signed manifest artifact provenance rejects an unapproved source commit', () => {
  const { approval } = fixture();
  const contracts = installContracts(approval);
  const skill = contracts.manifest.signed.skills[0];
  const artifact = {
    ...skill.artifact,
    source: { ...skill.artifact.source, commit: 'c'.repeat(40) },
  };
  contracts.manifest.signed.skills[0] = { ...skill, artifact };
  contracts.manifest.skills[0] = contracts.manifest.signed.skills[0];
  resignInstallContracts(contracts);
  assert.throws(
    () => validateSignedInstallContracts(
      contracts.manifest,
      contracts.lockfile,
      approval,
      'https://skillstore.io',
      contracts.trustedSigningKey,
    ),
    /Signed Pack manifest artifact provenance differs from the approved candidate Skill/,
  );
});

test('standalone lockfile artifact provenance rejects an unapproved source path', () => {
  const { approval } = fixture();
  const contracts = installContracts(approval);
  const skill = contracts.lockfile.skills[0];
  contracts.lockfile.skills = contracts.lockfile.skills.map((entry, index) => (
    index === 0 ? {
      ...skill,
      artifact: {
        ...skill.artifact,
        source: { ...skill.artifact.source, path: 'skills/not-approved' },
      },
    } : entry
  ));
  resignInstallContracts(contracts);
  assert.throws(
    () => validateSignedInstallContracts(
      contracts.manifest,
      contracts.lockfile,
      approval,
      'https://skillstore.io',
      contracts.trustedSigningKey,
    ),
    /Independently signed Pack lockfile artifact provenance differs from the approved candidate Skill/,
  );
});

test('public artifact downloads refuse redirects', async () => {
  const { approval } = fixture();
  const { manifest, lockfile, contents, trustedSigningKey } = installContracts(approval);
  const routes = publicRoutes(approval, manifest, lockfile, (index) => (
    index === 0
      ? new Response('', { status: 302, headers: { location: 'https://evil.example/SKILL.md' } })
      : new Response(contents[index])
  ));
  let redirect;
  await assert.rejects(
    verifyPublicProduction(approval, {
      publicUrl: 'https://skillstore.io',
      trustedSigningKey,
      fetchImpl: async (url, options) => {
        if (url.includes('/downloads/')) redirect = options.redirect;
        return routes.get(url) ?? new Response('missing', { status: 404 });
      },
    }),
    /Artifact download returned HTTP 302/,
  );
  assert.equal(redirect, 'error');
});

test('public artifact downloads reject oversized Content-Length before reading', async () => {
  const { approval } = fixture();
  const { manifest, lockfile, contents, trustedSigningKey } = installContracts(approval);
  const routes = publicRoutes(approval, manifest, lockfile, (index) => new Response(contents[index], {
    headers: index === 0 ? { 'content-length': String(contents[index].length + 1) } : {},
  }));
  await assert.rejects(
    verifyPublicProduction(approval, {
      publicUrl: 'https://skillstore.io',
      trustedSigningKey,
      fetchImpl: async (url) => routes.get(url) ?? new Response('missing', { status: 404 }),
    }),
    /Content-Length mismatch/,
  );
});

test('public artifact downloads cancel an oversized stream', async () => {
  const { approval } = fixture();
  const { manifest, lockfile, contents, trustedSigningKey } = installContracts(approval);
  let cancelled = false;
  const routes = publicRoutes(approval, manifest, lockfile, (index) => {
    if (index > 0) return new Response(contents[index]);
    return new Response(new ReadableStream({
      start(controller) { controller.enqueue(new Uint8Array(contents[index].length + 1)); },
      cancel() { cancelled = true; },
    }));
  });
  await assert.rejects(
    verifyPublicProduction(approval, {
      publicUrl: 'https://skillstore.io',
      trustedSigningKey,
      fetchImpl: async (url) => routes.get(url) ?? new Response('missing', { status: 404 }),
    }),
    /exceeds its signed byte limit/,
  );
  assert.equal(cancelled, true);
});

test('public artifact downloads hash exact-size streamed bytes', async () => {
  const { approval } = fixture();
  const { manifest, lockfile, contents, trustedSigningKey } = installContracts(approval);
  let chunksRead = 0;
  const routes = publicRoutes(approval, manifest, lockfile, (index) => {
    const content = contents[index];
    const split = Math.max(1, Math.floor(content.length / 2));
    let part = 0;
    return new Response(new ReadableStream({
      pull(controller) {
        const start = part === 0 ? 0 : split;
        part += 1;
        chunksRead += 1;
        controller.enqueue(content.subarray(start, start === 0 ? split : content.length));
        if (start !== 0) controller.close();
      },
    }), { headers: { 'content-length': String(content.length) } });
  });
  const result = await verifyPublicProduction(approval, {
    publicUrl: 'https://skillstore.io',
    trustedSigningKey,
    fetchImpl: async (url) => routes.get(url) ?? new Response('missing', { status: 404 }),
  });
  assert.equal(chunksRead, 4);
  assert.deepEqual(result.downloads.map((file) => file.bytes), contents.map((content) => content.length));
});

test('fresh install readback binds registry provenance, orchestration, every member, and a fresh installed execution', async () => {
  const { approval, orchestrationContent, runtimeAcceptance } = fixture();
  const home = mkdtempSync(join(tmpdir(), 'pack-publish-readback-'));
  const skillsRoot = join(home, '.agents', 'skills');
  mkdirSync(skillsRoot, { recursive: true });
  for (const [index, skill] of approval.skills.entries()) {
    const directory = join(skillsRoot, skill.slug);
    mkdirSync(directory);
    writeFileSync(join(directory, 'SKILL.md'), SKILL_CONTENTS[index]);
  }
  const orchestration = {
    slug: approval.runtimeAcceptance.orchestration.canonicalId,
    contentHash: approval.runtimeAcceptance.orchestration.contentHash,
		treeHash: approval.runtimeAcceptance.orchestration.treeHash,
    version: approval.pack.version,
    bindingDigest: approval.executionBinding.bindingDigest,
  };
  const orchestrationDirectory = join(skillsRoot, orchestration.slug);
  mkdirSync(orchestrationDirectory);
  writeFileSync(join(orchestrationDirectory, 'SKILL.md'), orchestrationContent);
  writeFileSync(join(orchestrationDirectory, 'skillstore-pack-orchestration.json'), JSON.stringify({
    schemaVersion: 'skillstore.pack-orchestration-install/v1',
    managedBy: 'skillstore-cli',
    slug: orchestration.slug,
    packSlug: approval.pack.publicSlug,
    packVersion: orchestration.version,
    orchestrationVersion: orchestration.version,
    contentHash: orchestration.contentHash,
		treeHash: orchestration.treeHash,
    bindingDigest: orchestration.bindingDigest,
  }));
  mkdirSync(join(home, '.agents'), { recursive: true });
  writeFileSync(join(home, '.agents', '.skill-lock.json'), JSON.stringify({
    version: 1,
    skills: Object.fromEntries(approval.skills.map((skill) => [skill.slug, {
      slug: skill.slug,
      version: skill.version,
      treeHash: skill.treeHash,
      zipHash: 'f'.repeat(64),
      source: 'skillstore',
    }])),
  }));
  const registry = registryProofFixture();
  assert.equal(validateRegistryProof(
    registry.metadata,
    registry.packageLock,
    registry.signatureAudit,
  ).package, CLI_PACKAGE);
  const readback = await buildInstallReadback(approval, {
    home,
    registryMetadata: registry.metadata,
    packageLock: registry.packageLock,
    signatureAudit: registry.signatureAudit,
    cliCheck: { errors: [], updates: [], upToDate: approval.skills.map((skill) => skill.slug) },
  });
  assert.equal(validateInstallReadback(readback, approval), readback);
  assert.deepEqual(readback.orchestration, {
    canonicalId: orchestration.slug,
    contentHash: orchestration.contentHash,
		treeHash: orchestration.treeHash,
    version: orchestration.version,
    bindingDigest: orchestration.bindingDigest,
  });
  assert.deepEqual(readback.members, approval.runtimeAcceptance.expectedMemberTrace.map(
    ({ sequence: _sequence, ...identity }) => identity,
  ));
  const identities = await buildInstalledRuntimeIdentities(approval, readback, home);
  assert.equal(identities.orchestration.treeHash, readback.orchestration.treeHash);
  assert.equal(identities.orchestration.path, join(skillsRoot, orchestration.slug));
  assert.deepEqual(identities.members.map(({ path, ...identity }) => identity),
    approval.executionBinding.executionDag.skillBindings.map((binding) => ({
      canonicalId: binding.canonicalId,
      contentHash: binding.contentHash,
      treeHash: binding.treeHash,
      version: binding.version,
      slotIds: binding.slotIds,
    })));

  const installedAcceptance = structuredClone(runtimeAcceptance);
  installedAcceptance.trace.events[0] = {
    canonicalId: readback.orchestration.canonicalId,
    contentHash: readback.orchestration.contentHash,
    treeHash: readback.orchestration.treeHash,
    version: readback.orchestration.version,
    sequence: 1,
  };
  delete installedAcceptance.evidenceDigest;
  installedAcceptance.evidenceDigest = hash(canonicalJson(installedAcceptance));
  const runtimeReadback = buildRuntimeReadback(approval, readback, installedAcceptance);
  assert.equal(validateRuntimeReadback(runtimeReadback, approval, readback), runtimeReadback);
  assert.equal(runtimeReadback.runtimeEvidenceDigest, installedAcceptance.evidenceDigest);
  assert.equal(runtimeReadback.prepublishRuntimeEvidenceDigest,
    approval.runtimeAcceptance.prepublishEvidenceDigest);

	const rejectedAcceptance = structuredClone(installedAcceptance);
	rejectedAcceptance.trace.events[0].version = '9.9.9';
	delete rejectedAcceptance.evidenceDigest;
	rejectedAcceptance.evidenceDigest = hash(canonicalJson(rejectedAcceptance));
	assert.throws(
		() => buildRuntimeReadback(approval, readback, rejectedAcceptance),
		/Runtime orchestration trace/,
	);

	const receiptPath = join(orchestrationDirectory, 'skillstore-pack-orchestration.json');
	const receipt = JSON.parse(readFileSync(receiptPath, 'utf8'));
	writeFileSync(receiptPath, JSON.stringify({ ...receipt, treeHash: '0'.repeat(64) }));
	await assert.rejects(
		buildInstallReadback(approval, {
			home,
			registryMetadata: registry.metadata,
			packageLock: registry.packageLock,
			signatureAudit: registry.signatureAudit,
			cliCheck: { errors: [], updates: [], upToDate: approval.skills.map((skill) => skill.slug) },
		}),
		/Installed Pack orchestration identity differs/,
	);
	writeFileSync(receiptPath, JSON.stringify({ ...receipt, packVersion: '9.9.9', orchestrationVersion: '9.9.9' }));
	await assert.rejects(
		buildInstallReadback(approval, {
			home,
			registryMetadata: registry.metadata,
			packageLock: registry.packageLock,
			signatureAudit: registry.signatureAudit,
			cliCheck: { errors: [], updates: [], upToDate: approval.skills.map((skill) => skill.slug) },
		}),
		/Installed Pack orchestration identity differs/,
	);
});

test('runtime readback fails closed before it can accept missing evidence', () => {
  const { approval } = fixture();
  assert.equal(approval.runtimeAcceptance.executableFixtureIncluded, true);
  assert.equal(approval.runtimeAcceptance.executableValidatorIncluded, true);
  assert.throws(
    () => validateRuntimeReadback({}, approval, {}),
    /Install readback evidence is invalid/,
  );
});

test('public HTTP 5xx with an HTML body is retryable before JSON parsing', async () => {
  const { approval } = fixture();
  await assert.rejects(
    verifyPublicProduction(approval, {
      publicUrl: 'https://skillstore.io',
      fetchImpl: async () => new Response('<html>upstream unavailable</html>', { status: 503 }),
    }),
    (error) => error instanceof RetryablePublicReadbackError && /HTTP 503/.test(error.message),
  );
});

test('signature verification fails closed on a changed signed payload', () => {
  const { approval } = fixture();
  const { manifest, trustedSigningKey } = installContracts(approval);
  assert.equal(verifyCanonicalEd25519(manifest.signed, manifest.signature, trustedSigningKey), true);
  assert.throws(
    () => verifyCanonicalEd25519(manifest.signed, manifest.signature),
    /trusted production key/,
  );
  assert.throws(
    () => verifyCanonicalEd25519(
      { ...manifest.signed, generatedAt: 'changed' },
      manifest.signature,
      trustedSigningKey,
    ),
    /verification failed/,
  );
});

test('workflow separates public authority, credential-free runtime, and hosted completion', () => {
  const workflow = readFileSync(join(REPO_ROOT, '.github/workflows/publish-pack-production-v4.yml'), 'utf8');
  assert.match(workflow, /workflow_dispatch:\n\s+inputs:\n\s+source_run_id:/);
  const inputs = workflow.slice(workflow.indexOf('    inputs:'), workflow.indexOf('\npermissions:'));
  assert.doesNotMatch(inputs, /(?:content_dispatch_nonce|generation_id|pack_slug|binding_digest):/);
  assert.match(workflow, /  prepare:/);
  assert.match(workflow, /  publish:[\s\S]*needs: prepare/);
  assert.match(workflow, /  runtime:[\s\S]*needs: \[prepare, publish\][\s\S]*runs-on: ubuntu-24\.04/);
  assert.match(workflow, /  complete:[\s\S]*needs: \[prepare, publish, runtime\]/);
  assert.match(workflow, /environment:\n\s+name: production/);
  assert.match(workflow, /actions\/artifacts\/\$ARTIFACT_ID\/zip/);
  const sourceArtifactSection = workflow.slice(
    workflow.indexOf('      - name: Resolve the exact source run and final artifact'),
    workflow.indexOf('      - name: Validate generation, nonce, source SHA, quality, and binding'),
  );
  assert.doesNotMatch(sourceArtifactSection, /actions\/download-artifact/);
  assert.match(workflow, /source-artifact\.zip/);
  assert.match(workflow, /artifact digest mismatch/);
  assert.match(workflow, /compressed size is invalid or exceeds 32 MiB/);
  assert.match(workflow, /entry count exceeds 1024/);
  assert.match(workflow, /uncompressed size exceeds 128 MiB/);
  assert.match(workflow, /contains an unsafe ZIP path/);
  assert.match(workflow, /contains a symbolic-link entry/);
  assert.match(workflow, /contains a symbolic link/);
  assert.match(workflow, /PACK_PRODUCTION_AUTO_PUBLISH_ENABLED/);
  assert.match(workflow, /PACK_PRODUCTION_MANUAL_PUBLISH_KEY/);
  const publish = workflow.slice(workflow.indexOf('  publish:'), workflow.indexOf('  runtime:'));
  const cliPreflight = publish.slice(
    publish.indexOf('      - name: Preflight the exact public Marketplace CLI release'),
    publish.indexOf('      - name: Download the reviewed immutable approval handoff'),
  );
  assert.match(cliPreflight, /MARKETPLACE_CLI_VERSION: '__SET_AFTER_MARKETPLACE_CLI_RELEASE__'/);
  assert.match(cliPreflight, /\^\(0\|\[1-9\]\[0-9\]\*\)\\\.\(0\|\[1-9\]\[0-9\]\*\)\\\.\(0\|\[1-9\]\[0-9\]\*\)\$/);
  assert.match(cliPreflight, /npm view --registry=https:\/\/registry\.npmjs\.org "skillstore@\$MARKETPLACE_CLI_VERSION" --json/);
  assert.match(cliPreflight, /\.dist\.integrity[\s\S]*sha512-/);
  assert.ok(
    publish.indexOf('Preflight the exact public Marketplace CLI release')
      < publish.indexOf('Publish through the nonce-bound manual API'),
    'the placeholder must fail before the production publish POST',
  );
  assert.doesNotMatch(workflow, /skillstore@0\.1\.11/);
  assert.match(workflow, /npm audit signatures --json/);
  assert.match(workflow, /npm install --ignore-scripts --save-exact "skillstore@\$MARKETPLACE_CLI_VERSION"/);
  assert.match(workflow, /MARKETPLACE_CLI_VERSION: \$\{\{ needs\.publish\.outputs\.marketplace_cli_version \}\}/);
  assert.match(workflow, /MARKETPLACE_CLI_INTEGRITY: \$\{\{ needs\.publish\.outputs\.marketplace_cli_integrity \}\}/);
  assert.match(workflow, /package-lock\.json[\s\S]*MARKETPLACE_CLI_INTEGRITY/);
  assert.match(workflow, /\.\/node_modules\/\.bin\/skillstore add "@\$PACK_SLUG" --agent codex --overwrite/);
  assert.match(workflow, /uses: \.\/\.github\/actions\/download-skillstore-cli/);
  assert.match(workflow, /actions\/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1 # v3/);
  assert.match(workflow, /repositories: marketplace,skillstore/);
  assert.match(workflow, /permission-contents: read/);
  assert.match(workflow, /token: \$\{\{ steps\.evaluation-cli-token\.outputs\.token \}\}/);
  assert.match(workflow, /require-checksum: 'true'/);
  assert.match(workflow, /expected-sha256: \$\{\{ needs\.prepare\.outputs\.cli_sha256 \}\}/);
  assert.match(workflow, /steps\.evaluation-cli\.outputs\.cli-sha256/);
  assert.match(workflow, /\/opt\/pack-evaluator\/bin\/skillstore-cli pack runtime-accept/);
  assert.match(workflow, /HOME="\$PACK_RUNTIME_HOME"/);
  assert.match(workflow, /CODEX_HOME=\/opt\/pack-evaluator\/codex-home/);
  assert.match(workflow, /--identity-file "\$PACK_RUNTIME_EVIDENCE\/installed-identities\.json"/);
  assert.match(workflow, /runtime-acceptance\.json/);
  assert.match(workflow, /runtime-readback/);
  const runtime = workflow.slice(workflow.indexOf('  runtime:'), workflow.indexOf('  complete:'));
  assert.doesNotMatch(runtime, /secrets\.PACK_PRODUCTION_MANUAL_PUBLISH_KEY/);
  assert.doesNotMatch(runtime, /secrets\.SKILLSTORE_API_URL/);
  assert.match(runtime, /secrets\.PACK_EVALUATOR_HELM_API_KEY/);
  assert.match(runtime, /secrets\.APP_PRIVATE_KEY/);
  assert.equal((runtime.match(/\$\{\{\s*secrets\./g) ?? []).length, 2);
  assert.match(runtime, /PACK_EVALUATOR_ACTIVITY_FILE=\/home\/packproxy\/evidence\/proxy-activity\.jsonl/);
  assert.match(runtime, /proxy-activity\.jsonl/);
  const completion = workflow.slice(workflow.indexOf('  complete:'));
  assert.match(completion, /runs-on: ubuntu-latest/);
  assert.doesNotMatch(completion, /name: pack-production-readback/);
  assert.match(completion, /secrets\.PACK_PRODUCTION_READBACK_KEY/);
  assert.doesNotMatch(completion, /secrets\.PACK_PRODUCTION_MANUAL_PUBLISH_KEY/);
  assert.match(completion, /if: always\(\) && github\.ref == 'refs\/heads\/main' && needs\.prepare\.result == 'success'/);
  const successCompletion = completion.slice(
    completion.indexOf('      - name: Record exact production acceptance'),
    completion.indexOf('      - name: Record terminal publish, proof, or runtime failure without production proof'),
  );
  const failedCompletion = completion.slice(
    completion.indexOf('      - name: Record terminal publish, proof, or runtime failure without production proof'),
    completion.indexOf('      - name: Upload completed production evidence'),
  );
  assert.match(successCompletion, /needs\.publish\.result == 'success'/);
  assert.match(successCompletion, /needs\.runtime\.result == 'success'/);
  assert.match(successCompletion, /steps\.public-proof\.outcome == 'success'/);
  assert.match(successCompletion, /steps\.runtime-proof\.outcome == 'success'/);
  assert.match(successCompletion, /--status succeeded/);
  assert.match(successCompletion, /--runtime-readback/);
  assert.match(completion, /id: public-proof\n\s+if: needs\.publish\.result == 'success'\n\s+continue-on-error: true/);
  assert.match(completion, /id: runtime-proof\n\s+if: needs\.publish\.result == 'success' && needs\.runtime\.result == 'success'\n\s+continue-on-error: true/);
  assert.match(failedCompletion, /always\(\)/);
  assert.match(failedCompletion, /needs\.publish\.result != 'success'/);
  assert.match(failedCompletion, /needs\.runtime\.result != 'success'/);
  assert.match(failedCompletion, /steps\.public-proof\.outcome != 'success'/);
  assert.match(failedCompletion, /steps\.runtime-proof\.outcome != 'success'/);
  assert.match(failedCompletion, /--status failed/);
  assert.doesNotMatch(failedCompletion, /runtime-readback|--status succeeded|retry|retract/);
  assert.match(completion, /Upload completed production evidence\n\s+if: always\(\)/);
  assert.match(workflow, /Upload exact public publication evidence\n\s+if: always\(\)/);
  const publisher = readFileSync(join(REPO_ROOT, 'scripts/pack-production-manual-publish.mjs'), 'utf8');
  assert.match(publisher, /CLI_PACKAGE = 'skillstore@__SET_AFTER_MARKETPLACE_CLI_RELEASE__'/);
  assert.doesNotMatch(publisher, /skillstore@0\.1\.11/);
  const production = readFileSync(join(REPO_ROOT, 'scripts/pack-production.mjs'), 'utf8');
  const finalize = production.slice(
    production.indexOf('async function finalize(args)'),
    production.indexOf('async function reportSlo(args)'),
  );
  assert.match(finalize, /buildHardDisabledReviewPendingResult/);
  assert.match(finalize, /autoPublishRequested/);
  assert.doesNotMatch(finalize, /\/api\/automation\/packs\/[^\n]+\/publish/);
  assert.doesNotMatch(finalize, /outcome: 'published'/);
});

test('legacy Pack review refuses guide replacement and marked v4 generation commands', () => {
  const workflow = readFileSync(join(REPO_ROOT, '.github/workflows/pack-review.yml'), 'utf8');
  assert.match(workflow, /\/approve --guide is disabled/);
  assert.match(workflow, /isPackProductionV4/);
  assert.match(workflow, /Pack Production v4 can only be published by the generation-bound production workflow/);
  assert.doesNotMatch(workflow, /const guideMatch =/);
  assert.match(workflow, /modifiedGuide: null/);
  assert.match(workflow, /const isMissingLegacyPack = response\.status === 404/);
  assert.match(workflow, /callbackError\?\.message === 'Pack not found'/);
  assert.match(workflow, /Callback no-op: legacy Pack/);
});
