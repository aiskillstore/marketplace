#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const LEGACY_TREE_HASH_SCHEME = 'legacy_path_sha256_merkle_v1';
const LEGACY_PREVIOUS_REPORT_TREE_HASH_SCHEME =
  'legacy_path_sha256_merkle_previous_report_v1';
const LEGACY_PREVIOUS_REPORT_INPUT_RELATION =
  'canonical_install_plus_previous_generated_report';
const CLASSIFICATIONS = [
  'exact',
  'legacy_algorithm_equivalent',
  'actual_or_unproven_drift',
];

function fail(message) {
  throw new Error(message);
}

function asMap(rows, key, label) {
  if (!Array.isArray(rows)) fail(`${label} is not an array`);
  const map = new Map();
  for (const row of rows) {
    const value = row?.[key];
    if (typeof value !== 'string' || !value || map.has(value)) {
      fail(`${label} contains an invalid or duplicate ${key}: ${value ?? '<missing>'}`);
    }
    map.set(value, row);
  }
  return map;
}

function expectedGroups(plan, allowedSlugs = null) {
  if (!Array.isArray(plan?.batches) || !Array.isArray(plan?.selected)) {
    fail('Plan lacks batches or selected rows');
  }
  const groups = [];
  for (const batch of plan.batches) {
    for (const group of batch.groups || []) {
      const slugs = allowedSlugs
        ? group.slugs.filter((slug) => allowedSlugs.has(slug))
        : [...group.slugs];
      if (slugs.length > 0) {
        groups.push({
          batchIndex: batch.index,
          marketplaceCommit: group.marketplaceCommit,
          slugs,
        });
      }
    }
  }
  return groups;
}

function validateWrapperShape(wrapper, expected, phase) {
  if (wrapper?.batchIndex !== expected.batchIndex) {
    fail(`${phase} batch index mismatch for ${expected.marketplaceCommit}`);
  }
  if (wrapper?.marketplaceCommit !== expected.marketplaceCommit) {
    fail(`${phase} marketplace commit order mismatch`);
  }
  if (wrapper?.selectedCount !== expected.slugs.length) {
    fail(`${phase} selected count mismatch for ${expected.marketplaceCommit}`);
  }
  if (!Number.isSafeInteger(wrapper?.exitCode) || wrapper.exitCode < 0) {
    fail(`${phase} has an invalid CLI exit code`);
  }
  const result = wrapper.result;
  if (!result || typeof result !== 'object' || !Array.isArray(result.results)) {
    fail(`${phase} CLI output is missing valid JSON results`);
  }
  if (
    result.artifactOnly !== true
    || result.repairStaleReportHashes !== true
    || result.dryRun !== (phase === 'classification')
    || result.mode !== (phase === 'classification' ? 'dry-run' : 'artifact-only')
  ) {
    fail(`${phase} CLI mode contract mismatch for ${expected.marketplaceCommit}`);
  }
  if (result.results.length !== expected.slugs.length) {
    fail(`${phase} result count mismatch for ${expected.marketplaceCommit}`);
  }
  if (
    !Array.isArray(result.slugs)
    || result.slugs.length !== expected.slugs.length
    || result.slugs.some((slug, index) => slug !== expected.slugs[index])
  ) {
    fail(`${phase} top-level slugs do not match the pinned plan`);
  }
  const bySlug = asMap(result.results, 'slug', `${phase} results`);
  if (
    bySlug.size !== expected.slugs.length
    || expected.slugs.some((slug) => !bySlug.has(slug))
  ) {
    fail(`${phase} result slugs do not match the pinned plan`);
  }
  return { result, bySlug };
}

