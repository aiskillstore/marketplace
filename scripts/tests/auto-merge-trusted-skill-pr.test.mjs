import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  AutoMergeBlockedError,
  AutoMergeUnknownEffectError,
  GitHubApi,
  latestStatusesByContext,
  runAutoMerge,
  runRecoverySweep,
  validateSnapshot,
} from '../auto-merge-trusted-skill-pr.mjs';

const REPO = { id: 9001, full_name: 'aiskillstore/marketplace', default_branch: 'main' };
const HEAD = 'a'.repeat(40);
const BASE = 'b'.repeat(40);
const MERGE = 'd'.repeat(40);
const ROOT = 'pending/example/skill';
const SOURCE_ROOT = 'skills/example/skill';

function snapshot(overrides = {}) {
  const value = {
    repository: REPO,
    repositoryRules: [{
      enforcement: 'active',
      target: 'branch',
      bypass_actors: [{ actor_id: 2628292, actor_type: 'Integration', bypass_mode: 'always' }],
      conditions: { ref_name: { include: ['refs/heads/main'], exclude: [] } },
      rules: [
        { type: 'pull_request', parameters: { allowed_merge_methods: ['merge'] } },
        { type: 'required_status_checks', parameters: { strict_required_status_checks_policy: true, required_status_checks: [{ context: 'publication-admission', integration_id: 15368 }] } },
      ],
    }],
    workflowRun: {
      id: 123,
      name: 'Validate Marketplace',
      event: 'pull_request',
      status: 'completed',
      conclusion: 'success',
      head_sha: HEAD,
      pull_requests: [{ number: 42 }],
    },
    pr: {
      number: 42,
      state: 'open',
      draft: false,
      merged: false,
      changed_files: 2,
      mergeable: true,
      mergeable_state: 'clean',
      user: { id: 254047988, login: 'ai-skill-store[bot]', type: 'Bot' },
      labels: [{ name: 'pending-review' }],
      base: { ref: 'main', sha: BASE, repo: { ...REPO } },
      head: { ref: 'submission/example-42', sha: HEAD, repo: { ...REPO } },
    },
    files: [
      { filename: `${ROOT}/SKILL.md`, status: 'added', sha: '1'.repeat(40) },
      { filename: `${ROOT}/skill-report.json`, status: 'added', sha: '2'.repeat(40) },
    ],
    checks: [
      {
        id: 1001, name: 'publication-admission', status: 'completed', conclusion: 'success', app: { id: 15368 },
        workflow: { run_id: 200, id: 330383167, name: 'Publication Provenance', path: '.github/workflows/publication-provenance.yml', event: 'pull_request', head_sha: HEAD, status: 'completed', conclusion: 'success' },
      },
      {
        id: 1002, name: 'action-pin-policy', status: 'completed', conclusion: 'success', app: { id: 15368 },
        workflow: { run_id: 123, id: 219313535, name: 'Validate Marketplace', path: '.github/workflows/validate-marketplace.yml', event: 'pull_request', head_sha: HEAD, status: 'completed', conclusion: 'success' },
      },
      {
        id: 1003, name: 'validate', status: 'completed', conclusion: 'success', app: { id: 15368 },
        workflow: { run_id: 123, id: 219313535, name: 'Validate Marketplace', path: '.github/workflows/validate-marketplace.yml', event: 'pull_request', head_sha: HEAD, status: 'completed', conclusion: 'success' },
      },
    ],
    statuses: [],
    tree: {
      truncated: false,
      entries: [
        { path: `${ROOT}/SKILL.md`, type: 'blob', mode: '100644', sha: '1'.repeat(40) },
        { path: `${ROOT}/skill-report.json`, type: 'blob', mode: '100644', sha: '2'.repeat(40) },
      ],
    },
    reports: [{
      path: `${ROOT}/skill-report.json`,
      sha: '2'.repeat(40),
    }],
    basePendingExists: false,
    baseSkillRootsExist: false,
    publishedTargetExists: false,
  };
  return structuredClone(Object.assign(value, overrides));
}

