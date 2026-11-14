import test from 'node:test';
import assert from 'node:assert/strict';
import { verifySubmissionRecovery, verifyProviderProjection, verifiedArtifactSlugs } from '../reconcile-submission-sync.mjs';
import { verifiedScoreArtifact } from '../ancillary-sync-reconciliation.mjs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { admitMonitor } from '../source-monitor-admission.mjs';
import { recoveredPushSync, latestStatus } from '../recovered-push-sync.mjs';

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
  if(endpoint.endsWith('/status')){const {creator,...combined}=status;return {statuses:[combined]};}
  if(endpoint.endsWith('/statuses?per_page=100&page=1'))return overrides.history ?? [{...status,...overrides.status}];
  if(endpoint.endsWith('/actions/runs/4'))return {...attestation,...overrides.run};
  if(endpoint.includes('/runs/4/attempts/1/jobs'))return {total_count:1,jobs:[{steps:[{name:'Verify exact recovery and provider state',conclusion:overrides.step||'success'},{name:'Record separate reconciliation result',conclusion:'success'}]}]};
  throw new Error(endpoint);
 };}
 assert.equal(recoveredPushSync(push,[push],api()).id,4);
 assert.equal(push.conclusion,'failure');
 assert.equal(recoveredPushSync(push,[push],api({run:{display_title:'Reconcile bounded submission push 2 using recoveries 3,5'}})).id,4);
 for (const title of ['Reconcile bounded submission push 9 using recoveries 3,5','Reconcile bounded submission push 2 using recoveries 3','Reconcile bounded submission push 2 using recoveries 3,zero']) assert.equal(recoveredPushSync(push,[push],api({run:{display_title:title}})),null);
 for(const state of ['failure','pending','error'])assert.equal(recoveredPushSync(push,[push],api({history:[{...status,state},status]})),null,'newest non-success cannot fall back to old success');
 assert.equal(recoveredPushSync(push,[push],api({history:[{...status,creator:{id:1}},status]})),null,'newest wrong creator cannot fall back');
 const monitorApi=endpoint=>endpoint==='git/trees/main'?{tree:[]}
   :endpoint.includes('/workflows/')?{workflow_runs:endpoint.includes('sync-to-supabase')?[push]:[]}
     :api()(`repos/${repo}/${endpoint}`);
 assert.equal(admitMonitor(monitorApi),'');
 for(const overrides of [{status:{state:'failure'}},{status:{creator:{id:1}}},{run:{head_branch:'other'}},{run:{conclusion:'failure'}},{run:{display_title:'Reconcile submission push 9 using recovery 3'}},{run:{created_at:'invalid'}},{run:{head_repository:{full_name:'fork/repo'}}},{run:{path:'.github/workflows/sync-to-supabase.yml'}},{step:'skipped'}])assert.equal(recoveredPushSync(push,[push],api(overrides)),null);
});

test('status list is bounded, paginated and never falls back past a newer matching state',()=>{
 const calls=[];
 const full=Array.from({length:100},(_,i)=>({context:`other/${i}`}));
 const failure={context:'wanted',state:'failure'};
 assert.equal(latestStatus(sha,'wanted',endpoint=>{
   calls.push(endpoint);
   return calls.length===1?full:[failure,{context:'wanted',state:'success'}];
 }),failure);
 assert.equal(calls.length,2);
 assert.match(calls[1],/statuses\?per_page=100&page=2$/);
 assert.equal(latestStatus(sha,'wanted',()=>[]),null);
 for(const invalid of [{statuses:[]},null,[null],Array(101).fill({context:'other'})])assert.throws(()=>latestStatus(sha,'wanted',()=>invalid),/Malformed/);
 let pages=0;
 assert.throws(()=>latestStatus(sha,'wanted',()=>{pages++;return full;}),/limit/);
 assert.equal(pages,10);
});

test('a resumed run on newer main needs the exact failed-run binding, validated scope and unchanged trees',()=>{
  const e=structuredClone(evidence());
  e.recovery.head_sha='9'.repeat(40);e.recovery.display_title=`Recover provider sync ${e.push.id}`;
  e.recoveryJobs.jobs[0].steps.push({name:'Validate trusted sync correlation',conclusion:'success'});
  e.recoveryTrees=[{root,published:'8'.repeat(40),recovered:'8'.repeat(40)}];
  assert.equal(verifySubmissionRecovery(e)[0].marketplace_commit_sha,sha);
  for(const mutate of [x=>x.recovery.display_title='Recover provider sync 999',x=>x.recoveryTrees=[],x=>x.recoveryTrees[0].recovered='7'.repeat(40),x=>x.recoveryJobs.jobs[0].steps.at(-1).conclusion='skipped']) {
    const x=structuredClone(e);mutate(x);assert.throws(()=>verifySubmissionRecovery(x));
  }
});

