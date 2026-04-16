import * as path from 'node:path';
import * as YAML from 'yaml';
import { editorPresets } from '../core/presets/editors.js';
import { loadRegistry } from '../core/registry.js';
import { Engine } from '../core/engine.js';
import { createAdapter } from '../core/adapters/index.js';
import { pathExists, readFile } from '../core/fs-utils.js';
import { InstallScope } from '../types/index.js';

export async function importCommand(inFile: string) {
  if (!(await pathExists(inFile))) {
    console.log(`文件不存在: ${inFile}`);
    process.exit(1);
  }

  const content = await readFile(inFile, 'utf-8');
  const doc = YAML.parse(content);
  const registry = await loadRegistry();
  const allSkills = registry.flatMap((g) => g.skills);
  const skillMap = new Map(allSkills.map((s) => [s.name, s]));

  const stacks: { editor: string; scope: InstallScope; skills: string[] }[] = doc.stacks || [];

  for (const stack of stacks) {
    const preset = editorPresets.find((p) => p.id === stack.editor);
    if (!preset) {
      console.log(`跳过未知编辑器: ${stack.editor}`);
      continue;
    }

    const skills = stack.skills.map((name: string) => skillMap.get(name)).filter((s): s is NonNullable<typeof s> => !!s);
    if (skills.length === 0) continue;

    const adapter = createAdapter(preset);
    const engine = new Engine();
    const res = await engine.process(adapter, stack.scope, skills);
    const success = res.filter((r) => r.success).length;
    console.log(`${preset.name}: 导入 ${success}/${res.length} 个 skills`);
  }
}
