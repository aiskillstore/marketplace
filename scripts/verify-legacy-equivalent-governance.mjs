#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const CLI_VERSION = '2.11.4';
const EXECUTABLE_BOUNDARY_CLI_SHA256 = new Map([
  ['2.11.1', '9aa6a6e15d249e52bed690049974d8312f3257c205025823a68d249cc5cc8367'],
  ['2.11.2', 'c596ca3b6d27875fdcd231bfb889899f08ea8ae95217def7bf46de2aa3722b81'],
  ['2.11.3', 'af5d2718c527d5228ce356182e1a80b9efba065b0a794888a79215666344b201'],
  ['2.11.4', '236c0d3f5091d6cf15d3fa90a247706ab2419f7cfb672554fc5336f0f4212394'],
]);
const MAX_BATCH_SIZE = 500;
const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
const AUDIT_PAYLOAD_HASH_RE = /^[0-9a-f]{32}$/;
const LOWER_HEX_RE = /^[0-9a-f]+$/;
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

export function canonicalSourceEvidence(value) {
  return canonicalJson({
    ...value,
    skills: [...(value?.skills || [])].sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US')),
    audits: [...(value?.audits || [])].sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US')),
    bindings: [...(value?.bindings || [])].sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US')),
  });
}

function assertSourceEvidenceUnchangedOrResumable({
  frozenSourceEvidence,
  currentSourceEvidence,
  currentSkills,
  resumableSkillIds,
}) {
  if (canonicalSourceEvidence({ ...frozenSourceEvidence, skills: [] })
    !== canonicalSourceEvidence({ ...currentSourceEvidence, skills: [] })) {
    fail('Skill metadata or source audit changed after the frozen dry-run boundary');
  }
  const frozenMetadata = asMap(frozenSourceEvidence.skills, 'id', 'frozen Skill metadata');
  const currentMetadata = asMap(currentSourceEvidence.skills, 'id', 'current Skill metadata');
  if (frozenMetadata.size !== currentMetadata.size) {
    fail('Skill metadata or source audit changed after the frozen dry-run boundary');
  }
  for (const [skillId, frozen] of frozenMetadata) {
    const current = currentMetadata.get(skillId);
    const currentInventory = currentSkills.get(frozen.slug);
    if (canonicalJson(frozen) === canonicalJson(current)) {
      if (
        resumableSkillIds.has(skillId)
        && current?.public_eligibility_audit_id !== currentInventory?.public_eligibility_audit_id
      ) {
        fail('Skill metadata or source audit changed after the frozen dry-run boundary');
      }
      continue;
    }
    if (
      !current
      || !resumableSkillIds.has(skillId)
      || current.public_eligibility_audit_id !== currentInventory?.public_eligibility_audit_id
      || canonicalJson(frozen) !== canonicalJson({
        ...current,
        public_eligibility_audit_id: frozen.public_eligibility_audit_id,
      })
    ) {
      fail('Skill metadata or source audit changed after the frozen dry-run boundary');
    }
  }
}

function canonicalPackTopology(inventory) {
  const packMemberships = [...(inventory?.packMemberships || [])]
    .sort((left, right) => `${left.skill_id}:${left.pack_id}`.localeCompare(
      `${right.skill_id}:${right.pack_id}`,
      'en-US'
    ));
  const packs = [...(inventory?.packs || [])]
    .map((pack) => ({ id: pack.id, slug: pack.slug, published_at: pack.published_at }))
    .sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US'));
  return canonicalJson({ packMemberships, packs });
}

function canonicalPackState(inventory) {
  const packMemberships = [...(inventory?.packMemberships || [])]
    .sort((left, right) => `${left.skill_id}:${left.pack_id}`.localeCompare(
      `${right.skill_id}:${right.pack_id}`,
      'en-US'
    ));
  const packs = [...(inventory?.packs || [])]
    .sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US'));
  return canonicalJson({ packMemberships, packs });
}

