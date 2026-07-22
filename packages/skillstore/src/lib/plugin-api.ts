import type { PluginConfig } from './plugin-config.js';
import type { PackInstallReport } from './pack-install-truth.js';
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
export interface ManifestSkillArtifactFile {
	path: string;
	url: string;
	sha256?: string;
	bytes?: number;
	mode?: '100644' | '100755';
}

export const MAX_ARTIFACT_FILE_BYTES = 10 * 1024 * 1024;

export interface ManifestSkillArtifactSource {
	type: 'github';
	owner: string;
	repo: string;
	ref: string;
	commit: string;
	path: string;
}

export interface ManifestSkillArtifact {
	type?: string;
	files?: ManifestSkillArtifactFile[];
	sha256?: string;
	source?: ManifestSkillArtifactSource;
}

export interface ManifestSkill {
	slug: string;
	name: string;
	/** Compatibility alias for authorVersion. */
	version?: string | null;
	authorVersion?: string | null;
	skillstoreRevision?: number | null;
	versionStatus?: string;
	treeHash?: string | null;
	contentHash: string;
	downloadUrl: string;
	artifact?: ManifestSkillArtifact;
}

export interface ManifestSignatureInfo {
	algorithm: 'Ed25519';
	keyId: string;
	publicKeyJwk: {
		kty: 'OKP';
		crv: 'Ed25519';
		x: string;
	};
	signedAt: string;
	value: string;
}

export interface PackExecutionDag {
	schemaVersion: 'skillstore.pack-execution-dag/v1';
	workflowDigest: string;
	bindingDigest: string;
	nodes: Array<{
		id: string;
		instruction: string;
		dependsOn: string[];
		artifactIds: string[];
	}>;
	handoffs: Array<{
		from: string;
		to: string;
		artifactIds: string[];
		contract: 'validated-artifacts-only';
	}>;
	skillBindings: Array<{
		canonicalId: string;
		contentHash: string;
		treeHash: string;
		version: string;
		slotIds: string[];
	}>;
	usageGuideMarker: string;
}

export interface PackExecutionBinding {
	schemaVersion: 'skillstore.pack-execution-binding/v1';
	generationId: string;
	evidenceDigest: string;
	executionDag: PackExecutionDag;
	workflowDigest: string;
	bindingDigest: string;
	usageGuideMarker: string;
	marketplaceCommitSha: string;
	skills: PackExecutionDag['skillBindings'];
}

