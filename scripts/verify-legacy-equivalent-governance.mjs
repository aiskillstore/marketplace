#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CLI_VERSION = '2.4.2';
const MAX_BATCH_SIZE = 500;
const SHA256_RE = /^[0-9a-f]{64}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function fail(message) {
  throw new Error(message);
}

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value)
      .sort(([left], [right]) => left.localeCompare(right, 'en-US'))
      .map(([key, item]) => [key, canonicalize(item)]));
  }
  return value;
}

function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function asMap(rows, key, label) {
  if (!Array.isArray(rows)) fail(`${label} is not an array`);
  const map = new Map();
  for (const row of rows) {
    const value = row?.[key];
    if (typeof value !== 'string' || !value || map.has(value)) {
      fail(`${label} contains an invalid or duplicate ${key}`);
    }
    map.set(value, row);
  }
  return map;
}

function legacyGroups(plan, classification) {
  const legacyRows = classification?.cohorts?.legacy_algorithm_equivalent;
  const selected = asMap(plan?.selected, 'slug', 'plan selected rows');
  const legacy = asMap(legacyRows, 'slug', 'legacy cohort');
  if (plan?.selectedCount !== plan?.selected?.length || plan.selectedCount > MAX_BATCH_SIZE) {
    fail('plan is not a bounded complete batch');
  }
  if (classification?.schemaVersion !== 1 || classification?.status !== 'classified') {
    fail('classification contract is not frozen');
  }
  for (const slug of legacy.keys()) {
    if (!selected.has(slug)) fail(`legacy cohort contains an unplanned slug: ${slug}`);
  }
  const groups = [];
  for (const batch of plan.batches || []) {
    for (const group of batch.groups || []) {
      const slugs = group.slugs.filter((slug) => legacy.has(slug));
      if (slugs.length === 0) continue;
      groups.push({
        batchIndex: batch.index,
        marketplaceCommit: group.marketplaceCommit,
        count: slugs.length,
        slugs,
        paths: slugs.map((slug) => selected.get(slug).path),
      });
    }
  }
  if (groups.reduce((count, group) => count + group.count, 0) !== legacy.size) {
    fail('legacy execution groups do not cover the frozen cohort exactly once');
  }
  return groups;
}

function validateAdminWrapper(wrapper, expected, mode, classification) {
  if (
    wrapper?.batchIndex !== expected.batchIndex
    || wrapper?.marketplaceCommit !== expected.marketplaceCommit
    || wrapper?.selectedCount !== expected.count
    || wrapper?.exitCode !== 0
    || canonicalJson(wrapper?.slugs) !== canonicalJson(expected.slugs)
  ) {
    fail(`${mode} wrapper does not match the frozen group`);
  }
  const result = wrapper.result;
  if (
    result?.success !== true
    || result?.mode !== mode
    || result?.validated !== expected.count
    || result?.governed !== (mode === 'execute' ? expected.count : 0)
    || !Array.isArray(result?.results)
    || result.results.length !== expected.count
  ) {
    fail(`${mode} administrator result has an invalid summary`);
  }
  const legacy = asMap(classification.cohorts.legacy_algorithm_equivalent, 'slug', 'legacy cohort');
  const results = asMap(result.results, 'slug', `${mode} administrator rows`);
  for (const slug of expected.slugs) {
    const frozen = legacy.get(slug);
    const row = results.get(slug);
    if (
      !frozen
      || row?.mode !== mode
      || row?.skillId !== frozen.id
      || row?.sourceAuditId !== frozen.publicEligibilityAuditId
    ) {
      fail(`${mode} administrator row is not bound to frozen evidence for ${slug}`);
    }
    if (mode === 'dry-run') {
      if (
        row.derivedAuditId !== null
        || row.artifactVersionId !== null
        || row.artifactRevision !== null
        || row.artifactCreated !== null
        || row.scoreSnapshotId !== null
      ) {
        fail(`dry-run reported a write for ${slug}`);
      }
    } else if (
      !UUID_RE.test(String(row.derivedAuditId || ''))
      || !UUID_RE.test(String(row.artifactVersionId || ''))
      || row.artifactRevision !== 1
      || typeof row.artifactCreated !== 'boolean'
      || !UUID_RE.test(String(row.scoreSnapshotId || ''))
    ) {
      fail(`execute result lacks immutable identities for ${slug}`);
    }
  }
}

