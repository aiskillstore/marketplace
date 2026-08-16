// ----------------------------------------------------------------------------
// snapshot.js
//
// Reads the loaded page and produces a compact text rendering for the LLM
// agent to reason over. Output is a numbered list of interactive elements
// and visible structural text. Each entry has a `[ref]` token; the same
// ref can be passed back to `click <ref>` / `fill <ref> <text>` because
// the snapshot writes its index into a `data-browse-ref` attribute on the
// live DOM, which `lib/dom-extract.js` (and the CLI) can then re-locate.
//
// Filtering rules:
//   - Keep <a>, <button>, <input>, <select>, <textarea>
//   - Keep elements with role=button/link/searchbox/checkbox/menuitem
//   - Keep <h1>–<h6>
//   - Keep visible text nodes that look like prices, hotel names, or
//     review scores
//   - Skip elements that are hidden (display:none, visibility:hidden,
//     opacity:0, zero-size) or inside <script>/<style>
//
// Token-budget conscious: each entry is one line; the whole snapshot is
// typically 200–800 lines (~1–4k tokens) for a busy results page.
// ----------------------------------------------------------------------------

/**
 * Public API. Call after page.goto / page.waitForLoadState.
 * Returns:
 *   {
 *     text: "[1] input placeholder=\"Where to?\"\\n[2] button \"Search\"\\n…",
 *     refs: { 1: "<stable CSS selector>", 2: "<stable CSS selector>", … }
 *   }
 *
 * The daemon caches the `refs` map so subsequent click/type/fill commands
 * can look up the stable selector even if React rerenders and wipes our
 * `data-browse-ref` attribute.
 *
 * Stable selector strategy: prefer stable attributes (`data-testid`,
 * `data-selenium`, `data-element-name`), then unique aria-label or href,
 * then path-based nth-of-type chain. Always validated to be unique at
 * snapshot time.
 */
