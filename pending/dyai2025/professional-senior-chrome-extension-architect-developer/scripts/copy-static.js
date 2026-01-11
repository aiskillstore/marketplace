import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, '..');
const dist = path.join(root, 'dist');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function copyFile(source, target) {
  ensureDir(path.dirname(target));
  fs.copyFileSync(source, target);
}

function copyDir(sourceDir, targetDir) {
  ensureDir(targetDir);
  for (const entry of fs.readdirSync(sourceDir)) {
    const source = path.join(sourceDir, entry);
    const target = path.join(targetDir, entry);
    const stat = fs.statSync(source);
    if (stat.isDirectory()) {
      copyDir(source, target);
    } else {
      copyFile(source, target);
    }
  }
}

ensureDir(dist);
copyFile(path.join(root, 'manifest.json'), path.join(dist, 'manifest.json'));
copyFile(path.join(root, 'src', 'ui', 'popup.html'), path.join(dist, 'ui', 'popup.html'));
copyFile(path.join(root, 'src', 'background', 'offscreen.html'), path.join(dist, 'background', 'offscreen.html'));
copyDir(path.join(root, 'assets'), path.join(dist, 'assets'));
