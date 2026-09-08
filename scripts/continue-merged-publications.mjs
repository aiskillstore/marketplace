import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const repo = 'aiskillstore/marketplace';
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
  if (refs.length >= 8) return { wait: 'outbox attempt limit; inspection required' };
  for (const ref of refs) {
    if (!ref.ref.startsWith(prefix) || !/^\d{13}-[1-9]\d*$/.test(ref.ref.slice(prefix.length))
      || ref.object.type !== 'commit' || ref.object.sha !== merge) throw new Error('Invalid publication outbox');
  }
  const context = `agentcrew/publication/${digest}`;
  // Any prior receiver reservation is authoritative. Failure may include partial
  // effects; automatic continuation must not invent a safe retry from it.
  if (statuses.some(s => s.context === context || s.context.startsWith(`agentcrew/publication-attempt/${digest}/`))) {
    return { wait: 'receiver has durable evidence; reconcile before replay' };
  }
  const newest = Math.max(0, ...refs.map(r => Number(r.ref.slice(prefix.length).split('-')[0])));
  if (newest > now - 15 * 60_000) return { wait: 'fresh dispatch awaiting receiver' };
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
export function main(request = api) {
  const live = process.argv.includes('--apply');
  const tree = request(`repos/${repo}/git/trees/main`);
  const pending = tree.tree.find(t => t.path === 'pending');
  if (!pending) return console.log('No pending skills');
  const inventory = request(`repos/${repo}/git/trees/${pending.sha}?recursive=1`);
  if (inventory.truncated) throw new Error('Truncated pending inventory');
  const reports = new Map(inventory.tree.filter(t => t.path.endsWith('/skill-report.json'))
    .map(t => [`pending/${t.path}`, t.sha]));
  if (!reports.size) return console.log('No pending skills');
  const owners = new Map();
  const skillCounts = new Map();
  // Stop when every CURRENT pending report has an exact merged owner. Scanning
  // the entire closed-PR history first always hits the 1000-item bound here.
  for (let page = 1; page <= 10 && owners.size < reports.size; page++) {
    const batch = request(`repos/${repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page=${page}`);
    for (const pr of batch.filter(trustedMerged).sort((a, b) => b.merged_at.localeCompare(a.merged_at))) {
      const files = pages(`repos/${repo}/pulls/${pr.number}/files`, request);
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
  // GitHub's concurrency group only preserves one pending run. Let each push sync
  // close before creating the next publication push, including Cody's dispatches.
  const syncRuns = request(`repos/${repo}/actions/workflows/sync-to-supabase.yml/runs?per_page=100`).workflow_runs;
  if (syncRuns.some(r => r.status !== 'completed')) return console.log('Waiting for provider sync');
  const lastPush = syncRuns.filter(r => r.event === 'push')
    .sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
  // Publication already removed its pending report before provider/cache work.
  // Its absence cannot hide a failed downstream run and release the next item.
  if (lastPush && !['success', 'skipped'].includes(lastPush.conclusion)) {
    throw new Error(`Previous push sync ${lastPush.id} is ${lastPush.conclusion}; reconcile before continuing`);
  }
  const publicationRuns = request(`repos/${repo}/actions/workflows/on-pr-merge.yml/runs?per_page=100`).workflow_runs;
  if (publicationRuns.some(r => r.status !== 'completed')) return console.log('Waiting for publication receiver');
  const batchRuns = request(`repos/${repo}/actions/workflows/publish-approved-batch.yml/runs?per_page=100`).workflow_runs;
  if (batchRuns.some(r => r.status !== 'completed')) return console.log('Waiting for batch publication receiver');
  const selected = [];
  let skillCount = 0;
  for (const candidate of candidates) {
    const count = skillCounts.get(candidate.number);
    if (!count || count > 25) throw new Error('Submission exceeds bounded batch capacity');
    if (skillCount + count > 25 || selected.length === 25) break;
    const pr = request(`repos/${repo}/pulls/${candidate.number}`);
    const { correlation, digest } = publicationIdentity(pr);
    const refs = request(`repos/${repo}/git/matching-refs/tags/agentcrew-dispatch-outbox/publication/${digest}/`);
    const statuses = pages(`repos/${repo}/commits/${pr.merge_commit_sha}/statuses`, request);
    const choice = chooseAttempt({ refs, statuses, digest, merge: pr.merge_commit_sha, now: Date.now() });
    if (choice.wait) {
      // Oldest-first is a safety boundary: a missing or non-terminal effect
      // blocks later publications until its exact correlation is reconciled.
      return console.log(`#${pr.number}: ${choice.wait}`);
    }
    selected.push({ number: pr.number, correlation });
    skillCount += count;
  }
  if (selected.length) {
    const inputs = { pr_numbers: selected.map(p => p.number).join(','), batch_id: batchIdentity(selected.map(p => p.correlation)) };
    if (live) request(`repos/${repo}/actions/workflows/publish-approved-batch.yml/dispatches`, { ref: 'main', inputs });
    console.log(`${live ? 'Dispatched' : 'Would dispatch'} ${skillCount} skills: ${JSON.stringify(inputs)}; receiver owns durable reservations`);
    return;
  }
  if (reports.size) throw new Error('Remaining pending skills require inspection; no safe fresh dispatch');
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main();
