#!/usr/bin/env node

import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const SKIP_DIRECTORIES = new Set(['node_modules', '.git', '.venv', 'venv', 'dist', 'build', '__pycache__', '.cache']);

function fail(message) {
  throw new Error(message);
}

function option(args, name, { required = true, defaultValue = null } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) fail(`missing required option ${name}`);
    return defaultValue;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function topLevelName(skillMdPath, content) {
  const lines = content.replace(/^\uFEFF/, '').split(/\r?\n/);
  if (lines[0]?.trim() !== '---') return null;
  const end = lines.findIndex((line, index) => index > 0 && line.trim() === '---');
  if (end === -1) fail(`${skillMdPath}: frontmatter is not terminated`);
  let name = null;
  for (let index = 1; index < end; index += 1) {
    const line = lines[index];
    if (line.trim() === '' || /^\s*#/.test(line) || /^\s/.test(line)) continue;
    const match = line.match(/^([A-Za-z0-9_-]+):(?:\s*(.*))?$/);
    if (!match) fail(`${skillMdPath}:${index + 1}: invalid top-level YAML`);
    const [, key, rawValue = ''] = match;
    const value = rawValue.trim();
    if (value !== '' && !/^[>|][+-]?$/.test(value) && !value.startsWith('"') && !value.startsWith("'") && /:\s/.test(value)) {
      fail(`${skillMdPath}:${index + 1}: invalid YAML plain scalar; quote values containing ': '`);
    }
    if (key !== 'name') continue;
    if (name !== null) fail(`${skillMdPath}: duplicate top-level name field`);
    if (value.startsWith('"')) {
      try {
        name = JSON.parse(value);
      } catch {
        fail(`${skillMdPath}:${index + 1}: invalid quoted name`);
      }
    } else if (value.startsWith("'")) {
      if (!value.endsWith("'") || value.length < 2) fail(`${skillMdPath}:${index + 1}: invalid quoted name`);
      name = value.slice(1, -1).replace(/''/g, "'");
    } else {
      name = value.replace(/\s+#.*$/, '').trim();
    }
    if (typeof name !== 'string' || name === '') fail(`${skillMdPath}:${index + 1}: name must be a non-empty scalar`);
  }
  return name;
}

function collectSkillFiles(root) {
  const files = [];
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      if (entry.isDirectory() && !SKIP_DIRECTORIES.has(entry.name)) {
        walk(join(directory, entry.name));
      } else if (entry.isFile() && entry.name === 'SKILL.md') {
        files.push(join(directory, entry.name));
      }
    }
  }
  walk(root);
  return files.sort();
}

export function discoverSubmissionSkills({ sourceDir, skillPath = '', explicitPath = false }) {
  const sourceRoot = resolve(sourceDir);
  const searchRoot = resolve(sourceRoot, skillPath);
  const relativeSearch = relative(sourceRoot, searchRoot);
  if (relativeSearch === '..' || relativeSearch.startsWith(`..${sep}`)) fail(`skill path escapes source repository: ${skillPath}`);
  let searchStat;
  try {
    searchStat = lstatSync(searchRoot);
  } catch {
    if (explicitPath) fail(`explicit skill path does not exist: ${skillPath}`);
    return { schemaVersion: 1, explicitPath, skillPath, skills: [] };
  }
  if (!searchStat.isDirectory() || searchStat.isSymbolicLink()) fail(`skill search root must be a real directory: ${skillPath || '.'}`);

  const skillFiles = collectSkillFiles(searchRoot);
  if (explicitPath && skillFiles.length === 0) fail(`explicit skill path contains no SKILL.md: ${skillPath}`);
  const skills = [];
  const seen = new Set();
  for (const file of skillFiles) {
    const directory = dirname(file);
    const name = topLevelName(relative(sourceRoot, file), readFileSync(file, 'utf8'));
    if (directory === sourceRoot && name === null) {
      fail('root-level SKILL.md must define a valid name so Marketplace and CLI discovery use the same slug');
    }
    const slug = slugify(name ?? basename(directory));
    if (slug === '') fail(`${relative(sourceRoot, file)} resolves to an empty slug`);
    if (seen.has(slug)) fail(`duplicate discovered skill slug: ${slug}`);
    seen.add(slug);
    skills.push({ slug, path: relative(sourceRoot, directory) || '.' });
  }
  return { schemaVersion: 1, explicitPath, skillPath, skills };
}

function main() {
  const args = process.argv.slice(2);
  const result = discoverSubmissionSkills({
    sourceDir: option(args, '--source-dir'),
    skillPath: option(args, '--skill-path', { required: false, defaultValue: '' }),
    explicitPath: option(args, '--explicit-path', { required: false, defaultValue: 'false' }) === 'true',
  });
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Submission skill discovery failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
