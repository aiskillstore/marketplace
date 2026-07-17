#!/usr/bin/env node

import {
  lstatSync,
  readFileSync,
  readdirSync,
} from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CANONICAL_INDEX = /^(0|[1-9][0-9]*)$/;
const SLUG = /^[a-z0-9][a-z0-9-]*$/;
const OVERALL_STATUSES = new Set(['succeeded', 'failed', 'cancelled', 'skipped']);
const ATTEMPT_STATUSES = new Set(['succeeded', 'failed', 'cancelled', 'skipped']);
const FAILURE_CATEGORIES = new Set([
  'cancelled',
  'cli_nonzero',
  'cli_spawn_failed',
  'duplicate_result',
  'invalid_result',
  'missing_result',
  'process_step_failed',
  'skipped',
  'unexpected_result',
]);

function fail(message) {
  throw new Error(message);
}

function option(args, name, { required = true } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) fail(`missing required option ${name}`);
    return null;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) {
    fail(`missing value for ${name}`);
  }
  return args[index + 1];
}

export function parseCanonicalShardIndex(value, label = 'shard index') {
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value) || value < 0) fail(`${label} must be a non-negative safe integer`);
    return value;
  }
  if (typeof value !== 'string' || !CANONICAL_INDEX.test(value)) {
    fail(`${label} must be canonical decimal (0 or a non-zero digit followed by digits)`);
  }
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed)) fail(`${label} exceeds the safe integer range`);
  return parsed;
}

export function parseSlugCsv(value, label = 'slug list') {
  if (typeof value !== 'string') fail(`${label} must be a CSV string`);
  if (value === '') return [];
  const slugs = value.split(',');
  const seen = new Set();
  for (const slug of slugs) {
    if (!SLUG.test(slug)) fail(`${label} contains invalid slug ${JSON.stringify(slug)}`);
    if (seen.has(slug)) fail(`${label} contains duplicate slug ${JSON.stringify(slug)}`);
    seen.add(slug);
  }
  return slugs;
}

function validateSlugArray(value, label) {
  if (!Array.isArray(value)) fail(`${label} must be an array`);
  const seen = new Set();
  for (const slug of value) {
    if (typeof slug !== 'string' || !SLUG.test(slug)) fail(`${label} contains invalid slug ${JSON.stringify(slug)}`);
    if (seen.has(slug)) fail(`${label} contains duplicate slug ${JSON.stringify(slug)}`);
    seen.add(slug);
  }
  return [...value];
}

function sorted(values) {
  return [...values].sort((left, right) => left.localeCompare(right, 'en'));
}

function assertSameSet(actual, expected, label) {
  assert.deepEqual(sorted(actual), sorted(expected), label);
}

