#!/usr/bin/env node
// wunderui-token-check — finds hard-coded colours, spacing and radii and maps each to the nearest
// WunderUI token. No dependencies, Node 20+.
//
//   token-check.mjs scan [paths…]          → .wunderui/token-check.json + a summary on stdout
//   token-check.mjs fix [--visible]        → replaces the "swap" findings (and "visible" ones with --visible)
//   token-check.mjs show <id>              → one finding with its alternatives
//
// Colour distance is ΔE in OKLab ×100 (≈ 1 is the smallest difference people notice on a screen):
//   swap     ΔE ≤ 2   or the exact px value   — replace, nobody will see it
//   visible  ΔE ≤ 6   or ≤ 2 px off           — replace, the shift is visible side by side
//   review   anything further                 — not a token; the design decides (new token or keep)
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs"
import { dirname, join, relative, resolve, sep } from "node:path"
import { fileURLToPath } from "node:url"

const HERE = dirname(fileURLToPath(import.meta.url))
const TOKENS = JSON.parse(readFileSync(join(HERE, "..", "references", "tokens.json"), "utf8"))
const cwd = process.cwd()
const OUT = join(cwd, ".wunderui", "token-check.json")
const args = process.argv.slice(2)
const cmd = args[0]
const posix = (p) => p.split(sep).join("/")

/* ---------------------------------------------------------------- colour maths */
function parseColor(raw) {
  let s = raw.trim().toLowerCase()
  let m = /^#([0-9a-f]{3,8})$/.exec(s)
  if (m) {
    let h = m[1]
    if (h.length === 3 || h.length === 4) h = [...h].map((c) => c + c).join("")
    const n = (i) => parseInt(h.slice(i, i + 2), 16) / 255
    return { r: n(0), g: n(2), b: n(4), a: h.length === 8 ? n(6) : 1 }
  }
  m = /^rgba?\(\s*([\d.]+%?)[\s,]+([\d.]+%?)[\s,]+([\d.]+%?)(?:[\s,/]+([\d.]+%?))?\s*\)$/.exec(s)
  if (m) {
    const ch = (v) => (v.endsWith("%") ? parseFloat(v) / 100 : parseFloat(v) / 255)
    return { r: ch(m[1]), g: ch(m[2]), b: ch(m[3]), a: m[4] ? (m[4].endsWith("%") ? parseFloat(m[4]) / 100 : parseFloat(m[4])) : 1 }
  }
  m = /^hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%(?:[\s,/]+([\d.]+%?))?\s*\)$/.exec(s)
  if (m) {
    const h = parseFloat(m[1]) / 360, sat = parseFloat(m[2]) / 100, l = parseFloat(m[3]) / 100
    const q = l < 0.5 ? l * (1 + sat) : l + sat - l * sat, p = 2 * l - q
    const f = (t) => { t = (t + 1) % 1; return t < 1 / 6 ? p + (q - p) * 6 * t : t < 1 / 2 ? q : t < 2 / 3 ? p + (q - p) * (2 / 3 - t) * 6 : p }
    return { r: f(h + 1 / 3), g: f(h), b: f(h - 1 / 3), a: m[4] ? parseFloat(m[4]) / (m[4].endsWith("%") ? 100 : 1) : 1 }
  }
  m = /^oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?(?:\s*\/\s*([\d.]+%?))?\s*\)$/.exec(s)
  if (m) {
    // OKLCH → OKLab → linear sRGB → sRGB
    const L = parseFloat(m[1]) / (m[2] ? 100 : 1), C = parseFloat(m[3]), H = (parseFloat(m[4]) * Math.PI) / 180
    const a = C * Math.cos(H), b = C * Math.sin(H)
    const l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3, mm = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3, ss = (L - 0.0894841775 * a - 1.291485548 * b) ** 3
    const toS = (v) => { v = Math.min(1, Math.max(0, v)); return v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055 }
    return { r: toS(4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * ss), g: toS(-1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * ss), b: toS(-0.0041960863 * l - 0.7034186147 * mm + 1.707614701 * ss), a: m[5] ? parseFloat(m[5]) / (m[5].endsWith("%") ? 100 : 1) : 1 }
  }
  if (s === "white") return { r: 1, g: 1, b: 1, a: 1 }
  if (s === "black") return { r: 0, g: 0, b: 0, a: 1 }
  return null
}
const lin = (c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
function oklab({ r, g, b }) {
  const [R, G, B] = [lin(r), lin(g), lin(b)]
  const l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B)
  const m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B)
  const s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B)
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s]
}
const dE = (a, b) => { const [x, y] = [oklab(a), oklab(b)]; return Math.hypot(x[0] - y[0], x[1] - y[1], x[2] - y[2]) * 100 }

