import { select } from '@inquirer/prompts';
import { InstallScope } from '../types/index.js';

export async function promptScope(): Promise<InstallScope | '__back__'> {
  const answer = await select<string>({
    message: '\u9009\u62e9\u5b89\u88c5\u8303\u56f4\uff1a',
    choices: [
      { name: '\u5168\u5c40\u5b89\u88c5 (Global)', value: 'global' },
      { name: '\u672c\u5730\u5b89\u88c5 (Local)', value: 'local' },
      { name: '\u00ab \u8fd4\u56de\u4e0a\u4e00\u6b65', value: '__back__' },
    ],
  });
  if (answer === '__back__') return '__back__';
  return answer as InstallScope;
}
