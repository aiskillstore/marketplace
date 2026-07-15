import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { materializeLegacyReportOriginEvidence } from '../materialize-legacy-report-origin-evidence.mjs';

const SKILL_ID = '11111111-1111-4111-8111-111111111111';
const SKILL_PATH = 'skills/owner/demo';
const SLUG = 'owner-demo';

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function git(repositoryRoot, args, encoding = 'utf8') {
  return execFileSync('git', args, { cwd: repositoryRoot, encoding }).trim();
}

function write(repositoryRoot, relativePath, contents, mode = null) {
  const path = join(repositoryRoot, relativePath);
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, contents);
  if (mode != null) chmodSync(path, mode);
}

function commit(repositoryRoot, message) {
  git(repositoryRoot, ['add', '.']);
  git(repositoryRoot, ['commit', '-m', message]);
  return git(repositoryRoot, ['rev-parse', 'HEAD']);
}

function gitFile(repositoryRoot, commitSha, repositoryPath) {
  const line = git(repositoryRoot, ['ls-tree', '--full-tree', commitSha, '--', repositoryPath]);
  const match = line.match(/^(100644|100755) blob ([0-9a-f]{40,64})\t(.+)$/);
  assert.ok(match, `expected ordinary Git file: ${repositoryPath}`);
  assert.equal(match[3], repositoryPath);
  const bytes = execFileSync('git', ['cat-file', 'blob', match[2]], {
    cwd: repositoryRoot,
    encoding: 'buffer',
  });
  return { mode: match[1], gitBlob: match[2], sha256: sha256(bytes), bytes };
}

function sourceSet(repositoryRoot, commitSha) {
  const output = execFileSync('git', [
    'ls-tree', '-r', '-z', '--full-tree', commitSha, '--', `${SKILL_PATH}/`,
  ], { cwd: repositoryRoot, encoding: 'buffer' });
  const prefix = `${SKILL_PATH}/`;
  const entries = output.toString('utf8').split('\0').filter(Boolean).map((record) => {
    const [metadata, repositoryPath] = record.split('\t');
    const [mode, type, gitBlob] = metadata.split(' ');
    assert.equal(type, 'blob');
    const bytes = execFileSync('git', ['cat-file', 'blob', gitBlob], {
      cwd: repositoryRoot,
      encoding: 'buffer',
    });
    return {
      path: repositoryPath.slice(prefix.length),
      mode,
      gitBlob,
      sha256: sha256(bytes),
    };
  }).filter((entry) => entry.path !== 'skill-report.json');
  entries.sort((left, right) => Buffer.compare(
    Buffer.from(left.path, 'utf8'),
    Buffer.from(right.path, 'utf8'),
  ));
  return { entries, sha256: sha256(JSON.stringify(entries)) };
}

function legacyTreeHash(sourceEntries, previousReportSha256) {
  const root = new Map();
  for (const input of sourceEntries
    .map((entry) => ({ path: entry.path, sha256: entry.sha256 }))
    .concat({ path: 'skill-report.json', sha256: previousReportSha256 })) {
    const parts = input.path.split('/');
    let directory = root;
    for (let index = 0; index < parts.length; index++) {
      const name = parts[index];
      if (index === parts.length - 1) directory.set(name, { sha256: input.sha256 });
      else {
        if (!directory.has(name)) directory.set(name, { children: new Map() });
        directory = directory.get(name).children;
      }
    }
  }
  const entries = [];
  function walk(directory, prefix = '') {
    for (const [name, child] of [...directory].sort(([left], [right]) => left.localeCompare(right))) {
      const path = prefix ? `${prefix}/${name}` : name;
      if (child.children) walk(child.children, path);
      else entries.push(`${path}:${child.sha256}`);
    }
  }
  walk(root);
  return { entries, treeHash: sha256(entries.join('\n')) };
}

