import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { publicationRoots, verifyRootIdentity, verifyBoundedRecoveryCoverage, artifactSlugs,
  providerRead, verifyProviderProjection, submissionIdentity, verifyPublishedSubmission } from './reconcile-submission-sync.mjs';

const repo = 'aiskillstore/marketplace';
const workflow = '.github/workflows/sync-to-supabase.yml';
const sha = /^[a-f0-9]{40}$/;
const api = path => JSON.parse(execFileSync('gh', ['api', `repos/${repo}/${path}`], {encoding:'utf8',maxBuffer:16*1024*1024,timeout:30000}));
const git = args => execFileSync('git', args, {encoding:'utf8',maxBuffer:16*1024*1024,timeout:120000}).trim();
function trusted(run, event, conclusion) {
  assert.ok(Number.isSafeInteger(run.id) && run.id > 0 && Number.isSafeInteger(run.run_attempt) && run.run_attempt > 0);
  assert.ok(run.event === event && run.status === 'completed' && run.conclusion === conclusion
    && run.path === workflow && run.head_branch === 'main' && run.head_repository?.full_name === repo && sha.test(run.head_sha), 'Untrusted recovery run');
}
function steps(jobs) {
  assert.ok(jobs.jobs?.length && jobs.total_count === jobs.jobs.length, 'Incomplete job inventory');
  return jobs.jobs.flatMap(j => j.steps ?? []);
}
function step(jobs, name, conclusion) {
  const matches = steps(jobs).filter(s => s.name === name);
  assert.ok(matches.length === 1 && matches[0].conclusion === conclusion, `Unverified stage: ${name}`);
}
export function verifyPrewriteFailure(run, attempts) {
  trusted(run, 'push', 'failure');
  assert.ok(attempts.length === run.run_attempt, 'Incomplete prior attempt history');
  for (const jobs of attempts) {
    step(jobs, 'Wait for authoritative publication completion', 'success');
    step(jobs, 'Validate bounded sync admission', 'failure');
    for (const name of ['Sync skills to Supabase','Upload provider-complete synced slugs artifact','Notify skillstore - Published submissions']) step(jobs,name,'skipped');
  }
}
export function selectBoundedSubset(expected, requested, prior) {
  assert.ok(Array.isArray(requested) && requested.length > 0 && requested.length <= 64, 'Bounded subset requires 1..64 slugs');
  assert.equal(new Set(requested).size, requested.length, 'Duplicate requested slug');
  const seen = new Set();
  for (const batch of prior) for (const slug of batch.slugs) {
    assert.ok(expected.includes(slug) && !seen.has(slug), 'Previous recovery coverage is ambiguous'); seen.add(slug);
  }
  for (const slug of requested) assert.ok(expected.includes(slug) && !seen.has(slug), 'Unknown or already recovered slug');
  return [...requested].sort();
}
export function verifyBoundedRun(run, jobs, failedId) {
  trusted(run,'workflow_dispatch','success');
  assert.equal(run.display_title, `Bounded provider recovery ${failedId}`);
  for (const name of ['Validate trusted sync correlation','Sync skills to Supabase','Upload provider-complete synced slugs artifact','Reconcile durable security change events']) step(jobs,name,'success');
  step(jobs,'Notify skillstore - Published submissions','skipped');
  for (const name of ['calculate-scores','cache-invalidate']) {
    const matches=jobs.jobs.filter(j=>j.name===name);
    assert.ok(matches.length===1 && matches[0].conclusion==='success', `Incomplete ${name}`);
  }
}
const runJobs = run => api(`actions/runs/${run.id}/attempts/${run.run_attempt}/jobs?per_page=100`);

