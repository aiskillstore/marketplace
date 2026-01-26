import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
	fetchManifest,
	fetchPluginInfo,
	fetchPluginList,
	reportInstallation,
	downloadSkill,
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
				'https://api.test.com/plugins/test-plugin/manifest',
				expect.objectContaining({
					method: 'GET',
					headers: { Accept: 'application/json' },
				})
			);
			expect(result).toEqual(mockManifest);
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
				'https://api.test.com/plugins/test-plugin',
				expect.any(Object)
			);
			expect(result).toEqual(mockInfo);
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
				'https://api.test.com/plugins',
				expect.any(Object)
			);
			expect(result).toEqual(mockResponse);
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
		it('should report installation with default method', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true, installationId: 'inst-123' }),
			});

			const result = await reportInstallation(config, 'test-plugin');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://api.test.com/plugins/test-plugin/install',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify({ method: 'cli' }),
				})
			);
			expect(result.success).toBe(true);
		});

		it('should report installation with custom method', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: () => Promise.resolve({ success: true }),
			});

			await reportInstallation(config, 'test-plugin', 'npm');

			expect(mockFetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					body: JSON.stringify({ method: 'npm' }),
				})
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

			const result = await reportInstallation(config, 'test-plugin');

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

			mockFetch.mockResolvedValueOnce({
				ok: true,
				text: () => Promise.resolve('# Skill Content'),
			});

			const result = await downloadSkill(downloadConfig, '/downloads/skill.md');

			// apiBaseUrl.replace('/api', '') = 'https://skillstore.io'
			expect(mockFetch).toHaveBeenCalledWith(
				'https://skillstore.io/downloads/skill.md',
				expect.any(Object)
			);
			expect(result).toBe('# Skill Content');
		});

		it('should download skill with absolute URL', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				text: () => Promise.resolve('# Content'),
			});

			await downloadSkill(config, 'https://cdn.example.com/skill.md');

			expect(mockFetch).toHaveBeenCalledWith(
				'https://cdn.example.com/skill.md',
				expect.any(Object)
			);
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
