#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
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
    /[\u0000-\u001f\u007f?#]/.test(path) ||
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
    if (!slug || /[\u0000-\u001f\u007f,\s]/.test(slug)) fail('Production inventory contains an unsafe slug');
    if (seenSlugs.has(slug)) fail(`Production inventory contains duplicate slug ${slug}`);
    seenSlugs.add(slug);

    const marketplaceCommit = String(raw.marketplace_commit_sha ?? '').trim();
    const contentHash = String(raw.content_hash ?? '').trim();
    const treeHash = String(raw.tree_hash ?? '').trim();
    const artifactRevision = Number(raw.artifact_revision);
    if (!COMMIT_RE.test(marketplaceCommit)) fail(`Invalid production marketplace commit for ${slug}`);
    if (!SHA256_RE.test(contentHash)) fail(`Invalid production content_hash for ${slug}`);
    if (!SHA256_RE.test(treeHash)) fail(`Invalid production tree_hash for ${slug}`);
    if (!Number.isSafeInteger(artifactRevision) || artifactRevision < 0) {
      fail(`Invalid production artifact_revision for ${slug}`);
    }
    const path = normalizePath(raw.plugin_path, slug);
    if (seenPaths.has(path)) fail(`Production inventory contains duplicate plugin_path ${path}`);
    seenPaths.add(path);
    return {
      slug,
      path,
      marketplaceCommit,
      contentHash,
      treeHash,
      artifactRevision,
    };
  }).sort((left, right) => left.slug < right.slug ? -1 : left.slug > right.slug ? 1 : 0);
}

export function buildArtifactBackfillPlan({
  repositoryRoot,
  inventory,
  batchSize,
  startAfter = null,
}) {
  const root = resolve(repositoryRoot);
  const boundedBatchSize = parsePositiveInteger(batchSize, 'batch-size');
  if (boundedBatchSize > MAX_BATCH_SIZE) fail(`batch-size must be between 1 and ${MAX_BATCH_SIZE}`);

  const catalog = normalizeInventory(inventory);
  const cursor = String(startAfter ?? '').trim() || null;
  if (cursor && !catalog.some((row) => row.slug === cursor)) {
    fail(`start-after is not an exact production Skill slug: ${cursor}`);
  }

  const eligible = catalog.filter((row) =>
    row.artifactRevision === 0 && (!cursor || row.slug > cursor)
  );
  const selected = eligible.slice(0, boundedBatchSize);
  for (const row of selected) validatePinnedSnapshot(root, row);

  const groupMap = new Map();
  for (const row of selected) {
    if (!groupMap.has(row.marketplaceCommit)) groupMap.set(row.marketplaceCommit, []);
    groupMap.get(row.marketplaceCommit).push(row);
  }
  const groups = [...groupMap.entries()]
    .sort(([left], [right]) => left < right ? -1 : left > right ? 1 : 0)
    .map(([marketplaceCommit, rows]) => ({
      marketplaceCommit,
      count: rows.length,
      paths: rows.map((row) => row.path),
      slugs: rows.map((row) => row.slug),
    }));

  const lastSelected = selected.at(-1)?.slug ?? null;
  const remainingAfterBatch = Math.max(0, eligible.length - selected.length);
  const legacyAtOrBeforeCursor = cursor
    ? catalog.filter((row) => row.artifactRevision === 0 && row.slug <= cursor).length
    : 0;

  return {
    schemaVersion: 2,
    inventoryCount: catalog.length,
    totalLegacy: catalog.filter((row) => row.artifactRevision === 0).length,
    batchSize: boundedBatchSize,
    startAfter: cursor,
    legacyAtOrBeforeCursor,
    selectedCount: selected.length,
    lastSelected,
    hasMore: remainingAfterBatch > 0,
    nextStartAfter: remainingAfterBatch > 0 ? lastSelected : null,
    remainingAfterBatch,
    selected,
    groups,
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
    groupCount: plan.groups.length,
    hasMore: plan.hasMore,
    nextStartAfter: plan.nextStartAfter,
    remainingAfterBatch: plan.remainingAfterBatch,
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
