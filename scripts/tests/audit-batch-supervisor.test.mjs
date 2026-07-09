import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const SUPERVISOR = join(REPO_ROOT, 'scripts', 'audit-batch-supervisor.mjs');

test('audit batch supervisor scopes batches by risk level and pinned CLI version', () => {
	const source = readFileSync(SUPERVISOR, 'utf8');

	assert.match(source, /const cliVersion = process\.env\.CLI_VERSION \|\| getArg\('--cli-version', 'latest'\)/);
	assert.match(source, /const riskLevelFilter = \(process\.env\.RISK_LEVEL \|\| getArg\('--risk-level', ''\)\)/);
	assert.match(source, /function matchesRiskFilter\(report\)/);
	assert.match(source, /if \(!matchesRiskFilter\(report\)\) continue;/);
	assert.match(source, /`cli_version=\$\{cliVersion\}`/);
	assert.match(source, /`risk_level=\$\{riskLevelFilter\.join\(','\)\}`/);
	assert.match(source, /riskLevel: riskLevelFilter\.join\(','\) \|\| 'all'/);
});

test('audit batch supervisor can require structured audit verdicts before marking reports fresh', () => {
	const tempRoot = mkdtempSync(join(tmpdir(), 'audit-supervisor-'));
	try {
		writeReport(tempRoot, 'a', 'missing-structured', {
			meta: { slug: 'missing-structured' },
			security_audit: {
				risk_level: 'medium',
				audited_at: '2026-07-04T01:00:00.000Z',
			},
		});
		writeReport(tempRoot, 'b', 'incomplete-verdict', {
			meta: { slug: 'incomplete-verdict' },
			security_audit: {
				risk_level: 'medium',
				audited_at: '2026-07-04T01:00:00.000Z',
				static_findings: [{ id: 'static-1' }],
				finding_verdicts: [],
				semantic_findings: [],
			},
		});
		writeReport(tempRoot, 'c', 'complete-structured', {
			meta: { slug: 'complete-structured' },
			security_audit: {
				risk_level: 'medium',
				audited_at: '2026-07-04T01:00:00.000Z',
				static_findings: [{ id: 'static-1' }],
				finding_verdicts: [{ id: 'static-1', verdict: 'false_positive' }],
				semantic_findings: [],
			},
		});

		const strict = runPrintNext(tempRoot, { REQUIRE_STRUCTURED_AUDIT: '1' });
		assert.equal(strict.status, 0, strict.stderr);
		assert.deepEqual(strict.stdout.trim().split('\n'), ['missing-structured', 'incomplete-verdict']);

		const timestampOnly = runPrintNext(tempRoot);
		assert.equal(timestampOnly.status, 0, timestampOnly.stderr);
		assert.equal(timestampOnly.stdout.trim(), '');
	} finally {
		rmSync(tempRoot, { recursive: true, force: true });
	}
});

test('audit batch supervisor refuses to retrigger an unchanged stale batch', () => {
	const source = readFileSync(SUPERVISOR, 'utf8');

	assert.match(source, /function batchSlugSignature\(batch\)/);
	assert.match(source, /lastTriggeredBatchSignature/);
	assert.match(source, /No audit progress detected for the same stale batch/);
	assert.match(source, /avoid an empty audit PR loop/);
});

function writeReport(root, owner, slug, report) {
	const dir = join(root, 'skills', owner, slug);
	mkdirSync(dir, { recursive: true });
	writeFileSync(join(dir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
}

function runPrintNext(worktree, extraEnv = {}) {
	return spawnSync(process.execPath, [SUPERVISOR, '--print-next'], {
		encoding: 'utf8',
		env: {
			...process.env,
			WORKTREE: worktree,
			RISK_LEVEL: 'medium',
			FRESH_CUTOFF: '2026-07-04T00:00:00.000Z',
			BATCH_SIZE: '10',
			...extraEnv,
		},
	});
}
