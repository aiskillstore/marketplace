import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');
const assetsDir = path.join(root, 'assets');
const base64Path = path.join(assetsDir, 'icons.base64.json');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function loadIcons() {
  if (!fs.existsSync(base64Path)) {
    throw new Error(`Missing icon base64 definitions at ${base64Path}`);
  }
  const raw = fs.readFileSync(base64Path, 'utf8');
  return JSON.parse(raw);
}

function writeIcon(size, data) {
  const target = path.join(assetsDir, `icon${size}.png`);
  fs.writeFileSync(target, Buffer.from(data, 'base64'));
}

function main() {
  ensureDir(assetsDir);
  const icons = loadIcons();
  const sizes = ['16', '48', '128'];
  for (const size of sizes) {
    const data = icons[size];
    if (!data) {
      throw new Error(`Missing base64 data for icon size ${size}`);
    }
    writeIcon(size, data);
  }
  console.log('Icons generated from base64 definitions.');
}

main();
