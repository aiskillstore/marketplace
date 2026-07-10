import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import {
	chmodSync,
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
const APPROVAL_LIBRARY_PATH = join(REPO_ROOT, 'scripts', 'lib', 'publication-approval.mjs');
const GITHUB_REPOSITORY = 'aiskillstore/marketplace';
const COMMENT_ID = 123456789;
const PR_NUMBER = 2405;
const ISSUE_NUMBER = PR_NUMBER;
const SUBMISSION_ID = '12345678-1234-4234-8234-123456789abc';
const SOURCE_URL = 'https://github.com/example/fixture';
const CREATED_AT = '2026-07-10T01:00:00.000Z';
const EXPIRES_AT = '2026-08-09T01:00:00.000Z';
const PR_BASE_SHA = 'a'.repeat(40);
const PR_HEAD_SHA = 'b'.repeat(40);
const LIVE_PR_HEAD_SHA = 'c'.repeat(40);
const PR_HEAD_REF = `submission/fixture-${SUBMISSION_ID}`;
const ISSUE_URL = `https://github.com/${GITHUB_REPOSITORY}/pull/${ISSUE_NUMBER}`;
const COMMENT_URL = `${ISSUE_URL}#issuecomment-${COMMENT_ID}`;
const PR_URL = `https://github.com/${GITHUB_REPOSITORY}/pull/${PR_NUMBER}`;
const NOW = Date.parse('2026-07-10T02:00:00.000Z');
const AUDIT_MODEL = 'gpt-5.5:high';
const AUDIT_COMPLETED_AT = '2026-07-10T00:00:01.000Z';

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
	sourceUrl = 'https://github.com/example/fixture/tree/main/fixture-skill',
}) {
	return {
		schema_version: '2.0',
		meta: {
			generated_at: '2026-07-10T00:00:00.000Z',
			slug,
			source_url: sourceUrl,
			source_ref: 'main',
			model: 'codex',
			analysis_version: '3.0.0',
			source_type: 'community',
			content_hash: contentHash,
			tree_hash: treeHash,
			provenance: {
				model_requested: AUDIT_MODEL,
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
	if (report.security_audit.safe_to_publish === false) {
		await writeAuditAttestation(packageDir, report);
	}
	return report;
}

async function writeAuditAttestation(packageDir, report) {
	const { calculatePackageHashes } = await loadGate();
	const hashes = await calculatePackageHashes(packageDir);
	const reportDigest = createHash('sha256')
		.update(readFileSync(join(packageDir, 'skill-report.json')))
		.digest('hex');
	const attestation = {
		schema_version: '1.0',
		slug: report.meta.slug,
		producer: {
			repository: 'aiskillstore/skillstore',
			commit: 'd'.repeat(40),
			package_version: '9.9.9',
			audit_command_version: '1.2.0',
		},
		invocation: {
			id: '12345678-1234-4234-8234-123456789abc',
			started_at: '2026-07-09T23:59:59.000Z',
			completed_at: AUDIT_COMPLETED_AT,
			cwd: '/tmp/skillstore-audit',
			command: [
				process.execPath,
				'--import',
				'tsx',
				'/tmp/skillstore-audit/src/cli/index.ts',
				'skill',
				'audit',
				'../marketplace/skills',
				'--slugs',
				report.meta.slug,
				'--model',
				AUDIT_MODEL,
			],
			skills_root: '/tmp/marketplace/skills',
			slugs: [report.meta.slug],
			model: AUDIT_MODEL,
			stdout_digest: 'e'.repeat(64),
			stderr_digest: 'f'.repeat(64),
		},
		report: {
			input_digest: '0'.repeat(64),
			raw_audit_digest: '1'.repeat(64),
			final_digest: reportDigest,
		},
		package: {
			content_hash: hashes.contentHash,
			tree_hash: hashes.treeHash,
		},
	};
	writeFileSync(
		join(packageDir, 'skill-report.attestation.json'),
		`${JSON.stringify(attestation, null, 2)}\n`,
	);
	return attestation;
}

function humanApproval(report, overrides = {}) {
	return {
		schema_version: '2.0',
		approvals: [
			{
				slug: report.meta.slug,
				content_hash: report.meta.content_hash,
				tree_hash: report.meta.tree_hash,
				submission_id: SUBMISSION_ID,
				submission_source_url: SOURCE_URL,
				approval_issue_number: ISSUE_NUMBER,
				approval_issue_url: ISSUE_URL,
				approval_comment_id: COMMENT_ID,
				approval_comment_url: COMMENT_URL,
				actor: 'mylukin',
				created_at: CREATED_AT,
				updated_at: CREATED_AT,
				expires_at: EXPIRES_AT,
				audit_completed_at: AUDIT_COMPLETED_AT,
				reason: 'Reviewed the unsafe publication recommendation and accepted the documented risk.',
				pr_number: PR_NUMBER,
				pr_url: PR_URL,
				pr_base_sha: PR_BASE_SHA,
				pr_base_ref: 'main',
				pr_head_ref: PR_HEAD_REF,
				pr_head_sha: PR_HEAD_SHA,
				scope: 'safe_to_publish',
				...overrides,
			},
		],
	};
}

function githubEvidence(report, {
	approvalOverrides = {},
	commentOverrides = {},
	issueOverrides = {},
	prOverrides = {},
	commitsOverrides,
	compareOverrides = {},
	permission = 'write',
	requestError,
	now = NOW,
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
		html_url: approval.approval_comment_url,
		issue_url: `https://api.github.com/repos/${GITHUB_REPOSITORY}/issues/${approval.approval_issue_number}`,
		created_at: approval.created_at,
		updated_at: approval.updated_at,
		body: `/approve safe-to-publish ${report.meta.slug}`
			+ ` --content-hash ${report.meta.content_hash}`
			+ ` --tree-hash ${report.meta.tree_hash}`
			+ ` --head ${approval.pr_head_sha}`
			+ ` --base ${approval.pr_base_sha}`
			+ `\n${approval.reason}`,
		...commentOverrides,
		user: {
			...defaultUser,
			...(commentOverrides.user ?? {}),
		},
	};
	const issue = {
		number: approval.approval_issue_number,
		html_url: approval.approval_issue_url,
		state: 'open',
		labels: [{ name: 'pending-review' }],
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		pull_request: {
			url: `https://api.github.com/repos/${GITHUB_REPOSITORY}/pulls/${approval.pr_number}`,
		},
		...issueOverrides,
	};
	const defaultBase = {
		sha: approval.pr_base_sha,
		ref: approval.pr_base_ref,
		repo: { full_name: GITHUB_REPOSITORY },
	};
	const defaultHead = {
		sha: LIVE_PR_HEAD_SHA,
		ref: approval.pr_head_ref,
		repo: { full_name: GITHUB_REPOSITORY },
	};
	const pullRequest = {
		number: approval.pr_number,
		html_url: approval.pr_url,
		state: 'open',
		merged: false,
		merged_at: null,
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		base: defaultBase,
		head: defaultHead,
		...prOverrides,
	};
	pullRequest.base = {
		...defaultBase,
		...(prOverrides.base ?? {}),
		repo: {
			...defaultBase.repo,
			...(prOverrides.base?.repo ?? {}),
		},
	};
	pullRequest.head = {
		...defaultHead,
		...(prOverrides.head ?? {}),
		repo: {
			...defaultHead.repo,
			...(prOverrides.head?.repo ?? {}),
		},
	};
	const commits = commitsOverrides ?? [
		{ sha: PR_HEAD_SHA },
		{ sha: LIVE_PR_HEAD_SHA },
	];
	const comparison = {
		status: 'ahead',
		ahead_by: 1,
		behind_by: 0,
		total_commits: 1,
		base_commit: { sha: approval.pr_head_sha },
		merge_base_commit: { sha: approval.pr_head_sha },
		commits: [{ sha: LIVE_PR_HEAD_SHA }],
		files: [{ filename: '.github/skill-publish-approvals.json', status: 'modified' }],
		...compareOverrides,
	};

	return {
		approvalDocument,
		githubRepository: GITHUB_REPOSITORY,
		currentPrNumber: pullRequest.number,
		currentPrHeadSha: pullRequest.head.sha,
		now,
		requests,
		githubRequest: async (apiPath) => {
			requests.push(apiPath);
			if (requestError) throw requestError;
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/issues/comments/${COMMENT_ID}`) {
				return comment;
			}
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/issues/${approval.approval_issue_number}`) {
				return issue;
			}
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/pulls/${approval.pr_number}`) {
				return pullRequest;
			}
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/pulls/${approval.pr_number}/commits?per_page=100`) {
				return commits;
			}
			if (apiPath === `/repos/${GITHUB_REPOSITORY}/compare/${approval.pr_head_sha}...${LIVE_PR_HEAD_SHA}`) {
				return comparison;
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

test('valid-looking attestation cannot substitute for stale report meta hashes', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'stale-attested-report');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		report.meta.content_hash = 'a'.repeat(64);
		report.meta.tree_hash = 'b'.repeat(64);
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
		await writeAuditAttestation(packageDir, report);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, {
			enforcePublicationPolicy: false,
			requireAuditAttestation: true,
		});
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /meta\.content_hash does not match current SKILL\.md/i);
		assert.match(result.errors.join('\n'), /meta\.tree_hash does not match current package tree/i);
		assert.doesNotMatch(result.errors.join('\n'), /final_digest does not match/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('report changes after attestation invalidate the final report digest', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'changed-attested-report');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		await writeAuditAttestation(packageDir, report);
		report.security_audit.summary = 'Changed after the audit attestation was written.';
		writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, {
			enforcePublicationPolicy: false,
			requireAuditAttestation: true,
		});
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /report\.final_digest does not match skill-report\.json/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('attestation raw audit digest must be valid and differ from its input digest', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'invalid-raw-digest');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir);
		const attestation = await writeAuditAttestation(packageDir, report);
		const attestationPath = join(packageDir, 'skill-report.attestation.json');
		const { validatePackage } = await loadGate();

		await t.test('unchanged digest', async () => {
			attestation.report.raw_audit_digest = attestation.report.input_digest;
			writeFileSync(attestationPath, `${JSON.stringify(attestation, null, 2)}\n`);
			const result = await validatePackage(packageDir, {
				enforcePublicationPolicy: false,
				requireAuditAttestation: true,
			});
			assert.equal(result.ok, false);
			assert.match(result.errors.join('\n'), /did not replace the input report/i);
		});

		await t.test('invalid digest', async () => {
			attestation.report.raw_audit_digest = 'not-a-digest';
			writeFileSync(attestationPath, `${JSON.stringify(attestation, null, 2)}\n`);
			const result = await validatePackage(packageDir, {
				enforcePublicationPolicy: false,
				requireAuditAttestation: true,
			});
			assert.equal(result.ok, false);
			assert.match(result.errors.join('\n'), /report\.raw_audit_digest must be a SHA-256 hash/i);
		});
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

test('approval URL parser accepts exact GitHub pull and issue comment URLs', async () => {
	const { parseIssueCommentUrl } = await import(
		`${pathToFileURL(APPROVAL_LIBRARY_PATH).href}?test=${Date.now()}-${Math.random()}`
	);
	for (const pathKind of ['pull', 'issues']) {
		const parsed = parseIssueCommentUrl(
			`https://github.com/${GITHUB_REPOSITORY}/${pathKind}/${PR_NUMBER}#issuecomment-${COMMENT_ID}`,
		);
		assert.equal(parsed.issueNumber, PR_NUMBER);
		assert.equal(parsed.commentId, COMMENT_ID);
	}
	for (const invalid of [
		`https://github.com/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}#issuecomment-${COMMENT_ID}`,
		`https://github.com/${GITHUB_REPOSITORY}/pull/${PR_NUMBER}?diff=split#issuecomment-${COMMENT_ID}`,
		`https://example.com/${GITHUB_REPOSITORY}/pull/${PR_NUMBER}#issuecomment-${COMMENT_ID}`,
	]) {
		assert.throws(() => parseIssueCommentUrl(invalid), /valid GitHub URL|issuecomment/i);
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
			`/repos/${GITHUB_REPOSITORY}/issues/${ISSUE_NUMBER}`,
			`/repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}`,
			`/repos/${GITHUB_REPOSITORY}/compare/${PR_HEAD_SHA}...${LIVE_PR_HEAD_SHA}`,
			`/repos/${GITHUB_REPOSITORY}/collaborators/mylukin/permission`,
		]);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('selects only the approval for the current PR when an older identical-byte approval remains', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'current-pr-approval');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report);
		const currentApproval = evidence.approvalDocument.approvals[0];
		const oldPrNumber = PR_NUMBER - 1;
		const oldCommentId = COMMENT_ID - 1;
		const oldApproval = {
			...currentApproval,
			submission_id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
			approval_issue_number: oldPrNumber,
			approval_issue_url: `https://github.com/${GITHUB_REPOSITORY}/pull/${oldPrNumber}`,
			approval_comment_id: oldCommentId,
			approval_comment_url: `https://github.com/${GITHUB_REPOSITORY}/pull/${oldPrNumber}#issuecomment-${oldCommentId}`,
			pr_number: oldPrNumber,
			pr_url: `https://github.com/${GITHUB_REPOSITORY}/pull/${oldPrNumber}`,
			pr_head_ref: `submission/old-${oldPrNumber}`,
		};
		evidence.approvalDocument.approvals.unshift(oldApproval);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, true, result.errors.join('\n'));
		assert.equal(result.approval?.pr_number, PR_NUMBER);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects same-PR approval evidence from a different source repository before API calls', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'wrong-source');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const wrongSource = 'https://github.com/attacker/unrelated-source';
		const wrongBody = `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${wrongSource}\n`;
		const evidence = githubEvidence(report, {
			approvalOverrides: { submission_source_url: wrongSource },
			issueOverrides: { body: wrongBody },
			prOverrides: { body: wrongBody },
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /source repository|submission source/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('unsafe override requires the exact current triggering PR and final head', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'missing-current-pr');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report);
		delete evidence.currentPrNumber;
		delete evidence.currentPrHeadSha;

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /current.*PR|triggering PR|final.*head/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('validator rechecks approval timing against the current audit attestation', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'reaudited-approval');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const attestationPath = join(packageDir, 'skill-report.attestation.json');
		const attestation = JSON.parse(readFileSync(attestationPath, 'utf8'));
		attestation.invocation.completed_at = '2026-07-10T01:30:00.000Z';
		writeFileSync(attestationPath, `${JSON.stringify(attestation, null, 2)}\n`);
		const evidence = githubEvidence(report);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /audit_completed_at|created_at.*earlier.*attestation/i);
		assert.deepEqual(evidence.requests, []);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('approval from PR A cannot replay onto same slug and hashes in PR B', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'cross-pr-replay');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, {
			safeToPublish: false,
			sourceUrl: 'https://github.com/different-owner/different-repo/tree/main/fixture-skill',
		});
		const evidence = githubEvidence(report);
		evidence.currentPrNumber = PR_NUMBER + 1;
		evidence.currentPrHeadSha = 'd'.repeat(40);

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /current.*PR|source.*owner|source.*repo|replay/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('approval-only ancestry remains valid beyond 100 commits without commit-list membership', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'long-approval-history');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const comparisonCommits = [
			...Array.from({ length: 100 }, () => ({ sha: 'd'.repeat(40) })),
			{ sha: LIVE_PR_HEAD_SHA },
		];
		const evidence = githubEvidence(report, {
			commitsOverrides: Array.from({ length: 100 }, () => ({ sha: 'd'.repeat(40) })),
			compareOverrides: {
				ahead_by: 101,
				total_commits: 101,
				commits: comparisonCommits,
			},
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, true, result.errors.join('\n'));
		assert.equal(
			evidence.requests.some((path) => path.includes('/commits?per_page=100')),
			false,
		);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('allows the exact closed PR issue only when that PR is merged', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'merged-human-approval');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report, {
			issueOverrides: { state: 'closed' },
			prOverrides: {
				state: 'closed',
				merged: true,
				merged_at: '2026-07-10T01:30:00.000Z',
			},
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, true, result.errors.join('\n'));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects an override record without exact issue-comment identity before any API call', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'missing-comment-url');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const evidence = githubEvidence(report, {
			approvalOverrides: { approval_comment_url: undefined },
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /approval_comment_url.*required/i);
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
			approval_comment_url: undefined,
		});

		const { validatePackage } = await loadGate();
		const result = await validatePackage(packageDir, evidence);
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /approvals\[1\]\.approval_comment_url.*required/i);
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
				pattern: /created_at.*approval|created_at.*record/i,
			},
			{
				name: 'edited comment',
				evidence: githubEvidence(report, {
					commentOverrides: { updated_at: '2026-07-10T01:00:01.000Z' },
				}),
				pattern: /edited|updated_at.*created_at/i,
			},
			{
				name: 'exact report slug',
				evidence: githubEvidence(report, {
					commentOverrides: {
						body: '/approve safe-to-publish fixture-owner-other-skill'
							+ ` --content-hash ${report.meta.content_hash}`
							+ ` --tree-hash ${report.meta.tree_hash}`
							+ ` --head ${PR_HEAD_SHA}`
							+ ` --base ${PR_BASE_SHA}\n`
							+ 'Reviewed the unsafe publication recommendation and accepted the documented risk.',
					},
					}),
					pattern: /exact.*slug|safe-to-publish.*slug|bindings.*tracked/i,
			},
			{
				name: 'recorded reason',
				evidence: githubEvidence(report, {
					commentOverrides: {
						body: `/approve safe-to-publish ${report.meta.slug}`
							+ ` --content-hash ${report.meta.content_hash}`
							+ ` --tree-hash ${report.meta.tree_hash}`
							+ ` --head ${PR_HEAD_SHA}`
							+ ` --base ${PR_BASE_SHA}`
							+ '\nA different approval reason.',
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

test('rejects replay across issue, submission, PR head, slug, or package hashes', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'identity-replay');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const cases = [
			{
				name: 'unrelated old issue',
				evidence: githubEvidence(report, {
					approvalOverrides: {
						approval_issue_number: 999,
						approval_issue_url: `https://github.com/${GITHUB_REPOSITORY}/issues/999`,
						approval_comment_url: `https://github.com/${GITHUB_REPOSITORY}/issues/999#issuecomment-${COMMENT_ID}`,
					},
					commentOverrides: {
						html_url: `https://github.com/${GITHUB_REPOSITORY}/issues/999#issuecomment-${COMMENT_ID}`,
						issue_url: `https://api.github.com/repos/${GITHUB_REPOSITORY}/issues/999`,
					},
					issueOverrides: {
						body: '**Submission ID**: `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`\n'
							+ '**Source**: https://github.com/unrelated/old-submission\n',
					},
				}),
				pattern: /submission|source|approval issue|approval_issue_number|same repository and PR/i,
			},
			{
				name: 'wrong submission',
				evidence: githubEvidence(report, {
					issueOverrides: {
						body: '**Submission ID**: `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`\n'
							+ `**Source**: ${SOURCE_URL}\n`,
					},
				}),
				pattern: /submission/i,
			},
				{
					name: 'wrong PR head',
					evidence: githubEvidence(report, {
						approvalOverrides: { pr_head_sha: 'd'.repeat(40) },
						commentOverrides: {
							body: `/approve safe-to-publish ${report.meta.slug}`
								+ ` --content-hash ${report.meta.content_hash}`
								+ ` --tree-hash ${report.meta.tree_hash}`
								+ ` --head ${PR_HEAD_SHA}`
								+ ` --base ${PR_BASE_SHA}`
								+ '\nReviewed the unsafe publication recommendation and accepted the documented risk.',
						},
					}),
					pattern: /head|commit|bindings.*tracked/i,
				},
			{
				name: 'wrong slug',
				evidence: githubEvidence(report, {
					approvalOverrides: { slug: 'fixture-owner-other' },
				}),
				pattern: /tracked human approval|exact.*slug|current.*slug/i,
			},
			{
				name: 'wrong content hash',
				evidence: githubEvidence(report, {
					approvalOverrides: { content_hash: 'd'.repeat(64) },
				}),
				pattern: /tracked human approval|content_hash/i,
			},
			{
				name: 'wrong tree hash',
				evidence: githubEvidence(report, {
					approvalOverrides: { tree_hash: 'e'.repeat(64) },
				}),
				pattern: /tracked human approval|tree_hash/i,
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

test('rejects expired approval and every bot identity form', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'expiry-and-bots');
		writeSkill(packageDir);
		const report = await writeFreshReport(packageDir, { safeToPublish: false });
		const cases = [
			{
				name: 'expired',
				evidence: githubEvidence(report, {
					approvalOverrides: { expires_at: '2026-07-10T01:30:00.000Z' },
				}),
				pattern: /expired|expires_at/i,
			},
			{
				name: 'ai-skill-store bot login',
				evidence: githubEvidence(report, {
					approvalOverrides: { actor: 'ai-skill-store[bot]' },
					commentOverrides: {
						user: { login: 'ai-skill-store[bot]', type: 'User' },
					},
				}),
				pattern: /bot/i,
			},
			{
				name: 'arbitrary bot login',
				evidence: githubEvidence(report, {
					approvalOverrides: { actor: 'release-helper[bot]' },
					commentOverrides: {
						user: { login: 'release-helper[bot]', type: 'User' },
					},
				}),
				pattern: /bot/i,
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
				currentPrNumber: PR_NUMBER,
				currentPrHeadSha: LIVE_PR_HEAD_SHA,
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

test('CommonMark link parsing handles nested parentheses, angles, escapes, titles, and encoding', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'commonmark-links');
		mkdirSync(join(packageDir, 'references'), { recursive: true });
		writeFileSync(
			join(packageDir, 'SKILL.md'),
			`---
name: commonmark-links
description: CommonMark destination fixture.
---

[Nested missing](references/missing(foo).md)
[Angle destination](<references/angle target.md> "angle title")
[Escaped destination](references/escaped\\(name\\).md 'escaped title')
[Percent encoded](references/percent%20target.md)
[Reference destination][local-ref]
[HTTP](http://example.com/a.md)
[HTTPS](https://example.com/a.md)
[Mail](mailto:test@example.com)
[Data](data:text/plain,fixture)
[Anchor](#local)

[local-ref]: references/reference(target).md "reference title"
`,
		);
		for (const relativePath of [
			'angle target.md',
			'escaped(name).md',
			'percent target.md',
			'reference(target).md',
			'missing(foo',
		]) {
			writeFileSync(join(packageDir, 'references', relativePath), '# Decoy or valid target\n');
		}

		const { scanMarkdownLinks } = await loadGate();
		const errors = await scanMarkdownLinks(packageDir);
		assert.equal(errors.length, 1, errors.join('\n'));
		assert.match(errors[0], /references\/missing\(foo\)\.md/);
		assert.doesNotMatch(errors[0], /missing\(foo$/);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('tree hash uses UTF-8 byte path order and includes executable mode', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'fixture-owner', 'mode-hash');
		mkdirSync(packageDir, { recursive: true });
		writeFileSync(
			join(packageDir, 'SKILL.md'),
			'---\nname: mode-hash\ndescription: Mode hash fixture.\n---\n\n# Fixture\n',
		);
		writeFileSync(join(packageDir, 'A.md'), '# A\n');
		writeFileSync(join(packageDir, 'z.md'), '# z\n');
		writeFileSync(join(packageDir, '\u00e4.md'), '# umlaut\n');
		writeFileSync(join(packageDir, 'run.sh'), '#!/bin/sh\necho fixture\n');
		chmodSync(join(packageDir, 'run.sh'), 0o644);

		const sha256 = (value) => createHash('sha256').update(value).digest('hex');
		const expectedEntries = [
			['100644', 'A.md'],
			['100644', 'SKILL.md'],
			['100644', 'run.sh'],
			['100644', 'z.md'],
			['100644', '\u00e4.md'],
		]
			.sort((left, right) => Buffer.compare(Buffer.from(left[1], 'utf8'), Buffer.from(right[1], 'utf8')))
			.map(([mode, relativePath]) => (
				`${mode} ${relativePath}\0${sha256(readFileSync(join(packageDir, relativePath)))}`
			));

		const { calculatePackageHashes, validatePackage } = await loadGate();
		const before = await calculatePackageHashes(packageDir);
		assert.equal(before.treeHash, sha256(expectedEntries.join('\n')));
		await writeFreshReport(packageDir);

		chmodSync(join(packageDir, 'run.sh'), 0o755);
		const after = await calculatePackageHashes(packageDir);
		assert.notEqual(after.treeHash, before.treeHash);

		const result = await validatePackage(packageDir, { enforcePublicationPolicy: false });
		assert.equal(result.ok, false);
		assert.match(result.errors.join('\n'), /tree_hash.*does not match/i);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('CommonMark parser dependency is exactly pinned', () => {
	const packageDocument = JSON.parse(readFileSync(join(REPO_ROOT, 'package.json'), 'utf8'));
	assert.equal(packageDocument.dependencies.marked, '17.0.3');
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
	assert.equal(schema.properties.schema_version.const, '2.0');
	for (const field of [
		'submission_id',
		'submission_source_url',
		'approval_issue_number',
		'approval_issue_url',
		'approval_comment_id',
		'approval_comment_url',
		'actor',
		'created_at',
		'updated_at',
		'expires_at',
		'audit_completed_at',
			'pr_number',
			'pr_url',
			'pr_base_sha',
			'pr_base_ref',
			'pr_head_ref',
		'pr_head_sha',
		'slug',
		'content_hash',
		'tree_hash',
	]) {
		assert.ok(approvalSchema.required.includes(field), `${field} must be required`);
	}
	assert.match(approvalSchema.properties.approval_comment_url.pattern, /issuecomment/);
	assert.match(approvalSchema.properties.approval_comment_url.pattern, /pull/);
	assert.match(approvalSchema.properties.approval_comment_url.pattern, /issues/);
	assert.match(approvalSchema.properties.approval_issue_url.pattern, /pull/);
	assert.match(approvalSchema.properties.approval_issue_url.pattern, /issues/);
	assert.equal(approvals.schema_version, '2.0');
	assert.deepEqual(approvals.approvals, []);
});
