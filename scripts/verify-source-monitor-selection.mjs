#!/usr/bin/env node

import {
  existsSync,
  lstatSync,
  readFileSync,
  readdirSync,
  realpathSync,
} from 'node:fs';
import { dirname, posix, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
const COMMIT_RE = /^[a-f0-9]{40}$/;

function fail(message) {
  throw new Error(message);
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
    fail(`missing required option ${name}`);
  }
  return args[index + 1];
}

function optionalOption(args, name) {
  const index = args.indexOf(name);
  if (index === -1) return null;
  if (index === args.length - 1 || args[index + 1].startsWith('--')) {
    fail(`missing value for ${name}`);
  }
  return args[index + 1];
}

export function parseRequestedSlugs(value) {
  const slugs = value.split(/[\s,]+/u).map((slug) => slug.trim()).filter(Boolean);
  if (slugs.length === 0) fail('explicit slug request is empty');
  const seen = new Set();
  for (const slug of slugs) {
    if (!SLUG_RE.test(slug)) fail(`invalid requested skill slug: ${slug}`);
    if (seen.has(slug)) fail(`duplicate requested skill slug: ${slug}`);
    seen.add(slug);
  }
  return slugs.sort((left, right) => left.localeCompare(right, 'en'));
}

export function parseResults(text) {
  const results = [];
  const seen = new Set();
  for (const [index, line] of text.split('\n').entries()) {
    if (line.trim() === '') continue;
    let result;
    try {
      result = JSON.parse(line);
    } catch (error) {
      fail(`invalid source monitor JSONL at line ${index + 1}: ${error.message}`);
    }
    if (typeof result?.slug !== 'string' || !SLUG_RE.test(result.slug)) {
      fail(`invalid result skill slug at line ${index + 1}`);
    }
    if (seen.has(result.slug)) fail(`duplicate source monitor result slug: ${result.slug}`);
    seen.add(result.slug);
    results.push(result);
  }
  return results.sort((left, right) => left.slug.localeCompare(right.slug, 'en'));
}

export function parseResultSlugs(text) {
  return parseResults(text).map(({ slug }) => slug);
}

export function verifyExactSelection(requestedValue, jsonlText, expectedUpstreamCommit = null) {
  const requested = parseRequestedSlugs(requestedValue);
  const records = parseResults(jsonlText);
  const results = records.map(({ slug }) => slug);
  const requestedSet = new Set(requested);
  const resultSet = new Set(results);
  const missing = requested.filter((slug) => !resultSet.has(slug));
  const unexpected = results.filter((slug) => !requestedSet.has(slug));
  if (missing.length > 0 || unexpected.length > 0) {
    fail(`source monitor selection mismatch: missing=[${missing.join(',')}], unexpected=[${unexpected.join(',')}]`);
  }
  if (expectedUpstreamCommit !== null) {
    if (!COMMIT_RE.test(expectedUpstreamCommit)) {
      fail(`invalid expected upstream commit: ${expectedUpstreamCommit}`);
    }
    const drifted = records
      .filter(({ upstream_commit_sha: commit }) => commit !== expectedUpstreamCommit)
      .map(({ slug, upstream_commit_sha: commit }) => `${slug}:${commit ?? 'missing'}`);
    if (drifted.length > 0) {
      fail(`source monitor upstream commit mismatch: expected=${expectedUpstreamCommit}, actual=[${drifted.join(',')}]`);
    }
    const invalidStatuses = records
      .filter(({ scan_status: status }) => status !== 'updated')
      .map(({ slug, scan_status: status }) => `${slug}:${status ?? 'missing'}`);
    if (invalidStatuses.length > 0) {
      fail(`source monitor update status mismatch: expected=updated, actual=[${invalidStatuses.join(',')}]`);
    }
  }
  return {
    requested: requested.length,
    results: results.length,
    expectedUpstreamCommit,
  };
}

function parseSummaryCount(text, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const matches = [...text.matchAll(new RegExp(`^\\| ${escaped} \\| ([0-9]+) \\|$`, 'gmu'))];
  if (matches.length !== 1) fail(`missing or duplicate source monitor summary metric: ${label}`);
  return Number(matches[0][1]);
}

export function verifyLocalActionSummary(text, expectedCount) {
  const metrics = {
    observed: parseSummaryCount(text, 'Observed updated skills'),
    selected: parseSummaryCount(text, 'Selected updated skills for this run'),
    applied: parseSummaryCount(text, 'Applied updated skills'),
    failed: parseSummaryCount(text, 'Failed selected updates'),
    deferred: parseSummaryCount(text, 'Deferred updated skills'),
  };
  if (
    metrics.observed !== expectedCount
    || metrics.selected !== expectedCount
    || metrics.applied !== expectedCount
    || metrics.failed !== 0
    || metrics.deferred !== 0
  ) {
    fail(`source monitor local action mismatch: expected=${expectedCount}, metrics=${JSON.stringify(metrics)}`);
  }
  return metrics;
}

function walkReports(directory, reports) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name);
    if (entry.isSymbolicLink()) continue;
    if (entry.isDirectory()) walkReports(path, reports);
    else if (entry.isFile() && entry.name === 'skill-report.json') reports.push(path);
  }
}

