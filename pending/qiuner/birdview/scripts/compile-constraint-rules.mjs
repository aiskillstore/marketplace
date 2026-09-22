import fs from 'node:fs';
import path from 'node:path';
import { isMainModule } from './main-module.mjs';
import { collectRuleHistory } from './constraint-rule-history.mjs';
export function compileConstraintRules(catalog, selection) {
    if (selection.revision !== catalog.project.revision)
        throw new Error('Rule review and source snapshot differ');
    if (!selection.scope || !Array.isArray(selection.groups))
        throw new Error('Reviewed scope and groups are required');
    const rules = [];
    for (const group of selection.groups) {
        const source = catalog.sources.find(item => item.path === group.sourcePath);
        if (!source)
            throw new Error(`Uncollected source: ${group.sourcePath}`);
        const lines = source.text.split(/\r?\n/);
        for (const authored of group.rules) {
            const matches = lines.map((text, index) => text.includes(authored.anchor) ? index : -1).filter(index => index >= 0);
            if (!authored.anchor || matches.length !== 1)
                throw new Error(`Source anchor must be unique: ${authored.id}`);
            const start = matches[0];
            let end = start;
            while (end + 1 < lines.length && lines[end + 1].trim() && !/^(#{1,6} |[-*+] |\d+[.)] )/.test(lines[end + 1]))
                end++;
            // Source positions are resolved afresh; never carry a stale author's history across snapshots.
            const { anchor, history: _history, ...rule } = authored;
            rules.push({ ...rule, sourcePath: source.path, line: start + 1, endLine: end + 1,
                category: group.category, ...(group.topic ? { topic: group.topic } : {}), applicability: rule.applicability || 'conditional' });
        }
    }
    return { ...catalog, ...(selection.architectureBinding ? { architectureBinding: selection.architectureBinding } : {}), rules, ruleReview: { scope: selection.scope, sourcePaths: [...new Set(rules.map(rule => rule.sourcePath))],
            reviewedAt: new Date().toISOString(), implementationVerification: 'unverified' } };
}
if (isMainModule(import.meta.url)) {
    const [input, selection, output, repository] = process.argv.slice(2);
    if (!input || !selection || !output)
        throw new Error('Usage: node scripts/compile-constraint-rules.mjs catalog.json reviewed-rules.json output.json');
    let result = compileConstraintRules(JSON.parse(fs.readFileSync(input, 'utf8')), JSON.parse(fs.readFileSync(selection, 'utf8')));
    if (repository)
        result = collectRuleHistory(result, repository);
    fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
    console.log(`${result.rules.length} reviewed rules; implementation verification remains unverified.`);
}
