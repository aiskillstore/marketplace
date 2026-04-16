import * as path from 'node:path';
import { pathExists as pathExistsFn, readdir, remove } from './fs-utils.js';

export async function cleanDirectory(
  targetPath: string,
  expectedFiles: Set<string>
): Promise<void> {
  if (!(await pathExistsFn(targetPath))) return;

  const entries = await readdir(targetPath, { withFileTypes: true });

  for (const entry of entries) {
    const entryPath = path.join(targetPath, entry.name);
    if (entry.isDirectory()) {
      await cleanDirectory(entryPath, expectedFiles);
      const remaining = await readdir(entryPath);
      if (remaining.length === 0) {
        await remove(entryPath);
      }
    } else {
      const relative = path.relative(targetPath, entryPath);
      if (!expectedFiles.has(relative) && !expectedFiles.has(entryPath)) {
        await remove(entryPath);
      }
    }
  }
}
