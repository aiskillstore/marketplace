#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptPath = fileURLToPath(import.meta.url);
const root = path.resolve(path.dirname(scriptPath), '..');

const PORTABLE_FIELDS = new Set(['name', 'description', 'license', 'compatibility', 'metadata']);
const FIELD = /^([a-z][a-z0-9-]*):(?:\s*(.*))?$/;
const METADATA_FIELD = /^  ([a-z][a-z0-9-]*):\s*(.*)$/;
const SAFE_UNQUOTED_CHARS = /^[A-Za-z0-9 ._/()+@,;'\"’—–-]+$/;
const YAML_LEADING_INDICATORS = new Set(['-', '?', ':', ',', '[', ']', '{', '}', '#', '&', '*', '!', '|', '>', "'", '"', '%', '@', '`']);
const BAD_CHARACTER = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/;

function isUnambiguousUnquotedScalar(value) {
  return SAFE_UNQUOTED_CHARS.test(value)
    && !YAML_LEADING_INDICATORS.has(value[0])
    && !value.includes('#')
    && !value.includes(':');
}

function parseScalar(raw, errors, label, allowUnquoted = true) {
  if (!raw?.trim()) {
    errors.push(`${label} must not be empty`);
    return '';
  }
  if (raw.includes('\t')) errors.push(`${label} must not contain tabs`);
  if (BAD_CHARACTER.test(raw)) errors.push(`${label} must not contain control characters`);

  const value = raw.trim();
  if (value.startsWith('"')) {
    try {
      const parsed = JSON.parse(value);
      if (typeof parsed !== 'string' || parsed.length === 0) throw new Error('not a non-empty string');
      return parsed;
    } catch {
      errors.push(`${label} contains invalid or unsafe quoted syntax`);
      return '';
    }
  }
  if (value.startsWith("'")) {
    if (!/^'(?:[^'\r\n]|'')*'$/.test(value)) {
      errors.push(`${label} contains invalid or unsafe quoted syntax`);
      return '';
    }
    const parsed = value.slice(1, -1).replaceAll("''", "'");
    if (!parsed) errors.push(`${label} must not be empty`);
    return parsed;
  }
  if (!allowUnquoted || !isUnambiguousUnquotedScalar(value)) {
    errors.push(`${label} must be a quoted string or a portable unquoted scalar`);
    return '';
  }
  return value;
}

export function parsePortableFrontmatter(text) {
  const errors = [];
  const values = new Map();
  const metadata = new Map();
  const lines = text.split(/\r?\n/);
  if (lines[0] !== '---') errors.push('frontmatter must start on line 1 with ---');
  const closing = lines.findIndex((line, index) => index > 0 && line === '---');
  if (closing === -1) {
    errors.push('frontmatter must have a closing --- line');
    return { errors, values, metadata };
  }

  let inMetadata = false;
  let afterMetadata = false;
  let sawMetadataContent = false;
  for (const line of lines.slice(1, closing)) {
    if (line.trim() === '') continue;
    if (line.includes('\t')) errors.push('frontmatter must not contain tabs');
    if (BAD_CHARACTER.test(line)) errors.push('frontmatter must not contain control characters');

    if (inMetadata) {
      if (!line.startsWith('  ') || line.startsWith('   ')) {
        errors.push(`metadata must be a one-level mapping: ${line}`);
        continue;
      }
      const item = line.match(METADATA_FIELD);
      if (!item) {
        errors.push(`malformed metadata line: ${line}`);
        continue;
      }
      if (metadata.has(item[1])) errors.push(`duplicate metadata field: ${item[1]}`);
      metadata.set(item[1], parseScalar(item[2], errors, `metadata.${item[1]}`, false));
      sawMetadataContent = true;
      continue;
    }

    const item = line.match(FIELD);
    if (!item) {
      errors.push(`unsupported or malformed frontmatter line: ${line}`);
      continue;
    }
    const [, key, raw] = item;
    if (!PORTABLE_FIELDS.has(key)) errors.push(`non-portable frontmatter field: ${key}`);
    if (values.has(key)) errors.push(`duplicate frontmatter field: ${key}`);
    if (key === 'metadata') {
      if (raw?.trim()) errors.push('metadata must be a one-level mapping');
      inMetadata = true;
      afterMetadata = true;
      values.set(key, metadata);
      continue;
    }
    if (afterMetadata) errors.push(`${key} must precede metadata`);
    values.set(key, parseScalar(raw, errors, key));
  }

  if (values.has('metadata') && !sawMetadataContent) errors.push('metadata must contain at least one string value');
  for (const key of values.keys()) if (key !== 'metadata' && !values.get(key)) errors.push(`${key} must not be empty`);
  const name = values.get('name') ?? '';
  if (name.length < 1 || name.length > 64 || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)) {
    errors.push('name must be 1–64 characters in lower-kebab-case without consecutive hyphens');
  }
  const description = values.get('description') ?? '';
  if (description.length < 1 || description.length > 1024) errors.push('description must contain 1–1024 characters');
  const compatibility = values.get('compatibility') ?? '';
  if (compatibility.length > 500) errors.push('compatibility must contain no more than 500 characters');
  return { errors, values, metadata };
}

