import type { PluginConfig } from './plugin-config.js';
import {
	getManifestUrl,
	getInstallUrl,
	getPluginInfoUrl,
	getPluginListUrl,
	getTelemetryUrl,
} from './plugin-config.js';

/**
 * Plugin API Client
 *
 * Handles all HTTP requests to the Skillstore API for plugin operations.
 */

/** Manifest skill entry */
export interface ManifestSkill {
	slug: string;
	name: string;
	contentHash: string;
	downloadUrl: string;
}

/** Plugin manifest response */
export interface PluginManifest {
	version: '1.0';
	plugin: {
		slug: string;
		name: string;
		version: string;
	};
	skills: ManifestSkill[];
	signature: string;
	generatedAt: string;
}

/** Plugin info response */
export interface PluginInfo {
	id: string;
	slug: string;
	name: string;
	description: string | null;
	pluginType: 'curated' | 'scenario' | 'user';
	visibility: 'public' | 'private';
	pricing: 'free' | 'paid';
	skillCount: number;
	installCount: number;
	priceCents: number;
	currency: string;
	scenarioTags: string[] | null;
	skills: Array<{
		slug: string;
		name: string;
		description: string | null;
		category: string | null;
		riskLevel: string | null;
		qualityScore: number | null;
	}>;
}

/** Plugin list item */
export interface PluginListItem {
	id: string;
	slug: string;
	name: string;
	description: string | null;
	pluginType: 'curated' | 'scenario' | 'user';
	visibility: 'public' | 'private';
	pricing: 'free' | 'paid';
	skillCount: number;
	installCount: number;
	score: number | null;
}

/** Plugin list response */
export interface PluginListResponse {
	data: PluginListItem[];
	pagination: {
		page: number;
		limit: number;
		total: number;
		totalPages: number;
	};
}

/** Install response */
export interface InstallReportResponse {
	success: boolean;
	installationId?: string;
	message?: string;
	duplicate?: boolean;
	error?: string;
}

/** API Error */
export class PluginApiError extends Error {
	constructor(
		message: string,
		public statusCode: number,
		public code?: string
	) {
		super(message);
		this.name = 'PluginApiError';
	}
}

/**
 * Fetch plugin manifest for installation
 */
export async function fetchManifest(
	config: PluginConfig,
	pluginSlug: string
): Promise<PluginManifest> {
	const url = getManifestUrl(config, pluginSlug);

	const response = await fetch(url, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
		},
		signal: AbortSignal.timeout(config.timeout),
	});

	if (!response.ok) {
		const errorText = await response.text().catch(() => 'Unknown error');
		let errorData: { error?: string; code?: string } = {};
		try {
			errorData = JSON.parse(errorText);
		} catch {
			// Not JSON
		}

		throw new PluginApiError(
			errorData.error || `Failed to fetch manifest: ${response.statusText}`,
			response.status,
			errorData.code
		);
	}

	const manifest = (await response.json()) as PluginManifest;
	return manifest;
}

/**
 * Fetch plugin info/details
 */
export async function fetchPluginInfo(
	config: PluginConfig,
	pluginSlug: string
): Promise<PluginInfo> {
	const url = getPluginInfoUrl(config, pluginSlug);

	const response = await fetch(url, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
		},
		signal: AbortSignal.timeout(config.timeout),
	});

	if (!response.ok) {
		const errorText = await response.text().catch(() => 'Unknown error');
		let errorData: { error?: string; code?: string } = {};
		try {
			errorData = JSON.parse(errorText);
		} catch {
			// Not JSON
		}

		throw new PluginApiError(
			errorData.error || `Failed to fetch plugin info: ${response.statusText}`,
			response.status,
			errorData.code
		);
	}

	const result = (await response.json()) as { data: PluginInfo };
	return result.data;
}

/**
 * Fetch plugin list
 */
