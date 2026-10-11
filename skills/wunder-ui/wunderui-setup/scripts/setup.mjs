#!/usr/bin/env node
// WunderUI setup helper — no dependencies, Node 20+. Run in the project root.
//
//   setup.mjs detect        → .wunderui/setup.json (framework, Tailwind, CSS entry, package, tokens; --plan free|core|pro)
//   setup.mjs install       → @wunderui/react from node_modules, a packed checkout copy, or npm
//   setup.mjs agent-files   → .wunderui/DESIGN.md + design.json
//   setup.mjs mcp           → MCP server entry for Claude Code / Cursor / VS Code
//   setup.mjs styles        → @import + @source in the CSS entry
//   setup.mjs probe         → a probe page with Card, Button, Badge, Input
//   setup.mjs report        → .wunderui/SETUP.md
//
// Options: --checkout <path to a wunderui-core checkout>, --dry (print, write nothing)
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync, copyFileSync } from "node:fs"
import { dirname, join, relative, resolve, sep } from "node:path"
import { execSync } from "node:child_process"

const cwd = process.cwd()
const args = process.argv.slice(2)
const cmd = args[0]
const flag = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : undefined }
const DRY = args.includes("--dry")
const STATE = join(cwd, ".wunderui", "setup.json")
const posix = (p) => p.split(sep).join("/")
const readJSON = (f) => { try { return JSON.parse(readFileSync(f, "utf8")) } catch { return null } }
const state = () => readJSON(STATE) ?? {}
const save = (s) => { if (DRY) return; mkdirSync(dirname(STATE), { recursive: true }); writeFileSync(STATE, JSON.stringify(s, null, 2) + "\n") }
const log = (o) => console.log(typeof o === "string" ? o : JSON.stringify(o, null, 2))
const write = (file, text, changes) => {
  if (!DRY) { mkdirSync(dirname(file), { recursive: true }); writeFileSync(file, text) }
  changes.push(posix(relative(cwd, file)))
}
const SKIP_DIRS = new Set(["node_modules", ".git", ".next", "dist", "build", ".turbo", ".vercel", "out", "coverage", ".wunderui"])
function walk(dir, test, acc = [], depth = 0) {
  if (depth > 6) return acc
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue
    const p = join(dir, name)
    let st
    try { st = statSync(p) } catch { continue }
    if (st.isDirectory()) walk(p, test, acc, depth + 1)
    else if (test(p)) acc.push(p)
  }
  return acc
}

function findCheckout() {
  const given = flag("--checkout")
  const candidates = [given, join(cwd, "..", "wunderui-core"), join(cwd, "..", "..", "wunderui-core"), join(cwd, "wunderui-core")].filter(Boolean)
  return candidates.map((c) => resolve(c)).find((c) => existsSync(join(c, "packages", "react", "package.json")))
}

