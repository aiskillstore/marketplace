import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
	getAllLockedSkills: vi.fn(),
}));

vi.mock('../src/lib/skill-lock.js', () => ({
	getAllLockedSkills: mocks.getAllLockedSkills,
}));

vi.mock('../src/lib/plugin-logger.js', () => ({
	logger: {
		info: vi.fn(),
		error: vi.fn(),
	},
}));

import listCommand from '../src/commands/list.js';

describe('list command', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('shows revisions and never renders a nullable version as vnull', async () => {
		mocks.getAllLockedSkills.mockResolvedValue([
			{
				slug: 'missing-version',
				version: null,
				authorVersion: null,
				skillstoreRevision: 3,
				zipHash: 'hash-3',
				source: 'skillstore',
				installedAt: '2026-07-14T00:00:00.000Z',
				updatedAt: '2026-07-14T00:00:00.000Z',
			},
			{
				slug: 'valid-version',
				version: '2.0.1',
				authorVersion: '2.0.1',
				skillstoreRevision: 2,
				zipHash: 'hash-2',
				source: 'skillstore',
				installedAt: '2026-07-13T00:00:00.000Z',
				updatedAt: '2026-07-13T00:00:00.000Z',
			},
		]);
		const log = vi.spyOn(console, 'log').mockImplementation(() => undefined);

		await listCommand.run?.({ args: { json: false } } as never);

		const output = log.mock.calls.map(([line]) => String(line)).join('\n');
		expect(output).toContain('missing-version  Not declared (r3)');
		expect(output).toContain('valid-version  v2.0.1 (r2)');
		expect(output).not.toContain('vnull');
		log.mockRestore();
	});
});
