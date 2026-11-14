import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';

// Only ancillary cache recovery. Provider/callback recovery keeps its existing
// contract; this path never sends writes or makes a failed provider look complete.
export function verifyCacheOnlyStages(e, original, recovered) {
  const successfulStep = (jobs, name) => {
    const steps = jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
    assert.ok(steps.length === 1 && steps[0].conclusion === 'success', `Missing completed cache recovery step: ${name}`);
  };
  for (const name of ['sync', 'calculate-scores']) {
    const jobs = original.filter(j => j.name === name);
    assert.ok(jobs.length === 1 && jobs[0].conclusion === 'success', `Original ${name} did not complete`);
  }
  for (const name of ['Wait for authoritative publication completion', 'Sync skills to Supabase',
    'Upload provider-complete synced slugs artifact', 'Reconcile durable security change events',
    'Notify skillstore - Published submissions', 'Record durable publication provider result']) successfulStep(original, name);
  const failures = original.filter(j => !['success', 'skipped'].includes(j.conclusion));
  assert.ok(failures.some(j => j.name === 'cache-invalidate' && j.conclusion === 'failure'));
  assert.ok(failures.length > 1 && failures.every(j => j.conclusion === 'failure'
    && /^(cache-invalidate|cache-invalidate-shard \([0-9]+\))$/.test(j.name)), 'Failure was not cache-only');
  verifyWarmCacheProof(e, recovered, original.filter(j => ['sync', 'calculate-scores'].includes(j.name)).map(j => j.completed_at));
}

