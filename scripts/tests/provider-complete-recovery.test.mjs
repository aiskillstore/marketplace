import assert from 'node:assert/strict';
import test from 'node:test';
import { recoveryPlan } from '../prepare-sync-recovery.mjs';

function evidence() {
  const root='skills/demo', sha='a'.repeat(40), tree='b'.repeat(40);
  const meta={slug:'demo',source_type:'official',source_ref:'1'.repeat(40),source_url:`https://github.com/anthropics/skills/tree/${'1'.repeat(40)}/skills/demo`,content_hash:'c'.repeat(64),tree_hash:'d'.repeat(64)};
  const projection={slug:meta.slug,plugin_path:root,marketplace_commit_sha:sha,content_hash:meta.content_hash,tree_hash:meta.tree_hash,id:'skill',current_artifact_version_id:'artifact',artifact_revision:3};
  const artifact={id:'artifact',skill_id:'skill',source_path:root,marketplace_commit_sha:sha,content_hash:meta.content_hash,tree_hash:meta.tree_hash,artifact_revision:3,snapshot_status:'exact'};
  return {
    run:{id:1,event:'push',status:'completed',conclusion:'failure',head_sha:sha,path:'.github/workflows/sync-to-supabase.yml',head_branch:'main',head_repository:{full_name:'aiskillstore/marketplace'}},latestPush:{id:1},
    jobs:{total_count:1,jobs:[{steps:[{name:'Wait for authoritative publication completion',conclusion:'success'},{name:'Sync skills to Supabase',conclusion:'success'},{name:'Upload provider-complete synced slugs artifact',conclusion:'success'},{name:'Notify skillstore - Published submissions',conclusion:'failure'}]}]},
    files:[{path:`${root}/SKILL.md`,status:'A'},{path:`${root}/skill-report.json`,status:'A'}],
    reports:[{root,meta}],trees:[{root,published:tree,current:tree,approved:tree}],
    approvals:[{merged:true,base:{ref:'main',repo:{full_name:'aiskillstore/marketplace'}},head:{ref:'submission/example',sha:'e'.repeat(40),repo:{full_name:'aiskillstore/marketplace'}},merge_commit_sha:'f'.repeat(40),user:{id:254047988,login:'ai-skill-store[bot]'}}],
    providerEvidence:{callback:{status:'approved',published_at:null,published_skill_slugs:[]},slugs:['demo'],projections:[{root,skills:[projection],artifacts:[artifact]}]},
  };
}
test('provider-complete official publication resumes only ancillary stages with exact production projection',()=>{
  assert.deepEqual(recoveryPlan(evidence()),{commit:'a'.repeat(40),roots:['skills/demo'],slugs:['demo'],providerComplete:true});
});
test('provider-complete recovery fails closed on incomplete or mismatched production evidence',()=>{
  for(const mutate of [e=>delete e.providerEvidence,e=>e.providerEvidence.callback.status='published',e=>e.providerEvidence.callback.published_at='2026-10-20',e=>delete e.providerEvidence.callback,e=>e.providerEvidence.slugs=[],e=>e.providerEvidence.slugs.push('extra'),e=>e.providerEvidence.projections=[],e=>e.providerEvidence.projections[0].skills[0].artifact_revision=4,e=>e.providerEvidence.projections[0].artifacts[0].marketplace_commit_sha='2'.repeat(40),e=>e.providerEvidence.projections[0].artifacts[0].snapshot_status='partial',e=>e.jobs.jobs[0].steps[2].conclusion='failure',e=>e.jobs.jobs[0].steps[3].conclusion='success',e=>e.trees[0].current='9'.repeat(40),e=>e.reports[0].meta.source_type='community',e=>e.reports[0].meta.source_url=e.reports[0].meta.source_url.replace('anthropics','impostor')]) {
    const e=evidence();mutate(e);assert.throws(()=>recoveryPlan(e));
  }
});
test('official root discovery rejects nested identities and unsafe files',()=>{
  for(const path of ['skills/../SKILL.md','skills/demo/../SKILL.md','skills//demo/SKILL.md','scripts/demo/SKILL.md']) {
    const e=evidence();e.files[0].path=path;assert.throws(()=>recoveryPlan(e));
  }
});
