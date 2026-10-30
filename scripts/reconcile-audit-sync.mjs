import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { verifyMergedAuditPullRequest, rawLogArgs } from './audit-publication-admission.mjs';
import { artifactSlugs, providerRead, verifyProviderProjection, verifyRootIdentity } from './reconcile-submission-sync.mjs';

const repo = 'aiskillstore/marketplace', prefix = `repos/${repo}`;
const SHA = /^[a-f0-9]{40}$/, HASH = /^[a-f0-9]{64}$/;
function trustedRun(r, event, conclusion) {
  assert(r?.event === event && r.status === 'completed' && r.conclusion === conclusion
    && r.path === '.github/workflows/sync-to-supabase.yml' && r.head_branch === 'main'
    && r.head_repository?.full_name === repo && SHA.test(r.head_sha)
    && Number.isSafeInteger(r.id) && r.id > 0 && r.run_attempt === 1, 'Untrusted or repeated sync run');
}
function jobs(result) {
  assert(result?.jobs?.length > 0 && result.total_count === result.jobs.length, 'Incomplete jobs');
  return result.jobs;
}
function step(list, name, conclusion) {
  const found = list.flatMap(j => j.steps ?? []).filter(s => s.name === name);
  assert(found.length === 1 && found[0].conclusion === conclusion, `Incomplete step: ${name}`);
}

