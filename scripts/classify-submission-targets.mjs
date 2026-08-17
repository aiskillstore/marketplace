#!/usr/bin/env node

import {
  lstatSync,
  readFileSync,
  readdirSync,
} from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { validateSlugAliasRegistry } from './discover-submission-skills.mjs';
import { calculateCanonicalTreeHash } from './resolve-approved-submission.mjs';
import { parseSelectionPlan, validateSelectionPlan } from './submission-selection-plan.mjs';

const SOURCE_TYPES = new Set(['community', 'official']);
// Must stay aligned with the exact CLI 2.15.7 trust allowlist pinned by the workflow.
const OFFICIAL_REPOSITORIES = new Set([
  'aiskillstore/marketplace',
  'anthropics/skills',
  'openai/codex',
]);
const CONTROL = /[\u0000-\u001f\u007f-\u009f]/u;
const HASH = /^[a-f0-9]{64}$/;
const RISK_LEVELS = new Set(['safe', 'low', 'medium', 'high', 'critical']);

class SourceIdentityMismatchError extends Error {}

function fail(message) {
  throw new Error(message);
}

function option(args, name) {
  const index = args.indexOf(name);
  if (index === -1) fail(`missing required option ${name}`);
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

function lstatIfPresent(path) {
  try {
    return lstatSync(path);
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
}

function assertDirectory(path, label) {
  const stat = lstatIfPresent(path);
  if (stat === null) fail(`${label} is missing: ${path}`);
  if (stat.isSymbolicLink() || !stat.isDirectory()) fail(`${label} must be a non-symlink directory: ${path}`);
}

function assertRegularFile(path, label) {
  const stat = lstatIfPresent(path);
  if (stat === null) fail(`${label} is missing: ${path}`);
  if (stat.isSymbolicLink() || !stat.isFile()) fail(`${label} must be a non-symlink regular file: ${path}`);
}

function pathState(root, relativePath, label) {
  let current = root;
  const segments = relativePath.split('/');
  for (const [index, segment] of segments.entries()) {
    current = join(current, segment);
    const stat = lstatIfPresent(current);
    if (stat === null) return null;
    if (stat.isSymbolicLink()) fail(`${label} contains a symlink path component: ${relativePath}`);
    if (index < segments.length - 1 && !stat.isDirectory()) {
      fail(`${label} contains a non-directory ancestor: ${relativePath}`);
    }
  }
  return lstatSync(current);
}

function assertSafeTree(root, label) {
  assertDirectory(root, label);
  const walk = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) fail(`${label} contains symlink: ${path}`);
      if (stat.isDirectory()) walk(path);
      else if (!stat.isFile()) fail(`${label} contains a non-regular entry: ${path}`);
    }
  };
  walk(root);
}

