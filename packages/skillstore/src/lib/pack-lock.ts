import type { PluginConfig } from './plugin-config.js';
import type { ManifestSkill } from './plugin-api.js';
import type { DownloadSummary } from './plugin-download.js';
import {
	fetchSkillManifest,
	getSkillLockVersionIdentity,
	getSkillZipHash,
} from './skill-api.js';
import { verifySkillManifest } from './plugin-verify.js';
import { addToLock } from './skill-lock.js';
import { logger } from './plugin-logger.js';

function hasOwn(value: object, key: PropertyKey): boolean {
	return Object.prototype.hasOwnProperty.call(value, key);
}

function packMemberIdentity(skill: ManifestSkill) {
	const authorVersion = hasOwn(skill, 'authorVersion')
		? skill.authorVersion ?? null
		: skill.version ?? null;
	return {
		version: skill.version ?? authorVersion,
		authorVersion,
		skillstoreRevision: skill.skillstoreRevision ?? null,
		versionStatus: skill.versionStatus || (authorVersion ? 'legacy_unknown' : 'missing'),
		treeHash: skill.treeHash ?? null,
	};
}

/**
 * Lock only pack members installed in this run. The pack's file aggregate hash
 * is not a single-skill ZIP hash, so each member is rebound to a separately
 * verified single-skill manifest before it becomes update-managed.
 */
export async function lockVerifiedPackMembers(
	config: PluginConfig,
	packSkills: ManifestSkill[],
	download: DownloadSummary
): Promise<{ locked: number; skipped: number }> {
	let locked = 0;
	let skipped = 0;
	const installed = download.results.filter((result) => result.success && !result.skipped);

	for (const result of installed) {
		const member = packSkills.find((skill) => skill.slug === result.slug);
		if (!member) {
			logger.warn(`Not locking ${result.slug}: missing from verified pack payload`);
			skipped++;
			continue;
		}

		try {
			const manifest = await fetchSkillManifest(config, result.slug);
			const verification = await verifySkillManifest(manifest);
			const zipHash = getSkillZipHash(manifest);
			const single = getSkillLockVersionIdentity(manifest.skill);
			const packed = packMemberIdentity(member);
			const identityMatches = manifest.skill.slug === member.slug
				&& !!single.treeHash
				&& single.version === packed.version
				&& single.authorVersion === packed.authorVersion
				&& single.skillstoreRevision === packed.skillstoreRevision
				&& single.versionStatus === packed.versionStatus
				&& single.treeHash === packed.treeHash;

			if (!verification.valid || !zipHash || !identityMatches) {
				logger.warn(`Not locking ${result.slug}: single-skill manifest does not match verified pack member`);
				skipped++;
				continue;
			}

			await addToLock({
				slug: result.slug,
				...single,
				zipHash,
				source: 'skillstore',
				installedAt: new Date().toISOString(),
			});
			locked++;
		} catch (error) {
			logger.warn(`Not locking ${result.slug}: ${error instanceof Error ? error.message : 'verification failed'}`);
			skipped++;
		}
	}

	return { locked, skipped };
}
