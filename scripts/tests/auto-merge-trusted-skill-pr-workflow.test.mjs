import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const WORKFLOW_PATH = resolve(ROOT, '.github/workflows/auto-merge-trusted-skill-pr.yml');
const PUBLISH_WORKFLOW_PATH = resolve(ROOT, '.github/workflows/on-pr-merge.yml');
const source = readFileSync(WORKFLOW_PATH, 'utf8');
const publishSource = readFileSync(PUBLISH_WORKFLOW_PATH, 'utf8');
const workflow = parse(source);
const trigger = workflow.on ?? workflow.true;

test('uses only the trusted default-branch validation workflow_run event', () => {
  assert.deepEqual(Object.keys(trigger), ['workflow_run']);
  assert.deepEqual(trigger.workflow_run.workflows, ['Validate Marketplace']);
  assert.deepEqual(trigger.workflow_run.types, ['completed']);
  assert.doesNotMatch(source, /pull_request_target|\bworkflow_dispatch\b/);
});

test('uses a literal hosted runner, non-cancelling serialization and exact minimal permissions', () => {
  assert.deepEqual(workflow.permissions, {
    actions: 'write',
    checks: 'read',
    contents: 'write',
    'pull-requests': 'write',
    statuses: 'read',
  });
  assert.equal(workflow.concurrency['cancel-in-progress'], false);
  assert.match(workflow.concurrency.group, /workflow_run\.head_sha/);
  const job = workflow.jobs['auto-merge'];
  assert.equal(job['runs-on'], 'ubuntu-latest');
  assert.match(job.if, /workflow_run\.event == 'pull_request'/);
  assert.ok(Number.parseInt(job['timeout-minutes'], 10) <= 15);
});

test('checks out only the trusted workflow SHA without credentials and executes the bounded helper', () => {
  const steps = workflow.jobs['auto-merge'].steps;
  const checkout = steps.find((step) => step.uses?.startsWith('actions/checkout@'));
  assert.match(checkout.uses, /^actions\/checkout@[0-9a-f]{40}$/);
  assert.equal(checkout.with.ref, '${{ github.sha }}');
  assert.equal(checkout.with['persist-credentials'], false);
  assert.ok(steps.every((step) => !String(step.with?.ref ?? '').includes('workflow_run.head_sha')));
  const run = steps.find((step) => step.run)?.run ?? '';
  assert.match(run, /^node scripts\/auto-merge-trusted-skill-pr\.mjs$/m);
  assert.equal(steps.find((step) => step.run).env.GH_TOKEN, '${{ github.token }}');
  assert.equal(steps.find((step) => step.run).env.GITHUB_RUN_ID, '${{ github.run_id }}');
  assert.equal(steps.find((step) => step.run).env.WORKFLOW_RUN_ID, '${{ github.event.workflow_run.id }}');
});

test('contains no bypass, force-push, auto-merge or untrusted PR execution path', () => {
  assert.doesNotMatch(source, /--admin|--auto|force-with-lease|git push|pull\/\$\{|workflow_run\.head_repository|workflow_run\.head_branch/);
});

test('post-merge recovery accepts the exact GitHub Actions bot merger identity', () => {
  assert.match(publishSource, /github-actions\\\[bot\\\]/);
});
