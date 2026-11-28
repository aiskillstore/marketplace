#!/usr/bin/env node
/**
 * validate_skill.mjs
 * Zero-dependency repository, manifest, relative-link, and media-asset validator
 * for livestream-style-video.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function fail(message) {
  console.error(`VALIDATION FAILED: ${message}`);
  process.exit(1);
}

function readUtf8(relPath) {
  const full = path.join(ROOT, relPath);
  if (!fs.existsSync(full)) {
    fail(`Missing required file: ${relPath}`);
  }
  return fs.readFileSync(full, "utf8");
}

function assertBinaryFile(relPath, minBytes = 1000) {
  const full = path.join(ROOT, relPath);
  if (!fs.existsSync(full)) {
    fail(`Missing required binary asset: ${relPath}`);
  }
  const sz = fs.statSync(full).size;
  if (sz < minBytes) {
    fail(`Binary asset too small (${sz}B < ${minBytes}B): ${relPath}`);
  }
}

const textFiles = [
  "SKILL.md",
  "README.md",
  "README.zh-CN.md",
  "docs/i18n/README.zh-TW.md",
  "docs/i18n/README.ja.md",
  "docs/i18n/README.ko.md",
  "docs/i18n/README.es.md",
  "docs/i18n/README.fr.md",
  "docs/i18n/README.de.md",
  "docs/i18n/README.pt-BR.md",
  "docs/i18n/README.ru.md",
  "LICENSE",
  "CHANGELOG.md",
  "package.json",
  "agents/openai.yaml",
  ".claude-plugin/plugin.json",
  ".claude-plugin/marketplace.json",
  ".cursor-plugin/plugin.json",
  "assets/icon.svg",
  "assets/library/catalog.json",
  "docs/pipeline.svg",
  "docs/pipeline.en.svg",
  "docs/pipeline.zh.svg",
  "docs/pipeline.zh-TW.svg",
  "references/camera-rigs-and-optics.md",
  "references/style-adapters-matrix.md",
  "references/plot-to-livestream-beats.md",
  "references/platform-ui-rea-ledger.md",
  "references/model-prompt-playbook.md",
  "references/rescue-and-anti-drift.md",
  "references/viral-livestream-archetypes.md",
  "templates/rig_and_streamer_card_template.md",
  "templates/storyboard_template.md",
  "templates/shot_prompt_template.md",
  "templates/custom_livestream_spec.json",
  "scripts/rig_spec.mjs",
  "scripts/hud_presets.mjs",
  "scripts/shot_compiler.mjs",
  "scripts/drift_check.mjs",
  "scripts/render_preview.mjs",
  "scripts/compose_hud.py",
  "scripts/validate_skill.mjs",
  "studio/index.html",
  "studio/live_hud_studio.js"
];

const binaryFiles = [
  "assets/showcase/livestream_pov_reel.gif",
  "assets/showcase/livestream_pov_reel.mp4",
  "assets/showcase/platform_hud_atlas.zh.png",
  "assets/showcase/platform_hud_atlas.en.png",
  "assets/showcase/platform_hud_atlas.png",
  "assets/showcase/camera_rigs_atlas.zh.png",
  "assets/showcase/camera_rigs_atlas.en.png",
  "assets/showcase/camera_rigs_atlas.png",
  "assets/showcase/clean_vs_hud_drift_comparison.zh.png",
  "assets/showcase/clean_vs_hud_drift_comparison.en.png",
  "assets/showcase/clean_vs_hud_drift_comparison.png",
  "assets/showcase/rig_setup_sheet.zh.png",
  "assets/showcase/rig_setup_sheet.en.png",
  "assets/showcase/rig_setup_sheet.png",
  "assets/showcase/interactive_hud_studio.png"
];

const examples = [
  ["irl-night-market-selfie", "irl_night_market_selfie"],
  ["desk-unboxing-autofocus", "desk_unboxing_autofocus"],
  ["midnight-corridor-fpv-live", "midnight_corridor_fpv_live"],
  ["late-night-study-webcam", "late_night_study_webcam"],
  ["wuxia-sword-flight-live", "wuxia_sword_flight_live"],
  ["roblox-obby-rage-pip", "roblox_obby_rage_pip"],
  ["roblox-doors-irl-selfie", "roblox_doors_irl_selfie"],
  ["roblox-pet-hatch-pk", "roblox_pet_hatch_pk"]
];

for (const [dirName, slug] of examples) {
  textFiles.push(
    `examples/${dirName}/README.md`,
    `examples/${dirName}/rig_card.md`,
    `examples/${dirName}/storyboard.md`,
    `examples/${dirName}/prompts.json`,
    `examples/${dirName}/drift_report.md`
  );
  binaryFiles.push(
    `examples/${dirName}/assets/storyboard_sheet.zh.png`,
    `examples/${dirName}/assets/storyboard_sheet.en.png`,
    `examples/${dirName}/assets/storyboard_sheet.png`,
    `examples/${dirName}/assets/${slug}.gif`,
    `examples/${dirName}/assets/${slug}.mp4`,
    `examples/${dirName}/assets/shot_01.png`,
    `examples/${dirName}/assets/shot_02.png`,
    `examples/${dirName}/assets/shot_03.png`,
    `examples/${dirName}/assets/shot_04.png`
  );
}

for (const rel of textFiles) readUtf8(rel);
for (const rel of binaryFiles) assertBinaryFile(rel);

// Validate SKILL.md frontmatter & semver sync
const skillText = readUtf8("SKILL.md");
const fmMatch = skillText.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
if (!fmMatch) fail("SKILL.md must begin with YAML frontmatter");
const fm = fmMatch[1];
if (!/^name:\s*livestream-style-video\s*$/m.test(fm)) {
  fail("SKILL.md YAML frontmatter must declare name: livestream-style-video");
}
const verMatch = fm.match(/^\s+version:\s*["']?([0-9]+\.[0-9]+\.[0-9]+)["']?\s*$/m);
if (!verMatch) fail("SKILL.md metadata.version must be a three-part semver string");
const skillVersion = verMatch[1];

const pkg = JSON.parse(readUtf8("package.json"));
const claudePlugin = JSON.parse(readUtf8(".claude-plugin/plugin.json"));
const cursorPlugin = JSON.parse(readUtf8(".cursor-plugin/plugin.json"));
const marketplace = JSON.parse(readUtf8(".claude-plugin/marketplace.json"));
const changelog = readUtf8("CHANGELOG.md");

const changelogMatch = changelog.match(/^## ([0-9]+\.[0-9]+\.[0-9]+)\s*$/m);
if (!changelogMatch) fail("CHANGELOG.md must include a ## x.y.z version heading");

const versions = new Set([
  skillVersion,
  pkg.version,
  claudePlugin.version,
  cursorPlugin.version,
  changelogMatch[1]
]);
if (versions.size !== 1) {
  fail(`Version mismatch across manifests: ${Array.from(versions).join(", ")}`);
}

const canonicalDesc =
  "Agent Skill to map any visual style or storyline into authentic 9:16 livestream camera perspectives, clean-plate I2V/T2V prompts, detachable HUDs, and local MP4 previews.";
for (const [label, desc] of [
  ["package.json", pkg.description],
  [".claude-plugin/plugin.json", claudePlugin.description],
  [".cursor-plugin/plugin.json", cursorPlugin.description],
  [".claude-plugin/marketplace.json", marketplace.plugins?.[0]?.description]
]) {
  if (desc !== canonicalDesc) {
    fail(`Description mismatch in ${label}: ${desc}`);
  }
}

// Validate relative links & UTF-8 cleanliness across all Markdown docs
const docFilesToCheckLinks = [
  "SKILL.md",
  "README.md",
  "README.zh-CN.md",
  "docs/i18n/README.zh-TW.md",
  "docs/i18n/README.ja.md",
  "docs/i18n/README.ko.md",
  "docs/i18n/README.es.md",
  "docs/i18n/README.fr.md",
  "docs/i18n/README.de.md",
  "docs/i18n/README.pt-BR.md",
  "docs/i18n/README.ru.md"
];

for (const docRel of docFilesToCheckLinks) {
  const txt = readUtf8(docRel);
  if (/\?\?\?|\uFFFD/.test(txt)) {
    fail(`Encoding corruption detected in ${docRel}`);
  }
  if (docRel !== "SKILL.md" && txt.split(/\r?\n/).length < 95) {
    fail(`Incomplete README detected in ${docRel} (must be >= 95 lines)`);
  }
  const baseDir = path.dirname(path.join(ROOT, docRel));
  const mdLinks = [...txt.matchAll(/\]\(([^)#\s]+)(?:#[^)]*)?\)/g)].map((m) => m[1]);
  const htmlLinks = [...txt.matchAll(/(?:src|href)="([^"#\s]+)(?:#[^"]*)?"/g)].map((m) => m[1]);
  for (const target of [...mdLinks, ...htmlLinks]) {
    if (/^(?:https?:|mailto:|data:)/i.test(target)) continue;
    const resolved = path.resolve(baseDir, target);
    if (!fs.existsSync(resolved)) {
      fail(`Broken relative link in ${docRel}: '${target}' -> ${resolved}`);
    }
  }
}

const skillWords = skillText.split(/\s+/).filter(Boolean).length;
if (skillWords > 5500) {
  fail(`Keep SKILL.md at 5,500 words or fewer; found ${skillWords}`);
}

const totalChecked = textFiles.length + binaryFiles.length;
console.log(
  `livestream-style-video v${skillVersion} package is valid (${totalChecked} files & all relative links verified, ${skillWords} words in SKILL.md)`
);