/** Plugin manifest response */
export interface PluginManifest {
	version: '1.0' | '1.1';
	kind?: 'pack';
	plugin: {
		slug: string;
		name: string;
		version: string;
	};
	pack?: {
		slug: string;
		name: string;
		version: string;
		visibility?: 'public' | 'private';
	};
	skills: ManifestSkill[];
	executionBinding?: PackExecutionBinding;
	signature: string | ManifestSignatureInfo;
	generatedAt: string;
	schemaVersion?: '2.0';
	signed?: unknown;
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
	type?: 'curated' | 'scenario' | 'user';
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

type JsonObject = Record<string, unknown>;

function isJsonObject(value: unknown): value is JsonObject {
	return !!value && typeof value === 'object' && !Array.isArray(value);
}

function normalizeManifest(rawManifest: unknown): PluginManifest {
	if (!isJsonObject(rawManifest)) {
		return rawManifest as PluginManifest;
	}

	const manifest = { ...rawManifest } as JsonObject;
	const pack = isJsonObject(manifest.pack) ? manifest.pack : null;
	const signed = isJsonObject(manifest.signed) ? manifest.signed : null;
	const signedPack = signed && isJsonObject(signed.pack) ? signed.pack : null;
	const signature = isJsonObject(manifest.signature) ? manifest.signature : null;
	const hasEd25519Envelope = signature?.algorithm === 'Ed25519' && !!signed;
	const signedVersion = signed?.version === '1.0' || signed?.version === '1.1'
		? signed.version
		: null;
	const sourcePack = hasEd25519Envelope ? signedPack || pack : pack || signedPack;

	if ((hasEd25519Envelope || !manifest.plugin) && sourcePack?.slug && sourcePack.name) {
		manifest.plugin = {
			slug: String(sourcePack.slug),
			name: String(sourcePack.name),
			version: String(sourcePack.version || '1.0.0'),
		};
	}

	if ((hasEd25519Envelope || !manifest.pack) && sourcePack?.slug && sourcePack.name) {
		manifest.pack = {
			slug: String(sourcePack.slug),
			name: String(sourcePack.name),
			version: String(sourcePack.version || '1.0.0'),
			visibility: sourcePack.visibility,
		};
	}

	if (hasEd25519Envelope && signed && Array.isArray(signed.skills)) {
		manifest.skills = signed.skills;
	} else if (!manifest.skills && signed && Array.isArray(signed.skills)) {
		manifest.skills = signed.skills;
	}

	if (hasEd25519Envelope) {
		manifest.executionBinding = signed?.executionBinding;
	} else if (!manifest.executionBinding && signed?.executionBinding) {
		manifest.executionBinding = signed.executionBinding;
	}

	if (hasEd25519Envelope && signedVersion) {
		manifest.version = signedVersion;
	} else if (!manifest.version) {
		manifest.version = signedVersion || '1.0';
	}

	if (hasEd25519Envelope && signed?.generatedAt) {
		manifest.generatedAt = signed.generatedAt;
	} else if (!manifest.generatedAt && signed?.generatedAt) {
		manifest.generatedAt = signed.generatedAt;
	}

	return manifest as unknown as PluginManifest;
}

function normalizePluginItem(item: JsonObject): JsonObject {
	const normalized = { ...item };
	const type = normalized.pluginType ?? normalized.packType ?? normalized.type;
	if (type && !normalized.pluginType) normalized.pluginType = type;
	if (!normalized.pricing) normalized.pricing = 'free';
	if (normalized.priceCents === undefined) normalized.priceCents = 0;
	if (!normalized.currency) normalized.currency = 'USD';
	return normalized;
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

	return normalizeManifest(await response.json());
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

	const result = (await response.json()) as { data: JsonObject };
	return normalizePluginItem(result.data) as unknown as PluginInfo;
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

	const result = (await response.json()) as { data: JsonObject[]; pagination: PluginListResponse['pagination'] };
	return {
		...result,
		data: (result.data || []).map((item) => normalizePluginItem(item)) as unknown as PluginListItem[],
	};
}

/**
 * Report installation to the API
 */
export async function reportInstallation(
	config: PluginConfig,
	pluginSlug: string,
	method: 'npm' | 'manual' | 'cli' = 'cli'
): Promise<InstallReportResponse> {
	return postInstallation(config, pluginSlug, { method }, config.timeout);
}

/** Report the final durable result of one CLI Pack install attempt. */
export async function reportPackInstallation(
	config: PluginConfig,
	pluginSlug: string,
	report: PackInstallReport
): Promise<InstallReportResponse> {
	return postInstallation(config, pluginSlug, report, Math.min(config.timeout, 5000));
}

async function postInstallation(
	config: PluginConfig,
	pluginSlug: string,
	body: { method: 'npm' | 'manual' | 'cli' } | PackInstallReport,
	timeout: number
): Promise<InstallReportResponse> {
	const url = getInstallUrl(config, pluginSlug);

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Accept: 'application/json',
		},
		body: JSON.stringify(body),
		signal: AbortSignal.timeout(timeout),
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
	const bytes = await downloadSkillFile(config, downloadUrl);
	return new TextDecoder().decode(bytes);
}

/**
 * Download a skill artifact file from the API.
 */
