import * as path from 'node:path';
import * as os from 'node:os';
import { simpleGit } from 'simple-git';
import { loadRegistryV3 } from '../core/registry-v3.js';
import { ensureDir, emptyDir, remove } from '../core/fs-utils.js';
import { mkdtemp } from '../core/fs-utils.js';
import { copy } from '../core/fs-utils.js';

function parseSyncArgs(args: string[]): { category?: string; name?: string } {
  const result: { category?: string; name?: string } = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--category' && args[i + 1]) {
      result.category = args[i + 1];
      i++;
    } else if (args[i] === '--name' && args[i + 1]) {
      result.name = args[i + 1];
      i++;
    }
  }
  return result;
}

export async function syncCommand(args: string[]) {
  const parsed = parseSyncArgs(args);
  const registry = await loadRegistryV3();
  const skills = registry.skills.filter((s) => {
    if (s.origin.type !== 'git' && s.origin.type !== 'github') return false;
    if (parsed.category && s.category !== parsed.category) return false;
    if (parsed.name && s.name !== parsed.name) return false;
    return true;
  });

  if (skills.length === 0) {
    console.log('\u672a\u627e\u5230\u9700\u8981\u540c\u6b65\u7684\u8fdc\u7a0b skills');
    return;
  }

  for (const skill of skills) {
    const url = skill.origin.type === 'github'
      ? `https://github.com/${skill.origin.ref}.git`
      : skill.origin.url || '';
    if (!url) {
      console.log(`\u8df3\u8fc7 ${skill.name}: \u7f3a\u5c11 git URL`);
      continue;
    }
    const dest = path.join(process.cwd(), skill.origin.path || path.join('bundles', 'skills', skill.name));
    await ensureDir(dest);
    await emptyDir(dest);

    try {
      const git = simpleGit();
      const ref = skill.origin.refName || 'main';
      const subPath = skill.origin.path || undefined;

      if (!subPath) {
        await git.clone(url, dest, ['--depth', '1', '--branch', ref]);
        await remove(path.join(dest, '.git'));
      } else {
        const tmpDir = await mkdtemp(path.join(os.tmpdir(), 'open-skills-sync-'));
        try {
          await git.clone(url, tmpDir, ['--depth', '1', '--branch', ref, '--no-checkout']);
          const repoGit = simpleGit(tmpDir);
          await repoGit.raw(['sparse-checkout', 'init', '--cone']);
          await repoGit.raw(['sparse-checkout', 'set', subPath]);
          await repoGit.checkout(ref);
          const src = path.join(tmpDir, subPath);
          await copy(src, dest);
        } finally {
          await remove(tmpDir);
        }
      }
      console.log(`\u2713 \u5df2\u540c\u6b65 ${skill.name} \u2192 ${dest}`);
    } catch (err: any) {
      console.log(`\u2717 \u540c\u6b65\u5931\u8d25 ${skill.name}: ${err.message || String(err)}`);
    }
  }
}
