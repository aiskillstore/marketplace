import { test } from 'node:test';
import assert from 'node:assert/strict';
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
const ISSUE_NUMBER = 2403;
const COMMENT_ID = 123456789;
const PR_NUMBER = 2405;
const HEAD_SHA = 'b'.repeat(40);
const APPROVAL_COMMIT_SHA = 'c'.repeat(40);
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

function makeTempRoot() {
	return mkdtempSync(join(tmpdir(), 'approval-record-'));
}

async function writeUnsafePackage(packageDir, { blocked = false } = {}) {
	mkdirSync(packageDir, { recursive: true });
	writeFileSync(
		join(packageDir, 'SKILL.md'),
		'---\nname: fixture\ndescription: Unsafe fixture.\n---\n\n# Fixture\n',
	);
	const report = {
		schema_version: '2.0',
		meta: {
			generated_at: CREATED_AT,
			slug: 'fixture-owner-fixture',
			source_url: SOURCE_URL,
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
	return report;
}

function githubFixture(report, {
	commentOverrides = {},
	issueOverrides = {},
	prOverrides = {},
	commitsOverrides,
	compareOverrides = {},
	permission = 'write',
} = {}) {
	const issueUrl = `https://github.com/${REPOSITORY}/issues/${ISSUE_NUMBER}`;
	const commentUrl = `${issueUrl}#issuecomment-${COMMENT_ID}`;
	const prUrl = `https://github.com/${REPOSITORY}/pull/${PR_NUMBER}`;
	const requests = [];
	const comment = {
		id: COMMENT_ID,
		html_url: commentUrl,
		issue_url: `https://api.github.com/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`,
		created_at: CREATED_AT,
		updated_at: CREATED_AT,
		body: `/approve safe-to-publish ${report.meta.slug}\n${REASON}`,
		user: { login: 'mylukin', type: 'User' },
		...commentOverrides,
	};
	const issue = {
		number: ISSUE_NUMBER,
		html_url: issueUrl,
		state: 'open',
		labels: [{ name: 'processing' }],
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		...issueOverrides,
	};
	const pullRequest = {
		number: PR_NUMBER,
		html_url: prUrl,
		state: 'open',
		merged: false,
		body: `**Submission ID**: \`${SUBMISSION_ID}\`\n**Source**: ${SOURCE_URL}\n`,
		base: { sha: BASE_SHA, ref: 'main' },
		head: { sha: HEAD_SHA, ref: HEAD_REF },
		...prOverrides,
	};
	const liveHeadSha = pullRequest.head?.sha;
	const commits = commitsOverrides ?? (
		liveHeadSha === HEAD_SHA
			? [{ sha: HEAD_SHA }]
			: [{ sha: HEAD_SHA }, { sha: liveHeadSha }]
	);
	const comparison = {
		status: 'ahead',
		ahead_by: 1,
		behind_by: 0,
		total_commits: 1,
		base_commit: { sha: HEAD_SHA },
		merge_base_commit: { sha: HEAD_SHA },
		commits: [{ sha: liveHeadSha }],
		files: [{ filename: APPROVAL_ARTIFACT_PATH, status: 'modified' }],
		...compareOverrides,
	};

	return {
		requests,
		githubRequest: async (apiPath) => {
			requests.push(apiPath);
			if (apiPath === `/repos/${REPOSITORY}/issues/comments/${COMMENT_ID}`) return comment;
			if (apiPath === `/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`) return issue;
			if (apiPath === `/repos/${REPOSITORY}/pulls/${PR_NUMBER}`) return pullRequest;
			if (apiPath === `/repos/${REPOSITORY}/pulls/${PR_NUMBER}/commits?per_page=100`) {
				return commits;
			}
			if (apiPath === `/repos/${REPOSITORY}/compare/${HEAD_SHA}...${liveHeadSha}`) {
				return comparison;
			}
			if (apiPath === `/repos/${REPOSITORY}/collaborators/mylukin/permission`) {
				return { permission };
			}
			throw new Error(`Unexpected GitHub API path: ${apiPath}`);
		},
	};
}

function expectedValidationRequests({ compare = true } = {}) {
	const requests = [
		`/repos/${REPOSITORY}/issues/comments/${COMMENT_ID}`,
		`/repos/${REPOSITORY}/issues/${ISSUE_NUMBER}`,
		`/repos/${REPOSITORY}/pulls/${PR_NUMBER}`,
		`/repos/${REPOSITORY}/pulls/${PR_NUMBER}/commits?per_page=100`,
	];
	if (compare) {
		requests.push(`/repos/${REPOSITORY}/compare/${HEAD_SHA}...${APPROVAL_COMMIT_SHA}`);
	}
	requests.push(`/repos/${REPOSITORY}/collaborators/mylukin/permission`);
	return requests;
}

function updateOptions(packageDir, approvalsPath, fixture) {
	return {
		approvalsPath,
		packageDirs: [packageDir],
		submissionId: SUBMISSION_ID,
		submissionSourceUrl: SOURCE_URL,
		issueNumber: ISSUE_NUMBER,
		commentId: COMMENT_ID,
		prNumber: PR_NUMBER,
		prHeadSha: HEAD_SHA,
		githubRepository: REPOSITORY,
		githubRequest: fixture.githubRequest,
		now: NOW,
	};
}

test('generated approval survives exactly one approval-artifact commit for open and merged PRs', async (t) => {
	for (const prState of [
		{
			name: 'open PR',
			prOverrides: {
				state: 'open',
				merged: false,
				merged_at: null,
				head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF },
			},
		},
		{
			name: 'merged PR',
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
				assert.equal(approval.slug, report.meta.slug);
				assert.equal(approval.content_hash, report.meta.content_hash);
				assert.equal(approval.tree_hash, report.meta.tree_hash);
				assert.equal(approval.reason, REASON);

				const validationFixture = githubFixture(report, {
					prOverrides: prState.prOverrides,
				});
				const { validatePackage } = await loadModule(GATE_PATH);
				const validated = await validatePackage(packageDir, {
					approvalDocument,
					githubRepository: REPOSITORY,
					githubRequest: validationFixture.githubRequest,
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
			now: NOW,
		});
		assert.equal(validated.ok, true, validated.errors.join('\n'));
		assert.deepEqual(validationFixture.requests, expectedValidationRequests({ compare: false }));
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
		const extraCommitSha = 'd'.repeat(40);
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
				name: 'multiple descendant commits',
				fixtureOptions: {
					prOverrides: { head: { sha: APPROVAL_COMMIT_SHA, ref: HEAD_REF } },
					commitsOverrides: [
						{ sha: HEAD_SHA },
						{ sha: extraCommitSha },
						{ sha: APPROVAL_COMMIT_SHA },
					],
					compareOverrides: {
						ahead_by: 2,
						total_commits: 2,
						commits: [{ sha: extraCommitSha }, { sha: APPROVAL_COMMIT_SHA }],
					},
				},
				pattern: /head changed|approval artifact|exactly one/i,
				expectCompare: true,
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
				pattern: /descendant approval commit|changing only/i,
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
				name: 'closed unmerged PR',
				fixtureOptions: {
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
				blocked: true,
				fixtureOptions: {},
				pattern: /is_blocked=true|cannot be overridden/i,
			},
			{
				name: 'edited comment',
				blocked: false,
				fixtureOptions: {
					commentOverrides: { updated_at: '2026-07-10T01:00:01.000Z' },
				},
				pattern: /edited|updated_at/i,
			},
			{
				name: 'bot actor',
				blocked: false,
				fixtureOptions: {
					commentOverrides: {
						user: { login: 'ai-skill-store[bot]', type: 'Bot' },
					},
				},
				pattern: /bot|user\.type/i,
			},
		];

		for (const testCase of cases) {
			await t.test(testCase.name, async () => {
				const packageDir = join(root, 'pending', testCase.name.replaceAll(' ', '-'));
				const report = await writeUnsafePackage(packageDir, { blocked: testCase.blocked });
				const fixture = githubFixture(report, testCase.fixtureOptions);
				await assert.rejects(
					upsertTrackedApprovals(updateOptions(packageDir, approvalsPath, fixture)),
					testCase.pattern,
				);
				assert.equal(readFileSync(approvalsPath, 'utf8'), original);
			});
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
