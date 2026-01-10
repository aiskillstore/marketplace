# AI Partner Chat 2.0

**个性化 AI 学习伙伴 - Claude Code Skill**

> 一个真正会"记住"你的 AI 助手，通过长期记忆实现跨项目知识积累和个性化对话。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ 核心特性

### 🧠 长期记忆系统
- **跨项目知识积累** - 项目 A 学的知识，项目 B 也能用
- **自动向量化** - 对话和笔记自动转换为 1024 维向量（BAAI/bge-m3）
- **智能检索** - 基于语义相似度的多源检索（笔记+对话+代码）
- **持久化存储** - ChromaDB 向量数据库，数据永不丢失

### 📝 智能笔记管理
- **自动检测** - 监控项目 `notes/` 目录，自动处理新笔记
- **代码提取** - 识别并独立索引笔记中的代码块
- **分层标签** - 智能生成主题/技术/自定义三层标签
- **去重机制** - 跟踪已处理笔记，避免重复向量化

### 💬 对话历史记录
- **完整保存** - 所有对话按月/日组织保存（YYYY-MM/YYYY-MM-DD.md）
- **重要性分级** - 1-5 级重要性评估，≥3 级自动向量化
- **上下文感知** - 回答问题时自动检索相关历史对话
- **自动记录** - Claude 在每次对话后自动保存（需激活 skill）

### 🎯 状态感知分析
- **情绪追踪** - 9 种情绪状态识别（exploration, confusion, breakthrough...）
- **思维层次** - Level 1-6 深度分析（记忆→应用→创造）
- **时间线分析** - 情绪和学习状态的时间轴可视化
- **个性化回应** - 根据当前状态调整 AI 的回应策略

---

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Claude Code CLI
- 约 5GB 磁盘空间（用于嵌入模型缓存）

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/ai-partner-chat.git
cd ai-partner-chat
```

### 2. 安装到 Claude Code

```bash
./install.sh
```

安装脚本会：
- ✅ 复制代码到 `~/.claude/skills/ai-partner-chat/`
- ✅ 保护现有 `data/` 目录（自动备份+恢复）
- ✅ 创建必要的目录结构
- ✅ 显示数据统计信息

### 3. 创建虚拟环境（在你的项目中）

```bash
cd /path/to/your/project
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r ~/.claude/skills/ai-partner-chat/scripts/requirements.txt
```

**依赖清单：**
- `chromadb>=0.4.0` - 向量数据库
- `sentence-transformers>=2.2.0` - 嵌入模型
- `numpy<2` - 数值计算
- `transformers<4.50` - 模型加载（兼容性）

**首次运行：**
- 自动下载 BAAI/bge-m3 模型（约 4.3GB）
- 缓存位置：
  - macOS/Linux: `~/.cache/huggingface/hub/`
  - Windows: `%USERPROFILE%\.cache\huggingface\hub\`

### 4. 配置双画像（首次使用）

```bash
mkdir -p config
cp ~/.claude/skills/ai-partner-chat/assets/user-persona-template.md config/user-persona.md
cp ~/.claude/skills/ai-partner-chat/assets/ai-persona-template.md config/ai-persona.md

