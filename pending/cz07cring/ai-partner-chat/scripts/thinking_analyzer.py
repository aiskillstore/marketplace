"""
思维模式分析器 - Thinking Pattern Analyzer

功能：
1. 分析知识结构（广度、深度、连贯性）
2. 识别学习模式（路径、速度、触发方式）
3. 判断思维层次（事实/原理/洞察/创新）
4. 生成学习报告

版本: 2.0
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import Counter, defaultdict


class ThinkingAnalyzer:
    """思维模式分析器"""

    def __init__(self, output_dir: str = "./analysis"):
        """初始化分析器"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_thinking_level(self, content: str) -> int:
        """
        判断思维层次（1-4）

        1: 记录事实
        2: 理解原理
        3: 形成洞察
        4: 创新应用

        Args:
            content: 内容文本

        Returns:
            思维层次 1-4
        """
        content_lower = content.lower()

        # Level 4 关键词
        innovation_keywords = [
            '创新', '优化', '改进', '自定义', '最佳实践',
            '设计模式', '架构', '重构'
        ]

        # Level 3 关键词
        insight_keywords = [
            '原来', '本质', '理解', '洞察', '总结',
            '为什么', '原理', '深入'
        ]

        # Level 2 关键词
        principle_keywords = [
            '工作原理', '如何实现', '机制', '流程',
            '步骤', '过程'
        ]

        # 判断层次
        if any(kw in content_lower for kw in innovation_keywords):
            return 4
        elif any(kw in content_lower for kw in insight_keywords):
            return 3
        elif any(kw in content_lower for kw in principle_keywords):
            return 2
        else:
            return 1

    def generate_learning_report(
        self,
        all_chunks: List[Dict],
        period: str = "本月"
    ) -> str:
        """
        生成学习分析报告

        Args:
            all_chunks: 所有chunks（包含metadata）
            period: 时间周期描述

        Returns:
            报告文件路径
        """
        # 统计分析
        total_chunks = len(all_chunks)
        chunk_types = Counter(c['metadata'].get('chunk_type') for c in all_chunks)

        # 主题分布
        all_tags = []
        for chunk in all_chunks:
            tags = chunk['metadata'].get('tags', [])
            if isinstance(tags, list):
                all_tags.extend(tags)

        top_topics = Counter(all_tags).most_common(10)

        # 思维层次分布
        thinking_levels = Counter(
            c['metadata'].get('thinking_level', 1) for c in all_chunks
        )

        # 生成报告
        report = f"""# 学习分析报告 - {period}

## 📊 整体统计

- 总内容数：{total_chunks}
- 笔记：{chunk_types.get('note', 0)}
- 对话：{chunk_types.get('conversation', 0)}
- 代码：{chunk_types.get('code', 0)}

## 🏷️ 主题分布

"""
        for topic, count in top_topics:
            percentage = (count / len(all_tags) * 100) if all_tags else 0
            report += f"- {topic}: {count}次 ({percentage:.1f}%)\n"

        report += f"""

## 🧠 思维层次分析

- Level 4 (创新应用): {thinking_levels.get(4, 0)}
- Level 3 (形成洞察): {thinking_levels.get(3, 0)}
- Level 2 (理解原理): {thinking_levels.get(2, 0)}
- Level 1 (记录事实): {thinking_levels.get(1, 0)}

## 💡 洞察与建议

"""

        # 简单建议生成
        if thinking_levels.get(1, 0) > total_chunks * 0.5:
            report += "- 建议：增加对原理的深入思考，不要只记录事实\n"

        if len(top_topics) < 3:
            report += "- 建议：扩大学习广度，涉及更多主题\n"

        if chunk_types.get('code', 0) == 0:
            report += "- 建议：增加代码实践，理论与实践结合\n"

        # 保存报告
        report_file = self.output_dir / "reports" / f"learning_report_{period}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(report_file)
