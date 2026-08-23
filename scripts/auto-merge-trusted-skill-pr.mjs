#!/usr/bin/env node
import { pathToFileURL } from 'node:url';

const TRUSTED_REPOSITORY = 'aiskillstore/marketplace';
const TRUSTED_BOT = Object.freeze({ id: 254047988, login: 'ai-skill-store[bot]', type: 'Bot' });
const GITHUB_ACTIONS_APP_ID = 15368;
const REQUIRED_CHECKS = Object.freeze(['publication-admission', 'action-pin-policy', 'validate']);
const SHA_RE = /^[0-9a-f]{40}$/;
const SEGMENT_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

export class AutoMergeBlockedError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AutoMergeBlockedError';
  }
}

export class AutoMergeWaitingError extends AutoMergeBlockedError {
  constructor(message) {
    super(message);
    this.name = 'AutoMergeWaitingError';
  }
}

export class AutoMergeUnknownEffectError extends Error {
  constructor(message) {
    super(message);
    this.name = 'AutoMergeUnknownEffectError';
  }
}

class GitHubApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = 'GitHubApiError';
    this.status = status;
    this.body = body;
  }
}

function block(condition, message) {
  if (!condition) throw new AutoMergeBlockedError(message);
}

function validSha(value) {
  return typeof value === 'string' && SHA_RE.test(value);
}

function sameRepository(candidate, repository) {
  return candidate?.id === repository.id && candidate?.full_name === repository.full_name;
}

function safePath(path) {
  if (typeof path !== 'string' || path.length === 0 || path.startsWith('/') || path.includes('\\')) return false;
  if (/[\u0000-\u001f\u007f]/u.test(path)) return false;
  const parts = path.split('/');
  return parts.every((part) => part.length > 0 && part !== '.' && part !== '..');
}

function rootForPath(path) {
  if (!safePath(path)) return null;
  const parts = path.split('/');
  if (parts.length < 4 || parts[0] !== 'pending') return null;
  if (!SEGMENT_RE.test(parts[1]) || !SEGMENT_RE.test(parts[2])) return null;
  return parts.slice(0, 3).join('/');
}

function checkTerminal(check) {
  const name = check?.name;
  block(typeof name === 'string' && name.length > 0, 'observed check has no name');
  if (check.status !== 'completed' || check.conclusion == null) {
    throw new AutoMergeWaitingError(`check ${name} is ${check.status ?? 'missing'}`);
  }
  block(check.conclusion === 'success', `check ${name} concluded ${check.conclusion}`);
}

