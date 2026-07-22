#!/usr/bin/env node
/**
 * design-lint — deterministic, no-LLM design anti-pattern detector.
 *
 * Why this exists: an LLM "review my design" pass is non-reproducible and drifts.
 * The same anti-pattern list enforced by a pure function is a real gate: identical
 * input → identical verdict, zero tokens, runnable in CI. This is the high-leverage
 * half of the impeccable "anti-pattern ban list" — the list as a *detector*, not a prompt.
 *
 * Input: one or more standalone HTML files (e.g. /ui-plan prototype/*.html) and,
 * optionally, the project's DESIGN-TOKENS.md token set for token-hygiene checks.
 * Output: JSON report to stdout (+ optional --md), exit code 1 if any error-severity
 * detector fails (so it can gate /refactoring·/redesign), 0 otherwise.
 *
 * NOTE: all 47 detectors in references/detectors.md are implemented; each is a
 * pure function (harvest, ctx) => Finding[]. No external deps —
 * regex detectors parse <style>/style="" blocks (standalone-HTML scope). Group A detectors
 * (contrast D-COLOR-05/06, box-model D-A11Y-02/D-SPACE-03, structure D-LAYOUT-03/04, runtime
 * overflow D-LAYOUT-08~11) consume ctx.observed — per-element computed-style observations the
 * SKILL.md collects in-browser via OBSERVE_SNIPPET (live-URL path). When ctx.observed is empty
 * they skip (same skip-don't-FP contract as token hygiene). Color-only-state detection (the
 * former D-A11Y-03) was DROPPED, not deferred — do not re-add: it needs DOM child content,
 * underivable from CSS/computed style alone, so any implementation would false-positive and
 * break the deterministic gate — see detectors.md.
 *
 * D-LAYOUT-08~11 (runtime overflow/clip/overlap) are the "works but looks broken after
 * interaction" gate: viewport-fixed (1280×800, same as all Group A) so they only catch
 * desktop-viewport breakage, not mobile-only clipping — see detectors.md. D-LAYOUT-11 (sibling
 * overlap) is low-confidence (overlap can be intentional — badges, stacked cards) so it only
 * runs under --strict and defaults off. --gate-runtime opt-in escalates document-level
 * (html/body) horizontal overflow from D-LAYOUT-08 to error — that specific case is close to
 * always a real bug (whole-page horizontal scroll), everything else stays warn to protect the
 * zero-false-positive contract (see detectors.md for the sr-only / overflow-x:auto exemptions
 * this required). A `D-MOTION-06` for `transition:all` was considered and rejected — D-MOTION-03
 * (nonCompositedMotion) already flags it; adding a second id would just duplicate findings.
 */
import { readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

// ---------- tiny CSS harvesting (regex; standalone-HTML scope) ----------
function harvest(html) {
  const styleBlocks = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map(m => m[1]).join("\n");
  const inline = [...html.matchAll(/style\s*=\s*"([^"]*)"/gi)].map(m => m[1]).join(";\n");
  // strip CSS comments so rule-block/selector parsing isn't polluted by /* ... */ text
  const css = (styleBlocks + "\n" + inline).replace(/\/\*[\s\S]*?\*\//g, "");
  const rootVars = {};
  for (const m of css.matchAll(/--([\w-]+)\s*:\s*([^;}\n]+)/g)) rootVars["--" + m[1].trim()] = m[2].trim();
  const decls = [...css.matchAll(/([\w-]+)\s*:\s*([^;}{]+)\s*[;}]/g)].map(m => ({ prop: m[1].toLowerCase().trim(), val: m[2].trim() }));
  return { css, rootVars, decls };
}

