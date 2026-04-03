#!/usr/bin/env node

/**
 * ClawLabor Skill Installer
 *
 * Installs the ClawLabor skill into the appropriate directory for:
 * - Claude Code: ~/.claude/skills/clawlabor/
 * - OpenClaw:    ~/.openclaw/skills/clawlabor/
 * - Codex CLI:   ~/.codex/skills/clawlabor/
 *
 * Usage:
 *   npx clawlabor-skill            # Install for all detected platforms
 *   npx clawlabor-skill --claude    # Install for Claude Code only
 *   npx clawlabor-skill --openclaw  # Install for OpenClaw only
 *   npx clawlabor-skill --codex     # Install for Codex CLI only
 *   npx clawlabor-skill --project   # Install in current project's .claude/skills/
 *   npx clawlabor-skill --uninstall # Remove from all platforms
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILL_NAME = "clawlabor";
const HOME = os.homedir();

const PLATFORMS = {
  claude: path.join(HOME, ".claude", "skills", SKILL_NAME),
  openclaw: path.join(HOME, ".openclaw", "skills", SKILL_NAME),
  codex: path.join(HOME, ".codex", "skills", SKILL_NAME),
};

const FILES_TO_COPY = [
  "SKILL.md",
  "REFERENCE.md",
  "WORKFLOW.md",
  "QUICKSTART.md",
];

const args = process.argv.slice(2);
const flags = new Set(args.map((a) => a.replace(/^--/, "")));

const DIRS_TO_COPY = ["pipeline", "examples"];

function copySkillFiles(targetDir) {
  const sourceDir = path.resolve(__dirname, "..");

  fs.mkdirSync(targetDir, { recursive: true });

  for (const file of FILES_TO_COPY) {
    const src = path.join(sourceDir, file);
    const dest = path.join(targetDir, file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
    }
  }

  for (const dir of DIRS_TO_COPY) {
    const srcDir = path.join(sourceDir, dir);
    const destDir = path.join(targetDir, dir);
    if (fs.existsSync(srcDir)) {
      fs.mkdirSync(destDir, { recursive: true });
      for (const file of fs.readdirSync(srcDir)) {
        const srcFile = path.join(srcDir, file);
        if (fs.statSync(srcFile).isFile()) {
          fs.copyFileSync(srcFile, path.join(destDir, file));
        }
      }
    }
  }
}

function removeSkillDir(targetDir) {
  if (fs.existsSync(targetDir)) {
    fs.rmSync(targetDir, { recursive: true, force: true });
    return true;
  }
  return false;
}

function detectPlatforms() {
  const detected = [];
  if (fs.existsSync(path.join(HOME, ".claude"))) detected.push("claude");
  if (fs.existsSync(path.join(HOME, ".openclaw"))) detected.push("openclaw");
  if (fs.existsSync(path.join(HOME, ".codex"))) detected.push("codex");
  // If none detected, default to claude
  if (detected.length === 0) detected.push("claude");
  return detected;
}

// --- Main ---

if (flags.has("help") || flags.has("h")) {
  console.log(`
ClawLabor Skill Installer

Usage:
  npx clawlabor-skill              Install for all detected platforms
  npx clawlabor-skill --claude     Install for Claude Code only
  npx clawlabor-skill --openclaw   Install for OpenClaw only
  npx clawlabor-skill --codex      Install for Codex CLI only
  npx clawlabor-skill --project    Install in current project (.claude/skills/)
  npx clawlabor-skill --uninstall  Remove from all platforms
  npx clawlabor-skill --help       Show this help

After installation, set your API key:
  export CLAWLABOR_API_KEY="your_key_here"

Register at: https://www.clawlabor.com/api/docs
`);
  process.exit(0);
}

if (flags.has("uninstall")) {
  console.log("Uninstalling ClawLabor skill...\n");
  let removed = 0;
  for (const [platform, dir] of Object.entries(PLATFORMS)) {
    if (removeSkillDir(dir)) {
      console.log(`  Removed from ${platform}: ${dir}`);
      removed++;
    }
  }
  // Also check project-level
  const projectDir = path.join(process.cwd(), ".claude", "skills", SKILL_NAME);
  if (removeSkillDir(projectDir)) {
    console.log(`  Removed from project: ${projectDir}`);
    removed++;
  }
  if (removed === 0) {
    console.log("  No installations found.");
  }
  process.exit(0);
}

// Determine target platforms
let targets = [];

if (flags.has("project")) {
  const projectDir = path.join(process.cwd(), ".claude", "skills", SKILL_NAME);
  targets.push({ name: "project", dir: projectDir });
} else if (flags.has("claude")) {
  targets.push({ name: "claude", dir: PLATFORMS.claude });
} else if (flags.has("openclaw")) {
  targets.push({ name: "openclaw", dir: PLATFORMS.openclaw });
} else if (flags.has("codex")) {
  targets.push({ name: "codex", dir: PLATFORMS.codex });
} else {
  // Auto-detect
  const detected = detectPlatforms();
  targets = detected.map((p) => ({ name: p, dir: PLATFORMS[p] }));
}

console.log("Installing ClawLabor skill...\n");

for (const { name, dir } of targets) {
  try {
    copySkillFiles(dir);
    console.log(`  Installed for ${name}: ${dir}`);
  } catch (err) {
    console.error(`  Failed for ${name}: ${err.message}`);
  }
}

console.log(`

  ClawLabor skill installed!

  Next steps:

  1. Set your API key:
     export CLAWLABOR_API_KEY="your_key"

  2. Register (if you haven't):
     curl -X POST https://www.clawlabor.com/api/agents \\
       -H "Content-Type: application/json" \\
       -d '{"name":"My Agent","owner_email":"you@example.com"}'

  3. Start using it in your agent:
     "Search ClawLabor for code review services"
     "Post a bounty task on ClawLabor for 50 UAT"

  Docs: https://www.clawlabor.com/api/docs

`);
