import { chmod, mkdtemp, mkdir, readFile, readdir, rm, stat, symlink, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
	stagePackSkillDownloads,
	stagePackTargetLinks,
	verifyInstalledPackMember,
} from '../src/lib/plugin-download.js';
import type { PluginConfig } from '../src/lib/plugin-config.js';
import type { ManifestSkill } from '../src/lib/plugin-api.js';

const mocks = vi.hoisted(() => ({ downloadSkillFile: vi.fn() }));

vi.mock('../src/lib/plugin-api.js', () => ({
	downloadSkillFile: mocks.downloadSkillFile,
	MAX_ARTIFACT_FILE_BYTES: 10 * 1024 * 1024,
}));

const roots: string[] = [];

afterEach(async () => {
	await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true })));
	vi.clearAllMocks();
});

async function fixture(): Promise<{ root: string; config: PluginConfig; members: ManifestSkill[] }> {
	const root = await mkdtemp(join(tmpdir(), 'skillstore-pack-members-'));
	roots.push(root);
	return {
		root,
		config: {
			apiBaseUrl: 'https://skillstore.test/api',
			installDir: join(root, 'skills'),
			timeout: 1000,
			maxConcurrent: 2,
			skipVerify: false,
			dryRun: false,
		},
		members: [
			{ slug: 'one', name: 'One', contentHash: '', downloadUrl: '/one' },
			{ slug: 'two', name: 'Two', contentHash: '', downloadUrl: '/two' },
		],
	};
}

