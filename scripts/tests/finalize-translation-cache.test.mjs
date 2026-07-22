import assert from 'node:assert/strict';
import {
  chmodSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  buildFinalizationPlan,
  executeFinalization,
  FinalizerError,
  groupsFromTranslationResults,
  planChecksum,
  verifyFinalizationPlan,
} from '../finalize-translation-cache.mjs';

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');

function workflowRunScript(workflow, stepName) {
  const marker = `      - name: ${stepName}\n`;
  const start = workflow.indexOf(marker);
  assert.notEqual(start, -1, `workflow step not found: ${stepName}`);
  const runMarker = '        run: |\n';
  const runStart = workflow.indexOf(runMarker, start);
  assert.notEqual(runStart, -1, `run block not found: ${stepName}`);
  const bodyStart = runStart + runMarker.length;
  const tail = workflow.slice(bodyStart);
  const boundary = tail.search(/\n(?:      - name:|  [a-zA-Z][a-zA-Z0-9_-]*:)/);
  const body = tail.slice(0, boundary === -1 ? tail.length : boundary);
  return body
    .split('\n')
    .map((line) => line.startsWith('          ') ? line.slice(10) : line)
    .join('\n');
}

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

function closureResponse({ locale = 'fr', all = [], warmable = all, preflight = true } = {}) {
  return {
    preflight,
    type: 'skills',
    slugs: ['alpha'],
    locales: [locale],
    closure: {
      dependentPacks: { all, warmable, overflow: false, cap: 100 },
    },
    invalidated: {
      total: 0,
      page: 0,
      api: 0,
      artifacts: 0,
      listVersionBumped: false,
      listMaxStaleSeconds: 86400,
    },
  };
}

test('extracts only successful mutated locale pairs and deduplicates slugs', () => {
  const groups = groupsFromTranslationResults([{ languages: [
    {
      language: 'fr',
      skills: [
        { slug: 'alpha', status: 'translated' },
        { slug: 'alpha', status: 'stale_retranslated' },
        { slug: 'beta', status: 'error' },
        { slug: 'gamma', status: 'skipped' },
      ],
    },
    { language: 'ja', skills: [{ slug: 'delta', status: 'stale_retranslated' }] },
  ] }]);
  assert.deepEqual(groups, [
    { locale: 'fr', slugs: ['alpha'] },
    { locale: 'ja', slugs: ['delta'] },
  ]);
});

test('all skipped translation results produce an empty no-op plan', async () => {
  const groups = groupsFromTranslationResults([{ languages: [
    { language: 'fr', skills: [{ slug: 'alpha', status: 'skipped' }] },
  ] }]);
  let calls = 0;
  const plan = await buildFinalizationPlan({
    groups,
    siteUrl: 'https://skillstore.test',
    cacheSecret: 'secret',
    fetchImpl: async () => { calls++; return jsonResponse({}); },
  });
  assert.equal(plan, null);
  assert.equal(calls, 0);
});

test('materializes exact Skill and anonymous-warmable Pack targets', async () => {
  const requests = [];
  const plan = await buildFinalizationPlan({
    groups: [{ locale: 'fr', slugs: ['alpha'] }],
    siteUrl: 'https://skillstore.test',
    cacheSecret: 'secret',
    fetchImpl: async (_url, init) => {
      requests.push(JSON.parse(init.body));
      return jsonResponse(closureResponse({
        all: ['private-pack', 'public-pack'],
        warmable: ['public-pack'],
      }));
    },
  });

  assert.equal(requests.length, 1);
  assert.deepEqual(requests[0], {
    type: 'skills',
    slugs: ['alpha'],
    locales: ['fr'],
    invalidateApi: true,
    invalidateLists: false,
    invalidateArtifacts: false,
    invalidateDependentPacks: true,
    preflight: true,
  });
  assert.deepEqual(plan.targets, [
    { resource: 'packs', slug: 'public-pack', locale: 'fr' },
    { resource: 'skills', slug: 'alpha', locale: 'fr' },
  ]);
  assert.deepEqual(plan.invalidateOnly, [
    { resource: 'packs', slug: 'private-pack', locale: 'fr', reason: 'not_anonymous_warmable' },
  ]);
  assert.equal(plan.counts.skills, 1);
  assert.equal(plan.counts.packs, 2);
  assert.equal(plan.counts.targets, 2);
  assert.equal(plan.budgets.requests, 66);
  assert.equal(verifyFinalizationPlan(plan), plan);
});

