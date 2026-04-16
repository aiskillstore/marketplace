import type { SkillMeta } from '../types/index.js';

export function transformSkillContent(
  content: string,
  skill: SkillMeta,
  editorId: string
): string {
  const rules = skill.transform?.[editorId];
  if (!rules) return content;

  let result = content;

  if (rules.inject_header) {
    result = rules.inject_header + result;
  }

  if (rules.remove_frontmatter && rules.remove_frontmatter.length > 0) {
    result = removeFrontmatterFields(result, rules.remove_frontmatter);
  }

  if (rules.map_tools && Object.keys(rules.map_tools).length > 0) {
    result = mapToolNames(result, rules.map_tools);
  }

  if (rules.strip_bash_preamble) {
    result = stripBashPreamble(result);
  }

  return result;
}

function removeFrontmatterFields(content: string, fields: string[]): string {
  const lines = content.split('\n');
  if (lines[0]?.trim() !== '---') return content;

  const endIndex = lines.findIndex((line, idx) => idx > 0 && line.trim() === '---');
  if (endIndex === -1) return content;

  const frontmatter = lines.slice(1, endIndex);
  const filtered = frontmatter.filter((line) => {
    const key = line.split(':')[0]?.trim();
    return !fields.includes(key);
  });

  return ['---', ...filtered, '---', ...lines.slice(endIndex + 1)].join('\n');
}

function mapToolNames(content: string, map: Record<string, string>): string {
  let result = content;
  for (const [from, to] of Object.entries(map)) {
    const regex = new RegExp(`\\b${from}\\b`, 'g');
    result = result.replace(regex, to);
  }
  return result;
}

function stripBashPreamble(content: string): string {
  return content.replace(/^#!\/bin\/bash\n/, '');
}