function assertPackUpdatedAtDoesNotRegress(beforeInventory, afterInventory, context) {
  const before = asMap(beforeInventory?.packs || [], 'id', `${context} prior Packs`);
  const after = asMap(afterInventory?.packs || [], 'id', `${context} current Packs`);
  if (before.size !== after.size) fail(`${context} Pack topology changed`);
  const advances = [];
  for (const [id, prior] of before) {
    const current = after.get(id);
    const priorTimestamp = Date.parse(prior?.updated_at);
    const currentTimestamp = Date.parse(current?.updated_at);
    if (
      !current
      || !Number.isFinite(priorTimestamp)
      || !Number.isFinite(currentTimestamp)
      || currentTimestamp < priorTimestamp
    ) {
      fail(`${context} Pack updated_at regressed for ${id}`);
    }
    if (currentTimestamp > priorTimestamp) {
      advances.push({
        packId: id,
        frozenUpdatedAt: prior.updated_at,
        currentUpdatedAt: current.updated_at,
      });
    }
  }
  return advances;
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

function decodePluginPath(value) {
  if (!value || value.length % 2 !== 0 || !LOWER_HEX_RE.test(value)) return null;
  const bytes = new Uint8Array(value.length / 2);
  for (let index = 0; index < value.length; index += 2) {
    bytes[index / 2] = Number.parseInt(value.slice(index, index + 2), 16);
  }
  let path;
  try {
    path = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    return null;
  }
  if (
    !path
    || path.trim() !== path
    || path.startsWith('/')
    || path.includes('\\')
    || path.includes('\0')
    || path.split('/').some((segment) => !segment || segment === '.' || segment === '..')
  ) return null;
  return path;
}

function qualifySourceAudit(audit, row, legacyBinding) {
  if (
    audit.skill_id !== row.id
    || audit.derived_from_audit_id != null
    || audit.derivation_kind != null
    || !Number.isSafeInteger(audit.version)
    || audit.version < 1
    || typeof audit.content_hash !== 'string'
  ) {
    return { eligible: false, reason: 'source_audit_identity_unproven' };
  }
  if (AUDIT_PAYLOAD_HASH_RE.test(audit.content_hash)) {
    if (
      legacyBinding
      && legacyBinding.skill_id === row.id
      && legacyBinding.source_audit_id === audit.id
      && legacyBinding.source_audit_version === audit.version
      && legacyBinding.source_audit_payload_hash === audit.content_hash
      && legacyBinding.subject_marketplace_commit_sha === row.marketplaceCommit
      && legacyBinding.subject_content_hash === row.contentHash
      && legacyBinding.subject_tree_hash === row.treeHash
      && legacyBinding.subject_plugin_path === row.path
      && legacyBinding.report_object_spec === `${row.marketplaceCommit}:${row.path}/skill-report.json`
      && audit.audit_payload_hash === null
      && audit.subject_marketplace_commit_sha === null
      && audit.subject_content_hash === null
      && audit.subject_tree_hash === null
      && audit.subject_plugin_path === null
    ) return { eligible: true, reason: 'eligible_legacy_binding_v1' };
    return { eligible: false, reason: 'source_audit_binding_unproven_legacy_digest' };
  }

  const parts = audit.content_hash.split(':');
  let binding;
  if (
    parts[0] === 'v2'
    && parts.length === 5
    && COMMIT_RE.test(parts[1])
    && SHA256_RE.test(parts[2])
    && SHA256_RE.test(parts[3])
    && AUDIT_PAYLOAD_HASH_RE.test(parts[4])
  ) {
    binding = {
      version: 'v2', marketplaceCommit: parts[1], contentHash: parts[2], treeHash: parts[3],
      pluginPath: null, auditPayloadHash: parts[4],
    };
  } else if (
    parts[0] === 'v3'
    && parts.length === 6
    && COMMIT_RE.test(parts[1])
    && SHA256_RE.test(parts[2])
    && SHA256_RE.test(parts[3])
    && AUDIT_PAYLOAD_HASH_RE.test(parts[5])
  ) {
    const pluginPath = decodePluginPath(parts[4]);
    if (pluginPath) {
      binding = {
        version: 'v3', marketplaceCommit: parts[1], contentHash: parts[2], treeHash: parts[3],
        pluginPath, auditPayloadHash: parts[5],
      };
    }
  }
  if (!binding) return { eligible: false, reason: 'source_audit_binding_malformed_or_unsupported' };
  if (
    binding.marketplaceCommit !== row.marketplaceCommit
    || binding.contentHash !== row.contentHash
    || binding.treeHash !== row.treeHash
    || (binding.version === 'v3' && binding.pluginPath !== row.path)
  ) {
    return { eligible: false, reason: 'source_audit_binding_subject_mismatch' };
  }

  const projections = [
    audit.subject_marketplace_commit_sha,
    audit.subject_content_hash,
    audit.subject_tree_hash,
    audit.subject_plugin_path,
  ];
  if (binding.version === 'v2') {
    if (audit.audit_payload_hash === null && projections.every((value) => value === null)) {
      return { eligible: true, reason: 'eligible_v2' };
    }
    return { eligible: false, reason: 'source_audit_projection_mismatch' };
  }
  if (
    audit.audit_payload_hash === binding.auditPayloadHash
    && audit.subject_marketplace_commit_sha === binding.marketplaceCommit
    && audit.subject_content_hash === binding.contentHash
    && audit.subject_tree_hash === binding.treeHash
    && audit.subject_plugin_path === binding.pluginPath
  ) {
    return { eligible: true, reason: 'eligible_v3' };
  }
  return { eligible: false, reason: 'source_audit_projection_mismatch' };
}

export function qualifyLegacyGovernanceClassification({ classification, sourceEvidence }) {
  if (classification?.schemaVersion !== 1 || classification?.status !== 'classified') {
    fail('classification contract is not frozen');
  }
  if (sourceEvidence?.schemaVersion !== 1 || sourceEvidence?.status !== 'source_evidence_fetched') {
    fail('source evidence contract is not complete');
  }
  const legacy = asMap(classification?.cohorts?.legacy_algorithm_equivalent, 'slug', 'legacy cohort');
  const skills = asMap(sourceEvidence.skills, 'id', 'source evidence Skills');
  const audits = asMap(sourceEvidence.audits, 'id', 'source evidence audits');
  const bindings = asMap(sourceEvidence.bindings || [], 'source_audit_id', 'source evidence bindings');
  if (
    skills.size !== legacy.size
    || audits.size !== legacy.size
    || canonicalJson(sourceEvidence.skillIds) !== canonicalJson([...legacy.values()].map((row) => row.id).sort())
  ) {
    fail('source evidence does not cover the hash-equivalent cohort exactly once');
  }

  const eligible = [];
  const unproven = [];
  for (const row of legacy.values()) {
    const skill = skills.get(row.id);
    const audit = audits.get(row.publicEligibilityAuditId);
    if (!skill || skill.slug !== row.slug || !audit || audit.id !== row.publicEligibilityAuditId) {
      fail(`source evidence identity mismatch for ${row.slug}`);
    }
    const decision = qualifySourceAudit(audit, row, bindings.get(audit.id));
    const frozen = {
      slug: row.slug,
      skillId: row.id,
      sourceAuditId: row.publicEligibilityAuditId,
      reason: decision.reason,
    };
    (decision.eligible ? eligible : unproven).push(frozen);
  }
  if (eligible.length + unproven.length !== legacy.size) {
    fail('source audit qualification lost a hash-equivalent row');
  }
  return {
    ...classification,
    governance: {
      schemaVersion: 1,
      status: 'source_audit_qualified',
      hashEquivalentCount: legacy.size,
      eligibleCount: eligible.length,
      unprovenCount: unproven.length,
      eligible,
      unproven,
    },
  };
}

function assertQualificationMatchesEvidence(classification, sourceEvidence) {
  const requalified = qualifyLegacyGovernanceClassification({ classification, sourceEvidence });
  if (canonicalJson(requalified.governance) !== canonicalJson(classification.governance)) {
    fail('frozen source audit qualification does not match source evidence');
  }
}

function governableLegacyRows(classification) {
  const rawLegacy = asMap(classification?.cohorts?.legacy_algorithm_equivalent, 'slug', 'legacy cohort');
  const governance = classification?.governance;
  const eligible = asMap(governance?.eligible, 'slug', 'governable legacy cohort');
  const unproven = asMap(governance?.unproven, 'slug', 'unproven source-audit cohort');
  if (
    governance?.schemaVersion !== 1
    || governance?.status !== 'source_audit_qualified'
    || governance.hashEquivalentCount !== rawLegacy.size
    || governance.eligibleCount !== eligible.size
    || governance.unprovenCount !== unproven.size
    || eligible.size + unproven.size !== rawLegacy.size
  ) {
    fail('source audit qualification coverage is invalid');
  }
  for (const slug of rawLegacy.keys()) {
    if (eligible.has(slug) === unproven.has(slug)) {
      fail(`source audit qualification is not a disjoint cover for ${slug}`);
    }
  }
  for (const decision of [...eligible.values(), ...unproven.values()]) {
    const row = rawLegacy.get(decision.slug);
    if (
      !row
      || decision.skillId !== row.id
      || decision.sourceAuditId !== row.publicEligibilityAuditId
      || typeof decision.reason !== 'string'
      || !decision.reason
    ) {
      fail(`source audit qualification identity mismatch for ${decision.slug}`);
    }
  }
  return [...eligible.keys()].map((slug) => rawLegacy.get(slug));
}

function legacyGroups(plan, classification) {
  const legacyRows = governableLegacyRows(classification);
  const selected = asMap(plan?.selected, 'slug', 'plan selected rows');
  const legacy = asMap(legacyRows, 'slug', 'legacy cohort');
  if (plan?.selectedCount !== plan?.selected?.length || plan.selectedCount > MAX_BATCH_SIZE) {
    fail('plan is not a bounded complete batch');
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

export function validateLegacyPreviousReportManifest(manifest, plan) {
  if (
    manifest?.schemaVersion !== 1
    || manifest?.status !== 'legacy_previous_reports_materialized'
    || manifest?.selectedCount !== plan?.selectedCount
    || !Array.isArray(manifest?.entries)
    || manifest.entries.length !== plan?.selectedCount
  ) {
    fail('previous-report manifest has an invalid summary');
  }
  const selected = asMap(plan?.selected, 'path', 'plan previous-report paths');
  const seen = new Set();
  let priorPath = null;
  for (const entry of manifest.entries) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
      fail('previous-report manifest entry is not an object');
    }
    const keys = Object.keys(entry).sort();
    if (canonicalJson(keys) !== canonicalJson([
      'currentCommit', 'parentCommit', 'path', 'present', 'sha256',
    ])) {
      fail('previous-report manifest entry has unexpected fields');
    }
    const planned = selected.get(entry.path);
    if (
      !planned
      || seen.has(entry.path)
      || entry.currentCommit !== planned.marketplaceCommit
      || !COMMIT_RE.test(String(entry.parentCommit || ''))
      || entry.parentCommit === entry.currentCommit
      || typeof entry.present !== 'boolean'
      || (entry.present && !SHA256_RE.test(String(entry.sha256 || '')))
      || (!entry.present && entry.sha256 !== null)
      || (priorPath !== null && priorPath >= entry.path)
    ) {
      fail(`previous-report manifest mismatch for ${entry?.path ?? '<missing>'}`);
    }
    seen.add(entry.path);
    priorPath = entry.path;
  }
  if (seen.size !== selected.size) fail('previous-report manifest does not cover the frozen plan');
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
  const legacy = asMap(governableLegacyRows(classification), 'slug', 'governable legacy cohort');
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
    || metadata.cliSha256 !== EXECUTABLE_BOUNDARY_CLI_SHA256.get(CLI_VERSION)
    || !/^\d+$/.test(String(metadata.runId))
    || !/^[0-9a-f]{40}$/.test(String(metadata.workflowCommit || ''))
    || metadata.repository !== 'aiskillstore/marketplace'
  ) {
    fail('invalid dry-run workflow metadata');
  }
  assertQualificationMatchesEvidence(
    classification,
    JSON.parse(readFileSync(paths.sourceEvidence, 'utf8'))
  );
  validateLegacyPreviousReportManifest(
    JSON.parse(readFileSync(paths.previousReportManifest, 'utf8')),
    plan,
  );
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
    hashEquivalentCount: classification.counts.legacy_algorithm_equivalent,
    legacyCount: classification.governance.eligibleCount,
    unprovenSourceAuditCount: classification.governance.unprovenCount,
    lastSelected: plan.lastSelected,
    hashes: {
      plan: sha256File(paths.plan),
      classification: sha256File(paths.classification),
      preInventory: sha256File(paths.preInventory),
      dryRunResults: sha256File(paths.dryRunResults),
      sourceEvidence: sha256File(paths.sourceEvidence),
      previousReportManifest: sha256File(paths.previousReportManifest),
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
    || EXECUTABLE_BOUNDARY_CLI_SHA256.get(boundary?.cliVersion) !== boundary?.cliSha256
  ) {
    fail('downloaded boundary metadata is invalid');
  }
  for (const [key, path] of Object.entries(paths)) {
    if (boundary.hashes?.[key] !== sha256File(path)) {
      fail(`downloaded boundary ${key} hash mismatch`);
    }
  }
  const expectedGroups = legacyGroups(plan, classification);
  validateLegacyPreviousReportManifest(
    JSON.parse(readFileSync(paths.previousReportManifest, 'utf8')),
    plan,
  );
  if (canonicalJson(boundary.groups) !== canonicalJson(expectedGroups)) {
    fail('downloaded boundary groups do not match plan/classification');
  }
  assertQualificationMatchesEvidence(classification, frozenSourceEvidence);
  const frozenSkills = asMap(frozenInventory.rows, 'slug', 'frozen Skills');
  const currentSkills = asMap(currentInventory.rows, 'slug', 'current Skills');
  const artifacts = asMap(currentInventory.artifacts, 'skill_id', 'current artifacts');
  const observations = asMap(currentInventory.observations, 'skill_id', 'current observations');
  const governableLegacy = asMap(governableLegacyRows(classification), 'slug', 'governable legacy cohort');
  const legacySlugs = new Set(governableLegacy.keys());
  if (
    canonicalPackTopology(frozenInventory) !== canonicalPackTopology(currentInventory)
    || frozenSkills.size !== currentSkills.size
  ) {
    fail('production state changed after the frozen dry-run boundary');
  }
  const packUpdatedAtAdvances = assertPackUpdatedAtDoesNotRegress(
    frozenInventory,
    currentInventory,
    'production state after the frozen dry-run boundary'
  );
  let resumableCount = 0;
  const resumableSkillIds = new Set();
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
    const repair = governableLegacy.get(selected.slug).evidence.artifact.hashRepair;
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
      || !timestampDoesNotRegress(selected.updatedAt, current.updated_at)
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
    resumableSkillIds.add(selected.id);
  }
  if (artifacts.size !== resumableCount || observations.size !== resumableCount) {
    fail('resumable artifact/observation scope contains unexpected rows');
  }
  assertSourceEvidenceUnchangedOrResumable({
    frozenSourceEvidence,
    currentSourceEvidence,
    currentSkills,
    resumableSkillIds,
  });
  return {
    schemaVersion: 1,
    status: 'execution_preflight_verified',
    runId: boundary.runId,
    legacyCount: boundary.legacyCount,
    resumableCount,
    packUpdatedAtAdvances,
    groups: expectedGroups,
  };
}

