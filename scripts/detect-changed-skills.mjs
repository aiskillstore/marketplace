#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { posix } from 'node:path';
import { pathToFileURL } from 'node:url';

function readOption(args, name) {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
    throw new Error(`missing required option ${name}`);
  }
  return args[index + 1];
}

function gitPaths(repositoryRoot, args) {
  const output = execFileSync('git', args, {
    cwd: repositoryRoot,
    encoding: 'buffer',
    maxBuffer: 64 * 1024 * 1024,
  });
  return output.toString('utf8').split('\0').filter(Boolean);
}

export function publishedSkillDirectory(reportPath) {
  if (!reportPath.startsWith('skills/') || posix.basename(reportPath) !== 'skill-report.json') {
    return null;
  }
  const segments = reportPath.split('/');
  if (segments.length !== 3 && segments.length !== 4) {
    throw new Error(`published skill report has invalid path depth: ${reportPath}`);
  }
  const identitySegments = segments.slice(1, -1);
  if (
    identitySegments.includes('pending')
    || identitySegments.some((segment) => !/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(segment))
  ) {
    throw new Error(`published skill report has invalid or reserved path identity: ${reportPath}`);
  }
  return identitySegments.join('/');
}

export function resolveChangedSkillPaths(changedPaths, reportPaths) {
  const published = new Set(reportPaths.map(publishedSkillDirectory).filter(Boolean));
  const changedSkills = new Set();

  for (const changedPath of changedPaths) {
    if (!changedPath.startsWith('skills/')) continue;

    let directory = posix.dirname(changedPath.slice('skills/'.length));
    while (directory && directory !== '.') {
      if (published.has(directory)) {
        changedSkills.add(directory);
        break;
      }
      const parent = posix.dirname(directory);
      if (parent === directory) break;
      directory = parent;
    }
  }

  return [...changedSkills].sort();
}

export function detectChangedSkillPathsFromGit({ repositoryRoot = '.', base, head }) {
  const changedPaths = gitPaths(repositoryRoot, [
    'diff',
    '--name-only',
    '-z',
    base,
    head,
    '--',
    'skills',
  ]);
  const headPaths = gitPaths(repositoryRoot, [
    'ls-tree',
    '-r',
    '--name-only',
    '-z',
    head,
    '--',
    'skills',
  ]);

  return resolveChangedSkillPaths(changedPaths, headPaths);
}

function main() {
  const args = process.argv.slice(2);
  const base = readOption(args, '--base');
  const head = readOption(args, '--head');
  const changedSkills = detectChangedSkillPathsFromGit({ base, head });
  process.stdout.write(`${changedSkills.join(' ')}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`::error::Incremental skill detection failed: ${message}`);
    process.exitCode = 1;
  }
}
