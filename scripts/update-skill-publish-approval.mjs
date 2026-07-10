#!/usr/bin/env node

import {
	existsSync,
	readFileSync,
	renameSync,
	writeFileSync,
} from 'node:fs';
import {
	dirname,
	join,
	resolve,
} from 'node:path';
import { pathToFileURL } from 'node:url';
import {
	approvalConstants,
	approvalExpiry,
	createGitHubRequest,
	extractSubmissionIdentity,
	parseIssueCommentUrl,
	parseSafeApprovalCommand,
	validateApprovalDocument,
	verifyTrackedApproval,
} from './lib/publication-approval.mjs';
import {
	discoverPackageDirs,
	validatePackage,
} from './validate-skill-publication.mjs';

const SHA_PATTERN = /^[a-f0-9]{40}$/;
const UUID_PATTERN = /^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;

function readJson(path, label) {
	let value;
	try {
		value = JSON.parse(readFileSync(path, 'utf8'));
	} catch (error) {
		throw new Error(`${label}: invalid JSON: ${error.message}`);
	}
	return value;
}

function atomicWriteJson(path, value) {
	const temporary = join(
		dirname(path),
		`.${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}.tmp`,
	);
	writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, { flag: 'wx' });
	renameSync(temporary, path);
}

function normalizedBody(value) {
	return typeof value === 'string' ? value.replace(/\r\n?/g, '\n') : '';
}

function normalizedRepository(value) {
	return typeof value === 'string' ? value.trim().toLowerCase() : '';
}

function normalizeSourceUrl(value) {
	if (typeof value !== 'string') return '';
	return value.trim().replace(/\.git$/i, '').replace(/\/$/, '');
}

function cachedGitHubRequest(githubRequest) {
	const cache = new Map();
	return async (apiPath) => {
		if (!cache.has(apiPath)) cache.set(apiPath, Promise.resolve().then(() => githubRequest(apiPath)));
		return cache.get(apiPath);
	};
}

function readPackageReports(packageDirs) {
	const packages = [];
	for (const packageDir of packageDirs) {
		const absoluteDir = resolve(packageDir);
		const reportPath = join(absoluteDir, 'skill-report.json');
		if (!existsSync(join(absoluteDir, 'SKILL.md'))) {
			throw new Error(`${absoluteDir}: SKILL.md is missing`);
		}
		if (!existsSync(reportPath)) {
			throw new Error(`${absoluteDir}: skill-report.json is missing`);
		}
		const report = readJson(reportPath, reportPath);
		packages.push({ packageDir: absoluteDir, report });
	}
	return packages;
}

function readAuditCompletedAt(packageDir) {
	const attestationPath = join(packageDir, 'skill-report.attestation.json');
	const attestation = readJson(attestationPath, attestationPath);
	const completedAt = attestation?.invocation?.completed_at;
	if (typeof completedAt !== 'string' || !Number.isFinite(Date.parse(completedAt))) {
		throw new Error(`${attestationPath}: invocation.completed_at is missing or invalid`);
	}
	return completedAt;
}

async function loadApprovedPackage(packageDirs, slug) {
	const selected = readPackageReports(packageDirs)
		.filter(({ report }) => report.meta?.slug === slug);
	if (selected.length !== 1) {
		throw new Error(`approval comment slug must identify exactly one final package: ${slug}`);
	}

	const packageResult = await validatePackage(selected[0].packageDir, {
		enforcePublicationPolicy: false,
		requireAuditAttestation: true,
	});
	if (!packageResult.ok) throw new Error(packageResult.errors.join('\n'));
	const report = packageResult.report;
	if (report.security_audit?.is_blocked === true) {
		throw new Error(`${slug}: is_blocked=true cannot be overridden`);
	}
	if (report.security_audit?.safe_to_publish !== false) {
		throw new Error(`${slug}: tracked override is only valid for safe_to_publish=false`);
	}
	return {
		packageDir: selected[0].packageDir,
		report,
		auditCompletedAt: readAuditCompletedAt(selected[0].packageDir),
	};
}

function assertExpectedValue(actual, expected, label) {
	if (typeof expected === 'string' && expected !== '' && actual !== expected) {
		throw new Error(`${label} does not match the current PR`);
	}
}

