import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import {
	existsSync,
	lstatSync,
	mkdirSync,
	mkdtempSync,
	readFileSync,
	rmSync,
	symlinkSync,
	writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, '..', '..');
const CLEANUP_PATH = join(REPO_ROOT, 'scripts', 'remove-empty-skill-files.mjs');

async function loadCleanup() {
	return import(`${pathToFileURL(CLEANUP_PATH).href}?test=${Date.now()}-${Math.random()}`);
}

function makeTempRoot() {
	return mkdtempSync(join(tmpdir(), 'empty-skill-cleanup-'));
}

test('deletes only a regular zero-byte SKILL.md and preserves tracked siblings', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'owner', 'nonempty package');
		mkdirSync(join(packageDir, 'nested'), { recursive: true });
		writeFileSync(join(packageDir, 'SKILL.md'), '');
		writeFileSync(join(packageDir, 'keep.txt'), 'tracked sibling\n');
		writeFileSync(join(packageDir, 'nested', 'keep.md'), '# Nested sibling\n');

		for (const args of [
			['init', '-q'],
			['config', 'user.email', 'fixture@example.com'],
			['config', 'user.name', 'Fixture'],
			['add', '.'],
			['commit', '-qm', 'base'],
		]) {
			const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' });
			assert.equal(result.status, 0, result.stderr);
		}

		const { removeEmptySkillFiles } = await loadCleanup();
		const result = removeEmptySkillFiles({
			roots: [join(root, 'skills'), join(root, 'pending')],
			workspaceRoot: root,
		});

		assert.equal(result.deletedFiles, 1);
		assert.equal(existsSync(packageDir), true);
		assert.equal(existsSync(join(packageDir, 'SKILL.md')), false);
		assert.equal(readFileSync(join(packageDir, 'keep.txt'), 'utf8'), 'tracked sibling\n');
		assert.equal(readFileSync(join(packageDir, 'nested', 'keep.md'), 'utf8'), '# Nested sibling\n');
		assert.match(
			spawnSync('git', ['status', '--short'], { cwd: root, encoding: 'utf8' }).stdout,
			/^ D "skills\/owner\/nonempty package\/SKILL\.md"$/m,
		);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('keeps whitespace-only SKILL.md for the normal fixer', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'owner', 'whitespace');
		mkdirSync(packageDir, { recursive: true });
		writeFileSync(join(packageDir, 'SKILL.md'), ' \n\t\n');

		const { removeEmptySkillFiles } = await loadCleanup();
		const result = removeEmptySkillFiles({
			roots: [join(root, 'skills')],
			workspaceRoot: root,
		});

		assert.equal(result.deletedFiles, 0);
		assert.equal(readFileSync(join(packageDir, 'SKILL.md'), 'utf8'), ' \n\t\n');
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('does not follow or delete a symlink named SKILL.md', async (t) => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'owner', 'symlinked');
		const target = join(root, 'target.md');
		mkdirSync(packageDir, { recursive: true });
		writeFileSync(target, '');
		try {
			symlinkSync(target, join(packageDir, 'SKILL.md'));
		} catch (error) {
			if (['EACCES', 'ENOSYS', 'ENOTSUP', 'EOPNOTSUPP', 'EPERM'].includes(error?.code)) {
				t.skip(`platform cannot create symlinks: ${error.code}`);
				return;
			}
			throw error;
		}

		const { removeEmptySkillFiles } = await loadCleanup();
		const result = removeEmptySkillFiles({
			roots: [join(root, 'skills')],
			workspaceRoot: root,
		});

		assert.equal(result.deletedFiles, 0);
		assert.equal(lstatSync(join(packageDir, 'SKILL.md')).isSymbolicLink(), true);
		assert.equal(existsSync(target), true);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('handles spaces and nested directories without recursively deleting parents', async () => {
	const root = makeTempRoot();
	try {
		const packageDir = join(root, 'skills', 'owner with spaces', 'nested', 'empty skill');
		mkdirSync(packageDir, { recursive: true });
		writeFileSync(join(packageDir, 'SKILL.md'), '');
		writeFileSync(join(root, 'skills', 'owner with spaces', 'keep.txt'), 'keep\n');

		const { removeEmptySkillFiles } = await loadCleanup();
		const result = removeEmptySkillFiles({
			roots: [join(root, 'skills')],
			workspaceRoot: root,
		});

		assert.equal(result.deletedFiles, 1);
		assert.equal(existsSync(packageDir), false);
		assert.equal(
			readFileSync(join(root, 'skills', 'owner with spaces', 'keep.txt'), 'utf8'),
			'keep\n',
		);
		assert.equal(existsSync(join(root, 'skills', 'owner with spaces', 'nested')), true);
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});

test('rejects roots that escape the workspace boundary', async () => {
	const root = makeTempRoot();
	const outside = makeTempRoot();
	try {
		const outsidePackage = join(outside, 'skills', 'owner', 'outside');
		mkdirSync(outsidePackage, { recursive: true });
		writeFileSync(join(outsidePackage, 'SKILL.md'), '');

		const { removeEmptySkillFiles } = await loadCleanup();
		assert.throws(
			() => removeEmptySkillFiles({
				roots: [outsidePackage],
				workspaceRoot: root,
			}),
			/outside workspace|escapes workspace/i,
		);
		assert.equal(existsSync(join(outsidePackage, 'SKILL.md')), true);
	} finally {
		rmSync(root, { recursive: true, force: true });
		rmSync(outside, { recursive: true, force: true });
	}
});

test('CLI treats option-like and parent-traversal roots as invalid input', () => {
	const root = makeTempRoot();
	try {
		for (const hostileRoot of ['--root', '../outside']) {
			const result = spawnSync(
				process.execPath,
				[CLEANUP_PATH, '--workspace', root, '--root', hostileRoot],
				{ cwd: root, encoding: 'utf8' },
			);
			assert.notEqual(result.status, 0, hostileRoot);
			assert.match(result.stderr, /root|workspace|path|argument/i);
		}
	} finally {
		rmSync(root, { recursive: true, force: true });
	}
});
