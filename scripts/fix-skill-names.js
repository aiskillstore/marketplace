#!/usr/bin/env node
/**
 * Batch fix SKILL.md name fields to conform to Agent Skills Specification
 *
 * Per specification (https://agentskills.io/specification):
 * - name must be 1-64 characters
 * - name must be lowercase alphanumeric + hyphens only (a-z, 0-9, -)
 * - name must not start or end with hyphen
 * - name must not contain consecutive hyphens (--)
 *
 * This script converts invalid names to valid slugs (e.g., "Writing Hookify Rules" → "writing-hookify-rules")
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
    .replace(/[^a-z0-9]+/g, '-')  // Replace non-alphanumeric with hyphens
    .replace(/^-+|-+$/g, '')       // Remove leading/trailing hyphens
    .replace(/-{2,}/g, '-')        // Replace consecutive hyphens with single
    .slice(0, 64);                 // Max 64 characters
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

  // Parse name field - handle both quoted and unquoted values
  const nameMatch = frontmatter.match(/^name:\s*["']?(.+?)["']?\s*$/m);

  if (!nameMatch) {
    // No name field - use directory name as fallback
    const dirName = path.basename(path.dirname(filePath));
    const validName = slugify(dirName);
    if (!dryRun) {
      const newFrontmatter = `name: ${validName}\n${frontmatter.trim()}`;
      const newContent = `---\n${newFrontmatter}\n---${body}`;
      fs.writeFileSync(filePath, newContent, 'utf8');
    }
    return { status: 'fixed', change: `added name: ${validName}` };
  }

  const currentName = nameMatch[1].trim();

  // Check if already valid
  if (isValidName(currentName)) {
    return { status: 'ok' };
  }

  // Convert to valid slug
  const validName = slugify(currentName);

  if (!validName) {
    return { status: 'error', error: `Cannot slugify: "${currentName}"` };
  }

  if (!dryRun) {
    // Fix name field - preserve quote style if present
    const newFrontmatter = frontmatter.replace(
      /^name:\s*["']?.+?["']?\s*$/m,
      `name: ${validName}`
    );

    const newContent = `---${newFrontmatter}---${body}`;
    fs.writeFileSync(filePath, newContent, 'utf8');
  }

  return { status: 'fixed', change: `"${currentName}" → ${validName}` };
}

// Main
const args = process.argv.slice(2);
const targetDirs = args.filter(a => !a.startsWith('--'));
const dryRun = args.includes('--dry-run');

if (targetDirs.length === 0) {
  targetDirs.push('./plugins', './pending');
}

console.log(`SKILL.md Name Fixer (Specification Compliance)`);
console.log(`==============================================`);
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
console.log(`  Already valid:   ${stats.ok}`);
console.log(`  ${dryRun ? 'Would fix' : 'Fixed'}:        ${stats.fixed}`);
console.log(`  Errors:          ${stats.error}`);
console.log(`  Skipped (binary): ${stats.skip}`);

if (dryRun && stats.fixed > 0) {
  console.log();
  console.log(`Run without --dry-run to apply fixes.`);
}

process.exit(stats.error > 0 ? 1 : 0);