export function createLegacyGovernanceBoundary({
  plan,
  classification,
  dryRunResults,
  paths,
  metadata,
}) {
  if (
    metadata.cliVersion !== CLI_VERSION
    || !SHA256_RE.test(String(metadata.cliSha256 || ''))
    || !/^\d+$/.test(String(metadata.runId))
    || !/^[0-9a-f]{40}$/.test(String(metadata.workflowCommit || ''))
    || metadata.repository !== 'aiskillstore/marketplace'
  ) {
    fail('invalid dry-run workflow metadata');
  }
  const groups = legacyGroups(plan, classification);
  if (!Array.isArray(dryRunResults) || dryRunResults.length !== groups.length) {
    fail('dry-run result group count does not match the frozen legacy cohort');
  }
  for (let index = 0; index < groups.length; index++) {
    validateAdminWrapper(dryRunResults[index], groups[index], 'dry-run', classification);
  }
  return {
    schemaVersion: 1,
    status: 'frozen',
    workflow: 'govern-legacy-equivalent-artifacts',
    repository: metadata.repository,
    runId: String(metadata.runId),
    workflowCommit: metadata.workflowCommit,
    cliVersion: CLI_VERSION,
    cliSha256: metadata.cliSha256,
    selectedCount: plan.selectedCount,
    legacyCount: classification.counts.legacy_algorithm_equivalent,
    lastSelected: plan.lastSelected,
    hashes: {
      plan: sha256File(paths.plan),
      classification: sha256File(paths.classification),
      preInventory: sha256File(paths.preInventory),
      dryRunResults: sha256File(paths.dryRunResults),
      sourceEvidence: sha256File(paths.sourceEvidence),
    },
    groups,
  };
}

