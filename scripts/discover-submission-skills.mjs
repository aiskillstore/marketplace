#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync, realpathSync } from 'node:fs';
import { basename, dirname, join, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { validatePortablePath } from './submission-selection-plan.mjs';

const SKIP_DIRECTORIES = new Set(['node_modules', '.git', '.venv', 'venv', 'dist', 'build', '__pycache__', '.cache']);
const PROJECT_LOCAL_SKILL_ROOTS = ['.agents/skills', '.claude/skills', '.codex/skills'];
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
  return validatePortablePath(value, label);
}

function publicationPath(value, label) {
  if (typeof value !== 'string' || value === '' || value !== value.normalize('NFC')) {
    fail(`${label} must be a non-empty NFC string`);
  }
  if (value.startsWith('/') || value.includes('\\')) fail(`${label} must be repository-relative POSIX path`);
  const withoutPrefix = value.startsWith('./') ? value.slice(2) : value;
  const normalized = withoutPrefix.replace(/\/+$/g, '');
  if (normalized === '') fail(`${label} must not resolve to the repository root`);
  return repositoryPath(normalized, label);
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

function collectSkillFiles(root, { strict = false } = {}) {
  const files = [];
  function walk(directory) {
    const seenNames = new Set();
    for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'variant' }))) {
      if (strict) {
        // Validate every traversed tree entry before opening it. This makes the
        // plan portable across case-insensitive and Windows checkouts.
        validatePortablePath(entry.name, `publication tree entry ${entry.name}`);
        const folded = entry.name.normalize('NFC').toLocaleLowerCase('en-US');
        if (seenNames.has(folded)) fail(`publication tree contains NFC/case-fold collision: ${entry.name}`);
        seenNames.add(folded);
      }
      if (entry.isDirectory() && !SKIP_DIRECTORIES.has(entry.name)) {
        walk(join(directory, entry.name));
      } else if (entry.isFile() && entry.name === 'SKILL.md') {
        files.push(join(directory, entry.name));
      } else if (strict && entry.isSymbolicLink()) {
        fail(`symbolic links are not allowed in the selected publication scope: ${join(directory, entry.name)}`);
      }
    }
  }
  walk(root);
  return files.sort();
}

function resolveContainedPath(sourceRoot, relativePath, label, { directory = true } = {}) {
  const normalized = relativePath === '.' ? '.' : repositoryPath(relativePath, label);
  const segments = normalized === '.' ? [] : normalized.split('/');
  let current = sourceRoot;
  for (const segment of segments) {
    current = join(current, segment);
    let stat;
    try { stat = lstatSync(current); } catch { fail(`${label} does not exist: ${relativePath}`); }
    if (stat.isSymbolicLink()) fail(`${label} contains a symbolic link: ${relativePath}`);
  }
  let resolved;
  try { resolved = realpathSync(current); } catch { fail(`${label} cannot be resolved: ${relativePath}`); }
  if (resolved !== sourceRoot && !resolved.startsWith(`${sourceRoot}${sep}`)) fail(`${label} escapes source repository: ${relativePath}`);
  const final = lstatSync(current);
  if (directory && !final.isDirectory()) fail(`${label} must be a real directory: ${relativePath}`);
  if (!directory && !final.isFile()) fail(`${label} must be a regular file: ${relativePath}`);
  return current;
}

