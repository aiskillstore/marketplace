import * as path from 'node:path';
import * as os from 'node:os';
import { simpleGit } from 'simple-git';
import type { BaseAdapter } from './adapters/base-adapter.js';
import type { InstallScope, SkillMeta, InstallResult } from '../types/index.js';
import { transformSkillContent } from './transformer.js';
import { cleanDirectory } from './cleaner.js';
import { mkdtemp, readFile, remove } from './fs-utils.js';

export class Engine {
  async process(
    adapter: BaseAdapter,
    scope: InstallScope,
    skills: SkillMeta[]
  ): Promise<InstallResult[]> {
    const skillContents = new Map<string, string>();

    for (const skill of skills) {
      const content = await this.downloadSkill(skill);
      const transformed = transformSkillContent(content, skill, adapter.id);
      skillContents.set(skill.name, transformed);
    }

    if (adapter.getOutputType() === 'directory') {
      const targetPath = adapter.getTargetPath(scope);
      const expectedFiles = new Set<string>();
      for (const skill of skills) {
        expectedFiles.add(path.join(skill.name, 'SKILL.md'));
      }
      expectedFiles.add('index.md');
      await cleanDirectory(targetPath, expectedFiles);
    }

    return adapter.generateOutput(scope, skills, skillContents);
  }

  private async downloadSkill(skill: SkillMeta): Promise<string> {
    if (skill.source) {
      if (skill.source.type === 'git') {
        return await this.downloadFromGit(skill);
      } else if (skill.source.type === 'local') {
        return await readFile(skill.source.url, 'utf-8');
      } else {
        throw new Error(`Unsupported source type: ${skill.source.type}`);
      }
    } else if (skill.bundle) {
      const bundlePath = path.join(process.cwd(), skill.bundle.path, 'SKILL.md');
      return await readFile(bundlePath, 'utf-8');
    }
    throw new Error('No source or bundle defined');
  }

  private async downloadFromGit(skill: SkillMeta): Promise<string> {
    const git = simpleGit();
    const url = skill.source!.url;
    const ref = skill.source!.ref || 'main';
    const subPath = skill.source!.path;

    if (!subPath) {
      const tmpDir = await mkdtemp(path.join(os.tmpdir(), 'open-skills-'));
      try {
        await git.clone(url, tmpDir, ['--depth', '1', '--branch', ref]);
        return await readFile(path.join(tmpDir, 'SKILL.md'), 'utf-8');
      } finally {
        await remove(tmpDir);
      }
    }

    const tmpDir = await mkdtemp(path.join(os.tmpdir(), 'open-skills-'));
    try {
      await git.clone(url, tmpDir, ['--depth', '1', '--branch', ref, '--no-checkout']);
      const repoGit = simpleGit(tmpDir);
      await repoGit.raw(['sparse-checkout', 'init', '--cone']);
      await repoGit.raw(['sparse-checkout', 'set', subPath]);
      await repoGit.checkout(ref);
      return await readFile(path.join(tmpDir, subPath, 'SKILL.md'), 'utf-8');
    } finally {
      await remove(tmpDir);
    }
  }
}
