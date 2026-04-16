import { loadRegistry } from '../core/registry.js';

export async function listCommand() {
  const registry = await loadRegistry();
  console.log('可用 skills 列表\n');
  for (const group of registry) {
    console.log(`[${group.displayName}]`);
    for (const skill of group.skills) {
      console.log(`  • ${skill.display_name} (${skill.name}) — ${skill.description}`);
    }
    console.log('');
  }
}