const HEX = /#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b/g;
const norm = h => { h = h.toLowerCase(); return h.length === 4 ? "#" + [...h.slice(1)].map(c => c + c).join("") : h; };
const isVarRef = v => /var\(\s*--/.test(v);
const rgbOf = hex => { const c = norm(hex); if (c.length !== 7) return null; return { r: parseInt(c.slice(1, 3), 16), g: parseInt(c.slice(3, 5), 16), b: parseInt(c.slice(5, 7), 16) }; };
// vivid accent: high chroma, not near-gray/white/black (so neutrals/surfaces don't read as accents)
const isSaturated = ({ r, g, b }) => { const mx = Math.max(r, g, b), mn = Math.min(r, g, b); return (mx - mn) > 60 && mx > 40 && mn < 235; };
// WCAG relative luminance + contrast ratio (sRGB linearization)
const relLum = hex => { const c = norm(hex); const v = [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16) / 255).map(x => x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const contrastRatio = (h1, h2) => { const a = relLum(h1), b = relLum(h2), hi = Math.max(a, b), lo = Math.min(a, b); return (hi + 0.05) / (lo + 0.05); };
// runtime-overflow helpers (D-LAYOUT-08~11): sr-only pattern (1x1 clipped text) is legitimate WCAG,
// not a clip bug; overflow-x:auto/scroll is an intentional scroll container (carousel/code block).
const srOnly = o => o.w <= 1 && o.h <= 1;
const isScrollContainer = o => /^(auto|scroll)$/.test(o.overflowX || "");

// ---------- detectors: pure (css/decls/ctx) => Finding[] ----------
// severity: "error" gates the pipeline; "warn" reports only.
const DETECTORS = [
  // ---- COLOR ----
  function colorCount({ decls }, ctx) {
    const colors = new Set();
    for (const d of decls) if (/color|background|fill|stroke|border/.test(d.prop))
      for (const h of d.val.matchAll(HEX)) colors.add(norm(h[0]));
    const limit = ctx.thresholds.maxDistinctColors;
    return colors.size > limit
      ? [{ id: "D-COLOR-01", severity: "warn", msg: `distinct hard-coded colors ${colors.size} > ${limit}`, evidence: [...colors].slice(0, 12).join(" ") }]
      : [];
  },
  function tokenHygieneColor({ decls }, ctx) {
    if (!ctx.tokenColors.size) return []; // no DESIGN-TOKENS.md → skip, don't false-positive
    const offenders = [];
    for (const d of decls) if (/color|background|fill|stroke/.test(d.prop) && !isVarRef(d.val))
      for (const h of d.val.matchAll(HEX)) if (!ctx.tokenColors.has(norm(h[0]))) offenders.push(norm(h[0]));
    return offenders.length
      ? [{ id: "D-COLOR-02", severity: "error", msg: `hard-coded colors not in DESIGN-TOKENS.md (token hygiene): ${[...new Set(offenders)].length} unique`, evidence: [...new Set(offenders)].slice(0, 10).join(" ") }]
      : [];
  },
  function textGradient({ css }) {
    return /background-clip\s*:\s*text|-webkit-background-clip\s*:\s*text/.test(css)
      ? [{ id: "D-COLOR-03", severity: "warn", msg: "gradient-on-text (background-clip:text) — common AI-default tell", evidence: "background-clip:text" }] : [];
  },
  function aiDefaultBeige({ decls }) {
    // cream/sand/beige page backgrounds: high R≈G, low-ish B, all high — the "AI beige" tell
    const hits = [];
    for (const d of decls) if (/background/.test(d.prop)) for (const h of d.val.matchAll(HEX)) {
      const c = norm(h[0]), r = parseInt(c.slice(1, 3), 16), g = parseInt(c.slice(3, 5), 16), b = parseInt(c.slice(5, 7), 16);
      if (r > 230 && g > 220 && b > 195 && b < g && (r - b) > 12 && (r - b) < 55) hits.push(c);
    }
    return hits.length ? [{ id: "D-AIDEFAULT-01", severity: "warn", msg: "cream/sand/beige background (generic AI-default palette)", evidence: [...new Set(hits)].join(" ") }] : [];
  },

  // ---- TYPOGRAPHY ----
  function fontFamilyCount({ decls }, ctx) {
    const fams = new Set();
    for (const d of decls) if (d.prop === "font-family" || d.prop === "font") {
      const first = d.val.split(",")[0].replace(/['"]/g, "").trim().toLowerCase();
      if (first && !/inherit|initial|unset/.test(first)) fams.add(first);
    }
    return fams.size > ctx.thresholds.maxFontFamilies
      ? [{ id: "D-TYPE-01", severity: "warn", msg: `distinct font families ${fams.size} > ${ctx.thresholds.maxFontFamilies}`, evidence: [...fams].join(" / ") }] : [];
  },
  function systemFontPrimary({ decls }) {
    const hits = [];
    for (const d of decls) if (d.prop === "font-family") {
      const first = d.val.split(",")[0].replace(/['"]/g, "").trim().toLowerCase();
      if (/^(system-ui|-apple-system|sans-serif|serif|arial|helvetica)$/.test(first)) hits.push(d.val.trim());
    }
    return hits.length ? [{ id: "D-TYPE-02", severity: "warn", msg: "system font as primary display face (templated default look)", evidence: hits[0] }] : [];
  },
  function uppercaseEyebrow({ css }) {
    // text-transform:uppercase + wide letter-spacing = the "tracked eyebrow" cliché
    const m = /text-transform\s*:\s*uppercase/.test(css) && /letter-spacing\s*:\s*(0?\.\d+|[1-9])/.test(css);
    return m ? [{ id: "D-AIDEFAULT-02", severity: "warn", msg: "uppercase + wide letter-spacing eyebrow (overused AI-default tell)", evidence: "text-transform:uppercase + letter-spacing" }] : [];
  },

  // ---- SPACING / SHAPE ----
  function offGridSpacing({ decls }, ctx) {
    const base = ctx.thresholds.spacingBase; // 4 by default
    const off = new Set();
    for (const d of decls) if (/margin|padding|gap/.test(d.prop))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) {
        const px = parseFloat(m[1]);
        if (px > 0 && px % base !== 0 && !(base === 4 && px % 4 === 0)) off.add(px + "px");
      }
    return off.size > ctx.thresholds.maxOffGrid
      ? [{ id: "D-SPACE-01", severity: "warn", msg: `off-grid spacing values (not multiples of ${base}px): ${off.size}`, evidence: [...off].slice(0, 12).join(" ") }] : [];
  },
  function radiusScale({ decls }, ctx) {
    const radii = new Set();
    for (const d of decls) if (/border-radius|^border$/.test(d.prop))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)(px|rem)/g)) radii.add(m[1] + m[2]);
    return radii.size > ctx.thresholds.maxRadii
      ? [{ id: "D-SHAPE-01", severity: "warn", msg: `distinct corner radii ${radii.size} > ${ctx.thresholds.maxRadii} (shape inconsistency)`, evidence: [...radii].join(" ") }] : [];
  },

  // ---- LAYOUT / EFFECT ----
  function glassmorphism({ css }) {
    const n = [...css.matchAll(/backdrop-filter\s*:\s*blur/gi)].length;
    return n >= 2 ? [{ id: "D-LAYOUT-01", severity: "warn", msg: `glassmorphism (backdrop-filter:blur) used ${n}× — AI-default when unmotivated`, evidence: `${n} blurred surfaces` }] : [];
  },
  function shadowDepth({ decls }, ctx) {
    const shadows = new Set();
    for (const d of decls) if (d.prop === "box-shadow" && !isVarRef(d.val)) shadows.add(d.val.replace(/\s+/g, " ").trim());
    return shadows.size > ctx.thresholds.maxShadows
      ? [{ id: "D-EFFECT-01", severity: "warn", msg: `distinct ad-hoc box-shadows ${shadows.size} > ${ctx.thresholds.maxShadows} (no shadow scale)`, evidence: [...shadows].slice(0, 3).join(" | ") }] : [];
  },
  function shadowTokenHygiene({ decls }, ctx) {
    if (!ctx.tokenColors.size && !ctx.tokenPx.size) return []; // no DESIGN-TOKENS.md → skip
    const off = [];
    for (const d of decls) if (d.prop === "box-shadow" && d.val !== "none" && !isVarRef(d.val)) off.push(d.val.replace(/\s+/g, " ").trim());
    return off.length
      ? [{ id: "D-EFFECT-02", severity: "warn", msg: `box-shadow hard-coded instead of var(--shadow-*) token: ${off.length}`, evidence: off.slice(0, 2).join(" | ") }] : [];
  },

  // ---- TOKEN HYGIENE (spacing) ----
  function spacingTokenHygiene({ decls }, ctx) {
    if (!ctx.tokenPx.size) return []; // no spacing/px tokens → skip, don't false-positive
    const offenders = new Set();
    for (const d of decls) if (/^(margin|padding|gap|row-gap|column-gap)/.test(d.prop) && !isVarRef(d.val))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) {
        const px = parseFloat(m[1]);
        if (px > 0 && !ctx.tokenPx.has(px)) offenders.add(px + "px");
      }
    return offenders.size
      ? [{ id: "D-TOKEN-01", severity: "error", msg: `hard-coded spacing px not in token scale (token hygiene): ${offenders.size} off-scale`, evidence: [...offenders].slice(0, 10).join(" ") }] : [];
  },

  // ---- TYPOGRAPHY (a11y / scale) ----
  function tinyBodyFont({ decls }, ctx) {
    const tiny = new Set();
    for (const d of decls) if (d.prop === "font-size")
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) { const px = parseFloat(m[1]); if (px > 0 && px < ctx.thresholds.minBodyFontPx) tiny.add(px + "px"); }
    return tiny.size
      ? [{ id: "D-TYPE-07", severity: "error", msg: `font-size below ${ctx.thresholds.minBodyFontPx}px (readability/a11y)`, evidence: [...tiny].join(" ") }] : [];
  },
  function fontWeightCount({ decls }, ctx) {
    const w = new Set();
    for (const d of decls) if (d.prop === "font-weight") { const v = d.val.trim().toLowerCase(); if (!/inherit|initial|unset/.test(v)) w.add(v); }
    return w.size > ctx.thresholds.maxFontWeights
      ? [{ id: "D-TYPE-06", severity: "warn", msg: `distinct font-weights ${w.size} > ${ctx.thresholds.maxFontWeights}`, evidence: [...w].join(" ") }] : [];
  },
  function justifyText({ decls }) {
    const hit = decls.some(d => d.prop === "text-align" && /justify/.test(d.val));
    return hit ? [{ id: "D-TYPE-08", severity: "warn", msg: "text-align:justify (rivers/readability degradation on the web)", evidence: "text-align:justify" }] : [];
  },

  // ---- COLOR (soft) ----
  function pureBlack({ decls }) {
    const hit = [];
    for (const d of decls) if (/color|shadow|border|background/.test(d.prop))
      for (const h of d.val.matchAll(HEX)) if (norm(h[0]) === "#000000") hit.push(d.prop);
    return hit.length ? [{ id: "D-COLOR-07", severity: "warn", msg: "pure #000 used (soft near-black recommended for less harsh contrast)", evidence: [...new Set(hit)].join(" ") }] : [];
  },

  // ---- LAYOUT ----
  function importantSpam({ css }, ctx) {
    const n = [...css.matchAll(/!important/gi)].length;
    return n > ctx.thresholds.maxImportant
      ? [{ id: "D-LAYOUT-07", severity: "warn", msg: `!important used ${n}× > ${ctx.thresholds.maxImportant} (specificity smell)`, evidence: `${n} occurrences` }] : [];
  },

  // ---- MOTION (deterministic emil rules) ----
  function slowMotion({ decls }, ctx) {
    const slow = new Set();
    for (const d of decls) if (/transition|animation/.test(d.prop))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)(ms|s)\b/g)) {
        const ms = m[2] === "s" ? parseFloat(m[1]) * 1000 : parseFloat(m[1]);
        if (ms > ctx.thresholds.maxMotionMs) slow.add(ms + "ms");
      }
    return slow.size
      ? [{ id: "D-MOTION-01", severity: "warn", msg: `transition/animation duration > ${ctx.thresholds.maxMotionMs}ms (sluggish UI)`, evidence: [...slow].slice(0, 5).join(" ") }] : [];
  },
  function reducedMotionMissing({ css }) {
    const hasMotion = /transition\s*:|animation\s*:|@keyframes/.test(css) && /(\d+(?:\.\d+)?)(ms|s)\b/.test(css);
    const hasGuard = /prefers-reduced-motion/.test(css);
    return hasMotion && !hasGuard
      ? [{ id: "D-MOTION-04", severity: "warn", msg: "motion present but no @media (prefers-reduced-motion) guard (a11y)", evidence: "no prefers-reduced-motion" }] : [];
  },

  // ---- A11Y (focus, CSS-block-level — feasible without DOM) ----
  function focusOutlineRemoved({ css }) {
    // Cross-rule-block merge: group all :focus rules by base target (selector minus the :focus
    // pseudo), then judge per target. `:focus{outline:none}` and `:focus{box-shadow}` split across
    // separate blocks for the same element must NOT false-positive — this is error-severity, so a
    // wrong flag blocks the pipeline. Single-block alt still passes (removed & alt collapse to one target).
    const targets = new Map(); // base selector → { removed, hasAlt, sel }
    for (const m of css.matchAll(/([^{}]+)\{([^}]*)\}/g)) {
      const selRaw = m[1], body = m[2];
      if (!/:focus/.test(selRaw)) continue;
      const removed = /outline\s*:\s*(none|0)\b/.test(body);
      const hasAlt = /box-shadow\s*:\s*(?!none)[^;]*\S/.test(body)
        || /border(-\w+)?\s*:\s*[^;]*\b(solid|dashed|dotted|double|\d+px)/.test(body)
        || /outline\s*:\s*[^;]*\b(solid|dashed|dotted|\d+px)/.test(body);
      for (const part of selRaw.split(",")) {
        if (!/:focus/.test(part)) continue;
        const base = part.replace(/:focus(-visible|-within)?/g, "").trim();
        const t = targets.get(base) || { removed: false, hasAlt: false, sel: part.trim() };
        t.removed = t.removed || removed;
        t.hasAlt = t.hasAlt || hasAlt;
        targets.set(base, t);
      }
    }
    const hits = [...targets.values()].filter(t => t.removed && !t.hasAlt).map(t => t.sel);
    return hits.length
      ? [{ id: "D-A11Y-01", severity: "error", msg: "focus outline removed with no visible alternative (keyboard a11y)", evidence: hits.slice(0, 4).join(", ") }] : [];
  },

  // ---- COLOR (accent discipline) ----
  function competingAccent({ decls }) {
    // distinct raw saturated colors applied as accents (token-defs/var-refs/gradients excluded → only ad-hoc accents)
    const accents = new Set();
    for (const d of decls) {
      if (d.prop.startsWith("--")) continue;            // palette definitions are legitimate
      if (!/^(color|background|background-color|border|border-color|fill|stroke)$/.test(d.prop)) continue;
      if (isVarRef(d.val) || /gradient/i.test(d.val)) continue; // var() = disciplined; gradients → D-COLOR-08
      for (const h of d.val.matchAll(HEX)) { const c = rgbOf(h[0]); if (c && isSaturated(c)) accents.add(norm(h[0])); }
    }
    return accents.size >= 2
      ? [{ id: "D-COLOR-04", severity: "warn", msg: `competing saturated accent colors ${accents.size} (no single accent discipline)`, evidence: [...accents].slice(0, 8).join(" ") }] : [];
  },
  function rainbowGradient({ decls }) {
    const hits = [];
    for (const d of decls) {
      if (!/gradient/i.test(d.val)) continue;
      const stops = new Set();
      for (const h of d.val.matchAll(HEX)) { const c = rgbOf(h[0]); if (c && isSaturated(c)) stops.add(norm(h[0])); }
      if (stops.size >= 3) hits.push([...stops].join(","));
    }
    return hits.length
      ? [{ id: "D-COLOR-08", severity: "warn", msg: "oversaturated multi-hue gradient (rainbow) — 3+ vivid stops", evidence: hits[0] }] : [];
  },

  // ---- TYPOGRAPHY (scale / leading) ----
  function typeScaleSprawl({ decls }, ctx) {
    const sizes = new Set();
    for (const d of decls) if (d.prop === "font-size")
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) sizes.add(parseFloat(m[1]));
    return sizes.size > ctx.thresholds.maxFontSizes
      ? [{ id: "D-TYPE-03", severity: "warn", msg: `distinct font-size values ${sizes.size} > ${ctx.thresholds.maxFontSizes} (no type scale)`, evidence: [...sizes].sort((a, b) => a - b).map(x => x + "px").join(" ") }] : [];
  },
  function tightLineHeight({ decls }) {
    // only unitless ratios are judgeable without font-size context; px/em/% line-heights are skipped
    const tight = new Set();
    for (const d of decls) if (d.prop === "line-height") {
      const v = d.val.trim();
      if (/^\d*\.?\d+$/.test(v)) { const n = parseFloat(v); if (n > 0 && n < 1.3) tight.add(v); }
    }
    return tight.size
      ? [{ id: "D-TYPE-04", severity: "warn", msg: "unitless line-height < 1.3 (tight leading hurts body readability)", evidence: [...tight].join(" ") }] : [];
  },

  // ---- SPACING / SHAPE / LAYOUT (scale sprawl) ----
  function distinctSpacing({ decls }, ctx) {
    const vals = new Set();
    for (const d of decls) if (/^(margin|padding|gap|row-gap|column-gap)$/.test(d.prop) || /^(margin|padding)-(top|right|bottom|left)$/.test(d.prop))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) { const px = parseFloat(m[1]); if (px > 0) vals.add(px); }
    return vals.size > ctx.thresholds.maxDistinctSpacing
      ? [{ id: "D-SPACE-02", severity: "warn", msg: `distinct spacing values ${vals.size} > ${ctx.thresholds.maxDistinctSpacing} (no spacing scale)`, evidence: [...vals].sort((a, b) => a - b).map(x => x + "px").join(" ") }] : [];
  },
  function radiusMixing({ decls }) {
    let round = false, sharp = false;
    for (const d of decls) if (d.prop === "border-radius") {
      const v = d.val.trim();
      if (/50%/.test(v) || /\b\d{4,}px/.test(v)) round = true;   // pill/circle: 50% or 4+ digit px
      if (/^0(px)?$/.test(v)) sharp = true;                       // explicit sharp corner
    }
    return (round && sharp)
      ? [{ id: "D-SHAPE-02", severity: "warn", msg: "mixed radius language: fully-round (pill/circle) coexists with sharp 0-radius (no shape rationale)", evidence: "fully-round + sharp 0" }] : [];
  },
  function borderWidthSprawl({ decls }, ctx) {
    const widths = new Set();
    for (const d of decls) if (/^(border|border-width|border-(top|right|bottom|left)|border-(top|right|bottom|left)-width)$/.test(d.prop))
      for (const m of d.val.matchAll(/(\d+(?:\.\d+)?)px/g)) widths.add(parseFloat(m[1]));
    return widths.size > ctx.thresholds.maxBorderWidths
      ? [{ id: "D-SHAPE-03", severity: "warn", msg: `distinct border widths ${widths.size} > ${ctx.thresholds.maxBorderWidths}`, evidence: [...widths].sort((a, b) => a - b).map(x => x + "px").join(" ") }] : [];
  },
  function sideStripe({ decls }) {
    const hits = [];
    for (const d of decls) if (/^border-(left|right)$/.test(d.prop)) {
      const m = d.val.match(/(\d+(?:\.\d+)?)px/);
      if (m && parseFloat(m[1]) >= 3 && /(solid|dashed|#|rgb|var\()/.test(d.val)) hits.push(d.prop + ":" + d.val.trim());
    }
    return hits.length
      ? [{ id: "D-LAYOUT-02", severity: "warn", msg: "thick side-stripe border (decorative left/right accent cliché)", evidence: hits[0] }] : [];
  },
  function zIndexMagic({ decls }) {
    const magic = new Set();
    for (const d of decls) if (d.prop === "z-index") { const n = parseInt(d.val, 10); if (!isNaN(n) && n >= 100) magic.add(n); }
    return magic.size
      ? [{ id: "D-LAYOUT-05", severity: "warn", msg: "z-index magic numbers (>=100; no layering scale)", evidence: [...magic].sort((a, b) => a - b).join(" ") }] : [];
  },

  // ---- TOKEN HYGIENE (definitions) ----
  function deadToken({ css, rootVars }) {
    const dead = [];
    for (const name of Object.keys(rootVars)) {
      const re = new RegExp("var\\(\\s*" + name + "\\b"); // name chars (a-z0-9-) are regex-literal-safe
      if (!re.test(css)) dead.push(name);
    }
    return dead.length
      ? [{ id: "D-TOKEN-02", severity: "warn", msg: `tokens defined but never referenced via var() (dead tokens): ${dead.length}`, evidence: dead.slice(0, 8).join(" ") }] : [];
  },
  function dupTokenValue({ rootVars }) {
    const byVal = {};
    for (const [name, val] of Object.entries(rootVars)) { const v = val.trim().toLowerCase(); (byVal[v] = byVal[v] || []).push(name); }
    const dups = Object.entries(byVal).filter(([, names]) => names.length >= 2);
    return dups.length
      ? [{ id: "D-TOKEN-03", severity: "warn", msg: `same value under multiple token names (duplicate tokens): ${dups.length}`, evidence: dups.map(([v, n]) => n.join("=") + ":" + v).slice(0, 4).join(" | ") }] : [];
  },
  function rawHexColorTokens({ rootVars }) {
    // a token whose value is a bare hex literal is a color token committed to static hex (no oklch/hsl → scale derivation harder)
    const hexTokens = Object.entries(rootVars).filter(([, val]) => /^#[0-9a-fA-F]{3,8}$/.test(val.trim())).map(([n]) => n);
    return hexTokens.length
      ? [{ id: "D-TOKEN-04", severity: "warn", msg: `color tokens defined as raw hex (oklch/hsl preferred for scale derivation): ${hexTokens.length}`, evidence: hexTokens.slice(0, 8).join(" ") }] : [];
  },

  // ---- MOTION (deterministic emil rules, cont.) ----
  function scaleZeroAppear({ css }) {
    const blocks = [...css.matchAll(/(from|0%)\s*\{([^}]*)\}/gi)];
    return blocks.some(b => /scale\(\s*0\s*[,)]/.test(b[2]))
      ? [{ id: "D-MOTION-02", severity: "warn", msg: "entrance animation starts from scale(0) (pop-in; subtle scale recommended)", evidence: "scale(0) in keyframe start" }] : [];
  },
  function nonCompositedMotion({ decls }) {
    const bad = new Set();
    const NONCOMP = /\b(width|height|top|left|right|bottom|margin|padding|box-shadow|border-width)\b/;
    for (const d of decls) if (/^(transition|transition-property|animation)$/.test(d.prop)) {
      if (/\ball\b/.test(d.val)) bad.add("all");
      const mp = d.val.match(NONCOMP); if (mp) bad.add(mp[1]);
    }
    return bad.size
      ? [{ id: "D-MOTION-03", severity: "warn", msg: "animating non-composited properties (layout/paint; prefer transform/opacity)", evidence: [...bad].join(" ") }] : [];
  },
  function easeInAppear({ css }) {
    return /\bease-in\b(?!-out)/.test(css)
      ? [{ id: "D-MOTION-05", severity: "warn", msg: "ease-in timing (ease-out feels more natural for entrances)", evidence: "ease-in" }] : [];
  },

  // ---- COLOR contrast (Group A: needs computed text/bg pairing from ctx.observed) ----
  function textContrast(_, ctx) {
    const errs = [], warns = [];
    for (const o of ctx.observed) {
      // skip unless we have a real text/bg pair; indeterminate bg → skip (never assume white — error-grade)
      if (!o.text || !o.color || !o.bg || o.bg.indeterminate || !o.bg.value) continue;
      const ratio = contrastRatio(o.color, o.bg.value);
      const fp = o.fontPx || 16, bold = parseInt(o.fontWeight, 10) >= 700;
      const large = fp >= 24 || (fp >= 19 && bold); // WCAG large text: ≥24px, or ≥18.66px bold
      if (large) { if (ratio < 3.0) warns.push({ o, ratio }); }
      else if (ratio < 4.5) errs.push({ o, ratio });
    }
    const ev = arr => arr.slice(0, 4).map(e => `${e.o.color} on ${e.o.bg.value} ${e.ratio.toFixed(2)}:1`).join(" | ");
    const out = [];
    if (errs.length) out.push({ id: "D-COLOR-05", severity: "error", msg: `body text contrast < 4.5:1 (WCAG AA): ${errs.length} element(s)`, evidence: ev(errs) });
    if (warns.length) out.push({ id: "D-COLOR-06", severity: "warn", msg: `large text contrast < 3:1 (WCAG AA large): ${warns.length} element(s)`, evidence: ev(warns) });
    return out;
  },

  // ---- A11Y / SPACING (Group A: box-model from ctx.observed) ----
  function smallTarget(_, ctx) {
    const small = ctx.observed.filter(o => o.interactive && o.w > 0 && o.h > 0 && (o.w < ctx.thresholds.minTargetPx || o.h < ctx.thresholds.minTargetPx));
    return small.length
      ? [{ id: "D-A11Y-02", severity: "warn", msg: `interactive target < ${ctx.thresholds.minTargetPx}px: ${small.length} element(s)`, evidence: small.slice(0, 4).map(o => `${o.tag} ${o.w}x${o.h}`).join(" | ") }] : [];
  },
  function wideTextContainer(_, ctx) {
    const wide = ctx.observed.filter(o => o.text && o.bg && o.maxWidth === "none" && o.w > ctx.thresholds.maxTextWidth);
    return wide.length
      ? [{ id: "D-SPACE-03", severity: "warn", msg: `full-width text, no max-width (measure > ${ctx.thresholds.maxTextWidth}px hurts readability): ${wide.length}`, evidence: wide.slice(0, 4).map(o => `${o.tag} ${o.w}px`).join(" | ") }] : [];
  },

  // ---- LAYOUT (regex: specified px width — computed style can't distinguish px from %) ----
  function fixedPxWidth({ decls }, ctx) {
    const fixed = new Set();
    for (const d of decls) if (d.prop === "width") { const m = d.val.trim().match(/^(\d+(?:\.\d+)?)px$/); if (m && parseFloat(m[1]) >= ctx.thresholds.minFixedWidthPx) fixed.add(m[1] + "px"); }
    return fixed.size
      ? [{ id: "D-LAYOUT-06", severity: "warn", msg: `fixed px width >= ${ctx.thresholds.minFixedWidthPx}px (non-responsive): ${fixed.size}`, evidence: [...fixed].join(" ") }] : [];
  },

  // ---- LAYOUT structure (Group A: DOM repetition from ctx.observed sig — LOW-CONFIDENCE, warn only) ----
  // Only classed elements (sig has non-empty class) count, so generic untagged wrappers don't inflate.
  function heroMetricTemplate(_, ctx) {
    const groups = {};
    for (const o of ctx.observed) if (/\|.+/.test(o.sig) && o.depth <= 3) { const k = o.sig + "@" + o.depth; (groups[k] = groups[k] || []).push(o); }
    const hits = Object.entries(groups).filter(([, arr]) => arr.length === 3); // the "3 identical stat cards" cliché
    return hits.length
      ? [{ id: "D-LAYOUT-03", severity: "warn", msg: "hero-metric template: 3 identical shallow blocks (stat-card cliché) [low-confidence]", evidence: hits.map(([k]) => k).slice(0, 3).join(" ") }] : [];
  },
  function repeatedBlocks(_, ctx) {
    const count = {};
    for (const o of ctx.observed) if (/\|.+/.test(o.sig)) count[o.sig] = (count[o.sig] || 0) + 1;
    const hits = Object.entries(count).filter(([, n]) => n >= ctx.thresholds.maxRepeatedBlocks);
    return hits.length
      ? [{ id: "D-LAYOUT-04", severity: "warn", msg: "repeated identical card blocks (visual monotony) [low-confidence]", evidence: hits.map(([k, n]) => `${k}×${n}`).slice(0, 3).join(" ") }] : [];
  },

  // ---- LAYOUT runtime overflow/clip (Group A: scrollWidth/clientWidth/overflow-x from ctx.observed) ----
  // "works fine, looks broken after render/interaction" gate — not caught by any static-CSS detector above.
  function horizontalOverflow(_, ctx) {
    const hits = ctx.observed.filter(o =>
      o.scrollW != null && o.clientW != null && o.scrollW > o.clientW + 1 && // +1px rounding tolerance
      !srOnly(o) && !isScrollContainer(o));
    if (!hits.length) return [];
    const bodyLevel = hits.filter(o => /^(html|body)$/.test(o.tag));
    const severity = (ctx.gateRuntime && bodyLevel.length) ? "error" : "warn";
    return [{ id: "D-LAYOUT-08", severity, msg: `horizontal overflow (scrollWidth>clientWidth): ${hits.length} element(s)${bodyLevel.length ? " incl. document-level (whole-page horizontal scroll)" : ""}`, evidence: hits.slice(0, 4).map(o => `${o.tag} ${o.scrollW}>${o.clientW}`).join(" | ") }];
  },
  function textClippedNoEllipsis(_, ctx) {
    const hits = ctx.observed.filter(o =>
      o.text && o.scrollW != null && o.clientW != null && o.scrollW > o.clientW + 1 &&
      !srOnly(o) && o.overflowX === "hidden" && o.textOverflow !== "ellipsis" &&
      !(o.lineClamp && o.lineClamp !== "none")); // -webkit-line-clamp = intentional multi-line truncation, not a bug
    return hits.length
      ? [{ id: "D-LAYOUT-09", severity: "warn", msg: `text clipped without ellipsis/line-clamp (overflow:hidden, no visible truncation cue): ${hits.length} element(s)`, evidence: hits.slice(0, 4).map(o => `${o.tag} ${o.sig}`).join(" | ") }] : [];
  },
  function interactiveTextOverflow(_, ctx) {
    const hits = ctx.observed.filter(o =>
      o.interactive && o.text && o.scrollW != null && o.clientW != null && o.scrollW > o.clientW + 1 &&
      !srOnly(o) && !isScrollContainer(o));
    return hits.length
      ? [{ id: "D-LAYOUT-10", severity: "warn", msg: `interactive element text exceeds its container (button/link label overflow): ${hits.length} element(s)`, evidence: hits.slice(0, 4).map(o => `${o.tag} ${o.scrollW}>${o.clientW}`).join(" | ") }] : [];
  },
  function siblingOverlap(_, ctx) {
    if (!ctx.strict) return []; // low-confidence (overlap can be intentional — badges/stacked cards); opt-in only
    const cand = ctx.observed.filter(o => o.x != null && o.y != null && o.w > 0 && o.h > 0 && !o.interactive).slice(0, 300);
    const hits = [];
    for (let a = 0; a < cand.length; a++) for (let b = a + 1; b < cand.length; b++) {
      const A = cand[a], B = cand[b];
      if (A.depth !== B.depth) continue; // same nesting depth as a rough sibling proxy
      const ox = Math.max(0, Math.min(A.x + A.w, B.x + B.w) - Math.max(A.x, B.x));
      const oy = Math.max(0, Math.min(A.y + A.h, B.y + B.h) - Math.max(A.y, B.y));
      const minArea = Math.min(A.w * A.h, B.w * B.h);
      if (minArea > 0 && (ox * oy) / minArea > 0.3) hits.push(`${A.tag}×${B.tag}`);
    }
    return hits.length
      ? [{ id: "D-LAYOUT-11", severity: "warn", msg: `possible unintended sibling overlap (--strict, low-confidence — verify visually): ${hits.length} pair(s)`, evidence: hits.slice(0, 4).join(" | ") }] : [];
  },
];

// ---------- token sets from DESIGN-TOKENS.md ----------
function loadTokenColors(path) {
  const set = new Set();
  if (!path) return set;
  try { for (const m of readFileSync(path, "utf8").matchAll(HEX)) set.add(norm(m[0])); } catch { /* missing → empty, hygiene skipped */ }
  return set;
}
// allowed px scale (union of spacing/radius/size px in the tokens file). Empty → hygiene skipped.
function loadTokenPx(path) {
  const set = new Set();
  if (!path) return set;
  try { for (const m of readFileSync(path, "utf8").matchAll(/(\d+(?:\.\d+)?)px/g)) set.add(parseFloat(m[1])); } catch { /* missing → empty */ }
  return set;
}
// ---------- computed-style observations (Group A: contrast, box-model, structure) ----------
// Array of per-element observations collected in-browser (see OBSERVE_SNIPPET). Empty → Group A
// detectors skip (same false-positive-avoidance contract as token hygiene). DOM order preserved.
function loadObserved(path) {
  if (!path) return [];
  try { const v = JSON.parse(readFileSync(path, "utf8")); return Array.isArray(v) ? v : []; } catch { return []; }
}

// Browser-side collector (string, injected via Playwright browser_evaluate — zero npm dep, mirrors
// ui-plan/extract-tokens COLLECT_SNIPPET). REQUIRES a FIXED viewport (caller sets 1280×800): box
// metrics (w/h/maxWidth/scrollW/clientW/x/y) are viewport-dependent, so determinism holds only
// under a fixed viewport — and mobile-only overflow/clipping is out of scope for the same reason
// (see detectors.md). Effective background walks ancestors and composites alpha;
// background-image/gradient → indeterminate (never assume white — an error-grade contrast
// false-positive would block the pipeline).
// CALLER MUST await document.fonts.ready (a separate browser_evaluate('document.fonts.ready'))
// immediately before injecting this snippet — collecting scrollW/clientW while a web font is
// still swapping in produces a transient false overflow reading (fallback-font metrics differ).
export const OBSERVE_SNIPPET = `(() => {
  const parse = (c) => { const m = c && c.match(/rgba?\\(([\\d.]+)[ ,]+([\\d.]+)[ ,]+([\\d.]+)(?:[ ,/]+([\\d.]+))?\\)/i); if (!m) return null; return { r:+m[1], g:+m[2], b:+m[3], a: m[4] === undefined ? 1 : parseFloat(m[4]) }; };
  const hex = ({ r, g, b }) => '#' + [r, g, b].map(x => Math.max(0, Math.min(255, Math.round(x))).toString(16).padStart(2, '0')).join('');
  const effBg = (el) => {
    const layers = []; let opaque = false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return { value: null, indeterminate: true }; // image/gradient → genuinely unknown
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) { opaque = true; break; } }
    }
    // bottom of the stack: the opaque ancestor if any, else the UA canvas default (white) — deterministic, NOT a guess.
    // Only background-image/gradient yields indeterminate; a fully-unset chain renders white in every browser.
    let base = opaque ? layers.pop() : { r: 255, g: 255, b: 255, a: 1 };
    for (let i = layers.length - 1; i >= 0; i--) { const t = layers[i], a = t.a; base = { r: t.r * a + base.r * (1 - a), g: t.g * a + base.g * (1 - a), b: t.b * a + base.b * (1 - a), a: 1 }; }
    return { value: hex(base), indeterminate: false };
  };
  const interactive = (el) => /^(a|button|input|select|textarea|summary)$/.test(el.tagName.toLowerCase()) || el.matches('[role=button],[role=link],[onclick],[tabindex]');
  const out = []; let i = 0;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    const r = el.getBoundingClientRect();
    const col = parse(cs.color);
    let depth = 0; for (let p = el.parentElement; p; p = p.parentElement) depth++;
    const cls = (el.className && el.className.toString) ? el.className.toString().trim().split(/\\s+/).filter(Boolean).sort().join('.') : '';
    out.push({
      i: i++, tag: el.tagName.toLowerCase(), role: el.getAttribute('role') || null, interactive: interactive(el),
      fontPx: Math.round(parseFloat(cs.fontSize)) || null, fontWeight: cs.fontWeight,
      color: col && col.a > 0 ? hex(col) : null, bg: effBg(el),
      w: Math.round(r.width), h: Math.round(r.height), maxWidth: cs.maxWidth, depth,
      sig: el.tagName.toLowerCase() + '|' + cls,
      text: [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0),
      scrollW: el.scrollWidth, clientW: el.clientWidth, overflowX: cs.overflowX,
      textOverflow: cs.textOverflow, whiteSpace: cs.whiteSpace,
      lineClamp: cs.getPropertyValue('-webkit-line-clamp') || cs.getPropertyValue('line-clamp') || 'none',
      x: Math.round(r.x), y: Math.round(r.y),
    });
  }
  return out;
})()`;

// ---------- main ----------
function run(argv) {
  const files = [], opt = { tokens: null, observed: null, md: false, gate: false, strict: false, gateRuntime: false, thresholds: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--tokens") opt.tokens = argv[++i];
    else if (a === "--observed") opt.observed = argv[++i];
    else if (a === "--md") opt.md = true;
    else if (a === "--gate") opt.gate = true;
    else if (a === "--strict") opt.strict = true; // opt-in: enables D-LAYOUT-11 (sibling overlap, low-confidence)
    else if (a === "--gate-runtime") opt.gateRuntime = true; // opt-in: escalates document-level D-LAYOUT-08 to error
    else if (a === "--observe-snippet") { process.stdout.write(OBSERVE_SNIPPET + "\n"); process.exit(0); }
    else if (a === "--max-colors") opt.thresholds.maxDistinctColors = +argv[++i];
    else if (!a.startsWith("--")) files.push(a);
  }
  const thresholds = {
    maxDistinctColors: 8, maxFontFamilies: 2, spacingBase: 4, maxOffGrid: 0,
    maxRadii: 3, maxShadows: 4, maxImportant: 2, maxFontWeights: 4,
    minBodyFontPx: 12, maxMotionMs: 300, maxFontSizes: 6,
    maxDistinctSpacing: 8, maxBorderWidths: 3,
    minTargetPx: 44, maxTextWidth: 760, minFixedWidthPx: 600, maxRepeatedBlocks: 6, ...opt.thresholds,
  };
  const observed = loadObserved(opt.observed);
  const ctx = { tokenColors: loadTokenColors(opt.tokens), tokenPx: loadTokenPx(opt.tokens), observed, thresholds, strict: opt.strict, gateRuntime: opt.gateRuntime };

  const perFile = files.map(f => {
    const { css, rootVars, decls } = harvest(readFileSync(f, "utf8"));
    const findings = DETECTORS.flatMap(d => { try { return d({ css, rootVars, decls }, ctx); } catch { return []; } });
    return { file: f, findings };
  });

  const all = perFile.flatMap(p => p.findings.map(x => ({ ...x, file: p.file })));
  const errors = all.filter(x => x.severity === "error");
  const report = {
    skill: "design-lint", files: files.length,
    detectorsRun: DETECTORS.length, detectorsTotal: 47, // 47 IDs via 46 fns (textContrast emits D-COLOR-05 + D-COLOR-06)
    summary: { error: errors.length, warn: all.length - errors.length },
    verdict: errors.length ? "FAIL" : "PASS",
    tokenHygiene: ctx.tokenColors.size ? "checked" : "skipped (no --tokens)",
    observed: ctx.observed.length ? "checked" : "skipped — Group A inactive (contrast D-COLOR-05/06, target D-A11Y-02, max-width D-SPACE-03, structure D-LAYOUT-03/04, runtime overflow D-LAYOUT-08~11 need --observed)",
    gated: opt.gate, strict: opt.strict, gateRuntime: opt.gateRuntime,
    findings: all,
  };
  if (opt.md) process.stderr.write(renderMd(report));
  process.stdout.write(JSON.stringify(report, null, 2) + "\n");
  // Contract: standalone = pure reporter (always exit 0; verdict lives in JSON).
  // Only --gate makes an error-severity finding a non-zero exit, so a caller
  // pipeline (/refactoring·/redesign) can block on it without standalone runs gating.
  process.exit(opt.gate && errors.length ? 1 : 0);
}

function renderMd(r) {
  let s = `\n# design-lint — ${r.verdict}\n${r.summary.error} error · ${r.summary.warn} warn · token-hygiene ${r.tokenHygiene}\n`;
  for (const f of r.findings) s += `- [${f.severity}] \`${f.id}\` ${f.msg} — ${f.file}\n    ${f.evidence}\n`;
  return s + "\n";
}

// import guard: run as CLI only when invoked directly (so OBSERVE_SNIPPET can be imported by tests).
// Compare realpaths, not raw strings — when invoked via a symlinked path (e.g. ~/.claude → a
// junction/share), process.argv[1] keeps the symlink path while import.meta.url resolves to the
// real path, so a `===` check silently never runs (pipeline gate dies as a no-op). realpathSync
// canonicalizes both sides; falls back to the raw compare if either path can't be resolved.
function isMainModule() {
  const entry = process.argv[1];
  if (!entry) return false;
  const self = fileURLToPath(import.meta.url);
  try { return realpathSync(entry) === realpathSync(self); }
  catch { return entry === self; }
}
if (isMainModule()) run(process.argv.slice(2));
