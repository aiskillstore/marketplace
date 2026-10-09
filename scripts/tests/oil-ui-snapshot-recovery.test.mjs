import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { INCIDENT, validateEvidence, correctedReport } from '../recover-oil-ui-snapshot.mjs';

function evidence() {
  return {
    pr: { number:3671, merged:true, merge_commit_sha:INCIDENT.merge,
      user:{id:254047988,login:'ai-skill-store[bot]'},
      head:{sha:INCIDENT.head,ref:INCIDENT.sourceBranch,repo:{full_name:'aiskillstore/marketplace'}},
      base:{ref:'main',repo:{full_name:'aiskillstore/marketplace'}},
      body:'Submission ID: `639e9449-9c6c-4491-b526-48333d0c087e`' }, 
    reportEntry:{sha:INCIDENT.reportBlob,mode:'100644',type:'blob'}, priorCorrections:[],
    pendingTree:INCIDENT.pendingTree, publishedTree:INCIDENT.publishedTree,
    originalPendingTree:INCIDENT.pendingTree,
    files:[`${INCIDENT.pending}/SKILL.md`,`${INCIDENT.pending}/skill-report.json`],
    statuses:[{creator:{id:254047988,login:'ai-skill-store[bot]'},context:INCIDENT.preflight,state:'failure',description:INCIDENT.failure,target_url:INCIDENT.failedRun}],
    outbox:[], comparison:{status:'ahead',ahead_by:1,behind_by:0,merge_base_commit:{sha:INCIDENT.previousRef}},
  };
}
function report() { return {meta:{slug:'oil-oil-oil-ui',source_type:'community',source_ref:INCIDENT.nextRef,
  source_url:`https://github.com/oil-oil/oil-ui/tree/${INCIDENT.nextRef}/`,content_hash:INCIDENT.contentHash,tree_hash:INCIDENT.treeHash}, untouched:{nested:['evidence']}}; }

test('accepts only inspected immutable zero-mutation incident',()=>assert.doesNotThrow(()=>validateEvidence(evidence())));
for (const [name,mutate] of [
  ['wrong author',e=>e.pr.user.id=1],['wrong head',e=>e.pr.head.sha='0'.repeat(40)],
  ['wrong merge',e=>e.pr.merge_commit_sha='0'.repeat(40)],['fork',e=>e.pr.head.repo.full_name='other/repo'],
  ['wrong branch',e=>e.pr.head.ref='submission/other'],['unmerged',e=>e.pr.merged=false],
  ['pending drift',e=>e.pendingTree='0'.repeat(40)],['published drift',e=>e.publishedTree='0'.repeat(40)],
  ['wrong report blob',e=>e.reportEntry.sha='0'.repeat(40)],
  ['prior closed correction',e=>e.priorCorrections.push({state:'closed'})],
  ['wrong submission',e=>e.pr.body='Submission ID: `wrong`'],
  ['original drift',e=>e.originalPendingTree='0'.repeat(40)],['mixed paths',e=>e.files.push('scripts/evil.mjs')],
  ['missing report',e=>e.files.pop()],['missing failure',e=>e.statuses=[]],
  ['reservation',e=>e.statuses.push({context:'agentcrew/publication/x',state:'pending'})],
  ['untrusted failure status',e=>e.statuses[0].creator.id=1],
  ['dispatch attempt',e=>e.outbox.push({ref:'attempt'})],['diverged source',e=>e.comparison.status='diverged'],
  ['wrong ancestor',e=>e.comparison.merge_base_commit.sha='0'.repeat(40)],
]) test(`rejects ${name} before writes`,()=>{const e=evidence();mutate(e);assert.throws(()=>validateEvidence(e));});

test('adds only the two reviewed update snapshot fields and preserves every other value',()=>{
 const before=report();const after=JSON.parse(correctedReport(JSON.stringify(before)));
 assert.equal(after.meta.previous_tree_hash,INCIDENT.previousTreeHash);
 assert.equal(after.meta.previous_source_ref,INCIDENT.previousRef);
 delete after.meta.previous_tree_hash;delete after.meta.previous_source_ref;
 assert.deepEqual(after,before);
});
for(const field of ['previous_tree_hash','previous_source_ref']) test(`refuses existing ${field} even if null`,()=>{
 const r=report();r.meta[field]=null;assert.throws(()=>correctedReport(JSON.stringify(r)));
});
test('refuses unexpected pending identity',()=>{const r=report();r.meta.source_ref='0'.repeat(40);assert.throws(()=>correctedReport(JSON.stringify(r)));});
test('workflow is manual main-only, immutable checkout, no publication or merge capability in script',()=>{
 const yaml=readFileSync(new URL('../../.github/workflows/recover-oil-ui-snapshot.yml',import.meta.url),'utf8');
 assert.match(yaml,/workflow_dispatch:/);assert.match(yaml,/github.ref == 'refs\/heads\/main'/);
 assert.match(yaml,/ref: \$\{\{ github.sha \}\}/);assert.match(yaml,/persist-credentials: false/);
 assert.doesNotMatch(yaml,/schedule:|pull_request_target:|secrets: inherit/);
 const script=readFileSync(new URL('../recover-oil-ui-snapshot.mjs',import.meta.url),'utf8');
 assert.doesNotMatch(script,/--admin|\/merges?['"`]|force: true/);
});
