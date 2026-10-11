import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { appendFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { publicationValidatorRevision, assertPublicationReportNotHeld } from './resolve-approved-submission.mjs';
import { recoveredPushSync } from './recovered-push-sync.mjs';

export const preflightContext = digest => `agentcrew/publication-preflight/${createHash('sha256')
  .update(`${digest}:${publicationValidatorRevision}`).digest('hex')}`;

const repo = 'aiskillstore/marketplace';
// Dependency outcomes are queue state, not a new execution failure. Keep the
// original failed run visible and do not mistake successful planning for delivery.
export function reportContinuation(outcome, reason, { runIds = [], prNumbers = [], skillCount = 0 } = {}, env = process.env) {
  const result = { outcome, reason, runIds, prNumbers, skillCount };
  console.log(JSON.stringify(result));
  if (outcome === 'blocked') {
    const message = reason.replace(/%/g, '%25').replace(/\r/g, '%0D').replace(/\n/g, '%0A');
    console.warn(`::warning title=Publication queue blocked::${message}`);
  }
  if (env.GITHUB_OUTPUT) appendFileSync(env.GITHUB_OUTPUT, `outcome=${outcome}\nresult=${JSON.stringify(result)}\n`);
  if (env.GITHUB_STEP_SUMMARY) {
    const links = runIds.map(id => `- [Dependency run ${id}](https://github.com/${repo}/actions/runs/${id})`).join('\n');
    appendFileSync(env.GITHUB_STEP_SUMMARY, `## Publication queue: ${outcome}\n\n${reason}\n\n`
      + (outcome === 'dispatched' ? `Dispatched ${skillCount} skills for receiver validation. Provider, callbacks and cache must still complete.\n`
        : 'No publication was dispatched. Existing publication and provider results are unchanged.\n')
      + (links ? `\n${links}\n` : '')
      + (prNumbers.length ? `\nPRs: ${prNumbers.map(n => `#${n}`).join(', ')}\n` : ''));
  }
  return result;
}
export const maxBatchSkills = 64;
export function trustedMerged(pr) {
  return pr.merged_at && pr.base?.ref === 'main'
    && pr.user?.id === 254047988 && pr.user?.login === 'ai-skill-store[bot]'
    && pr.head?.repo?.full_name === repo && pr.head?.ref?.startsWith('submission/')
    && [pr.head.sha, pr.merge_commit_sha].every(s => /^[a-f0-9]{40}$/.test(s));
}
export function publicationIdentity(pr) {
  if (!trustedMerged(pr)) throw new Error('Untrusted or unmerged submission');
  const correlation = `submission-pr-${pr.number}-${pr.head.sha}-${pr.merge_commit_sha}`;
  return { correlation, digest: createHash('sha256').update(correlation).digest('hex') };
}

export function batchIdentity(correlations) {
  if (!correlations.length || correlations.length > 25 || new Set(correlations).size !== correlations.length) throw new Error('Batch requires 1..25 unique correlations');
  for (const value of correlations) if (!/^submission-pr-[1-9][0-9]*-[a-f0-9]{40}-[a-f0-9]{40}$/.test(value)) throw new Error('Invalid batch correlation');
  return createHash('sha256').update([...correlations].sort().join('\n')).digest('hex');
}

// This continuation never merges PRs or interprets advisory audit risk fields.
// Existing receiver remains the authority for immutable source/tree validation.
export function chooseAttempt({ refs, statuses, digest, merge, now }) {
  const prefix = `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/`;
  if (refs.length >= 8) return { wait: 'outbox attempt limit; inspection required', outcome: 'blocked' };
  for (const ref of refs) {
    if (!ref.ref.startsWith(prefix) || !/^\d{13}-[1-9]\d*$/.test(ref.ref.slice(prefix.length))
      || ref.object.type !== 'commit' || ref.object.sha !== merge) throw new Error('Invalid publication outbox');
  }
  const context = `agentcrew/publication/${digest}`;
  // Any prior receiver reservation is authoritative. Failure may include partial
  // effects; automatic continuation must not invent a safe retry from it.
  if (statuses.some(s => s.context === context || s.context.startsWith(`agentcrew/publication-attempt/${digest}/`))) {
    return { wait: 'receiver has durable evidence; reconcile before replay', outcome: 'blocked' };
  }
  const newest = Math.max(0, ...refs.map(r => Number(r.ref.slice(prefix.length).split('-')[0])));
  if (newest > now - 15 * 60_000) return { wait: 'fresh dispatch awaiting receiver', outcome: 'waiting' };
  return { attempt: `${now}-${refs.length + 1}` };
}

function api(endpoint, data) {
  const args = ['api', endpoint];
  if (data) args.push('--method', 'POST', '--input', '-');
  const output = execFileSync('gh', args, {
    input: data ? JSON.stringify(data) : undefined, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024,
  });
  return output.trim() ? JSON.parse(output) : null;
}
function pages(endpoint, request = api) {
  const values = [];
  // ponytail: bounded GitHub inventory; fail visibly at 1000 rather than silently
  // omit older pending work. Increase pagination only if this ceiling is reached.
  for (let page = 1; page <= 10; page++) {
    const batch = request(`${endpoint}${endpoint.includes('?') ? '&' : '?'}per_page=100&page=${page}`);
    values.push(...batch);
    if (batch.length < 100) return values;
  }
  throw new Error(`Inventory limit reached: ${endpoint}`);
}
export function publicationFiles(pr, request = api) {
  // GitHub serves at most 3,000 PR files. Bind the full inventory to the PR's
  // declared count, including exactly-full pages; never accept truncation.
  const detail = Number.isSafeInteger(pr.changed_files) ? pr : request(`repos/${repo}/pulls/${pr.number}`);
  if (!Number.isSafeInteger(detail.changed_files) || detail.changed_files < 1 || detail.changed_files > 3000) {
    throw new Error(`PR #${pr.number} file inventory exceeds the complete GitHub API bound`);
  }
  const files = [];
  for (let page = 1; files.length < detail.changed_files; page++) {
    const batch = request(`repos/${repo}/pulls/${pr.number}/files?per_page=100&page=${page}`);
    if (!Array.isArray(batch) || !batch.length || batch.length > 100) throw new Error('Incomplete publication file inventory');
    files.push(...batch);
  }
  if (files.length !== detail.changed_files || new Set(files.map(f => f.filename)).size !== files.length) {
    throw new Error('Incomplete or duplicate publication file inventory');
  }
  return files;
}
export function main(request = api) {
  const live = process.argv.includes('--apply');
  const tree = request(`repos/${repo}/git/trees/main`);
  const pending = tree.tree.find(t => t.path === 'pending');
  if (!pending) return reportContinuation('idle', 'No pending skills');
  const inventory = request(`repos/${repo}/git/trees/${pending.sha}?recursive=1`);
  if (inventory.truncated) throw new Error('Truncated pending inventory');
  const reports = new Map(inventory.tree.filter(t => t.path.endsWith('/skill-report.json'))
    .map(t => [`pending/${t.path}`, t.sha]));
  if (!reports.size) return reportContinuation('idle', 'No pending skills');
  // Fail closed for the entire continuation, rather than skipping a candidate
  // whose old reservations/effects have not been reconciled. No dispatch here.
  for (const [reportPath, blobSha] of reports) assertPublicationReportNotHeld(reportPath, blobSha);
  // Check dependencies before the expensive PR/file inventory on every wakeup.
  // A failed write must be reconciled, never replayed by this planner.
  const syncRuns = request(`repos/${repo}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`).workflow_runs;
  if (syncRuns.some(r => r.status !== 'completed')) {
    const active = syncRuns.filter(r => r.status !== 'completed');
    if (active.some(r => Date.now() - Date.parse(r.created_at) > 60 * 60_000)) {
      throw new Error(`Provider sync stalled over 60 minutes: ${active.map(r => r.id).join(', ')}; inspect scoring locks and unfinished stages`);
    }
    return reportContinuation('waiting', 'Waiting for provider sync to finish before publishing another batch', { runIds: active.map(r => r.id) });
  }
  const lastPush = syncRuns.filter(r => r.event === 'push')
    .sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
  if (lastPush && !['success', 'skipped'].includes(lastPush.conclusion)
    && !recoveredPushSync(lastPush, syncRuns, request)) {
    return reportContinuation('blocked', `Previous push sync ${lastPush.id} is ${lastPush.conclusion}; inspect its effects and complete verified reconciliation before continuing`, { runIds: [lastPush.id] });
  }
  for (const workflow of ['on-pr-merge.yml', 'publish-approved-batch.yml']) {
    const active = request(`repos/${repo}/actions/workflows/${workflow}/runs?per_page=100`).workflow_runs.filter(r => r.status !== 'completed');
    if (active.length) return reportContinuation('waiting', `Waiting for ${workflow}`, { runIds: active.map(r => r.id) });
  }
  const owners = new Map();
  const skillCounts = new Map();
  // Stop when every CURRENT pending report has an exact merged owner. Scanning
  // the entire closed-PR history first always hits the 1000-item bound here.
  for (let page = 1; page <= 10 && owners.size < reports.size; page++) {
    const batch = request(`repos/${repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page=${page}`);
    for (const pr of batch.filter(trustedMerged).sort((a, b) => b.merged_at.localeCompare(a.merged_at))) {
      const files = publicationFiles(pr, request);
      skillCounts.set(pr.number, files.filter(f => f.filename.endsWith('/skill-report.json')).length);
      for (const file of files) {
        if (reports.get(file.filename) === file.sha && !owners.has(file.filename)) {
          owners.set(file.filename, pr);
        }
      }
      if (owners.size === reports.size) break;
    }
    if (batch.length < 100) break;
  }
  const unmatched = [...reports.keys()].filter(p => !owners.has(p));
  if (unmatched.length) console.error(`::warning::Pending reports need provenance inspection: ${unmatched.join(', ')}`);
  const candidates = [...new Set(owners.values())].sort((a, b) => a.merged_at.localeCompare(b.merged_at));
  console.log(JSON.stringify({ pending: reports.size, candidates: candidates.map(p => p.number), unmatched }));
  const selected = [];
  const rejected = [];
  let skillCount = 0;
  for (const candidate of candidates) {
    const count = skillCounts.get(candidate.number);
    if (!count || count > maxBatchSkills) throw new Error('Submission exceeds bounded batch capacity');
    if (skillCount + count > maxBatchSkills || selected.length === 25) break;
    const pr = request(`repos/${repo}/pulls/${candidate.number}`);
    const { correlation, digest } = publicationIdentity(pr);
    const refs = request(`repos/${repo}/git/matching-refs/tags/agentcrew-dispatch-outbox/publication/${digest}/`);
    const statuses = pages(`repos/${repo}/commits/${pr.merge_commit_sha}/statuses`, request);
    const choice = chooseAttempt({ refs, statuses, digest, merge: pr.merge_commit_sha, now: Date.now() });
    if (choice.wait) {
      // Oldest-first is a safety boundary: a missing or non-terminal effect
      // blocks later publications until its exact correlation is reconciled.
      return reportContinuation(choice.outcome, `#${pr.number}: ${choice.wait}`, { prNumbers: [pr.number] });
    }
    // Only validation that failed BEFORE any reservation/mutation may be
    // isolated. Unknown publication effects above still stop the entire queue.
    if (statuses.find(s => s.context === preflightContext(digest))?.state === 'failure') {
      rejected.push(pr.number);
      console.warn(`::warning::#${pr.number}: frozen publication preflight rejected; inspect its status. Other independent approvals can continue.`);
      continue;
    }
    selected.push({ number: pr.number, correlation });
    skillCount += count;
  }
  if (selected.length) {
    const inputs = { pr_numbers: selected.map(p => p.number).join(','), batch_id: batchIdentity(selected.map(p => p.correlation)) };
    if (live) request(`repos/${repo}/actions/workflows/publish-approved-batch.yml/dispatches`, { ref: 'main', inputs });
    console.log(`${live ? 'Dispatched' : 'Would dispatch'} ${skillCount} skills: ${JSON.stringify(inputs)}; receiver owns durable reservations`);
    return reportContinuation(live ? 'dispatched' : 'ready', 'Receiver owns durable reservations and final publication validation', { prNumbers: selected.map(p => p.number), skillCount });
  }
  return reportContinuation('blocked', `Remaining pending skills require inspection; no safe fresh dispatch. ${unmatched.length} reports lack verified ownership; ${rejected.length} PRs were rejected before mutation.`, { prNumbers: rejected });
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main();