export async function upsertTrackedApprovals(options) {
	const approvalsPath = resolve(options.approvalsPath);
	const packageDirs = [...new Set((options.packageDirs ?? []).map((path) => resolve(path)))];
	if (packageDirs.length === 0) throw new Error('at least one package is required');
	if (!existsSync(approvalsPath)) throw new Error(`${approvalsPath}: approval document is missing`);
	if (!Number.isSafeInteger(options.issueNumber) || options.issueNumber < 1) {
		throw new Error('issueNumber must be a positive integer');
	}
	if (!Number.isSafeInteger(options.commentId) || options.commentId < 1) {
		throw new Error('commentId must be a positive integer');
	}
	if (!Number.isSafeInteger(options.prNumber) || options.prNumber < 1) {
		throw new Error('prNumber must be a positive integer');
	}
	if (options.issueNumber !== options.prNumber) {
		throw new Error('issueNumber must equal prNumber for a publication override');
	}
	if (!SHA_PATTERN.test(options.prHeadSha ?? '')) {
		throw new Error('prHeadSha must be a lowercase 40-character Git SHA');
	}
	if (
		options.expectedPrBaseSha !== undefined
		&& !SHA_PATTERN.test(options.expectedPrBaseSha)
	) {
		throw new Error('expectedPrBaseSha must be a lowercase 40-character Git SHA');
	}

	const approvalDocument = readJson(approvalsPath, approvalsPath);
	const documentErrors = validateApprovalDocument(approvalDocument);
	if (documentErrors.length > 0) throw new Error(documentErrors.join('\n'));

	const githubRepository = options.githubRepository ?? process.env.GITHUB_REPOSITORY ?? '';
	if (!/^[^/]+\/[^/]+$/.test(githubRepository)) {
		throw new Error('githubRepository must be owner/repo');
	}
	const request = cachedGitHubRequest(options.githubRequest ?? createGitHubRequest({
		token: Object.hasOwn(options, 'githubToken')
			? options.githubToken
			: (process.env.GH_TOKEN || process.env.GITHUB_TOKEN || ''),
		fetchImpl: options.fetchImpl ?? globalThis.fetch,
	}));

	const comment = await request(
		`/repos/${githubRepository}/issues/comments/${options.commentId}`,
	);
	const body = normalizedBody(comment?.body);
	const [commandLine = '', ...reasonLines] = body.split('\n');
	const command = parseSafeApprovalCommand(commandLine);
	const reason = reasonLines.join('\n').trim();
	if (reason.length < 20) throw new Error('approval reason must contain at least 20 characters');
	const slug = command.slug;
	const { report, auditCompletedAt } = await loadApprovedPackage(packageDirs, slug);
	if (
		command.contentHash !== report.meta.content_hash
		|| command.treeHash !== report.meta.tree_hash
	) {
		throw new Error('approval command content_hash and tree_hash must match the current audited package');
	}

	const issue = await request(
		`/repos/${githubRepository}/issues/${options.issueNumber}`,
	);
	const pullRequest = await request(
		`/repos/${githubRepository}/pulls/${options.prNumber}`,
	);
	const commentIdentity = parseIssueCommentUrl(comment?.html_url ?? '');
	if (
		commentIdentity.issueNumber !== options.issueNumber
		|| commentIdentity.commentId !== options.commentId
	) {
		throw new Error('approval comment does not belong to the exact approval issue');
	}
	if (
		pullRequest?.state !== 'open'
		|| pullRequest?.merged === true
		|| pullRequest?.merged_at
	) {
		throw new Error('publication approval can only be recorded on the current open PR');
	}
	if (
		normalizedRepository(pullRequest?.base?.repo?.full_name)
			!== normalizedRepository(githubRepository)
		|| normalizedRepository(pullRequest?.head?.repo?.full_name)
			!== normalizedRepository(githubRepository)
	) {
		throw new Error(`PR base and head repositories must equal ${githubRepository}`);
	}
	if (pullRequest?.head?.sha !== options.prHeadSha) {
		throw new Error('checked-out head SHA does not match the current PR head SHA');
	}
	assertExpectedValue(
		pullRequest?.base?.sha,
		options.expectedPrBaseSha,
		'expected PR base SHA',
	);
	assertExpectedValue(
		pullRequest?.base?.ref,
		options.expectedPrBaseRef,
		'expected PR base ref',
	);
	assertExpectedValue(
		pullRequest?.head?.ref,
		options.expectedPrHeadRef,
		'expected PR head ref',
	);
	if (command.baseSha !== pullRequest?.base?.sha) {
		throw new Error('approval command base SHA does not match the current PR base SHA');
	}

	const submissionIdentity = extractSubmissionIdentity(pullRequest?.body);
	if (!UUID_PATTERN.test(submissionIdentity.submissionId)) {
		throw new Error('current PR body must contain one exact submission ID');
	}
	if (normalizeSourceUrl(submissionIdentity.sourceUrl) === '') {
		throw new Error('current PR body must contain one exact GitHub source URL');
	}
	if (
		typeof options.submissionId === 'string'
		&& options.submissionId !== ''
		&& submissionIdentity.submissionId !== options.submissionId.toLowerCase()
	) {
		throw new Error('submission ID does not match the current PR body');
	}
	if (
		typeof options.submissionSourceUrl === 'string'
		&& options.submissionSourceUrl !== ''
		&& normalizeSourceUrl(submissionIdentity.sourceUrl)
			!== normalizeSourceUrl(options.submissionSourceUrl)
	) {
		throw new Error('submission source URL does not match the current PR body');
	}

	const record = {
		slug,
		content_hash: report.meta.content_hash,
		tree_hash: report.meta.tree_hash,
		submission_id: submissionIdentity.submissionId,
		submission_source_url: submissionIdentity.sourceUrl,
		approval_issue_number: options.issueNumber,
		approval_issue_url: issue?.html_url,
		approval_comment_id: options.commentId,
		approval_comment_url: comment?.html_url,
		actor: comment?.user?.login,
		created_at: comment?.created_at,
		updated_at: comment?.updated_at,
		expires_at: approvalExpiry(comment?.created_at),
		audit_completed_at: auditCompletedAt,
		reason,
		pr_number: options.prNumber,
		pr_url: pullRequest?.html_url,
		pr_base_sha: command.baseSha,
		pr_base_ref: pullRequest?.base?.ref,
		pr_head_ref: pullRequest?.head?.ref,
		pr_head_sha: command.headSha,
		scope: approvalConstants.scope,
	};

	const evidenceErrors = await verifyTrackedApproval(report, record, {
		githubRepository,
		githubRequest: request,
		now: options.now,
		auditCompletedAt,
		currentPrNumber: options.prNumber,
		currentPrHeadSha: options.prHeadSha,
	});
	if (evidenceErrors.length > 0) throw new Error(evidenceErrors.join('\n'));

	const nextApprovals = approvalDocument.approvals.filter((approval) => !(
		approval.slug === record.slug
		&& approval.submission_id === record.submission_id
	));
	nextApprovals.push(record);
	nextApprovals.sort((left, right) => (
		left.slug.localeCompare(right.slug)
		|| left.submission_id.localeCompare(right.submission_id)
	));
	const updatedDocument = {
		schema_version: approvalConstants.schemaVersion,
		approvals: nextApprovals,
	};
	const updatedErrors = validateApprovalDocument(updatedDocument);
	if (updatedErrors.length > 0) throw new Error(updatedErrors.join('\n'));

	atomicWriteJson(approvalsPath, updatedDocument);
	return { approval: record, written: 1 };
}

