import { spawnSync } from 'node:child_process';
import fs from 'node:fs';

/**
 * Why --fix should not run here, or null if it's safe.
 *
 * --fix rewrites test files in place with no backup, so the undo path is
 * `git checkout -- <files>`. That only exists if the target is a git repo and
 * the tests aren't already carrying uncommitted edits. Untracked files are
 * fine — they can't be clobbered by an in-place rewrite.
 */
export function fixBlocker(projectDir) {
  if (!fs.existsSync(projectDir) || !fs.statSync(projectDir).isDirectory())
    return `${projectDir} is not an existing directory`;

  const git = (args) =>
    spawnSync('git', args, { cwd: projectDir, encoding: 'utf8', timeout: 60000 });

  const inside = git(['rev-parse', '--is-inside-work-tree']);
  if (inside.error) return 'git is not available, so there is no undo path';
  if (inside.status !== 0 || inside.stdout.trim() !== 'true')
    return 'not a git repository, so there is no undo path';

  const status = git(['status', '--porcelain', '--untracked-files=no']);
  if (status.status !== 0)
    return 'could not read git status, so the undo path is unverified';
  const dirty = status.stdout.trim();
  if (dirty)
    return `the working tree has ${dirty.split('\n').length} uncommitted change(s)`;
  return null;
}
