import type { PluginConfig } from './plugin-config.js';
import type { ManifestSignatureInfo } from './plugin-api.js';

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

/** Skill manifest for verification */
export interface SkillZipArtifact {
	type?: 'skill-zip' | string;
	url?: string;
	mediaType?: string;
	sha256?: string;
}

export interface SkillManifest {
	version: '1.0';
	kind?: 'skill';
	schemaVersion?: '2.0';
	skill: {
		slug: string;
		name: string;
		version: string;
		author?: string;
		zipHash?: string;
	};
	artifact?: SkillZipArtifact;
	downloadUrl?: string;
	signature: string | ManifestSignatureInfo;
	generatedAt: string;
	signed?: {
		kind?: 'skill';
		version?: '1.0';
		generatedAt?: string;
		skill?: SkillManifest['skill'];
		artifact?: SkillZipArtifact;
	};
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

function getSignedSkillArtifact(manifest: SkillManifest): SkillZipArtifact | undefined {
	if (manifest.signed?.kind === 'skill') {
		return manifest.signed.artifact;
	}
	return undefined;
}

function resolveDownloadUrl(config: PluginConfig, url: string): string {
	try {
		return new URL(url).toString();
	} catch {
		return new URL(url, config.apiBaseUrl).toString();
	}
}

/**
 * Get the expected ZIP SHA-256 from either the legacy or canonical manifest.
 */
export function getSkillZipHash(manifest: SkillManifest): string | undefined {
	return getSignedSkillArtifact(manifest)?.sha256
		|| manifest.artifact?.sha256
		|| manifest.skill?.zipHash;
}

/**
 * Get the ZIP URL from a skill manifest, falling back to the conventional API path.
 */
export function getSkillDownloadUrlFromManifest(
	config: PluginConfig,
	manifest: SkillManifest,
	skillSlug: string
): string {
	const manifestUrl = getSignedSkillArtifact(manifest)?.url
		|| manifest.artifact?.url
		|| manifest.downloadUrl;

	return manifestUrl
		? resolveDownloadUrl(config, manifestUrl)
		: getSkillDownloadUrl(config, skillSlug);
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
 * Get the manifest URL for a skill
 */
function getSkillManifestUrl(config: PluginConfig, skillSlug: string): string {
	return `${config.apiBaseUrl}/skills/${skillSlug}/manifest`;
}

/**
 * Fetch skill manifest for verification
 */
export async function fetchSkillManifest(
	config: PluginConfig,
	skillSlug: string
): Promise<SkillManifest> {
	const url = getSkillManifestUrl(config, skillSlug);

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
			errorData.error || `Failed to fetch manifest: ${response.statusText}`,
			response.status,
			errorData.code
		);
	}

	return (await response.json()) as SkillManifest;
}

/**
 * Download skill as ZIP
 */
export async function downloadSkillZip(
	config: PluginConfig,
	skillSlug: string,
	manifest?: SkillManifest
): Promise<ArrayBuffer> {
	const url = manifest
		? getSkillDownloadUrlFromManifest(config, manifest, skillSlug)
		: getSkillDownloadUrl(config, skillSlug);

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
