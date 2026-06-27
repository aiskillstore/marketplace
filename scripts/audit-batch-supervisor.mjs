#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';

const args = new Set(process.argv.slice(2));
const getArg = (name, fallback = '') => {
  const prefix = `${name}=`;
  const found = process.argv.slice(2).find((arg) => arg.startsWith(prefix));
  return found ? found.slice(prefix.length) : fallback;
};

const repo = process.env.REPO || 'aiskillstore/marketplace';
const worktree = process.env.WORKTREE || process.cwd();
const model = process.env.MODEL || 'gpt-5.5:high';
const cutoffIso = process.env.FRESH_CUTOFF || '2026-06-27T11:00:00Z';
const cutoffMs = Date.parse(cutoffIso);
const batchSize = Number(process.env.BATCH_SIZE || getArg('--batch-size', '100'));
const shardSize = Number(process.env.SHARD_SIZE || getArg('--shard-size', '25'));
const maxParallel = Number(process.env.MAX_PARALLEL || getArg('--max-parallel', '2'));
const pollSeconds = Number(process.env.POLL_SECONDS || getArg('--poll-seconds', '180'));
const maxBatches = Number(process.env.MAX_BATCHES || getArg('--max-batches', '0'));
const autoMerge = process.env.AUTO_MERGE === '1' || args.has('--auto-merge');
const dryRun = args.has('--dry-run');
const once = args.has('--once');

if (!Number.isFinite(cutoffMs)) {
  throw new Error(`Invalid FRESH_CUTOFF: ${cutoffIso}`);
}

function log(message) {
  console.log(`[${new Date().toISOString()}] ${message}`);
}

function run(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, {
    cwd: options.cwd || worktree,
    encoding: 'utf8',
    stdio: options.stdio || ['ignore', 'pipe', 'pipe'],
  });

  if (result.status !== 0) {
    const detail = [result.stdout, result.stderr].filter(Boolean).join('\n').trim();
    throw new Error(`${command} ${commandArgs.join(' ')} failed${detail ? `\n${detail}` : ''}`);
  }

  return (result.stdout || '').trim();
}

