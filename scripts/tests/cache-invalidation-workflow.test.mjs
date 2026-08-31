import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'yaml';
import { buildShardPlan } from '../plan-cache-invalidation.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const TEST_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'test-recalculate-scores.yml');
const AGGREGATE = join(REPO_ROOT, 'scripts', 'check-cache-invalidation-aggregate.sh');
const CORRELATED_ROOT_GUARD = join(REPO_ROOT, 'scripts', 'validate-correlated-sync-roots.mjs');

function section(workflow, start, end) {
  const startIndex = workflow.indexOf(start);
  assert.notEqual(startIndex, -1, `missing section: ${start}`);
  const endIndex = end ? workflow.indexOf(end, startIndex + start.length) : workflow.length;
  assert.notEqual(endIndex, -1, `missing section boundary: ${end}`);
  return workflow.slice(startIndex, endIndex);
}

function runAggregate({ plan = 'success', shards = 'success', scores = 'success' } = {}) {
  return spawnSync('/bin/bash', [AGGREGATE], {
    encoding: 'utf8',
    env: {
      ...process.env,
      CACHE_PLAN_RESULT: plan,
      CACHE_SHARD_RESULT: shards,
      SCORE_RESULT: scores,
    },
  });
}

test('publication provider writes use push as the only automatic trigger', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  assert.match(workflow, /^  push:/m);
  assert.match(workflow, /^  workflow_dispatch:/m);
  assert.doesNotMatch(workflow, /^  workflow_run:/m);
  assert.doesNotMatch(workflow, /github\.event\.workflow_run/);
  assert.match(workflow, /AgentCrew-Publication:/);
  assert.match(workflow, /Record durable publication provider result/);
  assert.match(workflow, /actions\/workflows\/on-pr-merge\.yml\/runs\?event=workflow_dispatch/);
  assert.match(workflow, /Wait for authoritative publication completion/);
  assert.match(workflow, /\.status \/\/ "".*completed/);
  assert.match(workflow, /\.conclusion \/\/ "".*success/);
  assert.match(workflow, /Correlated publication failed or completion is unknown/);
  assert.match(workflow, /Record durable correlated manual sync result/);
  assert.match(workflow, /status=completed&event=push/);
  assert.match(workflow, /actions\/runs\/\$run_id\/jobs/);
  assert.match(workflow, /Previous provider sync run .* lacks closed provider evidence/);
});

test('push-first and legacy-workflow-first orders admit one provider sync and one callback', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const parsed = parse(workflow);
  const trigger = parsed.on ?? parsed.true;
  const automaticTriggers = new Set(Object.keys(trigger).filter((name) => name !== 'workflow_dispatch'));
  assert.deepEqual([...automaticTriggers], ['push']);
  for (const sequence of [['push', 'workflow_run'], ['workflow_run', 'push']]) {
    const admitted = sequence.filter((event) => automaticTriggers.has(event));
    assert.deepEqual(admitted, ['push']);
  }
  assert.equal((workflow.match(/- name: Sync skills to Supabase/g) ?? []).length, 1);
  assert.equal((workflow.match(/- name: Notify skillstore - Published submissions/g) ?? []).length, 1);
  assert.ok(workflow.indexOf('- name: Wait for authoritative publication completion') < workflow.indexOf('- name: Sync skills to Supabase'));
  assert.ok(workflow.indexOf('- name: Sync skills to Supabase') < workflow.indexOf('- name: Upload provider-complete synced slugs artifact'));
  assert.ok(workflow.indexOf('- name: Upload provider-complete synced slugs artifact') < workflow.indexOf('- name: Notify skillstore - Published submissions'));
});

