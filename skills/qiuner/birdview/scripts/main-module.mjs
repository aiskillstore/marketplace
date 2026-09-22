import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
// import.meta.url reports the real path while process.argv[1] keeps the path as invoked, so a skill
// directory reached through a symlink makes the two differ and every CLI block is skipped silently.
// Resolving both sides with the same call keeps them comparable under symlinks, --preserve-symlinks-main
// and Windows path casing; an entry that cannot be resolved simply means this module is not the entry.
export function isMainModule(moduleUrl) {
    const entry = process.argv[1];
    if (!entry)
        return false;
    try {
        return fs.realpathSync(fileURLToPath(moduleUrl)) === fs.realpathSync(entry);
    }
    catch {
        return false;
    }
}
