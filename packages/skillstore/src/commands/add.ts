import { defineCommand } from 'citty';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { getPluginConfig } from '../lib/plugin-config.js';
import {
	fetchManifest,
	reportInstallation,
	reportSkillInstall,
	PluginApiError,
} from '../lib/plugin-api.js';
import { fetchSkillManifest, downloadSkillZip, SkillApiError } from '../lib/skill-api.js';
import { verifyManifest, verifySkillManifest, verifyZipHash } from '../lib/plugin-verify.js';
import { downloadAllSkills, printDownloadSummary } from '../lib/plugin-download.js';
import { logger } from '../lib/plugin-logger.js';
import {
	agents,
	detectInstalledAgents,
	getAgentsByIds,
	isValidAgentId,
	CANONICAL_SKILLS_DIR,
	type AgentConfig,
	type AgentId,
} from '../lib/agents.js';
import { addToLock, getLockEntry } from '../lib/skill-lock.js';
import { installToAgents, getCanonicalSkillPath } from '../lib/installer.js';

/**
 * Normalize skill/plugin slug
 * Converts "owner/name" format to "owner-name" format
 */
function normalizeSlug(slug: string): string {
	return slug.replace(/\//g, '-');
}

/**
 * Unified add command
 *
 * - `skillstore add <slug>` → Add single skill
 * - `skillstore add @<plugin>` → Add plugin (skill collection)
 */
export default defineCommand({
	meta: {
		name: 'add',
		description: 'Add skills or plugins from skillstore.io',
	},
	args: {
		target: {
			type: 'positional',
			description: 'Skill slug or @plugin to add',
			required: true,
		},
		agent: {
			type: 'string',
			alias: 'a',
			description: 'Target specific agents (comma-separated)',
		},
		global: {
			type: 'boolean',
			alias: 'g',
			description: 'Install to user-level (~/) instead of project-level',
			default: true, // Default to global for skillstore
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
			description: 'Overwrite existing files',
			default: false,
		},
	},
	async run({ args }) {
		const {
			target,
			agent: agentArg,
			global: isGlobal,
			'skip-verify': skipVerify,
			'dry-run': dryRun,
			overwrite,
		} = args;

		// Detect if target is a plugin (@prefix) or skill
		const isPlugin = target.startsWith('@');
		const rawSlug = isPlugin ? target.slice(1) : target;

		// Normalize slug: convert "owner/name" format to "owner-name"
		const slug = normalizeSlug(rawSlug);

		// Determine target agents
		let targetAgents: AgentConfig[];
		if (agentArg) {
			// Parse comma-separated agent IDs
			const agentIds = agentArg.split(',').map((s) => s.trim()) as AgentId[];
			const invalidIds = agentIds.filter((id) => !isValidAgentId(id));
			if (invalidIds.length > 0) {
				logger.error(`Invalid agent ID(s): ${invalidIds.join(', ')}`);
				console.log('');
				console.log('Valid agents: claude-code, cursor, windsurf, cline, codex, continue, etc.');
				process.exit(1);
			}
			targetAgents = getAgentsByIds(agentIds);
		} else {
			// Auto-detect installed agents
			targetAgents = detectInstalledAgents();
			if (targetAgents.length === 0) {
				logger.warn('No AI coding agents detected. Installing to Claude Code by default.');
				targetAgents = [agents['claude-code']];
			}
		}

		if (isPlugin) {
			await addPlugin(slug, { targetAgents, isGlobal, skipVerify, dryRun, overwrite });
		} else {
			await addSkill(slug, { targetAgents, isGlobal, skipVerify, dryRun, overwrite });
		}
	},
});

interface AddOptions {
	targetAgents: AgentConfig[];
	isGlobal: boolean;
	skipVerify: boolean;
	dryRun: boolean;
	overwrite: boolean;
}

/**
 * Add a single skill
 */
async function addSkill(slug: string, options: AddOptions): Promise<void> {
	const { targetAgents, isGlobal, skipVerify, dryRun, overwrite } = options;

	const config = getPluginConfig({
		installDir: CANONICAL_SKILLS_DIR, // Use canonical dir for extraction
		skipVerify,
		dryRun,
	});

	logger.info(`Adding skill: ${slug}`);
	logger.info(`Target agents: ${targetAgents.map((a) => a.name).join(', ')}`);

	if (dryRun) {
		logger.warn('Dry run mode - no files will be written');
	}

	try {
		// Step 1: Fetch skill manifest
		logger.startSpinner('Fetching skill manifest...');
		const manifest = await fetchSkillManifest(config, slug);
		logger.spinnerSuccess(`Found skill: "${manifest.skill.name}"`);

		// Step 2: Verify manifest signature
		if (!skipVerify) {
			logger.startSpinner('Verifying manifest signature...');
			const verifyResult = await verifySkillManifest(manifest);
			if (!verifyResult.valid) {
				logger.spinnerError('Manifest verification failed');
				logger.error(verifyResult.error || 'Unknown verification error');
				process.exit(1);
			}
			logger.spinnerSuccess('Manifest verified');
		} else {
			logger.warn('Skipping signature verification');
		}

		// Step 3: Show skill info
		logger.box(`Skill: ${manifest.skill.name}`, [
			`Slug: ${manifest.skill.slug}`,
			`Version: ${manifest.skill.version}`,
			`Author: ${manifest.skill.author || 'Unknown'}`,
		]);

		// Step 4: Check if already installed
		const existingLock = await getLockEntry(slug);
		if (existingLock && !overwrite) {
			if (existingLock.zipHash === manifest.skill.zipHash) {
				logger.warn(`Skill "${slug}" is already installed (v${existingLock.version})`);
				logger.info('Use --overwrite to reinstall');
				return;
			}
			logger.info(`Updating "${slug}" from v${existingLock.version} to v${manifest.skill.version}`);
		}

		if (dryRun) {
			logger.success('Dry run complete - no files were written');
			console.log('');
			console.log(`Would install to: ${getCanonicalSkillPath(slug)}`);
			console.log(`Would symlink to: ${targetAgents.map((a) => a.name).join(', ')}`);
			return;
		}

		// Step 5: Download skill ZIP
		logger.startSpinner('Downloading skill...');
		const zipBuffer = await downloadSkillZip(config, slug);
		logger.spinnerSuccess('Downloaded skill package');

		// Step 6: Verify ZIP hash
		if (!skipVerify) {
			logger.startSpinner('Verifying content integrity...');
			if (!verifyZipHash(zipBuffer, manifest.skill.zipHash)) {
				logger.spinnerError('Content verification failed');
				logger.error('ZIP hash mismatch - content may be corrupted or tampered');
				process.exit(1);
			}
			logger.spinnerSuccess('Content verified');
		}

		// Step 7: Extract ZIP to canonical location
		logger.startSpinner('Extracting files...');
		const canonicalPath = getCanonicalSkillPath(slug);
		await extractZip(zipBuffer, canonicalPath);
		logger.spinnerSuccess('Extracted files');

		// Step 8: Create symlinks to agents
		logger.startSpinner('Creating symlinks to agents...');
		const installResult = await installToAgents(slug, targetAgents, { global: isGlobal });
		if (installResult.successCount > 0) {
			logger.spinnerSuccess(
				`Linked to ${installResult.successCount} agent${installResult.successCount > 1 ? 's' : ''}`
			);
		} else {
			logger.spinnerError('Failed to link to any agents');
		}

		// Show symlink results
		for (const result of installResult.agents) {
			if (result.success) {
				if (result.symlinkFailed) {
					logger.warn(`  ${result.agentId}: copied (symlink failed)`);
				} else {
					logger.debug(`  ${result.agentId}: symlinked`);
				}
			} else {
				logger.error(`  ${result.agentId}: ${result.error}`);
			}
		}

		// Step 9: Update lock file
		await addToLock({
			slug,
			version: manifest.skill.version,
			zipHash: manifest.skill.zipHash,
			source: 'skillstore',
			installedAt: new Date().toISOString(),
		});
		logger.debug('Updated lock file');

		// Step 10: Report installation (non-blocking telemetry)
		try {
			await reportSkillInstall(config, slug);
			logger.debug('Installation telemetry reported');
		} catch {
			logger.debug('Failed to report telemetry (non-critical)');
		}

		logger.success(`Skill "${manifest.skill.name}" added successfully!`);
		console.log('');
		console.log(`Installed to: ${canonicalPath}`);
		console.log(`Agents: ${installResult.agents.filter((r) => r.success).map((r) => r.agentId).join(', ')}`);
	} catch (err) {
		logger.stopSpinner();

		if (err instanceof SkillApiError) {
			if (err.statusCode === 404) {
				logger.error(`Skill "${slug}" not found`);
				console.log('');
				console.log('Tip: Use @ prefix to add a plugin, e.g.:');
				console.log(`  npx skillstore add @${slug}`);
			} else {
				logger.error(`API error: ${err.message}`);
			}
		} else {
			logger.error('Installation failed', err instanceof Error ? err : undefined);
		}

		process.exit(1);
	}
}

/**
 * Add a plugin (skill collection)
 */
async function addPlugin(slug: string, options: AddOptions): Promise<void> {
	const { targetAgents, isGlobal, skipVerify, dryRun, overwrite } = options;

	// For plugins, use first agent's path as install dir (legacy behavior)
	// TODO: Update plugin download to use multi-agent installation
	const installDir = isGlobal
		? targetAgents[0]?.globalPath || agents['claude-code'].globalPath
		: join(process.cwd(), targetAgents[0]?.projectPath || '.claude/skills');

	const config = getPluginConfig({
		installDir,
		skipVerify,
		dryRun,
	});

	logger.info(`Adding plugin: @${slug}`);
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
				logger.debug('Failed to report installation (non-critical)');
			}

			// Report telemetry for each successfully installed skill
			const successfulSkills = downloadResult.results.filter((r) => r.success && !r.skipped);
			if (successfulSkills.length > 0) {
				// Report in parallel, non-blocking
				Promise.all(successfulSkills.map((r) => reportSkillInstall(config, r.slug))).catch(() => {
					logger.debug('Telemetry reporting failed (non-critical)');
				});
			}
		}

		// Final status
		if (downloadResult.failed > 0) {
			logger.warn(`Installation completed with ${downloadResult.failed} failures`);
			process.exit(1);
		} else if (dryRun) {
			logger.success('Dry run complete - no files were written');
		} else {
			logger.success(`Plugin "@${manifest.plugin.slug}" added successfully!`);
		}
	} catch (err) {
		logger.stopSpinner();

		if (err instanceof PluginApiError) {
			if (err.statusCode === 404) {
				logger.error(`Plugin "@${slug}" not found`);
				console.log('');
				console.log('Tip: Without @ prefix to add a single skill, e.g.:');
				console.log(`  npx skillstore add ${slug}`);
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
}

/**
 * Extract ZIP buffer to directory
 */
async function extractZip(buffer: ArrayBuffer, targetDir: string): Promise<void> {
	// Use fflate for extraction
	const { unzipSync } = await import('fflate');

	const data = new Uint8Array(buffer);
	const unzipped = unzipSync(data);

	for (const [path, content] of Object.entries(unzipped)) {
		// Skip directories (they end with /)
		if (path.endsWith('/')) continue;

		const fullPath = join(targetDir, path);
		await mkdir(dirname(fullPath), { recursive: true });
		await writeFile(fullPath, Buffer.from(content as Uint8Array));
	}
}
