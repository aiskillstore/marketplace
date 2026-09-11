#!/usr/bin/env node
// Command classifier shared by every host. "allow" runs without a card; "ask"
// needs the user's plain-language approval. Paths must stay inside the GTM
// workspace, its scratch directory, or ~/.gtm; anything the shell would expand
// (~, $VAR, globs) is treated as unknown and asks.
import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { constants } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(import.meta.url);
const home = homedir();

const READ_ONLY = new Set(["ls", "cat", "head", "tail", "grep", "find", "wc", "pwd", "echo", "printf", "test", "[", "true", "which", "sort", "uniq", "cut", "tr", "jq"]);
const WRITERS = new Set(["mkdir", "cp", "mv", "rm", "tee"]);
const GIT_READS = new Set(["status", "diff", "log", "fetch", "rev-parse", "show", "ls-files", "branch"]);
const GTM_READS = new Set(["check", "verify", "query", "diagram", "help"]);
const PROTECTED_FILES = /^(?:\.env(?!\.example$)[^/]*|\.gitignore|\.npmrc)$/;
const PROTECTED_DIRS = new Set([".git", "node_modules"]);

export function classify(command, cwd = process.cwd()) {
  if (!command.trim()) return "ask";
  if (/\$\(|`|\beval\b|\b(?:ba)?sh\s+-c\b|\bxargs\b|^\s*[A-Za-z_][A-Za-z0-9_]*=\S+\s+/.test(command)) return "ask";
  const stripped = stripHeredoc(command);
  if (stripped === null) return "ask";
  const parts = splitChain(stripped);
  if (!parts) return "ask";
  return parts.every((part) => classifyOne(part, cwd) === "allow") ? "allow" : "ask";
}

function classifyOne(command, cwd) {
  if (/\|/.test(command.replace(/'[^']*'|"[^"]*"/g, ""))) return "ask";
  const redirections = [...command.matchAll(/(?:^|\s)(?:>>?|<)\s*([^\s;|&]+)/g)];
  if (redirections.some((match) => !safePath(match[1].replace(/^['"]|['"]$/g, ""), cwd, { write: true }))) return "ask";
  command = command.replace(/(?:^|\s)(?:>>?|<)\s*([^\s;|&]+)/g, " ");
  const argv = split(command);
  if (!argv?.length) return "ask";
  const [bin, ...args] = argv;

  if (bin === "cd") return args.length === 1 && safePath(args[0], cwd) ? "allow" : "ask";
  if (READ_ONLY.has(bin)) return operands(args).every((value) => safePath(value, cwd)) ? "allow" : "ask";
  if (bin === "sed" && args[0] === "-n") return operands(args.slice(1)).every((value) => safePath(value, cwd)) ? "allow" : "ask";
  if (bin === "node" && args[0] === "--check") return operands(args.slice(1)).every((value) => safePath(value, cwd)) ? "allow" : "ask";
  if ((bin === "node" || bin === "npm") && args[0] === "--version") return "allow";
  if (WRITERS.has(bin)) {
    const targets = operands(args);
    if (!targets.length) return "ask";
    const written = bin === "cp" || bin === "mv" ? [targets.at(-1)] : targets;
    const read = bin === "cp" || bin === "mv" ? targets.slice(0, -1) : [];
    return written.every((value) => safePath(value, cwd, { write: true })) && read.every((value) => safePath(value, cwd)) ? "allow" : "ask";
  }
  if (bin === "npm") {
    if (args[0] === "ci") return "allow";
    if (args[0] === "run" && ["db:generate", "db:studio", "db:studio:cloud"].includes(args[1])) return "allow";
    if (args[0] === "run" && args[1] === "gtm" && args[2] === "--") {
      const [cmd, ...rest] = args.slice(3);
      if (GTM_READS.has(cmd)) return "allow";
      if (cmd === "runs" && rest[0] === "get") return "allow";
      if (cmd === "run" && rest.includes("--dry-run")) return "allow";
      return "ask";
    }
    return "ask";
  }
  if (bin === "git") {
    const [sub, ...rest] = args;
    if (sub === "commit") return "allow";
    if (sub === "add") {
      if (rest.some((value) => ["-f", "--force", "-A", "--all", "."].includes(value))) return "ask";
      return operands(rest).length > 0 && operands(rest).every((value) => safePath(value, cwd)) ? "allow" : "ask";
    }
    if (sub === "branch" && rest.some((value) => ["-D", "-d", "--delete", "-M", "-m"].includes(value))) return "ask";
    if (sub === "remote") return rest.length === 1 && rest[0] === "-v" ? "allow" : "ask";
    if (GIT_READS.has(sub)) return operands(rest).every((value) => safePath(value, cwd)) ? "allow" : "ask";
    return "ask";
  }
  return "ask";
}

/** Positional arguments: everything that is not a flag, a number, or a KEY=value pair. */
function operands(args) {
  return args.filter((value) => !value.startsWith("-") && !/^\d+$/.test(value) && !/^[\w.-]+=/.test(value));
}

function stripHeredoc(command) {
  const newline = command.indexOf("\n");
  if (newline < 0) return command;
  const header = command.slice(0, newline);
  const marker = header.match(/<<-?\s*['"]?([A-Za-z_][A-Za-z0-9_]*)['"]?/);
  if (!marker) return command;
  const rest = command.slice(newline + 1);
  const end = new RegExp(`^${marker[1]}$`, "m").exec(rest);
  if (!end) return null;
  if (rest.slice(end.index + end[0].length).trim()) return null;
  return header.replace(marker[0], " ").trim();
}

function splitChain(command) {
  const result = [];
  let value = "", quote = "";
  for (let i = 0; i < command.length; i++) {
    const char = command[i];
    if (quote) { value += char; if (char === quote && command[i - 1] !== "\\") quote = ""; continue; }
    if (char === "'" || char === '"') { quote = char; value += char; continue; }
    if (char === "\n" || char === ";" || (char === "&" && command[i + 1] === "&") || (char === "|" && command[i + 1] === "|")) {
      if (value.trim()) result.push(value.trim());
      value = "";
      if (char === "&" || char === "|") i++;
      continue;
    }
    value += char;
  }
  if (quote) return null;
  if (value.trim()) result.push(value.trim());
  return result;
}

function split(command) {
  const result = [];
  let value = "", quote = "", quoted = false;
  const push = () => { if (value || quoted) result.push(value); value = ""; quoted = false; };
  for (const char of command.trim()) {
    if (quote) { if (char === quote) quote = ""; else value += char; }
    else if (char === "'" || char === '"') { quote = char; quoted = true; }
    else if (/\s/.test(char)) push();
    else value += char;
  }
  if (quote) return null;
  push();
  return result;
}

function roots(cwd) { return [resolve(cwd), resolve(home, ".gtm"), "/tmp/gtm-scratch"]; }

/**
 * A path is safe when it resolves inside one of the roots and names nothing
 * the shell would expand. Writes may not touch protected files or root directories.
 */
function safePath(value, cwd, options = {}) {
  if (!value) return true;
  if (/[~$*?{}`\\]/.test(value)) return false;
  const path = resolve(cwd, value);
  const rootHits = roots(cwd).filter((root) => { const rel = relative(root, path); return rel === "" || (!rel.startsWith("..") && !isAbsolute(rel)); });
  if (!rootHits.length) return false;
  const name = basename(path);
  if (PROTECTED_FILES.test(name)) return false;
  if (options.write) {
    if (rootHits.some((root) => relative(root, path) === "")) return false;
    if (PROTECTED_DIRS.has(name)) return false;
    if (path.split("/").some((segment) => PROTECTED_DIRS.has(segment))) return false;
  }
  return true;
}

