#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import {
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { resolveApprovedSubmission } from './resolve-approved-submission.mjs';
import {
  parseCanonicalShardIndex,
  readAndValidateSubmissionShardManifest,
} from './submission-shard-contract.mjs';
import { validateSelectionPlan } from './submission-selection-plan.mjs';

function fail(message) {
  throw new Error(message);
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index === -1) fail(`missing required option ${name}`);
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

function parseMatrix(json, expectedCount) {
  let matrix;
  try {
    matrix = JSON.parse(json);
  } catch (error) {
    fail(`matrix is not valid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!matrix || typeof matrix !== 'object' || !Array.isArray(matrix.include)) fail('matrix.include must be an array');
  if (matrix.include.length !== expectedCount) {
    fail(`matrix contains ${matrix.include.length} shard(s), expected ${expectedCount}`);
  }
  const entries = new Map();
  // The union of these immutable shard subplans is the frozen full submission
  // plan; callers deliberately do not pass a separate mutable full-plan file.
  let identity = null;
  const slugs = new Set();
  const paths = new Set();
  const foldedPaths = new Set();
  for (const [position, entry] of matrix.include.entries()) {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)
      || JSON.stringify(Object.keys(entry).sort()) !== JSON.stringify(['selection_plan', 'shard'])) {
      fail(`matrix entry ${position} must contain only shard and selection_plan`);
    }
    if (typeof entry.shard !== 'number') fail(`matrix entry ${position} shard must be a canonical JSON integer`);
    const shard = parseCanonicalShardIndex(entry.shard, `matrix entry ${position} shard`);
    if (entries.has(shard)) fail(`matrix contains duplicate canonical shard index ${shard}`);
    const plan = validateSelectionPlan(entry.selection_plan);
    const planIdentity = JSON.stringify({ repository: plan.repository, sourceCommit: plan.sourceCommit, scope: plan.scope });
    if (identity !== null && identity !== planIdentity) fail(`matrix shard ${shard} selection plan identity does not match other shards`);
    identity = planIdentity;
    for (const skill of plan.skills) {
      if (slugs.has(skill.slug)) fail(`matrix selection plans contain duplicate slug ${skill.slug}`);
      if (paths.has(skill.path)) fail(`matrix selection plans contain duplicate path ${skill.path}`);
      const foldedPath = skill.path.normalize('NFC').toLocaleLowerCase('en-US');
      if (foldedPaths.has(foldedPath)) fail(`matrix selection plans contain NFC/case-fold path collision ${skill.path}`);
      slugs.add(skill.slug);
      paths.add(skill.path);
      foldedPaths.add(foldedPath);
    }
    entries.set(shard, plan);
  }
  return entries;
}

function readArchiveSelectionPlan(root, expectedPlan, shardIndex) {
  const expectedPath = join(root, 'selection-plan.json');
  if (!existsSync(expectedPath)) fail(`shard ${shardIndex} archive is missing root selection-plan.json`);
  const evidenceStat = lstatSync(expectedPath);
  if (evidenceStat.isSymbolicLink() || !evidenceStat.isFile()) {
    fail(`shard ${shardIndex} archive root selection-plan.json must be a regular file`);
  }
  let plan;
  try {
    plan = JSON.parse(readFileSync(expectedPath, 'utf8'));
  } catch (error) {
    fail(`shard ${shardIndex} archive selection plan is invalid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
  const normalized = validateSelectionPlan(plan);
  if (JSON.stringify(normalized) !== JSON.stringify(expectedPlan)) {
    fail(`shard ${shardIndex} archive selection plan does not match matrix selection plan`);
  }
  return normalized;
}

function collectFiles(root, predicate) {
  const files = [];
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) fail(`artifact tree contains symlink ${path}`);
      if (entry.isDirectory()) walk(path);
      else if (entry.isFile() && predicate(path)) files.push(path);
    }
  }
  walk(root);
  return files;
}

function collectArchives(artifactsDir, runAttempt) {
  const prefix = `process-shard-${runAttempt}-`;
  return collectFiles(artifactsDir, (path) => {
    const name = basename(path);
    return name.startsWith(prefix) && name.endsWith('.tar.gz');
  }).sort();
}

