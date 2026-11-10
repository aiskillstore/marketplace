# 现成技能调研

核查日期：2026-11-05。先检索分享站，再读相关技能正文；下表描述本次实际查到的内容，不声称穷尽所有公开技能。没有执行下载到的第三方脚本，也没有直接安装这些候选技能。

## 搜索范围

| 站点/合集 | 实际访问与结果 |
|---|---|
| [skills.sh](https://skills.sh/) | 公开搜索接口检索 `test automation`、`testing strategy`、`windows`、`uia`、`software testing`、`playwright`，每个查询检查返回的前 12 项，再获取重点候选正文 |
| [ClawHub](https://clawhub.ai/skills?q=testing) | 读取 testing 搜索页，可见 Testing Patterns、E2E Testing Patterns、QA & Testing Engine、API 测试等条目；同时含 skills.sh 外部索引 |
| [SkillsMP](https://skillsmp.com/search?q=testing) | 首页和搜索页 HTTP 200，但获取的搜索页停留在客户端 Searching 状态；没有将其算作完整搜索结果 |
| [Skills Directory](https://www.skillsdirectory.com/skills?q=testing) | 原会话已取得首页；续跑查询时 TLS 证书校验失败，未绕过校验，没有声称完成其结果页检索 |
| [VoltAgent awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 核查测试条目，包含 Anthropic、Microsoft、OpenAI、TestMu/LambdaTest 等来源，继续读取相关原始技能 |

搜索接口示例：[skills.sh Windows](https://skills.sh/api/search?q=windows&limit=12)。安装量、星数和榜单是动态发现线索，不是正确性或速度证明。原始获取文件的 SHA-256 和链接见 [sources.json](evidence/sources.json)。

## 重点比较

| 候选 | 有用之处 | 相对本次需求的缺口 |
|---|---|---|
| [Anthropic webapp-testing](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md) | Playwright 网页测试，提供本地服务启动辅助流程 | 面向网页，没有 Windows UIA/Qt/接口的统一选型 |
| [ECC windows-desktop-e2e](https://github.com/affaan-m/ecc/blob/main/skills/windows-desktop-e2e/SKILL.md) | 最接近 Windows 需求；pywinauto/UIA、Qt 注意事项、等待和产物 | 明确排除网页和纯内部测试；不是跨入口选择器。具体 AutomationId 映射应实测，不能直接照搬 |
| [windows-ui-automation](https://skills.sh/martinholovsky/claude-skills-generator/windows-ui-automation) | 可见入口介绍 UIA、Win32、可访问性与进程边界 | 本次读取的是站点可见摘要，未核查其全部 references；不据此宣称完整覆盖 |
| [Anthropic testing-strategy](https://github.com/anthropics/knowledge-work-plugins/blob/main/engineering/skills/testing-strategy/SKILL.md) | 按组件和测试金字塔设计测试计划，正文简洁 | 没有 Windows 控件探测、Pattern 操作或各入口实测 |
| [Jeffallan test-master](https://github.com/Jeffallan/claude-skills/blob/main/skills/test-master/SKILL.md) | 测试策略、断言、覆盖、性能与安全等综合方法 | 更广的 QA 工作流，不能直接替代针对低成本 UI 入口的能力校准 |
| [Microsoft playwright-cli](https://github.com/microsoft/playwright-cli/blob/main/skills/playwright-cli/SKILL.md) | CLI 会话、DOM 定位、批量代码执行、trace 等 | 主要操作浏览器，不覆盖 Windows 原生 UIA 与 Qt 内部行为 |

## 实现取舍

找到相似且可参考的单项技能，但本次核查没有找到同时提供“跨场景入口选择、减少截图点击往返、相应实测脚本和清楚覆盖边界”的现成完整方案。因此实现一个小型统一入口，按需链接本地参考页，而非复制或安装整套第三方测试技能。

技能以能否证明断言为前提，不能为了更快而跳过被测 UI。给出可执行的 UIA 助手，以及 CLI/API、DOM、Qt、图像证据的小型真实校验。其余平台明确标为未实测，不凭常识宣称验证成功。

封装遵循 [OpenAI 的技能结构与渐进披露说明](https://developers.openai.com/codex/skills)。没有添加强制 code review、多轮代理审查、自动发布或全局安装步骤。

当前运行包采用普通目录副本安装，版本和维护边界见 [维护说明](maintenance.md)。本页关于未执行第三方下载脚本或安装候选技能的记录保持为上述核查日期的历史事实。
