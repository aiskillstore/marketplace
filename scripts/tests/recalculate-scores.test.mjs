// scripts/tests/recalculate-scores.test.mjs
//
// Node test runner coverage for scripts/recalculate-scores.sh.
//
// We exercise the wrapper with a fake `skillstore-cli` (scripts/tests/fake-cli.sh)
// to prove three acceptance criteria from the source-of-truth requirement:
//
//   AC1: a single slug failure (simulated TimeoutError) does not abort
//        the whole run; other slugs still get processed.
//   AC2: the run exits 0 when at least one slug succeeds, and exits 1
//        only if all slugs failed after retries.
//   AC3: per-slug retries happen with backoff; after the retry budget
//        is exhausted, the slug is counted in Errors.
//
// We also cover the legacy --recalculate top-level retry path.
//
// Run with: `node --test scripts/tests/recalculate-scores.test.mjs`
// (No external dependencies; uses node:test + node:child_process.)

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const WRAPPER = join(REPO_ROOT, 'scripts', 'recalculate-scores.sh');
const FAKE_CLI = join(REPO_ROOT, 'scripts', 'tests', 'fake-cli.sh');
const RECALCULATE_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'recalculate-scores.yml');
const SYNC_WORKFLOW = join(REPO_ROOT, '.github', 'workflows', 'sync-to-supabase.yml');
const DOWNLOAD_CLI_ACTION = join(REPO_ROOT, '.github', 'actions', 'download-skillstore-cli', 'action.yml');

function runWrapper({ mode, failSlug, timeoutSlug, recalcFail = false, slugs, maxAttempts = 3, retryBase = 0 }) {
	const tmp = mkdtempSync(join(tmpdir(), 'recalc-test-'));
	const fakeCli = join(tmp, 'skillstore-cli');
	const log = join(tmp, 'fake-cli.log');
	// Copy fake CLI to a stable path with the +x bit set.
	writeFileSync(fakeCli, readFileSync(FAKE_CLI), { mode: 0o755 });

	const env = {
		...process.env,
		FAKE_CLI_MODE: mode,
		FAKE_CLI_LOG: log,
	};
	if (failSlug) env.FAKE_CLI_FAIL_SLUG = failSlug;
	if (timeoutSlug) env.FAKE_CLI_TIMEOUT_SLUG = timeoutSlug;
	if (recalcFail) env.FAKE_CLI_MODE = 'recalc-fail';

	const args = [
		WRAPPER,
		'--cli', fakeCli,
		'--max-attempts', String(maxAttempts),
		'--retry-base-seconds', String(retryBase),
	];
	if (slugs) {
		args.push('--slugs', slugs);
	} else if (recalcFail || mode === 'success') {
		args.push('--recalculate');
	} else {
		// default to a few slugs if nothing else specified
		args.push('--slugs', 'a,b,c,d,e');
	}

	const result = spawnSync('/bin/bash', args, {
		env,
		encoding: 'utf8',
		timeout: 30_000,
	});

	return { result, tmp, fakeCli, log };
}

function lastSummary(stdout) {
	// The wrapper emits a final `=== summary ===` block with the
	// aggregate `Processed/Updated/Errors/Duration` lines. We pick
	// the LAST occurrence of each label so we don't get fooled by
	// the per-slug `Processed: 1` lines the fake CLI echoes.
	const lines = stdout.split('\n');
	const get = (label) => {
		const matches = lines.filter((l) => l.startsWith(label));
		if (matches.length === 0) return null;
		return matches[matches.length - 1].replace(label, '').trim();
	};
	return {
		processed: get('Processed:'),
		updated: get('Updated:'),
		errors: get('Errors:'),
		duration: get('Duration:'),
	};
}

// -------- AC1+AC2+AC3: single slug fails with simulated TimeoutError --------

