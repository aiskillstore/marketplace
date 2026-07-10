import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
	mkdirSync,
	mkdtempSync,
	rmSync,
	writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const GATE_PATH = join(REPO_ROOT, 'scripts', 'validate-skill-publication.mjs');

function makeTempRepo() {
	const root = mkdtempSync(join(tmpdir(), 'changed-package-selection-'));
	for (const args of [
		['init', '-q'],
		['config', 'user.email', 'fixture@example.com'],
		['config', 'user.name', 'Fixture'],
	]) {
		const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
		assert.equal(result.status, 0, result.stderr);
	}
	return root;
}

function git(root, ...args) {
	const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
	assert.equal(result.status, 0, result.stderr);
	return result.stdout.trim();
}

function commitAll(root, message) {
	git(root, 'add', '-A');
	git(root, 'commit', '-qm', message);
}

function addIndexOnlyPadding(root, count = 5000) {
	const blob = spawnSync('git', ['hash-object', '-w', '--stdin'], {
		cwd: root,
		encoding: 'utf8',
		input: 'padding\n',
	});
	assert.equal(blob.status, 0, blob.stderr);
	const blobHash = blob.stdout.trim();
	const indexInfo = Array.from({ length: count }, (_, index) => {
		const paddedName = `${String(index).padStart(5, '0')}-${'x'.repeat(220)}.md`;
		return `100644 ${blobHash}\tskills/tree-padding/${paddedName}\n`;
	}).join('');
	const update = spawnSync('git', ['update-index', '--add', '--index-info'], {
		cwd: root,
		encoding: 'utf8',
		input: indexInfo,
	});
	assert.equal(update.status, 0, update.stderr);
}

async function loadGate() {
	return import(`${pathToFileURL(GATE_PATH).href}?test=${Date.now()}-${Math.random()}`);
}

function baseReport(slug) {
	return {
		schema_version: '2.0',
		meta: {
			generated_at: '2026-07-10T10:00:00.000Z',
			slug,
			source_url: 'https://github.com/example/fixture',
			source_ref: 'main',
			model: 'codex',
			analysis_version: '3.0.0',
			source_type: 'community',
			content_hash: '0'.repeat(64),
			tree_hash: '1'.repeat(64),
			provenance: {
				model_effective: 'codex:gpt-5.5:high',
				fallback_chain: [{ agent: 'codex', outcome: 'success' }],
				analysis_version: '3.0.0',
			},
		},
		security_audit: {
			risk_level: 'low',
			is_blocked: false,
			safe_to_publish: true,
			analysis_status: 'ok',
			summary: 'Fixture audit.',
			files_scanned: 2,
			total_lines: 10,
			audit_model: 'codex',
			audited_at: '2026-07-10T10:00:00.000Z',
			risk_factor_evidence: [],
			static_findings: [],
			semantic_findings: [],
			critical_findings: [],
			high_findings: [],
			medium_findings: [],
			low_findings: [],
			dangerous_patterns: [],
		},
	};
}

async function writePackage(root, relativeDir, {
	evidencePath,
	skillBody = '# Fixture\n',
	vendoredSkill = false,
} = {}) {
	const packageDir = join(root, relativeDir);
	mkdirSync(packageDir, { recursive: true });
	writeFileSync(
		join(packageDir, 'SKILL.md'),
		`---\nname: fixture\ndescription: Fixture package.\n---\n\n${skillBody}`,
	);

	if (vendoredSkill) {
		const vendoredDir = join(packageDir, 'vendored', 'vendor', 'child');
		mkdirSync(vendoredDir, { recursive: true });
		writeFileSync(
			join(vendoredDir, 'SKILL.md'),
			'---\nname: child\ndescription: Vendored child.\n---\n\n# Child\n',
		);
	}

	const report = baseReport(relativeDir.replaceAll('/', '-'));
	if (evidencePath) {
		const evidenceFile = join(packageDir, evidencePath);
		mkdirSync(dirname(evidenceFile), { recursive: true });
		writeFileSync(evidenceFile, '# Evidence\n');
		report.security_audit.static_findings = [{
			file: evidencePath,
			line_start: 1,
			line_end: 1,
		}];
	}

	writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
	const { calculatePackageHashes } = await loadGate();
	const hashes = await calculatePackageHashes(packageDir);
	report.meta.content_hash = hashes.contentHash;
	report.meta.tree_hash = hashes.treeHash;
	writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
	return packageDir;
}

