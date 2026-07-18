#!/usr/bin/env node

import { createHash } from 'node:crypto';

function fail(message) {
  throw new Error(`Fresh canonical audit campaign: ${message}`);
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function sha256(value) {
  return createHash('sha256').update(canonicalJson(value)).digest('hex');
}

export const CAMPAIGN_STATES = Object.freeze([
  'PLANNED',
  'EVIDENCE_READY',
  'AUDIT_READY',
  'COMMIT_READY',
  'DB_WRITTEN_NEEDS_SCORE',
  'COMMITTED_SCORED',
  'CACHE_PENDING',
  'ACTIVATED_VERIFIED',
  'CAMPAIGN_SEALED',
]);

const CAMPAIGN_TRANSITIONS = new Map([
  ['PLANNED', new Set(['EVIDENCE_READY'])],
  ['EVIDENCE_READY', new Set(['AUDIT_READY', 'COMMIT_READY'])],
  ['AUDIT_READY', new Set(['COMMIT_READY'])],
  ['COMMIT_READY', new Set(['DB_WRITTEN_NEEDS_SCORE', 'COMMITTED_SCORED'])],
  ['DB_WRITTEN_NEEDS_SCORE', new Set(['COMMITTED_SCORED'])],
  ['COMMITTED_SCORED', new Set(['CACHE_PENDING'])],
  ['CACHE_PENDING', new Set(['ACTIVATED_VERIFIED'])],
  ['ACTIVATED_VERIFIED', new Set(['CAMPAIGN_SEALED'])],
]);

function requireDigest(value, label) {
  if (!/^[0-9a-f]{64}$/.test(value || '')) fail(`invalid ${label}`);
  return value;
}

export function immutableEvidenceKeys({
  algorithmVersion = 'v1',
  commit,
  path,
  sourceDigest,
  treeHash,
}) {
  if (!/^[a-z0-9][a-z0-9.-]*$/.test(algorithmVersion)
    || !/^[0-9a-f]{40}$/.test(commit || '')
    || typeof path !== 'string' || !path || path.startsWith('/') || path.includes('..')) {
    fail('invalid immutable evidence identity');
  }
  requireDigest(sourceDigest, 'source digest');
  requireDigest(treeHash, 'tree hash');
  const pathHash = sha256(path);
  return {
    source: `source/${algorithmVersion}/${commit}/${pathHash}/${treeHash}.tar.zst`,
    evidence: `evidence/${algorithmVersion}/${sourceDigest}.json`,
  };
}

export function immutableFreshAuditKey({
  campaignId,
  model,
  policyVersion,
  promptVersion,
  scannerVersion,
  subjectDigest,
}) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(campaignId || '')) fail('invalid campaign identity');
  for (const [label, value] of Object.entries({ model, policyVersion, promptVersion, scannerVersion })) {
    if (typeof value !== 'string' || !value || value.includes('/')) fail(`invalid ${label}`);
  }
  requireDigest(subjectDigest, 'audit subject digest');
  return `fresh-audit/${campaignId}/${subjectDigest}/${scannerVersion}/${policyVersion}/${model}/${promptVersion}.json`;
}

export function buildCampaignManifest({ campaignId, cohortSha256, rows, shardSize = 10 }) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(campaignId || '') || !/^[0-9a-f]{64}$/.test(cohortSha256 || '')) {
    fail('invalid campaign identity');
  }
  if (!Number.isSafeInteger(shardSize) || shardSize < 1 || shardSize > 10 || !Array.isArray(rows) || rows.length === 0) {
    fail('invalid campaign rows or shard size');
  }
  const ordered = [...rows].sort((left, right) => left.slug.localeCompare(right.slug, 'en', { sensitivity: 'variant' }));
  if (new Set(ordered.map((row) => row.slug)).size !== ordered.length) fail('duplicate campaign slug');
  const shards = [];
  for (let offset = 0; offset < ordered.length; offset += shardSize) {
    const shardRows = ordered.slice(offset, offset + shardSize);
    const index = shards.length;
    shards.push({
      index,
      shardId: `${campaignId}-${String(index).padStart(4, '0')}`,
      startExclusive: offset === 0 ? null : ordered[offset - 1].slug,
      endInclusive: shardRows.at(-1).slug,
      count: shardRows.length,
      rowsSha256: sha256(shardRows),
      slugs: shardRows.map((row) => row.slug),
    });
  }
  const items = ordered.map((row) => ({
    slug: row.slug,
    inputSha256: sha256(row),
    requiresFreshAudit: row.requiresFreshAudit !== false,
    shardId: shards.find((shard) => shard.slugs.includes(row.slug)).shardId,
  }));
  const base = {
    schemaVersion: 1,
    campaignId,
    cohortSha256,
    totalCount: ordered.length,
    shardSize,
    shards,
    items,
  };
  return { ...base, manifestSha256: sha256(base) };
}