export function validatePortableFrontmatter(text) {
  return parsePortableFrontmatter(text).errors;
}

function main() {
  const failures = [];
  const fail = message => failures.push(message);
  const read = relative => fs.readFileSync(path.join(root, relative), 'utf8');
  const exists = relative => fs.existsSync(path.join(root, relative));

  const packageJson = JSON.parse(read('package.json'));
  const skillText = read('SKILL.md');
  const parsed = parsePortableFrontmatter(skillText);
  for (const error of parsed.errors) fail(`SKILL.md ${error}`);
  const frontmatter = parsed.values;
  const name = frontmatter.get('name');
  if (name !== packageJson.name) fail(`SKILL.md name (${name}) must match package name (${packageJson.name})`);
  if (name !== path.basename(root)) fail(`SKILL.md name (${name}) must match repository directory (${path.basename(root)})`);

  const referenced = new Set();
  for (const match of skillText.matchAll(/\[[^\]]+\]\((?!https?:|#)([^)]+)\)/g)) referenced.add(match[1].split('#')[0]);
  for (const match of skillText.matchAll(/(?:^|\s)((?:bin|lib|rules|config)\/[A-Za-z0-9_./-]+)/g)) referenced.add(match[1].replace(/[.,;:]$/, ''));
  for (const relative of referenced) if (!exists(relative)) fail(`SKILL.md references missing file: ${relative}`);

  const duplicateSkills = [];
  const findDuplicateSkills = directory => {
    for (const entry of fs.readdirSync(path.join(root, directory), { withFileTypes: true })) {
      if (['.git', 'node_modules', 'coverage'].includes(entry.name)) continue;
      if (entry.isDirectory() && entry.name.startsWith('.') && directory === '.') continue; // scratch, not skill definitions
      const relative = path.join(directory, entry.name);
      if (entry.isDirectory()) findDuplicateSkills(relative);
      else if (entry.isFile() && entry.name === 'SKILL.md' && relative !== 'SKILL.md') duplicateSkills.push(relative);
    }
  };
  findDuplicateSkills('.');
  for (const duplicate of duplicateSkills) fail(`committed duplicate skill definition may drift: ${duplicate}`);

  const requiredFiles = ['bin/check.mjs', 'lib/cli.mjs', 'rules/catalogue.json', 'config/default.json', 'config/profiles/un-v1.json', 'config/profiles/security.json', 'agents/openai.yaml', 'fonts/RobotoCondensed-Regular.ttf', 'fonts/RobotoCondensed-Bold.ttf', 'fonts/LICENSE-APACHE.txt', 'fonts/NOTICE.txt', 'README.md', 'USER-GUIDE.md', 'COMPATIBILITY.md', 'LICENSE'];
  for (const file of requiredFiles) if (!exists(file)) fail(`required repository file is missing: ${file}`);
  for (const file of requiredFiles) if (!packageJson.files?.some(entry => entry === file || file.startsWith(`${entry}/`))) fail(`package files allowlist omits: ${file}`);

  const compatibility = read('COMPATIBILITY.md');
  const supportedAgents = ['opencode', 'claude-code', 'codex', 'kimi-code-cli', 'cursor', 'gemini-cli', 'windsurf', 'cline', 'github-copilot', 'generic agent skills'];
  for (const agent of supportedAgents) {
    if (!compatibility.toLowerCase().includes(agent)) fail(`COMPATIBILITY.md does not mention ${agent}`);
    if (!read('README.md').toLowerCase().includes(agent)) fail(`README.md does not mention ${agent}`);
  }
  if (!compatibility.includes('25 September 2026')) fail('COMPATIBILITY.md must state its verification date');
  for (const stale of ['Node.js 16', 'Node 16', 'OpenCode 0.', 'skills 1.6.']) {
    for (const file of ['README.md', 'COMPATIBILITY.md', 'SKILL.md', 'MAINTAINING.md', 'CONTRIBUTING.md']) {
      if (read(file).includes(stale)) fail(`${file} contains stale version string: ${stale}`);
    }
  }
  for (const file of ['README.md', 'COMPATIBILITY.md', 'MAINTAINING.md', '.github/workflows/ci.yml']) {
    if (read(file).includes('skills check')) fail(`${file} references an undocumented skills command`);
  }

  const ignored = new Set(['.git', 'node_modules', 'coverage']);
  const visit = directory => {
    for (const entry of fs.readdirSync(path.join(root, directory), { withFileTypes: true })) {
      const relative = path.join(directory, entry.name);
      if (ignored.has(entry.name)) continue;
      if (entry.isDirectory() && entry.name.startsWith('.') && directory === '.') continue; // scratch, not shipped data
      if (entry.isDirectory()) visit(relative);
      else if (entry.isFile() && entry.name.endsWith('.json')) {
        try { JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8')); }
        catch (error) { fail(`invalid JSON in ${relative}: ${error.message}`); }
      }
    }
  };
  visit('.');

  if (failures.length) {
    console.error(`Portability validation failed (${failures.length}):`);
    for (const failure of failures) console.error(`- ${failure}`);
    process.exitCode = 1;
  } else {
    console.log('ok — restricted portable frontmatter, identity, references, package files, host coverage, versions and JSON');
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === scriptPath) main();
