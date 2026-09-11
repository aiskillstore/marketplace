# 三步开始

## 1. 准备数据

准备一张结构清晰的 Excel 或 CSV 业务表，并明确这次汇报要回答什么问题。当前版本每次处理一张表。

## 2. 把文件交给支持本地脚本的 AI 工具

确认该工具能够读取你提供的文件并运行本地 Python。首次使用可直接发送：

> 请用 sheet-to-report 分析这份 Excel，面向业务负责人做月度复盘。说明整体表现、主要变化、机会风险和下一步建议。先生成 HTML；如果需要 PPT，请先给我两页真实风格小样。

影响结论的指标口径不清时，Agent 会再向你确认；用户不需要编写代码或配置 JSON。

## 3. 按需选择产物

- 先生成离线 HTML 数据分析简报，核对结论、数据口径和依据。
- 需要汇报时再生成可编辑标准 PPT。
- 想进一步提升视觉效果时，可选择安装并使用 [SlideViber](https://github.com/tf71991/slideviber-skill) 生成美化版；不安装也能正常使用 HTML 和标准 PPT。

[查看完整案例](https://majichuan.github.io/sheet-to-report/) · [常见问题](FAQ.md) · [安装与环境](INSTALL.md) · [返回中文介绍](README.zh-CN.md)
