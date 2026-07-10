import {
	mkdtempSync,
	mkdirSync,
	rmSync,
} from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, resolve } from 'node:path';

const DEFAULT_MAX_ATTEMPTS = 5;
const GIT_OUTPUT_BUFFER_BYTES = 16 * 1024 * 1024;

function runGit(args, {
	cwd,
	env,
	allowFailure = false,
} = {}) {
	const result = spawnSync('git', args, {
		cwd,
		env: { ...process.env, ...env },
		encoding: 'utf8',
		maxBuffer: GIT_OUTPUT_BUFFER_BYTES,
	});
	if (!allowFailure && result.status !== 0) {
		throw new Error(
			`git ${args[0]} failed: ${(result.stderr || result.stdout).trim()}`,
		);
	}
	return result;
}

function isNonFastForward(result) {
	const output = `${result.stdout}\n${result.stderr}`;
	return result.status !== 0 && /non-fast-forward|fetch first/i.test(output);
}

export class RetryableApprovalCasError extends Error {
	constructor(message) {
		super(message);
		this.name = 'RetryableApprovalCasError';
	}
}

export async function pushApprovalArtifactWithRetry(options) {
	const artifactPath = options.artifactPath;
	const maxAttempts = options.maxAttempts ?? DEFAULT_MAX_ATTEMPTS;
	const remoteUrl = options.remoteUrl;
	const tempRoot = resolve(options.tempRoot);
	if (typeof artifactPath !== 'string' || artifactPath === '') {
		throw new Error('artifactPath is required');
	}
	if (!Number.isSafeInteger(maxAttempts) || maxAttempts < 1 || maxAttempts > 20) {
		throw new Error('maxAttempts must be an integer between 1 and 20');
	}
	if (typeof remoteUrl !== 'string' || remoteUrl === '') {
		throw new Error('remoteUrl is required');
	}
	if (typeof options.readLiveState !== 'function') {
		throw new Error('readLiveState must be a function');
	}
	if (typeof options.updateArtifact !== 'function') {
		throw new Error('updateArtifact must be a function');
	}
	mkdirSync(tempRoot, { recursive: true });

	let lastRetryableError;
	for (let attempt = 1; attempt <= maxAttempts; attempt++) {
		const liveState = await options.readLiveState({ attempt });
		if (!/^[a-f0-9]{40}$/.test(liveState?.headSha ?? '')) {
			throw new Error('live PR head SHA is missing or invalid');
		}
		const headRef = liveState?.headRef;
		if (typeof headRef !== 'string' || headRef === '') {
			throw new Error('live PR head ref is missing');
		}
		if (options.branch && options.branch !== headRef) {
			throw new Error('live PR head ref changed');
		}

		const worktree = mkdtempSync(join(tempRoot, 'approval-cas-'));
		try {
			runGit(['init', '--quiet'], { cwd: worktree });
			runGit(['remote', 'add', 'origin', remoteUrl], { cwd: worktree });
			runGit(
				[
					'-c',
					'credential.helper=',
					'-c',
					'core.askPass=',
					'-c',
					'http.extraHeader=',
					'-c',
					'http.https://github.com/.extraheader=',
					'fetch',
					'--quiet',
					'--no-tags',
					'--depth=1',
					'origin',
					liveState.headSha,
				],
				{
					cwd: worktree,
					env: {
						GIT_ASKPASS: 'false',
						GIT_TERMINAL_PROMPT: '0',
					},
				},
			);
			runGit(['checkout', '--quiet', '--detach', 'FETCH_HEAD'], { cwd: worktree });
			const checkedOutHead = runGit(['rev-parse', 'HEAD'], { cwd: worktree }).stdout.trim();
			if (checkedOutHead !== liveState.headSha) {
				throw new Error('fetched data worktree does not match the exact live PR head');
			}

			try {
				await options.updateArtifact({
					attempt,
					liveState,
					worktree,
				});
			} catch (error) {
				if (error instanceof RetryableApprovalCasError) {
					lastRetryableError = error;
					continue;
				}
				throw error;
			}

			const status = runGit(
				['status', '--short', '--untracked-files=all'],
				{ cwd: worktree },
			).stdout.trimEnd();
			if (status === '') {
				return {
					attempt,
					headSha: liveState.headSha,
					unchanged: true,
				};
			}
			if (status !== `M  ${artifactPath}` && status !== ` M ${artifactPath}`) {
				throw new Error(`approval update changed an unexpected path: ${status}`);
			}

			runGit(['add', '--', artifactPath], { cwd: worktree });
			const staged = runGit(
				['diff', '--cached', '--name-status'],
				{ cwd: worktree },
			).stdout.trim();
			if (staged !== `M\t${artifactPath}`) {
				throw new Error(`approval commit must modify only ${artifactPath}: ${staged}`);
			}

			runGit(['config', 'user.name', options.gitUserName ?? 'ai-skill-store[bot]'], {
				cwd: worktree,
			});
			runGit([
				'config',
				'user.email',
				options.gitUserEmail
					?? '2628292+ai-skill-store[bot]@users.noreply.github.com',
			], { cwd: worktree });
			runGit(
				[
					'-c',
					'commit.gpgsign=false',
					'commit',
					'--quiet',
					'-m',
					options.commitMessage ?? 'Track publication approval',
				],
				{ cwd: worktree },
			);

			const pushResult = runGit(
				[
					'push',
					options.pushRemoteUrl ?? remoteUrl,
					`HEAD:refs/heads/${headRef}`,
				],
				{
					cwd: worktree,
					env: options.pushEnv,
					allowFailure: true,
				},
			);
			if (pushResult.status === 0) {
				return {
					attempt,
					headSha: runGit(['rev-parse', 'HEAD'], { cwd: worktree }).stdout.trim(),
					unchanged: false,
				};
			}
			if (!isNonFastForward(pushResult)) {
				throw new Error(`git push failed: ${(pushResult.stderr || pushResult.stdout).trim()}`);
			}
			lastRetryableError = new RetryableApprovalCasError(
				'approval branch advanced before push',
			);
		} finally {
			rmSync(worktree, { recursive: true, force: true });
		}
	}

	throw new Error(
		`approval CAS retry exhausted after ${maxAttempts} attempts: `
			+ `${lastRetryableError?.message ?? 'branch kept advancing'}`,
	);
}
