import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
// Audit the committed source archive, not the current node_modules or dirty files.
const root = fileURLToPath(new URL('../', import.meta.url));
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'birdview-install-'));
function run(command, args, cwd) {
    const result = spawnSync(command, args, { cwd, stdio: 'inherit' });
    if (result.error)
        throw result.error;
    if (result.status !== 0)
        throw new Error(`${command} failed (${result.status}).`);
}
try {
    const npm = process.env.npm_execpath;
    if (!npm)
        throw new Error('Run through npm run check:install.');
    const archive = path.join(temporary, 'source.tar');
    const install = path.join(temporary, 'source');
    const project = path.join(temporary, 'project');
    fs.mkdirSync(install);
    fs.mkdirSync(project);
    run('git', ['archive', '--format=tar', 'HEAD', '-o', archive], root);
    run('tar', ['-xf', archive, '-C', install], temporary);
    for (const file of ['LICENSE', 'THIRD_PARTY_NOTICES', 'SKILL.md']) {
        if (!fs.statSync(path.join(install, file)).isFile())
            throw new Error(`Missing ${file}`);
    }
    run(process.execPath, [npm, 'ci', '--ignore-scripts'], install);
    // Exercise shipped JS before any build, from an unrelated working directory.
    const cli = path.join(install, 'scripts/birdview.mjs');
    run(process.execPath, [cli, 'doctor'], project);
    for (const agent of ['codex', 'claude-code', 'deepseek']) {
        run(process.execPath, [cli, 'setup', '--project', project, '--agent', agent], project);
        run(process.execPath, [cli, 'uninstall', '--project', project, '--agent', agent], project);
    }
    run(process.execPath, [npm, 'run', 'check:build'], install);
    console.log('Committed source archive installs, runs and reproduces distributed artifacts.');
}
finally {
    fs.rmSync(temporary, { recursive: true, force: true });
}
