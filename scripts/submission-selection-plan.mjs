#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const REPOSITORY = /^[a-z0-9][a-z0-9_.-]*\/[a-z0-9][a-z0-9_.-]*$/;
const COMMIT = /^[0-9a-f]{40,64}$/;
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const CONTROL = /[\u0000-\u001f\u007f-\u009f]/u;
const WINDOWS_RESERVED = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?$/i;

function fail(message) { throw new Error(message); }

function option(args, name, { required = true } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) fail(`missing required option ${name}`);
    return null;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

export function validatePortablePath(value, label, { rootSentinel = false } = {}) {
  if (rootSentinel && value === '.') return value;
  if (typeof value !== 'string' || value === '' || value !== value.normalize('NFC')
    || CONTROL.test(value) || /[<>:"|?*\\$'"`;%]/u.test(value) || value.startsWith('/') || value.startsWith('-')) {
    fail(`${label} must be a non-empty NFC, control-free, repository-relative POSIX path`);
  }
  for (const segment of value.split('/')) {
    if (segment === '' || segment === '.' || segment === '..' || segment.startsWith('-')
      || segment.endsWith('.') || segment.endsWith(' ') || WINDOWS_RESERVED.test(segment)) {
      fail(`${label} contains an unsafe path segment or non-portable path segment`);
    }
  }
  return value;
}

function validateSkills(skills) {
  if (!Array.isArray(skills)) fail('selection plan skills must be an array');
  const slugs = new Set();
  const paths = new Set();
  const foldedPaths = new Set();
  const validatedPaths = [];
  for (const [index, skill] of skills.entries()) {
    if (!skill || typeof skill !== 'object' || Array.isArray(skill)
      || JSON.stringify(Object.keys(skill).sort()) !== JSON.stringify(['path', 'slug'])) {
      fail(`selection plan skill ${index} must contain only slug and path`);
    }
    if (typeof skill.slug !== 'string' || !SLUG.test(skill.slug) || slugs.has(skill.slug)) {
      fail(`selection plan has invalid or duplicate slug at skill ${index}`);
    }
    const path = validatePortablePath(skill.path, `selection plan skill ${index}.path`, { rootSentinel: true });
    if (paths.has(path)) fail(`selection plan has duplicate path ${path}`);
    const foldedPath = path.normalize('NFC').toLocaleLowerCase('en-US');
    if (foldedPaths.has(foldedPath)) fail(`selection plan has an NFC/case-fold path collision at ${path}`);
    for (const previous of validatedPaths) {
      if (previous.foldedPath === '.' || foldedPath === '.'
        || foldedPath.startsWith(`${previous.foldedPath}/`)
        || previous.foldedPath.startsWith(`${foldedPath}/`)) {
        fail(`selection plan skill paths overlap: ${previous.path} and ${path}`);
      }
    }
    slugs.add(skill.slug);
    paths.add(path);
    foldedPaths.add(foldedPath);
    validatedPaths.push({ path, foldedPath });
  }
  return skills.map(({ slug, path }) => ({ slug, path }));
}

export function validateSelectionPlan(plan) {
  if (!plan || typeof plan !== 'object' || Array.isArray(plan)
    || JSON.stringify(Object.keys(plan).sort()) !== JSON.stringify(['repository', 'schemaVersion', 'scope', 'skills', 'sourceCommit'])) {
    fail('selection plan has unknown or missing fields');
  }
  if (plan.schemaVersion !== 1) fail('selection plan schemaVersion must be 1');
  if (typeof plan.repository !== 'string' || !REPOSITORY.test(plan.repository)) fail('selection plan repository must be canonical owner/repo');
  if (typeof plan.sourceCommit !== 'string' || !COMMIT.test(plan.sourceCommit)) fail('selection plan sourceCommit must be a lowercase commit');
  if (!plan.scope || typeof plan.scope !== 'object' || Array.isArray(plan.scope)
    || JSON.stringify(Object.keys(plan.scope).sort()) !== JSON.stringify(['path', 'reason'])) {
    fail('selection plan scope must contain only path and reason');
  }
  const scope = {
    path: validatePortablePath(plan.scope.path, 'selection plan scope.path', { rootSentinel: true }),
    reason: plan.scope.reason,
  };
  if (!['explicit_path', 'codex_plugin_manifest', 'conventional_skills', 'repository_fallback'].includes(scope.reason)) {
    fail('selection plan scope.reason is invalid');
  }
  const skills = validateSkills(plan.skills);
  for (const { path } of skills) {
    if (scope.path !== '.' && path !== scope.path && !path.startsWith(`${scope.path}/`)) {
      fail(`selection plan skill path escapes scope: ${path}`);
    }
  }
  return { schemaVersion: 1, repository: plan.repository, sourceCommit: plan.sourceCommit, scope, skills };
}

export function parseSelectionPlan(text) {
  let plan;
  try { plan = JSON.parse(text); } catch (error) { fail(`cannot parse selection plan: ${error instanceof Error ? error.message : String(error)}`); }
  return validateSelectionPlan(plan);
}

function main() {
  const args = process.argv.slice(2);
  const input = readFileSync(option(args, '--input'), 'utf8');
  const plan = parseSelectionPlan(input);
  const output = option(args, '--output', { required: false });
  const serialized = `${JSON.stringify(plan)}\n`;
  if (output === null) process.stdout.write(serialized);
  else writeFileSync(output, serialized, { mode: 0o600 });
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try { main(); } catch (error) {
    console.error(`::error::Selection plan validation failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
