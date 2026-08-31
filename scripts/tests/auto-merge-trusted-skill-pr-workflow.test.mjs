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

test('uses trusted validation events plus bounded default-branch recovery triggers', () => {
  assert.deepEqual(Object.keys(trigger), ['workflow_run', 'schedule']);
  assert.deepEqual(trigger.workflow_run.workflows, ['Validate Marketplace']);
  assert.deepEqual(trigger.workflow_run.types, ['completed']);
  assert.deepEqual(trigger.schedule, [{ cron: '*/5 * * * *' }]);
  assert.doesNotMatch(source, /pull_request_target/);
});

test('uses a literal hosted runner, non-cancelling repository serialization and exact minimal permissions', () => {
  assert.deepEqual(workflow.permissions, {
    actions: 'write',
    checks: 'read',
    contents: 'write',
    'pull-requests': 'write',
    statuses: 'write',
  });
  assert.equal(workflow.concurrency['cancel-in-progress'], false);
  assert.equal(workflow.concurrency.group, 'trusted-skill-auto-merge-${{ github.repository }}');
  const job = workflow.jobs['auto-merge'];
  assert.equal(job['runs-on'], 'ubuntu-latest');
  assert.match(job.if, /github\.event_name == 'schedule'/);
  assert.match(job.if, /workflow_run\.event == 'pull_request'/);
  assert.ok(Number.parseInt(job['timeout-minutes'], 10) <= 15);
});

test('checks out only trusted automation and confines the event-capable App token to update-branch', () => {
  const steps = workflow.jobs['auto-merge'].steps;
  const checkout = steps.find((step) => step.uses?.startsWith('actions/checkout@'));
  assert.match(checkout.uses, /^actions\/checkout@[0-9a-f]{40}$/);
  assert.equal(checkout.with.ref, '${{ github.sha }}');
  assert.equal(checkout.with['persist-credentials'], false);
  assert.ok(steps.every((step) => !String(step.with?.ref ?? '').includes('workflow_run.head_sha')));
  const appToken = steps.find((step) => step.id === 'app-token');
  assert.match(appToken.uses, /^actions\/create-github-app-token@[0-9a-f]{40}$/);
  assert.equal(appToken.with['client-id'], '${{ vars.APP_CLIENT_ID }}');
  assert.equal(appToken.with['private-key'], '${{ secrets.APP_PRIVATE_KEY }}');
  assert.equal(appToken.with.repositories, 'marketplace');
  assert.equal(appToken.with['permission-contents'], 'write');
  assert.equal(appToken.with['permission-pull-requests'], 'write');
  const executor = steps.find((step) => step.run);
  assert.match(executor.run, /^node scripts\/auto-merge-trusted-skill-pr\.mjs$/m);
  assert.equal(executor.env.GH_TOKEN, '${{ github.token }}');
  assert.equal(executor.env.GH_UPDATE_TOKEN, '${{ steps.app-token.outputs.token }}');
  assert.equal(executor.env.GITHUB_RUN_ID, '${{ github.run_id }}');
  assert.equal(executor.env.WORKFLOW_RUN_ID, '${{ github.event.workflow_run.id }}');
  assert.equal(executor.env.RECOVERY_SWEEP, "${{ github.event_name == 'schedule' }}");
});

test('contains no bypass, force-push, auto-merge or untrusted PR execution path', () => {
  assert.doesNotMatch(source, /--admin|--auto|force-with-lease|git push|pull\/\$\{|workflow_run\.head_repository|workflow_run\.head_branch/);
});

test('post-merge recovery accepts the exact GitHub Actions bot merger identity and binds dispatch correlation', () => {
  const publishWorkflow = parse(publishSource);
  assert.match(publishSource, /github-actions\\\[bot\\\]/);
  assert.match(publishSource, /^run-name:.*Publication.*inputs\.correlation_id/m);
  assert.match(publishWorkflow['run-name'], /Publish merged PR #\{0\}.*\}\}$/);
  assert.match(publishSource, /correlation_id:/);
  assert.match(publishSource, /required: true/);
  assert.match(publishSource, /EXPECTED_CORRELATION_ID="submission-pr-\$\{PR_NUMBER\}-\$\{HEAD_SHA\}-\$\{MERGE_COMMIT_SHA\}"/);
  assert.match(publishSource, /\[ "\$CORRELATION_ID" = "\$EXPECTED_CORRELATION_ID" \]/);
});

test('publication receiver serializes one correlation and verifies the durable claim before writes', () => {
  const publishWorkflow = parse(publishSource);
  assert.equal(publishWorkflow.concurrency.group, 'publication-${{ inputs.correlation_id }}');
  assert.equal(publishWorkflow.concurrency['cancel-in-progress'], false);
  const claimGuard = publishSource.indexOf('Verify durable publication dispatch claim');
  const appToken = publishSource.indexOf('Generate GitHub App Token');
  assert.ok(claimGuard > 0 && claimGuard < appToken);
  assert.match(publishSource, /agentcrew-dispatch-claims\/publication/);
  assert.match(publishSource, /object\.sha == \$merge_sha/);
  assert.match(publishSource, /Existing durable publication status refuses duplicate execution/);
  assert.match(publishSource, /steps\.publication_claim\.outputs\.owns_reservation == 'true'/);
});
