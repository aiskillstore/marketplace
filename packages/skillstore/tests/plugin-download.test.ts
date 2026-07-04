import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createHash } from 'node:crypto';
import { mkdir, rm, writeFile, access } from 'node:fs/promises';
import {
	downloadAllSkills,
	printDownloadSummary,
	type SkillDownloadResult,
	type DownloadSummary,
} from '../src/lib/plugin-download.js';
import { getPluginConfig, type PluginConfig } from '../src/lib/plugin-config.js';
import type { ManifestSkill } from '../src/lib/plugin-api.js';

// Mock fs/promises
vi.mock('node:fs/promises', () => ({
	mkdir: vi.fn(),
	rm: vi.fn(),
	writeFile: vi.fn(),
	access: vi.fn(),
}));

// Mock plugin-api
vi.mock('../src/lib/plugin-api.js', () => ({
	downloadSkillFile: vi.fn(),
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
const mockAccess = vi.mocked(access);

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
		mockAccess.mockRejectedValue(new Error('ENOENT')); // File doesn't exist
	});

	describe('downloadAllSkills', () => {
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

			expect(mockMkdir).toHaveBeenCalledTimes(3);
			expect(mockWriteFile).toHaveBeenCalledTimes(3);
		});

		it('should skip existing files when overwrite is false', async () => {
			mockAccess.mockResolvedValue(undefined); // File exists

			const summary = await downloadAllSkills(config, testSkills, { overwrite: false });

			expect(summary.skipped).toBe(3);
			expect(summary.success).toBe(0);
			expect(mockDownloadSkillFile).not.toHaveBeenCalled();
		});

		it('should overwrite existing files when overwrite is true', async () => {
			mockAccess.mockResolvedValue(undefined); // File exists

			const summary = await downloadAllSkills(config, testSkills, { overwrite: true });

			expect(summary.success).toBe(3);
			expect(summary.skipped).toBe(0);
			expect(mockDownloadSkillFile).toHaveBeenCalledTimes(3);
			expect(mockRm).toHaveBeenCalledWith('/test/skills/skill-1', { recursive: true, force: true });
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

			expect(summary.success).toBe(2);
			expect(summary.failed).toBe(1);
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
			const artifactSkill: ManifestSkill = {
				slug: 'artifact-skill',
				name: 'Artifact Skill',
				contentHash: '',
				downloadUrl: '/fallback',
				artifact: {
					type: 'skill-files',
					files: [
						{
							path: 'SKILL.md',
							url: '/files/SKILL.md',
							sha256: createHash('sha256').update(skillMd).digest('hex'),
						},
						{
							path: 'references/guide.md',
							url: '/files/references/guide.md',
							sha256: createHash('sha256').update(reference).digest('hex'),
						},
					],
				},
			};
			mockDownloadSkillFile
				.mockResolvedValueOnce(skillMd)
				.mockResolvedValueOnce(reference);

			const summary = await downloadAllSkills(config, [artifactSkill]);

			expect(summary.success).toBe(1);
			expect(mockWriteFile).toHaveBeenCalledWith('/test/skills/artifact-skill/SKILL.md', skillMd);
			expect(mockWriteFile).toHaveBeenCalledWith('/test/skills/artifact-skill/references/guide.md', reference);
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
						{ path: 'SKILL.md', url: '/files/SKILL.md' },
						{ path: '../outside.md', url: '/files/outside.md' },
					],
				},
			};

			const summary = await downloadAllSkills(config, [unsafeSkill]);

			expect(summary.failed).toBe(1);
			expect(summary.results[0].error).toContain('Invalid artifact path');
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
