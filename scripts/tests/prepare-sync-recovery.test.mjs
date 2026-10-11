import assert from 'node:assert/strict';
import test from 'node:test';
import { recoveryPlan } from '../prepare-sync-recovery.mjs';

const repo='aiskillstore/marketplace';
function evidence() {
  const root='skills/owner/demo', tree='b'.repeat(40);
  return {
    run:{id:1,event:'push',status:'completed',conclusion:'failure',head_sha:'a'.repeat(40),path:'.github/workflows/sync-to-supabase.yml',head_branch:'main',head_repository:{full_name:repo}},
    latestPush:{id:1},
    jobs:{total_count:1,jobs:[{steps:[{name:'Wait for authoritative publication completion',conclusion:'success'},{name:'Sync skills to Supabase',conclusion:'failure'}]}]},
    files:[{path:`${root}/SKILL.md`,status:'M'}],
    reports:[{root,meta:{slug:'owner-demo',content_hash:'c'.repeat(64),tree_hash:'d'.repeat(64)}}],
    trees:[{root,published:tree,current:tree,approved:tree}],
    approvals:[{merged:true,base:{ref:'main',repo:{full_name:repo}},head:{ref:'submission/example',sha:'e'.repeat(40),repo:{full_name:repo}},merge_commit_sha:'f'.repeat(40),user:{id:254047988,login:'ai-skill-store[bot]'}}],
  };
}
test('recovery derives a bounded exact scope from a failed push and unchanged approved trees',()=>{
  assert.deepEqual(recoveryPlan(evidence()),{commit:'a'.repeat(40),roots:['skills/owner/demo'],slugs:['owner-demo']});
});
test('unknown execution, wrong owners, changed trees and incomplete evidence cannot authorize resume',()=>{
  for(const mutate of [e=>e.latestPush.id=2,e=>e.run.event='workflow_dispatch',e=>e.run.conclusion='cancelled',e=>e.run.head_repository.full_name='fork/repo',e=>e.jobs.total_count=2,e=>e.jobs.jobs[0].steps[0].conclusion='failure',e=>e.jobs.jobs[0].steps[1].conclusion='success',e=>e.trees[0].current='9'.repeat(40),e=>e.trees[0].approved='9'.repeat(40),e=>e.reports=[],e=>e.approvals[0].user.id=1,e=>e.approvals[0].merged=false,e=>e.files[0].path='scripts/unsafe.mjs',e=>e.reports[0].meta.tree_hash=null]) {
    const e=evidence();mutate(e);assert.throws(()=>recoveryPlan(e));
  }
});
