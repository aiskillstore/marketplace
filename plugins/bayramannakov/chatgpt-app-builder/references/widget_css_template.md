# Widget CSS Template

Production-ready CSS template with all Apps SDK UI design tokens pre-configured.

Copy this template to your widget's `<style>` section for instant ChatGPT-native styling.

---

## Complete CSS Template

```css
/* ============================================
   Design Tokens (Apps SDK UI)
   ============================================ */
:root {
  /* Gray Scale (0-1000) */
  --gray-0: #ffffff;
  --gray-50: #fafafa;
  --gray-100: #f5f5f5;
  --gray-150: #eeeeee;
  --gray-200: #e5e5e5;
  --gray-300: #d4d4d4;
  --gray-400: #a3a3a3;
  --gray-500: #737373;
  --gray-600: #525252;
  --gray-700: #404040;
  --gray-800: #262626;
  --gray-900: #171717;
  --gray-1000: #0a0a0a;

  /* Semantic Colors (Light Mode) */
  --color-text: var(--gray-1000);
  --color-text-secondary: var(--gray-500);
  --color-text-tertiary: var(--gray-400);
  --color-bg: var(--gray-0);
  --color-bg-soft: var(--gray-100);
  --color-border: var(--gray-200);

  /* Status Colors */
  --color-success: #16a34a;
  --color-success-soft: #dcfce7;
  --color-warning: #ca8a04;
  --color-warning-soft: #fef9c3;
  --color-danger: #dc2626;
  --color-danger-soft: #fee2e2;
  --color-info: #2563eb;
  --color-info-soft: #dbeafe;

  /* Radius Scale */
  --radius-2xs: 2px;
  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 10px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;

  /* Spacing Scale (4px increments) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* Typography */
  --font-sans: ui-sans-serif, -apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
}

/* ============================================
   Dark Mode Overrides
   ============================================ */
.dark-mode {
  --color-text: var(--gray-0);
  --color-text-secondary: var(--gray-400);
  --color-text-tertiary: var(--gray-500);
  --color-bg: var(--gray-900);
  --color-bg-soft: var(--gray-800);
  --color-border: var(--gray-700);
}

/* ============================================
   Base Styles
   ============================================ */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
  background: var(--color-bg);
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ============================================
   Typography
   ============================================ */
.text-primary { color: var(--color-text); }
.text-secondary { color: var(--color-text-secondary); }
.text-tertiary { color: var(--color-text-tertiary); }

.text-sm { font-size: 12px; }
.text-base { font-size: 14px; }
.text-lg { font-size: 16px; }
.text-xl { font-size: 18px; }
.text-2xl { font-size: 24px; }

.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }

/* Section Headers (uppercase labels) */
.section-header {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-3);
}

/* ============================================
   Cards
   ============================================ */
.card {
  background: var(--color-bg-soft);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

.card-bordered {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

/* ============================================
   Avatars
   ============================================ */
.avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-weight: 600;
  flex-shrink: 0;
}

.avatar-sm { width: 24px; height: 24px; font-size: 10px; }
.avatar-md { width: 32px; height: 32px; font-size: 12px; }
.avatar-lg { width: 40px; height: 40px; font-size: 14px; }
.avatar-xl { width: 48px; height: 48px; font-size: 16px; }

/* Avatar with image */
.avatar img {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-full);
  object-fit: cover;
}

/* Avatar colors (soft variant) */
.avatar-secondary {
  background: var(--gray-200);
  color: var(--gray-700);
}

.dark-mode .avatar-secondary {
  background: var(--gray-700);
  color: var(--gray-200);
}

.avatar-success {
  background: var(--color-success-soft);
  color: var(--color-success);
}

/* ============================================
   Badges / Tags / Pills
   ============================================ */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-2);
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-full);
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
}

.badge-success {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.badge-warning {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.badge-danger {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

.badge-info {
  background: var(--color-info-soft);
  color: var(--color-info);
}

/* Tags container (for skills, keywords, etc.) */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* ============================================
   Buttons
   ============================================ */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-2) var(--space-3);
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--gray-900);
  color: var(--gray-0);
}

.dark-mode .btn-primary {
  background: var(--gray-100);
  color: var(--gray-900);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--color-bg-soft);
  color: var(--color-text);
}

.btn-secondary:hover {
  background: var(--gray-200);
}

.dark-mode .btn-secondary:hover {
  background: var(--gray-700);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
}

.btn-ghost:hover {
  background: var(--color-bg-soft);
  color: var(--color-text);
}

/* ============================================
   Loading States
   ============================================ */

/* LoadingDots - SDK Style */
.loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  animation: dotPulse 1.4s ease-in-out infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dotPulse {
  0%, 80%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}

/* Loading container */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

/* ============================================
   Copy Button with Feedback
   ============================================ */
.copy-btn {
  opacity: 0;
  padding: var(--space-1) var(--space-2);
  font-size: 11px;
  font-weight: 500;
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
  border: none;
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.item:hover .copy-btn,
.row:hover .copy-btn,
.card:hover .copy-btn {
  opacity: 1;
}

.copy-btn:hover {
  background: var(--gray-200);
  color: var(--color-text);
}

.dark-mode .copy-btn:hover {
  background: var(--gray-700);
}

.copy-btn.copied {
  background: var(--color-success);
  color: white;
  opacity: 1;
}

/* ============================================
   Show More/Less Toggle
   ============================================ */
.hidden-item {
  display: none;
}

.show-more-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.show-more-btn:hover {
  color: var(--color-text);
}

/* ============================================
   Links
   ============================================ */
a {
  color: var(--color-text);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

a:hover {
  opacity: 0.7;
}

.link-external {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text-secondary);
}

.link-external:hover {
  color: var(--color-text);
  opacity: 1;
}

/* ============================================
   Lists
   ============================================ */
.list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.list-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--color-bg-soft);
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.list-item:hover {
  background: var(--gray-150);
}

.dark-mode .list-item:hover {
  background: var(--gray-700);
}

/* ============================================
   Grid Layouts
   ============================================ */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

@media (max-width: 400px) {
  .grid-2, .grid-3 {
    grid-template-columns: 1fr;
  }
}

/* ============================================
   Stat Cards (for metrics)
   ============================================ */
.stat {
  text-align: center;
  padding: var(--space-3);
  background: var(--color-bg-soft);
  border-radius: var(--radius-md);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

/* ============================================
   Empty States
   ============================================ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  text-align: center;
  color: var(--color-text-tertiary);
}

.empty-state-icon {
  font-size: 32px;
  margin-bottom: var(--space-3);
}

.empty-state-text {
  font-size: 14px;
}

/* ============================================
   Utility Classes
   ============================================ */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }

.mt-2 { margin-top: var(--space-2); }
.mt-3 { margin-top: var(--space-3); }
.mt-4 { margin-top: var(--space-4); }
.mb-2 { margin-bottom: var(--space-2); }
.mb-3 { margin-bottom: var(--space-3); }
.mb-4 { margin-bottom: var(--space-4); }

.p-2 { padding: var(--space-2); }
.p-3 { padding: var(--space-3); }
.p-4 { padding: var(--space-4); }

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

---

## Usage

### HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    /* Paste the CSS template above */
  </style>
</head>
<body>
  <div id="root"></div>

  <script>
    // Theme detection
    function updateTheme() {
      const theme = window.openai?.theme || 'light';
      document.body.classList.toggle('dark-mode', theme === 'dark');
    }

    updateTheme();
    window.addEventListener('openai:set_globals', updateTheme);
  </script>
</body>
</html>
```

### Example Components

```html
<!-- Loading State -->
<div class="loading">
  <div class="loading-dots">
    <span></span><span></span><span></span>
  </div>
</div>

<!-- Avatar -->
<div class="avatar avatar-lg avatar-secondary">JD</div>

<!-- Badge/Tag -->
<span class="badge">JavaScript</span>
<span class="badge badge-success">Active</span>

<!-- Card with Copy Button -->
<div class="card">
  <div class="flex justify-between items-center">
    <span>john@example.com</span>
    <button class="copy-btn" onclick="handleCopy('john@example.com', this)">Copy</button>
  </div>
</div>

<!-- List with Show More -->
<div class="list" id="skills-list">
  <div class="list-item">Item 1</div>
  <div class="list-item">Item 2</div>
  <div class="list-item">Item 3</div>
  <div class="list-item hidden-item">Item 4</div>
  <div class="list-item hidden-item">Item 5</div>
</div>
<button class="show-more-btn" onclick="toggleShowMore()">Show 2 more</button>
```

---

## Related Resources

- [Apps SDK UI Design Tokens](./apps_sdk_ui_tokens.md)
- [Widget UI Patterns](./widget_ui_patterns.md)
- [Widget Development Guide](./widget_development.md)
