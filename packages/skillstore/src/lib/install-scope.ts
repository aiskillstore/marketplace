import { lstat } from 'node:fs/promises';
import { join, relative, resolve, sep } from 'node:path';
import { CANONICAL_SKILLS_DIR, LOCK_FILE_PATH, type AgentConfig } from './agents.js';

export function getInstallScope(global: boolean, cwd = process.cwd()) {
	return {
		canonicalDir: global ? CANONICAL_SKILLS_DIR : join(cwd, '.agents', 'skills'),
		lockFilePath: global ? LOCK_FILE_PATH : join(cwd, '.agents', '.skill-lock.json'),
	};
}

/** A project install must not follow an existing directory link outside its scope. */
export async function validateProjectInstallPaths(targetAgents: AgentConfig[], cwd = process.cwd()) {
	const directories = ['.agents/skills', ...targetAgents.map((agent) => agent.projectPath)];
	for (const directory of directories) {
		const path = relative(resolve(cwd), resolve(cwd, directory));
		if (path.startsWith(`..${sep}`) || path === '..') throw new Error('Invalid project install directory');
		let current = cwd;
		for (const part of path.split(sep)) {
			current = join(current, part);
			try {
				const stat = await lstat(current);
				if (!stat.isDirectory() || stat.isSymbolicLink()) {
					throw new Error(`Project install requires a real directory: ${current}. Preserve the existing path before reinstalling.`);
				}
			} catch (error) {
				if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
			}
		}
	}
	const { lockFilePath } = getInstallScope(false, cwd);
	try {
		const stat = await lstat(lockFilePath);
		if (!stat.isFile() || stat.isSymbolicLink()) throw new Error(`Refusing unsafe project lock path: ${lockFilePath}`);
	} catch (error) {
		if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
	}
}
