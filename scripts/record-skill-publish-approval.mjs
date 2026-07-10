#!/usr/bin/env node

import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import {
	RetryableApprovalCasError,
	pushApprovalArtifactWithRetry,
} from './lib/approval-cas.mjs';
import { createGitHubRequest } from './lib/publication-approval.mjs';
import { discoverPackageDirs } from './validate-skill-publication.mjs';
import { upsertTrackedApprovals } from './update-skill-publish-approval.mjs';

const SHA_PATTERN = /^[a-f0-9]{40}$/;

function normalizedRepository(value) {
	return typeof value === 'string' ? value.trim().toLowerCase() : '';
}

function parseArguments(argv) {
	const options = {
		maxAttempts: 5,
	};
	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		const value = argv[index + 1];
		if (arg === '--repository') options.repository = value, index++;
		else if (arg === '--pr-number') options.prNumber = Number(value), index++;
		else if (arg === '--comment-id') options.commentId = Number(value), index++;
		else if (arg === '--max-attempts') options.maxAttempts = Number(value), index++;
		else if (arg === '--temp-root') options.tempRoot = value, index++;
		else if (arg === '--help' || arg === '-h') options.help = true;
		else throw new Error(`Unknown argument: ${arg}`);
	}
	return options;
}

function validateOptions(options) {
	if (!/^[^/]+\/[^/]+$/.test(options.repository ?? '')) {
		throw new Error('--repository must be owner/repo');
	}
	for (const field of ['prNumber', 'commentId']) {
		if (!Number.isSafeInteger(options[field]) || options[field] < 1) {
			throw new Error(`--${field === 'prNumber' ? 'pr-number' : 'comment-id'} must be positive`);
		}
	}
	if (!Number.isSafeInteger(options.maxAttempts) || options.maxAttempts < 1) {
		throw new Error('--max-attempts must be positive');
	}
}

function printHelp() {
	console.log(`Usage:
  node scripts/record-skill-publish-approval.mjs \
    --repository <owner/repo> \
    --pr-number <number> \
    --comment-id <number> \
    --max-attempts 5
`);
}

async function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}
	validateOptions(options);
	const token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN || '';
	const appToken = process.env.APP_TOKEN || token;
	if (token === '' || appToken === '') {
		throw new Error('GH_TOKEN and APP_TOKEN are required');
	}
	const githubRequest = createGitHubRequest({
		token,
		fetchImpl: globalThis.fetch,
	});
	const readLiveState = async () => {
		const pullRequest = await githubRequest(
			`/repos/${options.repository}/pulls/${options.prNumber}`,
		);
		if (
			pullRequest?.number !== options.prNumber
			|| pullRequest?.state !== 'open'
			|| pullRequest?.merged === true
			|| pullRequest?.merged_at
		) {
			throw new Error('publication approval requires the current open PR');
		}
		if (
			normalizedRepository(pullRequest?.base?.repo?.full_name)
				!== normalizedRepository(options.repository)
			|| normalizedRepository(pullRequest?.head?.repo?.full_name)
				!== normalizedRepository(options.repository)
		) {
			throw new Error('PR base and head repositories must equal the publication repository');
		}
		if (pullRequest?.base?.ref !== 'main') {
			throw new Error('publication approval requires base branch main');
		}
		if (
			!SHA_PATTERN.test(pullRequest?.head?.sha ?? '')
			|| !SHA_PATTERN.test(pullRequest?.base?.sha ?? '')
			|| typeof pullRequest?.head?.ref !== 'string'
			|| pullRequest.head.ref === ''
		) {
			throw new Error('PR metadata contains an invalid ref or SHA');
		}
		return {
			headSha: pullRequest.head.sha,
			headRef: pullRequest.head.ref,
			baseSha: pullRequest.base.sha,
			baseRef: pullRequest.base.ref,
		};
	};
	const authorization = Buffer.from(`x-access-token:${appToken}`).toString('base64');
	const result = await pushApprovalArtifactWithRetry({
		artifactPath: '.github/skill-publish-approvals.json',
		commitMessage: `Track publication approval from PR #${options.prNumber}`,
		maxAttempts: options.maxAttempts,
		remoteUrl: `https://github.com/${options.repository}.git`,
		tempRoot: resolve(options.tempRoot ?? process.env.RUNNER_TEMP ?? '/tmp'),
		readLiveState,
		pushEnv: {
			GIT_CONFIG_COUNT: '1',
			GIT_CONFIG_KEY_0: 'http.https://github.com/.extraheader',
			GIT_CONFIG_VALUE_0: `AUTHORIZATION: basic ${authorization}`,
		},
		updateArtifact: async ({ liveState, worktree }) => {
			try {
				const packageDirs = await discoverPackageDirs(resolve(worktree, 'pending'));
				await upsertTrackedApprovals({
					approvalsPath: resolve(
						worktree,
						'.github',
						'skill-publish-approvals.json',
					),
					packageDirs,
					issueNumber: options.prNumber,
					commentId: options.commentId,
					prNumber: options.prNumber,
					prHeadSha: liveState.headSha,
					expectedPrBaseSha: liveState.baseSha,
					expectedPrBaseRef: liveState.baseRef,
					expectedPrHeadRef: liveState.headRef,
					githubRepository: options.repository,
					githubRequest,
				});
			} catch (error) {
				if (/checked-out head SHA does not match the current PR head SHA/i.test(error.message)) {
					throw new RetryableApprovalCasError(error.message);
				}
				throw error;
			}
		},
	});
	console.log(
		result.unchanged
			? `UNCHANGED PR #${options.prNumber}`
			: `UPDATED PR #${options.prNumber} after ${result.attempt} attempt(s)`,
	);
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