test('single slug timeout does not abort the whole run; others succeed', () => {
	const { result, log } = runWrapper({
		mode: 'timeout',
		timeoutSlug: 'bad-slug',
		slugs: 'alpha,beta,bad-slug,gamma,delta',
		retryBase: 0, // no sleeping in tests
	});

	assert.equal(result.status, 0, `wrapper should exit 0 when not all slugs fail\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
	const s = lastSummary(result.stdout);
	assert.ok(s, 'summary block must be present');
	assert.equal(s.processed, '5', 'all 5 slugs should be processed');
	// bad-slug ultimately succeeds after retry, so it counts as
	// updated too. 5 processed = 4 updated + 1 error.
	assert.equal(s.updated, '4', '4 slugs updated (1 error + 4 ok incl. retry success)');
	assert.equal(s.errors, '1', 'only the timed-out slug should be in errors');

	// Verify retry happened: bad-slug should be called multiple times
	// (1 fail + 1 success) per the fake CLI's mode=timeout contract.
	const logText = readFileSync(log, 'utf8');
	const badCalls = logText.split('\n').filter((l) => l.includes('slugs=bad-slug')).length;
	assert.ok(badCalls >= 2 && badCalls <= 4, `bad-slug should be retried (calls: ${badCalls})`);

	// The other slugs should each be called exactly once.
	for (const s of ['alpha', 'beta', 'gamma', 'delta']) {
		const n = logText.split('\n').filter((l) => l.includes(`slugs=${s}`)).length;
		assert.equal(n, 1, `${s} should be called exactly once`);
	}
});

test('a slug that fails repeatedly lets the run finish; partial success -> exit 0', () => {
	const { result } = runWrapper({
		mode: 'fail-slug',
		failSlug: 'doomed',
		slugs: 'a,doomed,b',
		maxAttempts: 3,
		retryBase: 0,
	});

	// Per the AC: a single failure must NOT take down the whole
	// workflow. Exit 0 when at least one slug succeeded.
	assert.equal(result.status, 0, 'wrapper should exit 0 when at least one slug succeeded');
	const sum = lastSummary(result.stdout);
	assert.equal(sum.processed, '3');
	assert.equal(sum.errors, '1');
	assert.match(result.stdout, /doomed/, 'failed slug name should be surfaced in summary');
});

test('all slugs fail -> exit 1 (no partial success)', () => {
	// Use a different env that fails every slug. Easiest: re-run the
	// fail-slug-always mode but with a slug set where the FAIL_SLUG
	// matches the first AND the second slug cannot succeed because
	// the fake CLI's case statement only matches one. We achieve
	// "every slug fails" by routing through a slug that always fails
	// and another that also always fails -- the test mode here is
	// 'fail-slug-always' and we set FAIL_SLUG to a regex that matches
	// any slug by using "*" (a literal "*" - our fake CLI checks for
	// exact equality, so we use the simpler approach: set FAIL_SLUG=a
	// but only pass slug "a").
	const { result } = runWrapper({
		mode: 'fail-slug-always',
		failSlug: 'onlyone',
		slugs: 'onlyone',
		maxAttempts: 2,
		retryBase: 0,
	});
	assert.equal(result.status, 1, 'exit 1 when every slug failed');
	const sum = lastSummary(result.stdout);
	assert.equal(sum.processed, '1');
	assert.equal(sum.errors, '1');
});

test('all slugs succeed -> exit 0, errors=0', () => {
	const { result } = runWrapper({
		mode: 'success',
		slugs: 'one,two,three',
		retryBase: 0,
	});

	assert.equal(result.status, 0);
	const sum = lastSummary(result.stdout);
	assert.equal(sum.processed, '3');
	assert.equal(sum.errors, '0');
	assert.equal(sum.updated, '3');
});

test('legacy --recalculate mode retries the whole CLI call on failure', () => {
	// In recalc-fail mode the fake CLI always returns non-zero.
	const { result } = runWrapper({
		mode: 'recalc-fail',
		recalcFail: true,
		maxAttempts: 2,
		retryBase: 0,
	});

	// Top-level retry: after MAX_ATTEMPTS, the wrapper still emits
	// a summary and exits 1 (no successes at all).
	assert.equal(result.status, 1, 'recalc-fail should ultimately exit 1');
	assert.match(result.stdout, /Errors:\s*1/, 'errors should be 1 after retries exhausted');
});

test('--recalculate success mode prints CLI summary directly and exits 0', () => {
	const { result } = runWrapper({
		mode: 'success',
		recalcFail: false, // not used in this branch; legacy mode
		slugs: undefined, // triggers --recalculate branch
		maxAttempts: 2,
		retryBase: 0,
	});

	assert.equal(result.status, 0);
	// The fake CLI prints its own summary lines in recalculate mode.
	assert.match(result.stdout, /Processed:\s*5/);
});

// -------- configuration error paths --------

test('wrapper rejects missing --cli with exit 2', () => {
	const result = spawnSync('/bin/bash', [WRAPPER, '--slugs', 'a'], { encoding: 'utf8' });
	assert.equal(result.status, 2);
	assert.match(result.stderr, /--cli is required/);
});

test('wrapper rejects nonexistent --cli with exit 2', () => {
	const result = spawnSync('/bin/bash', [WRAPPER, '--cli', '/no/such/path', '--slugs', 'a'], {
		encoding: 'utf8',
	});
	assert.equal(result.status, 2);
	assert.match(result.stderr, /CLI not found or not executable/);
});

test('wrapper rejects --recalculate + --slugs combination', () => {
	const tmp = mkdtempSync(join(tmpdir(), 'recalc-test-'));
	const fakeCli = join(tmp, 'skillstore-cli');
	writeFileSync(fakeCli, readFileSync(FAKE_CLI), { mode: 0o755 });
	const result = spawnSync('/bin/bash', [WRAPPER, '--cli', fakeCli, '--recalculate', '--slugs', 'a'], {
		encoding: 'utf8',
	});
	assert.equal(result.status, 2);
	assert.match(result.stderr, /mutually exclusive/);
});


// -------- workflow integration guards for Trent review blockers --------

test('recalculate-scores workflow checks out wrapper and skill paths', () => {
	const workflow = readFileSync(RECALCULATE_WORKFLOW, 'utf8');
	assert.match(workflow, /sparse-checkout:\s*\|[\s\S]*\.github\/actions/, 'download action path must be checked out');
	assert.match(workflow, /sparse-checkout:\s*\|[\s\S]*\n\s*scripts\n/, 'scripts directory containing the wrapper must be checked out');
	assert.match(workflow, /sparse-checkout:\s*\|[\s\S]*\n\s*skills\n/, 'skills tree must be checked out for all-skills enumeration');
});

test('recalculate-scores workflow default all-skills path uses per-slug wrapper', () => {
	const workflow = readFileSync(RECALCULATE_WORKFLOW, 'utf8');
	assert.match(workflow, /find skills -name "SKILL\.md"/, 'workflow must enumerate skills from the checkout');
	assert.match(workflow, /WRAPPER_ARGS\+=\( --slugs "\$SLUGS_CSV" \)/, 'default full run must pass explicit slugs to the wrapper');
	assert.match(workflow, /SUPPORTS_SLUGS=0/, 'workflow must feature-probe whether the downloaded CLI supports --slugs');
	assert.match(workflow, /WRAPPER_ARGS\+=\( --recalculate \)/, 'workflow must fall back to legacy --recalculate when the release asset is older than the tag');
});

test('workflows fail no-success/global scoring failures instead of masking them', () => {
	const recalc = readFileSync(RECALCULATE_WORKFLOW, 'utf8');
	const sync = readFileSync(SYNC_WORKFLOW, 'utf8');
	assert.match(recalc, /SUCCESSFUL=\$\(\( \$\{PROCESSED:-0\} - \$\{ERRORS:-0\} \)\)/);
	assert.match(recalc, /Recalculation failed: no skills were scored successfully/);
	assert.match(recalc, /exit "\$EXIT_CODE"/);
	assert.match(sync, /tee score-output\.log/);
	assert.match(sync, /Quality scoring failed: no synced skills were scored successfully/);
	assert.match(sync, /exit "\$EXIT_CODE"/);
});

test('download action invalidates stale local CLI cache entries', () => {
	const action = readFileSync(DOWNLOAD_CLI_ACTION, 'utf8');
	assert.match(action, /CACHED_VERSION=/, 'local cache hit must inspect the cached binary version');
	assert.match(action, /EXPECTED_VERSION=\$\{RELEASE_TAG#cli-v\}/, 'expected version must come from the resolved release tag');
	assert.match(action, /rm -f "\$CACHE_FILE" "\$GITHUB_WORKSPACE\/skillstore-cli"/, 'stale local cache must be removed so the Download CLI step runs');
	assert.match(action, /cache-hit=false/, 'stale local cache must flip cache-hit back to false');
});
