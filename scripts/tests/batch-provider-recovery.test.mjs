import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { classifyProjection, verifyCallbacks, verifyStage, verifyOriginalOutcomes } from '../batch-provider-recovery.mjs';
const expected={root:'skills/owner/demo',slug:'owner-demo',marketplace_commit_sha:'a'.repeat(40),content_hash:'b'.repeat(64),tree_hash:'c'.repeat(64)};
function projection() {
 const skill={...expected,id:'s',plugin_path:expected.root,status:'approved',distribution_state:'active',artifact_revision:1,current_artifact_version_id:'a'};
 const artifact={...expected,id:'a',skill_id:'s',source_path:expected.root,artifact_revision:1,snapshot_status:'exact'};
 return {skill,artifact};
}
test('only absent skill and absent source artifacts permit initial sync',()=>{
 assert.equal(classifyProjection(expected,[],[]),'initial');
 assert.throws(()=>classifyProjection(expected,[],[{id:'orphan'}]),/Orphan/);
});
test('exact approved active projection is reusable without provider mutation',()=>{
 const {skill,artifact}=projection();assert.equal(classifyProjection(expected,[skill],[artifact]),'reuse');
});
test('changed, suppressed, orphan, incomplete and duplicate projections fail closed',()=>{
 for(const field of ['content_hash','tree_hash','marketplace_commit_sha','artifact_revision','current_artifact_version_id','plugin_path','status','distribution_state']) {
  const {skill,artifact}=projection();skill[field]='wrong';assert.throws(()=>classifyProjection(expected,[skill],[artifact]),field);
 }
 for(const field of ['content_hash','tree_hash','marketplace_commit_sha','artifact_revision','skill_id','source_path','snapshot_status']) {
  const {skill,artifact}=projection();artifact[field]='wrong';assert.throws(()=>classifyProjection(expected,[skill],[artifact]),field);
 }
 const {skill,artifact}=projection();assert.throws(()=>classifyProjection(expected,[skill],[]));assert.throws(()=>classifyProjection(expected,[skill,skill],[artifact]));
});
test('callbacks cover each distinct owner rather than assigning all slugs to last PR',()=>{
 const reports=[{submissionId:'first',slug:'one'},{submissionId:'last',slug:'two'}];
 verifyCallbacks(reports,[{submission_id:'first',skill_slugs:['one']},{submission_id:'last',skill_slugs:['two']}]);
 assert.throws(()=>verifyCallbacks(reports,[{submission_id:'last',skill_slugs:['one','two']}]));
 assert.throws(()=>verifyCallbacks(reports,[{submission_id:'first',skill_slugs:['two']},{submission_id:'last',skill_slugs:['one']}]));
});
test('stage evidence must be complete, unique and successful',()=>{
 const jobs={total_count:1,jobs:[{steps:[{name:'provider',conclusion:'success'}]}]};verifyStage(jobs,'provider','success');
 assert.throws(()=>verifyStage({...jobs,total_count:2},'provider','success'));
 assert.throws(()=>verifyStage(jobs,'provider','failure'));
 assert.throws(()=>verifyStage({total_count:1,jobs:[{steps:[...jobs.jobs[0].steps,...jobs.jobs[0].steps]}]},'provider','success'));
});
test('partial batch writes only missing paths then verifies union before callbacks',()=>{
 const workflow=readFileSync(new URL('../../.github/workflows/sync-to-supabase.yml',import.meta.url),'utf8');
 assert.match(workflow,/CHANGED_SKILLS="\$BATCH_PENDING_PATHS"/);
 assert.match(workflow,/node scripts\/batch-provider-recovery.mjs verify\n\s+printf '%s\\n' "\$BATCH_REUSED_SLUGS"/);
 assert.match(workflow,/BATCH_RECOVERY === 'true'/);
});

test('reuse is grounded in original completed-item logs, not artifact existence alone',()=>{
 const reports=[{slug:'owner-ok'},{slug:'owner-failed'}];
 const log='2026-11-25 ✓ Synced: owner-ok\n2026-11-25 ✗ Error syncing owner-failed: Source distribution is suppressed or could not be verified\nSync complete: 1 synced, 1 errors';
 assert.deepEqual(verifyOriginalOutcomes(log,reports),{synced:['owner-ok'],failed:['owner-failed']});
 assert.throws(()=>verifyOriginalOutcomes(log.replace('Source distribution is suppressed or could not be verified','AI content failed'),reports));
 assert.throws(()=>verifyOriginalOutcomes(log+'\n✓ Synced: owner-ok',reports));
 assert.throws(()=>verifyOriginalOutcomes(log,[...reports,{slug:'foreign'}]));
});
