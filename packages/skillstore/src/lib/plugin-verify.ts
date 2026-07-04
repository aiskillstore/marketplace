import { createHmac, createHash, timingSafeEqual as cryptoTimingSafeEqual, webcrypto } from 'node:crypto';
import type { ManifestSignatureInfo, PluginManifest } from './plugin-api.js';
import { getSkillZipHash, type SkillManifest } from './skill-api.js';

/**
 * Plugin Manifest Verification
 *
 * Verifies HMAC-SHA256 signatures on plugin manifests to ensure integrity.
 */

/** Verification result */
export interface VerifyResult {
	valid: boolean;
	error?: string;
}

/**
 * Built-in verification key for skillstore.io manifests
 * This key is used to verify HMAC-SHA256 signatures on plugin manifests
 */
const DEFAULT_VERIFICATION_KEY = '3d2b8f367783854cbdb6f81c9a39d586201c8d898ec8737bfa464162a9177943';

/**
 * Get the signing key for manifest verification
 * Uses built-in key by default, can be overridden via environment variable
 */
export function getVerificationKey(): string {
	return process.env.SKILLSTORE_VERIFY_KEY || DEFAULT_VERIFICATION_KEY;
}

/**
 * Verify manifest signature using HMAC-SHA256
 *
 * The signature is computed over the manifest JSON without the signature field.
 */
export function verifyManifestSignature(
	manifest: PluginManifest,
	key: string
): VerifyResult {
	try {
		// Extract signature and create unsigned manifest
		const { signature, ...unsignedManifest } = manifest;

		if (!signature) {
			return { valid: false, error: 'Manifest has no signature' };
		}

		if (typeof signature !== 'string') {
			return { valid: false, error: 'Manifest uses a non-HMAC signature' };
		}

		// Compute expected signature (matching server-side implementation)
		const dataToSign = JSON.stringify(unsignedManifest, null, 0);
		const expectedSignature = createHmac('sha256', key)
			.update(dataToSign)
			.digest('hex');

		// Constant-time comparison to prevent timing attacks
		const valid = timingSafeEqual(signature, expectedSignature);

		if (!valid) {
			return { valid: false, error: 'Signature verification failed' };
		}

		return { valid: true };
	} catch (err) {
		return {
			valid: false,
			error: `Verification error: ${err instanceof Error ? err.message : 'Unknown error'}`,
		};
	}
}

function normalizeForJson(value: unknown): unknown {
	if (Array.isArray(value)) {
		return value.map(normalizeForJson);
	}

	if (value && typeof value === 'object') {
		const entries = Object.entries(value as Record<string, unknown>)
			.filter(([, entryValue]) => entryValue !== undefined)
			.sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
		return Object.fromEntries(entries.map(([key, entryValue]) => [key, normalizeForJson(entryValue)]));
	}

	return value;
}

function canonicalJson(value: unknown): string {
	return JSON.stringify(normalizeForJson(value));
}

function isManifestSignatureInfo(value: unknown): value is ManifestSignatureInfo {
	return !!value
		&& typeof value === 'object'
		&& (value as ManifestSignatureInfo).algorithm === 'Ed25519'
		&& !!(value as ManifestSignatureInfo).value
		&& (value as ManifestSignatureInfo).publicKeyJwk?.kty === 'OKP'
		&& (value as ManifestSignatureInfo).publicKeyJwk?.crv === 'Ed25519'
		&& !!(value as ManifestSignatureInfo).publicKeyJwk?.x;
}

function decodeBase64Url(value: string): ArrayBuffer {
	const padded = value.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - value.length % 4) % 4);
	const buffer = Buffer.from(padded, 'base64');
	return buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength) as ArrayBuffer;
}

async function verifyEd25519Envelope(manifest: {
	signature: unknown;
	signed?: unknown;
}): Promise<VerifyResult> {
	try {
		if (!isManifestSignatureInfo(manifest.signature)) {
			return { valid: false, error: 'Invalid Ed25519 signature metadata' };
		}

		if (!manifest.signed || typeof manifest.signed !== 'object') {
			return { valid: false, error: 'Manifest is missing signed payload' };
		}

		const subtle = globalThis.crypto?.subtle || webcrypto.subtle;
		const verifyKey = await subtle.importKey(
			'jwk',
			manifest.signature.publicKeyJwk,
			{ name: 'Ed25519' },
			false,
			['verify']
		);

		const valid = await subtle.verify(
			{ name: 'Ed25519' },
			verifyKey,
			decodeBase64Url(manifest.signature.value),
			new TextEncoder().encode(canonicalJson(manifest.signed))
		);

		if (!valid) {
			return { valid: false, error: 'Signature verification failed' };
		}

		return { valid: true };
	} catch (err) {
		return {
			valid: false,
			error: `Verification error: ${err instanceof Error ? err.message : 'Unknown error'}`,
		};
	}
}

