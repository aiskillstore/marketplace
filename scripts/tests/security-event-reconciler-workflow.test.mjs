import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import test from 'node:test';

const workflow = readFileSync(
  resolve(process.cwd(), '.github/workflows/sync-to-supabase.yml'),
  'utf8',
);

function stepBlock(name) {
  const marker = `      - name: ${name}`;
  const start = workflow.indexOf(marker);
  assert.notEqual(start, -1, `missing workflow step: ${name}`);
  const end = workflow.indexOf('\n      - name:', start + marker.length);
  return workflow.slice(start, end === -1 ? workflow.length : end);
}

function jobBlock(name) {
  const marker = `  ${name}:`;
  const start = workflow.indexOf(marker);
  assert.notEqual(start, -1, `missing workflow job: ${name}`);
  const end = workflow.indexOf('\n  # ===', start + marker.length);
  return workflow.slice(start, end === -1 ? workflow.length : end);
}

test('a staggered bounded schedule drains the durable outbox without cancelling writers', () => {
  assert.match(workflow, /schedule:\n\s+#.*\n\s+- cron: '7,22,37,52 \* \* \* \*'/);
  assert.match(workflow, /concurrency:\n\s+group: sync-supabase\n\s+cancel-in-progress: false/);

  const download = stepBlock('Download skillstore-cli');
  assert.match(download, /id: download-cli/);
  assert.match(download, /version: '2\.3\.0'/);
  assert.match(download, /minimum-version: '2\.3\.0'/);
  assert.doesNotMatch(download, /skip_sync|changed_skills/);
});

test('sync and reconciliation share the explicit notifications rollout flag', () => {
  const expectedFlag = /SECURITY_NOTIFICATIONS_ENABLED: \$\{\{ vars\.SECURITY_NOTIFICATIONS_ENABLED \|\| 'false' \}\}/;
  assert.match(stepBlock('Sync skills to Supabase'), expectedFlag);

  const reconcile = stepBlock('Reconcile durable security change events');
  assert.match(reconcile, expectedFlag);
  assert.match(reconcile, /PUBLIC_SUPABASE_URL: \$\{\{ secrets\.SUPABASE_URL \}\}/);
  assert.match(reconcile, /SUPABASE_SERVICE_ROLE_KEY: \$\{\{ secrets\.SUPABASE_SERVICE_KEY \}\}/);
  assert.match(reconcile, /if: \$\{\{ !cancelled\(\) && steps\.download-cli\.outcome == 'success' \}\}/);
  assert.match(reconcile, /continue-on-error: \$\{\{ github\.event_name != 'schedule' \}\}/);
  assert.match(reconcile, /timeout --signal=TERM --kill-after=30s 15m/);
  assert.match(reconcile, /skill reconcile-security-events --batch-size 100/);
  assert.doesNotMatch(reconcile, /skip_sync|changed_skills|AUTOMATION_API_KEY|SKILLSTORE_CALLBACK_TOKEN/);
});

test('scheduled no-change runs do not enter score, cache, or translation side effects', () => {
  assert.match(stepBlock('Find last successful sync commit'), /if: github\.event_name != 'schedule'/);
  const detection = stepBlock('Detect changed skills');
  assert.match(detection, /if \[ "\$\{\{ github\.event_name \}\}" = "schedule" \]; then/);
  assert.match(detection, /CHANGED=""/);
  assert.match(detection, /mode=reconcile-only/);
  assert.match(detection, /if \[ -z "\$CHANGED" \]; then[\s\S]*skip_sync=true/);
  assert.ok(
    detection.indexOf('github.event_name') < detection.indexOf('inputs.slugs'),
    'schedule must bypass all skill-selection modes',
  );

  for (const name of [
    'calculate-scores',
    'plan-cache-invalidation',
    'cache-invalidate-shard',
    'cache-invalidate',
    'finalize-english-cache',
    'trigger-translate',
  ]) {
    assert.match(jobBlock(name), /needs\.sync\.outputs\.skip_sync != 'true'/, name);
  }

  const reconcileStart = workflow.indexOf('      - name: Reconcile durable security change events');
  const syncStart = workflow.indexOf('      - name: Sync skills to Supabase');
  const cleanupStart = workflow.indexOf('      - name: Remove generated report evidence from synced audits');
  assert.ok(syncStart < reconcileStart && reconcileStart < cleanupStart);
});

test('a failed bounded drain stays observable and leaves durable jobs for retry', () => {
  const report = stepBlock('Report security event reconciliation failure');
  assert.match(report, /always\(\) && steps\.reconcile-security-events\.outcome == 'failure'/);
  assert.match(report, /queued jobs remain retryable/);
  assert.match(report, /next scheduled or sync-triggered run/);
});
