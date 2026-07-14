#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const MAX_BATCH_SIZE = 500;

function fail(message) {
  throw new Error(message);
}

function parsePositiveInteger(value, name) {
  if (!/^[0-9]+$/.test(String(value ?? ''))) fail(`${name} must be a positive integer`);
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) fail(`${name} must be a positive integer`);
  return parsed;
}

function normalizePath(value, slug) {
  const path = String(value ?? '').trim().replace(/^\.\//, '').replace(/\/$/, '');
  if (
    !path.startsWith('skills/') ||
    path.includes('\\') ||
    path.includes('//') ||
    /[\u0000-\u001f\u007f,?#]/.test(path) ||
    path.split('/').some((segment) => !segment || segment === '.' || segment === '..')
  ) {
    fail(`Invalid production plugin_path for ${slug}: ${value ?? '<null>'}`);
  }
  return path;
}

function git(repositoryRoot, args) {
  try {
    return execFileSync('git', ['-C', repositoryRoot, ...args], {
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (error) {
    const detail = error.stderr?.trim() || error.message;
    fail(`Git evidence check failed (${args.join(' ')}): ${detail}`);
  }
}

function validatePinnedSnapshot(repositoryRoot, row) {
  git(repositoryRoot, ['cat-file', '-e', `${row.marketplaceCommit}:${row.path}/SKILL.md`]);
  const reportText = git(repositoryRoot, ['show', `${row.marketplaceCommit}:${row.path}/skill-report.json`]);
  let report;
  try {
    report = JSON.parse(reportText);
  } catch (error) {
    fail(`Invalid pinned skill-report.json for ${row.slug}: ${error.message}`);
  }
  if (report?.meta?.slug !== row.slug) {
    fail(`Pinned report slug mismatch for ${row.slug} at ${row.marketplaceCommit}:${row.path}`);
  }
  if (report?.meta?.content_hash !== row.contentHash) {
    fail(`Pinned report content_hash mismatch for ${row.slug}`);
  }
  if (report?.meta?.tree_hash !== row.treeHash) {
    fail(`Pinned report tree_hash mismatch for ${row.slug}`);
  }
  if (report?.meta?.source_path != null && normalizePath(report.meta.source_path, row.slug) !== row.path) {
    fail(`Pinned report source_path mismatch for ${row.slug}`);
  }
}

function normalizeInventory(inventory) {
  const rows = Array.isArray(inventory) ? inventory : inventory?.rows;
  if (!Array.isArray(rows) || rows.length === 0) fail('Production inventory contains no Skill rows');

  const seenSlugs = new Set();
  const seenPaths = new Set();
  return rows.map((raw) => {
    const slug = typeof raw?.slug === 'string' ? raw.slug.trim() : '';
    const id = raw?.id == null ? '' : String(raw.id).trim();
    if (!slug || /[\u0000-\u001f\u007f,\s]/.test(slug)) fail('Production inventory contains an unsafe slug');
    if (seenSlugs.has(slug)) fail(`Production inventory contains duplicate slug ${slug}`);
    seenSlugs.add(slug);
    if (!UUID_RE.test(id)) fail(`Invalid production id for ${slug}`);

    const marketplaceCommit = String(raw.marketplace_commit_sha ?? '').trim();
    const contentHash = String(raw.content_hash ?? '').trim();
    const treeHash = String(raw.tree_hash ?? '').trim();
    const artifactRevision = Number(raw.artifact_revision);
    const currentArtifactVersionId = raw.current_artifact_version_id == null
      ? null
      : String(raw.current_artifact_version_id).trim();
    const status = typeof raw.status === 'string' ? raw.status.trim() : '';
    const publicEligible = raw.public_eligible;
    const publicEligibilityAuditId = raw.public_eligibility_audit_id == null
      ? null
      : String(raw.public_eligibility_audit_id).trim();
    const publishedAt = typeof raw.published_at === 'string' ? raw.published_at.trim() : '';
    const updatedAt = typeof raw.updated_at === 'string' ? raw.updated_at.trim() : '';
    if (!COMMIT_RE.test(marketplaceCommit)) fail(`Invalid production marketplace commit for ${slug}`);
    if (!SHA256_RE.test(contentHash)) fail(`Invalid production content_hash for ${slug}`);
    if (!SHA256_RE.test(treeHash)) fail(`Invalid production tree_hash for ${slug}`);
    if (!Number.isSafeInteger(artifactRevision) || artifactRevision < 0) {
      fail(`Invalid production artifact_revision for ${slug}`);
    }
    if (!status) fail(`Invalid production status for ${slug}`);
    if (typeof publicEligible !== 'boolean') fail(`Invalid production public_eligible for ${slug}`);
    if (publicEligibilityAuditId !== null && !UUID_RE.test(publicEligibilityAuditId)) {
      fail(`Invalid production public_eligibility_audit_id for ${slug}`);
    }
    if (!publishedAt || !Number.isFinite(Date.parse(publishedAt))) {
      fail(`Invalid production published_at for ${slug}`);
    }
    if (!updatedAt || !Number.isFinite(Date.parse(updatedAt))) {
      fail(`Invalid production updated_at for ${slug}`);
    }
    if (artifactRevision === 0 && currentArtifactVersionId !== null) {
      fail(`Legacy production row has a current artifact id for ${slug}`);
    }
    if (artifactRevision > 0 && !UUID_RE.test(currentArtifactVersionId || '')) {
      fail(`Versioned production row lacks a valid current artifact id for ${slug}`);
    }
    const path = normalizePath(raw.plugin_path, slug);
    if (seenPaths.has(path)) fail(`Production inventory contains duplicate plugin_path ${path}`);
    seenPaths.add(path);
    return {
      id,
      slug,
      path,
      marketplaceCommit,
      contentHash,
      treeHash,
      artifactRevision,
      currentArtifactVersionId,
      status,
      publicEligible,
      publicEligibilityAuditId,
      publishedAt,
      updatedAt,
    };
  }).sort((left, right) => left.slug < right.slug ? -1 : left.slug > right.slug ? 1 : 0);
}

export function buildArtifactBackfillPlan({
  repositoryRoot,
  inventory,
  batchSize,
  startAfter = null,
  endAt = null,
}) {
  const root = resolve(repositoryRoot);
  const boundedBatchSize = parsePositiveInteger(batchSize, 'batch-size');
  if (boundedBatchSize > MAX_BATCH_SIZE) fail(`batch-size must be between 1 and ${MAX_BATCH_SIZE}`);

  const catalog = normalizeInventory(inventory);
  const cursor = String(startAfter ?? '').trim() || null;
  const rangeEnd = String(endAt ?? '').trim() || null;
  const cursorIndex = cursor ? catalog.findIndex((row) => row.slug === cursor) : -1;
  const rangeEndIndex = rangeEnd ? catalog.findIndex((row) => row.slug === rangeEnd) : catalog.length - 1;
  if (cursor && cursorIndex < 0) {
    fail(`start-after is not an exact production Skill slug: ${cursor}`);
  }
  if (rangeEnd && rangeEndIndex < 0) {
    fail(`end-at is not an exact production Skill slug: ${rangeEnd}`);
  }
  if (cursor && rangeEnd && rangeEndIndex <= cursorIndex) {
    fail('end-at must sort after start-after');
  }

  const indexedLegacy = catalog
    .map((row, index) => ({ row, index }))
    .filter(({ row }) => row.artifactRevision === 0);
  const allLegacy = indexedLegacy.map(({ row }) => row);
  const eligible = indexedLegacy.filter(({ index }) =>
    index > cursorIndex && index <= rangeEndIndex
  ).map(({ row }) => row);
  if (rangeEnd && eligible.length > boundedBatchSize) {
    fail(`Pinned slug range contains ${eligible.length} legacy rows; maximum is ${boundedBatchSize}`);
  }
  const selected = eligible.slice(0, boundedBatchSize);
  for (const row of selected) validatePinnedSnapshot(root, row);

  const batches = [];
  for (let offset = 0; offset < selected.length; offset += boundedBatchSize) {
    const rows = selected.slice(offset, offset + boundedBatchSize);
    const groupMap = new Map();
    for (const row of rows) {
      if (!groupMap.has(row.marketplaceCommit)) groupMap.set(row.marketplaceCommit, []);
      groupMap.get(row.marketplaceCommit).push(row);
    }
    const groups = [...groupMap.entries()]
      .sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0)
      .map(([marketplaceCommit, groupRows]) => ({
        marketplaceCommit,
        count: groupRows.length,
        paths: groupRows.map((row) => row.path),
        slugs: groupRows.map((row) => row.slug),
      }));
    batches.push({
      index: batches.length + 1,
      count: rows.length,
      firstSlug: rows[0].slug,
      lastSlug: rows.at(-1).slug,
      groups,
    });
  }

  const selectedEndIndex = selected.length > 0
    ? catalog.findIndex((row) => row.slug === selected.at(-1).slug)
    : cursorIndex;

  return {
    schemaVersion: 3,
    inventoryCount: catalog.length,
    totalLegacy: allLegacy.length,
    batchSize: boundedBatchSize,
    startAfter: cursor,
    endAt: rangeEnd,
    selectedCount: selected.length,
    lastSelected: selected.at(-1)?.slug ?? null,
    nextClassificationCursor: selected.at(-1)?.slug ?? null,
    legacyAtOrBeforeCursor: cursor
      ? indexedLegacy.filter(({ index }) => index <= cursorIndex).length
      : 0,
    remainingLegacyOutsideBatch: allLegacy.length - selected.length,
    unclassifiedLegacyAfterBatch: indexedLegacy.filter(({ index }) => index > selectedEndIndex).length,
    selected,
    batches,
  };
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith('--')) fail(`Unexpected argument: ${key}`);
    const value = argv[index + 1];
    if (value === undefined || value.startsWith('--')) fail(`Missing value for ${key}`);
    values[key.slice(2)] = value;
    index += 1;
  }
  return values;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (!args.inventory || !args.output || !args['paths-output']) {
    fail('--inventory, --output, and --paths-output are required');
  }
  const inventory = JSON.parse(readFileSync(resolve(args.inventory), 'utf8'));
  const plan = buildArtifactBackfillPlan({
    repositoryRoot: resolve(args['repository-root'] || process.cwd()),
    inventory,
    batchSize: args['batch-size'],
    startAfter: args['start-after'] || null,
    endAt: args['end-at'] || null,
  });
  writeFileSync(resolve(args.output), `${JSON.stringify(plan, null, 2)}\n`);
  writeFileSync(
    resolve(args['paths-output']),
    plan.selected.length > 0 ? `${plan.selected.map((row) => row.path).join('\n')}\n` : ''
  );
  process.stdout.write(`${JSON.stringify({
    inventoryCount: plan.inventoryCount,
    totalLegacy: plan.totalLegacy,
    selectedCount: plan.selectedCount,
    lastSelected: plan.lastSelected,
    nextClassificationCursor: plan.nextClassificationCursor,
    remainingLegacyOutsideBatch: plan.remainingLegacyOutsideBatch,
    unclassifiedLegacyAfterBatch: plan.unclassifiedLegacyAfterBatch,
    batchCount: plan.batches.length,
    groupCount: plan.batches.reduce((count, batch) => count + batch.groups.length, 0),
  })}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`artifact backfill plan failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
