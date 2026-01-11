import { readdir, stat, readFile, mkdir, writeFile, copyFile } from "fs/promises";
import { join, resolve, dirname } from "path";
import { fileURLToPath } from "url";

// 自动定位当前项目的 docs 目录
const DOCS_ROOT = resolve(process.cwd(), "docs");

// 技能模板目录
const TEMPLATES_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "templates");

// 标准目录结构定义 (Generic Governance)
const REQUIRED_DIRS = [
  "adr",          // 架构决策
  "architecture", // 架构设计
  "issues",       // 任务/问题
  "pr",           // 变更记录
];

async function exists(path: string) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

// 0. Init: 初始化文档结构
async function init() {
  console.log(`📦 Initializing docs at: ${DOCS_ROOT}\n`);

  // 创建 docs 目录
  if (!(await exists(DOCS_ROOT))) {
    await mkdir(DOCS_ROOT, { recursive: true });
    console.log(`✅ Created: ${DOCS_ROOT}`);
  } else {
    console.log(`✅ Exists: ${DOCS_ROOT}`);
  }

  // 创建子目录
  for (const dir of REQUIRED_DIRS) {
    const path = join(DOCS_ROOT, dir);
    if (!(await exists(path))) {
      await mkdir(path, { recursive: true });
      console.log(`✅ Created: ${path}/`);
    } else {
      console.log(`✅ Exists: ${path}/`);
    }
  }

  console.log("\n✨ Documentation structure initialized!");
  console.log("\nNext steps:");
  console.log("  1. Create an issue: cp ~/.pi/agent/skills/workhub/templates/issue-template.md ./docs/issues/yyyymmdd-[描述].md");
  console.log("  2. View structure: bun ~/.pi/agent/skills/workhub/lib.ts tree");
}

// 1. Tree: 列出文档结构
async function tree(dir: string, prefix = "") {
  if (!(await exists(dir))) {
    console.log(`${prefix} (Directory not found)`);
    return;
  }
  const entries = await readdir(dir, { withFileTypes: true });
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    if (entry.name.startsWith(".")) continue; // 忽略隐藏文件

    const isLast = i === entries.length - 1;
    const connector = isLast ? "└── " : "├── ";
    console.log(`${prefix}${connector}${entry.name}`);

    if (entry.isDirectory()) {
      await tree(join(dir, entry.name), prefix + (isLast ? "    " : "│   "));
    }
  }
}

// 2. Audit: 审计目录完整性
async function audit() {
  console.log(`Auditing docs at: ${DOCS_ROOT}\n`);
  let healthy = true;

  if (!(await exists(DOCS_ROOT))) {
    console.error("❌ Critical: 'docs/' directory is missing!");
    process.exit(1);
  }

  for (const dir of REQUIRED_DIRS) {
    const path = join(DOCS_ROOT, dir);
    if (await exists(path)) {
      console.log(`✅ [OK] ${dir}/`);
    } else {
      console.log(`❌ [Missing] ${dir}/  (Recommended for: ${getPurpose(dir)})`);
      healthy = false;
    }
  }

  if (!healthy) {
    console.log("\n⚠️  Documentation structure needs improvement.");
  } else {
    console.log("\n✨ Documentation structure is healthy.");
  }
}

function getPurpose(dir: string) {
  const purposes: Record<string, string> = {
    adr: "Architecture Decision Records",
    architecture: "System design & boundaries",
    issues: "Task tracking (yyyymmdd-[描述].md)",
    pr: "Change logs & rollback plans (yyyymmdd-[描述].md)"
  };
  return purposes[dir] || "Standard documentation";
}

// 3. Read: 读取文件
async function read(target: string) {
  if (!target) {
    console.error("Please specify a filename or keyword.");
    process.exit(1);
  }

  // 简单路径匹配
  const fullPath = join(DOCS_ROOT, target);

  // 尝试直接读取
  if (await exists(fullPath)) {
    const content = await readFile(fullPath, "utf-8");
    console.log(`--- ${target} ---\n`);
    console.log(content);
    return;
  }

  // 如果找不到，尝试模糊搜索文件名
  console.error(`File not found: ${target}`);
  console.log(`\nAvailable files:`);
  await listFiles(DOCS_ROOT, "");
}

async function listFiles(dir: string, relativePath: string) {
  if (!(await exists(dir))) return;

  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;

    const fullPath = join(dir, entry.name);
    const relPath = join(relativePath, entry.name);

    if (entry.isDirectory()) {
      await listFiles(fullPath, relPath);
    } else if (entry.name.endsWith('.md')) {
      console.log(`  - ${relPath}`);
    }
  }
}

