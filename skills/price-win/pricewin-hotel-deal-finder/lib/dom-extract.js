// ----------------------------------------------------------------------------
// dom-extract.js
//
// Given a selector recipe (an object with CSS selectors per field), pull
// records out of the current page. Used by both the cache fast-path
// (`try-extract`) and the agent's discovery dry-run (`try-selectors`).
//
// Recipe shape (whatever the agent discovers, but these field names are
// expected downstream by the merger):
//   {
//     "card":  "[data-testid='property-card']",   // required — the row container
//     "name":  "[data-testid='title']",           // required — hotel name
//     "price": "[data-testid='price-and-discounted-price']",  // required
//     "link":  "a[data-testid='title-link']",     // optional — booking URL
//     "image": "img[data-testid='image']",        // optional
//     "rating":"[data-testid='review-score']",    // optional
//     "stars": "[data-testid='rating-stars']"     // optional
//   }
//
// `extractWithSelectors` returns:
//   {
//     records: [{name, price, currency, link, image?, rating?, stars?}, …],
//     stats:   { total, withPrice, withName, withLink }
//   }
//
// The stats let the caller decide whether the recipe is healthy enough to
// keep cached. `isExtractionHealthy` codifies that decision.
// ----------------------------------------------------------------------------

const REQUIRED_FIELDS = ['name', 'price'];

/**
 * Run a recipe against the live page. Card selector returns the list; the
 * other selectors are scoped *inside* each card so we don't accidentally
 * match the wrong row.
 */
export async function extractWithSelectors(page, selectors) {
  if (!selectors?.card) throw new Error('Recipe missing required "card" selector');
  for (const f of REQUIRED_FIELDS) {
    if (!selectors[f]) throw new Error(`Recipe missing required "${f}" selector`);
  }

  const raw = await page.evaluate(
    ({ sel }) => {
      const cleanText = (el) => (el?.textContent || '').replace(/\s+/g, ' ').trim();
      const parsePrice = (txt) => {
        if (!txt) return null;
        const digits = txt.replace(/[^\d]/g, '');
        const n = Number(digits);
        return Number.isFinite(n) && n > 0 ? n : null;
      };
      const detectCurrency = (txt) => {
        if (!txt) return null;
        if (/USD|\$/.test(txt)) return 'USD';
        if (/EUR|€/.test(txt)) return 'EUR';
        if (/GBP|£/.test(txt)) return 'GBP';
        if (/THB|฿/.test(txt)) return 'THB';
        if (/JPY|¥/.test(txt)) return 'JPY';
        if (/VND|₫/i.test(txt)) return 'VND';
        return null;
      };
      const cards = Array.from(document.querySelectorAll(sel.card));
      return cards.slice(0, 50).map((card) => {
        const nameEl = card.querySelector(sel.name);
        const priceEl = card.querySelector(sel.price);
        // Resolve link element. Fallback chain so Google's pattern (the card
        // itself is an <a> tag with no nested anchor) still produces a URL:
        //   1. Try the explicit `link` selector
        //   2. If missing, check if card itself is an <a> with href
        //   3. Last resort: any nested <a href>
        let linkEl = sel.link ? card.querySelector(sel.link) : null;
        if (!linkEl && card.tagName === 'A' && card.hasAttribute('href')) {
          linkEl = card;
        }
        if (!linkEl) linkEl = card.querySelector('a[href]');
        const imageEl = sel.image ? card.querySelector(sel.image) : card.querySelector('img');
        const ratingEl = sel.rating ? card.querySelector(sel.rating) : null;
        const starsEl = sel.stars ? card.querySelector(sel.stars) : null;
        const priceText = cleanText(priceEl);
        return {
          name: cleanText(nameEl) || null,
          priceText,
          price: parsePrice(priceText),
          currency: detectCurrency(priceText),
          link: linkEl?.getAttribute('href') || null,
          image: imageEl?.getAttribute('src') || null,
          rating: ratingEl ? cleanText(ratingEl) : null,
          starsText: starsEl ? cleanText(starsEl) : null,
        };
      });
    },
    { sel: selectors },
  );

  const records = raw.filter((r) => r.name && r.price);
  const stats = {
    total: raw.length,
    withPrice: raw.filter((r) => r.price).length,
    withName: raw.filter((r) => r.name).length,
    withLink: raw.filter((r) => r.link).length,
  };
  return { records, stats };
}

/**
 * Decide whether an extraction is good enough to keep the cached selectors
 * alive. Used by the CLI to drive the fail counter in selector-cache.js.
 *
 * Healthy if: at least 5 records returned AND at least 80% have both a
 * non-null price and link. Tunable.
 */
export function isExtractionHealthy({ records, stats }) {
  if (records.length < 5) return false;
  const ratio = stats.total === 0 ? 0 : stats.withPrice / stats.total;
  if (ratio < 0.8) return false;
  return true;
}
