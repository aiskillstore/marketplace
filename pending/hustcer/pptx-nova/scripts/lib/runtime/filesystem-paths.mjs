import { realpathSync, statSync } from 'node:fs'
import { basename, dirname, isAbsolute, resolve, sep } from 'node:path'

// path.resolve and the JavaScript realpathSync implementation fold symlink/..
// before consulting the filesystem. Resolve that traversal with the OS first.
// Keep the final filename (including a symlink) so sibling assets still belong
// to the submitted file's directory. Windows follows the native CLI's lexical rule.
export function resolveFilesystemPath(value, cwd = process.cwd()) {
  const absolute = isAbsolute(value) ? value : `${cwd}${sep}${value}`
  if (process.platform === 'win32' || !absolute.split('/').includes('..')) return resolve(absolute)

  let parent = dirname(absolute)
  const suffix = [basename(absolute)]
  for (;;) {
    try {
      if (!statSync(parent).isDirectory())
        throw Object.assign(new Error(`Not a directory: ${parent}`), { code: 'ENOTDIR' })
      return resolve(realpathSync.native(parent), ...suffix)
    } catch (error) {
      // New output subdirectories may not exist yet. Do not turn traversal
      // through a missing directory into a different, apparently valid path.
      const leaf = basename(parent)
      if (
        error.code !== 'ENOENT' ||
        !leaf ||
        leaf === '.' ||
        leaf === '..' ||
        suffix.includes('..')
      )
        throw error
      suffix.unshift(leaf)
      parent = dirname(parent)
    }
  }
}
