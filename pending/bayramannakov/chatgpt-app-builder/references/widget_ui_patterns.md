# Widget UI Patterns

Common UI patterns for ChatGPT App widgets with copy-paste code.

---

## LoadingDots Animation

CSS-only loading indicator matching SDK style:

### CSS
```css
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

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
```

### HTML
```html
<div class="loading">
  <div class="loading-dots">
    <span></span><span></span><span></span>
  </div>
</div>
```

### JavaScript (Dynamic Creation)
```javascript
function createLoadingDots() {
  const loading = document.createElement('div');
  loading.className = 'loading';

  const dots = document.createElement('div');
  dots.className = 'loading-dots';

  // Create three span elements for dots
  for (let i = 0; i < 3; i++) {
    dots.appendChild(document.createElement('span'));
  }

  loading.appendChild(dots);
  return loading;
}
```

---

## Copy Button with Feedback

### CSS
```css
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

/* Show on hover of parent */
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
```

### JavaScript
```javascript
function handleCopy(text, button) {
  navigator.clipboard.writeText(text).then(() => {
    const originalText = button.textContent;
    button.classList.add('copied');
    button.textContent = 'Copied!';

    setTimeout(() => {
      button.classList.remove('copied');
      button.textContent = originalText;
    }, 1500);
  });
}
```

### HTML
```html
<div class="item">
  <span class="item-text">john@example.com</span>
  <button class="copy-btn" onclick="handleCopy('john@example.com', this)">Copy</button>
</div>
```

---

## Show More/Less Expandable Sections

### CSS
```css
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
```

### JavaScript
```javascript
function setupShowMore(containerId, visibleCount) {
  const container = document.getElementById(containerId);
  const items = container.querySelectorAll('.item');
  const hiddenCount = items.length - visibleCount;

  if (hiddenCount <= 0) return;

  // Hide excess items
  items.forEach((item, i) => {
    if (i >= visibleCount) {
      item.classList.add('hidden-item');
    }
  });

  // Create toggle button
  const btn = document.createElement('button');
  btn.className = 'show-more-btn';
  btn.textContent = `Show ${hiddenCount} more`;
  btn.dataset.expanded = 'false';

  btn.onclick = () => {
    const isExpanded = btn.dataset.expanded === 'true';

    items.forEach((item, i) => {
      if (i >= visibleCount) {
        item.classList.toggle('hidden-item', isExpanded);
      }
    });

    btn.dataset.expanded = String(!isExpanded);
    btn.textContent = isExpanded
      ? `Show ${hiddenCount} more`
      : 'Show less';

    // CRITICAL: Notify parent of height change
    updateHeight();
  };

  container.parentNode.insertBefore(btn, container.nextSibling);
}

// Call after DOM ready
setupShowMore('experience-list', 3);
setupShowMore('education-list', 2);
```

### HTML
```html
<div class="section">
  <h3 class="section-header">Experience</h3>
  <div id="experience-list">
    <div class="item">Job 1</div>
    <div class="item">Job 2</div>
    <div class="item">Job 3</div>
    <div class="item">Job 4</div>
    <div class="item">Job 5</div>
  </div>
  <!-- Button inserted by JS -->
</div>
```

---

## Height Management

**Critical**: Always notify the parent container after DOM changes.

### JavaScript
```javascript
function updateHeight() {
  // Calculate actual height (minimum 200px)
  const height = Math.max(document.body.scrollHeight, 200);

  // Notify ChatGPT of new height
  if (typeof window.openai?.notifyIntrinsicHeight === 'function') {
    window.openai.notifyIntrinsicHeight(height);
  }
}

// Call after:
// - Initial render
// - Show more/less toggle
// - Accordion expand/collapse
// - Dynamic content load
// - Tab switches
// - Any DOM mutation that changes height
```

### When to Call `updateHeight()`

```javascript
// After initial render
function render() {
  // ... render content ...
  setTimeout(updateHeight, 100); // Small delay for DOM to settle
}

// After expanding/collapsing
function toggleSection(section) {
  section.classList.toggle('collapsed');
  updateHeight(); // Immediate call
}

// After loading async data
async function loadMoreItems() {
  const items = await fetchItems();
  renderItems(items);
  updateHeight(); // After DOM update
}

// After tab switch
function switchTab(tabId) {
  hideAllTabs();
  showTab(tabId);
  updateHeight(); // After tab content visible
}
```

---

## Theme Detection & Dark Mode

### JavaScript
```javascript
function updateTheme() {
  const theme = window.openai?.theme || 'light';
  document.body.classList.toggle('dark-mode', theme === 'dark');
}

// Initial setup
updateTheme();

// Listen for theme changes from ChatGPT
window.addEventListener('openai:set_globals', updateTheme);
```

