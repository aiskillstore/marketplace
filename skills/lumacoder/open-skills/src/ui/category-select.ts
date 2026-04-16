import { select } from '@inquirer/prompts';
import { CategoryGroup } from '../types/index.js';

export async function promptCategory(groups: CategoryGroup[]): Promise<CategoryGroup | null | '__back__'> {
  const choices = groups.map((g) => ({
    name: `${g.displayName} (${g.skills.length})`,
    value: g.id,
  }));

  choices.unshift({ name: '« 返回上一步', value: '__back__' });

  const answer = await select<string>({
    message: '选择分类：',
    choices,
  });

  if (answer === '__back__') return '__back__';
  return groups.find((g) => g.id === answer) || null;
}