function validateHashEvidence(artifact, before, expectedClassification) {
  const repair = artifact?.hashRepair;
  if (!repair || typeof repair !== 'object') fail(`Missing hash evidence for ${before.slug}`);
  if (
    repair.requested !== true
    || repair.applied !== false
    || repair.classification !== expectedClassification
    || repair.eligibleForExecution !== (expectedClassification === 'exact')
  ) {
    fail(`Invalid hash classification contract for ${before.slug}`);
  }
  const hashes = [
    repair.reportContentHash,
    repair.packagedContentHash,
    repair.reportTreeHash,
    repair.packagedTreeHash,
    repair.legacyCalculatedContentHash,
    repair.legacyCalculatedTreeHash,
  ];
  if (hashes.some((value) => !SHA256_RE.test(String(value ?? '')))) {
    fail(`Invalid hash evidence for ${before.slug}`);
  }
  if (
    repair.reportContentHash !== before.contentHash
    || repair.reportTreeHash !== before.treeHash
    || repair.packagedContentHash !== artifact.contentHash
    || repair.packagedTreeHash !== artifact.treeHash
    || artifact.observedAt !== repair.observedAt
    || artifact.observationTimeSource !== repair.observationTimeSource
  ) {
    fail(`Hash/provenance evidence does not match the pinned identity for ${before.slug}`);
  }
  for (const field of [
    'reportContentHashScheme',
    'packagedContentHashScheme',
    'reportTreeHashScheme',
    'packagedTreeHashScheme',
    'legacyCalculatedContentHashScheme',
    'legacyCalculatedTreeHashScheme',
    'observationTimeSource',
  ]) {
    if (typeof repair[field] !== 'string' || repair[field].length === 0) {
      fail(`Missing ${field} evidence for ${before.slug}`);
    }
  }
  if (!Number.isFinite(Date.parse(repair.observedAt))) {
    fail(`Invalid observation time for ${before.slug}`);
  }

  const contentMismatch = repair.reportContentHash !== repair.packagedContentHash;
  const treeMismatch = repair.reportTreeHash !== repair.packagedTreeHash;
  const canonicalMatch = !contentMismatch && !treeMismatch;
  const plainLegacyMatch =
    repair.reportContentHash === repair.legacyCalculatedContentHash
    && repair.reportTreeHash === repair.legacyCalculatedTreeHash;
  const previousReportEvidenceAbsent =
    repair.previousReportSha256 == null
    && repair.previousReportInputRelation == null
    && repair.legacyPreviousReportCalculatedTreeHash == null;
  const previousReportEvidenceComplete =
    SHA256_RE.test(String(repair.previousReportSha256 ?? ''))
    && repair.previousReportInputRelation === LEGACY_PREVIOUS_REPORT_INPUT_RELATION
    && SHA256_RE.test(String(repair.legacyPreviousReportCalculatedTreeHash ?? ''));
  if (
    (!previousReportEvidenceAbsent && !previousReportEvidenceComplete)
    || (previousReportEvidenceComplete
      && repair.legacyPreviousReportCalculatedTreeHashScheme
        !== LEGACY_PREVIOUS_REPORT_TREE_HASH_SCHEME)
    || (previousReportEvidenceAbsent
      && repair.legacyPreviousReportCalculatedTreeHashScheme != null
      && repair.legacyPreviousReportCalculatedTreeHashScheme
        !== LEGACY_PREVIOUS_REPORT_TREE_HASH_SCHEME)
  ) {
    fail(`Previous-report legacy evidence is incomplete for ${before.slug}`);
  }
  const previousReportLegacyMatch =
    previousReportEvidenceComplete
    && repair.reportContentHash === repair.legacyCalculatedContentHash
    && repair.reportTreeHash === repair.legacyPreviousReportCalculatedTreeHash;
  if (
    repair.contentHashMismatch !== contentMismatch
    || repair.treeHashMismatch !== treeMismatch
    || repair.packagedContentHashScheme !== 'skill_md_raw_bytes_v1'
    || repair.packagedTreeHashScheme !== 'canonical_entries_v1'
    || repair.legacyCalculatedContentHashScheme !== 'skill_md_strip_version_trim_v1'
    || repair.legacyCalculatedTreeHashScheme !== LEGACY_TREE_HASH_SCHEME
  ) {
    fail(`Hash algorithm evidence is internally inconsistent for ${before.slug}`);
  }

  const classificationEvidence = {
    exact: {
      reason: 'report_matches_canonical_packaged_hashes',
      contentScheme: 'skill_md_raw_bytes_v1',
      treeScheme: 'canonical_entries_v1',
      matches: canonicalMatch,
    },
    legacy_algorithm_equivalent: {
      reason: 'report_matches_complete_legacy_scheme_but_audit_rebinding_is_required',
      contentScheme: 'skill_md_strip_version_trim_v1',
      treeScheme: repair.reportTreeHashScheme,
      matches: !canonicalMatch && (
        repair.reportTreeHashScheme === LEGACY_TREE_HASH_SCHEME
          ? plainLegacyMatch
          : repair.reportTreeHashScheme === LEGACY_PREVIOUS_REPORT_TREE_HASH_SCHEME
            ? previousReportLegacyMatch && !plainLegacyMatch
            : false
      ),
    },
    actual_or_unproven_drift: {
      reason: 'report_hashes_do_not_match_one_complete_known_scheme',
      contentScheme: 'unproven',
      treeScheme: 'unproven',
      matches: !canonicalMatch && !plainLegacyMatch && !previousReportLegacyMatch,
    },
  }[expectedClassification];
  if (
    repair.reason !== classificationEvidence.reason
    || repair.reportContentHashScheme !== classificationEvidence.contentScheme
    || repair.reportTreeHashScheme !== classificationEvidence.treeScheme
    || classificationEvidence.matches !== true
  ) {
    fail(`Hash classification is not independently proven for ${before.slug}`);
  }
}

