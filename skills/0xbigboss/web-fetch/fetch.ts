import { parseHTML } from "linkedom";
import TurndownService from "turndown";

const url = process.argv[2];
if (!url) {
  console.error("Usage: bun fetch.ts <url>");
  process.exit(1);
}

// Step 1: Fetch
const response = await fetch(url, {
  headers: {
    "User-Agent": "Mozilla/5.0 (compatible; ClaudeCode/1.0)",
  },
});

if (!response.ok) {
  console.error(`Fetch failed: ${response.status} ${response.statusText}`);
  process.exit(1);
}

const html = await response.text();

// Step 2: Parse DOM
const { document } = parseHTML(html);

// Step 3: Find the content-rich element
const candidates = [
  ...document.querySelectorAll("article"),
  ...document.querySelectorAll("main"),
  ...document.querySelectorAll('[role="main"]'),
  ...document.querySelectorAll(".content"),
  ...document.querySelectorAll("#content"),
];

let contentEl: Element | null = null;
let maxLength = 0;

for (const el of candidates) {
  const len = el.textContent?.length || 0;
  if (len > maxLength) {
    maxLength = len;
    contentEl = el;
  }
}

if (!contentEl) {
  contentEl = document.body;
}

// Step 4: Clean up the content element before conversion
// Remove navigation elements
const removeSelectors = [
  "nav",
  "header",
  "footer",
  "script",
  "style",
  "noscript",
  '[role="navigation"]',
  ".sidebar",
  ".nav",
  ".menu",
  ".toc",
  '[aria-label="breadcrumb"]',
];

for (const selector of removeSelectors) {
  contentEl.querySelectorAll(selector).forEach((el) => el.remove());
}

// Step 5: Convert to Markdown with Turndown
const turndown = new TurndownService({
  headingStyle: "atx",
  codeBlockStyle: "fenced",
});

// Better code block handling
turndown.addRule("fencedCodeBlock", {
  filter: (node) => {
    return (
      node.nodeName === "PRE" &&
      node.firstChild &&
      node.firstChild.nodeName === "CODE"
    );
  },
  replacement: (content, node) => {
    const el = node as Element;
    const code = el.querySelector("code");
    const className = code?.className || "";
    const lang = className.match(/language-(\w+)/)?.[1] || "";
    const text = code?.textContent || "";
    return `\n\`\`\`${lang}\n${text}\n\`\`\`\n`;
  },
});

// Handle pre without code child
turndown.addRule("preBlock", {
  filter: (node) => {
    return (
      node.nodeName === "PRE" &&
      (!node.firstChild || node.firstChild.nodeName !== "CODE")
    );
  },
  replacement: (content, node) => {
    const text = (node as Element).textContent || "";
    return `\n\`\`\`\n${text}\n\`\`\`\n`;
  },
});

// Remove "Copy page" buttons and similar UI elements
turndown.addRule("removeButtons", {
  filter: (node) => {
    if (node.nodeName === "BUTTON") return true;
    const el = node as Element;
    if (el.getAttribute?.("aria-label")?.includes("Copy")) return true;
    return false;
  },
  replacement: () => "",
});

const markdown = turndown.turndown(contentEl.innerHTML);

// Step 6: Clean up the output
const cleaned = markdown
  // Remove Loading... placeholders
  .replace(/^Loading\.\.\.$/gm, "")
  // Remove Copy buttons
  .replace(/^Copy page$/gm, "")
  .replace(/^Copy$/gm, "")
  // Fix empty headings (## \n\nActual heading -> ## Actual heading)
  .replace(/^(#{1,6})\s*\n\n+([A-Z])/gm, "$1 $2")
  // Remove completely empty headings
  .replace(/^#{1,6}\s*$/gm, "")
  // Collapse multiple newlines
  .replace(/\n{3,}/g, "\n\n")
  .trim();

// Output with title
const title = document.title || "Untitled";
console.log(`# ${title}\n`);
console.log(cleaned);
