#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import {
  existsSync,
  lstatSync,
  readFileSync,
  realpathSync,
  writeFileSync,
} from 'node:fs';
import { dirname, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { calculateCanonicalTreeHash } from './resolve-approved-submission.mjs';

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

function normalizeSkillPath(value) {
  if (
    value === ''
    || value !== value.normalize('NFC')
    || value.includes('\\')
    || /[\0-\x1f\x7f]/.test(value)
  ) {
    fail(`unsafe SKILL.md path ${JSON.stringify(value)}`);
  }
  const segments = value.split('/');
  if (
    !['pending', 'skills'].includes(segments[0])
    || segments.at(-1) !== 'SKILL.md'
    || ![3, 4].includes(segments.length)
    || segments.some((segment) => segment === '' || segment === '.' || segment === '..')
  ) {
    fail(`noncanonical SKILL.md path ${JSON.stringify(value)}`);
  }
  return segments.join('/');
}

function ensureInside(root, path, label) {
  const rel = relative(root, path);
  if (rel === '..' || rel.startsWith(`..${sep}`) || rel === '') fail(`${label} escapes repository root`);
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`${label} is not valid JSON: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function sha256(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

// Source refreshes can restore upstream colon names in bundled sub-skills.
// Preserve only a proven baseline normalization, never invent names or undo a rename.
function preserveNestedSkillNames(root, skillDirectory) {
  const git = (args) => execFileSync('git', ['-C', root, ...args], { encoding: 'utf8' });
  const scalar = (content) => {
    const frontmatter = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(content);
    if (!frontmatter) return null;
    const names = [...frontmatter[1].matchAll(/^name: *([^\r\n]+)$/gm)];
    if (names.length !== 1) return null;
    const value = /^(?:([a-z0-9:-]+)|"([a-z0-9:-]+)"|'([a-z0-9:-]+)') *$/.exec(names[0][1]);
    if (!value) return null;
    return {
      name: value[1] ?? value[2] ?? value[3],
      offset: content.indexOf('\n') + 1 + names[0].index,
      length: names[0][0].length,
    };
  };
  for (const entry of git(['ls-tree', '-rz', 'HEAD', '--', skillDirectory]).split('\0').filter(Boolean)) {
    const tab = entry.indexOf('\t');
    const [mode, type, oid] = entry.slice(0, tab).split(' ');
    const path = entry.slice(tab + 1);
    if (type !== 'blob' || !['100644', '100755'].includes(mode)
      || !path.startsWith(`${skillDirectory}/`) || !path.endsWith('/SKILL.md')
      || path === `${skillDirectory}/SKILL.md`) continue;
    const absolute = resolve(root, path);
    if (!existsSync(absolute)) continue;
    if (realpathSync(absolute) !== absolute || !lstatSync(absolute).isFile()) {
      fail(`${path} is not a regular packaged file`);
    }
    const before = scalar(git(['cat-file', 'blob', oid]));
    const content = readFileSync(absolute, 'utf8');
    const incoming = scalar(content);
    if (!before || !incoming || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(before.name)
      || !/^[a-z0-9]+(?:-[a-z0-9]+)*(?::[a-z0-9]+(?:-[a-z0-9]+)*)+$/.test(incoming.name)
      || incoming.name.replaceAll(':', '-') !== before.name) continue;
    writeFileSync(absolute, `${content.slice(0, incoming.offset)}name: ${before.name}${content.slice(incoming.offset + incoming.length)}`);
  }
}

export function rebindSkillReportHashes({ repositoryRoot, skillPaths, preserveNestedNames = false }) {
  const root = realpathSync(repositoryRoot);
  const normalized = [...new Set(skillPaths.map(normalizeSkillPath))].sort();
  if (normalized.length === 0) fail('no changed SKILL.md paths were provided');

  const rebound = [];
  for (const skillPath of normalized) {
    const absoluteSkill = resolve(root, ...skillPath.split('/'));
    ensureInside(root, absoluteSkill, skillPath);
    if (!existsSync(absoluteSkill)) continue;
    const skillStat = lstatSync(absoluteSkill);
    if (!skillStat.isFile() || skillStat.isSymbolicLink()) fail(`${skillPath} is not a regular file`);

    const skillDirectory = dirname(skillPath).split(sep).join('/');
    const reportPath = `${skillDirectory}/skill-report.json`;
    const absoluteReport = resolve(root, ...reportPath.split('/'));
    ensureInside(root, absoluteReport, reportPath);
    if (!existsSync(absoluteReport)) fail(`${reportPath} is missing`);
    const reportStat = lstatSync(absoluteReport);
    if (!reportStat.isFile() || reportStat.isSymbolicLink()) fail(`${reportPath} is not a regular file`);

    const report = readJson(absoluteReport, reportPath);
    const sourceUrl = report?.meta?.source_url;
    const sourceRef = report?.meta?.source_ref;
    if (typeof sourceUrl !== 'string' || !sourceUrl.startsWith('https://github.com/')) {
      fail(`${reportPath} has invalid source_url lineage`);
    }
    if (typeof sourceRef !== 'string' || sourceRef.trim() === '') {
      fail(`${reportPath} has invalid source_ref lineage`);
    }

    if (preserveNestedNames) {
      if (!skillDirectory.startsWith('skills/')) fail('name preservation is restricted to published skills');
      preserveNestedSkillNames(root, skillDirectory);
    }
    const contentHash = sha256(absoluteSkill);
    const treeHash = calculateCanonicalTreeHash(root, skillDirectory);
    report.meta.content_hash = contentHash;
    report.meta.tree_hash = treeHash;
    writeFileSync(absoluteReport, `${JSON.stringify(report, null, 2)}\n`, { mode: reportStat.mode & 0o777 });

    const written = readJson(absoluteReport, reportPath);
    if (written.meta.source_url !== sourceUrl || written.meta.source_ref !== sourceRef) {
      fail(`${reportPath} source lineage changed during hash rebinding`);
    }
    if (written.meta.content_hash !== sha256(absoluteSkill)) fail(`${reportPath} content_hash rebinding failed`);
    if (written.meta.tree_hash !== calculateCanonicalTreeHash(root, skillDirectory)) {
      fail(`${reportPath} tree_hash rebinding failed`);
    }
    rebound.push({ skillPath, reportPath, contentHash, treeHash, sourceUrl, sourceRef });
  }
  if (rebound.length === 0) fail('no existing changed SKILL.md files were rebound');
  return rebound;
}

function main() {
  const args = process.argv.slice(2);
  const pathsFile = option(args, '--skill-paths-file');
  const bytes = readFileSync(pathsFile);
  const skillPaths = bytes.toString('utf8').split('\0').filter(Boolean);
  const rebound = rebindSkillReportHashes({
    repositoryRoot: option(args, '--repo-root'),
    skillPaths,
    preserveNestedNames: args.includes('--preserve-nested-names'),
  });
  process.stdout.write(`${JSON.stringify({ schemaVersion: 1, rebound }, null, 2)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Skill report hash rebinding failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
