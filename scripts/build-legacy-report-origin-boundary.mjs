#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

function fail(message) {
  throw new Error(message);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function canonicalIdentity(row) {
  return {
    slug: row.slug,
    skillId: row.skillId,
    classificationRunId: row.classificationRunId,
    path: row.path,
    currentMarketplaceCommit: row.currentMarketplaceCommit,
  };
}

function validateCohort(cohort) {
  if (
    !cohort
    || cohort.schemaVersion !== 2
    || cohort.status !== 'frozen_report_origin_cohort'
    || cohort.repository !== 'aiskillstore/marketplace'
    || !Number.isSafeInteger(cohort.selectedCount)
    || cohort.selectedCount < 1
    || !Array.isArray(cohort.rows)
    || cohort.rows.length !== cohort.selectedCount
    || !Array.isArray(cohort.sourceBoundaries)
    || cohort.sourceBoundaries.length < 1
  ) fail('report-origin cohort must freeze a positive exact row set and its source boundaries');
  const boundaries = new Map();
  for (const boundary of cohort.sourceBoundaries) {
    if (
      !boundary
      || !/^\d+$/.test(boundary.runId || '')
      || !SHA256_RE.test(boundary.classificationSha256 || '')
      || boundaries.has(boundary.runId)
    ) fail('invalid or duplicate source classification boundary');
    boundaries.set(boundary.runId, boundary.classificationSha256);
  }
  const slugs = new Set();
  const ids = new Set();
  const paths = new Set();
  for (const row of cohort.rows) {
    if (
      JSON.stringify(Object.keys(row || {})) !== JSON.stringify([
        'slug', 'skillId', 'classificationRunId', 'path', 'currentMarketplaceCommit',
      ])
      || typeof row.slug !== 'string'
      || !row.slug
      || !UUID_RE.test(row.skillId || '')
      || !boundaries.has(row.classificationRunId)
      || typeof row.path !== 'string'
      || !/^skills\/[^/]+\/[^/]+$/.test(row.path)
      || !COMMIT_RE.test(row.currentMarketplaceCommit || '')
      || slugs.has(row.slug)
      || ids.has(row.skillId)
      || paths.has(row.path)
    ) fail(`invalid or duplicate frozen identity: ${row?.slug || '<missing>'}`);
    slugs.add(row.slug);
    ids.add(row.skillId);
    paths.add(row.path);
  }
  return boundaries;
}

export function buildLegacyReportOriginBoundary({ cohort, boundariesRoot }) {
  const expectedBoundaries = validateCohort(cohort);
  const selectedCount = cohort.selectedCount;
  const classifications = new Map();
  for (const [runId, expectedSha256] of expectedBoundaries) {
    const path = join(resolve(boundariesRoot), runId, 'classification.json');
    const bytes = readFileSync(path);
    if (sha256(bytes) !== expectedSha256) {
      fail(`classification ${runId} differs from the frozen SHA-256`);
    }
    const document = JSON.parse(bytes.toString('utf8'));
    if (
      document?.schemaVersion !== 1
      || document?.status !== 'classified'
      || !Array.isArray(document?.cohorts?.actual_or_unproven_drift)
    ) fail(`classification ${runId} is not a complete frozen classification`);
    classifications.set(runId, document);
  }

  const selected = [];
  for (const identity of cohort.rows) {
    const document = classifications.get(identity.classificationRunId);
    const matches = document.cohorts.actual_or_unproven_drift.filter((row) => (
      row?.slug === identity.slug
    ));
    if (matches.length !== 1) {
      fail(`${identity.slug} is not exactly once in its frozen drift classification`);
    }
    const row = matches[0];
    if (
      row.id !== identity.skillId
      || row.path !== identity.path
      || row.marketplaceCommit !== identity.currentMarketplaceCommit
    ) fail(`${identity.slug} classification identity differs from the frozen cohort`);
    selected.push(row);
  }

  const identities = cohort.rows.map(canonicalIdentity)
    .sort((left, right) => Buffer.compare(Buffer.from(left.slug), Buffer.from(right.slug)));
  const identitySha256 = sha256(JSON.stringify(identities));
  const groupsByCommit = new Map();
  for (const identity of identities) {
    let group = groupsByCommit.get(identity.currentMarketplaceCommit);
    if (!group) {
      group = { marketplaceCommit: identity.currentMarketplaceCommit, identities: [] };
      groupsByCommit.set(identity.currentMarketplaceCommit, group);
    }
    group.identities.push(identity);
  }
  const groups = [...groupsByCommit.values()]
    .sort((left, right) => left.marketplaceCommit.localeCompare(right.marketplaceCommit))
    .map((group) => ({
      marketplaceCommit: group.marketplaceCommit,
      count: group.identities.length,
      slugs: group.identities.map((row) => row.slug),
      paths: group.identities.map((row) => row.path),
    }));

  return {
    classification: {
      schemaVersion: 1,
      status: 'classified',
      classifiedCount: selectedCount,
      counts: { exact: 0, legacy_algorithm_equivalent: 0, actual_or_unproven_drift: selectedCount },
      cohorts: { exact: [], legacy_algorithm_equivalent: [], actual_or_unproven_drift: selected },
    },
    plan: {
      schemaVersion: 1,
      status: 'frozen_report_origin_plan',
      selectedCount,
      identitySha256,
      sourceBoundaries: cohort.sourceBoundaries,
      identities,
      groups,
    },
  };
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null || value.startsWith('--')) fail(`invalid argument: ${key}`);
    const name = key.slice(2);
    if (Object.hasOwn(values, name)) fail(`duplicate argument: ${key}`);
    values[name] = value;
  }
  return values;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  for (const name of ['cohort', 'boundaries-root', 'classification-output', 'plan-output']) {
    if (!args[name]) fail(`--${name} is required`);
  }
  const output = buildLegacyReportOriginBoundary({
    cohort: JSON.parse(readFileSync(resolve(args.cohort), 'utf8')),
    boundariesRoot: args['boundaries-root'],
  });
  writeFileSync(resolve(args['classification-output']), `${JSON.stringify(output.classification, null, 2)}\n`, { flag: 'wx' });
  writeFileSync(resolve(args['plan-output']), `${JSON.stringify(output.plan, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`${JSON.stringify({ status: output.plan.status, selectedCount: output.plan.selectedCount })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try { main(); } catch (error) {
    process.stderr.write(`report-origin boundary build failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
