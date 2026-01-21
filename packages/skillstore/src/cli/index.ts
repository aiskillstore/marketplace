#!/usr/bin/env node

import { defineCommand, runMain } from 'citty';

const main = defineCommand({
	meta: {
		name: 'skillstore',
		version: '0.1.0',
		description: 'Skillstore CLI - Manage AI skills for Claude, Codex, and Claude Code',
	},
	subCommands: {
		// Primary command: install skills or plugins
		install: () => import('../commands/install.js').then((m) => m.default),
		// Plugin management (info, list)
		plugin: () => import('../commands/plugin/index.js').then((m) => m.default),
	},
	setup() {
		// NOTE: Do NOT use consola.wrapAll() - it intercepts process.stdout.write
		// in CI mode and adds [log] prefix, breaking machine-readable output
	},
});

runMain(main);