# 编辑画像文件
vim config/user-persona.md  # 填写你的学习背景、目标、风格
vim config/ai-persona.md    # 定义 AI 的回应风格、原则
```

### 5. 创建笔记目录

```bash
mkdir notes
echo "# 今天学习了 React Hooks" > notes/react-learning.md
```

### 6. 开始使用

在 Claude Code 中对话，系统会自动：
1. ✅ 初始化 orchestrator（加载长期记忆）
2. ✅ 检测并处理项目 `notes/` 中的新笔记
3. ✅ 记录每次对话到 `~/.claude/skills/ai-partner-chat/data/`
4. ✅ 在回答问题时检索相关历史知识

---

## 📂 目录结构

### Skill 目录（集中数据存储）
```
~/.claude/skills/ai-partner-chat/
├── scripts/                    # Python 模块（14 个）
│   ├── orchestrator.py         # 核心协调器
│   ├── note_processor.py       # 笔记自动处理器（新增）
│   ├── vector_indexer.py       # 向量索引管理
│   ├── vector_utils.py         # 多源检索工具
│   ├── tag_generator.py        # 标签生成
│   ├── tag_indexer.py          # 标签索引
│   ├── code_parser.py          # 代码块提取
│   ├── conversation_logger.py  # 对话记录
│   ├── emotion_analyzer.py     # 情绪分析
│   ├── thinking_analyzer.py    # 思维层次分析
│   ├── chunk_schema.py         # Chunk 元数据定义
│   └── requirements.txt        # Python 依赖
├── assets/                     # 画像模板
│   ├── user-persona-template.md
│   └── ai-persona-template.md
├── notes-examples/             # 笔记示例（仅供参考）
│   ├── example-learning.md
│   └── react_hooks_学习.md
├── SKILL.md                    # Skill 定义（Claude 读取）
└── data/                       # 运行时数据（长期记忆）
    ├── vector_db/              # ChromaDB 向量数据库
    │   ├── chroma.sqlite3      # 所有向量存储
    │   └── ...
    ├── conversations/          # 对话历史
    │   ├── raw/
    │   │   └── YYYY-MM/
    │   │       └── YYYY-MM-DD.md  # 按日期组织
    │   ├── summary/
    │   └── metadata.json
    ├── indexes/                # 索引文件
    │   ├── tags_index.json     # 标签索引
    │   ├── emotion_timeline.json  # 情绪时间线
    │   └── processed_notes.json   # 已处理笔记跟踪
    └── analysis/               # 分析报告
        └── weekly_*.md
```

### 项目目录（保持干净）
```
your-project/
├── config/                     # 画像配置（可选）
│   ├── user-persona.md
│   └── ai-persona.md
├── notes/                      # 你的学习笔记（原文保留）
│   ├── react-learning.md       # 被处理后向量进入 skill/data/
│   └── python-tips.md
└── venv/                       # Python 虚拟环境
```

---

## 💡 使用示例

### 示例 1：自动处理笔记

**在项目中创建笔记：**

```markdown
# React Hooks 学习笔记

今天深入学习了 useState 和 useEffect！

## 代码示例

\`\`\`javascript
const [count, setCount] = useState(0);

useEffect(() => {
  document.title = `点击了 ${count} 次`;
}, [count]);
\`\`\`

太棒了，终于理解了依赖数组的作用！
```

**系统自动处理：**
```
✅ 检测到新笔记: react-learning.md
✅ 提取代码块: 1 个（JavaScript）
✅ 生成标签: ['javascript', 'react', 'hooks']
✅ 分析情绪: breakthrough (突破性理解)
✅ 思维层次: Level 4 (分析层)
✅ 生成 chunks: 2 个（笔记主体 + 代码块）
✅ 向量化存储: skill/data/vector_db/
```

### 示例 2：对话记忆

**第一天：**
```
你: 我在学习 React Hooks，感觉有点难理解
Claude: [回答并自动记录，向量化存储]
```

**一周后：**
```
你: useState 的更新是同步的还是异步的？
Claude: [自动检索到你之前学习过 React Hooks，给出个性化回答]
       "根据你上周的学习笔记，你已经理解了 useState 的基本用法..."
```

### 示例 3：跨项目知识共享

**项目 A：**
```
notes/react-best-practices.md
→ 向量化到 skill/data/vector_db/
```

**项目 B（几个月后）：**
```
你: React 中如何优化性能？
Claude: [自动检索到项目 A 的笔记]
       "根据你之前在项目 A 中学习的最佳实践..."
```

---

## 🔧 高级功能

### 手动处理笔记

```python
import sys
from pathlib import Path

# 添加 skill 脚本路径
sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))

from note_processor import check_and_process_notes

# 处理所有新笔记
result = check_and_process_notes()

print(f"处理了 {result['processed_count']} 个笔记")
for note in result['notes']:
    print(f"  📝 {note['file']}")
    print(f"     标签: {', '.join(note['tags'][:5])}")
    print(f"     代码块: {note['code_blocks']} 个")
```

### 获取系统统计

```python
from orchestrator import AIPartnerOrchestrator

orch = AIPartnerOrchestrator()
stats = orch.get_system_stats()

print(f"向量库: {stats['vector_db']['total_chunks']} chunks")
print(f"标签数: {stats['tags']['total_tags']}")
print(f"当前情绪: {stats['current_state']['state']}")
print(f"情绪趋势: {stats['current_state']['trend']}")
```

