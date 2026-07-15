#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { parseArgs } from 'node:util';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
const RAW_AUDIT_HASH_RE = /^[0-9a-f]{32}$/;

function fail(message) { throw new Error(message); }
function readJson(path) { return JSON.parse(readFileSync(path, 'utf8')); }
function sha256(path) { return createHash('sha256').update(readFileSync(path)).digest('hex'); }
function uniqueMap(rows, key, label) {
  const result = new Map();
  for (const row of rows || []) {
    const value = row?.[key];
    if (typeof value !== 'string' || !value || result.has(value)) fail(`${label} has duplicate or invalid ${key}`);
    result.set(value, row);
  }
  return result;
}

export function loadLegacyAuditBindingSources({ manifest, sourcesRoot }) {
  if (
    manifest?.schemaVersion !== 1
    || manifest?.status !== 'frozen'
    || manifest?.expected?.legacy_algorithm_equivalent !== 61
    || manifest?.expected?.actual_or_unproven_drift !== 24
    || manifest?.expected?.total !== 85
    || !Array.isArray(manifest?.sources)
    || manifest.sources.length !== 3
  ) fail('source-boundary manifest contract is invalid');
  const runIds = new Set();
  const allRows = [];
  const sources = [];
  const slugs = new Set();
  const skillIds = new Set();
  const auditIds = new Set();
  for (const source of manifest.sources) {
    if (
      !/^[1-9][0-9]*$/.test(source?.runId || '')
      || runIds.has(source.runId)
      || !COMMIT_RE.test(source?.headSha || '')
      || source?.artifactName !== `legacy-equivalent-boundary-${source.runId}`
      || !SHA256_RE.test(source?.sha256sumsSha256 || '')
      || !SHA256_RE.test(source?.classificationSha256 || '')
      || !Number.isSafeInteger(source?.expectedLegacy)
      || !Number.isSafeInteger(source?.expectedDrift)
    ) fail('source-boundary manifest entry is invalid');
    runIds.add(source.runId);
    const root = resolve(sourcesRoot, source.runId);
    const sumsPath = join(root, 'SHA256SUMS');
    const classificationPath = join(root, 'classification.json');
    const boundary = readJson(join(root, 'boundary.json'));
    if (
      sha256(sumsPath) !== source.sha256sumsSha256
      || sha256(classificationPath) !== source.classificationSha256
      || String(boundary?.runId) !== source.runId
      || boundary?.workflowCommit !== source.headSha
    ) fail(`source boundary identity mismatch for run ${source.runId}`);
    const classification = readJson(classificationPath);
    if (classification?.schemaVersion !== 1 || classification?.status !== 'classified') {
      fail(`classification contract is invalid for run ${source.runId}`);
    }
    const cohorts = {
      legacy_algorithm_equivalent: classification?.cohorts?.legacy_algorithm_equivalent,
      actual_or_unproven_drift: classification?.cohorts?.actual_or_unproven_drift,
    };
    for (const [classificationName, rows] of Object.entries(cohorts)) {
      if (!Array.isArray(rows)) fail(`source ${source.runId} lacks ${classificationName}`);
      for (const row of rows) {
        if (
          !row?.slug || !row?.id || !row?.publicEligibilityAuditId
          || slugs.has(row.slug) || skillIds.has(row.id) || auditIds.has(row.publicEligibilityAuditId)
        ) fail(`source boundaries overlap or lack identity at ${row?.slug || '<missing>'}`);
        slugs.add(row.slug); skillIds.add(row.id); auditIds.add(row.publicEligibilityAuditId);
        allRows.push({ source, classificationName, row });
      }
    }
    sources.push({ source, root, classification });
  }
  return { sources, allRows };
}

export function buildLegacyAuditBindingCandidateScope(input) {
  const loaded = loadLegacyAuditBindingSources(input);
  const rows = loaded.allRows.map(({ row }) => row).sort((a, b) => a.slug.localeCompare(b.slug));
  return {
    schemaVersion: 1,
    status: 'classified',
    counts: { exact: 0, legacy_algorithm_equivalent: rows.length, actual_or_unproven_drift: 0 },
    cohorts: { exact: [], legacy_algorithm_equivalent: rows, actual_or_unproven_drift: [] },
  };
}

