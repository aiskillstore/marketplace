import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import {
  RIG_PROFILES,
  STYLE_ADAPTERS,
  buildRigSpec,
  formatRigSpecMarkdown,
  normalizeLang
} from "../scripts/rig_spec.mjs";
import {
  PLATFORM_HUD_PRESETS,
  resolvePlatformPreset,
  buildShotHudTimeline
} from "../scripts/hud_presets.mjs";
import {
  TEMPLATES,
  compileStoryboard,
  formatStoryboardMarkdown,
  inferLivestreamConfigFromPlot
} from "../scripts/shot_compiler.mjs";
import {
  inspectPrompt,
  inspectPackageFile,
  formatDriftCheckMarkdown
} from "../scripts/drift_check.mjs";
import {
  computeEpisodeTimingPlan,
  buildEpisodeWavBuffer,
  encodePNG
} from "../scripts/render_preview.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

test("rig_spec combines all 8 livestream camera rigs with all 6 orthogonal style packs", () => {
  assert.equal(Object.keys(RIG_PROFILES).length, 8);
  assert.equal(Object.keys(STYLE_ADAPTERS).length, 6);

  const irlSelfie = buildRigSpec({
    rig: "handheld-selfie-irl",
    style: "realistic-irl",
    host: "Lin"
  });
  assert.equal(irlSelfie.rigId, "handheld-selfie-irl");
  assert.match(irlSelfie.setupAnchorPromptEn, /18mm–20mm ultra-wide/);
  assert.match(irlSelfie.setupAnchorPromptEn, /five-finger hand anatomy/);

  const robloxPip = buildRigSpec({
    rig: "pip-facecam-rig",
    style: "roblox-blocky",
    robloxRig: "r6",
    host: "BloxyKai"
  });
  assert.match(robloxPip.setupAnchorPromptEn, /2x2x1 chamfered rectangular torso/);
  assert.match(robloxPip.setupAnchorPromptEn, /fingerless and clawless solid 1x2x1/);
  assert.match(robloxPip.dualTrackNoteEn, /TWO separate clean plates/);
  assert.match(robloxPip.negativePromptEn, /Lego C-shaped claw/);
});

test("hud_presets exposes 6 platform chrome definitions with REA-calibrated safe zones and Periscope 6-color hearts", () => {
  for (const id of ["douyin", "kuaishou", "instagram", "x", "tiktok", "clean"]) {
    assert.ok(PLATFORM_HUD_PRESETS[id], `missing HUD preset ${id}`);
  }
  assert.equal(resolvePlatformPreset("ins").id, "instagram");
  assert.equal(resolvePlatformPreset("periscope").id, "x");
  assert.equal(PLATFORM_HUD_PRESETS.kuaishou.safeZone1080x1920.topAvoidPx, 340);
  assert.equal(PLATFORM_HUD_PRESETS.kuaishou.safeZone1080x1920.bottomAvoidPx, 620);
  assert.equal(PLATFORM_HUD_PRESETS.x.heartPalette.length, 6);

  const tl = buildShotHudTimeline({}, 2, 4, "douyin");
  assert.equal(tl.enabled, true);
  assert.equal(tl.activePopup, "gift_combo");
});

test("shot_compiler handles built-in templates, custom specs, 15s/30s/45s non-repeating beats, and arbitrary freeform plots", () => {
  // 1. 15s built-in template
  const irlPlan = compileStoryboard({
    template: "irl-night-market-selfie",
    duration: 15,
    engine: "kling"
  });
  assert.equal(irlPlan.shotCount, 4);
  assert.equal(irlPlan.platform, "douyin");
  assert.match(irlPlan.shots[0].i2vPromptZh, /可灵I2V纯净直播底片/);

  // 2. 30s Roblox PiP with Hailuo bracketed camera syntax & 8 unique shots
  const roblox30 = compileStoryboard({
    template: "roblox-obby-rage-pip",
    duration: 30,
    engine: "hailuo"
  });
  assert.equal(roblox30.shotCount, 8);
  assert.equal(new Set(roblox30.shots.map((s) => s.actionEn)).size, 8);
  assert.match(roblox30.shots[0].i2vPromptEn, /^\[Push in\]/);
  assert.ok(roblox30.shots[0].trackBFacecamPromptEn);

  // 3. Freeform cross-genre plot auto-inference & compilation
  const wuxiaInf = inferLivestreamConfigFromPlot("古代剑修在暴雨云海御剑飞行直播被仙鹤追尾");
  assert.equal(wuxiaInf.style, "cinematic-genre-adapt");
  assert.equal(wuxiaInf.rig, "handheld-selfie-irl");

  const customFree = compileStoryboard({
    plot: "Medieval knight unboxing an enchanted shield inside a dark dungeon when a mimic chest sneezes",
    platform: "instagram",
    engine: "veo"
  });
  assert.equal(customFree.shotCount, 4);
  assert.equal(customFree.platform, "instagram");
  assert.match(customFree.shots[0].i2vPromptEn, /Live Audio:/);

  // 4. Custom JSON spec file
  const specPlan = compileStoryboard({
    spec: path.join(ROOT, "templates", "custom_livestream_spec.json"),
    engine: "seedance"
  });
  assert.equal(specPlan.slug, "cyber_ramen_stall_live");
  assert.equal(specPlan.shotCount, 4);
});

