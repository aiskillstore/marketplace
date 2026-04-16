import { loadRegistryV3 } from './registry-v3.js';
import type { RegistryV3 } from '../types/index.js';

export interface ValidationError {
  file: string;
  message: string;
}

function validateRegistryData(registry: RegistryV3): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!Array.isArray(registry.categories)) {
    errors.push({ file: 'skills.json', message: 'categories must be an array' });
  }
  if (!Array.isArray(registry.skills)) {
    errors.push({ file: 'skills.json', message: 'skills must be an array' });
  }

  const catIds = new Set<string>();
  for (let i = 0; i < registry.categories.length; i++) {
    const cat = registry.categories[i];
    if (!cat.id) errors.push({ file: 'skills.json', message: `categories[${i}].id is required` });
    if (!cat.displayName) errors.push({ file: 'skills.json', message: `categories[${i}].displayName is required` });
    if (catIds.has(cat.id)) errors.push({ file: 'skills.json', message: `duplicate category id: ${cat.id}` });
    catIds.add(cat.id);
  }

  const skillNames = new Set<string>();
  for (let i = 0; i < registry.skills.length; i++) {
    const skill = registry.skills[i];
    if (!skill.name) errors.push({ file: 'skills.json', message: `skills[${i}].name is required` });
    if (!skill.displayName) errors.push({ file: 'skills.json', message: `skills[${i}].displayName is required` });
    if (!skill.description) errors.push({ file: 'skills.json', message: `skills[${i}].description is required` });
    if (!skill.category) errors.push({ file: 'skills.json', message: `skills[${i}].category is required` });
    if (!skill.origin || !skill.origin.type) errors.push({ file: 'skills.json', message: `skills[${i}].origin.type is required` });
    if (skill.category && !catIds.has(skill.category)) {
      errors.push({ file: 'skills.json', message: `unknown category: ${skill.category}` });
    }
    if (skillNames.has(skill.name)) errors.push({ file: 'skills.json', message: `duplicate skill name: ${skill.name}` });
    skillNames.add(skill.name);
  }

  return errors;
}

export async function validateRegistry(): Promise<ValidationError[]> {
  const registry = await loadRegistryV3();
  return validateRegistryData(registry);
}