export async function takeSnapshot(page) {
  const result = await page.evaluate(() => {
    const PRICE_RE = /[\d.,]{3,}\s*(VND|₫|\$|USD|THB|JPY|EUR|£)\b/i;
    const isVisible = (el) => {
      const style = getComputedStyle(el);
      if (style.display === 'none' || style.visibility === 'hidden' || +style.opacity === 0) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const cleanText = (s) => (s || '').replace(/\s+/g, ' ').trim().slice(0, 160);
    const kind = (el) => {
      const tag = el.tagName.toLowerCase();
      const role = (el.getAttribute('role') || '').toLowerCase();
      if (tag === 'a' || role === 'link') return 'link';
      if (tag === 'button' || role === 'button') return 'button';
      if (tag === 'input') {
        const t = (el.getAttribute('type') || 'text').toLowerCase();
        return t === 'submit' ? 'button' : 'input';
      }
      if (tag === 'select' || tag === 'textarea') return 'input';
      if (role === 'searchbox' || role === 'textbox' || role === 'combobox') return 'input';
      if (role === 'checkbox') return 'checkbox';
      if (role === 'menuitem' || role === 'option') return 'option';
      if (role === 'tab' || role === 'switch' || role === 'radio') return 'button';
      if (/^h[1-6]$/.test(tag)) return 'heading';
      return null;
    };
    const stableSelectorFor = (el) => {
      // 1) #id when id is css-safe
      const id = el.id;
      if (id && /^[A-Za-z][\w-]*$/.test(id) && document.querySelectorAll('#' + id).length === 1) {
        return '#' + id;
      }
      // 2) stable data-* attrs when unique
      for (const a of ['data-testid', 'data-selenium', 'data-element-name']) {
        const v = el.getAttribute(a);
        if (v) {
          const sel = '[' + a + '=' + JSON.stringify(v) + ']';
          if (document.querySelectorAll(sel).length === 1) return sel;
        }
      }
      // 3) unique aria-label
      const aria = el.getAttribute('aria-label');
      if (aria) {
        const sel = el.tagName.toLowerCase() + '[aria-label=' + JSON.stringify(aria) + ']';
        if (document.querySelectorAll(sel).length === 1) return sel;
      }
      // 4) unique href on anchors
      const href = el.getAttribute('href');
      if (href && el.tagName === 'A') {
        const sel = 'a[href=' + JSON.stringify(href) + ']';
        if (document.querySelectorAll(sel).length === 1) return sel;
      }
      // 5) path-based nth-of-type chain
      const parts = [];
      let cur = el;
      while (cur && cur !== document.body && cur.tagName) {
        const sibs = Array.from((cur.parentElement && cur.parentElement.children) || []).filter((c) => c.tagName === cur.tagName);
        const i = sibs.indexOf(cur);
        parts.unshift(cur.tagName.toLowerCase() + (sibs.length > 1 ? ':nth-of-type(' + (i + 1) + ')' : ''));
        cur = cur.parentElement;
      }
      return 'body > ' + parts.join(' > ');
    };
    // Clear any old refs from a prior snapshot.
    document.querySelectorAll('[data-browse-ref]').forEach((el) => el.removeAttribute('data-browse-ref'));
    let n = 0;
    const entries = [];
    const refMap = {};
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
    while (walker.nextNode()) {
      const el = walker.currentNode;
      if (!el || !el.tagName) continue;
      if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName)) continue;
      if (!isVisible(el)) continue;
      const k = kind(el);
      if (!k) continue;
      n += 1;
      el.setAttribute('data-browse-ref', String(n));
      const attrs = {};
      for (const name of ['data-testid', 'data-selenium', 'aria-label', 'placeholder', 'name', 'href', 'type', 'role', 'id']) {
        const v = el.getAttribute(name);
        if (v) attrs[name] = cleanText(v);
      }
      const entryText = cleanText(el.innerText || el.value || '');
      entries.push({ ref: n, kind: k, text: entryText, attrs });
      // Keep BOTH a CSS selector (fast path) and a signature (resilient
      // fallback if React re-renders strips attrs after snapshot).
      refMap[n] = {
        selector: stableSelectorFor(el),
        signature: {
          tag: el.tagName.toLowerCase(),
          kind: k,
          text: entryText,
          testid: el.getAttribute('data-testid') || el.getAttribute('data-selenium') || null,
          ariaLabel: el.getAttribute('aria-label') || null,
          placeholder: el.getAttribute('placeholder') || null,
          href: el.getAttribute('href') || null,
        },
      };
    }
    // Capture standalone price text nodes (Booking pattern).
    const priceWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (priceWalker.nextNode()) {
      const t = priceWalker.currentNode;
      const txt = cleanText(t.nodeValue);
      if (!txt || !PRICE_RE.test(txt)) continue;
      const parent = t.parentElement;
      if (!parent || parent.hasAttribute('data-browse-ref')) continue;
      if (!isVisible(parent)) continue;
      n += 1;
      parent.setAttribute('data-browse-ref', String(n));
      entries.push({ ref: n, kind: 'price', text: txt, attrs: {} });
      refMap[n] = {
        selector: stableSelectorFor(parent),
        signature: { tag: parent.tagName.toLowerCase(), kind: 'price', text: txt, testid: null, ariaLabel: null, placeholder: null, href: null },
      };
    }
    return { entries, refMap };
  });
  const refs = {};
  const lines = [];
  for (const e of result.entries) {
    refs[e.ref] = result.refMap[e.ref] || { selector: `[data-browse-ref="${e.ref}"]`, signature: null };
    const parts = [`[${e.ref}]`, e.kind];
    if (e.kind === 'price') {
      parts.push(JSON.stringify(e.text));
    } else if (e.kind === 'heading') {
      parts.push(JSON.stringify(e.text));
    } else {
      // For links/buttons/inputs, show label + key attrs that help the LLM
      // pick the right one (testid, href, placeholder).
      if (e.text) parts.push(JSON.stringify(e.text));
      for (const k of ['data-testid', 'data-selenium', 'aria-label', 'placeholder', 'href']) {
        if (e.attrs[k]) parts.push(`${k}=${JSON.stringify(e.attrs[k])}`);
      }
    }
    lines.push(parts.join(' '));
  }
  return { text: lines.join('\n'), refs };
}