test('rejects 26 Skills before making a preflight request', async () => {
  let calls = 0;
  await assert.rejects(
    buildFinalizationPlan({
      groups: [{ locale: 'fr', slugs: Array.from({ length: 26 }, (_, index) => `skill-${index}`) }],
      siteUrl: 'https://skillstore.test',
      cacheSecret: 'secret',
      fetchImpl: async () => { calls++; return jsonResponse(closureResponse()); },
    }),
    /26 Skills; cap is 25/
  );
  assert.equal(calls, 0);
});

test('rejects Pack and target amplification after preflight without truncation', async () => {
  const packs = Array.from({ length: 101 }, (_, index) => `pack-${index}`);
  await assert.rejects(
    buildFinalizationPlan({
      groups: [{ locale: 'fr', slugs: ['alpha'] }],
      siteUrl: 'https://skillstore.test',
      cacheSecret: 'secret',
      fetchImpl: async () => jsonResponse(closureResponse({ all: packs, warmable: packs })),
    }),
    /101 Packs; cap is 100/
  );

  const targets = Array.from({ length: 250 }, (_, index) => `pack-${index}`);
  await assert.rejects(
    buildFinalizationPlan({
      groups: [{ locale: 'fr', slugs: ['alpha'] }],
      siteUrl: 'https://skillstore.test',
      cacheSecret: 'secret',
      caps: { packs: 300, targets: 250, requestBudget: 100_000, byteBudget: 10_000_000_000 },
      fetchImpl: async () => jsonResponse(closureResponse({ all: targets, warmable: targets })),
    }),
    /251 resource-locale targets; cap is 250/
  );
});

test('detects immutable plan tampering', async () => {
  const plan = await buildFinalizationPlan({
    groups: [{ locale: 'fr', slugs: ['alpha'] }],
    siteUrl: 'https://skillstore.test',
    cacheSecret: 'secret',
    fetchImpl: async () => jsonResponse(closureResponse()),
  });
  const tampered = { ...plan, targets: [{ resource: 'skills', slug: 'other', locale: 'fr' }] };
  assert.notEqual(planChecksum(tampered), plan.checksum);
  assert.throws(() => verifyFinalizationPlan(tampered), /checksum mismatch/);
});

test('closure drift stops execution before warming', async () => {
  const bodies = [];
  await assert.rejects(
    executeFinalization({
      groups: [{ locale: 'fr', slugs: ['alpha'] }],
      siteUrl: 'https://skillstore.test',
      cacheSecret: 'secret',
      fetchImpl: async (_url, init) => {
        const body = JSON.parse(init.body);
        bodies.push(body);
        if (body.preflight) {
          return jsonResponse(closureResponse({ all: [], warmable: [], preflight: true }));
        }
        return jsonResponse(closureResponse({ all: ['new-pack'], warmable: ['new-pack'], preflight: false }));
      },
      warmFetchImpl: async () => {
        throw new Error('warming must not start after closure drift');
      },
    }),
    (error) => error instanceof FinalizerError && /HTTP 409|closure drift|closure.*execution/i.test(error.message)
  );
  assert.equal(bodies.length, 2);
  assert.deepEqual(bodies[1].expectedDependentPacks, []);
  assert.deepEqual(bodies[1].expectedWarmableDependentPacks, []);
});

test('warmability drift stops execution before the frozen target plan can warm', async () => {
  const bodies = [];
  await assert.rejects(
    executeFinalization({
      groups: [{ locale: 'fr', slugs: ['alpha'] }],
      siteUrl: 'https://skillstore.test',
      cacheSecret: 'secret',
      fetchImpl: async (_url, init) => {
        const body = JSON.parse(init.body);
        bodies.push(body);
        if (body.preflight) {
          return jsonResponse(closureResponse({
            all: ['visibility-changed-pack'],
            warmable: [],
            preflight: true,
          }));
        }
        return jsonResponse(closureResponse({
          all: ['visibility-changed-pack'],
          warmable: ['visibility-changed-pack'],
          preflight: false,
        }));
      },
      warmFetchImpl: async () => {
        throw new Error('warming must not start after warmability drift');
      },
    }),
    (error) => error instanceof FinalizerError && /warmability drifted/i.test(error.message)
  );
  assert.equal(bodies.length, 2);
  assert.deepEqual(bodies[1].expectedDependentPacks, ['visibility-changed-pack']);
  assert.deepEqual(bodies[1].expectedWarmableDependentPacks, []);
});

