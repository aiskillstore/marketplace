const { readFileSync } = require('node:fs');
const { dirname, relative, resolve, sep } = require('node:path');

const CANONICAL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const SOURCE_REF = /^[0-9a-f]{40,64}$/;

function invalid(name) {
  return `Field "name" must be lowercase alphanumeric with hyphens or match an exact verified path alias (got: ${name})`;
}

function validateSkillName({
  repoRoot,
  skillMdPath,
  name,
  aliasesPath = 'governance/submission-slug-aliases.json',
}) {
  if (typeof name !== 'string') return invalid(String(name));
  if (CANONICAL_NAME.test(name)) return null;

  const root = resolve(repoRoot);
  const relativePath = relative(root, resolve(root, skillMdPath)).split(sep).join('/');
  const [status, owner, baseSlug, file, ...extra] = relativePath.split('/');
  if (!['pending', 'skills'].includes(status) || !owner || !baseSlug || file !== 'SKILL.md' || extra.length > 0) {
    return invalid(name);
  }

  let registry;
  try {
    registry = JSON.parse(readFileSync(resolve(root, aliasesPath), 'utf8'));
  } catch {
    return invalid(name);
  }
  if (registry?.schemaVersion !== 1 || !Array.isArray(registry.aliases)) return invalid(name);

  const aliases = registry.aliases.filter((candidate) => {
    if (!candidate || typeof candidate !== 'object') return false;
    const repositoryOwner = typeof candidate.repository === 'string'
      ? candidate.repository.split('/')[0]
      : '';
    return repositoryOwner === owner && candidate.baseSlug === baseSlug;
  });
  if (aliases.length !== 1) return invalid(name);

  const alias = aliases[0];
  if (alias.expectedName !== name || name !== name.normalize('NFC')
    || !/^[a-z0-9_-]+\/[a-z0-9._-]+$/.test(alias.repository)
    || typeof alias.path !== 'string' || alias.path === ''
    || alias.path !== alias.path.normalize('NFC')
    || alias.path.split('/').some((segment) => segment === '' || segment === '.' || segment === '..')) {
    return invalid(name);
  }

  let report;
  try {
    report = JSON.parse(readFileSync(resolve(dirname(resolve(root, skillMdPath)), 'skill-report.json'), 'utf8'));
  } catch {
    return invalid(name);
  }

  const expectedSlug = `${owner}-${baseSlug}`;
  const sourceRef = report?.meta?.source_ref;
  if (report?.meta?.slug !== expectedSlug || report?.skill?.name !== name || !SOURCE_REF.test(sourceRef)) {
    return invalid(name);
  }
  const encodedPath = alias.path.split('/').map(encodeURIComponent).join('/');
  const expectedSource = `https://github.com/${alias.repository}/tree/${encodeURIComponent(sourceRef)}/${encodedPath}`;
  if (report?.meta?.source_url !== expectedSource && report?.meta?.source_url !== `${expectedSource}/`) {
    return invalid(name);
  }
  return null;
}

module.exports = { validateSkillName };
