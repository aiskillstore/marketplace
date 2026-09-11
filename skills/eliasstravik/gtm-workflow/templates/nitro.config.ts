import { defineConfig } from "nitro";

export default defineConfig({
  serverDir: "./server",
  traceDeps: ["@resvg/resvg-js"],
  modules: ["workflow/nitro"],
  workflow: { dirs: ["workflows"] },
  serverAssets: [
    { baseName: "workflows", dir: "./workflows", pattern: "**/*.ts" },
    { baseName: "fonts", dir: "./assets/fonts", pattern: "*.ttf" },
  ],
} as any);
