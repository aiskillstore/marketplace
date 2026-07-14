#!/usr/bin/env node

import { isDeepStrictEqual } from 'node:util';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ISO_TIMESTAMP_RE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,6}))?(Z|([+-])(\d{2}):(\d{2}))$/;

function fail(message) {
  throw new Error(message);
}

function parseStrictIsoTimestamp(value) {
  if (typeof value !== 'string') return null;
  const match = ISO_TIMESTAMP_RE.exec(value);
  if (!match) return null;

  const [
    , yearText, monthText, dayText, hourText, minuteText, secondText,
    fractionText, , offsetSign, offsetHourText, offsetMinuteText,
  ] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const hour = Number(hourText);
  const minute = Number(minuteText);
  const second = Number(secondText);
  const leapYear = year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
  const daysInMonth = [31, leapYear ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1];
  const offsetHour = Number(offsetHourText ?? 0);
  const offsetMinute = Number(offsetMinuteText ?? 0);
  if (
    month < 1 || month > 12
    || day < 1 || day > daysInMonth
    || hour > 23
    || minute > 59
    || second > 59
    || offsetHour > 23
    || offsetMinute > 59
  ) {
    return null;
  }

  const localTime = new Date(0);
  localTime.setUTCFullYear(year, month - 1, day);
  localTime.setUTCHours(hour, minute, second, 0);
  const offsetDirection = offsetSign === '-' ? -1 : 1;
  const offsetMilliseconds = offsetDirection * (offsetHour * 60 + offsetMinute) * 60_000;
  const epochMilliseconds = localTime.getTime() - offsetMilliseconds;
  const fractionMicroseconds = BigInt((fractionText ?? '').padEnd(6, '0') || '0');
  return BigInt(epochMilliseconds) * 1_000n + fractionMicroseconds;
}

function isSameIsoInstant(left, right) {
  const leftEpoch = parseStrictIsoTimestamp(left);
  const rightEpoch = parseStrictIsoTimestamp(right);
  return leftEpoch !== null && rightEpoch !== null && leftEpoch === rightEpoch;
}

