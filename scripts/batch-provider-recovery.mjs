import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { appendFileSync, readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { publicationRoots, verifyRootIdentity, submissionIdentity, providerRead, verifyProviderProjection, verifyPublishedSubmission, artifactSlugs, createGithubEvidenceReader } from './reconcile-submission-sync.mjs';
import { latestStatus } from './recovered-push-sync.mjs';

const repo = 'aiskillstore/marketplace';
const workflow = '.github/workflows/sync-to-supabase.yml';
const hash = value => createHash('sha256').update(value).digest('hex');
const api = path => JSON.parse(execFileSync('gh', ['api', `repos/${repo}/${path}`], { encoding:'utf8', maxBuffer:16*1024*1024, timeout:30000 }));
const git = args => execFileSync('git', args, { encoding:'utf8', maxBuffer:16*1024*1024, timeout:120000 }).trim();
const marker = /^AgentCrew-Publication: (submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40}))$/gm;
const skillColumns = 'id,slug,status,distribution_state,plugin_path,marketplace_commit_sha,content_hash,tree_hash,current_artifact_version_id,artifact_revision';
const artifactColumns = 'id,skill_id,source_path,marketplace_commit_sha,content_hash,tree_hash,artifact_revision,snapshot_status';

export function verifyStage(result, name, conclusion) {
  assert.ok(result.jobs?.length && result.total_count === result.jobs.length, 'Incomplete job evidence');
  const steps = result.jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
  assert.equal(steps.length, 1, `Missing stage ${name}`);
  assert.equal(steps[0].conclusion, conclusion, `Unclosed stage ${name}`);
}
function trusted(run, event, conclusion, path=workflow) {
  assert.ok(Number.isSafeInteger(run.id) && run.id>0 && Number.isSafeInteger(run.run_attempt) && run.run_attempt>0);
  assert.ok(run.event===event && run.conclusion===conclusion && run.status==='completed' && run.path===path
    && run.head_branch==='main' && run.head_repository?.full_name===repo && /^[a-f0-9]{40}$/.test(run.head_sha), 'Untrusted batch run');
}
const jobs = run => api(`actions/runs/${run.id}/attempts/${run.run_attempt}/jobs?per_page=100`);
export function classifyProjection(expected, skills, artifacts) {
  if (skills.length===0) {
    assert.deepEqual(artifacts, [], 'Orphan artifact requires separate recovery');
    return 'initial';
  }
  assert.equal(skills.length,1);
  assert.ok(skills[0].status==='approved' && skills[0].distribution_state==='active', 'Suppressed or inactive provider cannot be reused');
  verifyProviderProjection(expected, skills, artifacts);
  return 'reuse';
}
export function verifyOriginalOutcomes(log, reports) {
  const synced=[...log.matchAll(/✓ Synced: ([a-z0-9]+(?:-[a-z0-9]+)*)\r?$/gm)].map(m=>m[1]);
  const failed=[...log.matchAll(/✗ Error syncing ([a-z0-9]+(?:-[a-z0-9]+)*): Source distribution is suppressed or could not be verified\r?$/gm)].map(m=>m[1]);
  assert.ok(synced.length>0 && failed.length>0, 'Not an inspected source-gate partial failure');
  const all=[...synced,...failed];
  assert.equal(new Set(all).size,all.length,'Ambiguous original provider outcomes');
  assert.deepEqual(all.sort(),reports.map(r=>r.slug).sort(),'Original outcomes do not cover the exact batch');
  assert.ok(log.includes(`Sync complete: ${synced.length} synced, ${failed.length} errors`),'Missing original summary');
  return {synced,failed};
}

export function verifyCallbacks(reports, callbacks) {
  const expected = [...new Set(reports.map(r=>r.submissionId))].sort();
  assert.deepEqual(callbacks.map(c=>c.submission_id).sort(),expected,'Ambiguous callback ownership');
  for (const c of callbacks) assert.deepEqual([...c.skill_slugs].sort(),reports.filter(r=>r.submissionId===c.submission_id).map(r=>r.slug).sort(),'Callback scope mismatch');
}