function tryRun(command, commandArgs, options = {}) {
  const result = spawnSync(command, commandArgs, {
    cwd: options.cwd || worktree,
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  return {
    ok: result.status === 0,
    stdout: (result.stdout || '').trim(),
    stderr: (result.stderr || '').trim(),
    status: result.status,
  };
}

function ghJson(commandArgs) {
  const output = run('gh', commandArgs);
  return output ? JSON.parse(output) : null;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function reportSlug(reportPath, report) {
  if (report?.meta?.slug) return report.meta.slug;

  const relative = path.relative(path.join(worktree, 'skills'), reportPath);
  const parts = relative.split(path.sep);
  if (parts.length === 2) return parts[0];
  if (parts.length >= 3) return `${parts[0]}-${parts[1]}`;
  throw new Error(`Cannot derive slug from ${reportPath}`);
}

function walkReports(dir, reports = []) {
  for (const entry of readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkReports(fullPath, reports);
    } else if (entry.name === 'skill-report.json') {
      reports.push(fullPath);
    }
  }
  return reports;
}

function auditState() {
  const reportsDir = path.join(worktree, 'skills');
  const reports = walkReports(reportsDir);
  const stale = [];
  let fresh = 0;
  let missingAudit = 0;

  for (const reportPath of reports) {
    const report = JSON.parse(readFileSync(reportPath, 'utf8'));
    const auditedAt = report?.security_audit?.audited_at;
    const auditedMs = auditedAt ? Date.parse(auditedAt) : NaN;

    if (Number.isFinite(auditedMs) && auditedMs >= cutoffMs) {
      fresh += 1;
      continue;
    }

    if (!auditedAt) missingAudit += 1;
    stale.push({
      path: path.relative(worktree, reportPath),
      slug: reportSlug(reportPath, report),
      auditedAt: auditedAt || '',
    });
  }

  return {
    all: reports.length,
    fresh,
    stale,
    missingAudit,
    remainingBatches: Math.ceil(stale.length / batchSize),
  };
}

function listWorkflowRuns(workflow, limit = 20) {
  return ghJson([
    'run',
    'list',
    '--repo',
    repo,
    '--workflow',
    workflow,
    '--limit',
    String(limit),
    '--json',
    'databaseId,status,conclusion,createdAt,updatedAt,displayTitle,url,headBranch,event',
  ]);
}

function listActiveWorkflowRuns(workflow) {
  return listWorkflowRuns(workflow).filter((runItem) => runItem.status !== 'completed');
}

async function waitRunSuccess(runId, label) {
  while (true) {
    const runItem = ghJson([
      'run',
      'view',
      String(runId),
      '--repo',
      repo,
      '--json',
      'status,conclusion,url,createdAt,updatedAt',
    ]);

    if (runItem.status === 'completed') {
      if (runItem.conclusion !== 'success') {
        throw new Error(`${label} failed: ${runItem.url} (${runItem.conclusion})`);
      }
      log(`${label} completed: ${runItem.url}`);
      return runItem;
    }

    log(`${label} still ${runItem.status}: ${runItem.url}`);
    await sleep(pollSeconds * 1000);
  }
}

async function waitForNoActiveAuditRuns() {
  while (true) {
    const active = listActiveWorkflowRuns('Audit Skills');
    if (active.length === 0) return;

    log(`Waiting for ${active.length} active Audit Skills run(s).`);
    for (const runItem of active) {
      await waitRunSuccess(runItem.databaseId, `Audit Skills ${runItem.databaseId}`);
    }
  }
}

function listOpenAuditPrs() {
  const prs = ghJson([
    'pr',
    'list',
    '--repo',
    repo,
    '--state',
    'open',
    '--search',
    'Audit: in:title',
    '--json',
    'number,title,url,createdAt,headRefName,isDraft,mergeStateStatus',
  ]);

  return prs
    .filter((pr) => /^Audit: \d+ skills$/.test(pr.title) && pr.headRefName.startsWith('audit/'))
    .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
}

async function mergePr(pr) {
  if (!autoMerge) {
    throw new Error(`Audit PR is waiting for merge: ${pr.url}. Re-run with --auto-merge to let the supervisor merge audit PRs.`);
  }

  log(`Merging ${pr.url}`);
  for (let attempt = 1; attempt <= 30; attempt += 1) {
    const current = ghJson([
      'pr',
      'view',
      String(pr.number),
      '--repo',
      repo,
      '--json',
      'state,isDraft,mergeStateStatus,statusCheckRollup,url',
    ]);

    if (current.state === 'MERGED') {
      break;
    }
    if (current.isDraft) {
      throw new Error(`PR is draft and cannot be merged: ${current.url}`);
    }

    const result = tryRun('gh', [
      'pr',
      'merge',
      String(pr.number),
      '--repo',
      repo,
      '--squash',
      '--delete-branch',
    ]);

    if (result.ok) {
      break;
    }

    log(`Merge attempt ${attempt}/30 not ready yet for ${pr.url}: ${result.stderr || result.stdout}`);
    await sleep(60 * 1000);
  }

  const merged = ghJson([
    'pr',
    'view',
    String(pr.number),
    '--repo',
    repo,
    '--json',
    'state,mergedAt,mergeCommit,url',
  ]);

  if (merged.state !== 'MERGED') {
    throw new Error(`Could not merge ${pr.url}`);
  }

  log(`Merged ${merged.url} at ${merged.mergedAt}`);
  return merged;
}

async function waitForWorkflowAfter(workflow, afterIso) {
  const afterMs = Date.parse(afterIso) - 60 * 1000;

  while (true) {
    const candidates = listWorkflowRuns(workflow, 20)
      .filter((runItem) => Date.parse(runItem.createdAt) >= afterMs)
      .sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt));

    if (candidates.length > 0) {
      const latest = candidates[0];
      return waitRunSuccess(latest.databaseId, `${workflow} ${latest.databaseId}`);
    }

    log(`Waiting for ${workflow} to start after ${afterIso}.`);
    await sleep(pollSeconds * 1000);
  }
}

async function mergePendingAuditPrsAndWaitPostMerge() {
  const prs = listOpenAuditPrs();
  if (prs.length === 0) return false;

  for (const pr of prs) {
    const merged = await mergePr(pr);
    const syncRun = await waitForWorkflowAfter('Sync to Supabase (Incremental)', merged.mergedAt);
    await waitForWorkflowAfter('Warm KV Cache', syncRun.createdAt);
  }

  return true;
}

