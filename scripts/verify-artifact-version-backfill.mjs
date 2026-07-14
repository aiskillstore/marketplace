#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function fail(message) {
  throw new Error(message);
}

function rowsFromInventory(inventory) {
  const rows = Array.isArray(inventory) ? inventory : inventory?.rows;
  if (!Array.isArray(rows)) fail('Post-run inventory has no rows array');
  const bySlug = new Map();
  for (const row of rows) {
    if (typeof row?.slug !== 'string' || bySlug.has(row.slug)) {
      fail(`Post-run inventory contains an invalid or duplicate slug: ${row?.slug ?? '<missing>'}`);
    }
    bySlug.set(row.slug, row);
  }
  return bySlug;
}

export function verifyArtifactVersionReadback({ mode, plan, postInventory }) {
  if (mode !== 'dry-run' && mode !== 'execute') fail('mode must be dry-run or execute');
  if (!Array.isArray(plan?.selected)) fail('Plan has no selected rows');
  const postBySlug = rowsFromInventory(postInventory);
  const evidence = [];

  for (const before of plan.selected) {
    const after = postBySlug.get(before.slug);
    if (!after) fail(`Selected Skill disappeared from production: ${before.slug}`);

    const preserved = {
      status: after.status === before.status,
      publicEligible: after.public_eligible === before.publicEligible,
      path: after.plugin_path === before.path,
      marketplaceCommit: after.marketplace_commit_sha === before.marketplaceCommit,
      contentHash: after.content_hash === before.contentHash,
      treeHash: after.tree_hash === before.treeHash,
      publishedAt: after.published_at === before.publishedAt,
      updatedAt: after.updated_at === before.updatedAt,
    };
    for (const [field, matches] of Object.entries(preserved)) {
      if (!matches) fail(`Post-run ${field} changed for ${before.slug}`);
    }

    const afterRevision = Number(after.artifact_revision);
    const afterCurrentId = after.current_artifact_version_id ?? null;
    if (mode === 'dry-run') {
      if (afterRevision !== before.artifactRevision) {
        fail(`Dry-run changed artifact_revision for ${before.slug}`);
      }
      if (afterCurrentId !== before.currentArtifactVersionId) {
        fail(`Dry-run changed current_artifact_version_id for ${before.slug}`);
      }
    } else {
      const expectedRevision = before.artifactRevision + 1;
      if (!Number.isSafeInteger(afterRevision) || afterRevision !== expectedRevision) {
        fail(
          `Execute initialized unexpected artifact_revision for ${before.slug}: ` +
          `expected ${expectedRevision}, got ${after.artifact_revision}`
        );
      }
      if (!UUID_RE.test(String(afterCurrentId ?? ''))) {
        fail(`Execute did not initialize current_artifact_version_id for ${before.slug}`);
      }
    }

    evidence.push({
      slug: before.slug,
      preserved,
      before: {
        artifactRevision: before.artifactRevision,
        currentArtifactVersionId: before.currentArtifactVersionId,
        status: before.status,
        publicEligible: before.publicEligible,
        path: before.path,
        marketplaceCommit: before.marketplaceCommit,
        contentHash: before.contentHash,
        treeHash: before.treeHash,
        publishedAt: before.publishedAt,
        updatedAt: before.updatedAt,
      },
      after: {
        artifactRevision: afterRevision,
        currentArtifactVersionId: afterCurrentId,
        status: after.status,
        publicEligible: after.public_eligible,
        path: after.plugin_path,
        marketplaceCommit: after.marketplace_commit_sha,
        contentHash: after.content_hash,
        treeHash: after.tree_hash,
        publishedAt: after.published_at,
        updatedAt: after.updated_at,
      },
    });
  }

  return { schemaVersion: 1, mode, verifiedCount: evidence.length, evidence };
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null) fail(`Invalid argument: ${key ?? '<missing>'}`);
    values[key.slice(2)] = value;
  }
  return values;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  if (!args.mode || !args.plan || !args['post-inventory'] || !args.output) {
    fail('--mode, --plan, --post-inventory, and --output are required');
  }
  const result = verifyArtifactVersionReadback({
    mode: args.mode,
    plan: JSON.parse(readFileSync(resolve(args.plan), 'utf8')),
    postInventory: JSON.parse(readFileSync(resolve(args['post-inventory']), 'utf8')),
  });
  writeFileSync(resolve(args.output), `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify({ mode: result.mode, verifiedCount: result.verifiedCount })}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`artifact backfill readback failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
