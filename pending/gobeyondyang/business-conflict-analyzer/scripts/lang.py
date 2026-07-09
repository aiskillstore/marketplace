#!/usr/bin/env python3
"""
lang.py — i18n: en + zh bilingual support.

Language detection: --lang > pipe JSON > $LANG > locale > en.
"""

from __future__ import annotations

import os
import re
import locale

LANGUAGES = ("en", "zh")

# Centralized deletion prefixes — imported by diff_analyzer and impact_mapper.
# Add new deletion types here; all consumers pick them up automatically.
DELETION_PREFIXES = (
    "field_del:", "method_del:", "class_del:", "annotation_del:",
    "decorator_del:", "interface_del:", "enum_del:", "config_del:",
    "prop_del:",
    "type_del:", "event_del:", "taglib_del:", "include_del:",
)

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "common.files": "files",
        "common.no_change": "No change",

        "diff.summary.no_changes": "No uncommitted changes found",
        "diff.summary.p0": "Found {count} breaking change(s) — immediate impact analysis required",
        "diff.summary.p1": "Found {count} compatible change(s) — impact analysis recommended",
        "diff.summary.p2": "Internal refactor ({count} {files}) — on-demand analysis",

        "diff.reason.file_deleted": "File deleted, may involve interface deprecation",
        "diff.reason.breaking": "Breaking change (API/database contract changed)",
        "diff.reason.ddl": "DDL change",
        "diff.reason.file_change": "{ext} file change",
        "diff.reason.config_change": "Configuration file change",
        "diff.reason.internal_refactor": "Internal refactor",

        "layer.api": "API layer (external interface contract)",
        "layer.api_route": "API layer (route definition)",
        "layer.rpc": "RPC layer (inter-service call contract)",
        "layer.data": "Data layer (serialization/deserialization contract)",
        "layer.data_request": "Data layer (request data contract)",
        "layer.data_response": "Data layer (response data contract)",
        "layer.data_model": "Data layer (data model)",
        "layer.data_form": "Data layer (form contract)",
        "layer.business": "Business logic layer",
        "layer.business_impl": "Business logic implementation",
        "layer.data_access": "Data access layer",
        "layer.common": "Common definition layer",
        "layer.config": "Configuration layer",
        "layer.frontend_component": "Frontend component layer",
        "layer.frontend_logic": "Frontend logic layer",
        "layer.frontend_state": "Frontend state layer",
        "layer.frontend_page": "Frontend page layer",
        "layer.frontend_layout": "Frontend layout layer",
        "layer.type_contract": "Data layer (type contract)",
        "layer.public": "Public definition layer",
        "layer.middleware": "Common layer (middleware)",
        "layer.pipeline": "Common layer (pipeline)",
        "layer.admin": "Admin backend",
        "layer.app_module": "Application module",
        "layer.data_migration": "Data migration layer",
        "layer.app_config": "Application config",
        "layer.decorator": "Common layer (decorator)",
        "layer.guard": "Common layer (guard)",
        "layer.pipe": "Common layer (pipe)",
        "layer.filter": "Common layer (filter)",
        "layer.interceptor": "Common layer (interceptor)",
        "layer.resolver": "Data layer (resolver)",
        "layer.module": "Application module",
        "layer.provider": "Service provider layer",
        "layer.nest": "NestJS module",
        "layer.handler": "API layer (request handler)",
        "layer.transport": "API layer (transport)",
        "layer.delivery": "API layer (transport)",
        "layer.endpoint": "API layer (endpoint)",
        "layer.usecase": "Business logic layer",
        "layer.struct": "Data layer (struct)",
        "layer.ktor": "API layer (Ktor route)",
        "layer.concurrent": "Concurrency layer",
        "layer.test": "Test layer",
        "layer.doc": "Documentation layer",
        "layer.other": "Other",

        "impact.stderr.analysis_done": ">> Impact analysis complete",
        "impact.stderr.overall_level": ">> Overall impact level: {level}",
        "impact.stderr.breaking_count": ">> Breaking changes: {count} location(s)",
        "impact.stderr.data_migration_needed": ">> Data migration: Required (risk: {risk})",
        "impact.stderr.api_version_needed": ">> API version compatibility: Upgrade needed",
        "impact.stderr.frontend_affected": ">> Frontend impact: Needs sync update",

        "impact.refs_found": "Referenced by {count} location(s)",
        "impact.git_history": "Historically changed together: {files}",
        "impact.matched_pattern": "Pattern matched: {name}",
        "impact.pattern_scope": "Scope: {scope}",
        "impact.pattern_cost": "Fix cost: {cost}",

        "impact.recommend.critical": "Requires business confirmation before release — recommends version upgrade process",
        "impact.recommend.major": "Notify stakeholders, include in iteration plan",
        "impact.recommend.minor": "Compatible change, documentation notice suffices",

        "impact.data_migration.detail": "DDL changes involve schema changes — data migration plan required",
        "impact.api_compatibility.suggestion": "Release new API version first (backward compatible), deprecate old version after consumers migrate",

        "report.title": "⚠️ Business Impact Analysis Report",
        "report.section.summary": "Change Summary",
        "report.section.dependency_graph": "Impact Dependency Graph",
        "report.section.change_list": "Change Details",
        "report.section.impact_scope": "Impact Scope",
        "report.section.risk_advice": "Risk Assessment & Recommendation",
        "report.section.decision": "Decision",

        "report.table.risk": "Risk",
        "report.table.type": "Type",
        "report.table.scope": "Scope",
        "report.table.business_impact": "Business Impact",

        "report.risk.critical_label": "🔴 High",
        "report.risk.critical_note": "Downstream compilation failure / runtime error / data loss — must be confirmed by business owner",
        "report.risk.major_label": "🟡 Medium",
        "report.risk.major_note": "Behavior change with backward compatibility — notify relevant parties",
        "report.risk.minor_label": "🟢 Low",
        "report.risk.minor_note": "New capability / internal refactor — auto-handled",
        "report.risk.info_label": "⚪ Info",
        "report.risk.info_note": "No external impact",
        "report.risk.col_header": "Risk",
        "report.advice.content": "**Recommended Action**",

        "report.impact.breaking_title": "Affected Parties (code changes required)",
        "report.impact.major_title": "Affected Parties (confirmation needed)",
        "report.impact.breaking_item": "🔴 **Compile failure**: {location} — {detail}",
        "report.impact.major_item": "🟡 **Behavior change**: {location} — {detail}",
        "report.impact.data_migration_title": "Data Migration",
        "report.impact.data_migration_body": "{icon} **Migration required** — {detail}",
        "report.impact.api_version_title": "API Version Compatibility",
        "report.impact.api_version_body": "🔶 **Version upgrade needed** — {suggestion}",
        "report.impact.frontend_title": "Frontend Impact",
        "report.impact.frontend_body": "🖥️ **Frontend needs sync update** — type definitions in the frontend project reference these changes",
        "report.impact.frontend_and_more": "...and {count} more",
        "report.impact.frontend_list_header": "**Affected files:**",
        "report.impact.no_external": "> No external impact",

        "report.decision.instruction": "Reply with number:",
        "report.decision.accept": "[1] Accept — proceed, auto-fix all impacted consumers",
        "report.decision.reject": "[2] Reject — rollback change",
        "report.decision.modify": "[3] Revise — adjust approach",
        "report.decision.analysis_time": "Analysis time",

        "report.footer": "*🤖 Generated by business-conflict-analyzer Skill*",
        "report.saved_to": "📄 Report saved to: {path}",

        "report.graph.data_migration": "🔄 Data migration<br/><small>Plan required</small>",
        "report.graph.ref_prefix": "Other {count} caller(s)",

        "error.git_diff_failed": "git diff failed: {stderr}",
        "error.pipe_required": "Pipe diff_analyzer.py output via stdin",
        "error.usage_diff": "Usage: python diff_analyzer.py | python impact_mapper.py | python report_generator.py",
        "error.pipe_impact": "Pipe impact_mapper.py output via stdin",
        "error.unknown_format": "Unknown input format. Pipe impact_mapper.py or diff_analyzer.py output.",
        "error.impact_mapper_import": "Cannot auto-import impact_mapper: {error}\nUse: python diff_analyzer.py | python impact_mapper.py | python report_generator.py",

        "guard.block": (
            "P0 breaking changes detected, commit blocked.\n"
            "See the report above or conflict-report.md, then reply with number:\n"
            "[1] Accept / [2] Reject / [3] Revise"
        ),
    },

    "zh": {
        "common.files": "个文件",
        "common.no_change": "无变更",

        "diff.summary.no_changes": "无未提交变更",
        "diff.summary.p0": "发现 {count} 个破坏性变更，需立即分析业务影响",
        "diff.summary.p1": "发现 {count} 个兼容性变更，建议分析业务影响",
        "diff.summary.p2": "内部重构（{count} {files}），可按需分析",

        "diff.reason.file_deleted": "文件删除，可能涉及接口废弃",
        "diff.reason.breaking": "破坏性变更（涉及接口/API/数据库契约变化）",
        "diff.reason.ddl": "DDL 变更",
        "diff.reason.file_change": "{ext} 文件变更",
        "diff.reason.config_change": "配置文件变更",
        "diff.reason.internal_refactor": "内部重构",

        "layer.api": "API 层（对外接口契约）",
        "layer.api_route": "API 层（路由定义）",
        "layer.rpc": "RPC 层（服务间调用契约）",
        "layer.data": "数据层（序列化/反序列化契约）",
        "layer.data_request": "数据层（请求数据契约）",
        "layer.data_response": "数据层（响应数据契约）",
        "layer.data_model": "数据层（数据模型）",
        "layer.data_form": "数据层（表单契约）",
        "layer.business": "业务逻辑层",
        "layer.business_impl": "业务逻辑层",
        "layer.data_access": "数据访问层",
        "layer.common": "公共定义层",
        "layer.config": "配置层",
        "layer.frontend_component": "前端组件层",
        "layer.frontend_logic": "前端逻辑层",
        "layer.frontend_state": "前端状态层",
        "layer.frontend_page": "前端页面层",
        "layer.frontend_layout": "前端布局层",
        "layer.type_contract": "数据层（类型契约）",
        "layer.public": "公共定义层",
        "layer.middleware": "公共层（中间件）",
        "layer.pipeline": "公共层（管道）",
        "layer.admin": "管理后台",
        "layer.app_module": "应用模块",
        "layer.data_migration": "数据迁移层",
        "layer.app_config": "应用配置",
        "layer.decorator": "公共层（装饰器）",
        "layer.guard": "公共层（守卫）",
        "layer.pipe": "公共层（管道）",
        "layer.filter": "公共层（过滤器）",
        "layer.interceptor": "公共层（拦截器）",
        "layer.resolver": "数据层（数据解析）",
        "layer.module": "应用模块",
        "layer.provider": "服务提供层",
        "layer.nest": "NestJS 模块",
        "layer.handler": "API 层（请求处理）",
        "layer.transport": "API 层（传输层）",
        "layer.delivery": "API 层（传输层）",
        "layer.endpoint": "API 层（端点）",
        "layer.usecase": "业务逻辑层",
        "layer.struct": "数据层（结构体）",
        "layer.ktor": "API 层（Ktor 路由）",
        "layer.concurrent": "并发层",
        "layer.test": "测试层",
        "layer.doc": "文档层",
        "layer.other": "其他",

        "impact.stderr.analysis_done": ">> 影响分析完成",
        "impact.stderr.overall_level": ">> 总体影响等级：{level}",
        "impact.stderr.breaking_count": ">> 破坏性变更：{count} 处",
        "impact.stderr.data_migration_needed": ">> 数据迁移：需要（风险：{risk}）",
        "impact.stderr.api_version_needed": ">> API 版本兼容：需要升级",
        "impact.stderr.frontend_affected": ">> 前端影响：需同步更新",

        "impact.refs_found": "被 {count} 处引用",
        "impact.git_history": "曾一起变更：{files}",
        "impact.matched_pattern": "匹配模式：{name}",
        "impact.pattern_scope": "影响范围：{scope}",
        "impact.pattern_cost": "修复代价：{cost}",

        "impact.recommend.critical": "需业务方确认后方可执行，建议走版本升级流程",
        "impact.recommend.major": "需通知相关方，纳入迭代计划",
        "impact.recommend.minor": "兼容变更，文档通知即可",

        "impact.data_migration.detail": "DDL 变更涉及数据结构变化，需评估数据迁移方案",
        "impact.api_compatibility.suggestion": "建议先发布新版 API（兼容旧版），待消费者迁移后再废弃旧版",

        "report.title": "⚠️ 业务影响分析报告",
        "report.section.summary": "变更摘要",
        "report.section.dependency_graph": "影响链路图",
        "report.section.change_list": "变更明细",
        "report.section.impact_scope": "影响范围",
        "report.section.risk_advice": "风险等级与建议",
        "report.section.decision": "决策",

        "report.table.risk": "风险",
        "report.table.type": "类型",
        "report.table.scope": "范围",
        "report.table.business_impact": "业务影响说明",

        "report.risk.critical_label": "🔴 高",
        "report.risk.critical_note": "下游编译失败/运行时异常/数据丢失，必须经业务方确认",
        "report.risk.major_label": "🟡 中",
        "report.risk.major_note": "功能行为变化但兼容，需通知相关方",
        "report.risk.minor_label": "🟢 低",
        "report.risk.minor_note": "新增能力/内部重构，自动处理即可",
        "report.risk.info_label": "⚪ 信息",
        "report.risk.info_note": "无外部影响",
        "report.risk.col_header": "风险",
        "report.advice.content": "**建议操作**",

        "report.impact.breaking_title": "受影响方（需改代码）",
        "report.impact.major_title": "受影响方（需确认）",
        "report.impact.breaking_item": "🔴 **编译失败**：{location} — {detail}",
        "report.impact.major_item": "🟡 **行为变化**：{location} — {detail}",
        "report.impact.data_migration_title": "数据迁移",
        "report.impact.data_migration_body": "{icon} **需要数据迁移** — {detail}",
        "report.impact.api_version_title": "API 版本兼容",
        "report.impact.api_version_body": "🔶 **需要版本升级** — {suggestion}",
        "report.impact.frontend_title": "前端影响",
        "report.impact.frontend_body": "🖥️ **前端需要同步更新** — 前端项目中引用了本次变更的类型定义",
        "report.impact.frontend_and_more": "…等 {count} 个文件",
        "report.impact.frontend_list_header": "**受影响文件:**",
        "report.impact.no_external": "> 无外部影响",

        "report.decision.instruction": "回复数字选择：",
        "report.decision.accept": "[1] 采纳 — 继续执行，自动修复所有受影响引用方",
        "report.decision.reject": "[2] 拒绝 — 回滚变更",
        "report.decision.modify": "[3] 修改建议 — 调整方案",
        "report.decision.analysis_time": "分析时间",

        "report.footer": "*🤖 由 business-conflict-analyzer Skill 自动生成*",
        "report.saved_to": "📄 报告已保存到：{path}",

        "report.graph.data_migration": "🔄 数据迁移<br/><small>需评估方案</small>",
        "report.graph.ref_prefix": "其他 {count} 处调用方",

        "error.git_diff_failed": "git diff 失败：{stderr}",
        "error.pipe_required": "请通过管道传入 diff_analyzer.py 的输出",
        "error.usage_diff": "用法：python diff_analyzer.py | python impact_mapper.py | python report_generator.py",
        "error.pipe_impact": "请通过管道传入 impact_mapper.py 的输出",
        "error.unknown_format": "未知输入格式。请通过管道传入 impact_mapper.py 或 diff_analyzer.py 的输出",
        "error.impact_mapper_import": "无法自动调用 impact_mapper：{error}\n正确用法：python diff_analyzer.py | python impact_mapper.py | python report_generator.py",

        "guard.block": (
            "发现 P0 级别破坏性变更，commit 已被拦截。\n"
            "请查看上方报告或 conflict-report.md，回复数字确认：\n"
            "[1] 采纳 / [2] 拒绝 / [3] 修改建议"
        ),
    },
}

