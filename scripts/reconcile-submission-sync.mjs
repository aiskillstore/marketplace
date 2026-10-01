import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const repo = 'aiskillstore/marketplace';
const prefix = `repos/${repo}`;
const sha40 = /^[a-f0-9]{40}$/;
const sha64 = /^[a-f0-9]{64}$/;
const syncPath = '.github/workflows/sync-to-supabase.yml';
function closedJobs(result) {
  assert.ok(result.jobs?.length > 0 && result.total_count === result.jobs.length, 'Incomplete jobs evidence');
  return result.jobs;
}
function step(jobs, name, conclusion) {
  const matches = jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
  assert.ok(matches.length === 1 && matches[0].conclusion === conclusion, `Missing closed step: ${name}`);
}
function trustedRun(run, event, conclusion) {
  assert.ok(Number.isSafeInteger(run.id) && run.id > 0 && Number.isSafeInteger(run.run_attempt) && run.run_attempt > 0);
  assert.ok(run.event === event && run.status === 'completed' && run.conclusion === conclusion
    && run.head_branch === 'main' && run.head_repository?.full_name === repo
    && run.path === syncPath && sha40.test(run.head_sha), 'Untrusted run');
}

// Bounded intentionally: one linear submission publication, <=25 canonical roots.
// Accumulated/multi-publication pushes need their own explicit inspected proof.
export function verifySubmissionRecovery(e) {
  trustedRun(e.push, 'push', 'failure');
  trustedRun(e.recovery, 'workflow_dispatch', 'success');
  assert.ok(e.recovery.head_sha === e.push.head_sha && e.recovery.id !== e.push.id
    && Date.parse(e.recovery.created_at) > Date.parse(e.push.created_at), 'Recovery version mismatch');
  assert.ok(e.baseline?.conclusion === 'success' && sha40.test(e.baseline.head_sha));
  const trailers = [...e.commit.message.matchAll(/^AgentCrew-Publication: (submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40}))$/gm)];
  assert.equal(trailers.length, 1, 'Requires one publication correlation');
  const [, , number, head, merge] = trailers[0];
  assert.ok(e.commit.parents?.length === 1 && e.commit.parents[0].sha === merge, 'Not a linear submission publication');
  const p = e.pr;
  assert.ok(p.number === Number(number) && p.merged === true && p.merge_commit_sha === merge
    && p.user?.id === 254047988 && p.user.login === 'ai-skill-store[bot]'
    && p.head?.sha === head && p.head.ref?.startsWith('submission/')
    && p.head.repo?.full_name === repo && p.base?.ref === 'main' && p.base.repo?.full_name === repo, 'Untrusted publication owner');
  const original = closedJobs(e.originalJobs), recovered = closedJobs(e.recoveryJobs);
  step(original, 'Wait for authoritative publication completion', 'success');
  step(original, 'Sync skills to Supabase', 'failure');
  for (const name of ['Sync skills to Supabase', 'Upload provider-complete synced slugs artifact',
    'Reconcile durable security change events', 'Notify skillstore - Published submissions']) step(recovered, name, 'success');
  for (const name of ['calculate-scores', 'cache-invalidate']) {
    const matches = recovered.filter(j => j.name === name);
    assert.ok(matches.length === 1 && matches[0].conclusion === 'success', `Incomplete ${name}`);
  }
  assert.ok(e.files.length > 0 && e.files.length < 300, 'Incomplete changed files');
  const roots = new Set();
  for (const f of e.files) {
    const match = f.filename.match(/^(skills\/[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*)\/(.+)$/);
    assert.ok(match && !match[0].split('/').some(s => s === '.' || s === '..')
      && ['added','modified'].includes(f.status) && !f.previous_filename, 'Unsafe publication range');
    roots.add(match[1]);
  }
  assert.ok(roots.size > 0 && roots.size <= 25 && e.reports.length === roots.size);
  const seen = new Set();
  const plan = e.reports.map(({root,meta}) => {
    assert.ok(roots.has(root) && !seen.has(root)); seen.add(root);
    assert.ok(/^[a-z0-9][a-z0-9._-]*$/.test(meta.slug) && sha64.test(meta.content_hash) && sha64.test(meta.tree_hash), 'Missing pinned identity');
    assert.ok(e.files.some(f => f.filename === `${root}/SKILL.md`) && e.files.some(f => f.filename === `${root}/skill-report.json`));
    return {root,slug:meta.slug,content_hash:meta.content_hash,tree_hash:meta.tree_hash,marketplace_commit_sha:e.push.head_sha};
  }).sort((a,b)=>a.slug.localeCompare(b.slug));
  assert.equal(new Set(plan.map(p=>p.slug)).size, plan.length, 'Duplicate slugs');
  assert.deepEqual([...e.slugs].sort(), plan.map(p=>p.slug).sort(), 'Recovery must cover exact changed slug set');
  return plan;
}

