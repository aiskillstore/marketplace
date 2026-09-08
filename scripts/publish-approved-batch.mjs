import { execFileSync } from 'node:child_process';
import { existsSync, lstatSync, mkdirSync, renameSync, rmSync } from 'node:fs';
import { dirname } from 'node:path';
import { pathToFileURL } from 'node:url';
import { publicationIdentity, chooseAttempt, batchIdentity } from './continue-merged-publications.mjs';
import { resolveApprovedSubmission } from './resolve-approved-submission.mjs';

export { batchIdentity } from './continue-merged-publications.mjs';

const repository = 'aiskillstore/marketplace';
export function validateBatchPlans(rows) {
  const roots = new Set();
  for (const { plan } of rows) for (const skill of plan.skills) {
    if ([...roots].some(root => root === skill.targetDir || root.startsWith(`${skill.targetDir}/`) || skill.targetDir.startsWith(`${root}/`))) throw new Error(`Overlapping batch target: ${skill.targetDir}`);
    if (skill.duplicate) throw new Error('Duplicate-only cleanup must be reconciled separately');
    roots.add(skill.targetDir);
  }
  if (roots.size < 1 || roots.size > 25) throw new Error('Batch must contain 1..25 distinct skills');
  return roots;
}
function git(args, input) {
  return execFileSync('git', args, { encoding: 'utf8', input, maxBuffer: 32 * 1024 * 1024, env: { ...process.env, GIT_TERMINAL_PROMPT: '0' } }).trim();
}
function api(path, data) {
  const args = ['api', `repos/${repository}/${path}`];
  if (data) args.push('--method', 'POST', '--input', '-');
  const result = execFileSync('gh', args, { encoding: 'utf8', input: data ? JSON.stringify(data) : undefined, maxBuffer: 32 * 1024 * 1024 });
  return result.trim() ? JSON.parse(result) : null;
}
function all(path) {
  return JSON.parse(execFileSync('gh', ['api', '--paginate', '--slurp', `repos/${repository}/${path}`], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 })).flat();
}
function assertDirectoryAncestors(path) {
  const pieces = path.split('/');
  for (let i = 1; i <= pieces.length; i++) {
    const partial = pieces.slice(0, i).join('/');
    if (existsSync(partial)) {
      const stat = lstatSync(partial);
      if (stat.isSymbolicLink() || !stat.isDirectory()) throw new Error(`Unsafe publication ancestor: ${partial}`);
    }
    const entry = git(['ls-tree', 'HEAD', '--', partial]);
    if (entry && !/^040000 tree /.test(entry)) throw new Error(`Unsafe Git publication ancestor: ${partial}`);
  }
}
async function callback(row) {
  if (!row.submissionId) return;
  const payload = { submission_id: row.submissionId, event: 'merged', pr_number: row.pr.number,
    pr_url: row.pr.html_url, merged_by: row.pr.merged_by.login,
    workflow_run_id: Number(process.env.GITHUB_RUN_ID), workflow_run_url: row.owner };
  for (let attempt = 0; attempt < 3; attempt++) {
    const response = await fetch(`${process.env.SKILLSTORE_API_URL}/api/submit/callback`, {
      method: 'POST', headers: { Authorization: `Bearer ${process.env.SKILLSTORE_CALLBACK_TOKEN}`,
        'Content-Type': 'application/json', 'X-Skillstore-Callback': 'true', 'User-Agent': 'GitHub-Actions/SkillstoreBot',
        'Idempotency-Key': `publication-resolved-${row.correlation}` }, body: JSON.stringify(payload), signal: AbortSignal.timeout(30000),
    });
    if (response.ok) return;
    if (attempt === 2) throw new Error(`Merged callback failed for #${row.pr.number}: HTTP ${response.status}`);
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
export async function main() {
  const numbers = String(process.env.PR_NUMBERS || '').split(',').map(x => x.trim());
  if (!numbers.length || numbers.length > 25 || new Set(numbers).size !== numbers.length || numbers.some(n => !/^[1-9]\d*$/.test(n))) throw new Error('Expected 1..25 unique PR numbers');
  if (process.env.GITHUB_REF !== 'refs/heads/main' || process.env.GITHUB_REPOSITORY !== repository) throw new Error('Batch publication requires trusted main');
  if (!process.env.SKILLSTORE_API_URL || !process.env.SKILLSTORE_CALLBACK_TOKEN) throw new Error('Missing callback configuration');
  const rows = numbers.map(number => {
    const pr = api(`pulls/${number}`);
    const identity = publicationIdentity(pr);
    const files = all(`pulls/${number}/files?per_page=100`).map(f => f.filename);
    const roots = [...new Set(files.filter(f => /\/(SKILL\.md|skill-report\.json)$/.test(f)).map(f => f.slice(0, f.lastIndexOf('/'))))];
    if (!roots.length || roots.some(r => !/^pending\/[a-zA-Z0-9._-]+(?:\/[a-zA-Z0-9._-]+)?$/.test(r) || r.split('/').some(s => s === '.' || s === '..'))) throw new Error('Invalid batch pending roots');
    return { pr, ...identity, files, roots, submissionId: pr.body?.match(/Submission ID.*`([0-9a-f-]{36})`/)?.[1],
      owner: `https://github.com/${repository}/actions/runs/${process.env.GITHUB_RUN_ID}` };
  });
  if (batchIdentity(rows.map(r => r.correlation)) !== process.env.BATCH_ID) throw new Error('Batch identity does not bind exact merged PRs');
  const syncs = api('actions/workflows/sync-to-supabase.yml/runs?per_page=100').workflow_runs;
  if (syncs.some(r => r.status !== 'completed')) throw new Error('Previous provider sync remains active');
  const last = syncs.filter(r => r.event === 'push').sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
  if (!last || last.conclusion !== 'success') throw new Error('Previous push sync is not fully successful');
  git(['config', 'credential.helper', '!gh auth git-credential']);
  git(['fetch', '--depth=1', 'origin', 'main', ...new Set(rows.flatMap(r => [r.pr.base.sha, r.pr.merge_commit_sha]))]);
  const base = git(['rev-parse', 'origin/main']);
  // Runtime code is already imported from the immutable workflow checkout.
  git(['checkout', '--detach', base]);
  const paths = rows.flatMap(r => r.roots.flatMap(p => [p, p.replace(/^pending\//, 'skills/')]));
  for (const path of paths) assertDirectoryAncestors(path);
  git(['sparse-checkout', 'set', '--no-cone', '--stdin'], ['/scripts/', ...paths.map(p => `/${p}/`)].join('\n') + '\n');
  for (const row of rows) {
    row.plan = resolveApprovedSubmission({ repositoryRoot: process.cwd(), changedFiles: row.files,
      reportOnlyBaseCommit: row.pr.base.sha, reportOnlyMergeCommit: row.pr.merge_commit_sha });
    const refs = api(`git/matching-refs/tags/agentcrew-dispatch-outbox/publication/${row.digest}/`);
    const statuses = all(`commits/${row.pr.merge_commit_sha}/statuses?per_page=100`);
    const decision = chooseAttempt({ refs, statuses, digest: row.digest, merge: row.pr.merge_commit_sha, now: Date.now() });
    if (!decision.attempt) throw new Error(`#${row.pr.number}: ${decision.wait}`);
    row.attempt = decision.attempt;
    row.context = `agentcrew/publication/${row.digest}`;
    row.attemptContext = `agentcrew/publication-attempt/${row.digest}/${row.attempt}`;
  }
  validateBatchPlans(rows);
  const claimed = [];
  let pushed = false;
  const setStatus = (row, context, state, description) => api(`statuses/${row.pr.merge_commit_sha}`, { context, state, description, target_url: row.owner });
  try {
    for (const row of rows) {
      const ref = `refs/tags/agentcrew-dispatch-outbox/publication/${row.digest}/${row.attempt}`;
      api('git/refs', { ref, sha: row.pr.merge_commit_sha });
      if (api(`git/ref/${ref.slice(5)}`).object.sha !== row.pr.merge_commit_sha) throw new Error('Outbox readback mismatch');
      // Recheck after the durable outbox write, before any business mutation.
      const statuses = all(`commits/${row.pr.merge_commit_sha}/statuses?per_page=100`);
      if (statuses.some(s => s.context === row.context || s.context.startsWith(`agentcrew/publication-attempt/${row.digest}/`))) throw new Error('Concurrent receiver reservation');
      claimed.push(row);
      setStatus(row, row.attemptContext, 'pending', 'Exact publication attempt is running');
      setStatus(row, row.context, 'pending', 'Correlated publication is running');
    }
    git(['config', 'user.name', 'ai-skill-store[bot]']);
    git(['config', 'user.email', '2628292+ai-skill-store[bot]@users.noreply.github.com']);
    for (const row of rows) {
      for (const skill of row.plan.skills) {
        assertDirectoryAncestors(skill.pendingDir); assertDirectoryAncestors(skill.targetDir);
        if (skill.update) rmSync(skill.targetDir, { recursive: true });
        else if (existsSync(skill.targetDir)) throw new Error('Unexpected published target');
        mkdirSync(dirname(skill.targetDir), { recursive: true });
        renameSync(skill.pendingDir, skill.targetDir);
      }
      git(['add', '-A', '-f', '--', ...row.plan.skills.flatMap(s => [s.pendingDir, s.targetDir])]);
      git(['commit', '-m', `Approve reviewed skills for PR #${row.pr.number}${row.submissionId ? ` [submission: ${row.submissionId}]` : ''}`,
        '-m', `AgentCrew-Publication: ${row.correlation}`]);
    }
    const published = git(['rev-parse', 'HEAD']);
    // No rebase/force: any concurrent main change rejects the whole atomic push.
    if (git(['ls-remote', 'origin', 'refs/heads/main']).split(/\s/)[0] !== base) throw new Error('Main advanced; re-preflight required');
    git(['push', 'origin', 'HEAD:main']);
    const remote = git(['ls-remote', 'origin', 'refs/heads/main']).split(/\s/)[0];
    if (remote !== published) throw new Error('Publication push outcome requires inspection');
    pushed = true;
    for (const row of rows) await callback(row);
    for (const row of rows) setStatus(row, row.attemptContext, 'success', 'Exact publication attempt completed');
    console.log(JSON.stringify({ published, batch: process.env.BATCH_ID, prs: numbers, skills: rows.flatMap(r => r.plan.skills.map(s => s.reportSlug)) }));
  } catch (error) {
    for (const row of claimed) {
      setStatus(row, row.attemptContext, 'failure', 'Exact publication attempt failed');
      setStatus(row, row.context, 'failure', `Batch publication ${pushed ? 'partially completed' : 'requires inspection'}; no automatic replay`);
    }
    throw error;
  }
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main().catch(error => { console.error(error.message); process.exitCode = 1; });