export function validateSnapshot(snapshot) {
  block(snapshot && typeof snapshot === 'object', 'snapshot must be an object');
  const { repository, workflowRun, pr, files, checks, statuses, tree } = snapshot;
  block(repository?.full_name === TRUSTED_REPOSITORY, `repository must be ${TRUSTED_REPOSITORY}`);
  block(Number.isSafeInteger(repository.id), 'repository id is required');
  block(repository.default_branch === 'main', 'default branch must be main');
  block(Array.isArray(snapshot.repositoryRules), 'repository ruleset evidence is required');
  const publicationBoundary = snapshot.repositoryRules.find((ruleset) =>
    ruleset?.enforcement === 'active'
    && ruleset?.conditions?.ref_name?.include?.includes('refs/heads/main')
    && ruleset?.rules?.some((rule) => rule.type === 'pull_request')
    && ruleset?.rules?.some((rule) =>
      rule.type === 'required_status_checks'
      && rule.parameters?.strict_required_status_checks_policy === true
      && rule.parameters?.required_status_checks?.some((check) =>
        check.context === 'publication-admission' && check.integration_id === GITHUB_ACTIONS_APP_ID)))
  ;
  block(publicationBoundary, 'strict protected-main publication ruleset is missing');
  block(!(publicationBoundary.bypass_actors ?? []).some((actor) =>
    actor.actor_type === 'Integration' && actor.actor_id === GITHUB_ACTIONS_APP_ID),
  'GitHub Actions must not bypass the protected-main ruleset');

  block(workflowRun?.event === 'pull_request', 'trigger must be a pull_request workflow run');
  block(workflowRun?.name === 'Validate Marketplace', 'unexpected workflow run');
  block(workflowRun?.status === 'completed', 'workflow run is not completed');
  block(workflowRun?.conclusion === 'success', `workflow run concluded ${workflowRun?.conclusion ?? 'unknown'}`);
  block(Array.isArray(workflowRun.pull_requests) && workflowRun.pull_requests.length === 1, 'workflow run must bind exactly one PR');

  block(pr?.number === workflowRun.pull_requests[0]?.number, 'workflow run PR number does not match');
  block(pr.state === 'open' && pr.draft === false && pr.merged !== true, 'PR must be open and non-draft');
  block(pr.base?.ref === 'main', 'PR base must be main');
  block(sameRepository(pr.base?.repo, repository) && sameRepository(pr.head?.repo, repository), 'PR head and base must use the same repository');
  block(pr.user?.id === TRUSTED_BOT.id && pr.user?.login === TRUSTED_BOT.login && pr.user?.type === TRUSTED_BOT.type, 'PR author is not the trusted App identity');
  block(typeof pr.head?.ref === 'string' && pr.head.ref.startsWith('submission/'), 'PR head must use trusted submission/ provenance');
  block(validSha(pr.head?.sha) && validSha(pr.base?.sha), 'PR head and base SHA must be exact');
  block(workflowRun.head_sha === pr.head.sha, 'workflow run must bind the exact PR head');
  block(Array.isArray(pr.labels) && pr.labels.some((label) => label?.name === 'pending-review'), 'PR must have pending-review');
  block(pr.mergeable === true, 'PR is not mergeable');
  block(['clean', 'behind'].includes(pr.mergeable_state), `PR mergeable_state is ${pr.mergeable_state ?? 'unknown'}`);

  block(Array.isArray(files) && files.length > 0, 'PR files are required');
  block(Number.isSafeInteger(pr.changed_files) && pr.changed_files === files.length, 'PR file pagination/count is incomplete');
  const seenFiles = new Set();
  const roots = new Set();
  for (const file of files) {
    block(file?.status === 'added' && file.previous_filename == null, `every Skill file must be newly added: ${file?.filename ?? '<unknown>'}`);
    block(safePath(file.filename), 'PR contains an unsafe path');
    block(!seenFiles.has(file.filename), `duplicate PR file ${file.filename}`);
    seenFiles.add(file.filename);
    const root = rootForPath(file.filename);
    block(root !== null, 'PR must change only one pending Skill root');
    roots.add(root);
  }
  block(roots.size === 1, 'PR must change only one pending Skill root');
  const [root] = roots;
  block(seenFiles.has(`${root}/SKILL.md`), 'Skill root is missing SKILL.md');
  block(seenFiles.has(`${root}/skill-report.json`), 'Skill root is missing skill-report.json');
  block(snapshot.basePendingExists === false, 'pending root already exists on the base');

  block(tree?.truncated === false && Array.isArray(tree.entries), 'exact-head tree is truncated or missing');
  const treeFiles = new Set();
  for (const entry of tree.entries) {
    if (typeof entry?.path !== 'string' || (entry.path !== root && !entry.path.startsWith(`${root}/`))) continue;
    if (entry.path === root && entry.type === 'tree') continue;
    if (entry.type === 'tree') continue;
    block(entry.type === 'blob' && ['100644', '100755'].includes(entry.mode), 'Skill tree must contain ordinary blobs only');
    treeFiles.add(entry.path);
  }
  block(treeFiles.size === seenFiles.size && [...seenFiles].every((path) => treeFiles.has(path)), 'PR files do not equal the exact-head Skill tree');

  block(Array.isArray(checks) && checks.length > 0, 'exact-head checks are required');
  const checkNames = new Set();
  for (const check of checks) {
    block(check?.app?.id === GITHUB_ACTIONS_APP_ID, `check ${check?.name ?? '<unknown>'} is not from GitHub Actions`);
    block(!checkNames.has(check?.name), `duplicate check ${check?.name ?? '<unknown>'}`);
    checkNames.add(check.name);
    checkTerminal(check);
  }
  for (const required of REQUIRED_CHECKS) {
    if (!checkNames.has(required)) throw new AutoMergeWaitingError(`missing required check ${required}`);
  }
  block(Array.isArray(statuses), 'exact-head statuses are required');
  const statusNames = new Set();
  for (const status of statuses) {
    block(typeof status?.context === 'string' && !statusNames.has(status.context), `duplicate status ${status?.context ?? '<unknown>'}`);
    statusNames.add(status.context);
    if (status.state === 'pending') throw new AutoMergeWaitingError(`status ${status.context} is pending`);
    block(status.state === 'success', `status ${status.context} is ${status.state ?? 'unknown'}`);
  }

  return {
    eligible: true,
    action: pr.mergeable_state === 'behind' ? 'update_branch' : 'merge',
    classification: snapshot.publishedTargetExists === true ? 'UPDATE_SKILL' : 'NEW_SKILL',
    prNumber: pr.number,
    headSha: pr.head.sha,
    baseSha: pr.base.sha,
    root,
  };
}

