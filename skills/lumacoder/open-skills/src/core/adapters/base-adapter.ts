import * as path from 'node:path';
import * as os from 'node:os';
import type { InstallScope, SkillMeta, EditorPreset, InstallResult } from '../../types/index.js';

export abstract class BaseAdapter {
  constructor(public preset: EditorPreset) {}

  get id(): string {
    return this.preset.id;
  }

  get name(): string {
    return this.preset.name;
  }

  getOutputType(): 'file' | 'directory' {
    return this.preset.type;
  }

  getTargetPath(scope: InstallScope): string {
    const base = scope === 'global' ? os.homedir() : process.cwd();
    return path.join(base, this.preset.filePath);
  }

  abstract generateHeaderContent(skills: SkillMeta[]): string;
  abstract transformSkillContent(content: string, skill: SkillMeta): string;
  abstract shouldGenerateIndex(): boolean;
  abstract shouldCopySkillDirectory(): boolean;

  async generateOutput(
    scope: InstallScope,
    skills: SkillMeta[],
    skillContents: Map<string, string>
  ): Promise<InstallResult[]> {
    throw new Error('generateOutput must be implemented by subclass');
  }
}
