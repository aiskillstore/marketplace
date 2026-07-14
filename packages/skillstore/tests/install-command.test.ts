import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	access: vi.fn(),
	fetchSkillManifest: vi.fn(),
	downloadSkillZip: vi.fn(),
	verifySkillManifest: vi.fn(),
	verifyZipHash: vi.fn(),
	extractSkillZip: vi.fn(),
	linkSkillToDirectory: vi.fn(),
	addToLock: vi.fn(),
	reportSkillInstall: vi.fn(),
}));

vi.mock('node:fs/promises', () => ({
	access: mocks.access,
}));

vi.mock('../src/lib/plugin-config.js', () => ({
	getPluginConfig: (overrides: Record<string, unknown> = {}) => ({
		apiBaseUrl: 'https://api.test.com',
		installDir: '/mock/home/.agents/skills',
		timeout: 5000,
		...overrides,
	}),
}));

vi.mock('../src/lib/skill-api.js', async (importOriginal) => ({
	...(await importOriginal<typeof import('../src/lib/skill-api.js')>()),
	fetchSkillManifest: mocks.fetchSkillManifest,
	downloadSkillZip: mocks.downloadSkillZip,
}));

vi.mock('../src/lib/plugin-verify.js', () => ({
	verifyManifest: vi.fn(),
	verifySkillManifest: mocks.verifySkillManifest,
	verifyZipHash: mocks.verifyZipHash,
}));

vi.mock('../src/lib/plugin-api.js', () => ({
	fetchManifest: vi.fn(),
	reportInstallation: vi.fn(),
	reportSkillInstall: mocks.reportSkillInstall,
	PluginApiError: class PluginApiError extends Error {},
}));

vi.mock('../src/lib/plugin-download.js', () => ({
	downloadAllSkills: vi.fn(),
	printDownloadSummary: vi.fn(),
}));

vi.mock('../src/lib/plugin-logger.js', () => ({
	logger: {
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
		debug: vi.fn(),
		success: vi.fn(),
		box: vi.fn(),
		startSpinner: vi.fn(),
		stopSpinner: vi.fn(),
		spinnerSuccess: vi.fn(),
		spinnerError: vi.fn(),
	},
}));

vi.mock('../src/lib/agents.js', () => ({
	CANONICAL_SKILLS_DIR: '/mock/home/.agents/skills',
}));

vi.mock('../src/lib/installer.js', () => ({
	extractSkillZip: mocks.extractSkillZip,
	getCanonicalSkillPath: (slug: string) => `/mock/home/.agents/skills/${slug}`,
	linkSkillToDirectory: mocks.linkSkillToDirectory,
}));

vi.mock('../src/lib/skill-lock.js', () => ({
	addToLock: mocks.addToLock,
}));

import installCommand from '../src/commands/install.js';

describe('install command', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.access.mockRejectedValue(new Error('ENOENT'));
		mocks.fetchSkillManifest.mockResolvedValue({
			version: '1.0',
			schemaVersion: '2.0',
			kind: 'skill',
			skill: {
				slug: 'owner-skill',
				name: 'Owner Skill',
				version: '2.0.1',
				authorVersion: '2.0.1',
				skillstoreRevision: 2,
				versionStatus: 'valid',
				treeHash: 'tree-hash-r2',
				author: 'Owner',
			},
			artifact: { sha256: 'zip-hash-r2' },
			signature: 'signature',
			generatedAt: '2026-07-14T00:00:00.000Z',
		});
		mocks.downloadSkillZip.mockResolvedValue(new ArrayBuffer(8));
		mocks.verifySkillManifest.mockResolvedValue({ valid: true });
		mocks.verifyZipHash.mockReturnValue(true);
		mocks.extractSkillZip.mockResolvedValue(undefined);
		mocks.linkSkillToDirectory.mockResolvedValue({
			success: true,
			path: '/mock/target/owner-skill',
			symlinkFailed: false,
		});
		mocks.addToLock.mockResolvedValue(undefined);
		mocks.reportSkillInstall.mockResolvedValue(undefined);
	});

	it('writes the complete dual-version identity to the local lock', async () => {
		await installCommand.run?.({
			args: {
				target: 'owner-skill',
				dir: '/mock/target',
				'skip-verify': false,
				'dry-run': false,
				overwrite: false,
			},
		} as never);

		expect(mocks.addToLock).toHaveBeenCalledOnce();
		expect(mocks.addToLock).toHaveBeenCalledWith(
			expect.objectContaining({
				slug: 'owner-skill',
				version: '2.0.1',
				authorVersion: '2.0.1',
				skillstoreRevision: 2,
				versionStatus: 'valid',
				treeHash: 'tree-hash-r2',
				zipHash: 'zip-hash-r2',
				source: 'skillstore',
			})
		);
	});
});
