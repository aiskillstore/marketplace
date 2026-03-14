/**
 * Skillstore Static Site - Client-side JS
 * Handles: SPA routing, search/filter, copy-to-clipboard, mobile menu, toast
 */

(function () {
  'use strict';

  /* ===================== DATA ===================== */
  let SKILLS = [];     // populated after fetch
  let currentPage = '';

  /* ===================== ROUTER ===================== */
  function getRoute() {
    const hash = location.hash.replace(/^#\/?/, '');
    if (!hash) return { page: 'home' };
    if (hash === 'browse') return { page: 'browse' };
    if (hash.startsWith('skill/')) return { page: 'detail', slug: hash.slice(6) };
    return { page: 'home' };
  }

  function navigate(href) {
    location.hash = href;
  }

  window.addEventListener('hashchange', render);
  window.addEventListener('load', function () {
    loadSkills().then(render);
  });

  /* ===================== DATA LOADING ===================== */
  async function loadSkills() {
    try {
      const res = await fetch('data/skills.json');
      SKILLS = await res.json();
    } catch (e) {
      console.error('Failed to load skills:', e);
      SKILLS = [];
    }
  }

  /* ===================== RENDER DISPATCH ===================== */
  function render() {
    const route = getRoute();
    const main = document.getElementById('main-content');
    if (!main) return;

    // Update nav active state
    updateNavActive(route.page);

    if (route.page === 'home') {
      currentPage = 'home';
      main.innerHTML = renderHomePage();
      bindHomeEvents();
    } else if (route.page === 'browse') {
      currentPage = 'browse';
      main.innerHTML = renderBrowsePage(SKILLS);
      bindBrowseEvents();
    } else if (route.page === 'detail') {
      currentPage = 'detail';
      const skill = SKILLS.find(s => s.slug === route.slug);
      main.innerHTML = skill ? renderDetailPage(skill) : renderNotFound();
      bindDetailEvents();
    }

    // Scroll to top on page change
    window.scrollTo(0, 0);
  }

  function updateNavActive(page) {
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.remove('active');
    });
    if (page === 'home') {
      document.querySelector('[data-nav="home"]')?.classList.add('active');
    } else if (page === 'browse') {
      document.querySelector('[data-nav="browse"]')?.classList.add('active');
    }
  }

  /* ===================== HELPERS ===================== */
  function riskBadge(level) {
    const labels = { safe: '安全', low: '低风险', medium: '中风险', high: '高风险' };
    const icons = {
      safe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      low:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      medium: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>',
      high: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    };
    const l = level || 'safe';
    return `<span class="badge badge-${l}">${icons[l] || icons.safe}${labels[l] || l}</span>`;
  }

  function toolBadges(tools) {
    if (!tools || !tools.length) return '';
    return tools.map(t => {
      if (t === 'claude') return `<span class="tool-badge tool-badge-claude">Claude</span>`;
      if (t === 'codex')  return `<span class="tool-badge tool-badge-codex">Codex</span>`;
      if (t === 'claude-code') return `<span class="tool-badge tool-badge-cc">Claude Code</span>`;
      return `<span class="tool-badge">${t}</span>`;
    }).join('');
  }

  function skillCard(skill, size) {
    const isLarge = size === 'large';
    return `
<a class="skill-card page-enter" href="#skill/${skill.slug}" onclick="return false" data-href="#skill/${skill.slug}">
  <div class="skill-card-header">
    <div class="skill-icon${isLarge ? ' skill-icon-lg' : ''}">${skill.icon || '📦'}</div>
    <div style="flex:1;min-width:0">
      <div class="skill-name-row">
        <span class="skill-name text-sm font-semibold line-clamp-1">${escHtml(skill.name)}</span>
        ${riskBadge(skill.risk_level)}
      </div>
      <p class="skill-short-desc line-clamp-1">${escHtml(skill.summary || '')}</p>
      <p class="skill-author text-xs">by ${escHtml(skill.author || 'unknown')}</p>
    </div>
  </div>
  ${isLarge ? `<p class="skill-desc line-clamp-2">${escHtml(skill.value_statement || skill.summary || '')}</p>` : ''}
  <div class="skill-card-footer">
    <div class="skill-card-tools">${toolBadges(skill.supported_tools)}</div>
    <span class="card-category">${escHtml(skill.category || '')}</span>
  </div>
</a>`;
  }

  function escHtml(str) {
    return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  /* ===================== HOME PAGE ===================== */
  function renderHomePage() {
    const featured = SKILLS.slice(0, 4);
    const popular  = SKILLS.slice(0, 6);
    const categories = [...new Set(SKILLS.map(s => s.category).filter(Boolean))];

    const catPills = categories.map(c => `
      <button class="pill" data-cat="${escHtml(c)}" onclick="navigateBrowse('${escHtml(c)}')">
        ${catIcon(c)} ${escHtml(c)}
      </button>`).join('');

    return `
<section class="hero">
  <div class="hero-gradient"></div>
  <div class="px-container max-w-7xl">
    <div class="hero-content">
      <div style="display:inline-flex;align-items:center;gap:.5rem;padding:.375rem .75rem;border-radius:9999px;background:var(--accent-bg);color:var(--accent-foreground);font-size:.75rem;font-weight:600;margin-bottom:1rem">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        技能市场
      </div>
      <h1>发现 <span class="gradient-text">AI 技能</span><br>扩展你的智能体</h1>
      <p>浏览精选的 Claude Code、Codex 等 AI 工具技能库，每个技能均经过安全审计。</p>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input type="text" id="hero-search" placeholder="搜索技能…" autocomplete="off">
      </div>
      <div class="category-pills">${catPills}</div>
    </div>
  </div>
</section>

<div class="px-container max-w-7xl" style="padding-bottom:4rem">
  ${featured.length ? `
  <section style="padding:3rem 0 2rem">
    <div class="section-header">
      <div>
        <h2>精选技能</h2>
        <p>由官方维护者精心整理的高质量技能</p>
      </div>
      <a class="section-link" href="#browse" onclick="return false" data-href="#browse">
        查看全部
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
      </a>
    </div>
    <div class="skills-grid cols-4">${featured.map(s => skillCard(s, 'small')).join('')}</div>
  </section>` : ''}

  ${popular.length ? `
  <section class="section" style="padding:3rem 0 2rem">
    <div class="section-header">
      <div>
        <h2>热门技能</h2>
        <p>社区最喜爱的技能集合</p>
      </div>
      <a class="section-link" href="#browse" onclick="return false" data-href="#browse">
        查看全部
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
      </a>
    </div>
    <div class="skills-grid">${popular.map(s => skillCard(s, 'large')).join('')}</div>
  </section>` : ''}

  <section class="section" style="padding:3rem 0 2rem">
    <div class="section-header" style="margin-bottom:2rem">
      <div>
        <h2>为什么选择 Skills4Sec？</h2>
        <p>构建更安全、更智能的 AI 工作流</p>
      </div>
    </div>
    <div class="features">
      <div class="feature-item">
        <div class="feature-icon green">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div>
          <h3 class="font-semibold" style="margin-bottom:.25rem">全面安全审计</h3>
          <p class="text-sm text-muted">每个技能均经过自动化安全扫描，风险等级清晰可见，让你放心使用。</p>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon blue">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        </div>
        <div>
          <h3 class="font-semibold" style="margin-bottom:.25rem">一键安装</h3>
          <p class="text-sm text-muted">简洁的安装命令，支持多个 AI 平台，几秒钟即可开始使用新技能。</p>
        </div>
      </div>
      <div class="feature-item">
        <div class="feature-icon amber">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
        </div>
        <div>
          <h3 class="font-semibold" style="margin-bottom:.25rem">持续更新</h3>
          <p class="text-sm text-muted">技能库持续扩充，紧跟 AI 工具最新发展，始终保持最佳状态。</p>
        </div>
      </div>
    </div>
  </section>
</div>
`;
  }

  function catIcon(cat) {
    const icons = {
      productivity: '⚡',
      documentation: '📝',
      development: '🛠️',
      security: '🔒',
      data: '📊',
    };
    return icons[cat] || '📦';
  }

  function bindHomeEvents() {
    // Hero search → navigate to browse with query
    const heroSearch = document.getElementById('hero-search');
    if (heroSearch) {
      heroSearch.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && this.value.trim()) {
          location.hash = 'browse?q=' + encodeURIComponent(this.value.trim());
        }
      });
    }
    // Delegated click for cards and links
    bindCardClicks(document.getElementById('main-content'));
  }

  window.navigateBrowse = function (cat) {
    location.hash = 'browse?cat=' + encodeURIComponent(cat);
  };

  /* ===================== BROWSE PAGE ===================== */
  function renderBrowsePage(skills) {
    const categories = [...new Set(SKILLS.map(s => s.category).filter(Boolean))];
    const catItems = categories.map(c => `
      <div class="sidebar-item" data-sidebar-cat="${escHtml(c)}">
        <span style="width:1rem;text-align:center">${catIcon(c)}</span>
        <span>${escHtml(c)}</span>
      </div>`).join('');

    const riskLevels = ['safe', 'low', 'medium', 'high'];
    const riskItems = riskLevels.map(r => {
      const labels = { safe: '安全', low: '低风险', medium: '中风险', high: '高风险' };
      return `<div class="sidebar-item" data-sidebar-risk="${r}">
        <span style="width:.625rem;height:.625rem;border-radius:50%;background:${r==='safe'||r==='low'?'#16a34a':r==='medium'?'#d97706':'#dc2626'};display:inline-block;flex-shrink:0"></span>
        <span>${labels[r]}</span>
      </div>`;
    }).join('');

    return `
<div class="browse-layout px-container max-w-7xl">
  <!-- Sidebar -->
  <aside class="browse-sidebar">
    <div class="sidebar-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      <input type="text" id="browse-search" placeholder="搜索技能…" autocomplete="off">
    </div>

    <div class="sidebar-section">
      <p class="sidebar-title">分类</p>
      <div class="sidebar-item active" data-sidebar-cat="all">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
        <span>全部</span>
      </div>
      ${catItems}
    </div>

    <div class="sidebar-section">
      <p class="sidebar-title">安全级别</p>
      ${riskItems}
    </div>
  </aside>

  <!-- Main -->
  <div class="browse-main" style="padding:1.5rem 0 4rem">
    <div class="browse-header">
      <span class="browse-count" id="browse-count">${skills.length} 个技能</span>
      <select class="sort-select" id="browse-sort">
        <option value="default">默认排序</option>
        <option value="name">名称 A-Z</option>
        <option value="risk">风险等级</option>
        <option value="author">作者</option>
      </select>
    </div>
    <div class="skills-grid" id="browse-grid">
      ${skills.map(s => skillCard(s, 'large')).join('')}
    </div>
    <p id="browse-empty" class="text-center text-muted" style="display:none;padding:3rem 0">没有找到匹配的技能</p>
  </div>
</div>
`;
  }

  function bindBrowseEvents() {
    const main = document.getElementById('main-content');
    bindCardClicks(main);

    let activeCategory = 'all';
    let activeRisk = null;
    let searchQ = '';

    // Parse initial state from hash
    const rawHash = location.hash.replace(/^#\/?browse\??/, '');
    const params = new URLSearchParams(rawHash);
    if (params.get('q')) searchQ = params.get('q');
    if (params.get('cat')) activeCategory = params.get('cat');

    const searchInput = document.getElementById('browse-search');
    if (searchInput) {
      searchInput.value = searchQ;
      searchInput.addEventListener('input', function () {
        searchQ = this.value.toLowerCase();
        updateGrid();
      });
    }

    main.addEventListener('click', function (e) {
      const catEl = e.target.closest('[data-sidebar-cat]');
      if (catEl) {
        activeCategory = catEl.dataset.sidebarCat;
        main.querySelectorAll('[data-sidebar-cat]').forEach(el => el.classList.remove('active'));
        catEl.classList.add('active');
        main.querySelectorAll('[data-sidebar-risk]').forEach(el => el.classList.remove('active'));
        activeRisk = null;
        updateGrid();
        return;
      }
      const riskEl = e.target.closest('[data-sidebar-risk]');
      if (riskEl) {
        if (activeRisk === riskEl.dataset.sidebarRisk) {
          activeRisk = null;
          riskEl.classList.remove('active');
        } else {
          main.querySelectorAll('[data-sidebar-risk]').forEach(el => el.classList.remove('active'));
          activeRisk = riskEl.dataset.sidebarRisk;
          riskEl.classList.add('active');
        }
        updateGrid();
      }
    });

    const sortSelect = document.getElementById('browse-sort');
    if (sortSelect) {
      sortSelect.addEventListener('change', updateGrid);
    }

    // Trigger initial filter if params present
    if (searchQ || activeCategory !== 'all') updateGrid();

    function updateGrid() {
      let filtered = SKILLS.filter(s => {
        const matchCat = activeCategory === 'all' || s.category === activeCategory;
        const matchRisk = !activeRisk || s.risk_level === activeRisk;
        const q = searchQ.toLowerCase();
        const matchQ = !q || s.name.toLowerCase().includes(q) || (s.summary || '').toLowerCase().includes(q) || (s.author || '').toLowerCase().includes(q) || (s.tags || []).some(t => t.toLowerCase().includes(q));
        return matchCat && matchRisk && matchQ;
      });

      const sort = sortSelect?.value || 'default';
      if (sort === 'name') filtered.sort((a,b) => a.name.localeCompare(b.name));
      else if (sort === 'risk') filtered.sort((a,b) => riskOrder(a.risk_level) - riskOrder(b.risk_level));
      else if (sort === 'author') filtered.sort((a,b) => (a.author||'').localeCompare(b.author||''));

      const grid = document.getElementById('browse-grid');
      const empty = document.getElementById('browse-empty');
      const count = document.getElementById('browse-count');
      if (grid) grid.innerHTML = filtered.map(s => skillCard(s, 'large')).join('');
      if (empty) empty.style.display = filtered.length ? 'none' : 'block';
      if (count) count.textContent = filtered.length + ' 个技能';
      bindCardClicks(grid);
    }
  }

  function riskOrder(r) {
    return { safe: 0, low: 1, medium: 2, high: 3 }[r] ?? 99;
  }

  /* ===================== DETAIL PAGE ===================== */
  function renderDetailPage(skill) {
    const tools = toolBadges(skill.supported_tools);
    const capabilities = (skill.actual_capabilities || []).map(c => `<li>${escHtml(c)}</li>`).join('');
    const useCases = (skill.use_cases || []).map(u => `
      <div style="padding:1rem;border:1px solid var(--border);border-radius:var(--radius);background:var(--muted)">
        <p class="text-xs text-muted" style="margin-bottom:.25rem">${escHtml(u.target_user || '')}</p>
        <p class="font-semibold text-sm" style="margin-bottom:.25rem">${escHtml(u.title || '')}</p>
        <p class="text-sm text-muted">${escHtml(u.description || '')}</p>
      </div>`).join('');
    const prompts = (skill.prompt_templates || []).map(p => `
      <div style="padding:1rem;border:1px solid var(--border);border-radius:var(--radius);margin-bottom:.75rem">
        <p class="font-semibold text-sm" style="margin-bottom:.25rem">${escHtml(p.title || '')}</p>
        <p class="text-xs text-muted" style="margin-bottom:.5rem">${escHtml(p.scenario || '')}</p>
        <div class="clone-cmd" data-copy="${escHtml(p.prompt || '')}">
          <code>${escHtml(p.prompt || '')}</code>
          <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        </div>
      </div>`).join('');

    const installCmd = `gh skill install ${escHtml(skill.slug)}`;

    return `
<div class="detail-page px-container max-w-7xl" style="padding-bottom:4rem">
  <nav class="breadcrumb">
    <a href="#" onclick="return false" data-href="#">首页</a>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
    <a href="#browse" onclick="return false" data-href="#browse">技能</a>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 18 6-6-6-6"/></svg>
    <span>${escHtml(skill.name)}</span>
  </nav>

  <!-- Header Card -->
  <div class="detail-header">
    <div class="detail-top">
      <div class="skill-icon skill-icon-lg">${skill.icon || '📦'}</div>
      <div class="detail-info">
        <div style="display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;margin-bottom:.5rem">
          <h1>${escHtml(skill.name)}</h1>
          ${riskBadge(skill.risk_level)}
        </div>
        <p class="detail-meta">v${escHtml(skill.version || '1.0.0')} · by <strong>${escHtml(skill.author || 'unknown')}</strong> · ${escHtml(skill.license || '')} · ${escHtml(skill.category || '')}</p>
        <p class="detail-desc">${escHtml(skill.value_statement || skill.summary || '')}</p>
        <div class="detail-tools">
          <span class="text-xs text-muted">支持平台：</span>
          ${tools}
        </div>
      </div>
    </div>
    <div class="install-box">
      <div class="clone-cmd" data-copy="${installCmd}" style="flex:1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0;color:var(--muted-foreground)"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
        <code>$ ${installCmd}</code>
        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
      </div>
      <a class="btn-secondary" href="${escHtml(skill.source_url || '#')}" target="_blank" rel="noopener">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.38.6.11.82-.26.82-.57v-2c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5 1 .1-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 016 0c2.3-1.55 3.3-1.23 3.3-1.23.66 1.65.24 2.87.12 3.17.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.69.83.57C20.57 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/></svg>
        查看源码
      </a>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr;gap:1.5rem">
    <div style="display:grid;grid-template-columns:1fr;gap:1.5rem">
      ${capabilities ? `
      <div class="install-steps">
        <h2 class="font-semibold" style="margin-bottom:1rem">功能特性</h2>
        <ul style="padding-left:1.25rem;color:var(--secondary-foreground)">
          ${capabilities}
        </ul>
      </div>` : ''}

      ${useCases ? `
      <div class="install-steps">
        <h2 class="font-semibold" style="margin-bottom:1rem">使用场景</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.75rem">
          ${useCases}
        </div>
      </div>` : ''}

      ${prompts ? `
      <div class="install-steps">
        <h2 class="font-semibold" style="margin-bottom:1rem">提示词模板</h2>
        ${prompts}
      </div>` : ''}
    </div>
  </div>
</div>
`;
  }

  function bindDetailEvents() {
    bindCardClicks(document.getElementById('main-content'));
    // Copy command boxes
    document.querySelectorAll('.clone-cmd[data-copy]').forEach(el => {
      el.addEventListener('click', function () {
        const text = this.dataset.copy;
        copyText(text);
      });
    });
  }

  function renderNotFound() {
    return `<div style="text-align:center;padding:8rem 1rem">
      <p style="font-size:4rem;margin-bottom:1rem">🔍</p>
      <h2 style="font-size:1.5rem;font-weight:700;margin-bottom:.5rem">技能未找到</h2>
      <p class="text-muted" style="margin-bottom:1.5rem">该技能可能已被移除或链接有误。</p>
      <a class="btn-install" href="#browse" onclick="return false" data-href="#browse" style="padding:.75rem 1.5rem;font-size:.875rem">浏览所有技能</a>
    </div>`;
  }

  /* ===================== DELEGATED CARD CLICKS ===================== */
  function bindCardClicks(container) {
    if (!container) return;
    container.addEventListener('click', function (e) {
      const link = e.target.closest('[data-href]');
      if (link) {
        e.preventDefault();
        const href = link.dataset.href;
        if (href) location.hash = href.replace(/^#\/?/, '');
      }
    });
  }

  /* ===================== COPY ===================== */
  function copyText(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => showToast('已复制到剪贴板'));
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast('已复制到剪贴板');
    }
  }

  /* ===================== TOAST ===================== */
  function showToast(msg) {
    let toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), 2500);
  }

  /* ===================== MOBILE MENU ===================== */
  const mobileBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', function () {
      const open = mobileMenu.style.display === 'block';
      mobileMenu.style.display = open ? 'none' : 'block';
    });
    mobileMenu.addEventListener('click', function (e) {
      const link = e.target.closest('a[href]');
      if (link) mobileMenu.style.display = 'none';
    });
  }
})();
