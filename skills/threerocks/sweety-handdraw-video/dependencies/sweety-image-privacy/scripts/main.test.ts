import assert from "node:assert/strict";
import { spawnSync } from "child_process";
import { chmodSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "fs";
import { tmpdir } from "os";
import { dirname, join } from "path";
import test from "node:test";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CLI_TEST_TIMEOUT = { timeout: 30000 };

function runOrThrow(cmd: string, args: string[]) {
  const result = spawnSync(cmd, args, { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`${cmd} ${args.join(" ")} failed: ${result.stderr}`);
  }
  return result;
}

function createTestJpeg(tempDir: string) {
  const ppmPath = join(tempDir, "input.ppm");
  const jpgPath = join(tempDir, "input.jpg");
  writeFileSync(ppmPath, "P3\n1 1\n255\n12 34 56\n");
  runOrThrow("sips", ["-s", "format", "jpeg", ppmPath, "--out", jpgPath]);
  return jpgPath;
}

test("cli writes Apple and iPhone EXIF metadata to image files", CLI_TEST_TIMEOUT, async () => {
  const tempDir = mkdtempSync(join(tmpdir(), "sweety-image-privacy-"));

  try {
    const inputPath = createTestJpeg(tempDir);
    const scriptPath = join(__dirname, "main.ts");

    const result = spawnSync(process.execPath, [scriptPath, inputPath], {
      encoding: "utf8",
    });

    assert.equal(result.status, 0);
    assert.equal(result.stderr, "");

    const exif = runOrThrow("exiftool", [
      "-s3",
      "-Make",
      "-Model",
      "-HostComputer",
      "-LensModel",
      "-FocalLength",
      "-FocalLengthIn35mmFormat",
      "-FNumber",
      "-Software",
      "-SourceFile",
      "-GPSLatitude",
      inputPath,
    ]).stdout;
    assert.match(exif, /Apple/);
    assert.match(exif, /iPhone 16 Pro Max/);
    assert.match(exif, /back triple camera/);
    assert.match(exif, /24 mm/);
    assert.match(exif, /1\.8/);
    assert.doesNotMatch(exif, /Software/);
    assert.doesNotMatch(exif, /SourceFile/);
    assert.doesNotMatch(exif, /GPS/);
  } finally {
    rmSync(tempDir, { recursive: true, force: true });
  }
});

test("cli removes macOS Where Froms attributes", CLI_TEST_TIMEOUT, async () => {
  const tempDir = mkdtempSync(join(tmpdir(), "sweety-image-privacy-"));

  try {
    const inputPath = createTestJpeg(tempDir);
    const scriptPath = join(__dirname, "main.ts");

    runOrThrow("xattr", ["-w", "com.apple.metadata:kMDItemWhereFroms", "dummy", inputPath]);
    const before = runOrThrow("xattr", ["-l", inputPath]).stdout;
    assert.match(before, /com\.apple\.metadata:kMDItemWhereFroms/);

    const result = spawnSync(process.execPath, [scriptPath, inputPath], {
      encoding: "utf8",
    });

    assert.equal(result.status, 0);

    const after = runOrThrow("xattr", ["-l", inputPath]).stdout;
    assert.doesNotMatch(after, /com\.apple\.metadata:kMDItemWhereFroms/);
  } finally {
    rmSync(tempDir, { recursive: true, force: true });
  }
});

test("cli deletes full macOS source xattr names that contain colons", CLI_TEST_TIMEOUT, async () => {
  const tempDir = mkdtempSync(join(tmpdir(), "sweety-image-privacy-"));

  try {
    const inputPath = createTestJpeg(tempDir);
    const scriptPath = join(__dirname, "main.ts");
    const fakeBin = join(tempDir, "bin");
    const logPath = join(tempDir, "xattr-calls.log");
    const whereFromsState = join(tempDir, "wherefroms-present");
    const quarantineState = join(tempDir, "quarantine-present");
    runOrThrow("mkdir", ["-p", fakeBin]);
    writeFileSync(whereFromsState, "present");
    writeFileSync(quarantineState, "present");

    const fakeXattr = join(fakeBin, "xattr");
    writeFileSync(fakeXattr, `#!/bin/sh
if [ "$#" = "1" ]; then
  if [ -f "${whereFromsState}" ]; then
    echo "com.apple.metadata:kMDItemWhereFroms"
  fi
  if [ -f "${quarantineState}" ]; then
    echo "com.apple.quarantine"
  fi
  exit 0
fi
if [ "$1" = "-l" ]; then
  if [ -f "${whereFromsState}" ]; then
    echo "com.apple.metadata:kMDItemWhereFroms: dummy"
  fi
  if [ -f "${quarantineState}" ]; then
    echo "com.apple.quarantine: dummy"
  fi
  exit 0
fi
if [ "$1" = "-d" ]; then
  echo "$2" >> "${logPath}"
  if [ "$2" = "com.apple.metadata:kMDItemWhereFroms" ]; then
    rm -f "${whereFromsState}"
  fi
  if [ "$2" = "com.apple.quarantine" ]; then
    rm -f "${quarantineState}"
  fi
  exit 0
fi
exit 0
`);
    chmodSync(fakeXattr, 0o755);

    const result = spawnSync(process.execPath, [scriptPath, inputPath], {
      encoding: "utf8",
      env: { ...process.env, PATH: `${fakeBin}:${process.env.PATH ?? ""}` },
    });

    assert.equal(result.status, 0);
    const deletedAttrs = readFileSync(logPath, "utf8").trim().split(/\r?\n/);
    assert.ok(deletedAttrs.includes("com.apple.metadata:kMDItemWhereFroms"));
    assert.ok(deletedAttrs.includes("com.apple.quarantine"));
  } finally {
    rmSync(tempDir, { recursive: true, force: true });
  }
});

test("cli falls back to deleting source xattrs when clearing all xattrs is too large", CLI_TEST_TIMEOUT, async () => {
  const tempDir = mkdtempSync(join(tmpdir(), "sweety-image-privacy-"));

  try {
    const inputPath = createTestJpeg(tempDir);
    const scriptPath = join(__dirname, "main.ts");
    const fakeBin = join(tempDir, "bin");
    const logPath = join(tempDir, "xattr-calls.log");
    const whereFromsState = join(tempDir, "wherefroms-present");
    const quarantineState = join(tempDir, "quarantine-present");
    runOrThrow("mkdir", ["-p", fakeBin]);
    writeFileSync(whereFromsState, "present");
    writeFileSync(quarantineState, "present");

    const fakeXattr = join(fakeBin, "xattr");
    writeFileSync(fakeXattr, `#!/bin/sh
if [ "$#" = "1" ]; then
  if [ -f "${whereFromsState}" ]; then
    echo "com.apple.metadata:kMDItemWhereFroms"
  fi
  if [ -f "${quarantineState}" ]; then
    echo "com.apple.quarantine"
  fi
  exit 0
fi
if [ "$1" = "-c" ]; then
  echo "xattr: [Errno 34] Result too large: '$2'" >&2
  exit 1
fi
if [ "$1" = "-d" ]; then
  echo "$2" >> "${logPath}"
  if [ "$2" = "com.apple.metadata:kMDItemWhereFroms" ]; then
    rm -f "${whereFromsState}"
  fi
  if [ "$2" = "com.apple.quarantine" ]; then
    rm -f "${quarantineState}"
  fi
  exit 0
fi
exit 0
`);
    chmodSync(fakeXattr, 0o755);

    const result = spawnSync(process.execPath, [scriptPath, inputPath], {
      encoding: "utf8",
      env: { ...process.env, PATH: `${fakeBin}:${process.env.PATH ?? ""}` },
    });

    assert.equal(result.status, 0);
    assert.equal(result.stderr, "");
    const deletedAttrs = readFileSync(logPath, "utf8").trim().split(/\r?\n/);
    assert.ok(deletedAttrs.includes("com.apple.metadata:kMDItemWhereFroms"));
    assert.ok(deletedAttrs.includes("com.apple.quarantine"));
  } finally {
    rmSync(tempDir, { recursive: true, force: true });
  }
});

test("json output includes privacy audit after processing", CLI_TEST_TIMEOUT, async () => {
  const tempDir = mkdtempSync(join(tmpdir(), "sweety-image-privacy-"));

  try {
    const inputPath = createTestJpeg(tempDir);
    const scriptPath = join(__dirname, "main.ts");

    runOrThrow("exiftool", [
      "-overwrite_original",
      "-GPSLatitude=39.80035",
      "-GPSLatitudeRef=N",
      "-GPSLongitude=116.50708",
      "-GPSLongitudeRef=E",
      "-Software=AI Generator",
      inputPath,
    ]);

    const result = spawnSync(process.execPath, [scriptPath, inputPath, "--json"], {
      encoding: "utf8",
    });

    assert.equal(result.status, 0);
    assert.equal(result.stderr, "");

    const report = JSON.parse(result.stdout);
    assert.equal(report[0].privacy.gpsPresent, false);
    assert.equal(report[0].privacy.sourceExifPresent, false);
    assert.deepEqual(report[0].privacy.requiredMacSourceXattrsPresent, []);
    assert.equal(report[0].camera.make, "Apple");
    assert.equal(report[0].camera.model, "iPhone 16 Pro Max");
    assert.match(report[0].camera.lensModel, /iPhone 16 Pro Max back triple camera/);
  } finally {
    rmSync(tempDir, { recursive: true, force: true });
  }
});