function codexPluginScope(sourceRoot) {
  let pluginDirectory;
  try { pluginDirectory = lstatSync(join(sourceRoot, '.codex-plugin')); } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
  if (!pluginDirectory.isDirectory() || pluginDirectory.isSymbolicLink()) fail('Codex plugin directory must be a real directory');
  try { lstatSync(join(sourceRoot, '.codex-plugin', 'plugin.json')); } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
  const manifestPath = resolveContainedPath(sourceRoot, '.codex-plugin/plugin.json', 'Codex plugin manifest', { directory: false });
  let stat;
  try { stat = lstatSync(manifestPath); } catch (error) { if (error?.code === 'ENOENT') return null; throw error; }
  if (!stat.isFile() || stat.isSymbolicLink()) fail('Codex plugin manifest must be a regular file');
  let manifest;
  try {
    manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
  } catch (error) {
    fail(`cannot parse Codex plugin manifest: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!manifest || typeof manifest !== 'object' || Array.isArray(manifest)) fail('Codex plugin manifest must be an object');
  if (!Object.hasOwn(manifest, 'skills')) return null;
  if (typeof manifest.skills !== 'string') fail('Codex plugin skills must be one repository-relative directory path');
  return publicationPath(manifest.skills, 'Codex plugin skills path');
}

function resolvePublicationScope(sourceRoot, skillPath, explicitPath) {
  if (explicitPath) {
    const path = skillPath === '.' ? '.' : repositoryPath(skillPath, 'skillPath');
    resolveContainedPath(sourceRoot, path, 'explicit skill path');
    return { reason: 'explicit_path', path };
  }
  const manifestScope = codexPluginScope(sourceRoot);
  if (manifestScope !== null) {
    resolveContainedPath(sourceRoot, manifestScope, 'declared publication scope');
    return { reason: 'codex_plugin_manifest', path: manifestScope };
  }
  const conventional = join(sourceRoot, 'skills');
  try {
    const stat = lstatSync(conventional);
    if (stat.isSymbolicLink() || !stat.isDirectory()) fail('conventional publication scope must be a real directory: skills');
    resolveContainedPath(sourceRoot, 'skills', 'conventional publication scope');
    return { reason: 'conventional_skills', path: 'skills' };
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }
  return { reason: 'repository_fallback', path: '.' };
}

function canonicalTreeHash(skillDir) {
  const entries = [];
  function walk(directory) {
    const seenNames = new Set();
    for (const entry of readdirSync(directory, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'variant' }))) {
      validatePortablePath(entry.name, `mirrored skill tree entry ${entry.name}`);
      const folded = entry.name.normalize('NFC').toLocaleLowerCase('en-US');
      if (seenNames.has(folded)) fail(`mirrored skill tree contains NFC/case-fold collision: ${entry.name}`);
      seenNames.add(folded);
      const absolute = join(directory, entry.name);
      const relativePath = posixRelative(skillDir, absolute);
      const stat = lstatSync(absolute);
      if (entry.isSymbolicLink() || (!entry.isDirectory() && !entry.isFile())) {
        fail(`unsupported file type in mirrored skill tree: ${relativePath}`);
      }
      if (entry.isDirectory()) {
        walk(absolute);
        continue;
      }
      if (relativePath === 'skill-report.json' || entry.name === '.DS_Store' || entry.name.endsWith('~') || entry.name.endsWith('.tmp') || entry.name.endsWith('.temp')) continue;
      const bytes = readFileSync(absolute);
      entries.push({
        path: relativePath,
        mode: (stat.mode & 0o111) === 0 ? '100644' : '100755',
        sha256: createHash('sha256').update(bytes).digest('hex'),
        size: bytes.byteLength,
      });
    }
  }
  walk(skillDir);
  const serialized = entries
    .sort((a, b) => a.path.localeCompare(b.path, 'en', { sensitivity: 'variant' }))
    .map((entry) => JSON.stringify(entry))
    .join('\n');
  return createHash('sha256').update(serialized).digest('hex');
}

function projectLocalMirrorIdentity(relativeDirectory) {
  const root = PROJECT_LOCAL_SKILL_ROOTS.find((candidate) => relativeDirectory.startsWith(`${candidate}/`));
  if (!root) return null;
  return { root, logicalPath: relativeDirectory.slice(root.length + 1) };
}

function mirrorDiagnostics(sourceRoot, physicalSkillFiles, selectedSkillFiles, includeSelected) {
  const selected = new Set(selectedSkillFiles);
  const groups = new Map();
  for (const file of physicalSkillFiles) {
    if (!includeSelected && selected.has(file)) continue;
    const directory = dirname(file);
    const relativeDirectory = posixRelative(sourceRoot, directory);
    const identity = projectLocalMirrorIdentity(relativeDirectory);
    if (!identity) continue;
    let slug;
    try {
      slug = slugify(topLevelName(posixRelative(sourceRoot, file), readFileSync(file, 'utf8')) ?? basename(directory));
    } catch {
      continue;
    }
    if (slug === '') continue;
    const key = `${slug}\0${identity.logicalPath}`;
    const rows = groups.get(key) ?? [];
    let treeHash = null;
    try {
      treeHash = canonicalTreeHash(directory);
    } catch {
      // This path is outside the authoritative publication scope. Keep the
      // diagnostic conservative without allowing ignored local files to block it.
    }
    rows.push({ path: relativeDirectory, treeHash });
    groups.set(key, rows);
  }
  return [...groups.entries()]
    .filter(([, rows]) => rows.length > 1)
    .map(([key, rows]) => {
      const slug = key.split('\0', 1)[0];
      const hashes = [...new Set(rows.map(({ treeHash }) => treeHash))];
      const fullyInspected = hashes.every((hash) => typeof hash === 'string');
      return {
        slug,
        paths: rows.map(({ path }) => path).sort(),
        identical: fullyInspected && hashes.length === 1,
        treeHash: fullyInspected && hashes.length === 1 ? hashes[0] : null,
      };
    })
    .sort((a, b) => a.slug.localeCompare(b.slug, 'en', { sensitivity: 'variant' }));
}

export function discoverSubmissionSkills({
  sourceDir,
  skillPath = '',
  explicitPath = false,
  repository = '',
  slugAliasRegistry = { schemaVersion: 1, aliases: [] },
}) {
  const sourceRoot = realpathSync(resolve(sourceDir));
  const scope = resolvePublicationScope(sourceRoot, skillPath, explicitPath);
  const searchRoot = scope.path === '.' ? sourceRoot : resolve(sourceRoot, scope.path);
  const relativeSearch = relative(sourceRoot, searchRoot);
  if (relativeSearch === '..' || relativeSearch.startsWith(`..${sep}`)) fail(`skill path escapes source repository: ${skillPath}`);
  let searchStat;
  try {
    searchStat = lstatSync(searchRoot);
  } catch {
    if (explicitPath) fail(`explicit skill path does not exist: ${skillPath}`);
    return { schemaVersion: 2, explicitPath, skillPath, scope, stats: {
      physicalSkillFiles: 0,
      selectedSkillFiles: 0,
      ignoredSkillFiles: 0,
      identicalMirrorGroups: 0,
      conflictingMirrorGroups: 0,
    }, mirrorGroups: [], skills: [] };
  }
  if (!searchStat.isDirectory() || searchStat.isSymbolicLink()) fail(`skill search root must be a real directory: ${skillPath || '.'}`);

  const aliases = validateSlugAliasRegistry(slugAliasRegistry);
  const canonicalRepo = aliases.length > 0 || repository !== ''
    ? canonicalRepository(repository, 'submission repository')
    : '';
  const repositoryAliases = aliases.filter((alias) => alias.repository === canonicalRepo);
  const aliasByPath = new Map(repositoryAliases.map((alias) => [alias.path, alias]));
  const normalizedSkillPath = scope.path === '.' ? '' : scope.path;
  const scopedAliases = explicitPath && scope.path === '.'
    ? []
    : repositoryAliases.filter((alias) => isWithinScope(alias.path, normalizedSkillPath));
  const consumedAliases = new Set();

  const physicalSkillFiles = collectSkillFiles(sourceRoot);
  let skillFiles;
  // A root-level blob URL names only repository-root SKILL.md. Do not walk
  // unrelated nested content: it is outside this explicit authority boundary.
  if (explicitPath && scope.path === '.') {
    const rootSkill = join(sourceRoot, 'SKILL.md');
    try {
      const stat = lstatSync(rootSkill);
      if (stat.isSymbolicLink() || !stat.isFile()) fail('root-level explicit SKILL.md must be a regular file');
      skillFiles = [rootSkill];
    } catch (error) {
      if (error?.code === 'ENOENT') skillFiles = [];
      else throw error;
    }
  } else {
    skillFiles = collectSkillFiles(searchRoot, { strict: true });
  }
  if (explicitPath && skillFiles.length === 0) fail(`explicit skill path contains no SKILL.md: ${skillPath}`);
  const skills = [];
  const seen = new Map();
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
    const previous = seen.get(slug);
    if (previous) {
      const previousIdentity = projectLocalMirrorIdentity(previous.path);
      const currentIdentity = projectLocalMirrorIdentity(relativeDirectory);
      const approvedMirror = scope.reason === 'repository_fallback'
        && previousIdentity !== null
        && currentIdentity !== null
        && previousIdentity.logicalPath === currentIdentity.logicalPath;
      if (!approvedMirror) fail(`duplicate discovered skill slug: ${slug}`);
      const previousHash = canonicalTreeHash(previous.directory);
      const currentHash = canonicalTreeHash(directory);
      if (previousHash !== currentHash) fail(`conflicting project-local mirror slug: ${slug}`);
      continue;
    }
    seen.set(slug, { path: relativeDirectory, directory });
    skills.push({ slug, path: relativeDirectory });
  }
  const unconsumed = scopedAliases.filter((alias) => !consumedAliases.has(alias.path));
  if (unconsumed.length > 0) fail(`slug alias scope contains unconsumed paths: ${unconsumed.map((alias) => alias.path).join(', ')}`);
  const mirrorGroups = mirrorDiagnostics(
    sourceRoot,
    physicalSkillFiles,
    skillFiles,
    scope.reason === 'repository_fallback',
  );
  const identicalMirrorGroups = mirrorGroups.filter(({ identical }) => identical).length;
  return {
    schemaVersion: 2,
    explicitPath,
    skillPath,
    scope,
    stats: {
      physicalSkillFiles: physicalSkillFiles.length,
      selectedSkillFiles: skills.length,
      ignoredSkillFiles: physicalSkillFiles.length - skills.length,
      identicalMirrorGroups,
      conflictingMirrorGroups: mirrorGroups.length - identicalMirrorGroups,
    },
    mirrorGroups,
    skills,
  };
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