// palette primitives (indigo-600, neutral-dark-secondary …) stay the same in both modes, unlike semantic tokens
const PALETTE = /^(?:[a-z]+-\d{2,4}|neutral-[\w-]+|light-\d+|dark-\d+|black|white)$/
const colorTokens = Object.entries(TOKENS.colors).map(([name, t]) => ({ name, light: parseColor(t.light), dark: parseColor(t.dark), palette: PALETTE.test(name) })).filter((t) => t.light)
const ROLE = { text: /^(text|foreground|.*-foreground|muted-foreground|tint-text)/, bg: /^(background|bg-|card|popover|muted|accent|secondary|primary|sidebar|tint-(?!text))/, border: /^(border|input|ring|code-border)/ }
// Equal colours often have several names (primary = ring = sidebar-ring). Prefer the canonical ones.
const CANONICAL = ["primary", "background", "foreground", "card", "muted", "muted-foreground", "border", "text-secondary", "text-tertiary", "text-link", "text-error", "text-success", "destructive", "success", "secondary", "accent", "popover", "input"]
const rank = (name) => (CANONICAL.includes(name) ? -0.3 + CANONICAL.indexOf(name) * 0.001 : /^(sidebar|chart|ring|brand-|code-|border-control)/.test(name) ? 0.3 : 0)
// A token made for another role (a *-foreground on a background, a border colour as text) is only
// suggested when nothing in the right role is close: wrong role costs 3 ΔE, the right one earns 0.5.
const roleOf = (name) => (ROLE.text.test(name) ? "text" : ROLE.border.test(name) ? "border" : ROLE.bg.test(name) ? "bg" : null)
function nearestColor(c, prefix, mode = "light") {
  const want = prefix === "text" || prefix === "fill" || prefix === "stroke" || prefix === "decoration" ? "text" : prefix === "bg" || prefix === "from" || prefix === "via" || prefix === "to" ? "bg" : prefix === "border" || prefix === "ring" || prefix === "outline" || prefix === "divide" ? "border" : null
  const fit = (name) => { const r = roleOf(name); return !want || !r ? 0 : r === want ? -0.5 : 3 }
  return colorTokens
    .filter((t) => t[mode])
    .map((t) => ({ t, d: dE(c, t[mode]) + (t.palette ? 0.75 : 0) + fit(t.name) + rank(t.name), raw: dE(c, t[mode]) }))
    .sort((a, b) => a.d - b.d)
    .slice(0, 3)
    .map(({ t, raw }) => ({ token: t.name, var: TOKENS.colors[t.name].var, light: TOKENS.colors[t.name].light, dark: TOKENS.colors[t.name].dark, deltaE: +raw.toFixed(2), palette: t.palette, comparedWith: mode }))
}
const SPACING = (px) => { const step = px <= 8 ? 2 : 4; const snapped = Math.round(px / step) * step; return { px: snapped, tw: String(snapped / 4).replace(/\.0$/, "") } }
const RADII = Object.entries(TOKENS.radius).map(([k, v]) => ({ name: k, px: v }))
const nearestRadius = (px) => RADII.map((r) => ({ ...r, diff: Math.abs(r.px - px) })).sort((a, b) => a.diff - b.diff)[0]

/* ---------------------------------------------------------------- scanning */
const EXT = /\.(tsx|jsx|ts|js|mjs|css|scss|vue|svelte|astro|html)$/
const SKIP = new Set(["node_modules", ".git", ".next", "dist", "build", "out", ".turbo", ".vercel", "coverage", ".wunderui", "public"])
function files(paths) {
  const acc = []
  const walk = (p) => {
    let st
    try { st = statSync(p) } catch { return }
    if (st.isDirectory()) { for (const n of readdirSync(p)) if (!SKIP.has(n) && !n.startsWith(".")) walk(join(p, n)) }
    else if (EXT.test(p) && !/\.(test|spec|stories)\./.test(p) && !/tailwind\.config|\.d\.ts$/.test(p)) acc.push(p)
  }
  const roots = paths.length ? paths : ["src", "app", "components", "pages", "lib", "styles"].filter((d) => existsSync(join(cwd, d)))
  for (const p of roots) {
    const full = resolve(cwd, p)
    if (!existsSync(full)) console.error(`warning: ${p} does not exist — skipped`)
    walk(full)
  }
  if (!acc.length) console.error(`warning: no files found in ${roots.join(", ") || "(no default folders)"} — pass the folders to scan`)
  return acc
}

