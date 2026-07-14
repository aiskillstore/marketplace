import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	getAllLockedSkills: vi.fn(),
	addToLock: vi.fn(),
	fetchSkillManifest: vi.fn(),
	getSkillZipHash: vi.fn(),
	verifySkillManifest: vi.fn(),
}));

vi.mock('../src/lib/skill-lock.js', () => ({
	getAllLockedSkills: mocks.getAllLockedSkills,
	addToLock: mocks.addToLock,
}));

vi.mock('../src/lib/skill-api.js', async (importOriginal) => ({
	...(await importOriginal<typeof import('../src/lib/skill-api.js')>()),
	fetchSkillManifest: mocks.fetchSkillManifest,
	downloadSkillZip: vi.fn(),
	getSkillZipHash: mocks.getSkillZipHash,
}));

vi.mock('../src/lib/plugin-verify.js', () => ({
	verifySkillManifest: mocks.verifySkillManifest,
	verifyZipHash: vi.fn(),
}));

vi.mock('../src/lib/plugin-config.js', () => ({
	getPluginConfig: (options: Record<string, unknown>) => options,
}));

vi.mock('../src/lib/plugin-logger.js', () => ({
	logger: {
		info: vi.fn(),
		warn: vi.fn(),
		error: vi.fn(),
		success: vi.fn(),
		spinnerSuccess: vi.fn(),
		spinnerError: vi.fn(),
		startSpinner: vi.fn(),
		stopSpinner: vi.fn(),
	},
}));

vi.mock('../src/lib/agents.js', () => ({
	CANONICAL_SKILLS_DIR: '/mock/home/.agents/skills',
	agents: { 'claude-code': { id: 'claude-code', name: 'Claude Code' } },
	detectInstalledAgents: vi.fn(() => []),
}));

vi.mock('../src/lib/installer.js', () => ({
	extractSkillZip: vi.fn(),
	installToAgents: vi.fn(),
	getCanonicalSkillPath: (slug: string) => `/mock/home/.agents/skills/${slug}`,
}));

vi.mock('../src/lib/plugin-api.js', () => ({
	reportSkillInstall: vi.fn(),
}));

import updateCommand from '../src/commands/update.js';

describe('update command', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.getAllLockedSkills.mockResolvedValue([
			{
				slug: 'legacy-skill',
				version: '1.0.1',
				zipHash: 'old-zip-hash',
				source: 'skillstore',
				installedAt: '2026-07-13T00:00:00.000Z',
				updatedAt: '2026-07-13T00:00:00.000Z',
			},
		]);
		mocks.fetchSkillManifest.mockResolvedValue({
			version: '1.0',
			skill: {
				slug: 'legacy-skill',
				name: 'Legacy Skill',
				version: '1.0.2',
				authorVersion: null,
				skillstoreRevision: 2,
				versionStatus: 'legacy_unknown',
				treeHash: 'a'.repeat(64),
			},
			signature: 'signature',
			generatedAt: '2026-07-14T00:00:00.000Z',
		});
		mocks.getSkillZipHash.mockReturnValue('new-zip-hash');
		mocks.verifySkillManifest.mockResolvedValue({ valid: true });
	});

	it('does not present an explicit legacy alias as an author-owned version', async () => {
		const log = vi.spyOn(console, 'log').mockImplementation(() => undefined);

		await updateCommand.run?.({
			args: { slug: undefined, 'skip-verify': false, 'dry-run': true },
		} as never);

		const output = log.mock.calls.map(([line]) => String(line)).join('\n');
		expect(output).toContain('Legacy v1.0.2 (unverified) (r2)');
		expect(output).not.toContain('→ v1.0.2 (r2)');
		log.mockRestore();
	});
});