function samePlan(first, second) {
  return first.prNumber === second.prNumber && first.headSha === second.headSha && first.baseSha === second.baseSha && first.root === second.root && first.classification === second.classification && first.action === second.action;
}

function mergedReadback(pr, plan) {
  return pr?.merged === true && pr.state === 'closed' && pr.head?.sha === plan.headSha && validSha(pr.merge_commit_sha);
}

function definiteMutationRejection(error) {
  return error instanceof GitHubApiError && [405, 409, 422].includes(error.status);
}

export async function runAutoMerge(api, { workflowRunId }) {
  const firstSnapshot = await api.buildSnapshot(workflowRunId);
  if (firstSnapshot?.pr?.merged === true && firstSnapshot.pr.state === 'closed' && firstSnapshot.pr.head?.sha === firstSnapshot.workflowRun?.head_sha) {
    return { outcome: 'ALREADY_MERGED', prNumber: firstSnapshot.pr.number, headSha: firstSnapshot.pr.head.sha, mergeCommitSha: firstSnapshot.pr.merge_commit_sha };
  }
  const first = validateSnapshot(firstSnapshot);
  const secondSnapshot = await api.buildSnapshot(workflowRunId);
  const second = validateSnapshot(secondSnapshot);
  block(samePlan(first, second), 'candidate changed during pre-effect revalidation');

  if (second.action === 'update_branch') {
    let mutationError;
    try {
      await api.updateBranch(second.prNumber, second.headSha);
    } catch (error) {
      mutationError = error;
    }
    let changedHead;
    try {
      for (let attempt = 0; attempt < 12; attempt += 1) {
        const pr = await api.readPr(second.prNumber);
        if (validSha(pr?.head?.sha) && pr.head.sha !== second.headSha) {
          changedHead = pr.head.sha;
          break;
        }
        if (attempt < 11) await api.sleep(5_000);
      }
    } catch {
      throw new AutoMergeUnknownEffectError(`update-branch effect is unknown for PR #${second.prNumber}`);
    }
    if (changedHead) {
      return { outcome: 'UPDATE_CONFIRMED_AWAITING_CI', prNumber: second.prNumber, oldHeadSha: second.headSha, newHeadSha: changedHead, classification: second.classification };
    }
    if (mutationError && definiteMutationRejection(mutationError)) throw new AutoMergeBlockedError(`update-branch rejected with HTTP ${mutationError.status}`);
    throw new AutoMergeUnknownEffectError(`update-branch effect is unknown for PR #${second.prNumber}`);
  }

  let mutationError;
  try {
    await api.merge(second.prNumber, second.headSha, 'merge');
  } catch (error) {
    mutationError = error;
  }
  let readback;
  try {
    readback = await api.readPr(second.prNumber);
  } catch {
    throw new AutoMergeUnknownEffectError(`merge effect is unknown for PR #${second.prNumber}`);
  }
  if (mergedReadback(readback, second)) {
    return { outcome: 'MERGED_CONFIRMED', prNumber: second.prNumber, headSha: second.headSha, mergeCommitSha: readback.merge_commit_sha, classification: second.classification };
  }
  if (mutationError && definiteMutationRejection(mutationError)) throw new AutoMergeBlockedError(`merge rejected with HTTP ${mutationError.status}`);
  throw new AutoMergeUnknownEffectError(`merge effect is unknown for PR #${second.prNumber}`);
}

