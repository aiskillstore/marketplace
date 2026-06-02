#!/usr/bin/env node
/**
 * Install pitchcraft SKILL.md into agent skill directories.
 * Runs on postinstall (project/global npm install) or via: npx pitchcraft [options]
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILL_DIR = "pitchcraft";
const PKG_ROOT = path.join(__dirname, "..");

const AGENTS = {
  "claude-code": {
    project: [".claude", "skills"],
    global: [".claude", "skills"],
  },
  cursor: {
    project: [".cursor", "skills"],
    global: [".cursor", "skills"],
  },
  codex: {
    project: [".codex", "skills"],
    global: [".codex", "skills"],
  },
};

function parseArgs(argv) {
  const agents = [];
  let global = false;
  let lang = "en";
  let skip = false;

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-g" || a === "--global") global = true;
    else if (a === "-a" || a === "--agent") agents.push(argv[++i]);
    else if (a === "--lang" && argv[i + 1]) lang = argv[++i];
    else if (a === "--skip-install" || a === "skip") skip = true;
    else if (a === "install") {
      /* explicit subcommand */
    }
  }

  if (agents.length === 0) agents.push("claude-code");
  return { agents, global, lang, skip };
}

function isGlobalNpmInstall() {
  const prefix = process.env.npm_config_prefix || "";
  const globalPrefix = path.join(
    os.homedir(),
    process.platform === "win32" ? "AppData/Roaming/npm" : ".npm-global"
  );
  return (
    process.env.npm_config_global === "true" ||
    (prefix && !prefix.includes("node_modules"))
  );
}

function resolveProjectRoot() {
  return process.env.INIT_CWD || process.cwd();
}

function skillSource(lang) {
  const zh = path.join(
    PKG_ROOT,
    ".claude",
    "skills",
    "pitchcraft",
    "SKILL.zh-CN.md"
  );
  const en = path.join(PKG_ROOT, "SKILL.md");
  if (lang === "zh" || lang === "zh-CN") {
    if (!fs.existsSync(zh)) throw new Error("SKILL.zh-CN.md not found in package");
    return zh;
  }
  if (!fs.existsSync(en)) throw new Error("SKILL.md not found in package");
  return en;
}

function copySkill(targetDir, lang) {
  fs.mkdirSync(targetDir, { recursive: true });
  const dest = path.join(targetDir, "SKILL.md");
  fs.copyFileSync(skillSource(lang), dest);
  return dest;
}

function installAgent(agent, scope, lang) {
  const cfg = AGENTS[agent];
  if (!cfg) {
    console.warn(`[pitchcraft] Unknown agent "${agent}", skipped.`);
    return null;
  }
  const segments = scope === "global" ? cfg.global : cfg.project;
  const base =
    scope === "global"
      ? path.join(os.homedir(), ...segments)
      : path.join(resolveProjectRoot(), ...segments);
  const target = path.join(base, SKILL_DIR);
  const dest = copySkill(target, lang);
  return dest;
}

function main() {
  const { agents, global: globalFlag, lang, skip } = parseArgs(
    process.argv.slice(2)
  );

  if (skip || process.env.PITCHCRAFT_SKIP_INSTALL === "1") {
    return;
  }

  const scope = globalFlag || isGlobalNpmInstall() ? "global" : "project";
  const installed = [];

  for (const agent of agents) {
    try {
      const dest = installAgent(agent, scope, lang);
      if (dest) installed.push({ agent, dest });
    } catch (err) {
      console.error(`[pitchcraft] Failed for ${agent}:`, err.message);
      process.exitCode = 1;
    }
  }

  if (installed.length === 0) return;

  console.log(`[pitchcraft] Installed (${scope}, lang=${lang}):`);
  for (const { agent, dest } of installed) {
    console.log(`  ${agent} → ${dest}`);
  }
  console.log(
    "[pitchcraft] Chinese: npx pitchcraft --lang zh-CN  |  Skip postinstall: PITCHCRAFT_SKIP_INSTALL=1"
  );
}

main();