function sourceMonitorSnapshot(overrides = {}) {
  const value = snapshot({ baseSkillRootsExist: true, publishedTargetExists: true });
  value.pr.head.ref = 'skill-source-monitor/run-32942863771';
  value.pr.labels = [{ name: 'skill-source-monitor' }];
  value.files = [
    { filename: `${SOURCE_ROOT}/SKILL.md`, status: 'modified', sha: '3'.repeat(40) },
    { filename: `${SOURCE_ROOT}/skill-report.json`, status: 'modified', sha: '4'.repeat(40) },
  ];
  value.tree.entries = [
    { path: `${SOURCE_ROOT}/SKILL.md`, type: 'blob', mode: '100644', sha: '3'.repeat(40) },
    { path: `${SOURCE_ROOT}/skill-report.json`, type: 'blob', mode: '100644', sha: '4'.repeat(40) },
    { path: `${SOURCE_ROOT}/references/unchanged.md`, type: 'blob', mode: '100644', sha: '5'.repeat(40) },
  ];
  value.reports = [{
    path: `${SOURCE_ROOT}/skill-report.json`,
    sha: '4'.repeat(40),
  }];
  return structuredClone(Object.assign(value, overrides));
}

function expectBlocked(value, pattern) {
  assert.throws(() => validateSnapshot(value), (error) => {
    assert.ok(error instanceof AutoMergeBlockedError);
    assert.match(error.message, pattern);
    return true;
  });
}

test('qualifies one exact trusted NEW_SKILL root for ordinary merge', () => {
  assert.deepEqual(validateSnapshot(snapshot()), {
    eligible: true,
    action: 'merge',
    classification: 'NEW_SKILL',
    postMergeAction: 'publication',
    prNumber: 42,
    headSha: HEAD,
    baseSha: BASE,
    root: ROOT,
    roots: [ROOT],
  });
});

test('qualifies UPDATE_SKILL and requests only standard update-branch when behind', () => {
  const value = snapshot({ publishedTargetExists: true });
  value.pr.mergeable_state = 'behind';
  assert.equal(validateSnapshot(value).classification, 'UPDATE_SKILL');
  assert.equal(validateSnapshot(value).action, 'update_branch');
});

test('qualifies an exact trusted source-monitor update and routes its post-merge sync', () => {
  assert.deepEqual(validateSnapshot(sourceMonitorSnapshot()), {
    eligible: true,
    action: 'merge',
    classification: 'SOURCE_MONITOR_UPDATE',
    postMergeAction: 'provider_sync',
    prNumber: 42,
    headSha: HEAD,
    baseSha: BASE,
    root: SOURCE_ROOT,
    roots: [SOURCE_ROOT],
  });
});

test('source-monitor accepts a canonical flat published Skill root', () => {
  const value = sourceMonitorSnapshot();
  const flatRoot = 'skills/flat-skill';
  const rewrite = (path) => path.replace(SOURCE_ROOT, flatRoot);
  value.files = value.files.map((file) => ({ ...file, filename: rewrite(file.filename) }));
  value.tree.entries = value.tree.entries.map((entry) => ({ ...entry, path: rewrite(entry.path) }));
  value.reports = value.reports.map((report) => ({ ...report, path: rewrite(report.path) }));
  assert.deepEqual(validateSnapshot(value).roots, [flatRoot]);
});

test('source-monitor accepts auxiliary-only changes when exact-head SKILL.md and changed report remain bound', () => {
  const value = sourceMonitorSnapshot();
  value.files = value.files.filter((file) => file.filename !== `${SOURCE_ROOT}/SKILL.md`);
  value.pr.changed_files = value.files.length;
  assert.equal(validateSnapshot(value).classification, 'SOURCE_MONITOR_UPDATE');
});

