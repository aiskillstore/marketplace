#!/usr/bin/env node
/**
 * Batch fix SKILL.md files to conform to Agent Skills Specification
 *
 * Fixes:
 * 1. name field: lowercase alphanumeric + hyphens only (1-64 chars)
 * 2. description field: properly quoted if contains colons
 *
 * Per specification (https://agentskills.io/specification)
 */

const fs = require('fs');
const path = require('path');

const SKIP_DIRS = ['node_modules', '.git', '__pycache__', '.cache', 'dist', 'build'];
const MAX_DEPTH = 5;

// Valid name pattern per specification
const VALID_NAME_PATTERN = /^[a-z0-9]+(-[a-z0-9]+)*$/;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-')
    .slice(0, 64);
}

function isValidName(name) {
  if (!name || typeof name !== 'string') return false;
  if (name.length < 1 || name.length > 64) return false;
  return VALID_NAME_PATTERN.test(name);
}

function findSkillMdFiles(dir, depth = 0) {
  if (depth > MAX_DEPTH) return [];

  const files = [];

  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      if (SKIP_DIRS.includes(entry.name)) continue;

      const fullPath = path.join(dir, entry.name);

      if (entry.isDirectory()) {
        files.push(...findSkillMdFiles(fullPath, depth + 1));
      } else if (entry.name === 'SKILL.md') {
        files.push(fullPath);
      }
    }
  } catch (e) {
    // Skip unreadable directories
  }

  return files;
}

function fixSkillMd(filePath, dryRun = false) {
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    return { status: 'error', error: `Cannot read: ${e.message}` };
  }

  // Check for binary content
  if (content.includes('\x00')) {
    return { status: 'skip', reason: 'binary' };
  }

  // Check for YAML frontmatter
  if (!content.startsWith('---')) {
    return { status: 'error', error: 'Missing YAML frontmatter' };
  }

  const endIndex = content.indexOf('---', 3);
  if (endIndex === -1) {
    return { status: 'error', error: 'Missing closing YAML delimiter' };
  }

  const frontmatter = content.slice(3, endIndex);
  const body = content.slice(endIndex + 3);

  let newFrontmatter = frontmatter;
  const changes = [];

  // Fix 1: name field - must be valid slug
  const nameMatch = frontmatter.match(/^name:\s*["']?(.+?)["']?\s*$/m);
  if (nameMatch) {
    const currentName = nameMatch[1].trim();
    if (!isValidName(currentName)) {
      const validName = slugify(currentName);
      if (validName) {
        newFrontmatter = newFrontmatter.replace(
          /^name:\s*["']?.+?["']?\s*$/m,
          `name: ${validName}`
        );
        changes.push(`name: "${currentName}" → ${validName}`);
      }
    }
  } else {
    // No name field - add one
    const dirName = path.basename(path.dirname(filePath));
    const validName = slugify(dirName);
    newFrontmatter = `name: ${validName}\n${newFrontmatter.trim()}`;
    changes.push(`name: added ${validName}`);
  }

  // Fix 2: description field - quote if contains unescaped colons
  const descMatch = newFrontmatter.match(/^description:\s*(.+)$/m);
  if (descMatch) {
    const descValue = descMatch[1].trim();
    // Check if unquoted and contains a colon (besides being a quoted string)
    const isQuoted = (descValue.startsWith('"') && descValue.endsWith('"')) ||
                     (descValue.startsWith("'") && descValue.endsWith("'"));

    if (!isQuoted && descValue.includes(':')) {
      // Need to quote - escape any existing quotes
      const escaped = descValue.replace(/"/g, '\\"');
      newFrontmatter = newFrontmatter.replace(
        /^description:\s*.+$/m,
        `description: "${escaped}"`
      );
      changes.push(`description: quoted (contains colon)`);
    }
  }

  if (changes.length === 0) {
    return { status: 'ok' };
  }

  if (!dryRun) {
    const newContent = `---${newFrontmatter}---${body}`;
    fs.writeFileSync(filePath, newContent, 'utf8');
  }

  return { status: 'fixed', change: changes.join('; ') };
}

// Main
const args = process.argv.slice(2);
const targetDirs = args.filter(a => !a.startsWith('--'));
const dryRun = args.includes('--dry-run');

if (targetDirs.length === 0) {
  targetDirs.push('./plugins', './pending');
}

console.log(`SKILL.md Fixer (Specification Compliance)`);
console.log(`=========================================`);
console.log(`Targets: ${targetDirs.join(', ')}`);
console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}`);
console.log();

let allFiles = [];
for (const dir of targetDirs) {
  if (fs.existsSync(dir)) {
    allFiles.push(...findSkillMdFiles(dir));
  }
}

console.log(`Found ${allFiles.length} SKILL.md files`);
console.log();

let stats = { ok: 0, fixed: 0, error: 0, skip: 0 };

for (const file of allFiles) {
  const relPath = path.relative('.', file);
  const result = fixSkillMd(file, dryRun);

  switch (result.status) {
    case 'ok':
      stats.ok++;
      break;
    case 'fixed':
      console.log(`[${dryRun ? 'WOULD FIX' : 'FIXED'}] ${relPath}: ${result.change}`);
      stats.fixed++;
      break;
    case 'error':
      console.log(`[ERROR] ${relPath}: ${result.error}`);
      stats.error++;
      break;
    case 'skip':
      stats.skip++;
      break;
  }
}

console.log();
console.log(`Summary:`);
console.log(`  Already valid:    ${stats.ok}`);
console.log(`  ${dryRun ? 'Would fix' : 'Fixed'}:         ${stats.fixed}`);
console.log(`  Errors:           ${stats.error}`);
console.log(`  Skipped (binary): ${stats.skip}`);

if (dryRun && stats.fixed > 0) {
  console.log();
  console.log(`Run without --dry-run to apply fixes.`);
}

process.exit(stats.error > 0 ? 1 : 0);
