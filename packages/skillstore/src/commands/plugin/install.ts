import { defineCommand } from 'citty';
import { getPluginConfig } from '../../lib/plugin-config.js';
import { fetchManifest, reportInstallation, PluginApiError } from '../../lib/plugin-api.js';
import { verifyManifest } from '../../lib/plugin-verify.js';
import { downloadAllSkills, printDownloadSummary } from '../../lib/plugin-download.js';
import { logger } from '../../lib/plugin-logger.js';

export default defineCommand({
	meta: {
		name: 'install',
		description: 'Install a plugin (collection of skills) to your project',
	},
	args: {
		slug: {
			type: 'positional',
			description: 'Plugin slug to install',
			required: true,
		},
		dir: {
			type: 'string',
			description: 'Installation directory (default: .claude/skills)',
			default: '.claude/skills',
		},
		'skip-verify': {
			type: 'boolean',
			description: 'Skip manifest signature verification',
			default: false,
		},
		'dry-run': {
			type: 'boolean',
			description: 'Show what would be installed without actually installing',
			default: false,
		},
		overwrite: {
			type: 'boolean',
			description: 'Overwrite existing skill files',
			default: false,
		},
	},
	async run({ args }) {
		const { slug, dir, 'skip-verify': skipVerify, 'dry-run': dryRun, overwrite } = args;

		// Build config from args
		const config = getPluginConfig({
			installDir: dir,
			skipVerify,
			dryRun,
		});

		logger.info(`Installing plugin: ${slug}`);
		logger.info(`Target directory: ${config.installDir}`);

		if (dryRun) {
			logger.warn('Dry run mode - no files will be written');
		}

		try {
			// Step 1: Fetch manifest
			logger.startSpinner('Fetching plugin manifest...');
			const manifest = await fetchManifest(config, slug);
			logger.spinnerSuccess(`Fetched manifest for "${manifest.plugin.name}"`);

			// Step 2: Verify manifest
			if (!skipVerify) {
				logger.startSpinner('Verifying manifest signature...');
				const verifyResult = await verifyManifest(manifest, { skipSignature: skipVerify });

				if (!verifyResult.valid) {
					logger.spinnerError('Manifest verification failed');
					logger.error(verifyResult.error || 'Unknown verification error');
					process.exit(1);
				}

				if (verifyResult.error) {
					// Warning but continue
					logger.spinnerSuccess('Manifest structure valid');
					logger.warn(verifyResult.error);
				} else {
					logger.spinnerSuccess('Manifest verified');
				}
			} else {
				logger.warn('Skipping manifest signature verification');
			}

			// Step 3: Show plugin info
			logger.box(`Plugin: ${manifest.plugin.name}`, [
				`Version: ${manifest.plugin.version}`,
				`Skills: ${manifest.skills.length}`,
				`Generated: ${new Date(manifest.generatedAt).toLocaleDateString()}`,
			]);

			// Step 4: Download skills
			logger.info('');
			const downloadResult = await downloadAllSkills(config, manifest.skills, {
				overwrite,
				verifyHash: !skipVerify,
			});

			// Step 5: Print summary
			printDownloadSummary(downloadResult);

			// Step 6: Report installation (non-blocking)
			if (!dryRun && downloadResult.success > 0) {
				try {
					const reportResult = await reportInstallation(config, slug, 'cli');
					if (reportResult.duplicate) {
						logger.debug('Installation already recorded');
					} else if (reportResult.success) {
						logger.debug('Installation reported successfully');
					}
				} catch {
					// Don't fail on report error
					logger.debug('Failed to report installation (non-critical)');
				}
			}

			// Final status
			if (downloadResult.failed > 0) {
				logger.warn(`Installation completed with ${downloadResult.failed} failures`);
				process.exit(1);
			} else if (dryRun) {
				logger.success('Dry run complete - no files were written');
			} else {
				logger.success(`Plugin "${manifest.plugin.name}" installed successfully!`);
			}
		} catch (err) {
			logger.stopSpinner();

			if (err instanceof PluginApiError) {
				if (err.statusCode === 404) {
					logger.error(`Plugin "${slug}" not found`);
				} else if (err.statusCode === 403) {
					logger.error('Access denied - plugin may be private or require purchase');
				} else {
					logger.error(`API error: ${err.message}`);
				}
			} else {
				logger.error('Installation failed', err instanceof Error ? err : undefined);
			}

			process.exit(1);
		}
	},
});
