/**
 * Widget Embedding
 *
 * Reads the bundled widget JavaScript and CSS, then combines them
 * into a complete HTML document for the ChatGPT iframe.
 */

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Get the complete widget HTML with embedded JavaScript and CSS.
 */
export async function getWidgetHtml(): Promise<string> {
  // Paths to bundled assets
  const bundleJsPath = path.join(__dirname, "../../dist/widget/bundle.js");
  const bundleCssPath = path.join(__dirname, "../../dist/widget/bundle.css");

  // Read bundled JavaScript
  let js = "";
  try {
    js = fs.readFileSync(bundleJsPath, "utf-8");
  } catch (error) {
    console.error("Warning: Widget bundle not found. Run npm run build:widget");
    js = 'console.error("Widget not built. Run npm run build:widget");';
  }

  // Read bundled CSS (optional)
  let css = "";
  try {
    css = fs.readFileSync(bundleCssPath, "utf-8");
  } catch {
    // CSS is optional
  }

  // Combine into complete HTML document
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* Reset and base styles */
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
        'Helvetica Neue', Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: var(--text-primary, #1a1a1a);
      background: var(--bg-primary, #ffffff);
    }

    /* Theme variables */
    :root {
      --bg-primary: #ffffff;
      --bg-secondary: #f5f5f5;
      --text-primary: #1a1a1a;
      --text-secondary: #666666;
      --border-color: #e0e0e0;
      --accent-color: #0066cc;
      --error-color: #dc3545;
      --success-color: #28a745;
    }

    .dark-mode {
      --bg-primary: #1a1a1a;
      --bg-secondary: #2d2d2d;
      --text-primary: #ffffff;
      --text-secondary: #a0a0a0;
      --border-color: #404040;
      --accent-color: #4da6ff;
    }

    /* Bundled CSS */
    ${css}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    ${js}
  </script>
</body>
</html>
  `.trim();
}
