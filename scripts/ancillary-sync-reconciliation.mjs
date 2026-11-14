import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { verifyWarmCacheProof } from './cache-only-reconciliation.mjs';

// No provider/callback writes. This proof is only for a completed provider and
// callback whose sync job failed afterwards, with scoring originally skipped.
export function verifyAncillaryStages(e, original, recovered) {
  const step = (jobs, name) => {
    const matches = jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
    assert.ok(matches.length === 1 && matches[0].conclusion === 'success', `Incomplete ancillary stage: ${name}`);
  };
  const sync = original.filter(j => j.name === 'sync');
  const scoring = original.filter(j => j.name === 'calculate-scores');
  assert.ok(sync.length === 1 && sync[0].conclusion === 'failure');
  assert.ok(scoring.length === 1 && scoring[0].conclusion === 'skipped');
  assert.ok(original.every(j => j.name === 'sync' || j.conclusion === 'skipped'), 'Other original work may have run');
  for (const name of ['Wait for authoritative publication completion', 'Sync skills to Supabase',
    'Upload provider-complete synced slugs artifact', 'Reconcile durable security change events',
    'Notify skillstore - Published submissions']) step(original, name);
  const { scoreRecovery: run, scoreJobs: jobs, scoreEvidence: proof } = e;
  // Workflow-run REST records do not expose completed_at. Jobs are already
  // fetched from the exact run_attempt and supply authoritative finish times.
  assert.ok(jobs?.total_count === 2 && jobs.jobs?.length === 2);
  const originalCompleted = Date.parse(sync[0].completed_at);
  const completedTimes = jobs.jobs.map(j => Date.parse(j.completed_at));
  const scoreCompleted = Math.max(...completedTimes);
  assert.ok(Number.isFinite(originalCompleted) && completedTimes.every(Number.isFinite)
    && Date.parse(run.created_at) > originalCompleted
    && completedTimes.every(t => t >= Date.parse(run.created_at))
    && Date.parse(e.recovery.created_at) > scoreCompleted, 'Scoring/cache recovery order mismatch');
  for (const name of ['recalculate', 'score cache closure (hosted)']) {
    assert.equal(jobs.jobs.filter(j => j.name === name && j.conclusion === 'success').length, 1, 'Incomplete score recovery');
  }
  for (const name of ['Recalculate quality scores', 'Upload exact score closure',
    'Invalidate only successfully rescored API entries', 'Verify every production API cache readback']) step(jobs.jobs, name);
  const { metadata: m, slugs, failedSlugs, scores } = proof;
  assert.equal(m.sourceRunId, String(run.id));
  assert.equal(m.workflowCommit, run.head_sha);
  assert.equal(m.dryRun, false);
  for (const key of ['processed', 'successfulCount']) assert.equal(m[key], e.slugs.length);
  for (const key of ['failedCount', 'errors']) assert.equal(m[key], 0);
  assert.deepEqual(failedSlugs, []);
  assert.deepEqual([...slugs].sort(), [...e.slugs].sort(), 'Score recovery widened or omitted slugs');
  assert.ok(scores.length === e.slugs.length && scores.every(s => s.snapshotId
    && Number.isFinite(s.qualityScore) && s.qualityScore >= 0 && s.qualityScore <= 100
    && Date.parse(s.calculatedAt) >= Date.parse(run.created_at)
    && Date.parse(s.calculatedAt) <= scoreCompleted));
  assert.deepEqual(scores.map(s => s.slug).sort(), [...e.slugs].sort(), 'Score snapshots differ from recovered scope');
  verifyWarmCacheProof(e, recovered, jobs.jobs.map(j => j.completed_at));
}

export function verifiedScoreArtifact(zip, a) {
  assert.ok(!a.expired && zip.length === a.size_in_bytes && zip.length > 0 && zip.length <= 1024 * 1024);
  assert.equal(`sha256:${createHash('sha256').update(zip).digest('hex')}`, a.digest, 'Score artifact digest mismatch');
  const decoded = execFileSync('python3', ['-c', `import sys,io,zipfile,stat,json
z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))
items=z.infolist()
names=['metadata.json','successful-slugs.txt','failed-slugs.txt','expected-score-evidence.json']
assert len(items)==4 and sorted(i.filename for i in items)==sorted(names)
assert all(i.file_size<=262144 and stat.S_IFMT(i.external_attr >> 16) in [0,stat.S_IFREG] for i in items)
print(json.dumps({i.filename:z.read(i).decode('utf8') for i in items}))`], {input:zip,maxBuffer:2*1024*1024,timeout:10000});
  const files = JSON.parse(decoded);
  const lines = text => text.trim() ? text.trim().split('\n').map(s => s.trim()) : [];
  return {metadata:JSON.parse(files['metadata.json']),slugs:lines(files['successful-slugs.txt']),
    failedSlugs:lines(files['failed-slugs.txt']),scores:JSON.parse(files['expected-score-evidence.json']).scores};
}
