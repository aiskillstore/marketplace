#!/usr/bin/env node

import {
	existsSync,
	lstatSync,
	readdirSync,
	rmdirSync,
	unlinkSync,
} from 'node:fs';
import {
	isAbsolute,
	relative,
	resolve,
	sep,
} from 'node:path';
import { pathToFileURL } from 'node:url';

function isWithin(parentDir, candidatePath) {
	const rel = relative(parentDir, candidatePath);
	return rel === '' || (!rel.startsWith(`..${sep}`) && rel !== '..' && !isAbsolute(rel));
}

export function removeEmptySkillFiles({ roots, workspaceRoot }) {
	const workspace = resolve(workspaceRoot);
	if (!Array.isArray(roots) || roots.length === 0) {
		throw new Error('at least one root path is required');
	}
	const absoluteRoots = roots.map((root) => {
		if (typeof root !== 'string' || root.trim() === '' || root.startsWith('--')) {
			throw new Error(`invalid root path: ${root ?? ''}`);
		}
		const absoluteRoot = resolve(workspace, root);
		if (!isWithin(workspace, absoluteRoot)) {
			throw new Error(`root path escapes workspace: ${root}`);
		}
		return absoluteRoot;
	});

	let deletedFiles = 0;
	for (const root of absoluteRoots) {
		if (!existsSync(root)) continue;
		const rootStat = lstatSync(root);
		if (!rootStat.isDirectory() || rootStat.isSymbolicLink()) {
			throw new Error(`root path must be a regular directory inside workspace: ${root}`);
		}

		const walk = (dir) => {
			for (const entry of readdirSync(dir, { withFileTypes: true })) {
				const fullPath = resolve(dir, entry.name);
				if (!isWithin(root, fullPath)) {
					throw new Error(`discovered path escapes root: ${fullPath}`);
				}
				if (entry.isSymbolicLink()) continue;
				if (entry.isDirectory()) {
					walk(fullPath);
					continue;
				}
				if (!entry.isFile() || entry.name !== 'SKILL.md') continue;

				const stat = lstatSync(fullPath);
				if (!stat.isFile() || stat.isSymbolicLink() || stat.size !== 0) continue;
				unlinkSync(fullPath);
				deletedFiles++;
				try {
					rmdirSync(dir);
				} catch (error) {
					if (!['ENOTEMPTY', 'EEXIST'].includes(error?.code)) throw error;
				}
			}
		};
		walk(root);
	}

	return { deletedFiles };
}

function parseArguments(argv) {
	const options = { roots: [] };
	for (let index = 0; index < argv.length; index++) {
		const arg = argv[index];
		if (arg === '--workspace') {
			const value = argv[++index];
			if (!value || value.startsWith('--')) throw new Error('--workspace requires a path');
			options.workspaceRoot = value;
		} else if (arg === '--root') {
			const value = argv[++index];
			if (!value || value.startsWith('--')) throw new Error('--root requires a path');
			options.roots.push(value);
		} else if (arg === '--help' || arg === '-h') {
			options.help = true;
		} else {
			throw new Error(`Unknown argument: ${arg}`);
		}
	}
	if (!options.help && !options.workspaceRoot) throw new Error('--workspace is required');
	if (!options.help && options.roots.length === 0) throw new Error('at least one --root is required');
	return options;
}

function printHelp() {
	console.log(`Usage:
  node scripts/remove-empty-skill-files.mjs \
    --workspace <workspace> \
    --root <skills-or-pending> [--root <path> ...]
`);
}

function runCli(argv) {
	const options = parseArguments(argv);
	if (options.help) {
		printHelp();
		return 0;
	}
	const result = removeEmptySkillFiles(options);
	console.log(`Deleted ${result.deletedFiles} zero-byte SKILL.md file(s)`);
	return 0;
}

const invokedPath = process.argv[1] ? pathToFileURL(resolve(process.argv[1])).href : '';
if (invokedPath === import.meta.url) {
	try {
		process.exitCode = runCli(process.argv.slice(2));
	} catch (error) {
		console.error(`ERROR ${error.message}`);
		process.exitCode = 2;
	}
}
