import * as path from 'node:path';
import * as os from 'node:os';
import { editorPresets } from '../core/presets/editors.js';
import { loadRegistry } from '../core/registry.js';
import { Engine } from '../core/engine.js';
import { createAdapter } from '../core/adapters/index.js';
import { pathExists, readdir, readFile } from '../core/fs-utils.js';
import { InstallScope, SkillMeta } from '../types/index.js';
import { parseExistingFile } from '../core/marker-system.js';

async function detectInstalledSkills(targetPath: string): Promise<Set<string>> {
  if (!(await pathExists(targetPath))) return new Set();
  const entries = await readdir(targetPath, { withFileTypes: true });
  const names = new Set<string>();
  for (const entry of entries) {
    if (entry.isDirectory()) names.add(entry.name);
  }
  return names;
}

async function readSingleFileSkills(filePath: string): Promise<Set<string>> {
  if (!(await pathExists(filePath))) return new Set();
  const content = await readFile(filePath, 'utf-8');
  const blocks = parseExistingFile(content);
  return new Set(blocks.map((b) => b.source).filter((s): s is string => !!s));
}
export async function updateCommand() {
  const registry = await loadRegistry();
  const allSkills = registry.flatMap((g) => g.skills);
  const skillMap = new Map(allSkills.map((s) => [s.name, s]));

  const results: { editor: string; scope: InstallScope; skills: SkillMeta[] }[] = [];

  for (const preset of editorPresets.filter((p) => p.defaultEnabled)) {
    for (const scope of ['global', 'local'] as InstallScope[]) {
      const base = scope === 'global' ? os.homedir() : process.cwd();
      const targetPath = path.join(base, preset.filePath);

      let installedNames: Set<string>;
      if (preset.type === 'directory') {
        installedNames = await detectInstalledSkills(targetPath);
      } else {
        installedNames = await readSingleFileSkills(targetPath);
      }

      const toUpdate: SkillMeta[] = [];
      for (const name of Array.from(installedNames)) {
        const skill = skillMap.get(name);
        if (skill) toUpdate.push(skill);
      }

      if (toUpdate.length > 0) {
        results.push({ editor: preset.name, scope, skills: toUpdate });
      }
    }
  }

  if (results.length === 0) {
    console.log('未检测到已安装的 skills，无需更新');
    return;
  }

  console.log(`检测到以下编辑器存在已安装 skills：
`);
  for (const r of results) {
    console.log(`${r.editor} (${r.scope}): ${r.skills.map((s) => s.display_name).join(', ')}`);
  }

  console.log('\n正在执行更新...\n');
  const engine = new Engine();
  for (const r of results) {
    const preset = editorPresets.find((p) => p.name === r.editor)!;
    const adapter = createAdapter(preset);
    const res = await engine.process(adapter, r.scope, r.skills);
    const success = res.filter((x) => x.success).length;
    console.log(`${r.editor}: 更新 ${success}/${res.length} 个 skills`);
  }
}
