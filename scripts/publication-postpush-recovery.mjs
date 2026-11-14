import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { latestStatus } from './recovered-push-sync.mjs';
const repo='aiskillstore/marketplace', prefix=`repos/${repo}`, sha=/^[a-f0-9]{40}$/;
function steps(jobs){
  assert.ok(jobs.total_count === jobs.jobs?.length && jobs.jobs.length > 0, 'Incomplete jobs');
  return jobs.jobs.flatMap(j=>j.steps ?? []);
}
function stage(jobs,name,conclusion){const matches=steps(jobs).filter(s=>s.name===name);assert.ok(matches.length===1 && matches[0].conclusion===conclusion,`Unverified stage: ${name}`);}
function failedPush(run){return Number.isSafeInteger(run?.id) && run.id>0 && run.run_attempt===1 && run.event==='push' && run.status==='completed' && run.conclusion==='failure' && run.path==='.github/workflows/sync-to-supabase.yml' && run.head_branch==='main' && run.head_repository?.full_name===repo && sha.test(run.head_sha);}
export function publicationRecoveryPlan(e){
  const {run,jobs,publisher,publisherJobs,commit,pr,trees,receiver,submissionId}=e;
  assert.ok(failedPush(run),'Not a first-attempt failed publication push');
  stage(jobs,'Wait for authoritative publication completion','failure');
  stage(jobs,'Sync skills to Supabase','skipped');
  stage(jobs,'Notify skillstore - Published submissions','skipped');
  assert.ok(pr.merged===true && pr.user?.id===254047988 && pr.user.login==='ai-skill-store[bot]' && pr.head?.ref?.startsWith('submission/') && pr.head.repo?.full_name===repo && pr.base?.ref==='main' && pr.base.repo?.full_name===repo && sha.test(pr.head.sha) && sha.test(pr.merge_commit_sha),'Untrusted approval');
  const correlation=`submission-pr-${pr.number}-${pr.head.sha}-${pr.merge_commit_sha}`;
  const trailers=[...commit.message.matchAll(/^AgentCrew-Publication: (.+)$/gm)].map(m=>m[1]);
  assert.deepEqual(trailers,[correlation],'Requires one exact publication');
  assert.equal(commit.sha,run.head_sha);assert.equal(commit.parents?.length,1);
  assert.ok(publisher.id>0 && publisher.run_attempt===1 && publisher.event==='workflow_dispatch' && publisher.status==='completed' && publisher.conclusion==='failure' && publisher.head_branch==='main' && publisher.head_repository?.full_name===repo && publisher.path==='.github/workflows/publish-approved-batch.yml' && publisher.display_title===`Publication batch ${createHash('sha256').update(correlation).digest('hex')}`,'Untrusted failed publisher');
  stage(publisherJobs,'Verify every approval and publish one atomic batch','failure');
  assert.ok(trees.length>0 && trees.length<=25);
  assert.equal(new Set(trees.map(t=>t.root)).size,trees.length);
  for(const t of trees) assert.ok(/^skills\/[a-z0-9][a-z0-9._-]*(?:\/[a-z0-9][a-z0-9._-]*)?$/.test(t.root) && sha.test(t.approved) && t.approved===t.published && t.published===t.current,'Changed or unapproved package tree');
  assert.match(submissionId,/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/);
  assert.equal(receiver.pr_number,pr.number,'Receiver PR mismatch');
  assert.equal(receiver.published_at,null,'Already published');
  assert.ok(receiver.published_skill_slugs==null || (Array.isArray(receiver.published_skill_slugs) && receiver.published_skill_slugs.length===0));
  assert.ok(receiver.status==='in_review' || receiver.status==='approved','Unknown receiver state');
  if(receiver.status==='in_review') assert.equal(receiver.approved_at,null,'Ambiguous merged state');
  else {assert.equal(Number(receiver.workflow_run_id),publisher.id,'Another callback owns receiver');assert.ok(Number.isFinite(Date.parse(receiver.approved_at)),'Missing approval timestamp');}
  return {sendMerged:receiver.status==='in_review',publicationSha:run.head_sha,publisherId:publisher.id,submissionId,prNumber:pr.number};
}

