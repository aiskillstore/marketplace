"""
对话历史记录器 - Conversation Logger

功能：
1. 保存每次对话到 Markdown 文件
2. 评估对话重要性（1-5分）
3. 将重要对话向量化存入数据库
4. 生成每周对话摘要

版本: 2.0
"""

import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import sys

# 导入项目模块
sys.path.insert(0, str(Path(__file__).parent))
from chunk_schema import create_conversation_metadata, IMPORTANCE_MEDIUM
from vector_indexer import VectorIndexer


class ConversationLogger:
    """对话历史记录器"""

    def __init__(
        self,
        conversations_dir: str = "./conversations",
        db_path: str = "./vector_db"
    ):
        """
        初始化对话记录器

        Args:
            conversations_dir: 对话历史存储目录
            db_path: 向量数据库路径
        """
        self.conversations_dir = Path(conversations_dir)
        self.raw_dir = self.conversations_dir / "raw"
        self.summary_dir = self.conversations_dir / "summary"
        self.db_path = db_path

        # 创建目录
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.summary_dir.mkdir(parents=True, exist_ok=True)

        # 元数据文件
        self.metadata_file = self.conversations_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """加载对话元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"conversations": [], "total_count": 0}

    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def evaluate_importance(
        self,
        user_message: str,
        ai_response: str
    ) -> int:
        """
        评估对话重要性（简单规则，实际应用可用 LLM）

        评分标准:
        5分 - 重大决策、突破性理解、关键结论
        4分 - 深入讨论、问题解决、知识关联
        3分 - 有用信息、常规学习记录
        2分 - 简单问答、事实查询
        1分 - 寒暄、确认、无实质内容

        Args:
            user_message: 用户消息
            ai_response: AI回复

        Returns:
            重要性评分 1-5
        """
        # 简单规则判断（生产环境应该用 LLM）
        combined = (user_message + " " + ai_response).lower()

        # 关键词判断
        high_importance_keywords = [
            '重要', '决定', '突破', '理解了', '原来如此',
            '问题解决', '深入', '关键', '发现'
        ]

        medium_keywords = [
            '学习', '笔记', '记录', '整理', '总结',
            '思考', '分析', '讨论'
        ]

        low_keywords = [
            '谢谢', '你好', '好的', '明白', '知道了',
            'hi', 'hello', 'thanks', 'ok'
        ]

        # 长度判断（长对话通常更重要）
        total_length = len(user_message) + len(ai_response)

        if any(kw in combined for kw in high_importance_keywords):
            return 5 if total_length > 500 else 4

        if any(kw in combined for kw in medium_keywords):
            return 3 if total_length > 200 else 2

        if any(kw in combined for kw in low_keywords) and total_length < 50:
            return 1

        # 默认中等重要性
        return IMPORTANCE_MEDIUM

    def log_conversation(
        self,
        user_message: str,
        ai_response: str,
        topic: Optional[str] = None,
        importance: Optional[int] = None
    ) -> str:
        """
        记录一次对话

        Args:
            user_message: 用户消息
            ai_response: AI回复
            topic: 对话主题（可选，可由 LLM 提取）
            importance: 重要性评分（可选，如不提供则自动评估）

        Returns:
            对话ID
        """
        now = datetime.now()
        conversation_id = f"conv_{now.strftime('%Y%m%d_%H%M%S')}"

        # 评估重要性
        if importance is None:
            importance = self.evaluate_importance(user_message, ai_response)

        # 1. 保存到 Markdown 文件
        self._save_to_markdown(
            conversation_id, user_message, ai_response,
            now, topic, importance
        )

        # 2. 向量化（只有重要对话 ≥3分）
        if importance >= IMPORTANCE_MEDIUM:
            self._save_to_vector_db(
                conversation_id, user_message, ai_response,
                now, topic, importance
            )

        # 3. 更新元数据
        self._update_metadata(conversation_id, now, topic, importance)

        return conversation_id

    def _save_to_markdown(
        self,
        conversation_id: str,
        user_msg: str,
        ai_msg: str,
        timestamp: datetime,
        topic: Optional[str],
        importance: int
    ):
        """保存对话到 Markdown 文件"""
        # 按月份组织
        month_dir = self.raw_dir / timestamp.strftime('%Y-%m')
        month_dir.mkdir(parents=True, exist_ok=True)

        # 每天一个文件
        daily_file = month_dir / f"{timestamp.strftime('%Y-%m-%d')}.md"

        # 重要性标记
        importance_emoji = {
            5: '🔴',  # 关键
            4: '🟠',  # 重要
            3: '🟡',  # 中等
            2: '⚪',  # 一般
            1: '⚫'   # 琐碎
        }

        # 对话内容
        conversation_content = f"""
