#!/usr/bin/env node

/**
 * HTML to PDF Converter with Hebrew/RTL Support
 * Uses Puppeteer for pixel-perfect rendering
 *
 * Usage:
 *   node html-to-pdf.js <input> <output> [options]
 *
 * Input can be:
 *   - Local HTML file path
 *   - URL (http:// or https://)
 *   - "-" for stdin (pipe HTML content)
 *
 * Options:
 *   --format=<format>       Page format: A4, Letter, Legal, A3, A5 (default: A4)
 *   --landscape             Use landscape orientation
 *   --margin=<value>        Set all margins (e.g., "20mm" or "1in")
 *   --margin-top=<value>    Top margin
 *   --margin-right=<value>  Right margin
 *   --margin-bottom=<value> Bottom margin
 *   --margin-left=<value>   Left margin
 *   --scale=<number>        Scale factor 0.1-2.0 (default: 1)
 *   --background            Print background graphics (default: true)
 *   --no-background         Don't print background graphics
 *   --header=<html>         Header HTML template
 *   --footer=<html>         Footer HTML template
 *   --wait=<ms>             Additional wait time for fonts/JS (default: 1000)
 *   --rtl                   Force RTL direction
 *   --font=<path>           Load additional font file
 *   --executable-path=<path>  Use system Chrome/Edge executable
 *   --user-agent=<value>    Override default user agent
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

function findExecutablePath() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  const candidates = [
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return null;
}

// Parse command line arguments
function parseArgs(args) {
  const options = {
    input: null,
    output: null,
    format: 'A4',
    landscape: false,
    margin: { top: '20mm', right: '20mm', bottom: '20mm', left: '20mm' },
    scale: 1,
    printBackground: true,
    headerTemplate: '',
    footerTemplate: '',
    displayHeaderFooter: false,
    waitTime: 1000,
    forceRtl: false,
    additionalFonts: [],
    executablePath: null,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
  };

  const positional = [];

  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [key, value] = arg.slice(2).split('=');

      switch (key) {
        case 'format':
          options.format = value;
          break;
        case 'landscape':
          options.landscape = true;
          break;
        case 'margin':
          options.margin = { top: value, right: value, bottom: value, left: value };
          break;
        case 'margin-top':
          options.margin.top = value;
          break;
        case 'margin-right':
          options.margin.right = value;
          break;
        case 'margin-bottom':
          options.margin.bottom = value;
          break;
        case 'margin-left':
          options.margin.left = value;
          break;
        case 'scale':
          options.scale = parseFloat(value);
          break;
        case 'background':
          options.printBackground = true;
          break;
        case 'no-background':
          options.printBackground = false;
          break;
        case 'header':
          options.headerTemplate = value;
          options.displayHeaderFooter = true;
          break;
        case 'footer':
          options.footerTemplate = value;
          options.displayHeaderFooter = true;
          break;
        case 'wait':
          options.waitTime = parseInt(value, 10);
          break;
        case 'rtl':
          options.forceRtl = true;
          break;
        case 'font':
          options.additionalFonts.push(value);
          break;
        case 'executable-path':
          options.executablePath = value;
          break;
        case 'user-agent':
          options.userAgent = value;
          break;
      }
    } else {
      positional.push(arg);
    }
  }

  options.input = positional[0];
  options.output = positional[1];

  return options;
}

// Detect if content contains RTL characters (Hebrew, Arabic)
function containsRtlCharacters(text) {
  // Hebrew: \u0590-\u05FF, Arabic: \u0600-\u06FF, \u0750-\u077F
  const rtlPattern = /[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F]/;
  return rtlPattern.test(text);
}

// Read input from file, URL, or stdin
async function getInputContent(input) {
  if (input === '-') {
    // Read from stdin
    return new Promise((resolve, reject) => {
      let data = '';
      process.stdin.setEncoding('utf8');
      process.stdin.on('data', chunk => data += chunk);
      process.stdin.on('end', () => resolve({ type: 'html', content: data }));
      process.stdin.on('error', reject);
    });
  } else if (input.startsWith('http://') || input.startsWith('https://')) {
    return { type: 'url', content: input };
  } else {
    const absolutePath = path.resolve(input);
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`File not found: ${absolutePath}`);
    }
    return { type: 'file', content: absolutePath };
  }
}

// CSS to inject for proper RTL and font support
function getRtlCss(forceRtl) {
  return `
    /* Hebrew/RTL Support CSS */
    @font-face {
      font-family: 'Noto Sans Hebrew';
      src: local('Noto Sans Hebrew'), local('NotoSansHebrew');
      unicode-range: U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F;
    }

    /* Ensure proper RTL handling */
    [lang="he"], [lang="iw"], [dir="rtl"], .rtl {
      direction: rtl;
      text-align: right;
    }

    /* Auto-detect RTL content */
    :lang(he), :lang(iw), :lang(ar) {
      direction: rtl;
      text-align: right;
    }

    ${forceRtl ? `
    html, body {
      direction: rtl;
      text-align: right;
    }
    ` : ''}

    /* Improve print quality */
    @media print {
      * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
    }
  `;
}

async function convertHtmlToPdf(options) {
  const executablePath = options.executablePath || findExecutablePath();
  const outputsDir = path.resolve(__dirname, '..', 'outputs');
  const outputHasDir = options.output && path.dirname(options.output) !== '.';
  const outputPath = outputHasDir ? options.output : path.join(outputsDir, options.output);
  if (!fs.existsSync(outputsDir)) {
    fs.mkdirSync(outputsDir, { recursive: true });
  }
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: executablePath || undefined,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--font-render-hinting=none',
      '--disable-font-subpixel-positioning'
    ]
  });

  try {
    const page = await browser.newPage();

    // Set viewport for consistent rendering
    await page.setViewport({ width: 1200, height: 800, deviceScaleFactor: 2 });

    // Set user agent and basic headers to reduce 403 blocks
    if (options.userAgent) {
      await page.setUserAgent(options.userAgent);
    }
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9'
    });

    // Get input content
    const input = await getInputContent(options.input);

    // Navigate to content
    if (input.type === 'url') {
      await page.goto(input.content, {
        waitUntil: ['networkidle0', 'domcontentloaded'],
        timeout: 60000
      });
    } else if (input.type === 'file') {
      await page.goto(`file://${input.content}`, {
        waitUntil: ['networkidle0', 'domcontentloaded'],
        timeout: 60000
      });
    } else {
      await page.setContent(input.content, {
        waitUntil: ['networkidle0', 'domcontentloaded'],
        timeout: 60000
      });
    }

    // Inject RTL/font support CSS
    await page.addStyleTag({ content: getRtlCss(options.forceRtl) });

    // Auto-detect RTL content and set direction if needed
    const pageContent = await page.content();
    const hasRtl = containsRtlCharacters(pageContent);

    if (hasRtl || options.forceRtl) {
      await page.evaluate(() => {
        // Check if already has direction set
        const html = document.documentElement;
        const body = document.body;

        if (!html.getAttribute('dir') && !body.getAttribute('dir')) {
          // Auto-set RTL for Hebrew content
          const text = body.innerText || '';
          const hebrewPattern = /[\u0590-\u05FF]/;
          if (hebrewPattern.test(text)) {
            html.setAttribute('dir', 'rtl');
            html.setAttribute('lang', 'he');
          }
        }
      });
    }

    // Wait for fonts to load
    await page.evaluateHandle('document.fonts.ready');

    // Additional wait for complex content/fonts
    if (options.waitTime > 0) {
      await new Promise(resolve => setTimeout(resolve, options.waitTime));
    }

    // Generate PDF
    const pdfOptions = {
      path: outputPath,
      format: options.format,
      landscape: options.landscape,
      margin: options.margin,
      scale: options.scale,
      printBackground: options.printBackground,
      displayHeaderFooter: options.displayHeaderFooter,
      headerTemplate: options.headerTemplate,
      footerTemplate: options.footerTemplate,
      preferCSSPageSize: true
    };

    await page.pdf(pdfOptions);

    console.log(`PDF generated successfully: ${outputPath}`);
    return true;

  } finally {
    await browser.close();
  }
}

