#!/usr/bin/env node

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function fail(message) {
  throw new Error(`Fresh canonical audit recovery: ${message}`);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sameTimestamp(left, right) {
  return typeof left === 'string' && typeof right === 'string'
    && Number.isFinite(Date.parse(left)) && Date.parse(left) === Date.parse(right);
}

function withinRun(value, failedRun) {
  const time = Date.parse(value);
  const start = Date.parse(failedRun.run_started_at || failedRun.created_at);
  const end = Date.parse(failedRun.updated_at);
  return Number.isFinite(time) && Number.isFinite(start) && Number.isFinite(end)
    && time >= start && time <= end;
}

function uniqueBy(rows, key, label) {
  const result = new Map();
  for (const row of rows) {
    if (!row || typeof row[key] !== 'string' || result.has(row[key])) fail(`duplicate or invalid ${label}`);
    result.set(row[key], row);
  }
  return result;
}

function latestAuditsBySkill(rows, skillIds) {
  const result = new Map();
  for (const row of rows.filter((item) => skillIds.includes(item?.skill_id))) {
    const current = result.get(row.skill_id);
    if (!current || row.version > current.version
      || (row.version === current.version && Date.parse(row.created_at) > Date.parse(current.created_at))) {
      result.set(row.skill_id, row);
    }
  }
  return result;
}

export function verifyRecoveryState({ boundary, inventory, audits, snapshots, breakdowns, failedRun }) {
  if (boundary?.schemaVersion !== 1 || boundary?.status !== 'fresh_canonical_audit_frozen'
    || !Array.isArray(boundary.candidates) || boundary.candidates.length === 0) {
    fail('unsupported frozen boundary');
  }
  if (failedRun?.id !== 29666546406 || failedRun?.head_sha !== '3e7baf520a4d078047b53b95352156e3a3f74260'
    || failedRun?.conclusion !== 'failure' || failedRun?.event !== 'workflow_dispatch'
    || failedRun?.head_branch !== 'main' || failedRun?.run_attempt !== 1) {
    fail('failed run identity does not match the incident boundary');
  }
  if (inventory?.schemaVersion !== 2 || !Array.isArray(inventory.rows) || !Array.isArray(inventory.artifacts)) {
    fail('unsupported post-inventory');
  }

  const candidates = boundary.candidates;
  const candidateSlugs = candidates.map((candidate) => candidate?.row?.slug);
  const candidateIds = candidates.map((candidate) => candidate?.row?.skillId);
  if (new Set(candidateSlugs).size !== candidates.length || new Set(candidateIds).size !== candidates.length) {
    fail('boundary contains duplicate Skill identity');
  }
  const skillsById = uniqueBy(
    inventory.rows.filter((row) => candidateIds.includes(row.id)), 'id', 'post-inventory Skill id'
  );
  const artifactsBySkill = uniqueBy(
    inventory.artifacts.filter((row) => candidateIds.includes(row.skill_id)), 'skill_id', 'artifact Skill id'
  );
  const observationsBySkill = uniqueBy(
    inventory.observations.filter((row) => candidateIds.includes(row.skill_id)),
    'skill_id',
    'observation Skill id'
  );
  const auditsBySkill = latestAuditsBySkill(audits, candidateIds);
  const snapshotsById = uniqueBy(snapshots, 'id', 'score snapshot id');
  const breakdownsBySkill = uniqueBy(breakdowns, 'skill_id', 'score breakdown Skill id');
  if ([skillsById, artifactsBySkill, observationsBySkill, auditsBySkill, breakdownsBySkill]
    .some((map) => map.size !== candidates.length)) {
    fail('recovery evidence does not cover the exact frozen cohort');
  }

  const executionResults = [];
  const scoreEvidence = [];
  const rows = [];
  for (const candidate of candidates) {
    const { row, expectedSkill, expectedLatestAudit, rpcPayload, auditId } = candidate;
    const skill = skillsById.get(row.skillId);
    const artifact = artifactsBySkill.get(row.skillId);
    const observation = observationsBySkill.get(row.skillId);
    const audit = auditsBySkill.get(row.skillId);
    const snapshot = snapshotsById.get(skill?.current_quality_score_snapshot_id);
    const breakdown = breakdownsBySkill.get(row.skillId);
    const expectedAuditContentHash = rpcPayload?.p_audit_payload?.content_hash;
    const subject = snapshot?.score_subject;

    if (!skill || skill.slug !== row.slug || skill.artifact_revision !== 1
      || !UUID_RE.test(skill.current_artifact_version_id || '')
      || skill.current_artifact_version_id !== artifact?.id
      || skill.content_hash !== row.canonicalArtifact.contentHash
      || skill.tree_hash !== row.canonicalArtifact.treeHash
      || skill.marketplace_commit_sha !== row.marketplaceCommit || skill.plugin_path !== row.path
      || skill.public_eligible !== true || skill.status !== 'approved'
      || skill.public_eligibility_audit_id !== auditId
      || !sameTimestamp(skill.published_at, expectedSkill.published_at)
      || !sameTimestamp(skill.updated_at, expectedSkill.updated_at)) {
      fail(`canonical Skill or finalized timestamp mismatch for ${row.slug}`);
    }
    if (artifact?.artifact_revision !== 1 || artifact?.change_kind !== 'initial'
      || artifact?.previous_version_id !== null || artifact?.content_hash !== row.canonicalArtifact.contentHash
      || artifact?.tree_hash !== row.canonicalArtifact.treeHash
      || artifact?.marketplace_commit_sha !== row.marketplaceCommit || artifact?.source_path !== row.path
      || !withinRun(artifact?.created_at, failedRun)) {
      fail(`artifact evidence mismatch for ${row.slug}`);
    }
    if (observation?.artifact_version_id !== artifact.id
      || observation?.marketplace_commit_sha !== row.marketplaceCommit
      || observation?.source_path !== row.path
      || !withinRun(observation?.created_at, failedRun)) {
      fail(`artifact observation mismatch for ${row.slug}`);
    }
    if (audit?.id !== auditId || audit?.version !== expectedLatestAudit.version + 1
      || audit?.content_hash !== expectedAuditContentHash
      || audit?.analysis_status !== 'ok' || audit?.derived_from_audit_id !== null
      || audit?.derivation_kind !== null
      || audit?.subject_marketplace_commit_sha !== row.marketplaceCommit
      || audit?.subject_content_hash !== row.canonicalArtifact.contentHash
      || audit?.subject_tree_hash !== row.canonicalArtifact.treeHash
      || audit?.subject_plugin_path !== row.path
      || !withinRun(audit?.created_at, failedRun)) {
      fail(`fresh audit evidence mismatch for ${row.slug}`);
    }
    if (!snapshot || snapshot.skill_id !== row.skillId || !withinRun(snapshot.created_at, failedRun)
      || snapshot.scorer_version !== '1.9.1' || typeof snapshot.composite_score !== 'number'
      || subject?.auditId !== auditId || subject?.auditVersion !== audit.version
      || subject?.auditContentHash !== audit.content_hash
      || subject?.contentHash !== row.canonicalArtifact.contentHash
      || subject?.treeHash !== row.canonicalArtifact.treeHash
      || subject?.marketplaceCommitSha !== row.marketplaceCommit || subject?.pluginPath !== row.path
      || !sameTimestamp(snapshot?.score_inputs?.skill?.updatedAt, expectedSkill.updated_at)
      || breakdown?.score_snapshot_id !== snapshot.id || breakdown?.stale_at !== null
      || breakdown?.stale_reason !== null || breakdown?.scorer_version !== snapshot.scorer_version
      || breakdown?.composite_score !== snapshot.composite_score
      || !sameTimestamp(breakdown?.calculated_at, snapshot.calculated_at)) {
      fail(`score subject mismatch for ${row.slug}`);
    }
    if (snapshots.some((item) => item.skill_id === row.skillId
      && Date.parse(item.created_at) > Date.parse(snapshot.created_at))) {
      fail(`later score snapshot exists for ${row.slug}`);
    }
    if (skill.quality_score !== snapshot.composite_score || skill.quality_tier !== snapshot.quality_tier
      || !sameTimestamp(skill.quality_score_calculated_at, snapshot.calculated_at)) {
      fail(`current score pointer mismatch for ${row.slug}`);
    }

    executionResults.push({
      slug: row.slug,
      skillId: row.skillId,
      artifactVersionId: artifact.id,
      artifactRevision: 1,
      artifactCreated: true,
      auditId: audit.id,
      auditVersion: audit.version,
      scoreSnapshotId: snapshot.id,
      scoreBreakdownVerified: true,
    });
    scoreEvidence.push({
      calculatedAt: skill.quality_score_calculated_at,
      qualityScore: skill.quality_score,
      qualityTier: skill.quality_tier,
      slug: row.slug,
      snapshotId: snapshot.id,
    });
    rows.push({
      slug: row.slug,
      skillId: row.skillId,
      artifactVersionId: artifact.id,
      artifactCreatedAt: artifact.created_at,
      auditId: audit.id,
      auditVersion: audit.version,
      auditCreatedAt: audit.created_at,
      scoreSnapshotId: snapshot.id,
      scoreSnapshotCreatedAt: snapshot.created_at,
      publishedAtFinalized: true,
      updatedAtFinalized: true,
    });
  }

  return {
    executionResults,
    expectedScoreEvidence: { schemaVersion: 1, scores: scoreEvidence },
    recoveryEvidence: {
      schemaVersion: 1,
      status: 'fresh_canonical_audit_durable_writes_verified',
      failedExecuteRunId: String(failedRun.id),
      failedExecuteHeadSha: failedRun.head_sha,
      verifiedCount: rows.length,
      selectedSlugsCanonicalSha256Input: canonicalJson([...candidateSlugs].sort()),
      rows,
    },
  };
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index < 0 || !args[index + 1] || args[index + 1].startsWith('--')) fail(`missing ${name}`);
  return args[index + 1];
}

