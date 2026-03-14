#!/usr/bin/env node
/**
 * Build script for the skills4sec static site.
 *
 * What it does:
 *  1. Scans skills/ for skill-report.json files
 *  2. Builds docs/data/skills.json (normalized skill data)
 *  3. Writes docs/index.html (the SPA shell)
 *
 * Usage:  node scripts/build-site.js
 */

const fs   = require('fs');
const path = require('path');

const ROOT       = path.resolve(__dirname, '..');
const SKILLS_DIR = path.join(ROOT, 'skills');
const DOCS_DIR   = path.join(ROOT, 'docs');
const DATA_DIR   = path.join(DOCS_DIR, 'data');

/* ── Helpers ─────────────────────────────────────────── */
function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); }
  catch { return null; }
}

/* ── 1. Collect skills ───────────────────────────────── */
function collectSkills() {
  const skills = [];
  if (!fs.existsSync(SKILLS_DIR)) return skills;

  for (const entry of fs.readdirSync(SKILLS_DIR)) {
    const dir = path.join(SKILLS_DIR, entry);
    if (!fs.statSync(dir).isDirectory()) continue;

    const reportPath = path.join(dir, 'skill-report.json');
    if (!fs.existsSync(reportPath)) continue;

    const report = readJson(reportPath);
    if (!report) continue;

    const s  = report.skill        || {};
    const sa = report.security_audit || {};
    const c  = report.content       || {};
    const m  = report.meta          || {};

    skills.push({
      slug:              m.slug          || entry,
      name:              s.name          || entry,
      summary:           s.summary       || s.description || '',
      description:       s.description   || '',
      icon:              s.icon          || '📦',
      version:           s.version       || '1.0.0',
      author:            s.author        || 'unknown',
      license:           s.license       || '',
      category:          s.category      || '',
      tags:              s.tags          || [],
      supported_tools:   s.supported_tools || [],
      risk_factors:      s.risk_factors  || [],
      risk_level:        sa.risk_level   || 'safe',
      is_blocked:        sa.is_blocked   || false,
      safe_to_publish:   sa.safe_to_publish !== false,
      source_url:        m.source_url    || '',
      source_type:       m.source_type   || '',
      generated_at:      m.generated_at  || '',
      // content fields
      user_title:        c.user_title    || '',
      value_statement:   c.value_statement || '',
      actual_capabilities: c.actual_capabilities || [],
      use_cases:         c.use_cases     || [],
      prompt_templates:  c.prompt_templates || [],
      limitations:       c.limitations   || [],
      faq:               c.faq           || [],
    });
  }

  // Sort: safe/low first, then by name
  skills.sort((a, b) => {
    const riskOrder = { safe: 0, low: 1, medium: 2, high: 3 };
    const rd = (riskOrder[a.risk_level] ?? 9) - (riskOrder[b.risk_level] ?? 9);
    if (rd !== 0) return rd;
    return a.name.localeCompare(b.name);
  });

  return skills;
}

/* ── 2. Write docs/data/skills.json ─────────────────── */
function writeSkillsJson(skills) {
  ensureDir(DATA_DIR);
  const dest = path.join(DATA_DIR, 'skills.json');
  fs.writeFileSync(dest, JSON.stringify(skills, null, 2), 'utf8');
  console.log(`✓ Wrote ${dest} (${skills.length} skills)`);
}

/* ── 3. Write docs/index.html ────────────────────────── */
function writeIndexHtml(skills) {
  ensureDir(DOCS_DIR);

  // Build <title> and <meta> description
  const totalCount = skills.length;
  const categories = [...new Set(skills.map(s => s.category).filter(Boolean))];
  const catList    = categories.join('、') || 'AI';

  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skills4Sec — AI 技能市场</title>
  <meta name="description" content="发现 ${totalCount} 个经过安全审计的 AI 技能，涵盖 ${catList} 等分类，适用于 Claude Code、Codex 等主流 AI 工具。">
  <meta property="og:title" content="Skills4Sec — AI 技能市场">
  <meta property="og:description" content="经过安全审计的 AI 技能库，一键安装，扩展 AI 工作流。">
  <meta property="og:type" content="website">
  <link rel="stylesheet" href="assets/style.css">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
</head>
<body>
  <!-- Navigation -->
  <nav class="nav">
    <div class="max-w-7xl px-container">
      <div class="nav-inner">
        <a class="nav-logo" href="#" onclick="return false" data-href="#">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#6366f1"/>
            <path d="M17.5 7L9 17.5h7L14.5 25 23 14.5h-7L17.5 7z" fill="white"/>
          </svg>
          <span>Skills4Sec</span>
        </a>

        <div class="nav-links">
          <a class="nav-link active" href="#" onclick="return false" data-href="#" data-nav="home">首页</a>
          <a class="nav-link" href="#browse" onclick="return false" data-href="#browse" data-nav="browse">浏览技能</a>
        </div>

        <div class="nav-right">
          <a class="nav-github" href="https://github.com/cxm95/skills4sec" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.38.6.11.82-.26.82-.57v-2c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5 1 .1-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 016 0c2.3-1.55 3.3-1.23 3.3-1.23.66 1.65.24 2.87.12 3.17.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.69.83.57C20.57 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/></svg>
            <span class="text-sm">GitHub</span>
          </a>
          <button class="nav-mobile-btn" id="mobile-menu-btn" aria-label="菜单">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile dropdown -->
    <div id="mobile-menu" style="display:none;border-top:1px solid var(--border);background:var(--card);padding:.5rem 1rem 1rem">
      <a class="sidebar-item" href="#" onclick="return false" data-href="#">首页</a>
      <a class="sidebar-item" href="#browse" onclick="return false" data-href="#browse">浏览技能</a>
      <a class="sidebar-item" href="https://github.com/cxm95/skills4sec" target="_blank" rel="noopener">GitHub</a>
    </div>
  </nav>

  <!-- Main content (SPA) -->
  <main id="main-content" role="main"></main>

  <!-- Footer -->
  <footer class="footer">
    <div class="max-w-7xl px-container">
      <div class="footer-inner">
        <div class="nav-logo">
          <svg width="24" height="24" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#6366f1"/><path d="M17.5 7L9 17.5h7L14.5 25 23 14.5h-7L17.5 7z" fill="white"/></svg>
          <span style="font-weight:600">Skills4Sec</span>
        </div>
        <div class="footer-links">
          <a href="https://github.com/cxm95/skills4sec" target="_blank" rel="noopener">GitHub</a>
          <a href="#browse" onclick="return false" data-href="#browse">浏览技能</a>
        </div>
        <p class="footer-copy">&copy; 2026 Skills4Sec. 保留所有权利。</p>
      </div>
    </div>
  </footer>

  <!-- Toast container is created dynamically by app.js -->
  <script src="assets/app.js"></script>
</body>
</html>
`;

  const dest = path.join(DOCS_DIR, 'index.html');
  fs.writeFileSync(dest, html, 'utf8');
  console.log(`✓ Wrote ${dest}`);
}

/* ── Main ────────────────────────────────────────────── */
(function main() {
  console.log('Building skills4sec static site…');
  const skills = collectSkills();
  writeSkillsJson(skills);
  writeIndexHtml(skills);
  console.log(`\nDone! Open docs/index.html in your browser.`);
})();