export function createCampaignLedger(manifest) {
  if (manifest?.schemaVersion !== 1 || !Array.isArray(manifest.items)) {
    fail('unsupported campaign manifest');
  }
  return manifest.items.map((item) => ({
    campaignId: manifest.campaignId,
    slug: item.slug,
    shardId: item.shardId,
    state: 'PLANNED',
    inputSha256: item.inputSha256,
    outputSha256: null,
    attempt: 0,
    leaseOwner: null,
    leaseExpiresAt: null,
  }));
}

export function transitionCampaignItem(entry, {
  fromInputSha256,
  outputSha256,
  to,
  attempt,
  leaseOwner = null,
  leaseExpiresAt = null,
}) {
  if (!entry || !CAMPAIGN_STATES.includes(entry.state)
    || !CAMPAIGN_TRANSITIONS.get(entry.state)?.has(to)) {
    fail(`invalid campaign transition ${entry?.state || 'unknown'} -> ${to}`);
  }
  if (entry.inputSha256 !== requireDigest(fromInputSha256, 'transition input digest')) {
    fail(`stale campaign input for ${entry.slug}`);
  }
  requireDigest(outputSha256, 'transition output digest');
  if (!Number.isSafeInteger(attempt) || attempt !== entry.attempt + 1) {
    fail(`invalid campaign attempt for ${entry.slug}`);
  }
  if ((leaseOwner === null) !== (leaseExpiresAt === null)) fail('incomplete campaign lease');
  if (leaseExpiresAt !== null && !Number.isFinite(Date.parse(leaseExpiresAt))) {
    fail('invalid campaign lease expiry');
  }
  return {
    ...entry,
    state: to,
    inputSha256: outputSha256,
    outputSha256,
    attempt,
    leaseOwner,
    leaseExpiresAt,
  };
}

export function assignFreshAuditLanes(manifest, laneCount = 2) {
  if (manifest?.schemaVersion !== 1 || !Array.isArray(manifest.items)
    || !Number.isSafeInteger(laneCount) || laneCount < 1 || laneCount > 3) {
    fail('invalid Fresh audit lane request');
  }
  const lanes = Array.from({ length: laneCount }, (_, index) => ({ index, slugs: [] }));
  manifest.items
    .filter((item) => item.requiresFreshAudit)
    .sort((left, right) => left.slug.localeCompare(right.slug, 'en', { sensitivity: 'variant' }))
    .forEach((item, index) => lanes[index % laneCount].slugs.push(item.slug));
  return lanes.map((lane) => ({
    ...lane,
    count: lane.slugs.length,
    slugsSha256: sha256(lane.slugs),
  }));
}

export function finalizeCampaign({ manifest, ledger }) {
  if (manifest?.schemaVersion !== 1 || !Array.isArray(manifest.shards) || !Array.isArray(ledger)) {
    fail('unsupported campaign evidence');
  }
  const byShard = new Map();
  for (const entry of ledger) {
    if (byShard.has(entry?.shardId)) fail(`duplicate ledger shard ${entry?.shardId}`);
    byShard.set(entry?.shardId, entry);
  }
  for (const shard of manifest.shards) {
    const entry = byShard.get(shard.shardId);
    if (entry?.status !== 'fresh_canonical_audit_execution_complete'
      || entry.count !== shard.count || entry.endInclusive !== shard.endInclusive
      || !/^[0-9a-f]{64}$/.test(entry.proofSha256 || '')) {
      fail(`incomplete shard ${shard.shardId}`);
    }
  }
  if (byShard.size !== manifest.shards.length) fail('ledger contains an unknown shard');
  return {
    schemaVersion: 1,
    status: 'fresh_canonical_audit_campaign_complete',
    campaignId: manifest.campaignId,
    manifestSha256: manifest.manifestSha256,
    completedCount: manifest.totalCount,
    finalCursor: manifest.shards.at(-1).endInclusive,
    ledgerSha256: sha256([...ledger].sort((a, b) => a.shardId.localeCompare(b.shardId))),
  };
}
