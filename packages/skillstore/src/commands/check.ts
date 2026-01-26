import { defineCommand } from 'citty';
import { getAllLockedSkills, type SkillLockEntry } from '../lib/skill-lock.js';
import { fetchSkillManifest, SkillApiError } from '../lib/skill-api.js';
import { getPluginConfig } from '../lib/plugin-config.js';
import { logger } from '../lib/plugin-logger.js';

interface UpdateInfo {
	skill: SkillLockEntry;
	currentVersion: string;
	latestVersion: string;
	hasUpdate: boolean;
}

/**
 * Check for available skill updates
 */
export default defineCommand({
	meta: {
		name: 'check',
		description: 'Check for available skill updates',
	},
	args: {
		json: {
			type: 'boolean',
			description: 'Output as JSON',
			default: false,
		},
	},
	async run({ args }) {
		const { json: outputJson } = args;

		try {
			const skills = await getAllLockedSkills();

			if (skills.length === 0) {
				if (outputJson) {
					console.log(JSON.stringify({ skills: [], updates: 0 }));
				} else {
					logger.info('No skills installed.');
					console.log('');
					console.log('To add a skill, run:');
					console.log('  npx skillstore add <skill-slug>');
				}
				return;
			}

			const config = getPluginConfig({});

			if (!outputJson) {
				logger.info('Checking for updates...');
				console.log('');
			}

			const updates: UpdateInfo[] = [];
			const upToDate: UpdateInfo[] = [];
			const errors: { slug: string; error: string }[] = [];

			// Check each skill
			for (const skill of skills) {
				try {
					const manifest = await fetchSkillManifest(config, skill.slug);

					const info: UpdateInfo = {
						skill,
						currentVersion: skill.version,
						latestVersion: manifest.skill.version,
						hasUpdate: skill.zipHash !== manifest.skill.zipHash,
					};

					if (info.hasUpdate) {
						updates.push(info);
					} else {
						upToDate.push(info);
					}
				} catch (err) {
					if (err instanceof SkillApiError && err.statusCode === 404) {
						errors.push({ slug: skill.slug, error: 'Skill no longer available' });
					} else {
						errors.push({
							slug: skill.slug,
							error: err instanceof Error ? err.message : 'Unknown error',
						});
					}
				}
			}

			if (outputJson) {
				console.log(
					JSON.stringify(
						{
							updates: updates.map((u) => ({
								slug: u.skill.slug,
								currentVersion: u.currentVersion,
								latestVersion: u.latestVersion,
							})),
							upToDate: upToDate.map((u) => u.skill.slug),
							errors,
						},
						null,
						2
					)
				);
				return;
			}

			// Display updates available
			if (updates.length > 0) {
				console.log(`Updates available (${updates.length}):`);
				for (let i = 0; i < updates.length; i++) {
					const update = updates[i];
					const isLast = i === updates.length - 1;
					const prefix = isLast ? '└─' : '├─';
					console.log(
						`  ${prefix} ${update.skill.slug}  v${update.currentVersion} → v${update.latestVersion}`
					);
				}
				console.log('');
			}

			// Display up-to-date skills
			if (upToDate.length > 0) {
				console.log(`No updates (${upToDate.length}):`);
				for (let i = 0; i < upToDate.length; i++) {
					const skill = upToDate[i];
					const isLast = i === upToDate.length - 1;
					const prefix = isLast ? '└─' : '├─';
					console.log(`  ${prefix} ${skill.skill.slug}  v${skill.currentVersion} (latest)`);
				}
				console.log('');
			}

			// Display errors
			if (errors.length > 0) {
				console.log(`Errors (${errors.length}):`);
				for (let i = 0; i < errors.length; i++) {
					const err = errors[i];
					const isLast = i === errors.length - 1;
					const prefix = isLast ? '└─' : '├─';
					console.log(`  ${prefix} ${err.slug}  (${err.error})`);
				}
				console.log('');
			}

			// Summary
			if (updates.length > 0) {
				logger.info(`Run 'skillstore update' to install ${updates.length} update${updates.length > 1 ? 's' : ''}.`);
			} else {
				logger.success('All skills are up to date!');
			}
		} catch (err) {
			logger.error('Failed to check for updates', err instanceof Error ? err : undefined);
			process.exit(1);
		}
	},
});
