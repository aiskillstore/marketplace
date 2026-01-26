import { defineCommand } from 'citty';
import { getAllLockedSkills } from '../lib/skill-lock.js';
import { logger } from '../lib/plugin-logger.js';

/**
 * List installed skills
 */
export default defineCommand({
	meta: {
		name: 'list',
		description: 'List installed skills',
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

			if (outputJson) {
				console.log(JSON.stringify(skills, null, 2));
				return;
			}

			if (skills.length === 0) {
				logger.info('No skills installed.');
				console.log('');
				console.log('To add a skill, run:');
				console.log('  npx skillstore add <skill-slug>');
				return;
			}

			console.log('');
			console.log(`Installed skills (${skills.length}):`);
			console.log('');

			// Sort by updatedAt (most recent first)
			const sortedSkills = skills.sort(
				(a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
			);

			for (let i = 0; i < sortedSkills.length; i++) {
				const skill = sortedSkills[i];
				const isLast = i === sortedSkills.length - 1;
				const prefix = isLast ? '└─' : '├─';

				const relativeTime = getRelativeTime(new Date(skill.updatedAt));
				console.log(`  ${prefix} ${skill.slug}  v${skill.version}  (${relativeTime})`);
			}

			console.log('');
		} catch (err) {
			logger.error('Failed to list skills', err instanceof Error ? err : undefined);
			process.exit(1);
		}
	},
});

/**
 * Get relative time string
 */
function getRelativeTime(date: Date): string {
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffSeconds = Math.floor(diffMs / 1000);
	const diffMinutes = Math.floor(diffSeconds / 60);
	const diffHours = Math.floor(diffMinutes / 60);
	const diffDays = Math.floor(diffHours / 24);
	const diffWeeks = Math.floor(diffDays / 7);
	const diffMonths = Math.floor(diffDays / 30);

	if (diffSeconds < 60) {
		return 'just now';
	} else if (diffMinutes < 60) {
		return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
	} else if (diffHours < 24) {
		return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
	} else if (diffDays === 1) {
		return 'yesterday';
	} else if (diffDays < 7) {
		return `${diffDays} days ago`;
	} else if (diffWeeks === 1) {
		return '1 week ago';
	} else if (diffWeeks < 4) {
		return `${diffWeeks} weeks ago`;
	} else if (diffMonths === 1) {
		return '1 month ago';
	} else if (diffMonths < 12) {
		return `${diffMonths} months ago`;
	} else {
		return date.toLocaleDateString();
	}
}
