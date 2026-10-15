#!/usr/bin/env bun
import { existsSync, readdirSync, renameSync, statSync } from "fs";
import { basename, dirname, extname, join, resolve } from "path";
import { spawn } from "child_process";

const SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif"];
const MAC_SOURCE_XATTRS = [
  "com.apple.metadata:kMDItemWhereFroms",
  "com.apple.provenance",
  "com.apple.quarantine",
];
const REQUIRED_MAC_SOURCE_XATTRS = [
  "com.apple.metadata:kMDItemWhereFroms",
  "com.apple.quarantine",
];
const SOURCE_EXIF_TAGS = [
  "-Software",
  "-Source",
  "-SourceFile",
  "-ImageDescription",
  "-Comment",
  "-UserComment",
  "-Copyright",
  "-Artist",
  "-Creator",
];

interface PrivacyAudit {
  gpsPresent: boolean;
  sourceExifPresent: boolean;
  macSourceXattrsPresent: string[];
  requiredMacSourceXattrsPresent: string[];
}

interface CameraAudit {
  make: string;
  model: string;
  hostComputer: string;
  lensModel: string;
  focalLength: string;
  focalLengthIn35mmFormat: string;
  fNumber: string;
}

interface ProcessResult {
  input: string;
  output: string;
  used: string;
  camera: CameraAudit;
  privacy: PrivacyAudit;
}

function commandExists(cmd: string): Promise<boolean> {
  return new Promise((resolve) => {
    const proc = spawn("which", [cmd], { stdio: ["ignore", "ignore", "pipe"] });
    proc.on("close", (code) => resolve(code === 0));
    proc.on("error", () => resolve(false));
  });
}