function parseArchiveIndex(path, runAttempt) {
  const name = basename(path);
  const prefix = `process-shard-${runAttempt}-`;
  if (!name.startsWith(prefix) || !name.endsWith('.tar.gz')) fail(`unexpected shard archive name ${name}`);
  const raw = name.slice(prefix.length, -'.tar.gz'.length);
  return parseCanonicalShardIndex(raw, `archive index in ${name}`);
}

function assertSameIntegerSet(actual, expected, label) {
  const left = [...actual].sort((a, b) => a - b);
  const right = [...expected].sort((a, b) => a - b);
  if (JSON.stringify(left) !== JSON.stringify(right)) {
    fail(`${label}: expected [${right.join(',')}], found [${left.join(',')}]`);
  }
}

let tarSupportsEscapeQuoting;

function tarListingArgs(archive) {
  if (tarSupportsEscapeQuoting === undefined) {
    const help = spawnSync('tar', ['--help'], { encoding: 'utf8' });
    tarSupportsEscapeQuoting = help.status === 0 && help.stdout.includes('--quoting-style');
  }
  return tarSupportsEscapeQuoting
    ? ['--quoting-style=escape', '-tzf', archive]
    : ['-tzf', archive];
}

function validateTarEntries(archive) {
  const listed = spawnSync('tar', tarListingArgs(archive), {
    encoding: 'utf8',
    env: { ...process.env, LANG: 'C.UTF-8', LC_ALL: 'C.UTF-8' },
  });
  if (listed.status !== 0) fail(`cannot list ${basename(archive)}: ${listed.stderr.trim()}`);
  const entries = listed.stdout.split(/\r?\n/).filter(Boolean);
  if (entries.length === 0) fail(`${basename(archive)} is empty`);
  for (const entry of entries) {
    const normalized = entry.startsWith('./') ? entry.slice(2) : entry;
    if (
      normalized.startsWith('/')
      || normalized.includes('\\')
      || normalized.split('/').some((segment) => segment === '..')
    ) {
      fail(`${basename(archive)} contains unsafe path ${JSON.stringify(entry)}`);
    }
  }
}

function extractArchive(archive) {
  validateTarEntries(archive);
  const root = `${archive}.extracted`;
  rmSync(root, { recursive: true, force: true });
  mkdirSync(root, { recursive: true });
  const extracted = spawnSync('tar', ['-xzf', archive, '-C', root], { encoding: 'utf8' });
  if (extracted.status !== 0) fail(`cannot extract ${basename(archive)}: ${extracted.stderr.trim()}`);
  collectFiles(root, () => false);
  return root;
}

function relativePendingFiles(root) {
  const pending = join(root, 'pending');
  if (!existsSync(pending) || !lstatSync(pending).isDirectory()) fail('archive is missing pending/ directory');
  return collectFiles(pending, () => true)
    .map((path) => relative(root, path).split(sep).join('/'))
    .sort();
}

function assertSameStringSet(actual, expected, label) {
  const left = [...actual].sort((a, b) => a.localeCompare(b, 'en'));
  const right = [...expected].sort((a, b) => a.localeCompare(b, 'en'));
  if (JSON.stringify(left) !== JSON.stringify(right)) {
    fail(`${label}: expected ${JSON.stringify(right)}, got ${JSON.stringify(left)}`);
  }
}

function ensureInside(root, path, label) {
  const relativePath = relative(root, path);
  if (relativePath === '..' || relativePath.startsWith(`..${sep}`)) fail(`${label} escapes output root`);
}

function writeJson(path, value) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
}

