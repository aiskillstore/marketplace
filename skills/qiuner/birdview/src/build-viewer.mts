import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

// Source: src/build-viewer.mts. Regenerate scripts/build-viewer.mjs with npm run build.
const root = fileURLToPath(new URL('../', import.meta.url));
const check = process.argv.slice(2).includes('--check');
try {
  for (const module of ['routing', 'i18n', 'main', 'constraint-canvas', 'theme', 'site'] as const) {
    const format = module === 'routing' || module === 'i18n' ? 'esm' : 'iife';
    const target = module === 'main' ? 'assets/viewer.js' : module === 'constraint-canvas' ? 'assets/constraint-canvas.js' : module === 'theme' ? 'assets/theme.js' : module === 'site' ? 'docs/site.js' : `scripts/viewer/${module}.mjs`;
    const source = module === 'site' ? 'src/site/main.mts' : `src/viewer/${module}.mts`;
    const result = await build({
      absWorkingDir: root,
      entryPoints: [source],
      bundle: true,
      format,
      ...(module === 'constraint-canvas' ? { globalName: 'BirdviewConstraintCanvas' } : {}),
      platform: 'browser',
      target: 'es2022',
      write: false,
      banner: { js: `// Generated from ${source}. Do not edit directly.` },
    });
    const output = result.outputFiles[0];
    if (!output) throw new Error(`No browser output for ${target}.`);
    const file = path.join(root, target);
    if (check) {
      if (!fs.existsSync(file) || fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n') !== output.text) {
        throw new Error(`Generated ${target} is stale. Run npm run build.`);
      }
    } else {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, output.text);
    }
  }
  console.log(check ? 'Browser artifacts match TypeScript sources.' : 'Built browser artifacts.');
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
