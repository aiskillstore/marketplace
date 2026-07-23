#!/usr/bin/env node

import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { LineCounter, parseDocument } from 'yaml';

function workflowFiles(root) {
  const directory = join(root, '.github', 'workflows');
  return readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isFile() && /\.ya?ml$/i.test(entry.name))
    .map((entry) => join(directory, entry.name))
    .sort();
}

function eventConfig(on, name) {
  if (typeof on === 'string') return on === name ? {} : null;
  if (Array.isArray(on)) return on.includes(name) ? {} : null;
  if (on && typeof on === 'object' && Object.hasOwn(on, name)) return on[name] ?? {};
  return null;
}

function expressionText(value) {
  return typeof value === 'string'
    ? value.replace(/^\s*\$\{\{/, '').replace(/\}\}\s*$/, '').trim()
    : '';
}

function excludesPullRequest(condition) {
  const expression = expressionText(condition);
  if (!expression || /\|\|/.test(expression)) return false;
  return (
    /github\.event_name\s*!=\s*['"]pull_request['"]/.test(expression) ||
    /github\.event_name\s*==\s*['"](?:workflow_dispatch|push|schedule|workflow_run|repository_dispatch)['"]/.test(expression) ||
    /['"](?:workflow_dispatch|push|schedule|workflow_run|repository_dispatch)['"]\s*==\s*github\.event_name/.test(expression)
  );
}

function isSelfHosted(runsOn) {
  if (typeof runsOn === 'string') return /self-hosted/i.test(runsOn);
  return Array.isArray(runsOn) && runsOn.some((label) => typeof label === 'string' && /self-hosted/i.test(label));
}

function isGithubHosted(runsOn) {
  if (typeof runsOn !== 'string' || runsOn.includes('${{')) return false;
  return /^(?:ubuntu-(?:latest|\d{2}\.\d{2})|windows-(?:latest|\d{4})|macos-(?:latest|\d+))$/.test(runsOn);
}

function permissionsAreReadOnly(permissions) {
  if (!permissions || typeof permissions !== 'object' || Array.isArray(permissions)) return false;
  if (permissions.contents !== 'read') return false;
  return Object.values(permissions).every((value) => value === 'read' || value === 'none');
}

function pullRequestTypes(config) {
  if (!config || typeof config !== 'object' || Array.isArray(config)) return [];
  const types = config.types;
  if (typeof types === 'string') return [types];
  return Array.isArray(types) ? types : [];
}

function trustedClosedMergeMetadataJob(pullRequest, job) {
  const types = pullRequestTypes(pullRequest);
  if (types.length !== 1 || types[0] !== 'closed') return false;
  const condition = expressionText(job.if);
  if (!/github\.event\.pull_request\.merged\s*==\s*true/.test(condition)) return false;
  const serialized = JSON.stringify(job);
  if (/github\.event\.pull_request\.head\.(?:sha|ref|repo)/.test(serialized)) return false;
  return true;
}

function stepUses(step) {
  return typeof step?.uses === 'string' ? step.uses : '';
}

function checkoutStep(step) {
  return /^actions\/checkout@[0-9a-f]{40}$/i.test(stepUses(step));
}

function lineOf(document, lineCounter, path) {
  let node = document.contents;
  for (const segment of path) {
    if (!node || typeof node.get !== 'function') return 1;
    node = node.get(segment, true);
  }
  const offset = node?.range?.[0];
  return Number.isInteger(offset) ? lineCounter.linePos(offset).line : 1;
}

function add(violations, file, line, message) {
  violations.push({ file, line, message });
}

function inspectWorkflow(root, path) {
  const file = relative(root, path).replaceAll('\\', '/');
  const source = readFileSync(path, 'utf8');
  const lineCounter = new LineCounter();
  const document = parseDocument(source, {
    lineCounter,
    prettyErrors: false,
    strict: true,
    uniqueKeys: true,
  });
  const violations = [];
  if (document.errors.length > 0) {
    for (const error of document.errors) {
      const line = error.linePos?.[0]?.line ?? 1;
      add(violations, file, line, `YAML parse error: ${error.message}`);
    }
    return violations;
  }

  const workflow = document.toJS({ maxAliasCount: 100 });
  const pullRequest = eventConfig(workflow.on, 'pull_request');
  const pullRequestTarget = eventConfig(workflow.on, 'pull_request_target');
  const jobs = workflow.jobs && typeof workflow.jobs === 'object' ? workflow.jobs : {};

  for (const [jobName, job] of Object.entries(jobs)) {
    if (!job || typeof job !== 'object') continue;
    const jobLine = lineOf(document, lineCounter, ['jobs', jobName]);

    if (pullRequest !== null && !excludesPullRequest(job.if)) {
      const trustedMetadata = trustedClosedMergeMetadataJob(pullRequest, job);
      if (isSelfHosted(job['runs-on']) && !trustedMetadata) {
        add(
          violations,
          file,
          jobLine,
          `pull_request job ${jobName} can execute fork code on self-hosted; use a GitHub-hosted runner`,
        );
      } else if (!isSelfHosted(job['runs-on']) && !isGithubHosted(job['runs-on'])) {
        add(
          violations,
          file,
          jobLine,
          `pull_request job ${jobName} must use a literal GitHub-hosted runner, not a dynamic or unknown runs-on value`,
        );
      }

      if (!trustedMetadata) {
        const effectivePermissions = job.permissions ?? workflow.permissions;
        if (!permissionsAreReadOnly(effectivePermissions)) {
          add(
            violations,
            file,
            jobLine,
            `pull_request job ${jobName} must set permissions to contents: read with no write permission`,
          );
        }

        for (const [index, step] of (job.steps ?? []).entries()) {
          if (!step || typeof step !== 'object' || excludesPullRequest(step.if)) continue;
          const stepLine = lineOf(document, lineCounter, ['jobs', jobName, 'steps', index]);
          const serialized = JSON.stringify(step);
          if (/secrets\./.test(serialized) || /^actions\/create-github-app-token@/i.test(stepUses(step))) {
            add(
              violations,
              file,
              stepLine,
              `pull_request job ${jobName} has a fork-reachable secret or App token step`,
            );
          }
          if (checkoutStep(step) && step.with?.['persist-credentials'] !== false) {
            add(
              violations,
              file,
              stepLine,
              `pull_request checkout in ${jobName} must set persist-credentials: false`,
            );
          }
        }
      }
    }

    if (pullRequestTarget !== null && !excludesPullRequest(job.if)) {
      for (const [index, step] of (job.steps ?? []).entries()) {
        if (!step || typeof step !== 'object' || excludesPullRequest(step.if)) continue;
        const stepLine = lineOf(document, lineCounter, ['jobs', jobName, 'steps', index]);
        const serialized = JSON.stringify(step);
        if (
          checkoutStep(step) ||
          /github\.event\.pull_request\.head\.(?:sha|ref|repo)/.test(serialized) ||
          /github\.head_ref|github\.event\.pull_request\.head\.label/.test(serialized)
        ) {
          add(
            violations,
            file,
            stepLine,
            `pull_request_target must remain metadata-only and must not checkout or execute fork head data`,
          );
        }
      }
    }
  }

  return violations;
}

export function inspectWorkflowRunnerSafety(root) {
  const violations = [];
  for (const path of workflowFiles(root)) {
    const metadata = lstatSync(path);
    if (!metadata.isFile()) {
      violations.push({
        file: relative(root, path).replaceAll('\\', '/'),
        line: 1,
        message: 'workflow must be a regular file',
      });
      continue;
    }
    violations.push(...inspectWorkflow(root, path));
  }
  return violations;
}

function main() {
  const args = process.argv.slice(2);
  const rootIndex = args.indexOf('--root');
  const root = resolve(rootIndex === -1 ? process.cwd() : args[rootIndex + 1]);
  if (rootIndex !== -1 && !args[rootIndex + 1]) {
    console.error('--root requires a directory');
    process.exitCode = 2;
    return;
  }
  const violations = inspectWorkflowRunnerSafety(root);
  if (violations.length > 0) {
    for (const violation of violations) {
      console.error(`::error file=${violation.file},line=${violation.line}::${violation.message}`);
    }
    process.exitCode = 1;
    return;
  }
  console.log(`Workflow runner safety policy passed (${workflowFiles(root).length} workflows checked).`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  main();
}
