import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildShardPlan } from '../plan-cache-invalidation.mjs';

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const TEST_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'test-recalculate-scores.yml');
const AGGREGATE = join(REPO_ROOT, 'scripts', 'check-cache-invalidation-aggregate.sh');

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

test('workflow matrix is artifact-backed, id-only, bounded, and max-parallel 3', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const planJob = section(workflow, '  plan-cache-invalidation:', '  cache-invalidate-shard:');
  const shardJob = section(workflow, '  cache-invalidate-shard:', '  cache-invalidate:');

  assert.match(planJob, /name: synced-slugs/);
  assert.match(planJob, /run: node \.\/scripts\/plan-cache-invalidation\.mjs plan/);
  assert.match(planJob, /matrix: \$\{\{ steps\.plan\.outputs\.matrix \}\}/);
  assert.doesNotMatch(planJob, /synced_slugs.*GITHUB_OUTPUT|slugs.*GITHUB_OUTPUT/i);

  assert.match(shardJob, /matrix: \$\{\{ fromJSON\(needs\.plan-cache-invalidation\.outputs\.matrix\) \}\}/);
  assert.match(shardJob, /max-parallel: 3/);
  assert.match(shardJob, /fail-fast: false/);
  assert.doesNotMatch(shardJob, /continue-on-error:/);
  assert.match(shardJob, /timeout-minutes: 25/);
  assert.match(shardJob, /name: synced-slugs/);
  assert.match(shardJob, /--shard-id "\$\{\{ matrix\.shard \}\}"/);
  assert.match(shardJob, /SLUGS_FILE: .*cache-invalidation-shard\.txt/);
  assert.match(shardJob, /MAX_ITEMS: ['"]100['"]/);
  assert.doesNotMatch(shardJob, /needs\.sync\.outputs\.synced_slugs/);
});

test('workflow full_sync inputs above 100 use the configured bounded matrix', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const detectJob = section(workflow, '      - name: Detect changed skills', '      - name: Download skillstore-cli');
  const capacityGuard = section(workflow, '      - name: Validate cache matrix capacity', '      - name: Download skillstore-cli');
  const planJob = section(workflow, '  plan-cache-invalidation:', '  cache-invalidate-shard:');
  const shardJob = section(workflow, '  cache-invalidate-shard:', '  cache-invalidate:');
  const shardSize = Number(planJob.match(/--shard-size (\d+)/)?.[1]);
  const maxShards = Number(planJob.match(/--max-shards (\d+)/)?.[1]);

  assert.match(detectJob, /inputs\.full_sync.*true[\s\S]*CHANGED=\$\(find_all_skills/s);
  assert.equal(shardSize, 100);
  assert.equal(maxShards, 256);
  assert.match(capacityGuard, /MAX_CACHE_ITEMS=25600/);
  assert.match(capacityGuard, /exceeds cache matrix capacity/);
  assert.ok(
    workflow.indexOf('      - name: Validate cache matrix capacity')
      < workflow.indexOf('      - name: Sync skills to Supabase'),
    'matrix capacity must be checked before any Supabase write',
  );
  assert.match(shardJob, /max-parallel: 3/);

  for (const [slugCount, expectedShards] of [[101, 2], [5263, 53]]) {
    const plan = buildShardPlan(
      Array.from({ length: slugCount }, (_, index) => `full-sync-${index}`),
      { shardSize, maxShards },
    );
    assert.equal(plan.shardCount, expectedShards);
    assert.ok(plan.shards.every((shard) => shard.length >= 1 && shard.length <= 100));
  }
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
  assert.match(detectJob, /--base "\$BASE_SHA"/);
  assert.match(detectJob, /--head "\$\{\{ github\.sha \}\}"/);
  assert.doesNotMatch(detectJob, /get_skill_slug|\[ -f "skills\/\$first/);
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
  assert.match(materialize, /--commit "\$GITHUB_SHA"/);
  assert.match(materialize, /--skills "\$CHANGED_SKILLS"/);
  assert.doesNotMatch(materialize, /checkout\s+\.\s*$|sparse-checkout disable|git clean/mi);
  assert.match(sync, /skill sync --slugs "\$paths"/);
  assert.match(sync, /--marketplace-commit "\$GITHUB_SHA"/);
});

test('sync downloads the canonical-hash CLI release', () => {
  const workflow = readFileSync(WORKFLOW, 'utf8');
  const download = section(workflow, '      - name: Download skillstore-cli', '      - name: Sync skills to Supabase');

  assert.match(download, /version: '2\.2\.1'/);
  assert.match(download, /minimum-version: '2\.2\.1'/);
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
  assert.match(workflow, /scripts\/check-cache-invalidation-aggregate\.sh/);
  assert.match(workflow, /node --check scripts\/plan-cache-invalidation\.mjs/);
  assert.match(workflow, /node --check scripts\/detect-changed-skills\.mjs/);
  assert.match(workflow, /node --check scripts\/materialize-changed-skills\.mjs/);
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
