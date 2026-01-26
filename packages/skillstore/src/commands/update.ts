import { defineCommand } from 'citty';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { getAllLockedSkills, addToLock, type SkillLockEntry } from '../lib/skill-lock.js';
import { fetchSkillManifest, downloadSkillZip, SkillApiError } from '../lib/skill-api.js';
import { verifySkillManifest, verifyZipHash } from '../lib/plugin-verify.js';
import { getPluginConfig } from '../lib/plugin-config.js';
import { logger } from '../lib/plugin-logger.js';
import { detectInstalledAgents, agents, CANONICAL_SKILLS_DIR } from '../lib/agents.js';
import { installToAgents, getCanonicalSkillPath } from '../lib/installer.js';
import { reportSkillInstall } from '../lib/plugin-api.js';

/**
 * Update installed skills
 */
export default defineCommand({
	meta: {
		name: 'update',
		description: 'Update installed skills to latest versions',
	},
	args: {
		slug: {
			type: 'positional',
			description: 'Specific skill to update (optional, updates all if not specified)',
			required: false,
		},
		'skip-verify': {
			type: 'boolean',
			description: 'Skip manifest signature verification',
			default: false,
		},
		'dry-run': {
			type: 'boolean',
			description: 'Show what would be updated without actually updating',
			default: false,
		},
	},
	async run({ args }) {
		const { slug, 'skip-verify': skipVerify, 'dry-run': dryRun } = args;

		try {
			const skills = await getAllLockedSkills();

			if (skills.length === 0) {
				logger.info('No skills installed.');
				console.log('');
				console.log('To add a skill, run:');
				console.log('  npx skillstore add <skill-slug>');
				return;
			}

			// Filter to specific skill if provided
			let skillsToCheck: SkillLockEntry[];
			if (slug) {
				const found = skills.find((s) => s.slug === slug);
				if (!found) {
					logger.error(`Skill "${slug}" is not installed.`);
					console.log('');
					console.log('Installed skills:');
					for (const s of skills) {
						console.log(`  - ${s.slug}`);
					}
					process.exit(1);
				}
				skillsToCheck = [found];
			} else {
				skillsToCheck = skills;
			}

			const config = getPluginConfig({
				installDir: CANONICAL_SKILLS_DIR,
				skipVerify,
				dryRun,
			});

			logger.info(`Checking ${skillsToCheck.length} skill${skillsToCheck.length > 1 ? 's' : ''} for updates...`);

			if (dryRun) {
				logger.warn('Dry run mode - no files will be written');
			}

			// Find skills that need updates
			const updates: { skill: SkillLockEntry; latestVersion: string; latestHash: string }[] = [];

			for (const skill of skillsToCheck) {
				try {
					const manifest = await fetchSkillManifest(config, skill.slug);
					if (skill.zipHash !== manifest.skill.zipHash) {
						updates.push({
							skill,
							latestVersion: manifest.skill.version,
							latestHash: manifest.skill.zipHash,
						});
					}
				} catch (err) {
					if (err instanceof SkillApiError && err.statusCode === 404) {
						logger.warn(`Skill "${skill.slug}" no longer available, skipping`);
					} else {
						logger.warn(
							`Failed to check "${skill.slug}": ${err instanceof Error ? err.message : 'Unknown error'}`
						);
					}
				}
			}

			if (updates.length === 0) {
				logger.success('All skills are up to date!');
				return;
			}

			console.log('');
			console.log(`Updates available (${updates.length}):`);
			for (const update of updates) {
				console.log(
					`  - ${update.skill.slug}  v${update.skill.version} → v${update.latestVersion}`
				);
			}
			console.log('');

			if (dryRun) {
				logger.success('Dry run complete - no files were written');
				return;
			}

			// Detect agents for symlinking
			let targetAgents = detectInstalledAgents();
			if (targetAgents.length === 0) {
				targetAgents = [agents['claude-code']];
			}

			// Update each skill
			let successCount = 0;
			let failCount = 0;

			for (const update of updates) {
				const { skill, latestVersion } = update;

				try {
					logger.startSpinner(`Updating ${skill.slug}...`);

					// Fetch manifest
					const manifest = await fetchSkillManifest(config, skill.slug);

					// Verify manifest signature
					if (!skipVerify) {
						const verifyResult = await verifySkillManifest(manifest);
						if (!verifyResult.valid) {
							logger.spinnerError(`${skill.slug}: Manifest verification failed`);
							failCount++;
							continue;
						}
					}

					// Download ZIP
					const zipBuffer = await downloadSkillZip(config, skill.slug);

					// Verify ZIP hash
					if (!skipVerify) {
						if (!verifyZipHash(zipBuffer, manifest.skill.zipHash)) {
							logger.spinnerError(`${skill.slug}: Content verification failed`);
							failCount++;
							continue;
						}
					}

					// Extract to canonical location
					const canonicalPath = getCanonicalSkillPath(skill.slug);
					await extractZip(zipBuffer, canonicalPath);

					// Update symlinks (in case agents changed)
					await installToAgents(skill.slug, targetAgents, { global: true });

					// Update lock file
					await addToLock({
						slug: skill.slug,
						version: manifest.skill.version,
						zipHash: manifest.skill.zipHash,
						source: 'skillstore',
						installedAt: skill.installedAt,
					});

					// Report telemetry
					try {
						await reportSkillInstall(config, skill.slug);
					} catch {
						// Ignore telemetry errors
					}

					logger.spinnerSuccess(`${skill.slug}: v${skill.version} → v${latestVersion}`);
					successCount++;
				} catch (err) {
					logger.spinnerError(
						`${skill.slug}: ${err instanceof Error ? err.message : 'Unknown error'}`
					);
					failCount++;
				}
			}

			console.log('');
			if (failCount > 0) {
				logger.warn(`Updated ${successCount} skill${successCount !== 1 ? 's' : ''}, ${failCount} failed`);
				process.exit(1);
			} else {
				logger.success(`Updated ${successCount} skill${successCount !== 1 ? 's' : ''} successfully!`);
			}
		} catch (err) {
			logger.stopSpinner();
			logger.error('Update failed', err instanceof Error ? err : undefined);
			process.exit(1);
		}
	},
});

/**
 * Extract ZIP buffer to directory
 */
async function extractZip(buffer: ArrayBuffer, targetDir: string): Promise<void> {
	const { unzipSync } = await import('fflate');

	const data = new Uint8Array(buffer);
	const unzipped = unzipSync(data);

	for (const [path, content] of Object.entries(unzipped)) {
		if (path.endsWith('/')) continue;

		const fullPath = join(targetDir, path);
		await mkdir(dirname(fullPath), { recursive: true });
		await writeFile(fullPath, Buffer.from(content as Uint8Array));
	}
}
