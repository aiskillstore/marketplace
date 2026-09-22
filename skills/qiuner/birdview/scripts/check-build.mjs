import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
// Source: src/check-build.mts. Regenerate scripts/check-build.mjs with npm run build.
const root = fileURLToPath(new URL('../', import.meta.url));
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-build-'));
try {
    const result = spawnSync(process.execPath, [path.join(root, 'node_modules/typescript/bin/tsc'), '--project', path.join(root, 'tsconfig.json'), '--outDir', output], { stdio: 'inherit' });
    if (result.error)
        throw result.error;
    if (result.status !== 0)
        throw new Error('TypeScript build failed.');
    const inventory = JSON.parse(fs.readFileSync(path.join(root, 'build-artifacts.json'), 'utf8'));
    if (!Array.isArray(inventory) || !inventory.every((file) => typeof file === 'string') || new Set(inventory).size !== inventory.length) {
        throw new Error('Invalid generated artifact inventory.');
    }
    const emitted = [];
    for (const file of fs.readdirSync(output, { recursive: true, encoding: 'utf8' })) {
        if (!fs.statSync(path.join(output, file)).isFile())
            continue;
        emitted.push(`scripts/${file.replaceAll('\\', '/')}`);
        const target = path.join(root, 'scripts', file);
        if (!fs.existsSync(target) || fs.readFileSync(target, 'utf8').replace(/\r\n/g, '\n') !== fs.readFileSync(path.join(output, file), 'utf8')) {
            throw new Error(`Generated scripts/${file} is stale. Run npm run build.`);
        }
    }
    for (const file of emitted) {
        if (!inventory.includes(file))
            throw new Error(`Generated ${file} is missing from build-artifacts.json.`);
    }
    const browser = ['scripts/viewer/routing.mjs', 'scripts/viewer/i18n.mjs', 'assets/viewer.js', 'assets/constraint-canvas.js', 'assets/theme.js', 'docs/site.js'];
    const expected = new Set([...emitted, ...browser, 'schemas/activity.schema.json', 'schemas/architecture.schema.json']);
    for (const file of inventory) {
        if (!expected.has(file) || !fs.existsSync(path.join(root, file)))
            throw new Error(`Obsolete or missing generated artifact: ${file}`);
    }
    for (const file of expected) {
        if (!inventory.includes(file))
            throw new Error(`Generated ${file} is missing from build-artifacts.json.`);
    }
    for (const directory of ['scripts', 'assets', 'docs']) {
        for (const file of fs.readdirSync(path.join(root, directory), { recursive: true, encoding: 'utf8' })) {
            const relative = `${directory}/${file.replaceAll('\\', '/')}`;
            if (/\.(?:mjs|cjs|js)$/.test(file) && !inventory.includes(relative))
                throw new Error(`Untracked executable artifact: ${relative}`);
        }
    }
    const schemas = spawnSync(process.execPath, [path.join(root, 'scripts/contracts/export.mjs'), '--check'], { stdio: 'inherit' });
    if (schemas.error)
        throw schemas.error;
    if (schemas.status !== 0)
        throw new Error('Generated schema check failed.');
    console.log('TypeScript output and exchange schemas match distributed artifacts.');
}
catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
}
finally {
    fs.rmSync(output, { recursive: true, force: true });
}
