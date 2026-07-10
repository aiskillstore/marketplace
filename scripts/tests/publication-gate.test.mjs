import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	symlinkSync,
	writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const GATE_PATH = join(REPO_ROOT, 'scripts', 'validate-skill-publication.mjs');
const GITHUB_REPOSITORY = 'aiskillstore/marketplace';
const COMMENT_ID = 123456789;
const EVIDENCE_URL = `https://github.com/${GITHUB_REPOSITORY}/issues/2403#issuecomment-${COMMENT_ID}`;

async function loadGate() {
	return import(`${pathToFileURL(GATE_PATH).href}?test=${Date.now()}-${Math.random()}`);
}

function makeTempRoot() {
	return mkdtempSync(join(tmpdir(), 'publication-gate-'));
}

function writeSkill(packageDir, extra = '') {
	mkdirSync(packageDir, { recursive: true });
	writeFileSync(
		join(packageDir, 'SKILL.md'),
		`---
name: fixture-skill
description: Fixture skill for publication gate tests.
version: 1.0.0
---

# Fixture

[Local reference](references/local.md)
[External reference](https://example.com/reference.md)
[Mail](mailto:security@example.com)
[Anchor](#fixture)
${extra}`,
	);
	mkdirSync(join(packageDir, 'references'), { recursive: true });
	writeFileSync(join(packageDir, 'references', 'local.md'), '# Local\n');
}