### 生成学习报告

```python
# 生成本周学习报告
report_path = orch.generate_weekly_report()
print(f"报告已生成: {report_path}")
```

**报告内容包括：**
- 📊 对话摘要（数量、主题分布）
- 🧠 学习深度分析（思维层次统计）
- 📈 情绪变化趋势
- 🏆 学习成就总结

---

## 🎨 架构设计

### 数据流架构

```
┌───────────────────────┐
│  项目 notes/ 目录      │
│  (原文件保留)          │
└───────────┬───────────┘
            ↓
    检测新笔记/修改
            ↓
┌───────────────────────┐
│  note_processor.py    │
│  - 扫描目录            │
│  - 检查状态            │
│  - 避免重复            │
└───────────┬───────────┘
            ↓
    提取内容/标签/代码
            ↓
┌───────────────────────┐
│  orchestrator.py      │
│  - 标签分析            │
│  - 情绪识别            │
│  - 思维层次评估        │
│  - 生成 chunks         │
└───────────┬───────────┘
            ↓
    BAAI/bge-m3 向量化
            ↓
┌───────────────────────┐
│  skill/data/vector_db │
│  (ChromaDB)           │
│  - 跨项目共享          │
│  - 语义检索            │
└───────────────────────┘
```

### 方案 B：集中存储设计

**优势：**
- ✅ 跨项目知识积累
- ✅ 数据永不丢失
- ✅ 项目目录干净
- ✅ 自动恢复历史

**关键设计：**
1. **原文保留** - 笔记永远在项目 `notes/` 中
2. **向量入库** - 内容向量化到 `skill/data/vector_db/`
3. **状态跟踪** - `processed_notes.json` 记录处理历史
4. **全局共享** - 所有项目共享同一个向量库

---

## 📊 数据安全

### 自动备份机制

`install.sh` 脚本的安全特性：

```bash
# 1. 安装前自动备份
💾 检测到现有数据目录，正在备份...
   备份位置: /tmp/ai-partner-data-backup-$$

# 2. 选择性删除（只删除代码）
🗑️  清理旧版本文件...
   保留: data/ 目录
   删除: scripts/, assets/, SKILL.md

# 3. 安装后自动恢复
♻️  恢复历史数据...
   ✅ 历史数据已恢复

# 4. 数据统计确认
📊 数据统计:
   - 向量库文件: 5
   - 对话记录: 1 个文件
```

### 数据位置

所有长期记忆数据存储在：
```
~/.claude/skills/ai-partner-chat/data/
```

**重要：重新安装不会丢失数据！**

---

## 🛠️ 故障排查

### 问题 1: 模型下载失败

```bash
# 手动下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

### 问题 2: ChromaDB 初始化错误

```bash
# 重建向量库（会丢失数据，谨慎使用）
rm -rf ~/.claude/skills/ai-partner-chat/data/vector_db
# 重新处理笔记即可恢复
```

### 问题 3: 笔记未被处理

```python
# 查看已处理笔记列表
import json
from pathlib import Path

state_file = Path.home() / '.claude/skills/ai-partner-chat/data/indexes/processed_notes.json'
with open(state_file) as f:
    print(json.dumps(json.load(f), indent=2))
```

### 问题 4: 虚拟环境未激活

```bash
# 检查 Python 路径
which python  # macOS/Linux，应显示 venv/bin/python
where python  # Windows，应包含 venv\Scripts\python
```

---

## 🤝 贡献指南

欢迎贡献代码、文档或提出建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Claude Code](https://code.claude.com/) - Anthropic 的 AI 编程助手
- [ChromaDB](https://www.trychroma.com/) - 开源向量数据库
- [BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) - 多语言嵌入模型

---

## 📞 联系方式

- GitHub Issues: [提交问题](https://github.com/YOUR_USERNAME/ai-partner-chat/issues)
- Discussions: [参与讨论](https://github.com/YOUR_USERNAME/ai-partner-chat/discussions)

---

**开始你的个性化 AI 学习之旅！** 🚀