## {importance_emoji.get(importance, '🟡')} [{timestamp.strftime('%H:%M:%S')}] {topic or '对话'}
**ID**: `{conversation_id}` | **重要性**: {importance}/5

**用户**:
{user_msg}

**AI**:
{ai_msg}

---

"""

        # 追加到文件
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(conversation_content)

    def _save_to_vector_db(
        self,
        conversation_id: str,
        user_msg: str,
        ai_msg: str,
        timestamp: datetime,
        topic: Optional[str],
        importance: int
    ):
        """将对话向量化并存入数据库"""
        # 创建 chunk
        chunk = {
            'content': f"""对话主题: {topic or '未分类'}

用户问题: {user_msg}

AI回复: {ai_msg}""",
            'metadata': create_conversation_metadata(
                conversation_id=conversation_id,
                importance=importance,
                date=timestamp.strftime('%Y-%m-%d'),
                created_at=timestamp.isoformat(),
                topic=topic
            )
        }

        # 追加到向量库
        try:
            indexer = VectorIndexer(db_path=self.db_path)
            indexer.append_chunks([chunk])
            print(f"✅ 对话已向量化: {conversation_id} (重要性: {importance})")
        except Exception as e:
            print(f"❌ 向量化失败: {e}")

    def _update_metadata(
        self,
        conversation_id: str,
        timestamp: datetime,
        topic: Optional[str],
        importance: int
    ):
        """更新元数据"""
        self.metadata['conversations'].append({
            'id': conversation_id,
            'timestamp': timestamp.isoformat(),
            'topic': topic,
            'importance': importance
        })
        self.metadata['total_count'] += 1
        self._save_metadata()

    def get_recent_conversations(
        self,
        days: int = 7,
        min_importance: int = 3
    ) -> list:
        """
        获取最近的重要对话

        Args:
            days: 最近多少天
            min_importance: 最低重要性

        Returns:
            对话列表
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        recent = [
            conv for conv in self.metadata['conversations']
            if (datetime.fromisoformat(conv['timestamp']) > cutoff_date
                and conv['importance'] >= min_importance)
        ]

        # 按重要性和时间排序
        recent.sort(
            key=lambda x: (x['importance'], x['timestamp']),
            reverse=True
        )

        return recent

    def generate_weekly_summary(self) -> str:
        """
        生成本周对话摘要

        Returns:
            摘要文件路径
        """
        # 获取本周对话
        weekly = self.get_recent_conversations(days=7, min_importance=2)

        if not weekly:
            return None

        # 生成摘要文件
        now = datetime.now()
        week_num = now.strftime('%Y-W%W')
        summary_file = self.summary_dir / f"weekly-{week_num}.md"

        # 按主题分组
        by_topic = {}
        for conv in weekly:
            topic = conv.get('topic') or '未分类'
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(conv)

        # 生成摘要内容
        summary_content = f"""# 对话摘要 - {week_num}

生成时间: {now.strftime('%Y-%m-%d %H:%M')}

## 统计

- 总对话数: {len(weekly)}
- 重要对话 (≥4分): {len([c for c in weekly if c['importance'] >= 4])}
- 涉及主题: {len(by_topic)}

## 按主题分类

"""

        for topic, convs in sorted(by_topic.items()):
            summary_content += f"### {topic}\n\n"
            summary_content += f"对话次数: {len(convs)}\n"
            summary_content += f"平均重要性: {sum(c['importance'] for c in convs) / len(convs):.1f}\n\n"

            # 列出对话
            for conv in convs[:5]:  # 每个主题最多列5条
                timestamp = datetime.fromisoformat(conv['timestamp'])
                summary_content += f"- [{timestamp.strftime('%m-%d %H:%M')}] "
                summary_content += f"重要性: {conv['importance']}/5\n"

            summary_content += "\n"

        # 保存摘要
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        print(f"📊 已生成周摘要: {summary_file}")
        return str(summary_file)


# LLM 提示词模板（供 Claude Code 使用）

IMPORTANCE_EVALUATION_PROMPT = """
评估以下对话的重要性（1-5分）：

用户: {user_message}

AI: {ai_response}

评分标准:
5分 - 重大决策、突破性理解、关键结论
4分 - 深入讨论、问题解决、知识关联
3分 - 有用信息、常规学习记录
2分 - 简单问答、事实查询
1分 - 寒暄、确认、无实质内容

只返回数字1-5。
"""

TOPIC_EXTRACTION_PROMPT = """
从以下对话中提取主要主题（一句话概括）：

用户: {user_message}

AI: {ai_response}

只返回简短的主题（不超过10个字）。
"""
