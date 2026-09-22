#!/usr/bin/env node
// Source: src/birdview.mts. Regenerate scripts/birdview.mjs with npm run build.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
const start = '<!-- birdview:mode:start -->';
const end = '<!-- birdview:mode:end -->';
try {
    const args = process.argv.slice(2);
    const command = args.shift();
    if (command === 'doctor') {
        if (args.length)
            throw new Error('Usage: birdview doctor');
        // Keep the invocation path: resolving import.meta.url would hide broken
        // entry-point detection in an installation reached through a directory link.
        const entry = process.argv[1];
        if (!entry)
            throw new Error('Cannot determine the installed CLI path.');
        const scripts = path.dirname(path.resolve(entry));
        const example = path.join(scripts, '../examples/architecture.json');
        const checked = spawnSync(process.execPath, [
            ...process.execArgv.filter(arg => arg === '--preserve-symlinks-main'),
            path.join(scripts, 'validate.mjs'), example,
        ], { encoding: 'utf8', timeout: 30000 });
        if (checked.error || checked.status !== 0)
            throw new Error(`Installed validation CLI failed: ${checked.error?.message || checked.stderr.trim() || checked.status}`);
        let report;
        try {
            report = JSON.parse(checked.stdout);
        }
        catch {
            throw new Error('Installed validation CLI returned no valid JSON report.');
        }
        if (!report || typeof report !== 'object' || !('ok' in report) || report.ok !== true ||
            !('modules' in report) || typeof report.modules !== 'number' || report.modules < 1 ||
            !('errors' in report) || !Array.isArray(report.errors) || report.errors.length) {
            throw new Error('Installed validation CLI did not confirm the bundled example.');
        }
        const { renderArchitecture } = await import('./render.mjs');
        const map = JSON.parse(fs.readFileSync(new URL('../examples/architecture.json', import.meta.url), 'utf8'));
        const html = renderArchitecture(map);
        if (!html.includes('<html'))
            throw new Error('Renderer did not produce HTML.');
        console.log('OK: example validation through installed CLI, renderer dependencies and template assets. Agent activation must be checked in a new task.');
    }
    else {
        const usage = 'Usage: birdview mode [auto|on-demand|off] | setup | uninstall [--project <root>] [--agent codex|claude-code|deepseek]';
        if (!command || !['mode', 'setup', 'uninstall'].includes(command))
            throw new Error(usage + '\n       birdview doctor');
        let mode;
        if (command === 'mode' && args[0] && !args[0].startsWith('--'))
            mode = args.shift();
        let root = process.cwd();
        let agent = 'codex';
        const seen = new Set();
        while (args.length) {
            const flag = args.shift();
            const value = args.shift();
            if (!flag || !['--project', '--agent'].includes(flag) || !value || value.startsWith('--') || seen.has(flag))
                throw new Error(usage);
            seen.add(flag);
            if (flag === '--project')
                root = path.resolve(value);
            else
                agent = value;
        }
        if (!['codex', 'claude-code', 'deepseek'].includes(agent) || (mode && !['auto', 'on-demand', 'off'].includes(mode)))
            throw new Error(usage);
        const selectedAgent = agent;
        if (!fs.statSync(root).isDirectory())
            throw new Error('Project root must be a directory.');
        const filename = selectedAgent === 'claude-code' ? 'CLAUDE.md' : 'AGENTS.md';
        const file = path.join(root, filename);
        let info;
        try {
            info = fs.lstatSync(file);
        }
        catch (error) {
            if (!(error instanceof Error) || !('code' in error) || error.code !== 'ENOENT')
                throw error;
        }
        if (info && !info.isFile())
            throw new Error(`${filename} must be a regular file, not a link or directory.`);
        const original = info ? fs.readFileSync(file, 'utf8') : '';
        const starts = original.split(start).length - 1;
        const ends = original.split(end).length - 1;
        const from = original.indexOf(start);
        const to = original.indexOf(end);
        if (starts !== ends || starts > 1 || (starts && to < from))
            throw new Error(`Malformed or duplicate Birdview block; ${filename} was not changed.`);
        const existing = starts ? original.slice(from, to + end.length) : '';
        const current = existing.match(/^Birdview mode: (auto|on-demand|off)\r?$/m)?.[1];
        if (existing && !current)
            throw new Error(`Unrecognized Birdview mode block; ${filename} was not changed.`);
        if (command === 'setup')
            mode = current || 'on-demand';
        if (command === 'uninstall') {
            if (existing)
                fs.writeFileSync(file, original.slice(0, from) + original.slice(to + end.length), 'utf8');
            console.log(`Project rules: removed\n${file}\nInstalled skill files and project artifacts were not removed. Without a project block, an installed skill uses its default mode.`);
            process.exit(0);
        }
        if (!mode) {
            const foundation = existing.includes('Birdview foundation: on') ? 'on' : 'not installed';
            console.log(`${current || 'on-demand'}${current ? '' : ' (default; no project block)'}\n${file}\nFoundation: ${current === 'off' ? 'off' : foundation}\nStatus covers this file only; inherited instructions may differ.`);
        }
        else {
            const eol = original.includes('\r\n') ? '\r\n' : '\n';
            const trigger = mode === 'auto'
                ? 'Use the Birdview skill before every code-changing task, including small edits, and for planning that explicitly analyzes affected modules. Enter the workflow once per task; update activity before each edit group, not each line.'
                : 'Use the Birdview skill only when the user explicitly invokes it through the host skill selector, names Birdview, or asks to see an architecture/change map before editing (for example: 改前先看图). Ordinary coding or feature-planning requests do not activate Birdview.';
            const foundation = fs.readFileSync(new URL('../references/foundation.txt', import.meta.url), 'utf8').trim().split(/\r?\n/);
            const block = mode === 'off' ? [start, 'Birdview mode: off', 'Birdview foundation: off',
                'Do not activate Birdview or apply its foundation rules for this project unless the user explicitly requests it for the current task. Preserve other project instructions.', end].join(eol)
                : [start, `Birdview mode: ${mode}`, 'Birdview foundation: on', ...foundation, trigger,
                    'When active, first inspect existing project maps and report the reusable path or checked locations and why a new map is needed. Follow the skill to validate/reuse the map, preview it, and declare affected modules before editing.',
                    'After displaying the map and concrete change plan, wait for user confirmation before implementation. Preparing map and plan artifacts is allowed beforehand. Reuse confirmation of the same displayed plan; confirm material scope changes. Auto mode is not approval. Honor an explicit task-specific waiver.',
                    'Planning alone does not authorize code edits or fabricated activity. A one-task request overrides this mode for that task without changing this block. If the skill is unavailable, report it rather than claim its workflow ran.',
                    'This is agent guidance, not a filesystem write interceptor. Preserve all instructions outside this managed block.', end].join(eol);
            const updated = existing ? original.slice(0, from) + block + original.slice(to + end.length)
                : original + (original && !original.endsWith('\n') ? eol : '') + (original ? eol : '') + block + eol;
            if (updated !== original)
                fs.writeFileSync(file, updated, 'utf8');
            console.log(`${mode}\n${file}${updated === original ? '\nUnchanged.' : '\nUpdated managed block.'}`);
        }
    }
}
catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
}