export async function fetchPluginList(
	config: PluginConfig,
	options: {
		type?: 'curated' | 'scenario' | 'user';
		pricing?: 'free' | 'paid';
		limit?: number;
		page?: number;
	} = {}
): Promise<PluginListResponse> {
	const url = new URL(getPluginListUrl(config));

	if (options.type) url.searchParams.set('type', options.type);
	if (options.pricing) url.searchParams.set('pricing', options.pricing);
	if (options.limit) url.searchParams.set('limit', String(options.limit));
	if (options.page) url.searchParams.set('page', String(options.page));

	const response = await fetch(url.toString(), {
		method: 'GET',
		headers: {
			Accept: 'application/json',
		},
		signal: AbortSignal.timeout(config.timeout),
	});

	if (!response.ok) {
		throw new PluginApiError(
			`Failed to fetch plugin list: ${response.statusText}`,
			response.status
		);
	}

	return (await response.json()) as PluginListResponse;
}

/**
 * Report installation to the API
 */
export async function reportInstallation(
	config: PluginConfig,
	pluginSlug: string,
	method: 'npm' | 'manual' | 'cli' = 'cli'
): Promise<InstallReportResponse> {
	const url = getInstallUrl(config, pluginSlug);

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Accept: 'application/json',
		},
		body: JSON.stringify({ method }),
		signal: AbortSignal.timeout(config.timeout),
	});

	// Accept both success and rate-limited responses
	const result = (await response.json()) as InstallReportResponse;
	return result;
}

/**
 * Download skill content from the API
 */
export async function downloadSkill(
	config: PluginConfig,
	downloadUrl: string
): Promise<string> {
	// downloadUrl is relative, construct full URL
	const fullUrl = downloadUrl.startsWith('http')
		? downloadUrl
		: `${config.apiBaseUrl.replace('/api', '')}${downloadUrl}`;

	const response = await fetch(fullUrl, {
		method: 'GET',
		signal: AbortSignal.timeout(config.timeout),
	});

	if (!response.ok) {
		throw new PluginApiError(
			`Failed to download skill: ${response.statusText}`,
			response.status
		);
	}

	return await response.text();
}

/**
 * Telemetry event types for effectiveness tracking
 */
export type TelemetryEventType = 'invocation' | 'completion' | 'error' | 'feedback';

/**
 * Telemetry event payload
 */
export interface TelemetryEvent {
	skill_slug: string;
	event_type: TelemetryEventType;
	session_id?: string;
	client_id?: string;
	success?: boolean;
	iteration_count?: number;
	duration_ms?: number;
	error_type?: string;
	error_message?: string;
	user_rating?: number;
	feedback_type?: 'thumbs_up' | 'thumbs_down' | 'star_rating';
	tool_name?: 'claude_code' | 'codex' | 'claude' | 'other';
	tool_version?: string;
}

/**
 * Telemetry response
 */
export interface TelemetryResponse {
	success: boolean;
	event_id?: string;
	message?: string;
	error?: string;
}

/**
 * Report skill telemetry event (effectiveness tracking)
 *
 * Used to track skill usage for quality scoring.
 * Non-blocking - failures don't interrupt normal operation.
 */
export async function reportSkillTelemetry(
	config: PluginConfig,
	event: TelemetryEvent
): Promise<TelemetryResponse> {
	const url = getTelemetryUrl(config);

	try {
		const response = await fetch(url, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				Accept: 'application/json',
			},
			body: JSON.stringify(event),
			signal: AbortSignal.timeout(5000), // Short timeout for non-critical telemetry
		});

		if (!response.ok) {
			// Non-critical - return error but don't throw
			return {
				success: false,
				error: `HTTP ${response.status}: ${response.statusText}`,
			};
		}

		return (await response.json()) as TelemetryResponse;
	} catch (err) {
		// Non-critical - return error but don't throw
		return {
			success: false,
			error: err instanceof Error ? err.message : 'Unknown error',
		};
	}
}

/**
 * Report skill installation event
 *
 * Tracks when a skill is installed via CLI.
 */
export async function reportSkillInstall(
	config: PluginConfig,
	skillSlug: string,
	toolName: 'claude_code' | 'codex' | 'claude' | 'other' = 'claude_code'
): Promise<TelemetryResponse> {
	return reportSkillTelemetry(config, {
		skill_slug: skillSlug,
		event_type: 'invocation',
		tool_name: toolName,
		tool_version: '1.0.0', // CLI version
	});
}
