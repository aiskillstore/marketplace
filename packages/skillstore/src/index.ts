/**
 * Skillstore SDK
 *
 * AI Skills marketplace for Claude Code
 */

// Re-export plugin API for programmatic usage
export {
	fetchManifest,
	fetchPluginInfo,
	fetchPluginList,
	downloadSkill,
	reportInstallation,
	PluginApiError,
	type PluginManifest,
	type ManifestSkill,
	type PluginInfo,
	type PluginListItem,
	type PluginListResponse,
	type InstallReportResponse,
} from './lib/plugin-api.js';

// Re-export skill API for programmatic usage
export {
	fetchSkillInfo,
	downloadSkillZip,
	SkillApiError,
	type SkillInfo,
} from './lib/skill-api.js';

export {
	getPluginConfig,
	type PluginConfig,
	DEFAULT_INSTALL_DIR,
	API_BASE_URL,
} from './lib/plugin-config.js';

export {
	verifyManifest,
	verifyContentHash,
	type VerifyResult,
} from './lib/plugin-verify.js';

export {
	downloadAllSkills,
	printDownloadSummary,
	type SkillDownloadResult,
	type DownloadSummary,
} from './lib/plugin-download.js';
