import * as path from 'node:path';
import { ensureDir, writeFile } from '../../core/fs-utils.js';
import { BaseAdapter } from './base-adapter.js';
import type { InstallScope, SkillMeta, InstallResult } from '../../types/index.js';

export class ClaudeAdapter extends BaseAdapter {
  generateHeaderContent(): string {
    return '';
  }

  transformSkillContent(content: string): string {
    return content;
  }

  shouldGenerateIndex(): boolean {
    return true;
  }

  shouldCopySkillDirectory(): boolean {
    return true;
  }

  async generateOutput(
    scope: InstallScope,
    skills: SkillMeta[],
    skillContents: Map<string, string>
  ): Promise<InstallResult[]> {
    const targetPath = this.getTargetPath(scope);
    const results: InstallResult[] = [];

    for (const skill of skills) {
      const destDir = path.join(targetPath, skill.name);
      await ensureDir(destDir);

      const content = skillContents.get(skill.name) || '';
      const skillMdPath = path.join(destDir, 'SKILL.md');
      await writeFile(skillMdPath, content, 'utf-8');

      results.push({
        skill,
        success: true,
        message: `Written to ${skillMdPath}`,
        targetPath: skillMdPath,
      });
    }

    if (this.shouldGenerateIndex()) {
      await this.generateIndex(targetPath, skills);
    }

    return results;
  }

  private async generateIndex(targetPath: string, skills: SkillMeta[]): Promise<void> {
    const lines = [
      '# Skills Index',
      '',
      ...skills.map((s) => `- [${s.display_name}](./${s.name}/SKILL.md) — ${s.description}`),
      '',
    ];
    await writeFile(path.join(targetPath, 'index.md'), lines.join('\n'), 'utf-8');
  }
}
