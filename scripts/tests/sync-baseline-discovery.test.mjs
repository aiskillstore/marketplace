import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { parse } from 'yaml';
import { createHash } from 'node:crypto';

test('baseline uses unfiltered collection, newest completed push, and blocks newer partial effects', () => {
  const dir = mkdtempSync(join(tmpdir(), 'sync-baseline-'));
  try {
    const step = parse(readFileSync('.github/workflows/sync-to-supabase.yml', 'utf8')).jobs.sync.steps
      .find(s => s.name === 'Find last successful sync commit');
    const script = step.run.replaceAll('${{ github.repository }}', 'aiskillstore/marketplace')
      .replaceAll('${{ github.sha }}', 'f'.repeat(40));
    writeFileSync(join(dir, 'gh'), `#!${process.execPath}\n` + `
const fs = require('node:fs');
const endpoint = process.argv[3];
const data = JSON.parse(fs.readFileSync(process.env.FIXTURE));
if (endpoint.includes('/runs?')) {
  if (endpoint !== 'repos/aiskillstore/marketplace/actions/workflows/sync-to-supabase.yml/runs?per_page=100') process.exit(9);
  process.stdout.write(fs.readFileSync(process.env.FIXTURE));
} else {
  process.stdout.write(JSON.stringify(data.responses?.[endpoint] ?? {jobs:[{steps:[{name:'Wait for authoritative publication completion',conclusion:'success'},{name:'Sync skills to Supabase',conclusion:'success'}]}]}));
}
`, { mode: 0o755 });
    writeFileSync(join(dir, 'git'), '#!/bin/sh\nexit 0\n', { mode: 0o755 });
    const run = (id, day, extras = {}) => ({ id, head_sha: String(id).repeat(40), created_at: `2026-09-0${day}T00:00:00Z`, event: 'push', status: 'completed', conclusion: 'success', ...extras });
    const fixture = join(dir, 'runs.json'), output = join(dir, 'output');
    const execute = (runs, responses) => {
      writeFileSync(fixture, JSON.stringify({ workflow_runs: runs, responses }));
      writeFileSync(output, '');
      return spawnSync('bash', ['-c', script], { encoding: 'utf8', env: { ...process.env, PATH: `${dir}:${process.env.PATH}`, FIXTURE: fixture, GITHUB_OUTPUT: output } });
    };
    let result = execute([run(1, 1), run(4, 4, { status: 'in_progress' }), run(3, 3, { event: 'workflow_dispatch' }), run(2, 2)]);
    assert.equal(result.status, 0, result.stderr);
    assert.match(readFileSync(output, 'utf8'), new RegExp(`base_sha=${'2'.repeat(40)}`));
    result = execute([run(1, 1), run(2, 2, { conclusion: 'failure' })]);
    assert.notEqual(result.status, 0);
    assert.match(result.stdout, /downstream effects are incomplete/);
    assert.equal(readFileSync(output, 'utf8'), '');
    const failed = run(2, 2, { conclusion: 'failure', run_attempt: 1 });
    const correlation = `source-monitor-pr-12-${'a'.repeat(40)}-${failed.head_sha}-${'b'.repeat(64)}`;
    const recovery = run(3, 3, { event: 'workflow_dispatch', run_attempt: 1,
      head_branch: 'main', head_repository: { full_name: 'aiskillstore/marketplace' },
      path: '.github/workflows/sync-to-supabase.yml', display_title: `Provider sync ${correlation}` });
    const prefix = 'repos/aiskillstore/marketplace';
    const originalJobs = { total_count: 1, jobs: [{ steps: [
      { name: 'Wait for authoritative publication completion', conclusion: 'success' },
      { name: 'Sync skills to Supabase', conclusion: 'failure' },
    ] }] };
    const responses = {
      [`${prefix}/actions/runs/2/jobs?per_page=100`]: originalJobs,
      [`${prefix}/actions/runs/2/attempts/1/jobs?per_page=100`]: originalJobs,
      [`${prefix}/git/commits/${failed.head_sha}`]: { parents: [{ sha: '1'.repeat(40) }, { sha: 'a'.repeat(40) }] },
      [`${prefix}/actions/runs/3/attempts/1/jobs?per_page=100`]: { total_count: 1, jobs: [{ steps:
        ['Validate trusted sync correlation', 'Verify durable provider sync dispatch outbox', 'Sync skills to Supabase',
          'Upload provider-complete synced slugs artifact', 'Record durable correlated manual sync result']
          .map(name => ({ name, conclusion: 'success' })) }] },
      [`${prefix}/commits/${failed.head_sha}/status`]: { statuses: [{ state: 'success',
        context: `agentcrew/provider-sync/${createHash('sha256').update(correlation).digest('hex')}`,
        target_url: 'https://github.com/aiskillstore/marketplace/actions/runs/3' }] },
    };
    result = execute([recovery, failed, run(1, 1)], responses);
    assert.equal(result.status, 0, result.stderr);
    assert.match(readFileSync(output, 'utf8'), new RegExp(`base_sha=${failed.head_sha}`));
    assert.doesNotMatch(readFileSync(output, 'utf8'), new RegExp(`base_sha=${recovery.head_sha}`));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