// Shared cache proof; the original cache-only path and the separate ancillary
// recovery supply their own independently verified completion timestamps.
export function verifyWarmCacheProof(e, recovered, completedTimes) {
  const successfulStep = (jobs, name) => {
    const steps = jobs.flatMap(j => j.steps ?? []).filter(s => s.name === name);
    assert.ok(steps.length === 1 && steps[0].conclusion === 'success', `Missing completed cache recovery step: ${name}`);
  };
  assert.ok(recovered.length === 1 && recovered[0].name === 'warm' && recovered[0].conclusion === 'success');
  for (const name of ['Download changed slugs from source workflow', 'Resolve and validate warm scope',
    'Invalidate selected skill caches', 'Warm and verify API, HTML, and optional ZIP caches',
    'Upload warm verification evidence']) successfulStep(recovered, name);
  // A green warm run is stale if provider/scoring writes finished afterwards.
  // Use exact job/step times, not run creation times (the jobs may overlap).
  const invalidatedAt = Date.parse(recovered[0].steps.find(s => s.name === 'Invalidate selected skill caches').started_at);
  for (const completedTime of completedTimes) {
    const completedAt = Date.parse(completedTime);
    assert.ok(Number.isFinite(invalidatedAt) && Number.isFinite(completedAt) && invalidatedAt > completedAt,
      'Cache invalidation must follow completed provider and scoring writes');
  }
  const { sourceArtifact: a, summary: s, records, log } = e.cacheEvidence;
  assert.ok(a.name === 'synced-slugs' && !a.expired && Number.isSafeInteger(a.id) && a.id > 0
    && /^sha256:[a-f0-9]{64}$/.test(a.digest) && a.workflow_run?.id === e.push.id
    && a.workflow_run.head_sha === e.push.head_sha, 'Unbound cache source artifact');
  assert.ok(log.includes(`- synced-slugs (ID: ${a.id}, `) && log.includes(`Expected Digest: ${a.digest})`)
    && log.includes(`SHA256 digest of downloaded artifact is ${a.digest.slice(7)}`), 'Warm run did not consume the original artifact');
  const invalidations = log.split('\n').flatMap(line => {
    const match = line.match(/^\d{4}-\d{2}-\d{2}T[^ ]+Z (\{.*\})\s+✓\s*$/);
    if (!match) return [];
    const value = JSON.parse(match[1]);
    return value.type === 'skills' && value.invalidated ? [value] : [];
  });
  assert.equal(invalidations.length, 1, 'Expected one exact invalidation response');
  const v = invalidations[0];
  assert.equal(v.preflight, false);
  assert.match(v.planHash, /^[a-f0-9]{64}$/);
  assert.equal(v.closure?.dependentPacks?.overflow, false);
  assert.deepEqual(v.closure.dependentPacks.all, [], 'Dependent pack recovery requires its own coverage proof');
  assert.deepEqual([...v.slugs].sort(), [...e.slugs].sort(), 'Invalidation scope mismatch');
  assert.deepEqual([...v.locales].sort(), ['en', 'zh-hans', 'zh-hant', 'ja', 'ko', 'de', 'fr', 'es', 'pt', 'ru', 'ar'].sort(), 'Incomplete invalidation locales');
  assert.equal(v.invalidated.listVersionBumped, true);
  assert.equal(v.invalidated.listMaxStaleSeconds, 0);
  for (const kind of ['page', 'api', 'artifacts']) {
    assert.ok(Number.isSafeInteger(v.plan.totals[kind]) && v.plan.totals[kind] >= 0);
    assert.equal(v.invalidated[kind], v.plan.totals[kind], `Incomplete ${kind} invalidation`);
  }
  assert.ok(v.invalidated.api > 0 && v.invalidated.page > 0);
  assert.equal(v.invalidated.total, v.invalidated.api + v.invalidated.page + v.invalidated.artifacts);
  assert.ok(s.success === true && s.mode === 'force' && s.scope === 'changed'
    && s.slugs === e.slugs.length && s.targets === e.slugs.length && s.locales === 1);
  assert.ok(s.failedEndpoints === 0 && s.skippedEndpoints === 0 && s.failureCount === 0 && s.failures?.length === 0);
  for (const kind of ['api', 'page']) {
    assert.equal(s.plannedEndpoints[kind], e.slugs.length);
    assert.equal(s.completedEndpoints[kind], e.slugs.length);
  }
  assert.equal(s.plannedEndpoints.zip, 0);
  assert.equal(s.completedEndpoints.zip, 0);
  const proofs = records.filter(r => r.phase === 'ordinary-verification');
  assert.ok(proofs.length > 0 && proofs.every(r => e.slugs.includes(r.slug) && r.resource === 'skills'
    && ['api', 'page'].includes(r.kind) && r.locale === 'en' && r.ok === true && r.status === 200
    && r.cache === 'HIT' && r.truncated === false), 'Invalid English cache proof');
  for (const slug of e.slugs) for (const kind of ['api', 'page']) {
    assert.ok(proofs.some(r => r.slug === slug && r.kind === kind), 'Missing English cache coverage');
  }
}

export function verifiedWarmArtifact(zip, artifact) {
  assert.ok(!artifact.expired && zip.length === artifact.size_in_bytes && zip.length > 0 && zip.length <= 1024 * 1024);
  assert.equal(`sha256:${createHash('sha256').update(zip).digest('hex')}`, artifact.digest, 'Warm artifact digest mismatch');
  // Read only the exact two regular files; never extract paths from an archive.
  const decoded = execFileSync('python3', ['-c', `import sys,io,zipfile,stat,json
z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))
items=z.infolist()
names=['warm-cache-summary.json','warm-cache-report.jsonl']
assert len(items)==2 and sorted(i.filename for i in items)==sorted(names)
assert all(i.file_size<=2097152 and not stat.S_ISLNK(i.external_attr >> 16) for i in items)
print(json.dumps({i.filename:z.read(i).decode('utf8') for i in items}))`], { input: zip, maxBuffer: 5 * 1024 * 1024, timeout: 10000 });
  const files = JSON.parse(decoded);
  return { summary: JSON.parse(files['warm-cache-summary.json']),
    records: files['warm-cache-report.jsonl'].trim().split('\n').map(line => JSON.parse(line)) };
}