function runCmd(cmd: string, args: string[]): Promise<{ code: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const proc = spawn(cmd, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    proc.stdout?.on("data", (chunk) => { stdout += chunk.toString(); });
    proc.stderr?.on("data", (chunk) => { stderr += chunk.toString(); });
    proc.on("close", (code) => resolve({ code: code ?? 1, stdout, stderr }));
    proc.on("error", (err) => resolve({ code: 1, stdout: "", stderr: err.message }));
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function modifyWithExiftool(input: string, output?: string): Promise<string> {
  const args = [
    "-all=",
    "-GPS:all=",
    "-Source=",
    "-SourceFile=",
    "-ImageDescription=",
    "-Comment=",
    "-UserComment=",
    "-Copyright=",
    "-Artist=",
    "-Creator=",
    "-Software=",
    `-Make=Apple`,
    `-Model=iPhone 16 Pro Max`,
    `-HostComputer=iPhone 16 Pro Max`,
    `-LensModel=iPhone 16 Pro Max back triple camera 6.765mm f/1.78`,
    `-FocalLength=6.765 mm`,
    `-FocalLengthIn35mmFormat=24 mm`,
    `-FNumber=1.78`,
    `-ExposureProgram=Program AE`,
    `-MeteringMode=Multi-segment`,
    `-Flash=Off, Did not fire`,
    `-WhiteBalance=Auto`,
    `-ColorSpace=Uncalibrated`,
  ];
  if (output) {
    const temp = output + ".tmp";
    args.push("-o", temp, input);
    const result = await runCmd("exiftool", args);
    if (result.code !== 0) throw new Error(result.stderr.trim() || "exiftool failed");
    await clearMacSourceMetadata(temp);
    renameSync(temp, output);
    return output;
  }
  args.unshift("-overwrite_original");
  args.push(input);
  const result = await runCmd("exiftool", args);
  if (result.code !== 0) throw new Error(result.stderr.trim() || "exiftool failed");
  return input;
}

async function modifyWithSharp(input: string, output: string): Promise<string> {
  const sharp = (await import("sharp")).default;
  const tempOutput = `${output}.tmp`;
  await sharp(input)
    .withExif({
      IFD0: {
        Make: "Apple",
        Model: "iPhone 16 Pro Max",
        HostComputer: "iPhone 16 Pro Max",
        LensModel: "iPhone 16 Pro Max back triple camera 6.765mm f/1.78",
      },
    })
    .toFile(tempOutput);
  renameSync(tempOutput, output);
  return output;
}

async function listMacXattrs(path: string): Promise<string[]> {
  const hasXattr = await commandExists("xattr");
  if (!hasXattr) return [];
  const result = await runCmd("xattr", [path]);
  if (result.code !== 0) {
    throw new Error(`Failed to list macOS metadata from ${path}: ${result.stderr.trim() || "xattr failed"}`);
  }
  return result.stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

async function readExifLines(path: string, tags: string[]): Promise<string[]> {
  const result = await runCmd("exiftool", ["-s3", ...tags, path]);
  if (result.code !== 0) {
    throw new Error(`Failed to read EXIF from ${path}: ${result.stderr.trim() || "exiftool failed"}`);
  }
  return result.stdout.split(/\r?\n/).map((line) => line.trim());
}

async function auditImage(path: string): Promise<{ camera: CameraAudit; privacy: PrivacyAudit }> {
  const [
    make = "",
    model = "",
    hostComputer = "",
    lensModel = "",
    focalLength = "",
    focalLengthIn35mmFormat = "",
    fNumber = "",
  ] = await readExifLines(path, [
    "-Make",
    "-Model",
    "-HostComputer",
    "-LensModel",
    "-FocalLength",
    "-FocalLengthIn35mmFormat",
    "-FNumber",
  ]);
  const gpsLines = await readExifLines(path, ["-GPSLatitude", "-GPSLongitude"]);
  const sourceLines = await readExifLines(path, SOURCE_EXIF_TAGS);
  const macXattrs = await listMacXattrs(path);

  return {
    camera: {
      make,
      model,
      hostComputer,
      lensModel,
      focalLength,
      focalLengthIn35mmFormat,
      fNumber,
    },
    privacy: {
      gpsPresent: gpsLines.some(Boolean),
      sourceExifPresent: sourceLines.some(Boolean),
      macSourceXattrsPresent: MAC_SOURCE_XATTRS.filter((attr) => macXattrs.includes(attr)),
      requiredMacSourceXattrsPresent: REQUIRED_MAC_SOURCE_XATTRS.filter((attr) => macXattrs.includes(attr)),
    },
  };
}

async function clearMacSourceMetadata(path: string): Promise<void> {
  const hasXattr = await commandExists("xattr");
  if (!hasXattr) return;

  let lastRemainingRequired: string[] = [];
  for (let attempt = 1; attempt <= 5; attempt += 1) {
    const listResult = await runCmd("xattr", [path]);
    if (listResult.code !== 0) {
      throw new Error(`Failed to list macOS metadata from ${path}: ${listResult.stderr.trim() || "xattr failed"}`);
    }

    let attrs = new Set(listResult.stdout
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean));

    if (MAC_SOURCE_XATTRS.some((attr) => attrs.has(attr))) {
      const clearAllResult = await runCmd("xattr", ["-c", path]);
      if (clearAllResult.code === 0) {
        const refreshedListResult = await runCmd("xattr", [path]);
        if (refreshedListResult.code !== 0) {
          throw new Error(`Failed to list macOS metadata from ${path}: ${refreshedListResult.stderr.trim() || "xattr failed"}`);
        }
        attrs = new Set(refreshedListResult.stdout
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter(Boolean));
      } else if (!clearAllResult.stderr.includes("Result too large")) {
        throw new Error(`Failed to clear macOS metadata from ${path}: ${clearAllResult.stderr.trim() || "xattr failed"}`);
      }
    }

    for (const attr of MAC_SOURCE_XATTRS) {
      if (!attrs.has(attr)) continue;
      const deleteResult = await runCmd("xattr", ["-d", attr, path]);
      const missingAttr = deleteResult.stderr.includes("No such xattr");
      if (deleteResult.code !== 0 && REQUIRED_MAC_SOURCE_XATTRS.includes(attr) && !missingAttr) {
        throw new Error(`Failed to delete macOS source metadata ${attr} from ${path}: ${deleteResult.stderr.trim() || "xattr failed"}`);
      }
    }

    const verifyResult = await runCmd("xattr", [path]);
    if (verifyResult.code !== 0) {
      throw new Error(`Failed to verify macOS metadata from ${path}: ${verifyResult.stderr.trim() || "xattr failed"}`);
    }

    const remainingAttrs = new Set(verifyResult.stdout
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean));
    lastRemainingRequired = REQUIRED_MAC_SOURCE_XATTRS.filter((attr) => remainingAttrs.has(attr));
    if (lastRemainingRequired.length === 0) {
      await sleep(250);
      const stableVerifyResult = await runCmd("xattr", [path]);
      if (stableVerifyResult.code !== 0) {
        throw new Error(`Failed to verify macOS metadata from ${path}: ${stableVerifyResult.stderr.trim() || "xattr failed"}`);
      }
      const stableRemainingAttrs = new Set(stableVerifyResult.stdout
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean));
      lastRemainingRequired = REQUIRED_MAC_SOURCE_XATTRS.filter((attr) => stableRemainingAttrs.has(attr));
      if (lastRemainingRequired.length === 0) return;
    }
    if (attempt < 5) await sleep(100);
  }

  throw new Error(`Failed to clear macOS source metadata from ${path}: ${lastRemainingRequired.join(", ")}`);
}

async function findRemainingRequiredMacSourceMetadata(paths: string[]): Promise<Array<{ path: string; attrs: string[] }>> {
  const hasXattr = await commandExists("xattr");
  if (!hasXattr) return [];

  const remaining: Array<{ path: string; attrs: string[] }> = [];
  for (const path of paths) {
    if (!existsSync(path)) continue;
    const listResult = await runCmd("xattr", [path]);
    if (listResult.code !== 0) {
      throw new Error(`Failed to list macOS metadata from ${path}: ${listResult.stderr.trim() || "xattr failed"}`);
    }
    const attrs = new Set(listResult.stdout
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean));
    const requiredAttrs = REQUIRED_MAC_SOURCE_XATTRS.filter((attr) => attrs.has(attr));
    if (requiredAttrs.length > 0) remaining.push({ path, attrs: requiredAttrs });
  }
  return remaining;
}

