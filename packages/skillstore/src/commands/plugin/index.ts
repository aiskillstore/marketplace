import { defineCommand } from 'citty';

export default defineCommand({
	meta: {
		name: 'plugin',
		description: 'Plugin management commands - install and manage skill collections',
	},
	subCommands: {
		install: () => import('./install.js').then((m) => m.default),
		info: () => import('./info.js').then((m) => m.default),
		list: () => import('./list.js').then((m) => m.default),
	},
});
