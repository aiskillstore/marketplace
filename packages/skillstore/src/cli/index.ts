#!/usr/bin/env node

import { defineCommand, runMain } from 'citty';

const main = defineCommand({
	meta: {
		name: 'skillstore',
		version: '0.2.0',
		description: 'Skillstore CLI - Manage AI skills for Claude, Codex, and Claude Code',
	},
	subCommands: {
		// Primary command: add skills or plugins
		add: () => import('../commands/add.js').then((m) => m.default),
		// Alias for backwards compatibility
		install: () => import('../commands/add.js').then((m) => m.default),
		// List installed skills
		list: () => import('../commands/list.js').then((m) => m.default),
		// Check for updates
		check: () => import('../commands/check.js').then((m) => m.default),
		// Update skills
		update: () => import('../commands/update.js').then((m) => m.default),
		// Generate lock file
		'generate-lock': () => import('../commands/generate-lock.js').then((m) => m.default),
		// Plugin management (info, list)
		plugin: () => import('../commands/plugin/index.js').then((m) => m.default),
	},
	setup() {
		// NOTE: Do NOT use consola.wrapAll() - it intercepts process.stdout.write
		// in CI mode and adds [log] prefix, breaking machine-readable output
	},
});

runMain(main);
