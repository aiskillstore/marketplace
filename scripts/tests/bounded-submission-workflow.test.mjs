import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = path => readFileSync(new URL(`../../${path}`,import.meta.url),'utf8');
test('bounded sync pins original source and defers partial published callback without raising cap',()=>{
 const text=read('.github/workflows/sync-to-supabase.yml');
 assert.match(text,/bounded_failed_run:/);
 assert.match(text,/BOUNDED_FAILED_RUN: \$\{\{ inputs\.bounded_failed_run \}\}/);
 assert.match(text,/node scripts\/bounded-submission-recovery\.mjs prepare/);
 assert.match(text,/inputs\.bounded_failed_run == ''/);
 assert.match(text,/MAX_SYNC_SKILLS=64/);
 assert.match(text,/\/scripts\/bounded-submission-recovery\.mjs/);
 const start=text.indexOf('- name: Resolve published submissions');
 assert.match(text.slice(start,start+450),/inputs\.bounded_failed_run == ''/);
});
test('multi-run finalization is opt-in and uses existing separate reconciliation context',()=>{
 const text=read('.github/workflows/reconcile-submission-sync.yml');
 assert.match(text,/recovery_run_ids:/);
 assert.match(text,/node scripts\/bounded-submission-recovery\.mjs finalize/);
 assert.match(text,/SKILLSTORE_CALLBACK_TOKEN: \$\{\{ secrets\.SKILLSTORE_CALLBACK_TOKEN \}\}/);
 assert.match(text,/agentcrew\/provider-reconciliation/);
 assert.match(text,/fetch-depth: 0/);
});
