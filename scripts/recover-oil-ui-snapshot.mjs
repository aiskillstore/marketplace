import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

// Incident-specific correction, not an alternate publisher or relaxed validator.
// These immutable values were independently inspected before recovery review.
export const INCIDENT = Object.freeze({
  head: '4b85b545be916371fb7eeaa9d2d999fddc074653',
  merge: '6f4b33012f276898d109099ccd1d735c06f6a39a',
  sourceBranch: 'submission/oil-ui-639e9449-9c6c-4491-b526-48333d0c087e',
  pending: 'pending/oil-oil/oil-ui', target: 'skills/oil-oil/oil-ui',
  pendingTree: 'c4fd7bfc921031a433b55b2bf480e1ed0e20a13b',
  publishedTree: 'dd69021639954aed29dad075b5113fb843fc3c02',
  reportBlob: '07a9e0976ffff42eb107a9badfb7bc2894819e18',
  previousRef: 'b7004ab84654f04d9a0820dbaacd9f555bbb269a',
  nextRef: '48518fd02946ccbda54cd3544f8bd102413128cf',
  previousTreeHash: '74dfcc43cd92eb80de5c25761160452842152842998f71db5053d996e5d148f7',
  contentHash: 'b0cb831880a5c7b06680c69a1fb58377e3880c6b39f3cac99ebc6dd647b7e05f',
  treeHash: 'a1ededc25c8944a52727a8d0e2d657af08e24ca8883570b3b2c0a58c9e1085ec',
  preflight: 'agentcrew/publication-preflight/38214431643158e74a545536b3fc3b4f70103c1e576f1878900af3d0baa9af26',
  failure: 'No publication mutations: pending/oil-oil/oil-ui reviewed update snapshot does not match the published target',
  failedRun: 'https://github.com/aiskillstore/marketplace/actions/runs/37313430404',
});
const repo = 'aiskillstore/marketplace';
const branch = 'submission/recover-oil-ui-3671-snapshot';
const reportPath = `${INCIDENT.pending}/skill-report.json`;

export function validateEvidence(e) {
  const p = e.pr;
  assert.equal(p.number, 3671); assert.equal(p.merged, true);
  assert.equal(p.user.id, 254047988); assert.equal(p.user.login, 'ai-skill-store[bot]');
  assert.equal(p.head.sha, INCIDENT.head); assert.equal(p.merge_commit_sha, INCIDENT.merge);
  assert.equal(p.head.ref, INCIDENT.sourceBranch); assert.equal(p.head.repo.full_name, repo);
  assert.equal(p.base.ref, 'main'); assert.equal(p.base.repo.full_name, repo);
  assert.deepEqual([...String(p.body).matchAll(/Submission ID[^\r\n]*?`([0-9a-f-]{36})`/g)].map(m=>m[1]),
    ['639e9449-9c6c-4491-b526-48333d0c087e']);
  assert.equal(e.priorCorrections.length, 0, 'Prior correction PR exists; do not replay even if branch was deleted');
  assert.deepEqual(e.reportEntry, {sha:INCIDENT.reportBlob,mode:'100644',type:'blob'});
  assert.equal(e.pendingTree, INCIDENT.pendingTree); assert.equal(e.originalPendingTree, INCIDENT.pendingTree);
  assert.equal(e.publishedTree, INCIDENT.publishedTree);
  assert(e.files.length > 1 && e.files.length < 100);
  assert(e.files.every(f => f.startsWith(`${INCIDENT.pending}/`) && !f.includes('..') && !f.includes('\\')));
  assert(e.files.includes(reportPath)); assert(e.files.includes(`${INCIDENT.pending}/SKILL.md`));
  assert.equal(e.outbox.length, 0, 'Prior dispatch evidence forbids automatic correction');
  assert.equal(e.statuses.length, 1, 'Any new status requires independent inspection');
  const s = e.statuses[0];
  assert.equal(s.creator?.id, 254047988); assert.equal(s.creator?.login, 'ai-skill-store[bot]');
  assert.equal(s.context, INCIDENT.preflight); assert.equal(s.state, 'failure');
  assert.equal(s.description, INCIDENT.failure); assert.equal(s.target_url, INCIDENT.failedRun);
  assert.equal(e.comparison.status, 'ahead'); assert.equal(e.comparison.behind_by, 0);
  assert.equal(e.comparison.ahead_by, 1); assert.equal(e.comparison.merge_base_commit.sha, INCIDENT.previousRef);
}

