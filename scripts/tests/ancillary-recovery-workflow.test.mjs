import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
const workflow=readFileSync(new URL('../../.github/workflows/sync-to-supabase.yml',import.meta.url),'utf8');
test('recovery materializes read-only verifier and passes provider handles only inside the job',()=>{
  assert.match(workflow,/\/scripts\/reconcile-submission-sync\.mjs/);
  const step=workflow.split('      - name: Validate trusted sync correlation')[1].split('      - name:')[0];
  assert.match(step,/SUPABASE_URL: \$\{\{ secrets\.SUPABASE_URL \}\}/);
  assert.match(step,/SUPABASE_SERVICE_KEY: \$\{\{ secrets\.SUPABASE_SERVICE_KEY \}\}/);
});
test('provider-complete mode exits before provider mutation and retains verified slug plan',()=>{
  const step=workflow.split('      - name: Sync skills to Supabase')[1].split('      - name:')[0];
  assert.match(step,/PROVIDER_COMPLETE: \$\{\{ steps\.trusted-correlation\.outputs\.provider_complete \}\}/);
  const skip=step.indexOf('if [ "$PROVIDER_COMPLETE" = true ]');
  const exit=step.indexOf('exit 0',skip);
  assert.ok(skip>=0 && exit>skip && exit<step.indexOf('configure_tls()'));
  assert.match(step.slice(skip,exit),/synced-slugs\.txt/);
  assert.match(step.slice(skip,exit),/synced_count=/);
  assert.match(step,/VERIFIED_RECOVERY_SLUGS: \$\{\{ steps\.trusted-correlation\.outputs\.recovery_slugs \}\}/);
  assert.match(step.slice(skip,exit),/VERIFIED_RECOVERY_SLUGS/);
});
test('successful ancillary provider stages do not replay during callback-only recovery',()=>{
  for(const name of ['Reconcile durable security change events','Remove generated report evidence from synced audits','Refresh security research snapshot']) {
    const step=workflow.split(`      - name: ${name}`)[1].split('      - name:')[0];
    assert.match(step,/steps\.trusted-correlation\.outputs\.provider_complete != 'true'/);
  }
});
