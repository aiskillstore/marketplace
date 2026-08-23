import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  AutoMergeBlockedError,
  AutoMergeUnknownEffectError,
  runAutoMerge,
  validateSnapshot,
} from '../auto-merge-trusted-skill-pr.mjs';

const REPO = { id: 9001, full_name: 'aiskillstore/marketplace', default_branch: 'main' };
const HEAD = 'a'.repeat(40);
const BASE = 'b'.repeat(40);
const ROOT = 'pending/example/skill';

function snapshot(overrides = {}) {
  const value = {
    repository: REPO,
    repositoryRules: [{
      enforcement: 'active',
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
      { name: 'publication-admission', status: 'completed', conclusion: 'success', app: { id: 15368 } },
      { name: 'action-pin-policy', status: 'completed', conclusion: 'success', app: { id: 15368 } },
      { name: 'validate', status: 'completed', conclusion: 'success', app: { id: 15368 } },
    ],
    statuses: [],
    tree: {
      truncated: false,
      entries: [
        { path: `${ROOT}/SKILL.md`, type: 'blob', mode: '100644', sha: '1'.repeat(40) },
        { path: `${ROOT}/skill-report.json`, type: 'blob', mode: '100644', sha: '2'.repeat(40) },
      ],
    },
    basePendingExists: false,
    publishedTargetExists: false,
  };
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
    prNumber: 42,
    headSha: HEAD,
    baseSha: BASE,
    root: ROOT,
  });
});

test('qualifies UPDATE_SKILL and requests only standard update-branch when behind', () => {
  const value = snapshot({ publishedTargetExists: true });
  value.pr.mergeable_state = 'behind';
  assert.equal(validateSnapshot(value).classification, 'UPDATE_SKILL');
  assert.equal(validateSnapshot(value).action, 'update_branch');
});

test('fails closed on identity, provenance, scope, label, state and exact-head drift', () => {
  const cases = [
    [() => { const v = snapshot(); v.pr.user.id = 7; return v; }, /trusted App identity/],
    [() => { const v = snapshot(); v.pr.user.login = 'ai-skill-store'; return v; }, /trusted App identity/],
    [() => { const v = snapshot(); v.pr.head.repo.id = 7; return v; }, /same repository/],
    [() => { const v = snapshot(); v.pr.head.ref = 'skill-source-monitor/x'; return v; }, /submission\//],
    [() => { const v = snapshot(); v.pr.draft = true; return v; }, /open and non-draft/],
    [() => { const v = snapshot(); v.pr.labels = []; return v; }, /pending-review/],
    [() => { const v = snapshot(); v.workflowRun.head_sha = 'c'.repeat(40); return v; }, /exact PR head/],
    [() => { const v = snapshot(); v.files.push({ filename: '.github/workflows/pwn.yml', status: 'added', sha: '3'.repeat(40) }); v.pr.changed_files = 3; return v; }, /one pending Skill root/],
    [() => { const v = snapshot(); v.files[0].status = 'modified'; return v; }, /newly added/],
    [() => { const v = snapshot(); v.basePendingExists = true; return v; }, /pending root already exists/],
  ];
  for (const [build, pattern] of cases) expectBlocked(build(), pattern);
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
    [() => { const v = snapshot(); v.repositoryRules[0].bypass_actors.push({ actor_id: 15368, actor_type: 'Integration' }); return v; }, /must not bypass/],
    [() => { const v = snapshot(); v.repositoryRules[0].rules[1].parameters.strict_required_status_checks_policy = false; return v; }, /strict protected-main/],
  ];
  for (const [build, pattern] of cases) expectBlocked(build(), pattern);
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
    async sleep() {},
    async updateBranch(number, headSha) {
      calls.push(['update', number, headSha]);
      return { message: 'Updating pull request branch.' };
    },
    async merge(number, headSha, method) {
      calls.push(['merge', number, headSha, method]);
      return { merged: true, sha: 'd'.repeat(40), message: 'Pull Request successfully merged' };
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

test('returns a harmless no-op for the duplicate prerequisite event after merge', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.equal(result.outcome, 'ALREADY_MERGED');
  assert.deepEqual(api.calls, []);
});

test('revalidates immediately before exact-head ordinary merge and confirms authoritative readback', async () => {
  const merged = snapshot();
  merged.pr.state = 'closed';
  merged.pr.merged = true;
  merged.pr.merge_commit_sha = 'd'.repeat(40);
  const api = fakeApi([snapshot(), snapshot(), merged]);
  const result = await runAutoMerge(api, { workflowRunId: 123 });
  assert.deepEqual(api.calls, [['merge', 42, HEAD, 'merge']]);
  assert.deepEqual(result, {
    outcome: 'MERGED_CONFIRMED',
    prNumber: 42,
    headSha: HEAD,
    mergeCommitSha: 'd'.repeat(40),
    classification: 'NEW_SKILL',
  });
});

test('update-branch uses expected exact head and stops for a fresh CI run', async () => {
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

test('an accepted but unconfirmed asynchronous update is UNKNOWN and is never repeated', async () => {
  const behind = snapshot();
  behind.pr.mergeable_state = 'behind';
  const api = fakeApi([behind, behind, ...Array.from({ length: 12 }, () => behind.pr)]);
  await assert.rejects(() => runAutoMerge(api, { workflowRunId: 123 }), AutoMergeUnknownEffectError);
  assert.equal(api.calls.filter(([kind]) => kind === 'update').length, 1);
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