function gitPaths(repositoryRoot, args) {
  const result = spawnSync('git', ['-C', repositoryRoot, ...args], { encoding: 'buffer' });
  if (result.status !== 0) {
    fail(`git ${args.join(' ')} failed: ${result.stderr.toString('utf8').trim()}`);
  }
  let output;
  try {
    output = new TextDecoder('utf-8', { fatal: true }).decode(result.stdout);
  } catch {
    fail(`git ${args.join(' ')} returned a non-UTF-8 path`);
  }
  return output.split('\0').filter(Boolean);
}

function validateChangedPath(path) {
  if (
    path.startsWith('/')
    || path.includes('\\')
    || /[\u0000-\u001f\u007f]/u.test(path)
    || path.split('/').some((segment) => segment === '..')
    || posix.normalize(path) !== path
  ) {
    fail(`unsafe changed path: ${path}`);
  }
  return path;
}

export function verifyLocalMutations({
  repositoryRoot,
  requested,
  expectedUpstreamCommit,
  summaryText,
}) {
  const root = realpathSync(resolve(repositoryRoot));
  const requestedSlugs = parseRequestedSlugs(requested);
  if (!COMMIT_RE.test(expectedUpstreamCommit)) fail(`invalid expected upstream commit: ${expectedUpstreamCommit}`);
  const metrics = verifyLocalActionSummary(summaryText, requestedSlugs.length);

  const reportPaths = [];
  walkReports(resolve(root, 'skills'), reportPaths);
  const reportIndex = new Map();
  for (const reportPath of reportPaths) {
    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    const slug = report?.meta?.slug;
    if (!requestedSlugs.includes(slug)) continue;
    const matches = reportIndex.get(slug) ?? [];
    matches.push({ reportPath, report });
    reportIndex.set(slug, matches);
  }

  const authorized = [];
  for (const slug of requestedSlugs) {
    const matches = reportIndex.get(slug) ?? [];
    if (matches.length !== 1) fail(`expected one marketplace report for ${slug}, found ${matches.length}`);
    const [{ reportPath, report }] = matches;
    if (lstatSync(reportPath).isSymbolicLink() || !lstatSync(reportPath).isFile()) {
      fail(`marketplace report is not a regular file: ${reportPath}`);
    }
    if (report.meta.upstream_commit_sha !== expectedUpstreamCommit) {
      fail(`marketplace report commit mismatch for ${slug}: ${report.meta.upstream_commit_sha ?? 'missing'}`);
    }
    const relativeReport = posix.normalize(reportPath.slice(root.length + 1).replaceAll('\\', '/'));
    authorized.push({ slug, directory: `${dirname(relativeReport).replaceAll('\\', '/')}/`, report: relativeReport });
  }

  const changed = new Set([
    ...gitPaths(root, ['diff', '--name-only', '-z', '--no-renames', 'HEAD', '--']),
    ...gitPaths(root, ['ls-files', '--others', '--exclude-standard', '-z', '--']),
  ].map(validateChangedPath));
  if (changed.size === 0) fail('source monitor produced no marketplace file changes');

  for (const path of changed) {
    if (!authorized.some(({ directory }) => path.startsWith(directory))) {
      fail(`source monitor changed an unauthorized path: ${path}`);
    }
    const absolute = resolve(root, path);
    if (existsSync(absolute) && lstatSync(absolute).isSymbolicLink()) {
      fail(`source monitor changed a symbolic link: ${path}`);
    }
  }
  for (const entry of authorized) {
    if (!changed.has(entry.report)) fail(`source monitor did not update report provenance for ${entry.slug}`);
    if (![...changed].some((path) => path.startsWith(entry.directory) && path !== entry.report)) {
      fail(`source monitor produced no payload file changes for ${entry.slug}`);
    }
  }
  return { ...metrics, changedPaths: changed.size, authorizedDirectories: authorized.length };
}

function main() {
  const args = process.argv.slice(2);
  const requested = option(args, '--requested');
  const jsonlPath = resolve(option(args, '--jsonl'));
  const expectedUpstreamCommit = optionalOption(args, '--expected-upstream-commit');
  const requireLocalUpdates = args.includes('--require-local-updates');
  const jsonlText = readFileSync(jsonlPath, 'utf8');
  const summary = verifyExactSelection(
    requested,
    jsonlText,
    expectedUpstreamCommit,
  );
  if (requireLocalUpdates) {
    if (expectedUpstreamCommit === null) fail('--require-local-updates requires --expected-upstream-commit');
    const summaryPath = resolve(option(args, '--summary'));
    const repositoryRoot = resolve(option(args, '--repository-root'));
    const mutations = verifyLocalMutations({
      repositoryRoot,
      requested,
      expectedUpstreamCommit,
      summaryText: readFileSync(summaryPath, 'utf8'),
    });
    process.stdout.write(
      `Verified source monitor mutations: ${mutations.applied}/${summary.requested}, ${mutations.changedPaths} changed path(s)\n`,
    );
  }
  process.stdout.write(`Verified exact source monitor selection: ${summary.results}/${summary.requested}\n`);
}

const isMain = process.argv[1]
  && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
if (isMain) {
  try {
    main();
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
