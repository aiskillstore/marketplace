"""
情绪与状态追踪器 - Emotion Analyzer

功能：
1. 分析笔记和对话的情绪状态
2. 追踪学习状态变化
3. 生成情绪时间线
4. 提供状态感知能力

版本: 2.0
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from chunk_schema import (
    STATE_EXPLORATION, STATE_CONFUSION, STATE_BREAKTHROUGH,
    STATE_CONSOLIDATION, STATE_BURNOUT, STATE_STAGNATION
)


class EmotionAnalyzer:
    """情绪与学习状态分析器"""

    def __init__(self, index_dir: str = "./indexes"):
        """初始化分析器"""
        timeline_path = Path(index_dir) / "emotion_timeline.json"
        self.timeline_path = Path(timeline_path)
        self.timeline_path.parent.mkdir(parents=True, exist_ok=True)
        self.timeline = self._load_timeline()

    def _load_timeline(self) -> List[Dict]:
        """加载时间线"""
        if self.timeline_path.exists():
            with open(self.timeline_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_timeline(self):
        """保存时间线"""
        with open(self.timeline_path, 'w', encoding='utf-8') as f:
            json.dump(self.timeline, f, ensure_ascii=False, indent=2)

    def analyze_emotion(self, content: str) -> Dict:
        """
        分析内容的情绪状态（简单规则，生产环境用 LLM）

        Returns:
            {
                'state': 'breakthrough',
                'excitement': 8,
                'confidence': 7,
                'confusion': 2,
                'fatigue': 3
            }
        """
        content_lower = content.lower()

        # 关键词情绪分析
        excitement_keywords = ['太好了', '明白了', '理解了', '原来', '成功', '！', '!!']
        confusion_keywords = ['不懂', '困惑', '难', '复杂', '？？', '为什么']
        fatigue_keywords = ['累', '疲', '倦', '休息', '放弃']
        confidence_keywords = ['掌握', '学会', '完成', '搞定', '理解']

        # 计算情绪分数
        excitement = min(10, sum(1 for kw in excitement_keywords if kw in content_lower) * 2)
        confusion = min(10, sum(1 for kw in confusion_keywords if kw in content_lower) * 2)
        fatigue = min(10, sum(1 for kw in fatigue_keywords if kw in content_lower) * 3)
        confidence = min(10, sum(1 for kw in confidence_keywords if kw in content_lower) * 2)

        # 状态判断
        if excitement > 6 and confusion < 3:
            state = STATE_BREAKTHROUGH
        elif confusion > 6:
            state = STATE_CONFUSION
        elif fatigue > 6:
            state = STATE_BURNOUT
        elif confidence > 5:
            state = STATE_CONSOLIDATION
        else:
            state = STATE_EXPLORATION

        return {
            'state': state,
            'excitement': excitement or 5,
            'confidence': confidence or 5,
            'confusion': confusion or 2,
            'fatigue': fatigue or 3
        }

    def update_timeline(self, date: str, emotion: Dict, notes_count: int = 0):
        """更新情绪时间线"""
        # 查找是否已有当天记录
        existing = next((item for item in self.timeline if item['date'] == date), None)

        if existing:
            # 更新现有记录（取平均值）
            for key in ['excitement', 'confidence', 'confusion', 'fatigue']:
                existing[key] = (existing[key] + emotion[key]) // 2
            existing['notes_count'] += notes_count
        else:
            # 添加新记录
            self.timeline.append({
                'date': date,
                'state': emotion['state'],
                **{k: v for k, v in emotion.items() if k != 'state'},
                'notes_count': notes_count
            })

        # 排序并保存
        self.timeline.sort(key=lambda x: x['date'])
        self._save_timeline()

    def get_current_state(self, days: int = 7) -> Dict:
        """
        获取当前学习状态（最近N天）

        Returns:
            当前状态摘要
        """
        if not self.timeline:
            return {
                'state': STATE_EXPLORATION,
                'trend': 'stable',
                'avg_confusion': 5,
                'avg_excitement': 5
            }

        # 获取最近记录
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent = [item for item in self.timeline if item['date'] >= cutoff]

        if not recent:
            return {'state': STATE_EXPLORATION}

        # 计算平均值
        avg_confusion = sum(item['confusion'] for item in recent) / len(recent)
        avg_excitement = sum(item['excitement'] for item in recent) / len(recent)
        avg_confidence = sum(item['confidence'] for item in recent) / len(recent)

        # 趋势判断
        if len(recent) >= 3:
            recent_confusion = [item['confusion'] for item in recent[-3:]]
            if recent_confusion[2] < recent_confusion[0] - 2:
                trend = 'improving'
            elif recent_confusion[2] > recent_confusion[0] + 2:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'

        # 状态判断
        current_state = recent[-1]['state']

        return {
            'state': current_state,
            'trend': trend,
            'avg_confusion': round(avg_confusion, 1),
            'avg_excitement': round(avg_excitement, 1),
            'avg_confidence': round(avg_confidence, 1)
        }


# 情绪分析提示词（供 LLM 使用）
EMOTION_ANALYSIS_PROMPT = """
分析以下内容的学习状态和情绪：

{content}

请评估（0-10分）：
1. excitement（兴奋度）- 学习热情
2. confidence（信心度）- 自我效能感
3. confusion（困惑度）- 理解难度
4. fatigue（疲劳度）- 心理负荷

并判断认知状态：
- exploration（探索期）
- confusion（困惑期）
- breakthrough（突破期）
- consolidation（巩固期）
- burnout（倦怠期）

返回JSON格式。
"""
