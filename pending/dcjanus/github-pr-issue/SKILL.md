---
name: github-pr-issue
description: 查看/更新 GitHub Issue、PR（含评论与 diff），并按团队规范非交互创建或修改 PR；涉及 GitHub Issue/PR 的操作时使用。
---

# GitHub CLI Skill（Issue/PR）

## 链接快速查看
- Issue：`gh issue view <url>`。
- PR 详细信息（YAML，推荐）：直接调用脚本 [read_pr.py](scripts/read_pr.py)。
  - 说明：`gh` 没有简单的一条命令可一次性获取多类 PR 信息，因此封装 `read_pr.py` 按需拉取并拼接输出。
  - 建议：查看 PR 时尽量一次性调用该脚本获取所需信息，避免多次调用 `gh` 带来的额外开销。
  - 在当前 `SKILL.md` 所在目录执行：`./scripts/read_pr.py https://github.com/OWNER/REPO/pull/123`
  - 必须直接当作可执行文件执行。
  - 可选参数示例：
    - `--with-diff`：包含 diff。
    - `--with-body`：包含 PR body。
    - `--with-reviews` / `--with-review-comments` / `--with-comments`：按需包含评审/评审评论/评论。
    - `--with-files` / `--with-commits` / `--with-stats`：按需包含文件/提交/统计。
    - `--with-rate-limit`：输出 rate limit 信息（limit/remaining/reset_at）。
    - `--reviews-limit 50` / `--comments-limit 50` / `--review-comments-limit 50`：调整拉取数量。
    - `--files-limit 100` / `--commits-limit 100`：调整文件/提交数量。

## 创建 Issue（非交互）
1. 标题与描述风格同 PR，内容保持简洁清晰。
2. 用 `--body-file` 传多行描述，避免交互式编辑：
   ```bash
   gh issue create --title "feat: short summary" --body-file - <<'EOF'
   # 按上面的格式填充正文
   EOF
   ```
3. Issue 创建成功后，在终端**单独一行**输出 CLI 返回的完整 Issue URL。

## 创建 PR
以下标题与描述规范为默认推荐格式；如与团队/仓库/平台等既有约束冲突，以既有约束为准。若有明确要求（如需中文），则优先遵循。
1. 确认 `git status` 干净，`git push` 到远端。
2. 标题风格：英文、遵循语义化提交规范（如 `feat(scope): short summary`），简洁且描述核心目的；即使标题要求中文，语义化前缀仍需英文。
3. 描述风格：英文、短句和项目符号，优先让不看代码的读者也能理解动机与结果。重点是 what/why/impact 与必要约束，避免流水账与开发过程细节。若上下文不足以明确目标或约束，应主动向开发者确认后再撰写。涉及专有名词、函数名、方法名、类名、API 名称或配置键时，使用 inline code（反引号）包裹以提升可读性与准确性。
4. 期望正文格式（精简但信息完整，按需删减无关块）：
   - `## Summary`：用 1-2 条短句从功能层面概述目的与影响，强调功能变更而非逐条代码变更；跨层（如 Service/DAO）且语义一致的改动应合并为一次功能描述。
   - `## Key changes`：3-5 条要点列出主要变更。
   - `## Constraints / tradeoffs`：若存在约束、限制或非理想选择，简要说明。
   - `## Testing`：验证方式、命令或场景；未测试需注明原因。
   - `## Notes`（可选）：reviewers 关注点、发布注意事项或后续计划。
5. 用非交互式命令创建 PR，正文统一通过 `--body-file` 传入：
   ```bash
   gh pr new --title "feat(scope): short semantic summary" --body-file - <<'EOF'
   # 按上面的格式填充正文
   EOF
   ```
   - 可追加 `--base <branch>`、`--draft` 等参数。
   - 多行正文只能通过 `--body-file` 传入，避免在 `--body` 中写 `\n`。
6. `gh pr edit` 与 `gh pr new` 参数一致，需修改时复用。
7. PR 创建成功后，在终端**单独一行**输出 CLI 返回的完整 PR URL。

## 更新 Issue/PR 标题或描述（前置要求）
在更新 Issue 或 PR 的标题/描述之前，必须先读取当前标题/正文（即将被修改的内容），再进行修改。