function validatePinnedArtifact(artifact, before) {
  if (
    artifact?.marketplaceCommit !== before.marketplaceCommit
    || artifact?.sourcePath !== before.path
    || !SHA256_RE.test(String(artifact?.contentHash ?? ''))
    || !SHA256_RE.test(String(artifact?.treeHash ?? ''))
  ) {
    fail(`Artifact identity does not match the pinned plan for ${before.slug}`);
  }
}

export function classifyArtifactVersionResults({ plan, groupResults }) {
  const selectedBySlug = asMap(plan?.selected, 'slug', 'plan selected rows');
  const expected = expectedGroups(plan);
  if (!Array.isArray(groupResults) || groupResults.length !== expected.length) {
    fail(`Classification group count mismatch: expected ${expected.length}, got ${groupResults?.length ?? '<invalid>'}`);
  }

  const cohortRows = Object.fromEntries(CLASSIFICATIONS.map((name) => [name, []]));
  for (let index = 0; index < expected.length; index += 1) {
    const expectedGroup = expected[index];
    const wrapper = groupResults[index];
    const { result, bySlug } = validateWrapperShape(wrapper, expectedGroup, 'classification');
    let groupSynced = 0;
    let groupBlocked = 0;

    for (const slug of expectedGroup.slugs) {
      const before = selectedBySlug.get(slug);
      const row = bySlug.get(slug);
      const artifact = row.artifact;
      const classification = artifact?.hashRepair?.classification;
      if (!CLASSIFICATIONS.includes(classification)) {
        fail(`Missing supported classification for ${slug}`);
      }
      validatePinnedArtifact(artifact, before);
      validateHashEvidence(artifact, before, classification);
      if (
        row.mode !== 'dry-run'
        || row.writeOccurred !== false
        || row.skipped === true
        || artifact.artifactVersionId !== null
        || artifact.revision !== null
        || artifact.created !== null
        || artifact.changeKind !== null
      ) {
        fail(`Classification attempted or reported a write for ${slug}`);
      }

      groupSynced += 1;
      if (classification !== 'exact') groupBlocked += 1;
      if (
        row.success !== true
        || row.blocked !== (classification !== 'exact')
        || row.skillId !== before.id
        || row.error !== undefined
        || artifact.currentArtifactVersionId !== null
        || artifact.currentRevision !== 0
        || artifact.skillPublishedAt !== before.publishedAt
        || artifact.skillUpdatedAt !== before.updatedAt
        || artifact.publicEligible !== before.publicEligible
        || artifact.publicEligibilityAuditId !== before.publicEligibilityAuditId
      ) {
        fail(`Dry-run database projection evidence mismatch for ${slug}`);
      }
      cohortRows[classification].push({ ...before, evidence: row });
    }

    if (
      result.synced !== groupSynced
      || result.skipped !== 0
      || result.blocked !== groupBlocked
      || result.errors !== 0
      || result.success !== true
      || wrapper.exitCode !== 0
    ) {
      fail(`Classification summary/exit contract mismatch for ${expectedGroup.marketplaceCommit}`);
    }
  }

  const classifiedCount = CLASSIFICATIONS.reduce(
    (count, name) => count + cohortRows[name].length,
    0
  );
  if (classifiedCount !== selectedBySlug.size) {
    fail(`Classification coverage mismatch: expected ${selectedBySlug.size}, got ${classifiedCount}`);
  }
  const exactSlugs = new Set(cohortRows.exact.map((row) => row.slug));
  const exactBatches = expectedGroups(plan, exactSlugs).map((group) => ({
    ...group,
    count: group.slugs.length,
    paths: group.slugs.map((slug) => selectedBySlug.get(slug).path),
  }));
  const counts = Object.fromEntries(CLASSIFICATIONS.map((name) => [name, cohortRows[name].length]));

  return {
    schemaVersion: 1,
    status: 'classified',
    classifiedCount,
    counts,
    executionEligibleCount: counts.exact,
    remainingCohorts: {
      legacyAlgorithmEquivalent: counts.legacy_algorithm_equivalent,
      actualOrUnprovenDrift: counts.actual_or_unproven_drift,
      total: counts.legacy_algorithm_equivalent + counts.actual_or_unproven_drift,
    },
    cohorts: cohortRows,
    exactBatches,
  };
}