export function verifyLegacyGovernanceBoundary({
  boundary,
  plan,
  classification,
  frozenInventory,
  currentInventory,
  frozenSourceEvidence,
  currentSourceEvidence,
  paths,
  expectedRunId,
}) {
  if (
    boundary?.schemaVersion !== 1
    || boundary?.status !== 'frozen'
    || boundary?.workflow !== 'govern-legacy-equivalent-artifacts'
    || boundary?.repository !== 'aiskillstore/marketplace'
    || boundary?.runId !== String(expectedRunId)
    || boundary?.cliVersion !== CLI_VERSION
    || !SHA256_RE.test(String(boundary?.cliSha256 || ''))
  ) {
    fail('downloaded boundary metadata is invalid');
  }
  for (const [key, path] of Object.entries(paths)) {
    if (boundary.hashes?.[key] !== sha256File(path)) {
      fail(`downloaded boundary ${key} hash mismatch`);
    }
  }
  const expectedGroups = legacyGroups(plan, classification);
  if (canonicalJson(boundary.groups) !== canonicalJson(expectedGroups)) {
    fail('downloaded boundary groups do not match plan/classification');
  }
  if (canonicalJson(frozenSourceEvidence) !== canonicalJson(currentSourceEvidence)) {
    fail('Skill metadata or source audit changed after the frozen dry-run boundary');
  }
  const frozenSkills = asMap(frozenInventory.rows, 'slug', 'frozen Skills');
  const currentSkills = asMap(currentInventory.rows, 'slug', 'current Skills');
  const artifacts = asMap(currentInventory.artifacts, 'skill_id', 'current artifacts');
  const observations = asMap(currentInventory.observations, 'skill_id', 'current observations');
  const legacySlugs = new Set(classification.cohorts.legacy_algorithm_equivalent.map((row) => row.slug));
  if (
    canonicalJson(frozenInventory.packMemberships) !== canonicalJson(currentInventory.packMemberships)
    || canonicalJson(frozenInventory.packs) !== canonicalJson(currentInventory.packs)
    || frozenSkills.size !== currentSkills.size
  ) {
    fail('production state changed after the frozen dry-run boundary');
  }
  let resumableCount = 0;
  for (const selected of plan.selected) {
    const before = frozenSkills.get(selected.slug);
    const current = currentSkills.get(selected.slug);
    if (!before || !current) fail(`production state changed for ${selected.slug}`);
    if (!legacySlugs.has(selected.slug)) {
      if (canonicalJson(before) !== canonicalJson(current)) {
        fail(`non-legacy production state changed for ${selected.slug}`);
      }
      continue;
    }
    if (canonicalJson(before) === canonicalJson(current)) continue;
    const repair = selected.evidence.artifact.hashRepair;
    const artifact = artifacts.get(selected.id);
    const observation = observations.get(selected.id);
    if (
      current.artifact_revision !== 1
      || !UUID_RE.test(String(current.current_artifact_version_id || ''))
      || current.content_hash !== repair.packagedContentHash
      || current.tree_hash !== repair.packagedTreeHash
      || current.marketplace_commit_sha !== selected.marketplaceCommit
      || current.plugin_path !== selected.path
      || current.public_eligible !== true
      || !UUID_RE.test(String(current.public_eligibility_audit_id || ''))
      || current.public_eligibility_audit_id === selected.publicEligibilityAuditId
      || !sameTimestamp(current.published_at, selected.publishedAt)
      || !sameTimestamp(current.updated_at, selected.updatedAt)
      || artifact?.id !== current.current_artifact_version_id
      || artifact?.artifact_revision !== 1
      || artifact?.content_hash !== repair.packagedContentHash
      || artifact?.tree_hash !== repair.packagedTreeHash
      || artifact?.marketplace_commit_sha !== selected.marketplaceCommit
      || artifact?.source_path !== selected.path
      || artifact?.hash_provenance?.classification !== 'legacy_algorithm_equivalent'
      || artifact?.hash_provenance?.report?.contentHash !== repair.reportContentHash
      || artifact?.hash_provenance?.report?.treeHash !== repair.reportTreeHash
      || observation?.artifact_version_id !== artifact.id
      || observation?.marketplace_commit_sha !== selected.marketplaceCommit
      || observation?.source_path !== selected.path
    ) {
      fail(`production state changed incompatibly for ${selected.slug}`);
    }
    resumableCount++;
  }
  if (artifacts.size !== resumableCount || observations.size !== resumableCount) {
    fail('resumable artifact/observation scope contains unexpected rows');
  }
  return {
    schemaVersion: 1,
    status: 'execution_preflight_verified',
    runId: boundary.runId,
    legacyCount: boundary.legacyCount,
    resumableCount,
    groups: expectedGroups,
  };
}

function sameTimestamp(left, right) {
  return Number.isFinite(Date.parse(left))
    && Number.isFinite(Date.parse(right))
    && Date.parse(left) === Date.parse(right);
}

