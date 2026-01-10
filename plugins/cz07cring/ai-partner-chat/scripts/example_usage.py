"""
AI Partner Chat 2.0 - 完整使用示例

演示如何使用核心协调器处理笔记和对话
"""

import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import AIPartnerOrchestrator


def example_1_process_note():
    """示例 1: 处理新笔记"""
    print("\n" + "="*60)
    print("示例 1: 处理新笔记")
    print("="*60)

    # 初始化协调器
    orch = AIPartnerOrchestrator()

    # 模拟笔记内容
    note_content = """# React Hooks 学习

今天深入学习了 useState,终于理解了状态更新的原理!

## 基础用法

```javascript
const [count, setCount] = useState(0);

function handleClick() {
    setCount(count + 1);
}
```

## 核心原理

原来 useState 是通过闭包保存状态的,每次渲染都会调用组件函数,
但是 state 变量的值会被 React 记住。

这太好了! 我理解了为什么 Hooks 必须在顶层调用 - 因为 React
依赖调用顺序来关联每个 Hook 和它的状态。

## 注意事项

- 不要在循环、条件或嵌套函数中调用 Hooks
- state 更新是异步的
- 使用函数式更新避免闭包陷阱
"""

    # 处理笔记 - 一行代码搞定所有分析
    result = orch.process_new_note(
        note_path="./notes/react_hooks_学习.md",
        content=note_content
    )

    # 查看处理结果
    print(f"\n✅ 处理完成!")
    print(f"   - 创建了 {result['chunks_created']} 个 chunks")
    print(f"   - 成功索引了 {result['chunks_indexed']} 个 chunks")
    print(f"   - 标签: {', '.join(result['tags'])}")
    print(f"   - 情绪状态: {result['emotion']['state']}")
    print(f"   - 兴奋度: {result['emotion']['excitement']}/10")
    print(f"   - 思维层次: Level {result['thinking_level']}")
    print(f"   - 代码块数量: {result['code_blocks']}")


def example_2_conversation():
    """示例 2: 处理对话"""
    print("\n" + "="*60)
    print("示例 2: 处理对话")
    print("="*60)

    orch = AIPartnerOrchestrator()

    # 第一步: 获取上下文
    user_message = "React Hooks 的 useState 为什么要用数组解构?"

    print(f"\n用户问题: {user_message}")
    print("\n正在检索相关上下文...")

    context = orch.handle_conversation(
        user_message=user_message,
        generate_response=True
    )

    # 查看上下文
    print(f"\n📊 当前学习状态:")
    state = context['context']['user_state']
    print(f"   - 状态: {state['state']}")
    print(f"   - 趋势: {state['trend']}")
    print(f"   - 平均困惑度: {state['avg_confusion']}/10")
    print(f"   - 平均兴奋度: {state['avg_excitement']}/10")

    print(f"\n🔍 检索结果:")
    results = context['context']['search_results']
    print(f"   - 相关笔记: {len(results['notes'])} 条")
    print(f"   - 相关对话: {len(results['conversations'])} 条")
    print(f"   - 相关代码: {len(results['code'])} 条")

    # 模拟 AI 生成回复
    ai_response = """基于你的笔记,我看到你已经理解了 useState 的闭包原理,很棒!

关于为什么用数组解构,主要有以下原因:

1. **灵活命名**: 数组解构允许你自由命名变量
   const [count, setCount] = useState(0);
   const [name, setName] = useState('');

2. **顺序固定**: React 保证返回值的顺序始终是 [state, setState]

3. **对比对象解构**: 如果用对象,你就必须使用固定的属性名
   const {state, setState} = useState(0); // 不灵活

这种设计体现了 React 团队对 API 易用性的深思熟虑。
"""

    print(f"\n💬 AI 回复: (省略具体内容)")

    # 第二步: 记录对话
    result = orch.handle_conversation(
        user_message=user_message,
        ai_response=ai_response
    )

    print(f"\n✅ 对话已记录!")
    print(f"   - 对话ID: {result['conversation_id']}")
    print(f"   - 情绪已更新: {result['emotion_updated']}")


def example_3_weekly_report():
    """示例 3: 生成周报"""
    print("\n" + "="*60)
    print("示例 3: 生成周报")
    print("="*60)

    orch = AIPartnerOrchestrator()

    print("\n正在生成本周学习报告...")

    report_path = orch.generate_weekly_report()

    print(f"\n✅ 报告已生成: {report_path}")
    print("\n报告内容包括:")
    print("   - 📊 整体统计 (笔记/对话/代码数量)")
    print("   - 🏷️ 主题分布 (学习主题排行)")
    print("   - 🧠 思维层次分析 (Level 1-4 分布)")
    print("   - 💡 个性化学习建议")


def example_4_system_stats():
    """示例 4: 查看系统统计"""
    print("\n" + "="*60)
    print("示例 4: 系统统计")
    print("="*60)

    orch = AIPartnerOrchestrator()

    stats = orch.get_system_stats()

    print(f"\n📊 向量数据库:")
    print(f"   - 总 chunks: {stats['vector_db']['total_chunks']}")
    print(f"   - 笔记: {stats['vector_db']['chunk_types'].get('note', 0)}")
    print(f"   - 对话: {stats['vector_db']['chunk_types'].get('conversation', 0)}")
    print(f"   - 代码: {stats['vector_db']['chunk_types'].get('code', 0)}")

    print(f"\n🏷️ 标签统计:")
    print(f"   - 总标签数: {stats['tags']['total_tags']}")
    if stats['tags']['top_tags']:
        print(f"   - Top 3 标签:")
        for tag_info in stats['tags']['top_tags'][:3]:
            print(f"     • {tag_info['tag']}: {tag_info['count']} 次")

    print(f"\n😊 当前状态:")
    print(f"   - 学习状态: {stats['current_state']['state']}")
    print(f"   - 趋势: {stats['current_state']['trend']}")


if __name__ == "__main__":
    print("\n🚀 AI Partner Chat 2.0 - 完整使用示例")
    print("="*60)

    # 运行所有示例
    try:
        example_1_process_note()
    except Exception as e:
        print(f"\n❌ 示例 1 执行失败: {e}")

    try:
        example_2_conversation()
    except Exception as e:
        print(f"\n❌ 示例 2 执行失败: {e}")

    try:
        example_3_weekly_report()
    except Exception as e:
        print(f"\n❌ 示例 3 执行失败: {e}")

    try:
        example_4_system_stats()
    except Exception as e:
        print(f"\n❌ 示例 4 执行失败: {e}")

    print("\n" + "="*60)
    print("✨ 所有示例运行完成!")
    print("="*60)
    print("\n💡 提示:")
    print("   - 首次运行会下载嵌入模型 (~4.3GB)")
    print("   - 后续运行会使用缓存,速度很快")
    print("   - 所有数据保存在项目根目录")
    print("\n")
