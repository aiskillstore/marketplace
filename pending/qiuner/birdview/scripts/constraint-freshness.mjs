import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { isMainModule } from './main-module.mjs';
import { validate } from './validate.mjs';
// Compare only declared files. Symbols and line numbers locate evidence; they do
// not narrow the comparison or prove that a behavioral contract still holds.
export function inspectConstraintFreshness(map, repository) {
    const validation = validate(map);
    if (!validation.ok)
        throw new Error(JSON.stringify(validation.errors));
    const git = (...args) => {
        const result = spawnSync('git', ['--no-optional-locks', ...args], {
            cwd: repository, encoding: 'utf8', timeout: 15000, windowsHide: true,
            env: { ...process.env, GIT_TERMINAL_PROMPT: '0' }
        });
        if (result.error || result.status !== 0)
            throw new Error('Git inspection unavailable.');
        return result.stdout.trim();
    };
    const root = fs.realpathSync(repository);
    const requestedRoot = fs.statSync(repository);
    const gitRoot = fs.statSync(git('rev-parse', '--show-toplevel'));
    if (!requestedRoot.isDirectory() || requestedRoot.dev !== gitRoot.dev || requestedRoot.ino !== gitRoot.ino) {
        throw new Error('Use the Git repository root.');
    }
    const head = git('rev-parse', '--verify', 'HEAD');
    const report = { checkedAt: new Date().toISOString(), head, rules: {} };
    const cache = new Map();
    for (const rule of map.constraints || []) {
        const result = {
            status: 'unverified', ...(rule.baselineCommit ? { baselineCommit: rule.baselineCommit } : {}), files: []
        };
        report.rules[rule.id] = result;
        if (!rule.baselineCommit) {
            result.reason = 'no-baseline';
            continue;
        }
        try {
            git('cat-file', '-e', `${rule.baselineCommit}^{commit}`);
        }
        catch {
            result.reason = 'unavailable-baseline';
            continue;
        }
        for (const [role, files] of [['source', rule.evidence], ['code', rule.code || []]]) {
            for (const file of files) {
                const key = `${rule.baselineCommit}:${file.path}`;
                if (!cache.has(key)) {
                    let status = 'unverified';
                    const absolute = path.resolve(root, file.path);
                    try {
                        const relative = path.relative(root, fs.realpathSync(absolute));
                        if (!relative.startsWith('..' + path.sep) && !path.isAbsolute(relative) && fs.lstatSync(absolute).isFile()) {
                            const target = `:(literal)${file.path}`;
                            const entry = git('ls-tree', rule.baselineCommit, '--', target);
                            const indexEntry = git('ls-files', '-v', '--', target);
                            if (/^100[0-7]{3} blob /.test(entry) && !/^[a-zS] /.test(indexEntry)) {
                                const working = git('diff', '--no-ext-diff', '--no-textconv', '--ignore-submodules=none', '--name-only', rule.baselineCommit, '--', target);
                                const staged = git('diff', '--cached', '--no-ext-diff', '--no-textconv', '--ignore-submodules=none', '--name-only', rule.baselineCommit, '--', target);
                                status = working || staged ? 'changed' : 'unchanged';
                            }
                        }
                    }
                    catch (error) {
                        status = error instanceof Error && 'code' in error && error.code === 'ENOENT' ? 'missing' : 'unverified';
                    }
                    cache.set(key, status);
                }
                result.files.push({ path: file.path, role, status: cache.get(key) });
            }
        }
        result.status = result.files.some(file => file.status === 'changed' || file.status === 'missing') ? 'changed'
            : result.files.length && result.files.every(file => file.status === 'unchanged') ? 'unchanged' : 'unverified';
    }
    return report;
}
if (isMainModule(import.meta.url)) {
    try {
        const [input, repository, ...extra] = process.argv.slice(2);
        if (!input || !repository || extra.length)
            throw new Error('Usage: node scripts/constraint-freshness.mjs architecture.json repository-root');
        console.log(JSON.stringify(inspectConstraintFreshness(JSON.parse(fs.readFileSync(input, 'utf8')), repository), null, 2));
    }
    catch (error) {
        console.error(error instanceof Error ? error.message : String(error));
        process.exitCode = 1;
    }
}
