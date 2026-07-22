import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { PluginConfig } from '../src/lib/plugin-config.js';
import type { ManifestSkill } from '../src/lib/plugin-api.js';
import type { DownloadSummary } from '../src/lib/plugin-download.js';

const mocks = vi.hoisted(() => ({
	fetchSkillManifest: vi.fn(),
	getSkillLockVersionIdentity: vi.fn(),
	getSkillZipHash: vi.fn(),
	verifySkillManifest: vi.fn(),
	addToLock: vi.fn(),
	warn: vi.fn(),
}));

vi.mock('../src/lib/skill-api.js', () => ({
	fetchSkillManifest: mocks.fetchSkillManifest,
	getSkillLockVersionIdentity: mocks.getSkillLockVersionIdentity,
	getSkillZipHash: mocks.getSkillZipHash,
}));

vi.mock('../src/lib/plugin-verify.js', () => ({
	verifySkillManifest: mocks.verifySkillManifest,
}));

vi.mock('../src/lib/skill-lock.js', () => ({
	addToLock: mocks.addToLock,
}));

vi.mock('../src/lib/plugin-logger.js', () => ({
	logger: { warn: mocks.warn },
}));

import { lockVerifiedPackMembers } from '../src/lib/pack-lock.js';

const config: PluginConfig = {
	apiBaseUrl: 'https://skillstore.test/api',
	installDir: '/tmp/skills',
	timeout: 1000,
	maxConcurrent: 1,
	skipVerify: false,
	dryRun: false,
};

const member: ManifestSkill = {
	slug: 'owner-skill',
	name: 'Owner Skill',
	version: '2.0.1',
	authorVersion: '2.0.1',
	skillstoreRevision: 7,
	versionStatus: 'declared',
	treeHash: 'a'.repeat(64),
	contentHash: 'pack-content-hash',
	downloadUrl: 'https://skillstore.test/member',
};

function download(overrides: Partial<DownloadSummary['results'][number]> = {}): DownloadSummary {
	return {
		total: 1,
		success: 1,
		failed: 0,
		skipped: 0,
		results: [{ slug: member.slug, success: true, ...overrides }],
	};
}

describe('pack-lock', () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mocks.fetchSkillManifest.mockResolvedValue({ skill: { ...member } });
		mocks.getSkillLockVersionIdentity.mockReturnValue({
			version: member.version,
			authorVersion: member.authorVersion,
			skillstoreRevision: member.skillstoreRevision,
			versionStatus: member.versionStatus,
			treeHash: member.treeHash,
		});
		mocks.getSkillZipHash.mockReturnValue('single-skill-zip-hash');
		mocks.verifySkillManifest.mockResolvedValue({ valid: true });
	});

	it('locks a verified matching member with the single-skill ZIP hash', async () => {
		await expect(lockVerifiedPackMembers(config, [member], download()))
			.resolves.toEqual({ locked: 1, skipped: 0 });

		expect(mocks.addToLock).toHaveBeenCalledWith(expect.objectContaining({
			slug: member.slug,
			version: '2.0.1',
			skillstoreRevision: 7,
			treeHash: 'a'.repeat(64),
			zipHash: 'single-skill-zip-hash',
		}));
	});

	it('leaves a member unlocked when the signed identities differ', async () => {
		mocks.getSkillLockVersionIdentity.mockReturnValue({
			version: member.version,
			authorVersion: member.authorVersion,
			skillstoreRevision: 8,
			versionStatus: member.versionStatus,
			treeHash: member.treeHash,
		});

		await expect(lockVerifiedPackMembers(config, [member], download()))
			.resolves.toEqual({ locked: 0, skipped: 1 });
		expect(mocks.addToLock).not.toHaveBeenCalled();
	});

	it('leaves a member unlocked when its single-skill signature is invalid', async () => {
		mocks.verifySkillManifest.mockResolvedValue({ valid: false, error: 'bad signature' });

		await expect(lockVerifiedPackMembers(config, [member], download()))
			.resolves.toEqual({ locked: 0, skipped: 1 });
		expect(mocks.addToLock).not.toHaveBeenCalled();
	});

	it('locks an already-present member after its fresh verified reuse check', async () => {
		await expect(lockVerifiedPackMembers(config, [member], download({ skipped: true })))
			.resolves.toEqual({ locked: 1, skipped: 0 });
		expect(mocks.fetchSkillManifest).toHaveBeenCalledWith(config, member.slug);
		expect(mocks.addToLock).toHaveBeenCalled();
	});
});