test('workflow DAG has one serialized finalizer and no fire-and-forget warm', () => {
  const translation = readFileSync(
    resolve(REPO_ROOT, '.github/workflows/translate-skills.yml'),
    'utf8'
  );
  const sync = readFileSync(
    resolve(REPO_ROOT, '.github/workflows/sync-to-supabase.yml'),
    'utf8'
  );
  const warm = readFileSync(
    resolve(REPO_ROOT, '.github/workflows/warm-cache.yml'),
    'utf8'
  );

  assert.match(translation, /group:\s*translate-skills-cache-owner/);
  assert.match(translation, /cancel-in-progress:\s*false/);
  assert.match(translation, /^  finalize-cache:/m);
  assert.match(translation, /finalize-translation-cache\.mjs/);
  assert.match(translation, /CACHE_FINALIZER_AUTOMATION_ENABLED/);
  assert.match(translation, /CACHE_FINALIZER_MAX_SKILLS/);
  assert.match(translation, /github\.event_name == 'workflow_dispatch'/);
  assert.match(
    translation,
    /fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\) >= 1/
  );
  assert.match(
    translation,
    /fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\) <= 25/
  );
  assert.match(
    translation,
    /fromJSON\(needs\.detect-and-plan\.outputs\.skill_count \|\| '0'\) <= fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\)/
  );
  assert.match(
    translation,
    /github\.event_name == 'workflow_dispatch' \|\|\s*vars\.CACHE_FINALIZER_AUTOMATION_ENABLED == 'true'/
  );
  assert.match(
    translation,
    /^  merge-results:[\s\S]*?needs\.translate\.result == 'success'[\s\S]*?^  finalize-cache:/m
  );
  assert.match(translation, /status == "translated" or \.status == "stale_retranslated"/);
  assert.doesNotMatch(translation, /^  invalidate-cache:/m);

  assert.match(sync, /^  finalize-english-cache:/m);
  assert.match(sync, /vars\.CACHE_FINALIZER_AUTOMATION_ENABLED == 'true'/);
  assert.match(sync, /synced_skill_count: \$\{\{ steps\.synced-plan\.outputs\.skill_count \}\}/);
  assert.match(sync, /echo "skill_count=\$SLUG_COUNT" >> "\$GITHUB_OUTPUT"/);
  assert.match(
    sync,
    /fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\) >= 1/
  );
  assert.match(
    sync,
    /fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\) <= 25/
  );
  assert.match(
    sync,
    /fromJSON\(needs\.sync\.outputs\.synced_skill_count \|\| '0'\) <= fromJSON\(vars\.CACHE_FINALIZER_MAX_SKILLS \|\| '5'\)/
  );
  assert.match(sync, /needs: \[sync, cache-invalidate, finalize-english-cache\]/);
  assert.match(sync, /english_cache_finalizer_failed/);
  assert.doesNotMatch(sync, /gh workflow run warm-cache\.yml/);

  assert.match(warm, /^      locales:/m);
  assert.match(warm, /default: 'en'/);
  assert.match(warm, /Unsupported locale/);
});

