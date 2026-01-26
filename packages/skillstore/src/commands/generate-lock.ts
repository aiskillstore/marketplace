import { defineCommand } from 'citty';
import { readdir, access } from 'node:fs/promises';
import { writeSkillLock, LOCK_VERSION, type SkillLock, type SkillLockEntry } from '../lib/skill-lock.js';
import { fetchSkillManifest, SkillApiError } from '../lib/skill-api.js';
import { getPluginConfig } from '../lib/plugin-config.js';
import { logger } from '../lib/plugin-logger.js';
import { CANONICAL_SKILLS_DIR } from '../lib/agents.js';

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

					matched.push({
						slug,
						version: manifest.skill.version,
						zipHash: manifest.skill.zipHash,
						source: 'skillstore',
						installedAt: new Date().toISOString(),
						updatedAt: new Date().toISOString(),
					});

					console.log(`  ✓ ${slug} (v${manifest.skill.version})`);
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
				logger.warn('No skills matched with skillstore.io');
				console.log('');
				console.log('Skills not from skillstore.io cannot be tracked for updates.');
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
					console.log(`  - ${skipped.length} skipped (not from skillstore.io)`);
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
