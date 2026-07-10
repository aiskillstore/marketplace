import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const BINDER_PATH = join(REPO_ROOT, 'scripts', 'bind-skill-report-hashes.mjs');
const GATE_PATH = join(REPO_ROOT, 'scripts', 'validate-skill-publication.mjs');
const STALE_CONTENT_HASH = '0'.repeat(64);
const STALE_TREE_HASH = '1'.repeat(64);

function makeTempRoot() {
	return mkdtempSync(join(tmpdir(), 'bind-skill-report-hashes-'));
}

function writePackage(packageDir, reportContent) {
	mkdirSync(join(packageDir, 'references'), { recursive: true });
	writeFileSync(
		join(packageDir, 'SKILL.md'),
		'---\nname: fixture-skill\ndescription: Fixture skill.\nversion: 1.0.0\n---\n\n# Fixture\n',
	);
	writeFileSync(join(packageDir, 'references', 'audit.md'), '# Audit evidence\n');
	if (reportContent !== undefined) {
		writeFileSync(join(packageDir, 'skill-report.json'), reportContent);
	}
}

function reportText(slug) {
	return [
		'{',
		'  "schema_version": "2.0",',
		'  "meta": {',
		'    "generated_at": "2026-07-10T09:18:31.772Z",',
		`    "slug": "${slug}",`,
		'    "model": "codex",',
		'    "analysis_version": "3.0.0",',
		`    "content_hash" : "${STALE_CONTENT_HASH}",`,
		`    "tree_hash":    "${STALE_TREE_HASH}",`,
		'    "provenance": {',
		'      "model_requested": "gpt-5.5:high",',
		'      "fallback_chain": [{"agent":"codex","outcome":"success"}]',
		'    }',
		'  },',
		'  "security_audit": {',
		'    "analysis_status": "ok",',
		'    "is_blocked": true,',
		'    "safe_to_publish": false,',
		'    "summary": "Preserve this audit conclusion byte-for-byte.",',
		'    "audit_model": "codex:gpt-5.5:high",',
		'    "audited_at": "2026-07-10T09:18:31.772Z"',
		'  }',
		'}',
		'',
	].join('\r\n');
}

function runBinder(packageDirs) {
	return spawnSync(
		process.execPath,
		[
			BINDER_PATH,
			...packageDirs.flatMap((packageDir) => ['--package', packageDir]),
		],
		{
			cwd: REPO_ROOT,
			encoding: 'utf8',
		},
	);
}

async function expectedReport(packageDir, original) {
	const { calculatePackageHashes } = await import(
		`${pathToFileURL(GATE_PATH).href}?test=${Date.now()}-${Math.random()}`
	);
	const hashes = await calculatePackageHashes(packageDir);
	return original
		.replace(STALE_CONTENT_HASH, hashes.contentHash)
		.replace(STALE_TREE_HASH, hashes.treeHash);
}

test('updates only meta.content_hash and meta.tree_hash for explicit packages and is re-runnable', async () => {
	const root = makeTempRoot();
	try {
		const firstPackage = join(root, 'skills', 'fixture-owner', 'first');
		const secondPackage = join(root, 'skills', 'fixture-owner', 'second');
		const originals = new Map([
			[firstPackage, reportText('fixture-owner-first')],
			[secondPackage, reportText('fixture-owner-second')],
		]);

		for (const [packageDir, original] of originals) writePackage(packageDir, original);

		const firstRun = runBinder([secondPackage, firstPackage]);
		assert.equal(firstRun.status, 0, firstRun.stderr);

		for (const [packageDir, original] of originals) {
			const actual = readFileSync(join(packageDir, 'skill-report.json'), 'utf8');
			assert.equal(actual, await expectedReport(packageDir, original));
		}

		const afterFirstRun = new Map(
			[...originals].map(([packageDir]) => [
				packageDir,
				readFileSync(join(packageDir, 'skill-report.json')),
			]),
		);
		const secondRun = runBinder([firstPackage, secondPackage]);
		assert.equal(secondRun.status, 0, secondRun.stderr);
		assert.match(secondRun.stdout, /UNCHANGED/);

		for (const [packageDir, expectedBytes] of afterFirstRun) {
			assert.deepEqual(
				readFileSync(join(packageDir, 'skill-report.json')),
				expectedBytes,
			);
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed on malformed reports before writing any package', () => {
	const root = makeTempRoot();
	try {
		const validPackage = join(root, 'skills', 'fixture-owner', 'valid');
		const malformedPackage = join(root, 'skills', 'fixture-owner', 'malformed');
		const original = reportText('fixture-owner-valid');
		writePackage(validPackage, original);
		writePackage(malformedPackage, '{"meta":{"content_hash":');

		const result = runBinder([validPackage, malformedPackage]);
		assert.notEqual(result.status, 0);
		assert.match(result.stderr, /invalid JSON/i);
		assert.equal(readFileSync(join(validPackage, 'skill-report.json'), 'utf8'), original);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed when a report is missing', () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'missing');
		writePackage(packageDir);

		const result = runBinder([packageDir]);
		assert.notEqual(result.status, 0);
		assert.match(result.stderr, /skill-report\.json.*missing/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
