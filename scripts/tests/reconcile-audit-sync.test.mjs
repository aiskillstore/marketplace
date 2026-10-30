import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { verifyAuditRecovery } from '../reconcile-audit-sync.mjs';
const sha = c => c.repeat(40);
const root = 'skills/owner/skill';
const run = (id,event,conclusion,head,day) => ({id,run_attempt:1,event,conclusion,status:'completed',head_sha:head,head_branch:'main',head_repository:{full_name:'aiskillstore/marketplace'},path:'.github/workflows/sync-to-supabase.yml',created_at:`2026-10-${day}T00:00:00Z`});
const steps = (pairs) => ({total_count:1,jobs:[{name:'sync',conclusion:'success',steps:pairs.map(([name,conclusion])=>({name,conclusion}))}]});
function fixture() {
  const originalJobs=steps([['Wait for authoritative publication completion','success'],['Find last successful sync commit','failure'],['Download skillstore-cli','skipped'],['Sync skills to Supabase','skipped'],['Reconcile durable security change events','skipped'],['Notify skillstore - Published submissions','skipped']]);
  const recoveryJobs=steps(['Sync skills to Supabase','Upload provider-complete synced slugs artifact','Save synced slugs to artifact','Reconcile durable security change events','Resolve published submissions'].map(n=>[n,'success']).concat([['Notify skillstore - Published submissions','skipped']]));
  recoveryJobs.jobs.push(...['calculate-scores','cache-invalidate'].map(name=>({name,conclusion:'success',steps:[]}))); recoveryJobs.total_count=3;
  return {push:run(3,'push','failure',sha('b'),'29'),recovery:run(4,'workflow_dispatch','success',sha('b'),'30'),baseline:run(1,'push','success',sha('a'),'27'),originalJobs,recoveryJobs,
    pr:{number:42,merged:true,state:'closed',merge_commit_sha:sha('b'),head:{sha:sha('c')}},
    merge:{parents:[{sha:sha('a')},{sha:sha('c')}]},
    provenance:{head:sha('c'),paths:[`${root}/skill-report.json`]},
    files:[{filename:`${root}/skill-report.json`,status:'modified'},{filename:`${root}/templates/SKILL.md`,status:'modified'}],
    reports:[{root,approvedTree:sha('d'),publishedTree:sha('d'),meta:{slug:'owner-skill',content_hash:'e'.repeat(64),tree_hash:'f'.repeat(64)}}],slugs:['owner-skill']};
}
test('reconciles only blocked audited push fully covered by actual manual recovery',()=>{
  const e=fixture(); assert.deepEqual(verifyAuditRecovery(e),[{root,slug:'owner-skill',content_hash:'e'.repeat(64),tree_hash:'f'.repeat(64),marketplace_commit_sha:sha('b')}]);
});
for(const [name,change] of [
  ['wrong recovery tree',e=>e.recovery.head_sha=sha('e')],
  ['not merged',e=>e.pr.merged=false],
  ['wrong merge',e=>e.pr.merge_commit_sha=sha('e')],
  ['different approved tree',e=>e.reports[0].approvedTree=sha('e')],
  ['unrelated source root',e=>e.files.push({filename:'skills/other/skill/SKILL.md',status:'modified'})],
  ['deleted source',e=>e.files[1].status='removed'],
  ['rename',e=>e.files[1].previous_filename='skills/old/skill.md'],
  ['source traversal',e=>e.files[1].filename=`${root}/../escape`],
  ['extra artifact slug',e=>e.slugs.push('other')],
  ['duplicate artifact slug',e=>e.slugs.push('owner-skill')],
  ['partial jobs',e=>e.recoveryJobs.total_count=100],
  ['partial provider',e=>e.recoveryJobs.jobs[0].steps[0].conclusion='failure'],
  ['callback replay',e=>e.recoveryJobs.jobs[0].steps.at(-1).conclusion='success'],
  ['partial cache',e=>e.recoveryJobs.jobs.at(-1).conclusion='failure'],
  ['push already wrote',e=>e.originalJobs.jobs[0].steps.find(s=>s.name==='Sync skills to Supabase').conclusion='success'],
  ['unknown preflight',e=>e.originalJobs.jobs[0].steps.find(s=>s.name==='Download skillstore-cli').conclusion='success'],
  ['untrusted producer head',e=>e.provenance.head=sha('e')],
  ['wrong merge parent',e=>e.merge.parents[1].sha=sha('e')],
  ['old recovery',e=>e.recovery.created_at=e.baseline.created_at],
  ['missing hashes',e=>delete e.reports[0].meta.tree_hash],
]) test(`rejects ${name}`,()=>{const e=fixture();change(e);assert.throws(()=>verifyAuditRecovery(e));});
test('audit mode uses existing read-only reconciliation workflow, not a provider replay',()=>{
 const w=readFileSync(new URL('../../.github/workflows/reconcile-submission-sync.yml',import.meta.url),'utf8');
 assert.match(w,/audit_pr:/); assert.match(w,/AUDIT_PR:/); assert.doesNotMatch(w,/contents: write|skill sync|workflow run/);
 const ci=readFileSync(new URL('../../.github/workflows/validate-marketplace.yml',import.meta.url),'utf8');
 assert.match(ci,/scripts\/tests\/reconcile-audit-sync.test.mjs/);
});
test('existing consumer accepts only separately verified audit proof with exact title and owner',async()=>{
 const { recoveredPushSync }=await import('../recovered-push-sync.mjs');
 const push=fixture().push;
 const status={context:`agentcrew/provider-reconciliation/${push.id}`,state:'success',creator:{id:41898282,login:'github-actions[bot]'},target_url:'https://github.com/aiskillstore/marketplace/actions/runs/9'};
 const proof={...run(9,'workflow_dispatch','success',sha('e'),'31'),path:'.github/workflows/reconcile-submission-sync.yml',display_title:'Reconcile audit push 3 using recovery 4 and PR 42'};
 const proofJobs=steps([['Verify exact recovery and provider state','success'],['Record separate reconciliation result','success']]);
 const api=p=>p.includes('/statuses?')?[status]:p.includes('/jobs?')?proofJobs:proof;
 assert.equal(recoveredPushSync(push,[push],api),proof);
 for(const title of ['Reconcile audit push 2 using recovery 4 and PR 42','Reconcile audit push 3 using recovery 4','Reconcile audit push 3 using recovery 4 and PR 0']) {
   assert.equal(recoveredPushSync(push,[push],p=>p.includes('/statuses?')?[status]:p.includes('/jobs?')?proofJobs:{...proof,display_title:title}),null);
 }
});
