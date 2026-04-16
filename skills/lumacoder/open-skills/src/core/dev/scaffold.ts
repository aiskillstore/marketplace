import * as path from 'node:path';
import { ensureDir, writeFile, pathExists, readdir } from '../fs-utils.js';
import { loadRegistryV3, saveRegistryV3 } from '../registry-v3.js';
import type { SkillMetaV3 } from '../../types/index.js';

const BUNDLES_DIR = path.join(process.cwd(), 'bundles');

export interface ScaffoldOptions {
  name: string;
  category: string;
  displayName?: string;
  description?: string;
  author?: string;
}

export async function createSkillScaffold(options: ScaffoldOptions): Promise<string> {
  const { name, category, displayName, description, author } = options;
  const bundleDir = path.join(BUNDLES_DIR, 'skills', name);

  const registry = await loadRegistryV3();
  if (registry.skills.some((s) => s.name === name)) {
    throw new Error(`Skill "${name}" already registered in registry/skills.json`);
  }

  await ensureDir(bundleDir);

  const skillMdContent = generateSkillMd({ name, displayName, description, author });
  await writeFile(path.join(bundleDir, 'SKILL.md'), skillMdContent, 'utf-8');

  const skill: SkillMetaV3 = {
    name,
    displayName: displayName || name,
    description: description || '',
    category,
    tags: [],
    origin: { type: 'bundle', path: path.join('bundles', 'skills', name) },
    author: author || 'unknown',
    version: '1.0.0',
    license: 'MIT',
  };

  registry.skills.push(skill);
  await saveRegistryV3(registry);

  return bundleDir;
}

function generateSkillMd(opts: { name: string; displayName?: string; description?: string; author?: string }): string {
  const lines = [
    '---',
    `name: ${opts.name}`,
    `display_name: "${opts.displayName || opts.name}"`,
    `description: "${opts.description || ''}"`,
    'version: "1.0.0"',
    opts.author ? `author: ${opts.author}` : 'author: unknown',
    '---',
    '',
    `# ${opts.displayName || opts.name}`,
    '',
    opts.description || 'Add your skill description here.',
    '',
    '## Rules',
    '',
    '1. ...',
    '',
  ];
  return lines.join('\n');
}

export async function scanAndAutoRegister(): Promise<{ registered: string[]; skipped: string[] }> {
  const registered: string[] = [];
  const skipped: string[] = [];
  const skillsDir = path.join(BUNDLES_DIR, 'skills');

  if (!(await pathExists(skillsDir))) {
    return { registered, skipped };
  }

  const registry = await loadRegistryV3();
  const existingNames = new Set(registry.skills.map((s) => s.name));

  const skillDirs = await readdir(skillsDir, { withFileTypes: true });

  for (const skillDir of skillDirs.filter((d) => d.isDirectory())) {
    const skillName = skillDir.name;
    if (existingNames.has(skillName)) {
      skipped.push(skillName);
      continue;
    }

    const hasSkillMd = await pathExists(path.join(skillsDir, skillName, 'SKILL.md'));
    if (!hasSkillMd) {
      skipped.push(`${skillName} (missing SKILL.md)`);
      continue;
    }

    registry.skills.push({
      name: skillName,
      displayName: skillName,
      description: `Auto-registered skill for ${skillName}`,
      category: '__uncategorized__',
      tags: [],
      origin: {
        type: 'bundle',
        path: path.join('bundles', 'skills', skillName),
      },
      version: '1.0.0',
      license: 'MIT',
    });
    registered.push(skillName);
  }

  if (registered.length > 0) {
    await saveRegistryV3(registry);
  }

  return { registered, skipped };
}
