#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation generator module
Convert inspection results into visual reports (HTML/Markdown/JSON format)"""

import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Annotation:
    """Annotate data"""

    start: int
    end: int
    message: str
    suggestion: Optional[str] = None
    severity: str = "warning"
    category: str = "general"
    color: str = "#FFC107"


class AnnotationGenerator:
    """Annotation generator"""

    def __init__(self):
        self.severity_colors = {
            "error": "#FF5252",
            "warning": "#FFC107",
            "info": "#2196F3",
        }

        self.category_icons = {
            "spelling": "🔤",
            "grammar": "📝",
            "punctuation": "📖",
            "style": "✏️",
            "capitalization": "🔠",
            "terminology": "📚",
            "abbreviation": "📎",
            "consistency": "🔗",
            "typo": "❌",
            "format": "📐",
            "general": "⚠️",
        }

        self.severity_styles = {
            "error": {"background": "#FFEBEE", "border": "#FF5252", "icon": "❌"},
            "warning": {"background": "#FFF8E1", "border": "#FFC107", "icon": "⚠️"},
            "info": {"background": "#E3F2FD", "border": "#2196F3", "icon": "ℹ️"},
        }

    def to_html(
        self, text: str, results: Dict, title: str = "Academic Proofreader Report"
    ) -> str:
        """Generate HTML report"""
        issues = results.get("issues", [])
        grouped_issues = self._group_issues(issues)

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 20px;
            background: white;
            margin-top: -30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .summary-card {{
            text-align: center;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .summary-card.total {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .summary-card.error {{
            background: #FFEBEE;
        }}
        
        .summary-card.warning {{
            background: #FFF8E1;
        }}
        
        .summary-card.info {{
            background: #E3F2FD;
        }}
        
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .content {{
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 30px;
            margin-top: 30px;
        }}
        
        @media (max-width: 900px) {{
            .content {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .document-viewer {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .document-header {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            font-weight: 600;
        }}
        
        .document-content {{
            padding: 20px;
            font-family: 'Georgia', serif;
            font-size: 16px;
            line-height: 1.8;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .highlight {{
            padding: 2px 4px;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .highlight:hover {{
            filter: brightness(0.9);
        }}
        
        .highlight.error {{
            background-color: #FFEBEE;
            border-bottom: 2px solid #FF5252;
        }}
        
        .highlight.warning {{
            background-color: #FFF8E1;
            border-bottom: 2px solid #FFC107;
        }}
        
        .highlight.info {{
            background-color: #E3F2FD;
            border-bottom: 2px solid #2196F3;
        }}
        
        .issues-panel {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-height: 700px;
            overflow-y: auto;
        }}
        
        .issues-header {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
            font-weight: 600;
        }}
        
        .issue-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #f0f0f0;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        .issue-item:hover {{
            background-color: #f8f9fa;
        }}
        
        .issue-item:last-child {{
            border-bottom: none;
        }}
        
        .issue-severity {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .issue-severity.error {{
            background: #FFEBEE;
            color: #D32F2F;
        }}
        
        .issue-severity.warning {{
            background: #FFF8E1;
            color: #F57C00;
        }}
        
        .issue-severity.info {{
            background: #E3F2FD;
            color: #1976D2;
        }}
        
        .issue-category {{
            font-size: 0.85em;
            color: #666;
            margin-bottom: 8px;
        }}
        
        .issue-message {{
            font-weight: 500;
            margin-bottom: 5px;
        }}
        
        .issue-suggestion {{
            font-size: 0.9em;
            color: #4CAF50;
            padding: 8px;
            background: #E8F5E9;
            border-radius: 4px;
            margin-top: 8px;
        }}
        
        .issue-location {{
            font-size: 0.8em;
            color: #999;
            margin-top: 8px;
        }}
        
        .category-section {{
            margin-bottom: 20px;
        }}
        
        .category-header {{
            padding: 10px 20px;
            background: #f0f0f0;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .no-issues {{
            padding: 40px;
            text-align: center;
            color: #4CAF50;
        }}
        
        .no-issues .icon {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .legend {{
            display: flex;
            gap: 20px;
            justify-content: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        .legend-color.error {{
            background: #FF5252;
        }}
        
        .legend-color.warning {{
            background: #FFC107;
        }}
        
        .legend-color.info {{
            background: #2196F3;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📋 {title}</h1>
        <p>Automatic inspection report for academic articles</p>
    </header>
    
    <div class="container">
        <div class="summary">
            <div class="summary-card total">
                <div class="number">{len(issues)}</div>
                <div class="label">Total number of problems found</div>
            </div>
            <div class="summary-card error">
                <div class="number">{len([i for i in issues if i["severity"] == "error"])}</div>
                <div class="label">mistake</div>
            </div>
            <div class="summary-card warning">
                <div class="number">{len([i for i in issues if i["severity"] == "warning"])}</div>
                <div class="label">warn</div>
            </div>
            <div class="summary-card info">
                <div class="number">{len([i for i in issues if i["severity"] == "info"])}</div>
                <div class="label">suggestion</div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color error"></div>
                <span>mistake (Need to modify)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color warning"></div>
                <span>warn (English)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color info"></div>
                <span>suggestion (Optional modifications)</span>
            </div>
        </div>
        
        <div class="content">
            <div class="document-viewer">
                <div class="document-header">📄 Document content (Click on the issue to locate it)</div>
                <div class="document-content" id="document-content">
                    {self._highlight_text(text, issues)}
                </div>
            </div>
            
            <div class="issues-panel">
                <div class="issues-header">📝 Question list</div>
                {self._generate_issues_list(grouped_issues)}
            </div>
        </div>
    </div>
    
    <footer>
        <p>Generated by Academic Proofreader | {self._get_current_date()}</p>
    </footer>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const highlights = document.querySelectorAll('.highlight');
            const issueItems = document.querySelectorAll('.issue-item');
            
            highlights.forEach((highlight, index) => {{
                highlight.addEventListener('click', function() {{
                    issueItems[index].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    issueItems.forEach(item => item.style.background = '');
                    issueItems[index].style.background = '#e3f2fd';
                }});
            }});
            
            issueItems.forEach((item, index) => {{
                item.addEventListener('click', function() {{
                    highlights[index].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }});
            }});
        }});
    </script>
</body>
</html>"""

        return html_content

    def to_markdown(self, text: str, results: Dict) -> str:
        """Generate Markdown report"""
        issues = results.get("issues", [])
        summary = results.get("summary", {})

        md_content = f"""# 📋 Academic Proofreader Report
## Academic article inspection report

---

## 📊 Check summary

| index | quantity |
|------|------|
| Total number of problems found | {summary.get("total_issues", len(issues))} |
| mistake | {len([i for i in issues if i["severity"] == "error"])} |
| warn | {len([i for i in issues if i["severity"] == "warning"])} |
| suggestion | {len([i for i in issues if i["severity"] == "info"])} |

---

## 📝 Question list

"""

        grouped_issues = self._group_issues(issues)

        for category, category_issues in grouped_issues.items():
            icon = self.category_icons.get(category, "⚠️")
            md_content += f"\n### {icon} {category}\n\n"

            for i, issue in enumerate(category_issues, 1):
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(
                    issue["severity"], "⚠️"
                )

                md_content += f"**{i}.** {severity_icon} **{issue['message']}**\n\n"

                if issue.get("suggestion"):
                    md_content += f"   > 💡 suggestion: {issue['suggestion']}\n\n"

                md_content += f"   - Location: No. {issue['position']['line']} OK\n"
                md_content += f"   - Severity: {issue['severity']}\n\n"
                md_content += "---\n\n"

        md_content += f"""
---

## 📄 Original text with annotations

```
{self._highlight_text_plain(text, issues)}
```

---

*Generated by Academic Proofreader | {self._get_current_date()}*
"""

        return md_content

    def to_json(self, results: Dict) -> str:
        """Generate JSON results"""
        return json.dumps(results, ensure_ascii=False, indent=2)

    def _group_issues(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Group questions by category"""
        grouped = {}
        for issue in issues:
            category = issue.get("category", "general")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(issue)
        return grouped

    def _highlight_text(self, text: str, issues: List[Dict]) -> str:
        """Mark question location in text"""
        issues_sorted = sorted(issues, key=lambda x: x["position"]["start"])

        annotated_text = ""
        current_pos = 0

        for issue in issues_sorted:
            start = issue["position"]["start"]
            end = issue["position"]["end"]
            severity = issue.get("severity", "warning")

            if start < current_pos:
                continue

            annotated_text += text[current_pos:start]
            annotated_text += f'<span class="highlight {severity}" title="{issue["message"]}">{text[start:end]}</span>'

            current_pos = end

        annotated_text += text[current_pos:]

        return annotated_text

    def _highlight_text_plain(self, text: str, issues: List[Dict]) -> str:
        """Mark question location in text (text-only version)"""
        issues_sorted = sorted(issues, key=lambda x: x["position"]["start"])

        annotated_text = ""
        current_pos = 0

        for issue in issues_sorted:
            start = issue["position"]["start"]
            end = issue["position"]["end"]

            if start < current_pos:
                continue

            annotated_text += text[current_pos:start]
            annotated_text += f"[^{issue['severity']}]" + text[start:end] + "[/^]"

            current_pos = end

        annotated_text += text[current_pos:]

        return annotated_text

    def _generate_issues_list(self, grouped_issues: Dict[str, List[Dict]]) -> str:
        """Generate question list HTML"""
        if not grouped_issues:
            return """<div class="no-issues">
                <div class="icon">✅</div>
                <div>No problems found</div>
            </div>"""

        html = ""

        for category, issues in grouped_issues.items():
            icon = self.category_icons.get(category, "⚠️")
            html += f"""
            <div class="category-section">
                <div class="category-header">
                    {icon} {category}
                    <span style="margin-left: auto; font-size: 0.9em; opacity: 0.7;">
                        {len(issues)} indivual
                    </span>
                </div>
            """

            for i, issue in enumerate(issues):
                severity = issue.get("severity", "warning")
                style = self.severity_styles.get(
                    severity, self.severity_styles["warning"]
                )

                html += f'''
                <div class="issue-item" data-index="{i}">
                    <span class="issue-severity {severity}">{style["icon"]} {str(severity).upper()}</span>
                    <div class="issue-category">{icon} {category}</div>
                    <div class="issue-message">{issue["message"]}</div>
                '''

                if issue.get("suggestion"):
                    html += (
                        f'<div class="issue-suggestion">💡 {issue["suggestion"]}</div>'
                    )

                position = issue.get("position", {})
                html += f"""
                    <div class="issue-location">📍 No. {position.get("line", "?")} OK</div>
                </div>
                """

            html += "</div>"

        return html

    def _get_current_date(self) -> str:
        """Get current date"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def create_annotated_document(
        self, text: str, issues: List[Dict], output_format: str = "html"
    ) -> str:
        """Create annotated documents"""
        if output_format == "html":
            return self.to_html(text, {"issues": issues})
        elif output_format == "markdown":
            return self.to_markdown(text, {"issues": issues})
        else:
            return self.to_json({"issues": issues})

    def generate_statistics(self, results: Dict) -> Dict:
        """Generate statistics"""
        issues = results.get("issues", [])

        stats = {
            "total_issues": len(issues),
            "by_severity": {"error": 0, "warning": 0, "info": 0},
            "by_category": {},
            "by_line": {},
            "top_issues": [],
        }

        for issue in issues:
            severity = issue.get("severity", "warning")
            stats["by_severity"][severity] += 1

            category = issue.get("category", "general")
            if category not in stats["by_category"]:
                stats["by_category"][category] = 0
            stats["by_category"][category] += 1

            line = issue.get("position", {}).get("line", 0)
            if line not in stats["by_line"]:
                stats["by_line"][line] = 0
            stats["by_line"][line] += 1

        message_counts = {}
        for issue in issues:
            message = issue.get("message", "")
            message_counts[message] = message_counts.get(message, 0) + 1

        stats["top_issues"] = sorted(
            [{"message": k, "count": v} for k, v in message_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10]

        return stats