function makeReport({
	contentHash,
	treeHash,
	blocked = false,
	safeToPublish = true,
	slug = 'fixture-owner-fixture-skill',
}) {
	return {
		schema_version: '2.0',
		meta: {
			generated_at: '2026-07-10T00:00:00.000Z',
			slug,
			source_url: 'https://github.com/example/fixture/tree/main/fixture-skill',
			source_ref: 'main',
			model: 'codex',
			analysis_version: '3.0.0',
			source_type: 'community',
			content_hash: contentHash,
			tree_hash: treeHash,
			provenance: {
				model_effective: 'codex',
				fallback_chain: [{ agent: 'codex', outcome: 'success' }],
				analysis_version: '3.0.0',
			},
		},
		security_audit: {
			risk_level: blocked ? 'critical' : 'low',
			is_blocked: blocked,
			safe_to_publish: safeToPublish,
			analysis_status: 'ok',
			summary: 'Fixture audit.',
			files_scanned: 2,
			total_lines: 20,
			audit_model: 'codex',
			audited_at: '2026-07-10T00:00:00.000Z',
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

async function writeFreshReport(packageDir, overrides = {}) {
	const { calculatePackageHashes } = await loadGate();
	const hashes = await calculatePackageHashes(packageDir);
	const report = makeReport({
		contentHash: hashes.contentHash,
		treeHash: hashes.treeHash,
		...overrides,
	});
	writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
	return report;
}

function humanApproval(report, overrides = {}) {
	return {
		schema_version: '1.0',
		approvals: [
			{
				slug: report.meta.slug,
				content_hash: report.meta.content_hash,
				tree_hash: report.meta.tree_hash,
				actor: 'mylukin',
				approved_at: '2026-07-10T01:00:00.000Z',
				reason: 'Reviewed the unsafe publication recommendation and accepted the documented risk.',
				evidence_url: EVIDENCE_URL,
				scope: 'safe_to_publish',
				...overrides,
			},
		],
	};
}

function githubEvidence(report, {
	approvalOverrides = {},
	commentOverrides = {},
	permission = 'write',
	requestError,
} = {}) {
	const approvalDocument = humanApproval(report, approvalOverrides);
	const approval = approvalDocument.approvals[0];
	const requests = [];
	const defaultUser = {
		login: approval.actor,
		type: 'User',
	};
	const comment = {
		id: COMMENT_ID,
		html_url: approval.evidence_url,
		created_at: approval.approved_at,
		body: `/approve safe-to-publish ${report.meta.slug}\n${approval.reason}`,
		...commentOverrides,
		user: {
			...defaultUser,
			...(commentOverrides.user ?? {}),
		},
	};

	return {
		approvalDocument,
		githubRepository: GITHUB_REPOSITORY,
		requests,
		githubRequest: async (apiPath) => {
			requests.push(apiPath);
			if (requestError) throw requestError;
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/issues/comments/${COMMENT_ID}`) {
				return comment;
			}
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/collaborators/${encodeURIComponent(approval.actor)}/permission`) {
				return { permission };
			}
			throw new Error(`Unexpected GitHub API path: ${apiPath}`);
		},
	};
}

test('accepts a fresh standalone package', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'fixture-skill');
		writeSkill(packageDir);
		await writeFreshReport(packageDir);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir);
		assert.equal(result.ok, true, result.errors.join('\n'));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed when a package contains a symbolic link', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'symlinked-skill');
		writeSkill(packageDir);
		await writeFreshReport(packageDir);

		try {
			symlinkSync(
				join('references', 'local.md'),
				join(packageDir, 'untracked-link.md'),
				'file',
			);
		} catch (error) {
			if (['EACCES', 'ENOSYS', 'ENOTSUP', 'EOPNOTSUPP', 'EPERM'].includes(error?.code)) {
				t.skip(`platform cannot create symlinks: ${error.code}`);
				return;
			}
			throw error;
		}

		const { calculatePackageHashes, validatePackage } = await loadGate();
		await assert.rejects(
			calculatePackageHashes(packageDir),
			/untracked-link\.md: symbolic links are not allowed in skill packages/,
		);

		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(
			result.errors.join('\n'),
			/untracked-link\.md: symbolic links are not allowed in skill packages/,
		);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('accepts a package with nested vendored SKILL.md files without requiring nested reports', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'meta-skill');
		writeSkill(packageDir);
		const vendoredDir = join(packageDir, 'vendored', 'vendor', 'nested-skill');
		mkdirSync(vendoredDir, { recursive: true });
		writeFileSync(
			join(vendoredDir, 'SKILL.md'),
			'---\nname: nested-skill\ndescription: Nested package content.\n---\n\n# Nested\n',
		);
		await writeFreshReport(packageDir, { slug: 'fixture-owner-meta-skill' });

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir);
		assert.equal(result.ok, true, result.errors.join('\n'));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed when skill-report.json is missing', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'missing-report');
		writeSkill(packageDir);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /skill-report\.json.*missing/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed when required publication gate fields are missing', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'missing-fields');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		delete report.meta.content_hash;
		delete report.security_audit.analysis_status;
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /meta\.content_hash/);
		assert.match(result.errors.join('\n'), /security_audit\.analysis_status/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects stale content and tree hashes', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'stale-report');
		writeSkill(packageDir);
		await writeFreshReport(packageDir);
		writeFileSync(join(packageDir, 'references', 'local.md'), '# Changed after audit\n');

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /tree_hash.*does not match/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects evidence with a missing file or invalid line range', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'bad-evidence');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		report.security_audit.static_findings = [
			{
				id: 'network:missing.md:99:test',
				category: 'network',
				severity: 'low',
				pattern: 'Test',
				file: 'missing.md',
				line_start: 99,
				line_end: 100,
				snippet: 'missing',
			},
		];
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /missing\.md.*does not exist/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects evidence one line past a newline-terminated file', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'past-eof-evidence');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		report.security_audit.static_findings = [
			{
				id: 'network:references/local.md:2:test',
				category: 'network',
				severity: 'low',
				pattern: 'Test',
				file: 'references/local.md',
				line_start: 2,
				line_end: 2,
				snippet: 'past EOF',
			},
		];
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /line range 2-2 exceeds.*1 lines/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects GitHub Bot approval even when the login has no bot suffix', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'bot-approval');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report, {
			approvalOverrides: { actor: 'release-manager' },
			commentOverrides: {
				user: {
					login: 'release-manager',
					type: 'Bot',
				},
			},
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /user\.type.*User|Bot/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('allows a hash-bound override backed by a matching human issue comment', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'human-approval');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, true, result.errors.join('\n'));
		assert.equal(result.approval?.actor, 'mylukin');
		assert.deepEqual(evidence.requests, [
			`/repos/${GITHUB_REPOSITORY}/issues/comments/${COMMENT_ID}`,
			`/repos/${GITHUB_REPOSITORY}/collaborators/mylukin/permission`,
		]);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects an override record without an issue-comment evidence URL before any API call', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'missing-comment-url');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report, {
			approvalOverrides: { evidence_url: undefined },
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /evidence_url.*required/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('requires issue-comment evidence on every tracked override record', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'all-records-need-evidence');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report);
		evidence.approvalDocument.approvals.push({
			...evidence.approvalDocument.approvals[0],
			slug: 'fixture-owner-historical-skill',
			content_hash: 'a'.repeat(64),
			tree_hash: 'b'.repeat(64),
			evidence_url: undefined,
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /approvals\[1\]\.evidence_url.*required/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects issue-comment evidence mismatches', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'evidence-mismatch');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const cases = [
			{
				name: 'author login',
				evidence: githubEvidence(report, {
					commentOverrides: { user: { login: 'someone-else' } },
				}),
				pattern: /author.*actor|login.*actor/i,
			},
			{
				name: 'approval timestamp',
				evidence: githubEvidence(report, {
					commentOverrides: { created_at: '2026-07-10T01:00:01.000Z' },
				}),
				pattern: /created_at.*approved_at/i,
			},
			{
				name: 'exact report slug',
				evidence: githubEvidence(report, {
					commentOverrides: {
						body: '/approve safe-to-publish fixture-owner-other-skill\n'
							+ 'Reviewed the unsafe publication recommendation and accepted the documented risk.',
					},
				}),
				pattern: /exact.*slug|safe-to-publish.*slug/i,
			},
			{
				name: 'recorded reason',
				evidence: githubEvidence(report, {
					commentOverrides: {
						body: `/approve safe-to-publish ${report.meta.slug}\nA different approval reason.`,
					},
				}),
				pattern: /recorded.*reason|reason.*comment/i,
			},
		];

		const { validatePackage } = await loadGate();
		for (const testCase of cases) {
			await t.test(testCase.name, async () => {
				const result = await validatePackage(packageDir, testCase.evidence);
				assert.equal(result.ok, false);
				assert.match(result.errors.join('\n'), testCase.pattern);
			});
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects issue-comment approval without write-equivalent collaborator permission', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'insufficient-permission');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report, { permission: 'read' });

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /permission.*write|write.*permission/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('accepts write, maintain, and admin collaborator permissions', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'allowed-permissions');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const { validatePackage } = await loadGate();

		for (const permission of ['write', 'maintain', 'admin']) {
			const result = await validatePackage(packageDir, githubEvidence(report, { permission }));
			assert.equal(result.ok, true, `${permission}: ${result.errors.join('\n')}`);
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('fails closed on missing token or GitHub API failure without making real network calls', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'github-failure');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const approvalDocument = humanApproval(report);
		const { validatePackage } = await loadGate();

		await t.test('missing token', async () => {
			let fetchCalls = 0;
			const result = await validatePackage(packageDir, {
				approvalDocument,
				githubRepository: GITHUB_REPOSITORY,
				githubToken: '',
				fetchImpl: async () => {
					fetchCalls++;
					throw new Error('test fetch must not run');
				},
			});
			assert.equal(result.ok, false);
			assert.match(result.errors.join('\n'), /GH_TOKEN|GITHUB_TOKEN|token/i);
			assert.equal(fetchCalls, 0);
		});

		await t.test('API failure', async () => {
			const evidence = githubEvidence(report, {
				requestError: new Error('simulated GitHub outage'),
			});
			const result = await validatePackage(packageDir, evidence);
			assert.equal(result.ok, false);
			assert.match(result.errors.join('\n'), /GitHub.*simulated GitHub outage|simulated GitHub outage/i);
			assert.equal(evidence.requests.length, 1);
		});
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects is_blocked=true without making any approval API call', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'hard-blocked');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, {
			blocked: true,
			safeToPublish: false,
		});
		const evidence = githubEvidence(report);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /is_blocked=true.*cannot be overridden/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('relative link scanner ignores external URLs, mailto links, and pure anchors', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'link-scan');
		writeSkill(packageDir);

		const { scanMarkdownLinks } = await loadGate();
		const valid = await scanMarkdownLinks(packageDir);
		assert.deepEqual(valid, []);

		writeFileSync(
			join(packageDir, 'references', 'local.md'),
			'# Local\n\n[Broken package-local reference](missing.md)\n',
		);
		const broken = await scanMarkdownLinks(packageDir);
		assert.equal(broken.length, 1);
		assert.match(broken[0], /missing\.md/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('publication integrity rejects a broken package-local Markdown reference', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'broken-link');
		writeSkill(packageDir, '\n[Broken package-local reference](references/missing.md)\n');
		await writeFreshReport(packageDir);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /relative Markdown reference does not exist.*missing\.md/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('all imported internet-court packages have resolvable package-local Markdown references', async () => {
	const { discoverPackageDirs, scanMarkdownLinks } = await loadGate();
	const packageDirs = await discoverPackageDirs(join(REPO_ROOT, 'skills', 'internet-court'));
	const failures = [];

	for (const packageDir of packageDirs) {
		for (const error of await scanMarkdownLinks(packageDir)) {
			failures.push(error);
		}
	}

	assert.deepEqual(failures, [], failures.join('\n'));
});

test('approval schema and tracked approval artifact are present and versioned', () => {
	const schemaPath = join(REPO_ROOT, 'schemas', 'skill-publish-approvals.schema.json');
	const approvalsPath = join(REPO_ROOT, '.github', 'skill-publish-approvals.json');

	const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));
	const approvals = JSON.parse(readFileSync(approvalsPath, 'utf8'));
	const approvalSchema = schema.properties.approvals.items;
	assert.equal(schema.properties.schema_version.const, '1.0');
	assert.ok(approvalSchema.required.includes('evidence_url'));
	assert.match(approvalSchema.properties.evidence_url.pattern, /issuecomment/);
	assert.equal(approvals.schema_version, '1.0');
	assert.deepEqual(approvals.approvals, []);
});
