import { promptEditor } from '../ui/editor-select.js';
import { promptScope } from '../ui/scope-select.js';
import { promptCategory } from '../ui/category-select.js';
import { promptSkills } from '../ui/skill-select.js';
import { promptConfirm } from '../ui/confirm-panel.js';
import { loadRegistry } from '../core/registry.js';
import { Engine } from '../core/engine.js';
import { createAdapter } from '../core/adapters/index.js';
import { editorPresets } from '../core/presets/editors.js';
import { InstallScope, SkillMeta, CategoryGroup, EditorPreset } from '../types/index.js';

interface InstallArgs {
  editors?: string[];
  category?: string;
  scope?: InstallScope;
}

function parseArgs(args: string[]): InstallArgs {
  const result: InstallArgs = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--editor' && args[i + 1]) {
      result.editors = args[i + 1].split(',').map((s) => s.trim());
      i++;
    } else if (args[i] === '--category' && args[i + 1]) {
      result.category = args[i + 1];
      i++;
    } else if (args[i] === '--scope' && args[i + 1]) {
      result.scope = args[i + 1] as InstallScope;
      i++;
    }
  }
  return result;
}

const STEP_EDITOR = 0;
const STEP_SCOPE = 1;
const STEP_CATEGORY = 2;
const STEP_SKILL = 3;
const STEP_CONFIRM = 4;
const STEP_INSTALL = 5;

export async function installCommand(args: string[] = []) {
  const parsed = parseArgs(args);
  const registry = await loadRegistry();

  let step = parsed.editors
    ? parsed.scope
      ? parsed.category
        ? STEP_SKILL
        : STEP_CATEGORY
      : STEP_SCOPE
    : STEP_EDITOR;

  let selectedEditors: EditorPreset[] = parsed.editors
    ? editorPresets.filter((p) => parsed.editors!.includes(p.id))
    : [];
  let scope: InstallScope | null = parsed.scope || null;
  let category: CategoryGroup | null = parsed.category
    ? registry.find((g) => g.id === parsed.category) || null
    : null;
  let selectedSkills: SkillMeta[] = [];

  if (parsed.editors && selectedEditors.length === 0) {
    console.log('未找到指定的编辑器');
    process.exit(1);
  }
  if (parsed.category && !category) {
    console.log('未找到指定的分类');
    process.exit(1);
  }

  while (step <= STEP_CONFIRM) {
    if (step === STEP_EDITOR) {
      selectedEditors = await promptEditor(editorPresets.filter((p) => p.defaultEnabled));
      if (selectedEditors.length === 0) {
        console.log('未选择编辑器，已取消');
        process.exit(0);
      }
      step = STEP_SCOPE;
      continue;
    }

    if (step === STEP_SCOPE) {
      const scopeResult = await promptScope();
      if (scopeResult === '__back__') {
        step = STEP_EDITOR;
        continue;
      }
      scope = scopeResult;
      step = STEP_CATEGORY;
      continue;
    }

    if (step === STEP_CATEGORY) {
      const catResult = await promptCategory(registry);
      if (catResult === '__back__') {
        step = STEP_SCOPE;
        continue;
      }
      if (!catResult) {
        console.log('已取消');
        process.exit(0);
      }
      category = catResult;
      step = STEP_SKILL;
      continue;
    }

    if (step === STEP_SKILL && category) {
      const skillResult = await promptSkills(category.displayName, category.skills);
      if (skillResult === '__back__') {
        step = STEP_CATEGORY;
        continue;
      }
      selectedSkills = skillResult;
      step = STEP_CONFIRM;
      continue;
    }

    if (step === STEP_CONFIRM) {
      const confirm = await promptConfirm(selectedEditors, scope!, selectedSkills);
      if (confirm === null) {
        console.log('已取消');
        process.exit(0);
      }
      if (confirm === false) {
        step = STEP_SKILL;
        continue;
      }
      step = STEP_INSTALL;
      break;
    }
  }

  console.log(`\n正在安装 ${selectedSkills.length} 个 skills 到 ${selectedEditors.length} 个编辑器...\n`);
  const engine = new Engine();
  const results: { skill: SkillMeta; success: boolean; message: string }[] = [];

  for (const preset of selectedEditors) {
    const adapter = createAdapter(preset);
    const res = await engine.process(adapter, scope!, selectedSkills);
    results.push(...res);
  }

  const success = results.filter((r) => r.success);
  const failed = results.filter((r) => !r.success);

  console.log(`安装完成：成功 ${success.length}，失败 ${failed.length}`);
  for (const r of failed) {
    console.log(`✗ ${r.skill.display_name}: ${r.message}`);
  }
  for (const r of success) {
    console.log(`✓ ${r.skill.display_name}: ${r.message}`);
  }
}
