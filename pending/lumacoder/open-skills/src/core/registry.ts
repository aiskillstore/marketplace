import { loadRegistryV3, toLegacyCategoryGroups } from './registry-v3.js';
import type { CategoryGroup } from '../types/index.js';

export async function loadRegistry(): Promise<CategoryGroup[]> {
  const registry = await loadRegistryV3();
  return toLegacyCategoryGroups(registry);
}

export function getCategoryById(groups: CategoryGroup[], id: string): CategoryGroup | undefined {
  return groups.find((g) => g.id === id);
}