test('source-monitor route fails closed on branch, label, published scope and exact-head binding', () => {
  const cases = [
    [() => { const v = sourceMonitorSnapshot(); v.pr.head.ref = 'skill-source-monitor/manual'; return v; }, /trusted source-monitor provenance/],
    [() => { const v = sourceMonitorSnapshot(); v.pr.labels = [{ name: 'pending-review' }]; return v; }, /skill-source-monitor label/],
    [() => { const v = sourceMonitorSnapshot(); v.pr.labels.push({ name: 'pending-review' }); return v; }, /must not have pending-review/],
    [() => { const v = sourceMonitorSnapshot(); v.files.push({ filename: 'scripts/injected.mjs', status: 'modified', sha: '6'.repeat(40) }); v.pr.changed_files = 3; return v; }, /published Skill root/],
    [() => { const v = sourceMonitorSnapshot(); v.files[0].status = 'renamed'; v.files[0].previous_filename = 'skills/example/old/SKILL.md'; return v; }, /unsupported source-monitor file status/],
    [() => { const v = sourceMonitorSnapshot(); v.files[1].status = 'removed'; return v; }, /skill-report\.json/],
    [() => { const v = sourceMonitorSnapshot(); v.baseSkillRootsExist = false; return v; }, /must already exist on the base/],
    [() => { const v = sourceMonitorSnapshot(); v.files[0].sha = '6'.repeat(40); return v; }, /exact PR head/],
    [() => {
      const v = sourceMonitorSnapshot();
      for (let index = 2; index <= 26; index += 1) {
        const root = `skills/example/skill-${index}`;
        const skillSha = index.toString(16).padStart(40, '0');
        const reportSha = (index + 100).toString(16).padStart(40, '0');
        v.files.push(
          { filename: `${root}/SKILL.md`, status: 'modified', sha: skillSha },
          { filename: `${root}/skill-report.json`, status: 'modified', sha: reportSha },
        );
        v.tree.entries.push(
          { path: `${root}/SKILL.md`, type: 'blob', mode: '100644', sha: skillSha },
          { path: `${root}/skill-report.json`, type: 'blob', mode: '100644', sha: reportSha },
        );
        v.reports.push({ path: `${root}/skill-report.json`, sha: reportSha });
      }
      v.pr.changed_files = v.files.length;
      return v;
    }, /provider sync limit/],
  ];
  for (const [build, pattern] of cases) expectBlocked(build(), pattern);
});

test('fails closed on identity, provenance, scope, label, state and exact-head drift', () => {
  const cases = [
    [() => { const v = snapshot(); v.pr.user.id = 7; return v; }, /trusted App identity/],
    [() => { const v = snapshot(); v.pr.user.login = 'ai-skill-store'; return v; }, /trusted App identity/],
    [() => { const v = snapshot(); v.pr.head.repo.id = 7; return v; }, /same repository/],
    [() => { const v = snapshot(); v.pr.head.ref = 'feature/x'; return v; }, /submission\/ or source-monitor/],
    [() => { const v = snapshot(); v.pr.draft = true; return v; }, /open and non-draft/],
    [() => { const v = snapshot(); v.pr.labels = []; return v; }, /pending-review/],
    [() => { const v = snapshot(); v.workflowRun.head_sha = 'c'.repeat(40); return v; }, /exact PR head/],
    [() => { const v = snapshot(); v.files.push({ filename: '.github/workflows/pwn.yml', status: 'added', sha: '3'.repeat(40) }); v.pr.changed_files = 3; return v; }, /pending Skill root/],
    [() => { const v = snapshot(); v.files[0].status = 'modified'; return v; }, /newly added/],
    [() => { const v = snapshot(); v.basePendingExists = true; return v; }, /pending root already exists/],
  ];
  for (const [build, pattern] of cases) expectBlocked(build(), pattern);
});

test('uses only the newest commit status per context across retry history', () => {
  assert.deepEqual(latestStatusesByContext([
    { id: 3, context: 'legacy', state: 'success' },
    { id: 2, context: 'other', state: 'success' },
    { id: 1, context: 'legacy', state: 'failure' },
  ]), [
    { id: 3, context: 'legacy', state: 'success' },
    { id: 2, context: 'other', state: 'success' },
  ]);
});

test('fails closed on incomplete files, unsafe tree entries, truncation and ambiguous checks', () => {
  const cases = [
    [() => { const v = snapshot(); v.files.pop(); v.tree.entries.pop(); v.pr.changed_files = 1; return v; }, /skill-report\.json/],
    [() => { const v = snapshot(); v.tree.entries[0].mode = '120000'; return v; }, /ordinary blobs/],
    [() => { const v = snapshot(); v.tree.truncated = true; return v; }, /truncated/],
    [() => { const v = snapshot(); v.checks[2].conclusion = 'failure'; return v; }, /check validate.*failure/],
    [() => { const v = snapshot(); v.checks.push({ ...v.checks[2] }); return v; }, /duplicate check/],
    [() => { const v = snapshot(); v.checks.pop(); return v; }, /missing required check validate/],
    [() => { const v = snapshot(); v.statuses = [{ context: 'legacy', state: 'pending' }]; return v; }, /status legacy.*pending/],
    [() => { const v = snapshot(); v.checks[0].app.id = 999; return v; }, /not from GitHub Actions/],
    [() => { const v = snapshot(); v.checks[2].workflow.id = 999; return v; }, /not bound to the trusted workflow/],
    [() => { const v = snapshot(); v.checks[2].workflow.run_id = 999; return v; }, /not bound to the trusted workflow/],
    [() => { const v = snapshot(); v.repositoryRules[0].target = 'tag'; return v; }, /strict protected-main/],
    [() => { const v = snapshot(); v.repositoryRules[0].conditions.ref_name.exclude = ['refs/heads/main']; return v; }, /strict protected-main/],
    [() => { const v = snapshot(); v.repositoryRules[0].bypass_actors.push({ actor_id: 15368, actor_type: 'Integration' }); return v; }, /must not bypass/],
    [() => { const v = snapshot(); v.repositoryRules[0].rules[1].parameters.strict_required_status_checks_policy = false; return v; }, /strict protected-main/],
  ];
  for (const [build, pattern] of cases) expectBlocked(build(), pattern);
});

