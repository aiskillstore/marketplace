# Security Engineer Agent 技能使用指南 (PDF)

本 PDF 文档是 `security-engineer` 技能的完整使用手册，包含技能概述、工作流详解、工具链速查、漏洞速查表、安全编码检查清单、常见陷阱、快速参考命令、报告模板等全部内容。

## 文件位置

`~/security_engineer_agent_guide.pdf`

## 生成方式

该 PDF 由 `script/generate_pdf.py` 脚本自动生成（使用 fpdf2 + Arial Unicode.ttf 字体），通过 `skill_manage(action='write_file', ...)` 保存。

## 文档结构（16页）

1. 封面
2. 目录
3. 第一章：技能概述 — 名称/标签/覆盖9大领域
4. 第二章：触发条件与通用原则
5. 第三章：工作流详解（10个子章节）
6. 第四章：常见漏洞速查表（12种漏洞）
7. 第五章：安全编码检查清单
8. 第六章：常见陷阱与注意事项
9. 第七章：快速参考命令
10. 第八章：安全报告模板
11. 第九章：安全资源参考
12. 第十章：如何使用本技能

## 重新生成

```bash
python3 ~/.hermes/skills/software-engineering/security-engineer/scripts/generate_pdf.py
```
