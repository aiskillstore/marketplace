import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createHash } from 'node:crypto';
import { mkdir, rm, writeFile, lstat, rename } from 'node:fs/promises';
import {
	downloadAllSkills,
	printDownloadSummary,
	MAX_PACK_SKILLS,
	type SkillDownloadResult,
	type DownloadSummary,
} from '../src/lib/plugin-download.js';
import { getPluginConfig, type PluginConfig } from '../src/lib/plugin-config.js';
import type { ManifestSkill } from '../src/lib/plugin-api.js';

// Mock fs/promises
vi.mock('node:fs/promises', () => ({
	chmod: vi.fn(),
	mkdir: vi.fn(),
	rm: vi.fn(),
	writeFile: vi.fn(),
	lstat: vi.fn(),
	rename: vi.fn(),
}));

// Mock plugin-api
vi.mock('../src/lib/plugin-api.js', () => ({
	downloadSkillFile: vi.fn(),
	MAX_ARTIFACT_FILE_BYTES: 10 * 1024 * 1024,
}));

// Mock plugin-verify
vi.mock('../src/lib/plugin-verify.js', () => ({
	verifyContentHash: vi.fn(),
}));

// Mock plugin-logger
vi.mock('../src/lib/plugin-logger.js', () => ({
	logger: {
		startProgress: vi.fn(),
		incrementProgress: vi.fn(),
		completeProgress: vi.fn(),
		skillSummary: vi.fn(),
	},
}));

import { downloadSkillFile } from '../src/lib/plugin-api.js';
import { verifyContentHash } from '../src/lib/plugin-verify.js';
import { logger } from '../src/lib/plugin-logger.js';

const mockDownloadSkillFile = vi.mocked(downloadSkillFile);
const mockVerifyContentHash = vi.mocked(verifyContentHash);
const mockMkdir = vi.mocked(mkdir);
const mockRm = vi.mocked(rm);
const mockWriteFile = vi.mocked(writeFile);
const mockLstat = vi.mocked(lstat);
const mockRename = vi.mocked(rename);

function artifactTreeHash(files: Array<{ path: string; mode: '100644' | '100755'; bytes: Uint8Array }>): string {
	return createHash('sha256').update([...files]
		.sort((left, right) => left.path.localeCompare(right.path, 'en', { sensitivity: 'variant' }))
		.map((file) => JSON.stringify({
			path: file.path,
			mode: file.mode,
			sha256: createHash('sha256').update(file.bytes).digest('hex'),
			size: file.bytes.byteLength,
		}))
		.join('\n')).digest('hex');
}

