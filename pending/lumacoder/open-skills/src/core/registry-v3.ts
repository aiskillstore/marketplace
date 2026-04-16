import * as path from 'node:path';
import { readFile, writeFile, pathExists } from './fs-utils.js';
import type { RegistryV3, SkillMetaV3, CategoryGroupV3, SkillMeta, CategoryGroup } from '../types/index.js';

const REGISTRY_PATH = path.join(process.cwd(), 'registry', 'skills.json');

export async function loadRegistryV3(): Promise<RegistryV3> {
  if (!(await pathExists(REGISTRY_PATH))) {
    return {
      version: '3.0.0',
      updatedAt: new Date().toISOString(),
      categories: [],
      skills: [],
    };
  }
  const content = await readFile(REGISTRY_PATH, 'utf-8');
  return JSON.parse(content) as RegistryV3;
}

export async function saveRegistryV3(registry: RegistryV3): Promise<void> {
  registry.updatedAt = new Date().toISOString();
  await writeFile(REGISTRY_PATH, JSON.stringify(registry, null, 2), 'utf-8');
}

export function toLegacySkillMeta(skill: SkillMetaV3): SkillMeta {
  const legacy: SkillMeta = {
    name: skill.name,
    display_name: skill.displayName,
    description: skill.description,
    category: skill.category,
    tags: skill.tags,
    author: skill.author,
    version: skill.version,
    license: skill.license,
    agent: skill.agent,
    transform: skill.transform,
  };

  if (skill.origin.type === 'bundle') {
    legacy.bundle = { path: skill.origin.path || path.join('bundles', 'skills', skill.name) };
  } else if (skill.origin.type === 'git') {
    legacy.source = {
      type: 'git',
      url: skill.origin.url || skill.origin.ref || '',
      path: skill.origin.path,
      ref: skill.origin.refName || 'main',
    };
  } else if (skill.origin.type === 'github') {
    legacy.source = {
      type: 'git',
      url: `https://github.com/${skill.origin.ref}.git`,
      path: skill.origin.path,
      ref: skill.origin.refName || 'main',
    };
  } else {
    // clawhub / skillstore — treat as git for MVP, resolver can override at runtime
    legacy.source = {
      type: 'git',
      url: skill.origin.url || '',
      path: skill.origin.path,
      ref: skill.origin.refName || 'main',
    };
  }

  return legacy;
}

export function toLegacyCategoryGroups(registry: RegistryV3): CategoryGroup[] {
  const categoryMap = new Map<string, CategoryGroupV3>();
  for (const cat of registry.categories) {
    categoryMap.set(cat.id, cat);
  }

  const skillsByCategory = new Map<string, SkillMeta[]>();
  for (const skill of registry.skills) {
    const list = skillsByCategory.get(skill.category) || [];
    list.push(toLegacySkillMeta(skill));
    skillsByCategory.set(skill.category, list);
  }

  const groups: CategoryGroup[] = [];
  const sortedCategories = [...registry.categories].sort((a, b) => a.order - b.order);

  for (const cat of sortedCategories) {
    const skills = skillsByCategory.get(cat.id) || [];
    if (skills.length > 0) {
      groups.push({
        id: cat.id,
        displayName: cat.displayName,
        skills: skills.sort((a, b) => a.display_name.localeCompare(b.display_name)),
      });
    }
  }

  for (const [catId, skills] of Array.from(skillsByCategory)) {
    if (!categoryMap.has(catId)) {
      groups.push({
        id: catId,
        displayName: catId,
        skills: skills.sort((a, b) => a.display_name.localeCompare(b.display_name)),
      });
    }
  }

  return groups;
}

export function getCategoryByIdV3(registry: RegistryV3, id: string): CategoryGroupV3 | undefined {
  return registry.categories.find((c) => c.id === id);
}

export function getSkillByNameV3(registry: RegistryV3, name: string): SkillMetaV3 | undefined {
  return registry.skills.find((s) => s.name === name);
}

export function ensureSkillBundlePath(skill: SkillMetaV3): SkillMetaV3 {
  if (skill.origin.type === 'bundle' && !skill.origin.path) {
    skill.origin.path = path.join('bundles', 'skills', skill.name);
  }
  return skill;
}
