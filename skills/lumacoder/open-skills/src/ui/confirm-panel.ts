import { select } from '@inquirer/prompts';
import { SkillMeta, InstallScope, EditorPreset } from '../types/index.js';

export async function promptConfirm(
  editors: EditorPreset[],
  scope: InstallScope,
  skills: SkillMeta[]
): Promise<boolean | null> {
  console.log(`\n即将安装/同步以下 ${skills.length} 个 skills`);
  console.log(`目标编辑器: ${editors.map((e) => e.name).join(', ')}`);
  console.log(`安装范围: ${scope === 'global' ? '全局 (Global)' : '本地 (Local)'}`);
  for (const s of skills) {
    console.log(`  ✓ ${s.display_name}`);
  }

  const answer = await select<string>({
    message: '请确认：',
    choices: [
      { name: '确认安装', value: 'confirm' },
      { name: '返回重选', value: 'back' },
      { name: '取消', value: 'cancel' },
    ],
  });

  if (answer === 'confirm') return true;
  if (answer === 'back') return false;
  return null;
}