// 4. Create Issue: 创建 Issue 文件
async function createIssue(description: string, category?: string) {
  if (!description) {
    console.error("Please provide a description for the issue.");
    console.error("Usage: bun lib.ts create issue <description> [category]");
    process.exit(1);
  }

  // 生成文件名
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const filename = `${date}-${description}.md`;

  // 确定目标目录
  let targetDir = join(DOCS_ROOT, "issues");
  if (category) {
    targetDir = join(targetDir, category);
    if (!(await exists(targetDir))) {
      await mkdir(targetDir, { recursive: true });
      console.log(`✅ Created category directory: ${category}/`);
    }
  }

  const targetPath = join(targetDir, filename);

  // 检查文件是否已存在
  if (await exists(targetPath)) {
    console.error(`❌ Error: File already exists: ${targetPath}`);
    process.exit(1);
  }

  // 复制模板
  const templatePath = join(TEMPLATES_DIR, "issue-template.md");
  await copyFile(templatePath, targetPath);

  console.log(`✅ Created issue: ${targetPath}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Edit the issue file: ${targetPath}`);
  console.log(`  2. Fill in Goal, Phases, Acceptance Criteria`);
  console.log(`  3. Start working on the tasks`);
}

// 5. Create PR: 创建 PR 文件
async function createPR(description: string, category?: string) {
  if (!description) {
    console.error("Please provide a description for the PR.");
    console.error("Usage: bun lib.ts create pr <description> [category]");
    process.exit(1);
  }

  // 生成文件名
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const filename = `${date}-${description}.md`;

  // 确定目标目录
  let targetDir = join(DOCS_ROOT, "pr");
  if (category) {
    targetDir = join(targetDir, category);
    if (!(await exists(targetDir))) {
      await mkdir(targetDir, { recursive: true });
      console.log(`✅ Created category directory: ${category}/`);
    }
  }

  const targetPath = join(targetDir, filename);

  // 检查文件是否已存在
  if (await exists(targetPath)) {
    console.error(`❌ Error: File already exists: ${targetPath}`);
    process.exit(1);
  }

  // 复制模板
  const templatePath = join(TEMPLATES_DIR, "pr-template.md");
  await copyFile(templatePath, targetPath);

  console.log(`✅ Created PR: ${targetPath}`);
  console.log(`\nNext steps:`);
  console.log(`  1. Edit the PR file: ${targetPath}`);
  console.log(`  2. Fill in background, changes, tests, rollback plan`);
  console.log(`  3. Link to related issue`);
}

// 6. List Issues: 列出所有 Issues
async function listIssues() {
  const issuesDir = join(DOCS_ROOT, "issues");

  if (!(await exists(issuesDir))) {
    console.log("No issues directory found.");
    return;
  }

  console.log(`📋 Issues in ${issuesDir}:\n`);

  const issues: { path: string; content: string }[] = [];

  async function collectIssues(dir: string, relativePath: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue;

      const fullPath = join(dir, entry.name);
      const relPath = join(relativePath, entry.name);

      if (entry.isDirectory()) {
        await collectIssues(fullPath, relPath);
      } else if (entry.name.endsWith('.md')) {
        const content = await readFile(fullPath, "utf-8");
        issues.push({ path: relPath, content });
      }
    }
  }

  await collectIssues(issuesDir, "");

  // 提取状态信息
  for (const issue of issues) {
    const statusMatch = issue.content.match(/状态[:：]\s*[📝🚧✅⏸️]/);
    const status = statusMatch ? statusMatch[0] : "📝 待办";
    const titleMatch = issue.content.match(/^# Issue: (.+)$/m);
    const title = titleMatch ? titleMatch[1] : issue.path;

    console.log(`  [${status}] ${title}`);
    console.log(`    → ${issue.path}\n`);
  }

  console.log(`Total: ${issues.length} issue(s)`);
}

// 7. List PRs: 列出所有 PRs
async function listPRs() {
  const prDir = join(DOCS_ROOT, "pr");

  if (!(await exists(prDir))) {
    console.log("No PR directory found.");
    return;
  }

  console.log(`🔀 PRs in ${prDir}:\n`);

  const prs: { path: string; content: string }[] = [];

  async function collectPRs(dir: string, relativePath: string) {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue;

      const fullPath = join(dir, entry.name);
      const relPath = join(relativePath, entry.name);

      if (entry.isDirectory()) {
        await collectPRs(fullPath, relPath);
      } else if (entry.name.endsWith('.md')) {
        const content = await readFile(fullPath, "utf-8");
        prs.push({ path: relPath, content });
      }
    }
  }

  await collectPRs(prDir, "");

  // 提取状态信息
  for (const pr of prs) {
    const statusMatch = pr.content.match(/状态[:：]\s*[📝🚧✅❌]/);
    const status = statusMatch ? statusMatch[0] : "📝 待审查";
    const titleMatch = pr.content.match(/^# (.+)$/m);
    const title = titleMatch ? titleMatch[1] : pr.path;

    console.log(`  [${status}] ${title}`);
    console.log(`    → ${pr.path}\n`);
  }

  console.log(`Total: ${prs.length} PR(s)`);
}

