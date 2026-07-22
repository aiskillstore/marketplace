import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
	fetchManifest,
	fetchPluginInfo,
	fetchPluginList,
	reportInstallation,
	reportPackInstallation,
	downloadSkill,
	downloadSkillFile,
	reportSkillTelemetry,
	reportSkillInstall,
	PluginApiError,
	type PluginManifest,
	type PluginInfo,
	type PluginListResponse,
	type InstallReportResponse,
	type TelemetryResponse,
	type TelemetryEvent,
} from '../src/lib/plugin-api.js';
import { getPluginConfig, type PluginConfig } from '../src/lib/plugin-config.js';
import type { PackInstallReport } from '../src/lib/pack-install-truth.js';

// Mock global fetch
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('plugin-api', () => {
	let config: PluginConfig;

	beforeEach(() => {
		config = getPluginConfig({
			apiBaseUrl: 'https://api.test.com',
			timeout: 5000,
		});
		mockFetch.mockReset();
	});

	describe('PluginApiError', () => {
		it('should create error with status code', () => {
			const error = new PluginApiError('Test error', 404);

			expect(error.message).toBe('Test error');
			expect(error.statusCode).toBe(404);
			expect(error.name).toBe('PluginApiError');
		});

		it('should create error with optional code', () => {
			const error = new PluginApiError('Test error', 400, 'INVALID_INPUT');

			expect(error.code).toBe('INVALID_INPUT');
		});

		it('should be instanceof Error', () => {
			const error = new PluginApiError('Test', 500);

			expect(error).toBeInstanceOf(Error);
			expect(error).toBeInstanceOf(PluginApiError);
		});
	});

	describe('fetchManifest', () => {
		const mockManifest: PluginManifest = {
			version: '1.0',
			plugin: { slug: 'test-plugin', name: 'Test Plugin', version: '1.0.0' },
			skills: [{ slug: 'skill-1', name: 'Skill 1', contentHash: 'abc', downloadUrl: '/dl' }],
			signature: 'sig123',
			generatedAt: '2024-01-01',
		};

		it('should fetch manifest successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockManifest),
			});

			const result = await fetchManifest(config, 'test-plugin');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/packs/test-plugin/manifest',
				expect.objectContaining({
					method: 'GET',
					headers: { Accept: 'application/json' },
				})
			);
			expect(result).toEqual(mockManifest);
		});

		it('should normalize canonical pack manifest to plugin-compatible shape', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({
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
						{ slug: 'skill-1', name: 'Skill 1', contentHash: 'abc', downloadUrl: 'https://example.com/SKILL.md' },
					],
					schemaVersion: '2.0',
					signed: {
						kind: 'pack',
						version: '1.0',
						pack: {
							slug: 'frontend-ui-builder-pack',
							name: 'Frontend UI Builder Pack',
							version: '2026.07.04',
							visibility: 'public',
						},
						skills: [
							{ slug: 'skill-1', name: 'Skill 1', contentHash: 'abc', downloadUrl: 'https://example.com/SKILL.md' },
						],
					},
					signature: {
						algorithm: 'Ed25519',
						keyId: 'key',
						publicKeyJwk: { kty: 'OKP', crv: 'Ed25519', x: 'abc' },
						signedAt: '2026-07-04T00:00:00Z',
						value: 'sig',
					},
				}),
			});

			const result = await fetchManifest(config, 'frontend-ui-builder-pack');

			expect(result.plugin).toEqual({
				slug: 'frontend-ui-builder-pack',
				name: 'Frontend UI Builder Pack',
				version: '2026.07.04',
			});
			expect(result.pack?.slug).toBe('frontend-ui-builder-pack');
			expect(result.skills).toHaveLength(1);
			expect(typeof result.signature).toBe('object');
		});

		it('should preserve additive dual-version fields on pack members', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () =>
					Promise.resolve({
						kind: 'pack',
						version: '1.0',
						generatedAt: '2026-07-14T00:00:00Z',
						pack: { slug: 'test-pack', name: 'Test Pack', version: '2026.07.14' },
						skills: [
							{
								slug: 'owner-skill',
								name: 'Owner Skill',
								version: null,
								authorVersion: null,
								skillstoreRevision: 2,
								versionStatus: 'missing',
								treeHash: 'tree-hash-r2',
								contentHash: 'content-hash',
								downloadUrl: 'https://example.com/SKILL.md',
							},
						],
						signature: 'signature',
					}),
			});

			const result = await fetchManifest(config, 'test-pack');

			expect(result.skills[0]).toMatchObject({
				version: null,
				authorVersion: null,
				skillstoreRevision: 2,
				versionStatus: 'missing',
				treeHash: 'tree-hash-r2',
			});
		});

		it('should ignore tampered top-level pack aliases and skills for Ed25519 envelopes', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({
					kind: 'pack', version: '1.0', generatedAt: 'evil',
					plugin: { slug: 'evil', name: 'Evil', version: '9.9.9' },
					pack: { slug: 'evil', name: 'Evil', version: '9.9.9' },
					executionBinding: { bindingDigest: 'evil' },
					skills: [{ slug: 'evil', name: 'Evil', contentHash: 'evil', downloadUrl: 'https://evil.test' }],
					signed: {
						kind: 'pack', version: '1.0', generatedAt: 'safe',
						pack: { slug: 'safe', name: 'Safe', version: '1.0.0', visibility: 'public' },
						skills: [{ slug: 'safe-skill', name: 'Safe', contentHash: 'safe', downloadUrl: 'https://safe.test' }],
						executionBinding: { bindingDigest: 'safe' },
					},
					signature: {
						algorithm: 'Ed25519', keyId: 'k',
						publicKeyJwk: { kty: 'OKP', crv: 'Ed25519', x: 'x' },
						signedAt: 'safe', value: 'sig',
					},
				}),
			});

			const result = await fetchManifest(config, 'safe');
			expect(result.plugin.slug).toBe('safe');
			expect(result.pack?.slug).toBe('safe');
			expect(result.skills[0].slug).toBe('safe-skill');
			expect(result.executionBinding).toEqual({ bindingDigest: 'safe' });
			expect(result.generatedAt).toBe('safe');
		});

		it('should throw PluginApiError on 404', async () => {
			mockFetch.mockResolvedValue({
				ok: false,
				status: 404,
				statusText: 'Not Found',
				text: () => Promise.resolve(JSON.stringify({ error: 'Plugin not found' })),
			});

			await expect(fetchManifest(config, 'nonexistent')).rejects.toThrow(PluginApiError);
			await expect(fetchManifest(config, 'nonexistent')).rejects.toMatchObject({
				statusCode: 404,
				message: 'Plugin not found',
			});
		});

		it('should handle non-JSON error response', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Server Error',
				text: () => Promise.resolve('Internal error'),
			});

			await expect(fetchManifest(config, 'test')).rejects.toMatchObject({
				statusCode: 500,
				message: 'Failed to fetch manifest: Server Error',
			});
		});

		it('should handle text() failure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 503,
				statusText: 'Unavailable',
				text: () => Promise.reject(new Error('Stream error')),
			});

			await expect(fetchManifest(config, 'test')).rejects.toMatchObject({
				statusCode: 503,
			});
		});
	});

	describe('fetchPluginInfo', () => {
		const mockInfo: PluginInfo = {
			id: '123',
			slug: 'test-plugin',
			name: 'Test Plugin',
			description: 'A test plugin',
			pluginType: 'curated',
			visibility: 'public',
			pricing: 'free',
			skillCount: 5,
			installCount: 100,
			priceCents: 0,
			currency: 'USD',
			scenarioTags: null,
			skills: [],
		};

		it('should fetch plugin info successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ data: mockInfo }),
			});

			const result = await fetchPluginInfo(config, 'test-plugin');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/packs/test-plugin',
				expect.any(Object)
			);
			expect(result).toEqual(mockInfo);
		});

		it('should normalize canonical pack detail fields', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({
					data: {
						id: '123',
						slug: 'test-pack',
						name: 'Test Pack',
						description: null,
						type: 'scenario',
						visibility: 'public',
						skillCount: 3,
						installCount: 10,
						scenarioTags: ['frontend'],
						skills: [],
					},
				}),
			});

			const result = await fetchPluginInfo(config, 'test-pack');

			expect(result.pluginType).toBe('scenario');
			expect(result.pricing).toBe('free');
			expect(result.priceCents).toBe(0);
			expect(result.currency).toBe('USD');
		});

		it('should throw error on failure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 404,
				statusText: 'Not Found',
				text: () => Promise.resolve(JSON.stringify({ error: 'Not found', code: 'NOT_FOUND' })),
			});

			await expect(fetchPluginInfo(config, 'test')).rejects.toMatchObject({
				statusCode: 404,
				code: 'NOT_FOUND',
			});
		});
	});

	describe('fetchPluginList', () => {
		const mockResponse: PluginListResponse = {
			data: [
				{
					id: '1',
					slug: 'plugin-1',
					name: 'Plugin 1',
					description: null,
					pluginType: 'curated',
					visibility: 'public',
					pricing: 'free',
					priceCents: 0,
					currency: 'USD',
					skillCount: 3,
					installCount: 50,
					score: 85,
				},
			],
			pagination: { page: 1, limit: 10, total: 1, totalPages: 1 },
		};

		it('should fetch plugin list without filters', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			});

			const result = await fetchPluginList(config);

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/packs',
				expect.any(Object)
			);
			expect(result).toEqual(mockResponse);
		});

		it('should normalize canonical pack list fields', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({
					data: [
						{
							id: '1',
							slug: 'pack-1',
							name: 'Pack 1',
							description: null,
							type: 'user',
							visibility: 'public',
							skillCount: 3,
							installCount: 50,
							score: 85,
						},
					],
					pagination: { page: 1, limit: 10, total: 1, totalPages: 1 },
				}),
			});

			const result = await fetchPluginList(config);

			expect(result.data[0].pluginType).toBe('user');
			expect(result.data[0].pricing).toBe('free');
		});

		it('should apply filter options to URL', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(mockResponse),
			});

			await fetchPluginList(config, {
				type: 'curated',
				pricing: 'free',
				limit: 20,
				page: 2,
			});

			const callUrl = mockFetch.mock.calls[0][0];
			expect(callUrl).toContain('type=curated');
			expect(callUrl).toContain('pricing=free');
			expect(callUrl).toContain('limit=20');
			expect(callUrl).toContain('page=2');
		});

		it('should throw error on failure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 400,
				statusText: 'Bad Request',
			});

			await expect(fetchPluginList(config)).rejects.toMatchObject({
				statusCode: 400,
			});
		});
	});

	describe('reportInstallation', () => {
		it('preserves the legacy SDK reporting contract', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true }),
			});

			await reportInstallation(config, 'test-plugin', 'manual');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/packs/test-plugin/install',
				expect.objectContaining({ body: JSON.stringify({ method: 'manual' }) })
			);
		});
	});

	describe('reportPackInstallation', () => {
		const completeReport: PackInstallReport = {
			method: 'cli',
			attemptId: '11111111-1111-4111-8111-111111111111',
			anonymousClientId: '22222222-2222-4222-8222-222222222222',
			status: 'complete',
			expectedSkillCount: 2,
			installedSkillCount: 2,
			failedSkillCount: 0,
			cliVersion: '0.1.10',
			osPlatform: 'linux',
			targetAgents: ['codex'],
			readbackPassed: true,
		};

		it('should report the complete CLI installation truth payload', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true, installationId: 'inst-123' }),
			});

			const result = await reportPackInstallation(config, 'test-plugin', completeReport);

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/packs/test-plugin/install',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify(completeReport),
				})
			);
			expect(result.success).toBe(true);
		});

		it.each(['partial', 'error'] as const)('should preserve a %s outcome', async (status) => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true }),
			});

			const report: PackInstallReport = {
				...completeReport,
				status,
				installedSkillCount: status === 'partial' ? 1 : 0,
				failedSkillCount: status === 'partial' ? 1 : 2,
				readbackPassed: false,
			};
			await reportPackInstallation(config, 'test-plugin', report);

			expect(mockFetch).toHaveBeenCalledWith(
				expect.any(String),
					expect.objectContaining({ body: JSON.stringify(report) })
			);
		});

		it('should handle duplicate installation response', async () => {
			const response: InstallReportResponse = {
				success: true,
				duplicate: true,
				message: 'Already installed',
			};
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve(response),
			});

			const result = await reportPackInstallation(config, 'test-plugin', completeReport);

			expect(result.duplicate).toBe(true);
		});
	});

	describe('downloadSkill', () => {
		it('should download skill with relative URL', async () => {
			// Use a config that matches the real URL pattern
			const downloadConfig = getPluginConfig({
				apiBaseUrl: 'https://skillstore.io/api',
				timeout: 5000,
			});

			mockFetch.mockResolvedValueOnce(new Response('# Skill Content'));

			const result = await downloadSkill(downloadConfig, '/downloads/skill.md');

			// apiBaseUrl.replace('/api', '') = 'https://skillstore.io'
			expect(String(mockFetch.mock.calls[0][0])).toBe('https://skillstore.io/downloads/skill.md');
			expect(mockFetch.mock.calls[0][1].redirect).toBe('error');
			expect(result).toBe('# Skill Content');
		});

		it('rejects an absolute artifact URL from another origin before fetching', async () => {
			await expect(downloadSkill(config, 'https://cdn.example.com/skill.md'))
				.rejects.toThrow('outside the configured Skillstore origin');
			expect(mockFetch).not.toHaveBeenCalled();
		});

		it('allows only an exact, explicitly approved immutable raw GitHub URL', async () => {
			const url = 'https://raw.githubusercontent.com/aiskillstore/marketplace/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/skills/example/SKILL.md';
			mockFetch.mockResolvedValueOnce(new Response('ok'));
			await expect(downloadSkillFile(config, url, { approvedExternalUrl: url }))
				.resolves.toEqual(new TextEncoder().encode('ok'));
			expect(String(mockFetch.mock.calls[0][0])).toBe(url);

			await expect(downloadSkillFile(config, url, {
				approvedExternalUrl: url.replace('SKILL.md', 'OTHER.md'),
			})).rejects.toThrow('outside the configured Skillstore origin');
		});

		it('should throw error on download failure', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 403,
				statusText: 'Forbidden',
			});

			await expect(downloadSkill(config, '/skill.md')).rejects.toMatchObject({
				statusCode: 403,
			});
		});

		it('should download raw skill file bytes', async () => {
			const bytes = new Uint8Array([1, 2, 3]);
			mockFetch.mockResolvedValueOnce(new Response(bytes));

			const result = await downloadSkillFile(config, '/skill.bin');

			expect(result).toEqual(bytes);
		});

		it('fails closed on redirects and signed-size mismatches', async () => {
			mockFetch.mockResolvedValueOnce(new Response('abc', { headers: { 'content-length': '3' } }));
			await expect(downloadSkillFile(config, '/skill.bin', { expectedBytes: 4, maxBytes: 10 }))
				.rejects.toThrow('does not match signed manifest');
			expect(String(mockFetch.mock.calls[0][0])).toBe('https://api.test.com/skill.bin');
			expect(mockFetch.mock.calls[0][1].redirect).toBe('error');

			mockFetch.mockResolvedValueOnce(new Response('abcd'));
			await expect(downloadSkillFile(config, '/skill.bin', { maxBytes: 3 }))
				.rejects.toThrow('exceeds 3 byte limit');
		});

		it('compares limits and signed bytes with the decoded body when Content-Length describes compression', async () => {
			mockFetch.mockResolvedValueOnce(new Response('abcd', {
				headers: {
					'content-encoding': 'gzip',
					'content-length': '11',
				},
			}));

			await expect(downloadSkillFile(config, '/skill.bin', { expectedBytes: 4, maxBytes: 10 }))
				.resolves.toEqual(new TextEncoder().encode('abcd'));
		});

		it('allows only an explicitly configured localhost test origin over HTTP', async () => {
			const local = getPluginConfig({ apiBaseUrl: 'http://localhost:8787/api' });
			mockFetch.mockResolvedValueOnce(new Response('ok'));
			await expect(downloadSkillFile(local, 'http://localhost:8787/artifact')).resolves.toEqual(new TextEncoder().encode('ok'));
		});
	});

	describe('reportSkillTelemetry', () => {
		const mockEvent: TelemetryEvent = {
			skill_slug: 'test-skill',
			event_type: 'invocation',
			success: true,
		};

		it('should report telemetry successfully', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true, event_id: 'evt-123' }),
			});

			const result = await reportSkillTelemetry(config, mockEvent);

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/telemetry/effectiveness',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify(mockEvent),
				})
			);
			expect(result.success).toBe(true);
		});

		it('should return error response without throwing on HTTP error', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				statusText: 'Server Error',
			});

			const result = await reportSkillTelemetry(config, mockEvent);

			expect(result.success).toBe(false);
			expect(result.error).toContain('500');
		});

		it('should handle network errors gracefully', async () => {
			mockFetch.mockRejectedValueOnce(new Error('Network error'));

			const result = await reportSkillTelemetry(config, mockEvent);

			expect(result.success).toBe(false);
			expect(result.error).toBe('Network error');
		});

		it('should handle non-Error exceptions', async () => {
			mockFetch.mockRejectedValueOnce('String error');

			const result = await reportSkillTelemetry(config, mockEvent);

			expect(result.success).toBe(false);
			expect(result.error).toBe('Unknown error');
		});
	});

	describe('reportSkillInstall', () => {
		it('should report skill install with default tool', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true }),
			});

			await reportSkillInstall(config, 'my-skill');

			const body = JSON.parse(mockFetch.mock.calls[0][1].body);
			expect(body.skill_slug).toBe('my-skill');
			expect(body.event_type).toBe('invocation');
			expect(body.tool_name).toBe('claude_code');
		});

		it('should report skill install with custom tool', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true }),
			});

			await reportSkillInstall(config, 'my-skill', 'codex');

			const body = JSON.parse(mockFetch.mock.calls[0][1].body);
			expect(body.tool_name).toBe('codex');
		});
	});
});