function encodeContentPath(path) {
  return path.split('/').map(encodeURIComponent).join('/');
}

export class GitHubApi {
  constructor({ token, repository, currentRunId }) {
    block(typeof token === 'string' && token.length > 0, 'GH_TOKEN is required');
    block(repository === TRUSTED_REPOSITORY, `GITHUB_REPOSITORY must be ${TRUSTED_REPOSITORY}`);
    block(Number.isSafeInteger(Number(currentRunId)) && Number(currentRunId) > 0, 'GITHUB_RUN_ID is invalid');
    this.token = token;
    this.repository = repository;
    this.currentRunId = Number(currentRunId);
    this.baseUrl = `https://api.github.com/repos/${repository}`;
  }

  async request(path, { method = 'GET', body } = {}) {
    let response;
    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: {
          Accept: 'application/vnd.github+json',
          Authorization: `Bearer ${this.token}`,
          'X-GitHub-Api-Version': '2022-11-28',
          'User-Agent': 'skillstore-trusted-auto-merge',
        },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        signal: AbortSignal.timeout(20_000),
      });
    } catch (error) {
      throw error;
    }
    const text = await response.text();
    const parsed = text.length === 0 ? null : JSON.parse(text);
    if (!response.ok) throw new GitHubApiError(`GitHub API ${method} ${path} returned ${response.status}`, response.status, parsed);
    return parsed;
  }

  async paginate(path, extract = (value) => value) {
    const all = [];
    for (let page = 1; page <= 30; page += 1) {
      const separator = path.includes('?') ? '&' : '?';
      const value = await this.request(`${path}${separator}per_page=100&page=${page}`);
      const items = extract(value);
      block(Array.isArray(items), `paginated GitHub response is invalid for ${path}`);
      all.push(...items);
      if (items.length < 100) return all;
    }
    throw new AutoMergeBlockedError(`GitHub pagination exceeded the bounded limit for ${path}`);
  }

  async sleep(milliseconds) {
    await new Promise((resolve) => setTimeout(resolve, milliseconds));
  }

  async readPr(number) {
    return this.request(`/pulls/${number}`);
  }

  async existsAt(path, ref) {
    try {
      await this.request(`/contents/${encodeContentPath(path)}?ref=${encodeURIComponent(ref)}`);
      return true;
    } catch (error) {
      if (error instanceof GitHubApiError && error.status === 404) return false;
      throw error;
    }
  }

  async buildSnapshot(workflowRunId) {
    block(Number.isSafeInteger(Number(workflowRunId)) && Number(workflowRunId) > 0, 'WORKFLOW_RUN_ID is invalid');
    const repository = await this.request('');
    const rulesetSummaries = await this.paginate('/rulesets');
    const repositoryRules = await Promise.all(rulesetSummaries.map((ruleset) => this.request(`/rulesets/${ruleset.id}`)));
    const workflowRun = await this.request(`/actions/runs/${Number(workflowRunId)}`);
    block(workflowRun.event === 'pull_request' && validSha(workflowRun.head_sha), 'workflow run is not bound to an exact pull_request head');
    const associatedPrs = await this.paginate(`/commits/${workflowRun.head_sha}/pulls`);
    const exactAssociatedPrs = associatedPrs.filter((candidate) =>
      candidate?.head?.sha === workflowRun.head_sha
      && candidate?.base?.ref === 'main'
      && candidate?.base?.repo?.full_name === this.repository
      && candidate?.head?.repo?.full_name === this.repository);
    const payloadNumbers = (workflowRun.pull_requests ?? []).map((candidate) => candidate.number).filter(Number.isSafeInteger);
    const candidateNumbers = [...new Set([...exactAssociatedPrs.map((candidate) => candidate.number), ...payloadNumbers])];
    block(candidateNumbers.length === 1, 'workflow run must resolve exactly one PR from the exact head');
    const pr = await this.request(`/pulls/${candidateNumbers[0]}`);
    const headSha = pr.head?.sha;
    block(validSha(headSha) && headSha === workflowRun.head_sha, 'PR head does not match the workflow run');
    const files = await this.paginate(`/pulls/${pr.number}/files`);
    const currentRun = await this.request(`/actions/runs/${this.currentRunId}`);
    const checks = (await this.paginate(`/commits/${headSha}/check-runs?filter=latest`, (value) => value?.check_runs))
      .filter((check) => check.check_suite?.id !== currentRun.check_suite_id && !(check.name === 'auto-merge' && check.app?.id === GITHUB_ACTIONS_APP_ID));
    const statuses = await this.paginate(`/commits/${headSha}/statuses`);
    const tree = await this.request(`/git/trees/${headSha}?recursive=1`);
    const roots = new Set(files.map((file) => rootForPath(file.filename)).filter(Boolean));
    const root = roots.size === 1 ? [...roots][0] : 'pending/invalid/invalid';
    const published = `skills/${root.slice('pending/'.length)}`;
    const baseSha = pr.base?.sha;
    block(validSha(baseSha), 'PR base SHA is invalid');
    const [basePendingExists, publishedTargetExists] = await Promise.all([
      this.existsAt(root, baseSha),
      this.existsAt(published, baseSha),
    ]);
    return {
      repository: { id: repository.id, full_name: repository.full_name, default_branch: repository.default_branch },
      repositoryRules,
      workflowRun: {
        id: workflowRun.id,
        name: workflowRun.name,
        event: workflowRun.event,
        status: workflowRun.status,
        conclusion: workflowRun.conclusion,
        head_sha: workflowRun.head_sha,
        pull_requests: [{ number: pr.number }],
      },
      pr: {
        number: pr.number,
        state: pr.state,
        draft: pr.draft,
        merged: pr.merged,
        merge_commit_sha: pr.merge_commit_sha,
        changed_files: pr.changed_files,
        mergeable: pr.mergeable,
        mergeable_state: pr.mergeable_state,
        user: { id: pr.user?.id, login: pr.user?.login, type: pr.user?.type },
        labels: (pr.labels ?? []).map((label) => ({ name: label.name })),
        base: { ref: pr.base?.ref, sha: pr.base?.sha, repo: { id: pr.base?.repo?.id, full_name: pr.base?.repo?.full_name } },
        head: { ref: pr.head?.ref, sha: pr.head?.sha, repo: { id: pr.head?.repo?.id, full_name: pr.head?.repo?.full_name } },
      },
      files: files.map((file) => ({ filename: file.filename, status: file.status, sha: file.sha, ...(file.previous_filename ? { previous_filename: file.previous_filename } : {}) })),
      checks: checks.map((check) => ({ name: check.name, status: check.status, conclusion: check.conclusion, app: { id: check.app?.id } })),
      statuses: statuses.map((status) => ({ context: status.context, state: status.state })),
      tree: { truncated: tree.truncated, entries: (tree.tree ?? []).map((entry) => ({ path: entry.path, type: entry.type, mode: entry.mode, sha: entry.sha })) },
      basePendingExists,
      publishedTargetExists,
    };
  }

  async updateBranch(number, headSha) {
    return this.request(`/pulls/${number}/update-branch`, { method: 'PUT', body: { expected_head_sha: headSha } });
  }

  async merge(number, headSha, method) {
    return this.request(`/pulls/${number}/merge`, { method: 'PUT', body: { sha: headSha, merge_method: method } });
  }
}

async function main() {
  const api = new GitHubApi({ token: process.env.GH_TOKEN, repository: process.env.GITHUB_REPOSITORY, currentRunId: process.env.GITHUB_RUN_ID });
  try {
    const result = await runAutoMerge(api, { workflowRunId: Number(process.env.WORKFLOW_RUN_ID) });
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    if (error instanceof AutoMergeWaitingError) {
      process.stdout.write(`${JSON.stringify({ outcome: 'WAITING_CI', reason: error.message })}\n`);
      return;
    }
    const kind = error instanceof AutoMergeUnknownEffectError ? 'UNKNOWN_EFFECT' : 'BLOCKED';
    process.stderr.write(`::error title=Trusted Skill auto-merge ${kind}::${error.message}\n`);
    process.exitCode = 1;
  }
}

const invokedPath = process.argv[1] ? pathToFileURL(process.argv[1]).href : '';
if (import.meta.url === invokedPath) await main();
