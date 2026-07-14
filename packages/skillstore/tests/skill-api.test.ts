import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
	fetchSkillInfo,
	fetchSkillManifest,
	downloadSkillZip,
	formatSkillVersionIdentity,
	getSkillVersionIdentity,
	getSkillDownloadUrlFromManifest,
	getSkillZipHash,
	normalizeSkillManifest,
	SkillApiError,
	type SkillInfo,
	type SkillManifest,
} from '../src/lib/skill-api.js';
import { getPluginConfig, type PluginConfig } from '../src/lib/plugin-config.js';

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('skill-api', () => {
	let config: PluginConfig;

	beforeEach(() => {
		config = getPluginConfig({
			apiBaseUrl: 'https://api.test.com',
			timeout: 5000,
		});
		mockFetch.mockReset();
	});

	describe('SkillApiError', () => {
		it('should create error with status code', () => {
			const error = new SkillApiError('Skill not found', 404);

			expect(error.message).toBe('Skill not found');
			expect(error.statusCode).toBe(404);
			expect(error.name).toBe('SkillApiError');
		});

		it('should create error with optional code', () => {
			const error = new SkillApiError('Error', 400, 'INVALID_SLUG');

			expect(error.code).toBe('INVALID_SLUG');
		});

		it('should be instanceof Error', () => {
			const error = new SkillApiError('Test', 500);

			expect(error).toBeInstanceOf(Error);
			expect(error).toBeInstanceOf(SkillApiError);
		});
	});

	describe('fetchSkillInfo', () => {
		const mockSkillInfo: SkillInfo = {
			slug: 'test-skill',
			name: 'Test Skill',
			description: 'A test skill',
			category: 'testing',
			version: '1.0.0',
			author: 'Test Author',
			riskLevel: 'low',
			qualityScore: 85,
			pluginPath: 'test-plugin',
		};

		it('should fetch skill info successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ data: mockSkillInfo }),
			});

			const result = await fetchSkillInfo(config, 'test-skill');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/test-skill',
				expect.objectContaining({
					method: 'GET',
					headers: { Accept: 'application/json' },
				})
			);
			expect(result).toEqual(mockSkillInfo);
		});

		it('should throw SkillApiError on 404', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 404,
				statusText: 'Not Found',
				text: () => Promise.resolve(JSON.stringify({ error: 'Skill not found' })),
			});

			await expect(fetchSkillInfo(config, 'nonexistent')).rejects.toThrow(SkillApiError);
			await expect(fetchSkillInfo(config, 'nonexistent')).rejects.toMatchObject({
				statusCode: 404,
				message: 'Skill not found',
			});
		});

		it('should throw error with code when provided', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				statusText: 'Bad Request',
				text: () =>
					Promise.resolve(JSON.stringify({ error: 'Invalid slug', code: 'INVALID_SLUG' })),
			});

			await expect(fetchSkillInfo(config, 'bad slug')).rejects.toMatchObject({
				statusCode: 400,
				code: 'INVALID_SLUG',
			});
		});

		it('should handle non-JSON error response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
				text: () => Promise.resolve('Server crashed'),
			});

			await expect(fetchSkillInfo(config, 'test')).rejects.toMatchObject({
				statusCode: 500,
				message: 'Failed to fetch skill info: Internal Server Error',
			});
		});

		it('should handle text() failure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 503,
				statusText: 'Service Unavailable',
				text: () => Promise.reject(new Error('Stream error')),
			});

			await expect(fetchSkillInfo(config, 'test')).rejects.toMatchObject({
				statusCode: 503,
			});
		});

		it('should use correct URL structure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ data: mockSkillInfo }),
			});

			await fetchSkillInfo(config, 'my-skill-slug');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/my-skill-slug',
				expect.any(Object)
			);
		});
	});

	describe('fetchSkillManifest', () => {
		const mockManifest: SkillManifest = {
			version: '1.0',
			skill: {
				slug: 'test-skill',
				name: 'Test Skill',
				version: '1.0.0',
				author: 'Test Author',
				zipHash: 'abc123def456',
			},
			downloadUrl: '/api/skills/test-skill/download',
			signature: 'valid-signature',
			generatedAt: '2024-01-01T00:00:00Z',
		};

		it('should fetch skill manifest successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockManifest),
			});

			const result = await fetchSkillManifest(config, 'test-skill');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/test-skill/manifest',
				expect.objectContaining({
					method: 'GET',
					headers: { Accept: 'application/json' },
				})
			);
			expect(result).toEqual(mockManifest);
		});

		it('should throw SkillApiError on 404', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 404,
				statusText: 'Not Found',
				text: () => Promise.resolve(JSON.stringify({ error: 'Skill not found' })),
			});

			await expect(fetchSkillManifest(config, 'nonexistent')).rejects.toThrow(SkillApiError);
			await expect(fetchSkillManifest(config, 'nonexistent')).rejects.toMatchObject({
				statusCode: 404,
				message: 'Skill not found',
			});
		});

		it('should throw error with code when provided', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				statusText: 'Bad Request',
				text: () =>
					Promise.resolve(JSON.stringify({ error: 'Invalid slug', code: 'INVALID_SLUG' })),
			});

			await expect(fetchSkillManifest(config, 'bad slug')).rejects.toMatchObject({
				statusCode: 400,
				code: 'INVALID_SLUG',
			});
		});

		it('should handle non-JSON error response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
				text: () => Promise.resolve('Server crashed'),
			});

			await expect(fetchSkillManifest(config, 'test')).rejects.toMatchObject({
				statusCode: 500,
				message: 'Failed to fetch manifest: Internal Server Error',
			});
		});

		it('should use correct URL structure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockManifest),
			});

			await fetchSkillManifest(config, 'my-skill-slug');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/my-skill-slug/manifest',
				expect.any(Object)
			);
		});
	});

	describe('manifest helpers', () => {
		const legacyManifest: SkillManifest = {
			version: '1.0',
			skill: {
				slug: 'test-skill',
				name: 'Test Skill',
				version: '1.0.0',
				zipHash: 'legacy-hash',
			},
			downloadUrl: '/api/skills/test-skill/download',
			signature: 'valid-signature',
			generatedAt: '2024-01-01T00:00:00Z',
		};

		it('should project Ed25519 convenience fields from the signed payload', () => {
			const signedSkill = { slug: 'safe', name: 'Safe', version: '2.0.1' };
			const manifest = normalizeSkillManifest({
				version: '1.0',
				skill: { slug: 'evil', name: 'Evil', version: '9.9.9' },
				artifact: { url: 'https://evil.test/x.zip', sha256: 'evil' },
				signed: {
					kind: 'skill',
					version: '1.0',
					skill: signedSkill,
					artifact: { url: 'https://safe.test/x.zip', sha256: 'safe' },
				},
				signature: {
					algorithm: 'Ed25519', keyId: 'k',
					publicKeyJwk: { kty: 'OKP', crv: 'Ed25519', x: 'x' },
					signedAt: '2026-07-14T00:00:00Z', value: 'sig',
				},
				generatedAt: '2026-07-14T00:00:00Z',
			});

			expect(manifest.skill.slug).toBe('safe');
			expect(manifest.artifact?.url).toBe('https://safe.test/x.zip');
		});

		const modernManifest: SkillManifest = {
			kind: 'skill',
			version: '1.0',
			schemaVersion: '2.0',
			skill: {
				slug: 'test-skill',
				name: 'Test Skill',
				version: '1.0.0',
			},
			artifact: {
				type: 'skill-zip',
				url: 'https://cdn.test.com/test-skill.zip',
				mediaType: 'application/zip',
				sha256: 'artifact-hash',
			},
			signature: {
				algorithm: 'Ed25519',
				keyId: 'test-key',
				publicKeyJwk: {
					kty: 'OKP',
					crv: 'Ed25519',
					x: 'test-public-key',
				},
				signedAt: '2026-07-04T00:00:00Z',
				value: 'test-signature',
			},
			generatedAt: '2026-07-04T00:00:00Z',
		};

		it('should read ZIP hash from legacy skill.zipHash', () => {
			expect(getSkillZipHash(legacyManifest)).toBe('legacy-hash');
		});

		it('should read ZIP hash from canonical artifact.sha256', () => {
			expect(getSkillZipHash(modernManifest)).toBe('artifact-hash');
		});

		it('should prefer signed artifact hash when present', () => {
			const manifest: SkillManifest = {
				...modernManifest,
				artifact: { ...modernManifest.artifact, sha256: 'tampered-hash' },
				signed: {
					kind: 'skill',
					version: '1.0',
					generatedAt: modernManifest.generatedAt,
					skill: modernManifest.skill,
					artifact: { ...modernManifest.artifact, sha256: 'signed-hash' },
				},
			};

			expect(getSkillZipHash(manifest)).toBe('signed-hash');
		});

		it('should resolve canonical artifact download URL', () => {
			expect(getSkillDownloadUrlFromManifest(config, modernManifest, 'test-skill')).toBe(
				'https://cdn.test.com/test-skill.zip'
			);
		});

		it('should resolve relative download URL against API base', () => {
			expect(getSkillDownloadUrlFromManifest(config, legacyManifest, 'test-skill')).toBe(
				'https://api.test.com/api/skills/test-skill/download'
			);
		});

		it('should fall back to conventional download endpoint', () => {
			const manifest = { ...legacyManifest, downloadUrl: undefined };

			expect(getSkillDownloadUrlFromManifest(config, manifest, 'test-skill')).toBe(
				'https://api.test.com/skills/test-skill/download'
			);
		});

		it('should preserve the complete dual-version identity', () => {
			const identity = getSkillVersionIdentity({
				slug: 'test-skill',
				name: 'Test Skill',
				version: '2.0.1',
				authorVersion: '2.0.1',
				skillstoreRevision: 2,
				versionStatus: 'valid',
				treeHash: 'tree-hash-r2',
			});

			expect(identity).toEqual({
				authorVersion: '2.0.1',
				skillstoreRevision: 2,
				versionStatus: 'valid',
				treeHash: 'tree-hash-r2',
			});
		});

		it('should represent an undeclared author version without emitting vnull', () => {
			const skill = {
				slug: 'test-skill',
				name: 'Test Skill',
				version: null,
				skillstoreRevision: 1,
			} satisfies SkillManifest['skill'];

			expect(getSkillVersionIdentity(skill)).toEqual({
				authorVersion: null,
				skillstoreRevision: 1,
				versionStatus: 'missing',
				treeHash: null,
			});
			expect(formatSkillVersionIdentity(skill)).toBe('Not declared (r1)');
		});

		it('should remain compatible with legacy manifests', () => {
			expect(getSkillVersionIdentity(legacyManifest.skill)).toEqual({
				authorVersion: '1.0.0',
				skillstoreRevision: null,
				versionStatus: 'legacy_unknown',
				treeHash: null,
			});
			expect(formatSkillVersionIdentity(legacyManifest.skill)).toBe('v1.0.0');
		});

		it('should not relabel an explicit null authorVersion legacy alias', () => {
			const skill = {
				slug: 'legacy-skill',
				name: 'Legacy Skill',
				version: '1.0.2',
				authorVersion: null,
				versionStatus: 'legacy_unknown',
			} satisfies SkillManifest['skill'];

			expect(getSkillVersionIdentity(skill).authorVersion).toBeNull();
			expect(formatSkillVersionIdentity(skill)).toBe('Legacy v1.0.2 (unverified)');
		});

		it('should visibly distinguish revisions under the same author version', () => {
			expect(formatSkillVersionIdentity({ version: '2.0.1', skillstoreRevision: 1 })).toBe(
				'v2.0.1 (r1)'
			);
			expect(formatSkillVersionIdentity({ version: '2.0.1', skillstoreRevision: 2 })).toBe(
				'v2.0.1 (r2)'
			);
		});
	});

	describe('downloadSkillZip', () => {
		it('should download skill as ArrayBuffer', async () => {
			const mockBuffer = new ArrayBuffer(100);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				arrayBuffer: () => Promise.resolve(mockBuffer),
			});

			const result = await downloadSkillZip(config, 'test-skill');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/test-skill/download',
				expect.objectContaining({
					method: 'GET',
				})
			);
			expect(result).toBe(mockBuffer);
		});

		it('should use doubled timeout for downloads', async () => {
			const mockBuffer = new ArrayBuffer(50);
			mockFetch.mockResolvedValueOnce({
				ok: true,
				arrayBuffer: () => Promise.resolve(mockBuffer),
			});

			await downloadSkillZip(config, 'test-skill');

			// Verify the signal has timeout of 2x the config timeout
			const callOptions = mockFetch.mock.calls[0][1];
			expect(callOptions.signal).toBeDefined();
		});

		it('should throw SkillApiError on download failure', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 403,
				statusText: 'Forbidden',
			});

			await expect(downloadSkillZip(config, 'test-skill')).rejects.toThrow(SkillApiError);
			await expect(downloadSkillZip(config, 'test-skill')).rejects.toMatchObject({
				statusCode: 403,
				message: 'Failed to download skill: Forbidden',
			});
		});

		it('should throw error on 404', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: 'Not Found',
			});

			await expect(downloadSkillZip(config, 'nonexistent')).rejects.toMatchObject({
				statusCode: 404,
			});
		});

		it('should throw error on server error', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Internal Server Error',
			});

			await expect(downloadSkillZip(config, 'test')).rejects.toMatchObject({
				statusCode: 500,
			});
		});

		it('should use correct download URL structure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				arrayBuffer: () => Promise.resolve(new ArrayBuffer(10)),
			});

			await downloadSkillZip(config, 'complex-skill-slug');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/skills/complex-skill-slug/download',
				expect.any(Object)
			);
		});

		it('should download from manifest artifact URL when provided', async () => {
			const mockBuffer = new ArrayBuffer(10);
			const manifest: SkillManifest = {
				version: '1.0',
				skill: {
					slug: 'test-skill',
					name: 'Test Skill',
					version: '1.0.0',
				},
				artifact: {
					type: 'skill-zip',
					url: 'https://cdn.test.com/test-skill.zip',
					sha256: 'artifact-hash',
				},
				signature: 'valid-signature',
				generatedAt: '2026-07-04T00:00:00Z',
			};
			mockFetch.mockResolvedValueOnce({
				ok: true,
				arrayBuffer: () => Promise.resolve(mockBuffer),
			});

			const result = await downloadSkillZip(config, 'test-skill', manifest);

			expect(mockFetch).toHaveBeenCalledWith(
				'https://cdn.test.com/test-skill.zip',
				expect.objectContaining({
					method: 'GET',
				})
			);
			expect(result).toBe(mockBuffer);
		});
	});
});
