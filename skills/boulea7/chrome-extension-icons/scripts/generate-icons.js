#!/usr/bin/env node

/**
 * Chrome Extension Icons Generator
 *
 * Automatically searches, downloads, and converts icons from Iconify
 * to Chrome Extension compatible PNG formats (16x16, 32x32, 48x48, 128x128)
 * and updates manifest.json configuration.
 *
 * Usage:
 *   search <keyword>                            - Search for icons
 *   generate --icon <id> [options]              - Generate icons from Iconify
 *   convert --input <svg> [options]             - Convert local SVG
 *   batch --config <json>                       - Batch generate from config file
 */

const fs = require('fs').promises;
const path = require('path');
const https = require('https');
const http = require('http');

// Dynamic import for sharp (ESM module)
let sharp;
(async () => {
  try {
    sharp = (await import('sharp')).default;
  } catch (err) {
    console.error('❌ Failed to load sharp. Please install it: npm install sharp');
    console.error('   For installation issues, see: https://sharp.pixelplumbing.com/install');
    process.exit(1);
  }
})();

// Default icon sizes for Chrome extensions
const DEFAULT_SIZES = [16, 32, 48, 128];

// Store for top 5 search results
const searchCache = {
  lastQuery: null,
  topResults: []
};

/**
 * Fetch data from URL with retry logic
 */
async function fetchWithRetry(url, options = {}, retries = 3) {
  const protocol = url.startsWith('https') ? https : http;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await new Promise((resolve, reject) => {
        const req = protocol.get(url, options, (res) => {
          if (res.statusCode === 429) {
            const retryAfter = res.headers['retry-after'] || 60;
            reject(new Error(`RATE_LIMIT:${retryAfter}`));
            return;
          }

          if (res.statusCode !== 200) {
            reject(new Error(`HTTP ${res.statusCode}: ${res.statusMessage}`));
            return;
          }

          const chunks = [];
          res.on('data', chunk => chunks.push(chunk));
          res.on('end', () => resolve(Buffer.concat(chunks)));
        });

        req.on('error', reject);
        req.setTimeout(10000, () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });
      });
    } catch (error) {
      if (error.message.startsWith('RATE_LIMIT:')) {
        const waitSeconds = parseInt(error.message.split(':')[1]);
        console.log(`⏳ API rate limit reached. Waiting ${waitSeconds} seconds...`);
        await new Promise(resolve => setTimeout(resolve, waitSeconds * 1000));
        continue;
      }

      if (attempt === retries) {
        throw error;
      }

      const backoff = Math.min(1000 * Math.pow(2, attempt), 10000);
      console.log(`⚠️  Attempt ${attempt} failed. Retrying in ${backoff/1000}s...`);
      await new Promise(resolve => setTimeout(resolve, backoff));
    }
  }
}

/**
 * Search icons on Iconify
 */
async function searchIcons(keyword, limit = 20) {
  console.log(`🔍 Searching for "${keyword}"...`);

  const url = `https://api.iconify.design/search?query=${encodeURIComponent(keyword)}&limit=${limit}`;

  try {
    const buffer = await fetchWithRetry(url);
    const data = JSON.parse(buffer.toString());

    if (!data.icons || data.icons.length === 0) {
      console.log('❌ No icons found. Try a different keyword.');
      return [];
    }

    const results = data.icons.map((iconId, index) => {
      const [prefix, name] = iconId.split(':');
      return {
        rank: index + 1,
        id: iconId,
        prefix,
        name,
        downloadUrl: `https://api.iconify.design/${prefix}/${name}.svg`,
        previewUrl: `https://icon-sets.iconify.design/${prefix}/icons/${name}.html`
      };
    });

    // Store top 5 for reference
    searchCache.lastQuery = keyword;
    searchCache.topResults = results.slice(0, 5);

    return results;
  } catch (error) {
    console.error(`❌ Search failed: ${error.message}`);
    throw error;
  }
}

/**
 * Download icon SVG from Iconify
 */
