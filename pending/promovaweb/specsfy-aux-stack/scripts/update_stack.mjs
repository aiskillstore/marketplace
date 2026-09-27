#!/usr/bin/env node
import { existsSync } from "node:fs";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";

const START = "<!-- specsfy:stack:start -->"; const END = "<!-- specsfy:stack:end -->";
const project = resolve(process.argv.includes("--project") ? process.argv[process.argv.indexOf("--project") + 1] : process.cwd());
async function json(path) { try { const data = JSON.parse(await readFile(path, "utf8")); return data && typeof data === "object" ? data : {}; } catch { return {}; } }
const composer = await json(join(project, "composer.json")); const packageJson = await json(join(project, "package.json"));
const rows = [];
const add = (kind, name, source) => { if (!rows.some((row) => row.join("|") === [kind, name, source].join("|"))) rows.push([kind, name, source]); };
const composerPackages = { ...(composer.require ?? {}), ...(composer["require-dev"] ?? {}) };
for (const [dependency, kind, label] of [["laravel/framework", "Framework", "Laravel"], ["php", "Linguagem", "PHP"], ["pestphp/pest", "Testes", "Pest"], ["phpunit/phpunit", "Testes", "PHPUnit"]]) if (dependency in composerPackages) add(kind, label, `\`composer.json\` (\`${dependency}\`)`);
if (Object.keys(composer).length && !rows.some((row) => row[1] === "PHP")) add("Linguagem", "PHP", "`composer.json`");
const packages = { ...(packageJson.dependencies ?? {}), ...(packageJson.devDependencies ?? {}) };
for (const [dependency, kind, label] of [["next", "Framework", "Next.js"], ["astro", "Framework", "Astro"], ["react", "Biblioteca", "React"], ["typescript", "Linguagem", "TypeScript"], ["vitest", "Testes", "Vitest"], ["prisma", "Persistência", "Prisma"], ["@prisma/client", "Persistência", "Prisma Client"], ["drizzle-orm", "Persistência", "Drizzle ORM"]]) if (dependency in packages) add(kind, label, `\`package.json\` (\`${dependency}\`)`);
if (Object.keys(packageJson).length) add("Runtime", "Node.js", "`package.json`");
if (existsSync(join(project, "docker-compose.yml")) || existsSync(join(project, "compose.yaml"))) add("Infraestrutura", "Containers", "arquivo Compose");
const target = join(project, ".specsfy", "STACK.md"); let existing = existsSync(target) ? await readFile(target, "utf8") : "";
const old = existing.includes(START) && existing.includes(END) ? existing.split(START)[1].split(END)[0].split(/\r?\n/).filter((line) => /^\|/.test(line)).map((line) => line.split("|").slice(1, -1).map((cell) => cell.trim())).filter((row) => row.length === 3 && !["Camada", "---"].includes(row[0])) : [];
for (const row of old) add(...row);
const active = rows.length ? rows : [["Framework", "A confirmar", "Nenhum manifest reconhecido"]];
const block = `${START}\n| Camada | Tecnologia | Evidência |\n| --- | --- | --- |\n${active.map((row) => `| ${row.join(" | ")} |`).join("\n")}\n${END}`;
const updated = existing.includes(START) && existing.includes(END) ? `${existing.split(START)[0]}${block}${existing.split(END).slice(1).join(END)}`.trimEnd() + "\n" : `${(existing.trim() || "# Stack do sistema")}\n\n## Inventário detectado\n\n${block}\n`;
if (updated !== existing) { await mkdir(join(project, ".specsfy"), { recursive: true }); await writeFile(target, updated); console.log(target); }