function makeRepository({ wrongTree = false } = {}) {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'legacy-report-origin-'));
  git(repositoryRoot, ['init', '--initial-branch=main']);
  git(repositoryRoot, ['config', 'user.name', 'Skillstore Test']);
  git(repositoryRoot, ['config', 'user.email', 'test@skillstore.local']);
  git(repositoryRoot, ['config', 'commit.gpgSign', 'false']);

  write(repositoryRoot, `${SKILL_PATH}/SKILL.md`, '# Demo\n');
  write(repositoryRoot, `${SKILL_PATH}/scripts/tool.sh`, '#!/bin/sh\necho demo\n', 0o755);
  const previousReportBytes = Buffer.from('{"revision":1}\n');
  write(repositoryRoot, `${SKILL_PATH}/skill-report.json`, previousReportBytes);
  const originParent = commit(repositoryRoot, 'previous report');

  const parentSource = sourceSet(repositoryRoot, originParent);
  const legacyTree = legacyTreeHash(parentSource.entries, sha256(previousReportBytes));
  const reportTreeHash = wrongTree ? 'f'.repeat(64) : legacyTree.treeHash;
  const report = {
    schema_version: '1.0.0',
    meta: {
      slug: SLUG,
      content_hash: sha256('# Demo\n'),
      tree_hash: reportTreeHash,
    },
  };
  write(repositoryRoot, `${SKILL_PATH}/skill-report.json`, `${JSON.stringify(report)}\n`);
  const originCommit = commit(repositoryRoot, 'audit report origin');
  write(repositoryRoot, 'unrelated.txt', 'does not change the Skill\n');
  const currentCommit = commit(repositoryRoot, 'later unrelated commit');

  const currentReport = gitFile(repositoryRoot, currentCommit, `${SKILL_PATH}/skill-report.json`);
  const previousReport = gitFile(repositoryRoot, originParent, `${SKILL_PATH}/skill-report.json`);
  const currentSource = sourceSet(repositoryRoot, currentCommit);
  const originSource = sourceSet(repositoryRoot, originCommit);
  const row = {
    slug: SLUG,
    skillId: SKILL_ID,
    classificationRunId: '123456789',
    path: SKILL_PATH,
    marketplaceCommit: currentCommit,
    reportOriginCommit: originCommit,
    reportOriginParent: originParent,
    currentReportGitBlob: currentReport.gitBlob,
    currentReportSha256: currentReport.sha256,
    previousReportGitBlob: previousReport.gitBlob,
    previousReportSha256: previousReport.sha256,
    reportContentHash: report.meta.content_hash,
    reportTreeHash,
    originCalculatedTreeHash: reportTreeHash,
    originTreeInputSha256: reportTreeHash,
    originTreeEntryCount: legacyTree.entries.length,
    treeHashScheme: 'legacy_path_sha256_merkle_previous_report_v1',
    inputRelation: 'canonical_install_plus_previous_generated_report',
    originContentRelation: 'canonical',
    currentContentRelation: 'canonical',
    sourceSetEquality: {
      equal: true,
      currentSha256: currentSource.sha256,
      originSha256: originSource.sha256,
      currentEntryCount: currentSource.entries.length,
      originEntryCount: originSource.entries.length,
    },
    lineageClassification: 'legacy_previous_report_tree_equivalent',
    governanceEligibleByLineage: true,
  };
  return { repositoryRoot, originParent, originCommit, currentCommit, row, previousReportBytes };
}

function cohortFor(row) {
  return {
    schemaVersion: 1,
    repository: 'aiskillstore/marketplace',
    status: 'lineage_recovered',
    count: 1,
    method: {
      reportOrigin: 'last first-parent commit changing the same-path skill-report.json',
      treeHashScheme: 'legacy_path_sha256_merkle_previous_report_v1',
      inputRelation: 'canonical_install_plus_previous_generated_report',
      sourceSetIdentity: 'canonical JSON of sorted non-report path, mode, git blob, sha256 entries',
    },
    rows: [row],
  };
}

function outputs(repositoryRoot, suffix = '') {
  return {
    originRoot: join(repositoryRoot, `origin-output${suffix}`),
    previousReportRoot: join(repositoryRoot, `previous-output${suffix}`),
    manifestPath: join(repositoryRoot, `manifest${suffix}.json`),
  };
}

test('materializes exact origin sources and previous report with complete deterministic evidence', () => {
  const fixture = makeRepository();
  try {
    // The old temporary audit digest is selection evidence, not the new
    // canonical_source_set_v1 authority. Independent Git recomputation wins.
    fixture.row.sourceSetEquality.currentSha256 = 'a'.repeat(64);
    fixture.row.sourceSetEquality.originSha256 = 'b'.repeat(64);
    const paths = outputs(fixture.repositoryRoot);
    const manifest = materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...paths,
    });

    assert.equal(manifest.status, 'legacy_report_origin_evidence_materialized');
    assert.equal(manifest.selectedCount, 1);
    assert.equal(manifest.sourceSetScheme, 'canonical_source_set_v1');
    const entry = manifest.entries[0];
    assert.equal(entry.originCommit, fixture.originCommit);
    assert.equal(entry.originParent, fixture.originParent);
    assert.equal(entry.sourceSetEvidence.equal, true);
    assert.equal(
      entry.sourceSetEvidence.current.sha256,
      entry.sourceSetEvidence.origin.sha256,
    );
    assert.deepEqual(
      entry.sourceSetEvidence.current.entries,
      entry.sourceSetEvidence.origin.entries,
    );
    assert.equal(entry.legacyTreeEvidence.matchesCurrentReport, true);
    assert.deepEqual(
      readFileSync(join(paths.previousReportRoot, entry.previousReport.relativePath)),
      fixture.previousReportBytes,
    );
    const executable = entry.originFiles.find((file) => file.path.endsWith('scripts/tool.sh'));
    assert.ok(executable);
    assert.equal(executable.mode, '100755');
    assert.ok(statSync(join(paths.originRoot, executable.relativePath)).mode & 0o100);
    assert.deepEqual(JSON.parse(readFileSync(paths.manifestPath, 'utf8')), manifest);

    const second = outputs(fixture.repositoryRoot, '-second');
    const repeated = materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...second,
    });
    assert.deepEqual(repeated, manifest);
    assert.deepEqual(readFileSync(second.manifestPath), readFileSync(paths.manifestPath));
  } finally {
    rmSync(fixture.repositoryRoot, { recursive: true, force: true });
  }
});

