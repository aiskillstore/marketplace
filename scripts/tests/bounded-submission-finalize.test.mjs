import test from 'node:test';
import assert from 'node:assert/strict';
import { finalize } from '../bounded-submission-recovery.mjs';
const sha='a'.repeat(40);
function fixture({published=false,badProvider=false,partial=false,fetchFailure=false}={}) {
 const reports=Array.from({length:79},(_,i)=>({slug:`skill-${i}`,root:`skills/demo/skill-${i}`,marketplace_commit_sha:sha,content_hash:'b'.repeat(64),tree_hash:'c'.repeat(64)}));
 const slugs=reports.map(r=>r.slug).sort();
 let posted=published; const calls=[],outputs=[];
 return {calls,outputs,deps:{
 env:{FAILED_RUN_ID:'20',RECOVERY_RUN_IDS:'21,22',GITHUB_RUN_ID:'23',GITHUB_OUTPUT:'unused',SKILLSTORE_API_URL:'https://example.test',SKILLSTORE_CALLBACK_TOKEN:'synthetic'},
 manifestLoader:()=>({run:{id:20,head_sha:sha},reports,submissionId:'synthetic-submission'}),
 batchReader:()=>[{runId:21,slugs:slugs.slice(0,40)},{runId:22,slugs:slugs.slice(40)}],
 readProvider:async(table,filter)=>{
  calls.push(table);
  if(table==='submissions')return [{status:posted?'published':'approved',published_at:posted?'2026-11-02T16:00:00Z':null,published_skill_slugs:posted?(partial?slugs.slice(0,40):slugs):null}];
  const slug=filter[1].replace(/^artifact-/,''),expected=reports.find(r=>r.slug===slug);
  assert.ok(expected);
  const base={...expected,marketplace_commit_sha:badProvider?'d'.repeat(40):sha};
  return table==='skills'?[{...base,id:`id-${slug}`,plugin_path:expected.root,current_artifact_version_id:`artifact-${slug}`,artifact_revision:1}]:[{...base,id:`artifact-${slug}`,skill_id:`id-${slug}`,source_path:expected.root,artifact_revision:1,snapshot_status:'exact'}];
 },
 fetcher:async(url,options)=>{
  calls.push('POST');assert.equal(calls.filter(c=>c==='skills').length,79);assert.equal(calls.filter(c=>c==='skill_artifact_versions').length,79);
  const body=JSON.parse(options.body);assert.deepEqual(body.skill_slugs,slugs);assert.equal(body.published_count,79);
  assert.equal(options.headers['Idempotency-Key'],'publication-published-synthetic-submission');
  if(fetchFailure)throw new Error('transport outcome unknown');
  posted=true;return {ok:true,json:async()=>({success:true})};
 },
 output:(_path,text)=>outputs.push(text),
 }};
}
test('all provider projections precede one full callback, then source-of-truth readback',async()=>{
 const f=fixture();await finalize(f.deps);assert.equal(f.calls.filter(x=>x==='POST').length,1);
 assert.equal(f.calls.at(-1),'submissions');assert.equal(f.outputs.length,1);
});
test('complete callback is not replayed; mismatches or partial published state cannot be closed',async()=>{
 const done=fixture({published:true});await finalize(done.deps);assert.equal(done.calls.includes('POST'),false);
 for(const options of [{badProvider:true},{published:true,partial:true}]) {
  const f=fixture(options);await assert.rejects(()=>finalize(f.deps));assert.equal(f.calls.includes('POST'),false);assert.equal(f.outputs.length,0);
 }
});
test('unknown callback transport outcome is not retried and cannot emit completion',async()=>{
 const f=fixture({fetchFailure:true});await assert.rejects(()=>finalize(f.deps),/transport/);
 assert.equal(f.calls.filter(x=>x==='POST').length,1);assert.equal(f.outputs.length,0);
});
