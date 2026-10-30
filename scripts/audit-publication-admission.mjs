import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const SHA = /^[0-9a-f]{40}$/;
const REPORT = /^skills\/[a-z0-9][a-z0-9._-]*(?:\/[a-z0-9][a-z0-9._-]*)?\/skill-report\.json$/;
const WORKFLOW = '.github/workflows/audit-skills.yml';

function reportPaths(files) {
  assert(files.length > 0 && files.length < 3000, 'Missing or truncated report inventory');
  const paths = files.map(file => {
    assert(REPORT.test(file.filename) && !file.filename.split('/').some(p => p === '.' || p === '..'), 'Noncanonical report path');
    assert(file.status === 'modified' && !file.previous_filename, 'Audit may only modify existing reports');
    return file.filename;
  });
  assert.equal(new Set(paths).size, paths.length, 'Duplicate report path');
  return paths.sort();
}

// GitHub PR/commit/run/job APIs paginate differently. Never accept a partial inventory.
async function inventory(api, endpoint, key) {
  const items = [];
  for (let page = 1; page <= 20; page++) {
    const result = await api(`${endpoint}${endpoint.includes('?') ? '&' : '?'}per_page=100&page=${page}`);
    const batch = key ? result[key] : result;
    assert(Array.isArray(batch), 'Malformed GitHub inventory');
    items.push(...batch);
    if (batch.length < 100) return items;
  }
  throw new Error('GitHub inventory exceeds bounded admission lookup');
}

async function ancestor(api, root, from, to) {
  assert(SHA.test(from) && SHA.test(to), 'Invalid commit identity');
  if (from === to) return;
  const comparison = await api(`${root}/compare/${from}...${to}`);
  assert(['identical', 'ahead'].includes(comparison.status), 'Producer commit is not an ancestor');
}

export const admitAuditPullRequest = (input, api) => verifyAuditPullRequest(input, api, false);
export const verifyMergedAuditPullRequest = (input, api) => verifyAuditPullRequest(input, api, true);