function aggregate(config) {
  if (!existsSync(config.artifactsDir)) fail(`artifacts directory does not exist: ${config.artifactsDir}`);
  const expectedCount = Number(config.expectedCount);
  if (!Number.isSafeInteger(expectedCount) || expectedCount < 1) fail('--expected-count must be a positive integer');
  const runAttempt = parseCanonicalShardIndex(config.runAttempt, 'run attempt');
  const matrix = parseMatrix(config.matrixJson, expectedCount);
  const archives = collectArchives(config.artifactsDir, runAttempt);
  const byIndex = new Map();
  for (const archive of archives) {
    const index = parseArchiveIndex(archive, runAttempt);
    if (byIndex.has(index)) fail(`duplicate canonical shard archive index ${index}`);
    byIndex.set(index, archive);
  }
  assertSameIntegerSet(byIndex.keys(), matrix.keys(), 'found shard index set must equal expected matrix index set');

  const shards = [];
  const skills = [];
  for (const index of [...matrix.keys()].sort((a, b) => a - b)) {
    const archive = byIndex.get(index);
    const root = extractArchive(archive);
    const pendingRoot = join(root, 'pending');
    const manifestPath = join(root, 'shard-manifest.json');
    const expectedPlan = matrix.get(index);
    readArchiveSelectionPlan(root, expectedPlan, index);
    const manifest = readAndValidateSubmissionShardManifest(manifestPath, {
      expectedIndex: index,
      expectedPlanned: expectedPlan.skills.map(({ slug }) => slug),
      expectedSelectionPlan: expectedPlan,
      pendingRoot,
      requireSuccess: true,
    });

    let shardSkills = [];
    if (manifest.reasonCode === 'processed_all_planned') {
      const changedFiles = relativePendingFiles(root);
      const plan = resolveApprovedSubmission({
        repositoryRoot: root,
        changedFiles,
      });
      shardSkills = plan.skills;
      assertSameStringSet(
        shardSkills.map(({ pendingDir }) => basename(pendingDir)),
        manifest.succeeded,
        `shard ${index} resolved plan does not match manifest succeeded slugs`,
      );
    } else if (manifest.reasonCode !== 'no_skills_planned') {
      fail(`shard ${index} has unsupported successful reasonCode ${manifest.reasonCode}`);
    }
    shards.push({ index, manifest, root, skills: shardSkills });
    skills.push(...shardSkills);
  }

  const uniqueFields = ['pendingDir', 'targetDir', 'reportSlug'];
  for (const field of uniqueFields) {
    const values = skills.map((skill) => skill[field]);
    if (new Set(values).size !== values.length) fail(`duplicate ${field} across submission shards`);
  }

  rmSync(config.mergedResults, { recursive: true, force: true });
  mkdirSync(config.mergedResults, { recursive: true });
  for (const shard of shards) {
    for (const skill of shard.skills) {
      const source = resolve(shard.root, ...skill.pendingDir.split('/'));
      const destination = resolve(config.mergedResults, ...skill.pendingDir.split('/'));
      ensureInside(config.mergedResults, destination, skill.pendingDir);
      if (existsSync(destination)) fail(`duplicate pending path across shards: ${skill.pendingDir}`);
      mkdirSync(dirname(destination), { recursive: true });
      cpSync(source, destination, { recursive: true, errorOnExist: true });
    }
  }

  const plan = { schemaVersion: 1, skills: skills.sort((left, right) => left.pendingDir.localeCompare(right.pendingDir, 'en')) };
  writeJson(config.approvalPlan, plan);
  const shardIndices = [...matrix.keys()].sort((a, b) => a - b);
  if (skills.length === 0) {
    if (!shards.every(({ manifest }) => manifest.reasonCode === 'no_skills_planned')) {
      fail('empty aggregate is only legal when every shard explicitly reports no_skills_planned');
    }
    writeJson(config.summary, {
      schemaVersion: 1,
      status: 'no_op',
      reasonCode: 'no_skills_planned',
      shardIndices,
    });
  } else {
    writeJson(config.summary, {
      schemaVersion: 1,
      status: 'has_results',
      reasonCode: 'processed_all_planned',
      shardIndices,
      processedCount: skills.length,
    });
  }
}

function main() {
  const args = process.argv.slice(2);
  const config = {
    artifactsDir: option(args, '--artifacts-dir'),
    runAttempt: option(args, '--run-attempt'),
    matrixJson: option(args, '--matrix-json'),
    expectedCount: option(args, '--expected-count'),
    approvalPlan: option(args, '--approval-plan'),
    mergedResults: option(args, '--merged-results'),
    summary: option(args, '--summary'),
  };
  aggregate(config);
  const summary = JSON.parse(readFileSync(config.summary, 'utf8'));
  process.stdout.write(`Aggregated shards: ${summary.status} (${summary.reasonCode})\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Submission shard aggregation failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
