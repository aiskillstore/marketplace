import { describe, expect, it } from 'vitest';
import { parseInstalledSkillReceipt } from '../src/lib/skill-receipt.js';

function receipt(revision = 'r12', treeHash = 'a'.repeat(64)): string {
	return `# Example

## Skillstore Install Receipt

| Property | Value |
|----------|-------|
| **Skillstore revision** | ${revision} |
| **Tree hash** | \`${treeHash}\` |
`;
}

describe('skill-receipt', () => {
	it('parses a complete install receipt', () => {
		expect(parseInstalledSkillReceipt(receipt())).toEqual({
			skillstoreRevision: 12,
			treeHash: 'a'.repeat(64),
		});
	});

	it('rejects receipts without both immutable identity fields', () => {
		expect(parseInstalledSkillReceipt(receipt().replace(/\| \*\*Tree hash\*\*.*\n/, ''))).toBeNull();
		expect(parseInstalledSkillReceipt(receipt().replace(/\| \*\*Skillstore revision\*\*.*\n/, ''))).toBeNull();
	});

	it.each([
		['revision zero', 'r0', 'a'.repeat(64)],
		['revision without prefix', '12', 'a'.repeat(64)],
		['short tree hash', 'r12', 'abc123'],
		['non-hex tree hash', 'r12', 'z'.repeat(64)],
	])('rejects malformed %s', (_label, revision, treeHash) => {
		expect(parseInstalledSkillReceipt(receipt(revision, treeHash))).toBeNull();
	});

	it('rejects metadata tables that are not an install receipt', () => {
		expect(parseInstalledSkillReceipt(receipt().replace('## Skillstore Install Receipt', '## Metadata')))
			.toBeNull();
	});
});