test("drift_check catches cinema drift, burned-in gibberish UI, passive 4th wall, T2V PiP melt, Roblox fingers, overload, and watermarks", () => {
  // 1. Cinema crane + burned-in TikTok comments + official logo -> FAIL
  const badUiCinema = inspectPrompt({
    prompt:
      "Sweeping Hollywood crane shot with 2.39:1 letterbox bars of a girl ignoring the camera at a market with scrolling TikTok comments, gift animation banner, and official TikTok logo watermark.",
    engine: "kling",
    mode: "t2v"
  });
  assert.equal(badUiCinema.overallStatus, "FAIL");
  assert.equal(badUiCinema.checks[0].status, "FAIL");
  assert.equal(badUiCinema.checks[1].status, "FAIL");
  assert.equal(badUiCinema.checks[2].status, "FAIL");
  assert.equal(badUiCinema.checks[7].status, "FAIL");

  // 2. Single-pass raw T2V corner facecam + Roblox five fingers + Chinese overload -> FAIL
  const badRobloxPip = inspectPrompt({
    prompt:
      "Roblox R6主播用五根手指抓着鼠标在右上角画中画小窗里先跳上平台，然后打开宝箱，接着挥剑砍向怪物，最后跳起庆祝。",
    engine: "wan",
    mode: "t2v",
    style: "roblox-blocky"
  });
  assert.equal(badRobloxPip.overallStatus, "FAIL");
  assert.equal(badRobloxPip.checks[4].status, "FAIL");
  assert.equal(badRobloxPip.checks[5].status, "FAIL");
  assert.equal(badRobloxPip.checks[6].status, "FAIL");

  // 3. Clean-plate prompts with protective negations ("zero burned-in UI text, zero human fingers") -> PASS!
  for (const tplKey of Object.keys(TEMPLATES)) {
    const plan = compileStoryboard({ template: tplKey, engine: "kling" });
    for (const sh of plan.shots) {
      const rep = inspectPrompt({
        prompt: sh.i2vPromptEn,
        engine: "kling",
        mode: "i2v",
        style: plan.style,
        rig: plan.rig
      });
      assert.equal(rep.overallStatus, "PASS", `Expected PASS for ${tplKey} shot ${sh.shotNumber}`);
    }
  }

  const customAudit = inspectPackageFile(path.join(ROOT, "templates", "custom_livestream_spec.json"), {
    engine: "kling"
  });
  assert.equal(customAudit.overallStatus, "PASS");
  assert.equal(customAudit.uniqueActionCount, 4);
});

test("render_preview computes exact timing, synthesizes live WAV audio, and renders custom --spec MP4/GIF", () => {
  const timing = computeEpisodeTimingPlan({
    durationSeconds: 15,
    shots: [{ durationSec: 3.5 }, { durationSec: 4.0 }, { durationSec: 4.0 }, { durationSec: 3.5 }]
  });
  assert.equal(timing.totalDurationSec, 15);
  const wav = buildEpisodeWavBuffer([{}, {}, {}, {}], timing.shotDurations);
  assert.equal(wav.length, 44 + Math.floor(22050 * 15) * 2);

  const tinyPng = encodePNG(4, 4, new Uint8Array(4 * 4 * 4).fill(200));
  assert.equal(tinyPng[0], 137);
  assert.equal(tinyPng[1], 80);

  // End-to-end CLI render smoke test on custom_livestream_spec.json into temp directory
  const tmpOut = fs.mkdtempSync(path.join(os.tmpdir(), "live-pov-test-"));
  try {
    execFileSync(
      process.execPath,
      [
        path.join(ROOT, "scripts", "render_preview.mjs"),
        "--spec",
        path.join(ROOT, "templates", "custom_livestream_spec.json"),
        "--out-dir",
        tmpOut,
        "--platform",
        "x",
        "--workers",
        "2",
        "--force"
      ],
      { cwd: ROOT, stdio: "pipe" }
    );
    assert.ok(fs.existsSync(path.join(tmpOut, "shot_01.png")));
    assert.ok(fs.existsSync(path.join(tmpOut, "cyber_ramen_stall_live.gif")));
    assert.ok(fs.existsSync(path.join(tmpOut, "cyber_ramen_stall_live.mp4")));
  } finally {
    fs.rmSync(tmpOut, { recursive: true, force: true });
  }
});

test("CLI formatters support all 10 languages plus zh-en bilingual mode", () => {
  const rigSpec = buildRigSpec({ rig: "desktop-webcam", style: "realistic-irl" });
  const plan = compileStoryboard({ template: "late-night-study-webcam", engine: "wan" });
  const drift = inspectPrompt({
    prompt: plan.shots[0].i2vPromptEn,
    engine: "wan",
    mode: "i2v"
  });

  for (const code of ["en", "zh", "zh-tw", "ja", "ko", "es", "fr", "de", "pt", "ru", "zh-en"]) {
    assert.equal(normalizeLang(code), code);
    assert.match(formatRigSpecMarkdown(rigSpec, code), new RegExp(`lang: ${code}`));
    assert.match(formatStoryboardMarkdown(plan, code), new RegExp(`lang: ${code}`));
    assert.match(formatDriftCheckMarkdown(drift, code), new RegExp(`lang: ${code}`));
  }
});

test("validate_skill verifies all required files, manifests, media assets, and relative links", () => {
  const out = execFileSync(process.execPath, [path.join(ROOT, "scripts", "validate_skill.mjs")], {
    cwd: ROOT,
    encoding: "utf8"
  });
  assert.match(out, /livestream-style-video v1\.1\.0 package is valid/);
});