async function downloadIcon(iconId, color = null) {
  const [prefix, name] = iconId.split(':');

  if (!prefix || !name) {
    throw new Error('Invalid icon ID format. Expected format: "prefix:name" (e.g., "mdi:home")');
  }

  let url = `https://api.iconify.design/${prefix}/${name}.svg`;

  if (color) {
    // Remove # from color if present
    const colorHex = color.replace('#', '');
    url += `?color=%23${colorHex}`;
    console.log(`🎨 Applying color: #${colorHex}`);
  }

  console.log(`⬇️  Downloading: ${iconId}`);

  try {
    const buffer = await fetchWithRetry(url);
    console.log(`✓ Downloaded ${buffer.length} bytes`);
    return buffer;
  } catch (error) {
    console.error(`❌ Download failed: ${error.message}`);
    throw error;
  }
}

/**
 * Read local SVG file
 */
async function readLocalSvg(filePath) {
  console.log(`📂 Reading local SVG: ${filePath}`);

  try {
    const buffer = await fs.readFile(filePath);
    console.log(`✓ Read ${buffer.length} bytes`);
    return buffer;
  } catch (error) {
    console.error(`❌ Failed to read file: ${error.message}`);
    throw error;
  }
}

/**
 * Apply color to SVG (simple find-replace for fill attribute)
 */
