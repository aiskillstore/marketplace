#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const MAX_BATCH_SIZE = 10;
const AUDIT_SCHEMA_PATH = 'schemas/skill-report.schema.json';

function fail(message) { throw new Error(message); }
function git(root, args) {
  try {
    return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch (error) {
    fail(`Git evidence failed (${args.join(' ')}): ${error.stderr?.trim() || error.message}`);
  }
}

export function prepareFreshCanonicalAuditBatch({
  repositoryRoot,
  cohort,
  startAfter = null,
  batchSize = 10,
  productionInventory,
  previousBoundary = null,
  cohortSha256 = null,
}) {
  if (cohort?.schemaVersion !== 1 || cohort?.status !== 'lineage_unproven'
    || !Array.isArray(cohort.rows) || cohort.count !== cohort.rows.length) fail('Invalid lineage-unproven cohort');
  const size = Number(batchSize);
  if (!Number.isSafeInteger(size) || size < 1 || size > MAX_BATCH_SIZE) fail(`batch-size must be 1-${MAX_BATCH_SIZE}`);
  const seen = new Set();
  const rows = cohort.rows.map((row) => {
    if (typeof row?.slug !== 'string' || !row.slug || seen.has(row.slug)
      || !UUID_RE.test(row.skillId || '') || !COMMIT_RE.test(row.marketplaceCommit || '')
      || !SHA256_RE.test(row.reportContentHash || '') || !SHA256_RE.test(row.reportTreeHash || '')
      || !SHA256_RE.test(row.canonicalArtifact?.contentHash || '')
      || !SHA256_RE.test(row.canonicalArtifact?.treeHash || '')
      || row.governanceEligibleByLineage !== false
      || !['same_source_tree_unproven', 'source_changed_after_report_subject'].includes(row.remainingReason)
      || typeof row.path !== 'string' || !row.path.startsWith('skills/')
      || row.path.includes('\\') || row.path.split('/').some((part) => !part || part === '.' || part === '..')) {
      fail(`Invalid fresh-audit cohort row: ${row?.slug || '<unknown>'}`);
    }
    seen.add(row.slug);
    return row;
  }).sort((left, right) => left.slug.localeCompare(right.slug, 'en', { sensitivity: 'variant' }));
  const cursor = startAfter || null;
  const cursorIndex = cursor ? rows.findIndex((row) => row.slug === cursor) : -1;
  if (cursor && cursorIndex < 0) fail(`start-after is not in the cohort: ${cursor}`);
  if (!productionInventory || !Array.isArray(productionInventory.rows)) {
    fail('Exact production inventory is required for cursor continuity');
  }
  if (!cursor && previousBoundary !== null) fail('Initial batch cannot consume a previous boundary');
  if (cursor) {
    const metadata = previousBoundary?.metadata;
    const selection = previousBoundary?.selection;
    const execution = previousBoundary?.executionProof;
    const supportedExecutionProof = execution?.schemaVersion === 1
      || (execution?.schemaVersion === 2
        && execution.producerKind === 'fresh_canonical_audit_recovery'
        && execution.failedExecuteRunId === '29623717000'
        && execution.failedExecuteHeadSha === '15492b473b84a835e8b63083510ad1e59184b8db'
        && [
          execution.executionResultsSha256,
          execution.postInventorySha256,
          execution.boundaryManifestSha256,
          execution.recoveryEvidenceManifestSha256,
          execution.scoreTimestampEvidenceSha256,
          execution.cacheClosureEvidenceSha256,
          execution.cacheReadbackSha256,
          execution.smokeResultSha256,
        ].every((value) => typeof value === 'string' && /^[0-9a-f]{64}$/.test(value)));
    if (metadata?.status !== 'fresh_canonical_audit_frozen'
      || metadata.lastSelected !== cursor || selection?.lastSelected !== cursor
      || selection?.status !== 'lineage_unproven'
      || typeof metadata.runId !== 'string' || !metadata.runId
      || !cohortSha256 || metadata.cohortSha256 !== cohortSha256
      || execution?.status !== 'fresh_canonical_audit_execution_complete'
      || !supportedExecutionProof
      || execution.dryRunId !== metadata.runId
      || execution.lastSelected !== cursor || execution.cohortSha256 !== cohortSha256
      || typeof execution.executeRunId !== 'string' || !execution.executeRunId
      || execution.scoreFinalized !== true || execution.timestampFinalized !== true
      || execution.cacheClosureCompleted !== true || execution.packClosureCompleted !== true
      || execution.productionSmokeCompleted !== true) {
      fail('Cursor is not chained to a successfully closed previous execution');
    }
    const productionById = new Map(productionInventory.rows.map((row) => [row.id, row]));
    for (const row of rows.slice(0, cursorIndex + 1)) {
      const production = productionById.get(row.skillId);
      if (production?.slug !== row.slug || !Number.isSafeInteger(production.artifact_revision)
        || production.artifact_revision < 1
        || typeof production.current_artifact_version_id !== 'string'
        || !production.current_artifact_version_id) {
        fail(`Cursor prefix is not fully governed in production: ${row.slug}`);
      }
    }
  }
  const selected = rows.slice(cursorIndex + 1, cursorIndex + 1 + size);
  for (const row of selected) {
    git(repositoryRoot, ['cat-file', '-e', `${row.marketplaceCommit}:${row.path}/SKILL.md`]);
    git(repositoryRoot, ['cat-file', '-e', `${row.marketplaceCommit}:${row.path}/skill-report.json`]);
  }
  for (const commit of new Set(selected.map((row) => row.marketplaceCommit))) {
    git(repositoryRoot, ['cat-file', '-e', `${commit}:${AUDIT_SCHEMA_PATH}`]);
  }
  const grouped = new Map();
  for (const row of selected) {
    if (!grouped.has(row.marketplaceCommit)) grouped.set(row.marketplaceCommit, []);
    grouped.get(row.marketplaceCommit).push(row);
  }
  const groups = [...grouped.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([marketplaceCommit, group]) => ({
      marketplaceCommit,
      count: group.length,
      paths: [AUDIT_SCHEMA_PATH, ...group.map((row) => row.path)],
      slugs: group.map((row) => row.slug),
    }));
  return {
    schemaVersion: 1,
    status: 'lineage_unproven',
    count: selected.length,
    counts: {
      same_source_tree_unproven: selected.filter((row) => row.remainingReason === 'same_source_tree_unproven').length,
      source_changed_after_report_subject: selected.filter((row) => row.remainingReason === 'source_changed_after_report_subject').length,
    },
    rows: selected,
    groups,
    sourceCount: rows.length,
    startAfter: cursor,
    lastSelected: selected.at(-1)?.slug ?? null,
    remaining: rows.length - (cursorIndex + 1 + selected.length),
  };
}

function args(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 2) result[argv[index]?.replace(/^--/, '')] = argv[index + 1];
  return result;
}

