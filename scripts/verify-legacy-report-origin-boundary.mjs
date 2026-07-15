#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const SHA256_RE = /^[0-9a-f]{64}$/;
const COMMIT_RE = /^[0-9a-f]{40}$/;

function fail(message) { throw new Error(message); }
function sha256(bytes) { return createHash('sha256').update(bytes).digest('hex'); }
function bytes(path) { return readFileSync(resolve(path)); }
function json(path) { return JSON.parse(bytes(path).toString('utf8')); }

function identity(row) {
  return {
    slug: row.slug,
    skillId: row.skillId,
    classificationRunId: row.classificationRunId,
    path: row.path,
    currentMarketplaceCommit: row.currentMarketplaceCommit,
  };
}

function canonicalIdentities(rows) {
  return rows.map(identity)
    .sort((left, right) => Buffer.compare(Buffer.from(left.slug), Buffer.from(right.slug)));
}

export function verifyLegacyReportOriginDocuments({ cohort, plan, classification, manifest, dryRunResults }) {
  if (
    cohort?.schemaVersion !== 2
    || cohort?.status !== 'frozen_report_origin_cohort'
    || cohort?.selectedCount !== 70
    || cohort?.rows?.length !== 70
    || plan?.status !== 'frozen_report_origin_plan'
    || plan?.selectedCount !== 70
    || manifest?.status !== 'legacy_report_origin_evidence_materialized'
    || manifest?.selectedCount !== 70
    || classification?.status !== 'classified'
    || classification?.classifiedCount !== 70
    || classification?.counts?.exact !== 0
    || classification?.counts?.legacy_algorithm_equivalent !== 0
    || classification?.counts?.actual_or_unproven_drift !== 70
    || classification?.cohorts?.actual_or_unproven_drift?.length !== 70
    || !Array.isArray(dryRunResults)
  ) fail('report-origin boundary must cover exactly the frozen 70-row cohort');

  const expected = canonicalIdentities(cohort.rows);
  const fromPlan = canonicalIdentities(plan.identities || []);
  const fromManifest = canonicalIdentities(manifest.entries || []);
  const classificationRuns = new Map(cohort.rows.map((row) => [row.slug, row.classificationRunId]));
  const fromClassification = canonicalIdentities(
    classification.cohorts.actual_or_unproven_drift.map((row) => ({
      slug: row.slug,
      skillId: row.id,
      classificationRunId: classificationRuns.get(row.slug),
      path: row.path,
      currentMarketplaceCommit: row.marketplaceCommit,
    }))
  );
  const identityJson = JSON.stringify(expected);
  if (
    JSON.stringify(fromPlan) !== identityJson
    || JSON.stringify(fromManifest) !== identityJson
    || JSON.stringify(fromClassification) !== identityJson
    || plan.identitySha256 !== sha256(identityJson)
    || JSON.stringify(plan.sourceBoundaries) !== JSON.stringify(cohort.sourceBoundaries)
  ) fail('cohort, classification, plan, and origin manifest identities differ');

  const dryRows = dryRunResults.flatMap((group) => group?.result?.results || []);
  const drySlugs = dryRows.map((row) => row?.slug).sort();
  const expectedSlugs = expected.map((row) => row.slug).sort();
  if (
    dryRows.length !== 70
    || JSON.stringify(drySlugs) !== JSON.stringify(expectedSlugs)
    || dryRows.some((row) => (
      row?.mode !== 'dry-run'
      || row?.artifactVersionId !== null
      || row?.artifactRevision !== null
      || row?.derivedAuditId !== null
    ))
  ) fail('administrator dry-run does not cover exactly 70 no-write results');
  return { identitySha256: plan.identitySha256 };
}

export function freezeLegacyReportOriginBoundary(input) {
  const verified = verifyLegacyReportOriginDocuments(input);
  if (
    !/^\d+$/.test(input.runId || '')
    || input.repository !== 'aiskillstore/marketplace'
    || !COMMIT_RE.test(input.workflowCommit || '')
    || input.cliVersion !== '2.6.0'
    || !SHA256_RE.test(input.cliSha256 || '')
  ) fail('invalid frozen execution identity');
  return {
    schemaVersion: 1,
    status: 'frozen',
    workflow: 'govern-legacy-report-origin-70',
    runId: input.runId,
    repository: input.repository,
    workflowCommit: input.workflowCommit,
    cliVersion: input.cliVersion,
    cliSha256: input.cliSha256,
    selectedCount: 70,
    identitySha256: verified.identitySha256,
    cohortSha256: input.cohortSha256,
    planSha256: input.planSha256,
    classificationSha256: input.classificationSha256,
    manifestSha256: input.manifestSha256,
    dryRunResultsSha256: input.dryRunResultsSha256,
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

function fileInputs(args) {
  return {
    cohort: json(args.cohort),
    plan: json(args.plan),
    classification: json(args.classification),
    manifest: json(args.manifest),
    dryRunResults: json(args['dry-run-results']),
  };
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  for (const name of ['phase', 'cohort', 'plan', 'classification', 'manifest', 'dry-run-results']) {
    if (!args[name]) fail(`--${name} is required`);
  }
  const documents = fileInputs(args);
  if (args.phase === 'freeze') {
    for (const name of ['run-id', 'repository', 'workflow-commit', 'cli-version', 'cli-sha256', 'output']) {
      if (!args[name]) fail(`--${name} is required`);
    }
    const output = freezeLegacyReportOriginBoundary({
      ...documents,
      runId: args['run-id'],
      repository: args.repository,
      workflowCommit: args['workflow-commit'],
      cliVersion: args['cli-version'],
      cliSha256: args['cli-sha256'],
      cohortSha256: sha256(bytes(args.cohort)),
      planSha256: sha256(bytes(args.plan)),
      classificationSha256: sha256(bytes(args.classification)),
      manifestSha256: sha256(bytes(args.manifest)),
      dryRunResultsSha256: sha256(bytes(args['dry-run-results'])),
    });
    writeFileSync(resolve(args.output), `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx' });
    return output;
  }
  if (args.phase === 'execute-preflight') {
    if (!args.boundary || !args['expected-run-id']) fail('--boundary and --expected-run-id are required');
    const boundary = json(args.boundary);
    const verified = verifyLegacyReportOriginDocuments(documents);
    const digests = {
      cohortSha256: sha256(bytes(args.cohort)),
      planSha256: sha256(bytes(args.plan)),
      classificationSha256: sha256(bytes(args.classification)),
      manifestSha256: sha256(bytes(args.manifest)),
      dryRunResultsSha256: sha256(bytes(args['dry-run-results'])),
    };
    if (
      boundary?.status !== 'frozen'
      || boundary?.workflow !== 'govern-legacy-report-origin-70'
      || boundary?.runId !== args['expected-run-id']
      || boundary?.selectedCount !== 70
      || boundary?.identitySha256 !== verified.identitySha256
      || Object.entries(digests).some(([key, value]) => boundary[key] !== value)
    ) fail('execute inputs differ from the successful frozen boundary');
    return { status: 'verified', selectedCount: 70 };
  }
  fail(`unsupported phase: ${args.phase}`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    process.stdout.write(`${JSON.stringify(main())}\n`);
  } catch (error) {
    process.stderr.write(`report-origin boundary verification failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