test('workflow matrix is artifact-backed, one-Skill, and serial', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const planJob = section(workflow, '  plan-cache-invalidation:', '  cache-invalidate-shard:');
  const shardJob = section(workflow, '  cache-invalidate-shard:', '  cache-invalidate:');

  assert.match(planJob, /name: synced-slugs/);
  assert.match(planJob, /run: node \.\/scripts\/plan-cache-invalidation\.mjs plan/);
  assert.match(planJob, /matrix: \$\{\{ steps\.plan\.outputs\.matrix \}\}/);
  assert.doesNotMatch(planJob, /synced_slugs.*GITHUB_OUTPUT|slugs.*GITHUB_OUTPUT/i);

  assert.match(shardJob, /matrix: \$\{\{ fromJSON\(needs\.plan-cache-invalidation\.outputs\.matrix\) \}\}/);
  assert.match(planJob, /--shard-size 1 --max-shards 25/);
  assert.match(shardJob, /max-parallel: 1/);
  assert.match(shardJob, /fail-fast: false/);
  assert.doesNotMatch(shardJob, /continue-on-error:/);
  assert.match(shardJob, /timeout-minutes: 5/);
  assert.match(shardJob, /name: synced-slugs/);
  assert.match(shardJob, /--shard-id "\$\{\{ matrix\.shard \}\}"/);
  assert.match(shardJob, /SLUGS_FILE: .*cache-invalidation-shard\.txt/);
  assert.match(shardJob, /BATCH_SIZE: ['"]1['"]/);
  assert.match(shardJob, /MAX_ITEMS: ['"]1['"]/);
  assert.match(shardJob, /FALLBACK_CONCURRENCY: ['"]1['"]/);
  assert.match(shardJob, /FALLBACK_MAX_ATTEMPTS: ['"]1['"]/);
  assert.match(shardJob, /MAX_RUNTIME_SECONDS: ['"]240['"]/);
  assert.doesNotMatch(shardJob, /needs\.sync\.outputs\.synced_slugs/);
});

test('workflow rejects 26 sync targets before Supabase writes and removes full sync', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const detectJob = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');
  const admission = section(workflow, '      - name: Validate bounded sync admission', '      - name: Download skillstore-cli');
  const planJob = section(workflow, '  plan-cache-invalidation:', '  cache-invalidate-shard:');
  const shardSize = Number(planJob.match(/--shard-size (\d+)/)?.[1]);
  const maxShards = Number(planJob.match(/--max-shards (\d+)/)?.[1]);

  assert.doesNotMatch(workflow, /full_sync|find_all_skills/);
  assert.equal(shardSize, 1);
  assert.equal(maxShards, 25);
  assert.match(detectJob, /echo "target_count=\$TARGET_COUNT" >> \$GITHUB_OUTPUT/);
  assert.match(detectJob, /if \[ "\$TARGET_COUNT" -le 25 \]; then\s+echo "changed_skills=\$CHANGED" >> \$GITHUB_OUTPUT/);
  assert.match(admission, /MAX_SYNC_SKILLS=25/);
  assert.match(admission, /TARGET_COUNT: \$\{\{ steps\.changes\.outputs\.target_count \}\}/);
  assert.doesNotMatch(admission, /CHANGED_SKILLS/);
  assert.match(admission, /exceeds the production limit \$MAX_SYNC_SKILLS/);
  assert.ok(
    workflow.indexOf('      - name: Validate bounded sync admission')
      < workflow.indexOf('      - name: Sync skills to Supabase'),
    'bounded admission must be checked before any Supabase write',
  );
  assert.doesNotMatch(detectJob, /mode=full/);

  const runMarker = '        run: |\n';
  const runStart = admission.indexOf(runMarker) + runMarker.length;
  const script = admission.slice(runStart).split('\n').map((line) => line.replace(/^ {10}/, '')).join('\n');
  const runAdmission = (count) => spawnSync('/bin/bash', ['-c', script], {
    encoding: 'utf8',
    env: {
      ...process.env,
      TARGET_COUNT: String(count),
    },
  });
  const accepted = runAdmission(25);
  assert.equal(accepted.status, 0, `${accepted.stdout}\n${accepted.stderr}`);
  const rejected = runAdmission(26);
  assert.equal(rejected.status, 1);
  assert.match(`${rejected.stdout}\n${rejected.stderr}`, /Sync target count 26 exceeds the production limit 25/);
  const oversized = runAdmission(1000000);
  assert.equal(oversized.status, 1);
  assert.match(`${oversized.stdout}\n${oversized.stderr}`, /Sync target count 1000000 exceeds the production limit 25/);

  const plan = buildShardPlan(
    Array.from({ length: 25 }, (_, index) => `bounded-sync-${index}`),
    { shardSize, maxShards },
  );
  assert.equal(plan.shardCount, 25);
  assert.ok(plan.shards.every((shard) => shard.length === 1));
});

test('workflow treats an empty sync as a no-op before planning or invalidation', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const planJob = section(workflow, '  plan-cache-invalidation:', '  cache-invalidate-shard:');
  const aggregateJob = section(workflow, '  cache-invalidate:', '  # ENGLISH CACHE FINALIZER');

  assert.match(planJob, /if: needs\.sync\.outputs\.skip_sync != 'true'/);
  assert.match(aggregateJob, /needs\.sync\.outputs\.skip_sync != 'true'/);
  assert.match(workflow, /No skills to sync[\s\S]*skip_sync=true/);
});

test('incremental detection resolves both sides from pinned Git trees', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const detectJob = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');

  assert.match(detectJob, /node \.\/scripts\/detect-changed-skills\.mjs/);
  assert.match(detectJob, /node \.\/scripts\/resolve-manual-skills\.mjs/);
  assert.match(detectJob, /INPUT_SLUGS: \$\{\{ inputs\.slugs \}\}/);
  assert.match(detectJob, /HEAD_SHA: \$\{\{ github\.sha \}\}/);
  assert.doesNotMatch(detectJob.slice(detectJob.indexOf('run: |')), /\$\{\{\s*inputs\./);
  assert.match(detectJob, /--commit "\$SYNC_COMMIT_SHA"/);
  assert.match(detectJob, /--base "\$BASE_SHA"/);
  assert.match(detectJob, /--head "\$HEAD_SHA"/);
  assert.doesNotMatch(detectJob, /get_skill_slug|\[ -f "skills\/\$first/);
});

test('incremental detection subtracts only verified successful manual recovery artifacts', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const lastSync = section(workflow, '      - name: Find last successful sync commit', '      - name: Detect changed skills');
  const detect = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');

  assert.match(lastSync, /if: inputs\.slugs == ''/);
  assert.match(lastSync, /status=completed&event=push/);
  assert.match(lastSync, /Sync skills to Supabase/);
  assert.match(lastSync, /SYNC_CONCLUSION.*success/);
  assert.match(lastSync, /lacks closed provider evidence/);
  assert.match(lastSync, /did not establish authoritative publication success/);
  assert.doesNotMatch(lastSync, /event=workflow_dispatch/);
  assert.match(lastSync, /set -euo pipefail/);
  assert.match(lastSync, /git merge-base --is-ancestor "\$LAST_SHA"/);
  assert.match(lastSync, /refusing an incomplete fallback/);
  assert.doesNotMatch(lastSync, /HEAD~1|2>\/dev\/null \|\| echo/);
  assert.match(detect, /status=completed&event=workflow_dispatch/);
  assert.match(detect, /Correlated provider sync run .* lacks complete provider and downstream evidence/);
  assert.match(lastSync, /completed the provider write but downstream effects are incomplete/);
  assert.match(detect, /exactly one provider-complete synced-slugs artifact/);
  assert.match(detect, /synced-slugs/);
  assert.match(detect, /sha256sum/);
  assert.match(detect, /artifact_digest/);
  assert.match(detect, /--recoveries "\$RECOVERIES_FILE"/);
  assert.match(detect, /MAX_RECOVERY_RUNS=100/);
  assert.match(workflow, /retention-days: 30/);
});

test('correlated provider sync verifies exact root versions and uses the correlated merge commit', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const correlation = section(workflow, '      - name: Validate trusted sync correlation', '      - name: Generate GitHub App Token');
  const detect = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');
  const materialize = section(workflow, '      - name: Materialize changed skills', '      - name: Sync skills to Supabase');
  const sync = section(workflow, '      - name: Sync skills to Supabase', '      - name: Reconcile durable security change events');
  assert.match(correlation, /id: trusted-correlation/);
  assert.match(correlation, /validate-correlated-sync-roots\.mjs/);
  assert.match(correlation, /sync_commit_sha=\$MERGE_COMMIT_SHA/);
  assert.match(detect, /SYNC_COMMIT_SHA: \$\{\{ steps\.trusted-correlation\.outputs\.sync_commit_sha \}\}/);
  assert.match(detect, /--commit "\$SYNC_COMMIT_SHA"/);
  assert.match(materialize, /--commit "\$SYNC_COMMIT_SHA"/);
  assert.match(sync, /--marketplace-commit "\$SYNC_COMMIT_SHA"/);
  assert.match(sync, /\.meta\.slug/);
  assert.match(sync, /materialized Skill report is missing or unsafe/);
  assert.match(sync, /diff -u expected-synced-slugs\.txt synced-slugs\.txt/);

  const tmp = mkdtempSync(join(tmpdir(), 'marketplace-correlated-roots-'));
  try {
    const git = (...args) => spawnSync('git', args, { cwd: tmp, encoding: 'utf8' });
    assert.equal(git('init').status, 0);
    assert.equal(git('config', 'user.email', 'test@example.com').status, 0);
    assert.equal(git('config', 'user.name', 'Test').status, 0);
    assert.equal(spawnSync('/bin/mkdir', ['-p', join(tmp, 'skills/example/skill'), join(tmp, 'skills/other/skill')]).status, 0);
    assert.equal(spawnSync('/bin/sh', ['-c', "printf 'v1\\n' > skills/example/skill/SKILL.md; printf '{}\\n' > skills/example/skill/skill-report.json; printf 'o1\\n' > skills/other/skill/SKILL.md"], { cwd: tmp }).status, 0);
    assert.equal(git('add', '.').status, 0);
    assert.equal(git('commit', '-m', 'merge').status, 0);
    const mergeSha = git('rev-parse', 'HEAD').stdout.trim();
    assert.equal(spawnSync('/bin/sh', ['-c', "printf 'o2\\n' > skills/other/skill/SKILL.md"], { cwd: tmp }).status, 0);
    assert.equal(git('commit', '-am', 'unrelated').status, 0);
    const unrelatedSha = git('rev-parse', 'HEAD').stdout.trim();
    const unchanged = spawnSync(process.execPath, [CORRELATED_ROOT_GUARD, '--merge', mergeSha, '--current', unrelatedSha, '--slugs', 'example/skill'], { cwd: tmp, encoding: 'utf8' });
    assert.equal(unchanged.status, 0, `${unchanged.stdout}\n${unchanged.stderr}`);
    assert.equal(spawnSync('/bin/sh', ['-c', "printf 'v2\\n' > skills/example/skill/SKILL.md"], { cwd: tmp }).status, 0);
    assert.equal(git('commit', '-am', 'same root changed').status, 0);
    const changedSha = git('rev-parse', 'HEAD').stdout.trim();
    const changed = spawnSync(process.execPath, [CORRELATED_ROOT_GUARD, '--merge', mergeSha, '--current', changedSha, '--slugs', 'example/skill'], { cwd: tmp, encoding: 'utf8' });
    assert.notEqual(changed.status, 0);
    assert.match(`${changed.stdout}\n${changed.stderr}`, /changed after the marker-bound merge/);
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
});

test('manual slug sync carries an optional exact correlation without requiring an incremental baseline', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  assert.match(workflow, /correlation_id:/);
  assert.match(workflow, /format\('Provider sync \{0\}', inputs\.correlation_id\)/);
  const lastSync = section(workflow, '      - name: Find last successful sync commit', '      - name: Detect changed skills');
  assert.match(lastSync, /if: inputs\.slugs == ''/);
  const correlation = section(workflow, '      - name: Validate trusted sync correlation', '      - name: Generate GitHub App Token');
  assert.match(correlation, /\^source-monitor-pr-\(\[1-9\]\[0-9\]\*\)-\(\[0-9a-f\]\{40\}\)-\(\[0-9a-f\]\{40\}\)-\(\[0-9a-f\]\{64\}\)\$/);
  assert.match(correlation, /MERGE_COMMIT_SHA/);
  assert.match(correlation, /Provider sync correlation does not match the authoritative merged source-monitor PR/);
  assert.match(correlation, /Correlated merge is not on the current main lineage/);
  assert.match(correlation, /Provider sync correlation is not bound to the exact canonical root set/);
  assert.match(correlation, /agentcrew-dispatch-outbox\/provider-sync/);
  assert.match(correlation, /length > 0 and length <= 8/);
  assert.match(correlation, /"\$EVENT_NAME" != 'workflow_dispatch'/);
  assert.match(correlation, /"\$GIT_REF" != 'refs\/heads\/main'/);
  const detect = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');
  assert.match(detect, /if \[ -n "\$INPUT_SLUGS" \]/);
  assert.ok(detect.indexOf('Specific slugs requested') < detect.indexOf('Comparing HEAD against'));
  const callbacks = section(workflow, '      - name: Resolve published submissions', '      - name: Record durable publication provider result');
  assert.match(callbacks, /!startsWith\(inputs\.correlation_id, 'source-monitor-pr-'\)/);
});

test('manual recovery resolves its original submission and fails closed on callback errors', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const resolvePublished = section(workflow, '      - name: Resolve published submissions', '      - name: Notify skillstore - Published submissions');
  const notifyPublished = section(workflow, '      - name: Notify skillstore - Published submissions', '      - name: Record durable publication provider result');

  assert.match(resolvePublished, /SYNC_MODE: \$\{\{ steps\.changes\.outputs\.mode \}\}/);
  assert.match(resolvePublished, /CHANGED_SKILLS: \$\{\{ steps\.changes\.outputs\.changed_skills \}\}/);
  assert.match(resolvePublished, /syncMode === 'manual-slugs'/);
  assert.match(resolvePublished, /--grep=\\\\\[submission:/);
  assert.doesNotMatch(resolvePublished, /BASE_SHA \|\| 'HEAD~1'/);
  assert.match(notifyPublished, /curl --fail-with-body -sS/);
  assert.match(notifyPublished, /callback secrets are not configured[\s\S]*exit 1/);
  assert.doesNotMatch(notifyPublished, /Failed to notify skillstore|\|\| echo/);
});

test('sync uses a blobless sparse checkout before invoking pinned-tree resolvers', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const checkout = section(workflow, '      - name: Clear inherited sync checkout', '      - name: Normalize pinned sync runtime checkout');
  const runtime = section(workflow, '      - name: Normalize pinned sync runtime checkout', '      - name: Generate GitHub App Token');
  const detect = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');

  assert.match(checkout, /for CHECKOUT_ATTEMPT in 1 2 3/);
  assert.match(checkout, /--filter=blob:none/);
  assert.match(checkout, /sparse-checkout init --no-cone/);
  assert.match(checkout, /scripts\/refresh-security-research-stats\.sh/);
  assert.match(checkout, /checkout --detach --force "\$EXPECTED_SHA"/);
  assert.match(runtime, /checked_out_sha=\$\(git rev-parse HEAD\)/);
  assert.doesNotMatch(runtime, /sparse-checkout disable|git reset --hard/);
  assert.match(runtime, /git config --bool core\.sparseCheckout/);
  assert.match(runtime, /scripts\/resolve-manual-skills\.mjs/);
  assert.match(runtime, /scripts\/detect-changed-skills\.mjs/);
  assert.match(runtime, /scripts\/materialize-changed-skills\.mjs/);
  assert.match(runtime, /scripts\/refresh-security-research-stats\.sh/);
  assert.match(runtime, /\.github\/actions\/download-skillstore-cli\/action\.yml/);
  assert.match(runtime, /git rev-parse "\$EXPECTED_SHA:\$required_path"/);
  assert.match(runtime, /git hash-object "\$required_path"/);
  assert.ok(workflow.indexOf('      - name: Normalize pinned sync runtime checkout') < workflow.indexOf('      - name: Detect changed skills'));
  assert.match(detect, /node \.\/scripts\/resolve-manual-skills\.mjs/);
  assert.doesNotMatch(detect.slice(detect.indexOf('run: |')), /\$\{\{\s*inputs\./);
});

test('sync materializes only the detected paths from the exact workflow commit', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const materialize = section(workflow, '      - name: Materialize changed skills', '      - name: Sync skills to Supabase');
  const sync = section(workflow, '      - name: Sync skills to Supabase', '      - name: Remove generated report evidence');

  assert.ok(
    workflow.indexOf('      - name: Download skillstore-cli')
      < workflow.indexOf('      - name: Materialize changed skills'),
    'materialization must run after the helper checkout is available',
  );
  assert.match(materialize, /CHANGED_SKILLS: \$\{\{ steps\.changes\.outputs\.changed_skills \}\}/);
  assert.match(materialize, /node \.\/scripts\/materialize-changed-skills\.mjs/);
  assert.match(materialize, /SYNC_COMMIT_SHA: \$\{\{ steps\.trusted-correlation\.outputs\.sync_commit_sha \}\}/);
  assert.match(materialize, /--commit "\$SYNC_COMMIT_SHA"/);
  assert.match(materialize, /--skills "\$CHANGED_SKILLS"/);
  assert.doesNotMatch(materialize, /checkout\s+\.\s*$|sparse-checkout disable|git clean/mi);
  assert.match(sync, /skill sync[\s\S]*--slugs "\$paths"/);
  assert.match(sync, /--marketplace-commit "\$SYNC_COMMIT_SHA"/);
});

test('sync writes are single-concurrency, single-attempt, and wall-clock bounded', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const syncStep = section(workflow, '      - name: Sync skills to Supabase', '      - name: Reconcile durable security change events');

  assert.match(syncStep, /Sync attempt 1\/1/);
  assert.match(syncStep, /run_sync_once "\$SKILL_PATHS" 1/);
  assert.doesNotMatch(syncStep, /CONCURRENCY=(?:3|10)/);
  assert.doesNotMatch(syncStep, /MAX_SYNC_ATTEMPTS|retrying affected skills/);
  assert.match(syncStep, /timeout --signal=TERM --kill-after=30s 60m/);
  assert.match(syncStep, /--concurrency "\$concurrency"/);
});

test('sync downloads the security-event-capable CLI release', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const download = section(workflow, '      - name: Download skillstore-cli', '      - name: Sync skills to Supabase');

  assert.match(download, /version: '2\.4\.4'/);
  assert.match(download, /minimum-version: '2\.4\.4'/);
});

test('one permanently failed shard makes the aggregate fail closed', () => {
  const success = runAggregate();
  assert.equal(success.status, 0, success.stderr);

  for (const failedResult of ['failure', 'cancelled', 'skipped']) {
    const failed = runAggregate({ shards: failedResult });
    assert.notEqual(failed.status, 0, `matrix result ${failedResult} must fail closed`);
    assert.match(failed.stderr, /Cache invalidation did not complete successfully/);
  }
});

test('CI tracks and executes the planner, aggregate guard, and full script suite', () => {
  const workflow = readFileSync(TEST_WORKFLOW, 'utf8');

  assert.match(workflow, /scripts\/plan-cache-invalidation\.mjs/);
  assert.match(workflow, /scripts\/detect-changed-skills\.mjs/);
  assert.match(workflow, /scripts\/materialize-changed-skills\.mjs/);
  assert.match(workflow, /scripts\/resolve-manual-skills\.mjs/);
  assert.match(workflow, /scripts\/check-cache-invalidation-aggregate\.sh/);
  assert.match(workflow, /node --check scripts\/plan-cache-invalidation\.mjs/);
  assert.match(workflow, /node --check scripts\/detect-changed-skills\.mjs/);
  assert.match(workflow, /node --check scripts\/materialize-changed-skills\.mjs/);
  assert.match(workflow, /node --check scripts\/resolve-manual-skills\.mjs/);
  assert.match(workflow, /bash -n scripts\/check-cache-invalidation-aggregate\.sh/);
  assert.match(workflow, /node --test scripts\/tests\/\*\.test\.mjs/);
});

test('downstream finalizer and translation require aggregate success', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const aggregateJob = section(workflow, '  cache-invalidate:', '  # ENGLISH CACHE FINALIZER');
  const finalizerJob = section(workflow, '  finalize-english-cache:', '  # TRIGGER TRANSLATION');
  const triggerJob = section(workflow, '  trigger-translate:');

  assert.match(aggregateJob, /if: always\(\)/);
  assert.match(aggregateJob, /CACHE_SHARD_RESULT: \$\{\{ needs\.cache-invalidate-shard\.result \}\}/);
  assert.match(aggregateJob, /run: \.\/scripts\/check-cache-invalidation-aggregate\.sh/);
  assert.doesNotMatch(aggregateJob, /continue-on-error:/);

  assert.match(finalizerJob, /needs: \[sync, calculate-scores, cache-invalidate\]/);
  assert.match(finalizerJob, /needs\.cache-invalidate\.result == 'success'/);
  assert.match(triggerJob, /needs: \[sync, cache-invalidate, finalize-english-cache\]/);
  assert.match(
    triggerJob,
    /needs\.sync\.result == 'success' && needs\.cache-invalidate\.result == 'success'/,
  );
});
