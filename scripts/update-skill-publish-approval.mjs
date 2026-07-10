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
	parseIssueCommentUrl,
	validateApprovalDocument,
	verifyTrackedApproval,
} from './lib/publication-approval.mjs';
import {
	calculatePackageHashes,
	discoverPackageDirs,
} from './validate-skill-publication.mjs';

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

async function loadReports(packageDirs) {
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
		if (report.security_audit?.is_blocked === true) {
			throw new Error(`${report.meta?.slug ?? absoluteDir}: is_blocked=true cannot be overridden`);
		}
		const hashes = await calculatePackageHashes(absoluteDir);
		if (
			report.meta?.content_hash !== hashes.contentHash
			|| report.meta?.tree_hash !== hashes.treeHash
		) {
			throw new Error(`${report.meta?.slug ?? absoluteDir}: report hashes are stale`);
		}
		packages.push({ packageDir: absoluteDir, report });
	}
	return packages;
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
	if (!/^[a-f0-9]{40}$/.test(options.prHeadSha ?? '')) {
		throw new Error('prHeadSha must be a lowercase 40-character Git SHA');
	}

	const packages = await loadReports(packageDirs);
	const approvalDocument = readJson(approvalsPath, approvalsPath);
	const documentErrors = validateApprovalDocument(approvalDocument);
	if (documentErrors.length > 0) throw new Error(documentErrors.join('\n'));

	const githubRepository = options.githubRepository ?? process.env.GITHUB_REPOSITORY ?? '';
	if (!/^[^/]+\/[^/]+$/.test(githubRepository)) {
		throw new Error('githubRepository must be owner/repo');
	}
	const githubRequest = options.githubRequest ?? createGitHubRequest({
		token: Object.hasOwn(options, 'githubToken')
			? options.githubToken
			: (process.env.GH_TOKEN || process.env.GITHUB_TOKEN || ''),
		fetchImpl: options.fetchImpl ?? globalThis.fetch,
	});

	const comment = await githubRequest(
		`/repos/${githubRepository}/issues/comments/${options.commentId}`,
	);
	const body = normalizedBody(comment?.body);
	const [commandLine = '', ...reasonLines] = body.split('\n');
	const commandMatch = commandLine.trim().match(
		/^\/approve safe-to-publish ([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$/,
	);
	if (!commandMatch) {
		throw new Error('approval comment must use /approve safe-to-publish <exact-report-slug>');
	}
	const reason = reasonLines.join('\n').trim();
	if (reason.length < 20) throw new Error('approval reason must contain at least 20 characters');
	const slug = commandMatch[1];
	const selected = packages.filter(({ report }) => report.meta?.slug === slug);
	if (selected.length !== 1) {
		throw new Error(`approval comment slug must identify exactly one final package: ${slug}`);
	}
	const report = selected[0].report;
	if (report.security_audit?.safe_to_publish !== false) {
		throw new Error(`${slug}: tracked override is only valid for safe_to_publish=false`);
	}

	const issue = await githubRequest(
		`/repos/${githubRepository}/issues/${options.issueNumber}`,
	);
	const pullRequest = await githubRequest(
		`/repos/${githubRepository}/pulls/${options.prNumber}`,
	);
	const commentIdentity = parseIssueCommentUrl(comment?.html_url ?? '');
	if (
		commentIdentity.issueNumber !== options.issueNumber
		|| commentIdentity.commentId !== options.commentId
	) {
		throw new Error('approval comment does not belong to the exact approval issue');
	}

	const record = {
		slug,
		content_hash: report.meta.content_hash,
		tree_hash: report.meta.tree_hash,
		submission_id: options.submissionId,
		submission_source_url: options.submissionSourceUrl,
		approval_issue_number: options.issueNumber,
		approval_issue_url: issue?.html_url,
		approval_comment_id: options.commentId,
		approval_comment_url: comment?.html_url,
		actor: comment?.user?.login,
		created_at: comment?.created_at,
		updated_at: comment?.updated_at,
		expires_at: approvalExpiry(comment?.created_at),
		reason,
		pr_number: options.prNumber,
		pr_url: pullRequest?.html_url,
		pr_base_sha: pullRequest?.base?.sha,
		pr_head_ref: pullRequest?.head?.ref,
		pr_head_sha: options.prHeadSha,
		scope: approvalConstants.scope,
	};

	const evidenceErrors = await verifyTrackedApproval(report, record, {
		githubRepository,
		githubRequest,
		now: options.now,
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
		else if (arg === '--help' || arg === '-h') options.help = true;
		else throw new Error(`Unknown argument: ${arg}`);
	}
	return options;
}

function printHelp() {
	console.log(`Usage:
  node scripts/update-skill-publish-approval.mjs \
    --discover pending \
    --submission-id <uuid> \
    --submission-source-url <url> \
    --issue-number <number> \
    --comment-id <number> \
    --pr-number <number> \
    --pr-head-sha <sha>
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
