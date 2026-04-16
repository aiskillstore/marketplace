import { input, select } from '@inquirer/prompts';
import { loadRegistryV3, saveRegistryV3, ensureSkillBundlePath } from '../core/registry-v3.js';
import { ensureDir, writeFile } from '../core/fs-utils.js';
import * as path from 'node:path';
import type { SkillMetaV3 } from '../types/index.js';

function parseCreateArgs(args: string[]): {
  name?: string;
  category?: string;
  displayName?: string;
  description?: string;
  author?: string;
} {
  const result: ReturnType<typeof parseCreateArgs> = {};
  const positional = args.find((a) => !a.startsWith('--'));
  if (positional) result.name = positional;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--category' && args[i + 1]) {
      result.category = args[i + 1];
      i++;
    } else if (args[i] === '--display-name' && args[i + 1]) {
      result.displayName = args[i + 1];
      i++;
    } else if (args[i] === '--description' && args[i + 1]) {
      result.description = args[i + 1];
      i++;
    } else if (args[i] === '--author' && args[i + 1]) {
      result.author = args[i + 1];
      i++;
    }
  }
  return result;
}

function generateSkillMd(opts: { name: string; displayName: string; description: string; author?: string }): string {
  const lines = [
    '---',
    `name: ${opts.name}`,
    `display_name: "${opts.displayName}"`,
    `description: "${opts.description}"`,
    'version: "1.0.0"',
    opts.author ? `author: ${opts.author}` : 'author: unknown',
    '---',
    '',
    `# ${opts.displayName}`,
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

export async function createCommand(args: string[]) {
  const parsed = parseCreateArgs(args);
  const registry = await loadRegistryV3();
  const categories = registry.categories.map((g) => ({ name: g.displayName, value: g.id }));

  if (categories.length === 0) {
    console.log('\u6ca1\u6709\u53ef\u7528\u7684\u5206\u7c7b\uff0c\u8bf7\u5148\u5728 Web \u9762\u677f\u6216 skills.json \u4e2d\u521b\u5efa\u5206\u7c7b\u3002');
    process.exit(1);
  }

  const name =
    parsed.name ||
    (await input({
      message: 'Skill \u6807\u8bc6\u540d\uff08\u5982 my-awesome-skill\uff09\uff1a',
      validate: (value) => {
        if (!value.trim()) return '\u4e0d\u80fd\u4e3a\u7a7a';
        if (!/^[a-z0-9-]+$/.test(value)) return '\u53ea\u80fd\u4f7f\u7528\u5c0f\u5199\u5b57\u6bcd\u3001\u6570\u5b57\u548c\u77ed\u6a2a\u7ebf';
        return true;
      },
    }));

  if (registry.skills.some((s) => s.name === name)) {
    console.log(`Skill "${name}" \u5df2\u5b58\u5728\u4e8e registry/skills.json`);
    process.exit(1);
  }

  const category =
    parsed.category ||
    (await select<string>({
      message: '\u9009\u62e9\u5206\u7c7b\uff1a',
      choices: categories,
    }));

  const displayName = parsed.displayName || (await input({ message: 'Skill \u663e\u793a\u540d\uff08\u53ef\u7559\u7a7a\uff09\uff1a', default: name }));
  const description = parsed.description || (await input({ message: '\u7b80\u8981\u63cf\u8ff0\uff08\u53ef\u7559\u7a7a\uff09\uff1a' }));
  const author = parsed.author || (await input({ message: '\u4f5c\u8005\uff08\u53ef\u7559\u7a7a\uff09\uff1a' }));

  const bundlePath = path.join('bundles', 'skills', name);
  const absoluteBundleDir = path.join(process.cwd(), bundlePath);
  await ensureDir(absoluteBundleDir);

  const skillMd = generateSkillMd({ name, displayName: displayName || name, description, author });
  await writeFile(path.join(absoluteBundleDir, 'SKILL.md'), skillMd, 'utf-8');

  const skill: SkillMetaV3 = {
    name,
    displayName: displayName || name,
    description,
    category,
    tags: [],
    origin: { type: 'bundle', path: bundlePath },
    author: author || 'unknown',
    version: '1.0.0',
    license: 'MIT',
  };

  registry.skills.push(skill);
  await saveRegistryV3(registry);

  console.log(`\n\u2713 \u5df2\u521b\u5efa Skill \u811a\u624b\u67b6\uff1a`);
  console.log(`  Bundle: ${absoluteBundleDir}`);
  console.log(`  Registry: registry/skills.json`);
  console.log('\n\u63d0\u793a\uff1a\u8bf7\u7f16\u8f91 bundle \u4e0b\u7684 SKILL.md \u5185\u5bb9\uff0c\u5b8c\u6210\u540e\u8fd0\u884c open-skills validate \u8fdb\u884c\u6821\u9a8c\u3002');
}