test('does not use security-report risk fields as automatic merge gates', () => {
  for (const securityAudit of [
    { is_blocked: true, safe_to_publish: false, risk_level: 'critical' },
    { is_blocked: false, safe_to_publish: false, risk_level: 'medium' },
    {},
    undefined,
  ]) {
    const value = snapshot();
    value.reports[0].securityAudit = securityAudit;
    assert.equal(validateSnapshot(value).eligible, true);
  }
});

test('qualifies multiple canonical pending Skill roots when every root has a bound report', () => {
  const secondRoot = 'pending/example/second-skill';
  const value = snapshot();
  value.files.push(
    { filename: `${secondRoot}/SKILL.md`, status: 'added', sha: '3'.repeat(40) },
    { filename: `${secondRoot}/skill-report.json`, status: 'added', sha: '4'.repeat(40) },
  );
  value.pr.changed_files = 4;
  value.tree.entries.push(
    { path: `${secondRoot}/SKILL.md`, type: 'blob', mode: '100644', sha: '3'.repeat(40) },
    { path: `${secondRoot}/skill-report.json`, type: 'blob', mode: '100644', sha: '4'.repeat(40) },
  );
  value.reports.push({
    path: `${secondRoot}/skill-report.json`,
    sha: '4'.repeat(40),
  });
  assert.deepEqual(validateSnapshot(value).roots, [ROOT, secondRoot].sort());
});

test('still requires every report file to be bound to the exact head', () => {
  const value = snapshot();
  value.reports[0].sha = '3'.repeat(40);
  expectBlocked(value, /exact PR head/);
});

function fakeApi(sequence) {
  const calls = [];
  return {
    calls,
    async buildSnapshot() {
      const next = sequence.shift();
      if (next instanceof Error) throw next;
      return structuredClone(next);
    },
    async readPr() {
      const next = sequence.shift();
      if (next instanceof Error) throw next;
      return structuredClone(next?.pr ?? next);
    },
    async readCommit(sha) {
      return { sha, parents: [{ sha: HEAD }, { sha: BASE }] };
    },
    async isCommitAncestor(ancestorSha, descendantSha) {
      return ancestorSha === descendantSha;
    },
    async sleep() {},
    async updateBranch(number, headSha) {
      calls.push(['update', number, headSha]);
      return { message: 'Updating pull request branch.' };
    },
    async merge(number, headSha, method) {
      calls.push(['merge', number, headSha, method]);
      return { merged: true, sha: 'd'.repeat(40), message: 'Pull Request successfully merged' };
    },
    async dispatchPublication(...args) {
      calls.push(['dispatch-publication', ...args]);
      return { outcome: 'PUBLICATION_DISPATCH_CONFIRMED' };
    },
    async dispatchProviderSync(...args) {
      calls.push(['dispatch-provider-sync', ...args]);
      return { outcome: 'PROVIDER_SYNC_DISPATCH_CONFIRMED' };
    },
  };
}

test('rejects base drift before the effect and performs no mutation', async () => {
  const changedBase = snapshot();
  changedBase.pr.base.sha = 'c'.repeat(40);
  const api = fakeApi([snapshot(), changedBase]);
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), /candidate changed/);
  assert.deepEqual(api.calls, []);
});

test('reconciles publication for an already merged trusted submission', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.equal(result.outcome, 'PUBLICATION_DISPATCH_CONFIRMED');
  assert.deepEqual(api.calls, [['dispatch-publication', 42, HEAD, 'd'.repeat(40)]]);
});

test('waits for transient GitHub mergeability before qualifying and updating a behind PR', async () => {
  const computing = snapshot();
  computing.pr.mergeable = null;
  computing.pr.mergeable_state = 'unknown';
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  changed.workflowRun.head_sha = 'e'.repeat(40);
  const api = fakeApi([computing, behind, behind, changed]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [['update', 42, HEAD]]);
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
});

