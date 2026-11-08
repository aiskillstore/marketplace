# 准备发布单元与材料

## 先确定内容边界

读取用户指定的 SKILL.md 和实际被引用的运行文件。优先使用该项目已有校验器，检查名称/描述、相对引用、运行资源和许可声明；结构有效仍不等于行为正确。不要把本指南维护仓库的检查器当成所有其他 skill 的通用规则。

Agent Skills 格式要求一个含 SKILL.md 的目录及 name、description；`metadata.version` 和 license 在通用格式中是可选项。建议发布项目维护可追溯的版本，但 SemVer 是项目约定或具体渠道要求，不能说所有平台一律强制。

确认源码提交、skill 在仓库内的路径及本次版本。使用干净、已验证的提交最便于重现；有未提交改动时保留它们，明确本次选中的内容，不通过 reset/clean 清除用户工作。源文件夹已有版本/许可时沿用；仅缺登录也可以完成本地打包。

## 与新版一致的介绍材料

按 [介绍内容同步](introduction-content.md) 区分包内正文、SKILL.md 的 description、GitHub README、平台简介、详情页概述及翻译/展示副本。准备简介和概述全文，覆盖功能变化、系统支持、运行依赖和真实验证范围；记录来源/ref、拟更新内容、语言及目标入口。已有自定义概述不能只靠新 ZIP、版本号或仓库 push 推定已更新，来源未明时保留待核验。

## GitHub URL 不是同一种输入

| 输入 | 表达的范围 | 仍需核验 |
| --- | --- | --- |
| `https://github.com/OWNER/REPO` | 仓库 | 平台是否扫描全部 skill、仓库是否公开 |
| `https://github.com/OWNER/REPO/tree/REF/PATH` | 指定 ref 的目录 | 平台是否尊重子目录，预览/发现数量是否符合本次范围 |
| raw SKILL.md URL | 单个说明文件 | 平台是否支持；是否会取得 references/scripts 等依赖 |
| Release 附件下载 URL | 一个归档文件 | 这是安装源、投稿输入还是仅下载附件，须按平台区分 |

`skills/<name>/SKILL.md` 是便于维护的布局建议；根目录和其他容器布局也可能合法。不要仅为一站改造整个源码仓库。若平台强制仓库级导入，而用户只授权一个 skill，先准备受控的单技能发布源方案；创建新公开仓库仍属于新的外部范围。

## 两种 ZIP 层级

按目标当前规则选择，并查看解压后的文件清单：

```text
带一个目录：                  直接 skill 根：
example-skill/SKILL.md          SKILL.md
example-skill/references/...    references/...
example-skill/scripts/...       scripts/...
example-skill/LICENSE.md        LICENSE.md
```

平台若会归一化公共目录前缀，以其实际预览后的路径为准。多个技能、外层 README、测试、.git、虚拟环境或整仓源码 ZIP 不会自动变成一个正确的单技能包。按真实运行依赖保留资源，不能只复制 SKILL.md 而丢掉被引用的内容。

下面是 Git 命令模板；用已核验的提交、仓库内路径和新输出文件名替换占位符。先确认输出文件不存在，不覆盖已有发行包：

```text
git -c core.autocrlf=false archive --format=zip --prefix=example-skill/ --output=package.zip COMMIT:skills/example-skill
git -c core.autocrlf=false archive --format=zip --output=package-skillroot.zip COMMIT:skills/example-skill
```

若发布单元在仓库根，只有确定该树全部属于发布内容时才直接归档 COMMIT；否则按核验后的文件清单构建临时发布单元。无 Git 来源时记录所用文件清单和哈希，不能编造提交号。

打开归档检查层级、完整性、路径和内容，计算 SHA-256，并将来源提交/路径和校验值随材料保存。比较的是文件字节与本次来源；ZIP 有时间戳等元数据，不能仅凭文件名认定同一产物。

## 提交前最后核对

材料应能回答：哪个平台/账号、哪个 skill/版本、提交哪个 URL 或包、简介与概述分别采用哪份全文、会公开什么、哪些字段或条款已经确定、成功后如何分别核验版本、下载包和两种文案。缺失的关键选择单独列出；独立可完成的预检、完整文案、分类候选和本地包继续完成。需要用户手动提交时，同时交付可复制文案及已核实的概述处理步骤。

记录结构见 [模板](submission-record.md)，通用格式来源见 [来源页](sources-and-maintenance.md)。
