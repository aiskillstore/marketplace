import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { validate, parseJsonSafe } from '../../../src/request-transit/adapters/normalize.mjs';

export function isGitHubActionsRun(doc) {
  return !!doc && typeof doc === 'object' && Array.isArray(doc.jobs) && doc.jobs.some((j) => Array.isArray(j.steps));
}

// GitHub reports unset times as null or the zero time 0001-01-01T00:00:00Z (seen on skipped steps of real runs).
const ns = (value) => { if (value == null) return null; const ms = new Date(value).getTime(); return Number.isFinite(ms) && ms > 946684800000 ? BigInt(ms) * 1000000n : null; };
const MAX_STEPS = 150;   // above this many steps in one run, only failed/cancelled steps stay as stations
const statusFor = (conclusion) => conclusion === 'failure' || conclusion === 'cancelled' ? 'error' : conclusion === 'skipped' ? 'unset' : 'ok';
const id = (prefix, value) => `${prefix}-${String(value)}`;

export function normalizeGh(doc, options = {}) {
  if (typeof doc === 'string') doc = parseJsonSafe(doc);
  if (!isGitHubActionsRun(doc)) throw new Error('unrecognized GitHub Actions run: expected jobs[] with steps[]');
  const warnings = [];
  const jobs = doc.jobs;
  const maxSteps = options.maxSteps ?? MAX_STEPS;
  const totalSteps = jobs.reduce((n, j) => n + (j.steps || []).length, 0);
  const collapse = maxSteps > 0 && totalSteps > maxSteps;
  if (collapse) warnings.push(`large run: ${totalSteps} steps; showing only failed or cancelled steps as stations (pass --max-steps 0 to show all)`);
  const runStart = ns(doc.startedAt || doc.createdAt);
  if (runStart == null) throw new Error('GitHub Actions run is missing startedAt/createdAt');
  const spanData = [];
  const add = (s) => spanData.push(s);
  const jobRecords = new Map();
  const rootId = id('run', doc.databaseId || doc.url || doc.workflowName || 'unknown');
  const rootEnd = ns(doc.updatedAt || doc.startedAt || doc.createdAt) || runStart;
  const rootConclusion = doc.conclusion || doc.status;
  add({ spanId: rootId, parentId: null, service: doc.workflowName || doc.name || 'GitHub Actions', name: doc.displayTitle || doc.name || 'workflow run', startNs: runStart, endNs: rootEnd, status: statusFor(rootConclusion), kind: 'server', statusMessage: rootConclusion === 'failure' ? 'workflow failed' : undefined, attrs: {
    'ci.attempt': doc.attempt, 'ci.branch': doc.headBranch, 'ci.event': doc.event,
  }});
  for (const j of jobs) {
    const jobId = id('job', j.databaseId || j.name);
    const start = ns(j.startedAt) ?? runStart;
    const conclusion = j.conclusion || j.status;
    const end = conclusion === 'skipped' ? start : (ns(j.completedAt) ?? start);
    const job = { spanId: jobId, parentId: rootId, service: j.name, name: j.name, startNs: start, endNs: end, status: statusFor(conclusion), kind: 'internal', statusMessage: conclusion === 'failure' ? `job failed: ${j.name}` : conclusion === 'cancelled' ? `job cancelled: ${j.name}` : undefined, attrs: { 'ci.job': j.name, 'ci.conclusion': conclusion, 'ci.needs': (doc.needs && doc.needs[j.name]) || [], 'ci.attempt': doc.attempt, 'ci.branch': doc.headBranch, 'ci.event': doc.event } };
    add(job);
    const record = { job, steps: [] };
    jobRecords.set(j.name, record);
    let previousStepId = jobId;
    let previousEndNs = start;
    for (const [stepIndex, st] of (j.steps || []).entries()) {
      const conclusion = st.conclusion || st.status;
      if (collapse && conclusion !== 'failure' && conclusion !== 'cancelled') continue;
      let startNs = ns(st.startedAt), endNs = ns(st.completedAt);
      if (conclusion === 'skipped') {
        // GitHub commonly omits timestamps for skipped steps. Keep their station
        // in the job-local chain at the preceding station's completion time.
        const pointNs = startNs ?? endNs ?? previousEndNs;
        startNs ??= pointNs;
        endNs ??= pointNs;
      } else if (startNs == null || endNs == null) {
        warnings.push(`step ${j.name}/${st.name} is missing startedAt or completedAt; skipped`);
        continue;
      }
      const stepId = id(`${jobId}-step`, st.number || stepIndex + 1);
      const step = { spanId: stepId, parentId: previousStepId, service: stepId, name: st.name, startNs, endNs: conclusion === 'skipped' ? startNs : endNs, status: statusFor(conclusion), kind: 'internal', statusMessage: conclusion === 'failure' ? `step failed: ${st.name}` : conclusion === 'cancelled' ? `step cancelled: ${st.name}` : undefined, attrs: { 'ci.job': j.name, 'ci.step.name': st.name, 'ci.step.number': st.number ?? stepIndex + 1, 'ci.conclusion': conclusion, 'ci.attempt': doc.attempt, 'ci.branch': doc.headBranch, 'ci.event': doc.event } };
      add(step);
      record.steps.push(step);
      previousStepId = stepId;
      previousEndNs = step.endNs;
    }
  }
  // A dependent job keeps one parent: the last station of the dependency that
  // finished latest. The other dependency stops are recorded separately for
  // the CI renderer, which can draw them without changing the trace tree.
  for (const record of jobRecords.values()) {
    const needs = record.job.attrs['ci.needs'];
    if (!Array.isArray(needs) || needs.length === 0) continue;
    const candidates = needs.map((name) => jobRecords.get(name)).filter(Boolean);
    const latest = candidates.reduce((best, candidate) => !best || candidate.job.endNs > best.job.endNs ? candidate : best, null);
    if (latest) {
      const latestStop = latest.steps[latest.steps.length - 1] || latest.job;
      record.job.parentId = latestStop.spanId;
      const extraStops = candidates
        .filter((candidate) => candidate !== latest)
        .map((candidate) => (candidate.steps[candidate.steps.length - 1] || candidate.job).spanId);
      if (extraStops.length) record.job.attrs['ci.needs.from'] = extraStops;
    }
  }
  const t0 = spanData.reduce((m, s) => s.startNs < m ? s.startNs : m, spanData[0].startNs);
  const spans = spanData.map((s) => ({ spanId: s.spanId, parentId: s.parentId, service: s.service, name: s.name, start: Number(s.startNs - t0) / 1e6, duration: Math.max(0, Number(s.endNs - s.startNs) / 1e6), status: s.status, kind: s.kind, ...(s.statusMessage ? { statusMessage: s.statusMessage } : {}), attrs: Object.fromEntries(Object.entries(s.attrs).filter(([, v]) => v != null)) })).sort((a, b) => a.start - b.start || (a.parentId ? 1 : -1));
  const trace = { traceId: String(doc.databaseId || doc.url || 'gh-run'), meta: { format: 'gh-actions', source: doc._comment || null, synthetic: /synthetic/i.test(doc._comment || ''), startUnixNs: String(t0), warnings }, spans };
  return validate(trace);
}

export function normalize(doc, options = {}) { return normalizeGh(doc, options); }

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const file = process.argv[2]; if (!file) throw new Error('usage: node normalize-gh.mjs <run.json>');
  const t = normalizeGh(readFileSync(file, 'utf8')); for (const w of t.meta.warnings) console.error('warning:', w); console.log(JSON.stringify(t, null, 2));
}
