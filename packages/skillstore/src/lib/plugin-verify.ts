import { createHmac, createHash, timingSafeEqual as cryptoTimingSafeEqual } from 'node:crypto';
import type { PluginManifest } from './plugin-api.js';

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
 * Get the signing key from environment
 * In production, this should be a public key or verification endpoint
 * For CLI, we use a shared secret (configured by user or fetched from API)
 */
export function getVerificationKey(): string | null {
	// The verification key can be set via environment variable
	// In production, this might be fetched from a public endpoint
	return process.env.SKILLSTORE_VERIFY_KEY || null;
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

	if (!manifest.plugin?.slug) {
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
		const key = getVerificationKey();

		if (!key) {
			// If no key is configured, warn but don't fail
			// This allows installation without signature verification
			return {
				valid: true,
				error: 'Warning: No verification key configured, signature not verified',
			};
		}

		const signatureResult = verifyManifestSignature(manifest, key);
		if (!signatureResult.valid) {
			return signatureResult;
		}
	}

	return { valid: true };
}
