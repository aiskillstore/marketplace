/**
 * Widget Build Script
 *
 * Uses esbuild to bundle the React widget into a single JavaScript file.
 * The bundled output is then embedded into the MCP server responses.
 */

import * as esbuild from "esbuild";
import * as fs from "fs";
import * as path from "path";

async function build() {
  console.log("Building widget...");

  // Ensure output directory exists
  fs.mkdirSync("dist/widget", { recursive: true });

  try {
    // Bundle React widget
    const result = await esbuild.build({
      entryPoints: ["src/widget/App.tsx"],
      bundle: true,
      format: "esm",
      minify: process.env.NODE_ENV === "production",
      sourcemap: process.env.NODE_ENV !== "production",
      write: false,
      target: ["es2020"],
      loader: {
        ".tsx": "tsx",
        ".ts": "ts",
        ".css": "css",
      },
      // Bundle all dependencies (they run in browser iframe)
      external: [],
      define: {
        "process.env.NODE_ENV": JSON.stringify(
          process.env.NODE_ENV || "development"
        ),
      },
      jsx: "automatic",
    });

    // Get bundled JavaScript
    const bundledJs = result.outputFiles[0].text;

    // Read CSS file if it exists
    const cssPath = path.join("src/widget/styles.css");
    let css = "";
    if (fs.existsSync(cssPath)) {
      css = fs.readFileSync(cssPath, "utf-8");
    }

    // Write bundle files
    fs.writeFileSync("dist/widget/bundle.js", bundledJs);
    fs.writeFileSync("dist/widget/bundle.css", css);

    console.log("Widget built successfully!");
    console.log(`  - dist/widget/bundle.js (${(bundledJs.length / 1024).toFixed(1)} KB)`);
    if (css) {
      console.log(`  - dist/widget/bundle.css (${(css.length / 1024).toFixed(1)} KB)`);
    }
  } catch (error) {
    console.error("Widget build failed:", error);
    process.exit(1);
  }
}

build();