export function correctedReport(raw) {
  const report = JSON.parse(raw);
  const m = report.meta;
  assert.equal(m.slug, 'oil-oil-oil-ui'); assert.equal(m.source_type, 'community');
  assert.equal(m.source_ref, INCIDENT.nextRef);
  assert.equal(m.source_url, `https://github.com/oil-oil/oil-ui/tree/${INCIDENT.nextRef}/`);
  assert.equal(m.content_hash, INCIDENT.contentHash); assert.equal(m.tree_hash, INCIDENT.treeHash);
  assert(!Object.hasOwn(m, 'previous_tree_hash')); assert(!Object.hasOwn(m, 'previous_source_ref'));
  m.previous_tree_hash = INCIDENT.previousTreeHash;
  m.previous_source_ref = INCIDENT.previousRef;
  return `${JSON.stringify(report, null, 2)}\n`;
}
function api(path, data) {
  const args = ['api', path];
  if (data) args.push('--method', 'POST', '--input', '-');
  return JSON.parse(execFileSync('gh', args, {
    encoding: 'utf8', input: data ? JSON.stringify(data) : undefined,
    maxBuffer: 8 * 1024 * 1024, timeout: 60_000,
  }));
}
const endpoint = path => `repos/${repo}/${path}`;
function treeAt(commit, path) {
  const value = api(endpoint(`git/trees/${commit}:${path}`));
  assert.equal(value.truncated, false); return value.sha;
}
function gitBlob(content) {
  const bytes = Buffer.from(content);
  return createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
}
export function main() {
  const apply = process.argv.includes('--apply');
  if (apply) {
    assert.equal(process.env.GITHUB_REPOSITORY, repo);
    assert.equal(process.env.GITHUB_REF, 'refs/heads/main');
    assert.equal(process.env.GITHUB_EVENT_NAME, 'workflow_dispatch');
    assert.match(process.env.GITHUB_SHA ?? '', /^[a-f0-9]{40}$/);
  }
  const base = api(endpoint('git/ref/heads/main')).object.sha;
  if (apply) assert.equal(base, process.env.GITHUB_SHA, 'Main advanced; review before another dispatch');
  const correlation = `submission-pr-3671-${INCIDENT.head}-${INCIDENT.merge}`;
  const digest = createHash('sha256').update(correlation).digest('hex');
  const e = {
    pr: api(endpoint('pulls/3671')),
    priorCorrections: api(endpoint(`pulls?state=all&head=aiskillstore:${branch}&per_page=100`)),
    reportEntry: (() => {
      const entry = api(endpoint(`git/trees/${INCIDENT.pendingTree}`)).tree.find(t=>t.path==='skill-report.json');
      return {sha:entry?.sha,mode:entry?.mode,type:entry?.type};
    })(),
    pendingTree: treeAt(base, INCIDENT.pending), publishedTree: treeAt(base, INCIDENT.target),
    originalPendingTree: treeAt(INCIDENT.merge, INCIDENT.pending),
    files: api(endpoint('pulls/3671/files?per_page=100')).map(f => f.filename),
    statuses: api(endpoint(`commits/${INCIDENT.merge}/statuses?per_page=100`)),
    outbox: api(endpoint(`git/matching-refs/tags/agentcrew-dispatch-outbox/publication/${digest}/`)),
    comparison: api(`repos/oil-oil/oil-ui/compare/${INCIDENT.previousRef}...${INCIDENT.nextRef}`),
  };
  validateEvidence(e);
  const existing = api(endpoint(`git/matching-refs/heads/${branch}`));
  assert.equal(existing.length, 0, 'Recovery branch already exists; inspect its PR, never replay');
  const blob = api(endpoint(`git/blobs/${INCIDENT.reportBlob}`));
  assert.equal(blob.encoding, 'base64');
  const raw = Buffer.from(blob.content, 'base64').toString('utf8');
  assert.equal(gitBlob(raw), INCIDENT.reportBlob);
  const content = correctedReport(raw);
  if (!apply) return console.log(JSON.stringify({mode:'read-only',base,pr:3671,branch,changed:[reportPath],expectedBlob:gitBlob(content)}));

  // The only business effect is a new reviewable bot PR. Never changes main,
  // the original report/PR/status, or provider data. Deterministic branch fences
  // replay; any failed/unknown effect requires inspection, not automatic retry.
  assert.equal(api(endpoint('git/ref/heads/main')).object.sha, base);
  const newBlob = api(endpoint('git/blobs'), {content,encoding:'utf-8'});
  assert.equal(newBlob.sha, gitBlob(content));
  const baseTree = api(endpoint(`git/commits/${base}`)).tree.sha;
  const newTree = api(endpoint('git/trees'), {base_tree:baseTree,tree:[{path:reportPath,mode:'100644',type:'blob',sha:newBlob.sha}]});
  const commit = api(endpoint('git/commits'), {message:'fix(submission): bind oil-ui reviewed update snapshot for PR #3671',tree:newTree.sha,parents:[base]});
  const check = api(endpoint(`commits/${commit.sha}`));
  assert.deepEqual(check.files.map(f=>f.filename), [reportPath]);
  assert.equal(check.files[0].sha, newBlob.sha);
  assert.equal(api(endpoint(`contents/${reportPath}?ref=${commit.sha}`)).sha, newBlob.sha);
  api(endpoint('git/refs'), {ref:`refs/heads/${branch}`,sha:commit.sha});
  assert.equal(api(endpoint(`git/ref/heads/${branch}`)).object.sha,commit.sha);
  const pr = api(endpoint('pulls'), {title:'fix(submission): recover oil-ui update snapshot (PR #3671)',head:branch,base:'main',body:
    `Supersedes blocked publication of https://github.com/${repo}/pull/3671.\n\nOnly adds previous_tree_hash and previous_source_ref to the exact reviewed report; all Skill bytes and other report values are unchanged. Published target is pinned to tree ${INCIDENT.publishedTree}, source ${INCIDENT.previousRef}. Next source ${INCIDENT.nextRef} is its direct successor.\n\nOriginal preflight recorded zero publication mutations. No original status is overwritten. This new trusted PR must pass normal CI/review/merge/publication/provider sync.\n\nSubmission ID: \`639e9449-9c6c-4491-b526-48333d0c087e\`\nOriginal head: ${INCIDENT.head}; merge: ${INCIDENT.merge}.`});
  const readback = api(endpoint(`pulls/${pr.number}`));
  assert.equal(readback.head.sha,commit.sha); assert.equal(readback.user.id,254047988);
  api(endpoint(`issues/${pr.number}/labels`),{labels:['pending-review']});
  assert(api(endpoint(`issues/${pr.number}/labels`)).some(l=>l.name==='pending-review'));
  console.log(JSON.stringify({pr:pr.html_url,head:commit.sha,base,changed:[reportPath]}));
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main();