test('provider-complete official callback recovery is separately reconciled without replaying completed provider stages',()=>{
  const e=structuredClone(evidence());
  e.recovery.display_title=`Recover provider sync ${e.push.id}`;
  e.recoveryJobs.jobs[0].steps.push({name:'Validate trusted sync correlation',conclusion:'success'});
  e.originalJobs.jobs[0].steps[1].conclusion='success';
  e.originalJobs.jobs[0].steps.push({name:'Upload provider-complete synced slugs artifact',conclusion:'success'},{name:'Notify skillstore - Published submissions',conclusion:'failure'});
  e.recoveryJobs.jobs[0].steps.find(s=>s.name==='Reconcile durable security change events').conclusion='skipped';
  e.files=e.files.map(f=>({...f,filename:f.filename.replace(root,'skills/demo')}));
  e.reports=[{root:'skills/demo',meta:{...meta,slug:'demo',source_type:'official',source_ref:head,source_url:`https://github.com/anthropics/skills/tree/${head}/skills/demo`}}];
  e.slugs=['demo'];e.recoveryTrees=[{root:'skills/demo',published:sha,recovered:sha}];
  assert.equal(verifySubmissionRecovery(e)[0].slug,'demo');
  const changed=structuredClone(e);changed.recoveryTrees[0].recovered=before;
  assert.throws(()=>verifySubmissionRecovery(changed));
});