// This proof describes the actual atomic publisher push. A later runtime commit
// may contain pending approvals, but may not change any published Skill tree.
export async function loadBatch(id, currentSha=process.env.GITHUB_SHA) {
  assert.match(String(id),/^[1-9][0-9]*$/);
  assert.match(currentSha ?? '',/^[a-f0-9]{40}$/);
  const run=api(`actions/runs/${id}`); trusted(run,'push','failure');
  const runs=api('actions/workflows/sync-to-supabase.yml/runs?per_page=100').workflow_runs;
  const pushes=runs.filter(r=>r.event==='push').sort((a,b)=>b.created_at.localeCompare(a.created_at));
  assert.equal(pushes[0]?.id,run.id,'A newer provider push requires separate inspection');
  const baseline=pushes[1]; trusted(baseline,'push','success');
  assert.equal(run.run_attempt,1,'Batch recovery requires inspection of a single original attempt');
  const originalJobs=jobs(run);
  verifyStage(originalJobs,'Wait for authoritative publication completion','success');
  verifyStage(originalJobs,'Sync skills to Supabase','failure');
  verifyStage(originalJobs,'Notify skillstore - Published submissions','skipped');
  verifyStage(originalJobs,'Record durable publication provider result','success');
  git(['fetch','--no-tags','origin',run.head_sha,baseline.head_sha,currentSha]);
  git(['merge-base','--is-ancestor',run.head_sha,currentSha]);
  const publications=[]; let cursor=run.head_sha;
  while (publications.length<=25) {
    const commit=api(`git/commits/${cursor}`);
    const matches=[...commit.message.matchAll(marker)];
    if (!matches.length) break;
    assert.equal(matches.length,1); assert.equal(commit.parents.length,1,'Nonlinear publisher commit');
    const [,correlation,number,head,merge]=matches[0];
    publications.unshift({commit,sha:cursor,correlation,number:Number(number),head,merge});
    cursor=commit.parents[0].sha;
  }
  assert.ok(publications.length>1 && publications.length<=25,'Not a bounded multi-PR publication');
  assert.equal(new Set(publications.map(p=>p.correlation)).size,publications.length);
  assert.equal(git(['diff','--name-only',baseline.head_sha,cursor,'--','skills/']),'','Unrelated unsynced publication');
  assert.equal(git(['diff','--name-only',run.head_sha,currentSha,'--','skills/']),'','Published skills changed after failure');
  const batch=hash(publications.map(p=>p.correlation).sort().join('\n'));
  let publisherId; const reports=[];
  for (const p of publications) {
    const pr=api(`pulls/${p.number}`);
    assert.ok(pr.merged && pr.head.sha===p.head && pr.merge_commit_sha===p.merge && pr.user?.id===254047988
      && pr.user.login==='ai-skill-store[bot]' && pr.head.ref.startsWith('submission/') && pr.base.ref==='main'
      && pr.base.repo.full_name===repo && pr.head.repo.full_name===repo,'Untrusted batch approval');
    git(['fetch','--no-tags','origin',p.head]);
    git(['merge-base','--is-ancestor',p.merge,p.commit.parents[0].sha]);
    const status=latestStatus(p.merge,`agentcrew/publication/${hash(p.correlation)}`,endpoint=>api(endpoint.slice(`repos/${repo}/`.length)));
    const match=status?.target_url?.match(/^https:\/\/github.com\/aiskillstore\/marketplace\/actions\/runs\/([1-9][0-9]*)$/);
    assert.ok(status?.state==='failure' && status.creator?.id===41898282 && status.creator.login==='github-actions[bot]'
      && status.description==='Correlated provider sync failed; inspection required' && match,'Unexpected provider result');
    const statuses=api(`commits/${p.merge}/statuses?per_page=100`);
    assert.ok(statuses.length<100,'Truncated publication attempts');
    const seen=new Set();
    const attempts=statuses.filter(s=> { if(seen.has(s.context)) return false; seen.add(s.context); return s.context.startsWith(`agentcrew/publication-attempt/${hash(p.correlation)}/`); });
    const completed=attempts.filter(s=>s.state==='success' && s.creator?.id===254047988 && s.creator.login==='ai-skill-store[bot]'
      && s.description==='Exact publication attempt completed' && s.target_url===status.target_url);
    assert.equal(completed.length,1,'Missing unique successful publication attempt');
    if (publisherId) assert.equal(publisherId,match[1],'Mixed publication owners'); else publisherId=match[1];
    const submissionId=submissionIdentity(pr,p.commit.message);
    const paths=git(['diff','--name-only','--no-renames',p.commit.parents[0].sha,p.sha,'--','skills/']).split('\n').filter(Boolean);
    const roots=publicationRoots(paths.map(path=>({path})),64);
    for(const root of roots) {
      const tree=git(['rev-parse',`${p.sha}:${root}`]);
      assert.equal(tree,git(['rev-parse',`${p.head}:${root.replace(/^skills\//,'pending/')}`]),'Unapproved tree');
      assert.equal(tree,git(['rev-parse',`${run.head_sha}:${root}`]),'Batch overwrote another member');
      const {meta}=JSON.parse(git(['show',`${run.head_sha}:${root}/skill-report.json`]));
      verifyRootIdentity(root,meta);
      assert.match(meta.slug,/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
      for(const field of ['content_hash','tree_hash']) assert.match(meta[field]??'',/^[a-f0-9]{64}$/);
      reports.push({root,slug:meta.slug,content_hash:meta.content_hash,tree_hash:meta.tree_hash,marketplace_commit_sha:run.head_sha,submissionId,prNumber:p.number});
    }
  }
  assert.ok(reports.length<=64 && new Set(reports.map(r=>r.slug)).size===reports.length);
  const actualRoots=publicationRoots(git(['diff','--name-only',cursor,run.head_sha,'--','skills/']).split('\n').map(path=>({path})),64);
  assert.deepEqual(reports.map(r=>r.root).sort(),actualRoots,'Batch root coverage differs');
  const publisher=api(`actions/runs/${publisherId}`); trusted(publisher,'workflow_dispatch','success','.github/workflows/publish-approved-batch.yml');
  assert.equal(publisher.display_title,`Publication batch ${batch}`,'Publisher batch identity mismatch');
  const callbacks=publications.map(p=>({submission_id:reports.find(r=>r.prNumber===p.number).submissionId,skill_slugs:reports.filter(r=>r.prNumber===p.number).map(r=>r.slug).sort()}));
  verifyCallbacks(reports,callbacks);
  const providerJob=originalJobs.jobs.filter(j=>j.steps?.some(s=>s.name==='Sync skills to Supabase'));
  assert.equal(providerJob.length,1);
  const raw=createGithubEvidenceReader();
  const outcomes=verifyOriginalOutcomes(raw(`repos/${repo}/actions/jobs/${providerJob[0].id}/logs`).toString('utf8'),reports);
  return {run,reports,callbacks,publisherId,outcomes};
}
async function projection(r) {
  const skills=await providerRead('skills',['slug',r.slug],skillColumns);
  const artifacts=await providerRead('skill_artifact_versions',skills[0]?.current_artifact_version_id ? ['id',skills[0].current_artifact_version_id] : ['source_path',r.root],artifactColumns);
  return {skills,artifacts};
}
export async function prepareBatch(id) {
  const plan=await loadBatch(id);
  const pending=[],reused=[];
  for(const r of plan.reports) {
    const p=await projection(r);
    (classifyProjection(r,p.skills,p.artifacts)==='initial'?pending:reused).push(r);
  }
  assert.deepEqual(reused.map(r=>r.slug).sort(),[...plan.outcomes.synced].sort(),'Unproven provider reuse');
  assert.deepEqual(pending.map(r=>r.slug).sort(),[...plan.outcomes.failed].sort(),'Original failed roots already changed; inspect effects');
  for (const c of plan.callbacks) {
    const rows=await providerRead('submissions',['id',c.submission_id],'status,pr_number,workflow_run_id,published_at,published_skill_slugs');
    assert.equal(rows.length,1); assert.equal(rows[0].pr_number,plan.reports.find(r=>r.submissionId===c.submission_id).prNumber);
    assert.equal(String(rows[0].workflow_run_id),String(plan.publisherId));
    assert.equal(rows[0].status,'approved'); assert.equal(rows[0].published_at,null);
    assert.ok(rows[0].published_skill_slugs==null || rows[0].published_skill_slugs.length===0,'Callback already received');
  }
  writeFileSync('batch-recovery-plan.json',JSON.stringify(plan));
  writeFileSync('batch-recovery-callbacks.json',JSON.stringify(plan.callbacks));
  appendFileSync(process.env.GITHUB_OUTPUT,`sync_commit_sha=${plan.run.head_sha}\nrecovery_slugs=${plan.reports.map(r=>r.slug).join(',')}\nprovider_mode=partial-batch\nprovider_complete=false\nbatch_recovery=true\nbatch_pending_paths=${pending.map(r=>r.root.slice(7)).join(' ')}\nbatch_reused_slugs=${reused.map(r=>r.slug).join(',')}\n`);
  console.log(JSON.stringify({failedRunId:plan.run.id,initial:pending.map(r=>r.slug),reused:reused.map(r=>r.slug)}));
}
export async function verifyBatchProviders(plan) {
  for (const r of plan.reports) {
    const p=await projection(r); assert.equal(classifyProjection(r,p.skills,p.artifacts),'reuse','Provider still absent');
  }
}
export async function reconcileBatch(id,recovery) {
  trusted(recovery,'workflow_dispatch','success');
  assert.equal(recovery.display_title,`Recover provider sync ${id}`);
  const plan=await loadBatch(id,recovery.head_sha);
  assert.ok(Date.parse(recovery.created_at)>Date.parse(plan.run.created_at));
  const recovered=jobs(recovery);
  for(const name of ['Validate trusted sync correlation','Sync skills to Supabase','Upload provider-complete synced slugs artifact','Notify skillstore - Published submissions']) verifyStage(recovered,name,'success');
  for(const name of ['calculate-scores','cache-invalidate']) assert.ok(recovered.jobs.filter(j=>j.name===name && j.conclusion==='success').length===1,`Incomplete ${name}`);
  assert.deepEqual(artifactSlugs(recovery.id).sort(),plan.reports.map(r=>r.slug).sort());
  await verifyBatchProviders(plan);
  for(const c of plan.callbacks) verifyPublishedSubmission(c.skill_slugs,await providerRead('submissions',['id',c.submission_id],'status,published_at,published_skill_slugs'));
  appendFileSync(process.env.GITHUB_OUTPUT,`publication_sha=${plan.run.head_sha}\n`);
  console.log(JSON.stringify({failedRunId:plan.run.id,recoveryRunId:recovery.id,verifiedSlugs:plan.reports.map(r=>r.slug)}));
}
if(import.meta.url===pathToFileURL(process.argv[1]??'').href) {
  assert.equal(process.argv[2],'verify');
  await verifyBatchProviders(JSON.parse(readFileSync('batch-recovery-plan.json','utf8')));
}
