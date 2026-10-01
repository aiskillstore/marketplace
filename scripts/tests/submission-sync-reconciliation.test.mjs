import test from 'node:test';
import assert from 'node:assert/strict';
import { verifySubmissionRecovery, verifyProviderProjection, verifiedArtifactSlugs } from '../reconcile-submission-sync.mjs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { admitMonitor } from '../source-monitor-admission.mjs';
import { recoveredPushSync } from '../recovered-push-sync.mjs';

const repo = 'aiskillstore/marketplace';
const sha = 'b'.repeat(40), head = 'c'.repeat(40), merge = 'd'.repeat(40), before = 'a'.repeat(40);
const correlation = `submission-pr-3619-${head}-${merge}`;
const push = {id:2,run_attempt:1,event:'push',status:'completed',conclusion:'failure',head_sha:sha,head_branch:'main',path:'.github/workflows/sync-to-supabase.yml',head_repository:{full_name:repo},created_at:'2026-10-01T00:00:00Z'};
const recovery = {...push,id:3,event:'workflow_dispatch',conclusion:'success',created_at:'2026-10-01T01:00:00Z'};
const root = 'skills/apidojo-io/tiktok-scraper';
const meta = {slug:'apidojo-io-tiktok-scraper',content_hash:'e'.repeat(64),tree_hash:'f'.repeat(64)};
const required = ['Sync skills to Supabase','Upload provider-complete synced slugs artifact','Reconcile durable security change events','Notify skillstore - Published submissions'];
function evidence() {
  return {push,recovery,baseline:{head_sha:before,conclusion:'success'},commit:{parents:[{sha:merge}],message:`Publish\n\nAgentCrew-Publication: ${correlation}`},pr:{number:3619,merged:true,merge_commit_sha:merge,user:{id:254047988,login:'ai-skill-store[bot]'},head:{sha:head,ref:'submission/example',repo:{full_name:repo}},base:{ref:'main',repo:{full_name:repo}}},files:[{filename:`${root}/SKILL.md`,status:'modified'},{filename:`${root}/skill-report.json`,status:'modified'}],reports:[{root,meta}],slugs:[meta.slug],originalJobs:{total_count:1,jobs:[{steps:[{name:'Wait for authoritative publication completion',conclusion:'success'},{name:'Sync skills to Supabase',conclusion:'failure'}]}]},recoveryJobs:{total_count:3,jobs:[{name:'sync',conclusion:'success',steps:required.map(name=>({name,conclusion:'success'}))},{name:'calculate-scores',conclusion:'success'},{name:'cache-invalidate',conclusion:'success'}]}};
}
test('exact submission publication and full recovered slug set produce a read-only reconciliation plan',()=>{
  assert.deepEqual(verifySubmissionRecovery(evidence()), [{root,...meta,marketplace_commit_sha:sha}]);
});
test('unrelated, partial, duplicate, stale and nonterminal recovery never authorize reconciliation',()=>{
  const mutations=[e=>e.recovery.head_sha=before,e=>e.recovery.head_repository.full_name='fork/repo',e=>e.recovery.path='other.yml',e=>e.recovery.created_at=e.push.created_at,e=>e.push.conclusion='success',e=>e.recovery.status='in_progress',e=>e.baseline.conclusion='failure',e=>e.commit.parents.push({sha:head}),e=>e.commit.message='No publication trailer',e=>e.pr.head.sha=before,e=>e.pr.user.id=9,e=>e.files.push({filename:'scripts/other.mjs',status:'modified'}),e=>e.files[0].status='removed',e=>e.files.push({filename:`skills/other/root/SKILL.md`,status:'added'}),e=>e.slugs=[],e=>e.slugs.push(e.slugs[0]),e=>e.reports[0].meta.tree_hash='missing',e=>e.recoveryJobs.total_count=4,e=>e.recoveryJobs.jobs[0].steps[0].conclusion='skipped',e=>e.recoveryJobs.jobs[1].conclusion='failure',e=>e.originalJobs.jobs[0].steps[1].conclusion='success'];
  for(const mutate of mutations){const e=structuredClone(evidence());mutate(e);assert.throws(()=>verifySubmissionRecovery(e));}
});
test('provider must confirm the current exact artifact, not a historical artifact or stale projection',()=>{
  const expected=verifySubmissionRecovery(evidence())[0];
  const skill={id:'skill-id',slug:meta.slug,plugin_path:root,marketplace_commit_sha:sha,content_hash:meta.content_hash,tree_hash:meta.tree_hash,current_artifact_version_id:'version-id',artifact_revision:1};
  const artifact={id:'version-id',skill_id:'skill-id',source_path:root,marketplace_commit_sha:sha,content_hash:meta.content_hash,tree_hash:meta.tree_hash,artifact_revision:1,snapshot_status:'exact'};
  assert.doesNotThrow(()=>verifyProviderProjection(expected,[skill],[artifact]));
  for(const field of ['slug','plugin_path','marketplace_commit_sha','content_hash','tree_hash','current_artifact_version_id']) assert.throws(()=>verifyProviderProjection(expected,[{...skill,[field]:'wrong'}],[artifact]));
  for(const field of ['id','skill_id','source_path','marketplace_commit_sha','content_hash','tree_hash','artifact_revision','snapshot_status']) assert.throws(()=>verifyProviderProjection(expected,[skill],[{...artifact,[field]:'wrong'}]));
  assert.throws(()=>verifyProviderProjection(expected,[],[artifact]));
  assert.throws(()=>verifyProviderProjection(expected,[skill,skill],[artifact]));
});
test('artifact verification rejects unsafe manifests and altered/expired archive bytes',()=>{
 const make=entries=>execFileSync('python3',['-c',`import io,sys,json,zipfile\nb=io.BytesIO()\nwith zipfile.ZipFile(b,'w') as z:\n for name,text in json.loads(sys.argv[1]):z.writestr(name,text)\nsys.stdout.buffer.write(b.getvalue())`,JSON.stringify(entries)]);
 const zip=make([['synced-slugs.txt',meta.slug+'\n']]);
 const info=b=>({size_in_bytes:b.length,digest:`sha256:${createHash('sha256').update(b).digest('hex')}`,expired:false});
 assert.deepEqual(verifiedArtifactSlugs(zip,info(zip)),[meta.slug]);
 assert.throws(()=>verifiedArtifactSlugs(zip,{...info(zip),digest:'sha256:'+'0'.repeat(64)}));
 assert.throws(()=>verifiedArtifactSlugs(zip,{...info(zip),expired:true}));
 for(const entries of [[['../synced-slugs.txt',meta.slug]],[['synced-slugs.txt','x'],['extra','x']],[['synced-slugs.txt','x'],['synced-slugs.txt','x']],[['synced-slugs.txt','x'.repeat(8193)]]]){const b=make(entries);assert.throws(()=>verifiedArtifactSlugs(b,info(b)));}
});
test('new receiver is pinned, main-only, read-only for provider and emits a separate context',()=>{
 const w=readFileSync('.github/workflows/reconcile-submission-sync.yml','utf8');
 assert.match(w,/ref: \$\{\{ github.sha \}\}/);
 assert.match(w,/github.ref == 'refs\/heads\/main'/);
 assert.match(w,/agentcrew\/provider-reconciliation\/\$FAILED_RUN_ID/);
 assert.doesNotMatch(w,/contents: write|workflow_run:|push:|skill sync|\/dispatches|agentcrew\/publication\//);
 const source=readFileSync('scripts/reconcile-submission-sync.mjs','utf8');
 assert.match(source,/method:'GET'/);
 assert.doesNotMatch(source,/method:'POST'|method:'PATCH'|method:'PUT'|skill sync|\/rpc\//);
 for(const name of ['scripts/source-monitor-admission.mjs','scripts/continue-merged-publications.mjs','scripts/publish-approved-batch.mjs'])assert.match(readFileSync(name,'utf8'),/recoveredPushSync/);
 assert.match(readFileSync('.github/workflows/sync-to-supabase.yml','utf8'),/node \.\/scripts\/recovered-push-sync.mjs/);
});
test('shared guard accepts only a separate successful attestation run, preserving the old failure',()=>{
 const attestation={id:4,run_attempt:1,event:'workflow_dispatch',status:'completed',conclusion:'success',path:'.github/workflows/reconcile-submission-sync.yml',head_branch:'main',head_repository:{full_name:repo},display_title:'Reconcile submission push 2 using recovery 3',created_at:'2026-10-01T02:00:00Z'};
 const status={context:'agentcrew/provider-reconciliation/2',state:'success',creator:{id:41898282,login:'github-actions[bot]'},target_url:`https://github.com/${repo}/actions/runs/4`};
 function api(overrides={}){return endpoint=>{
  if(endpoint.endsWith('/status'))return {statuses:[{...status,...overrides.status}]};
  if(endpoint.endsWith('/actions/runs/4'))return {...attestation,...overrides.run};
  if(endpoint.includes('/runs/4/attempts/1/jobs'))return {total_count:1,jobs:[{steps:[{name:'Verify exact recovery and provider state',conclusion:overrides.step||'success'},{name:'Record separate reconciliation result',conclusion:'success'}]}]};
  throw new Error(endpoint);
 };}
 assert.equal(recoveredPushSync(push,[push],api()).id,4);
 assert.equal(push.conclusion,'failure');
 const monitorApi=endpoint=>endpoint==='git/trees/main'?{tree:[]}
   :endpoint.includes('/workflows/')?{workflow_runs:endpoint.includes('sync-to-supabase')?[push]:[]}
     :api()(`repos/${repo}/${endpoint}`);
 assert.equal(admitMonitor(monitorApi),'');
 for(const overrides of [{status:{state:'failure'}},{status:{creator:{id:1}}},{run:{head_branch:'other'}},{run:{conclusion:'failure'}},{run:{display_title:'Reconcile submission push 9 using recovery 3'}},{run:{created_at:'invalid'}},{run:{head_repository:{full_name:'fork/repo'}}},{run:{path:'.github/workflows/sync-to-supabase.yml'}},{step:'skipped'}])assert.equal(recoveredPushSync(push,[push],api(overrides)),null);
});