/**
 * Constant-time string comparison to prevent timing attacks
 */
function timingSafeEqual(a: string, b: string): boolean {
	if (a.length !== b.length) {
		return false;
	}

	const bufA = Buffer.from(a, 'utf8');
	const bufB = Buffer.from(b, 'utf8');

	return cryptoTimingSafeEqual(bufA, bufB);
}

/**
 * Verify skill content hash
 *
 * Ensures downloaded skill content matches the hash in the manifest.
 */
export function verifyContentHash(content: string, expectedHash: string): boolean {
	const actualHash = createHash('sha256').update(content).digest('hex');

	// Content hash might be truncated, compare common length
	const compareLength = Math.min(actualHash.length, expectedHash.length);
	return actualHash.substring(0, compareLength) === expectedHash.substring(0, compareLength);
}

/**
 * Verify entire manifest (signature + metadata)
 */
export async function verifyManifest(
	manifest: PluginManifest,
	options: { skipSignature?: boolean } = {}
): Promise<VerifyResult> {
	// Validate manifest structure
	if (!manifest.version || manifest.version !== '1.0') {
		return { valid: false, error: 'Unsupported manifest version' };
	}

	if (!manifest.plugin?.slug && !manifest.pack?.slug) {
		return { valid: false, error: 'Missing plugin slug in manifest' };
	}

	if (!Array.isArray(manifest.skills) || manifest.skills.length === 0) {
		return { valid: false, error: 'Manifest contains no skills' };
	}

	// Validate skill entries
	for (const skill of manifest.skills) {
		if (!skill.slug || !skill.downloadUrl) {
			return { valid: false, error: `Invalid skill entry: ${skill.slug || 'unknown'}` };
		}
	}

	// Verify signature unless skipped
	if (!options.skipSignature) {
		const signatureResult = isManifestSignatureInfo(manifest.signature)
			? await verifyEd25519Envelope(manifest)
			: verifyManifestSignature(manifest, getVerificationKey());
		if (!signatureResult.valid) {
			return signatureResult;
		}
	}

	return { valid: true };
}

/**
 * Verify skill manifest signature using HMAC-SHA256
 *
 * Similar to verifyManifestSignature but for single skill manifests.
 */
export function verifySkillManifestSignature(
	manifest: SkillManifest,
	key: string
): VerifyResult {
	try {
		// Extract signature and create unsigned manifest
		const { signature, ...unsignedManifest } = manifest;

		if (!signature) {
			return { valid: false, error: 'Manifest has no signature' };
		}

		if (typeof signature !== 'string') {
			return { valid: false, error: 'Manifest uses a non-HMAC signature' };
		}

		// Compute expected signature (matching server-side implementation)
		const dataToSign = JSON.stringify(unsignedManifest, null, 0);
		const expectedSignature = createHmac('sha256', key)
			.update(dataToSign)
			.digest('hex');

		// Constant-time comparison to prevent timing attacks
		const valid = timingSafeEqual(signature, expectedSignature);

		if (!valid) {
			return { valid: false, error: 'Signature verification failed' };
		}

		return { valid: true };
	} catch (err) {
		return {
			valid: false,
			error: `Verification error: ${err instanceof Error ? err.message : 'Unknown error'}`,
		};
	}
}

/**
 * Verify skill manifest (signature + structure)
 */
export async function verifySkillManifest(
	manifest: SkillManifest,
	options: { skipSignature?: boolean } = {}
): Promise<VerifyResult> {
	// Validate manifest structure
	if (!manifest.version || manifest.version !== '1.0') {
		return { valid: false, error: 'Unsupported manifest version' };
	}

	if (!manifest.skill?.slug) {
		return { valid: false, error: 'Missing skill slug in manifest' };
	}

	if (!getSkillZipHash(manifest)) {
		return { valid: false, error: 'Missing zipHash or artifact.sha256 in manifest' };
	}

	// Verify signature unless skipped
	if (!options.skipSignature) {
		const key = getVerificationKey();
		const signatureResult = isManifestSignatureInfo(manifest.signature)
			? await verifyEd25519Envelope(manifest)
			: verifySkillManifestSignature(manifest, key);
		if (!signatureResult.valid) {
			return signatureResult;
		}
	}

	return { valid: true };
}

/**
 * Verify ZIP content hash
 *
 * Computes SHA-256 hash of the ZIP buffer and compares with expected hash.
 */
export function verifyZipHash(zipBuffer: ArrayBuffer, expectedHash: string): boolean {
	const hash = createHash('sha256')
		.update(Buffer.from(zipBuffer))
		.digest('hex');

	return hash === expectedHash;
}