function detect() {
  const pkg = readJSON(join(cwd, "package.json"))
  if (!pkg) { log({ error: "No package.json in " + cwd }); process.exit(1) }
  const deps = { ...pkg.dependencies, ...pkg.devDependencies }
  const framework = deps.next ? (existsSync(join(cwd, "app")) || existsSync(join(cwd, "src", "app")) ? "next-app" : "next-pages")
    : deps["@react-router/dev"] || deps["@remix-run/react"] ? "react-router"
    : deps.astro ? "astro"
    : deps.vite ? "vite"
    : deps.react ? "react" : null
  const installedTw = readJSON(join(cwd, "node_modules", "tailwindcss", "package.json"))?.version
  const tailwind = installedTw ?? deps.tailwindcss ?? null
  const twMajor = tailwind ? Number(String(tailwind).replace(/^[^\d]*/, "").split(".")[0]) : null
  const cssFiles = walk(cwd, (p) => p.endsWith(".css"))
  const entry = cssFiles.find((f) => /@import\s+["']tailwindcss["']|@tailwind\s+base/.test(readFileSync(f, "utf8")))
  const tokens = []
  for (const f of cssFiles) {
    for (const m of readFileSync(f, "utf8").matchAll(/(--[\w-]+)\s*:\s*(#[0-9a-f]{3,8}\b|(?:rgb|hsl|oklch)a?\([^)]*\))/gi)) tokens.push({ file: posix(relative(cwd, f)), name: m[1], value: m[2] })
  }
  const installed = readJSON(join(cwd, "node_modules", "@wunderui", "react", "package.json"))
  const checkout = findCheckout()
  const s = {
    ...state(),
    project: pkg.name ?? null,
    // the WunderUI plan decides which components other skills may use (free = tier "free" only)
    plan: ["free", "core", "pro"].includes(flag("--plan")) ? flag("--plan") : state().plan ?? null,
    framework,
    react: deps.react ?? null,
    tailwind,
    tailwindV4: twMajor === 4,
    cssEntry: entry ? posix(relative(cwd, entry)) : null,
    package: installed ? { source: "node_modules", version: installed.version } : checkout ? { source: "checkout", path: posix(checkout) } : { source: "npm" },
    existingTokens: tokens.slice(0, 60),
    existingTokenCount: tokens.length,
    detectedAt: new Date().toISOString(),
  }
  const problems = []
  if (!framework) problems.push("No React found in package.json.")
  if (twMajor !== 4) problems.push(tailwind ? `Tailwind ${tailwind} — WunderUI needs Tailwind v4.` : "Tailwind is not installed — WunderUI needs Tailwind v4.")
  if (!entry) problems.push("No CSS file imports Tailwind yet.")
  s.problems = problems
  save(s)
  log(s)
}

async function agentFiles() {
  const s = state()
  const changes = []
  const out = join(cwd, ".wunderui")
  const sources = [
    join(cwd, "node_modules", "@wunderui", "react"),
    s.package?.path && join(s.package.path, "agent"),
    s.package?.path && join(s.package.path, "packages", "mcp", "data"),
  ].filter(Boolean)
  for (const file of ["DESIGN.md", "design.json", "INSTRUCTIONS.md"]) {
    const local = sources.map((d) => join(d, file)).find((f) => existsSync(f))
    if (local) { if (!DRY) { mkdirSync(out, { recursive: true }); copyFileSync(local, join(out, file)) } changes.push(`.wunderui/${file} (from ${posix(relative(cwd, local))})`); continue }
    const res = await fetch(`https://wunderui.com/${file}`).catch(() => null)
    if (!res?.ok) { log({ error: `Could not get ${file} — no local copy and https://wunderui.com/${file} did not answer.` }); continue }
    write(join(out, file), await res.text(), changes)
  }
  // the short always-on rules go into the agent's rules file itself; DESIGN.md stays a reference beside it
  const instructions = existsSync(join(out, "INSTRUCTIONS.md")) ? readFileSync(join(out, "INSTRUCTIONS.md"), "utf8").trim() : null
  const note = "UI work follows .wunderui/DESIGN.md — read its \"Rules for agents\" first."
  const block = instructions ? `<!-- wunderui:instructions -->\n${instructions}\n\n${note}\n<!-- /wunderui:instructions -->` : note
  const agentFile = ["CLAUDE.md", "AGENTS.md"].map((f) => join(cwd, f)).find((f) => existsSync(f)) ?? join(cwd, "CLAUDE.md")
  const current = existsSync(agentFile) ? readFileSync(agentFile, "utf8") : ""
  if (current.includes("<!-- wunderui:instructions -->")) {
    // refresh the block in place, so a later run picks up new rules
    const next = current.replace(/<!-- wunderui:instructions -->[\s\S]*?<!-- \/wunderui:instructions -->/, block)
    if (next !== current) write(agentFile, next, changes)
  } else if (!current.includes(".wunderui/DESIGN.md") || instructions) {
    write(agentFile, (current ? current.trimEnd() + "\n\n" : "") + block + "\n", changes)
  }
  // the scripts of the other skills write their results here — keep those out of git, keep the agent files and the packed package
  const ignore = join(out, ".gitignore")
  if (!existsSync(ignore)) write(ignore, ["# WunderUI skill outputs (regenerated on every run)", "*.json", "!design.json", "!setup.json", "motion-audit.md", "a11y*.md", "figma-write.js", ""].join("\n"), changes)
  save({ ...s, agentFiles: changes })
  log({ changed: changes })
}

// From a checkout, install a packed copy — never `npm install <path>`: that symlinks a folder outside
// the project, which Turbopack refuses ("leaves the filesystem root") and which resolves React twice.
function install() {
  const s = state()
  const changes = []
  if (s.package?.source === "node_modules") { log({ note: `@wunderui/react ${s.package.version} is installed already.` }); return }
  let target = "@wunderui/react"
  if (s.package?.source === "checkout") {
    const pkgDir = join(s.package.path, "packages", "react")
    if (!existsSync(join(pkgDir, "dist", "index.js"))) { log({ error: `${posix(pkgDir)}/dist is missing — run \`npm install && npm run build\` in the checkout first.` }); process.exit(1) }
    const out = join(cwd, ".wunderui")
    mkdirSync(out, { recursive: true })
    const packed = execSync(`npm pack "${pkgDir}" --pack-destination "${out}" --silent`, { cwd, encoding: "utf8" }).trim().split("\n").pop()
    target = `./.wunderui/${packed}`
    changes.push(`.wunderui/${packed}`)
  }
  if (DRY) { log({ would: `npm install ${target}` }); return }
  execSync(`npm install ${target}`, { cwd, stdio: "inherit" })
  changes.push("package.json")
  save({ ...state(), package: { ...s.package, installed: target } })
  log({ installed: target, changed: changes, note: s.package?.source === "checkout" ? "Re-run `setup.mjs install` after `git pull` + build in the checkout to update." : undefined })
}

function mcp() {
  const s = state()
  const checkout = s.package?.path
  const local = checkout && existsSync(join(checkout, "packages", "mcp", "src", "index.mjs"))
  const server = local
    ? { command: "node", args: [posix(join(checkout, "packages", "mcp", "src", "index.mjs"))] }
    : { command: "npx", args: ["-y", "wunderui-mcp"] }
  const changes = []
  const targets = [[join(cwd, ".mcp.json"), "mcpServers"]]
  if (existsSync(join(cwd, ".cursor"))) targets.push([join(cwd, ".cursor", "mcp.json"), "mcpServers"])
  if (existsSync(join(cwd, ".vscode"))) targets.push([join(cwd, ".vscode", "mcp.json"), "servers"])
  for (const [file, key] of targets) {
    const json = readJSON(file) ?? {}
    json[key] = { ...json[key], wunderui: key === "servers" ? { type: "stdio", ...server } : server }
    write(file, JSON.stringify(json, null, 2) + "\n", changes)
  }
  const needsInstall = local && !existsSync(join(checkout, "packages", "mcp", "node_modules")) && !existsSync(join(checkout, "node_modules", "@modelcontextprotocol"))
  save({ ...s, mcp: { server, files: changes, needsInstall } })
  log({ server, changed: changes, note: needsInstall ? `Run \`npm install\` in ${checkout} once — the MCP server needs its dependencies.` : "Restart the agent to load the wunderui MCP tools, then call get_library_info." })
}

function styles() {
  const s = state()
  if (!s.cssEntry) { log({ error: "No CSS entry found — run detect first, or create one that starts with @import \"tailwindcss\";" }); process.exit(1) }
  const file = join(cwd, s.cssEntry)
  let css = readFileSync(file, "utf8")
  const dist = join(cwd, "node_modules", "@wunderui", "react", "dist")
  let rel = posix(relative(dirname(file), dist))
  if (!rel.startsWith(".")) rel = "./" + rel
  const changes = []
  const lines = []
  if (!/@import\s+["']@wunderui\/react\/styles\.css["']/.test(css)) lines.push('@import "@wunderui/react/styles.css";')
  if (!/@source\s+["'][^"']*@wunderui\/react\/dist["']/.test(css)) lines.push(`@source "${rel}";`)
  if (lines.length) {
    const tw = /@import\s+["']tailwindcss["'][^;]*;/.exec(css)
    css = tw ? css.slice(0, tw.index + tw[0].length) + "\n" + lines.join("\n") + css.slice(tw.index + tw[0].length) : lines.join("\n") + "\n" + css
  }
  // --drop-defaults (after the user agreed): remove the starter template's own colours and body font,
  // which otherwise win over WunderUI's tokens. Only blocks that hold nothing but those defaults go.
  const dropped = []
  if (args.includes("--drop-defaults")) {
    const onlyBgFg = (body) => body.split(";").map((d) => d.trim()).filter(Boolean).every((d) => /^--(background|foreground)\s*:/.test(d))
    css = css.replace(/@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^{}]*)\}\s*\}\s*/g, (m, body) => (onlyBgFg(body) ? (dropped.push("dark-mode media query with --background/--foreground"), "") : m))
    css = css.replace(/:root\s*\{([^{}]*)\}\s*/g, (m, body) => (onlyBgFg(body) ? (dropped.push(":root --background/--foreground"), "") : m))
    for (let before = ""; before !== css; ) {
      before = css
      css = css.replace(/(@theme\s+inline\s*\{[^{}]*?)\s*--color-(background|foreground)\s*:\s*var\(--\2\);/, (m, head, name) => (dropped.push(`@theme --color-${name}`), head))
    }
    css = css.replace(/body\s*\{([^{}]*)\}\s*/g, (m, body) => {
      const decls = body.split(";").map((d) => d.trim()).filter(Boolean)
      return decls.every((d) => /^(background|color)\s*:\s*var\(--(background|foreground)\)$|^font-family\s*:\s*Arial/.test(d)) ? (dropped.push("body background/color/Arial"), "") : m
    })
    css = css.replace(/@theme\s+inline\s*\{\s*\}\s*/g, "")
  }
  if (lines.length || dropped.length) write(file, css.replace(/\n{3,}/g, "\n\n"), changes)
  save({ ...s, styles: { file: s.cssEntry, added: lines, dropped } })
  log({ file: s.cssEntry, added: lines, dropped, note: lines.length || dropped.length ? "Order: tailwindcss, then WunderUI, then the project's own :root overrides." : "Already wired." })
}

function probe() {
  const s = state()
  const appDir = ["app", "src/app"].map((d) => join(cwd, d)).find((d) => existsSync(d))
  const file = s.framework === "next-app" && appDir ? join(appDir, "wunderui-probe", "page.tsx") : join(cwd, existsSync(join(cwd, "src")) ? "src" : ".", "wunderui-probe.tsx")
  const client = s.framework === "next-app" ? '"use client"\n\n' : ""
  const body = `${client}import { Badge, Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input } from "@wunderui/react"

/** WunderUI probe — delete it once the setup is confirmed. */
export default function WunderUIProbe() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-10 text-foreground">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">WunderUI is set up <Badge color="green" badgeStyle="light" shape="pill">Live</Badge></CardTitle>
          <CardDescription>Tokens, Tailwind and the package are wired.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Input placeholder="you@example.com" aria-label="Email" />
          <Button data-wunderui-probe>Continue</Button>
        </CardContent>
      </Card>
    </main>
  )
}
`
  const changes = []
  if (existsSync(file)) log({ note: "Probe exists already", file: posix(relative(cwd, file)) })
  else write(file, body, changes)
  const route = s.framework === "next-app" ? "/wunderui-probe" : "(render <WunderUIProbe /> from your app entry)"
  save({ ...s, probe: { file: posix(relative(cwd, file)), route } })
  log({ file: posix(relative(cwd, file)), route, check: "In the browser: getComputedStyle(document.querySelector('[data-wunderui-probe]')).backgroundColor must not be transparent." })
}

function report() {
  const s = state()
  // re-read what may have changed since detect: the installed package and the project's own colour tokens
  const installed = readJSON(join(cwd, "node_modules", "@wunderui", "react", "package.json"))
  if (installed) s.package = { ...s.package, source: s.package?.installed?.endsWith(".tgz") ? "checkout" : "node_modules", version: installed.version }
  if (s.cssEntry && existsSync(join(cwd, s.cssEntry))) s.existingTokenCount = [...readFileSync(join(cwd, s.cssEntry), "utf8").matchAll(/(--[\w-]+)\s*:\s*(#[0-9a-f]{3,8}\b|(?:rgb|hsl|oklch)a?\([^)]*\))/gi)].length
  const lines = [
    "# WunderUI setup",
    "",
    `Project: ${s.project ?? "—"} · ${s.framework ?? "unknown framework"} · React ${s.react ?? "—"} · Tailwind ${s.tailwind ?? "—"} · Plan: ${s.plan ?? "not set"}`,
    "",
    "## What was found",
    `- CSS entry: ${s.cssEntry ?? "none"}`,
    `- Package: ${s.package?.version ? `@wunderui/react ${s.package.version} installed` : "not installed yet"}${s.package?.source === "checkout" ? ` (packed from the checkout ${s.package.path})` : ""}`,
    `- Existing colour tokens in the project: ${s.existingTokenCount ?? 0}`,
    "",
    "## What changed",
    ...[...(s.agentFiles ?? []), ...(s.mcp?.files ?? []), ...(s.styles?.added?.length ? [`${s.styles.file}: ${s.styles.added.join(" ")}`] : []), ...(s.probe ? [`${s.probe.file} (probe)`] : [])].map((c) => `- ${c}`),
    "",
    "## Open",
    ...[...(s.problems ?? []), ...(s.mcp?.needsInstall ? ["Install the MCP server's dependencies in the checkout."] : []), ...(s.mcp ? ["Restart the agent so the wunderui MCP tools load."] : ["MCP server not registered yet."])].map((p) => `- ${p}`),
    "",
    "## Next",
    "- Build a first screen: ask for it in one sentence (skill wunderui-screen).",
    "- Check hard-coded colours, spacing and radii: skill wunderui-token-check.",
    "- Read `.wunderui/DESIGN.md` → \"Rules for agents\".",
    "",
  ]
  const changes = []
  write(join(cwd, ".wunderui", "SETUP.md"), lines.join("\n"), changes)
  log(lines.join("\n"))
}

const commands = { detect, install, "agent-files": agentFiles, mcp, styles, probe, report }
if (!commands[cmd]) { log("usage: setup.mjs detect | install | agent-files | mcp | styles | probe | report [--checkout <path>] [--dry]"); process.exit(cmd ? 1 : 0) }
await commands[cmd]()
