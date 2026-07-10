import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
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
const CAS_PATH = join(REPO_ROOT, 'scripts', 'lib', 'approval-cas.mjs');
const ARTIFACT_PATH = '.github/skill-publish-approvals.json';
const BRANCH = 'submission/concurrent-approvals';

function git(args, cwd) {
	return execFileSync('git', args, {
		cwd,
		encoding: 'utf8',
		stdio: ['ignore', 'pipe', 'pipe'],
	}).trim();
}

test('bounded CAS retry preserves three concurrent approval artifact updates', async () => {
	const root = mkdtempSync(join(tmpdir(), 'approval-cas-'));
	try {
		const remote = join(root, 'remote.git');
		const seed = join(root, 'seed');
		mkdirSync(seed);
		git(['init', '--bare', remote], root);
		git(['init'], seed);
		git(['config', 'user.name', 'Fixture'], seed);
		git(['config', 'user.email', 'fixture@example.com'], seed);
		mkdirSync(join(seed, '.github'));
		writeFileSync(
			join(seed, ARTIFACT_PATH),
			'{"schema_version":"2.0","approvals":[]}\n',
		);
		git(['add', '--', ARTIFACT_PATH], seed);
		git(['commit', '-m', 'seed approval artifact'], seed);
		git(['branch', '-M', BRANCH], seed);
		git(['remote', 'add', 'origin', remote], seed);
		git(['push', '-u', 'origin', BRANCH], seed);

		const { pushApprovalArtifactWithRetry } = await import(
			`${pathToFileURL(CAS_PATH).href}?test=${Date.now()}-${Math.random()}`
		);
		const attempts = new Map();
		const worktrees = new Set();
		let firstAttemptArrivals = 0;
		let releaseFirstAttempts;
		const firstAttemptsReady = new Promise((resolveReady) => {
			releaseFirstAttempts = resolveReady;
		});
		const readLiveState = async () => ({
			headSha: git(['--git-dir', remote, 'rev-parse', `refs/heads/${BRANCH}`], root),
			headRef: BRANCH,
		});

		await Promise.all(['first', 'second', 'third'].map((id) => (
			pushApprovalArtifactWithRetry({
				artifactPath: ARTIFACT_PATH,
				branch: BRANCH,
				maxAttempts: 5,
				remoteUrl: remote,
				tempRoot: root,
				readLiveState,
				commitMessage: `record ${id}`,
				updateArtifact: async ({ attempt, worktree }) => {
					attempts.set(id, attempt);
					assert.equal(worktrees.has(worktree), false, 'every retry must use a fresh worktree');
					worktrees.add(worktree);
					if (attempt === 1) {
						firstAttemptArrivals++;
						if (firstAttemptArrivals === 3) releaseFirstAttempts();
						await firstAttemptsReady;
					}
					const path = join(worktree, ARTIFACT_PATH);
					const document = JSON.parse(readFileSync(path, 'utf8'));
					document.approvals.push({ id });
					document.approvals.sort((left, right) => left.id.localeCompare(right.id));
					writeFileSync(path, `${JSON.stringify(document, null, 2)}\n`);
				},
			})
		)));

		const verify = join(root, 'verify');
		git(['clone', '--branch', BRANCH, remote, verify], root);
		const finalDocument = JSON.parse(readFileSync(join(verify, ARTIFACT_PATH), 'utf8'));
		assert.deepEqual(
			finalDocument.approvals.map((approval) => approval.id),
			['first', 'second', 'third'],
		);
		assert.ok(
			[...attempts.values()].some((attempt) => attempt > 1),
			'at least one writer must observe a non-fast-forward and retry',
		);
		assert.ok([...attempts.values()].every((attempt) => attempt <= 5));
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
