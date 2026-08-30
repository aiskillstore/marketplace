#!/usr/bin/env node
import { pathToFileURL } from 'node:url';

const TRUSTED_REPOSITORY = 'aiskillstore/marketplace';
const TRUSTED_BOT = Object.freeze({ id: 254047988, login: 'ai-skill-store[bot]', type: 'Bot' });
const GITHUB_ACTIONS_APP_ID = 15368;
const TRUSTED_WORKFLOWS = Object.freeze({
  'publication-admission': { id: 330383167, name: 'Publication Provenance', path: '.github/workflows/publication-provenance.yml' },
  'action-pin-policy': { id: 219313535, name: 'Validate Marketplace', path: '.github/workflows/validate-marketplace.yml' },
  validate: { id: 219313535, name: 'Validate Marketplace', path: '.github/workflows/validate-marketplace.yml' },
});
const REQUIRED_CHECKS = Object.freeze(Object.keys(TRUSTED_WORKFLOWS));
const SHA_RE = /^[0-9a-f]{40}$/;
const SEGMENT_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
const SOURCE_MONITOR_REF_RE = /^skill-source-monitor\/run-[1-9][0-9]*$/u;
const SUBMISSION_ROUTE = 'submission';
const SOURCE_MONITOR_ROUTE = 'source_monitor';
const RECOVERY_MARKER_EPOCH = '2026-08-30T00:00:00Z';

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

