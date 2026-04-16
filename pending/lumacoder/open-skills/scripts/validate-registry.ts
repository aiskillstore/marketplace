import { validateRegistry } from '../src/core/validator.js';
import { scanAndAutoRegister } from '../src/core/dev/scaffold.js';

async function main() {
  const { registered } = await scanAndAutoRegister();
  if (registered.length > 0) {
    console.log(`Auto-registered ${registered.length} skill(s) from bundles/:`);
    for (const name of registered) {
      console.log(`  + ${name}`);
    }
    console.log('');
  }

  const errors = await validateRegistry();
  if (errors.length > 0) {
    console.error(`\u2717 Registry validation failed with ${errors.length} error(s):`);
    for (const err of errors) {
      console.error(`  ${err.file}: ${err.message}`);
    }
    process.exit(1);
  }
  console.log('\u2713 Registry validation passed');
}

main();