function updateLocalMain() {
  log('Updating local main from origin/main.');
  run('git', ['fetch', 'origin', 'main']);
  run('git', ['pull', '--ff-only', 'origin', 'main']);
}

function triggerAuditBatch(batch) {
  const csv = batch.map((item) => item.slug).join(',');
  const startedAfterMs = Date.now() - 60 * 1000;

  log(`Next batch: ${batch.length} skills, first=${batch[0]?.slug || ''}, last=${batch[batch.length - 1]?.slug || ''}`);
  if (dryRun) {
    log('Dry run enabled; not triggering Audit Skills.');
    return null;
  }

  run('gh', [
    'workflow',
    'run',
    'Audit Skills',
    '--repo',
    repo,
    '-f',
    `model=${model}`,
    '-f',
    `slugs=${csv}`,
    '-f',
    'limit=',
    '-f',
    `shard_size=${shardSize}`,
    '-f',
    `max_parallel=${maxParallel}`,
    '-f',
    'cli_version=latest',
    '-f',
    'dry_run=false',
    '-f',
    'failed_only=false',
  ]);

  log('Triggered Audit Skills workflow.');
  return startedAfterMs;
}

async function waitForAuditRunToAppear(startedAfterMs) {
  for (let attempt = 1; attempt <= 30; attempt += 1) {
    const candidates = listWorkflowRuns('Audit Skills', 10)
      .filter((runItem) => Date.parse(runItem.createdAt) >= startedAfterMs)
      .sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt));

    if (candidates.length > 0) {
      const latest = candidates[0];
      log(`New Audit Skills run detected: ${latest.databaseId} ${latest.url}`);
      return latest;
    }

    log(`Waiting for new Audit Skills run to appear (${attempt}/30).`);
    await sleep(10 * 1000);
  }

  throw new Error('Triggered Audit Skills, but no new run appeared in GitHub run list.');
}

async function printStatus() {
  const state = auditState();
  const activeAudits = listActiveWorkflowRuns('Audit Skills');
  const openPrs = listOpenAuditPrs();

  console.log(
    JSON.stringify(
      {
        repo,
        worktree,
        model,
        cutoff: cutoffIso,
        batchSize,
        shardSize,
        maxParallel,
        autoMerge,
        dryRun,
        all: state.all,
        fresh: state.fresh,
        stale: state.stale.length,
        missingAudit: state.missingAudit,
        remainingBatches: state.remainingBatches,
        activeAudits: activeAudits.map((runItem) => ({
          databaseId: runItem.databaseId,
          status: runItem.status,
          conclusion: runItem.conclusion,
          url: runItem.url,
        })),
        openAuditPrs: openPrs,
      },
      null,
      2,
    ),
  );
}

async function main() {
  if (!existsSync(path.join(worktree, 'skills'))) {
    throw new Error(`Missing skills directory under ${worktree}`);
  }

  if (args.has('--status')) {
    await printStatus();
    return;
  }

  if (args.has('--print-next')) {
    const state = auditState();
    const batch = state.stale.slice(0, batchSize);
    console.log(batch.map((item) => item.slug).join('\n'));
    return;
  }

  let triggered = 0;
  while (true) {
    await waitForNoActiveAuditRuns();
    const mergedAny = await mergePendingAuditPrsAndWaitPostMerge();
    if (mergedAny) {
      updateLocalMain();
    } else {
      updateLocalMain();
    }

    const state = auditState();
    log(`Audit state: all=${state.all}, fresh=${state.fresh}, stale=${state.stale.length}, remainingBatches=${state.remainingBatches}`);

    if (state.stale.length === 0) {
      log('All reports are fresh. Done.');
      return;
    }

    const batch = state.stale.slice(0, batchSize);
    const startedAfterMs = triggerAuditBatch(batch);
    if (startedAfterMs !== null) {
      await waitForAuditRunToAppear(startedAfterMs);
    }
    triggered += dryRun ? 0 : 1;

    if (once || (maxBatches > 0 && triggered >= maxBatches)) {
      log('Stopping after requested batch count.');
      return;
    }

    await sleep(30 * 1000);
  }
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
