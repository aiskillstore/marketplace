#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const PAGE_SIZE = 1000;
const FILTER_CHUNK_SIZE = 100;
const SELECT = [
  'id',
  'slug',
  'plugin_path',
  'marketplace_commit_sha',
  'content_hash',
  'tree_hash',
  'artifact_revision',
  'current_artifact_version_id',
  'status',
  'public_eligible',
  'public_eligibility_audit_id',
  'published_at',
  'updated_at',
  'quality_score',
  'quality_tier',
  'quality_score_calculated_at',
  'current_quality_score_snapshot_id',
].join(',');
const ARTIFACT_SELECT = [
  'id',
  'skill_id',
  'artifact_revision',
  'upstream_version_raw',
  'upstream_version_normalized',
  'upstream_version_source',
  'upstream_version_status',
  'content_hash',
  'tree_hash',
  'upstream_commit_sha',
  'marketplace_commit_sha',
  'source_path',
  'previous_version_id',
  'change_kind',
  'observed_at',
  'created_at',
  'install_snapshot_hash',
  'snapshot_status',
  'readme_template_version',
  'artifact_builder_version',
  'hash_provenance',
].join(',');
const OBSERVATION_SELECT = [
  'id',
  'skill_id',
  'artifact_version_id',
  'marketplace_commit_sha',
  'source_path',
  'upstream_commit_sha',
  'observed_at',
  'created_at',
].join(',');

function fail(message) {
  throw new Error(message);
}

function requestHeaders(serviceKey, range, exactCount = false) {
  return {
    apikey: serviceKey,
    Authorization: `Bearer ${serviceKey}`,
    'Accept-Profile': 'skillstore',
    ...(exactCount ? { Prefer: 'count=exact' } : {}),
    Range: range,
    'Range-Unit': 'items',
  };
}

async function fetchExactSkills({ supabaseUrl, serviceKey, fetchImpl }) {
  const rows = [];
  let expectedTotal = null;
  for (let start = 0; ; start += PAGE_SIZE) {
    const url = new URL('/rest/v1/skills', supabaseUrl);
    url.searchParams.set('select', SELECT);
    url.searchParams.set('order', 'slug.asc');
    const response = await fetchImpl(url, {
      headers: requestHeaders(serviceKey, `${start}-${start + PAGE_SIZE - 1}`, true),
    });
    if (!response.ok) fail(`Production inventory request failed: HTTP ${response.status}`);
    const contentRange = response.headers.get('content-range');
    const match = contentRange?.match(/^(\d+)-(\d+)\/(\d+)$/);
    if (!match) fail(`Production inventory returned invalid Content-Range: ${contentRange ?? '<missing>'}`);
    const total = Number(match[3]);
    if (expectedTotal === null) expectedTotal = total;
    if (total !== expectedTotal) fail('Production inventory count changed during pagination');

    const page = await response.json();
    if (!Array.isArray(page)) fail('Production inventory response is not an array');
    rows.push(...page);
    if (rows.length >= expectedTotal) break;
    if (page.length === 0) fail('Production inventory pagination ended before the exact count');
  }
  if (rows.length !== expectedTotal) {
    fail(`Production inventory count mismatch: expected ${expectedTotal}, received ${rows.length}`);
  }
  return rows;
}

async function fetchScopedRows({
  supabaseUrl,
  serviceKey,
  fetchImpl,
  table,
  select,
  filterColumn,
  filterValues,
  order,
}) {
  const values = [...new Set(filterValues)].sort();
  const rows = [];
  for (let offset = 0; offset < values.length; offset += FILTER_CHUNK_SIZE) {
    const chunk = values.slice(offset, offset + FILTER_CHUNK_SIZE);
    for (let start = 0; ; start += PAGE_SIZE) {
      const url = new URL(`/rest/v1/${table}`, supabaseUrl);
      url.searchParams.set('select', select);
      url.searchParams.set(filterColumn, `in.(${chunk.join(',')})`);
      url.searchParams.set('order', order);
      const response = await fetchImpl(url, {
        headers: requestHeaders(serviceKey, `${start}-${start + PAGE_SIZE - 1}`),
      });
      if (!response.ok) fail(`Production ${table} request failed: HTTP ${response.status}`);
      const page = await response.json();
      if (!Array.isArray(page)) fail(`Production ${table} response is not an array`);
      rows.push(...page);
      if (page.length < PAGE_SIZE) break;
    }
  }
  return rows;
}