function applySvgColor(svgBuffer, color) {
  if (!color) return svgBuffer;

  let svgString = svgBuffer.toString();
  const colorHex = color.replace('#', '');

  // Replace fill attributes
  svgString = svgString.replace(/fill="[^"]*"/g, `fill="#${colorHex}"`);
  svgString = svgString.replace(/fill:[^;"]*/g, `fill:#${colorHex}`);

  return Buffer.from(svgString);
}

/**
 * Convert SVG to PNG at multiple sizes
 */
async function convertToPng(svgBuffer, sizes, outputDir, baseName = 'icon', color = null) {
  // Wait for sharp to be loaded
  while (!sharp) {
    await new Promise(resolve => setTimeout(resolve, 100));
  }

  console.log(`🔄 Converting to PNG...`);

  // Create output directory
  await fs.mkdir(outputDir, { recursive: true });

  // Apply color if needed (for local SVGs)
  if (color) {
    svgBuffer = applySvgColor(svgBuffer, color);
  }

  const generatedFiles = [];

  for (const size of sizes) {
    const outputPath = path.join(outputDir, `${baseName}${size}.png`);

    try {
      await sharp(svgBuffer, { density: 300 })
        .resize(size, size, {
          fit: 'contain',
          background: { r: 0, g: 0, b: 0, alpha: 0 }
        })
        .png({ compressionLevel: 9, quality: 100 })
        .toFile(outputPath);

      const stats = await fs.stat(outputPath);
      const sizeKB = (stats.size / 1024).toFixed(1);
      console.log(`✓ Generated ${size}x${size}: ${outputPath} (${sizeKB} KB)`);

      generatedFiles.push({
        size,
        path: outputPath,
        sizeBytes: stats.size
      });
    } catch (error) {
      console.error(`❌ Failed to generate ${size}x${size}: ${error.message}`);
      throw error;
    }
  }

  return generatedFiles;
}

/**
 * Update manifest.json with icon paths
 */
async function updateManifest(manifestPath, iconDir, sizes, baseName = 'icon') {
  console.log(`📝 Updating manifest.json...`);

  let manifest = {};
  let isNew = false;

  try {
    const content = await fs.readFile(manifestPath, 'utf-8');
    manifest = JSON.parse(content);
  } catch (error) {
    if (error.code === 'ENOENT') {
      console.log('ℹ️  manifest.json not found. Creating new one...');
      manifest = {
        manifest_version: 3,
        name: "My Extension",
        version: "1.0.0",
        description: "Chrome extension"
      };
      isNew = true;
    } else {
      console.error(`❌ Failed to read manifest.json: ${error.message}`);
      throw error;
    }
  }

  // Build icons object
  const icons = {};
  for (const size of sizes) {
    const relativePath = path.join(iconDir, `${baseName}${size}.png`).replace(/\\/g, '/');
    icons[size.toString()] = relativePath;
  }

  manifest.icons = icons;

  // Also update action.default_icon if action exists
  if (manifest.action) {
    manifest.action.default_icon = icons;
    console.log('✓ Updated action.default_icon');
  }

  // Write back to file
  await fs.writeFile(
    manifestPath,
    JSON.stringify(manifest, null, 2) + '\n',
    'utf-8'
  );

  console.log(`✓ ${isNew ? 'Created' : 'Updated'}: ${manifestPath}`);

  return manifest;
}

/**
 * Generate icons from Iconify
 */
async function generateFromIconify(options) {
  const {
    icon,
    output = './icons',
    manifest: manifestPath = './manifest.json',
    color = null,
    sizes = DEFAULT_SIZES,
    baseName = 'icon'
  } = options;

  if (!icon) {
    throw new Error('Icon ID is required. Use --icon flag.');
  }

  // Download SVG
  const svgBuffer = await downloadIcon(icon, color);

  // Convert to PNG
  const files = await convertToPng(svgBuffer, sizes, output, baseName, null);

  // Update manifest
  const iconDir = path.relative(path.dirname(manifestPath), output);
  await updateManifest(manifestPath, iconDir, sizes, baseName);

  console.log('\n✅ Icon generation complete!');
  console.log(`   Generated ${files.length} PNG files`);
  console.log(`   Total size: ${(files.reduce((sum, f) => sum + f.sizeBytes, 0) / 1024).toFixed(1)} KB`);

  return files;
}

/**
 * Convert local SVG file
 */
async function convertLocalSvg(options) {
  const {
    input,
    output = './icons',
    manifest: manifestPath = './manifest.json',
    color = null,
    sizes = DEFAULT_SIZES,
    baseName = 'icon'
  } = options;

  if (!input) {
    throw new Error('Input SVG file is required. Use --input flag.');
  }

  // Read local SVG
  const svgBuffer = await readLocalSvg(input);

  // Convert to PNG
  const files = await convertToPng(svgBuffer, sizes, output, baseName, color);

  // Update manifest
  const iconDir = path.relative(path.dirname(manifestPath), output);
  await updateManifest(manifestPath, iconDir, sizes, baseName);

  console.log('\n✅ Conversion complete!');
  console.log(`   Converted ${files.length} PNG files`);
  console.log(`   Total size: ${(files.reduce((sum, f) => sum + f.sizeBytes, 0) / 1024).toFixed(1)} KB`);

  return files;
}

/**
 * Batch generate icons from config file
 */
async function batchGenerate(configPath) {
  console.log(`📋 Reading batch configuration: ${configPath}`);

  const configContent = await fs.readFile(configPath, 'utf-8');
  const config = JSON.parse(configContent);

  if (!config.projects || !Array.isArray(config.projects)) {
    throw new Error('Config file must contain a "projects" array');
  }

  console.log(`\n🚀 Starting batch generation for ${config.projects.length} projects...\n`);

  const results = [];

  for (let i = 0; i < config.projects.length; i++) {
    const project = config.projects[i];
    const projectName = project.name || `Project ${i + 1}`;

    console.log(`\n[${ i + 1}/${config.projects.length}] ${projectName}`);
    console.log('─'.repeat(50));

    try {
      let files;

      if (project.input) {
        // Local SVG conversion
        files = await convertLocalSvg({
          input: project.input,
          output: project.output || './icons',
          manifest: project.manifest,
          color: project.color,
          sizes: project.sizes || DEFAULT_SIZES
        });
      } else if (project.icon) {
        // Iconify download
        files = await generateFromIconify({
          icon: project.icon,
          output: project.output || './icons',
          manifest: project.manifest,
          color: project.color,
          sizes: project.sizes || DEFAULT_SIZES
        });
      } else {
        throw new Error('Project must have either "icon" or "input" property');
      }

      results.push({ project: projectName, status: 'success', files });
    } catch (error) {
      console.error(`❌ Failed: ${error.message}`);
      results.push({ project: projectName, status: 'failed', error: error.message });
    }
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 Batch Generation Summary');
  console.log('='.repeat(50));

  const successful = results.filter(r => r.status === 'success').length;
  const failed = results.filter(r => r.status === 'failed').length;

  console.log(`✓ Successful: ${successful}`);
  console.log(`✗ Failed: ${failed}`);

  if (failed > 0) {
    console.log('\nFailed projects:');
    results.filter(r => r.status === 'failed').forEach(r => {
      console.log(`  - ${r.project}: ${r.error}`);
    });
  }

  return results;
}

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0];

  const options = {};

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.substring(2);
      const value = args[i + 1];

      if (key === 'sizes' && value) {
        options[key] = value.split(',').map(s => parseInt(s.trim()));
        i++;
      } else if (value && !value.startsWith('--')) {
        options[key] = value;
        i++;
      } else {
        options[key] = true;
      }
    } else if (!command) {
      return { command: arg, options };
    }
  }

  return { command, options };
}