export function verifyLegacyGovernanceExecution({
  boundary,
  plan,
  classification,
  executionResults,
  frozenInventory,
  postInventory,
  readback,
  frozenSourceEvidence,
}) {
  const groups = legacyGroups(plan, classification);
  if (!Array.isArray(executionResults) || executionResults.length !== groups.length) {
    fail('execute result group count mismatch');
  }
  const resultRows = [];
  for (let index = 0; index < groups.length; index++) {
    validateAdminWrapper(executionResults[index], groups[index], 'execute', classification);
    resultRows.push(...executionResults[index].result.results);
  }
  if (resultRows.length !== boundary.legacyCount) fail('executed count differs from frozen boundary');

  const results = asMap(resultRows, 'slug', 'execution results');
  const frozenSkills = asMap(frozenInventory.rows, 'slug', 'frozen Skills');
  const postSkills = asMap(postInventory.rows, 'slug', 'post Skills');
  const artifacts = asMap(postInventory.artifacts, 'id', 'post artifacts');
  const observationsBySkill = asMap(postInventory.observations, 'skill_id', 'post observations');
  const audits = asMap(readback.audits, 'id', 'audit readback');
  const snapshots = asMap(readback.scoreSnapshots, 'id', 'score snapshots');
  const breakdowns = asMap(readback.scoreBreakdowns, 'skill_id', 'score breakdowns');
  const skillReadback = asMap(readback.skills, 'id', 'Skill score readback');
  const frozenSourceAudits = asMap(frozenSourceEvidence?.audits, 'id', 'frozen source audits');
  const frozenSkillMetadata = asMap(frozenSourceEvidence?.skills, 'id', 'frozen Skill metadata');
  const attestations = readback.attestations || [];
  const legacyRows = classification.cohorts.legacy_algorithm_equivalent;
  const legacySlugs = new Set(legacyRows.map((row) => row.slug));

  if (
    canonicalJson(frozenInventory.packMemberships) !== canonicalJson(postInventory.packMemberships)
    || canonicalJson(frozenInventory.packs) !== canonicalJson(postInventory.packs)
  ) {
    fail('dependent Pack identity or timestamps changed during governance');
  }

  for (const frozen of classification.cohorts.exact.concat(
    classification.cohorts.actual_or_unproven_drift
  )) {
    if (canonicalJson(frozenSkills.get(frozen.slug)) !== canonicalJson(postSkills.get(frozen.slug))) {
      fail(`non-legacy cohort row changed: ${frozen.slug}`);
    }
  }

  for (const frozen of legacyRows) {
    const result = results.get(frozen.slug);
    const before = frozenSkills.get(frozen.slug);
    const skill = postSkills.get(frozen.slug);
    const scoredSkill = skillReadback.get(frozen.id);
    const artifact = artifacts.get(result.artifactVersionId);
    const observation = observationsBySkill.get(frozen.id);
    const sourceAudit = audits.get(result.sourceAuditId);
    const frozenSourceAudit = frozenSourceAudits.get(result.sourceAuditId);
    const frozenMetadata = frozenSkillMetadata.get(frozen.id);
    const derivedAudit = audits.get(result.derivedAuditId);
    const snapshot = snapshots.get(result.scoreSnapshotId);
    const breakdown = breakdowns.get(frozen.id);
    const repair = frozen.evidence.artifact.hashRepair;
    if (
      !before || !skill || !scoredSkill || !artifact || !observation
      || !sourceAudit || !frozenSourceAudit || !frozenMetadata
      || !derivedAudit || !snapshot || !breakdown
      || canonicalJson(sourceAudit) !== canonicalJson(frozenSourceAudit)
      || scoredSkill.name !== frozenMetadata.name
      || scoredSkill.description !== frozenMetadata.description
      || scoredSkill.author_name !== frozenMetadata.author_name
      || canonicalJson(scoredSkill.supported_tools) !== canonicalJson(frozenMetadata.supported_tools)
      || canonicalJson(scoredSkill.file_structure) !== canonicalJson(frozenMetadata.file_structure)
      || before.artifact_revision !== 0
      || skill.artifact_revision !== 1
      || skill.current_artifact_version_id !== result.artifactVersionId
      || skill.content_hash !== frozen.evidence.artifact.contentHash
      || skill.tree_hash !== frozen.evidence.artifact.treeHash
      || skill.public_eligibility_audit_id !== result.derivedAuditId
      || !sameTimestamp(skill.published_at, frozen.publishedAt)
      || !sameTimestamp(skill.updated_at, frozen.updatedAt)
      || scoredSkill.current_quality_score_snapshot_id !== result.scoreSnapshotId
      || typeof scoredSkill.quality_score !== 'number'
      || artifact.skill_id !== frozen.id
      || artifact.artifact_revision !== 1
      || artifact.content_hash !== frozen.evidence.artifact.contentHash
      || artifact.tree_hash !== frozen.evidence.artifact.treeHash
      || artifact.marketplace_commit_sha !== frozen.marketplaceCommit
      || artifact.source_path !== frozen.path
      || artifact.hash_provenance?.classification !== 'legacy_algorithm_equivalent'
      || artifact.hash_provenance?.report?.contentHash !== repair.reportContentHash
      || artifact.hash_provenance?.report?.treeHash !== repair.reportTreeHash
      || artifact.hash_provenance?.packaged?.contentHash !== repair.packagedContentHash
      || artifact.hash_provenance?.packaged?.treeHash !== repair.packagedTreeHash
      || observation.artifact_version_id !== result.artifactVersionId
      || observation.marketplace_commit_sha !== frozen.marketplaceCommit
      || observation.source_path !== frozen.path
      || sourceAudit.id !== frozen.publicEligibilityAuditId
      || derivedAudit.derived_from_audit_id !== sourceAudit.id
      || derivedAudit.derivation_kind !== 'legacy_algorithm_equivalent_hash_rebind'
      || derivedAudit.version !== sourceAudit.version + 1
      || derivedAudit.subject_content_hash !== repair.packagedContentHash
      || derivedAudit.subject_tree_hash !== repair.packagedTreeHash
      || snapshot.skill_id !== frozen.id
      || snapshot.score_subject?.auditId !== derivedAudit.id
      || snapshot.score_subject?.auditVersion !== derivedAudit.version
      || snapshot.score_subject?.contentHash !== repair.packagedContentHash
      || snapshot.score_subject?.treeHash !== repair.packagedTreeHash
      || breakdown.score_snapshot_id !== snapshot.id
      || breakdown.stale_at !== null
      || breakdown.stale_reason !== null
      || attestations.some((attestation) => attestation.audit_id === derivedAudit.id)
    ) {
      fail(`production readback mismatch for ${frozen.slug}`);
    }
  }

  if (postInventory.artifacts.length !== legacySlugs.size
      || postInventory.observations.length !== legacySlugs.size) {
    fail('scoped artifact/observation counts differ from the frozen legacy cohort');
  }
  return {
    schemaVersion: 1,
    status: 'executed_and_verified',
    boundaryRunId: boundary.runId,
    executedCount: resultRows.length,
    slugs: resultRows.map((row) => row.slug),
  };
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null) fail(`invalid argument: ${key || '<missing>'}`);
    values[key.slice(2)] = value;
  }
  return values;
}

