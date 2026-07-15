import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import test from 'node:test';

const syncWorkflow = readFileSync(
  resolve(process.cwd(), '.github/workflows/sync-to-supabase.yml'),
  'utf8',
);
const scheduledWorkflow = readFileSync(
  resolve(process.cwd(), '.github/workflows/reconcile-security-events.yml'),
  'utf8',
);
const testWorkflow = readFileSync(
  resolve(process.cwd(), '.github/workflows/test-recalculate-scores.yml'),
  'utf8',
);

function stepBlock(workflow, name) {
  const marker = `      - name: ${name}`;
  const start = workflow.indexOf(marker);
  assert.notEqual(start, -1, `missing workflow step: ${name}`);
  const end = workflow.indexOf('\n      - name:', start + marker.length);
  return workflow.slice(start, end === -1 ? workflow.length : end);
}

test('the scheduled drain is isolated from the incremental sync baseline', () => {
  assert.doesNotMatch(syncWorkflow, /^\s{2}schedule:/m);
  assert.match(syncWorkflow, /concurrency:\n\s+group: sync-supabase\n\s+cancel-in-progress: false/);
  assert.doesNotMatch(syncWorkflow, /mode=reconcile-only/);

  assert.match(scheduledWorkflow, /schedule:\n\s+#.*\n\s+- cron: '7,22,37,52 \* \* \* \*'/);
  assert.match(scheduledWorkflow, /workflow_dispatch:/);
  assert.match(
    scheduledWorkflow,
    /concurrency:\n\s+group: security-event-reconciler\n\s+cancel-in-progress: false/,
  );
  assert.match(scheduledWorkflow, /runs-on: ubuntu-latest/);
  assert.match(scheduledWorkflow, /timeout-minutes: 20/);
});

test('the scheduled drain uses the pinned CLI and least required credentials', () => {
  const checkout = stepBlock(scheduledWorkflow, 'Checkout CLI download action');
  assert.match(checkout, /persist-credentials: false/);
  assert.match(checkout, /sparse-checkout: \.github\/actions\/download-skillstore-cli/);

  const token = stepBlock(scheduledWorkflow, 'Generate GitHub App Token');
  assert.match(token, /repositories: marketplace,skillstore/);

  const download = stepBlock(scheduledWorkflow, 'Download skillstore-cli');
  assert.match(download, /version: '2\.3\.0'/);
  assert.match(download, /minimum-version: '2\.3\.0'/);

  const reconcile = stepBlock(scheduledWorkflow, 'Reconcile durable security change events');
  assert.match(reconcile, /PUBLIC_SUPABASE_URL: \$\{\{ secrets\.SUPABASE_URL \}\}/);
  assert.match(reconcile, /SUPABASE_SERVICE_ROLE_KEY: \$\{\{ secrets\.SUPABASE_SERVICE_KEY \}\}/);
  assert.match(
    reconcile,
    /SECURITY_NOTIFICATIONS_ENABLED: \$\{\{ vars\.SECURITY_NOTIFICATIONS_ENABLED \|\| 'false' \}\}/,
  );
  assert.match(reconcile, /timeout --signal=TERM --kill-after=30s 15m/);
  assert.match(reconcile, /skill reconcile-security-events --batch-size 100/);
  assert.doesNotMatch(reconcile, /continue-on-error|AUTOMATION_API_KEY|SKILLSTORE_CALLBACK_TOKEN/);
});

test('the scheduled workflow cannot trigger sync, score, cache, or translation side effects', () => {
  assert.doesNotMatch(
    scheduledWorkflow,
    /skill sync|changed_skills|sync-supabase|calculate-scores|cache-invalidate|trigger-translate|repository_dispatch/,
  );
});

test('normal syncs use 2.4.4 and keep reconciliation best-effort', () => {
  const download = stepBlock(syncWorkflow, 'Download skillstore-cli');
  assert.match(download, /if: steps\.changes\.outputs\.skip_sync != 'true'/);
  assert.match(download, /version: '2\.4\.4'/);
  assert.match(download, /minimum-version: '2\.4\.4'/);

  const expectedFlag = /SECURITY_NOTIFICATIONS_ENABLED: \$\{\{ vars\.SECURITY_NOTIFICATIONS_ENABLED \|\| 'false' \}\}/;
  assert.match(stepBlock(syncWorkflow, 'Sync skills to Supabase'), expectedFlag);
  const reconcile = stepBlock(syncWorkflow, 'Reconcile durable security change events');
  assert.match(reconcile, expectedFlag);
  assert.match(reconcile, /continue-on-error: true/);
  assert.match(reconcile, /skill reconcile-security-events --batch-size 100/);
});

test('CI tracks the isolated scheduled workflow contract', () => {
  assert.match(testWorkflow, /\.github\/workflows\/reconcile-security-events\.yml/);
  assert.match(testWorkflow, /node --test scripts\/tests\/\*\.test\.mjs/);
});
