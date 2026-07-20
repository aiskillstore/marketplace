#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';

const RAW32_RE = /^[0-9a-f]{32}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function fail(message) { throw new Error(message); }
function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
function uniqueMap(rows, key, label) {
  const result = new Map();
  for (const row of rows || []) {
    if (!row?.[key] || result.has(row[key])) fail(`${label} identity is invalid`);
    result.set(row[key], row);
  }
  return result;
}
function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }

export function buildLegacyReportOriginAuditBindingPlan({
  classification,
  originLineage,
  sourceEvidence,
  repositoryRoot,
  expectedSelected,
  expectedV2Revision0,
  expectedGoverned,
}) {
  const rows = classification?.cohorts?.actual_or_unproven_drift;
  if (
    classification?.schemaVersion !== 1
    || classification?.status !== 'classified'
    || classification?.classifiedCount !== 70
    || classification?.counts?.actual_or_unproven_drift !== 70
    || !Array.isArray(rows)
    || rows.length !== 70
  ) fail('report-origin classification is not the exact frozen 70-row drift cohort');
  if (
    originLineage?.status !== 'legacy_report_origin_evidence_materialized'
    || originLineage?.selectedCount !== 70
    || !Array.isArray(originLineage?.entries)
    || originLineage.entries.length !== 70
  ) fail('report-origin lineage is not the exact materialized 70-row proof');
  if (sourceEvidence?.schemaVersion !== 1 || sourceEvidence?.status !== 'source_evidence_fetched') {
    fail('report-origin source evidence is incomplete');
  }

  const skills = uniqueMap(sourceEvidence.skills, 'id', 'source Skills');
  const audits = uniqueMap(sourceEvidence.audits, 'id', 'source audits');
  const bindings = uniqueMap(sourceEvidence.bindings, 'source_audit_id', 'legacy bindings');
  const lineage = uniqueMap(originLineage.entries, 'slug', 'origin lineage');
  if (skills.size !== 70 || audits.size !== 70 || lineage.size !== 70) {
    fail('report-origin source evidence does not cover exactly 70 identities');
  }

  const entries = [];
  let v2Revision0 = 0;
  let governed = 0;
  for (const row of rows) {
    const skill = skills.get(row.id);
    const audit = audits.get(row.publicEligibilityAuditId);
    const proof = lineage.get(row.slug);
    if (
      !skill || skill.slug !== row.slug
      || skill.marketplace_commit_sha !== row.marketplaceCommit
      || skill.plugin_path !== row.path
      || skill.public_eligible !== true
      || !audit || audit.skill_id !== row.id || audit.id !== row.publicEligibilityAuditId
      || !proof || proof.skillId !== row.id || proof.path !== row.path
      || proof.currentMarketplaceCommit !== row.marketplaceCommit
      || proof.currentReport?.contentHash !== row.contentHash
      || proof.currentReport?.treeHash !== row.treeHash
    ) fail(`report-origin immutable identity changed for ${row.slug}`);

    if (skill.artifact_revision === 1 && UUID_RE.test(skill.current_artifact_version_id || '')) {
      if (
        skill.content_hash !== row.evidence?.artifact?.contentHash
        || skill.tree_hash !== row.evidence?.artifact?.treeHash
        || !UUID_RE.test(skill.public_eligibility_audit_id || '')
      ) fail(`report-origin governed projection changed for ${row.slug}`);
      governed += 1;
      continue;
    }
    if (
      skill.artifact_revision !== 0
      || skill.current_artifact_version_id !== null
      || skill.content_hash !== row.contentHash
      || skill.tree_hash !== row.treeHash
      || skill.public_eligibility_audit_id !== row.publicEligibilityAuditId
    ) {
      fail(`report-origin artifact projection is inconsistent for ${row.slug}`);
    }
    if (!RAW32_RE.test(audit.content_hash || '')) {
      const v2Prefix = `v2:${row.marketplaceCommit}:${row.contentHash}:${row.treeHash}:`;
      if (
        !audit.content_hash.startsWith(v2Prefix)
        || !RAW32_RE.test(audit.content_hash.slice(v2Prefix.length))
        || audit.audit_payload_hash !== null
        || audit.subject_marketplace_commit_sha !== null
        || audit.subject_content_hash !== null
        || audit.subject_tree_hash !== null
        || audit.subject_plugin_path !== null
        || audit.derived_from_audit_id !== null
        || audit.derivation_kind !== null
      ) fail(`report-origin v2 source audit changed for ${row.slug}`);
      v2Revision0 += 1;
      continue;
    }
    if (bindings.has(audit.id)) fail(`report-origin raw32 audit is already bound for ${row.slug}`);
    if (
      audit.audit_payload_hash !== null
      || audit.subject_marketplace_commit_sha !== null
      || audit.subject_content_hash !== null
      || audit.subject_tree_hash !== null
      || audit.subject_plugin_path !== null
      || audit.derived_from_audit_id !== null
      || audit.derivation_kind !== null
    ) fail(`report-origin raw32 audit columns changed for ${row.slug}`);

    const objectSpec = `${row.marketplaceCommit}:${row.path}/skill-report.json`;
    const reportBytes = execFileSync('git', ['-C', repositoryRoot, 'show', objectSpec]);
    const reportBlob = execFileSync(
      'git', ['-C', repositoryRoot, 'rev-parse', `${row.marketplaceCommit}:${row.path}/skill-report.json`],
      { encoding: 'utf8' }
    ).trim();
    if (sha256(reportBytes) !== proof.currentReport.sha256 || reportBlob !== proof.currentReport.gitBlob) {
      fail(`report-origin report bytes changed for ${row.slug}`);
    }
    const report = JSON.parse(reportBytes.toString('utf8'));
    if (
      report?.meta?.slug !== row.slug
      || report?.meta?.content_hash !== row.contentHash
      || report?.meta?.tree_hash !== row.treeHash
      || !report?.security_audit
    ) fail(`report-origin pinned report identity mismatch for ${row.slug}`);
    entries.push({
      skillId: row.id,
      slug: row.slug,
      pluginPath: row.path,
      marketplaceCommit: row.marketplaceCommit,
      skillContentHash: row.contentHash,
      treeHash: row.treeHash,
      sourceAuditId: audit.id,
      sourceAuditVersion: audit.version,
      sourceAuditPayloadHash: audit.content_hash,
      reportBlobSha256: sha256(reportBytes),
    });
  }
  entries.sort((left, right) => left.slug.localeCompare(right.slug, 'en-US'));
  if (
    entries.length !== expectedSelected
    || v2Revision0 !== expectedV2Revision0
    || governed !== expectedGoverned
    || bindings.size !== 0
  ) fail(`report-origin binding split changed: selected=${entries.length} v2=${v2Revision0} governed=${governed} bound=${bindings.size}`);

  const identity = { schemaVersion: 1, entries };
  return {
    ...identity,
    planSha256: sha256(canonical(identity)),
    status: 'legacy_report_origin_audit_binding_plan',
    counts: { selected: entries.length, v2Revision0, governed, existingBindings: bindings.size },
  };
}

