#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { parseArgs } from 'node:util';

const HASH32 = /^[0-9a-f]{32}$/;
function fail(message) { throw new Error(message); }
function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map((key) =>
    `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
function map(rows, key, label) {
  const result = new Map();
  for (const row of rows || []) {
    if (!row?.[key] || result.has(row[key])) fail(`${label} identity is invalid`);
    result.set(row[key], row);
  }
  return result;
}

export function buildLegacyAuditBindingPlan({ classification, sourceEvidence, repositoryRoot }) {
  if (classification?.schemaVersion !== 1 || classification?.status !== 'classified') {
    fail('classification is not frozen');
  }
  const legacy = classification?.cohorts?.legacy_algorithm_equivalent || [];
  const drift = classification?.cohorts?.actual_or_unproven_drift || [];
  const skills = map(sourceEvidence?.skills, 'id', 'source Skills');
  const audits = map(sourceEvidence?.audits, 'id', 'source audits');
  const entries = [];
  for (const row of legacy) {
    const skill = skills.get(row.id);
    const audit = audits.get(row.publicEligibilityAuditId);
    if (!skill || skill.slug !== row.slug || !audit || audit.skill_id !== row.id
      || audit.id !== row.publicEligibilityAuditId || !HASH32.test(audit.content_hash || '')) {
      continue;
    }
    const objectSpec = `${row.marketplaceCommit}:${row.path}/skill-report.json`;
    const raw = execFileSync('git', ['-C', repositoryRoot, 'show', objectSpec]);
    const report = JSON.parse(raw.toString('utf8'));
    if (report?.meta?.slug !== row.slug || report?.meta?.content_hash !== row.contentHash
      || report?.meta?.tree_hash !== row.treeHash || !report?.security_audit) {
      fail(`pinned report identity mismatch for ${row.slug}`);
    }
    entries.push({
      skillId: row.id, slug: row.slug, pluginPath: row.path,
      marketplaceCommit: row.marketplaceCommit, skillContentHash: row.contentHash,
      treeHash: row.treeHash, sourceAuditId: audit.id,
      sourceAuditVersion: audit.version, sourceAuditPayloadHash: audit.content_hash,
      reportBlobSha256: createHash('sha256').update(raw).digest('hex'),
    });
  }
  entries.sort((a, b) => a.slug.localeCompare(b.slug, 'en-US'));
  const identity = { schemaVersion: 1, entries };
  return {
    ...identity,
    planSha256: createHash('sha256').update(canonical(identity)).digest('hex'),
    driftQuarantine: drift.map((row) => ({
      slug: row.slug, skillId: row.id, sourceAuditId: row.publicEligibilityAuditId,
      artifactGovernanceAllowed: false,
    })).sort((a, b) => a.slug.localeCompare(b.slug, 'en-US')),
  };
}

if (process.argv[1]?.endsWith('build-legacy-audit-binding-plan.mjs')) {
  try {
    const { values } = parseArgs({ options: {
      classification: { type: 'string' }, 'source-evidence': { type: 'string' },
      'repository-root': { type: 'string' }, output: { type: 'string' },
      'expected-targeted': { type: 'string' }, 'expected-drift': { type: 'string' },
    } });
    const result = buildLegacyAuditBindingPlan({
      classification: JSON.parse(readFileSync(resolve(values.classification), 'utf8')),
      sourceEvidence: JSON.parse(readFileSync(resolve(values['source-evidence']), 'utf8')),
      repositoryRoot: resolve(values['repository-root']),
    });
    if (values['expected-targeted'] && result.entries.length !== Number(values['expected-targeted']))
      fail('targeted binding count mismatch');
    if (values['expected-drift'] && result.driftQuarantine.length !== Number(values['expected-drift']))
      fail('drift quarantine count mismatch');
    writeFileSync(resolve(values.output), `${JSON.stringify(result, null, 2)}\n`, { flag: 'wx' });
  } catch (error) {
    process.stderr.write(`${error.message}\n`); process.exitCode = 1;
  }
}
