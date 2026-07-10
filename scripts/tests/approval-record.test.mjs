import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
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
const GATE_PATH = join(REPO_ROOT, 'scripts', 'validate-skill-publication.mjs');
const UPDATE_PATH = join(REPO_ROOT, 'scripts', 'update-skill-publish-approval.mjs');
const REPOSITORY = 'aiskillstore/marketplace';
const SUBMISSION_ID = '12345678-1234-4234-8234-123456789abc';
const SOURCE_URL = 'https://github.com/example/fixture';
const PR_NUMBER = 2405;
const ISSUE_NUMBER = PR_NUMBER;
const COMMENT_ID = 123456789;
const SECOND_COMMENT_ID = 123456790;
const HEAD_SHA = 'b'.repeat(40);
const APPROVAL_COMMIT_SHA = 'c'.repeat(40);
const SECOND_APPROVAL_COMMIT_SHA = 'd'.repeat(40);
const BASE_SHA = 'a'.repeat(40);
const HEAD_REF = `submission/fixture-${SUBMISSION_ID}`;
const CREATED_AT = '2026-07-10T01:00:00.000Z';
const MERGED_AT = '2026-07-10T01:30:00.000Z';
const NOW = Date.parse('2026-07-10T02:00:00.000Z');
const REASON = 'Reviewed the exact unsafe package and accepted the documented publication risk.';
const APPROVAL_ARTIFACT_PATH = '.github/skill-publish-approvals.json';

async function loadModule(path) {
	return import(`${pathToFileURL(path).href}?test=${Date.now()}-${Math.random()}`);
}

function approvalCommand(report, {
	headSha = HEAD_SHA,
	baseSha = BASE_SHA,
} = {}) {
	return `/approve safe-to-publish ${report.meta.slug}`
		+ ` --content-hash ${report.meta.content_hash}`
		+ ` --tree-hash ${report.meta.tree_hash}`
		+ ` --head ${headSha}`
		+ ` --base ${baseSha}`;
}

function makeTempRoot() {
	return mkdtempSync(join(tmpdir(), 'approval-record-'));
}