export class AutoMergeSkippedError extends AutoMergeBlockedError {
  constructor(message) {
    super(message);
    this.name = 'AutoMergeSkippedError';
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

function skip(condition, message) {
  if (!condition) throw new AutoMergeSkippedError(message);
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

function rootForPath(path, topLevel = 'pending') {
  if (!safePath(path)) return null;
  const parts = path.split('/');
  if (parts.length < 4 || parts[0] !== topLevel) return null;
  if (!SEGMENT_RE.test(parts[1]) || !SEGMENT_RE.test(parts[2])) return null;
  return parts.slice(0, 3).join('/');
}

function publishedRootSyntax(root) {
  if (!safePath(root)) return false;
  const parts = root.split('/');
  return parts[0] === 'skills'
    && [2, 3].includes(parts.length)
    && parts.slice(1).every((part) => SEGMENT_RE.test(part));
}

function publishedRootsFromTree(tree) {
  const blobs = new Set((tree?.entries ?? [])
    .filter((entry) => entry?.type === 'blob' && typeof entry.path === 'string')
    .map((entry) => entry.path));
  const roots = new Set();
  for (const path of blobs) {
    if (!path.endsWith('/skill-report.json')) continue;
    const root = path.slice(0, -'/skill-report.json'.length);
    if (publishedRootSyntax(root) && blobs.has(`${root}/SKILL.md`)) roots.add(root);
  }
  return [...roots].sort();
}

function publishedRootForPath(path, candidates) {
  if (!safePath(path) || !Array.isArray(candidates)) return null;
  const matches = candidates
    .filter((root) => path === root || path.startsWith(`${root}/`))
    .sort((first, second) => second.length - first.length);
  return matches[0] ?? null;
}

function routeForPr(pr) {
  const ref = pr?.head?.ref;
  if (typeof ref === 'string' && ref.startsWith('submission/')) return SUBMISSION_ROUTE;
  if (typeof ref === 'string' && ref.startsWith('skill-source-monitor/')) {
    block(SOURCE_MONITOR_REF_RE.test(ref), 'PR head must use trusted source-monitor provenance');
    return SOURCE_MONITOR_ROUTE;
  }
  throw new AutoMergeSkippedError('PR head must use trusted submission/ or source-monitor provenance');
}

export function latestStatusesByContext(statusHistory) {
  block(Array.isArray(statusHistory), 'status history must be an array');
  const latest = [];
  const seen = new Set();
  for (const status of statusHistory) {
    block(typeof status?.context === 'string' && status.context.length > 0, 'status context is required');
    if (seen.has(status.context)) continue;
    seen.add(status.context);
    latest.push(status);
  }
  return latest;
}

function checkTerminal(check) {
  const name = check?.name;
  block(typeof name === 'string' && name.length > 0, 'observed check has no name');
  if (check.status !== 'completed' || check.conclusion == null) {
    throw new AutoMergeWaitingError(`check ${name} is ${check.status ?? 'missing'}`);
  }
  block(check.conclusion === 'success', `check ${name} concluded ${check.conclusion}`);
}

export function validateSnapshot(snapshot, { allowMerged = false } = {}) {
  block(snapshot && typeof snapshot === 'object', 'snapshot must be an object');
  const { repository, workflowRun, pr, files, checks, statuses, tree } = snapshot;
  block(repository?.full_name === TRUSTED_REPOSITORY, `repository must be ${TRUSTED_REPOSITORY}`);
  block(Number.isSafeInteger(repository.id), 'repository id is required');
  block(repository.default_branch === 'main', 'default branch must be main');
  block(Array.isArray(snapshot.repositoryRules), 'repository ruleset evidence is required');
  const publicationBoundary = snapshot.repositoryRules.find((ruleset) =>
    ruleset?.enforcement === 'active'
    && ruleset?.target === 'branch'
    && Array.isArray(ruleset?.conditions?.ref_name?.exclude)
    && ruleset.conditions.ref_name.exclude.length === 0
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
  if (allowMerged) {
    block(pr.state === 'closed' && pr.merged === true && validSha(pr.merge_commit_sha), 'PR must be authoritatively merged');
  } else {
    skip(pr.state === 'open' && pr.draft === false && pr.merged !== true, 'PR must be open and non-draft');
  }
  skip(pr.base?.ref === 'main', 'PR base must be main');
  skip(sameRepository(pr.base?.repo, repository) && sameRepository(pr.head?.repo, repository), 'PR head and base must use the same repository');
  skip(pr.user?.id === TRUSTED_BOT.id && pr.user?.login === TRUSTED_BOT.login && pr.user?.type === TRUSTED_BOT.type, 'PR author is not the trusted App identity');
  const route = routeForPr(pr);
  block(validSha(pr.head?.sha) && validSha(pr.base?.sha), 'PR head and base SHA must be exact');
  block(workflowRun.head_sha === pr.head.sha, 'workflow run must bind the exact PR head');
  const labelNames = new Set((Array.isArray(pr.labels) ? pr.labels : []).map((label) => label?.name));
  if (route === SUBMISSION_ROUTE) {
    skip(labelNames.has('pending-review'), 'PR must have pending-review');
  } else {
    skip(labelNames.has('skill-source-monitor'), 'source-monitor PR must have skill-source-monitor label');
    skip(!labelNames.has('pending-review'), 'source-monitor PR must not have pending-review');
  }
  if (!allowMerged) {
    block(pr.mergeable === true, 'PR is not mergeable');
    block(['clean', 'behind'].includes(pr.mergeable_state), `PR mergeable_state is ${pr.mergeable_state ?? 'unknown'}`);
  }

  block(Array.isArray(files), 'PR files are required');
  skip(files.length > 0, 'PR files are required');
  block(Number.isSafeInteger(pr.changed_files) && pr.changed_files === files.length, 'PR file pagination/count is incomplete');
  block(tree?.truncated === false && Array.isArray(tree.entries), 'exact-head tree is truncated or missing');
  const seenFiles = new Set();
  const roots = new Set();
  const topLevel = route === SUBMISSION_ROUTE ? 'pending' : 'skills';
  const publishedRootCandidates = route === SOURCE_MONITOR_ROUTE ? publishedRootsFromTree(tree) : [];
  for (const file of files) {
    skip(safePath(file?.filename), 'PR contains an unsafe path');
    skip(!seenFiles.has(file.filename), `duplicate PR file ${file.filename}`);
    seenFiles.add(file.filename);
    if (route === SUBMISSION_ROUTE) {
      skip(file.status === 'added' && file.previous_filename == null, `every Skill file must be newly added: ${file.filename}`);
    } else {
      skip(['added', 'modified', 'removed', 'changed'].includes(file.status) && file.previous_filename == null,
        `unsupported source-monitor file status: ${file.status ?? 'missing'}`);
    }
    const root = route === SUBMISSION_ROUTE
      ? rootForPath(file.filename, topLevel)
      : publishedRootForPath(file.filename, publishedRootCandidates);
    skip(root !== null, `PR must change only ${topLevel === 'pending' ? 'pending' : 'published'} Skill roots`);
    roots.add(root);
  }
  skip(roots.size > 0, `PR must change ${topLevel} Skill roots`);
  const rootList = [...roots].sort();
  if (route === SOURCE_MONITOR_ROUTE) skip(rootList.length <= 25, 'source-monitor PR exceeds the provider sync limit');
  for (const root of rootList) {
    const skillFile = files.find((file) => file.filename === `${root}/SKILL.md`);
    const reportFile = files.find((file) => file.filename === `${root}/skill-report.json`);
    if (route === SUBMISSION_ROUTE) skip(skillFile && skillFile.status !== 'removed', 'Skill root is missing SKILL.md');
    skip(reportFile && reportFile.status !== 'removed', 'Skill root is missing skill-report.json');
  }
  if (route === SUBMISSION_ROUTE) {
    skip(snapshot.basePendingExists === false, 'pending root already exists on the base');
  } else {
    skip(snapshot.baseSkillRootsExist === true, 'source-monitor Skill roots must already exist on the base');
  }

  const treeByPath = new Map();
  for (const entry of tree.entries) {
    if (typeof entry?.path !== 'string' || !rootList.some((root) => entry.path === root || entry.path.startsWith(`${root}/`))) continue;
    if (entry.type === 'tree') continue;
    skip(entry.type === 'blob' && ['100644', '100755'].includes(entry.mode), 'Skill tree must contain ordinary blobs only');
    treeByPath.set(entry.path, entry);
  }
  if (route === SUBMISSION_ROUTE) {
    skip(treeByPath.size === seenFiles.size && [...seenFiles].every((path) => treeByPath.has(path)), 'PR files do not equal the exact-head Skill tree');
  } else {
    for (const file of files) {
      const entry = treeByPath.get(file.filename);
      if (file.status === 'removed') {
        skip(entry == null, `removed source-monitor file remains on the exact PR head: ${file.filename}`);
      } else {
        block(entry?.sha === file.sha && validSha(file.sha), `source-monitor file is not bound to the exact PR head: ${file.filename}`);
      }
    }
    for (const root of rootList) {
      skip(treeByPath.has(`${root}/SKILL.md`) && treeByPath.has(`${root}/skill-report.json`), 'source-monitor Skill root is incomplete on the exact PR head');
    }
  }

  block(Array.isArray(snapshot.reports) && snapshot.reports.length === rootList.length, 'exact-head skill reports are required');
  const reportsByPath = new Map(snapshot.reports.map((report) => [report?.path, report]));
  for (const root of rootList) {
    const reportPath = `${root}/skill-report.json`;
    const reportFile = files.find((file) => file.filename === reportPath);
    const reportTreeEntry = treeByPath.get(reportPath);
    const report = reportsByPath.get(reportPath);
    block(reportFile?.status !== 'removed'
      && report?.path === reportPath
      && validSha(report.sha)
      && report.sha === reportFile?.sha
      && report.sha === reportTreeEntry?.sha,
    'skill report is not bound to the exact PR head');
  }

  block(Array.isArray(checks), 'exact-head checks are required');
  if (checks.length === 0) throw new AutoMergeWaitingError('exact-head checks are required');
  const checkNames = new Set();
  for (const check of checks) {
    block(check?.app?.id === GITHUB_ACTIONS_APP_ID, `check ${check?.name ?? '<unknown>'} is not from GitHub Actions`);
    block(!checkNames.has(check?.name), `duplicate check ${check?.name ?? '<unknown>'}`);
    checkNames.add(check.name);
    checkTerminal(check);
  }
  for (const required of REQUIRED_CHECKS) {
    if (!checkNames.has(required)) throw new AutoMergeWaitingError(`missing required check ${required}`);
    const check = checks.find((candidate) => candidate.name === required);
    const expected = TRUSTED_WORKFLOWS[required];
    block(Number.isSafeInteger(check?.id)
      && Number.isSafeInteger(check?.workflow?.run_id)
      && check.workflow.id === expected.id
      && check.workflow.name === expected.name
      && check.workflow.path === expected.path
      && check.workflow.event === 'pull_request'
      && check.workflow.head_sha === pr.head.sha
      && check.workflow.status === 'completed'
      && check.workflow.conclusion === 'success'
      && (required === 'publication-admission' || check.workflow.run_id === workflowRun.id),
    `check ${required} is not bound to the trusted workflow run`);
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
    classification: route === SOURCE_MONITOR_ROUTE
      ? 'SOURCE_MONITOR_UPDATE'
      : (snapshot.publishedTargetExists === true ? 'UPDATE_SKILL' : 'NEW_SKILL'),
    postMergeAction: route === SOURCE_MONITOR_ROUTE ? 'provider_sync' : 'publication',
    prNumber: pr.number,
    headSha: pr.head.sha,
    baseSha: pr.base.sha,
    root: rootList.join(','),
    roots: rootList,
  };
}

function samePlan(first, second) {
  return first.prNumber === second.prNumber
    && first.headSha === second.headSha
    && first.baseSha === second.baseSha
    && first.root === second.root
    && first.classification === second.classification
    && first.postMergeAction === second.postMergeAction
    && first.action === second.action;
}

function mergedReadback(pr, plan) {
  return pr?.merged === true && pr.state === 'closed' && pr.head?.sha === plan.headSha && validSha(pr.merge_commit_sha);
}

function mergeabilityIsComputing(pr) {
  return pr?.merged !== true && (pr?.mergeable == null || pr?.mergeable_state === 'unknown');
}

async function buildStableSnapshot(api, workflowRunId) {
  let snapshot;
  for (let attempt = 0; attempt < 6; attempt += 1) {
    snapshot = await api.buildSnapshot(workflowRunId);
    if (!mergeabilityIsComputing(snapshot?.pr)) return snapshot;
    if (attempt < 5) await api.sleep(5_000);
  }
  return snapshot;
}

function definiteMutationRejection(error) {
  return error instanceof GitHubApiError && [405, 409, 422].includes(error.status);
}

export async function runAutoMerge(api, { workflowRunId, deferPostMergeDispatch = false }) {
  const firstSnapshot = await buildStableSnapshot(api, workflowRunId);
  if (firstSnapshot?.pr?.merged === true && firstSnapshot.pr.state === 'closed' && firstSnapshot.pr.head?.sha === firstSnapshot.workflowRun?.head_sha) {
    const merged = validateSnapshot(firstSnapshot, { allowMerged: true });
    let dispatchResult;
    try {
      dispatchResult = merged.postMergeAction === 'provider_sync'
        ? await api.dispatchProviderSync(merged.prNumber, merged.headSha, firstSnapshot.pr.merge_commit_sha, merged.roots)
        : await api.dispatchPublication(merged.prNumber, merged.headSha, firstSnapshot.pr.merge_commit_sha);
    } catch (error) {
      if (error instanceof AutoMergeBlockedError || error instanceof AutoMergeUnknownEffectError) throw error;
      const effect = merged.postMergeAction === 'provider_sync' ? 'provider sync' : 'publication';
      throw new AutoMergeUnknownEffectError(`merge is confirmed but ${effect} reconciliation is unknown for PR #${merged.prNumber}`);
    }
    return {
      ...dispatchResult,
      prNumber: merged.prNumber,
      headSha: merged.headSha,
      mergeCommitSha: firstSnapshot.pr.merge_commit_sha,
      classification: merged.classification,
    };
  }
  const first = validateSnapshot(firstSnapshot);
  const secondSnapshot = await buildStableSnapshot(api, workflowRunId);
  const second = validateSnapshot(secondSnapshot);
  block(samePlan(first, second), 'candidate changed during pre-effect revalidation');

  if (second.action === 'update_branch') {
    let mutationError;
    try {
      await api.updateBranch(second.prNumber, second.headSha);
    } catch (error) {
      mutationError = error;
    }
    for (let attempt = 0; attempt < 12; attempt += 1) {
      let pr;
      try {
        pr = await api.readPr(second.prNumber);
      } catch {
        if (attempt < 11) await api.sleep(5_000);
        continue;
      }
      if (validSha(pr?.head?.sha) && pr.head.sha !== second.headSha) {
        let commit;
        try {
          commit = await api.readCommit(pr.head.sha);
        } catch {
          if (attempt < 11) await api.sleep(5_000);
          continue;
        }
        const parentShas = [...new Set((commit?.parents ?? []).map((parent) => parent.sha))];
        const readbackBaseSha = pr.base?.sha;
        const updateBaseParents = parentShas.filter((sha) => sha !== second.headSha);
        if (parentShas.length === 2
          && parentShas.includes(second.headSha)
          && updateBaseParents.length === 1
          && validSha(readbackBaseSha)) {
          let updateBaseIsOnMain;
          try {
            updateBaseIsOnMain = updateBaseParents[0] === readbackBaseSha
              || await api.isCommitAncestor(updateBaseParents[0], readbackBaseSha);
          } catch {
            if (attempt < 11) await api.sleep(5_000);
            continue;
          }
          if (updateBaseIsOnMain) {
            return {
              outcome: 'UPDATE_CONFIRMED_AWAITING_CI',
              prNumber: second.prNumber,
              oldHeadSha: second.headSha,
              newHeadSha: pr.head.sha,
              classification: second.classification,
            };
          }
        }
        throw new AutoMergeUnknownEffectError(`update-branch produced an uncorrelated head for PR #${second.prNumber}`);
      }
      if (attempt < 11) await api.sleep(5_000);
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
    if (deferPostMergeDispatch) {
      return {
        outcome: second.postMergeAction === 'provider_sync'
          ? 'MERGED_AWAITING_PROVIDER_SYNC_RECONCILIATION'
          : 'MERGED_AWAITING_PUBLICATION_RECONCILIATION',
        prNumber: second.prNumber,
        headSha: second.headSha,
        mergeCommitSha: readback.merge_commit_sha,
        classification: second.classification,
      };
    }
    try {
      if (second.postMergeAction === 'provider_sync') {
        await api.dispatchProviderSync(second.prNumber, second.headSha, readback.merge_commit_sha, second.roots);
        return { outcome: 'MERGED_AND_PROVIDER_SYNC_DISPATCHED', prNumber: second.prNumber, headSha: second.headSha, mergeCommitSha: readback.merge_commit_sha, classification: second.classification };
      }
      await api.dispatchPublication(second.prNumber, second.headSha, readback.merge_commit_sha);
      return { outcome: 'MERGED_AND_PUBLICATION_DISPATCHED', prNumber: second.prNumber, headSha: second.headSha, mergeCommitSha: readback.merge_commit_sha, classification: second.classification };
    } catch (error) {
      if (error instanceof AutoMergeBlockedError || error instanceof AutoMergeUnknownEffectError) throw error;
      const effect = second.postMergeAction === 'provider_sync' ? 'provider sync' : 'publication';
      throw new AutoMergeUnknownEffectError(`merge is confirmed but ${effect} dispatch is unknown for PR #${second.prNumber}`);
    }
  }
  if (mutationError && definiteMutationRejection(mutationError)) throw new AutoMergeBlockedError(`merge rejected with HTTP ${mutationError.status}`);
  throw new AutoMergeUnknownEffectError(`merge effect is unknown for PR #${second.prNumber}`);
}

export async function runRecoverySweep(api) {
  const candidates = await api.listRecoveryCandidates();
  for (const candidate of candidates) {
    if (candidate.phase === 'MERGED') {
      const result = candidate.postMergeAction === 'provider_sync'
        ? await api.dispatchProviderSync(candidate.prNumber, candidate.headSha, candidate.mergeCommitSha, candidate.roots)
        : await api.dispatchPublication(candidate.prNumber, candidate.headSha, candidate.mergeCommitSha);
      if (['PUBLICATION_ALREADY_DISPATCHED', 'PROVIDER_SYNC_ALREADY_DISPATCHED'].includes(result.outcome)) continue;
      return {
        ...result,
        prNumber: candidate.prNumber,
        headSha: candidate.headSha,
        mergeCommitSha: candidate.mergeCommitSha,
      };
    }
    if (candidate.workflowRunId == null) {
      return {
        outcome: 'WAITING_CI',
        prNumber: candidate.prNumber,
        headSha: candidate.headSha,
        reason: 'missing exact-head Validate Marketplace run',
      };
    }
    try {
      const result = await runAutoMerge(api, {
        workflowRunId: candidate.workflowRunId,
        deferPostMergeDispatch: true,
      });
      if (['PUBLICATION_ALREADY_DISPATCHED', 'PROVIDER_SYNC_ALREADY_DISPATCHED'].includes(result.outcome)) continue;
      return result;
    } catch (error) {
      if (error instanceof AutoMergeSkippedError) continue;
      if (error instanceof AutoMergeWaitingError) {
        return { outcome: 'WAITING_CI', prNumber: candidate.prNumber, workflowRunId: candidate.workflowRunId, reason: error.message };
      }
      throw error;
    }
  }
  return { outcome: 'NO_ELIGIBLE_RECOVERY' };
}

function encodeContentPath(path) {
  return path.split('/').map(encodeURIComponent).join('/');
}

function trustedRecoverySeed(pr, repository) {
  const labels = new Set((Array.isArray(pr?.labels) ? pr.labels : []).map((label) => label?.name));
  const merged = pr?.state === 'closed' && pr.draft === false
    && typeof pr.merged_at === 'string' && validSha(pr.merge_commit_sha);
  const submission = typeof pr?.head?.ref === 'string'
    && pr.head.ref.startsWith('submission/')
    && (merged || labels.has('pending-review'));
  const sourceMonitor = SOURCE_MONITOR_REF_RE.test(pr?.head?.ref ?? '')
    && (merged || (labels.has('skill-source-monitor') && !labels.has('pending-review')));
  const lifecycle = (pr?.state === 'open' && pr.draft === false && pr.merged_at == null) || merged;
  return lifecycle
    && pr.base?.ref === 'main'
    && sameRepository(pr.base?.repo, repository)
    && sameRepository(pr.head?.repo, repository)
    && pr.user?.id === TRUSTED_BOT.id
    && pr.user?.login === TRUSTED_BOT.login
    && pr.user?.type === TRUSTED_BOT.type
    && validSha(pr.head?.sha)
    && (submission || sourceMonitor);
}

function workflowRunIdFromCheck(check) {
  if (check?.name !== 'validate' || check?.app?.id !== GITHUB_ACTIONS_APP_ID) return null;
  const match = /^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/(\d+)\/job\/\d+(?:\?.*)?$/u.exec(check.details_url ?? '');
  const runId = match ? Number(match[1]) : NaN;
  return Number.isSafeInteger(runId) && runId > 0 ? runId : null;
}

export class GitHubApi {
  constructor({ token, updateToken, repository, currentRunId }) {
    block(typeof token === 'string' && token.length > 0, 'GH_TOKEN is required');
    block(typeof updateToken === 'string' && updateToken.length > 0, 'GH_UPDATE_TOKEN is required');
    block(repository === TRUSTED_REPOSITORY, `GITHUB_REPOSITORY must be ${TRUSTED_REPOSITORY}`);
    block(Number.isSafeInteger(Number(currentRunId)) && Number(currentRunId) > 0, 'GITHUB_RUN_ID is invalid');
    this.token = token;
    this.updateToken = updateToken;
    this.repository = repository;
    this.currentRunId = Number(currentRunId);
    this.baseUrl = `https://api.github.com/repos/${repository}`;
  }

  async request(path, { method = 'GET', body, token = this.token } = {}) {
    let response;
    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: {
          Accept: 'application/vnd.github+json',
          Authorization: `Bearer ${token}`,
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

  async readCommit(sha) {
    return this.request(`/commits/${sha}`);
  }

  async isCommitAncestor(ancestorSha, descendantSha) {
    block(validSha(ancestorSha) && validSha(descendantSha), 'commit lineage requires exact SHAs');
    const comparison = await this.request(`/compare/${ancestorSha}...${descendantSha}`);
    return comparison?.base_commit?.sha === ancestorSha
      && comparison?.merge_base_commit?.sha === ancestorSha
      && ['ahead', 'identical'].includes(comparison?.status);
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

  async listRecoveryCandidates() {
    const repository = await this.request('');
    block(repository?.full_name === TRUSTED_REPOSITORY && Number.isSafeInteger(repository.id), 'trusted repository evidence is unavailable');
    const openPulls = await this.paginate('/pulls?state=open&base=main&sort=created&direction=asc');
    const closedPulls = [];
    for (let page = 1; page <= 30; page += 1) {
      const items = await this.request(`/pulls?state=closed&base=main&sort=updated&direction=desc&per_page=100&page=${page}`);
      block(Array.isArray(items), 'merged PR recovery evidence is unavailable');
      closedPulls.push(...items.filter((pr) => String(pr?.merged_at ?? '') >= RECOVERY_MARKER_EPOCH));
      const reachedEpoch = items.length < 100
        || items.every((pr) => String(pr?.updated_at ?? '') < RECOVERY_MARKER_EPOCH);
      if (reachedEpoch) break;
      if (page === 30) throw new AutoMergeBlockedError('merged PR recovery search exceeded the bounded marker epoch');
    }

    const seeds = [];
    for (const pr of closedPulls) {
      if (!trustedRecoverySeed(pr, repository) || pr.state !== 'closed') continue;
      const mergeCommit = await this.readCommit(pr.merge_commit_sha);
      const marker = `Trusted auto-merge PR #${pr.number}\n\nAgentCrew-Recovery: ${pr.number}:${pr.head.sha}`;
      if (mergeCommit?.commit?.message !== marker) continue;
      const sourceMonitor = SOURCE_MONITOR_REF_RE.test(pr.head?.ref ?? '');
      let roots = [];
      if (sourceMonitor) {
        const [files, tree] = await Promise.all([
          this.paginate(`/pulls/${pr.number}/files`),
          this.request(`/git/trees/${pr.head.sha}?recursive=1`),
        ]);
        block(tree?.truncated === false && Array.isArray(tree.tree), `merged source-monitor PR #${pr.number} has no exact tree evidence`);
        const candidates = publishedRootsFromTree({ entries: tree.tree });
        roots = [...new Set(files.map((file) => publishedRootForPath(file.filename, candidates)).filter(Boolean))].sort();
        block(roots.length > 0 && roots.length <= 25, `merged source-monitor PR #${pr.number} has invalid sync roots`);
      }
      seeds.push({
        pr,
        phase: 'MERGED',
        mergeCommitSha: pr.merge_commit_sha,
        postMergeAction: sourceMonitor ? 'provider_sync' : 'publication',
        roots,
      });
    }
    for (const pr of openPulls) {
      if (trustedRecoverySeed(pr, repository) && pr.state === 'open') seeds.push({ pr, phase: 'OPEN' });
    }
    seeds.sort((left, right) => String(left.pr.created_at).localeCompare(String(right.pr.created_at)) || left.pr.number - right.pr.number);

    const candidates = [];
    for (const seed of seeds) {
      const { pr } = seed;
      let workflowRunId = null;
      if (seed.phase === 'OPEN') {
        const checks = await this.paginate(`/commits/${pr.head.sha}/check-runs?filter=latest`, (value) => value?.check_runs);
        const runIds = [...new Set(checks.map(workflowRunIdFromCheck).filter(Number.isSafeInteger))];
        block(runIds.length <= 1, `PR #${pr.number} has ambiguous exact-head validation runs`);
        workflowRunId = runIds[0] ?? null;
      }
      candidates.push({
        prNumber: pr.number,
        headSha: pr.head.sha,
        workflowRunId,
        phase: seed.phase,
        ...(seed.phase === 'MERGED' ? {
          mergeCommitSha: seed.mergeCommitSha,
          postMergeAction: seed.postMergeAction,
          roots: seed.roots,
        } : {}),
      });
    }
    return candidates;
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
    const rawChecks = (await this.paginate(`/commits/${headSha}/check-runs?filter=latest`, (value) => value?.check_runs))
      .filter((check) => check.check_suite?.id !== currentRun.check_suite_id && !(check.name === 'auto-merge' && check.app?.id === GITHUB_ACTIONS_APP_ID));
    const trustedCheckRefs = new Map();
    for (const check of rawChecks) {
      if (!REQUIRED_CHECKS.includes(check.name)) continue;
      const match = /^https:\/\/github\.com\/aiskillstore\/marketplace\/actions\/runs\/(\d+)\/job\/(\d+)(?:\?.*)?$/u.exec(check.details_url ?? '');
      block(match, `check ${check.name} has no trusted workflow-run URL`);
      trustedCheckRefs.set(check.name, { runId: Number(match[1]), jobId: Number(match[2]), checkId: check.id });
    }
    const uniqueRunIds = [...new Set([...trustedCheckRefs.values()].map((ref) => ref.runId))];
    const uniqueJobIds = [...new Set([...trustedCheckRefs.values()].map((ref) => ref.jobId))];
    const trustedRuns = new Map(await Promise.all(uniqueRunIds.map(async (runId) => [runId, await this.request(`/actions/runs/${runId}`)])));
    const trustedJobs = new Map(await Promise.all(uniqueJobIds.map(async (jobId) => [jobId, await this.request(`/actions/jobs/${jobId}`)])));
    for (const ref of trustedCheckRefs.values()) {
      const job = trustedJobs.get(ref.jobId);
      block(job?.run_id === ref.runId
        && job?.check_run_url === `https://api.github.com/repos/${this.repository}/check-runs/${ref.checkId}`,
      'required check is not bound to its GitHub Actions job');
    }
    const uniqueWorkflowIds = [...new Set([...trustedRuns.values()].map((run) => run.workflow_id))];
    const trustedWorkflowDefinitions = new Map(await Promise.all(uniqueWorkflowIds.map(async (workflowId) => [workflowId, await this.request(`/actions/workflows/${workflowId}`)])));
    const checks = rawChecks.map((check) => {
      const ref = trustedCheckRefs.get(check.name);
      if (!ref) return check;
      const run = trustedRuns.get(ref.runId);
      const definition = trustedWorkflowDefinitions.get(run.workflow_id);
      return {
        ...check,
        workflow: {
          run_id: run.id,
          id: run.workflow_id,
          name: run.name,
          path: definition.path,
          event: run.event,
          head_sha: run.head_sha,
          status: run.status,
          conclusion: run.conclusion,
        },
      };
    });
    const statusHistory = await this.paginate(`/commits/${headSha}/statuses`);
    const latestStatuses = latestStatusesByContext(statusHistory);
    const tree = await this.request(`/git/trees/${headSha}?recursive=1`);
    const topLevel = SOURCE_MONITOR_REF_RE.test(pr.head?.ref ?? '') ? 'skills' : 'pending';
    const publishedRootCandidates = topLevel === 'skills' ? publishedRootsFromTree({ entries: tree.tree ?? [] }) : [];
    const roots = [...new Set(files.map((file) => topLevel === 'pending'
      ? rootForPath(file.filename, topLevel)
      : publishedRootForPath(file.filename, publishedRootCandidates)).filter(Boolean))].sort();
    const reports = await Promise.all(roots.map(async (root) => {
      const reportPath = `${root}/skill-report.json`;
      const reportBlob = await this.request(`/contents/${encodeContentPath(reportPath)}?ref=${encodeURIComponent(headSha)}`);
      block(reportBlob?.type === 'file' && validSha(reportBlob.sha),
        `exact-head skill report is unavailable: ${reportPath}`);
      return { path: reportPath, sha: reportBlob.sha };
    }));
    const baseSha = pr.base?.sha;
    block(validSha(baseSha), 'PR base SHA is invalid');
    const baseRootEvidence = await Promise.all(roots.map((root) => this.existsAt(root, baseSha)));
    const publishedEvidence = topLevel === 'pending'
      ? await Promise.all(roots.map((root) => this.existsAt(`skills/${root.slice('pending/'.length)}`, baseSha)))
      : baseRootEvidence;
    const basePendingExists = topLevel === 'pending' && baseRootEvidence.some(Boolean);
    const baseSkillRootsExist = topLevel === 'skills' && roots.length > 0 && baseRootEvidence.every(Boolean);
    const publishedTargetExists = publishedEvidence.some(Boolean);
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
      checks: checks.map((check) => ({
        id: check.id,
        name: check.name,
        status: check.status,
        conclusion: check.conclusion,
        app: { id: check.app?.id },
        ...(check.workflow ? { workflow: check.workflow } : {}),
      })),
      statuses: latestStatuses.map((status) => ({ context: status.context, state: status.state })),
      tree: { truncated: tree.truncated, entries: (tree.tree ?? []).map((entry) => ({ path: entry.path, type: entry.type, mode: entry.mode, sha: entry.sha })) },
      reports,
      basePendingExists,
      baseSkillRootsExist,
      publishedTargetExists,
    };
  }

  async updateBranch(number, headSha) {
    return this.request(`/pulls/${number}/update-branch`, {
      method: 'PUT',
      body: { expected_head_sha: headSha },
      token: this.updateToken,
    });
  }

  async merge(number, headSha, method) {
    return this.request(`/pulls/${number}/merge`, {
      method: 'PUT',
      body: {
        sha: headSha,
        merge_method: method,
        commit_title: `Trusted auto-merge PR #${number}`,
        commit_message: `AgentCrew-Recovery: ${number}:${headSha}`,
      },
    });
  }

  async findPublicationRun(correlationTitle) {
    for (let page = 1; page <= 30; page += 1) {
      const result = await this.request(`/actions/workflows/on-pr-merge.yml/runs?event=workflow_dispatch&per_page=100&page=${page}`);
      block(Array.isArray(result?.workflow_runs), 'publication workflow run evidence is invalid');
      const match = result.workflow_runs.find((run) => run?.display_title === correlationTitle
        && run?.event === 'workflow_dispatch'
        && run?.head_branch === 'main'
        && run?.head_repository?.full_name === this.repository);
      if (match) return match;
      if (result.workflow_runs.length < 100) return undefined;
    }
    throw new AutoMergeBlockedError('publication workflow run search exceeded the bounded limit');
  }

  async dispatchPublication(prNumber, headSha, mergeCommitSha) {
    block(Number.isSafeInteger(prNumber) && prNumber > 0, 'publication PR number is invalid');
    block(validSha(headSha), 'publication head SHA is invalid');
    block(validSha(mergeCommitSha), 'publication merge commit SHA is invalid');
    const correlationId = `submission-pr-${prNumber}-${headSha}-${mergeCommitSha}`;
    const correlationTitle = `Publication ${correlationId}`;
    const existing = await this.findPublicationRun(correlationTitle);
    if (existing?.status === 'completed' && existing.conclusion === 'success') {
      return { outcome: 'PUBLICATION_ALREADY_DISPATCHED', workflowRunId: existing.id };
    }
    if (existing && existing.status !== 'completed') {
      return { outcome: 'PUBLICATION_IN_PROGRESS', workflowRunId: existing.id };
    }
    if (existing) {
      let rerunError;
      try {
        await this.request(`/actions/runs/${existing.id}/rerun`, { method: 'POST' });
      } catch (error) {
        rerunError = error;
      }
      if (!rerunError) return { outcome: 'PUBLICATION_RETRY_CONFIRMED', workflowRunId: existing.id };
      const readback = await this.findPublicationRun(correlationTitle);
      if (readback && readback.status !== 'completed') return { outcome: 'PUBLICATION_RETRY_CONFIRMED', workflowRunId: readback.id };
      if (definiteMutationRejection(rerunError)) throw new AutoMergeBlockedError(`publication rerun rejected with HTTP ${rerunError.status}`);
      throw new AutoMergeUnknownEffectError(`publication rerun effect is unknown for PR #${prNumber}`);
    }

    let mutationError;
    try {
      await this.request('/actions/workflows/on-pr-merge.yml/dispatches', {
        method: 'POST',
        body: { ref: 'main', inputs: { pr_number: String(prNumber), correlation_id: correlationId } },
      });
    } catch (error) {
      mutationError = error;
    }
    for (let attempt = 0; attempt < 12; attempt += 1) {
      const run = await this.findPublicationRun(correlationTitle);
      if (run) return { outcome: 'PUBLICATION_DISPATCH_CONFIRMED', workflowRunId: run.id };
      if (attempt < 11) await this.sleep(5_000);
    }
    if (mutationError && definiteMutationRejection(mutationError)) throw new AutoMergeBlockedError(`publication dispatch rejected with HTTP ${mutationError.status}`);
    throw new AutoMergeUnknownEffectError(`publication dispatch effect is unknown for PR #${prNumber}`);
  }

  async findProviderSyncRun(correlationTitle) {
    for (let page = 1; page <= 30; page += 1) {
      const result = await this.request(`/actions/workflows/sync-to-supabase.yml/runs?event=workflow_dispatch&per_page=100&page=${page}`);
      block(Array.isArray(result?.workflow_runs), 'provider sync workflow run evidence is invalid');
      const match = result.workflow_runs.find((run) => run?.display_title === correlationTitle
        && run?.event === 'workflow_dispatch'
        && run?.head_branch === 'main'
        && run?.head_repository?.full_name === this.repository);
      if (match) return match;
      if (result.workflow_runs.length < 100) return undefined;
    }
    throw new AutoMergeBlockedError('provider sync workflow run search exceeded the bounded limit');
  }

  async dispatchProviderSync(prNumber, headSha, mergeCommitSha, roots) {
    block(Number.isSafeInteger(prNumber) && prNumber > 0, 'provider sync PR number is invalid');
    block(validSha(headSha), 'provider sync head SHA is invalid');
    block(validSha(mergeCommitSha), 'provider sync merge commit SHA is invalid');
    block(Array.isArray(roots) && roots.length > 0 && roots.length <= 25, 'provider sync roots are required');
    const slugs = roots.map((root) => {
      block(publishedRootSyntax(root), `invalid provider sync root: ${root}`);
      return root.slice('skills/'.length);
    });
    const correlationId = `source-monitor-pr-${prNumber}-${headSha}-${mergeCommitSha}`;
    const correlationTitle = `Provider sync ${correlationId}`;
    const existing = await this.findProviderSyncRun(correlationTitle);
    if (existing?.status === 'completed' && existing.conclusion === 'success') {
      return { outcome: 'PROVIDER_SYNC_ALREADY_DISPATCHED', workflowRunId: existing.id };
    }
    if (existing && existing.status !== 'completed') {
      return { outcome: 'PROVIDER_SYNC_IN_PROGRESS', workflowRunId: existing.id };
    }
    if (existing) {
      let rerunError;
      try {
        await this.request(`/actions/runs/${existing.id}/rerun`, { method: 'POST' });
      } catch (error) {
        rerunError = error;
      }
      if (!rerunError) return { outcome: 'PROVIDER_SYNC_RETRY_CONFIRMED', workflowRunId: existing.id };
      const readback = await this.findProviderSyncRun(correlationTitle);
      if (readback && readback.status !== 'completed') return { outcome: 'PROVIDER_SYNC_RETRY_CONFIRMED', workflowRunId: readback.id };
      if (definiteMutationRejection(rerunError)) throw new AutoMergeBlockedError(`provider sync rerun rejected with HTTP ${rerunError.status}`);
      throw new AutoMergeUnknownEffectError(`provider sync rerun effect is unknown for PR #${prNumber}`);
    }

    let mutationError;
    try {
      await this.request('/actions/workflows/sync-to-supabase.yml/dispatches', {
        method: 'POST',
        body: {
          ref: 'main',
          inputs: {
            slugs: slugs.join(' '),
            correlation_id: correlationId,
            merge_commit_sha: mergeCommitSha,
          },
        },
      });
    } catch (error) {
      mutationError = error;
    }
    for (let attempt = 0; attempt < 12; attempt += 1) {
      if (await this.findProviderSyncRun(correlationTitle)) return { outcome: 'PROVIDER_SYNC_DISPATCH_CONFIRMED' };
      if (attempt < 11) await this.sleep(5_000);
    }
    if (mutationError && definiteMutationRejection(mutationError)) throw new AutoMergeBlockedError(`provider sync dispatch rejected with HTTP ${mutationError.status}`);
    throw new AutoMergeUnknownEffectError(`provider sync dispatch effect is unknown for PR #${prNumber}`);
  }
}

async function main() {
  const api = new GitHubApi({
    token: process.env.GH_TOKEN,
    updateToken: process.env.GH_UPDATE_TOKEN,
    repository: process.env.GITHUB_REPOSITORY,
    currentRunId: process.env.GITHUB_RUN_ID,
  });
  try {
    const result = await runRecoverySweep(api);
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    if (error instanceof AutoMergeSkippedError) {
      process.stdout.write(`${JSON.stringify({ outcome: 'SKIPPED', reason: error.message })}\n`);
      return;
    }
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
