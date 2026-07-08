#!/usr/bin/env bun

import { join } from "path";
import { init } from "./commands/init";
import { tree } from "./commands/tree";
import { audit } from "./commands/audit";
import { read } from "./commands/read";
import { createIssue, createPR } from "./commands/create";
import { listIssues, listPRs } from "./commands/list";
import { search } from "./commands/search";

const DOCS_ROOT = join(process.cwd(), "docs");

const HELP = `
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
`;

async function main() {
  const [cmd, arg1, arg2, arg3] = process.argv.slice(2);

  switch (cmd) {
    case "init": await init(DOCS_ROOT); break;
    case "tree": await tree(DOCS_ROOT); break;
    case "audit": await audit(DOCS_ROOT); break;
    case "read": await read(arg1); break;
    case "create":
      if (arg1 === "issue") await createIssue(arg2, arg3);
      else if (arg1 === "pr") await createPR(arg2, arg3);
      else { console.error("Usage: create [issue|pr] <desc> [cat]"); process.exit(1); }
      break;
    case "list":
      if (arg1 === "issues") await listIssues();
      else if (arg1 === "prs") await listPRs();
      else { console.error("Usage: list [issues|prs]"); process.exit(1); }
      break;
    case "status":
      await listIssues();
      console.log();
      await listPRs();
      break;
    case "search": await search(arg1); break;
    default: console.log(HELP);
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
