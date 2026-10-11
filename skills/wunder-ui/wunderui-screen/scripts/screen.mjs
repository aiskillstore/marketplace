#!/usr/bin/env node
// wunderui-screen helper — no dependencies, Node 20+. Run in the project root.
//
//   screen.mjs find "<keywords>"     best matching blocks (registry index) and components (design.json)
//   screen.mjs check <file…>         lint new screen files against the WunderUI rules (exit 1 on errors)
//
// --plan free|core|pro (default: .wunderui/setup.json → plan, else pro). On free, only components with
// tier "free" are suggested, Pro components are errors in `check`, and blocks are blueprints only.
//
// design.json is read from .wunderui/design.json, else fetched from wunderui.com.
// The block index comes from https://wunderui.com/api/registry/index (public).
import { existsSync, readFileSync } from "node:fs"
import { join, relative } from "node:path"

const argv = process.argv.slice(2)
const planFlag = argv.indexOf("--plan")
const PLAN = (planFlag >= 0 ? argv.splice(planFlag, 2)[1] : (() => { try { return JSON.parse(readFileSync(join(process.cwd(), ".wunderui", "setup.json"), "utf8")).plan } catch { return null } })()) ?? "pro"
const FREE = PLAN === "free"
const [cmd, ...rest] = argv
const SITE = process.env.WUNDERUI_SITE ?? "https://wunderui.com"

async function design() {
  const local = join(process.cwd(), ".wunderui", "design.json")
  if (existsSync(local)) return JSON.parse(readFileSync(local, "utf8"))
  const res = await fetch(`${SITE}/design.json`).catch(() => null)
  return res?.ok ? res.json() : null
}

const words = (s) => String(s ?? "").toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length > 1)
const STOP = new Set(["the", "and", "with", "for", "a", "an", "of", "to", "in", "on", "page", "screen", "view", "build", "make", "create"])
function score(query, text) {
  const t = new Set(words(text))
  let s = 0
  for (const w of query) if (t.has(w)) s += 2; else if ([...t].some((x) => x.startsWith(w) || w.startsWith(x))) s += 1
  return s
}

// Pro category → the Free components that come closest (same table as references/free-plan.md)
const STAND_INS = {
  Charts: ["Card", "NumberValue", "TrendChip", "Progress", "Meter"],
  KPI: ["Card", "NumberValue", "TrendChip", "Progress"],
  "Data Display": ["ItemCard", "Card", "Badge", "Pagination"],
  Primitives: ["ItemCard", "Card", "Badge", "Pagination"],
  Navigation: ["Breadcrumb", "Tabs", "Sheet"],
  Layout: ["Breadcrumb", "Tabs", "Sheet"],
  "Block Parts": ["Card", "Button", "Badge"],
  AI: ["Textarea", "Button", "Timeline", "Alert"],
  Agents: ["Timeline", "Alert", "Badge"],
}

async function find(q) {
  const query = words(q).filter((w) => !STOP.has(w))
  if (!query.length) { console.log('usage: screen.mjs find "<keywords>"'); process.exit(1) }
  const [index, d] = await Promise.all([fetch(`${SITE}/api/registry/index`).then((r) => (r.ok ? r.json() : null)).catch(() => null), design()])
  // block screens list their own building blocks too (AppFrame …) — mark what is not a library export
  const exported = new Set((d?.components ?? []).flatMap((c) => c.exports))
  const label = (u) => (exported.size && !exported.has(u) ? `${u} (block part, comes with the block)` : u)
  const blocks = (index?.blocks ?? []).flatMap((b) => b.screens.map((s) => ({ id: `${b.id}`, screen: s.slug, title: s.title, uses: s.uses.map(label), score: score(query, `${b.title} ${b.description} ${s.title} ${s.uses.join(" ")}`) })))
  const tierOf = (name) => (d?.components ?? []).find((c) => c.exports.includes(name))?.tier
  const comps = (d?.components ?? []).map((c) => ({ name: c.exports[0], slug: c.slug, category: c.category, plan: c.tier ?? "pro", description: c.description, score: score(query, `${c.title} ${c.description} ${c.category}`) }))
  const top = (arr, n) => arr.filter((x) => x.score > 0).sort((a, b) => b.score - a.score).slice(0, n)
  const matchedPro = top(comps, 12).filter((c) => c.plan === "pro")
  const out = {
    query,
    plan: PLAN,
    blocks: top(blocks, 8).map(({ score, ...b }) => (FREE
      // on Free a block is a blueprint: which of its parts exist in Free, which need Pro
      ? { id: b.id, screen: b.screen, title: b.title, freeParts: b.uses.filter((u) => tierOf(u) === "free"), proParts: b.uses.filter((u) => tierOf(u) === "pro") }
      : { ...b, add: `npx @wunderui/cli add ${b.id} --screen ${b.screen}` })),
    components: top(FREE ? comps.filter((c) => c.plan === "free") : comps, 12).map(({ score, ...c }) => c),
    ...(FREE && matchedPro.length ? { proWouldAdd: matchedPro.map((c) => `${c.name} — ${c.description}`) } : {}),
    // the Free stand-ins for the Pro parts the request needs (references/free-plan.md)
    ...(FREE && matchedPro.length ? { freeStandIns: [...new Set(matchedPro.flatMap((c) => STAND_INS[c.category] ?? []))] } : {}),
    notes: [
      !index && "Block index not reachable — build from components.",
      !d && "No design.json (run wunderui-setup, or check the network).",
      FREE ? "Free plan: build only with the components above; references/free-plan.md maps each Pro component to its closest Free stand-in. Tell the user what proWouldAdd lists." : "Block source needs WunderUI Pro; without it, use the block's `uses` list as the blueprint.",
    ].filter(Boolean),
  }
  console.log(JSON.stringify(out, null, 2))
}

