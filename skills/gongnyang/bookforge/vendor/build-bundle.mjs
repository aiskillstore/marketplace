#!/usr/bin/env node
// antv-ssr.bundle.mjs 재생성기 — AntV 버전을 올릴 때만 실행한다.
// 평시 렌더는 커밋된 번들만 쓰므로 npm 레지스트리·node_modules 없이 재현된다.
//
// 재생성 절차:
//   cd <SKILL> && npm ci && node vendor/build-bundle.mjs
// 검증(필수): 기존 도해 전량 재렌더 → SVG byte-identical 확인 후 커밋.
import { execSync } from "node:child_process";

const ESBUILD = "esbuild@0.24.2"; // 재현성 — 버전 고정
const BANNER = "import { createRequire as __bfCreateRequire } from 'node:module'; "
  + "const require = __bfCreateRequire(import.meta.url);";

execSync(
  `npx -y ${ESBUILD} vendor/antv-entry.mjs --bundle --platform=node --format=esm `
  + `--outfile=vendor/antv-ssr.bundle.mjs --log-level=warning --banner:js="${BANNER}"`,
  { stdio: "inherit", cwd: new URL("..", import.meta.url).pathname });
console.log("OK: vendor/antv-ssr.bundle.mjs 재생성 — byte-identical 검증을 잊지 말 것");