### CSS (Dark Mode Pattern)
```css
/* Define semantic colors that change with theme */
:root {
  --color-text: var(--gray-1000);
  --color-bg: var(--gray-0);
  --color-bg-soft: var(--gray-100);
  --color-border: var(--gray-200);
}

/* Override only semantic colors in dark mode */
.dark-mode {
  --color-text: var(--gray-0);
  --color-bg: var(--gray-900);
  --color-bg-soft: var(--gray-800);
  --color-border: var(--gray-700);
}

/* Components use semantic colors - no dark mode overrides needed */
.card {
  background: var(--color-bg-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
```

---

## Empty States

### CSS
```css
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
  opacity: 0.5;
}

.empty-state-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.empty-state-text {
  font-size: 13px;
}
```

### HTML
```html
<div class="empty-state">
  <div class="empty-state-icon">📭</div>
  <div class="empty-state-title">No results found</div>
  <div class="empty-state-text">Try adjusting your search criteria</div>
</div>
```

---

## Error States

### CSS
```css
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  text-align: center;
  background: var(--color-danger-soft);
  border-radius: var(--radius-md);
}

.error-icon {
  font-size: 24px;
  margin-bottom: var(--space-2);
}

.error-message {
  font-size: 14px;
  color: var(--color-danger);
}

.retry-btn {
  margin-top: var(--space-3);
  padding: var(--space-2) var(--space-4);
  font-size: 13px;
  font-weight: 500;
  background: var(--color-danger);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.retry-btn:hover {
  opacity: 0.9;
}
```

### HTML
```html
<div class="error-state">
  <div class="error-icon">⚠️</div>
  <div class="error-message">Failed to load profile. Please try again.</div>
  <button class="retry-btn" onclick="retry()">Retry</button>
</div>
```

---

## Skeleton Loading

### CSS
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-soft) 25%,
    var(--gray-200) 50%,
    var(--color-bg-soft) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-xs);
}

.dark-mode .skeleton {
  background: linear-gradient(
    90deg,
    var(--gray-800) 25%,
    var(--gray-700) 50%,
    var(--gray-800) 75%
  );
  background-size: 200% 100%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text {
  height: 14px;
  margin-bottom: var(--space-2);
}

.skeleton-text.short { width: 40%; }
.skeleton-text.medium { width: 70%; }
.skeleton-text.long { width: 100%; }

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
}

.skeleton-card {
  height: 80px;
  border-radius: var(--radius-md);
}
```

### HTML
```html
<div class="profile-skeleton">
  <div class="flex gap-3 items-center mb-4">
    <div class="skeleton skeleton-avatar"></div>
    <div class="flex-1">
      <div class="skeleton skeleton-text medium"></div>
      <div class="skeleton skeleton-text short"></div>
    </div>
  </div>
  <div class="skeleton skeleton-card"></div>
</div>
```

---

## Tooltips

### CSS
```css
.tooltip-container {
  position: relative;
}

.tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-1) var(--space-2);
  font-size: 12px;
  background: var(--gray-900);
  color: var(--gray-0);
  border-radius: var(--radius-xs);
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-fast);
  z-index: 100;
  margin-bottom: var(--space-1);
}

.dark-mode .tooltip {
  background: var(--gray-100);
  color: var(--gray-900);
}

.tooltip-container:hover .tooltip {
  opacity: 1;
  visibility: visible;
}
```

### HTML
```html
<div class="tooltip-container">
  <button class="btn-icon">🔗</button>
  <span class="tooltip">Open LinkedIn Profile</span>
</div>
```

---

## Safe DOM Manipulation

When rendering dynamic content, use safe DOM methods:

### Using textContent (Plain Text)
```javascript
// Safe: escapes HTML automatically
element.textContent = userData.name;
```

### Using createElement (Structured Content)
```javascript
function createProfileCard(data) {
  const card = document.createElement('div');
  card.className = 'card';

  const name = document.createElement('h2');
  name.textContent = data.name; // Safe

  const bio = document.createElement('p');
  bio.textContent = data.bio; // Safe

  card.appendChild(name);
  card.appendChild(bio);
  return card;
}
```

### Using Template Literals (Escaped)
```javascript
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.textContent; // Returns escaped version
}

// Use escaped values in templates
const html = `<div class="name">${escapeHtml(data.name)}</div>`;
```

---

## Related Resources

- [Apps SDK UI Design Tokens](./apps_sdk_ui_tokens.md)
- [Widget CSS Template](./widget_css_template.md)
- [Widget Development Guide](./widget_development.md)