// Rules run on style code only: strings on lines with className / class= / cn() / cva() / clsx(),
// style objects and CSS files — so copy like "Invoice #1024" or href="#add" is never read as a colour.
const STYLE_LINE = /className|class=|\bcn\(|\bcva\(|\bclsx\(|twMerge\(|style=\{/
const PALETTE = "slate|gray|zinc|neutral|stone|sky|teal|emerald|lime|amber|cyan|violet|fuchsia|rose"
const CLASS_RULES = [
  { id: "arbitrary-colour", level: "error", re: /\b(?:bg|text|border|ring|fill|stroke|from|to|via|outline|divide|decoration|shadow)-\[(?:#|rgb|hsl|oklch|color\()[^\]]*\]/g, msg: "Arbitrary colour value — use a token utility (bg-card, text-text-secondary …); wunderui-token-check finds the nearest." },
  { id: "palette-colour", level: "error", re: new RegExp(`\\b(?:bg|text|border|ring|fill|stroke|from|to|via|outline|divide|decoration)-(?:white|black|(?:${PALETTE})-\\d{2,3})(?:/\\d+)?\\b`, "g"), msg: "Tailwind palette colour, not a WunderUI token — bg-background, text-foreground, bg-muted, border-border, text-text-secondary …" },
  { id: "arbitrary-px", level: "warn", re: /\b(?:p[xytrblse]?|m[xytrblse]?|gap(?:-[xy])?|space-[xy]|rounded(?:-[trblse]{1,2})?)-\[\d+(?:\.\d+)?px\]/g, msg: "Arbitrary spacing/radius — the Tailwind scale (p-4, gap-6) and the radius tokens (rounded-md/lg/xl)." },
  { id: "transition-all", level: "error", re: /\btransition-all\b|\btransition-\[all\]/g, msg: "Never transition-all — name the properties (transition-[opacity,transform]) or use bare transition." },
  { id: "raw-duration", level: "error", re: /\bduration-(?:\d+|\[[^\]]+\])(?![-\w])/g, msg: "Raw duration — duration-instant|fast|base|slow|deliberate|ambient." },
  { id: "generic-easing", level: "error", re: /\bease-(?:in-out|in|out|linear)\b(?![-\w])|\bease-\[[^\]]+\]/g, msg: "Generic easing — ease-entrance (arriving), ease-exit (leaving), ease-move (repositioning)." },
]
const STYLE_RULES = [
  { id: "raw-colour", level: "error", re: /\b(?:color|background|backgroundColor|borderColor|outlineColor|fill|stroke)\s*:\s*["'`](?:#[0-9a-fA-F]{3,8}|rgba?\(|hsla?\(|oklch\(|[a-z]+["'`])/g, msg: "Hard-coded colour in a style object — var(--token) or a token utility." },
  { id: "raw-duration", level: "error", re: /\b(?:transition|animation)(?:Duration)?\s*:\s*["'`][^"'`]*\d+m?s/g, msg: "Raw duration in a style object — var(--duration-base) etc." },
  { id: "inline-style-px", level: "warn", re: /\b(?:padding|margin|gap|borderRadius)\w*\s*:\s*["'`]?\d+(?:px)?/g, msg: "Inline spacing/radius — the Tailwind scale (p-4, gap-6, rounded-xl)." },
]
const LINE_RULES = [
  { id: "deep-import", level: "error", re: /from\s+["']@wunderui\/react\/(dist|src)[^"']*["']/g, msg: "Import from the package root: \"@wunderui/react\"." },
  { id: "hand-table", level: "warn", re: /<table[\s>]/g, msg: "Hand-built <table> — DataGrid or Table from @wunderui/react?" },
]
const CSS_RULES = [
  { id: "raw-colour", level: "error", re: /(?:^|[;{\s])(?:color|background(?:-color)?|border(?:-\w+)?-color|fill|stroke)\s*:\s*(?:#[0-9a-fA-F]{3,8}|rgba?\(|hsla?\(|oklch\()/g, msg: "Hard-coded colour — var(--token)." },
  { id: "transition-all", level: "error", re: /transition(?:-property)?\s*:\s*all\b/g, msg: "Never transition: all." },
  { id: "raw-duration", level: "error", re: /(?:transition|animation)(?:-duration)?\s*:[^;]*?\b\d*\.?\d+m?s\b/g, msg: "Raw duration — var(--duration-base) etc." },
]
const strings = (line) => [...line.matchAll(/"([^"]*)"|'([^']*)'|`([^`]*)`/g)].map((m) => m[1] ?? m[2] ?? m[3])

async function check(files) {
  if (!files.length) { console.log("usage: screen.mjs check <file…>"); process.exit(1) }
  const d = FREE ? await design() : null
  const tierOf = (name) => (d?.components ?? []).find((c) => c.exports.includes(name))?.tier
  const findings = []
  const summary = []
  for (const file of files) {
    if (!existsSync(file)) { findings.push({ file, level: "error", rule: "missing", msg: "File not found" }); continue }
    const src = readFileSync(file, "utf8")
    const lines = src.split("\n")
    const isCss = /\.(s?css)$/.test(file)
    const add = (r, i, m) => findings.push({ file: relative(process.cwd(), file), line: i + 1, level: r.level, rule: r.id, match: m, msg: r.msg })
    lines.forEach((line, i) => {
      if (/^\s*(\/\/|\*|\/\*)/.test(line)) return
      if (isCss) { for (const r of CSS_RULES) for (const m of line.matchAll(r.re)) add(r, i, m[0].trim()); return }
      for (const r of LINE_RULES) for (const m of line.matchAll(r.re)) add(r, i, m[0])
      if (!STYLE_LINE.test(line)) return
      for (const str of strings(line)) for (const r of CLASS_RULES) for (const m of str.matchAll(r.re)) add(r, i, m[0])
      if (/style=\{|style:/.test(line)) for (const r of STYLE_RULES) for (const m of line.matchAll(r.re)) add(r, i, m[0])
    })
    const usesLib = /from\s+["']@wunderui\/react["']/.test(src)
    const imported = [...src.matchAll(/import\s*\{([^}]+)\}\s*from\s*["']@wunderui\/react["']/g)].flatMap((m) => m[1].split(",").map((s) => s.trim().split(/\s+as\s+/)[0]).filter(Boolean))
    const states = {
      // components or explicit state branches — words in the copy do not count
      loading: /\bloading(?:=\{|\s*\/?>|\s+[\w-]+=)|<Skeleton\b|===\s*["']loading["']/.test(src),
      empty: /<EmptyState\b|===\s*["']empty["']/.test(src),
      error: /<Alert\b|<RunError\b|===\s*["']error["']/.test(src),
    }
    // Free plan: every Pro component is a license problem, not a style issue
    if (FREE) for (const name of imported) if (tierOf(name) === "pro") findings.push({ file: relative(process.cwd(), file), level: "error", rule: "pro-component", match: name, msg: `${name} is a Pro component — on the Free plan use a Free stand-in (references/free-plan.md) and tell the user what Pro adds.` })
    const dataRegion = /<(DataGrid|Table|AreaChart|BarChart|LineChart|PieChart|DonutChart|ChartCard|KPIGroup|MetricCard|List|Kanban)\b|\.map\(/.test(src)
    if (!usesLib) findings.push({ file, level: "error", rule: "no-library", msg: "Nothing is imported from @wunderui/react." })
    if (dataRegion) for (const [state, ok] of Object.entries(states)) if (!ok) findings.push({ file: relative(process.cwd(), file), level: "error", rule: `state-${state}`, msg: `No ${state} state found for the data on this screen (see references/states.md).` })
    if (/^\s*["']use client["']/.test(src) === false && /\buse(State|Effect|Reducer|Ref)\(/.test(src) && /[\\/]app[\\/]/.test(file)) findings.push({ file, level: "warn", rule: "use-client", msg: "Hooks in an App Router file without \"use client\"." })
    summary.push({ file: relative(process.cwd(), file), components: imported, states, dataRegion })
  }
  const errors = findings.filter((f) => f.level === "error").length
  console.log(JSON.stringify({ plan: PLAN, errors, warnings: findings.length - errors, summary, findings }, null, 2))
  process.exit(errors ? 1 : 0)
}

if (cmd === "find") await find(rest.join(" "))
else if (cmd === "check") await check(rest)
else { console.log('usage: screen.mjs find "<keywords>" | check <file…>'); process.exit(cmd ? 1 : 0) }