export function selectLegacyAuditBindingSourceCohort({ manifest, sourcesRoot, sourceEvidence }) {
  const loaded = loadLegacyAuditBindingSources({ manifest, sourcesRoot });
  if (sourceEvidence?.schemaVersion !== 1 || sourceEvidence?.status !== 'source_evidence_fetched') {
    fail('candidate source evidence is incomplete');
  }
  const skills = uniqueMap(sourceEvidence.skills, 'id', 'candidate Skills');
  const audits = uniqueMap(sourceEvidence.audits, 'id', 'candidate audits');
  if (skills.size !== loaded.allRows.length || audits.size !== loaded.allRows.length) {
    fail('candidate source evidence does not cover all fixed boundaries');
  }
  const selected = { exact: [], legacy_algorithm_equivalent: [], actual_or_unproven_drift: [] };
  const countsByRun = new Map(manifest.sources.map((source) => [source.runId, { legacy: 0, drift: 0 }]));
  for (const { source, classificationName, row } of loaded.allRows) {
    const skill = skills.get(row.id);
    const audit = audits.get(row.publicEligibilityAuditId);
    if (
      !skill || skill.slug !== row.slug
      || !audit || audit.skill_id !== row.id
    ) {
      fail(`candidate source identity mismatch for ${row.slug}`);
    }
    if (!RAW_AUDIT_HASH_RE.test(audit.content_hash || '')) continue;
    if (skill.public_eligibility_audit_id !== row.publicEligibilityAuditId) {
      fail(`current raw32 audit pointer changed for ${row.slug}`);
    }
    selected[classificationName].push(row);
    const counter = countsByRun.get(source.runId);
    if (classificationName === 'legacy_algorithm_equivalent') counter.legacy += 1;
    else counter.drift += 1;
  }
  for (const source of manifest.sources) {
    const actual = countsByRun.get(source.runId);
    if (actual.legacy !== source.expectedLegacy || actual.drift !== source.expectedDrift) {
      fail(`raw32 cohort count changed for source run ${source.runId}`);
    }
  }
  for (const rows of Object.values(selected)) rows.sort((a, b) => a.slug.localeCompare(b.slug));
  if (
    selected.legacy_algorithm_equivalent.length !== manifest.expected.legacy_algorithm_equivalent
    || selected.actual_or_unproven_drift.length !== manifest.expected.actual_or_unproven_drift
  ) fail('merged raw32 cohort is not the frozen 61/24 split');
  const classification = {
    schemaVersion: 1,
    status: 'classified',
    counts: {
      exact: 0,
      legacy_algorithm_equivalent: selected.legacy_algorithm_equivalent.length,
      actual_or_unproven_drift: selected.actual_or_unproven_drift.length,
    },
    cohorts: selected,
  };
  const planRows = [...selected.legacy_algorithm_equivalent, ...selected.actual_or_unproven_drift]
    .map(({ evidence: _evidence, ...row }) => row)
    .sort((a, b) => a.slug.localeCompare(b.slug));
  return {
    classification,
    plan: { schemaVersion: 1, status: 'legacy_audit_binding_scope', selectedCount: 85, selected: planRows },
  };
}

function main() {
  const { values } = parseArgs({ options: {
    phase: { type: 'string' }, manifest: { type: 'string' }, 'sources-root': { type: 'string' },
    'source-evidence': { type: 'string' }, output: { type: 'string' },
    'classification-output': { type: 'string' }, 'plan-output': { type: 'string' },
  }, strict: true });
  const manifest = readJson(resolve(values.manifest));
  const sourcesRoot = resolve(values['sources-root']);
  if (values.phase === 'candidate') {
    const result = buildLegacyAuditBindingCandidateScope({ manifest, sourcesRoot });
    writeFileSync(resolve(values.output), `${JSON.stringify(result, null, 2)}\n`, { flag: 'wx' });
  } else if (values.phase === 'select') {
    const result = selectLegacyAuditBindingSourceCohort({
      manifest, sourcesRoot, sourceEvidence: readJson(resolve(values['source-evidence'])),
    });
    writeFileSync(resolve(values['classification-output']), `${JSON.stringify(result.classification, null, 2)}\n`, { flag: 'wx' });
    writeFileSync(resolve(values['plan-output']), `${JSON.stringify(result.plan, null, 2)}\n`, { flag: 'wx' });
  } else fail('phase must be candidate or select');
}

if (process.argv[1]?.endsWith('build-legacy-audit-binding-source-cohort.mjs')) {
  try { main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