async function installedScope(cwd) {
  const gtm = resolve(home, ".gtm");
  const path = resolve(cwd);
  if (path === gtm || path.startsWith(`${gtm}/`)) return true;
  try { await access(join(path, "ORG.md"), constants.F_OK); return true; } catch { return false; }
}

async function install() {
  const settingsPath = join(home, ".claude", "settings.json");
  await mkdir(dirname(settingsPath), { recursive: true });
  let settings = {};
  try { settings = JSON.parse(await readFile(settingsPath, "utf8")); } catch {}
  const command = `node ${JSON.stringify(script)}`;
  const hooks = settings.hooks ?? {};
  const entries = (hooks.PreToolUse ?? []).filter((entry) => !JSON.stringify(entry).includes(script));
  for (const matcher of ["Bash", "Write|Edit|MultiEdit"]) entries.push({ matcher, hooks: [{ type: "command", command }] });
  settings.hooks = { ...hooks, PreToolUse: entries };
  await writeFile(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
  process.stdout.write("Restart Claude Code to finish setup.\n");
}

async function hook() {
  const payload = JSON.parse((await readFile(0, "utf8")) || "{}");
  const cwd = payload.cwd ?? process.cwd();
  if (!(await installedScope(cwd))) return;
  const tool = payload.tool_name ?? "Bash";
  const input = payload.tool_input ?? {};
  const decision = tool === "Bash" ? classify(input.command ?? "", cwd) : safePath(input.file_path ?? "", cwd, { write: true }) ? "allow" : "ask";
  process.stdout.write(`${JSON.stringify({ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: decision, permissionDecisionReason: decision === "allow" ? "Allowed inside the GTM workspace." : "This action needs approval." } })}\n`);
}

if (process.argv[1] === script) {
  if (process.argv[2] === "--install-claude-code") await install();
  else if (process.argv[2] === "--classify") process.stdout.write(`${JSON.stringify({ decision: classify(process.argv.slice(3).join(" ")) })}\n`);
  else await hook();
}
