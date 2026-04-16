import type { IncomingMessage, ServerResponse } from 'node:http';
import type { RegistryV3, SkillMetaV3, CategoryGroupV3 } from '../types/index.js';
import { loadRegistryV3, saveRegistryV3, ensureSkillBundlePath } from '../core/registry-v3.js';
import { resolveGitHub } from '../core/resolvers/github-resolver.js';
import { SkillStoreResolver } from '../core/resolvers/skillstore-resolver.js';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(res: ServerResponse, data: unknown, status = 200) {
  res.writeHead(status, { 'Content-Type': 'application/json', ...CORS_HEADERS });
  res.end(JSON.stringify(data));
}

function error(res: ServerResponse, message: string, status = 400) {
  json(res, { error: message }, status);
}

async function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => resolve(body));
  });
}

export async function handleApi(req: IncomingMessage, res: ServerResponse): Promise<boolean> {
  const url = new URL(req.url || '/', `http://${req.headers.host}`);
  const pathname = url.pathname;

  if (pathname === '/api/registry') {
    if (req.method === 'GET' || req.method === 'OPTIONS') {
      if (req.method === 'OPTIONS') {
        res.writeHead(204, CORS_HEADERS);
        res.end();
        return true;
      }
      const registry = await loadRegistryV3();
      json(res, registry);
      return true;
    }

    if (req.method === 'POST') {
      const body = await readBody(req);
      try {
        const data = JSON.parse(body) as RegistryV3;
        await saveRegistryV3(data);
        json(res, { success: true });
      } catch (e: any) {
        error(res, e.message || 'Invalid JSON');
      }
      return true;
    }
  }

  if (pathname === '/api/resolve' && req.method === 'POST') {
    const body = await readBody(req);
    try {
      const { provider, ref } = JSON.parse(body) as { provider: string; ref: string };
      if (!provider || !ref) {
        error(res, 'Missing provider or ref');
        return true;
      }
      if (provider === 'github') {
        const result = await resolveGitHub(ref);
        json(res, result);
      } else if (provider === 'skillstore') {
        const resolver = new SkillStoreResolver();
        const result = await resolver.resolve(ref);
        json(res, result);
      } else {
        error(res, `Provider ${provider} not implemented yet`);
      }
    } catch (e: any) {
      error(res, e.message || 'Resolve failed');
    }
    return true;
  }

  if (pathname === '/api/validate' && req.method === 'POST') {
    const body = await readBody(req);
    try {
      const data = JSON.parse(body) as RegistryV3;
      const errors = validateRegistry(data);
      json(res, { valid: errors.length === 0, errors });
    } catch (e: any) {
      error(res, e.message || 'Invalid JSON');
    }
    return true;
  }

  return false;
}

function validateRegistry(registry: RegistryV3): { path: string; message: string }[] {
  const errors: { path: string; message: string }[] = [];

  if (!Array.isArray(registry.categories)) {
    errors.push({ path: 'categories', message: 'categories must be an array' });
  }
  if (!Array.isArray(registry.skills)) {
    errors.push({ path: 'skills', message: 'skills must be an array' });
  }

  const catIds = new Set<string>();
  for (let i = 0; i < registry.categories.length; i++) {
    const cat = registry.categories[i];
    if (!cat.id) errors.push({ path: `categories[${i}].id`, message: 'id is required' });
    if (!cat.displayName) errors.push({ path: `categories[${i}].displayName`, message: 'displayName is required' });
    if (catIds.has(cat.id)) errors.push({ path: `categories[${i}].id`, message: `duplicate id: ${cat.id}` });
    catIds.add(cat.id);
  }

  const skillNames = new Set<string>();
  for (let i = 0; i < registry.skills.length; i++) {
    const skill = registry.skills[i];
    if (!skill.name) errors.push({ path: `skills[${i}].name`, message: 'name is required' });
    if (!skill.displayName) errors.push({ path: `skills[${i}].displayName`, message: 'displayName is required' });
    if (!skill.description) errors.push({ path: `skills[${i}].description`, message: 'description is required' });
    if (!skill.category) errors.push({ path: `skills[${i}].category`, message: 'category is required' });
    if (!skill.origin || !skill.origin.type) errors.push({ path: `skills[${i}].origin`, message: 'origin.type is required' });
    if (skill.category && !catIds.has(skill.category)) {
      errors.push({ path: `skills[${i}].category`, message: `unknown category: ${skill.category}` });
    }
    if (skillNames.has(skill.name)) errors.push({ path: `skills[${i}].name`, message: `duplicate name: ${skill.name}` });
    skillNames.add(skill.name);
  }

  return errors;
}
