#!/usr/bin/env node

import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const SKIP_DIRECTORIES = new Set(['node_modules', '.git', '.venv', 'venv', 'dist', 'build', '__pycache__', '.cache']);
const REPOSITORY = /^[a-z0-9_-]+\/[a-z0-9._-]+$/;
const CANONICAL_SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

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

function repositoryPath(value, label) {
  if (typeof value !== 'string' || value === '' || value !== value.normalize('NFC') || value.includes('\\')) {
    fail(`${label} must be a non-empty NFC POSIX repository-relative path`);
  }
  const segments = value.split('/');
  if (segments.some((segment) => segment === '' || segment === '.' || segment === '..')) {
    fail(`${label} contains an empty or unsafe path segment`);
  }
  return segments.join('/');
}

function canonicalRepository(value, label) {
  if (typeof value !== 'string' || !REPOSITORY.test(value) || value !== value.toLowerCase()) {
    fail(`${label} must be canonical lowercase owner/repo`);
  }
  return value;
}

export function validateSlugAliasRegistry(registry) {
  if (!registry || typeof registry !== 'object' || Array.isArray(registry)) fail('slug alias registry must be an object');
  if (JSON.stringify(Object.keys(registry).sort()) !== JSON.stringify(['aliases', 'schemaVersion'])) {
    fail('slug alias registry has unknown or missing fields');
  }
  if (registry.schemaVersion !== 1) fail('slug alias registry schemaVersion must be 1');
  if (!Array.isArray(registry.aliases)) fail('slug alias registry aliases must be an array');

  const aliases = [];
  const paths = new Set();
  const repositorySlugs = new Set();
  const finalSlugs = new Set();
  for (const [index, raw] of registry.aliases.entries()) {
    const label = `slug alias ${index}`;
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) fail(`${label} must be an object`);
    const expectedKeys = ['baseSlug', 'expectedName', 'path', 'repository'];
    const actualKeys = Object.keys(raw).sort();
    if (JSON.stringify(actualKeys) !== JSON.stringify(expectedKeys)) fail(`${label} has unknown or missing fields`);
    const repository = canonicalRepository(raw.repository, `${label}.repository`);
    const path = repositoryPath(raw.path, `${label}.path`);
    if (typeof raw.expectedName !== 'string' || raw.expectedName === '' || raw.expectedName !== raw.expectedName.normalize('NFC')) {
      fail(`${label}.expectedName must be a non-empty NFC string`);
    }
    if (typeof raw.baseSlug !== 'string' || !CANONICAL_SLUG.test(raw.baseSlug)) {
      fail(`${label}.baseSlug must be canonical lowercase ASCII kebab-case`);
    }

    const pathKey = `${repository}:${path}`;
    const repositorySlugKey = `${repository}:${raw.baseSlug}`;
    const owner = repository.split('/', 1)[0];
    const finalSlug = `${owner}-${raw.baseSlug}`;
    if (paths.has(pathKey)) fail(`duplicate slug alias path: ${pathKey}`);
    if (repositorySlugs.has(repositorySlugKey)) fail(`duplicate slug alias baseSlug in repository: ${repositorySlugKey}`);
    if (finalSlugs.has(finalSlug)) fail(`duplicate slug alias final community slug: ${finalSlug}`);
    paths.add(pathKey);
    repositorySlugs.add(repositorySlugKey);
    finalSlugs.add(finalSlug);
    aliases.push({ repository, path, expectedName: raw.expectedName, baseSlug: raw.baseSlug });
  }
  return aliases;
}

function posixRelative(root, path) {
  return relative(root, path).split(sep).join('/');
}

function isWithinScope(path, scope) {
  return scope === '' || path === scope || path.startsWith(`${scope}/`);
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

export function discoverSubmissionSkills({
  sourceDir,
  skillPath = '',
  explicitPath = false,
  repository = '',
  slugAliasRegistry = { schemaVersion: 1, aliases: [] },
}) {
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

  const aliases = validateSlugAliasRegistry(slugAliasRegistry);
  const canonicalRepo = aliases.length > 0 || repository !== ''
    ? canonicalRepository(repository, 'submission repository')
    : '';
  const repositoryAliases = aliases.filter((alias) => alias.repository === canonicalRepo);
  const aliasByPath = new Map(repositoryAliases.map((alias) => [alias.path, alias]));
  const normalizedSkillPath = skillPath === '' ? '' : repositoryPath(skillPath, 'skillPath');
  const scopedAliases = repositoryAliases.filter((alias) => isWithinScope(alias.path, normalizedSkillPath));
  const consumedAliases = new Set();

  const skillFiles = collectSkillFiles(searchRoot);
  if (explicitPath && skillFiles.length === 0) fail(`explicit skill path contains no SKILL.md: ${skillPath}`);
  const skills = [];
  const seen = new Set();
  for (const file of skillFiles) {
    const directory = dirname(file);
    const relativeFile = posixRelative(sourceRoot, file);
    const relativeDirectory = posixRelative(sourceRoot, directory) || '.';
    const name = topLevelName(relativeFile, readFileSync(file, 'utf8'));
    if (directory === sourceRoot && name === null) {
      fail('root-level SKILL.md must define a valid name so Marketplace and CLI discovery use the same slug');
    }
    let slug = slugify(name ?? basename(directory));
    const alias = aliasByPath.get(relativeDirectory);
    if (slug !== '' && alias) fail(`${relativeFile} has an alias that would override an existing ASCII identity`);
    if (slug === '') {
      if (!alias) fail(`${relativeFile} resolves to an empty slug and has no verified path alias`);
      if (name !== alias.expectedName) fail(`${relativeFile} name does not match its verified path alias`);
      slug = alias.baseSlug;
      consumedAliases.add(alias.path);
    }
    if (seen.has(slug)) fail(`duplicate discovered skill slug: ${slug}`);
    seen.add(slug);
    skills.push({ slug, path: relativeDirectory });
  }
  const unconsumed = scopedAliases.filter((alias) => !consumedAliases.has(alias.path));
  if (unconsumed.length > 0) fail(`slug alias scope contains unconsumed paths: ${unconsumed.map((alias) => alias.path).join(', ')}`);
  return { schemaVersion: 1, explicitPath, skillPath, skills };
}

function main() {
  const args = process.argv.slice(2);
  const aliasFile = option(args, '--slug-aliases-file', { required: false, defaultValue: '' });
  let slugAliasRegistry = { schemaVersion: 1, aliases: [] };
  if (aliasFile !== '') {
    try {
      slugAliasRegistry = JSON.parse(readFileSync(aliasFile, 'utf8'));
    } catch (error) {
      fail(`cannot read slug alias registry: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  const result = discoverSubmissionSkills({
    sourceDir: option(args, '--source-dir'),
    skillPath: option(args, '--skill-path', { required: false, defaultValue: '' }),
    explicitPath: option(args, '--explicit-path', { required: false, defaultValue: 'false' }) === 'true',
    repository: option(args, '--repository', { required: false, defaultValue: '' }),
    slugAliasRegistry,
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