async function clearMacSourceMetadataAfterImageWrites(paths: string[]): Promise<void> {
  let remaining: Array<{ path: string; attrs: string[] }> = [];
  let cleanPasses = 0;
  for (let pass = 1; pass <= 10; pass += 1) {
    await sleep(1500);
    remaining = await findRemainingRequiredMacSourceMetadata(paths);
    if (remaining.length === 0) {
      cleanPasses += 1;
      if (cleanPasses >= 3) return;
      continue;
    }
    cleanPasses = 0;
    for (const item of remaining) {
      await clearMacSourceMetadata(item.path);
    }
  }

  remaining = await findRemainingRequiredMacSourceMetadata(paths);
  if (remaining.length > 0) {
    const detail = remaining.map((item) => `${item.path}: ${item.attrs.join(", ")}`).join("; ");
    throw new Error(`Failed to clear macOS source metadata after final verification: ${detail}`);
  }
}

function printHelp() {
  console.log(`Usage: bun main.ts <input> [options]

Options:
  -o, --output <path>   Output file path
  -k, --keep            Keep original file when processing in place
  -r, --recursive       Process directories recursively
      --json            JSON output
  -h, --help            Show this help message
`);
}

interface Options {
  input: string;
  output?: string;
  keep: boolean;
  recursive: boolean;
  json: boolean;
}

function parseArgs(args: string[]): Options | null {
  const opts: Options = { input: "", keep: false, recursive: false, json: false };
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    }
    if (arg === "-o" || arg === "--output") {
      opts.output = args[++i];
    } else if (arg === "-k" || arg === "--keep") {
      opts.keep = true;
      } else if (arg === "-r" || arg === "--recursive") {
      opts.recursive = true;
    } else if (arg === "--json") {
      opts.json = true;
    } else if (!arg.startsWith("-") && !opts.input) {
      opts.input = arg;
    }
  }
  if (!opts.input) {
    console.error("Error: Input file or directory required");
    printHelp();
    return null;
  }
  return opts;
}

function collectFiles(dir: string, recursive: boolean): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (recursive) results.push(...collectFiles(full, recursive));
      continue;
    }
    if (SUPPORTED_EXTS.includes(extname(entry.name).toLowerCase())) {
      results.push(full);
    }
  }
  return results;
}

function getDefaultOutputPath(input: string, keep: boolean): string {
  if (keep) {
    const ext = extname(input);
    const base = basename(input, ext);
    return join(dirname(input), `${base}-exif${ext}`);
  }
  return input;
}

async function processOne(input: string, opts: Options): Promise<ProcessResult> {
  const abs = resolve(input);
  const output = opts.output ? resolve(opts.output) : getDefaultOutputPath(abs, opts.keep);
  const useExiftool = await commandExists("exiftool");
  await clearMacSourceMetadata(abs);
  let resultPath = output;
  let used = "sharp";
  if (useExiftool) {
    const targetOutput = opts.output || (opts.keep ? output : undefined);
    resultPath = await modifyWithExiftool(abs, targetOutput);
    await clearMacSourceMetadata(resultPath);
    used = "exiftool";
  } else {
    try {
      resultPath = await modifyWithSharp(abs, output);
      await clearMacSourceMetadata(resultPath);
    } catch (error) {
      throw new Error(`Failed to modify EXIF: ${error instanceof Error ? error.message : String(error)}. Install sharp with 'bun add sharp' or 'npm install sharp'.`);
    }
  }
  const audit = await auditImage(resultPath);
  return { input: abs, output: resultPath, used, ...audit };
}

async function main() {
  const args = process.argv.slice(2);
  const opts = parseArgs(args);
  if (!opts) process.exit(1);
  const input = resolve(opts.input);
  if (!existsSync(input)) {
    console.error(`Error: ${input} not found`);
    process.exit(1);
  }

  const taskInputs: string[] = [];
  if (statSync(input).isDirectory()) {
    const files = collectFiles(input, true); // Always recursive for directories
    if (files.length === 0) {
      console.error("No supported images found in directory");
      process.exit(1);
    }
    taskInputs.push(...files);
  } else {
    taskInputs.push(input);
  }

  const results: ProcessResult[] = [];
  for (const file of taskInputs) {
    results.push(await processOne(file, opts));
  }
  await clearMacSourceMetadataAfterImageWrites(results.map((item) => item.output));
  for (let i = 0; i < results.length; i += 1) {
    const audit = await auditImage(results[i].output);
    results[i] = { ...results[i], ...audit };
  }
  if (opts.json) {
    console.log(JSON.stringify(results, null, 2));
    return;
  }
  for (const item of results) {
    console.log(`${item.input} → ${item.output} (${item.used})`);
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
