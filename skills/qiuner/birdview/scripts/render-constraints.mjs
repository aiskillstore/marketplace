import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { isMainModule } from './main-module.mjs';
import { buildRuleGraph } from './constraint-rule-view.mjs';
const assets = fileURLToPath(new URL('../assets/', import.meta.url));
export function buildConstraintGraph(catalog, { view = 'rules', sourceHref } = {}) {
    if (catalog.schema !== 'birdview.constraint-catalog/v1' || !catalog.project?.name || !Array.isArray(catalog.sources)
        || !catalog.coverage || !Array.isArray(catalog.references))
        throw new Error('Invalid constraint catalog');
    if (view === 'rules')
        return buildRuleGraph(catalog, sourceHref);
    if (view !== 'sources')
        throw new Error('Unknown constraint view');
    const nodes = [], documents = {}, ids = new Set();
    const revision = catalog.project.revision;
    const add = (id, parent, title, desc, body, history) => {
        if (ids.has(id) || (parent && !ids.has(parent)))
            throw new Error(`Duplicate id or missing parent: ${id}`);
        ids.add(id);
        nodes.push({ id, parent, title, desc, role: 'generic', kind: 'source',
            label: history?.complete ? 'file v' + history.version : '待审查 / Unreviewed' });
        documents[id] = { body };
    };
    const coverage = catalog.coverage;
    const introduction = '约束来源图 / Constraint source graph。原文章节尚需适用性审查；节点数不是有效规则数。vN 仅表示来源文件的 Git 历史版本数，时间是文件最后修改时间。灰点表示尚未完成语义核验，不代表代码有误。';
    const list = (values) => values.length ? values.map(value => `- ${value}`).join('\n') : '无 / None';
    const coverageBody = `# ${catalog.project.name}\n\n${introduction}\n\n## 采集覆盖 / Coverage\n\n快照：${revision}\n\n采集时间：${coverage.checkedAt}\n\n来源文件：${catalog.sources.length}；章节：${catalog.sources.reduce((n, source) => n + source.sections.length, 0)}\n\n语义审查：${coverage.semanticReview}\n\n## 尚未读取 / Uninspected\n\n${list(coverage.uninspectedPaths)}\n\n## 未解析引用 / Unresolved\n\n${list(coverage.unresolved.map(item => `${item.from} → ${item.target} (${item.reason})`))}\n\n## 排除记录 / Exclusions\n\n${list(coverage.excluded.map(item => `${item.path} (${item.reason})`))}\n\n## 边界 / Limitations\n\n${list(coverage.limitations)}`;
    add('project', null, catalog.project.name, introduction, coverageBody);
    for (const [id, title] of [['instruction', '目录指令'], ['skill', '任务技能'], ['reference', '引用规范']]) {
        add(id, 'project', title, '按实际来源展开；不自动判定生效。', `# ${title}\n\n${introduction}`);
    }
    const paths = new Set(catalog.sources.map(source => source.path));
    if (paths.size !== catalog.sources.length)
        throw new Error('Duplicate source path');
    for (const source of catalog.sources) {
        if (!['instruction', 'skill', 'reference'].includes(source.kind))
            throw new Error('Unknown source kind');
        const scope = source.scope ?? '按任务和引用关系判断 / Conditional';
        let parent = source.kind;
        const folders = source.path.split('/').slice(0, -1);
        for (let index = 0; index < folders.length; index++) {
            const folder = folders.slice(0, index + 1).join('/');
            const id = `folder:${source.kind}:${folder}`;
            if (!ids.has(id))
                add(id, parent, folders[index], folder, `# ${folder}\n\n${introduction}`);
            parent = id;
        }
        add(source.id, parent, path.posix.basename(source.path), `范围：${scope} · 适用性：${source.applicability}`, `# ${source.path}\n\n范围：${scope}\n\n来源于：${source.discoveredFrom || '本地约束入口'}\n\n${introduction}\n\n## 原文 / Source\n\n${source.text}`, source.history);
        const ancestors = [];
        for (const section of source.sections) {
            while (ancestors.length && ancestors.at(-1).level >= section.level)
                ancestors.pop();
            add(section.id, ancestors.at(-1)?.id || source.id, section.title === catalog.project.name ? `文档：${section.title}` : section.title, `${source.path}:${section.line}-${section.endLine} · 待审查 / Unreviewed`, `来源：\`${source.path}:${section.line}-${section.endLine}\`\n\n${introduction}\n\n${section.text}`);
            ancestors.push(section);
        }
    }
    for (const rule of catalog.rules || []) {
        const source = catalog.sources.find(item => item.path === rule.sourcePath);
        if (!source || !rule.id || !rule.name || !rule.explanation || !rule.condition || !rule.verification
            || !Number.isInteger(rule.line) || !Number.isInteger(rule.endLine) || rule.line < 1 || rule.endLine < rule.line
            || rule.endLine > source.text.split(/\r?\n/).length
            || !['applicable', 'conditional', 'superseded', 'conflict', 'uncertain'].includes(rule.applicability))
            throw new Error('Invalid reviewed rule');
        const quote = source.text.split(/\r?\n/).slice(rule.line - 1, rule.endLine).join('\n');
        add(rule.id, source.id, rule.name, rule.condition, `# ${rule.name}\n\n${rule.explanation}\n\n## 适用条件\n\n${rule.condition}\n\n适用性：${rule.applicability}\n\n## 原文\n\n${quote}\n\n## 验证计划\n\n${rule.verification}\n\n尚未验证实现；规则适用性不等于合规结果。`);
    }
    return { schema: 'birdview.constraint-view/v1', mode: 'sources', title: catalog.project.name,
        revision, scope: introduction, nodes, documents };
}
export function renderConstraintCatalog(catalog, _shell, options = {}) {
    const payload = buildConstraintGraph(catalog, options);
    // The optional shell argument is retained for callers; rendering always uses Birdview assets.
    const read = (file) => fs.readFileSync(path.join(assets, file), 'utf8').replace(/\r\n?/g, '\n');
    return read('constraint-page.html')
        .replace('<head>', () => '<head><!--\n' + fs.readFileSync(new URL('../LICENSE', import.meta.url), 'utf8') + '\n-->')
        .replace('/* CONSTRAINT_DATA */', () => JSON.stringify(payload).replace(/</g, '\\u003c'))
        .replace('/* CONSTRAINT_CSS */', () => read('constraint-canvas.css'))
        .replace('/* CONSTRAINT_JS */', () => read('constraint-canvas.js'));
}
if (isMainModule(import.meta.url)) {
    const [input, output, option] = process.argv.slice(2);
    if (!input || !output)
        throw new Error('Usage: node scripts/render-constraints.mjs catalog.json constraints.html');
    if (option && option !== '--sources')
        throw new Error('Only --sources is supported');
    const catalog = JSON.parse(fs.readFileSync(input, 'utf8'));
    const sourceOutput = output.replace(/\.html$/i, '') + '.sources.html';
    const html = renderConstraintCatalog(catalog, undefined, { view: option ? 'sources' : 'rules', sourceHref: path.basename(sourceOutput) });
    fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
    if (!option)
        fs.writeFileSync(sourceOutput, renderConstraintCatalog(catalog, undefined, { view: 'sources' }));
    fs.writeFileSync(output, html);
    console.log(path.resolve(output));
}
