# GitHub：源码、标签和 Release

核验：2026-11-07，一手 CLI 文档。GitHub 托管仓库及发行附件；没有通用的 skill ZIP 根层级限制。其他市场需要的包格式仍按各自要求准备。

## 输入与准备

- 读取已有 remote、真实默认分支、仓库可见性、选中的 skill 路径、版本和许可证。`gh auth status` 可检查已有登录；不要读取/打印令牌来排障。
- 核对用户是否授权公开该内容。多技能仓库、私有资源及历史提交的公开范围与单个 ZIP 不同；不能把用户选中的子目录理解为整仓公开授权。
- GitHub 自动提供的 Source code ZIP 是整仓快照。需要独立技能包时，将经过验证的单技能 ZIP 作为 Release 附件。
- 若任务只是本地准备，到包、说明和具体发布计划即可；创建远程仓库、草稿 Release 或 PR 已是远程写入。

## 发布或更新

在已授权范围内提交源码、推送相应提交/标签，并从已核验的提交生成附件。已有 tag/Release 时先比较提交、版本及附件；不 force tag、不覆盖既有发行内容。相同发布若能证实等价，返回现有结果；不同内容使用合适的新版本。

`gh release create` 在标签不存在时可能自动从默认分支创建标签。为固定来源，先确认远端标签存在且正确，再使用 `--verify-tag`。多行说明用 `--notes-file`。命令形状如下，实际值取自本次材料：

```text
gh release create TAG PACKAGE.zip PACKAGE.sha256 PACKAGE.commit.txt --repo OWNER/REPO --verify-tag --notes-file RELEASE_NOTES.md
```

`--draft` 是远端草稿状态，`--prerelease` 是预发行标记；不能把它们当作本地预演或正式公开发行。

## 核验

检查仓库可见性、Release URL、draft/prerelease、tag 指向的提交及预期附件。需要宣称用户可获得本次包时，从该附件入口读取并比对哈希/文件范围，不能只看创建命令退出码。

当前目标若只要求 GitHub，不自动提交到其他市场。后续自动索引与 GitHub 推送分别记录。

来源：[gh release create](https://cli.github.com/manual/gh_release_create)、[gh auth login](https://cli.github.com/manual/gh_auth_login)。状态记录见 [核验与恢复](verification-and-recovery.md)。