function parseCount(value, name) {
  if (!/^(0|[1-9][0-9]*)$/.test(value || '')) fail(`${name} must be a non-negative integer`);
  return Number(value);
}

if (process.argv[1]?.endsWith('build-legacy-report-origin-audit-binding-plan.mjs')) {
  try {
    const { values } = parseArgs({ options: {
      classification: { type: 'string' },
      'origin-lineage': { type: 'string' },
      'source-evidence': { type: 'string' },
      'repository-root': { type: 'string' },
      'expected-selected': { type: 'string' },
      'expected-v2': { type: 'string' },
      'expected-governed': { type: 'string' },
      output: { type: 'string' },
    } });
    const plan = buildLegacyReportOriginAuditBindingPlan({
      classification: JSON.parse(readFileSync(resolve(values.classification), 'utf8')),
      originLineage: JSON.parse(readFileSync(resolve(values['origin-lineage']), 'utf8')),
      sourceEvidence: JSON.parse(readFileSync(resolve(values['source-evidence']), 'utf8')),
      repositoryRoot: resolve(values['repository-root']),
      expectedSelected: parseCount(values['expected-selected'], '--expected-selected'),
      expectedV2Revision0: parseCount(values['expected-v2'], '--expected-v2'),
      expectedGoverned: parseCount(values['expected-governed'], '--expected-governed'),
    });
    writeFileSync(resolve(values.output), `${JSON.stringify(plan, null, 2)}\n`, { flag: 'wx' });
    process.stdout.write(`${JSON.stringify(plan.counts)}\n`);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  }
}
