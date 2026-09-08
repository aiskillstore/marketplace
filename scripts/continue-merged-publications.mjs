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
  // Stop when every CURRENT pending report has an exact merged owner. Scanning
  // the entire closed-PR history first always hits the 1000-item bound here.
  for (let page = 1; page <= 10 && owners.size < reports.size; page++) {
    const batch = request(`repos/${repo}/pulls?state=closed&sort=updated&direction=desc&per_page=100&page=${page}`);
    for (const pr of batch.filter(trustedMerged).sort((a, b) => b.merged_at.localeCompare(a.merged_at))) {
      const files = pages(`repos/${repo}/pulls/${pr.number}/files`, request);
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
  const publicationRuns = request(`repos/${repo}/actions/workflows/on-pr-merge.yml/runs?per_page=100`).workflow_runs;
  if (publicationRuns.some(r => r.status !== 'completed')) return console.log('Waiting for publication receiver');
  for (const candidate of candidates) {
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
    if (!live) { console.log(`Would dispatch #${pr.number}: ${correlation}`); return; }
    const ref = `refs/tags/agentcrew-dispatch-outbox/publication/${digest}/${choice.attempt}`;
    request(`repos/${repo}/git/refs`, { ref, sha: pr.merge_commit_sha });
    const readback = request(`repos/${repo}/git/ref/${ref.slice(5)}`);
    if (readback.object.sha !== pr.merge_commit_sha) throw new Error('Outbox readback mismatch');
    request(`repos/${repo}/actions/workflows/on-pr-merge.yml/dispatches`, {
      ref: 'main', inputs: { pr_number: String(pr.number), correlation_id: correlation, outbox_attempt: choice.attempt },
    });
    console.log(`Dispatched #${pr.number}: ${correlation}; receiver status is the completion evidence`);
    return;
  }
  if (reports.size) throw new Error('Remaining pending skills require inspection; no safe fresh dispatch');
}
if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) main();