const COLOR_RE = /#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)/g
// a palette primitive is never an automatic swap: it keeps the look but not the dark-mode behaviour
const verdictColor = (d, palette = false) => (d <= 2 && !palette ? "swap" : d <= 6 ? "visible" : "review")
const verdictPx = (diff) => (diff === 0 ? "swap" : diff <= 2 ? "visible" : "review")

function scanFile(file) {
  const src = readFileSync(file, "utf8")
  const isCss = /\.(s?css)$/.test(file)
  const rel = posix(relative(cwd, file))
  const out = []
  const lines = src.split("\n")
  lines.forEach((line, i) => {
    if (/^\s*(\/\/|\*|\/\*)/.test(line) || /@theme|--[\w-]+\s*:/.test(line) && isCss) return // comments and token definitions themselves
    // 1. arbitrary Tailwind values: bg-[#123], p-[13px], rounded-[10px]
    // a class behind dark: is compared with the tokens' dark values
    const modeAt = (idx) => (/(?:^|[\s"'`])(?:[\w-]+:)*dark:(?:[\w-]+:)*$/.test(line.slice(0, idx)) ? "dark" : "light")
    for (const m of line.matchAll(/\b(bg|text|border|ring|fill|stroke|from|via|to|outline|divide|decoration|shadow)-\[([^\]]+)\]/g)) {
      const c = parseColor(m[2].replace(/_/g, " "))
      if (!c) continue
      const mode = modeAt(m.index)
      const near = nearestColor(c, m[1], mode)
      out.push({ kind: "colour", file: rel, line: i + 1, literal: m[0], value: m[2], prefix: m[1], mode, near, verdict: verdictColor(near[0].deltaE, near[0].palette), replacement: `${m[1]}-${near[0].token}` })
    }
    // white and black are colours too: bg-white is not the theme's background
    if (!isCss) for (const m of line.matchAll(/\b(bg|text|border|ring|fill|stroke|from|via|to|outline|divide)-(white|black)(?:\/(\d+|\[[^\]]+\]))?(?![\w-])/g)) {
      const mode = modeAt(m.index)
      const near = nearestColor(parseColor(m[2]), m[1], mode)
      out.push({ kind: "colour", file: rel, line: i + 1, literal: m[0], value: m[2], prefix: m[1], mode, near, verdict: m[3] ? "review" : "visible", replacement: m[3] ? undefined : `${m[1]}-${near[0].token}`, note: m[3] ? "Translucent white/black — check against the surface it sits on." : "Fixed white/black does not follow dark mode; the token does. Shown as visible: the swap changes the dark look on purpose." })
    }
    for (const m of line.matchAll(/\b(p|px|py|pt|pr|pb|pl|ps|pe|m|mx|my|mt|mr|mb|ml|gap|gap-x|gap-y|space-x|space-y|inset|top|right|bottom|left)-\[(\d+(?:\.\d+)?)px\]/g)) {
      const px = parseFloat(m[2]), s = SPACING(px)
      out.push({ kind: "spacing", file: rel, line: i + 1, literal: m[0], value: `${px}px`, near: [{ token: `${m[1]}-${s.tw}`, px: s.px, diff: Math.abs(s.px - px) }], verdict: verdictPx(Math.abs(s.px - px)), replacement: `${m[1]}-${s.tw}` })
    }
    for (const m of line.matchAll(/\brounded(-[trblse]{1,2})?-\[(\d+(?:\.\d+)?)px\]/g)) {
      const px = parseFloat(m[2]), r = nearestRadius(px)
      out.push({ kind: "radius", file: rel, line: i + 1, literal: m[0], value: `${px}px`, near: [{ token: `rounded${m[1] ?? ""}-${r.name}`, px: r.px, diff: r.diff }], verdict: verdictPx(r.diff), replacement: `rounded${m[1] ?? ""}-${r.name}` })
    }
    // 2. CSS declarations and style objects
    const decl = isCss ? [...line.matchAll(/(color|background(?:-color)?|border(?:-[a-z]+)?-color|border|fill|stroke|outline-color|box-shadow)\s*:\s*([^;]+)/g)] : [...line.matchAll(/\b(color|background(?:Color)?|border(?:[A-Z][a-z]+)?Color|borderColor|fill|stroke)\s*:\s*["'`]([^"'`]+)["'`]/g)]
    for (const m of decl) {
      for (const cm of m[2].matchAll(COLOR_RE)) {
        const c = parseColor(cm[0])
        if (!c) continue
        const near = nearestColor(c, /color$|^color|fill|stroke/i.test(m[1]) && !/background|border/i.test(m[1]) ? "text" : /border|outline/i.test(m[1]) ? "border" : "bg")
        out.push({ kind: "colour", file: rel, line: i + 1, literal: cm[0], value: cm[0], prop: m[1], near, verdict: c.a < 1 ? "review" : verdictColor(near[0].deltaE, near[0].palette), replacement: `var(${near[0].var})`, note: c.a < 1 ? "Translucent — check against the surface it sits on." : undefined })
      }
    }
    const spacingDecl = isCss ? [...line.matchAll(/\b(padding|margin|gap|row-gap|column-gap)(?:-[a-z]+)?\s*:\s*([^;]+)/g)] : [...line.matchAll(/\b(padding|margin|gap|rowGap|columnGap)(?:[A-Z][a-z]+)?\s*:\s*["'`]?([\d.]+(?:px)?(?:\s+[\d.]+px)*)["'`]?/g)]
    for (const m of spacingDecl) for (const pm of m[2].matchAll(/(\d+(?:\.\d+)?)px/g)) {
      const px = parseFloat(pm[1])
      if (px === 0) continue
      const s = SPACING(px)
      out.push({ kind: "spacing", file: rel, line: i + 1, literal: `${m[1]}: ${pm[0]}`, value: pm[0], near: [{ token: `${s.px}px (Tailwind ${s.tw})`, px: s.px, diff: Math.abs(s.px - px) }], verdict: verdictPx(Math.abs(s.px - px)), replacement: `calc(var(--spacing) * ${s.tw})` })
    }
    const radiusDecl = isCss ? [...line.matchAll(/\bborder(?:-[a-z]+)*-radius\s*:\s*(\d+(?:\.\d+)?)px/g)] : [...line.matchAll(/\bborder(?:[A-Z][a-z]+)*Radius\s*:\s*["'`]?(\d+(?:\.\d+)?)(?:px)?/g)]
    for (const m of radiusDecl) {
      const px = parseFloat(m[1]), r = nearestRadius(px)
      if (px === 0 || px >= 999) continue
      out.push({ kind: "radius", file: rel, line: i + 1, literal: m[0], value: `${px}px`, near: [{ token: `--radius-${r.name}`, px: r.px, diff: r.diff }], verdict: verdictPx(r.diff), replacement: `var(--radius-${r.name})` })
    }
    // 3. Tailwind's own palette (bg-blue-500) — not WunderUI tokens
    for (const m of line.matchAll(/\b(bg|text|border|ring|fill|stroke|from|via|to)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900|950)\b/g)) {
      if (TOKENS.colors[`${m[2]}-${m[3]}`]) continue // the palette name exists in WunderUI too
      out.push({ kind: "palette", file: rel, line: i + 1, literal: m[0], value: m[0], near: [], verdict: "review", note: "Tailwind palette colour, not a WunderUI token — pick the semantic token for its role (text-text-secondary, bg-muted, border-border, text-text-error …)." })
    }
  })
  return out
}

function summarise(findings) {
  const by = (k) => findings.reduce((a, f) => ((a[f[k]] = (a[f[k]] ?? 0) + 1), a), {})
  return { total: findings.length, byKind: by("kind"), byVerdict: by("verdict"), files: Object.keys(by("file")).length }
}

if (cmd === "scan") {
  const list = files(args.slice(1))
  const findings = list.flatMap(scanFile).map((f, i) => ({ id: `T-${String(i + 1).padStart(3, "0")}`, ...f }))
  mkdirSync(dirname(OUT), { recursive: true })
  writeFileSync(OUT, JSON.stringify({ scanned: list.length, tokens: TOKENS.source, findings }, null, 2) + "\n")
  const s = summarise(findings)
  console.log(JSON.stringify({ scanned: list.length, ...s, report: posix(relative(cwd, OUT)) }, null, 2))
  const show = (v) => findings.filter((f) => f.verdict === v).slice(0, 15).map((f) => `${f.id} ${f.file}:${f.line}  ${f.literal}  →  ${f.replacement ?? "—"}${f.near?.[0]?.deltaE !== undefined ? `  (ΔE ${f.near[0].deltaE})` : f.near?.[0]?.diff !== undefined ? `  (${f.near[0].diff}px off)` : ""}`)
  for (const v of ["swap", "visible", "review"]) if (s.byVerdict[v]) console.log(`\n${v} (${s.byVerdict[v]}):\n` + show(v).join("\n"))
} else if (cmd === "show") {
  const data = JSON.parse(readFileSync(OUT, "utf8"))
  console.log(JSON.stringify(data.findings.find((f) => f.id === args[1]) ?? { error: "no such id" }, null, 2))
} else if (cmd === "fix") {
  const data = JSON.parse(readFileSync(OUT, "utf8"))
  // --ids T-001,T-004 applies exactly those (any verdict); --pick T-003=2 uses the 2nd suggestion
  const allowed = new Set(["swap", ...(args.includes("--visible") ? ["visible"] : [])])
  const optOf = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined }
  const ids = optOf("--ids")?.split(",").map((s) => s.trim())
  const picks = Object.fromEntries((optOf("--pick") ?? "").split(",").filter(Boolean).map((p) => p.split("=").map((s) => s.trim())))
  for (const f of data.findings) {
    const n = Number(picks[f.id])
    if (n > 1 && f.kind === "colour" && f.near?.[n - 1]) {
      const alt = f.near[n - 1]
      f.near = [alt, ...f.near.filter((x) => x !== alt)]
      f.replacement = f.literal.includes("[") || /^(bg|text|border|ring|fill|stroke|from|via|to|outline|divide)-(white|black)/.test(f.literal) ? `${f.prefix}-${alt.token}` : `var(${alt.var})`
    }
  }
  const todo = data.findings.filter((f) => (ids ? ids.includes(f.id) || f.id in picks : allowed.has(f.verdict) || f.id in picks) && f.replacement && f.kind !== "palette")
  const byFile = Object.groupBy ? Object.groupBy(todo, (f) => f.file) : todo.reduce((a, f) => ((a[f.file] ??= []).push(f), a), {})
  const applied = []
  for (const [file, list] of Object.entries(byFile)) {
    const lines = readFileSync(join(cwd, file), "utf8").split("\n")
    for (const f of list) {
      const i = f.line - 1
      const isCss = /\.(s?css)$/.test(file)
      // arbitrary classes are replaced whole; declarations keep their property and swap the value
      const target = f.literal.includes("[") ? f.literal : f.kind === "colour" ? f.literal : f.kind === "radius" && isCss ? f.literal : null
      if (!target || !lines[i].includes(target)) continue
      const repl = f.literal.includes("[") ? f.replacement : f.kind === "colour" ? (isCss ? f.replacement : f.replacement) : `border-radius: ${f.replacement}`
      lines[i] = lines[i].replace(target, repl)
      applied.push({ id: f.id, file, line: f.line, from: target, to: repl, deltaE: f.near?.[0]?.deltaE, pxOff: f.near?.[0]?.diff })
    }
    writeFileSync(join(cwd, file), lines.join("\n"))
  }
  const maxDE = Math.max(0, ...applied.map((a) => a.deltaE ?? 0))
  const maxPx = Math.max(0, ...applied.map((a) => a.pxOff ?? 0))
  console.log(JSON.stringify({ applied: applied.length, largestColourShift: `ΔE ${maxDE.toFixed(2)}`, largestPxShift: `${maxPx}px`, changes: applied }, null, 2))
} else {
  console.log("usage: token-check.mjs scan [paths…] | show <id> | fix [--visible]")
  process.exit(cmd ? 1 : 0)
}