test('rebuilds evidence from a minimal checked-in identity cohort', () => {
  const fixture = makeRepository();
  try {
    const paths = outputs(fixture.repositoryRoot, '-identity');
    const cohort = {
      schemaVersion: 2,
      status: 'frozen_report_origin_cohort',
      repository: 'aiskillstore/marketplace',
      selectedCount: 1,
      sourceBoundaries: [{
        runId: fixture.row.classificationRunId,
        classificationSha256: 'a'.repeat(64),
      }],
      rows: [{
        slug: fixture.row.slug,
        skillId: fixture.row.skillId,
        classificationRunId: fixture.row.classificationRunId,
        path: fixture.row.path,
        currentMarketplaceCommit: fixture.row.marketplaceCommit,
      }],
    };
    const manifest = materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort,
      expectedCount: 1,
      ...paths,
    });
    assert.equal(manifest.entries[0].originCommit, fixture.originCommit);
    assert.equal(manifest.entries[0].originParent, fixture.originParent);
    assert.equal(manifest.entries[0].classificationRunId, fixture.row.classificationRunId);
  } finally {
    rmSync(fixture.repositoryRoot, { recursive: true, force: true });
  }
});

test('fails closed without partial outputs when source changed after the report origin', () => {
  const fixture = makeRepository();
  try {
    write(fixture.repositoryRoot, `${SKILL_PATH}/SKILL.md`, '# Changed after report\n');
    fixture.row.marketplaceCommit = commit(fixture.repositoryRoot, 'source changed');
    const paths = outputs(fixture.repositoryRoot);
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...paths,
    }), /non-report source changed after the report-origin subject/);
    assert.equal(existsSync(paths.originRoot), false);
    assert.equal(existsSync(paths.previousReportRoot), false);
    assert.equal(existsSync(paths.manifestPath), false);
  } finally {
    rmSync(fixture.repositoryRoot, { recursive: true, force: true });
  }
});

test('fails closed without outputs when the legacy DFS tree cannot reproduce the report', () => {
  const fixture = makeRepository({ wrongTree: true });
  try {
    const paths = outputs(fixture.repositoryRoot);
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...paths,
    }), /report tree hash is not reproducible from report-origin evidence/);
    assert.equal(existsSync(paths.originRoot), false);
    assert.equal(existsSync(paths.previousReportRoot), false);
    assert.equal(existsSync(paths.manifestPath), false);
  } finally {
    rmSync(fixture.repositoryRoot, { recursive: true, force: true });
  }
});

test('rejects unproven cohorts, frozen identity drift, unsafe output overlap, and overwrites', () => {
  const fixture = makeRepository();
  try {
    const invalidStatus = cohortFor(fixture.row);
    invalidStatus.status = 'lineage_unproven';
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: invalidStatus,
      expectedCount: 1,
      ...outputs(fixture.repositoryRoot),
    }), /does not match the frozen report-origin contract/);

    const drifted = structuredClone(fixture.row);
    drifted.reportOriginCommit = fixture.originParent;
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(drifted),
      expectedCount: 1,
      ...outputs(fixture.repositoryRoot),
    }), /report-origin commit differs from the frozen lineage cohort/);

    const overlapping = outputs(fixture.repositoryRoot, '-overlap');
    overlapping.previousReportRoot = join(overlapping.originRoot, 'previous');
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...overlapping,
    }), /must be separate safe paths/);

    const occupied = outputs(fixture.repositoryRoot, '-occupied');
    write(occupied.originRoot, 'sentinel', 'keep\n');
    assert.throws(() => materializeLegacyReportOriginEvidence({
      repositoryRoot: fixture.repositoryRoot,
      cohort: cohortFor(fixture.row),
      expectedCount: 1,
      ...occupied,
    }), /origin source output root is not empty/);
  } finally {
    rmSync(fixture.repositoryRoot, { recursive: true, force: true });
  }
});