function rowsByKey(rows, key, label) {
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

function rowsBySkill(rows, label) {
  if (!Array.isArray(rows)) fail(`${label} is not an array`);
  const map = new Map();
  for (const row of rows) {
    if (typeof row?.skill_id !== 'string' || !row.skill_id) {
      fail(`${label} contains a row without skill_id`);
    }
    if (!map.has(row.skill_id)) map.set(row.skill_id, []);
    map.get(row.skill_id).push(row);
  }
  return map;
}

function sortedJson(rows) {
  return [...rows].sort((left, right) => {
    const a = JSON.stringify(left);
    const b = JSON.stringify(right);
    return a < b ? -1 : a > b ? 1 : 0;
  });
}

function assertSameRows(before, after, label) {
  if (!isDeepStrictEqual(sortedJson(before), sortedJson(after))) {
    fail(`${label} changed during the backfill`);
  }
}

function expectedHashProvenance(artifact) {
  const repair = artifact.hashRepair;
  return {
    schemaVersion: 1,
    classification: 'exact',
    report: {
      contentHash: repair.reportContentHash,
      contentHashScheme: repair.reportContentHashScheme,
      treeHash: repair.reportTreeHash,
      treeHashScheme: repair.reportTreeHashScheme,
    },
    packaged: {
      contentHash: repair.packagedContentHash,
      contentHashScheme: repair.packagedContentHashScheme,
      treeHash: repair.packagedTreeHash,
      treeHashScheme: repair.packagedTreeHashScheme,
    },
    legacyCalculated: {
      contentHash: repair.legacyCalculatedContentHash,
      contentHashScheme: repair.legacyCalculatedContentHashScheme,
      treeHash: repair.legacyCalculatedTreeHash,
      treeHashScheme: repair.legacyCalculatedTreeHashScheme,
    },
    observationTimeSource: repair.observationTimeSource,
  };
}

export function verifyArtifactVersionReadback({
  mode,
  plan,
  classification,
  execution,
  preInventory,
  postInventory,
}) {
  if (mode !== 'dry-run' && mode !== 'execute') fail('mode must be dry-run or execute');
  if (!Array.isArray(plan?.selected)) fail('Plan has no selected rows');
  if (classification?.classifiedCount !== plan.selected.length) {
    fail('Classification does not cover the full legacy plan');
  }

  const expectedScope = plan.selected.map((row) => row.id).sort();
  if (
    !isDeepStrictEqual(preInventory?.scopedSkillIds, expectedScope)
    || !isDeepStrictEqual(postInventory?.scopedSkillIds, expectedScope)
  ) {
    fail('Pre/post evidence scope does not match the complete bounded plan');
  }

  const preSkills = rowsByKey(preInventory?.rows, 'slug', 'pre-run Skills');
  const postSkills = rowsByKey(postInventory?.rows, 'slug', 'post-run Skills');
  const preArtifacts = rowsBySkill(preInventory?.artifacts, 'pre-run artifacts');
  const postArtifacts = rowsBySkill(postInventory?.artifacts, 'post-run artifacts');
  const preObservations = rowsBySkill(preInventory?.observations, 'pre-run observations');
  const postObservations = rowsBySkill(postInventory?.observations, 'post-run observations');
  const exactSlugs = new Set((classification?.cohorts?.exact || []).map((row) => row.slug));
  const executionBySlug = new Map(
    (execution?.evidence || []).map((row) => [row.slug, row.result])
  );
  if (mode === 'execute' && executionBySlug.size !== exactSlugs.size) {
    fail('Execution evidence does not cover the complete exact cohort');
  }

  assertSameRows(
    preInventory?.packMemberships || [],
    postInventory?.packMemberships || [],
    'Dependent Pack membership closure'
  );
  assertSameRows(preInventory?.packs || [], postInventory?.packs || [], 'Dependent Pack timestamps');

  const evidence = [];
  for (const planned of plan.selected) {
    const before = preSkills.get(planned.slug);
    const after = postSkills.get(planned.slug);
    if (!before || !after) fail(`Selected Skill disappeared from inventory: ${planned.slug}`);
    const preserved = {
      id: after.id === before.id && before.id === planned.id,
      status: after.status === before.status && before.status === planned.status,
      publicEligible:
        after.public_eligible === before.public_eligible
        && before.public_eligible === planned.publicEligible,
      publicEligibilityAuditId:
        after.public_eligibility_audit_id === before.public_eligibility_audit_id
        && before.public_eligibility_audit_id === planned.publicEligibilityAuditId,
      path: after.plugin_path === before.plugin_path && before.plugin_path === planned.path,
      marketplaceCommit:
        after.marketplace_commit_sha === before.marketplace_commit_sha
        && before.marketplace_commit_sha === planned.marketplaceCommit,
      contentHash:
        after.content_hash === before.content_hash && before.content_hash === planned.contentHash,
      treeHash: after.tree_hash === before.tree_hash && before.tree_hash === planned.treeHash,
      publishedAt:
        after.published_at === before.published_at && before.published_at === planned.publishedAt,
      updatedAt: after.updated_at === before.updated_at && before.updated_at === planned.updatedAt,
    };
    for (const [field, matches] of Object.entries(preserved)) {
      if (!matches) fail(`Post-run ${field} changed for ${planned.slug}`);
    }

    const beforeArtifactRows = preArtifacts.get(planned.id) || [];
    const afterArtifactRows = postArtifacts.get(planned.id) || [];
    const beforeObservationRows = preObservations.get(planned.id) || [];
    const afterObservationRows = postObservations.get(planned.id) || [];
    const shouldExecute = mode === 'execute' && exactSlugs.has(planned.slug);
    if (!shouldExecute) {
      if (
        Number(after.artifact_revision) !== Number(before.artifact_revision)
        || after.current_artifact_version_id !== before.current_artifact_version_id
      ) {
        fail(`Non-executed cohort artifact projection changed for ${planned.slug}`);
      }
      assertSameRows(beforeArtifactRows, afterArtifactRows, `Artifact history for ${planned.slug}`);
      assertSameRows(beforeObservationRows, afterObservationRows, `Observation history for ${planned.slug}`);
    } else {
      if (beforeArtifactRows.length !== 0 || beforeObservationRows.length !== 0) {
        fail(`Exact legacy row already had artifact history for ${planned.slug}`);
      }
      const result = executionBySlug.get(planned.slug);
      const artifactEvidence = result?.artifact;
      if (!artifactEvidence) fail(`Missing execution artifact evidence for ${planned.slug}`);
      if (
        Number(after.artifact_revision) !== 1
        || after.current_artifact_version_id !== artifactEvidence.artifactVersionId
        || afterArtifactRows.length !== 1
        || afterObservationRows.length !== 1
      ) {
        fail(`Exact cohort did not initialize one artifact and observation for ${planned.slug}`);
      }
      const artifact = afterArtifactRows[0];
      const observation = afterObservationRows[0];
      if (
        artifact.id !== artifactEvidence.artifactVersionId
        || artifact.skill_id !== planned.id
        || artifact.artifact_revision !== 1
        || artifact.upstream_version_normalized !== artifactEvidence.candidateAuthorVersion
        || artifact.upstream_version_status !== artifactEvidence.versionStatus
        || artifact.content_hash !== artifactEvidence.contentHash
        || artifact.tree_hash !== artifactEvidence.treeHash
        || artifact.marketplace_commit_sha !== planned.marketplaceCommit
        || artifact.source_path !== planned.path
        || artifact.upstream_commit_sha !== artifactEvidence.upstreamCommit
        || !isSameIsoInstant(artifact.observed_at, artifactEvidence.observedAt)
        || artifact.previous_version_id !== null
        || artifact.change_kind !== 'initial'
        || artifact.snapshot_status !== 'exact'
        || !SHA256_RE.test(String(artifact.install_snapshot_hash ?? ''))
        || !Number.isSafeInteger(artifact.readme_template_version)
        || artifact.readme_template_version < 1
        || !Number.isSafeInteger(artifact.artifact_builder_version)
        || artifact.artifact_builder_version < 1
        || !isDeepStrictEqual(artifact.hash_provenance, expectedHashProvenance(artifactEvidence))
      ) {
        fail(`Artifact install identity/hash provenance readback mismatch for ${planned.slug}`);
      }
      if (
        !UUID_RE.test(String(observation.id ?? ''))
        || observation.skill_id !== planned.id
        || observation.artifact_version_id !== artifact.id
        || observation.marketplace_commit_sha !== planned.marketplaceCommit
        || observation.source_path !== planned.path
        || observation.upstream_commit_sha !== artifactEvidence.upstreamCommit
        || !isSameIsoInstant(observation.observed_at, artifactEvidence.observedAt)
      ) {
        fail(`Artifact observation readback mismatch for ${planned.slug}`);
      }
    }

    evidence.push({
      slug: planned.slug,
      cohort: exactSlugs.has(planned.slug)
        ? 'exact'
        : classification.cohorts.legacy_algorithm_equivalent.some((row) => row.slug === planned.slug)
          ? 'legacy_algorithm_equivalent'
          : 'actual_or_unproven_drift',
      executed: shouldExecute,
      preserved,
      before: {
        artifactRevision: Number(before.artifact_revision),
        currentArtifactVersionId: before.current_artifact_version_id,
      },
      after: {
        artifactRevision: Number(after.artifact_revision),
        currentArtifactVersionId: after.current_artifact_version_id,
      },
    });
  }

  return {
    schemaVersion: 2,
    mode,
    verifiedCount: evidence.length,
    executedCount: evidence.filter((row) => row.executed).length,
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
  const required = ['mode', 'plan', 'classification', 'pre-inventory', 'post-inventory', 'output'];
  if (required.some((name) => !args[name])) {
    fail(`Missing required argument; expected ${required.map((name) => `--${name}`).join(', ')}`);
  }
  if (args.mode === 'execute' && !args.execution) fail('--execution is required in execute mode');
  const result = verifyArtifactVersionReadback({
    mode: args.mode,
    plan: JSON.parse(readFileSync(resolve(args.plan), 'utf8')),
    classification: JSON.parse(readFileSync(resolve(args.classification), 'utf8')),
    execution: args.execution
      ? JSON.parse(readFileSync(resolve(args.execution), 'utf8'))
      : { evidence: [] },
    preInventory: JSON.parse(readFileSync(resolve(args['pre-inventory']), 'utf8')),
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
