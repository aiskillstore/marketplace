#!/usr/bin/env node
import { installCommand } from './commands/install.js';
import { listCommand } from './commands/list.js';
import { searchCommand } from './commands/search.js';
import { validateCommand } from './commands/validate.js';
import { syncCommand } from './commands/sync.js';
import { updateCommand } from './commands/update.js';
import { exportCommand } from './commands/export.js';
import { importCommand } from './commands/import.js';
import { devPanelCommand } from './commands/dev-panel.js';
import { createCommand } from './commands/create.js';
import { migrateCommand } from './commands/migrate.js';
import { startDevServer } from './dev-server/server.js';

const args = process.argv.slice(2);
const command = args[0];

async function main() {
  if (args.includes('--dev') || process.env.OPEN_SKILLS_DEV === '1') {
    await startDevServer(3890);
    return;
  }

  switch (command) {
    case 'list':
      await listCommand();
      break;
    case 'search':
      await searchCommand(args.slice(1));
      break;
    case 'validate':
      await validateCommand();
      break;
    case 'sync':
      await syncCommand(args.slice(1));
      break;
    case 'update':
      await updateCommand();
      break;
    case 'export':
      await exportCommand(args[1] || 'stack.yaml');
      break;
    case 'import':
      await importCommand(args[1] || 'stack.yaml');
      break;
    case 'create':
      await createCommand(args.slice(1));
      break;
    case 'migrate':
      await migrateCommand();
      break;
    default:
      await installCommand(args);
      break;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