export async function downloadSkillFile(
	config: PluginConfig,
	downloadUrl: string,
	limits: {
		maxBytes?: number;
		expectedBytes?: number;
		onBytes?: (bytes: number) => void;
		approvedExternalUrl?: string;
	} = {}
): Promise<Uint8Array> {
	const apiUrl = new URL(config.apiBaseUrl);
	const fullUrl = new URL(downloadUrl, apiUrl.origin);
	const isLoopback = fullUrl.hostname === 'localhost'
		|| fullUrl.hostname === '127.0.0.1'
		|| fullUrl.hostname === '[::1]';
	const approvedExternalUrl = limits.approvedExternalUrl
		? new URL(limits.approvedExternalUrl)
		: null;
	const isApprovedExternal = approvedExternalUrl?.href === fullUrl.href
		&& fullUrl.origin === 'https://raw.githubusercontent.com'
		&& fullUrl.protocol === 'https:'
		&& !fullUrl.username
		&& !fullUrl.password;
	const isApprovedSameOrigin = fullUrl.origin === apiUrl.origin
		&& (fullUrl.protocol === 'https:' || isLoopback);
	if (!isApprovedSameOrigin && !isApprovedExternal) {
		throw new Error(`Refusing artifact URL outside the configured Skillstore origin: ${downloadUrl}`);
	}
	const maxBytes = limits.maxBytes ?? MAX_ARTIFACT_FILE_BYTES;
	if (!Number.isSafeInteger(maxBytes) || maxBytes < 0) {
		throw new Error('Invalid artifact size limit');
	}
	if (limits.expectedBytes !== undefined && (!Number.isSafeInteger(limits.expectedBytes) || limits.expectedBytes < 0)) {
		throw new Error('Invalid signed artifact byte count');
	}
	const controller = new AbortController();
	const signal = AbortSignal.any([AbortSignal.timeout(config.timeout), controller.signal]);

	const response = await fetch(fullUrl, {
		method: 'GET',
		redirect: 'error',
		signal,
	});

	if (!response.ok) {
		throw new PluginApiError(
			`Failed to download skill: ${response.statusText}`,
			response.status
		);
	}

	const contentLength = response.headers.get('content-length');
	if (contentLength !== null) {
		if (!/^\d+$/.test(contentLength)) {
			controller.abort();
			throw new Error('Invalid artifact Content-Length');
		}
		const length = Number(contentLength);
		const contentEncoding = response.headers.get('content-encoding')?.trim().toLowerCase();
		const hasEncodedRepresentation = !!contentEncoding && contentEncoding !== 'identity';
		if (!Number.isSafeInteger(length) || (!hasEncodedRepresentation && length > maxBytes)) {
			controller.abort();
			throw new Error(`Artifact exceeds ${maxBytes} byte limit`);
		}
		if (!hasEncodedRepresentation && limits.expectedBytes !== undefined && length !== limits.expectedBytes) {
			controller.abort();
			throw new Error(`Artifact byte count does not match signed manifest: expected ${limits.expectedBytes}, got ${length}`);
		}
	}
	if (!response.body) {
		controller.abort();
		throw new Error('Artifact response has no readable body');
	}

	const reader = response.body.getReader();
	const chunks: Uint8Array[] = [];
	let total = 0;
	try {
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			total += value.byteLength;
			if (total > maxBytes) {
				controller.abort();
				await reader.cancel('artifact exceeds byte limit');
				throw new Error(`Artifact exceeds ${maxBytes} byte limit`);
			}
			try {
				limits.onBytes?.(value.byteLength);
			} catch (error) {
				controller.abort();
				await reader.cancel('Pack artifact budget exceeded');
				throw error;
			}
			chunks.push(value);
		}
	} finally {
		reader.releaseLock();
	}
	if (limits.expectedBytes !== undefined && total !== limits.expectedBytes) {
		throw new Error(`Artifact byte count does not match signed manifest: expected ${limits.expectedBytes}, got ${total}`);
	}
	const bytes = new Uint8Array(total);
	let offset = 0;
	for (const chunk of chunks) {
		bytes.set(chunk, offset);
		offset += chunk.byteLength;
	}
	return bytes;
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
