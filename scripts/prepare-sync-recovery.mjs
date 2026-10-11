import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const repo = 'aiskillstore/marketplace';
const sha = /^[a-f0-9]{40}$/;
const api = path => JSON.parse(execFileSync('gh', ['api', `repos/${repo}/${path}`], { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }));
const git = args => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }).trim();

export function recoveryPlan({ run, jobs, latestPush, files, reports, trees, approvals }) {
  assert.ok(Number.isSafeInteger(run.id) && run.id > 0 && sha.test(run.head_sha));
  assert.ok(run.event === 'push' && run.status === 'completed' && run.conclusion === 'failure'
    && run.path === '.github/workflows/sync-to-supabase.yml' && run.head_branch === 'main'
    && run.head_repository?.full_name === repo && latestPush.id === run.id, 'Not the latest failed main provider push');
  assert.ok(jobs.jobs?.length && jobs.total_count === jobs.jobs.length, 'Incomplete original jobs');
  const steps = jobs.jobs.flatMap(j => j.steps ?? []);
  for (const [name, conclusion] of [['Wait for authoritative publication completion', 'success'], ['Sync skills to Supabase', 'failure']]) {
    const matches = steps.filter(s => s.name === name);
    assert.ok(matches.length === 1 && matches[0].conclusion === conclusion, `Unverified original stage: ${name}`);
  }
  assert.ok(files.length > 0 && files.length <= 10000, 'Incomplete or oversized recovery range');
  const roots = [...new Set(files.map(f => {
    assert.ok(/^[AMD]$/.test(f.status) && /^skills\/[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*\/.+/.test(f.path)
      && !f.path.split('/').some(s => s === '.' || s === '..'), 'Unsafe recovery file');
    return f.path.split('/').slice(0, 3).join('/');
  }))].sort();
  assert.ok(roots.length <= 25 && reports.length === roots.length && trees.length === roots.length);
  assert.ok(approvals.length === 1, 'Recovery requires one approved publication');
  for (const pr of approvals) assert.ok(pr.merged === true && pr.base?.ref === 'main'
    && pr.base.repo?.full_name === repo && pr.head?.repo?.full_name === repo
    && pr.head.ref?.startsWith('submission/') && pr.user?.id === 254047988
    && pr.user.login === 'ai-skill-store[bot]' && sha.test(pr.head.sha) && sha.test(pr.merge_commit_sha), 'Untrusted recovery approval');
  const slugs = [];
  for (const root of roots) {
    const report = reports.filter(r => r.root === root);
    const tree = trees.filter(t => t.root === root);
    assert.ok(report.length === 1 && tree.length === 1);
    const { meta } = report[0], t = tree[0];
    assert.ok(sha.test(t.published) && t.published === t.current && t.published === t.approved, 'Recovery would overwrite a newer or unapproved tree');
    assert.ok(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(meta.slug)
      && /^[a-f0-9]{64}$/.test(meta.content_hash) && /^[a-f0-9]{64}$/.test(meta.tree_hash), 'Incomplete report identity');
    slugs.push(meta.slug);
  }
  assert.equal(new Set(slugs).size, roots.length, 'Duplicate recovery slugs');
  return { commit: run.head_sha, roots, slugs };
}

export function main() {
  const id = process.env.RESUME_FAILED_RUN;
  assert.ok(/^[1-9][0-9]*$/.test(id ?? '') && process.env.GITHUB_REF === 'refs/heads/main'
    && process.env.GITHUB_EVENT_NAME === 'workflow_dispatch' && process.env.GITHUB_REPOSITORY === repo);
  assert.ok(!process.env.INPUT_SLUGS && !process.env.CORRELATION_ID && !process.env.MERGE_COMMIT_SHA, 'Recovery cannot mix scope inputs');
  const run = api(`actions/runs/${id}`);
  assert.ok(sha.test(run.head_sha) && sha.test(process.env.GITHUB_SHA));
  const runs = api('actions/workflows/sync-to-supabase.yml/runs?per_page=100').workflow_runs
    .filter(r => r.event === 'push').sort((a,b) => b.created_at.localeCompare(a.created_at));
  const index = runs.findIndex(r => r.id === run.id);
  const baseline = runs[index + 1];
  assert.ok(index === 0 && baseline?.status === 'completed' && baseline.conclusion === 'success' && sha.test(baseline.head_sha), 'No complete preceding push baseline');
  git(['fetch', '--no-tags', 'origin', run.head_sha, baseline.head_sha]);
  const commit = api(`git/commits/${run.head_sha}`);
  const trailers = [...commit.message.matchAll(/^AgentCrew-Publication: submission-pr-([1-9][0-9]*)-([a-f0-9]{40})-([a-f0-9]{40})$/gm)];
  assert.ok(trailers.length === 1, 'Recovery requires one publication correlation');
  const approvals = trailers.map(([,number,head,merge]) => {
    const pr = api(`pulls/${number}`);
    assert.equal(pr.head.sha, head); assert.equal(pr.merge_commit_sha, merge);
    git(['fetch', '--no-tags', 'origin', head]);
    return pr;
  });
  const entries = git(['diff', '--name-status', '-z', '--no-renames', baseline.head_sha, run.head_sha, '--', 'skills/']).split('\0').filter(Boolean);
  assert.equal(entries.length % 2, 0);
  const files = [];
  for (let i=0; i<entries.length; i+=2) files.push({ status: entries[i], path: entries[i+1] });
  const roots = [...new Set(files.map(f => f.path.split('/').slice(0,3).join('/')))];
  const reports = [], trees = [];
  for (const root of roots) {
    assert.match(root, /^skills\/[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/);
    const published = git(['rev-parse', `${run.head_sha}:${root}`]);
    const current = git(['rev-parse', `${process.env.GITHUB_SHA}:${root}`]);
    const owners = approvals.filter(pr => {
      try { return git(['rev-parse', `${pr.head.sha}:${root.replace(/^skills\//, 'pending/')}`]) === published; }
      catch { return false; }
    });
    assert.equal(owners.length, 1, 'Recovery tree needs exactly one approval');
    trees.push({ root, published, current, approved: published });
    reports.push({ root, meta: JSON.parse(git(['show', `${run.head_sha}:${root}/skill-report.json`])).meta });
  }
  const plan = recoveryPlan({run, latestPush:runs[0], jobs:api(`actions/runs/${id}/attempts/${run.run_attempt}/jobs?per_page=100`), files, reports, trees, approvals});
  appendFileSync(process.env.GITHUB_OUTPUT, `sync_commit_sha=${plan.commit}\nrecovery_slugs=${plan.slugs.join(',')}\n`);
  console.log(JSON.stringify({ failedRunId:run.id, publicationSha:plan.commit, slugs:plan.slugs, mode:'resume-current' }));
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main();