test('sync chains bounded translation batches without concurrent pending runs', () => {
  const syncWorkflow = readFileSync(
    resolve(REPO_ROOT, '.github/workflows/sync-to-supabase.yml'),
    'utf8'
  );
  const translationWorkflow = readFileSync(
    resolve(REPO_ROOT, '.github/workflows/translate-skills.yml'),
    'utf8'
  );
  const initialScript = workflowRunScript(syncWorkflow, 'Trigger translation workflow')
    .replaceAll('${{ github.repository }}', 'aiskillstore/marketplace');
  const nextScript = workflowRunScript(translationWorkflow, 'Dispatch next bounded translation batch')
    .replaceAll('${{ github.repository }}', 'aiskillstore/marketplace');
  const temp = mkdtempSync(resolve(tmpdir(), 'translation-dispatch-'));

  try {
    const planDir = resolve(temp, 'translation-plan');
    mkdirSync(planDir);
    const slugs = Array.from({ length: 20 }, (_, index) => `owner-skill-${index + 1}`);
    writeFileSync(resolve(planDir, 'synced-slugs.txt'), `${slugs.join('\n')}\n`);

    const fakeGh = resolve(temp, 'gh');
    writeFileSync(fakeGh, '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$GH_CALLS"\n');
    chmodSync(fakeGh, 0o755);

    const baseEnv = {
      ...process.env,
      PATH: `${temp}:${process.env.PATH}`,
      GH_CALLS: resolve(temp, 'gh-calls.txt'),
      CACHE_FINALIZER_MAX_SKILLS: '5',
      ENGLISH_CACHE_FINALIZER_FAILED: 'false',
    };
    const result = spawnSync('bash', ['-c', initialScript], {
      cwd: temp,
      encoding: 'utf8',
      env: {
        ...baseEnv,
        SYNCED_SKILL_COUNT: '20',
        ENGLISH_CACHE_FINALIZER_RESULT: 'success',
      },
    });
    assert.equal(result.status, 0, result.stderr || result.stdout);

    let calls = readFileSync(resolve(temp, 'gh-calls.txt'), 'utf8').trim().split('\n');
    assert.equal(calls.length, 1, 'sync must dispatch only one run into the concurrency group');
    while (true) {
      const remaining = calls.at(-1).match(/client_payload\[remaining_skill_slugs\]=([^ ]*)/);
      assert.ok(remaining, `missing remaining queue: ${calls.at(-1)}`);
      if (remaining[1] === '') break;
      const chained = spawnSync('bash', ['-c', nextScript], {
        cwd: temp,
        encoding: 'utf8',
        env: { ...baseEnv, REMAINING_SKILL_SLUGS: remaining[1] },
      });
      assert.equal(chained.status, 0, chained.stderr || chained.stdout);
      calls = readFileSync(resolve(temp, 'gh-calls.txt'), 'utf8').trim().split('\n');
    }

    assert.equal(calls.length, 4);
    const dispatched = calls.flatMap((call) => {
      assert.match(call, /client_payload\[triggered_by\]=sync-to-supabase/);
      assert.match(call, /client_payload\[english_cache_finalizer_failed\]=false/);
      const match = call.match(/client_payload\[skill_slugs\]=([^ ]+)/);
      assert.ok(match, `missing skill payload: ${call}`);
      const batch = match[1].split(',');
      assert.equal(batch.length, 5);
      return batch;
    });
    assert.deepEqual(dispatched, slugs);
    assert.equal(new Set(dispatched).size, slugs.length);
  } finally {
    rmSync(temp, { recursive: true, force: true });
  }
});

test('translation mutation gate is fail-closed for automation and rollout caps', () => {
  const mayTranslate = ({ eventName, automationEnabled, skillCount, configuredMax }) => (
    Number.isSafeInteger(configuredMax) &&
    configuredMax >= 1 &&
    configuredMax <= 25 &&
    skillCount <= configuredMax &&
    (eventName === 'workflow_dispatch' || automationEnabled === true)
  );

  assert.equal(mayTranslate({
    eventName: 'repository_dispatch',
    automationEnabled: false,
    skillCount: 1,
    configuredMax: 5,
  }), false, 'disabled automation must prevent translation writes');

  assert.equal(mayTranslate({
    eventName: 'repository_dispatch',
    automationEnabled: true,
    skillCount: 6,
    configuredMax: 5,
  }), false, 'over-cap automation must be blocked before translation');

  assert.equal(mayTranslate({
    eventName: 'repository_dispatch',
    automationEnabled: true,
    skillCount: 1,
    configuredMax: 26,
  }), false, 'the automatic finalizer ceiling must never exceed 25 Skills');

  assert.equal(mayTranslate({
    eventName: 'workflow_dispatch',
    automationEnabled: false,
    skillCount: 1,
    configuredMax: 5,
  }), true, 'a bounded manual one-Skill canary may proceed while automation is disabled');
});
