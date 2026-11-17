# Security Policy

> 中文版见文末「安全策略（中文）」。

anyviz is a **specification and documentation library** for AI-assisted visualization, not a
runtime service or executable application. It ships Markdown specs, JSON theme
files, a small Python validation script, and example visualizations. As such,
the security surface differs from a typical software package — there is no server,
no user data handling, and no production deployment within this repository.

That said, we take the integrity and safety of what anyviz produces seriously.

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅        |
| < 1.0   | ❌        |

## What to Report

Please report any of the following:

- **Harmful visualization guidance** — recommendations in the specs, guides, or
  templates that could lead to misleading, deceptive, or inaccessible charts
  (e.g. truncated axes presented as a default, colorblind-hostile encodings).
- **Insecure example code** — patterns in `examples/` or adapter docs that, if
  copied into a real project, would introduce a vulnerability (e.g. unsanitized
  data injected into the DOM, unsafe `innerHTML` usage).
- **Dependency concerns** — the examples reference CDN-hosted libraries
  (D3.js, ECharts, Mapbox GL, Three.js) via `<script>` tags. Report pinned
  versions with known CVEs, or integrity/SRI gaps you think we should address.
- **Supply-chain or typosquatting risks** in any referenced package names.

## How to Report

For sensitive reports, **please do not open a public issue.** Email
**yuuzelin@icloud.com** with:

1. A description of the issue and its potential impact
2. The file(s) or template(s) affected
3. Steps to reproduce, or a proof-of-concept where applicable
4. Any suggested remediation

We aim to acknowledge reports within **5 business days** and to provide a
resolution timeline after triage. We will credit reporters in the changelog
unless anonymity is requested.

For non-sensitive documentation errors, a regular issue using the bug-report
template is perfectly fine.

## Scope

Because anyviz does not execute untrusted input or run as a service, the
following are generally **out of scope**: denial-of-service, issues requiring a
compromised local machine, and vulnerabilities in third-party libraries that are
merely referenced (report those upstream, though we welcome a heads-up).

---

## 安全策略（中文）

anyviz 是一个面向 AI 辅助可视化的**规范与文档库**，并非运行时服务或可执行应用。仓库内
仅包含 Markdown 规范、JSON 主题文件、一个小型 Python 校验脚本和示例可视化，因此其
安全范畴与常规软件包不同——没有服务器、不处理用户数据、不在本仓库内进行生产部署。

尽管如此，我们重视 anyviz 产出内容的正确性与安全性，欢迎报告以下问题：

- **有害的可视化建议**：规范、指南或模板中可能导致误导、欺骗或不可访问图表的建议
  （例如把截断坐标轴作为默认、对色盲不友好的编码）。
- **不安全的示例代码**：`examples/` 或适配器文档中的写法，若被复制到真实项目会引入
  漏洞（例如未经清洗的数据注入 DOM、不安全的 `innerHTML` 使用）。
- **依赖问题**：示例通过 `<script>` 引用 CDN 托管的库（D3.js、ECharts、Mapbox GL、
  Three.js）。如发现固定版本存在已知 CVE，或认为应补充完整性校验（SRI），请报告。
- 任何被引用包名中的**供应链或仿冒（typosquatting）风险**。

**报告方式**：涉及敏感问题，请勿公开提交 issue，改为发送邮件至 **yuuzelin@icloud.com**，
说明问题描述与潜在影响、受影响文件、复现步骤及修复建议。我们将在 **5 个工作日**内确认，
并在分类后给出处理时间表。除非要求匿名，否则会在变更日志中致谢报告者。

非敏感的文档错误，使用 bug 报告模板正常提交 issue 即可。