// Main execution
async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2 || args.includes('--help') || args.includes('-h')) {
    console.log(`
HTML to PDF Converter with Hebrew/RTL Support
==============================================

Usage:
  html-to-pdf <input> <output.pdf> [options]

Input:
  - Local HTML file path
  - URL (http:// or https://)
  - "-" for stdin (pipe HTML content)

Options:
  --format=<format>       Page format: A4, Letter, Legal, A3, A5 (default: A4)
  --landscape             Use landscape orientation
  --margin=<value>        Set all margins (e.g., "20mm" or "1in")
  --margin-top=<value>    Top margin
  --margin-right=<value>  Right margin
  --margin-bottom=<value> Bottom margin
  --margin-left=<value>   Left margin
  --scale=<number>        Scale factor 0.1-2.0 (default: 1)
  --background            Print background graphics (default: true)
  --no-background         Don't print background graphics
  --header=<html>         Header HTML template
  --footer=<html>         Footer HTML template
  --wait=<ms>             Additional wait time for fonts/JS (default: 1000)
  --rtl                   Force RTL direction for entire document
  --executable-path=<path>  Use system Chrome/Edge executable
  --user-agent=<value>    Override default user agent
  (env) PUPPETEER_EXECUTABLE_PATH  Use system Chrome/Edge executable

Examples:
  # Convert local HTML file
  html-to-pdf document.html output.pdf

  # Convert URL to PDF
  html-to-pdf https://example.com page.pdf

  # Hebrew document with forced RTL
  html-to-pdf hebrew.html hebrew.pdf --rtl

  # Custom margins and format
  html-to-pdf doc.html out.pdf --format=Letter --margin=1in

  # Pipe HTML content
  echo "<h1>שלום עולם</h1>" | html-to-pdf - hello.pdf --rtl
`);
    process.exit(args.includes('--help') || args.includes('-h') ? 0 : 1);
  }

  const options = parseArgs(args);

  if (!options.input || !options.output) {
    console.error('Error: Both input and output are required');
    process.exit(1);
  }

  try {
    await convertHtmlToPdf(options);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
