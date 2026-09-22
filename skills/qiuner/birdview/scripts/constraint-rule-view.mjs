import { validateRuleHistory } from './constraint-rule-history.mjs';
export const ruleCategories = [
    { id: 'lifecycle', name: '生命周期' },
    { id: 'interfaces', name: '接口与数据' },
    { id: 'configuration', name: '配置与扩展' },
    { id: 'security', name: '安全边界' },
    { id: 'testing', name: '测试与验证' },
    { id: 'delivery', name: '协作与交付' },
];
// Same role meanings and dark/light tokens as architecture.js / architecture.html.
export const constraintRoles = {
    frontend: { name: '前端', dark: ['#a8d7f3', '#273744', '#557f9e'], light: ['#2169a8', '#e8f3ff', '#3781c5'] },
    backend: { name: '后端', dark: ['#a1e2ce', '#203b37', '#497e70'], light: ['#087a58', '#dff5eb', '#129870'] },
    cache: { name: '缓存', dark: ['#8bddea', '#193c43', '#448e9d'], light: ['#087e93', '#dff6fa', '#1596ad'] },
    database: { name: '数据存储', dark: ['#d1b9f4', '#342d46', '#806aab'], light: ['#763bc8', '#eee6ff', '#8b51de'] },
    queue: { name: '任务与队列', dark: ['#ead096', '#3b3324', '#897243'], light: ['#b06b08', '#fff2da', '#d18a17'] },
    security: { name: '安全', dark: ['#edb7cb', '#3e2c34', '#916276'], light: ['#bf3058', '#ffebf0', '#df4a72'] },
    generic: { name: '通用', dark: ['#c0d6df', '#303b40', '#718892'], light: ['#526780', '#edf0f5', '#7b8ba4'] },
};
export function buildRuleGraph(catalog, sourceHref) {
    if (!Array.isArray(catalog.rules) || !catalog.rules.length || !catalog.ruleReview?.scope) {
        throw new Error('Rule graph requires reviewed rules and ruleReview.scope. Collecting sources is not rule review. Use --sources for an explicit source index.');
    }
    const nodes = [], documents = {};
    const ids = new Set();
    const categories = ruleCategories.filter(category => catalog.rules.some(rule => rule.category === category.id));
    const counts = Object.fromEntries(categories.map(category => [category.id, catalog.rules.filter(rule => rule.category === category.id).length]));
    for (const rule of catalog.rules) {
        if (!Object.hasOwn(constraintRoles, rule.targetRole || 'generic'))
            throw new Error(`Unknown targetRole: ${rule.id}`);
        if (rule.targetRole && rule.targetRole !== 'generic' && !rule.roleReason)
            throw new Error(`Role mapping requires evidence: ${rule.id}`);
    }
    const groupRole = (rules) => {
        const roles = new Set(rules.map(rule => rule.targetRole || 'generic'));
        return roles.size === 1 ? [...roles][0] : 'generic';
    };
    const add = (id, parent, title, desc, body, role, label) => {
        if (!/^[a-z][a-z0-9-]*$/.test(id) || ids.has(id))
            throw new Error(`Invalid or duplicate rule node id: ${id}`);
        ids.add(id);
        nodes.push({ id, parent, title, desc, role, label, kind: 'group' });
        documents[id] = { body };
    };
    const used = new Set(catalog.rules.map(rule => rule.sourcePath));
    const coverage = `已整理 ${catalog.rules.length} 条规则，来自 ${used.size} 份来源。${catalog.ruleReview.scope}。其他来源尚未逐条提炼；这不是整个仓库的合规审计。`;
    add('project', null, catalog.project.name, coverage, `# ${catalog.project.name}\n\n${coverage}\n\n## 怎么阅读\n\n单击展开分类，选择规则阅读详情。编号区分主题；颜色与架构图一致，表示适用角色，不代表通过或失败。跨角色或未明确归属用通用色，混合分组也用通用色。实现核验尚未完成。\n\n## 本轮提炼来源\n\n${[...used].map(file => `- ${file}`).join('\n')}\n\n## 覆盖边界\n\n来源扫描包含 ${catalog.sources.length} 份文件；${catalog.coverage.unresolved.length} 条引用仍需核对。\n\n快照：${catalog.project.revision}`, 'generic', `${catalog.rules.length} 条规则 · ${categories.length} 类`);
    for (const category of categories) {
        const number = String(ruleCategories.indexOf(category) + 1).padStart(2, '0');
        add(`category-${category.id}`, 'project', `${number} ${category.name}`, `${counts[category.id]} 条已提炼规则`, `# ${category.name}\n\n${catalog.rules.filter(rule => rule.category === category.id).map(rule => `- **${rule.name}**：${rule.condition}`).join('\n')}\n\n编号表示主题，颜色表示适用角色；混合分组为通用色。所有实现结果仍未验证。`, groupRole(catalog.rules.filter(rule => rule.category === category.id)), `${counts[category.id]} 条规则`);
    }
    for (const [index, rule] of catalog.rules.entries()) {
        const category = categories.find(item => item.id === rule.category);
        const source = catalog.sources.find(item => item.path === rule.sourcePath);
        if (!category || !source || !rule.name || !rule.explanation || !rule.condition || !rule.verification
            || !Number.isInteger(rule.line) || !Number.isInteger(rule.endLine) || rule.line < 1 || rule.endLine < rule.line
            || rule.endLine > source.text.split(/\r?\n/).length
            || !['applicable', 'conditional', 'superseded', 'conflict', 'uncertain'].includes(rule.applicability))
            throw new Error(`Invalid reviewed rule: ${rule.id}`);
        const quote = source.text.split(/\r?\n/).slice(rule.line - 1, rule.endLine).join('\n');
        const states = { applicable: '适用', conditional: '按条件适用', superseded: '已被替代', conflict: '存在冲突', uncertain: '适用性待确认' };
        const role = rule.targetRole || 'generic';
        const history = rule.history?.status === 'tracked' && validateRuleHistory(rule.history, rule, catalog.project.revision) ? rule.history : undefined;
        const version = history ? `v${history.version}` : '版本未追踪';
        const label = `R${String(index + 1).padStart(3, '0')} · ${version} · ${constraintRoles[role].name}`;
        let parent = `category-${category.id}`;
        if (rule.topic) {
            if (!/^[a-z][a-z0-9-]*$/.test(rule.topic.id) || !rule.topic.name)
                throw new Error('Invalid topic');
            parent = `topic-${category.id}-${rule.topic.id}`;
            if (!ids.has(parent)) {
                const grouped = catalog.rules.filter(item => item.category === rule.category && item.topic?.id === rule.topic.id);
                add(parent, `category-${category.id}`, rule.topic.name, `${grouped.length} 条规则`, `# ${rule.topic.name}\n\n${grouped.map(item => `- **${item.name}**：${item.condition}`).join('\n')}`, groupRole(grouped), `${grouped.length} 条规则`);
            }
        }
        add(rule.id, parent, rule.name, rule.explanation, `# ${rule.name}\n\n## 什么时候用\n\n${rule.condition}\n\n适用性：${states[rule.applicability]}\n\n适用角色：${constraintRoles[role].name}。${rule.roleReason || '跨领域规则或尚无单一角色归属；不推断具体模块所有权。'}\n\n## 具体要求\n\n${rule.explanation}\n\n## 怎么检查\n\n${rule.verification}\n\n**当前核验：未执行实现核验。**\n\n## 来源依据\n\n\`${rule.sourcePath}:${rule.line}-${rule.endLine}\`\n\n${quote.split('\n').map(line => `> ${line}`).join('\n')}\n\n来源文件最后修改：${source.history?.lastEdited || '未知'}。文件历史不作为规则版本。`, role, label);
        const node = nodes.at(-1);
        Object.assign(node, { kind: 'rule', modules: rule.modules || [], ordinal: index + 1, applicability: rule.applicability });
        // Version belongs to this rule's quoted source range, never to its source file as a whole.
        if (history)
            Object.assign(node, { version: history.version, lastEdited: history.lastEdited });
        documents[rule.id].body += history
            ? `\n\n## 规则原文版本\n\nv${history.version} · ${history.lastEdited}\n\n按 Git 原文行段历史计数，不是语义版本，也不是提炼解释的修订次数。移动、格式修改或共同段落可能影响计数。\n\n快照：${history.snapshot}\n\n${history.commits.map(item => `- ${item.commit} · ${item.date}`).join('\n')}`
            : '\n\n## 规则原文版本\n\n版本未追踪。尚无完整且匹配当前快照的规则行段历史。';
    }
    const directoryNodes = [{ ...nodes[0] }];
    const directoryIds = new Map([['.', 'directory-root']]);
    const directoryNode = (directory) => {
        if (directoryIds.has(directory) && directory !== '.')
            return directoryIds.get(directory);
        const id = directoryIds.get(directory) || `directory-${directoryIds.size}`;
        if (directoryNodes.some(node => node.id === id))
            return id;
        directoryIds.set(directory, id);
        const parentPath = directory.includes('/') ? directory.slice(0, directory.lastIndexOf('/')) : '.';
        const parent = directory === '.' ? 'project' : directoryNode(parentPath);
        const local = catalog.sources.filter(source => (source.path.includes('/') ? source.path.slice(0, source.path.lastIndexOf('/')) : '.') === directory);
        const inherited = catalog.sources.filter(source => source.kind === 'instruction' && source.scope != null
            && source.scope !== directory && (source.scope === '.' || directory.startsWith(source.scope + '/')));
        const describe = (sources) => sources.map(source => {
            const rules = catalog.rules.filter(rule => rule.sourcePath === source.path);
            return `- ${source.path} · ${rules.length} 条已整理规则\n${rules.map(rule => `  ${rule.name}：${rule.condition}（${rule.applicability}）`).join('\n')}`;
        }).join('\n') || '无已采集来源 / No collected sources';
        directoryNodes.push({ id, parent, title: directory === '.' ? '/ · 项目根目录' : directory.split('/').at(-1), kind: 'group', role: 'generic', label: directory, desc: '目录来源与上级关系；不自动判定覆盖或合规。' });
        documents[id] = { body: `# ${directory}\n\n## 本目录来源 / Local sources\n\n${describe(local)}\n\n## 上级指令来源 / Ancestor instructions\n\n${describe(inherited)}\n\n## 生效边界 / Applicability boundary\n\n上级指令是继承审查的候选依据，不代表其中每条规则都无条件生效。结合当前工具、任务条件、显式覆盖和冲突审查判断。目录包含关系本身不证明覆盖。Skills 与引用文档按调用和引用关系判断，不以存放目录推断作用域。仅展示已采集来源；没有来源不等于没有约束。\n\n${coverage}` };
        return id;
    };
    for (const [index, source] of catalog.sources.entries()) {
        const directory = source.path.includes('/') ? source.path.slice(0, source.path.lastIndexOf('/')) : '.';
        const id = `directory-source-${index}`;
        const rules = nodes.filter(node => node.kind === 'rule' && catalog.rules[node.ordinal - 1]?.sourcePath === source.path);
        directoryNodes.push({ id, parent: directoryNode(directory), title: source.path.split('/').at(-1), kind: 'group', role: 'generic', label: `${rules.length} 条规则 · ${source.kind || 'reference'}`, desc: source.path });
        documents[id] = { body: `# ${source.path}\n\n类型：${source.kind || 'reference'}\n\n记录作用域：${source.scope ?? '按任务与引用判断'}\n\n来源审查状态：${source.applicability || 'unreviewed'}\n\n${rules.length ? rules.map(rule => `- ${rule.title}`).join('\n') : '尚未提炼规则；不代表不存在约束。'}\n\n## 原文 / Source\n\n${source.text.split('\n').map(line => '> ' + line).join('\n')}` };
        directoryNodes.push(...rules.map(rule => ({ ...rule, parent: id })));
    }
    return { schema: 'birdview.constraint-view/v1', mode: 'rules', title: catalog.project.name,
        revision: catalog.project.revision, scope: coverage, ...(sourceHref ? { sourceHref } : {}), roles: constraintRoles, nodes, directoryNodes, documents };
}
