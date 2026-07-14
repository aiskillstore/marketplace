import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

export interface InstalledSkillReceipt {
	skillstoreRevision: number;
	treeHash: string;
}

function parseReceipt(content: string): InstalledSkillReceipt | null {
	if (!content.includes('## Skillstore Install Receipt')) return null;

	const values = new Map<string, string>();
	for (const line of content.split(/\r?\n/)) {
		const match = /^\|\s*\*\*([^*]+)\*\*\s*\|\s*(.*?)\s*\|$/.exec(line);
		if (match) values.set(match[1].trim(), match[2].trim().replace(/^`|`$/g, ''));
	}

	const revision = /^r([1-9]\d*)$/.exec(values.get('Skillstore revision') || '');
	const treeHash = values.get('Tree hash') || '';
	if (!revision || !/^[0-9a-f]{64}$/i.test(treeHash)) return null;

	return {
		skillstoreRevision: Number(revision[1]),
		treeHash: treeHash.toLowerCase(),
	};
}

export async function readInstalledSkillReceipt(skillDir: string): Promise<InstalledSkillReceipt | null> {
	for (const filename of ['SKILLSTORE.md', 'README.md']) {
		try {
			const receipt = parseReceipt(await readFile(join(skillDir, filename), 'utf8'));
			if (receipt) return receipt;
		} catch {
			// Try the next generated-receipt filename.
		}
	}
	return null;
}

export { parseReceipt as parseInstalledSkillReceipt };
