import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import {mkdtempSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import { publicationRecoveryPlan, verifiedPublicationRecovery, main } from '../publication-postpush-recovery.mjs';
const repo='aiskillstore/marketplace', sha=c=>c.repeat(40);
function fixture(){
  const correlation=`submission-pr-12-${sha('a')}-${sha('b')}`;
  const digest=createHash('sha256').update(correlation).digest('hex');
  return { correlation, run:{id:20,run_attempt:1,event:'push',status:'completed',conclusion:'failure',path:'.github/workflows/sync-to-supabase.yml',head_branch:'main',head_repository:{full_name:repo},head_sha:sha('c')},
    jobs:{total_count:1,jobs:[{steps:[{name:'Wait for authoritative publication completion',conclusion:'failure'},{name:'Sync skills to Supabase',conclusion:'skipped'},{name:'Notify skillstore - Published submissions',conclusion:'skipped'}]}]},
    publisher:{id:19,run_attempt:1,event:'workflow_dispatch',status:'completed',conclusion:'failure',head_branch:'main',head_repository:{full_name:repo},path:'.github/workflows/publish-approved-batch.yml',display_title:`Publication batch ${digest}`},
    publisherJobs:{total_count:1,jobs:[{name:'publish',conclusion:'failure',steps:[{name:'Verify every approval and publish one atomic batch',conclusion:'failure'}]}]},
    commit:{sha:sha('c'),parents:[{sha:sha('d')}],message:`Approve reviewed skills for PR #12 [submission: 00000000-0000-4000-8000-000000000001]\n\nAgentCrew-Publication: ${correlation}`},
    pr:{number:12,merged:true,merge_commit_sha:sha('b'),head:{sha:sha('a'),ref:'submission/example',repo:{full_name:repo}},base:{ref:'main',repo:{full_name:repo}},user:{id:254047988,login:'ai-skill-store[bot]'}},
    trees:[{root:'skills/acme/example',approved:sha('e'),published:sha('e'),current:sha('e')}],
    receiver:{status:'in_review',pr_number:12,workflow_run_id:5,approved_at:null,published_at:null,published_skill_slugs:null},
    submissionId:'00000000-0000-4000-8000-000000000001'};
}
test('postpush recovery resumes only missing merged callback; never push/provider',()=>{
  const e=fixture(); assert.deepEqual(publicationRecoveryPlan(e),{sendMerged:true,publicationSha:sha('c'),publisherId:19,submissionId:e.submissionId,prNumber:12});
  e.receiver={...e.receiver,status:'approved',workflow_run_id:19,approved_at:'2026-11-14T04:00:00Z'};
  assert.equal(publicationRecoveryPlan(e).sendMerged,false);
});
for(const [name,mutate] of [
  ['partial provider',e=>e.jobs.jobs[0].steps[1].conclusion='failure'],
  ['rerun without full attempt history',e=>e.run.run_attempt=2],
  ['wrong publisher digest',e=>e.publisher.display_title='Publication batch deadbeef'],
  ['foreign publisher',e=>e.publisher.head_repository.full_name='other/repo'],
  ['foreign PR author',e=>e.pr.user.id=1],
  ['changed current tree',e=>e.trees[0].current=sha('f')],
  ['different approved tree',e=>e.trees[0].approved=sha('f')],
  ['published receiver',e=>e.receiver.status='published'],
  ['approved by another workflow',e=>Object.assign(e.receiver,{status:'approved',approved_at:'2026-11-14T04:00:00Z'})],
  ['wrong receiver PR',e=>e.receiver.pr_number=13],
  ['callback persisted but state in_review',e=>e.receiver.approved_at='2026-11-14T04:00:00Z'],
]) test(`reject ${name}`,()=>{const e=fixture();mutate(e);assert.throws(()=>publicationRecoveryPlan(e));});
function proofFixture(){
 const e=fixture(), root=`repos/${repo}`;
 const proof={id:30,event:'workflow_dispatch',status:'completed',conclusion:'success',path:'.github/workflows/reconcile-submission-sync.yml',head_branch:'main',head_repository:{full_name:repo},run_attempt:1,created_at:'2026-11-14T05:00:00Z',display_title:'Reconcile publication push 20 using publisher 19'};
 e.run.created_at='2026-11-14T04:00:00Z';
 const status={context:'agentcrew/publication-reconciliation/20',state:'success',creator:{id:41898282,login:'github-actions[bot]'},target_url:`https://github.com/${repo}/actions/runs/30`};
 const data={[`${root}/commits/${sha('c')}/statuses?per_page=100&page=1`]:[status],[`${root}/actions/runs/30`]:proof,[`${root}/actions/runs/30/attempts/1/jobs?per_page=100`]:{total_count:1,jobs:[{steps:['Verify exact recovery and provider state','Record separate reconciliation result'].map(name=>({name,conclusion:'success'}))}]}};
 return {e,status,proof,data,request:path=>{assert.ok(path in data,`unexpected read ${path}`);return data[path];}};
}
test('consume only independently verified, trusted Actions publication proof',()=>{const f=proofFixture();assert.equal(verifiedPublicationRecovery(f.e.run,f.request).id,30);});
for(const [name,mutate] of [['untrusted creator',f=>f.status.creator.id=1],['nonterminal proof',f=>f.proof.status='in_progress'],['foreign branch',f=>f.proof.head_branch='feature'],['wrong source',f=>f.proof.display_title='Reconcile publication push 21 using publisher 19'],['stale proof',f=>f.proof.created_at='2026-11-14T03:00:00Z']])
 test(`reject proof ${name}`,()=>{const f=proofFixture();mutate(f);assert.equal(verifiedPublicationRecovery(f.e.run,f.request),null);});
test('transport uncertainty stops once; next inspection of committed receiver never repeats callback',async()=>{
 const directory=mkdtempSync(join(process.cwd(),'.publication-callback-test-'));
 const saved={GITHUB_OUTPUT:process.env.GITHUB_OUTPUT,SKILLSTORE_API_URL:process.env.SKILLSTORE_API_URL,SKILLSTORE_CALLBACK_TOKEN:process.env.SKILLSTORE_CALLBACK_TOKEN};
 try{
  process.env.GITHUB_OUTPUT=join(directory,'output');writeFileSync(process.env.GITHUB_OUTPUT,'');
  process.env.SKILLSTORE_API_URL='https://callback.invalid';process.env.SKILLSTORE_CALLBACK_TOKEN='synthetic-test-only';
  const e=fixture();e.pr.html_url=`https://github.com/${repo}/pull/12`;e.pr.merged_by={login:'test-merger'};
  const approved={...e.receiver,status:'approved',workflow_run_id:19,approved_at:'2026-11-14T04:00:00Z'};
  let requests=0;
  const inspect=async()=>({plan:publicationRecoveryPlan(e),evidence:e,correlation:e.correlation,readReceiver:async()=>approved});
  await assert.rejects(main({inspect,post:async(url,options)=>{requests++;assert.equal(String(url),'https://callback.invalid/api/submit/callback');assert.equal(options.redirect,'error');assert.equal(JSON.parse(options.body).workflow_run_id,19);throw new Error('transport uncertain');}}),/transport uncertain/);
  assert.equal(requests,1);assert.equal(readFileSync(process.env.GITHUB_OUTPUT,'utf8'),'');
  e.receiver=approved;
  await main({inspect,post:async()=>{requests++;throw new Error('must not repeat committed callback');}});
  assert.equal(requests,1);assert.match(readFileSync(process.env.GITHUB_OUTPUT,'utf8'),/publication_sha=/);
 }finally{for(const [key,value]of Object.entries(saved)){if(value===undefined)delete process.env[key];else process.env[key]=value;}rmSync(directory,{recursive:true,force:true});}
});
