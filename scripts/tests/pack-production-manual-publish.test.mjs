import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash, generateKeyPairSync, sign } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  buildManualApproval,
  canonicalJson,
  publishManualApproval,
  recordReadback,
  RetryablePublicReadbackError,
  validateCliCheck,
  validateGenerationReadback,
  validateManualApproval,
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

function hash(value) {
  return createHash('sha256').update(value).digest('hex');
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
  });
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
    requestedRunId: RUN_ID,
    hashes: { persistSummarySha256: 'c'.repeat(64), finalResultSha256: 'd'.repeat(64) },
  });
  return { evaluation, selected, persisted, finalResult, sourceRun, workflow, artifact, approval };
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
      url: `https://raw.example/${skill.slug}/SKILL.md`,
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
      treeHash: `${index + 1}`.repeat(64),
      downloadUrl: artifactFiles[0].url,
      contentHash: skill.contentHash,
      artifact: {
        type: 'skill-files',
        source: { type: 'github', owner: 'aiskillstore', repo: 'marketplace', ref: SOURCE_SHA, commit: SOURCE_SHA, path: `skills/${skill.slug}` },
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
    pack: { slug: approval.pack.publicSlug, name: 'Pack', version: '1.0.0', visibility: 'public' },
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
    trustedSigningKey: { keyId: 'test-key', publicKeyX: publicJwk.x },
  };
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
  ]) {
    const value = fixture();
    mutate(value);
    assert.throws(() => buildManualApproval({
      ...value,
      requestedRunId: RUN_ID,
      hashes: { persistSummarySha256: 'c'.repeat(64), finalResultSha256: 'd'.repeat(64) },
    }));
  }
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
      generationId: approval.generationId,
      contentDispatchNonce: approval.contentDispatchNonce,
      sourceRunId: approval.source.runId,
    } });
    return jsonResponse({ data: generationReadback(approval, 'published') });
  };
  const result = await publishManualApproval(approval, {
    apiUrl: 'https://skillstore.example', token: 'manual-key-1234567890', fetchImpl,
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
    apiUrl: 'https://skillstore.example',
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
    cliPackage: 'skillstore@0.1.9',
    cliCheck: 'passed',
  };
  const attempt = {
    ...generationReadback(approval, 'published').attempt,
    production_readback_status: 'succeeded',
    production_readback_error: null,
    production_readback_evidence: evidence,
  };
  const recorded = await recordReadback(
    'https://skillstore.example',
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
      'https://skillstore.example',
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
      executionBinding: approval.executionBinding,
      usageGuide: `# Guide\n${approval.executionBinding.usageGuideMarker}`,
      skills: approval.skills,
    } })],
    [`https://skillstore.io/packs/${approval.pack.publicSlug}`, new Response('<html></html>', { status: 200 })],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/manifest`, jsonResponse(manifest)],
    [`https://skillstore.io/api/packs/${approval.pack.publicSlug}/lockfile`, jsonResponse(lockfile)],
    [`https://raw.example/${approval.skills[0].slug}/SKILL.md`, new Response(contents[0])],
    [`https://raw.example/${approval.skills[1].slug}/SKILL.md`, new Response(contents[1])],
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

test('workflow has source-run-only input, two phases, environment gate, exact artifact id, and real Linux CLI', () => {
  const workflow = readFileSync(join(REPO_ROOT, '.github/workflows/publish-pack-production-v4.yml'), 'utf8');
  assert.match(workflow, /workflow_dispatch:\n\s+inputs:\n\s+source_run_id:/);
  const inputs = workflow.slice(workflow.indexOf('    inputs:'), workflow.indexOf('\npermissions:'));
  assert.doesNotMatch(inputs, /(?:content_dispatch_nonce|generation_id|pack_slug|binding_digest):/);
  assert.match(workflow, /  prepare:/);
  assert.match(workflow, /  publish:[\s\S]*needs: prepare/);
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
  assert.match(workflow, /contains a symbolic link/);
  assert.match(workflow, /PACK_PRODUCTION_AUTO_PUBLISH_ENABLED/);
  assert.match(workflow, /PACK_PRODUCTION_MANUAL_PUBLISH_KEY/);
  assert.match(workflow, /npx --yes skillstore@0\.1\.9 add "@\$PACK_SLUG" --agent codex --overwrite/);
  assert.match(workflow, /npx --yes skillstore@0\.1\.9 check --json/);
  assert.match(workflow, /public_readback=[^;]+; cli_readback=/);
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
});
