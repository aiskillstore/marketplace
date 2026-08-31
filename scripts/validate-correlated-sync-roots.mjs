#!/usr/bin/env node
import { execFileSync } from 'node:child_process';

const SHA_RE = /^[0-9a-f]{40}$/u;
const SEGMENT_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/u;

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
}

function parseArgs(argv) {
  const values = new Map();
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith('--') || value == null) throw new Error('expected --merge, --current and --slugs');
    values.set(key.slice(2), value);
  }
  const merge = values.get('merge');
  const current = values.get('current');
  const slugs = (values.get('slugs') ?? '').split(/[\s,]+/u).filter(Boolean);
  if (!SHA_RE.test(merge ?? '') || !SHA_RE.test(current ?? '') || slugs.length === 0 || slugs.length > 25) {
    throw new Error('invalid correlated sync root arguments');
  }
  const uniqueSlugs = [...new Set(slugs)].sort();
  if (uniqueSlugs.length !== slugs.length || uniqueSlugs.some((slug) => {
    const segments = slug.split('/');
    return ![1, 2].includes(segments.length) || segments.some((segment) => !SEGMENT_RE.test(segment));
  })) throw new Error('invalid canonical correlated sync slugs');
  return { merge, current, slugs: uniqueSlugs };
}

function gitObject(commit, path) {
  return execFileSync('git', ['rev-parse', '--verify', `${commit}:${path}`], {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  }).trim();
}

try {
  const { merge, current, slugs } = parseArgs(process.argv.slice(2));
  for (const slug of slugs) {
    const root = `skills/${slug}`;
    const mergeObject = gitObject(merge, root);
    const currentObject = gitObject(current, root);
    const mergeType = execFileSync('git', ['cat-file', '-t', mergeObject], { encoding: 'utf8' }).trim();
    const currentType = execFileSync('git', ['cat-file', '-t', currentObject], { encoding: 'utf8' }).trim();
    if (mergeType !== 'tree' || currentType !== 'tree') throw new Error(`correlated provider sync root is not a tree: ${root}`);
    if (mergeObject !== currentObject) throw new Error(`correlated provider sync root changed after the marker-bound merge: ${root}`);
  }
  process.stdout.write(`${merge}\n`);
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}
