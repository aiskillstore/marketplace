# ClawHub：本地文件夹经官方 CLI 发布

核验：2026-11-07，一手 CLI 与 publishing 文档。

## 先核对发布条件

官方当前说明：发布到 ClawHub 的 skill 以 **MIT-0** 分发，可免费使用、修改和再分发且无需署名；平台不支持付费 skill 或逐技能定价。这是平台内容分发条件，不能与 CLI 程序自身的许可证混淆。

确认用户拥有相应权利并同意该渠道的分发条件。已有 MIT 或其他许可证不等于授权代理自动改成 MIT-0；也不能移除第三方要求保留的声明。条件尚未确定时，继续准备包和其他已授权渠道，将该项决策单独列出。

## 预检与身份

读取当前官方 CLI 的版本和帮助，检查本次 skill 文件夹及 namespace/slug。`clawhub whoami` 可核对已有账号；`clawhub login` 涉及用户登录时再请求必要操作。`--owner` 只能指定当前身份获授权的发布者。

当前标准命令是 `clawhub skill publish <path>`；旧 `clawhub publish <path>` 是兼容别名。示意命令如下，填入本次真实来源与作者版本：

```text
clawhub skill publish SKILL_DIR --version VERSION --dry-run --json
clawhub skill publish SKILL_DIR --version VERSION --json
```

先准备/预演，在明确授权发布且条件满足后才执行上传。`--dry-run` 不上传，但不保证所有服务端检查完成，例如分类 slug 只在实际发布时由注册表校验。没有登录时先完成本地材料，不把远端检查伪报为已做。

不要默认使用 `clawhub sync --all`；它可能批量发布用户未选择的其他 skill。

## 版本与分类

当前 CLI 会为新技能默认 1.0.0、对变更内容默认升一个 patch、跳过未变内容；显式版本即使内容相同也可能触发发布。因此按项目已确定的版本显式传值，先检查既有版本，不能把自动升版当作用户意图。

当前文档给出最多 3 个分类、5 个 topic；只使用支持的分类值。版本已存在或返回结果未知时，查询 owner/slug/版本及内容，再决定下一步，不借自动 bump 重复提交。

## 待审和公开

发布文档明确：新 release 先保留在 pending，完成安全检查前不出现在公共搜索、安装和下载入口中。旧公开版可能继续存在。

用有权限的 owner inspect/状态入口关联本次版本，再核对它在公共读取/下载面的 owner、slug、版本和内容。CLI 退出码 0、接收回执或旧版可安装都不能单独证明目标新版已公开。

来源：[当前 CLI 文档](https://github.com/openclaw/clawhub/blob/main/docs/cli.md)、[发布流程](https://github.com/openclaw/clawhub/blob/main/docs/publishing.md)、[官方 ClawHub skill](https://github.com/openclaw/openclaw/blob/main/skills/clawhub/SKILL.md)。旧示例可能使用兼容命令，以当前官方帮助为准。
