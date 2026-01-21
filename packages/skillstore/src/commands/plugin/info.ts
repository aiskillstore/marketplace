import { defineCommand } from 'citty';
import { getPluginConfig } from '../../lib/plugin-config.js';
import { fetchPluginInfo, PluginApiError } from '../../lib/plugin-api.js';
import { logger } from '../../lib/plugin-logger.js';

export default defineCommand({
	meta: {
		name: 'info',
		description: 'Show detailed information about a plugin',
	},
	args: {
		slug: {
			type: 'positional',
			description: 'Plugin slug to get info for',
			required: true,
		},
	},
	async run({ args }) {
		const { slug } = args;
		const config = getPluginConfig();

		logger.startSpinner(`Fetching info for plugin: ${slug}`);

		try {
			const info = await fetchPluginInfo(config, slug);
			logger.stopSpinner();

			// Display plugin info
			logger.box(`Plugin: ${info.name}`, [
				`Slug: ${info.slug}`,
				`Type: ${info.pluginType}`,
				`Pricing: ${info.pricing}${info.priceCents > 0 ? ` ($${(info.priceCents / 100).toFixed(2)} ${info.currency})` : ''}`,
				`Visibility: ${info.visibility}`,
				`Skills: ${info.skillCount}`,
				`Installs: ${info.installCount}`,
			]);

			if (info.description) {
				console.log('');
				console.log('Description:');
				console.log(`  ${info.description}`);
			}

			if (info.scenarioTags && info.scenarioTags.length > 0) {
				console.log('');
				console.log('Scenario Tags:');
				console.log(`  ${info.scenarioTags.join(', ')}`);
			}

			if (info.skills && info.skills.length > 0) {
				console.log('');
				console.log('Skills:');
				for (const skill of info.skills) {
					const score = skill.qualityScore ? ` (score: ${skill.qualityScore})` : '';
					const category = skill.category ? ` [${skill.category}]` : '';
					console.log(`  • ${skill.name}${category}${score}`);
					if (skill.description) {
						console.log(`    ${skill.description}`);
					}
				}
			}

			console.log('');
			console.log(`Install with: npx skillstore plugin install ${info.slug}`);
		} catch (err) {
			logger.stopSpinner();

			if (err instanceof PluginApiError) {
				if (err.statusCode === 404) {
					logger.error(`Plugin "${slug}" not found`);
				} else {
					logger.error(`API error: ${err.message}`);
				}
			} else {
				logger.error('Failed to fetch plugin info', err instanceof Error ? err : undefined);
			}

			process.exit(1);
		}
	},
});