test('revalidates immediately before exact-head ordinary merge and confirms authoritative readback', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([snapshot(), snapshot(), merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [['merge', 42, HEAD, 'merge'], ['dispatch-publication', 42, HEAD, 'd'.repeat(40)]]);
  assert.deepEqual(result, {
    outcome: 'MERGED_AND_PUBLICATION_DISPATCHED',
    prNumber: 42,
    headSha: HEAD,
    mergeCommitSha: 'd'.repeat(40),
    classification: 'NEW_SKILL',
  });
});

test('scheduled recovery performs only the merge effect and defers publication reconciliation', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([snapshot(), snapshot(), merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123, deferPostMergeDispatch: true });
  assert.equal(result.outcome, 'MERGED_AWAITING_PUBLICATION_RECONCILIATION');
  assert.deepEqual(api.calls, [['merge', 42, HEAD, 'merge']]);
});

test('update-branch uses expected exact head through the event-capable update credential and awaits fresh CI', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  changed.workflowRun.head_sha = 'e'.repeat(40);
  const api = fakeApi([behind, behind, changed]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [['update', 42, HEAD]]);
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
  assert.equal(result.newHeadSha, 'e'.repeat(40));
});

test('confirms update-branch against the fresh base readback when main advances after pre-effect validation', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  changed.pr.base.sha = 'c'.repeat(40);
  const api = fakeApi([behind, behind, changed.pr]);
  api.readCommit = async (sha) => ({ sha, parents: [{ sha: HEAD }, { sha: changed.pr.base.sha }] });
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
  assert.equal(result.newHeadSha, changed.pr.head.sha);
});

test('confirms update when the update base is an ancestor of a twice-advanced main tip', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const updateBase = 'c'.repeat(40);
  const currentBase = 'd'.repeat(40);
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  changed.pr.base.sha = currentBase;
  const api = fakeApi([behind, behind, changed.pr]);
  api.readCommit = async (sha) => ({ sha, parents: [{ sha: HEAD }, { sha: updateBase }] });
  api.isCommitAncestor = async (ancestorSha, descendantSha) => ancestorSha === updateBase && descendantSha === currentBase;
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
  assert.equal(result.newHeadSha, changed.pr.head.sha);
});

test('rejects a new-head second parent that is not on the trusted main lineage', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const unrelated = 'c'.repeat(40);
  const currentBase = 'd'.repeat(40);
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  changed.pr.base.sha = currentBase;
  const api = fakeApi([behind, behind, changed.pr]);
  api.readCommit = async (sha) => ({ sha, parents: [{ sha: HEAD }, { sha: unrelated }] });
  api.isCommitAncestor = async () => false;
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'update').length, 1);
});

test('retries a transient new-head commit read and returns confirmed instead of UNKNOWN', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  const api = fakeApi([behind, behind, changed.pr, changed.pr]);
  let reads = 0;
  api.readCommit = async (sha) => {
    reads += 1;
    if (reads === 1) throw new TypeError('transient commit read failure');
    return { sha, parents: [{ sha: HEAD }, { sha: BASE }] };
  };
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
  assert.equal(reads, 2);
});

test('an unrelated concurrent head change cannot confirm update-branch', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const changed = snapshot();
  changed.pr.head.sha = 'e'.repeat(40);
  const api = fakeApi([behind, behind, changed.pr]);
  api.readCommit = async (sha) => ({ sha, parents: [{ sha: 'f'.repeat(40) }] });
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'update').length, 1);
});

test('an accepted but unconfirmed asynchronous update is UNKNOWN and is never repeated', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const api = fakeApi([behind, behind, ...Array.from({ length: 12 }, () => behind.pr)]);
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'update').length, 1);
});

test('source-monitor merge dispatches exact changed Skill roots to provider sync without publication recovery', async () => {
  const merged = sourceMonitorSnapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([sourceMonitorSnapshot(), sourceMonitorSnapshot(), merged.pr]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [
    ['merge', 42, HEAD, 'merge'],
    ['dispatch-provider-sync', 42, HEAD, MERGE, [SOURCE_ROOT]],
  ]);
  assert.deepEqual(result, {
    outcome: 'MERGED_AND_PROVIDER_SYNC_DISPATCHED',
    prNumber: 42,
    headSha: HEAD,
    mergeCommitSha: 'd'.repeat(40),
    classification: 'SOURCE_MONITOR_UPDATE',
  });
});

