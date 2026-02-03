---
name: discover-skills
description: 当你发现当前可用的技能都不够合适（或用户明确要求你寻找技能）时使用。本技能会基于任务目标和约束，给出一份精简的候选技能清单，帮助你选出最适配当前任务的技能。
---

# Discover Skills

## 你要做什么

当触发本技能后，你只需要完成三步：

1. 从用户的问题中提取任务目标、任务约束，并整理出关键词。
2. 调用 `scripts/discover.py` 脚本，向 SkillRadar 服务查询符合条件的技能。
3. 根据返回的候选结果，展示相关信息给用户，并根据权限自动安装技能，或者在不确定和高风险的情况下与用户确认是否安装。

## 输入

### 任务目标（必选）

* **任务目标**是你希望技能完成的动作或任务。明确表达任务的目标帮助 SkillRadar 理解你的需求。
* 示例：合并文件、提取数据、生成报告、处理图片、创建账户等。

### 任务约束（可选）

* **约束**是对任务目标的限制条件。它决定了在执行任务时可接受的条件范围。
* 示例：
  * 任务必须在本地运行（禁止联网）
  * 需要生成特定格式的输出（如 CSV、JSON）
  * 数据处理过程中需要特定的权限或工具支持

### 关键词（可选）

* 从用户需求中提炼 3～10 个关键词即可。
* 关键词用**逗号分隔**，保持简短、直观。
* 关键词建议覆盖：
  * 任务对象/领域（如：pdf、excel、health、calendar、法律、科研）
  * 关键动作（如：extract、summarize、merge、audit、deploy）
  * 关键格式/工具（如：markdown、csv、sql、api）

### 候选数量（可选）

* 表示希望返回多少条候选结果。
* 若用户未指定，默认用 5 条。

## 脚本执行方式

本技能必须通过自带脚本执行查询。

* **脚本路径**：`scripts/discover.py`（相对于本 SKILL.md 所在目录）
* **执行时的工作目录**：必须先切换到本 skill 所在目录（即包含此 SKILL.md 的目录），再执行脚本
* **调用方式示例**：

```bash
# 先 cd 到本 skill 目录，再执行脚本
cd <本skill所在目录> && python scripts/discover.py --task_goal "合并多个文件" --task_constraints "必须支持 PDF、必须支持批量处理" --keywords "pdf, merge, batch" --max_results 5
```

---

## 输出

服务器返回的候选技能清单包含以下字段：

* **candidates**：候选技能列表（按推荐顺序排列，第一项最推荐）
  * **skillradar_id**：UUIDv4（唯一标识每个候选技能）
  * **name**：技能名称
  * **description**：一句话描述该技能的功能
  * **score**：匹配得分（0-1，越高越匹配）
  * **match_reasons**：匹配原因列表（如"意图匹配: 0.85"、"关键词命中: 摘要, 总结"）
  * **install_url**：技能的安装地址（直接访问该 URL 即可获取技能文件）
* **note**：补充说明（用于提示信息缺失/不确定性/风险点）

**输出 JSON 示例**：

```json
{
  "candidates": [
    {
      "skillradar_id": "52a78db1-00b0-4163-9154-c8236bd0df37",
      "name": "extract-action-items",
      "description": "从会议纪要或聊天记录中提取待办事项、负责人和截止时间。",
      "score": 0.87,
      "match_reasons": ["意图匹配: 0.92", "关键词命中: 会议, 待办"],
      "install_url": "https://cdn.skillradar.quest/skills/extract-action-items/skill.zip?v=1738300000"
    }
  ],
  "note": ""
}
```

### 如何安装技能

`install_url` 指向技能的 ZIP 压缩包地址（如 `https://cdn.skillradar.quest/skills/xxx/skill.zip?v=1738300000`）。

**关于 URL 中的 `?v=` 参数**：这是用于绕过 CDN 缓存的时间戳，确保你下载到的是最新版本。请保留此参数，不要删除。

**安装步骤**：
1. 询问用户要安装到项目级目录（当前工作目录下，如 `./xxx/skills/`）还是全局目录（用户主目录下，如 `~/xxx/skills/`）
2. 根据你自身的工具类型，选择正确的安装路径：
   - **Claude Code**：项目级 `.claude/skills/`，全局 `~/.claude/skills/`
   - **OpenCode**：项目级 `.opencode/skills/`，全局 `~/.config/opencode/skills/`
   - **Codex CLI**：项目级 `.codex/skills/`，全局 `~/.codex/skills/`
   - **Gemini CLI**：项目级 `.gemini/skills/`，全局 `~/.gemini/skills/`
3. 下载 `install_url` 指向的 `skill.zip` 文件（保留完整 URL，包括 `?v=` 参数）
4. 解压 ZIP 文件到对应目录（ZIP 第一层是技能名目录）
5. 删除 ZIP 压缩包
6. 验证文件结构是否正确（应包含 SKILL.md）

**ZIP 内部结构示例**：
```
skill.zip
└── extract-action-items/
    ├── SKILL.md
    ├── scripts/
    │   └── ...
    └── references/
        └── ...
```

---

## 结果判断

向量检索总会返回结果，但返回的技能不一定真的适合用户需求。你需要：

1. 阅读每个候选技能的 `name` 和 `description`，判断它是否真的能解决用户的问题
2. 如果所有候选技能都和用户需求无关，应该诚实告诉用户"没有找到合适的技能"，而不是硬推一个不相关的
3. 如果不确定某个技能是否合适，可以向用户说明情况，让用户自己决定

---

## 错误与异常处理

### 找不到匹配的候选技能

当查询没有返回任何匹配项时，返回空结果：

```json
{
  "candidates": [],
  "note": "未找到匹配的技能，请尝试补充更具体的任务目标或关键词。"
}
```

### 服务不可用

如果无法连接到 SkillRadar 服务，会返回错误信息：

```json
{
  "candidates": [],
  "note": "无法连接到 SkillRadar 服务: <错误原因>"
}
```

### 任务目标不明确

如果任务目标或约束不明确，可以提示用户进一步确认或补充信息。
