import { checkbox } from '@inquirer/prompts';
import { SkillMeta } from '../types/index.js';

export async function promptSkills(
  categoryName: string,
  skills: SkillMeta[]
): Promise<SkillMeta[] | '__back__'> {
  const choices = skills.map((s) => ({
    name: `${s.display_name} \u2014 ${s.description} (${s.author || 'unknown'})`,
    value: s.name,
  }));

  const selectedNames = await checkbox<string>({
    message: `${categoryName} \u2014 \u9009\u62e9\u8981\u5b89\u88c5\u7684 skills\uff08Space \u591a\u9009\uff0cEnter \u786e\u8ba4\uff09\uff1a`,
    choices,
  });

  if (selectedNames.length === 0) return '__back__';
  return skills.filter((s) => selectedNames.includes(s.name));
}
