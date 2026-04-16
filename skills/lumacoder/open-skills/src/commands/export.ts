import * as path from 'node:path';
import * as os from 'node:os';
import * as YAML from 'yaml';
import { editorPresets } from '../core/presets/editors.js';
import { loadRegistry } from '../core/registry.js';
import { pathExists, readdir, writeFile } from '../core/fs-utils.js';
import { InstallScope, SkillMeta } from '../types/index.js';

async function detectInstalledSkills(targetPath: string): Promise<Set<string>> {
  if (!(await pathExists(targetPath))) return new Set();
  const entries = await readdir(targetPath, { withFileTypes: true });
  const names = new Set<string>();
  for (const entry of entries) {
    if (entry.isDirectory()) names.add(entry.name);
  }
  return names;
}

export async function exportCommand(outFile: string) {
  const registry = await loadRegistry();
  const allSkills = registry.flatMap((g) => g.skills);
  const skillMap = new Map(allSkills.map((s) => [s.name, s]));

  const stacks: { editor: string; scope: InstallScope; skills: string[] }[] = [];

  for (const preset of editorPresets.filter((p) => p.defaultEnabled)) {
    for (const scope of ['global', 'local'] as InstallScope[]) {
      const base = scope === 'global' ? os.homedir() : process.cwd();
      const targetPath = path.join(base, preset.filePath);
      if (preset.type === 'directory') {
        const installed = await detectInstalledSkills(targetPath);
        const skillNames = Array.from(installed).filter((n) => skillMap.has(n));
        if (skillNames.length > 0) {
          stacks.push({ editor: preset.id, scope, skills: skillNames });
        }
      }
    }
  }

  const output = {
    version: '1.0.0',
    generatedAt: new Date().toISOString(),
    stacks,
  };

  await writeFile(outFile, YAML.stringify(output), 'utf-8');
  console.log(`已导出当前 stack 到 ${path.resolve(outFile)}`);
}