async function writeAuditAttestation(packageDir, report) {
	const { calculatePackageHashes } = await loadModule(GATE_PATH);
	const hashes = await calculatePackageHashes(packageDir);
	const reportDigest = createHash('sha256')
		.update(readFileSync(join(packageDir, 'skill-report.json')))
		.digest('hex');
	const attestation = {
		schema_version: '1.0',
		slug: report.meta.slug,
		producer: {
			repository: 'aiskillstore/skillstore',
			commit: 'e'.repeat(40),
			package_version: '9.9.9',
			audit_command_version: '1.2.0',
		},
		invocation: {
			id: SUBMISSION_ID,
			started_at: '2026-07-10T00:59:59.000Z',
			completed_at: CREATED_AT,
			cwd: '/tmp/skillstore-audit',
			command: [
				process.execPath,
				'--import',
				'tsx',
				'/tmp/skillstore-audit/src/cli/index.ts',
				'skill',
				'audit',
				'../marketplace/pending',
				'--slugs',
				report.meta.slug,
				'--model',
				'codex:gpt-5.5:high',
			],
			skills_root: '/tmp/marketplace/pending',
			slugs: [report.meta.slug],
			model: 'codex:gpt-5.5:high',
			stdout_digest: 'f'.repeat(64),
			stderr_digest: '0'.repeat(64),
		},
		report: {
			input_digest: '1'.repeat(64),
			raw_audit_digest: '2'.repeat(64),
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

async function writeUnsafePackage(packageDir, {
	attested = true,
	blocked = false,
	slug = 'fixture-owner-fixture',
	skillName = 'fixture',
} = {}) {
	mkdirSync(packageDir, { recursive: true });
	writeFileSync(
		join(packageDir, 'SKILL.md'),
		`---\nname: ${skillName}\ndescription: Unsafe fixture.\n---\n\n# Fixture\n`,
	);
	const report = {
		schema_version: '2.0',
		meta: {
			generated_at: CREATED_AT,
			slug,
			source_url: SOURCE_URL,
			source_ref: 'main',
			model: 'codex',
			analysis_version: '3.0.0',
			source_type: 'community',
			content_hash: '0'.repeat(64),
			tree_hash: '1'.repeat(64),
			provenance: {
				model_requested: 'codex:gpt-5.5:high',
				model_effective: 'codex:gpt-5.5:high',
				fallback_chain: [{ agent: 'codex', outcome: 'success' }],
				analysis_version: '3.0.0',
			},
		},
		security_audit: {
			risk_level: blocked ? 'critical' : 'medium',
			is_blocked: blocked,
			safe_to_publish: false,
			analysis_status: 'ok',
			summary: 'Fixture audit.',
			files_scanned: 1,
			total_lines: 5,
			audit_model: 'codex:gpt-5.5:high',
			audited_at: CREATED_AT,
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
	writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
	const { calculatePackageHashes } = await loadModule(GATE_PATH);
	const hashes = await calculatePackageHashes(packageDir);
	report.meta.content_hash = hashes.contentHash;
	report.meta.tree_hash = hashes.treeHash;
	writeFileSync(join(packageDir, 'skill-report.json'), `${JSON.stringify(report, null, 2)}\n`);
	if (attested) await writeAuditAttestation(packageDir, report);
	return report;
}

function githubFixture(report, {
	approvedHeadSha = HEAD_SHA,
	commentId = COMMENT_ID,
	commentPath = 'pull',
	commentOverrides = {},
	issuePath = commentPath,
	issueOverrides = {},
	prOverrides = {},
	commitsOverrides,
	compareOverrides = {},
	permission = 'write',
	reason = REASON,
} = {}) {
	const issueUrl = `https://github.com/${REPOSITORY}/${issuePath}/${ISSUE_NUMBER}`;
	const commentUrl = `https://github.com/${REPOSITORY}/${commentPath}/${ISSUE_NUMBER}#issuecomment-${commentId}`;
	const prUrl = `https://github.com/${REPOSITORY}/pull/${PR_NUMBER}`;
	const requests = [];
	const comment = {
		id: commentId,
		html_url: commentUrl,
		issue_url: `https://api.github.com/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`,
		created_at: CREATED_AT,
		updated_at: CREATED_AT,
		body: `${approvalCommand(report, { headSha: approvedHeadSha })}\n${reason}`,
		user: { login: 'mylukin', type: 'User' },
		...commentOverrides,
	};
	const issue = {
		number: ISSUE_NUMBER,
		html_url: issueUrl,
		state: 'open',
		labels: [{ name: 'pending-review' }],
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		pull_request: {
			url: `https://api.github.com/repos/${REPOSITORY}/pulls/${PR_NUMBER}`,
		},
		...issueOverrides,
	};
	const defaultBase = {
		sha: BASE_SHA,
		ref: 'main',
		repo: { full_name: REPOSITORY },
	};
	const defaultHead = {
		sha: approvedHeadSha,
		ref: HEAD_REF,
		repo: { full_name: REPOSITORY },
	};
	const pullRequest = {
		number: PR_NUMBER,
		html_url: prUrl,
		state: 'open',
		merged: false,
		merged_at: null,
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		base: {
			...defaultBase,
			...(prOverrides.base ?? {}),
			repo: {
				...defaultBase.repo,
				...(prOverrides.base?.repo ?? {}),
			},
		},
		head: {
			...defaultHead,
			...(prOverrides.head ?? {}),
			repo: {
				...defaultHead.repo,
				...(prOverrides.head?.repo ?? {}),
			},
		},
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
	const liveHeadSha = pullRequest.head?.sha;
	const commits = commitsOverrides ?? (
		liveHeadSha === approvedHeadSha
			? [{ sha: approvedHeadSha }]
			: [{ sha: approvedHeadSha }, { sha: liveHeadSha }]
	);
	const comparison = {
		status: 'ahead',
		ahead_by: 1,
		behind_by: 0,
		total_commits: 1,
		base_commit: { sha: approvedHeadSha },
		merge_base_commit: { sha: approvedHeadSha },
		commits: [{ sha: liveHeadSha }],
		files: [{ filename: APPROVAL_ARTIFACT_PATH, status: 'modified' }],
		...compareOverrides,
	};

	return {
		requests,
		currentPrNumber: PR_NUMBER,
		currentPrHeadSha: liveHeadSha,
		githubRequest: async (apiPath) => {
			requests.push(apiPath);
			if (apiPath === `/repos/${REPOSITORY}/issues/comments/${commentId}`) return comment;
			if (apiPath === `/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`) return issue;
			if (apiPath === `/repos/${REPOSITORY}/pulls/${PR_NUMBER}`) return pullRequest;
			if (apiPath === `/repos/${REPOSITORY}/pulls/${PR_NUMBER}/commits?per_page=100`) {
				return commits;
			}
			if (apiPath === `/repos/${REPOSITORY}/compare/${approvedHeadSha}...${liveHeadSha}`) {
				return comparison;
			}
			if (apiPath === `/repos/${REPOSITORY}/collaborators/mylukin/permission`) {
				return { permission };
			}
			throw new Error(`Unexpected GitHub API path: ${apiPath}`);
		},
	};
}

function expectedValidationRequests({
	approvedHeadSha = HEAD_SHA,
	commentId = COMMENT_ID,
	compare = true,
	liveHeadSha = APPROVAL_COMMIT_SHA,
} = {}) {
	const requests = [
		`/repos/${REPOSITORY}/issues/comments/${commentId}`,
		`/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`,
		`/repos/${REPOSITORY}/pulls/${PR_NUMBER}`,
	];
	if (compare) {
		requests.push(`/repos/${REPOSITORY}/compare/${approvedHeadSha}...${liveHeadSha}`);
	}
	requests.push(`/repos/${REPOSITORY}/collaborators/mylukin/permission`);
	return requests;
}

function updateOptions(packageDirs, approvalsPath, fixture, overrides = {}) {
	return {
		approvalsPath,
		packageDirs: Array.isArray(packageDirs) ? packageDirs : [packageDirs],
		submissionId: SUBMISSION_ID,
		submissionSourceUrl: SOURCE_URL,
		issueNumber: ISSUE_NUMBER,
		commentId: COMMENT_ID,
		prNumber: PR_NUMBER,
		prHeadSha: HEAD_SHA,
		expectedPrBaseSha: BASE_SHA,
		expectedPrBaseRef: 'main',
		expectedPrHeadRef: HEAD_REF,
		githubRepository: REPOSITORY,
		githubRequest: fixture.githubRequest,
		now: NOW,
		...overrides,
	};
}

test('PR-comment approval survives approval-only commits for open and merged PRs', async (t) => {
	for (const prState of [
		{
			name: 'open PR',
			issueOverrides: {
				state: 'open',
			},
			prOverrides: {
				state: 'open',
				merged: false,
				merged_at: null,
				head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF },
			},
		},
		{
			name: 'merged PR',
			issueOverrides: {
				state: 'closed',
			},
			prOverrides: {
				state: 'closed',
				merged: true,
				merged_at: MERGED_AT,
				head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF },
			},
		},
	]) {
		await t.test(prState.name, async () => {
			const root = makeTempRoot();
			try {
				const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
				const approvalsPath = join(root, 'skill-publish-approvals.json');
				const report = await writeUnsafePackage(packageDir);
				const generationFixture = githubFixture(report);
				writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

				const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
				const update = await upsertTrackedApprovals(
					updateOptions(packageDir, approvalsPath, generationFixture),
				);
				assert.equal(update.written, 1);

				const approvalDocument = JSON.parse(readFileSync(approvalsPath, 'utf8'));
				const approval = approvalDocument.approvals[0];
				assert.equal(approval.pr_head_sha, HEAD_SHA);
				assert.equal(approval.submission_id, SUBMISSION_ID);
				assert.equal(approval.approval_issue_number, ISSUE_NUMBER);
				assert.equal(approval.approval_comment_id, COMMENT_ID);
				assert.equal(approval.pr_number, PR_NUMBER);
				assert.equal(approval.pr_base_ref, 'main');
				assert.equal(approval.slug, report.meta.slug);
				assert.equal(approval.content_hash, report.meta.content_hash);
				assert.equal(approval.tree_hash, report.meta.tree_hash);
				assert.equal(approval.audit_completed_at, CREATED_AT);
				assert.equal(approval.reason, REASON);

				const validationFixture = githubFixture(report, {
					issueOverrides: prState.issueOverrides,
					prOverrides: prState.prOverrides,
				});
				const { validatePackage } = await loadModule(GATE_PATH);
				const validated = await validatePackage(packageDir, {
					approvalDocument,
					githubRepository: REPOSITORY,
					githubRequest: validationFixture.githubRequest,
					currentPrNumber: validationFixture.currentPrNumber,
					currentPrHeadSha: validationFixture.currentPrHeadSha,
					now: NOW,
				});
				assert.equal(validated.ok, true, validated.errors.join('\n'));
				assert.deepEqual(validationFixture.requests, expectedValidationRequests());
			} finally {
				rmSync(root, { recursive: true, force: true });
			}
		});
	}
});

test('earlier approvals survive multiple approval-only commits on the same PR branch', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const report = await writeUnsafePackage(packageDir);
		const generationFixture = githubFixture(report);
		writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		await upsertTrackedApprovals(updateOptions(packageDir, approvalsPath, generationFixture));
		const approvalDocument = JSON.parse(readFileSync(approvalsPath, 'utf8'));
		const validationFixture = githubFixture(report, {
			prOverrides: {
				head: { sha: SECOND_APPROVAL_COMMIT_SHA },
			},
			commitsOverrides: [
				{ sha: HEAD_SHA },
				{ sha: APPROVAL_COMMIT_SHA },
				{ sha: SECOND_APPROVAL_COMMIT_SHA },
			],
			compareOverrides: {
				ahead_by: 2,
				total_commits: 2,
				commits: [
					{ sha: APPROVAL_COMMIT_SHA },
					{ sha: SECOND_APPROVAL_COMMIT_SHA },
				],
			},
		});

		const { validatePackage } = await loadModule(GATE_PATH);
		const validated = await validatePackage(packageDir, {
			approvalDocument,
			githubRepository: REPOSITORY,
			githubRequest: validationFixture.githubRequest,
			currentPrNumber: validationFixture.currentPrNumber,
			currentPrHeadSha: validationFixture.currentPrHeadSha,
			now: NOW,
		});
		assert.equal(validated.ok, true, validated.errors.join('\n'));
		assert.deepEqual(validationFixture.requests, expectedValidationRequests({
			liveHeadSha: SECOND_APPROVAL_COMMIT_SHA,
		}));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('generated approval retains the equal-head compatibility path without compare', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const report = await writeUnsafePackage(packageDir);
		const fixture = githubFixture(report);
		writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		await upsertTrackedApprovals(updateOptions(packageDir, approvalsPath, fixture));
		const approvalDocument = JSON.parse(readFileSync(approvalsPath, 'utf8'));

		const validationFixture = githubFixture(report);
		const { validatePackage } = await loadModule(GATE_PATH);
		const validated = await validatePackage(packageDir, {
			approvalDocument,
			githubRepository: REPOSITORY,
			githubRequest: validationFixture.githubRequest,
			currentPrNumber: validationFixture.currentPrNumber,
			currentPrHeadSha: validationFixture.currentPrHeadSha,
			now: NOW,
		});
		assert.equal(validated.ok, true, validated.errors.join('\n'));
		assert.deepEqual(validationFixture.requests, expectedValidationRequests({ compare: false }));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('safe approval command binds hashes and PR SHAs in one exact fixed-order line', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const report = await writeUnsafePackage(packageDir);
		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

		const validFixture = githubFixture(report);
		const update = await upsertTrackedApprovals(
			updateOptions(packageDir, approvalsPath, validFixture),
		);
		assert.equal(update.approval.pr_head_sha, HEAD_SHA);
		assert.equal(update.approval.pr_base_sha, BASE_SHA);

		for (const [name, firstLine] of [
			['slug only', `/approve safe-to-publish ${report.meta.slug}`],
			[
				'wrong option order',
				`/approve safe-to-publish ${report.meta.slug}`
					+ ` --tree-hash ${report.meta.tree_hash}`
					+ ` --content-hash ${report.meta.content_hash}`
					+ ` --head ${HEAD_SHA}`
					+ ` --base ${BASE_SHA}`,
			],
			[
				'wrong content hash',
				approvalCommand({
					meta: { ...report.meta, content_hash: 'f'.repeat(64) },
				}),
			],
			[
				'wrong approved head',
				approvalCommand(report, { headSha: 'e'.repeat(40) }),
			],
			[
				'wrong base',
				approvalCommand(report, { baseSha: 'd'.repeat(40) }),
			],
		]) {
			await t.test(name, async () => {
				writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');
				const fixture = githubFixture(report, {
					commentOverrides: { body: `${firstLine}\n${REASON}` },
				});
				await assert.rejects(
					upsertTrackedApprovals(updateOptions(
						packageDir,
						approvalsPath,
						fixture,
					)),
					/bind|command|content_hash|head|base|exact/i,
				);
			});
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('pre-audit approval comments fail closed and are never written', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const original = '{"schema_version":"2.0","approvals":[]}\n';
		const report = await writeUnsafePackage(packageDir);
		const fixture = githubFixture(report, {
			commentOverrides: {
				created_at: '2026-07-10T00:59:58.000Z',
				updated_at: '2026-07-10T00:59:58.000Z',
			},
		});
		writeFileSync(approvalsPath, original);

		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		await assert.rejects(
			upsertTrackedApprovals(updateOptions(packageDir, approvalsPath, fixture)),
			/audit|attestation|generated_at|audited_at|completed_at|pre-audit/i,
		);
		assert.equal(readFileSync(approvalsPath, 'utf8'), original);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('generated approval rejects replay and every non-artifact PR-head transition', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'pending', 'fixture-owner', 'fixture');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const report = await writeUnsafePackage(packageDir);
		const generationFixture = githubFixture(report);
		writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		await upsertTrackedApprovals(updateOptions(packageDir, approvalsPath, generationFixture));
		const generatedDocument = JSON.parse(readFileSync(approvalsPath, 'utf8'));
		const cases = [
			{
				name: 'unrelated issue',
				fixtureOptions: {
					issueOverrides: {
						body: '**Submission ID**: `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`\n'
							+ '**Source**: https://github.com/unrelated/replayed-submission\n',
					},
				},
				pattern: /submission|source/i,
			},
			{
				name: 'edited approval comment',
				fixtureOptions: {
					commentOverrides: { updated_at: '2026-07-10T01:00:01.000Z' },
				},
				pattern: /edited|updated_at/i,
			},
			{
				name: 'bot approval actor',
				fixtureOptions: {
					commentOverrides: { user: { login: 'mylukin', type: 'Bot' } },
				},
				pattern: /human User|Bot/i,
			},
			{
				name: 'wrong slug binding',
				approvalOverrides: { slug: 'fixture-owner-replayed' },
				pattern: /tracked human approval|exact.*slug/i,
			},
			{
				name: 'wrong content hash binding',
				approvalOverrides: { content_hash: 'e'.repeat(64) },
				pattern: /tracked human approval|content_hash/i,
			},
			{
				name: 'wrong tree hash binding',
				approvalOverrides: { tree_hash: 'f'.repeat(64) },
				pattern: /tracked human approval|tree_hash/i,
			},
			{
				name: 'wrong submission binding',
				fixtureOptions: {
					prOverrides: {
						body: '**Submission ID**: `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`\n'
							+ `**Source**: ${SOURCE_URL}\n`,
					},
				},
				pattern: /submission/i,
			},
			{
				name: 'wrong base binding',
				fixtureOptions: {
					prOverrides: { base: { sha: 'e'.repeat(40), ref: 'main' } },
				},
				pattern: /base SHA/i,
			},
			{
				name: 'wrong compare ancestor',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF } },
					compareOverrides: {
						base_commit: { sha: 'e'.repeat(40) },
						merge_base_commit: { sha: 'e'.repeat(40) },
					},
				},
				pattern: /head changed|approval artifact|descendant/i,
				expectCompare: true,
			},
			{
				name: 'wrong head repository',
				fixtureOptions: {
					prOverrides: {
						head: {
							sha: APPROVAL_COMMIT_SHA,
							repo: { full_name: 'attacker/fork' },
						},
					},
				},
				pattern: /head repositor|base and head repositor|publication repository|same repository/i,
			},
			{
				name: 'extra changed file',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF } },
					compareOverrides: {
						files: [
							{ filename: APPROVAL_ARTIFACT_PATH, status: 'modified' },
							{ filename: 'pending/fixture-owner/fixture/SKILL.md', status: 'modified' },
						],
					},
				},
				pattern: /descendant approval commit|approval-only|changing only/i,
				expectCompare: true,
			},
			{
				name: 'diverged compare',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF } },
					compareOverrides: { status: 'diverged', ahead_by: 1, behind_by: 1 },
				},
				pattern: /head changed|approval artifact|descendant/i,
				expectCompare: true,
			},
			{
				name: 'zero compared commits',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA } },
					compareOverrides: {
						ahead_by: 0,
						total_commits: 0,
						commits: [],
					},
				},
				pattern: /approval-only|approval artifact|descendant|commit/i,
				expectCompare: true,
			},
			{
				name: 'unknown compared commits',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA } },
					compareOverrides: {
						ahead_by: undefined,
						total_commits: undefined,
						commits: undefined,
					},
				},
				pattern: /approval-only|approval artifact|descendant|commit/i,
				expectCompare: true,
			},
			{
				name: 'closed unmerged PR',
				fixtureOptions: {
					issueOverrides: {
						state: 'closed',
					},
					prOverrides: {
						state: 'closed',
						merged: false,
						merged_at: null,
					},
				},
				pattern: /open or closed.*merged=true/i,
			},
			{
				name: 'closed PR missing merged timestamp',
				fixtureOptions: {
					issueOverrides: {
						state: 'closed',
					},
					prOverrides: {
						state: 'closed',
						merged: true,
						merged_at: null,
					},
				},
				pattern: /open or merged|merged_at/i,
			},
		];

		const { validatePackage } = await loadModule(GATE_PATH);
		for (const testCase of cases) {
			await t.test(testCase.name, async () => {
				const approvalDocument = structuredClone(generatedDocument);
				Object.assign(
					approvalDocument.approvals[0],
					testCase.approvalOverrides ?? {},
				);
				const fixture = githubFixture(report, testCase.fixtureOptions);
				const result = await validatePackage(packageDir, {
					approvalDocument,
					githubRepository: REPOSITORY,
					githubRequest: fixture.githubRequest,
					currentPrNumber: fixture.currentPrNumber,
					currentPrHeadSha: fixture.currentPrHeadSha,
					now: NOW,
				});
				assert.equal(result.ok, false);
				assert.match(result.errors.join('\n'), testCase.pattern);
				if (testCase.expectCompare) {
					assert.ok(
						fixture.requests.includes(
							`/repos/${REPOSITORY}/compare/${HEAD_SHA}...${APPROVAL_COMMIT_SHA}`,
						),
						'head-transition rejection must use the exact GitHub compare endpoint',
					);
				}
			});
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('two unsafe package approvals coexist and validate after separate PR comments', async () => {
	const root = makeTempRoot();
	try {
		const firstDir = join(root, 'pending', 'fixture-owner', 'first');
		const secondDir = join(root, 'pending', 'fixture-owner', 'second');
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const firstReport = await writeUnsafePackage(firstDir, {
			slug: 'fixture-owner-first',
			skillName: 'first',
		});
		const secondReport = await writeUnsafePackage(secondDir, {
			slug: 'fixture-owner-second',
			skillName: 'second',
		});
		const packageDirs = [firstDir, secondDir];
		writeFileSync(approvalsPath, '{"schema_version":"2.0","approvals":[]}\n');

		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		const firstFixture = githubFixture(firstReport);
		await upsertTrackedApprovals(updateOptions(
			packageDirs,
			approvalsPath,
			firstFixture,
		));

		const secondFixture = githubFixture(secondReport, {
			approvedHeadSha: APPROVAL_COMMIT_SHA,
			commentId: SECOND_COMMENT_ID,
		});
		await upsertTrackedApprovals(updateOptions(
			packageDirs,
			approvalsPath,
			secondFixture,
			{
				commentId: SECOND_COMMENT_ID,
				prHeadSha: APPROVAL_COMMIT_SHA,
			},
		));

		const approvalDocument = JSON.parse(readFileSync(approvalsPath, 'utf8'));
		assert.deepEqual(
			approvalDocument.approvals.map((approval) => approval.slug),
			[firstReport.meta.slug, secondReport.meta.slug],
		);

		const finalCommits = [
			{ sha: HEAD_SHA },
			{ sha: APPROVAL_COMMIT_SHA },
			{ sha: SECOND_APPROVAL_COMMIT_SHA },
		];
		const firstValidation = githubFixture(firstReport, {
			prOverrides: { head: { sha: SECOND_APPROVAL_COMMIT_SHA } },
			commitsOverrides: finalCommits,
			compareOverrides: {
				ahead_by: 2,
				total_commits: 2,
				commits: [
					{ sha: APPROVAL_COMMIT_SHA },
					{ sha: SECOND_APPROVAL_COMMIT_SHA },
				],
			},
		});
		const secondValidation = githubFixture(secondReport, {
			approvedHeadSha: APPROVAL_COMMIT_SHA,
			commentId: SECOND_COMMENT_ID,
			prOverrides: { head: { sha: SECOND_APPROVAL_COMMIT_SHA } },
			commitsOverrides: finalCommits,
		});
		const { validatePackage } = await loadModule(GATE_PATH);
		for (const [packageDir, fixture] of [
			[firstDir, firstValidation],
			[secondDir, secondValidation],
		]) {
			const result = await validatePackage(packageDir, {
				approvalDocument,
				githubRepository: REPOSITORY,
				githubRequest: fixture.githubRequest,
				currentPrNumber: fixture.currentPrNumber,
				currentPrHeadSha: fixture.currentPrHeadSha,
				now: NOW,
			});
			assert.equal(result.ok, true, result.errors.join('\n'));
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('validates all evidence before writing and never records blocked, edited, or bot approval', async (t) => {
	const root = makeTempRoot();
	try {
		const approvalsPath = join(root, 'skill-publish-approvals.json');
		const original = '{"schema_version":"2.0","approvals":[]}\n';
		writeFileSync(approvalsPath, original);
		const { upsertTrackedApprovals } = await loadModule(UPDATE_PATH);
		const cases = [
			{
				name: 'hard blocked package',
				packageOptions: { blocked: true },
				fixtureOptions: {},
				pattern: /is_blocked=true|cannot be overridden/i,
			},
			{
				name: 'missing audit attestation',
				packageOptions: { attested: false },
				fixtureOptions: {},
				pattern: /attestation.*missing/i,
			},
			{
				name: 'stale audited package hashes',
				packageOptions: {},
				mutatePackage(packageDir) {
					writeFileSync(
						join(packageDir, 'SKILL.md'),
						'---\nname: fixture\ndescription: Changed after audit.\n---\n\n# Changed\n',
					);
				},
				fixtureOptions: {},
				pattern: /content_hash|tree_hash|attestation/i,
			},
			{
				name: 'edited comment',
				packageOptions: {},
				fixtureOptions: {
					commentOverrides: { updated_at: '2026-07-10T01:00:01.000Z' },
				},
				pattern: /edited|updated_at/i,
			},
			{
				name: 'bot actor',
				packageOptions: {},
				fixtureOptions: {
					commentOverrides: {
						user: { login: 'ai-skill-store[bot]', type: 'Bot' },
					},
				},
				pattern: /bot|user\.type/i,
			},
			{
				name: 'wrong exact slug',
				packageOptions: {},
				fixtureOptions(report) {
					return {
						commentOverrides: {
							body: `${approvalCommand({
								meta: {
									...report.meta,
									slug: 'fixture-owner-other',
								},
							})}\n${REASON}`,
						},
					};
				},
				pattern: /slug.*exactly one|exact.*slug/i,
			},
			{
				name: 'wrong submission id',
				packageOptions: {},
				fixtureOptions: {},
				updateOverrides: {
					submissionId: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
				},
				pattern: /submission/i,
			},
			{
				name: 'wrong source url',
				packageOptions: {},
				fixtureOptions: {},
				updateOverrides: {
					submissionSourceUrl: 'https://github.com/unrelated/source',
				},
				pattern: /source/i,
			},
			{
				name: 'wrong base sha',
				packageOptions: {},
				fixtureOptions: {},
				updateOverrides: {
					expectedPrBaseSha: '9'.repeat(40),
				},
				pattern: /base SHA/i,
			},
			{
				name: 'wrong checked out head',
				packageOptions: {},
				fixtureOptions: {},
				updateOverrides: {
					prHeadSha: '8'.repeat(40),
				},
				pattern: /head SHA|checked-out/i,
			},
			{
				name: 'wrong head repository',
				packageOptions: {},
				fixtureOptions: {
					prOverrides: {
						head: { repo: { full_name: 'attacker/fork' } },
					},
				},
				pattern: /head repositor|base and head repositor|publication repository|same repository/i,
			},
		];

		for (const testCase of cases) {
			await t.test(testCase.name, async () => {
				const packageDir = join(root, 'pending', testCase.name.replaceAll(' ', '-'));
				const report = await writeUnsafePackage(packageDir, testCase.packageOptions);
				testCase.mutatePackage?.(packageDir);
				const fixture = githubFixture(
					report,
					typeof testCase.fixtureOptions === 'function'
						? testCase.fixtureOptions(report)
						: testCase.fixtureOptions,
				);
				await assert.rejects(
					upsertTrackedApprovals(updateOptions(
						packageDir,
						approvalsPath,
						fixture,
						testCase.updateOverrides,
					)),
					testCase.pattern,
				);
				assert.equal(readFileSync(approvalsPath, 'utf8'), original);
			});
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
