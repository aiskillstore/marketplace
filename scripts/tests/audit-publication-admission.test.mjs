import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { admitAuditPullRequest } from '../audit-publication-admission.mjs';

const repository = 'aiskillstore/marketplace';
const head = '1'.repeat(40), base = '2'.repeat(40), source = '3'.repeat(40);
const path = 'skills/owner/skill/skill-report.json';
function fixture() {
  const pr = { number: 42, state: 'open', draft: false, changed_files: 1,
    created_at: '2026-10-29T18:24:40Z', user: { id: 254047988, login: 'ai-skill-store[bot]' },
    head: { sha: head, ref: 'audit/20261029-182431', repo: { full_name: repository } },
    base: { sha: base, ref: 'main', repo: { full_name: repository } } };
  const run = { id: 10, workflow_id: 20, path: '.github/workflows/audit-skills.yml', event: 'workflow_dispatch',
    head_branch: 'main', head_sha: base, status: 'completed', conclusion: 'success',
    repository: { full_name: repository }, head_repository: { full_name: repository },
    created_at: '2026-10-29T18:13:42Z', updated_at: '2026-10-29T18:25:00Z' };
  const files = [{ filename: path, status: 'modified' }];
  const data = { pr, run, files, originalFiles: structuredClone(files), generated: head,
    logs: `2026-10-29T18:24:34Z [${pr.head.ref} ${head.slice(0, 8)}] chore(audit): audit 1 skills\n2026-10-29T18:24:40Z ##[notice]Created PR: https://github.com/${repository}/pull/42\n`,
    blob: 'a'.repeat(40), originalBlob: 'a'.repeat(40), ancestor: 'ahead', jobConclusion: 'success' };
  const api = async (endpoint, raw = false) => {
    if (endpoint === `repos/${repository}/pulls/42`) return data.pr;
    if (endpoint.includes('/pulls/42/files?')) return data.files;
    if (endpoint.endsWith('/actions/workflows/audit-skills.yml')) return { id: 20 };
    if (endpoint.includes('/actions/workflows/20/runs?')) return { workflow_runs: [data.run] };
    if (endpoint.includes('/actions/runs/10/jobs?')) return { jobs: [{ id: 30, name: 'merge', conclusion: data.jobConclusion,
      steps: [{ name: 'Apply results and create PR', conclusion: 'success' }] }] };
    if (endpoint.endsWith('/actions/jobs/30/logs') && raw) return data.logs;
    if (endpoint.endsWith(`/commits/${head.slice(0, 8)}`) || endpoint.endsWith(`/commits/${head}`))
      return { sha: data.generated, parents: [{ sha: base }] };
    if (endpoint.includes(`/commits/${data.generated}?`)) return { files: data.originalFiles };
    if (endpoint.includes('/compare/')) return { status: data.ancestor };
    if (endpoint.includes('/contents/')) return { type: 'file', sha: endpoint.endsWith(`ref=${data.generated}`) ? data.originalBlob : data.blob };
    throw new Error(`Unexpected request: ${endpoint}`);
  };
  return { data, api };
}
const admit = (f) => admitAuditPullRequest({ repository, number: 42, expectedHead: f.data.pr.head.sha }, f.api);

test('admits existing audit using GitHub-resolved commit from authenticated producer logs', async () => {
  const f = fixture();
  assert.equal((await admit(f)).generatedHead, head);
});
test('admits merge-updated head only when generated report bytes are unchanged', async () => {
  const f = fixture(); f.data.pr.head.sha = source;
  assert.equal((await admit(f)).generatedHead, head);
  f.data.blob = 'different';
  await assert.rejects(admit(f), /report bytes/);
});
for (const [name, change] of [
  ['human', d => { d.pr.user.id = 1; }],
  ['fork', d => { d.pr.head.repo.full_name = 'other/repo'; }],
  ['wrong base', d => { d.pr.base.ref = 'dev'; }],
  ['changed exact head', d => { d.pr.head.sha = ''; }],
  ['source change', d => { d.files[0].filename = 'skills/owner/skill/SKILL.md'; }],
  ['report added', d => { d.files[0].status = 'added'; }],
  ['rename', d => { d.files[0].previous_filename = 'skills/old/skill-report.json'; }],
  ['path traversal', d => { d.files[0].filename = 'skills/../skill/skill-report.json'; }],
  ['noncanonical depth', d => { d.files[0].filename = 'skills/a/b/c/skill-report.json'; }],
  ['truncated files', d => { d.pr.changed_files = 2; }],
  ['wrong workflow', d => { d.run.workflow_id = 21; }],
  ['wrong event', d => { d.run.event = 'push'; }],
  ['non-main run', d => { d.run.head_branch = 'attacker'; }],
  ['failed run', d => { d.run.conclusion = 'failure'; }],
  ['foreign run', d => { d.run.repository.full_name = 'other/repo'; }],
  ['failed producer job', d => { d.jobConclusion = 'failure'; }],
  ['unrelated PR notice', d => { d.logs = d.logs.replace('/pull/42', '/pull/43'); }],
  ['unresolved short SHA', d => { d.generated = '4'.repeat(40); }],
  ['unrelated original source change', d => { d.originalFiles.push({ filename: '.github/workflows/evil.yml', status: 'added' }); }],
  ['original not ancestor', d => { d.pr.head.sha = source; d.ancestor = 'diverged'; }],
]) test(`rejects ${name}`, async () => {
  const f = fixture(); change(f.data);
  await assert.rejects(admit(f));
});
test('workflow uses trusted base code with read-only producer permissions and exact PR head', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/publication-provenance.yml', import.meta.url), 'utf8');
  assert.match(workflow, /actions: read/);
  assert.match(workflow, /ref: \$\{\{ github.event.pull_request.base.sha \}\}/);
  assert.match(workflow, /persist-credentials: false/);
  assert.match(workflow, /HEAD_SHA: \$\{\{ github.event.pull_request.head.sha \}\}/);
  assert.match(workflow, /run: node scripts\/audit-publication-admission.mjs/);
  assert.doesNotMatch(workflow, /pull_request_target|contents: write|pull-requests: write/);
});
test('normal validate CI runs the new admission regression suite', () => {
  const workflow = readFileSync(new URL('../../.github/workflows/validate-marketplace.yml', import.meta.url), 'utf8');
  assert.match(workflow, /node --test[\s\S]*scripts\/tests\/audit-publication-admission.test.mjs/);
  assert.equal(workflow.split('"scripts/audit-publication-admission.mjs"').length - 1, 2);
});
test('propagates GitHub failure, never treats it as absence or success', async () => {
  await assert.rejects(admitAuditPullRequest({ repository, number: 42, expectedHead: head }, async () => { throw new Error('HTTP 503'); }), /503/);
});