export function verifyArtifactVersionExecution({ plan, classification, groupResults }) {
  const selectedBySlug = asMap(plan?.selected, 'slug', 'plan selected rows');
  const exactRows = classification?.cohorts?.exact;
  const exactBySlug = asMap(exactRows, 'slug', 'exact cohort');
  const expected = expectedGroups(plan, new Set(exactBySlug.keys()));
  if (!Array.isArray(groupResults) || groupResults.length !== expected.length) {
    fail(`Execution group count mismatch: expected ${expected.length}, got ${groupResults?.length ?? '<invalid>'}`);
  }

  const evidence = [];
  for (let index = 0; index < expected.length; index += 1) {
    const expectedGroup = expected[index];
    const wrapper = groupResults[index];
    const { result, bySlug } = validateWrapperShape(wrapper, expectedGroup, 'execution');
    for (const slug of expectedGroup.slugs) {
      if (!exactBySlug.has(slug)) fail(`Execution attempted a non-exact cohort row: ${slug}`);
      const before = selectedBySlug.get(slug);
      const row = bySlug.get(slug);
      const artifact = row.artifact;
      validatePinnedArtifact(artifact, before);
      validateHashEvidence(artifact, before, 'exact');
      if (
        row.success !== true
        || row.skipped === true
        || row.skillId !== before.id
        || row.mode !== 'artifact-only'
        || row.writeOccurred !== true
        || row.error !== undefined
        || artifact.currentArtifactVersionId !== null
        || artifact.currentRevision !== 0
        || !UUID_RE.test(String(artifact.artifactVersionId ?? ''))
        || artifact.revision !== 1
        || artifact.created !== true
        || artifact.changeKind !== 'initial'
        || artifact.skillPublishedAt !== before.publishedAt
        || artifact.skillUpdatedAt !== before.updatedAt
        || artifact.publicEligible !== before.publicEligible
        || artifact.publicEligibilityAuditId !== before.publicEligibilityAuditId
      ) {
        fail(`Exact cohort execution contract mismatch for ${slug}`);
      }
      evidence.push({ slug, before, result: row });
    }
    if (
      wrapper.exitCode !== 0
      || result.success !== true
      || result.synced !== expectedGroup.slugs.length
      || result.skipped !== 0
      || result.blocked !== 0
      || result.errors !== 0
    ) {
      fail(`Execution summary/exit contract mismatch for ${expectedGroup.marketplaceCommit}`);
    }
  }

  return {
    schemaVersion: 1,
    status: 'executed',
    executedCount: evidence.length,
    remainingCohorts: classification.remainingCohorts,
    evidence,
  };
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
  if (!args.phase || !args.plan || !args.results || !args.output) {
    fail('--phase, --plan, --results, and --output are required');
  }
  const plan = JSON.parse(readFileSync(resolve(args.plan), 'utf8'));
  const groupResults = JSON.parse(readFileSync(resolve(args.results), 'utf8'));
  let output;
  if (args.phase === 'classification') {
    output = classifyArtifactVersionResults({ plan, groupResults });
  } else if (args.phase === 'execution') {
    if (!args.classification) fail('--classification is required for execution verification');
    output = verifyArtifactVersionExecution({
      plan,
      classification: JSON.parse(readFileSync(resolve(args.classification), 'utf8')),
      groupResults,
    });
  } else {
    fail('--phase must be classification or execution');
  }
  writeFileSync(resolve(args.output), `${JSON.stringify(output, null, 2)}\n`);
  process.stdout.write(`${JSON.stringify({ phase: args.phase, status: output.status })}\n`);
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`artifact backfill ${process.argv.includes('execution') ? 'execution' : 'classification'} verification failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
