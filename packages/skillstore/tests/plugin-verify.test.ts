import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createHmac, createHash, webcrypto } from 'node:crypto';
import {
	getVerificationKey,
	verifyManifestSignature,
	verifyContentHash,
	verifyManifest,
	verifySkillManifest,
	verifySkillManifestSignature,
	verifyZipHash,
	type VerifyResult,
} from '../src/lib/plugin-verify.js';
import type { PluginManifest } from '../src/lib/plugin-api.js';
import type { SkillManifest } from '../src/lib/skill-api.js';

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

function encodeBase64Url(bytes: Uint8Array): string {
	return Buffer.from(bytes)
		.toString('base64')
		.replace(/\+/g, '-')
		.replace(/\//g, '_')
		.replace(/=+$/g, '');
}

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

		it('should reject truncated hashes', () => {
			const content = 'Test content';
			const fullHash = createHash('sha256').update(content).digest('hex');
			const truncatedHash = fullHash.substring(0, 16);

			expect(verifyContentHash(content, truncatedHash)).toBe(false);
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

		it('should accept pack payload schema 1.1 for nullable member versions', async () => {
			const manifest = createValidManifest({ version: '1.1' });
			manifest.skills[0].version = null;

			await expect(verifyManifest(manifest, { skipSignature: true }))
				.resolves.toMatchObject({ valid: true });
		});

		it('should reject a self-signed canonical Pack manifest', async () => {
			const subtle = globalThis.crypto?.subtle || webcrypto.subtle;
			const keyPair = await subtle.generateKey({ name: 'Ed25519' }, true, ['sign', 'verify']);
			const privateJwk = await subtle.exportKey('jwk', keyPair.privateKey);
			const publicJwk = await subtle.exportKey('jwk', keyPair.publicKey);
			const signed = {
				kind: 'pack',
				version: '1.0',
				generatedAt: '2026-07-04T00:00:00Z',
				pack: {
					slug: 'frontend-ui-builder-pack',
					name: 'Frontend UI Builder Pack',
					version: '2026.07.04',
					visibility: 'public',
				},
				skills: [
					{
						slug: 'skill-1',
						name: 'Skill 1',
						version: '1.0.0',
						downloadUrl: 'https://example.com/SKILL.md',
						contentHash: 'abc',
					},
				],
			};
			const rawSignature = await subtle.sign(
				{ name: 'Ed25519' },
				await subtle.importKey('jwk', privateJwk, { name: 'Ed25519' }, false, ['sign']),
				new TextEncoder().encode(canonicalJson(signed))
			);
			const manifest = {
				...signed,
				plugin: {
					slug: signed.pack.slug,
					name: signed.pack.name,
					version: signed.pack.version,
				},
				schemaVersion: '2.0',
				signed,
				signature: {
					algorithm: 'Ed25519',
					keyId: 'test-key',
					publicKeyJwk: {
						kty: 'OKP',
						crv: 'Ed25519',
						x: publicJwk.x,
					},
					signedAt: '2026-07-04T00:00:00Z',
					value: encodeBase64Url(new Uint8Array(rawSignature)),
				},
			} as PluginManifest;

			const result = await verifyManifest(manifest);

			expect(result).toEqual({
				valid: false,
				error: 'Ed25519 signature key is not trusted',
			});
		});

		it('should reject an unknown Ed25519 key id even when it claims the production public key', async () => {
			const manifest = createValidManifest() as PluginManifest;
			manifest.signed = { kind: 'pack', version: '1.0', skills: manifest.skills };
			manifest.signature = {
				algorithm: 'Ed25519',
				keyId: 'unknown-key',
				publicKeyJwk: {
					kty: 'OKP',
					crv: 'Ed25519',
					x: '2tbC6eNY4T9sx4Pvuo_NwHlXGyWWz95WAtHyHUTqzs8',
				},
				signedAt: '2026-07-22T00:00:00.000Z',
				value: 'AA',
			};

			await expect(verifyManifest(manifest)).resolves.toEqual({
				valid: false,
				error: 'Ed25519 signature key is not trusted',
			});
		});

		it('should verify signatures with the built-in production public key, not manifest key material', async () => {
			const manifest = createValidManifest() as PluginManifest;
			manifest.signed = { kind: 'pack', version: '1.0', skills: manifest.skills };
			manifest.signature = {
				algorithm: 'Ed25519',
				keyId: 'EP0Myk7rTk_J0RdG1fvpkP',
				publicKeyJwk: {
					kty: 'OKP',
					crv: 'Ed25519',
					x: '2tbC6eNY4T9sx4Pvuo_NwHlXGyWWz95WAtHyHUTqzs8',
				},
				signedAt: '2026-07-22T00:00:00.000Z',
				value: 'AA',
			};

			await expect(verifyManifest(manifest)).resolves.toEqual({
				valid: false,
				error: 'Signature verification failed',
			});
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

	describe('verifySkillManifestSignature', () => {
		const secretKey = 'test-skill-secret-key';

		function createSignedSkillManifest(
			manifest: Omit<SkillManifest, 'signature'>
		): SkillManifest {
			const dataToSign = JSON.stringify(manifest, null, 0);
			const signature = createHmac('sha256', secretKey).update(dataToSign).digest('hex');
			return { ...manifest, signature };
		}

		const validSkillManifest: Omit<SkillManifest, 'signature'> = {
			version: '1.0',
			skill: {
				slug: 'test-skill',
				name: 'Test Skill',
				version: '1.0.0',
				author: 'Test Author',
				zipHash: 'abc123def456',
			},
			downloadUrl: '/api/skills/test-skill/download',
			generatedAt: '2024-01-01T00:00:00Z',
		};

		it('should verify valid signature', () => {
			const manifest = createSignedSkillManifest(validSkillManifest);
			const result = verifySkillManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(true);
			expect(result.error).toBeUndefined();
		});

		it('should reject manifest without signature', () => {
			const manifest = { ...validSkillManifest, signature: undefined } as unknown as SkillManifest;
			const result = verifySkillManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Manifest has no signature');
		});

		it('should reject manifest with wrong signature', () => {
			const manifest = createSignedSkillManifest(validSkillManifest);
			manifest.signature = 'invalid-signature';

			const result = verifySkillManifestSignature(manifest, secretKey);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});

		it('should reject manifest signed with different key', () => {
			const manifest = createSignedSkillManifest(validSkillManifest);

			const result = verifySkillManifestSignature(manifest, 'different-key');

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});
	});

	describe('verifySkillManifest', () => {
		const secretKey = 'test-skill-key';

		function createValidSkillManifest(overrides = {}): SkillManifest {
			const base = {
				version: '1.0' as const,
				skill: {
					slug: 'test-skill',
					name: 'Test Skill',
					version: '1.0.0',
					zipHash: 'abc123',
				},
				downloadUrl: '/api/skills/test-skill/download',
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

		it('should validate a complete skill manifest', async () => {
			const manifest = createValidSkillManifest();
			const result = await verifySkillManifest(manifest);

			expect(result.valid).toBe(true);
		});

		it('should accept single-skill payload schema 1.1 with a null version', async () => {
			const manifest = createValidSkillManifest();
			manifest.version = '1.1';
			manifest.skill.version = null;

			await expect(verifySkillManifest(manifest, { skipSignature: true }))
				.resolves.toMatchObject({ valid: true });
		});

		it('should reject unsupported manifest version', async () => {
			const manifest = createValidSkillManifest({ version: '2.0' });
			const result = await verifySkillManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Unsupported manifest version');
		});

		it('should reject missing skill slug', async () => {
			const manifest = createValidSkillManifest({
				skill: { name: 'Test', version: '1.0.0', zipHash: 'abc' },
			});
			const result = await verifySkillManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Missing skill slug in manifest');
		});

		it('should reject missing ZIP hash', async () => {
			const manifest = createValidSkillManifest({
				skill: { slug: 'test', name: 'Test', version: '1.0.0' },
			});
			const result = await verifySkillManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Missing zipHash or artifact.sha256 in manifest');
		});

		it('should reject a self-signed canonical Skill manifest', async () => {
			const subtle = globalThis.crypto?.subtle || webcrypto.subtle;
			const keyPair = await subtle.generateKey({ name: 'Ed25519' }, true, ['sign', 'verify']);
			const privateJwk = await subtle.exportKey('jwk', keyPair.privateKey);
			const publicJwk = await subtle.exportKey('jwk', keyPair.publicKey);
			const signed = {
				kind: 'skill',
				version: '1.0',
				generatedAt: '2026-07-04T00:00:00Z',
				skill: {
					slug: 'test-skill',
					name: 'Test Skill',
					version: '1.0.0',
					author: 'Test Author',
				},
				artifact: {
					type: 'skill-zip',
					url: 'https://skillstore.io/api/skills/test-skill/download?ref=abc123',
					mediaType: 'application/zip',
					sha256: 'abc123def456',
				},
			};
			const rawSignature = await subtle.sign(
				{ name: 'Ed25519' },
				await subtle.importKey('jwk', privateJwk, { name: 'Ed25519' }, false, ['sign']),
				new TextEncoder().encode(canonicalJson(signed))
			);
			const manifest = {
				...signed,
				schemaVersion: '2.0',
				signed,
				signature: {
					algorithm: 'Ed25519',
					keyId: 'test-key',
					publicKeyJwk: {
						kty: 'OKP',
						crv: 'Ed25519',
						x: publicJwk.x,
					},
					signedAt: '2026-07-04T00:00:00Z',
					value: encodeBase64Url(new Uint8Array(rawSignature)),
				},
			} as SkillManifest;

			const result = await verifySkillManifest(manifest);

			expect(result).toEqual({
				valid: false,
				error: 'Ed25519 signature key is not trusted',
			});
		});

		it('should skip signature verification when option is set', async () => {
			const manifest = createValidSkillManifest();
			manifest.signature = 'invalid';

			const result = await verifySkillManifest(manifest, { skipSignature: true });

			expect(result.valid).toBe(true);
		});

		it('should fail signature verification with wrong key', async () => {
			process.env.SKILLSTORE_VERIFY_KEY = 'wrong-key';

			const manifest = createValidSkillManifest();
			const result = await verifySkillManifest(manifest);

			expect(result.valid).toBe(false);
			expect(result.error).toBe('Signature verification failed');
		});
	});

	describe('verifyZipHash', () => {
		it('should verify matching ZIP hash', () => {
			const content = 'Hello, World!';
			const buffer = new TextEncoder().encode(content).buffer;
			const expectedHash = createHash('sha256').update(Buffer.from(buffer)).digest('hex');

			expect(verifyZipHash(buffer, expectedHash)).toBe(true);
		});

		it('should reject non-matching ZIP hash', () => {
			const content = 'Hello, World!';
			const buffer = new TextEncoder().encode(content).buffer;
			const wrongHash = 'deadbeef1234567890';

			expect(verifyZipHash(buffer, wrongHash)).toBe(false);
		});

		it('should handle empty buffer', () => {
			const buffer = new ArrayBuffer(0);
			const expectedHash = createHash('sha256').update(Buffer.from(buffer)).digest('hex');

			expect(verifyZipHash(buffer, expectedHash)).toBe(true);
		});

		it('should handle binary content', () => {
			const bytes = new Uint8Array([0x50, 0x4b, 0x03, 0x04]); // ZIP magic bytes
			const buffer = bytes.buffer;
			const expectedHash = createHash('sha256').update(Buffer.from(buffer)).digest('hex');

			expect(verifyZipHash(buffer, expectedHash)).toBe(true);
		});
	});
});
