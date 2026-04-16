import type { MarkerBlock } from '../types/index.js';

export function createFileMarker(params: { editor: string; version: string; content: string }): MarkerBlock {
  const raw = `<!-- OPEN-SKILLS:BEGIN-FILE editor="${params.editor}" version="${params.version}" -->\n${params.content}\n<!-- OPEN-SKILLS:END-FILE -->`;
  return { type: 'file', content: params.content, raw };
}

export function createSourceMarker(params: { source: string; count: number; content: string }): MarkerBlock {
  const raw = `<!-- OPEN-SKILLS:BEGIN-SOURCE source="${params.source}" count="${params.count}" -->\n${params.content}\n<!-- OPEN-SKILLS:END-SOURCE source="${params.source}" -->`;
  return { type: 'source', source: params.source, count: params.count, content: params.content, raw };
}

export function createRuleMarker(params: { source: string; id: string; priority: string; content: string }): MarkerBlock {
  const raw = `<!-- OPEN-SKILLS:BEGIN-RULE source="${params.source}" id="${params.id}" priority="${params.priority}" -->\n${params.content}\n<!-- OPEN-SKILLS:END-RULE -->`;
  return { type: 'rule', source: params.source, id: params.id, priority: params.priority, content: params.content, raw };
}

export function parseExistingFile(content: string): MarkerBlock[] {
  const blocks: MarkerBlock[] = [];
  const fileRegex = /<!-- OPEN-SKILLS:BEGIN-FILE[^>]*>\n([\s\S]*?)\n<!-- OPEN-SKILLS:END-FILE -->/;
  const fileMatch = content.match(fileRegex);
  if (!fileMatch) return [];

  const inner = fileMatch[1];
  const sourceRegex = /<!-- OPEN-SKILLS:BEGIN-SOURCE source="([^"]+)" count="(\d+)" -->\n([\s\S]*?)\n<!-- OPEN-SKILLS:END-SOURCE source="\1" -->/g;
  let m: RegExpExecArray | null;
  while ((m = sourceRegex.exec(inner)) !== null) {
    blocks.push({
      type: 'source',
      source: m[1],
      count: parseInt(m[2], 10),
      content: m[3],
      raw: m[0],
    });
  }

  return blocks;
}

export function serializeBlocks(blocks: MarkerBlock[]): string {
  return blocks.map((b) => b.raw).join('\n\n');
}