/**
 * Display help message
 */
function showHelp() {
  console.log(`
Chrome Extension Icons Generator

USAGE:
  generate-icons.js <command> [options]

COMMANDS:
  search <keyword>                Search for icons on Iconify

  generate                        Generate icons from Iconify
    --icon <id>                   Icon ID (e.g., "mdi:home")
    --output <dir>                Output directory (default: ./icons)
    --manifest <path>             Manifest.json path (default: ./manifest.json)
    --color <hex>                 Custom color (e.g., "#ba3329")
    --sizes <sizes>               Comma-separated sizes (default: 16,32,48,128)

  convert                         Convert local SVG file
    --input <svg>                 Input SVG file path
    --output <dir>                Output directory (default: ./icons)
    --manifest <path>             Manifest.json path (default: ./manifest.json)
    --color <hex>                 Custom color (e.g., "#ba3329")
    --sizes <sizes>               Comma-separated sizes (default: 16,32,48,128)

  batch                           Batch generate from config file
    --config <json>               JSON configuration file path

EXAMPLES:
  # Search for calendar icons
  generate-icons.js search "calendar"

  # Generate icons from Iconify
  generate-icons.js generate --icon "mdi:calendar" --output ./icons

  # Generate with custom color
  generate-icons.js generate --icon "mdi:home" --color "#ff0000"

  # Convert local SVG
  generate-icons.js convert --input ./logo.svg --output ./icons

  # Batch generate
  generate-icons.js batch --config icons-config.json
`);
}

/**
 * Main function
 */
async function main() {
  const { command, options } = parseArgs();

  if (!command || command === 'help' || command === '--help' || command === '-h') {
    showHelp();
    return;
  }

  try {
    switch (command) {
      case 'search': {
        const keyword = options.icon || process.argv[3];
        if (!keyword) {
          console.error('❌ Keyword is required for search');
          process.exit(1);
        }

        const results = await searchIcons(keyword, 20);

        if (results.length > 0) {
          console.log(`\n✨ Found ${results.length} icons:\n`);

          // Show top 5
          results.slice(0, 5).forEach(icon => {
            console.log(`${icon.rank}. ${icon.id}`);
            console.log(`   Preview: ${icon.previewUrl}\n`);
          });

          console.log(`💡 Best match: ${results[0].id}`);
          console.log(`   Use: generate-icons.js generate --icon "${results[0].id}"`);

          if (results.length > 5) {
            console.log(`\n... and ${results.length - 5} more results`);
          }

          console.log(`\n📌 Top 5 alternatives saved for reference`);
        }
        break;
      }

      case 'generate': {
        await generateFromIconify(options);

        // Show cached alternatives if available
        if (searchCache.topResults.length > 0) {
          console.log('\n📌 Top 5 alternatives:');
          searchCache.topResults.forEach(icon => {
            console.log(`   ${icon.rank}. ${icon.id} - ${icon.previewUrl}`);
          });
        }
        break;
      }

      case 'convert': {
        await convertLocalSvg(options);
        break;
      }

      case 'batch': {
        const configPath = options.config;
        if (!configPath) {
          console.error('❌ Config file is required. Use --config flag.');
          process.exit(1);
        }
        await batchGenerate(configPath);
        break;
      }

      default:
        console.error(`❌ Unknown command: ${command}`);
        console.log('   Run "generate-icons.js help" for usage information');
        process.exit(1);
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    if (process.env.DEBUG) {
      console.error(error.stack);
    }
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error(`Fatal error: ${error.message}`);
    process.exit(1);
  });
}

module.exports = {
  searchIcons,
  downloadIcon,
  convertToPng,
  updateManifest,
  generateFromIconify,
  convertLocalSvg,
  batchGenerate
};