async function fetchRows({ table, select, filter, supabaseUrl, serviceKey }) {
  if (!/^https:\/\//.test(supabaseUrl || '') || !serviceKey) fail('Supabase read credentials are required');
  const url = new URL(`/rest/v1/${table}`, supabaseUrl);
  url.searchParams.set('select', select);
  url.searchParams.set(...filter);
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
      'Accept-Profile': 'skillstore',
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
    },
  });
  if (!response.ok) fail(`${table} read failed: HTTP ${response.status}`);
  const rows = await response.json();
  if (!Array.isArray(rows)) fail(`${table} read returned a non-array`);
  return rows;
}

export async function main(args = process.argv.slice(2)) {
  const boundary = JSON.parse(readFileSync(option(args, '--boundary'), 'utf8'));
  const inventory = JSON.parse(readFileSync(option(args, '--post-inventory'), 'utf8'));
  const failedRun = JSON.parse(readFileSync(option(args, '--failed-run'), 'utf8'));
  const outputDir = resolve(option(args, '--output-dir'));
  const ids = boundary.candidates.map((candidate) => candidate.row.skillId);
  const common = {
    supabaseUrl: process.env.SUPABASE_URL,
    serviceKey: process.env.SUPABASE_SERVICE_KEY,
  };
  const [audits, snapshots, breakdowns] = await Promise.all([
    fetchRows({ ...common, table: 'skill_security_audit',
      select: 'id,skill_id,version,content_hash,analysis_status,derived_from_audit_id,derivation_kind,subject_marketplace_commit_sha,subject_content_hash,subject_tree_hash,subject_plugin_path,created_at', filter: ['skill_id', `in.(${ids.join(',')})`] }),
    fetchRows({ ...common, table: 'skill_quality_score_snapshots',
      select: 'id,skill_id,scorer_version,score_subject,score_inputs,breakdown,composite_score,quality_tier,calculated_at,created_at',
      filter: ['skill_id', `in.(${ids.join(',')})`] }),
    fetchRows({ ...common, table: 'skill_quality_breakdown',
      select: 'skill_id,score_snapshot_id,stale_at,stale_reason,calculated_at,scorer_version,composite_score',
      filter: ['skill_id', `in.(${ids.join(',')})`] }),
  ]);
  const result = verifyRecoveryState({
    boundary,
    inventory,
    audits,
    snapshots,
    breakdowns,
    failedRun,
  });
  mkdirSync(outputDir, { recursive: true });
  writeFileSync(resolve(outputDir, 'execution-results.json'), `${JSON.stringify(result.executionResults, null, 2)}\n`);
  writeFileSync(resolve(outputDir, 'expected-score-evidence.json'), `${JSON.stringify(result.expectedScoreEvidence, null, 2)}\n`);
  writeFileSync(resolve(outputDir, 'score-timestamp-evidence.json'), `${JSON.stringify(result.recoveryEvidence, null, 2)}\n`);
}

if (import.meta.url === pathToFileURL(resolve(process.argv[1] || '')).href) {
  main().catch((error) => {
    process.stderr.write(`fresh canonical audit recovery verification failed: ${error.message}\n`);
    process.exitCode = 1;
  });
}