describe('plugin-download', () => {
	let config: PluginConfig;

	const testSkills: ManifestSkill[] = [
		{ slug: 'skill-1', name: 'Skill 1', contentHash: 'hash1', downloadUrl: '/dl/1' },
		{ slug: 'skill-2', name: 'Skill 2', contentHash: 'hash2', downloadUrl: '/dl/2' },
		{ slug: 'skill-3', name: 'Skill 3', contentHash: 'hash3', downloadUrl: '/dl/3' },
	];

	beforeEach(() => {
		config = getPluginConfig({
			apiBaseUrl: 'https://api.test.com',
			installDir: '/test/skills',
			maxConcurrent: 2,
		});

		vi.clearAllMocks();

		// Default mocks
		mockDownloadSkillFile.mockResolvedValue(new TextEncoder().encode('# Skill content'));
		mockVerifyContentHash.mockReturnValue(true);
		mockMkdir.mockResolvedValue(undefined);
		mockRm.mockResolvedValue(undefined);
		mockWriteFile.mockResolvedValue(undefined);
		mockLstat.mockRejectedValue(Object.assign(new Error('ENOENT'), { code: 'ENOENT' }));
		mockRename.mockResolvedValue(undefined);
	});

	describe('downloadAllSkills', () => {
		it('rejects an oversized Pack before any download begins', async () => {
			const tooMany = Array.from({ length: MAX_PACK_SKILLS + 1 }, (_, index) => ({
				slug: `skill-${index}`,
				name: `Skill ${index}`,
				contentHash: '',
				downloadUrl: `/dl/${index}`,
			}));
			await expect(downloadAllSkills(config, tooMany)).rejects.toThrow('too many Skills');
			expect(mockDownloadSkillFile).not.toHaveBeenCalled();
		});
		it('should download all skills successfully', async () => {
			const summary = await downloadAllSkills(config, testSkills);

			expect(summary.total).toBe(3);
			expect(summary.success).toBe(3);
			expect(summary.failed).toBe(0);
			expect(summary.skipped).toBe(0);
		});

		it('should call progress tracking methods', async () => {
			await downloadAllSkills(config, testSkills);

			expect(logger.startProgress).toHaveBeenCalledWith(3, 'Downloading skills');
			expect(logger.incrementProgress).toHaveBeenCalledTimes(3);
			expect(logger.completeProgress).toHaveBeenCalled();
		});

		it('should create directories and write files', async () => {
			await downloadAllSkills(config, testSkills);

			expect(mockMkdir).toHaveBeenCalled();
			expect(mockWriteFile).toHaveBeenCalledTimes(3);
		});

		it('should overwrite existing files when overwrite is true', async () => {
			mockLstat.mockResolvedValue({
				isSymbolicLink: () => false,
				isDirectory: () => true,
			} as never);

			const summary = await downloadAllSkills(config, testSkills, { overwrite: true });

			expect(summary.success).toBe(3);
			expect(summary.skipped).toBe(0);
			expect(mockDownloadSkillFile).toHaveBeenCalledTimes(3);
			expect(mockRename).toHaveBeenCalledWith('/test/skills/skill-1', expect.stringMatching(/\.backup-/));
		});

		it('should verify content hash when enabled', async () => {
			await downloadAllSkills(config, testSkills, { verifyHash: true });

			expect(mockVerifyContentHash).toHaveBeenCalledTimes(3);
		});

		it('should fail when hash verification fails', async () => {
			mockVerifyContentHash.mockReturnValue(false);

			const summary = await downloadAllSkills(config, testSkills, { verifyHash: true });

			expect(summary.failed).toBe(3);
			expect(summary.results[0].error).toBe('Content hash verification failed for SKILL.md');
		});

		it('should skip hash verification when disabled', async () => {
			await downloadAllSkills(config, testSkills, { verifyHash: false });

			expect(mockVerifyContentHash).not.toHaveBeenCalled();
		});

		it('should handle download errors gracefully', async () => {
			mockDownloadSkillFile.mockRejectedValue(new Error('Network error'));

			const summary = await downloadAllSkills(config, testSkills);

			expect(summary.failed).toBe(3);
			expect(summary.results[0].error).toBe('Network error');
		});

		it('should handle partial failures', async () => {
			mockDownloadSkillFile
				.mockResolvedValueOnce(new TextEncoder().encode('# Content 1'))
				.mockRejectedValueOnce(new Error('Failed'))
				.mockResolvedValueOnce(new TextEncoder().encode('# Content 3'));

			const summary = await downloadAllSkills(config, testSkills);

			expect(summary.success).toBe(0);
			expect(summary.failed).toBe(3);
			expect(summary.results.filter((result) => result.error === 'Pack download aborted because another member failed')).toHaveLength(2);
		});

		it('should respect maxConcurrent setting', async () => {
			// With maxConcurrent=2, should process in batches
			const downloadCalls: number[] = [];
			mockDownloadSkillFile.mockImplementation(async () => {
				downloadCalls.push(Date.now());
				await new Promise((resolve) => setTimeout(resolve, 10));
				return new TextEncoder().encode('# Content');
			});

			await downloadAllSkills(config, testSkills);

			// All 3 skills should be downloaded
			expect(mockDownloadSkillFile).toHaveBeenCalledTimes(3);
		});

		it('should not download in dry run mode', async () => {
			const dryRunConfig = getPluginConfig({
				...config,
				dryRun: true,
			});

			const summary = await downloadAllSkills(dryRunConfig, testSkills);

			expect(summary.skipped).toBe(3);
			expect(mockDownloadSkillFile).not.toHaveBeenCalled();
			expect(mockWriteFile).not.toHaveBeenCalled();
		});

		it('should handle empty skills array', async () => {
			const summary = await downloadAllSkills(config, []);

			expect(summary.total).toBe(0);
			expect(summary.success).toBe(0);
			expect(logger.startProgress).toHaveBeenCalledWith(0, 'Downloading skills');
		});

		it('should return proper result structure', async () => {
			const summary = await downloadAllSkills(config, [testSkills[0]]);

			expect(summary.results).toHaveLength(1);
			expect(summary.results[0]).toMatchObject({
				slug: 'skill-1',
				success: true,
				path: '/test/skills/skill-1',
			});
		});

		it('should install all artifact files under the skill directory', async () => {
			const skillMd = new TextEncoder().encode('# Skill');
			const reference = new TextEncoder().encode('Reference');
			const treeFiles = [
				{ path: 'SKILL.md', mode: '100644' as const, bytes: skillMd },
				{ path: 'references/guide.md', mode: '100644' as const, bytes: reference },
			];
			const artifactSkill: ManifestSkill = {
				slug: 'artifact-skill',
				name: 'Artifact Skill',
				contentHash: createHash('sha256').update(skillMd).digest('hex'),
				treeHash: artifactTreeHash(treeFiles),
				downloadUrl: '/fallback',
				artifact: {
					type: 'skill-files',
					files: [
						{
							path: 'SKILL.md',
							url: '/files/SKILL.md',
							sha256: createHash('sha256').update(skillMd).digest('hex'),
							bytes: skillMd.byteLength,
							mode: '100644',
						},
						{
							path: 'references/guide.md',
							url: '/files/references/guide.md',
							sha256: createHash('sha256').update(reference).digest('hex'),
							bytes: reference.byteLength,
							mode: '100644',
						},
					],
				},
			};
			mockDownloadSkillFile
				.mockResolvedValueOnce(skillMd)
				.mockResolvedValueOnce(reference);

			const summary = await downloadAllSkills(config, [artifactSkill]);

			expect(summary.success).toBe(1);
			expect(mockWriteFile).toHaveBeenCalledWith(expect.stringMatching(/\.artifact-skill\.stage-.*\/SKILL\.md$/), skillMd);
			expect(mockWriteFile).toHaveBeenCalledWith(expect.stringMatching(/\.artifact-skill\.stage-.*\/references\/guide\.md$/), reference);
		});

		it('should reject an artifact file without an exact SHA-256 before download', async () => {
			const unhashedSkill: ManifestSkill = {
				slug: 'unhashed-artifact',
				name: 'Unhashed Artifact',
				contentHash: '',
				downloadUrl: '/fallback',
				artifact: {
					type: 'skill-files',
					files: [{ path: 'SKILL.md', url: '/files/SKILL.md', sha256: 'deadbeef' }],
				},
			};

			await expect(downloadAllSkills(config, [unhashedSkill])).rejects.toThrow('Missing exact SHA-256');
			expect(mockDownloadSkillFile).not.toHaveBeenCalled();
			expect(mockWriteFile).not.toHaveBeenCalled();
		});

		it('downloads raw GitHub files only when URL and signed provenance match exactly', async () => {
			const commit = 'a'.repeat(40);
			const bytes = new TextEncoder().encode('# verified');
			const sha256 = createHash('sha256').update(bytes).digest('hex');
			const url = `https://raw.githubusercontent.com/aiskillstore/marketplace/${commit}/skills/example/SKILL.md`;
			const skill: ManifestSkill = {
				slug: 'example',
				name: 'Example',
				contentHash: sha256,
				treeHash: artifactTreeHash([{ path: 'SKILL.md', mode: '100644', bytes }]),
				downloadUrl: url,
				artifact: {
					type: 'skill-files',
					source: {
						type: 'github',
						owner: 'aiskillstore',
						repo: 'marketplace',
						ref: commit,
						commit,
						path: 'skills/example',
					},
					files: [{ path: 'SKILL.md', url, sha256, bytes: bytes.byteLength, mode: '100644' }],
				},
			};
			mockDownloadSkillFile.mockResolvedValue(bytes);

			await expect(downloadAllSkills(config, [skill])).resolves.toMatchObject({ success: 1, failed: 0 });
			expect(mockDownloadSkillFile).toHaveBeenCalledWith(config, url, expect.objectContaining({
				approvedExternalUrl: url,
				expectedBytes: bytes.byteLength,
			}));

			const mismatched = structuredClone(skill);
			mismatched.artifact!.source!.commit = 'b'.repeat(40);
			mismatched.artifact!.source!.ref = 'b'.repeat(40);
			await expect(downloadAllSkills(config, [mismatched]))
				.rejects.toThrow('does not match signed GitHub provenance');

			const outsideMirror = structuredClone(skill);
			outsideMirror.artifact!.source!.owner = 'someone-else';
			await expect(downloadAllSkills(config, [outsideMirror]))
				.rejects.toThrow('outside the approved Marketplace mirror');
		});

		it('should reject artifact paths outside the skill directory before writing files', async () => {
			const unsafeSkill: ManifestSkill = {
				slug: 'unsafe-skill',
				name: 'Unsafe Skill',
				contentHash: '',
				downloadUrl: '/fallback',
				artifact: {
					type: 'skill-files',
					files: [
						{ path: 'SKILL.md', url: '/files/SKILL.md', sha256: 'a'.repeat(64), bytes: 1 },
						{ path: '../outside.md', url: '/files/outside.md', sha256: 'b'.repeat(64), bytes: 1 },
					],
				},
			};

			await expect(downloadAllSkills(config, [unsafeSkill])).rejects.toThrow('Invalid artifact path');
			expect(mockDownloadSkillFile).not.toHaveBeenCalled();
			expect(mockWriteFile).not.toHaveBeenCalled();
		});

		it('should handle skills without contentHash', async () => {
			const skillWithoutHash: ManifestSkill = {
				slug: 'no-hash',
				name: 'No Hash',
				contentHash: '',
				downloadUrl: '/dl/no-hash',
			};

			const summary = await downloadAllSkills(config, [skillWithoutHash], { verifyHash: true });

			// Should not verify hash if contentHash is empty
			expect(summary.success).toBe(1);
		});
	});

	describe('printDownloadSummary', () => {
		it('should print summary for successful downloads', () => {
			const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

			const summary: DownloadSummary = {
				total: 3,
				success: 2,
				failed: 1,
				skipped: 0,
				results: [
					{ slug: 'skill-1', success: true, path: '/path/1' },
					{ slug: 'skill-2', success: true, path: '/path/2' },
					{ slug: 'skill-3', success: false, error: 'Download failed' },
				],
			};

			printDownloadSummary(summary);

			expect(logger.skillSummary).toHaveBeenCalledWith('skill-1', 'installed');
			expect(logger.skillSummary).toHaveBeenCalledWith('skill-2', 'installed');
			expect(logger.skillSummary).toHaveBeenCalledWith('skill-3', 'failed');

			consoleSpy.mockRestore();
		});

		it('should print summary for skipped downloads', () => {
			const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

			const summary: DownloadSummary = {
				total: 2,
				success: 0,
				failed: 0,
				skipped: 2,
				results: [
					{ slug: 'skill-1', success: true, skipped: true },
					{ slug: 'skill-2', success: true, skipped: true },
				],
			};

			printDownloadSummary(summary);

			expect(logger.skillSummary).toHaveBeenCalledWith('skill-1', 'skipped');
			expect(logger.skillSummary).toHaveBeenCalledWith('skill-2', 'skipped');

			consoleSpy.mockRestore();
		});

		it('should print error messages for failed downloads', () => {
			const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

			const summary: DownloadSummary = {
				total: 1,
				success: 0,
				failed: 1,
				skipped: 0,
				results: [{ slug: 'skill-1', success: false, error: 'Network timeout' }],
			};

			printDownloadSummary(summary);

			expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Network timeout'));

			consoleSpy.mockRestore();
		});
	});
});
