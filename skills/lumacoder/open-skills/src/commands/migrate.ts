import * as path from 'node:path';
import * as fs from 'node:fs/promises';
import * as YAML from 'yaml';
import { pathExists, ensureDir } from '../core/fs-utils.js';
import { saveRegistryV3 } from '../core/registry-v3.js';
import type { RegistryV3, SkillMetaV3, CategoryGroupV3 } from '../types/index.js';

const REGISTRY_DIR = path.join(process.cwd(), 'registry');
const BACKUP_DIR = path.join(REGISTRY_DIR, '_v2_backup');

export async function migrateCommand() {
  const indexPath = path.join(REGISTRY_DIR, '_index.yaml');
  if (!(await pathExists(indexPath))) {
    console.log('未找到 V2 的 registry/_index.yaml，无需迁移。');
    process.exit(0);
  }

  const indexContent = await fs.readFile(indexPath, 'utf-8');
  const indexParsed = YAML.parse(indexContent) as { categories?: { id: string; display_name: string; order: number }[] };

  const categories: CategoryGroupV3[] = (indexParsed.categories || []).map((c) => ({
    id: c.id,
    displayName: c.display_name,
    order: c.order,
  }));

  const entries = await fs.readdir(REGISTRY_DIR);
  const yamlFiles = entries.filter((f) => (f.endsWith('.yaml') || f.endsWith('.yml')) && f !== '_index.yaml');

  const skills: SkillMetaV3[] = [];
  for (const file of yamlFiles) {
    const content = await fs.readFile(path.join(REGISTRY_DIR, file), 'utf-8');
    const parsed = YAML.parse(content);

    const origin: SkillMetaV3['origin'] = { type: 'bundle', path: '' };
    if (parsed.source) {
      origin.type = parsed.source.type === 'git' ? 'git' : 'git';
      origin.url = parsed.source.url;
      origin.path = parsed.source.path;
      origin.refName = parsed.source.ref;
    } else if (parsed.bundle) {
      origin.type = 'bundle';
      origin.path = parsed.bundle.path;
    }

    skills.push({
      name: parsed.name,
      displayName: parsed.display_name || parsed.name,
      description: parsed.description || '',
      category: parsed.category,
      tags: parsed.tags || [],
      origin,
      author: parsed.author,
      version: parsed.version,
      license: parsed.license,
      agent: parsed.agent,
      transform: parsed.transform,
    });
  }

  const registry: RegistryV3 = {
    version: '3.0.0',
    updatedAt: new Date().toISOString(),
    categories,
    skills,
  };

  await saveRegistryV3(registry);

  // Backup V2 files
  await ensureDir(BACKUP_DIR);
  for (const file of [...yamlFiles, '_index.yaml']) {
    const src = path.join(REGISTRY_DIR, file);
    const dest = path.join(BACKUP_DIR, file);
    if (await pathExists(src)) {
      await fs.rename(src, dest);
    }
  }

  console.log(`\u2713 迁移完成：${skills.length} 个 skills，${categories.length} 个分类`);
  console.log(`\u2713 已生成 registry/skills.json`);
  console.log(`\u2713 V2 文件已备份到 registry/_v2_backup/`);
}
