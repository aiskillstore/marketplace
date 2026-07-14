#!/usr/bin/env node
import {
  existsSync,
  lstatSync,
  readFileSync,
  readdirSync,
} from 'node:fs';
import { isAbsolute, join, relative, resolve, sep } from 'node:path';

function parseArgs(argv) {
  const options = { repo: process.cwd(), format: 'json' };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--repo') {
      options.repo = argv[++index];
    } else if (arg === '--format') {
      options.format = argv[++index];
    } else if (arg === '-h' || arg === '--help') {
      console.log('Usage: resolve-pending-skill-path.mjs [--repo PATH] [--format json|tsv]');
      process.exit(0);
    } else {
      throw new Error(`unknown argument: ${arg}`);
    }
  }
  if (!options.repo) throw new Error('--repo requires a path');
  if (!['json', 'tsv'].includes(options.format)) {
    throw new Error('--format must be json or tsv');
  }
  return options;
}

function toPosix(path) {
  return path.split(sep).join('/');
}

function assertInside(root, candidate, label) {
  const child = relative(root, candidate);
  if (child === '..' || child.startsWith(`..${sep}`) || isAbsolute(child)) {
    throw new Error(`${label} escapes its trusted root`);
  }
  return child;
}

function findSkillDirectories(pendingRoot) {
  if (!existsSync(pendingRoot)) return [];
  if (!lstatSync(pendingRoot).isDirectory()) {
    throw new Error('pending must be a directory');
  }

  const directories = [];
  const walk = (dir) => {
    const entries = readdirSync(dir, { withFileTypes: true })
      .sort((left, right) => left.name.localeCompare(right.name));
    if (entries.some((entry) => entry.isFile() && entry.name === 'SKILL.md')) {
      directories.push(dir);
    }
    for (const entry of entries) {
      if (entry.isSymbolicLink()) {
        throw new Error(`symbolic links are forbidden under pending: ${toPosix(relative(pendingRoot, join(dir, entry.name)))}`);
      }
      if (entry.isDirectory()) walk(join(dir, entry.name));
    }
  };
  walk(pendingRoot);
  return directories;
}

function parseReportAuthor(skillDir) {
  const reportPath = join(skillDir, 'skill-report.json');
  if (!existsSync(reportPath)) {
    throw new Error(`${toPosix(skillDir)} is missing trusted skill-report.json`);
  }

  let report;
  try {
    report = JSON.parse(readFileSync(reportPath, 'utf8'));
  } catch (error) {
    throw new Error(`${toPosix(reportPath)} is invalid JSON: ${error.message}`);
  }

  const author = report?.skill?.author;
  if (typeof author !== 'string' || author.trim() === '') {
    throw new Error(`${toPosix(reportPath)} author is empty`);
  }
  return author;
}

function parseFrontmatterSlug(skillDir) {
  const skillPath = join(skillDir, 'SKILL.md');
  const content = readFileSync(skillPath, 'utf8');
  const frontmatter = content.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)/);
  if (!frontmatter) {
    throw new Error(`${toPosix(skillPath)} is missing valid YAML frontmatter`);
  }

  const nameLine = frontmatter[1].match(/^name:[ \t]*(.*)$/m);
  if (!nameLine) {
    throw new Error(`${toPosix(skillPath)} slug is empty (frontmatter name is missing)`);
  }

  let slug = nameLine[1].trim();
  if (
    slug.length >= 2
    && ((slug.startsWith('"') && slug.endsWith('"')) || (slug.startsWith("'") && slug.endsWith("'")))
  ) {
    slug = slug.slice(1, -1);
  }
  if (slug === '') {
    throw new Error(`${toPosix(skillPath)} slug is empty`);
  }
  return slug;
}

const WINDOWS_RESERVED_SEGMENT = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$/i;

function assertPortablePathSegment(value, label) {
  if (WINDOWS_RESERVED_SEGMENT.test(value)) {
    throw new Error(`${label} uses a Windows reserved path segment: ${JSON.stringify(value)}`);
  }
  if (/[. ]$/.test(value)) {
    throw new Error(`${label} has a trailing dot or space: ${JSON.stringify(value)}`);
  }
}

function validateAuthor(author) {
  assertPortablePathSegment(author, 'author');
  if (!/^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$/.test(author)) {
    throw new Error(`author has unsafe path segment: ${JSON.stringify(author)}`);
  }
}

function validateSlug(slug) {
  assertPortablePathSegment(slug, 'slug');
  if (slug.length > 64 || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
    throw new Error(`slug has unsafe path segment: ${JSON.stringify(slug)}`);
  }
}

function resolveSkill(repoRoot, pendingRoot, skillDir) {
  const pendingRelative = assertInside(pendingRoot, skillDir, 'pending skill');
  const parts = pendingRelative === '' ? [] : pendingRelative.split(sep);
  if (parts.length !== 0 && parts.length !== 2) {
    throw new Error(
      `unsupported pending layout ${JSON.stringify(toPosix(relative(repoRoot, skillDir)))}; expected pending or pending/author/slug`,
    );
  }

  const author = parseReportAuthor(skillDir);
  const slug = parseFrontmatterSlug(skillDir);
  validateAuthor(author);
  validateSlug(slug);
  if (author.toLowerCase() === 'pending' && slug.toLowerCase() === 'pending') {
    throw new Error('pending/pending destination is forbidden');
  }

  const layout = parts.length === 0 ? 'flat' : 'nested';
  if (layout === 'nested' && (parts[0] !== author || parts[1] !== slug)) {
    throw new Error(
      `nested pending path ${parts.join('/')} does not match trusted metadata ${author}/${slug}`,
    );
  }

  const targetAbsolute = resolve(repoRoot, 'skills', author, slug);
  assertInside(resolve(repoRoot, 'skills'), targetAbsolute, 'target skill');
  return {
    source: toPosix(relative(repoRoot, skillDir)),
    target: toPosix(relative(repoRoot, targetAbsolute)),
    author,
    slug,
    layout,
  };
}

function resolvePendingSkills(repo) {
  const repoRoot = resolve(repo);
  const pendingRoot = resolve(repoRoot, 'pending');
  const skillDirectories = findSkillDirectories(pendingRoot);
  const resolved = skillDirectories
    .map((skillDir) => resolveSkill(repoRoot, pendingRoot, skillDir))
    .sort((left, right) => {
      if (left.layout !== right.layout) return left.layout === 'nested' ? -1 : 1;
      return left.source.localeCompare(right.source);
    });
  const seenTargets = new Set();
  for (const entry of resolved) {
    if (seenTargets.has(entry.target)) {
      throw new Error(`multiple pending skills resolve to the same target: ${entry.target}`);
    }
    seenTargets.add(entry.target);
  }
  return resolved;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const resolved = resolvePendingSkills(options.repo);
  if (options.format === 'json') {
    process.stdout.write(`${JSON.stringify(resolved, null, 2)}\n`);
    return;
  }
  for (const entry of resolved) {
    process.stdout.write(`${entry.source}\t${entry.target}\t${entry.author}\t${entry.slug}\t${entry.layout}\n`);
  }
}

try {
  main();
} catch (error) {
  console.error(`::error::${error.message}`);
  process.exitCode = 1;
}