function runChangedSince(root) {
	return spawnSync(
		process.execPath,
		[GATE_PATH, '--integrity-only', '--changed-since', 'HEAD~1'],
		{ cwd: root, encoding: 'utf8' },
	);
}

test('changed-since selects a changed standalone package', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/standalone');
		commitAll(root, 'base');
		writeFileSync(join(packageDir, 'notes.md'), '# Added after base\n');
		const report = JSON.parse(
			await import('node:fs').then(({ readFileSync }) => (
				readFileSync(join(packageDir, 'skill-report.json'), 'utf8')
			)),
		);
		const { calculatePackageHashes } = await loadGate();
		const hashes = await calculatePackageHashes(packageDir);
		report.meta.content_hash = hashes.contentHash;
		report.meta.tree_hash = hashes.treeHash;
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
		commitAll(root, 'update standalone');

		const result = runChangedSince(root);
		assert.equal(result.status, 0, result.stderr);
		assert.match(result.stdout, /PASS skills\/owner\/standalone/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('changed-since selects a nested vendored package when evidence is deleted', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/meta', {
			evidencePath: 'vendored/vendor/child/evidence.md',
			vendoredSkill: true,
		});
		commitAll(root, 'base');
		rmSync(join(packageDir, 'vendored', 'vendor', 'child', 'evidence.md'));
		commitAll(root, 'delete vendored evidence');

		const result = runChangedSince(root);
		assert.equal(result.status, 1, `${result.stdout}\n${result.stderr}`);
		assert.match(result.stderr, /evidence file .* does not exist/i);
		assert.doesNotMatch(result.stdout, /No skill packages found/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('changed-since selects a package when report evidence is deleted', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/evidence', {
			evidencePath: 'references/evidence.md',
		});
		commitAll(root, 'base');
		rmSync(join(packageDir, 'references', 'evidence.md'));
		commitAll(root, 'delete evidence');

		const result = runChangedSince(root);
		assert.equal(result.status, 1, `${result.stdout}\n${result.stderr}`);
		assert.match(result.stderr, /evidence file references\/evidence\.md does not exist/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('changed-since selects a package when a package-local Markdown target is deleted', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/references', {
			evidencePath: 'references/target.md',
			skillBody: '# Fixture\n\n[Target](references/target.md)\n',
		});
		const reportPath = join(packageDir, 'skill-report.json');
		const report = JSON.parse(
			await import('node:fs').then(({ readFileSync }) => readFileSync(reportPath, 'utf8')),
		);
		report.security_audit.static_findings = [];
		writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
		commitAll(root, 'base');
		rmSync(join(packageDir, 'references', 'target.md'));
		commitAll(root, 'delete reference target');

		const result = runChangedSince(root);
		assert.equal(result.status, 1, `${result.stdout}\n${result.stderr}`);
		assert.match(result.stderr, /relative Markdown reference does not exist.*target\.md/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('changed-since skips only a fully deleted package', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/deleted');
		commitAll(root, 'base');
		rmSync(packageDir, { recursive: true });
		commitAll(root, 'delete entire package');

		const result = runChangedSince(root);
		assert.equal(result.status, 0, result.stderr);
		assert.match(result.stdout, /No skill packages found for validation/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('changed-since handles repository trees larger than the default child-process buffer', async () => {
	const root = makeTempRepo();
	try {
		const packageDir = await writePackage(root, 'skills/owner/large-tree');
		git(root, 'add', '-A');
		addIndexOnlyPadding(root);
		git(root, 'commit', '-qm', 'large base tree');

		writeFileSync(join(packageDir, 'notes.md'), '# Changed package\n');
		const reportPath = join(packageDir, 'skill-report.json');
		const report = JSON.parse(
			await import('node:fs').then(({ readFileSync }) => readFileSync(reportPath, 'utf8')),
		);
		const { calculatePackageHashes } = await loadGate();
		const hashes = await calculatePackageHashes(packageDir);
		report.meta.content_hash = hashes.contentHash;
		report.meta.tree_hash = hashes.treeHash;
		writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
		git(root, 'add', 'skills/owner/large-tree');
		git(root, 'commit', '-qm', 'update package in large tree');

		const result = runChangedSince(root);
		assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
		assert.match(result.stdout, /PASS skills\/owner\/large-tree/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