export async function fetchArtifactVersionInventory({
  supabaseUrl,
  serviceKey,
  fetchImpl = fetch,
  scopeInventory = null,
  skillsOnly = false,
}) {
  if (!/^https:\/\//.test(supabaseUrl || '')) fail('SUPABASE_URL must be HTTPS');
  if (!serviceKey) fail('SUPABASE_SERVICE_KEY is required');

  const rows = await fetchExactSkills({ supabaseUrl, serviceKey, fetchImpl });
  if (skillsOnly) {
    return {
      schemaVersion: 2,
      count: rows.length,
      scopedSkillIds: [],
      rows,
      packMemberships: [],
      packs: [],
      artifacts: [],
      observations: [],
    };
  }
  const explicitScopeIds = scopeInventory?.scopedSkillIds;
  const scopedRows = scopeInventory
    ? (Array.isArray(scopeInventory)
        ? scopeInventory
        : scopeInventory?.selected || scopeInventory?.rows)
    : rows.filter((row) => Number(row.artifact_revision) === 0);
  if (!Array.isArray(scopedRows)) fail('Scope inventory has no rows or selected array');
  const skillIds = Array.isArray(explicitScopeIds)
    ? explicitScopeIds
    : scopedRows.map((row) => row.id);
  if (skillIds.some((id) => typeof id !== 'string' || id.length === 0)) {
    fail('Scope inventory contains a Skill without an id');
  }

  const packMemberships = await fetchScopedRows({
    supabaseUrl,
    serviceKey,
    fetchImpl,
    table: 'pack_skills',
    select: 'skill_id,pack_id',
    filterColumn: 'skill_id',
    filterValues: skillIds,
    order: 'skill_id.asc,pack_id.asc',
  });
  const packs = await fetchScopedRows({
    supabaseUrl,
    serviceKey,
    fetchImpl,
    table: 'packs',
    select: 'id,slug,published_at,updated_at',
    filterColumn: 'id',
    filterValues: packMemberships.map((row) => row.pack_id),
    order: 'id.asc',
  });
  const artifacts = await fetchScopedRows({
    supabaseUrl,
    serviceKey,
    fetchImpl,
    table: 'skill_artifact_versions',
    select: ARTIFACT_SELECT,
    filterColumn: 'skill_id',
    filterValues: skillIds,
    order: 'skill_id.asc,artifact_revision.asc',
  });
  const observations = await fetchScopedRows({
    supabaseUrl,
    serviceKey,
    fetchImpl,
    table: 'skill_artifact_observations',
    select: OBSERVATION_SELECT,
    filterColumn: 'skill_id',
    filterValues: skillIds,
    order: 'skill_id.asc,created_at.asc,id.asc',
  });

  return {
    schemaVersion: 2,
    count: rows.length,
    scopedSkillIds: [...new Set(skillIds)].sort(),
    rows,
    packMemberships,
    packs,
    artifacts,
    observations,
  };
}

export async function main(argv = process.argv.slice(2)) {
  const outputIndex = argv.indexOf('--output');
  const output = outputIndex >= 0 ? argv[outputIndex + 1] : null;
  if (!output) fail('--output is required');
  const scopeIndex = argv.indexOf('--scope-inventory');
  const scopePath = scopeIndex >= 0 ? argv[scopeIndex + 1] : null;
  if (scopeIndex >= 0 && !scopePath) fail('--scope-inventory requires a path');
  const inventory = await fetchArtifactVersionInventory({
    supabaseUrl: process.env.SUPABASE_URL,
    serviceKey: process.env.SUPABASE_SERVICE_KEY,
    scopeInventory: scopePath ? JSON.parse(readFileSync(resolve(scopePath), 'utf8')) : null,
    skillsOnly: argv.includes('--skills-only'),
  });
  writeFileSync(resolve(output), `${JSON.stringify(inventory, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify({ count: inventory.count })}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  main().catch((error) => {
    process.stderr.write(`artifact inventory fetch failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