// This verifies a NEW completed repair, never reclassifies the old write as successful.
// Only an audited push that stopped BEFORE the provider is eligible; the manual
// result must cover the whole canonical range, so adopting its SHA cannot replay it.
export function verifyAuditRecovery(e) {
  trustedRun(e.push, 'push', 'failure'); trustedRun(e.baseline, 'push', 'success');
  trustedRun(e.recovery, 'workflow_dispatch', 'success');
  assert(e.recovery.head_sha === e.push.head_sha && e.recovery.id !== e.push.id
    && Date.parse(e.baseline.created_at) < Date.parse(e.push.created_at)
    && Date.parse(e.push.created_at) < Date.parse(e.recovery.created_at), 'Wrong recovery version/order');
  assert(e.pr.merged === true && e.pr.state === 'closed' && e.pr.merge_commit_sha === e.push.head_sha
    && e.provenance.head === e.pr.head.sha, 'Not the verified audit merge');
  assert(e.merge.parents?.length === 2 && e.merge.parents[1].sha === e.pr.head.sha, 'Audit merge parent mismatch');
  const roots = e.provenance.paths.map(p => p.replace(/\/skill-report\.json$/, '')).sort();
  assert(roots.length > 0 && roots.length <= 25 && new Set(roots).size === roots.length);
  assert(roots.every(r => /^skills\/[a-z0-9][a-z0-9._-]*(?:\/[a-z0-9][a-z0-9._-]*)?$/.test(r)
    && !r.split('/').some(p => p === '.' || p === '..')), 'Noncanonical root');
  assert(e.files.length > 0 && e.files.length < 300, 'Incomplete canonical range');
  for (const f of e.files) {
    assert(f.status === 'modified' && !f.previous_filename, 'Only existing non-renamed source allowed');
    assert(!f.filename.includes('\\') && !f.filename.split('/').some(p => !p || p === '.' || p === '..'), 'Unsafe source path');
    assert(roots.filter(r => f.filename.startsWith(`${r}/`)).length === 1, 'Uncovered canonical change');
  }
  const original = jobs(e.originalJobs), recovered = jobs(e.recoveryJobs);
  step(original, 'Wait for authoritative publication completion', 'success');
  step(original, 'Find last successful sync commit', 'failure');
  for (const name of ['Download skillstore-cli','Sync skills to Supabase',
    'Reconcile durable security change events','Notify skillstore - Published submissions']) step(original,name,'skipped');
  for (const name of ['Sync skills to Supabase','Upload provider-complete synced slugs artifact',
    'Save synced slugs to artifact','Reconcile durable security change events','Resolve published submissions']) step(recovered,name,'success');
  // This route does not settle a submission callback or impersonate its correlation.
  step(recovered, 'Notify skillstore - Published submissions', 'skipped');
  for (const name of ['calculate-scores','cache-invalidate']) {
    const found=recovered.filter(j=>j.name===name);
    assert(found.length===1 && found[0].conclusion==='success',`Incomplete ${name}`);
  }
  assert(e.reports.length === roots.length && new Set(e.reports.map(r=>r.root)).size === roots.length);
  const plan = e.reports.map(({root,meta,approvedTree,publishedTree}) => {
    assert(roots.includes(root) && SHA.test(approvedTree) && approvedTree===publishedTree, 'Audit source tree changed');
    assert(/^[a-z0-9][a-z0-9._-]*$/.test(meta.slug) && HASH.test(meta.content_hash) && HASH.test(meta.tree_hash));
    verifyRootIdentity(root,meta);
    return {root,slug:meta.slug,content_hash:meta.content_hash,tree_hash:meta.tree_hash,marketplace_commit_sha:e.recovery.head_sha};
  }).sort((a,b)=>a.slug.localeCompare(b.slug));
  assert.equal(new Set(plan.map(p=>p.slug)).size,plan.length);
  assert.deepEqual([...e.slugs].sort(),plan.map(p=>p.slug).sort(),'Recovery scope mismatch');
  return plan;
}
function api(endpoint, raw=false) {
  const out=execFileSync('gh',raw ? rawLogArgs(endpoint) : ['api','--method','GET',endpoint],
    {encoding:'utf8',timeout:30000,maxBuffer:16*1024*1024});
  return raw ? out : JSON.parse(out);
}
const runJobs = (run, api) => api(`${prefix}/actions/runs/${run.id}/attempts/${run.run_attempt}/jobs?per_page=100`);
function comparison(from,to,api) {
  const c=api(`${prefix}/compare/${from}...${to}`);
  assert(c.status==='ahead' && c.total_commits>0 && c.total_commits<=100
    && c.commits?.length===c.total_commits && c.files?.length<300,'Incomplete repair comparison');
  // Publication callbacks have their own original-tree reconciliation contract.
  assert(c.commits.every(c=>!/^AgentCrew-Publication:/m.test(c.commit.message)), 'Publication range not eligible');
  return c.files.filter(f=>f.filename.startsWith('skills/'));
}
function rootTree(commit,root,api) {
  let tree=api(`${prefix}/git/commits/${commit}`).tree.sha;
  for(const segment of root.split('/')) {
    const result=api(`${prefix}/git/trees/${tree}`);
    assert(result.truncated===false && Array.isArray(result.tree),'Incomplete Git tree');
    const matches=result.tree.filter(e=>e.path===segment && e.type==='tree' && e.mode==='040000');
    assert(matches.length===1 && SHA.test(matches[0].sha),'Missing canonical tree'); tree=matches[0].sha;
  }
  return tree;
}
export async function collectAuditRecovery({failedRunId,recoveryRunId,auditPr}, apiRequest=api, readSlugs=artifactSlugs) {
  const api=apiRequest;
  const ids=[failedRunId,recoveryRunId,auditPr].map(String);
  assert(ids.every(id=>/^[1-9][0-9]*$/.test(id)) && ids[0]!==ids[1]);
  const [push,recovery]=ids.slice(0,2).map(id=>api(`${prefix}/actions/runs/${id}`));
  trustedRun(push,'push','failure'); trustedRun(recovery,'workflow_dispatch','success');
  const inventory=api(`${prefix}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`).workflow_runs;
  assert(Array.isArray(inventory) && inventory.some(r=>r.id===push.id),'Push outside bounded inventory');
  const pushes=inventory.filter(r=>r.event==='push' && r.created_at<=push.created_at).sort((a,b)=>b.created_at.localeCompare(a.created_at));
  const baseline=pushes.find(r=>r.created_at<push.created_at && r.status==='completed' && r.conclusion==='success');
  trustedRun(baseline,'push','success');
  const pending=pushes.filter(r=>r.created_at>baseline.created_at);
  assert(pending.length>0 && pending.length<=25 && pending.every(r=>r.status==='completed' && r.conclusion==='failure'), 'Unsettled push range');
  const pr=api(`${prefix}/pulls/${ids[2]}`);
  const provenance=await verifyMergedAuditPullRequest({repository:repo,number:Number(ids[2]),expectedHead:pr.head.sha},api);
  const files=new Map();
  // Check EACH failed push against the prior successful baseline as well as the
  // repaired tip. A later revert cannot hide an earlier affected canonical root.
  for(const r of pending) {
    trustedRun(r,'push','failure');
    for(const f of comparison(baseline.head_sha,r.head_sha,api)) {
      assert(f.status==='modified' && !f.previous_filename,'Unsafe historical canonical change');
      files.set(f.filename,f);
    }
  }
  const reports=provenance.paths.map(path=> {
    const root=path.replace(/\/skill-report\.json$/,'');
    const report=api(`${prefix}/contents/${path}?ref=${push.head_sha}`);
    assert(report.encoding==='base64' && report.size>0 && report.size<=1024*1024);
    const {meta}=JSON.parse(Buffer.from(report.content,'base64').toString('utf8'));
    return {root,meta:{slug:meta.slug,source_type:meta.source_type,source_ref:meta.source_ref,source_url:meta.source_url,content_hash:meta.content_hash,tree_hash:meta.tree_hash},
      approvedTree:rootTree(pr.head.sha,root,api),publishedTree:rootTree(push.head_sha,root,api)};
  });
  const plan=verifyAuditRecovery({push,recovery,baseline,pr,provenance,reports,files:[...files.values()],
    merge:api(`${prefix}/git/commits/${push.head_sha}`),slugs:readSlugs(recovery.id),originalJobs:runJobs(push,api),recoveryJobs:runJobs(recovery,api)});
  return {push,recovery,pr,plan};
}
export async function mainAuditRecovery() {
  assert.equal(process.env.GITHUB_EVENT_NAME,'workflow_dispatch');
  assert.equal(process.env.GITHUB_REF,'refs/heads/main'); assert.equal(process.env.GITHUB_REPOSITORY,repo);
  const {push,recovery,pr,plan}=await collectAuditRecovery({failedRunId:process.env.FAILED_RUN_ID,
    recoveryRunId:process.env.RECOVERY_RUN_ID,auditPr:process.env.AUDIT_PR});
  for(const expected of plan) {
    const skills=await providerRead('skills',['slug',expected.slug],'id,slug,plugin_path,marketplace_commit_sha,content_hash,tree_hash,current_artifact_version_id,artifact_revision');
    assert.equal(skills.length,1);
    const artifacts=await providerRead('skill_artifact_versions',['id',skills[0].current_artifact_version_id],'id,skill_id,source_path,marketplace_commit_sha,content_hash,tree_hash,artifact_revision,snapshot_status');
    verifyProviderProjection(expected,skills,artifacts);
  }
  console.log(JSON.stringify({failedRunId:push.id,recoveryRunId:recovery.id,auditPr:pr.number,verifiedSlugs:plan.map(p=>p.slug)}));
  appendFileSync(process.env.GITHUB_OUTPUT,`publication_sha=${push.head_sha}\n`);
}
