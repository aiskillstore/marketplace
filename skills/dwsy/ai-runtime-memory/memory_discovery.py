#!/usr/bin/env python3
"""Memory Discovery and Query Utilities for AI Runtime

- 加载 `.ai-runtime/memory/episodic/index.yml`
- 提供 SQL 风格 (WHERE / ORDER BY / LIMIT) 的事件查询接口
- 提供 table/json 两种格式化输出

依赖：PyYAML（项目中已作为核心依赖使用）
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


@dataclass
class MemoryEvent:
    """单条情景记忆事件的索引信息"""

    id: str
    type: str
    level: str
    timestamp: dt.datetime
    date_bucket: str
    path: Path
    title: str = ""
    tags: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def date(self) -> str:
        """YYYY-MM-DD 字符串，便于 WHERE 子句使用 date 字段。"""

        return self.timestamp.date().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为可 JSON 序列化的字典。"""

        return {
            "id": self.id,
            "type": self.type,
            "level": self.level,
            "timestamp": self.timestamp.isoformat(),
            "date": self.date,
            "date_bucket": self.date_bucket,
            "path": str(self.path),
            "title": self.title,
            "tags": list(self.tags),
            "related": list(self.related),
            "meta": dict(self.meta),
        }


class MemoryDiscovery:
    """Episodic 记忆索引加载与查询"""

    def __init__(self, memory_root: Path) -> None:
        self.memory_root = memory_root
        self.episodic_root = memory_root / "episodic"
        self.index_path = self.episodic_root / "index.yml"
        self.events: List[MemoryEvent] = []
        self.refresh()

    # ------------------------------------------------------------------
    # 加载索引
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """重新加载索引文件。"""

        self.events = self._load_events()

    def _load_events(self) -> List[MemoryEvent]:
        """从 episodic 目录扫描 Markdown 事件文件并解析元信息。"""

        if not self.episodic_root.exists():
            return []

        events: List[MemoryEvent] = []
        for md_path in self.episodic_root.rglob("*.md"):
            event = self._parse_event_file(md_path)
            if event is not None:
                events.append(event)

        return events

    def _parse_event_file(self, path: Path) -> Optional[MemoryEvent]:
        """解析单个事件 Markdown 文件。

        协议：
        - 可选顶部 YAML front matter: `--- ... ---`
        - 正文中可使用:
          - `# 标题` 作为事件标题
          - `## 时间` 下第一行非空文本作为时间
          - `## 标签` 下第一行非空文本作为标签列表
        """

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return None

        lines = text.splitlines()
        front_matter, body_lines = self._parse_front_matter(lines)

        stem = path.stem

        # 基础字段
        id_value = str(front_matter.get("id") or stem)
        type_value = str(front_matter.get("type") or "event")

        # level: 优先 front matter，其次目录结构推断
        level_value = str(front_matter.get("level") or self._infer_level_from_path(path))

        # 标题：优先 front matter.title，其次正文第一个 '# ' 标题
        title = front_matter.get("title") or self._extract_title_from_body(body_lines) or stem

        # 标签：支持 front matter.tags 或 '## 标签' 段
        tags = front_matter.get("tags")
        if isinstance(tags, str):
            tags = [t.strip() for t in re.split(r"[,\s]+", tags) if t.strip()]
        elif isinstance(tags, list):
            tags = [str(t) for t in tags]
        else:
            tags = self._extract_tags_from_body(body_lines)

        # 时间：front matter.timestamp/time → 正文 '## 时间' → 文件名/mtime 兜底
        ts_str = front_matter.get("timestamp") or front_matter.get("time")
        timestamp: Optional[dt.datetime] = None
        if isinstance(ts_str, str):
            timestamp = self._parse_datetime(ts_str)
        if timestamp is None:
            body_time = self._extract_time_from_body(body_lines)
            if body_time:
                timestamp = self._parse_datetime(body_time)
        if timestamp is None:
            timestamp = self._infer_datetime_from_filename_or_mtime(path)

        if timestamp is None:
            # 无法推断时间的事件对查询意义有限，忽略该文件
            return None

        # date_bucket: 优先 front matter.date_bucket，其次目录结构 / 时间推断
        date_bucket = front_matter.get("date_bucket") or self._infer_date_bucket(path, timestamp)

        related = front_matter.get("related") or []
        if isinstance(related, str):
            related = [related]
        elif not isinstance(related, list):
            related = []

        # meta: 保留所有未被提升为显式字段的 front matter 信息
        meta: Dict[str, Any] = dict(front_matter)
        for k in [
            "id",
            "type",
            "level",
            "title",
            "tags",
            "timestamp",
            "time",
            "date_bucket",
            "related",
        ]:
            meta.pop(k, None)

        return MemoryEvent(
            id=id_value,
            type=type_value,
            level=level_value,
            timestamp=timestamp,
            date_bucket=str(date_bucket),
            path=path,
            title=str(title),
            tags=list(tags or []),
            related=list(related),
            meta=meta,
        )

    def _parse_front_matter(self, lines: List[str]):
        """解析 YAML front matter，如果不存在则返回空字典和原始行。"""

        if not lines:
            return {}, []

        if lines[0].strip() != "---":
            return {}, lines

        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_text = "\n".join(lines[1:i])
                try:
                    data = yaml.safe_load(fm_text) or {}
                except Exception:
                    data = {}
                return data, lines[i + 1 :]

        # 未找到结束分隔符，视为无 front matter
        return {}, lines

    @staticmethod
    def _extract_title_from_body(body_lines: List[str]) -> Optional[str]:
        for line in body_lines:
            s = line.strip()
            if s.startswith("# "):
                return s[2:].strip()
        return None

    @staticmethod
    def _extract_time_from_body(body_lines: List[str]) -> Optional[str]:
        for i, line in enumerate(body_lines):
            if line.strip().startswith("## 时间"):
                for j in range(i + 1, len(body_lines)):
                    value = body_lines[j].strip()
                    if value:
                        return value
                break
        return None

    @staticmethod
    def _extract_tags_from_body(body_lines: List[str]) -> List[str]:
        for i, line in enumerate(body_lines):
            if line.strip().startswith("## 标签"):
                for j in range(i + 1, len(body_lines)):
                    raw = body_lines[j].strip()
                    if not raw:
                        continue
                    parts = [p.strip() for p in re.split(r"[,\s]+", raw) if p.strip()]
                    return parts
                break
        return []

    def _infer_level_from_path(self, path: Path) -> str:
        """根据相对路径推断级别: year/month/day/event。"""

        try:
            rel = path.relative_to(self.episodic_root)
        except ValueError:
            return "event"

        parts = rel.parts
        if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
            return "day"
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            return "month"
        if len(parts) >= 1 and parts[0].isdigit():
            return "year"
        return "event"

    def _infer_date_bucket(self, path: Path, ts: dt.datetime) -> str:
        """推断 date_bucket，例如 "2025/11/14"。"""

        try:
            rel = path.relative_to(self.episodic_root)
            parts = rel.parts
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                return f"{parts[0]}/{parts[1]}/{parts[2]}"
        except ValueError:
            pass

        return ts.date().isoformat()

    def _infer_datetime_from_filename_or_mtime(self, path: Path) -> Optional[dt.datetime]:
        """从文件名 (YYYYMMDD-HHMM) 或 mtime 推断时间。"""

        m = re.match(r"(\d{8})-(\d{4})", path.stem)
        if m:
            date_str, hm = m.groups()
            try:
                return dt.datetime.strptime(date_str + hm, "%Y%m%d%H%M")
            except Exception:
                pass

        m2 = re.match(r"(\d{4})(\d{2})(\d{2})", path.stem)
        if m2:
            y, mth, d = m2.groups()
            try:
                return dt.datetime.strptime(f"{y}{mth}{d}", "%Y%m%d")
            except Exception:
                pass

        try:
            return dt.datetime.fromtimestamp(path.stat().st_mtime)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # SQL 风格查询接口
    # ------------------------------------------------------------------
    def query(
        self,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryEvent]:
        """基于 SQL 风格参数查询事件列表。"""

        events: List[MemoryEvent] = list(self.events)

        if where:
            events = list(self._apply_where(events, where))

        if order_by:
            events = self._apply_order_by(events, order_by)

        if offset:
            events = events[offset:]

        if limit is not None:
            events = events[:limit]

        return events

    def _apply_where(
        self, events: Iterable[MemoryEvent], where: str
    ) -> Iterable[MemoryEvent]:
        """简易 WHERE 解析，仅支持 AND，运算符子集。

        支持的形式：
        - field = 'value' / != / >= / <=
        - tags CONTAINS 'tag'
        - 通过 AND 连接多个条件（不支持 OR / 括号）
        """

        conditions = [part.strip() for part in re.split(r"\s+AND\s+", where, flags=re.I) if part.strip()]

        def match(event: MemoryEvent) -> bool:
            for cond in conditions:
                if not self._eval_condition(event, cond):
                    return False
            return True

        return (e for e in events if match(e))

    def _eval_condition(self, event: MemoryEvent, cond: str) -> bool:
        # tags CONTAINS 'tag'
        if re.search(r"\bCONTAINS\b", cond, flags=re.I):
            left, right = re.split(r"\bCONTAINS\b", cond, maxsplit=1, flags=re.I)
            field = left.strip()
            value = self._strip_quotes(right.strip())
            if field.lower() != "tags":
                return False
            return value in (event.tags or [])

        # field op value
        m = re.match(r"^(\w+)\s*(=|!=|>=|<=)\s*(.+)$", cond)
        if not m:
            return False

        field, op, raw_value = m.groups()
        field = field.strip().lower()
        value = self._strip_quotes(raw_value.strip())

        # 取事件属性或 meta 字段
        lhs: Any
        if field == "id":
            lhs = event.id
        elif field == "type":
            lhs = event.type
        elif field == "level":
            lhs = event.level
        elif field == "title":
            lhs = event.title
        elif field == "date":
            lhs = event.date
        elif field == "timestamp":
            lhs = event.timestamp
        else:
            if field in event.meta:
                lhs = event.meta[field]
            else:
                # 未知字段直接返回 False，避免误匹配
                return False

        # 时间 / 日期字段支持 >= <=
        if isinstance(lhs, dt.datetime):
            rhs = self._parse_datetime(value)
            if rhs is None:
                return False
        else:
            rhs = value

        try:
            if op == "=":
                return lhs == rhs
            if op == "!=":
                return lhs != rhs
            if op == ">=":
                return lhs >= rhs
            if op == "<=":
                return lhs <= rhs
        except TypeError:
            return False

        return False

    @staticmethod
    def _strip_quotes(text: str) -> str:
        if (text.startswith("'") and text.endswith("'")) or (
            text.startswith('"') and text.endswith('"')
        ):
            return text[1:-1]
        return text

    @staticmethod
    def _parse_datetime(value: str) -> Optional[dt.datetime]:
        # 支持 "YYYY-MM-DD" 或 ISO8601 字符串
        try:
            if len(value) == 10:
                return dt.datetime.fromisoformat(value + "T00:00:00")
            return dt.datetime.fromisoformat(value)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 格式化输出
    # ------------------------------------------------------------------
    def format_events(
        self,
        events: List[MemoryEvent],
        select: Optional[List[str]] = None,
        format_type: str = "table",
    ) -> str:
        if select is None or not select:
            select = ["id", "timestamp", "title"]

        rows = []
        for ev in events:
            d = ev.to_dict()
            rows.append({field: d.get(field) for field in select})

        if format_type == "json":
            return json.dumps(rows, ensure_ascii=False, indent=2)

        # table 格式
        return self._format_table(rows, select)

    @staticmethod
    def _format_table(rows: List[Dict[str, Any]], headers: List[str]) -> str:
        if not rows:
            return "(no events)"

        # 计算列宽
        widths: Dict[str, int] = {}
        for h in headers:
            widths[h] = max(len(h), *(len(str(row.get(h, ""))) for row in rows))

        def fmt_row(row: Dict[str, Any]) -> str:
            return "  ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers)

        header_line = "  ".join(h.ljust(widths[h]) for h in headers)
        sep_line = "  ".join("-" * widths[h] for h in headers)
        data_lines = [fmt_row(r) for r in rows]

        return "\n".join([header_line, sep_line, *data_lines])