# Applied by report_generator to convert language-agnostic detail/symbol text
# into user-facing business language.
TECH_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "en": [
        # Symbol-level patterns (show examples in change table)
        (r"^field_add:(\S+)", r"New field '\1'"),
        (r"^field_del:(\S+)", r"Field '\1' removed"),
        (r"^method_add:(\S+)", r"New method '\1'"),
        (r"^method_del:(\S+)", r"Method '\1' removed"),
        (r"^class_add:(\S+)", r"New class '\1'"),
        (r"^class_del:(\S+)", r"Class '\1' removed"),
        (r"^interface_add:(\S+)", r"New interface '\1'"),
        (r"^interface_del:(\S+)", r"Interface '\1' removed"),
        (r"^annotation_add:(.+)", r"New annotation: \1"),
        (r"^annotation_del:(.+)", r"Annotation removed: \1"),
        (r"^decorator_add:(.+)", r"New decorator: \1"),
        (r"^decorator_del:(.+)", r"Decorator removed: \1"),
        (r"^config_add:(\S+)", r"New config key: \1"),
        (r"^config_del:(\S+)", r"Config key removed: \1"),
        (r"^enum_add:(\S+)", r"New enum value: \1"),
        (r"^enum_del:(\S+)", r"Enum value removed: \1"),
        (r"^type_add:(\S+)", r"New type: \1"),
        (r"^type_del:(\S+)", r"Type removed: \1"),
        (r"^prop_add:(\S+)", r"New property: \1"),
        (r"^prop_del:(\S+)", r"Property removed: \1"),

        # Detail-level patterns (main business description)
        (r"(?:^|\| )java:\+(\d+)/-(\d+)", r"Java interface changed: +\1/-\2 declarations"),
        (r"(?:^|\| )python:\+(\d+)/-(\d+)", r"Python module changed: +\1/-\2 definitions"),
        (r"(?:^|\| )typescript:\+(\d+)/-(\d+)", r"TypeScript definitions changed: +\1/-\2"),
        (r"(?:^|\| )go:\+(\d+)/-(\d+)", r"Go definitions changed: +\1/-\2"),
        (r"(?:^|\| )vue:\+(\d+)/-(\d+)", r"Vue component changed: +\1/-\2 declarations"),
        (r"(?:^|\| )jsp:\+(\d+)/-(\d+)", r"JSP template changed: +\1/-\2 references"),
        (r"(?:^|\| )xml:\+(\d+)/-(\d+)", r"XML file changed: +\1/-\2 lines"),
        (r"^event_add:(\w[\w-]*)", r"New custom event: '\1'"),
        (r"^event_del:(\w[\w-]*)", r"Custom event removed: '\1'"),
        (r"^taglib_add:(.+)", r"New tag library: \1"),
        (r"^taglib_del:(.+)", r"Tag library removed: \1"),
        (r"^include_add:(.+)", r"New page include: \1"),
        (r"^include_del:(.+)", r"Page include removed: \1"),
        (r"(?:^|\| )sql:(\d+) DDL", r"Database schema: \1 structural change(s)"),
        (r"(?:^|\| )config:(\d+) changes?", r"Configuration changed: \1 item(s)"),
        (r"(?:^|\| )ddl:(.+)", r"Database structure: \1"),
        (r"(?:^|\| )file_del:(.+)", r"File deleted: \1"),
    ],
    "zh": [
        (r"^field_add:(\S+)", r"新增字段：\1"),
        (r"^field_del:(\S+)", r"删除字段：\1"),
        (r"^method_add:(\S+)", r"新增方法：\1"),
        (r"^method_del:(\S+)", r"删除方法：\1"),
        (r"^class_add:(\S+)", r"新增类：\1"),
        (r"^class_del:(\S+)", r"删除类：\1"),
        (r"^interface_add:(\S+)", r"新增接口：\1"),
        (r"^interface_del:(\S+)", r"删除接口：\1"),
        (r"^annotation_add:(.+)", r"新增注解：\1"),
        (r"^annotation_del:(.+)", r"移除注解：\1"),
        (r"^decorator_add:(.+)", r"新增装饰器：\1"),
        (r"^decorator_del:(.+)", r"移除装饰器：\1"),
        (r"^config_add:(\S+)", r"新增配置项：\1"),
        (r"^config_del:(\S+)", r"删除配置项：\1"),
        (r"^enum_add:(\S+)", r"新增枚举值：\1"),
        (r"^enum_del:(\S+)", r"删除枚举值：\1"),
        (r"^type_add:(\S+)", r"新增类型：\1"),
        (r"^type_del:(\S+)", r"删除类型：\1"),
        (r"^prop_add:(\S+)", r"新增属性：\1"),
        (r"^prop_del:(\S+)", r"删除属性：\1"),

        (r"(?:^|\| )java:\+(\d+)/-(\d+)", r"Java 接口变更：+\1/-\2 处声明变化"),
        (r"(?:^|\| )python:\+(\d+)/-(\d+)", r"Python 模块变更：+\1/-\2 处定义变化"),
        (r"(?:^|\| )typescript:\+(\d+)/-(\d+)", r"TypeScript 类型变更：+\1/-\2"),
        (r"(?:^|\| )go:\+(\d+)/-(\d+)", r"Go 类型变更：+\1/-\2"),
        (r"(?:^|\| )vue:\+(\d+)/-(\d+)", r"Vue 组件变更：+\1/-\2 处声明变化"),
        (r"(?:^|\| )jsp:\+(\d+)/-(\d+)", r"JSP 模板变更：+\1/-\2 处引用变化"),
        (r"(?:^|\| )xml:\+(\d+)/-(\d+)", r"XML 文件变更：+\1/-\2 行"),
        (r"^event_add:(\w[\w-]*)", r"新增自定义事件：\1"),
        (r"^event_del:(\w[\w-]*)", r"移除自定义事件：\1"),
        (r"^taglib_add:(.+)", r"新增标签库：\1"),
        (r"^taglib_del:(.+)", r"移除标签库：\1"),
        (r"^include_add:(.+)", r"新增页面包含：\1"),
        (r"^include_del:(.+)", r"移除页面包含：\1"),
        (r"(?:^|\| )sql:(\d+) DDL", r"数据库结构：\1 处 DDL 变更"),
        (r"(?:^|\| )config:(\d+) changes?", r"配置变更：\1 项"),
        (r"(?:^|\| )ddl:(.+)", r"数据库结构变更：\1"),
        (r"(?:^|\| )file_del:(.+)", r"文件删除：\1"),
    ],
}