// A new proof is consumed separately. Never rewrite the failed publisher/push or
// its old publication/attempt statuses, and never trust a green manual sync alone.
export function verifiedPublicationRecovery(push,request){
  if(!failedPush(push)) return null;
  const status=latestStatus(push.head_sha,`agentcrew/publication-reconciliation/${push.id}`,request);
  if(status?.state!=='success' || status.creator?.id!==41898282 || status.creator.login!=='github-actions[bot]') return null;
  const match=status.target_url?.match(/^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/([1-9][0-9]*)$/);
  if(!match)return null;
  const proof=request(`${prefix}/actions/runs/${match[1]}`);
  if(String(proof.id)!==match[1] || proof.event!=='workflow_dispatch' || proof.status!=='completed' || proof.conclusion!=='success' || proof.path!=='.github/workflows/reconcile-submission-sync.yml' || proof.head_branch!=='main' || proof.head_repository?.full_name!==repo || !Number.isSafeInteger(proof.run_attempt) || proof.run_attempt<1 || !(Date.parse(proof.created_at)>Date.parse(push.created_at)) || !new RegExp(`^Reconcile publication push ${push.id} using publisher [1-9][0-9]*$`).test(proof.display_title ?? ''))return null;
  const jobs=request(`${prefix}/actions/runs/${proof.id}/attempts/${proof.run_attempt}/jobs?per_page=100`);
  stage(jobs,'Verify exact recovery and provider state','success');stage(jobs,'Record separate reconciliation result','success');
  return proof;
}
const api=path=>JSON.parse(execFileSync('gh',['api',`${prefix}/${path}`],{encoding:'utf8',maxBuffer:16*1024*1024}));
const git=args=>execFileSync('git',args,{encoding:'utf8',maxBuffer:16*1024*1024}).trim();
export async function inspectPublication({receiverRead}={}){
  const {providerRead,submissionIdentity,publicationRoots}=await import('./reconcile-submission-sync.mjs');
  const id=process.env.FAILED_RUN_ID,publisherId=process.env.PUBLICATION_RUN_ID;
  assert.ok(/^[1-9][0-9]*$/.test(id ?? '') && /^[1-9][0-9]*$/.test(publisherId ?? '') && process.env.GITHUB_REF==='refs/heads/main' && process.env.GITHUB_EVENT_NAME==='workflow_dispatch' && process.env.GITHUB_REPOSITORY===repo);
  assert.ok(!process.env.RECOVERY_RUN_ID && !process.env.RECOVERY_RUN_IDS && !process.env.SCORE_RECOVERY_RUN_ID && !process.env.AUDIT_PR,'Cannot mix recovery modes');
  const run=api(`actions/runs/${id}`),publisher=api(`actions/runs/${publisherId}`);
  assert.ok(failedPush(run),'Unsupported original run');
  const runs=api('actions/workflows/sync-to-supabase.yml/runs?per_page=100').workflow_runs.filter(r=>r.event==='push').sort((a,b)=>b.created_at.localeCompare(a.created_at));
  assert.equal(runs[0]?.id,run.id,'Not latest failed push');
  const commit=api(`git/commits/${run.head_sha}`);
  const match=commit.message.match(/^AgentCrew-Publication: submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40})$/m);
  assert.ok(match,'Missing publication correlation');const pr=api(`pulls/${match[1]}`);
  const digest=createHash('sha256').update(match[0].slice('AgentCrew-Publication: '.length)).digest('hex');
  const owner=latestStatus(pr.merge_commit_sha,`agentcrew/publication/${digest}`,path=>api(path.slice(prefix.length+1)));
  assert.ok(owner?.state==='failure' && owner.target_url===`https://github.com/${repo}/actions/runs/${publisher.id}`,'Publisher does not own failed reservation');
  assert.equal(pr.head.sha,match[2]);assert.equal(pr.merge_commit_sha,match[3]);
  assert.ok(commit.parents?.length===1 && sha.test(process.env.GITHUB_SHA));
  assert.equal(runs[1]?.head_sha,commit.parents[0].sha,'Publication must immediately follow preceding complete provider push');
  assert.equal(runs[1]?.conclusion,'success');
  git(['fetch','--no-tags','origin',run.head_sha,pr.head.sha,commit.parents[0].sha]);
  git(['merge-base','--is-ancestor',run.head_sha,process.env.GITHUB_SHA]);
  const entries=git(['diff','--name-status','--no-renames','-z',commit.parents[0].sha,run.head_sha]).split('\0').filter(Boolean);
  assert.equal(entries.length%2,0);const files=[];for(let i=0;i<entries.length;i+=2)files.push({status:entries[i],path:entries[i+1]});
  const roots=publicationRoots(files.filter(f=>f.path.startsWith('skills/'))),trees=[];
  assert.ok(files.length>0 && files.length<=10000);
  for(const f of files) assert.ok(roots.some(root=>(f.status==='A' && f.path.startsWith(`${root}/`)) || (f.status==='D' && f.path.startsWith(`${root.replace(/^skills\//,'pending/')}/`))),'Not a pure pending-to-published move');
  for(const root of roots){
    const pending=root.replace(/^skills\//,'pending/');
    const approved=git(['rev-parse',`${pr.head.sha}:${pending}`]);
    const published=git(['rev-parse',`${run.head_sha}:${root}`]);
    const current=git(['rev-parse',`${process.env.GITHUB_SHA}:${root}`]);
    assert.equal(git(['rev-parse',`${commit.parents[0].sha}:${pending}`]),approved,'Pending tree changed before publication');
    const pendingFiles=git(['ls-tree','-r','--name-only',pr.head.sha,'--',pending]).split('\n');
    assert.ok(pendingFiles.includes(`${pending}/SKILL.md`) && pendingFiles.includes(`${pending}/skill-report.json`));
    assert.equal(files.filter(f=>f.status==='D' && f.path.startsWith(`${pending}/`)).length,pendingFiles.length,'Incomplete pending deletion');
    trees.push({root,approved,published,current});
  }
  const submissionId=submissionIdentity(pr,commit.message);
  const readReceiver=async()=>{const rows=receiverRead ? await receiverRead(submissionId) : await providerRead('submissions',['id',submissionId],'status,pr_number,workflow_run_id,approved_at,published_at,published_skill_slugs');assert.equal(rows.length,1,'Missing receiver');return rows[0];};
  const evidence={run,jobs:api(`actions/runs/${id}/attempts/1/jobs?per_page=100`),publisher,publisherJobs:api(`actions/runs/${publisherId}/attempts/1/jobs?per_page=100`),commit,pr,trees,receiver:await readReceiver(),submissionId};
  return {plan:publicationRecoveryPlan(evidence),evidence,readReceiver,correlation:match[0].slice('AgentCrew-Publication: '.length)};
}
export async function main({inspect=inspectPublication,post=fetch}={}){
  const {plan,evidence,readReceiver,correlation}=await inspect();
  const {run,publisher,pr,submissionId}=evidence;
  if(plan.sendMerged){
    const endpoint=new URL(process.env.SKILLSTORE_API_URL);assert.equal(endpoint.protocol,'https:');assert.ok(process.env.SKILLSTORE_CALLBACK_TOKEN,'Missing callback credential');
    const response=await post(new URL('/api/submit/callback',endpoint),{method:'POST',redirect:'error',headers:{Authorization:`Bearer ${process.env.SKILLSTORE_CALLBACK_TOKEN}`,'Content-Type':'application/json','X-Skillstore-Callback':'true','User-Agent':'GitHub-Actions/SkillstoreBot','Idempotency-Key':`publication-resolved-${correlation}`},body:JSON.stringify({submission_id:submissionId,event:'merged',pr_number:pr.number,pr_url:pr.html_url,merged_by:pr.merged_by.login,workflow_run_id:publisher.id,workflow_run_url:`https://github.com/${repo}/actions/runs/${publisher.id}`}),signal:AbortSignal.timeout(30000)});
    assert.ok(response.ok,`Merged callback HTTP ${response.status}; inspect receiver before retry`);
  }
  const final=publicationRecoveryPlan({...evidence,receiver:await readReceiver()});assert.equal(final.sendMerged,false,'Merged callback not committed');
  appendFileSync(process.env.GITHUB_OUTPUT,`publication_sha=${run.head_sha}\n`);
  console.log(JSON.stringify({failedPush:run.id,publisher:publisher.id,publicationSha:run.head_sha,prNumber:pr.number,callback:plan.sendMerged?'completed-missing':'already-committed',providerExecuted:false}));
}
if(import.meta.url===pathToFileURL(process.argv[1] ?? '').href)main().catch(error=>{console.error(error.message);process.exitCode=1;});
