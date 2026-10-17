---
name: dbs-update
description: 更新官方 dbskill，并保留其他 Skill 与用户存档。用户要求更新、升级、检查 dbskill 版本，或在更新提醒后回复 1 时使用。
---

# dbs-update：更新 dbskill

用户已经明确要求更新 dbskill，或在上一条 dbskill 更新提醒后回复了 `1`。两种情况都直接执行更新，不再做第二次文字确认；宿主若要求 Shell 权限，由用户在宿主的权限窗口中决定。

只有上一条助手回复明确包含 dbskill 更新提醒时，单独回复的 `1` 才代表更新。缺少这段上下文时，不要自行解释数字含义。

## 更新范围

- 只更新官方仓库 `dontbesilent2025/dbskill`。
- 保留用户在 `~/.dbs/` 中的存档、报告和决策记录。
- 不更新用户安装的其他 Skill。
- 清理已下线的官方旧入口时，只处理能确认来自官方的副本；用户改过的或同名的自有 Skill 一律保留。
- 不创建后台任务、定时任务或 Agent Hook。

## 执行步骤

1. 判断 dbskill 的安装渠道。两种渠道可能同时存在，只更新实际检测到的渠道：

   - **Claude Code 插件**：本 Skill 所在路径包含 `/.claude/plugins/`，或 `claude plugin list` 的输出中有以 `@dontbesilent-skills` 结尾的插件。
   - **Skills CLI**：`~/.agents/skills/`、`~/.claude/skills/` 或其他 Agent 的 Skill 目录中存在 `dbs` 等官方 Skill，且它们不在 `/.claude/plugins/` 下。

2. 更新 Claude Code 插件渠道：先刷新 marketplace，再逐个更新 `claude plugin list` 中以 `@dontbesilent-skills` 结尾的插件。

   ```bash
   claude plugin marketplace update dontbesilent-skills
   claude plugin update dbs@dontbesilent-skills
   ```

   用户单独安装过其他插件（例如 `dbs-diagnosis@dontbesilent-skills`）时，对每个插件分别执行 `claude plugin update`。不要为插件用户再执行 Skills CLI 安装，否则会多出一套副本。

3. 更新 Skills CLI 渠道：

   ```bash
   npx -y skills add dontbesilent2025/dbskill -g --all
   ```

   两种渠道都检测不到时，按这个命令更新。

4. 清理已下线的官方旧入口。名单与官方历史版本指纹在本 Skill 的 [references/retired-skills.json](references/retired-skills.json)：

   - **Claude Code 插件渠道**：`claude plugin list` 中以 `@dontbesilent-skills` 结尾、且名称在名单里的插件，逐个执行 `claude plugin uninstall <名称>@dontbesilent-skills`。
   - **本地 Skill 目录**：解析本 Skill 所在目录的绝对路径，运行其中的 `scripts/cleanup_retired_skills.py`（macOS 与 Linux 用 `python3`，Windows 用 `python` 或 `py`）。脚本只移除失效链接和指向官方旧版本的链接；与官方旧版本完全一致的目录移到 `~/.dbs/retired-skills/<时间>/` 备份；其余同名项保留并说明原因。
   - 当前环境没有 Python 时跳过脚本，在回复中列出名单里的名称，请用户自行检查各 Agent 的 Skill 目录。

5. 命令成功后记录本次更新时间，避免当前对话仍加载旧 Skill 时重复提醒：

   ```bash
   mkdir -p "$HOME/.dbs" && date +%s > "$HOME/.dbs/update_check_at"
   ```

6. 根据命令的退出状态确认是否完成。命令成功时告诉用户更新已完成：插件渠道提醒用户运行 `/reload-plugins` 或新建对话；Skills CLI 渠道提醒用户新建一次对话后再使用新能力。

7. 命令失败时，用一句话说明失败原因和下一步需要用户处理的权限或网络问题。不要把完整终端日志直接贴给用户，除非用户要求。

## 回复格式

成功：

> dbskill 已更新完成（{更新的渠道}）。当前对话如果还没有读取到新能力，{插件渠道：运行 `/reload-plugins`；其他渠道：新建一次对话}后即可使用。

清理了旧入口时追加一句：

> 已清理下线的旧入口：{名称与位置}。{有备份时：原文件备份在 `{备份目录}`。}{有保留项时：`{路径}` 与官方版本不一致，已保留。}

没有残留时不提清理。

失败：

> dbskill 没有更新完成：{简短原因}。处理完 {权限或网络问题} 后，再说一次「更新 dbskill」。

## 边界

- 用户只问版本、更新内容或是否需要更新时，先回答问题，不执行命令。
- 用户明确要求检查更新且希望实际同步时，按本 Skill 更新。
- 不使用 `npx skills update`，该命令可能更新用户安装的其他 Skill。

---

完成当前任务后直接结束。用户的请求超出本 Skill 的范围、任务完成后用户的材料里出现明确的后续需求，或用户询问下一步时，用一句话说明还需要哪种能力，不点名其他 Skill；当前环境已经安装 `/dbs` 时，补一句「可以输入 `/dbs`，由它匹配对应的 Skill」。