function cacheEvidence() {
  const e = structuredClone(evidence());
  e.recovery.path = '.github/workflows/warm-cache.yml';
  e.recovery.display_title = 'Warm KV Cache';
  e.originalJobs = { total_count: 4, jobs: [
    { name: 'sync', conclusion: 'success', steps: ['Wait for authoritative publication completion', ...required,
      'Record durable publication provider result'].map(name => ({ name, conclusion: 'success' })) },
    { name: 'calculate-scores', conclusion: 'success', steps: [] },
    { name: 'cache-invalidate-shard (0)', conclusion: 'failure', steps: [{ name: 'Invalidate cache for shard 0', conclusion: 'failure' }] },
    { name: 'cache-invalidate', conclusion: 'failure', steps: [] },
  ] };
  e.recoveryJobs = { total_count: 1, jobs: [{ id: 11, name: 'warm', conclusion: 'success', steps: [
    'Download changed slugs from source workflow', 'Resolve and validate warm scope', 'Invalidate selected skill caches',
    'Warm and verify API, HTML, and optional ZIP caches', 'Upload warm verification evidence',
  ].map(name => ({ name, conclusion: 'success' })) }] };
  e.originalJobs.jobs[0].completed_at = '2026-10-01T00:30:00Z';
  e.originalJobs.jobs[1].completed_at = '2026-10-01T00:40:00Z';
  e.recoveryJobs.jobs[0].steps.find(s => s.name === 'Invalidate selected skill caches').started_at = '2026-10-01T01:01:00Z';
  const sourceArtifact = { id: 10, name: 'synced-slugs', expired: false, digest: 'sha256:' + '1'.repeat(64), workflow_run: { id: push.id, head_sha: sha } };
  const invalidation = { preflight: false, type: 'skills', slugs: e.slugs, locales: ['en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'de', 'fr', 'es', 'pt', 'ru', 'ar'], planHash: '2'.repeat(64),
    closure: { dependentPacks: { overflow: false, all: [] } },
    plan: { totals: { page: 1, api: 1, artifacts: 0 } },
    invalidated: { total: 2, page: 1, api: 1, artifacts: 0, listVersionBumped: true, listMaxStaleSeconds: 0 } };
  e.cacheEvidence = { sourceArtifact,
    log: `2026-10-01T01:01:00.000Z - synced-slugs (ID: 10, Size: 162, Expected Digest: ${sourceArtifact.digest})\n2026-10-01T01:01:01.000Z SHA256 digest of downloaded artifact is ${'1'.repeat(64)}\n2026-10-01T01:01:02.000Z ${JSON.stringify(invalidation)}    ✓\n`,
    summary: { success: true, mode: 'force', scope: 'changed', targets: 1, slugs: 1, locales: 1,
      failedEndpoints: 0, skippedEndpoints: 0, failureCount: 0, failures: [],
      plannedEndpoints: { api: 1, page: 1, zip: 0 }, completedEndpoints: { api: 1, page: 1, zip: 0 } },
    records: ['api', 'page'].map(kind => ({ phase: 'ordinary-verification', kind, resource: 'skills', slug: meta.slug,
      locale: 'en', ok: true, status: 200, cache: 'HIT', truncated: false })),
  };
  return e;
}
test('cache-only recovery proves original provider completion without replaying provider or callback', () => {
  assert.deepEqual(verifySubmissionRecovery(cacheEvidence()), [{ root, ...meta, marketplace_commit_sha: sha }]);
});
test('cache-only recovery rejects unrelated, partial, stale, forged and incomplete evidence', () => {
  const mutations = [
    e => e.recovery.head_sha = before,
    e => e.originalJobs.jobs[1].completed_at = '2026-10-01T01:02:00Z',
    e => e.originalJobs.jobs[0].completed_at = undefined,
    e => e.originalJobs.jobs[1].completed_at = 'invalid',
    e => e.recoveryJobs.jobs[0].steps.find(s => s.name === 'Invalidate selected skill caches').started_at = null,
    e => e.originalJobs.jobs[0].conclusion = 'failure',
    e => e.originalJobs.jobs[0].steps[1].conclusion = 'failure',
    e => e.originalJobs.jobs[0].steps.find(s => s.name === 'Notify skillstore - Published submissions').conclusion = 'failure',
    e => e.originalJobs.jobs[1].conclusion = 'failure',
    e => { e.originalJobs.jobs.push({ name: 'other-write', conclusion: 'failure', steps: [] }); e.originalJobs.total_count++; },
    e => e.recoveryJobs.jobs[0].steps[2].conclusion = 'skipped',
    e => e.cacheEvidence.sourceArtifact.workflow_run.id = 999,
    e => e.cacheEvidence.sourceArtifact.workflow_run.head_sha = before,
    e => e.cacheEvidence.sourceArtifact.expired = true,
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('ID: 10', 'ID: 999'),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('digest of downloaded artifact is ' + '1'.repeat(64), 'digest of downloaded artifact is ' + '9'.repeat(64)),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('"listVersionBumped":true', '"listVersionBumped":false'),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('"total":2', '"total":1'),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('"overflow":false', '"overflow":true'),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('"all":[]', '"all":["unverified-pack"]'),
    e => e.cacheEvidence.log = e.cacheEvidence.log.replace('"en","zh-hans"', '"en"'),
    e => e.cacheEvidence.summary.mode = 'warm',
    e => e.cacheEvidence.summary.failedEndpoints = 1,
    e => e.cacheEvidence.summary.completedEndpoints.page = 0,
    e => e.cacheEvidence.records = e.cacheEvidence.records.slice(0, 1),
    e => e.cacheEvidence.records[0].slug = 'another-skill',
    e => e.cacheEvidence.records[0].ok = false,
    e => e.cacheEvidence.records[0].cache = 'MISS',
    e => e.cacheEvidence.records[0].locale = 'fr',
    e => e.slugs.push('uncovered-skill'),
  ];
  for (const mutate of mutations) {
    const e = cacheEvidence(); mutate(e);
    assert.throws(() => verifySubmissionRecovery(e), mutate.toString());
  }
});

function ancillaryEvidence() {
  const e = cacheEvidence();
  e.originalJobs.jobs = e.originalJobs.jobs.slice(0, 2);
  e.originalJobs.total_count = 2;
  e.originalJobs.jobs[0].conclusion = 'failure';
  e.originalJobs.jobs[0].steps.at(-1).conclusion = null;
  e.originalJobs.jobs[1].conclusion = 'skipped';
  e.scoreRecovery = {...e.recovery, id: 5, path: '.github/workflows/recalculate-scores.yml',
    created_at: '2026-10-01T00:40:00Z'};
  e.scoreJobs = {total_count: 2, jobs: [
    {name:'recalculate',conclusion:'success',completed_at:'2026-10-01T00:49:00Z',steps:[{name:'Recalculate quality scores',conclusion:'success'},{name:'Upload exact score closure',conclusion:'success'}]},
    {name:'score cache closure (hosted)',conclusion:'success',completed_at:'2026-10-01T00:50:00Z',steps:[{name:'Invalidate only successfully rescored API entries',conclusion:'success'},{name:'Verify every production API cache readback',conclusion:'success'}]},
  ]};
  e.scoreEvidence = {metadata:{sourceRunId:'5',workflowCommit:sha,processed:1,successfulCount:1,failedCount:0,errors:0,dryRun:false},
    slugs:e.slugs,failedSlugs:[],scores:[{slug:meta.slug,snapshotId:'score-snapshot',qualityScore:50,calculatedAt:'2026-10-01T00:45:00Z'}]};
  return e;
}
test('completed provider and callback can be reconciled after separate exact scoring and cache recovery', () => {
  assert.deepEqual(verifySubmissionRecovery(ancillaryEvidence()), [{root,...meta,marketplace_commit_sha:sha}]);
});
test('separate ancillary recovery rejects replay, stale or widened score/cache evidence', () => {
  const mutations = [
    e=>e.originalJobs.jobs[0].steps.find(s=>s.name==='Sync skills to Supabase').conclusion='failure',
    e=>e.originalJobs.jobs[0].steps.find(s=>s.name==='Notify skillstore - Published submissions').conclusion='failure',
    e=>e.originalJobs.jobs[1].conclusion='success',
    e=>e.scoreRecovery.head_sha=before,
    e=>e.scoreRecovery.path='.github/workflows/sync-to-supabase.yml',
    e=>e.scoreRecovery.head_repository.full_name='fork/repo',
    e=>e.scoreRecovery.status='in_progress',
    e=>e.scoreRecovery.created_at=e.push.created_at,
    e=>e.scoreJobs.jobs[1].completed_at=e.recovery.created_at,
    e=>delete e.scoreJobs.jobs[0].completed_at,
    e=>delete e.originalJobs.jobs[0].completed_at,
    e=>e.scoreJobs.jobs[1].conclusion='failure',
    e=>e.scoreJobs.jobs[1].steps[1].conclusion='skipped',
    e=>e.scoreEvidence.slugs=['other'],
    e=>e.scoreEvidence.metadata.dryRun=true,
    e=>e.scoreEvidence.metadata.sourceRunId='9',
    e=>e.scoreEvidence.metadata.workflowCommit=before,
    e=>e.scoreEvidence.metadata.successfulCount=2,
    e=>e.scoreEvidence.scores[0].slug='other',
    e=>e.scoreEvidence.scores[0].calculatedAt=e.push.created_at,
    e=>e.scoreEvidence.failedSlugs=['other'],
    e=>e.cacheEvidence.summary.failedEndpoints=1,
  ];
  for (const mutate of mutations) {const e=structuredClone(ancillaryEvidence());mutate(e);assert.throws(()=>verifySubmissionRecovery(e));}
});
test('score artifact is bounded, digest-bound and has only the exact regular closure files', () => {
  const make=entries=>execFileSync('python3',['-c',`import io,sys,json,zipfile
b=io.BytesIO()
with zipfile.ZipFile(b,'w') as z:
 for name,text in json.loads(sys.argv[1]):z.writestr(name,text)
sys.stdout.buffer.write(b.getvalue())`,JSON.stringify(entries)]);
  const e=ancillaryEvidence().scoreEvidence;
  const entries=[['metadata.json',JSON.stringify(e.metadata)],['successful-slugs.txt',meta.slug+'\n'],['failed-slugs.txt',''],['expected-score-evidence.json',JSON.stringify({scores:e.scores})]];
  const info=b=>({size_in_bytes:b.length,digest:`sha256:${createHash('sha256').update(b).digest('hex')}`,expired:false});
  const zip=make(entries);
  assert.deepEqual(verifiedScoreArtifact(zip,info(zip)),e);
  assert.throws(()=>verifiedScoreArtifact(zip,{...info(zip),expired:true}));
  assert.throws(()=>verifiedScoreArtifact(zip,{...info(zip),digest:'sha256:'+'0'.repeat(64)}));
  for (const files of [entries.slice(1),[...entries,['other','x']],entries.map(([n,t])=>[n==='metadata.json'?'../metadata.json':n,t])]) {
    const b=make(files);assert.throws(()=>verifiedScoreArtifact(b,info(b)));
  }
});
test('separate scoring input is opt-in and cannot mix bounded write finalization', () => {
  const workflow=readFileSync('.github/workflows/reconcile-submission-sync.yml','utf8');
  assert.match(workflow,/score_recovery_run_id:/);
  assert.match(workflow,/SCORE_RECOVERY_RUN_ID: \$\{\{ inputs.score_recovery_run_id \}\}/);
  assert.match(workflow,/if \[ -n "\$RECOVERY_RUN_IDS" \]; then\s+test -z "\$SCORE_RECOVERY_RUN_ID"/);
  const source=readFileSync('scripts/reconcile-submission-sync.mjs','utf8');
  assert.match(source,/verifyPublishedSubmission\(plan.map/);
  assert.match(source,/verifyProviderProjection\(expected,skills,artifacts\)/);
  assert.doesNotMatch(readFileSync('scripts/ancillary-sync-reconciliation.mjs','utf8'),/fetch\(|gh api|method:/);
});
