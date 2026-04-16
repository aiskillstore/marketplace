import { checkbox } from '@inquirer/prompts';
import { EditorPreset } from '../types/index.js';

export async function promptEditor(editors: EditorPreset[]): Promise<EditorPreset[]> {
  const choices = editors.map((e) => ({
    name: `${e.name} ${e.type === 'directory' ? '→ directory' : '→ ' + e.filePath}`,
    value: e.id,
  }));

  const selectedIds = await checkbox<string>({
    message: '选择目标编辑器/Agent（Space 多选，Enter 确认）：',
    choices,
    required: true,
  });

  return editors.filter((e) => selectedIds.includes(e.id));
}