function sameTimestamp(left, right) {
  return Number.isFinite(Date.parse(left))
    && Number.isFinite(Date.parse(right))
    && Date.parse(left) === Date.parse(right);
}

function timestampDoesNotRegress(before, after) {
  return Number.isFinite(Date.parse(before))
    && Number.isFinite(Date.parse(after))
    && Date.parse(after) >= Date.parse(before);
}

export function verifyLegacyGovernanceExecution({
  boundary,
  plan,
  classification,
  executionResults,
  frozenInventory,
  currentInventory,
  postInventory,
  readback,
  frozenSourceEvidence,
  postSourceEvidence,
}) {
  if (canonicalSourceEvidence(frozenSourceEvidence) !== canonicalSourceEvidence(postSourceEvidence)) {
    fail('Skill metadata or source audit changed during governance execution');
  }
  assertQualificationMatchesEvidence(classification, frozenSourceEvidence);
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
  const legacyRows = governableLegacyRows(classification);
  const legacySlugs = new Set(legacyRows.map((row) => row.slug));
  const rawLegacy = asMap(classification.cohorts.legacy_algorithm_equivalent, 'slug', 'legacy cohort');
  const sourceAuditUnproven = classification.governance.unproven.map((decision) => rawLegacy.get(decision.slug));

  if (
    canonicalPackTopology(frozenInventory) !== canonicalPackTopology(currentInventory)
    || canonicalPackTopology(frozenInventory) !== canonicalPackTopology(postInventory)
  ) {
    fail('dependent Pack topology changed during governance');
  }
  assertPackUpdatedAtDoesNotRegress(
    frozenInventory,
    currentInventory,
    'dependent Pack state before governance'
  );
  if (canonicalPackState(currentInventory) !== canonicalPackState(postInventory)) {
    fail('dependent Pack state changed during governance execution');
  }

  for (const frozen of classification.cohorts.exact.concat(
    classification.cohorts.actual_or_unproven_drift,
    sourceAuditUnproven
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
  if (args.phase === 'qualify') {
    output = qualifyLegacyGovernanceClassification({
      classification: readJson(args.classification),
      sourceEvidence: readJson(args['source-evidence']),
    });
  } else if (args.phase === 'groups') {
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
        previousReportManifest: resolve(args['previous-report-manifest']),
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
        previousReportManifest: resolve(args['previous-report-manifest']),
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
      currentInventory: readJson(args['current-inventory']),
      postInventory: readJson(args['post-inventory']),
      readback: readJson(args.readback),
      frozenSourceEvidence: readJson(args['frozen-source-evidence']),
      postSourceEvidence: readJson(args['post-source-evidence']),
    });
  } else {
    fail('--phase must be qualify, groups, freeze, execute-preflight, or execution');
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
