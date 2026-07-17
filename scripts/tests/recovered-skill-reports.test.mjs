import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import test from 'node:test';
import {
  CANONICAL_CONTENT_HASH_SCHEME,
  CANONICAL_TREE_HASH_SCHEME,
  RECOVERED_SKILL_REPORTS,
  calculateCanonicalSkillHashes,
  verifyRecoveredSkillReport,
  verifyRecoveredSkillReports,
} from '../verify-recovered-skill-reports.mjs';

const REPOSITORY_ROOT = resolve(import.meta.dirname, '../..');

test('ten recovered reports match canonical slugs, source URLs, paths, and exact bytes', () => {
  const results = verifyRecoveredSkillReports(REPOSITORY_ROOT);
  assert.equal(results.length, 10);
  assert.equal(new Set(results.map((row) => row.slug)).size, 10);
  assert.equal(new Set(results.map((row) => row.contentHash)).size, 10);
  assert.equal(new Set(results.map((row) => row.treeHash)).size, 10);
  assert.deepEqual(new Set(results.map((row) => row.contentHashScheme)), new Set([
    CANONICAL_CONTENT_HASH_SCHEME,
  ]));
  assert.deepEqual(new Set(results.map((row) => row.treeHashScheme)), new Set([
    CANONICAL_TREE_HASH_SCHEME,
  ]));
  assert.deepEqual(
    results.map((row) => row.slug),
    RECOVERED_SKILL_REPORTS.map((target) => target.slug),
  );
});

test('verification fails closed when report identity drifts from canonical bytes', () => {
  const repositoryRoot = mkdtempSync(join(tmpdir(), 'recovered-skill-report-'));
  const target = {
    path: 'skills/example/demo',
    slug: 'example-demo',
    sourceUrl: 'https://github.com/example/skills/tree/main/demo/',
  };
  const skillDirectory = join(repositoryRoot, target.path);
  const skillPath = join(skillDirectory, 'SKILL.md');
  const reportPath = join(skillDirectory, 'skill-report.json');
  try {
    mkdirSync(dirname(skillPath), { recursive: true });
    writeFileSync(skillPath, '---\nname: demo\ndescription: Demo\n---\n\n# Demo\n');
    const canonical = calculateCanonicalSkillHashes(skillDirectory);
    writeFileSync(reportPath, JSON.stringify({
      schema_version: '2.0',
      meta: {
        slug: target.slug,
        source_url: target.sourceUrl,
        source_ref: 'main',
        source_type: 'community',
        content_hash: canonical.contentHash,
        tree_hash: canonical.treeHash,
      },
      file_structure: [{ name: 'SKILL.md', type: 'file', path: 'SKILL.md', lines: 7 }],
      security_audit: { analysis_status: 'ok' },
    }, null, 2));
    assert.equal(verifyRecoveredSkillReport(repositoryRoot, target).slug, target.slug);

    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    report.meta.content_hash = '0'.repeat(64);
    writeFileSync(reportPath, JSON.stringify(report, null, 2));
    assert.throws(
      () => verifyRecoveredSkillReport(repositoryRoot, target),
      /content_hash does not match exact SKILL\.md bytes/,
    );
  } finally {
    rmSync(repositoryRoot, { recursive: true, force: true });
  }
});
