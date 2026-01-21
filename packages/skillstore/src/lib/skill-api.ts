import type { PluginConfig } from './plugin-config.js';

/**
 * Skill API Client
 *
 * Handles HTTP requests for single skill operations.
 */

/** Skill info response */
export interface SkillInfo {
	slug: string;
	name: string;
	description: string | null;
	category: string | null;
	version: string | null;
	author: string | null;
	riskLevel: string | null;
	qualityScore: number | null;
	pluginPath: string | null;
}

/** API Error */
export class SkillApiError extends Error {
	constructor(
		message: string,
		public statusCode: number,
		public code?: string
	) {
		super(message);
		this.name = 'SkillApiError';
	}
}

/**
 * Get the API endpoint for skill info
 */
function getSkillInfoUrl(config: PluginConfig, skillSlug: string): string {
	return `${config.apiBaseUrl}/skills/${skillSlug}`;
}

/**
 * Get the download URL for a skill
 */
function getSkillDownloadUrl(config: PluginConfig, skillSlug: string): string {
	return `${config.apiBaseUrl}/skills/${skillSlug}/download`;
}

/**
 * Fetch skill info/details
 */
export async function fetchSkillInfo(
	config: PluginConfig,
	skillSlug: string
): Promise<SkillInfo> {
	const url = getSkillInfoUrl(config, skillSlug);

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

		throw new SkillApiError(
			errorData.error || `Failed to fetch skill info: ${response.statusText}`,
			response.status,
			errorData.code
		);
	}

	const result = (await response.json()) as { data: SkillInfo };
	return result.data;
}

/**
 * Download skill as ZIP
 */
export async function downloadSkillZip(
	config: PluginConfig,
	skillSlug: string
): Promise<ArrayBuffer> {
	const url = getSkillDownloadUrl(config, skillSlug);

	const response = await fetch(url, {
		method: 'GET',
		signal: AbortSignal.timeout(config.timeout * 2), // Longer timeout for download
	});

	if (!response.ok) {
		throw new SkillApiError(
			`Failed to download skill: ${response.statusText}`,
			response.status
		);
	}

	return await response.arrayBuffer();
}