// 8. Status: 查看所有 Issues 状态
async function status() {
  console.log(`📊 Workhub Status Report\n`);
  console.log(`=== Issues ===`);
  await listIssues();
  console.log(`\n=== PRs ===`);
  await listPRs();
}

// 9. Search: 搜索 Issues/PRs
async function search(keyword: string) {
  if (!keyword) {
    console.error("Please provide a search keyword.");
    console.error("Usage: bun lib.ts search <keyword>");
    process.exit(1);
  }

  console.log(`🔍 Searching for "${keyword}"...\n`);

  const results: { type: string; path: string; matches: string[] }[] = [];

  // 搜索 Issues
  const issuesDir = join(DOCS_ROOT, "issues");
  if (await exists(issuesDir)) {
    await searchDirectory(issuesDir, "Issue", keyword, results);
  }

  // 搜索 PRs
  const prDir = join(DOCS_ROOT, "pr");
  if (await exists(prDir)) {
    await searchDirectory(prDir, "PR", keyword, results);
  }

  if (results.length === 0) {
    console.log("No results found.");
  } else {
    console.log(`Found ${results.length} result(s):\n`);
    for (const result of results) {
      console.log(`[${result.type}] ${result.path}`);
      for (const match of result.matches) {
        console.log(`  ${match}`);
      }
      console.log();
    }
  }
}

async function searchDirectory(dir: string, type: string, keyword: string, results: any[]) {
  const entries = await readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;

    const fullPath = join(dir, entry.name);

    if (entry.isDirectory()) {
      await searchDirectory(fullPath, type, keyword, results);
    } else if (entry.name.endsWith('.md')) {
      const content = await readFile(fullPath, "utf-8");
      const relativePath = fullPath.replace(DOCS_ROOT + "/", "");

      // 搜索匹配行
      const lines = content.split('\n');
      const matches: string[] = [];

      for (let i = 0; i < lines.length; i++) {
        if (lines[i].toLowerCase().includes(keyword.toLowerCase())) {
          matches.push(`:${i + 1}: ${lines[i].trim().substring(0, 100)}`);
        }
      }

      if (matches.length > 0) {
        results.push({
          type,
          path: relativePath,
          matches
        });
      }
    }
  }
}

// Main
const args = process.argv.slice(2);
const command = args[0];
const param = args[1];
const param2 = args[2];

switch (command) {
  // 基础命令
  case "init":
    init();
    break;
  case "tree":
    console.log(`📦 Docs Root: ${DOCS_ROOT}`);
    tree(DOCS_ROOT);
    break;
  case "audit":
    audit();
    break;
  case "read":
    read(param);
    break;

  // 创建命令
  case "create":
    if (param === "issue") {
      createIssue(param2, args[3]);
    } else if (param === "pr") {
      createPR(param2, args[3]);
    } else {
      console.error("Usage: bun lib.ts create [issue|pr] <description> [category]");
      process.exit(1);
    }
    break;

  // 列表命令
  case "list":
    if (param === "issues") {
      listIssues();
    } else if (param === "prs") {
      listPRs();
    } else {
      console.error("Usage: bun lib.ts list [issues|prs]");
      process.exit(1);
    }
    break;

  // 状态命令
  case "status":
    status();
    break;

  // 搜索命令
  case "search":
    search(param);
    break;

  default:
    console.log(`
Workhub - Documentation & Task Management

Usage: bun lib.ts <command> [options]

Commands:
  init                    Initialize docs structure
  tree                    Show docs directory tree
  audit                   Audit docs structure
  read <file>             Read a document file

  create issue <desc> [category]  Create a new issue
  create pr <desc> [category]     Create a new PR

  list issues             List all issues
  list prs                List all PRs
  status                  Show overall status (issues + PRs)

  search <keyword>        Search issues and PRs

Examples:
  bun lib.ts init
  bun lib.ts create issue "添加深色模式" 前端
  bun lib.ts create pr "修复登录bug" 后端
  bun lib.ts list issues
  bun lib.ts status
  bun lib.ts search "深色模式"
  bun lib.ts read issues/20250106-添加深色模式.md
    `);
}
