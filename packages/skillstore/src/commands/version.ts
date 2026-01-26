import { defineCommand } from 'citty';

const VERSION = '0.2.0';

export default defineCommand({
	meta: {
		name: 'version',
		description: 'Show skillstore version',
	},
	run() {
		console.log(`skillstore v${VERSION}`);
	},
});