// Freeze a single approved publication, not the workflow runtime's newer SHA.
// This function only reads; no provider/callback mutation precedes these checks.
export function loadBoundedManifest(id, { request = api, gitRead = git, env = process.env } = {}) {
  assert.match(String(id), /^[1-9][0-9]*$/);
  assert.equal(env.GITHUB_REF,'refs/heads/main');
  assert.equal(env.GITHUB_EVENT_NAME,'workflow_dispatch');
  assert.equal(env.GITHUB_REPOSITORY,repo);
  assert.match(env.GITHUB_SHA ?? '',sha);
  const run=request(`actions/runs/${id}`);
  const inventory=request('actions/workflows/sync-to-supabase.yml/runs?per_page=100').workflow_runs;
  const pushes=inventory.filter(r=>r.event==='push').sort((a,b)=>b.created_at.localeCompare(a.created_at));
  assert.equal(pushes[0]?.id,run.id,'A newer push requires separate inspection');
  const baseline=pushes[1]; trusted(baseline,'push','success');
  assert.ok(run.run_attempt<=8,'Oversized original attempt inventory');
  verifyPrewriteFailure(run,Array.from({length:run.run_attempt},(_,i)=>request(`actions/runs/${id}/attempts/${i+1}/jobs?per_page=100`)));
  const commit=request(`git/commits/${run.head_sha}`);
  const trailers=[...commit.message.matchAll(/^AgentCrew-Publication: submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40})$/gm)];
  assert.equal(trailers.length,1,'One approved publication required');
  const [,number,head,merge]=trailers[0], pr=request(`pulls/${number}`);
  assert.ok(pr.merged && pr.user?.id===254047988 && pr.user.login==='ai-skill-store[bot]'
    && pr.head?.sha===head && pr.merge_commit_sha===merge && pr.head.ref.startsWith('submission/')
    && pr.base?.ref==='main' && pr.base.repo?.full_name===repo && pr.head.repo?.full_name===repo,'Untrusted publication');
  assert.ok(commit.parents.length===1 && commit.parents[0].sha===merge,'Nonlinear publication');
  gitRead(['fetch','--no-tags','origin',run.head_sha,baseline.head_sha,head,merge]);
  gitRead(['merge-base','--is-ancestor',run.head_sha,env.GITHUB_SHA]);
  const diff = base => gitRead(['diff','--raw','--no-abbrev','--no-renames',base,run.head_sha,'--','skills/']);
  assert.equal(diff(baseline.head_sha),diff(merge),'Failed push includes another publication');
  const entries=gitRead(['diff','--name-status','-z','--no-renames',merge,run.head_sha,'--','skills/']).split('\0').filter(Boolean);
  assert.equal(entries.length%2,0);
  const files=[];
  for(let i=0;i<entries.length;i+=2) { assert.ok(['A','M'].includes(entries[i]),'Unsafe publication mutation'); files.push({path:entries[i+1]}); }
  const roots=publicationRoots(files,1000);
  assert.ok(roots.length>64,'Bounded mode only handles oversized publications');
  const reports=roots.map(root=>{
    const tree=gitRead(['rev-parse',`${run.head_sha}:${root}`]);
    assert.match(tree,sha);
    assert.equal(gitRead(['rev-parse',`${head}:${root.replace(/^skills\//,'pending/')}`]),tree,'Approved tree mismatch');
    assert.equal(gitRead(['rev-parse',`${env.GITHUB_SHA}:${root}`]),tree,'Current source tree changed');
    const {meta}=JSON.parse(gitRead(['show',`${run.head_sha}:${root}/skill-report.json`]));
    verifyRootIdentity(root,meta);
    assert.match(meta.slug,/^[a-z0-9][a-z0-9._-]*$/);
    for(const field of ['content_hash','tree_hash']) assert.match(meta[field]??'',/^[a-f0-9]{64}$/);
    return {root,tree,slug:meta.slug,content_hash:meta.content_hash,tree_hash:meta.tree_hash,marketplace_commit_sha:run.head_sha};
  });
  assert.equal(new Set(reports.map(r=>r.slug)).size,reports.length,'Duplicate publication slug');
  return {run,reports,submissionId:submissionIdentity(pr,commit.message)};
}