class Translator:
    """Bilingual translator for the business-conflict-analyzer skill."""

    def __init__(self, lang: str | None = None):
        self.lang = self._detect_lang(lang)

    @staticmethod
    def _detect_lang(override: str | None) -> str:
        if override and override in LANGUAGES:
            return override
        # Check env vars: LC_ALL > LC_MESSAGES > LANG > system locale
        for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
            env = os.environ.get(var, "")
            if env.startswith("zh"):
                return "zh"
            if env.startswith("en"):
                return "en"
        # Fallback to system locale
        # Linux/Mac: locale is "zh_CN.UTF-8" → startswith("zh") works
        # Windows:   locale is "Chinese (Simplified)_China" → need "Chinese" in lc
        try:
            lc = locale.getlocale()[0]
            if lc:
                lc_lower = lc.lower().replace("-", "_")
                if lc_lower.startswith("zh") or "chinese" in lc_lower:
                    return "zh"
                if lc_lower.startswith("en") or "english" in lc_lower:
                    return "en"
        except Exception:
            pass
        return "en"

    def t(self, key: str, **kwargs) -> str:
        """Look up a translated string by dot-notation key."""
        text = STRINGS.get(self.lang, {}).get(key) or STRINGS.get("en", {}).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def tech_to_business(self, text: str) -> str:
        """Translate language-agnostic tech description to business language."""
        patterns = TECH_PATTERNS.get(self.lang, TECH_PATTERNS["en"])
        for pattern, replacement in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def translate_symbol(self, symbol: str) -> str:
        """Translate a language-agnostic symbol (e.g. 'field_add:phone') to human display."""
        return self.tech_to_business(symbol)

    def lang_for_pipe(self) -> str:
        """Return lang identifier for embedding in JSON output."""
        return self.lang

    def risk_display(self, impact: str) -> tuple[str, str]:
        """Get (label, note) for an overall_impact level."""
        key_map = {
            "CRITICAL": "report.risk.critical",
            "MAJOR": "report.risk.major",
            "MINOR": "report.risk.minor",
            "INFO": "report.risk.info",
        }
        prefix = key_map.get(impact, "report.risk.info")
        return self.t(f"{prefix}_label"), self.t(f"{prefix}_note")

