import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createHmac, createHash } from 'node:crypto';
import {
	getVerificationKey,
	verifyManifestSignature,
	verifyContentHash,
	verifyManifest,
	type VerifyResult,
} from '../src/lib/plugin-verify.js';
import type { PluginManifest } from '../src/lib/plugin-api.js';

describe('plugin-verify', () => {
	describe('getVerificationKey', () => {
		const originalKey = process.env.SKILLSTORE_VERIFY_KEY;

		afterEach(() => {
			if (originalKey === undefined) {
				delete process.env.SKILLSTORE_VERIFY_KEY;
			} else {
				process.env.SKILLSTORE_VERIFY_KEY = originalKey;
			}
		});

		it('should return built-in key when env variable is not set', () => {
			delete process.env.SKILLSTORE_VERIFY_KEY;
			const key = getVerificationKey();
			expect(key).toBe('3d2b8f367783854cbdb6f81c9a39d586201c8d898ec8737bfa464162a9177943');
		});

		it('should return key from env variable when set', () => {
			process.env.SKILLSTORE_VERIFY_KEY = 'custom-override-key';
			expect(getVerificationKey()).toBe('custom-override-key');
		});

		it('should return built-in key for empty string (falsy)', () => {
			// The implementation uses || which treats empty string as falsy
			process.env.SKILLSTORE_VERIFY_KEY = '';
			expect(getVerificationKey()).toBe('3d2b8f367783854cbdb6f81c9a39d586201c8d898ec8737bfa464162a9177943');
		});
	});

	describe('verifyManifestSignature', () => {
		const secretKey = 'test-secret-key-123';

		function createSignedManifest(manifest: Omit<PluginManifest, 'signature'>): PluginManifest {
			const dataToSign = JSON.stringify(manifest, null, 0);
			const signature = createHmac('sha256', secretKey).update(dataToSign).digest('hex');
			return { ...manifest, signature };
		}

		const validManifest: Omit<PluginManifest, 'signature'> = {
			version: '1.0',
			plugin: { slug: 'test-plugin', name: 'Test Plugin', version: '1.0.0' },
			skills: [
				{ slug: 'skill-1', name: 'Skill 1', contentHash: 'abc123', downloadUrl: '/download/1' },
			],
			generatedAt: '2024-01-01T00:00:00Z',
		};

		it('should verify valid signature', () => {
			const manifest = createSignedManifest(validManifest);
			const result = verifyManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(true);
			expect(result.error).toBeUndefined();
		});

		it('should reject manifest without signature', () => {
			const manifest = { ...validManifest, signature: undefined } as unknown as PluginManifest;
			const result = verifyManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Manifest has no signature');
		});

		it('should reject manifest with empty signature', () => {
			const manifest = { ...validManifest, signature: '' } as PluginManifest;
			const result = verifyManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Manifest has no signature');
		});

		it('should reject manifest with wrong signature', () => {
			const manifest = createSignedManifest(validManifest);
			manifest.signature = 'invalid-signature';

			const result = verifyManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});

		it('should reject manifest with tampered data', () => {
			const manifest = createSignedManifest(validManifest);
			manifest.plugin.name = 'Tampered Name';

			const result = verifyManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});

		it('should reject manifest signed with different key', () => {
			const manifest = createSignedManifest(validManifest);

			const result = verifyManifestSignature(manifest, 'different-key');

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});

		it('should be timing-safe against signature length attacks', () => {
			const manifest = createSignedManifest(validManifest);

			// Test with different length signatures - should still fail with same error
			const shortSignature = 'abc';
			manifest.signature = shortSignature;
			const result1 = verifyManifestSignature(manifest, secretKey);

			const longSignature = manifest.signature + 'extra';
			manifest.signature = longSignature;
			const result2 = verifyManifestSignature(manifest, secretKey);

			expect(result1.valid).toBe(false);
			expect(result2.valid).toBe(false);
		});
	});

	describe('verifyContentHash', () => {
		it('should verify matching content hash', () => {
			const content = 'Hello, World!';
			const expectedHash = createHash('sha256').update(content).digest('hex');

			expect(verifyContentHash(content, expectedHash)).toBe(true);
		});

		it('should reject non-matching content hash', () => {
			const content = 'Hello, World!';
			const wrongHash = 'deadbeef1234567890';

			expect(verifyContentHash(content, wrongHash)).toBe(false);
		});

		it('should handle truncated hash comparison', () => {
			const content = 'Test content';
			const fullHash = createHash('sha256').update(content).digest('hex');
			const truncatedHash = fullHash.substring(0, 16);

			// Should match when comparing common length
			expect(verifyContentHash(content, truncatedHash)).toBe(true);
		});

		it('should handle empty content', () => {
			const content = '';
			const expectedHash = createHash('sha256').update(content).digest('hex');

			expect(verifyContentHash(content, expectedHash)).toBe(true);
		});

		it('should handle unicode content', () => {
			const content = '你好世界 🌍';
			const expectedHash = createHash('sha256').update(content).digest('hex');

			expect(verifyContentHash(content, expectedHash)).toBe(true);
		});

		it('should be case-sensitive for hash comparison', () => {
			const content = 'Test';
			const hash = createHash('sha256').update(content).digest('hex');
			const uppercaseHash = hash.toUpperCase();

			// SHA256 hex is lowercase, uppercase should fail
			expect(verifyContentHash(content, uppercaseHash)).toBe(false);
		});
	});

	describe('verifyManifest', () => {
		const secretKey = 'test-secret-key';

		function createValidManifest(overrides = {}): PluginManifest {
			const base = {
				version: '1.0' as const,
				plugin: { slug: 'test-plugin', name: 'Test Plugin', version: '1.0.0' },
				skills: [
					{ slug: 'skill-1', name: 'Skill 1', contentHash: 'abc', downloadUrl: '/download/1' },
				],
				generatedAt: '2024-01-01T00:00:00Z',
				...overrides,
			};

			const dataToSign = JSON.stringify(base, null, 0);
			const signature = createHmac('sha256', secretKey).update(dataToSign).digest('hex');
			return { ...base, signature };
		}

		beforeEach(() => {
			process.env.SKILLSTORE_VERIFY_KEY = secretKey;
		});

		afterEach(() => {
			delete process.env.SKILLSTORE_VERIFY_KEY;
		});

		it('should validate a complete manifest', async () => {
			const manifest = createValidManifest();
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(true);
		});

		it('should reject unsupported manifest version', async () => {
			const manifest = createValidManifest({ version: '2.0' });
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Unsupported manifest version');
		});

		it('should reject missing manifest version', async () => {
			const manifest = createValidManifest({ version: undefined });
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Unsupported manifest version');
		});

		it('should reject missing plugin slug', async () => {
			const manifest = createValidManifest({
				plugin: { name: 'Test', version: '1.0.0' },
			});
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Missing plugin slug in manifest');
		});

		it('should reject missing plugin object', async () => {
			const manifest = createValidManifest({ plugin: null });
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Missing plugin slug in manifest');
		});

		it('should reject empty skills array', async () => {
			const manifest = createValidManifest({ skills: [] });
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Manifest contains no skills');
		});

		it('should reject non-array skills', async () => {
			const manifest = createValidManifest({ skills: 'not-an-array' });
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Manifest contains no skills');
		});

		it('should reject skill without slug', async () => {
			const manifest = createValidManifest({
				skills: [{ name: 'Skill', downloadUrl: '/download' }],
			});
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toContain('Invalid skill entry');
		});

		it('should reject skill without downloadUrl', async () => {
			const manifest = createValidManifest({
				skills: [{ slug: 'skill-1', name: 'Skill', contentHash: 'abc' }],
			});
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toContain('Invalid skill entry');
		});

		it('should skip signature verification when option is set', async () => {
			const manifest = createValidManifest();
			manifest.signature = 'invalid';

			const result = await verifyManifest(manifest, { skipSignature: true });

			expect(result.valid).toBe(true);
		});

		it('should use built-in key when env not set', async () => {
			delete process.env.SKILLSTORE_VERIFY_KEY;

			const manifest = createValidManifest();
			const result = await verifyManifest(manifest);

			// With built-in key, verification should work (but fail since test uses different key)
			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});

		it('should fail signature verification with wrong key', async () => {
			process.env.SKILLSTORE_VERIFY_KEY = 'wrong-key';

			const manifest = createValidManifest();
			const result = await verifyManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});
	});
});