export function verifyProviderProjection(expected, skills, artifacts) {
  assert.equal(skills.length,1,'Missing/ambiguous provider skill');
  assert.equal(artifacts.length,1,'Missing/ambiguous current artifact');
  const s=skills[0], a=artifacts[0];
  assert.ok(s.id && s.current_artifact_version_id && Number.isSafeInteger(s.artifact_revision) && s.artifact_revision>0);
  assert.equal(s.slug,expected.slug); assert.equal(s.plugin_path,expected.root);
  assert.equal(a.id,s.current_artifact_version_id); assert.equal(a.skill_id,s.id);
  assert.equal(a.source_path,expected.root); assert.equal(a.artifact_revision,s.artifact_revision);
  assert.equal(a.snapshot_status,'exact');
  for(const field of ['marketplace_commit_sha','content_hash','tree_hash']) {
    assert.equal(s[field],expected[field],`Provider projection ${field}`);
    assert.equal(a[field],expected[field],`Current artifact ${field}`);
  }
}
function rawApi(endpoint) {
  return execFileSync('gh',['api',endpoint],{maxBuffer:2*1024*1024,timeout:30000});
}
const api = endpoint => JSON.parse(rawApi(endpoint));
function artifactSlugs(runId) {
  const result=api(`${prefix}/actions/runs/${runId}/artifacts?per_page=100`);
  assert.ok(result.total_count === result.artifacts.length && result.total_count < 100);
  const matches=result.artifacts.filter(a=>a.name==='synced-slugs');
  assert.equal(matches.length,1,'One exact provider artifact required');
  const a=matches[0];
  assert.ok(!a.expired && a.size_in_bytes>0 && a.size_in_bytes<=65536 && /^sha256:[a-f0-9]{64}$/.test(a.digest), 'Invalid artifact metadata');
  const zip=rawApi(`${prefix}/actions/artifacts/${a.id}/zip`);
  return verifiedArtifactSlugs(zip,a);
}
export function verifiedArtifactSlugs(zip,a) {
  assert.ok(!a.expired && a.size_in_bytes===zip.length && zip.length>0 && zip.length<=65536);
  assert.equal(`sha256:${createHash('sha256').update(zip).digest('hex')}`,a.digest,'Artifact digest mismatch');
  // stdlib, no filesystem extraction and no archive paths used as commands.
  const text=execFileSync('python3',['-c',`import sys,io,zipfile,stat\nz=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))\ni=z.infolist()\nassert len(i)==1 and i[0].filename=='synced-slugs.txt' and i[0].file_size<=8192\nassert not stat.S_ISLNK(i[0].external_attr >> 16)\nsys.stdout.buffer.write(z.read(i[0]))`],{input:zip,maxBuffer:8192,timeout:10000}).toString('utf8');
  return text.trim().split('\n').map(s=>s.trim());
}
async function providerRead(table, filter, select) {
  const base=new URL(process.env.SUPABASE_URL);
  assert.ok(base.protocol==='https:' && !base.username && !base.password);
  const url=new URL(`/rest/v1/${table}`,base);
  url.searchParams.set('select',select); url.searchParams.set(filter[0],`eq.${filter[1]}`); url.searchParams.set('limit','2');
  const key=process.env.SUPABASE_SERVICE_KEY;
  assert.ok(key,'Missing runtime provider handle');
  const response=await fetch(url,{method:'GET',redirect:'error',signal:AbortSignal.timeout(15000),headers:{apikey:key,Authorization:`Bearer ${key}`,'Accept-Profile':'skillstore'}});
  assert.ok(response.ok,`Provider read failed: HTTP ${response.status}`);
  const text=await response.text(); assert.ok(text.length<=16384,'Oversized provider evidence');
  return JSON.parse(text);
}
export async function main() {
  assert.equal(process.env.GITHUB_EVENT_NAME,'workflow_dispatch');
  assert.equal(process.env.GITHUB_REF,'refs/heads/main');
  assert.equal(process.env.GITHUB_REPOSITORY,repo);
  const ids=[process.env.FAILED_RUN_ID,process.env.RECOVERY_RUN_ID];
  assert.ok(ids.every(id=>/^[1-9][0-9]*$/.test(id)) && ids[0]!==ids[1]);
  const [push,recovery]=ids.map(id=>api(`${prefix}/actions/runs/${id}`));
  const inventory=api(`${prefix}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`).workflow_runs;
  // Exact historical run is outside bounded inventory -> visible failure, not guessed coverage.
  assert.ok(inventory.some(r=>r.id===push.id),'Failed push outside bounded inventory');
  const baseline=inventory.filter(r=>r.event==='push' && r.status==='completed' && r.created_at<push.created_at)
    .sort((a,b)=>b.created_at.localeCompare(a.created_at))[0];
  trustedRun(baseline,'push','success');
  const commit=api(`${prefix}/git/commits/${push.head_sha}`);
  const comparison=api(`${prefix}/compare/${baseline.head_sha}...${push.head_sha}`);
  assert.equal(comparison.status,'ahead'); assert.ok(comparison.files.length<300,'Truncated comparison');
  const trailer=commit.message.match(/^AgentCrew-Publication: submission-pr-([1-9][0-9]*)-[a-f0-9]{40}-[a-f0-9]{40}$/m);
  assert.ok(trailer,'No exact submission publication');
  const pr=api(`${prefix}/pulls/${trailer[1]}`);
  const roots=[...new Set(comparison.files.map(f=>f.filename.split('/').slice(0,3).join('/')))];
  assert.ok(roots.length>0 && roots.length<=25);
  const reports=roots.map(root=> {
    assert.ok(/^skills\/[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/.test(root));
    const pinned=api(`${prefix}/contents/${root}?ref=${push.head_sha}`);
    const pending=api(`${prefix}/contents/${root.replace(/^skills\//,'pending/')}?ref=${pr.head.sha}`);
    const entries=list=> {
      assert.ok(Array.isArray(list) && list.length>0 && list.length<1000 && list.every(f=>['file','dir'].includes(f.type)));
      assert.ok(['SKILL.md','skill-report.json'].every(n=>list.some(f=>f.name===n && f.type==='file')));
      return list.map(f=>({name:f.name,type:f.type,sha:f.sha})).sort((a,b)=>a.name.localeCompare(b.name));
    };
    assert.deepEqual(entries(pinned),entries(pending),'Publication differs from trusted pending tree');
    const report=api(`${prefix}/contents/${root}/skill-report.json?ref=${push.head_sha}`);
    assert.equal(report.encoding,'base64'); assert.ok(report.size<=1024*1024);
    const {meta}=JSON.parse(Buffer.from(report.content,'base64').toString('utf8'));
    return {root,meta:{slug:meta.slug,content_hash:meta.content_hash,tree_hash:meta.tree_hash}};
  });
  const jobs=run=>api(`${prefix}/actions/runs/${run.id}/attempts/${run.run_attempt}/jobs?per_page=100`);
  const plan=verifySubmissionRecovery({push,recovery,baseline,commit,pr,files:comparison.files,reports,slugs:artifactSlugs(recovery.id),originalJobs:jobs(push),recoveryJobs:jobs(recovery)});
  for(const expected of plan) {
    const skills=await providerRead('skills',['slug',expected.slug],'id,slug,plugin_path,marketplace_commit_sha,content_hash,tree_hash,current_artifact_version_id,artifact_revision');
    assert.equal(skills.length,1);
    const artifacts=await providerRead('skill_artifact_versions',['id',skills[0].current_artifact_version_id],'id,skill_id,source_path,marketplace_commit_sha,content_hash,tree_hash,artifact_revision,snapshot_status');
    verifyProviderProjection(expected,skills,artifacts);
  }
  // Output only safe control identifiers, never provider response or credentials.
  console.log(JSON.stringify({failedRunId:push.id,recoveryRunId:recovery.id,publicationSha:push.head_sha,verifiedSlugs:plan.map(p=>p.slug)}));
  const {appendFileSync}=await import('node:fs');
  appendFileSync(process.env.GITHUB_OUTPUT,`publication_sha=${push.head_sha}\n`);
}
if(import.meta.url===pathToFileURL(process.argv[1]??'').href) main().catch(()=>{console.error('Exact submission reconciliation rejected; no provider writes or status closure performed.');process.exitCode=1;});
