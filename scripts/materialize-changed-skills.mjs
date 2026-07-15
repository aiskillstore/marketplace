#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { lstatSync, readFileSync, rmSync } from 'node:fs';
import { posix, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { publishedSkillDirectory } from './detect-changed-skills.mjs';

const MAX_GIT_OUTPUT = 64 * 1024 * 1024;

function readOption(args, name) {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
    throw new Error(`missing required option ${name}`);
  }
  return args[index + 1];
}

function git(repositoryRoot, args, options = {}) {
  return execFileSync('git', args, {
    cwd: repositoryRoot,
    encoding: options.encoding ?? 'buffer',
    input: options.input,
    maxBuffer: MAX_GIT_OUTPUT,
    stdio: options.input === undefined ? ['ignore', 'pipe', 'pipe'] : ['pipe', 'pipe', 'pipe'],
  });
}

export function parseChangedSkillPaths(rawSkills) {
  const skillPaths = [...new Set(
    String(rawSkills ?? '')
      .split(/[\s,]+/)
      .map((value) => value.trim())
      .filter(Boolean),
  )].sort();

  if (skillPaths.length === 0) {
    throw new Error('no changed skill paths were provided');
  }

  for (const skillPath of skillPaths) {
    const segments = skillPath.split('/');
    if (
      skillPath.startsWith('/')
      || skillPath.startsWith('skills/')
      || skillPath.includes('\\')
      || posix.normalize(skillPath) !== skillPath
      || segments.some((segment) => !segment || segment === '.' || segment === '..')
    ) {
      throw new Error(`invalid changed skill path: ${skillPath}`);
    }
    publishedSkillDirectory(`skills/${skillPath}/skill-report.json`);
  }

  return skillPaths;
}

function resolveExactCommit(repositoryRoot, commit) {
  if (!/^[0-9a-f]{40}$/i.test(commit)) {
    throw new Error(`commit must be an exact 40-character SHA: ${commit}`);
  }

  const resolvedCommit = git(
    repositoryRoot,
    ['rev-parse', '--verify', `${commit}^{commit}`],
    { encoding: 'utf8' },
  ).trim();

  if (resolvedCommit.toLowerCase() !== commit.toLowerCase()) {
    throw new Error(`commit did not resolve exactly: ${commit}`);
  }

  return resolvedCommit;
}

function reportEntriesAtCommit(repositoryRoot, commit) {
  const output = git(repositoryRoot, [
    'ls-tree',
    '-r',
    '-z',
    '--full-tree',
    commit,
    '--',
    'skills',
  ]).toString('utf8');
  const reports = new Map();

  for (const record of output.split('\0')) {
    if (!record) continue;
    const tabIndex = record.indexOf('\t');
    if (tabIndex === -1) continue;

    const [mode, type, oid] = record.slice(0, tabIndex).split(' ');
    const treePath = record.slice(tabIndex + 1);
    if (treePath.endsWith('/skill-report.json')) {
      publishedSkillDirectory(treePath);
      reports.set(treePath, { mode, type, oid });
    }
  }

  return reports;
}

function assertSafeRemoval(repositoryRoot, repositoryPath) {
  const root = resolve(repositoryRoot);
  const target = resolve(root, ...repositoryPath.split('/'));
  if (!target.startsWith(`${root}${sep}`)) {
    throw new Error(`refusing to remove path outside repository: ${repositoryPath}`);
  }
  return target;
}

function hashMaterializedReports(repositoryRoot, reportPaths) {
  const output = git(
    repositoryRoot,
    ['hash-object', '--no-filters', '--stdin-paths'],
    {
      encoding: 'utf8',
      input: `${reportPaths.join('\n')}\n`,
    },
  );
  return output.trim().split('\n').filter(Boolean);
}

export function materializeChangedSkills({ repositoryRoot = '.', commit, skills }) {
  const exactCommit = resolveExactCommit(repositoryRoot, commit);
  const skillPaths = Array.isArray(skills) ? parseChangedSkillPaths(skills.join(' ')) : parseChangedSkillPaths(skills);
  const treeReports = reportEntriesAtCommit(repositoryRoot, exactCommit);
  const targets = skillPaths.map((skillPath) => {
    const directory = `skills/${skillPath}`;
    const reportPath = `${directory}/skill-report.json`;
    const report = treeReports.get(reportPath);

    if (!report || report.type !== 'blob' || !report.mode.startsWith('100')) {
      throw new Error(`published report is missing from ${exactCommit}: ${reportPath}`);
    }

    return { directory, reportPath, reportOid: report.oid };
  });

  // Remove only the selected directories first so stale untracked files from a
  // mutable self-hosted workspace cannot leak into the sync payload.
  for (const target of targets) {
    rmSync(assertSafeRemoval(repositoryRoot, target.directory), { recursive: true, force: true });
  }

  // A NUL-delimited literal pathspec avoids shell expansion and ARG_MAX while
  // --ignore-skip-worktree-bits materializes paths omitted by sparse checkout.
  const pathspec = Buffer.from(
    `${targets.map(({ directory }) => `:(literal)${directory}`).join('\0')}\0`,
  );
  git(repositoryRoot, [
    'restore',
    `--source=${exactCommit}`,
    '--worktree',
    '--ignore-skip-worktree-bits',
    '--pathspec-from-file=-',
    '--pathspec-file-nul',
  ], { input: pathspec });

  for (const target of targets) {
    let reportStat;
    try {
      reportStat = lstatSync(resolve(repositoryRoot, ...target.reportPath.split('/')));
    } catch {
      throw new Error(`materialized report is missing: ${target.reportPath}`);
    }
    if (!reportStat.isFile() || reportStat.isSymbolicLink()) {
      throw new Error(`materialized report is not a regular file: ${target.reportPath}`);
    }
  }

  const materializedOids = hashMaterializedReports(
    repositoryRoot,
    targets.map(({ reportPath }) => reportPath),
  );
  if (materializedOids.length !== targets.length) {
    throw new Error(`verified ${materializedOids.length}/${targets.length} materialized reports`);
  }

  for (const [index, target] of targets.entries()) {
    if (materializedOids[index] !== target.reportOid) {
      throw new Error(`materialized report does not match ${exactCommit}: ${target.reportPath}`);
    }
    // Ensure the report is readable before handing the directory to the CLI.
    readFileSync(resolve(repositoryRoot, ...target.reportPath.split('/')));
  }

  return targets.map(({ directory }) => directory);
}

function main() {
  const args = process.argv.slice(2);
  const commit = readOption(args, '--commit');
  const skills = readOption(args, '--skills');
  const materialized = materializeChangedSkills({ commit, skills });
  console.log(`Materialized ${materialized.length} changed skill(s) from ${commit}`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`::error::Changed skill materialization failed: ${message}`);
    process.exitCode = 1;
  }
}