const assert = {
  deepEqual(actual, expected, message) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      fail(`${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  },
};

function assertPartition(planned, succeeded, failed, label) {
  const succeededSet = new Set(succeeded);
  const failedSet = new Set(failed);
  const overlap = succeeded.filter((slug) => failedSet.has(slug));
  if (overlap.length > 0) fail(`${label} succeeded and failed overlap: ${overlap.join(',')}`);
  const combined = [...succeededSet, ...failedSet];
  assertSameSet(combined, planned, `${label} succeeded union failed must equal planned`);
}

function collectReportSlugs(root) {
  const slugs = [];
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) fail(`pending output contains symlink ${path}`);
      if (entry.isDirectory()) {
        walk(path);
      } else if (entry.isFile() && entry.name === 'skill-report.json') {
        slugs.push(basename(dirname(path)));
      }
    }
  }
  walk(root);
  return slugs;
}

function validateAttempt(attempt, planned, expectedNumber) {
  if (!attempt || typeof attempt !== 'object' || Array.isArray(attempt)) fail(`attempt ${expectedNumber} must be an object`);
  if (attempt.number !== expectedNumber) fail(`attempt number must be contiguous; expected ${expectedNumber}`);
  const expectedPhase = expectedNumber === 1 ? 'first' : 'retry';
  if (attempt.phase !== expectedPhase) fail(`attempt ${expectedNumber} phase must be ${expectedPhase}`);
  if (!ATTEMPT_STATUSES.has(attempt.status)) fail(`attempt ${expectedNumber} has invalid status ${JSON.stringify(attempt.status)}`);
  const requested = validateSlugArray(attempt.requested, `attempt ${expectedNumber}.requested`);
  const succeeded = validateSlugArray(attempt.succeeded, `attempt ${expectedNumber}.succeeded`);
  const failed = validateSlugArray(attempt.failed, `attempt ${expectedNumber}.failed`);
  for (const slug of requested) {
    if (!planned.includes(slug)) fail(`attempt ${expectedNumber} requested unplanned slug ${slug}`);
  }
  assertPartition(requested, succeeded, failed, `attempt ${expectedNumber}`);
  if (attempt.status === 'succeeded' && (attempt.exitCode !== 0 || failed.length !== 0)) {
    fail(`attempt ${expectedNumber} succeeded must have exitCode 0 and no failed slugs`);
  }
  if (attempt.status === 'failed' && !Number.isInteger(attempt.exitCode)) {
    fail(`attempt ${expectedNumber} failed must have an integer exitCode`);
  }
  if ((attempt.status === 'cancelled' || attempt.status === 'skipped') && attempt.exitCode !== null) {
    fail(`attempt ${expectedNumber} ${attempt.status} must have a null exitCode`);
  }
}

export function validateSubmissionShardManifest(manifest, {
  expectedIndex = null,
  expectedPlanned = null,
  pendingRoot = null,
  requireSuccess = false,
} = {}) {
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) fail('manifest must be an object');
  if (manifest.schemaVersion !== 1) fail('manifest schemaVersion must be 1');
  const shardIndex = parseCanonicalShardIndex(manifest.shardIndex, 'manifest shardIndex');
  if (expectedIndex !== null && shardIndex !== parseCanonicalShardIndex(expectedIndex, 'expected shard index')) {
    fail(`manifest shardIndex ${shardIndex} does not match expected shard index ${expectedIndex}`);
  }
  if (!OVERALL_STATUSES.has(manifest.status)) fail(`manifest has invalid status ${JSON.stringify(manifest.status)}`);
  if (typeof manifest.reasonCode !== 'string' || manifest.reasonCode.length === 0) fail('manifest reasonCode is required');

  const planned = validateSlugArray(manifest.planned, 'manifest.planned');
  const succeeded = validateSlugArray(manifest.succeeded, 'manifest.succeeded');
  const failed = validateSlugArray(manifest.failed, 'manifest.failed');
  assertPartition(planned, succeeded, failed, 'manifest');
  if (expectedPlanned !== null) assertSameSet(planned, expectedPlanned, 'manifest planned slugs do not match matrix');

  if (!Array.isArray(manifest.failureCategories)) fail('manifest.failureCategories must be an array');
  for (const category of manifest.failureCategories) {
    if (!FAILURE_CATEGORIES.has(category)) fail(`manifest has unknown failure category ${JSON.stringify(category)}`);
  }
  if (new Set(manifest.failureCategories).size !== manifest.failureCategories.length) {
    fail('manifest.failureCategories contains duplicates');
  }

  if (!Array.isArray(manifest.attempts) || manifest.attempts.length === 0) fail('manifest.attempts must not be empty');
  manifest.attempts.forEach((attempt, index) => validateAttempt(attempt, planned, index + 1));

  if (manifest.status === 'succeeded') {
    if (planned.length === 0) {
      if (manifest.reasonCode !== 'no_skills_planned') fail('empty successful manifest must use no_skills_planned');
      if (succeeded.length !== 0 || failed.length !== 0) fail('no_skills_planned must have empty outcome sets');
      if (manifest.attempts.length !== 1 || manifest.attempts[0].status !== 'skipped') {
        fail('no_skills_planned must contain one skipped first attempt');
      }
    } else {
      if (manifest.reasonCode !== 'processed_all_planned') fail('successful manifest must use processed_all_planned');
      if (failed.length !== 0) fail('successful manifest cannot contain failed slugs');
      assertSameSet(succeeded, planned, 'successful manifest must succeed every planned slug');
      if (manifest.attempts.at(-1)?.status !== 'succeeded') fail('successful manifest terminal attempt must be succeeded');
    }
    if (manifest.failureCategories.length !== 0) fail('successful manifest cannot contain failure categories');
  }

  if (pendingRoot !== null) {
    const reports = collectReportSlugs(pendingRoot);
    if (new Set(reports).size !== reports.length) fail('pending output contains duplicate canonical report slug');
    assertSameSet(reports, succeeded, 'pending report slugs do not match manifest succeeded slugs');
  }

  if (requireSuccess && manifest.status !== 'succeeded') {
    fail(`shard ${shardIndex} terminal status is ${manifest.status} (${manifest.reasonCode})`);
  }

  return { ...manifest, shardIndex, planned, succeeded, failed };
}

export function readAndValidateSubmissionShardManifest(path, options = {}) {
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`cannot read shard manifest ${path}: ${error instanceof Error ? error.message : String(error)}`);
  }
  return validateSubmissionShardManifest(manifest, options);
}

function main() {
  const args = process.argv.slice(2);
  const manifestPath = option(args, '--manifest');
  const expectedIndex = option(args, '--expected-index');
  const expectedSlugs = parseSlugCsv(option(args, '--expected-slugs'), 'expected slugs');
  const pendingRoot = option(args, '--pending-root');
  const manifest = readAndValidateSubmissionShardManifest(manifestPath, {
    expectedIndex,
    expectedPlanned: expectedSlugs,
    pendingRoot,
    requireSuccess: args.includes('--require-success'),
  });
  process.stdout.write(`Validated shard ${manifest.shardIndex}: ${manifest.status} (${manifest.reasonCode})\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Shard manifest validation failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