async function verifyAuditPullRequest({ repository, number, expectedHead }, api, merged) {
  assert(/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository), 'Invalid repository');
  assert(Number.isSafeInteger(Number(number)) && Number(number) > 0 && SHA.test(expectedHead), 'Invalid PR/head');
  const root = `repos/${repository}`;
  const pr = await api(`${root}/pulls/${number}`);
  assert(!pr.draft && pr.number === Number(number), 'PR must be non-draft');
  assert(merged ? pr.state === 'closed' && pr.merged === true && SHA.test(pr.merge_commit_sha)
    : pr.state === 'open', 'Unexpected PR lifecycle for this verifier');
  assert(pr.user.id === 254047988 && pr.user.login === 'ai-skill-store[bot]', 'Untrusted author');
  assert(pr.head.repo.full_name === repository && pr.base.repo.full_name === repository && pr.base.ref === 'main', 'Untrusted repository/base');
  assert.equal(pr.head.sha, expectedHead, 'PR head changed');
  assert(/^audit\/[0-9]{8}-[0-9]{6}$/.test(pr.head.ref), 'Untrusted audit branch');
  const files = await inventory(api, `${root}/pulls/${number}/files`);
  assert.equal(files.length, pr.changed_files, 'Incomplete PR files');
  const paths = reportPaths(files);
  const workflow = await api(`${root}/actions/workflows/audit-skills.yml`);
  const runs = await inventory(api, `${root}/actions/workflows/${workflow.id}/runs?event=workflow_dispatch&branch=main&created=${encodeURIComponent(`<=${pr.created_at}`)}`, 'workflow_runs');
  for (const run of runs) {
    if (run.workflow_id !== workflow.id || run.path !== WORKFLOW || run.event !== 'workflow_dispatch' ||
        run.head_branch !== 'main' || run.repository?.full_name !== repository || run.head_repository?.full_name !== repository ||
        run.status !== 'completed' || run.conclusion !== 'success' ||
        !(run.created_at <= pr.created_at && run.updated_at >= pr.created_at)) continue;
    await ancestor(api, root, run.head_sha, pr.base.sha);
    const jobs = await inventory(api, `${root}/actions/runs/${run.id}/jobs?filter=latest`, 'jobs');
    const job = jobs.find(j => j.name === 'merge' && j.conclusion === 'success' &&
      j.steps?.some(s => s.name === 'Apply results and create PR' && s.conclusion === 'success'));
    if (!job) continue;
    // Authenticated producer-job logs, NOT a PR body, commit author or branch assertion.
    // Legacy git output abbreviates SHA; resolve through GitHub to a full, unambiguous commit.
    const logs = await api(`${root}/actions/jobs/${job.id}/logs`, true);
    const lines = logs.replace(/\x1b\[[0-9;]*m/g, '').split(/\r?\n/).map(line => line.replace(/^\d{4}-\d\d-\d\dT\S+ /, ''));
    const notice = `##[notice]Created PR: https://github.com/${repository}/pull/${number}`;
    if (!lines.includes(notice)) continue;
    const commits = lines.map(line => /^\[(audit\/[0-9]{8}-[0-9]{6}) ([0-9a-f]{7,40})\] chore\(audit\): audit [0-9]+ skills(?: \([0-9]+ shards\))?$/.exec(line))
      .filter(match => match?.[1] === pr.head.ref);
    assert.equal(commits.length, 1, 'Missing or ambiguous producer commit');
    const generated = await api(`${root}/commits/${commits[0][2]}`);
    assert(SHA.test(generated.sha) && generated.sha.startsWith(commits[0][2]), 'Unresolved producer commit');
    assert.equal(generated.parents?.length, 1, 'Producer must create a single-parent audit commit');
    await ancestor(api, root, run.head_sha, generated.parents[0].sha);
    await ancestor(api, root, generated.parents[0].sha, pr.base.sha);
    await ancestor(api, root, generated.sha, expectedHead);
    const originalFiles = await inventory(api, `${root}/commits/${generated.sha}`, 'files');
    assert.deepEqual(reportPaths(originalFiles), paths, 'Generated report scope changed');
    // A normal main merge update may change head SHA, but cannot replace the generated reports.
    for (const path of paths) {
      const endpoint = `${root}/contents/${path.split('/').map(encodeURIComponent).join('/')}`;
      const original = await api(`${endpoint}?ref=${generated.sha}`);
      const current = await api(`${endpoint}?ref=${expectedHead}`);
      assert(original.type === 'file' && current.type === 'file' && SHA.test(original.sha) && current.sha === original.sha, 'Generated report bytes changed');
    }
    // Close a concurrent head-change window before reporting success.
    assert.equal((await api(`${root}/pulls/${number}`)).head.sha, expectedHead, 'PR head changed during verification');
    return { runId: run.id, jobId: job.id, generatedHead: generated.sha, head: expectedHead, paths };
  }
  throw new Error('No successful main Audit Skills producer bound to this PR and commit');
}

// Job logs contain ANSI color escapes, which gh refuses to print unless this flag is set.
// It only permits the text; parsing and every admission decision below stay unchanged.
export function rawLogArgs(endpoint) {
  assert(/^repos\/[^/]+\/[^/]+\/actions\/jobs\/[1-9][0-9]*\/logs$/.test(endpoint), 'Unexpected raw log endpoint');
  return ['api', '--allow-escape-sequences', '--method', 'GET', endpoint];
}
function github(endpoint, raw = false) {
  const result = execFileSync('gh', raw ? rawLogArgs(endpoint) : ['api', '--method', 'GET', endpoint], {
    encoding: 'utf8', timeout: 30_000, maxBuffer: 16 * 1024 * 1024,
  });
  return raw ? result : JSON.parse(result);
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  if (process.argv[2] === '--print-raw-log-args') {
    console.log(JSON.stringify(rawLogArgs(process.argv[3] ?? 'repos/o/r/actions/jobs/1/logs')));
    process.exit(0);
  }
  const result = await admitAuditPullRequest({ repository: process.env.REPOSITORY,
    number: Number(process.env.PR_NUMBER), expectedHead: process.env.HEAD_SHA }, github);
  console.log(JSON.stringify(result));
}