function readReport(path) {
  assertRegularFile(path, 'published skill report');
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    fail(`published skill report is malformed JSON at ${path}: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function assertObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
}

function assertString(value, label) {
  if (typeof value !== 'string' || value === '') fail(`${label} must be a non-empty string`);
}

function assertReportContract(report, reportPath) {
  assertObject(report, `published skill report at ${reportPath}`);
  if (report.schema_version !== '2.0') fail(`published skill report schema_version must be 2.0 at ${reportPath}`);
  assertObject(report.meta, `published skill report meta at ${reportPath}`);
  for (const field of ['generated_at', 'slug', 'source_url', 'source_ref', 'model', 'analysis_version', 'source_type']) {
    assertString(report.meta[field], `published skill report meta.${field} at ${reportPath}`);
  }
  if (!SOURCE_TYPES.has(report.meta.source_type)) fail(`published skill report has an invalid source_type at ${reportPath}`);
  if (Number.isNaN(Date.parse(report.meta.generated_at))) fail(`published skill report has an invalid generated_at at ${reportPath}`);
  for (const field of ['content_hash', 'tree_hash']) {
    if (report.meta[field] !== undefined && (typeof report.meta[field] !== 'string' || !HASH.test(report.meta[field]))) {
      fail(`published skill report meta.${field} is invalid at ${reportPath}`);
    }
  }

  assertObject(report.skill, `published skill report skill at ${reportPath}`);
  assertString(report.skill.name, `published skill report skill.name at ${reportPath}`);
  if (typeof report.skill.description !== 'string' || !Array.isArray(report.skill.supported_tools)) {
    fail(`published skill report skill contract is incomplete at ${reportPath}`);
  }

  assertObject(report.security_audit, `published skill report security_audit at ${reportPath}`);
  const audit = report.security_audit;
  if (!RISK_LEVELS.has(audit.risk_level) || typeof audit.is_blocked !== 'boolean'
    || typeof audit.safe_to_publish !== 'boolean' || typeof audit.summary !== 'string'
    || !Number.isInteger(audit.files_scanned) || audit.files_scanned < 0
    || !Number.isInteger(audit.total_lines) || audit.total_lines < 0
    || typeof audit.audit_model !== 'string' || typeof audit.audited_at !== 'string'
    || Number.isNaN(Date.parse(audit.audited_at))) {
    fail(`published skill report security_audit contract is incomplete at ${reportPath}`);
  }

  assertObject(report.content, `published skill report content at ${reportPath}`);
  for (const field of ['user_title', 'value_statement']) {
    if (typeof report.content[field] !== 'string') fail(`published skill report content.${field} must be a string at ${reportPath}`);
  }
  for (const field of [
    'seo_keywords', 'actual_capabilities', 'limitations', 'use_cases', 'prompt_templates',
    'output_examples', 'best_practices', 'anti_patterns', 'faq',
  ]) {
    if (!Array.isArray(report.content[field])) fail(`published skill report content.${field} must be an array at ${reportPath}`);
  }
}

function decodeSourceSegment(segment, url) {
  let decoded;
  try {
    decoded = decodeURIComponent(segment);
  } catch {
    fail(`published skill report source_url contains invalid percent encoding: ${url}`);
  }
  if (decoded === '' || decoded !== decoded.normalize('NFC') || CONTROL.test(decoded)
    || decoded === '.' || decoded === '..' || decoded.startsWith('-') || decoded.includes('\\')) {
    fail(`published skill report source_url contains an unsafe segment: ${url}`);
  }
  return decoded;
}

function decodedSegments(url) {
  const authorityStart = url.indexOf('//');
  const pathStart = url.indexOf('/', authorityStart === -1 ? 0 : authorityStart + 2);
  const rawPath = pathStart === -1 ? '' : url.slice(pathStart).split(/[?#]/, 1)[0];
  for (const rawSegment of rawPath.split('/').filter(Boolean)) decodeSourceSegment(rawSegment, url);

  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    fail(`published skill report has an invalid source_url: ${JSON.stringify(url)}`);
  }
  if (parsed.protocol !== 'https:' || parsed.hostname !== 'github.com'
    || parsed.username !== '' || parsed.password !== '' || parsed.port !== ''
    || parsed.search !== '' || parsed.hash !== '') {
    fail(`published skill report source_url must be a canonical HTTPS GitHub URL: ${url}`);
  }
  return parsed.pathname.split('/').filter(Boolean).map((segment) => decodeSourceSegment(segment, url));
}

function sourceMismatch(message) {
  throw new SourceIdentityMismatchError(message);
}

function assertSourceIdentity(report, { repository }, reportPath) {
  const sourceUrl = report?.meta?.source_url;
  const reportRef = report?.meta?.source_ref;
  if (typeof sourceUrl !== 'string' || typeof reportRef !== 'string' || reportRef === '') {
    fail(`published skill report is missing source_url or source_ref: ${reportPath}`);
  }

  const segments = decodedSegments(sourceUrl);
  const [owner, repo, kind, actualRef, ...actualPathSegments] = segments;
  if (`${owner ?? ''}/${repo ?? ''}` !== repository || kind !== 'tree') {
    sourceMismatch(`published target source repository mismatch at ${reportPath}: expected ${repository}`);
  }
  if (actualRef === undefined) {
    fail(`published target source_url has no source ref at ${reportPath}`);
  }
  if (actualPathSegments.some((segment) => segment.includes('/'))) {
    fail(`published target source_url encodes a path separator inside a path segment at ${reportPath}`);
  }
  if (actualRef !== reportRef) {
    fail(`published target source_url does not match source_ref at ${reportPath}`);
  }
  const sourcePath = actualPathSegments.join('/');
  const canonicalPath = `/${repository}/tree/${encodeURIComponent(reportRef)}${sourcePath === ''
    ? ''
    : `/${actualPathSegments.map((segment) => encodeURIComponent(segment)).join('/')}`}`;
  const parsedPath = new URL(sourceUrl).pathname;
  if (parsedPath !== canonicalPath && parsedPath !== `${canonicalPath}/`) {
    fail(`published target source_url is not canonical at ${reportPath}`);
  }
  return { sourcePath, sourceRef: reportRef };
}

function validateCandidate(candidate, identity) {
  assertSafeTree(candidate.directory, 'published skill target');
  assertRegularFile(join(candidate.directory, 'SKILL.md'), 'published SKILL.md');
  const reportPath = join(candidate.directory, 'skill-report.json');
  const report = readReport(reportPath);
  assertReportContract(report, reportPath);

  const expectedReportSlug = candidate.layout === 'community'
    ? `${identity.owner}-${identity.slug}`
    : identity.slug;
  if (report?.meta?.slug !== expectedReportSlug) {
    fail(`published target report slug mismatch at ${reportPath}: expected ${expectedReportSlug}`);
  }
  if (report?.skill?.name !== identity.expectedName) {
    fail(`published target skill name mismatch at ${reportPath}: expected ${identity.expectedName}`);
  }
  if (candidate.layout === 'community') {
    if (report.meta.source_type !== 'community') {
      fail(`namespaced published target must be community at ${reportPath}`);
    }
    if (typeof report?.skill?.author !== 'string'
      || report.skill.author.toLowerCase() !== identity.owner.toLowerCase()) {
      fail(`published target author mismatch at ${reportPath}: expected ${identity.owner}`);
    }
  } else if (report.meta.source_type !== 'official') {
    fail(`flat published target must be official at ${reportPath}`);
  }

  const sourceIdentity = assertSourceIdentity(report, identity, reportPath);
  return {
    directory: candidate.directory,
    relativePath: candidate.relativePath,
    ...sourceIdentity,
  };
}

function assertNoPendingCollision(root, owner, slug) {
  for (const relativePath of [`pending/${owner}/${slug}`, `pending/${slug}`]) {
    if (pathState(root, relativePath, 'pending target') !== null) {
      fail(`pending target collision: ${relativePath}`);
    }
  }
}

export function classifySubmissionTargets({
  marketplaceRoot,
  selectionPlan,
  slugAliasRegistry = { schemaVersion: 1, aliases: [] },
}) {
  const plan = typeof selectionPlan === 'string'
    ? parseSelectionPlan(selectionPlan)
    : validateSelectionPlan(selectionPlan);
  assertDirectory(marketplaceRoot, 'marketplace root');
  const root = resolve(marketplaceRoot);
  const sourceRef = plan.sourceCommit;

  const [owner] = plan.repository.split('/');
  const aliases = new Map(validateSlugAliasRegistry(slugAliasRegistry)
    .filter((alias) => alias.repository === plan.repository)
    .map((alias) => [alias.path, alias]));
  const expectedLayout = OFFICIAL_REPOSITORIES.has(plan.repository) ? 'official' : 'community';
  const existingTargets = [];
  const sameRevisionTargets = [];
  const updateTargets = [];
  const updateSnapshots = [];
  const processingSkills = [];
  const newTargets = [];

  for (const skill of plan.skills) {
    const alias = aliases.get(skill.path);
    if (alias && alias.baseSlug !== skill.slug) {
      fail(`slug alias does not match planned slug for ${skill.path}: expected ${alias.baseSlug}`);
    }
    assertNoPendingCollision(root, owner, skill.slug);
    const identity = {
      repository: plan.repository,
      sourceRef,
      skillPath: skill.path,
      owner,
      slug: skill.slug,
      expectedName: alias?.expectedName ?? skill.slug,
    };
    const candidates = [
      {
        layout: 'community',
        relativePath: `skills/${owner}/${skill.slug}`,
        directory: join(root, 'skills', owner, skill.slug),
      },
      {
        layout: 'official',
        relativePath: `skills/${skill.slug}`,
        directory: join(root, 'skills', skill.slug),
      },
    ];
    const expectedCandidate = candidates.find(({ layout }) => layout === expectedLayout);
    const present = candidates.filter(({ layout, relativePath }) => {
      const state = pathState(root, relativePath, 'published target');
      if (state === null) return false;
      if (layout === expectedLayout || !state.isDirectory()) return true;
      return pathState(root, `${relativePath}/SKILL.md`, 'alternate published target') !== null
        || pathState(root, `${relativePath}/skill-report.json`, 'alternate published target') !== null;
    });
    const presentExpected = present.find(({ layout }) => layout === expectedLayout);
    let expectedTarget = null;
    if (presentExpected !== undefined) {
      expectedTarget = validateCandidate(presentExpected, identity);
    }

    const alternate = present.find(({ layout }) => layout !== expectedLayout);
    let alternateExact = null;
    if (alternate !== undefined) {
      try {
        alternateExact = validateCandidate(alternate, identity);
      } catch (error) {
        if (!(error instanceof SourceIdentityMismatchError)) throw error;
        // A structurally valid target from another source is valid in the alternate namespace.
      }
    }

    if (expectedTarget !== null && alternateExact !== null) {
      fail(`ambiguous published target identity for ${skill.slug}: ${expectedTarget.relativePath}, ${alternateExact.relativePath}`);
    }
    if (expectedTarget === null && alternateExact !== null) {
      fail(`published target identity for ${skill.slug} exists at unexpected path: ${alternateExact.relativePath}`);
    }
    if (expectedTarget !== null) {
      existingTargets.push(expectedTarget.relativePath);
      if (expectedTarget.sourceRef === sourceRef && expectedTarget.sourcePath === skill.path) {
        sameRevisionTargets.push(expectedTarget.relativePath);
      } else {
        const treeHash = calculateCanonicalTreeHash(root, expectedTarget.relativePath);
        updateTargets.push(expectedTarget.relativePath);
        processingSkills.push(skill);
        updateSnapshots.push({
          targetDir: expectedTarget.relativePath,
          treeHash,
          sourceRef: expectedTarget.sourceRef,
        });
      }
      continue;
    }
    newTargets.push(expectedCandidate.relativePath);
    processingSkills.push(skill);
  }

  const disposition = sameRevisionTargets.length === plan.skills.length && plan.skills.length > 0
    ? 'all_existing'
    : 'processable';
  let reasonCode = 'no_selected_targets_already_published';
  if (disposition === 'all_existing') reasonCode = 'all_selected_targets_already_published';
  else if (updateTargets.length === plan.skills.length) reasonCode = 'all_selected_targets_are_updates';
  else if (updateTargets.length > 0 && newTargets.length > 0) reasonCode = 'selected_targets_include_new_and_updates';
  else if (updateTargets.length > 0) reasonCode = 'selected_targets_include_updates';
  else if (newTargets.length < plan.skills.length) reasonCode = 'selected_targets_include_new';
  const result = {
    schemaVersion: 1,
    disposition,
    reasonCode,
    selectedCount: plan.skills.length,
    processingPlan: { ...plan, skills: processingSkills },
    existingCount: existingTargets.length,
    existingTargets: existingTargets.sort((left, right) => left.localeCompare(right, 'en')),
    updateTargets: updateTargets.sort((left, right) => left.localeCompare(right, 'en')),
  };
  if (updateSnapshots.length > 0) result.updateSnapshots = updateSnapshots;
  return result;
}

function main() {
  const args = process.argv.slice(2);
  const selectionPlanPath = option(args, '--selection-plan');
  const slugAliasesPath = option(args, '--slug-aliases-file');
  const result = classifySubmissionTargets({
    marketplaceRoot: option(args, '--marketplace-root'),
    selectionPlan: readFileSync(selectionPlanPath, 'utf8'),
    slugAliasRegistry: JSON.parse(readFileSync(slugAliasesPath, 'utf8')),
  });
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  try {
    main();
  } catch (error) {
    console.error(`::error::Submission target classification failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  }
}
