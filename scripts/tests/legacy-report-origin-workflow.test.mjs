import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { buildLegacyReportOriginBoundary } from '../build-legacy-report-origin-boundary.mjs';
import { verifyLegacyReportOriginDocuments } from '../verify-legacy-report-origin-boundary.mjs';

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function fixture() {
  const root = mkdtempSync(join(tmpdir(), 'origin-boundary-'));
  const rows = Array.from({ length: 70 }, (_, index) => ({
    slug: `owner-skill-${String(index).padStart(2, '0')}`,
    skillId: `00000000-0000-4000-8000-${String(index).padStart(12, '0')}`,
    classificationRunId: String(1000 + (index % 7)),
    path: `skills/owner/skill-${String(index).padStart(2, '0')}`,
    currentMarketplaceCommit: 'a'.repeat(40),
  }));
  const sourceBoundaries = [];
  for (let index = 0; index < 7; index++) {
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
      selectedCount: 70,
      sourceBoundaries,
      rows,
    },
  };
}

test('builds and verifies only the exact 70 identities from seven hash-bound classifications', () => {
  const item = fixture();
  try {
    const built = buildLegacyReportOriginBoundary({ cohort: item.cohort, boundariesRoot: item.root });
    const manifest = {
      status: 'legacy_report_origin_evidence_materialized',
      selectedCount: 70,
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

    const outside = structuredClone(manifest);
    outside.selectedCount = 71;
    outside.entries.push({ ...outside.entries[0], slug: 'outside-row' });
    assert.throws(() => verifyLegacyReportOriginDocuments({
      cohort: item.cohort,
      plan: built.plan,
      classification: built.classification,
      manifest: outside,
      dryRunResults,
    }), /exactly the frozen 70-row cohort/);

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
    '../data/legacy-report-origin-cohort-v1.json'
  ), 'utf8'));
  assert.equal(cohort.selectedCount, 70);
  assert.equal(cohort.rows.length, 70);
  assert.equal(cohort.sourceBoundaries.length, 7);
  assert.match(workflow, /ORIGIN_CLI_SHA256: 'ae2d7caf57ea7849ad39b0518d640ee2a0c51f1eee3f4eb2b9797c1abb0bd4cc'/);
  assert.match(workflow, /\[\[ "\$ORIGIN_CLI_SHA256" =~ \^\[0-9a-f\]\{64\}\$ \]\]/);
  assert.match(workflow, /\.workflowName == "Govern Legacy Report-Origin 70"/);
  assert.match(workflow, /sha256sum --check SHA256SUMS/);
  assert.match(workflow, /cmp "\$RUNNER_TEMP\/boundary\/origin-lineage\.json" "\$RUNNER_TEMP\/current-origin-lineage\.json"/);
  assert.match(workflow, /--expected-count 70/);
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