test('publication dispatch binds exact merged identity and confirms a correlated workflow run', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  let dispatched = false;
  const mergeSha = 'd'.repeat(40);
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    if ((options?.method ?? 'GET') === 'POST') {
      dispatched = true;
      return new Response(null, { status: 204 });
    }
    return Response.json({ workflow_runs: dispatched ? [{
      id: 9001,
      event: 'workflow_dispatch',
      status: 'queued',
      conclusion: null,
      display_title: `Publication submission-pr-42-${HEAD}-${mergeSha}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] : [] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    const result = await api.dispatchPublication(42, HEAD, mergeSha);
    assert.equal(result.outcome, 'PUBLICATION_DISPATCH_CONFIRMED');
    const post = observed.find(({ options }) => options?.method === 'POST');
    assert.deepEqual(JSON.parse(post.options.body), {
      ref: 'main',
      inputs: { pr_number: '42', correlation_id: `submission-pr-42-${HEAD}-${mergeSha}` },
    });
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 1);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('publication reconciliation does not redispatch an existing exact correlation', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  const mergeSha = 'd'.repeat(40);
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    return Response.json({ workflow_runs: [{
      id: 9001,
      event: 'workflow_dispatch',
      status: 'completed',
      conclusion: 'success',
      display_title: `Publication submission-pr-42-${HEAD}-${mergeSha}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    const result = await api.dispatchPublication(42, HEAD, mergeSha);
    assert.equal(result.outcome, 'PUBLICATION_ALREADY_DISPATCHED');
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('publication reconciliation waits on an in-progress run without another effect', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    return Response.json({ workflow_runs: [{
      id: 9001,
      event: 'workflow_dispatch',
      status: 'in_progress',
      conclusion: null,
      display_title: `Publication submission-pr-42-${HEAD}-${MERGE}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    const result = await api.dispatchPublication(42, HEAD, MERGE);
    assert.equal(result.outcome, 'PUBLICATION_IN_PROGRESS');
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('publication reconciliation fails closed on a partial failed run without replaying effects', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    if ((options?.method ?? 'GET') === 'POST') return new Response(null, { status: 201 });
    return Response.json({ workflow_runs: [{
      id: 9001,
      event: 'workflow_dispatch',
      status: 'completed',
      conclusion: 'failure',
      display_title: `Publication submission-pr-42-${HEAD}-${MERGE}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    const result = await api.dispatchPublication(42, HEAD, MERGE);
    assert.equal(result.outcome, 'PUBLICATION_FAILED_REQUIRES_INSPECTION');
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('provider sync dispatch binds canonical source-monitor roots and idempotency key to exact manual slugs', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  let dispatched = false;
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    if ((options?.method ?? 'GET') === 'POST') {
      dispatched = true;
      return new Response(null, { status: 204 });
    }
    return Response.json({ workflow_runs: dispatched ? [{
      id: 9101,
      event: 'workflow_dispatch',
      status: 'queued',
      conclusion: null,
      display_title: `Provider sync source-monitor-pr-42-${HEAD}-${MERGE}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] : [] });
  };
  try {
    const api = new GitHubApi({
      token: 'test-token',
      updateToken: 'test-update-token',
      repository: REPO.full_name,
      currentRunId: 999,
    });
    await api.dispatchProviderSync(42, HEAD, MERGE, [SOURCE_ROOT, 'skills/flat-skill']);
    const post = observed.find(({ options }) => options?.method === 'POST');
    assert.ok(post);
    assert.equal(post.url, 'https://api.github.com/repos/aiskillstore/marketplace/actions/workflows/sync-to-supabase.yml/dispatches');
    assert.deepEqual(JSON.parse(post.options.body), {
      ref: 'main',
      inputs: {
        slugs: 'example/skill flat-skill',
        correlation_id: `source-monitor-pr-42-${HEAD}-${MERGE}`,
        merge_commit_sha: MERGE,
      },
    });
    assert.ok(observed.some(({ url, options }) => (options?.method ?? 'GET') === 'GET'
      && url.includes('/actions/workflows/sync-to-supabase.yml/runs?event=workflow_dispatch')));
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('provider sync reconciliation does not redispatch an existing exact correlation', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    return Response.json({ workflow_runs: [{
      id: 9101,
      event: 'workflow_dispatch',
      status: 'completed',
      conclusion: 'success',
      display_title: `Provider sync source-monitor-pr-42-${HEAD}-${MERGE}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    await api.dispatchProviderSync(42, HEAD, MERGE, [SOURCE_ROOT]);
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('provider sync reconciliation finds an exact correlation on a later bounded page', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    const page = Number(new URL(String(url)).searchParams.get('page'));
    if (page === 1) {
      return Response.json({ workflow_runs: Array.from({ length: 100 }, (_, index) => ({
        display_title: `unrelated-${index}`,
        head_branch: 'main',
        head_repository: { full_name: REPO.full_name },
      })) });
    }
    return Response.json({ workflow_runs: [{
      id: 9101,
      event: 'workflow_dispatch',
      status: 'completed',
      conclusion: 'success',
      display_title: `Provider sync source-monitor-pr-42-${HEAD}-${MERGE}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    }] });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    await api.dispatchProviderSync(42, HEAD, MERGE, [SOURCE_ROOT]);
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
    assert.ok(observed.some(({ url }) => new URL(url).searchParams.get('page') === '2'));
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('provider sync reconciliation fails closed after bounded pagination without redispatch', async () => {
  const originalFetch = globalThis.fetch;
  const observed = [];
  globalThis.fetch = async (url, options) => {
    observed.push({ url: String(url), options });
    return Response.json({ workflow_runs: Array.from({ length: 100 }, (_, index) => ({
      display_title: `unrelated-${index}`,
      head_branch: 'main',
      head_repository: { full_name: REPO.full_name },
    })) });
  };
  try {
    const api = new GitHubApi({ token: 'test-token', updateToken: 'test-update-token', repository: REPO.full_name, currentRunId: 999 });
    await assert.rejects(() => api.dispatchProviderSync(42, HEAD, MERGE, [SOURCE_ROOT]), /bounded limit/);
    assert.equal(observed.filter(({ options }) => options?.method === 'POST').length, 0);
    assert.equal(observed.length, 30);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('a rerun reconciles provider sync for an already merged source-monitor PR', async () => {
  const merged = sourceMonitorSnapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [['dispatch-provider-sync', 42, HEAD, MERGE, [SOURCE_ROOT]]]);
  assert.equal(result.outcome, 'PROVIDER_SYNC_DISPATCH_CONFIRMED');
});

test('confirmed source-monitor merge with failed provider sync dispatch is UNKNOWN and is never repeated', async () => {
  const merged = sourceMonitorSnapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([sourceMonitorSnapshot(), sourceMonitorSnapshot(), merged.pr]);
  api.dispatchProviderSync = async (...args) => {
    api.calls.push(['dispatch-provider-sync', ...args]);
    throw new TypeError('dispatch response lost');
  };
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'merge').length, 1);
  assert.equal(api.calls.filter(([kind]) => kind === 'dispatch-provider-sync').length, 1);
  assert.equal(api.calls.filter(([kind]) => kind === 'dispatch-publication').length, 0);
});

test('confirmed merge with failed publication dispatch is UNKNOWN and is never repeated', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([snapshot(), snapshot(), merged.pr]);
  api.dispatchPublication = async (...args) => {
    api.calls.push(['dispatch-publication', ...args]);
    throw new TypeError('dispatch response lost');
  };
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'merge').length, 1);
  assert.equal(api.calls.filter(([kind]) => kind === 'dispatch-publication').length, 1);
});

test('successful merge followed by readback failure is UNKNOWN and is never repeated', async () => {
  const api = fakeApi([snapshot(), snapshot(), new TypeError('readback lost')]);
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'merge').length, 1);
});

test('does not repeat an unknown merge effect and only trusts merged readback', async () => {
  const api = fakeApi([snapshot(), snapshot(), snapshot().pr]);
  api.merge = async (...args) => {
    api.calls.push(['merge', ...args]);
    throw new TypeError('network lost');
  };
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'merge').length, 1);
});

test('recovery sweep performs at most one effect when it merges a clean submission', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([snapshot(), snapshot(), merged]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: 101, phase: 'OPEN' },
  ];
  const result = await runRecoverySweep(api);
  assert.equal(result.outcome, 'MERGED_AWAITING_PUBLICATION_RECONCILIATION');
  assert.deepEqual(api.calls, [['merge', 42, HEAD, 'merge']]);
});

test('recovery sweep reconciles a marker-bound merged submission without historical workflow metadata', async () => {
  const api = fakeApi([]);
  api.listRecoveryCandidates = async () => [{
    prNumber: 42,
    headSha: HEAD,
    mergeCommitSha: 'd'.repeat(40),
    workflowRunId: null,
    phase: 'MERGED',
    postMergeAction: 'publication',
    roots: [ROOT],
  }];
  const result = await runRecoverySweep(api);
  assert.equal(result.outcome, 'PUBLICATION_DISPATCH_CONFIRMED');
  assert.deepEqual(api.calls, [['dispatch-publication', 42, HEAD, 'd'.repeat(40)]]);
});

test('recovery sweep skips ineligible historical PRs and performs only the first eligible effect', async () => {
  const unsafe = snapshot();
  unsafe.files.push({ filename: 'scripts/injected.mjs', status: 'added', sha: '9'.repeat(40) });
  unsafe.pr.changed_files = unsafe.files.length;
  const behind = snapshot();
  behind.pr.number = 43;
  behind.workflowRun.pull_requests = [{ number: 43 }];
  behind.pr.mergeable_state = 'behind';
  const changed = structuredClone(behind);
  changed.pr.head.sha = 'e'.repeat(40);
  const api = fakeApi([unsafe, behind, behind, changed.pr]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: 101 },
    { prNumber: 43, headSha: HEAD, workflowRunId: 102 },
    { prNumber: 44, headSha: HEAD, workflowRunId: 103 },
  ];
  api.readCommit = async (sha) => ({ sha, parents: [{ sha: HEAD }, { sha: BASE }] });
  const result = await runRecoverySweep(api);
  assert.equal(result.outcome, 'UPDATE_CONFIRMED_AWAITING_CI');
  assert.equal(result.prNumber, 43);
  assert.deepEqual(api.calls, [['update', 43, HEAD]]);
});

test('recovery sweep stops at the oldest waiting candidate and never updates a later behind PR', async () => {
  const waiting = snapshot();
  waiting.checks = waiting.checks.filter((check) => check.name !== 'validate');
  const later = snapshot();
  later.pr.number = 43;
  later.workflowRun.pull_requests = [{ number: 43 }];
  later.pr.mergeable_state = 'behind';
  const api = fakeApi([waiting, later, later]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: 101 },
    { prNumber: 43, headSha: HEAD, workflowRunId: 102 },
  ];
  const result = await runRecoverySweep(api);
  assert.match(result.reason, /missing required check validate/);
  assert.equal(result.outcome, 'WAITING_CI');
  assert.deepEqual(api.calls, []);
});

test('recovery sweep reports oldest-candidate CI failure instead of scanning later PRs', async () => {
  const failed = snapshot();
  failed.checks.find((check) => check.name === 'validate').conclusion = 'failure';
  const later = snapshot();
  later.pr.number = 43;
  later.workflowRun.pull_requests = [{ number: 43 }];
  later.pr.mergeable_state = 'behind';
  const api = fakeApi([failed, later, later]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: 101 },
    { prNumber: 43, headSha: HEAD, workflowRunId: 102 },
  ];
  await assert.rejects(() => runRecoverySweep(api), /check validate concluded failure/);
  assert.deepEqual(api.calls, []);
});

test('recovery sweep reports oldest-candidate conflict instead of scanning later PRs', async () => {
  const conflicted = snapshot();
  conflicted.pr.mergeable = false;
  conflicted.pr.mergeable_state = 'dirty';
  const later = snapshot();
  later.pr.number = 43;
  later.workflowRun.pull_requests = [{ number: 43 }];
  later.pr.mergeable_state = 'behind';
  const api = fakeApi([conflicted, later, later]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: 101 },
    { prNumber: 43, headSha: HEAD, workflowRunId: 102 },
  ];
  await assert.rejects(() => runRecoverySweep(api), /PR is not mergeable/);
  assert.deepEqual(api.calls, []);
});

test('recovery sweep stops before later PRs when the oldest trusted seed has no validation run yet', async () => {
  const api = fakeApi([]);
  api.listRecoveryCandidates = async () => [
    { prNumber: 42, headSha: HEAD, workflowRunId: null, phase: 'OPEN' },
    { prNumber: 43, headSha: HEAD, workflowRunId: 102, phase: 'OPEN' },
  ];
  assert.deepEqual(await runRecoverySweep(api), {
    outcome: 'WAITING_CI',
    prNumber: 42,
    headSha: HEAD,
    reason: 'missing exact-head Validate Marketplace run',
  });
  assert.deepEqual(api.calls, []);
});

test('recovery sweep is a no-op when no trusted open candidate is recoverable', async () => {
  const api = fakeApi([]);
  api.listRecoveryCandidates = async () => [];
  assert.deepEqual(await runRecoverySweep(api), { outcome: 'NO_ELIGIBLE_RECOVERY' });
  assert.deepEqual(api.calls, []);
});
