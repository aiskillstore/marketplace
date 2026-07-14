import { defineCommand } from 'citty';
import { readdir, access } from 'node:fs/promises';
import { join } from 'node:path';
import { writeSkillLock, LOCK_VERSION, type SkillLock, type SkillLockEntry } from '../lib/skill-lock.js';
import {
	fetchSkillManifest,
	formatSkillVersionIdentity,
	getSkillLockVersionIdentity,
	getSkillZipHash,
	SkillApiError,
} from '../lib/skill-api.js';
import { getPluginConfig } from '../lib/plugin-config.js';
import { logger } from '../lib/plugin-logger.js';
import { CANONICAL_SKILLS_DIR } from '../lib/agents.js';
import { verifySkillManifest } from '../lib/plugin-verify.js';
import { readInstalledSkillReceipt } from '../lib/skill-receipt.js';

/**
 * Generate lock file from installed skills
 */
export default defineCommand({
	meta: {
		name: 'generate-lock',
		description: 'Generate lock file from installed skills',
	},
	args: {
		dir: {
			type: 'string',
			description: 'Directory to scan for skills',
			default: CANONICAL_SKILLS_DIR,
		},
		'dry-run': {
			type: 'boolean',
			description: 'Show what would be generated without writing',
			default: false,
		},
	},
	async run({ args }) {
		const { dir, 'dry-run': dryRun } = args;

		try {
			logger.info(`Scanning ${dir}...`);

			// Check if directory exists
			try {
				await access(dir);
			} catch {
				logger.error(`Directory not found: ${dir}`);
				console.log('');
				console.log('No skills are installed yet.');
				console.log('To add a skill, run:');
				console.log('  npx skillstore add <skill-slug>');
				return;
			}

			// List skill directories
			const entries = await readdir(dir, { withFileTypes: true });
			const skillDirs = entries.filter((e) => e.isDirectory()).map((e) => e.name);

			if (skillDirs.length === 0) {
				logger.info('No skill directories found.');
				return;
			}

			const config = getPluginConfig({});

			console.log('');
			logger.info(`Found ${skillDirs.length} skill director${skillDirs.length > 1 ? 'ies' : 'y'}`);
			console.log('');

			const matched: SkillLockEntry[] = [];
			const skipped: { slug: string; reason: string }[] = [];

			for (const slug of skillDirs) {
				// Skip hidden directories
				if (slug.startsWith('.')) {
					skipped.push({ slug, reason: 'hidden directory' });
					continue;
				}

				try {
					// Try to fetch manifest from skillstore.io
					const manifest = await fetchSkillManifest(config, slug);
					const zipHash = getSkillZipHash(manifest);
					const lockIdentity = getSkillLockVersionIdentity(manifest.skill);
					if (!zipHash) {
						skipped.push({ slug, reason: 'manifest is missing ZIP hash' });
						console.log(`  ✗ ${slug} (manifest is missing ZIP hash)`);
						continue;
					}
					const verifyResult = await verifySkillManifest(manifest);
					if (!verifyResult.valid) {
						skipped.push({ slug, reason: 'manifest verification failed' });
						console.log(`  ✗ ${slug} (manifest verification failed)`);
						continue;
					}
					const receipt = await readInstalledSkillReceipt(join(dir, slug));
					if (!receipt) {
						skipped.push({ slug, reason: 'verified Skillstore receipt missing' });
						console.log(`  ✗ ${slug} (verified Skillstore receipt missing)`);
						continue;
					}
					if (
						lockIdentity.skillstoreRevision == null
						|| !lockIdentity.treeHash
						|| receipt.skillstoreRevision !== lockIdentity.skillstoreRevision
						|| receipt.treeHash !== lockIdentity.treeHash.toLowerCase()
					) {
						skipped.push({ slug, reason: 'installed receipt does not match current artifact' });
						console.log(`  ✗ ${slug} (installed receipt does not match current artifact)`);
						continue;
					}

					matched.push({
						slug,
						...lockIdentity,
						zipHash,
						source: 'skillstore',
						installedAt: new Date().toISOString(),
						updatedAt: new Date().toISOString(),
					});

					console.log(`  ✓ ${slug} (${formatSkillVersionIdentity(manifest.skill)})`);
				} catch (err) {
					if (err instanceof SkillApiError && err.statusCode === 404) {
						skipped.push({ slug, reason: 'not from skillstore.io' });
						console.log(`  ✗ ${slug} (not found on skillstore.io)`);
					} else {
						skipped.push({
							slug,
							reason: err instanceof Error ? err.message : 'unknown error',
						});
						console.log(`  ✗ ${slug} (error: ${err instanceof Error ? err.message : 'unknown'})`);
					}
				}
			}

			console.log('');

			if (matched.length === 0) {
				logger.warn('No installed skills could be verified for update tracking');
				console.log('');
				console.log('Only skills with a valid Skillstore manifest and matching install receipt can be tracked.');
				return;
			}

			// Build lock file
			const lock: SkillLock = {
				version: LOCK_VERSION,
				skills: {},
			};

			for (const entry of matched) {
				lock.skills[entry.slug] = entry;
			}

			if (dryRun) {
				logger.success('Dry run complete - lock file not written');
				console.log('');
				console.log('Would generate lock file with:');
				console.log(`  - ${matched.length} skill${matched.length > 1 ? 's' : ''} from skillstore.io`);
				if (skipped.length > 0) {
					console.log(`  - ${skipped.length} skipped (not verifiable for update tracking)`);
				}
				console.log('');
				console.log(JSON.stringify(lock, null, 2));
				return;
			}

			// Write lock file
			await writeSkillLock(lock);

			logger.success(`Generated lock file with ${matched.length} skill${matched.length > 1 ? 's' : ''}`);

			if (skipped.length > 0) {
				console.log('');
				console.log(`Skipped (${skipped.length}):`);
				for (const skip of skipped) {
					console.log(`  - ${skip.slug}: ${skip.reason}`);
				}
			}
		} catch (err) {
			logger.error('Failed to generate lock file', err instanceof Error ? err : undefined);
			process.exit(1);
		}
	},
});