export function completedBatches(manifest, currentRunId) {
  const response=api('actions/workflows/sync-to-supabase.yml/runs?event=workflow_dispatch&per_page=100');
  const runs=response.workflow_runs;
  // Incomplete historical inventory is not evidence of no prior writes.
  assert.ok(runs.length<100 || runs.some(r=>Date.parse(r.created_at)<Date.parse(manifest.run.created_at)), 'Recovery inventory truncated');
  const prior=runs.filter(r=>r.display_title===`Bounded provider recovery ${manifest.run.id}` && r.id!==currentRunId);
  return prior.map(run=>{
    assert.ok(Date.parse(run.created_at)>Date.parse(manifest.run.created_at),'Recovery predates failure');
    verifyBoundedRun(run,runJobs(run),manifest.run.id);
    const slugs=artifactSlugs(run.id);
    assert.ok(slugs.length>0 && slugs.length<=64 && new Set(slugs).size===slugs.length,'Invalid bounded artifact');
    git(['fetch','--no-tags','origin',run.head_sha]);
    for(const slug of slugs) {
      const report=manifest.reports.find(r=>r.slug===slug); assert.ok(report,'Foreign recovered slug');
      assert.equal(git(['rev-parse',`${run.head_sha}:${report.root}`]),report.tree,'Recovered source tree drifted');
    }
    return {runId:run.id,slugs};
  });
}
export async function prepare() {
  assert.ok(!process.env.RESUME_FAILED_RUN && !process.env.CORRELATION_ID && !process.env.MERGE_COMMIT_SHA,'Cannot mix recovery modes');
  const manifest=loadBoundedManifest(process.env.BOUNDED_FAILED_RUN);
  const prior=completedBatches(manifest,Number(process.env.GITHUB_RUN_ID));
  const requested=String(process.env.INPUT_SLUGS??'').split(/[\s,]+/).filter(Boolean);
  const selected=selectBoundedSubset(manifest.reports.map(r=>r.slug),requested,prior);
  appendFileSync(process.env.GITHUB_OUTPUT,`sync_commit_sha=${manifest.run.head_sha}\nrecovery_slugs=${selected.join(',')}\n`);
  console.log(JSON.stringify({failedRunId:manifest.run.id,sourceSha:manifest.run.head_sha,count:selected.length,callback:'deferred'}));
}
export async function finalize({ manifestLoader = loadBoundedManifest, batchReader = completedBatches, readProvider = providerRead, fetcher = fetch, output = appendFileSync, env = process.env } = {}) {
  assert.ok(!env.AUDIT_PR && !env.RECOVERY_RUN_ID,'Cannot mix reconciliation modes');
  const manifest=manifestLoader(env.FAILED_RUN_ID);
  const requested=String(env.RECOVERY_RUN_IDS??'').split(',');
  assert.ok(requested.length>=2 && requested.length<=100 && requested.every(x=>/^[1-9][0-9]*$/.test(x)) && new Set(requested).size===requested.length,'Invalid recovery run IDs');
  const batches=batchReader(manifest,Number(env.GITHUB_RUN_ID));
  assert.deepEqual(batches.map(r=>String(r.runId)).sort(),[...requested].sort(),'Recovery run inventory mismatch');
  const slugs=verifyBoundedRecoveryCoverage(manifest.reports.map(r=>r.slug),batches);
  for(const expected of manifest.reports) {
    const skills=await readProvider('skills',['slug',expected.slug],'id,slug,plugin_path,marketplace_commit_sha,content_hash,tree_hash,current_artifact_version_id,artifact_revision');
    assert.equal(skills.length,1);
    const artifacts=await readProvider('skill_artifact_versions',['id',skills[0].current_artifact_version_id],'id,skill_id,source_path,marketplace_commit_sha,content_hash,tree_hash,artifact_revision,snapshot_status');
    verifyProviderProjection(expected,skills,artifacts);
  }
  const callback = () => readProvider('submissions',['id',manifest.submissionId],'status,published_at,published_skill_slugs');
  const before=await callback(); assert.equal(before.length,1);
  if(before[0].status==='published') {
    verifyPublishedSubmission(slugs,before); // Already complete: never send again.
  } else {
    assert.ok(before[0].status==='approved' && before[0].published_at===null
      && (before[0].published_skill_slugs==null || (Array.isArray(before[0].published_skill_slugs) && before[0].published_skill_slugs.length===0)),'Callback state requires inspection');
    const origin=new URL(env.SKILLSTORE_API_URL); assert.equal(origin.protocol,'https:');
    const secret=env.SKILLSTORE_CALLBACK_TOKEN; assert.ok(secret,'Missing callback handle');
    // One full-set callback only. A transport error is read/reconciled on the next
    // invocation; never automatically repeat it within this execution.
    const response=await fetcher(new URL('/api/submit/callback',origin),{method:'POST',redirect:'error',signal:AbortSignal.timeout(90000),
      headers:{Authorization:`Bearer ${secret}`,'Content-Type':'application/json','X-Skillstore-Callback':'true','User-Agent':'GitHub-Actions/SkillstoreBot','Idempotency-Key':`publication-published-${manifest.submissionId}`},
      body:JSON.stringify({submission_id:manifest.submissionId,event:'published',skill_slugs:slugs,published_count:slugs.length,
        workflow_run_id:Number(env.GITHUB_RUN_ID),workflow_run_url:`https://github.com/${repo}/actions/runs/${env.GITHUB_RUN_ID}`})});
    assert.ok(response.ok,`Published callback HTTP ${response.status}`);
    assert.equal((await response.json()).success,true,'Published callback not accepted');
    verifyPublishedSubmission(slugs,await callback());
  }
  output(env.GITHUB_OUTPUT,`publication_sha=${manifest.run.head_sha}\n`);
  console.log(JSON.stringify({failedRunId:manifest.run.id,recoveryRunIds:requested,verifiedCount:slugs.length}));
}
if(import.meta.url===pathToFileURL(process.argv[1]??'').href) {
  const action=process.argv[2];
  assert.ok(['prepare','finalize'].includes(action));
  (action==='prepare'?prepare():finalize()).catch(error=>{console.error(error.message);process.exitCode=1;});
}
