import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as resolver from '../resolve-approved-submission.mjs';
import { main } from '../continue-merged-publications.mjs';

const path='pending/cagdasyurekli/agy-worker/skill-report.json';
const oldBlob='9db4ee7c8a2fe82d3dd189dfb36198d10ffd583f';
const newBlob='a'.repeat(40);
function exercise(blob,apply=true){
 const calls=[],writes=[];
 const pr={number:3697,merged_at:'2026-10-07T01:01:08Z',base:{ref:'main'},
  user:{id:254047988,login:'ai-skill-store[bot]'},head:{repo:{full_name:'aiskillstore/marketplace'},ref:'submission/test',sha:'b3abb28a220e59e65bd5a5225d7f84a483cb12aa'},
  merge_commit_sha:'561c1742ac3fb557a3b96169586dad1dd14454c6'};
 const request=(endpoint,data)=>{
  calls.push(endpoint);
  if(data){writes.push({endpoint,data});return;}
  if(endpoint.endsWith('/git/trees/main'))return {tree:[{path:'pending',sha:'tree'}]};
  if(endpoint.includes('/git/trees/tree?'))return {truncated:false,tree:[{path:path.slice(8),sha:blob}]};
  if(endpoint.includes('/pulls?'))return [pr];
  if(endpoint.includes('/pulls/3697/files'))return [{filename:path,sha:blob}];
  if(endpoint.endsWith('/pulls/3697'))return pr;
  // All downstream gates appear clear: this is the dangerous recovered-provider counterexample.
  if(endpoint.includes('/actions/workflows/'))return {workflow_runs:[]};
  if(endpoint.includes('/statuses?')||endpoint.includes('/git/matching-refs/'))return [];
  throw Error(`Unexpected endpoint: ${endpoint}`);
 };
 const before=[...process.argv];
 if(apply)process.argv.push('--apply');
 let error;
 try{main(request);}catch(e){error=e;}finally{process.argv.splice(0,process.argv.length,...before);}
 return {calls,writes,error};
}

test('old reviewed report cannot dispatch after provider gate clears, even with --apply',()=>{
 const result=exercise(oldBlob);
 assert.match(result.error?.message??'',/publication hold.*3703/i);
 assert.deepEqual(result.writes,[]);
 assert.equal(result.calls.length,2,'hold acts on current inventory before querying/dispatching receivers');
});
test('dry-run uses the same hold rather than displaying a releasable batch',()=>{
 const result=exercise(oldBlob,false);
 assert.match(result.error?.message??'',/publication hold.*3703/i);assert.deepEqual(result.writes,[]);
});
test('an unrelated blob is not automatically held and still follows ordinary gates',()=>{
 const result=exercise(newBlob);
 assert.equal(result.error,undefined);assert.equal(result.writes.length,1);
 assert.match(result.writes[0].endpoint,/publish-approved-batch.yml\/dispatches$/);
});
test('shared guard is pinned to exact report path and immutable blob, not all agy-worker versions',()=>{
 assert.equal(typeof resolver.assertPublicationReportNotHeld,'function');
 assert.throws(()=>resolver.assertPublicationReportNotHeld(path,oldBlob),resolver.PublicationValidationError);
 assert.doesNotThrow(()=>resolver.assertPublicationReportNotHeld(path,newBlob));
 assert.doesNotThrow(()=>resolver.assertPublicationReportNotHeld('pending/other/skill-report.json',oldBlob));
});
test('receiver derives the same Git SHA1 from raw bytes, including UTF-8 length',()=>{
 assert.equal(typeof resolver.publicationReportBlobSha,'function');
 assert.equal(resolver.publicationReportBlobSha(Buffer.from('hello\n')),'ce013625030ba8dba906f756967f9e9ca394464a');
 // Git hash-object result for the exact UTF-8 bytes of é + newline.
 assert.equal(resolver.publicationReportBlobSha(Buffer.from('é\n')),'c6003325155f475bd7c87731607525dce73be9cf');
});
test('single and batch receivers share the raw-report hold before resolving publication plan',()=>{
 const source=readFileSync('scripts/resolve-approved-submission.mjs','utf8');
 assert.match(source,/assertPublicationReportNotHeld\(`\$\{pendingDir\}\/skill-report\.json`, publicationReportBlobSha\(readFileSync\(reportPath\)\)\)/);
 assert.ok(source.indexOf('assertPublicationReportNotHeld(`${pendingDir}')<source.indexOf("const report = readJson(reportPath"));
 const batch=readFileSync('scripts/publish-approved-batch.mjs','utf8');
 assert.match(batch,/row\.plan = resolveApprovedSubmission/);
 const single=readFileSync('.github/workflows/on-pr-merge.yml','utf8');
 assert.match(single,/scripts\/resolve-approved-submission.mjs/);
});
