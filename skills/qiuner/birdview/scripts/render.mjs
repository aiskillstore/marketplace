import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { isMainModule } from './main-module.mjs';
import { validate } from './validate.mjs';
import { inspectConstraintFreshness } from './constraint-freshness.mjs';
import { buildConstraintGraph, renderConstraintCatalog } from './render-constraints.mjs';
// Source: src/render.mts. Regenerate scripts/render.mjs with npm run build.
const root = fileURLToPath(new URL('../', import.meta.url));
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8').replace(/\r\n?/g, '\n');
const dataUrl = (file, type) => `data:${type};base64,${fs.readFileSync(path.join(root, file)).toString('base64')}`;
export function renderArchitecture(map, events = [], { simulation = false, repository, constraintCatalog, constraintSourceHref } = {}) {
    const result = validate(map, events);
    if (!result.ok)
        throw new Error(JSON.stringify(result.errors));
    const architecture = map;
    const icons = Object.fromEntries(['sun', 'moon', 'layers', 'database', 'zoom-in', 'zoom-out', 'maximize', 'scan', 'x', 'panel-right', 'panels-top-left', 'code', 'zap', 'list-ordered', 'shield-check', 'box', 'skip-forward', 'columns-2', 'chevron-left', 'chevron-right'].map((name) => [name, read(`node_modules/lucide-static/icons/${name}.svg`)]));
    const brandLogo = dataUrl('assets/brand/logo-192.png', 'image/png');
    const constraintFreshness = repository ? inspectConstraintFreshness(architecture, repository) : undefined;
    let constraintView;
    if (constraintCatalog) {
        const binding = constraintCatalog.architectureBinding;
        if (constraintCatalog.project.name !== architecture.project.name)
            throw new Error('Constraint and architecture project names differ');
        if (binding && (binding.mapId !== architecture.mapId || binding.mapRevision !== architecture.revision || binding.sourceRevision !== constraintCatalog.project.revision))
            throw new Error('Stale architecture binding');
        for (const rule of constraintCatalog.rules) {
            if (rule.modules !== undefined && (!binding || rule.modules.some(id => !architecture.modules.some(module => module.id === id))))
                throw new Error(`Invalid module binding: ${rule.id}`);
        }
        constraintView = { graph: buildConstraintGraph(constraintCatalog, constraintSourceHref ? { sourceHref: constraintSourceHref } : {}), snapshot: constraintCatalog.project.revision,
            scope: constraintCatalog.ruleReview.scope, rules: constraintCatalog.rules.map(({ id, modules = [] }) => ({ id, modules })) };
    }
    const data = JSON.stringify({ map: architecture, icons, events, simulation, brandLogo, constraintFreshness, constraintView }).replace(/</g, '\\u003c');
    return read('assets/architecture.html')
        .replace('/* BIRDVIEW_THEME */', () => read('assets/theme.js'))
        .replace('<head>', () => `<head>\n<!--\n${read('LICENSE')}\n${read('THIRD_PARTY_NOTICES')}\n-->`)
        .replace('/* BIRDVIEW_FAVICON */', () => dataUrl('assets/brand/favicon-32.png', 'image/png'))
        .replace('/* BIRDVIEW_CSS */', () => read('assets/demo.css'))
        .replace('/* BIRDVIEW_DATA */', () => `const DATA = ${data};`)
        .replace('/* BIRDVIEW_JS */', () => read('assets/viewer.js'))
        .replace('/* BIRDVIEW_GUIDE_CSS */', () => read('assets/architecture-guide.css'))
        .replace('/* BIRDVIEW_CONSTRAINTS_CSS */', () => read('assets/architecture-constraints.css') + (constraintView ? `\n${read('assets/constraint-canvas.css')}\n${read('assets/architecture-constraint-view.css')}` : ''));
}
if (isMainModule(import.meta.url)) {
    try {
        const args = process.argv.slice(2);
        let repository;
        let constraintCatalog;
        const constraintsIndex = args.indexOf('--constraints');
        if (constraintsIndex !== -1) {
            const file = args[constraintsIndex + 1];
            if (!file || file.startsWith('--'))
                throw new Error('--constraints requires a reviewed catalog JSON file.');
            constraintCatalog = JSON.parse(fs.readFileSync(file, 'utf8'));
            args.splice(constraintsIndex, 2);
        }
        const repositoryIndex = args.indexOf('--repo');
        if (repositoryIndex !== -1) {
            repository = args[repositoryIndex + 1];
            if (!repository || repository.startsWith('--'))
                throw new Error('--repo requires a Git repository root.');
            args.splice(repositoryIndex, 2);
        }
        const simulation = args.includes('--simulation');
        const [input, output, activity, ...extra] = args.filter(arg => arg !== '--simulation');
        if (!input || !output || extra.length)
            throw new Error('Usage: node scripts/render.mjs architecture.json architecture.html [activity.jsonl] [--simulation] [--repo repository-root] [--constraints reviewed.json]');
        if (path.extname(output).toLowerCase() !== '.html')
            throw new Error('Output must be an .html file.');
        if (path.resolve(input).toLowerCase() === path.resolve(output).toLowerCase())
            throw new Error('Input and output must differ.');
        if (activity && path.resolve(activity).toLowerCase() === path.resolve(output).toLowerCase())
            throw new Error('Activity input and output must differ.');
        const events = activity ? fs.readFileSync(activity, 'utf8').split(/\r?\n/).filter(line => line.trim()).map((line, i) => {
            try {
                return JSON.parse(line);
            }
            catch {
                throw new Error(`Invalid JSON in activity record ${i + 1}.`);
            }
        }) : [];
        const map = JSON.parse(fs.readFileSync(input, 'utf8'));
        const sourceOutput = output.replace(/\.html$/i, '.sources.html');
        const options = { simulation, ...(repository ? { repository } : {}), ...(constraintCatalog ? { constraintCatalog, constraintSourceHref: encodeURIComponent(path.basename(sourceOutput)) } : {}) };
        const html = renderArchitecture(map, events, options);
        fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
        fs.writeFileSync(output, html);
        if (constraintCatalog)
            fs.writeFileSync(sourceOutput, renderConstraintCatalog(constraintCatalog, undefined, { view: 'sources' }));
        console.log(path.resolve(output));
    }
    catch (error) {
        console.error(error instanceof Error ? error.message : String(error));
        process.exitCode = 1;
    }
}