function readJson(path) {
  return JSON.parse(readFileSync(resolve(path), 'utf8'));
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  let output;
  if (args.phase === 'groups') {
    output = {
      schemaVersion: 1,
      status: 'legacy_groups_planned',
      groups: legacyGroups(readJson(args.plan), readJson(args.classification)),
    };
  } else if (args.phase === 'freeze') {
    output = createLegacyGovernanceBoundary({
      plan: readJson(args.plan),
      classification: readJson(args.classification),
      dryRunResults: readJson(args['dry-run-results']),
      paths: {
        plan: resolve(args.plan),
        classification: resolve(args.classification),
        preInventory: resolve(args['pre-inventory']),
        dryRunResults: resolve(args['dry-run-results']),
        sourceEvidence: resolve(args['source-evidence']),
      },
      metadata: {
        runId: args['run-id'],
        repository: args.repository,
        workflowCommit: args['workflow-commit'],
        cliVersion: args['cli-version'],
        cliSha256: args['cli-sha256'],
      },
    });
  } else if (args.phase === 'execute-preflight') {
    output = verifyLegacyGovernanceBoundary({
      boundary: readJson(args.boundary),
      plan: readJson(args.plan),
      classification: readJson(args.classification),
      frozenInventory: readJson(args['frozen-inventory']),
      currentInventory: readJson(args['current-inventory']),
      frozenSourceEvidence: readJson(args['frozen-source-evidence']),
      currentSourceEvidence: readJson(args['current-source-evidence']),
      paths: {
        plan: resolve(args.plan),
        classification: resolve(args.classification),
        preInventory: resolve(args['frozen-inventory']),
        dryRunResults: resolve(args['dry-run-results']),
        sourceEvidence: resolve(args['frozen-source-evidence']),
      },
      expectedRunId: args['expected-run-id'],
    });
  } else if (args.phase === 'execution') {
    output = verifyLegacyGovernanceExecution({
      boundary: readJson(args.boundary),
      plan: readJson(args.plan),
      classification: readJson(args.classification),
      executionResults: readJson(args['execution-results']),
      frozenInventory: readJson(args['frozen-inventory']),
      postInventory: readJson(args['post-inventory']),
      readback: readJson(args.readback),
      frozenSourceEvidence: readJson(args['frozen-source-evidence']),
    });
  } else {
    fail('--phase must be groups, freeze, execute-preflight, or execution');
  }
  writeFileSync(resolve(args.output), `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`${JSON.stringify({ status: output.status })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`legacy-equivalent governance verification failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
