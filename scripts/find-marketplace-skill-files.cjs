const fs = require('node:fs');
const path = require('node:path');

// A canonical package owns all descendant bytes, including SKILL.md templates.
// Keep discovering unbound entries so a missing report cannot hide invalid metadata.
function findSkillMdFiles(dir) {
  if (!fs.existsSync(dir)) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const hasFile = (name) => entries.some((entry) => entry.name === name && entry.isFile());
  const segments = dir.split(path.sep);
  const canonicalDepth = segments[0] === 'skills'
    ? segments.length === 2 || segments.length === 3
    : segments[0] === 'pending' && segments.length === 3;
  if (canonicalDepth && hasFile('SKILL.md') && hasFile('skill-report.json')) {
    return [path.join(dir, 'SKILL.md')];
  }
  return entries.flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) return findSkillMdFiles(fullPath);
    return entry.name === 'SKILL.md' ? [fullPath] : [];
  });
}

module.exports = { findSkillMdFiles };
