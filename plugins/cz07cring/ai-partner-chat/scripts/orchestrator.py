"""
核心协调器 - Orchestrator

整个 AI Partner Chat 2.0 的核心大脑，串联所有功能：
1. 处理新笔记（标签、代码、情绪、向量化）
2. 处理对话（状态感知、多源检索、记录）
3. 生成分析报告
4. 统一调度所有模块

版本: 2.0
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 导入所有模块
sys.path.insert(0, str(Path(__file__).parent))

from tag_generator import TagGenerator
from tag_indexer import TagIndexer
from conversation_logger import ConversationLogger
from code_parser import CodeParser
from emotion_analyzer import EmotionAnalyzer
from thinking_analyzer import ThinkingAnalyzer
from vector_indexer import VectorIndexer
from vector_utils import MultiSourceRetriever
from chunk_schema import (
    create_note_metadata, create_code_metadata,
    CHUNK_TYPE_NOTE, CHUNK_TYPE_CODE
)


class AIPartnerOrchestrator:
    """AI Partner 核心协调器 - 串联所有功能"""

    def __init__(self, project_root: str = ".", skill_dir: str = None):
        """
        初始化协调器

        Args:
            project_root: 项目根目录（用于读取 notes/ 和 config/）
            skill_dir: skill 目录路径（默认 ~/.claude/skills/ai-partner-chat）
        """
        self.project_root = Path(project_root).resolve()

        # 确定 skill 数据目录
        if skill_dir is None:
            skill_dir = Path.home() / '.claude' / 'skills' / 'ai-partner-chat'
        self.skill_dir = Path(skill_dir)
        self.data_dir = self.skill_dir / 'data'

        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / 'vector_db').mkdir(exist_ok=True)
        (self.data_dir / 'conversations').mkdir(exist_ok=True)
        (self.data_dir / 'indexes').mkdir(exist_ok=True)
        (self.data_dir / 'analysis').mkdir(exist_ok=True)

        # 初始化所有模块（使用 skill 目录的数据路径）
        self.tag_generator = TagGenerator()
        self.tag_indexer = TagIndexer(
            index_dir=str(self.data_dir / 'indexes')
        )
        self.conversation_logger = ConversationLogger(
            conversations_dir=str(self.data_dir / 'conversations')
        )
        self.code_parser = CodeParser()
        self.emotion_analyzer = EmotionAnalyzer(
            index_dir=str(self.data_dir / 'indexes')
        )
        self.thinking_analyzer = ThinkingAnalyzer()
        self.vector_indexer = VectorIndexer(
            db_path=str(self.data_dir / 'vector_db')
        )
        self.retriever = MultiSourceRetriever(
            db_path=str(self.data_dir / 'vector_db')
        )

        # 显示初始化信息
        stats = self.vector_indexer.get_stats()
        print(f"✅ AI Partner 协调器已初始化")
        print(f"   项目: {self.project_root.name}")
        print(f"   数据: ~/.claude/skills/ai-partner-chat/data/")
        print(f"   向量库: {stats['total_chunks']} chunks")
        if stats['total_chunks'] > 0:
            print(f"   💭 长期记忆已加载")

    def process_new_note(self, note_path: str, content: str) -> Dict:
        """
        处理新笔记 - 全流程

        流程：
        1. 分析标签
        2. 提取代码块
        3. 分析情绪状态
        4. 判断思维层次
        5. 生成chunks
        6. 向量化
        7. 更新索引

        Args:
            note_path: 笔记文件路径
            content: 笔记内容

        Returns:
            处理结果摘要
        """
        print(f"\n📝 处理新笔记: {note_path}")

        # 1. 并行分析
        tags_layers = self.tag_generator.generate_tag_layers(content, 'note')
        all_tags = (tags_layers['topic'] + tags_layers['tech'] +
                   tags_layers['custom'])

        code_blocks = self.code_parser.extract_code_blocks(content)
        emotion = self.emotion_analyzer.analyze_emotion(content)
        thinking_level = self.thinking_analyzer.analyze_thinking_level(content)

        print(f"  标签: {all_tags}")
        print(f"  情绪: {emotion['state']}")
        print(f"  思维层次: Level {thinking_level}")
        print(f"  代码块: {len(code_blocks)} 个")

        # 2. 生成 chunks
        chunks = []
        today = datetime.now().strftime('%Y-%m-%d')

        # 笔记主体 chunk
        note_chunk = {
            'content': content,
            'metadata': create_note_metadata(
                filename=Path(note_path).name,
                filepath=note_path,
                chunk_id=0,
                date=today,
                tags=all_tags,
                tag_layers=tags_layers,
                emotion=emotion,
                thinking_level=thinking_level,
                created_at=datetime.now().isoformat()
            )
        }
        chunks.append(note_chunk)

        # 代码块 chunks
        for idx, code_block in enumerate(code_blocks):
            code_analysis = self.code_parser.analyze_code(
                code_block['code'],
                code_block['language']
            )

            code_chunk = {
                'content': code_block['code'],
                'metadata': create_code_metadata(
                    filename=Path(note_path).name,
                    filepath=note_path,
                    chunk_id=idx + 1,
                    **code_analysis,  # code_analysis 已包含 language
                    tags=all_tags,  # 继承笔记标签
                    date=today,
                    created_at=datetime.now().isoformat()
                )
            }
            chunks.append(code_chunk)

        # 3. 向量化
        indexed = self.vector_indexer.append_chunks(chunks)

        # 4. 更新索引
        self.tag_indexer.add_tags(note_path, all_tags)

        # 5. 更新情绪时间线
        self.emotion_analyzer.update_timeline(today, emotion, notes_count=1)

        return {
            'chunks_created': len(chunks),
            'chunks_indexed': indexed,
            'tags': all_tags,
            'emotion': emotion,
            'thinking_level': thinking_level,
            'code_blocks': len(code_blocks)
        }

    def handle_conversation(
        self,
        user_message: str,
        ai_response: str = None,
        generate_response: bool = True,
        save_conversation: bool = True
    ) -> Dict:
        """
        处理对话 - 全流程

        两种使用模式：

        **模式 1 - 两步调用（推荐）**:
        ```python
        # 第一步: 获取上下文（用于生成回复）
        context = orch.handle_conversation(
            user_message="问题",
            generate_response=True,
            save_conversation=False  # 暂不保存
        )

        # 第二步: 生成回复并保存
        ai_response = your_ai_function(context)
        orch.handle_conversation(
            user_message="问题",
            ai_response=ai_response,
            save_conversation=True
        )
        ```

        **模式 2 - 一步调用（简单但无 AI 回复）**:
        ```python
        # 直接保存用户消息（AI 回复为空）
        orch.handle_conversation(
            user_message="问题",
            save_conversation=True
        )
        ```

        Args:
            user_message: 用户消息
            ai_response: AI回复（如果已生成）
            generate_response: 是否需要生成回复上下文
            save_conversation: 是否保存对话

        Returns:
            包含上下文和处理结果的字典
        """
        print(f"\n💬 处理对话: {user_message[:50]}...")

        # 1. 状态感知
        current_state = self.emotion_analyzer.get_current_state(days=7)
        print(f"  当前状态: {current_state['state']} (趋势: {current_state['trend']})")

        # 2. 多源检索
        search_results = self.retriever.search_all(
            query=user_message,
            notes_k=3,
            conversations_k=2,
            code_k=2
        )

        print(f"  检索结果: {len(search_results['notes'])} 笔记, "
              f"{len(search_results['conversations'])} 对话, "
              f"{len(search_results['code'])} 代码")

        # 3. 构建上下文
        context = {
            'user_state': current_state,
            'search_results': search_results,
            'user_message': user_message
        }

        # 4. 保存对话（如果需要）
        conv_id = None
        emotion_updated = False

        if save_conversation:
            # 记录对话（即使没有 AI 回复也保存用户消息）
            conv_id = self.conversation_logger.log_conversation(
                user_message=user_message,
                ai_response=ai_response or "[等待回复]"  # 如果没有回复，标记为等待
            )
            print(f"  ✅ 对话已保存: {conv_id}")

            # 分析对话情绪并更新（如果有 AI 回复）
            if ai_response:
                combined = user_message + " " + ai_response
                emotion = self.emotion_analyzer.analyze_emotion(combined)
                today = datetime.now().strftime('%Y-%m-%d')
                self.emotion_analyzer.update_timeline(today, emotion)
                emotion_updated = True

        # 返回结果
        return {
            'conversation_id': conv_id,
            'context': context,
            'emotion_updated': emotion_updated,
            'needs_response': ai_response is None
        }

    def generate_weekly_report(self) -> str:
        """
        生成本周分析报告

        Returns:
            报告文件路径
        """
        print("\n📊 生成周报...")

        # 1. 对话摘要
        conv_summary = self.conversation_logger.generate_weekly_summary()

        # 2. 获取本周所有 chunks 进行分析
        recent_chunks = self.retriever.get_recent(days=7, top_k=100)

        # 3. 生成学习报告
        learning_report = self.thinking_analyzer.generate_learning_report(
            recent_chunks,
            period="本周"
        )

        print(f"✅ 报告已生成")
        print(f"  对话摘要: {conv_summary}")
        print(f"  学习报告: {learning_report}")

        return learning_report

    def get_system_stats(self) -> Dict:
        """
        获取系统统计信息

        Returns:
            统计信息字典
        """
        # 向量库统计
        db_stats = self.vector_indexer.get_stats()

        # 标签统计
        tag_stats = self.tag_indexer.get_tag_statistics()

        # 情绪状态
        current_state = self.emotion_analyzer.get_current_state()

        return {
            'vector_db': db_stats,
            'tags': tag_stats,
            'current_state': current_state,
            'timestamp': datetime.now().isoformat()
        }


# 便捷函数

def process_note(note_path: str, content: str) -> Dict:
    """
    便捷函数：处理笔记

    Args:
        note_path: 笔记路径
        content: 笔记内容

    Returns:
        处理结果
    """
    orchestrator = AIPartnerOrchestrator()
    return orchestrator.process_new_note(note_path, content)


def handle_conversation_simple(user_msg: str, ai_msg: str) -> Dict:
    """
    便捷函数：处理对话

    Args:
        user_msg: 用户消息
        ai_msg: AI回复

    Returns:
        处理结果
    """
    orchestrator = AIPartnerOrchestrator()
    return orchestrator.handle_conversation(user_msg, ai_msg)


# 使用示例
if __name__ == "__main__":
    # 初始化
    orch = AIPartnerOrchestrator()

    # 示例1: 处理笔记
    result = orch.process_new_note(
        note_path="./notes/test.md",
        content="""# React Hooks 学习

今天学习了 useState，终于理解了状态更新的原理！

```javascript
const [count, setCount] = useState(0);
```

太好了，原来是这样工作的！
"""
    )
    print(f"\n处理结果: {result}")

    # 示例2: 系统统计
    stats = orch.get_system_stats()
    print(f"\n系统统计: {stats}")
