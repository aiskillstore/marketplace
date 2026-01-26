import { resolve } from 'node:path';
import { homedir } from 'node:os';

/**
 * Plugin CLI Configuration
 *
 * Manages default settings for plugin installation and API access.
 */

/** Default installation directory for skills (in user's home directory) */
export const DEFAULT_INSTALL_DIR = resolve(homedir(), '.claude/skills');

/** Skillstore API base URL */
export const API_BASE_URL =
	process.env.SKILLSTORE_API_URL || 'https://skillstore.io/api';

/** Request timeout in milliseconds */
export const REQUEST_TIMEOUT = 30_000;

/** Maximum concurrent skill downloads */
export const MAX_CONCURRENT_DOWNLOADS = 5;

export interface PluginConfig {
	/** Base URL for the Skillstore API */
	apiBaseUrl: string;
	/** Directory to install skills into */
	installDir: string;
	/** Request timeout in milliseconds */
	timeout: number;
	/** Maximum concurrent downloads */
	maxConcurrent: number;
	/** Skip manifest signature verification */
	skipVerify: boolean;
	/** Dry run mode - don't write files */
	dryRun: boolean;
}

/**
 * Get plugin configuration from environment and CLI args
 */
export function getPluginConfig(options: Partial<PluginConfig> = {}): PluginConfig {
	// If custom installDir is provided and is relative, resolve against home directory
	let installDir = options.installDir || DEFAULT_INSTALL_DIR;
	if (options.installDir && !options.installDir.startsWith('/') && !options.installDir.startsWith('~')) {
		// Relative path provided - resolve against home directory
		installDir = resolve(homedir(), options.installDir);
	} else if (options.installDir?.startsWith('~')) {
		// Expand ~ to home directory
		installDir = resolve(homedir(), options.installDir.slice(2));
	}

	return {
		apiBaseUrl: options.apiBaseUrl || API_BASE_URL,
		installDir,
		timeout: options.timeout || REQUEST_TIMEOUT,
		maxConcurrent: options.maxConcurrent || MAX_CONCURRENT_DOWNLOADS,
		skipVerify: options.skipVerify || false,
		dryRun: options.dryRun || false,
	};
}

/**
 * Resolve the full path for a skill within the install directory
 */
export function getSkillPath(config: PluginConfig, skillSlug: string): string {
	return resolve(config.installDir, skillSlug);
}

/**
 * Get the API endpoint for a specific plugin manifest
 */
export function getManifestUrl(config: PluginConfig, pluginSlug: string): string {
	return `${config.apiBaseUrl}/plugins/${pluginSlug}/manifest`;
}

/**
 * Get the API endpoint for recording an installation
 */
export function getInstallUrl(config: PluginConfig, pluginSlug: string): string {
	return `${config.apiBaseUrl}/plugins/${pluginSlug}/install`;
}

/**
 * Get the API endpoint for plugin info
 */
export function getPluginInfoUrl(config: PluginConfig, pluginSlug: string): string {
	return `${config.apiBaseUrl}/plugins/${pluginSlug}`;
}

/**
 * Get the API endpoint for plugin listing
 */
export function getPluginListUrl(config: PluginConfig): string {
	return `${config.apiBaseUrl}/plugins`;
}

/**
 * Get the API endpoint for telemetry/effectiveness tracking
 */
export function getTelemetryUrl(config: PluginConfig): string {
	return `${config.apiBaseUrl}/telemetry/effectiveness`;
}