describe('Pack member transaction', () => {
	it('keeps old members live until every member stages, then restores all replacements on rollback', async () => {
		const { config, members } = await fixture();
		for (const member of members) {
			const path = join(config.installDir, member.slug);
			await mkdir(path, { recursive: true });
			await writeFile(join(path, 'SKILL.md'), `old ${member.slug}`);
		}
		mocks.downloadSkillFile.mockImplementation(async (_config: PluginConfig, url: string) =>
			new TextEncoder().encode(url === '/one' ? 'new one' : 'new two')
		);

		const transaction = await stagePackSkillDownloads(config, members, { overwrite: true });

		expect(await readFile(join(config.installDir, 'one', 'SKILL.md'), 'utf8')).toBe('old one');
		expect(await readFile(join(config.installDir, 'two', 'SKILL.md'), 'utf8')).toBe('old two');
		await transaction.activate();
		expect(await readFile(join(config.installDir, 'one', 'SKILL.md'), 'utf8')).toBe('new one');
		expect(await readFile(join(config.installDir, 'two', 'SKILL.md'), 'utf8')).toBe('new two');

		await transaction.rollback();

		expect(await readFile(join(config.installDir, 'one', 'SKILL.md'), 'utf8')).toBe('old one');
		expect(await readFile(join(config.installDir, 'two', 'SKILL.md'), 'utf8')).toBe('old two');
		expect((await readdir(config.installDir)).some((entry) => entry.includes('.stage-') || entry.includes('.backup-'))).toBe(false);
	});

	it('does not replace any live member when staging another member fails', async () => {
		const { config, members } = await fixture();
		for (const member of members) {
			const path = join(config.installDir, member.slug);
			await mkdir(path, { recursive: true });
			await writeFile(join(path, 'SKILL.md'), `old ${member.slug}`);
		}
		mocks.downloadSkillFile
			.mockResolvedValueOnce(new TextEncoder().encode('new one'))
			.mockRejectedValueOnce(new Error('network failed'));

		const transaction = await stagePackSkillDownloads(config, members, { overwrite: true });

		expect(transaction.summary).toMatchObject({ success: 1, failed: 1 });
		expect(await readFile(join(config.installDir, 'one', 'SKILL.md'), 'utf8')).toBe('old one');
		expect(await readFile(join(config.installDir, 'two', 'SKILL.md'), 'utf8')).toBe('old two');
		await transaction.rollback();
	});

	it('fails closed for a tampered existing member without --overwrite', async () => {
		const { config, members } = await fixture();
		const signed = Buffer.from('signed member');
		const sha256 = createHash('sha256').update(signed).digest('hex');
		const member: ManifestSkill = {
			...members[0],
			contentHash: sha256,
			treeHash: createHash('sha256').update(JSON.stringify({
				path: 'SKILL.md', mode: '100644', sha256, size: signed.byteLength,
			})).digest('hex'),
			artifact: {
				files: [{ path: 'SKILL.md', url: '/one', sha256, bytes: signed.byteLength }],
			},
		};
		const path = join(config.installDir, member.slug);
		await mkdir(path, { recursive: true });
		await writeFile(join(path, 'SKILL.md'), 'tampered member');

		const transaction = await stagePackSkillDownloads(config, [member]);

		expect(transaction.summary).toMatchObject({ success: 0, failed: 1 });
		expect(transaction.summary.results[0].error).toContain('does not match signed artifact files');
		expect(mocks.downloadSkillFile).not.toHaveBeenCalled();
		expect(await readFile(join(path, 'SKILL.md'), 'utf8')).toBe('tampered member');
		await transaction.rollback();
	});

	it('reuses an existing member only when its signed tree matches exactly', async () => {
		const { config, members } = await fixture();
		const signed = Buffer.from('signed member');
		const sha256 = createHash('sha256').update(signed).digest('hex');
		const member: ManifestSkill = {
			...members[0],
			contentHash: sha256,
			treeHash: createHash('sha256').update(JSON.stringify({
				path: 'SKILL.md', mode: '100644', sha256, size: signed.byteLength,
			})).digest('hex'),
			artifact: {
				files: [{ path: 'SKILL.md', url: '/one', sha256, bytes: signed.byteLength }],
			},
		};
		const path = join(config.installDir, member.slug);
		await mkdir(path, { recursive: true });
		await writeFile(join(path, 'SKILL.md'), signed);

		const transaction = await stagePackSkillDownloads(config, [member]);

		expect(transaction.summary).toMatchObject({ success: 0, skipped: 1, failed: 0 });
		expect(mocks.downloadSkillFile).not.toHaveBeenCalled();
		await transaction.rollback();
	});

	it('derives and applies legacy executable modes only when they match the signed tree hash', async () => {
		const { config, members } = await fixture();
		const skillMd = new TextEncoder().encode('# Skill');
		const script = new TextEncoder().encode('#!/usr/bin/env python3\nprint("ok")\n');
		const files = [
			{ path: 'SKILL.md', url: '/skill', bytes: skillMd, mode: '100644' },
			{ path: 'scripts/run.py', url: '/script', bytes: script, mode: '100755' },
		] as const;
		const member: ManifestSkill = {
			...members[0],
			contentHash: createHash('sha256').update(skillMd).digest('hex'),
			treeHash: createHash('sha256').update([...files]
				.sort((left, right) => left.path.localeCompare(right.path, 'en', { sensitivity: 'variant' }))
				.map((file) => JSON.stringify({
					path: file.path,
					mode: file.mode,
					sha256: createHash('sha256').update(file.bytes).digest('hex'),
					size: file.bytes.byteLength,
				})).join('\n')).digest('hex'),
			artifact: {
				type: 'skill-files',
				files: files.map((file) => ({
					path: file.path,
					url: file.url,
					sha256: createHash('sha256').update(file.bytes).digest('hex'),
					bytes: file.bytes.byteLength,
				})),
			},
		};
		mocks.downloadSkillFile.mockImplementation(async (_config: PluginConfig, url: string) =>
			url === '/skill' ? skillMd : script
		);

		const transaction = await stagePackSkillDownloads(config, [member]);
		expect(transaction.summary).toMatchObject({ success: 1, failed: 0 });
		await transaction.activate();
		const scriptPath = join(config.installDir, member.slug, 'scripts/run.py');
		await expect(verifyInstalledPackMember(join(config.installDir, member.slug), member)).resolves.toBeUndefined();
		if (process.platform !== 'win32') {
			expect((await stat(join(config.installDir, member.slug, 'SKILL.md'))).mode & 0o777).toBe(0o644);
			expect((await stat(scriptPath)).mode & 0o777).toBe(0o755);
			await chmod(scriptPath, 0o644);
			await expect(verifyInstalledPackMember(join(config.installDir, member.slug), member))
				.rejects.toThrow('file modes do not match signed manifest');
		}
		await transaction.rollback();
	});

	it('refuses to replace a symlinked member path', async () => {
		const { root, config, members } = await fixture();
		await mkdir(config.installDir, { recursive: true });
		const outside = join(root, 'outside');
		await mkdir(outside);
		await symlink(outside, join(config.installDir, members[0].slug));
		mocks.downloadSkillFile.mockResolvedValue(new TextEncoder().encode('new one'));

		const transaction = await stagePackSkillDownloads(config, [members[0]], { overwrite: true });

		expect(transaction.summary.results[0].error).toContain('non-directory skill path');
		await transaction.rollback();
	});

	it('restores copied agent targets and removes newly linked targets on rollback', async () => {
		const { root, config, members } = await fixture();
		const firstTarget = join(root, 'agent-one');
		const secondTarget = join(root, 'agent-two');
		const oldCopy = join(firstTarget, members[0].slug);
		await mkdir(oldCopy, { recursive: true });
		await writeFile(join(oldCopy, 'SKILL.md'), 'old copy');

		const transaction = await stagePackTargetLinks([members[0].slug], [firstTarget, secondTarget], config.installDir);
		await transaction.activate();
		await mkdir(join(firstTarget, members[0].slug), { recursive: true });
		await writeFile(join(firstTarget, members[0].slug, 'SKILL.md'), 'new copy');
		await mkdir(join(secondTarget, members[0].slug), { recursive: true });
		await writeFile(join(secondTarget, members[0].slug, 'SKILL.md'), 'new target');

		await transaction.rollback();

		expect(await readFile(join(firstTarget, members[0].slug, 'SKILL.md'), 'utf8')).toBe('old copy');
		await expect(readFile(join(secondTarget, members[0].slug, 'SKILL.md'), 'utf8'))
			.rejects.toMatchObject({ code: 'ENOENT' });
	});
});
