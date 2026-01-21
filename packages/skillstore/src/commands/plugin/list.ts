import { defineCommand } from 'citty';
import { getPluginConfig } from '../../lib/plugin-config.js';
import { fetchPluginList, PluginApiError } from '../../lib/plugin-api.js';
import { logger } from '../../lib/plugin-logger.js';

export default defineCommand({
	meta: {
		name: 'list',
		description: 'List available plugins from skillstore.io',
	},
	args: {
		type: {
			type: 'string',
			description: 'Filter by type: curated, scenario, or user',
		},
		pricing: {
			type: 'string',
			description: 'Filter by pricing: free or paid',
		},
		limit: {
			type: 'string',
			description: 'Number of plugins to show',
			default: '10',
		},
		page: {
			type: 'string',
			description: 'Page number for pagination',
			default: '1',
		},
	},
	async run({ args }) {
		const { type, pricing, limit, page } = args;
		const config = getPluginConfig();

		logger.startSpinner('Fetching plugins...');

		try {
			const response = await fetchPluginList(config, {
				type: type as 'curated' | 'scenario' | 'user' | undefined,
				pricing: pricing as 'free' | 'paid' | undefined,
				limit: parseInt(limit, 10),
				page: parseInt(page, 10),
			});

			logger.stopSpinner();

			if (response.data.length === 0) {
				logger.warn('No plugins found');
				return;
			}

			console.log('');
			console.log(`Showing ${response.data.length} of ${response.pagination.total} plugins (page ${response.pagination.page}/${response.pagination.totalPages})`);
			console.log('');

			for (const plugin of response.data) {
				const pricingBadge = plugin.pricing === 'paid' ? ' [PAID]' : '';
				const typeBadge = `[${plugin.pluginType.toUpperCase()}]`;

				console.log(`  ${plugin.name} ${typeBadge}${pricingBadge}`);
				console.log(`    Slug: ${plugin.slug}`);
				console.log(`    Skills: ${plugin.skillCount} | Installs: ${plugin.installCount}`);
				if (plugin.description) {
					console.log(`    ${plugin.description.substring(0, 80)}${plugin.description.length > 80 ? '...' : ''}`);
				}
				console.log('');
			}

			if (response.pagination.page < response.pagination.totalPages) {
				console.log(`Use --page ${response.pagination.page + 1} to see more`);
			}
		} catch (err) {
			logger.stopSpinner();

			if (err instanceof PluginApiError) {
				logger.error(`API error: ${err.message}`);
			} else {
				logger.error('Failed to fetch plugin list', err instanceof Error ? err : undefined);
			}

			process.exit(1);
		}
	},
});
