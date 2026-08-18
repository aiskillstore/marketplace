#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, lstatSync, readFileSync } from 'node:fs';
import { posix, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

import { publishedSkillDirectory, resolveChangedSkillPaths } from './detect-changed-skills.mjs';
import { calculateCanonicalTreeHash } from './resolve-approved-submission.mjs';

function fail(message) {
  throw new Error(message);
}

function git(root, args) {
  const result = spawnSync('git', ['-C', root, ...args], { encoding: 'utf8' });
  if (result.status !== 0) {
    fail(`git ${args.join(' ')} failed: ${result.stderr.trim()}`);
  }
  return result.stdout;
}

function safeRelative(path) {
  if (
    typeof path !== 'string'
    || path === ''
    || path.startsWith('/')
    || path.includes('\\')
    || /[\u0000-\u001f\u007f]/u.test(path)
    || path.split('/').some((segment) => segment === '..')
    || posix.normalize(path) !== path
  ) {
    fail(`unsafe source monitor path: ${String(path)}`);
  }
  return path;
}

function changedEntries(root) {
  const output = git(root, ['diff', '--name-status', '-z', '--no-renames', 'HEAD']);
  const fields = output.split('\0').filter(Boolean);
  if (fields.length % 2 !== 0) fail('malformed git name-status output');
  const entries = [];
  for (let index = 0; index < fields.length; index += 2) {
    const status = fields[index];
    if (!/^[ADMT]$/u.test(status)) fail(`unsupported source monitor change status: ${status}`);
    entries.push({ status, path: safeRelative(fields[index + 1]) });
  }
  for (const path of git(root, ['ls-files', '--others', '--exclude-standard', '-z'])
    .split('\0').filter(Boolean).map(safeRelative)) {
    entries.push({ status: 'A', path });
  }
  return entries.sort((left, right) => left.path.localeCompare(right.path, 'en'));
}

function existingRegular(path, label) {
  if (!existsSync(path)) fail(`${label} is missing: ${path}`);
  const stat = lstatSync(path);
  if (stat.isSymbolicLink() || !stat.isFile()) fail(`${label} must be a regular file: ${path}`);
}

function normalizeReference(raw) {
  let value = raw.trim().replace(/^['"]|['"]$/gu, '');
  value = value.split('#', 1)[0].split('?', 1)[0];
  try {
    value = decodeURIComponent(value);
  } catch {
    return null;
  }
  value = value.replace(/[)\]}>.,;:!?]+$/u, '');
  if (
    value === ''
    || /^(?:https?:|mailto:|data:|#)/iu.test(value)
    || value.startsWith('/')
    || value.includes('\\')
    || value.split('/').some((segment) => segment === '..')
  ) return null;
  return value;
}

function referencedPaths(skillText) {
  const references = new Set();
  for (const match of skillText.matchAll(/!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)/gu)) {
    const value = normalizeReference(match[1]);
    if (value) references.add(value);
  }
  for (const match of skillText.matchAll(/(?<![A-Za-z0-9._~!$&'()+,;=@%/:-])((?:[A-Za-z0-9._~!$&'()+,;=@%-]+\/)*(?:references|scripts|assets|commands|prompts|tests)\/[A-Za-z0-9._~!$&'()+,;=@%/-]+)/gu)) {
    const value = normalizeReference(match[1]);
    if (value) references.add(value);
  }
  return [...references].sort((left, right) => left.localeCompare(right, 'en'));
}

function validateReferences(root, directory) {
  const skillPath = resolve(root, directory, 'SKILL.md');
  existingRegular(skillPath, 'changed SKILL.md');
  const text = readFileSync(skillPath, 'utf8');
  for (const reference of referencedPaths(text)) {
    const relative = safeRelative(`${directory}/${reference}`);
    const absolute = resolve(root, relative);
    if (!existsSync(absolute)) fail(`SKILL.md references missing path: ${relative}`);
    const stat = lstatSync(absolute);
    if (stat.isSymbolicLink() || (!stat.isFile() && !stat.isDirectory())) {
      fail(`SKILL.md references unsafe path: ${relative}`);
    }
  }
}

function packageTargets(pkg) {
  const targets = new Set();
  if (typeof pkg.bin === 'string') targets.add(pkg.bin);
  else if (pkg.bin && typeof pkg.bin === 'object' && !Array.isArray(pkg.bin)) {
    for (const value of Object.values(pkg.bin)) if (typeof value === 'string') targets.add(value);
  }
  if (pkg.scripts && typeof pkg.scripts === 'object' && !Array.isArray(pkg.scripts)) {
    for (const command of Object.values(pkg.scripts)) {
      if (typeof command !== 'string') continue;
      for (const match of command.matchAll(/(?:^|&&|\|\|)\s*node\s+(['"]?[^\s'";&|]+['"]?)/gu)) {
        targets.add(match[1].replace(/^['"]|['"]$/gu, ''));
      }
    }
  }
  return [...targets];
}

function validatePackage(root, directory, report) {
  const packagePath = resolve(root, directory, 'package.json');
  if (!existsSync(packagePath)) return;
  existingRegular(packagePath, 'package.json');
  let pkg;
  try {
    pkg = JSON.parse(readFileSync(packagePath, 'utf8'));
  } catch (error) {
    fail(`invalid package.json at ${directory}: ${error.message}`);
  }
  for (const rawTarget of packageTargets(pkg)) {
    const target = normalizeReference(rawTarget);
    if (!target || /[*{}[\]]/u.test(target)) continue;
    const relative = safeRelative(`${directory}/${target}`);
    const absolute = resolve(root, relative);
    if (!existsSync(absolute) || lstatSync(absolute).isSymbolicLink() || !lstatSync(absolute).isFile()) {
      fail(`package target is missing: ${relative}`);
    }
  }
  if (
    typeof pkg.license === 'string'
    && typeof report?.skill?.license === 'string'
    && pkg.license !== report.skill.license
  ) {
    fail(`package/report license mismatch at ${directory}: package=${pkg.license}, report=${report.skill.license}`);
  }
}

function reportFor(root, directory) {
  const path = resolve(root, directory, 'skill-report.json');
  existingRegular(path, 'skill report');
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`invalid skill report at ${directory}: ${error.message}`);
  }
}

function auditPolicy(report) {
  const audit = report?.security_audit ?? {};
  return JSON.stringify({
    risk_level: audit.risk_level,
    is_blocked: audit.is_blocked,
    safe_to_publish: audit.safe_to_publish,
    agent_auto_install_policy: audit.agent_auto_install_policy,
    manual_install_policy: audit.manual_install_policy,
  });
}

function immutableIdentity(report) {
  const meta = report?.meta ?? {};
  const values = [meta.source_url, meta.upstream_commit_sha ?? meta.source_ref, meta.content_hash, meta.tree_hash];
  if (values.some((value) => typeof value !== 'string' || value === '')) return null;
  return values.join('\0');
}

function validateDuplicatePolicy(records, changedDirectories) {
  const byIdentity = new Map();
  for (const record of records) {
    const identity = immutableIdentity(record.report);
    if (identity === null) continue;
    const group = byIdentity.get(identity) ?? [];
    group.push(record);
    byIdentity.set(identity, group);
  }
  for (const group of byIdentity.values()) {
    if (group.length < 2 || !group.some(({ directory }) => changedDirectories.has(directory))) continue;
    const policies = new Set(group.map(({ report }) => auditPolicy(report)));
    if (policies.size > 1) {
      const slugs = group.map(({ report }) => report.meta.slug).sort((left, right) => left.localeCompare(right, 'en'));
      fail(`identical source tree has contradictory audit policy: ${slugs.join(', ')}`);
    }
  }
}

function validateHashBinding(root, directory, report, entries) {
  const reportPath = `${directory}/skill-report.json`;
  if (!entries.some(({ status, path }) => path === reportPath && status !== 'D')) {
    fail(`source monitor must rebind skill report: ${directory}`);
  }
  const skillPath = resolve(root, directory, 'SKILL.md');
  existingRegular(skillPath, 'changed SKILL.md');
  const contentHash = createHash('sha256').update(readFileSync(skillPath)).digest('hex');
  if (report?.meta?.content_hash !== contentHash) {
    fail(`source monitor report content_hash is stale: ${directory}`);
  }
  if (report?.meta?.tree_hash !== calculateCanonicalTreeHash(root, directory)) {
    fail(`source monitor report tree_hash is stale: ${directory}`);
  }
}

function publishedReportPaths(root, entries) {
  const reportPaths = new Set(git(root, [
    'ls-files', '-z', '--',
    ':(glob)skills/*/skill-report.json',
    ':(glob)skills/*/*/skill-report.json',
  ]).split('\0').filter(Boolean).map(safeRelative));
  for (const { path } of entries) {
    if (posix.basename(path) === 'skill-report.json') reportPaths.add(path);
  }
  return [...reportPaths].sort((left, right) => left.localeCompare(right, 'en'));
}

function publishedRecords(root, reportPaths) {
  return reportPaths.map((path) => {
    const identity = publishedSkillDirectory(path);
    if (identity === null) fail(`invalid published skill report path: ${path}`);
    const directory = `skills/${identity}`;
    return { directory, report: reportFor(root, directory) };
  });
}

function validateDestructiveChange(root, directory, entries, allowDestructiveSkills) {
  const baseline = git(root, ['ls-tree', '-r', '--name-only', 'HEAD', '--', directory])
    .split('\n').filter(Boolean).length;
  const deleted = entries.filter(({ status, path }) => status === 'D' && path.startsWith(`${directory}/`)).length;
  if (
    baseline >= 10
    && deleted >= 5
    && deleted / baseline > 0.5
    && !allowDestructiveSkills.has(directory)
  ) {
    fail(`destructive source update requires explicit review: ${directory} deleted=${deleted} baseline=${baseline}`);
  }
  return deleted;
}

export function verifySourceMonitorUpdate({ repositoryRoot, allowDestructiveSkills = [] }) {
  const root = resolve(repositoryRoot);
  const allowed = new Set(allowDestructiveSkills.map(safeRelative));
  const entries = changedEntries(root);
  const reportPaths = publishedReportPaths(root, entries);
  const directories = resolveChangedSkillPaths(entries.map(({ path }) => path), reportPaths)
    .map((directory) => `skills/${directory}`);
  const invalid = entries.find(({ path }) => (
    !directories.some((directory) => path.startsWith(`${directory}/`))
  ));
  if (invalid) fail(`source monitor changed path outside published skills: ${invalid.path}`);
  if (directories.length === 0) fail('source monitor produced no changed skill directories');
  for (const directory of allowed) {
    if (!directories.includes(directory)) fail(`destructive update allowlist does not match a changed skill: ${directory}`);
  }

  let deletedPaths = 0;
  for (const directory of directories) {
    deletedPaths += validateDestructiveChange(root, directory, entries, allowed);
    validateReferences(root, directory);
    const report = reportFor(root, directory);
    validateHashBinding(root, directory, report, entries);
    validatePackage(root, directory, report);
  }
  validateDuplicatePolicy(publishedRecords(root, reportPaths), new Set(directories));
  return { changedSkills: directories.length, changedPaths: entries.length, deletedPaths };
}

function options(args) {
  const value = (name) => {
    const index = args.indexOf(name);
    if (index === -1 || index === args.length - 1 || args[index + 1].startsWith('--')) {
      fail(`missing required option ${name}`);
    }
    return args[index + 1];
  };
  const destructive = [];
  for (let index = 0; index < args.length; index += 1) {
    if (args[index] !== '--allow-destructive-skill') continue;
    if (index === args.length - 1 || args[index + 1].startsWith('--')) {
      fail('missing value for --allow-destructive-skill');
    }
    destructive.push(args[index + 1]);
  }
  return { repositoryRoot: value('--repo-root'), allowDestructiveSkills: destructive };
}

const isMain = process.argv[1]
  && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url));
if (isMain) {
  try {
    const result = verifySourceMonitorUpdate(options(process.argv.slice(2)));
    process.stdout.write(`Verified source monitor update safety: ${result.changedSkills} skill(s), ${result.changedPaths} path(s), ${result.deletedPaths} deletion(s)\n`);
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}
