import test from 'node:test';
import assert from 'node:assert/strict';
import { verifyPrewriteFailure, selectBoundedSubset, verifyBoundedRun, loadBoundedManifest } from '../bounded-submission-recovery.mjs';
const sha = 'a'.repeat(40);
const run = {id: 20,created_at:'2026-11-02T16:15:00Z',run_attempt:1,event:'push',status:'completed',conclusion:'failure',path:'.github/workflows/sync-to-supabase.yml',head_branch:'main',head_repository:{full_name:'aiskillstore/marketplace'},head_sha:sha};
const makeJobs = () => ({total_count:1,jobs:[{steps:[
  ['Wait for authoritative publication completion','success'],['Validate bounded sync admission','failure'],
  ['Sync skills to Supabase','skipped'],['Upload provider-complete synced slugs artifact','skipped'],
  ['Notify skillstore - Published submissions','skipped'],
].map(([name,conclusion])=>({name,conclusion}))}]});
test('only exact pre-provider admission rejection permits bounded recovery',()=>{
  verifyPrewriteFailure(run,[makeJobs()]);
  for(const name of ['Validate bounded sync admission','Sync skills to Supabase','Notify skillstore - Published submissions']) {
    const jobs=makeJobs();jobs.jobs[0].steps.find(s=>s.name===name).conclusion='success';
    assert.throws(()=>verifyPrewriteFailure(run,[jobs]));
  }
  assert.throws(()=>verifyPrewriteFailure({...run,run_attempt:2},[makeJobs()]));
  assert.throws(()=>verifyPrewriteFailure({...run,head_repository:{full_name:'evil/repo'}},[makeJobs()]));
  assert.throws(()=>verifyPrewriteFailure(run,[{...makeJobs(),total_count:2}]));
});
test('subset uses exact original manifest and excludes earlier completed batches',()=>{
  const slugs=Array.from({length:79},(_,i)=>`skill-${i}`);
  assert.deepEqual(selectBoundedSubset(slugs,slugs.slice(40),[{runId:1,slugs:slugs.slice(0,40)}]),slugs.slice(40).sort());
  for(const subset of [[],slugs, ['extra'], ['skill-0'], ['skill-40','skill-40']]) assert.throws(()=>selectBoundedSubset(slugs,subset,[{runId:1,slugs:slugs.slice(0,40)}]));
});
test('bounded recovery requires successful downstreams and deferred callback',()=>{
  const recovery={...run,id:21,event:'workflow_dispatch',conclusion:'success',display_title:'Bounded provider recovery 20'};
  const jobs={total_count:3,jobs:[{name:'sync',steps:[['Validate trusted sync correlation','success'],['Sync skills to Supabase','success'],['Upload provider-complete synced slugs artifact','success'],['Reconcile durable security change events','success'],['Notify skillstore - Published submissions','skipped']].map(([name,conclusion])=>({name,conclusion}))},{name:'calculate-scores',conclusion:'success'},{name:'cache-invalidate',conclusion:'success'}]};
  verifyBoundedRun(recovery,jobs,20);
  assert.throws(()=>verifyBoundedRun({...recovery,display_title:'manual'},jobs,20));
  jobs.jobs[0].steps.at(-1).conclusion='success';
  assert.throws(()=>verifyBoundedRun(recovery,jobs,20));
});

function fixture(mutate = {}) {
 const head='b'.repeat(40),merge='c'.repeat(40),current='d'.repeat(40),tree='e'.repeat(40),before='f'.repeat(40);
 const id='11111111-1111-4111-8111-111111111111';
 const pr={merged:true,user:{id:254047988,login:'ai-skill-store[bot]'},head:{sha:head,ref:'submission/test',repo:{full_name:'aiskillstore/marketplace'}},merge_commit_sha:merge,base:{ref:'main',repo:{full_name:'aiskillstore/marketplace'}},body:`Submission ID: \`${id}\``};
 Object.assign(pr,mutate.pr);
 const baseline={...run,id:19,created_at:'2026-11-02T13:00:00Z',head_sha:before,conclusion:'success'};
 const request=path=>{
  if(path==='actions/runs/20') return run;
  if(path.includes('workflows/sync-to-supabase.yml/runs')) return {workflow_runs:[run,baseline]};
  if(path.includes('/attempts/1/jobs')) return makeJobs();
  if(path===`git/commits/${sha}`) return {message:`Approve [submission: ${id}]\nAgentCrew-Publication: submission-pr-5-${head}-${merge}`,parents:[{sha:merge}]};
  if(path==='pulls/5')return pr;
  throw new Error(path);
 };
 const gitRead=args=>{
  if(args[0]==='fetch'||args[0]==='merge-base')return '';
  if(args.includes('--raw'))return mutate.range && args.includes(before)?'other':'same';
  if(args.includes('--name-status'))return Array.from({length:79},(_,i)=>`A\0skills/demo/skill-${i}/SKILL.md\0A\0skills/demo/skill-${i}/skill-report.json`).join('\0');
  if(args[0]==='rev-parse')return mutate.tree && args[1].startsWith(current)?before:tree;
  if(args[0]==='show') {
   const n=args[1].match(/skill-(\d+)\//)[1];
   return JSON.stringify({meta:{slug:`skill-${n}`,content_hash:'1'.repeat(64),tree_hash:'2'.repeat(64)}});
  }
  throw new Error(JSON.stringify(args));
 };
 return {request,gitRead,env:{GITHUB_REF:'refs/heads/main',GITHUB_EVENT_NAME:'workflow_dispatch',GITHUB_REPOSITORY:'aiskillstore/marketplace',GITHUB_SHA:current}};
}
test('manifest proves exact trusted approval and immutable current source trees',()=>{
 const plan=loadBoundedManifest(20,fixture());
 assert.equal(plan.reports.length,79);assert.equal(plan.run.head_sha,sha);
 assert.throws(()=>loadBoundedManifest(20,fixture({pr:{user:{id:1,login:'evil'}}})));
 assert.throws(()=>loadBoundedManifest(20,fixture({pr:{merged:false}})));
 assert.throws(()=>loadBoundedManifest(20,fixture({tree:true})));
 assert.throws(()=>loadBoundedManifest(20,fixture({range:true})));
 const wrongRef=fixture();wrongRef.env.GITHUB_REF='refs/heads/fork';
 assert.throws(()=>loadBoundedManifest(20,wrongRef));
});
