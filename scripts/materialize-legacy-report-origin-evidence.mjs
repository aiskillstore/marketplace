#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const COMMIT_RE = /^[0-9a-f]{40}$/;
const OBJECT_ID_RE = /^[0-9a-f]{40,64}$/;
const SHA256_RE = /^[0-9a-f]{64}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const MAX_GIT_OUTPUT = 256 * 1024 * 1024;
const TREE_HASH_SCHEME = 'legacy_path_sha256_merkle_previous_report_v1';
const INPUT_RELATION = 'canonical_install_plus_previous_generated_report';
const SOURCE_SET_SCHEME = 'canonical_source_set_v1';
const SOURCE_SET_RELATION =
  'current_non_report_source_equals_report_origin_non_report_source_v1';

function fail(message) {
  throw new Error(message);
}

function sha256(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}

function git(repositoryRoot, args, encoding = 'utf8') {
  try {
    return execFileSync('git', ['-C', repositoryRoot, ...args], {
      encoding,
      maxBuffer: MAX_GIT_OUTPUT,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
  } catch (error) {
    const detail = error.stderr?.toString().trim() || error.message;
    fail(`Git evidence read failed (${args.join(' ')}): ${detail}`);
  }
}

function safeSkillPath(value) {
  if (typeof value !== 'string' || value !== value.trim()) {
    fail('cohort contains a non-canonical Skill path');
  }
  const segments = value.split('/');
  if (
    !value.startsWith('skills/')
    || value.startsWith('/')
    || value.includes('\\')
    || /[\u0000-\u001f\u007f,?#]/.test(value)
    || segments.length !== 3
    || segments.some((segment) => !segment || segment === '.' || segment === '..')
  ) {
    fail(`cohort contains an unsafe Skill path: ${value || '<empty>'}`);
  }
  return value;
}

function safeRelativePath(value, skillPath) {
  if (
    typeof value !== 'string'
    || !value
    || value.startsWith('/')
    || value.includes('\\')
    || /[\u0000-\u001f\u007f]/.test(value)
    || value.split('/').some((segment) => !segment || segment === '.' || segment === '..')
  ) {
    fail(`unsafe Git source path under ${skillPath}: ${value || '<empty>'}`);
  }
  return value;
}

function exactCommit(repositoryRoot, value, label) {
  if (typeof value !== 'string' || !COMMIT_RE.test(value)) {
    fail(`${label} is not an exact 40-character commit: ${value ?? '<missing>'}`);
  }
  const resolved = git(repositoryRoot, ['rev-parse', '--verify', `${value}^{commit}`]).trim();
  if (resolved !== value) fail(`${label} did not resolve exactly: ${value}`);
  return value;
}

function firstParent(repositoryRoot, commit) {
  const fields = git(repositoryRoot, ['rev-list', '--parents', '-n', '1', commit]).trim().split(' ');
  if (fields[0] !== commit || fields.length < 2 || fields.some((field) => !COMMIT_RE.test(field))) {
    fail(`commit has no valid first parent: ${commit}`);
  }
  return fields[1];
}

function parseTreeRecord(record, expectedPath, label) {
  const tab = record.indexOf('\t');
  const metadata = tab === -1 ? [] : record.slice(0, tab).split(' ');
  const treePath = tab === -1 ? '' : record.slice(tab + 1);
  const [mode, type, objectId] = metadata;
  if (
    treePath !== expectedPath
    || type !== 'blob'
    || !['100644', '100755'].includes(mode)
    || !OBJECT_ID_RE.test(objectId || '')
  ) {
    fail(`${label} is not an ordinary Git file: ${expectedPath}`);
  }
  return { mode, objectId };
}

function readTreeFile(repositoryRoot, commit, path, label, blobCache) {
  const output = git(repositoryRoot, [
    'ls-tree',
    '-z',
    '--full-tree',
    commit,
    '--',
    path,
  ], 'buffer');
  const records = output.toString('utf8').split('\0').filter(Boolean);
  if (records.length !== 1) {
    fail(`${label} must resolve to exactly one Git file: ${commit}:${path}`);
  }
  const { mode, objectId } = parseTreeRecord(records[0], path, label);
  let bytes = blobCache.get(objectId);
  if (!bytes) {
    bytes = git(repositoryRoot, ['cat-file', 'blob', objectId], 'buffer');
    blobCache.set(objectId, bytes);
  }
  return { mode, gitBlob: objectId, sha256: sha256(bytes), bytes };
}

function findReportOrigin(repositoryRoot, currentCommit, reportPath) {
  const commits = git(repositoryRoot, [
    'log',
    '--first-parent',
    '--format=%H',
    currentCommit,
    '--',
    reportPath,
  ]).trim().split('\n').filter(Boolean);
  if (commits.length === 0 || commits.some((commit) => !COMMIT_RE.test(commit))) {
    fail(`current report has no valid first-parent origin: ${currentCommit}:${reportPath}`);
  }
  return commits[0];
}

function readSourceSet(repositoryRoot, commit, skillPath, blobCache) {
  const prefix = `${skillPath}/`;
  const reportPath = `${skillPath}/skill-report.json`;
  const output = git(repositoryRoot, [
    'ls-tree',
    '-r',
    '-z',
    '--full-tree',
    commit,
    '--',
    `${skillPath}/`,
  ], 'buffer');
  const records = output.toString('utf8').split('\0').filter(Boolean);
  const entries = [];
  const seen = new Set();
  for (const record of records) {
    const tab = record.indexOf('\t');
    const treePath = tab === -1 ? '' : record.slice(tab + 1);
    if (!treePath.startsWith(prefix)) fail(`Git returned a source path outside ${skillPath}`);
    if (treePath === reportPath) continue;
    const { mode, objectId } = parseTreeRecord(record, treePath, 'non-report source');
    const path = safeRelativePath(treePath.slice(prefix.length), skillPath);
    if (seen.has(path)) fail(`duplicate non-report source path under ${skillPath}: ${path}`);
    seen.add(path);
    let bytes = blobCache.get(objectId);
    if (!bytes) {
      bytes = git(repositoryRoot, ['cat-file', 'blob', objectId], 'buffer');
      blobCache.set(objectId, bytes);
    }
    entries.push({ path, mode, gitBlob: objectId, sha256: sha256(bytes) });
  }
  // This evidence is a new cross-platform contract. Unlike the historical
  // tree walker below, it must not depend on the runner's ICU/default locale.
  entries.sort((left, right) => Buffer.compare(
    Buffer.from(left.path, 'utf8'),
    Buffer.from(right.path, 'utf8'),
  ));
  if (entries.length === 0 || !entries.some((entry) => entry.path === 'SKILL.md')) {
    fail(`non-report source at ${commit}:${skillPath} has no ordinary SKILL.md`);
  }
  const canonicalJson = JSON.stringify(entries);
  return {
    sha256: sha256(canonicalJson),
    entryCount: entries.length,
    entries,
    canonicalJson,
  };
}

function buildLegacyDfsInput(sourceEntries, previousReportSha256, skillPath) {
  const root = { type: 'directory', children: new Map() };
  const inputs = sourceEntries.map((entry) => ({ path: entry.path, sha256: entry.sha256 }));
  inputs.push({ path: 'skill-report.json', sha256: previousReportSha256 });

  for (const input of inputs) {
    const parts = input.path.split('/');
    let directory = root;
    for (let index = 0; index < parts.length; index++) {
      const name = parts[index];
      const isFile = index === parts.length - 1;
      const existing = directory.children.get(name);
      if (isFile) {
        if (existing) fail(`legacy DFS input has a path collision under ${skillPath}: ${input.path}`);
        directory.children.set(name, { type: 'file', sha256: input.sha256 });
      } else {
        if (existing?.type === 'file') {
          fail(`legacy DFS input has a file/directory collision under ${skillPath}: ${input.path}`);
        }
        if (!existing) {
          directory.children.set(name, { type: 'directory', children: new Map() });
        }
        directory = directory.children.get(name);
      }
    }
  }

  const entries = [];
  function walk(directory, prefix = '') {
    const children = [...directory.children.entries()]
      .sort(([left], [right]) => left.localeCompare(right));
    for (const [name, child] of children) {
      const path = prefix ? `${prefix}/${name}` : name;
      if (child.type === 'directory') walk(child, path);
      else entries.push(`${path}:${child.sha256}`);
    }
  }
  walk(root);
  const serialized = entries.length === 0 ? 'empty' : entries.join('\n');
  return { entries, serializedSha256: sha256(serialized), treeHash: sha256(serialized) };
}

function normalizeLegacySkillMdContent(content) {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (!frontmatterMatch) return content.trim();
  const body = content.slice(frontmatterMatch[0].length);
  const normalizedFrontmatter = frontmatterMatch[1]
    .split('\n')
    .filter((line) => !line.trim().startsWith('version:'))
    .join('\n');
  return `---\n${normalizedFrontmatter}\n---${body}`.trim();
}

function contentRelation(reportContentHash, skillBytes) {
  if (sha256(skillBytes) === reportContentHash) return 'canonical';
  const legacy = sha256(normalizeLegacySkillMdContent(skillBytes.toString('utf8')));
  if (legacy === reportContentHash) return 'legacy_strip_version_trim';
  return 'unknown';
}

function requireString(value, label, pattern) {
  if (typeof value !== 'string' || !pattern.test(value)) fail(`${label} is invalid`);
  return value;
}

function assertExpected(actual, expected, label) {
  if (actual !== expected) fail(`${label} differs from the frozen lineage cohort`);
}

function validateCohort(cohort, expectedCount, repositoryRoot) {
  const frozenIdentityOnly = cohort?.schemaVersion === 2
    && cohort?.status === 'frozen_report_origin_cohort';
  const sourceBoundaries = frozenIdentityOnly && Array.isArray(cohort?.sourceBoundaries)
    ? new Map(cohort.sourceBoundaries.map((boundary) => [
        boundary?.runId,
        boundary?.classificationSha256,
      ]))
    : null;
  if (
    !cohort
    || (!frozenIdentityOnly && (
      cohort.schemaVersion !== 1 || cohort.status !== 'lineage_recovered'
    ))
    || cohort.repository !== 'aiskillstore/marketplace'
    || !Array.isArray(cohort.rows)
    || !Number.isSafeInteger(frozenIdentityOnly ? cohort.selectedCount : cohort.count)
    || (frozenIdentityOnly ? cohort.selectedCount : cohort.count) !== cohort.rows.length
    || cohort.rows.length !== expectedCount
    || (frozenIdentityOnly && (
      JSON.stringify(Object.keys(cohort)) !== JSON.stringify([
        'schemaVersion', 'status', 'repository', 'selectedCount', 'sourceBoundaries', 'rows',
      ])
      || sourceBoundaries?.size !== cohort.sourceBoundaries.length
      || cohort.sourceBoundaries.length < 1
      || cohort.sourceBoundaries.some((boundary) => (
        !isFinite(Number(boundary?.runId))
        || !/^\d+$/.test(boundary?.runId || '')
        || !SHA256_RE.test(boundary?.classificationSha256 || '')
        || JSON.stringify(Object.keys(boundary || {}))
          !== JSON.stringify(['runId', 'classificationSha256'])
      ))
    ))
    || (!frozenIdentityOnly && (
      cohort.method?.reportOrigin !== 'last first-parent commit changing the same-path skill-report.json'
      || cohort.method?.treeHashScheme !== TREE_HASH_SCHEME
      || cohort.method?.inputRelation !== INPUT_RELATION
      || cohort.method?.sourceSetIdentity
        !== 'canonical JSON of sorted non-report path, mode, git blob, sha256 entries'
    ))
  ) {
    fail('lineage cohort does not match the frozen report-origin contract');
  }

  const slugs = new Set();
  const paths = new Set();
  for (const row of cohort.rows) {
    const slug = row?.slug;
    const path = safeSkillPath(row?.path);
    if (
      typeof slug !== 'string'
      || !slug
      || slug !== slug.trim()
      || /[\u0000-\u001f\u007f,\s]/.test(slug)
      || slugs.has(slug)
    ) {
      fail(`cohort contains an invalid or duplicate slug: ${slug ?? '<missing>'}`);
    }
    if (paths.has(path)) fail(`cohort contains a duplicate Skill path: ${path}`);
    slugs.add(slug);
    paths.add(path);
    requireString(row.skillId, `${slug} skill ID`, UUID_RE);
    requireString(row.classificationRunId, `${slug} classification run ID`, /^\d+$/);
    if (frozenIdentityOnly && !sourceBoundaries.has(row.classificationRunId)) {
      fail(`${slug} classification run is not in the frozen source boundaries`);
    }
    const currentCommit = frozenIdentityOnly ? row.currentMarketplaceCommit : row.marketplaceCommit;
    exactCommit(repositoryRoot, currentCommit, `${slug} Marketplace commit`);
    if (frozenIdentityOnly) {
      const expectedKeys = [
        'slug', 'skillId', 'classificationRunId', 'path', 'currentMarketplaceCommit',
      ];
      if (JSON.stringify(Object.keys(row)) !== JSON.stringify(expectedKeys)) {
        fail(`${slug} frozen cohort identity has unexpected fields`);
      }
      continue;
    }
    for (const [label, value] of [
      ['current report SHA-256', row.currentReportSha256],
      ['previous report SHA-256', row.previousReportSha256],
      ['report content hash', row.reportContentHash],
      ['report tree hash', row.reportTreeHash],
      ['origin calculated tree hash', row.originCalculatedTreeHash],
      ['origin tree input SHA-256', row.originTreeInputSha256],
      ['current source-set SHA-256', row.sourceSetEquality?.currentSha256],
      ['origin source-set SHA-256', row.sourceSetEquality?.originSha256],
    ]) requireString(value, `${slug} ${label}`, SHA256_RE);
    requireString(row.currentReportGitBlob, `${slug} current report Git blob`, OBJECT_ID_RE);
    requireString(row.previousReportGitBlob, `${slug} previous report Git blob`, OBJECT_ID_RE);
    requireString(row.reportOriginCommit, `${slug} report-origin commit`, COMMIT_RE);
    requireString(row.reportOriginParent, `${slug} report-origin parent`, COMMIT_RE);
    if (
      row.treeHashScheme !== TREE_HASH_SCHEME
      || row.inputRelation !== INPUT_RELATION
      || row.lineageClassification !== 'legacy_previous_report_tree_equivalent'
      || row.governanceEligibleByLineage !== true
      || row.sourceSetEquality?.equal !== true
      || !Number.isSafeInteger(row.sourceSetEquality.currentEntryCount)
      || row.sourceSetEquality.currentEntryCount < 1
      || row.sourceSetEquality.currentEntryCount !== row.sourceSetEquality.originEntryCount
      || !Number.isSafeInteger(row.originTreeEntryCount)
      || row.originTreeEntryCount !== row.sourceSetEquality.originEntryCount + 1
      || !['canonical', 'legacy_strip_version_trim'].includes(row.currentContentRelation)
      || !['canonical', 'legacy_strip_version_trim'].includes(row.originContentRelation)
    ) {
      fail(`${slug} is not independently eligible for report-origin governance`);
    }
  }
  return { frozenIdentityOnly };
}

function safeOutputPath(outputRoot, currentCommit, repositoryPath) {
  const relative = `${currentCommit}/${repositoryPath}`;
  const target = resolve(outputRoot, ...relative.split('/'));
  if (!target.startsWith(`${outputRoot}${sep}`)) fail(`refusing output path outside root: ${relative}`);
  return { relative, target };
}

function assertUnusedOutput(originRoot, previousReportRoot, manifestPath) {
  if (existsSync(manifestPath)) fail(`manifest output already exists: ${manifestPath}`);
  for (const [label, outputRoot] of [
    ['origin source', originRoot],
    ['previous-report', previousReportRoot],
  ]) {
    if (existsSync(outputRoot) && readdirSync(outputRoot).length > 0) {
      fail(`${label} output root is not empty: ${outputRoot}`);
    }
  }
}

export function materializeLegacyReportOriginEvidence({
  repositoryRoot,
  cohort,
  expectedCount,
  originRoot,
  previousReportRoot,
  manifestPath,
}) {
  const root = resolve(repositoryRoot);
  const originDestination = resolve(originRoot);
  const previousReportDestination = resolve(previousReportRoot);
  const manifest = resolve(manifestPath);
  if (!Number.isSafeInteger(expectedCount) || expectedCount < 1) fail('expected count must be positive');
  const unsafeRoot = [originDestination, previousReportDestination].some((destination) => (
    destination === resolve('/')
    || manifest === destination
    || manifest.startsWith(`${destination}${sep}`)
  ));
  if (
    unsafeRoot
    || originDestination === previousReportDestination
    || originDestination.startsWith(`${previousReportDestination}${sep}`)
    || previousReportDestination.startsWith(`${originDestination}${sep}`)
  ) {
    fail('origin, previous-report, and manifest outputs must be separate safe paths');
  }
  assertUnusedOutput(originDestination, previousReportDestination, manifest);
  const { frozenIdentityOnly } = validateCohort(cohort, expectedCount, root);

  // Read, recompute, and validate the entire cohort before creating any output.
  const blobCache = new Map();
  const pending = [];
  for (const row of cohort.rows) {
    const currentCommit = frozenIdentityOnly ? row.currentMarketplaceCommit : row.marketplaceCommit;
    const skillPath = row.path;
    const reportPath = `${skillPath}/skill-report.json`;
    const currentReport = readTreeFile(root, currentCommit, reportPath, 'current report', blobCache);
    const reportOriginCommit = findReportOrigin(root, currentCommit, reportPath);
    const reportOriginParent = firstParent(root, reportOriginCommit);
    const originReport = readTreeFile(
      root,
      reportOriginCommit,
      reportPath,
      'report at its first-parent origin',
      blobCache,
    );
    const previousReport = readTreeFile(
      root,
      reportOriginParent,
      reportPath,
      'previous report at report-origin first parent',
      blobCache,
    );
    if (
      currentReport.gitBlob !== originReport.gitBlob
      || currentReport.sha256 !== originReport.sha256
      || !currentReport.bytes.equals(originReport.bytes)
    ) {
      fail(`${row.slug} current report bytes do not equal the report-origin subject`);
    }

    let report;
    try {
      report = JSON.parse(currentReport.bytes.toString('utf8'));
    } catch (error) {
      fail(`${row.slug} current report is not valid JSON: ${error.message}`);
    }
    const reportContentHash = requireString(
      report?.meta?.content_hash,
      `${row.slug} current report content hash`,
      SHA256_RE,
    );
    const reportTreeHash = requireString(
      report?.meta?.tree_hash,
      `${row.slug} current report tree hash`,
      SHA256_RE,
    );
    if (report?.meta?.slug !== row.slug) fail(`${row.slug} current report slug differs from cohort`);

    const currentSourceSet = readSourceSet(root, currentCommit, skillPath, blobCache);
    const originSourceSet = readSourceSet(root, reportOriginCommit, skillPath, blobCache);
    if (currentSourceSet.canonicalJson !== originSourceSet.canonicalJson) {
      fail(`${row.slug} non-report source changed after the report-origin subject`);
    }
    const currentSkill = currentSourceSet.entries.find((entry) => entry.path === 'SKILL.md');
    const originSkill = originSourceSet.entries.find((entry) => entry.path === 'SKILL.md');
    const currentContentRelation = contentRelation(
      reportContentHash,
      blobCache.get(currentSkill.gitBlob),
    );
    const originContentRelation = contentRelation(
      reportContentHash,
      blobCache.get(originSkill.gitBlob),
    );
    if (currentContentRelation === 'unknown' || originContentRelation === 'unknown') {
      fail(`${row.slug} report content hash is not reproducible from equal source bytes`);
    }

    const legacyTree = buildLegacyDfsInput(
      originSourceSet.entries,
      previousReport.sha256,
      skillPath,
    );
    if (legacyTree.treeHash !== reportTreeHash) {
      fail(`${row.slug} report tree hash is not reproducible from report-origin evidence`);
    }

    const expected = frozenIdentityOnly ? [] : [
      [currentReport.gitBlob, row.currentReportGitBlob, 'current report Git blob'],
      [currentReport.sha256, row.currentReportSha256, 'current report SHA-256'],
      [previousReport.gitBlob, row.previousReportGitBlob, 'previous report Git blob'],
      [previousReport.sha256, row.previousReportSha256, 'previous report SHA-256'],
      [reportOriginCommit, row.reportOriginCommit, 'report-origin commit'],
      [reportOriginParent, row.reportOriginParent, 'report-origin first parent'],
      [reportContentHash, row.reportContentHash, 'report content hash'],
      [reportTreeHash, row.reportTreeHash, 'report tree hash'],
      [legacyTree.treeHash, row.originCalculatedTreeHash, 'origin calculated tree hash'],
      [legacyTree.serializedSha256, row.originTreeInputSha256, 'origin tree input SHA-256'],
      [legacyTree.entries.length, row.originTreeEntryCount, 'origin tree entry count'],
      [currentSourceSet.entryCount, row.sourceSetEquality.currentEntryCount, 'current source count'],
      [originSourceSet.entryCount, row.sourceSetEquality.originEntryCount, 'origin source count'],
      [currentContentRelation, row.currentContentRelation, 'current content relation'],
      [originContentRelation, row.originContentRelation, 'origin content relation'],
    ];
    for (const [actual, frozen, label] of expected) {
      assertExpected(actual, frozen, `${row.slug} ${label}`);
    }

    const previousReportOutput = safeOutputPath(
      previousReportDestination,
      currentCommit,
      `${skillPath}/skill-report.json`,
    );
    const originFiles = originSourceSet.entries.map((source) => {
      const output = safeOutputPath(
        originDestination,
        currentCommit,
        `${skillPath}/${source.path}`,
      );
      return {
        ...source,
        relativePath: output.relative,
        outputPath: output.target,
        bytes: blobCache.get(source.gitBlob),
      };
    });
    pending.push({
      slug: row.slug,
      skillId: row.skillId,
      classificationRunId: row.classificationRunId,
      path: skillPath,
      currentMarketplaceCommit: currentCommit,
      currentReport: {
        gitBlob: currentReport.gitBlob,
        sha256: currentReport.sha256,
        contentHash: reportContentHash,
        contentRelation: currentContentRelation,
        treeHash: reportTreeHash,
      },
      originCommit: reportOriginCommit,
      originParent: reportOriginParent,
      originReport: {
        gitBlob: originReport.gitBlob,
        sha256: originReport.sha256,
        contentRelation: originContentRelation,
      },
      previousReport: {
        gitBlob: previousReport.gitBlob,
        sha256: previousReport.sha256,
        relativePath: previousReportOutput.relative,
      },
      sourceSetEvidence: {
        scheme: SOURCE_SET_SCHEME,
        relation: SOURCE_SET_RELATION,
        equal: true,
        current: {
          sha256: currentSourceSet.sha256,
          entryCount: currentSourceSet.entryCount,
          entries: currentSourceSet.entries,
        },
        origin: {
          sha256: originSourceSet.sha256,
          entryCount: originSourceSet.entryCount,
          entries: originSourceSet.entries,
        },
      },
      legacyTreeEvidence: {
        treeHashScheme: TREE_HASH_SCHEME,
        inputRelation: INPUT_RELATION,
        entryCount: legacyTree.entries.length,
        entries: legacyTree.entries,
        inputSha256: legacyTree.serializedSha256,
        calculatedTreeHash: legacyTree.treeHash,
        matchesCurrentReport: true,
      },
      governanceEligible: true,
      previousReportBytes: previousReport.bytes,
      previousReportOutputPath: previousReportOutput.target,
      originFiles,
    });
  }
  pending.sort((left, right) => left.path.localeCompare(right.path));

  mkdirSync(originDestination, { recursive: true });
  mkdirSync(previousReportDestination, { recursive: true });
  for (const entry of pending) {
    for (const source of entry.originFiles) {
      mkdirSync(dirname(source.outputPath), { recursive: true });
      writeFileSync(source.outputPath, source.bytes, {
        flag: 'wx',
        mode: source.mode === '100755' ? 0o700 : 0o600,
      });
    }
    mkdirSync(dirname(entry.previousReportOutputPath), { recursive: true });
    writeFileSync(entry.previousReportOutputPath, entry.previousReportBytes, {
      flag: 'wx',
      mode: 0o600,
    });
  }
  const output = {
    schemaVersion: 1,
    status: 'legacy_report_origin_evidence_materialized',
    selectedCount: pending.length,
    treeHashScheme: TREE_HASH_SCHEME,
    inputRelation: INPUT_RELATION,
    sourceSetScheme: SOURCE_SET_SCHEME,
    sourceSetRelation: SOURCE_SET_RELATION,
    entries: pending.map(({
      previousReportBytes: _bytes,
      previousReportOutputPath: _previousPath,
      originFiles,
      ...entry
    }) => ({
      ...entry,
      originFiles: originFiles.map(({ bytes: _fileBytes, outputPath: _filePath, ...source }) => source),
    })),
  };
  mkdirSync(dirname(manifest), { recursive: true });
  writeFileSync(manifest, `${JSON.stringify(output, null, 2)}\n`, { flag: 'wx', mode: 0o600 });
  return output;
}

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null || value.startsWith('--')) {
      fail(`invalid argument: ${key || '<missing>'}`);
    }
    const name = key.slice(2);
    if (Object.hasOwn(values, name)) fail(`duplicate argument: ${key}`);
    values[name] = value;
  }
  return values;
}

export function main(argv = process.argv.slice(2)) {
  const args = parseArgs(argv);
  for (const name of ['cohort', 'expected-count', 'origin-root', 'previous-report-root', 'manifest']) {
    if (!args[name]) fail(`--${name} is required`);
  }
  if (!/^\d+$/.test(args['expected-count'])) fail('--expected-count must be a positive integer');
  const output = materializeLegacyReportOriginEvidence({
    repositoryRoot: args['repository-root'] || process.cwd(),
    cohort: JSON.parse(readFileSync(resolve(args.cohort), 'utf8')),
    expectedCount: Number(args['expected-count']),
    originRoot: args['origin-root'],
    previousReportRoot: args['previous-report-root'],
    manifestPath: args.manifest,
  });
  process.stdout.write(`${JSON.stringify({ status: output.status, selectedCount: output.selectedCount })}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    main();
  } catch (error) {
    process.stderr.write(`legacy report-origin evidence materialization failed: ${error.message}\n`);
    process.exitCode = 1;
  }
}
