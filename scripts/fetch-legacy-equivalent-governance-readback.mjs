#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const FILTER_CHUNK_SIZE = 100;

function fail(message) {
  throw new Error(message);
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort();
}

function sortRowsById(rows) {
  return [...rows].sort((left, right) => String(left.id).localeCompare(String(right.id), 'en-US'));
}

function headers(serviceKey) {
  return {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    'Accept-Profile': 'skillstore',
    Range: '0-999',
    'Range-Unit': 'items',
  };
}

async function fetchRows({ supabaseUrl, serviceKey, table, select, filter, values, fetchImpl }) {
  const rows = [];
  for (let offset = 0; offset < values.length; offset += FILTER_CHUNK_SIZE) {
    const chunk = values.slice(offset, offset + FILTER_CHUNK_SIZE);
    const url = new URL(`/rest/v1/${table}`, supabaseUrl);
    url.searchParams.set('select', select);
    url.searchParams.set(filter, `in.(${chunk.join(',')})`);
    const response = await fetchImpl(url, { headers: headers(serviceKey) });
    if (!response.ok) fail(`readback ${table} failed: HTTP ${response.status}`);
    const page = await response.json();
    if (!Array.isArray(page)) fail(`readback ${table} returned a non-array`);
    if (page.length >= 1000) fail(`readback ${table} exceeded the bounded page`);
    rows.push(...page);
  }
  return rows;
}

export async function fetchLegacyGovernanceReadback({
  supabaseUrl,
  serviceKey,
  executionResults,
  fetchImpl = fetch,
}) {
  if (!Array.isArray(executionResults)) fail('execution results must be an array');
  const results = executionResults.flatMap((wrapper) => wrapper?.result?.results || []);
  const skillIds = unique(results.map((row) => row.skillId));
  const auditIds = unique(results.flatMap((row) => [row.sourceAuditId, row.derivedAuditId]));
  const snapshotIds = unique(results.map((row) => row.scoreSnapshotId));
  const derivedAuditIds = unique(results.map((row) => row.derivedAuditId));
  if (skillIds.length !== results.length || snapshotIds.length !== results.length) {
    fail('execution results contain duplicate or missing immutable ids');
  }
  const request = (table, select, filter, values) => fetchRows({
    supabaseUrl,
    serviceKey,
    table,
    select,
    filter,
    values,
    fetchImpl,
  });
  const [skills, audits, scoreSnapshots, scoreBreakdowns, attestations] = await Promise.all([
    request(
      'skills',
      'id,slug,name,description,author_name,supported_tools,file_structure,current_artifact_version_id,artifact_revision,content_hash,tree_hash,marketplace_commit_sha,plugin_path,public_eligible,public_eligibility_audit_id,published_at,updated_at,current_quality_score_snapshot_id,quality_score',
      'id',
      skillIds
    ),
    request(
      'skill_security_audit',
      '*',
      'id',
      auditIds
    ),
    request(
      'skill_quality_score_snapshots',
      'id,skill_id,score_subject,score_subject_hash,score_input_hash,scorer_version',
      'id',
      snapshotIds
    ),
    request(
      'skill_quality_breakdown',
      'skill_id,score_snapshot_id,stale_at,stale_reason',
      'skill_id',
      skillIds
    ),
    request(
      'security_audit_attestations',
      'id,audit_id',
      'audit_id',
      derivedAuditIds
    ),
  ]);
  return {
    schemaVersion: 1,
    skillIds,
    skills,
    audits,
    scoreSnapshots,
    scoreBreakdowns,
    attestations,
  };
}

export async function fetchLegacyGovernanceSourceEvidence({
  supabaseUrl,
  serviceKey,
  classification,
  includeDrift = false,
  fetchImpl = fetch,
}) {
  const legacy = classification?.cohorts?.legacy_algorithm_equivalent;
  if (!Array.isArray(legacy)) fail('classification lacks the legacy-equivalent cohort');
  const drift = classification?.cohorts?.actual_or_unproven_drift;
  if (includeDrift && !Array.isArray(drift)) fail('classification lacks the drift cohort');
  const selected = includeDrift ? [...legacy, ...drift] : legacy;
  const skillIds = unique(selected.map((row) => row.id));
  const auditIds = unique(selected.map((row) => row.publicEligibilityAuditId));
  if (skillIds.length !== selected.length || auditIds.length !== selected.length) {
    fail('classification contains duplicate or missing Skill/audit ids');
  }
  const request = (table, select, filter, values) => fetchRows({
    supabaseUrl,
    serviceKey,
    table,
    select,
    filter,
    values,
    fetchImpl,
  });
  const [skills, audits, bindings] = await Promise.all([
    request(
      'skills',
      'id,slug,name,description,author_name,supported_tools,file_structure,current_artifact_version_id,artifact_revision,content_hash,tree_hash,marketplace_commit_sha,plugin_path,public_eligible,public_eligibility_audit_id,published_at,updated_at,repository,source_ref,current_quality_score_snapshot_id,quality_score',
      'id',
      skillIds
    ),
    request('skill_security_audit', '*', 'id', auditIds),
    request('legacy_audit_subject_bindings', '*', 'source_audit_id', auditIds),
  ]);
  if (skills.length !== selected.length || audits.length !== selected.length) {
    fail('source evidence readback is incomplete');
  }
  return {
    schemaVersion: 1,
    status: 'source_evidence_fetched',
    skillIds,
    skills: sortRowsById(skills),
    audits: sortRowsById(audits),
    bindings: sortRowsById(bindings),
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

export async function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (args['include-drift'] !== undefined && !['true', 'false'].includes(args['include-drift'])) {
    fail('--include-drift must be true or false');
  }
  const supabaseUrl = process.env.SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_KEY;
  if (!supabaseUrl || !serviceKey) fail('SUPABASE_URL and SUPABASE_SERVICE_KEY are required');
  const finalOutput = args.classification
    ? await fetchLegacyGovernanceSourceEvidence({
        supabaseUrl,
        serviceKey,
        classification: JSON.parse(readFileSync(resolve(args.classification), 'utf8')),
        includeDrift: args['include-drift'] === 'true',
      })
    : await fetchLegacyGovernanceReadback({
        supabaseUrl,
        serviceKey,
        executionResults: JSON.parse(readFileSync(resolve(args['execution-results']), 'utf8')),
      });
  writeFileSync(resolve(args.output), `${JSON.stringify(finalOutput, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`${JSON.stringify({ status: finalOutput.status || 'fetched', skills: finalOutput.skills.length })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  main().catch((error) => {
    process.stderr.write(`legacy-equivalent governance readback failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