function parseArguments(argv) {
	const options = {
		approvalsPath: '.github/skill-publish-approvals.json',
		discoverRoots: [],
		packageDirs: [],
	};
	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		const value = argv[index + 1];
		if (arg === '--approvals') options.approvalsPath = value, index++;
		else if (arg === '--package') options.packageDirs.push(value), index++;
		else if (arg === '--discover') options.discoverRoots.push(value), index++;
		else if (arg === '--submission-id') options.submissionId = value, index++;
		else if (arg === '--submission-source-url') options.submissionSourceUrl = value, index++;
		else if (arg === '--issue-number') options.issueNumber = Number(value), index++;
		else if (arg === '--comment-id') options.commentId = Number(value), index++;
		else if (arg === '--pr-number') options.prNumber = Number(value), index++;
		else if (arg === '--pr-head-sha') options.prHeadSha = value, index++;
		else if (arg === '--expected-pr-base-sha') options.expectedPrBaseSha = value, index++;
		else if (arg === '--expected-pr-base-ref') options.expectedPrBaseRef = value, index++;
		else if (arg === '--expected-pr-head-ref') options.expectedPrHeadRef = value, index++;
		else if (arg === '--help' || arg === '-h') options.help = true;
		else throw new Error(`Unknown argument: ${arg}`);
	}
	return options;
}

function printHelp() {
	console.log(`Usage:
  node scripts/update-skill-publish-approval.mjs \
    --discover pending \
    --issue-number <number> \
    --comment-id <number> \
    --pr-number <number> \
    --pr-head-sha <sha> \
    --expected-pr-base-sha <sha> \
    --expected-pr-base-ref <ref> \
    --expected-pr-head-ref <ref>
`);
}

async function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}
	for (const root of options.discoverRoots) {
		options.packageDirs.push(...await discoverPackageDirs(root));
	}
	const result = await upsertTrackedApprovals({
		...options,
		githubRepository: process.env.GITHUB_REPOSITORY,
		githubToken: process.env.GH_TOKEN || process.env.GITHUB_TOKEN,
	});
	console.log(`UPDATED ${result.approval.slug}`);
	return 0;
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : '';
if (invokedPath === import.meta.url) {
	runCli(process.argv.slice(2))
		.then((status) => {
			process.exitCode = status;
		})
		.catch((error) => {
			console.error(`ERROR ${error.message}`);
			process.exitCode = 2;
		});
}
