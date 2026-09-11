import { spawn } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import { existsSync } from "node:fs";
import { cp, mkdir, mkdtemp, readFile, readdir, writeFile } from "node:fs/promises";
import { createServer } from "node:net";
import { basename, join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { executeReadOnly, ensureMigrated, readAppliedMigrationHashes } from "../lib/db";
import { HELP, backgroundArgv, pendingFrom } from "../lib/cli-helpers";
import { ensureRunSecret } from "../lib/local-env";
import { diagramCost, parseDiagramSpec } from "../lib/diagram-spec";
import { overlayRun } from "../lib/diagram-overlay";
import { renderPng, renderSvg } from "../lib/diagram-svg";
import { layoutGraph } from "../lib/layout";
import { redact } from "../lib/redact";
import { childEnv } from "../lib/agent";

type Flags = Record<string, string | boolean>;
const root = process.cwd();
class AppError extends Error { constructor(readonly code: string, message: string, readonly exitCode = 1) { super(message); } }

main().catch((caught) => { const error = caught instanceof AppError ? caught : new AppError("internal_error", redact(caught)); process.stderr.write(`${JSON.stringify({ error: { code: error.code, message: error.message } })}\n`); process.exitCode = error.exitCode; });

async function main() {
  const [command = "help", ...rest] = process.argv.slice(2);
  if (["help", "--help", "-h"].includes(command) || rest.includes("--help")) return help();
  if (command === "run") return run(rest);
  if (command === "runs" && rest[0] === "get") return runsGet(rest.slice(1));
  if (command === "query") return query(rest);
  if (command === "check") return print(await check());
  if (command === "verify") return verify(rest);
  if (command === "diagram") return diagram(rest);
  if (command === "approve") return approve(rest);
  if (command === "cancel") return cancel(rest);
  if (command === "upgrade") return upgrade(rest);
  throw new AppError("invalid_command", "Use run, runs get, query, check, verify, diagram, approve, cancel, upgrade, or help.", 2);
}

function help() { process.stdout.write(HELP); }
function parse(args: string[]) { const positionals: string[] = [], flags: Flags = {}; for (let i = 0; i < args.length; i++) { const value = args[i]; if (!value.startsWith("--")) positionals.push(value); else { const key = value.slice(2); flags[key] = args[i + 1] && !args[i + 1].startsWith("--") ? args[++i] : true; } } return { positionals, flags }; }
function text(flags: Flags, name: string) { const value = flags[name]; return typeof value === "string" ? value : undefined; }
function print(value: unknown) { process.stdout.write(`${JSON.stringify(value, null, 2)}\n`); }
function workflowPath(file: string) { return relative(join(root, "workflows"), file).replace(/\.ts$/, "").split("\\").join("/"); }
async function workflowFile(slug: string) { const matches = await walk(join(root, "workflows"), (file) => file.endsWith(`${slug}.ts`)); if (!matches.length) throw new AppError("not_found", `No workflow named ${slug}.`, 2); if (matches.length > 1) throw new AppError("ambiguous_workflow", `More than one workflow is named ${slug}.`, 2); return matches[0]; }
async function walk(directory: string, accept: (path: string) => boolean): Promise<string[]> { if (!existsSync(directory)) return []; const result: string[] = []; for (const entry of await readdir(directory, { withFileTypes: true })) { const path = join(directory, entry.name); if (entry.isDirectory()) result.push(...await walk(path, accept)); else if (accept(path)) result.push(path); } return result; }

async function dryPlan(slug: string, inputFile: string) {
  const file = await workflowFile(slug), source = await readFile(file, "utf8"), module = await import(`${pathToFileURL(file).href}?t=${Date.now()}`);
  const body = JSON.parse(await readFile(resolve(inputFile), "utf8"));
  const parsed = module.input?.parse ? module.input.parse(body) : body;
  const rows = Array.isArray(parsed?.rows) ? parsed.rows.length : 1;
  const graph = parseDiagramSpec(source, workflowPath(file));
  const costPerRowUsd = diagramCost(graph), maxRows = Number(module.MAX_ROWS ?? rows), maxSpendUsd = Number(module.MAX_SPEND_USD ?? rows * costPerRowUsd);
  const projectedCostUsd = rows * costPerRowUsd;
  return { file, source, body, graph, plan: { workflow: slug, rows, paidStages: graph.nodes.filter((node) => node.unitCostUsd !== undefined).map((node) => ({ label: node.label, cost: `${node.upperBound ? "up to " : ""}$${node.unitCostUsd}/row` })), maxRows, costPerRowUsd, projectedCostUsd, maxSpendUsd, withinCaps: rows <= maxRows && projectedCostUsd <= maxSpendUsd } };
}

async function run(args: string[]) {
  const { positionals, flags } = parse(args), slug = positionals[0], inputFile = text(flags, "input");
  if (!slug || !inputFile) throw new AppError("invalid_input", "run requires <workflow> --input <file>.", 2);
  const dry = await dryPlan(slug, inputFile); if (flags["dry-run"]) return print(dry.plan); if (!dry.plan.withinCaps) throw new AppError("caps_exceeded", "The input exceeds the accepted workflow caps.", 2);
  if (flags.background) return background(slug, args);
  const origin = await originFor(flags); if (flags["wait-live"]) await waitLive(origin);
  const url = new URL(`/api/run/${workflowPath(dry.file)}`, origin); const checkpoint = text(flags, "checkpoint"); if (checkpoint) url.searchParams.set("checkpoint", checkpoint);
  const result = await request(url, { method: "POST", headers: { ...auth(), "x-gtm-workspace-head": await gitHead() }, body: JSON.stringify(dry.body) });
  print(result);
}

/** Start the same run in a detached process and return at once; the caller watches /api/runs/latest for it. */
async function background(slug: string, args: string[]) {
  const head = await gitHead(); await mkdir(join(root, "data"), { recursive: true });
  const log = join(root, "data", `background-${slug}.log`); const { openSync } = await import("node:fs"); const fd = openSync(log, "a");
  const child = spawn(process.execPath, [...process.execArgv, process.argv[1], "run", ...backgroundArgv(args)], { cwd: root, env: process.env, detached: true, stdio: ["ignore", fd, fd] });
  child.unref();
  print({ background: true, workflow: slug, head, log: relative(root, log) });
}

async function runsGet(args: string[]) {
  const { positionals, flags } = parse(args), id = positionals[0]; if (!id) throw new AppError("invalid_run", "runs get requires an id.", 2);
  const origin = await originFor(flags), seconds = Number(text(flags, "wait") ?? 0), deadline = Date.now() + seconds * 1000;
  while (true) { const row = await request(new URL(`/api/runs/${encodeURIComponent(id)}`, origin), { headers: auth() }); if (!seconds || !["running", "waiting", "cancelling"].includes(row.status) || Date.now() >= deadline) return print(row); await new Promise((resolve) => setTimeout(resolve, 2000)); }
}
async function approve(args: string[]) { const { positionals, flags } = parse(args), token = positionals[0]; if (!token || Boolean(flags.yes) === Boolean(flags.no)) throw new AppError("invalid_decision", "approve requires a token and exactly one of --yes or --no.", 2); const origin = await originFor(flags); print(await request(new URL(`/api/approve/${encodeURIComponent(token)}`, origin), { method: "POST", headers: auth(), body: JSON.stringify({ approved: Boolean(flags.yes), comment: text(flags, "comment") ?? null }) })); }
async function cancel(args: string[]) { const { positionals, flags } = parse(args), id = positionals[0]; if (!id) throw new AppError("invalid_run", "cancel requires an id.", 2); const origin = await originFor(flags); print(await request(new URL(`/api/runs/${encodeURIComponent(id)}/cancel`, origin), { method: "POST", headers: auth(), body: JSON.stringify({ reason: text(flags, "reason") ?? null }) })); }
async function query(args: string[]) { const { flags } = parse(args), sql = text(flags, "sql"); if (!sql) throw new AppError("invalid_query", "query requires --sql.", 2); if (flags.cloud) loadTurso(); const rows = await executeReadOnly(sql); const format = text(flags, "format") ?? "json"; if (format === "json") return print(rows); if (format === "markdown") return process.stdout.write(markdown(rows)); if (format === "csv") return process.stdout.write(csv(rows)); throw new AppError("invalid_format", "Use json, markdown, or csv.", 2); }

async function check() {
  await command(join(root, "node_modules/.bin/nitro"), ["build"]);
  const files = await walk(join(root, "workflows"), (file) => file.endsWith(".ts")); const warnings: string[] = [];
  for (const file of files) {
    const source = await readFile(file, "utf8"), slug = basename(file, ".ts"), expected = slug.replace(/-([a-z0-9])/g, (_, letter) => letter.toUpperCase());
    if (!new RegExp(`export\\s+async\\s+function\\s+${expected}\\s*\\(`).test(source)) throw new AppError("invalid_export", `${relative(root, file)} must export ${expected}.`, 2);
    if (!/\binput\.parse\s*\(/.test(source)) throw new AppError("invalid_input_parse", `${relative(root, file)} must parse input.`, 2);
    const graph = parseDiagramSpec(source, workflowPath(file)); const functions = new Set([...source.matchAll(/(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(/g)].map((match) => match[1]));
    for (const node of graph.nodes) if (node.step && !functions.has(node.step)) throw new AppError("diagram_step_missing", `${node.step} in the Diagram header is not a function.`, 2);
    const paid = [...source.matchAll(/\b(provider|agent|agentStage|withSpend)\s*\(\s*\{[\s\S]{0,500}?\bstep\s*:\s*["']([^"']+)/g)].map((match) => match[2]);
    for (const step of paid) { const node = graph.nodes.find((item) => item.step === step); if (!node) warnings.push(`Paid step ${step} has no Diagram node.`); else if (node.unitCostUsd === undefined) throw new AppError("diagram_cost_missing", `${step} needs [cost: $X/row] in the Diagram header.`, 2); }
    if (graph.workflow.schedule) { const vercel = JSON.parse(await readFile(join(root, "vercel.json"), "utf8").catch(() => "{}")); if (!(vercel.crons ?? []).some((cron: any) => cron.schedule === graph.workflow.schedule)) throw new AppError("schedule_missing", `Add ${graph.workflow.schedule} to vercel.json crons.`, 2); }
  }
  const pending = await pendingMigrations();
  for (const file of pending.files) { const sql = await readFile(file, "utf8"); if (/\b(?:DROP\s+TABLE|DROP\s+COLUMN|DELETE|TRUNCATE|RENAME)\b/i.test(sql)) warnings.push(`removes_data: ${relative(root, file)}`); }
  if ((process.env.TURSO_DATABASE_URL ?? "file:").startsWith("file:") && process.env.GTM_SANDBOX !== "1") await ensureMigrated();
  return { ok: true, workflows: files.length, warnings, pendingMigrations: pending.files.map((file) => relative(root, file)), pendingSource: pending.source };
}

async function verify(args: string[]) {
  const { positionals, flags } = parse(args), slug = positionals[0], inputFile = text(flags, "input"); if (!slug || !inputFile) throw new AppError("invalid_input", "verify requires <workflow> --input <file>.", 2);
  const checked = await check(), dry = await dryPlan(slug, inputFile); await mkdir(join(root, "data"), { recursive: true }); await writeFile(join(root, "data/draft-diagram.json"), JSON.stringify(dry.graph, null, 2));
  let missing: string[] = [];
  const origin = text(flags, "url"); if (origin) { const names = await environmentNames(dry.file, dry.source); const result = await request(new URL(`/api/deployment?names=${encodeURIComponent(names.join(","))}`, origin), { headers: auth() }); missing = result.missing ?? []; }
  print({ ok: dry.plan.withinCaps, check: checked, dryRun: dry.plan, missing, diagram: "data/draft-diagram.json" }); if (!dry.plan.withinCaps) process.exitCode = 2;
}

async function diagram(args: string[]) {
  const { positionals, flags } = parse(args), slug = positionals[0]; if (!slug) throw new AppError("invalid_workflow", "diagram requires a workflow.", 2);
  const file = await workflowFile(slug), graph = parseDiagramSpec(await readFile(file, "utf8"), workflowPath(file)), run = text(flags, "run"); if (run) await overlayRun(graph, run);
  const format = text(flags, "format") ?? "json"; if (format === "json") return print(graph);
  if (format === "web") { const origin = await originFor(flags); return print(await request(new URL(`/api/links/${workflowPath(file)}${run ? `?run=${encodeURIComponent(run)}` : ""}`, origin), { headers: auth() })); }
  const svg = renderSvg(layoutGraph(graph)), directory = join(root, "data/diagrams"); await mkdir(directory, { recursive: true }); const target = join(directory, `${slug}.${format}`);
  if (format === "svg") await writeFile(target, svg); else if (format === "png") await writeFile(target, renderPng(svg, await readFile(join(root, "assets/fonts/Inter-Regular.ttf")))); else throw new AppError("invalid_format", "Use json, svg, png, or web.", 2); print({ path: relative(root, target) });
}

async function upgrade(args: string[]) {
  const { positionals, flags } = parse(args), ref = positionals[0] ?? "main"; const temporary = await mkdtemp(join(root, ".gtm-upgrade-"));
  await command("curl", ["-fsSL", `https://github.com/eliasstravik/gtm-skills/archive/${ref}.tar.gz`, "-o", join(temporary, "skills.tgz")]); await command("tar", ["-xzf", join(temporary, "skills.tgz"), "-C", temporary]);
  const sourceRoot = (await walk(temporary, (path) => path.endsWith("/skills/gtm-workflow/templates/package.json")))[0]?.replace(/\/package\.json$/, ""); if (!sourceRoot) throw new AppError("upgrade_failed", "The release does not contain the workflow template.");
  if (!flags.yes) return print({ ref, replaces: ["lib", "server", "scripts", "nitro.config.ts", "drizzle.config.ts"], preserves: ["workflows", "db/tables", "providers", "drizzle", "data", ".env"] });
  for (const path of ["lib", "server", "scripts", "nitro.config.ts", "drizzle.config.ts"]) await cp(join(sourceRoot, path), join(root, path), { recursive: true, force: true });
  const current = JSON.parse(await readFile(join(root, "package.json"), "utf8")), next = JSON.parse(await readFile(join(sourceRoot, "package.json"), "utf8")); current.dependencies = { ...current.dependencies, ...next.dependencies }; current.devDependencies = { ...current.devDependencies, ...next.devDependencies }; current.gtm = { ...(current.gtm ?? {}), skillsRelease: ref }; await writeFile(join(root, "package.json"), `${JSON.stringify(current, null, 2)}\n`); process.stdout.write("Run npm ci.\n");
}

async function originFor(flags: Flags) {
  const explicit = text(flags, "url") ?? process.env.GTM_BASE_URL;
  if (explicit) { if (isLoopback(explicit)) await ensureRunSecret(root); return explicit; }
  if (process.env.GTM_SANDBOX === "1") throw new AppError("hosted_url_required", "The hosted agent needs the workflow project URL.", 2);
  const pkg = JSON.parse(await readFile(join(root, "package.json"), "utf8")); if (pkg.gtm?.vercel?.url) return pkg.gtm.vercel.url;
  return startLocal();
}
function isLoopback(origin: string) { try { const host = new URL(origin).hostname; return host === "127.0.0.1" || host === "localhost" || host === "::1"; } catch { return false; } }
async function startLocal() { await ensureRunSecret(root); const stateFile = join(root, ".gtm-local.json"); try { const state = JSON.parse(await readFile(stateFile, "utf8")); if (await alive(state.url)) return state.url; } catch {} const port = await freePort(); const child = spawn("npm", ["run", "dev", "--", "--port", String(port), "--host", "127.0.0.1"], { cwd: root, env: childEnv(), detached: true, stdio: "ignore" }); child.unref(); const url = `http://127.0.0.1:${port}`; await writeFile(stateFile, JSON.stringify({ url, pid: child.pid })); for (let i = 0; i < 60 && !(await alive(url)); i++) await new Promise((resolve) => setTimeout(resolve, 500)); if (!(await alive(url))) throw new AppError("server_failed", "The local server did not start."); process.stdout.write("Started the local server.\n"); return url; }
async function waitLive(origin: string) { const expected = await gitHead(), deadline = Date.now() + 480_000; while (Date.now() < deadline) { try { const result = await request(new URL("/api/deployment", origin), { headers: auth() }); if (String(result.migration).startsWith("failed")) throw new AppError("migration_failed", "Saved, but the new table could not be created. Ask whoever set this up to check the database."); if (result.head === expected && result.migration === "ok") return; } catch (error) { if (error instanceof AppError && error.code === "migration_failed") throw error; } await new Promise((resolve) => setTimeout(resolve, 3000)); } throw new AppError("deployment_timeout", "Saved, but the hosted copy did not come live in 8 minutes. Ask whoever set this up to check the Vercel build."); }
async function alive(origin: string) { try { const response = await fetch(new URL("/api/deployment", origin), { headers: auth(), signal: AbortSignal.timeout(1000) }); return response.status !== 404; } catch { return false; } }
function freePort() { return new Promise<number>((resolvePort, reject) => { const server = createServer(); server.once("error", reject); server.listen(0, "127.0.0.1", () => { const address = server.address(); const port = typeof address === "object" && address ? address.port : 3000; server.close(() => resolvePort(port)); }); }); }
function auth() { return { authorization: `Bearer ${process.env.GTM_SANDBOX === "1" ? "gtm-sandbox" : process.env.GTM_RUN_SECRET ?? ""}` }; }
async function request(url: URL, init: RequestInit = {}) { const response = await fetch(url, { ...init, signal: init.signal ?? AbortSignal.timeout(600_000), headers: { "content-type": "application/json", ...(init.headers ?? {}) } }); const body = await response.json().catch(() => ({})) as any; if (!response.ok) { if (response.status === 409 && body.error?.code === "deployment_not_ready") throw new AppError("deployment_not_ready", "Someone saved a newer version. Say run again to use it."); throw new AppError(body.error?.code ?? `http_${response.status}`, body.error?.message ?? `Request failed with ${response.status}.`); } return body; }
async function command(bin: string, args: string[]) { await new Promise<void>((resolveCommand, reject) => { const child = spawn(bin, args, { cwd: root, stdio: "inherit", env: process.env }); child.on("error", reject); child.on("close", (code) => code === 0 ? resolveCommand() : reject(new AppError("command_failed", `${basename(bin)} exited ${code}.`, 2))); }); }
async function gitHead() { return (await capture("git", ["rev-parse", "HEAD"])).trim(); }
async function capture(bin: string, args: string[]) { return new Promise<string>((resolveCapture, reject) => { const child = spawn(bin, args, { cwd: root, stdio: ["ignore", "pipe", "pipe"] }); let output = "", error = ""; child.stdout.on("data", (data) => output += data); child.stderr.on("data", (data) => error += data); child.on("close", (code) => code === 0 ? resolveCapture(output) : reject(new AppError("command_failed", error.trim()))); }); }
/** Migrations the card must mention: files not on origin/main, or, without a remote, files the local ledger has not applied. */
async function pendingMigrations(): Promise<{ files: string[]; source: "origin/main" | "ledger" }> {
  try { const output = await capture("git", ["diff", "--name-only", "origin/main", "--", "drizzle"]); return { files: output.split("\n").filter((name) => name.endsWith(".sql")).map((name) => join(root, name)), source: "origin/main" }; } catch {}
  const files = await walk(join(root, "drizzle"), (file) => file.endsWith(".sql"));
  const hashed = await Promise.all(files.map(async (file) => ({ file, hash: createHash("sha256").update(await readFile(file, "utf8")).digest("hex") })));
  return { files: pendingFrom(hashed, await readAppliedMigrationHashes()), source: "ledger" };
}
async function environmentNames(workflow: string, source: string) { const providers = await walk(join(root, "providers"), (file) => file.endsWith(".ts")); const corpus = [source, await readFile(join(root, "lib/provider.ts"), "utf8"), ...await Promise.all(providers.map((file) => readFile(file, "utf8")))].join("\n"); return [...new Set([...corpus.matchAll(/(?:process\.env(?:\.|\[["'])|\benv\.)([A-Z][A-Z0-9_]*)/g)].map((match) => match[1]))].sort(); }
function loadTurso() { const file = join(root, ".env.turso"); if (!existsSync(file)) throw new AppError("cloud_env_missing", "Add .env.turso first."); }
function markdown(rows: Record<string, unknown>[]) { if (!rows.length) return "No rows.\n"; const keys = Object.keys(rows[0]); return `| ${keys.join(" | ")} |\n| ${keys.map(() => "---").join(" | ")} |\n${rows.map((row) => `| ${keys.map((key) => String(row[key] ?? "")).join(" | ")} |`).join("\n")}\n`; }
function csv(rows: Record<string, unknown>[]) { if (!rows.length) return ""; const keys = Object.keys(rows[0]), cell = (value: unknown) => `"${String(value ?? "").replaceAll('"', '""')}"`; return `${keys.map(cell).join(",")}\n${rows.map((row) => keys.map((key) => cell(row[key])).join(",")).join("\n")}\n`; }