export function main(argv = process.argv.slice(2)) {
  const options = args(argv);
  if (!options.cohort || !options.output || !options['production-inventory']) {
    fail('--cohort, --production-inventory, and --output are required');
  }
  const cohortBytes = readFileSync(resolve(options.cohort));
  const result = prepareFreshCanonicalAuditBatch({
    repositoryRoot: resolve(options['repository-root'] || process.cwd()),
    cohort: JSON.parse(cohortBytes.toString('utf8')),
    startAfter: options['start-after'] || null,
    batchSize: options['batch-size'] || 10,
    productionInventory: JSON.parse(readFileSync(resolve(options['production-inventory']), 'utf8')),
    previousBoundary: options['previous-boundary']
      ? JSON.parse(readFileSync(resolve(options['previous-boundary']), 'utf8'))
      : null,
    cohortSha256: createHash('sha256').update(cohortBytes).digest('hex'),
  });
  if (result.count === 0) fail('No remaining rows after the requested cursor');
  writeFileSync(resolve(options.output), `${JSON.stringify(result, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify({ count: result.count, lastSelected: result.lastSelected, remaining: result.remaining })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try { main(); } catch (error) { process.stderr.write(`fresh audit batch preparation failed: ${error.message}\n`); process.exitCode = 1; }
}
