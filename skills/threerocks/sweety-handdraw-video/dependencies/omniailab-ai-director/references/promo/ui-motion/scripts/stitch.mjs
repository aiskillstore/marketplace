#!/usr/bin/env node
// stitch.mjs — assemble the final UI motion video.
//
// For v4 single-take storyboards: just mux the video with the BGM.
// For v4 multi-take storyboards (continuation): concat the takes first, then mux.
//
// Usage:
//   node stitch.mjs --manifest storyboard.json --out final.mp4
//   node stitch.mjs --manifest storyboard.json --out final.mp4 --vo audio/vo.mp3
//
// Exit codes:
//   0  success
//   1  ffmpeg missing
//   2  manifest malformed
//   3  ffmpeg returned non-zero

import { readFileSync, existsSync, mkdirSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
import { argv, exit } from "node:process";

function parseArgs() {
  const out = {};
  for (let i = 2; i < argv.length; i += 2) {
    const k = argv[i].replace(/^--/, "");
    out[k] = argv[i + 1];
  }
  return out;
}

function fail(msg, code = 1) {
  console.error(`stitch.mjs: ${msg}`);
  exit(code);
}

function which(cmd) {
  // Cross-platform: try `which` (unix + PowerShell 7+), fall back to `where` on Windows.
  const r1 = spawnSync("which", [cmd], { encoding: "utf8" });
  if (r1.status === 0 && r1.stdout.trim()) return r1.stdout.trim();
  if (process.platform === "win32") {
    const r2 = spawnSync("where", [cmd], { encoding: "utf8" });
    if (r2.status === 0) {
      return r2.stdout.trim().split(/\r?\n/)[0];
    }
  }
  return null;
}

function run(cmd, args, label) {
  console.log(`stitch.mjs: ${label}…`);
  const res = spawnSync(cmd, args, { stdio: ["ignore", "inherit", "inherit"] });
  if (res.status !== 0) {
    fail(`${label} failed with exit code ${res.status}`, 3);
  }
}

const args = parseArgs();
for (const k of ["manifest", "out"]) {
  if (!args[k]) fail(`missing --${k}`);
}

const manifestPath = resolve(args["manifest"]);
const outPath = resolve(args.out);
const voPath = args.vo ? resolve(args.vo) : null;

if (!existsSync(manifestPath)) fail(`manifest not found: ${manifestPath}`, 2);
let manifest;
try {
  manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
} catch (e) {
  fail(`manifest malformed JSON: ${e.message}`, 2);
}
if (manifest.version !== 4) {
  fail(`unsupported manifest version: ${manifest.version} (this script supports v4)`, 2);
}

const ffmpeg = which("ffmpeg");
if (!ffmpeg) {
  fail(
    "ffmpeg is not on PATH. Install it (https://ffmpeg.org/download.html) and retry. " +
      "Raw clips are still in your workspace and can be assembled manually.",
    1,
  );
}

const workspace = dirname(manifestPath);

// Resolve the video source(s).
// Single-take: there's no takes array, but the i2v clip is in the expected location.
// Multi-take: take clips are in workspace/clips/take-N.mp4.

const isMultiTake = Array.isArray(manifest.takes) && manifest.takes.length > 0;

let videoPath;
if (isMultiTake) {
  // Concat all take clips into one intermediate, then mux with audio.
  const takeClips = manifest.takes.map((take) => {
    const p = join(workspace, take.clip_file || `clips/take-${take.index}.mp4`);
    if (!existsSync(p)) fail(`take clip not found: ${p}`, 2);
    return p;
  });

  const concatList = join(workspace, "concat.txt");
  // Concat demuxer format: file paths in order. We re-encode to ensure consistent
  // timestamps across the joins (i2v clips may have slight timing drift).
  const concatContent = takeClips.map((p) => `file '${p}'`).join("\n") + "\n";
  const { writeFileSync } = await import("node:fs");
  writeFileSync(concatList, concatContent);

  const concatPath = join(workspace, "clips", "concat.mp4");
  mkdirSync(dirname(concatPath), { recursive: true });

  run(
    ffmpeg,
    [
      "-f", "concat", "-safe", "0", "-i", concatList,
      "-c:v", "libx264", "-preset", "medium", "-crf", "20",
      "-pix_fmt", "yuv420p",
      "-r", "30",
      concatPath,
    ],
    "concatenating takes",
  );
  videoPath = concatPath;
} else {
  // Single take — the i2v clip should be at clips/take-1.mp4.
  videoPath = join(workspace, "clips", "take-1.mp4");
  if (!existsSync(videoPath)) {
    fail(`single-take clip not found: ${videoPath}`, 2);
  }
}

const audioPath = manifest.music && manifest.music.file
  ? join(workspace, manifest.music.file)
  : null;

// Mux video with audio.
if (audioPath && existsSync(audioPath)) {
  // For multi-take, also mix in VO if present.
  if (voPath && existsSync(voPath)) {
    run(
      ffmpeg,
      [
        "-i", videoPath,
        "-i", audioPath,
        "-i", voPath,
        "-filter_complex",
        `[1:a]volume=0.25,atrim=0:${manifest.total_duration_sec}[a1];` +
          `[2:a]volume=1.0[vo];` +
          `[a1][vo]amix=inputs=2:duration=longest[aout]`,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-t", String(manifest.total_duration_sec),
        "-movflags", "+faststart",
        outPath,
      ],
      "muxing video + BGM (ducked) + VO",
    );
  } else {
    run(
      ffmpeg,
      [
        "-i", videoPath,
        "-i", audioPath,
        "-filter_complex",
        `[1:a]volume=0.25,atrim=0:${manifest.total_duration_sec}[a1]`,
        "-map", "0:v", "-map", "[a1]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-t", String(manifest.total_duration_sec),
        "-movflags", "+faststart",
        outPath,
      ],
      "muxing video + BGM",
    );
  }
} else {
  // No audio — just copy the video.
  run(
    ffmpeg,
    [
      "-i", videoPath,
      "-c:v", "copy",
      "-movflags", "+faststart",
      outPath,
    ],
    "copying video (no audio)",
  );
}

console.log(`stitch.mjs: wrote ${outPath}`);
