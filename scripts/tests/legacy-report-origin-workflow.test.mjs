import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { buildLegacyReportOriginBoundary } from '../build-legacy-report-origin-boundary.mjs';
import {
  freezeLegacyReportOriginBoundary,
  verifyLegacyReportOriginDocuments,
} from '../verify-legacy-report-origin-boundary.mjs';

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'origin-boundary-'));
  const rows = Array.from({ length: 50 }, (_, index) => ({
    slug: `owner-skill-${String(index).padStart(2, '0')}`,
    skillId: `00000000-0000-4000-8000-${String(index).padStart(12, '0')}`,
    classificationRunId: String(1000 + (index % 2)),
    path: `skills/owner/skill-${String(index).padStart(2, '0')}`,
    currentMarketplaceCommit: 'a'.repeat(40),
  }));
  const sourceBoundaries = [];
  for (let index = 0; index < 2; index++) {
    const runId = String(1000 + index);
    const selected = rows.filter((row) => row.classificationRunId === runId).map((row) => ({
      id: row.skillId,
      slug: row.slug,
      path: row.path,
      marketplaceCommit: row.currentMarketplaceCommit,
    }));
    const document = {
      schemaVersion: 1,
      status: 'classified',
      cohorts: { actual_or_unproven_drift: selected },
    };
    const bytes = `${JSON.stringify(document, null, 2)}\n`;
    const directory = join(root, runId);
    mkdirSync(directory, { recursive: true });
    writeFileSync(join(directory, 'classification.json'), bytes);
    sourceBoundaries.push({ runId, classificationSha256: sha256(bytes) });
  }
  return {
    root,
    cohort: {
      schemaVersion: 2,
      status: 'frozen_report_origin_cohort',
      repository: 'aiskillstore/marketplace',
      selectedCount: 50,
      sourceBoundaries,
      rows,
    },
  };
}

test('builds and verifies only the exact 50 identities from two hash-bound classifications', () => {
  const item = fixture();
  try {
    const built = buildLegacyReportOriginBoundary({ cohort: item.cohort, boundariesRoot: item.root });
    const manifest = {
      status: 'legacy_report_origin_evidence_materialized',
      selectedCount: 50,
      entries: item.cohort.rows,
    };
    const dryRunResults = [{
      result: {
        results: item.cohort.rows.map((row) => ({
          slug: row.slug,
          mode: 'dry-run',
          artifactVersionId: null,
          artifactRevision: null,
          derivedAuditId: null,
        })),
      },
    }];
    assert.doesNotThrow(() => verifyLegacyReportOriginDocuments({
      cohort: item.cohort,
      plan: built.plan,
      classification: built.classification,
      manifest,
      dryRunResults,
    }));
    const frozen = freezeLegacyReportOriginBoundary({
      cohort: item.cohort,
      plan: built.plan,
      classification: built.classification,
      manifest,
      dryRunResults,
      runId: '29773180840',
      repository: 'aiskillstore/marketplace',
      workflowCommit: 'a'.repeat(40),
      cliVersion: '2.15.9',
      cliSha256: 'b'.repeat(64),
    });
    assert.equal(frozen.cliVersion, '2.15.9');

    const outside = structuredClone(manifest);
    outside.selectedCount = 51;
    outside.entries.push({ ...outside.entries[0], slug: 'outside-row' });
    assert.throws(() => verifyLegacyReportOriginDocuments({
      cohort: item.cohort,
      plan: built.plan,
      classification: built.classification,
      manifest: outside,
      dryRunResults,
    }), /exactly the frozen cohort/);

    writeFileSync(join(item.root, '1000', 'classification.json'), '{"drift":true}\n');
    assert.throws(() => buildLegacyReportOriginBoundary({
      cohort: item.cohort,
      boundariesRoot: item.root,
    }), /differs from the frozen SHA-256/);
  } finally {
    rmSync(item.root, { recursive: true, force: true });
  }
});

test('workflow freezes and replays Git evidence with the audited CLI digest', () => {
  const workflow = readFileSync(resolve(
    import.meta.dirname,
    '../../.github/workflows/govern-legacy-report-origin-70.yml'
  ), 'utf8');
  const cohort = JSON.parse(readFileSync(resolve(
    import.meta.dirname,
    '../data/legacy-report-origin-v2-only-cohort-v1.json'
  ), 'utf8'));
  assert.equal(cohort.selectedCount, 50);
  assert.equal(cohort.rows.length, 50);
  assert.equal(cohort.sourceBoundaries.length, 2);
  assert.deepEqual(
    ['crossbill-highlights-css-colors', 'davila7-docx', 'davila7-pptx', 'dmitrypogrebnoy-generating-rbs']
      .filter((slug) => cohort.rows.some((row) => row.slug === slug)),
    []
  );
  assert.match(workflow, /ORIGIN_COHORT: scripts\/data\/legacy-report-origin-v2-only-cohort-v1\.json/);
  assert.match(workflow, /ORIGIN_COHORT_SHA256: 164edab51b71a2be141d726cb50f7ae94b1c3f7ae622353d28c3f9ad7ac9b346/);
  assert.match(workflow, /ORIGIN_CLI_VERSION: '2\.15\.9'/);
  assert.match(workflow, /ORIGIN_CLI_SHA256: '9a980bbb9574dd3da976803264796dd3ba57d15bafde5645afe6fe5783e5e9ec'/);
  assert.equal((workflow.match(/version: '2\.15\.9'/g) || []).length, 4);
  assert.match(workflow, /\[\[ "\$ORIGIN_CLI_SHA256" =~ \^\[0-9a-f\]\{64\}\$ \]\]/);
  assert.match(workflow, /\.workflowName == "Govern Legacy Report-Origin V2-Only"/);
  assert.match(workflow, /sha256sum --check SHA256SUMS/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/boundary\/origin-lineage\.json" "\$RUNNER_TEMP\/current-origin-lineage\.json"/);
  assert.match(workflow, /--expected-count 50/);
  assert.equal(
    (workflow.match(/Normalize full checkout and verify report-origin runtime/g) || []).length,
    2
  );
  assert.equal((workflow.match(/git sparse-checkout disable/g) || []).length, 2);
  assert.equal((workflow.match(/git reset --hard HEAD/g) || []).length, 2);
  assert.equal(
    (workflow.match(/Missing report-origin runtime after full-checkout normalization/g) || []).length,
    2
  );
  assert.equal((workflow.match(/--legacy-origin-lineage/g) || []).length, 2);
  assert.equal((workflow.match(/--legacy-origin-root/g) || []).length, 2);
  assert.equal((workflow.match(/--legacy-previous-report-root/g) || []).length, 2);
});
