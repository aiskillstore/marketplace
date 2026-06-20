# User Pattern Summary

- Generated at: `2026-06-15T00:00:00Z`
- Local only: `true`
- Explicit source: `evals/adaptation/user_signals.example.jsonl`
- Records: `8`
- Patterns: `5`
- Discarded signals: `0`

## Privacy Contract

- No implicit private log scan.
- No unredacted raw content stored.
- Scan and proposal stages do not write source files.

## Patterns

### Default language preference

- Pattern: `language_default`
- Support: `2`
- Confidence: `0.79`
- Reason: 2 redacted records matched repeated report-language signals.
- Recommended action: Keep generated reports Chinese-first with an English switch where user-facing.
- Redacted evidence:
  - `line-1`: 新生成的 Skill 报告默认使用中文简体，并在右上角提供英文切换。
  - `line-2`: HTML 报告需要双语能力，但默认内容应该保持中文简体。

### Report UI and visualization preference

- Pattern: `report_ui`
- Support: `5`
- Confidence: `0.95`
- Reason: 5 redacted records matched repeated artifact-design signals.
- Recommended action: Prioritize white-background Kami-style reports with readable charts and stable navigation.
- Redacted evidence:
  - `line-1`: 新生成的 Skill 报告默认使用中文简体，并在右上角提供英文切换。
  - `line-2`: HTML 报告需要双语能力，但默认内容应该保持中文简体。
  - `line-3`: 报告排版采用白底 Kami 风格，图表、模块和导航都要清晰。

### Approval and privacy boundary

- Pattern: `approval_safety`
- Support: `2`
- Confidence: `0.79`
- Reason: 2 redacted records matched repeated governance signals.
- Recommended action: Keep adaptive work proposal-only until a reviewer approves an allowlisted patch path.
- Redacted evidence:
  - `line-5`: 自适应升级必须先生成提案，不能直接自动修改源文件。
  - `line-6`: 用户偏好扫描必须由用户提供明确路径，不要默认扫描私人日志。

### Delivery format preference

- Pattern: `delivery_format`
- Support: `2`
- Confidence: `0.79`
- Reason: 2 redacted records matched repeated artifact-format signals.
- Recommended action: Surface stable artifact paths and formats in CLI output and generated summaries.
- Redacted evidence:
  - `line-2`: HTML 报告需要双语能力，但默认内容应该保持中文简体。
  - `line-6`: 用户偏好扫描必须由用户提供明确路径，不要默认扫描私人日志。

### Evidence and testing preference

- Pattern: `evidence_testing`
- Support: `2`
- Confidence: `0.79`
- Reason: 2 redacted records matched repeated quality-gate signals.
- Recommended action: Attach focused tests and refreshed evidence reports to every non-trivial skill upgrade.
- Redacted evidence:
  - `line-7`: 每次升级都需要测试、覆盖报告和可审计证据，推送前要跑 CI。
  - `line-8`: 涉及 GitHub 推送时，要保留证据链，避免把计划当作完成证明。
