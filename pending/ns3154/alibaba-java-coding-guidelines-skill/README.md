# Alibaba Java Coding Guidelines Skill

这是一个通用 Agent Skill，用于让支持 Agent Skills 规范的 AI 编程工具按《阿里巴巴 Java 开发手册》审查、生成和重构 Java 相关代码。

适用场景包括 Java、Spring、MyBatis、Maven、MySQL、SQL、日志、异常处理、安全校验和数据库建模等代码工作。规则摘要来自官方页面：

https://alibaba.github.io/Alibaba-Java-Coding-Guidelines/

## 目录结构

- `SKILL.md`：skill 入口，包含触发条件、工作流程和使用原则。
- `references/alibaba-java-rules.md`：阿里巴巴 Java 编码规范的中文摘要。
- `skills/alibaba-java-coding-guidelines-skill/`：面向要求 `skills/` 根目录结构的注册表镜像。
- `scripts/validate_skill.py`：Python 校验入口。
- `scripts/validate_skill.mjs`：Node.js 校验入口。
- `scripts/validate_skill.go`：Go 校验入口。
- `tests/test_validators.sh`：一次性验证三种校验入口。
- `agents/openai.yaml`：OpenAI/Codex UI 元数据，可选；Claude Code 等其他工具可以忽略。

## 使用方式

把本目录放到支持 Agent Skills 的工具所使用的 skills 目录中即可。常见示例：

```bash
# Claude Code
~/.claude/skills/alibaba-java-coding-guidelines-skill

# Codex
~/.codex/skills/alibaba-java-coding-guidelines-skill
```

使用时可以显式请求：

```text
使用 alibaba-java-coding-guidelines-skill 审查这次 Java 改动。
```

## 校验

任选一种本地运行时：

```bash
python3 scripts/validate_skill.py
node scripts/validate_skill.mjs
go run scripts/validate_skill.go
```

也可以一次性验证三种入口：

```bash
tests/test_validators.sh
```

## 兼容性说明

本项目不绑定单个应用或运行器。核心能力只依赖 `SKILL.md` 和 `references/`，因此 Claude Code、Codex 以及其他支持 Agent Skills 的工具都可以使用。
