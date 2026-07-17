#!/usr/bin/env node

import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

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

function decodePathSegment(raw) {
  let decoded;
  try {
    decoded = decodeURIComponent(raw);
  } catch {
    fail(`GitHub URL contains invalid percent encoding: ${raw}`);
  }
  if (decoded === '' || decoded === '.' || decoded === '..' || decoded.includes('\\') || decoded.includes('\0')) {
    fail(`GitHub URL contains an unsafe path segment: ${raw}`);
  }
  return decoded;
}

function parseRemoteRefs(text) {
  const refs = new Map();
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line === '') continue;
    const match = line.match(/^([0-9a-f]{40,64})\s+refs\/(heads|tags)\/(.+)$/);
    if (!match) fail(`invalid git ls-remote line: ${line}`);
    const [, sha, type, rawName] = match;
    const peeled = type === 'tags' && rawName.endsWith('^{}');
    const name = peeled ? rawName.slice(0, -3) : rawName;
    const key = `${type}:${name}`;
    if (refs.has(key) && refs.get(key).sha !== sha && !peeled) {
      fail(`remote ref is not unique: refs/${type}/${name}`);
    }
    if (!refs.has(key) || peeled) refs.set(key, { sha, peeled });
  }
  return refs;
}

function matchesForCandidate(refs, candidate) {
  const matches = [];
  for (const type of ['heads', 'tags']) {
    const key = `${type}:${candidate}`;
    if (refs.has(key)) matches.push({ type, name: candidate, sha: refs.get(key).sha });
  }
  return matches;
}

function normalizedTreeUrl(owner, repo, ref, skillPath) {
  const encodedRef = encodeURIComponent(ref);
  const encodedPath = skillPath.map((segment) => encodeURIComponent(segment)).join('/');
  return `https://github.com/${owner}/${repo}/tree/${encodedRef}${encodedPath === '' ? '' : `/${encodedPath}`}`;
}

export function parseGitHubRepository(githubUrl) {
  const authorityStart = githubUrl.indexOf('//');
  const rawPathStart = githubUrl.indexOf('/', authorityStart === -1 ? 0 : authorityStart + 2);
  const rawPath = rawPathStart === -1 ? '' : githubUrl.slice(rawPathStart).split(/[?#]/, 1)[0];
  for (const rawSegment of rawPath.split('/').filter(Boolean)) decodePathSegment(rawSegment);

  let parsed;
  try {
    parsed = new URL(githubUrl);
  } catch {
    fail(`invalid GitHub URL: ${githubUrl}`);
  }
  if (parsed.protocol !== 'https:' || parsed.hostname.toLowerCase() !== 'github.com'
      || parsed.username !== '' || parsed.password !== '' || parsed.port !== ''
      || parsed.search !== '' || parsed.hash !== '') {
    fail(`GitHub URL must be a plain https://github.com URL: ${githubUrl}`);
  }

  const rawSegments = parsed.pathname.split('/').filter(Boolean);
  if (rawSegments.length < 2) fail(`GitHub URL must include owner and repository: ${githubUrl}`);
  const segments = rawSegments.map(decodePathSegment);
  const owner = segments[0];
  const repo = segments[1].replace(/\.git$/i, '');
  if (!/^[A-Za-z0-9_-]+$/.test(owner) || !/^[A-Za-z0-9._-]+$/.test(repo) || repo === '') {
    fail(`invalid GitHub owner or repository: ${owner}/${repo}`);
  }
  return { owner, repo, segments };
}

export function resolveSubmissionSource({ githubUrl, defaultRef, refsText }) {
  const { owner, repo, segments } = parseGitHubRepository(githubUrl);

  const refs = parseRemoteRefs(refsText);
  const mode = segments[2] ?? null;
  if (mode !== null && mode !== 'tree' && mode !== 'blob') {
    fail(`unsupported GitHub URL path; expected repository, tree, or blob URL: ${githubUrl}`);
  }

  if (mode === null) {
    if (segments.length !== 2) fail(`unsupported GitHub repository URL: ${githubUrl}`);
    const matches = matchesForCandidate(refs, defaultRef).filter(({ type }) => type === 'heads');
    if (matches.length !== 1) fail(`default branch is not an exact remote head: ${defaultRef}`);
    return {
      schemaVersion: 1,
      owner,
      repo,
      ref: defaultRef,
      refType: 'heads',
      refSha: matches[0].sha,
      skillPath: '',
      explicitPath: false,
      normalizedUrl: normalizedTreeUrl(owner, repo, defaultRef, []),
    };
  }

  const tail = segments.slice(3);
  if (tail.length === 0) fail(`GitHub ${mode} URL is missing a ref: ${githubUrl}`);
  const candidates = [];
  for (let split = 1; split <= tail.length; split += 1) {
    const candidate = tail.slice(0, split).join('/');
    for (const match of matchesForCandidate(refs, candidate)) {
      candidates.push({ ...match, split });
    }
  }
  if (candidates.length === 0) fail(`GitHub URL ref does not exist: ${tail.join('/')}`);
  if (candidates.length !== 1) {
    fail(`GitHub tree URL is ambiguous across refs: ${candidates.map(({ type, name }) => `${type}/${name}`).join(', ')}`);
  }

  const selected = candidates[0];
  let skillPath = tail.slice(selected.split);
  if (mode === 'blob') {
    if (skillPath.length === 0) fail('GitHub blob URL is missing a file path');
    const file = skillPath.at(-1);
    if (file.toLowerCase() !== 'skill.md') fail(`submission blob URL must point to SKILL.md, got ${file}`);
    skillPath = skillPath.slice(0, -1);
  }
  return {
    schemaVersion: 1,
    owner,
    repo,
    ref: selected.name,
    refType: selected.type,
    refSha: selected.sha,
    skillPath: skillPath.join('/'),
    explicitPath: skillPath.length > 0,
    normalizedUrl: normalizedTreeUrl(owner, repo, selected.name, skillPath),
  };
}

function main() {
  const args = process.argv.slice(2);
  const githubUrl = option(args, '--github-url');
  if (args.includes('--repository-only')) {
    const { owner, repo } = parseGitHubRepository(githubUrl);
    process.stdout.write(`${JSON.stringify({ owner, repo })}\n`);
    return;
  }
  const result = resolveSubmissionSource({
    githubUrl,
    defaultRef: option(args, '--default-ref'),
    refsText: readFileSync(option(args, '--refs-file'), 'utf8'),
  });
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Submission source resolution failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
