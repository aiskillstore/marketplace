---
name: ai-partner-chat
description: 基于用户画像和向量化笔记提供个性化对话。当用户需要个性化交流、上下文感知的回应，或希望 AI 记住并引用其之前的想法和笔记时使用。
---

# AI Partner Chat 2.0

## ⚠️ IMPORTANT: 自动学习工作流程

**Claude，你必须遵循以下自动化工作流程：**

### 1. 会话开始时 - 初始化系统

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))
from orchestrator import AIPartnerOrchestrator

orch = AIPartnerOrchestrator()
```

### 2. 每次对话后 - 自动记录对话

```python
orch.handle_conversation(
    user_message="[用户的完整问题]",
    ai_response="[你的完整回复]",
    save_conversation=True
)
```

**重要性判断：**
- 简单问候、确认：重要性 1-2（仅保存到文件）
- 技术讨论、问题解决：重要性 3-4（保存+向量化）
- 深度学习、关键决策：重要性 5（保存+向量化+重点标记）

### 3. 检测项目笔记 - 自动处理新笔记

**使用专用的笔记处理器（推荐）：**

```python
from note_processor import check_and_process_notes

# 自动检测并处理新笔记
result = check_and_process_notes()

print(f"✅ 已处理 {result['processed_count']} 个笔记")
for note in result['notes']:
    print(f"   📝 {note['file']}: {note['tags']}")
```

**触发条件（自动检测以下情况）：**
- ✅ 会话开始时主动检查 `notes/` 目录
- ✅ 用户提到"我写了笔记"、"更新了 notes"
- ✅ 用户要求"处理笔记"、"学习我的笔记"
- ✅ 用户创建或修改 .md 文件后

**笔记处理器特性：**
- 🔍 自动扫描项目 `notes/` 目录
- 📊 跟踪已处理笔记（避免重复处理）
- 🔄 检测修改时间，只处理新的或更新的笔记
- 💾 状态持久化到 `~/.claude/skills/ai-partner-chat/data/indexes/processed_notes.json`

### 4. 检索增强 - 使用长期记忆回答

**在回答问题前，先检索相关知识：**

```python
# 检索相关内容
context = orch.handle_conversation(
    user_message="[用户问题]",
    generate_response=True,
    save_conversation=False  # 暂不保存，等生成回复后再保存
)

# 使用 context['context']['search_results'] 中的内容来增强回复
# - notes: 用户之前的笔记
# - conversations: 历史对话
# - code: 相关代码片段
```

**注意事项：**
- ✅ 每次对话都必须记录，不要遗漏
- ✅ 主动检查 `notes/` 目录，处理新笔记
- ✅ 使用长期记忆增强回答质量
- ✅ 如果用户明确要求"不要记录"，则跳过
- ✅ 在虚拟环境中运行：确保已激活 `venv`
- ✅ 所有数据保存到 `~/.claude/skills/ai-partner-chat/data/`

---

## Overview

AI Partner Chat 2.0 是一个全功能的个性化 AI 学习私人长期伙伴系统,整合了以下核心能力:

**🧠 核心功能:**
- **智能标签系统** - 自动生成分层标签(主题/技术/自定义),实现高效组织和检索
- **对话历史记忆** - 记录和向量化重要对话,支持对话内容的智能检索
- **代码片段管理** - 自动识别、提取和分析笔记中的代码块,独立索引
- **状态感知对话** - 追踪学习状态和情绪变化,提供个性化回应
- **思维模式分析** - 分析学习深度和广度,生成个性化学习报告

**✨ 关键特性:**
- ✅ 多源检索 - 统一检索笔记、对话、代码片段
- ✅ 增量更新 - 无需重建数据库,即时添加新内容
- ✅ 状态感知 - AI 根据你的学习状态调整回应策略
- ✅ 自动分析 - 定期生成学习报告和对话摘要
- ✅ 完整历史 - 所有对话永久保存,重要对话向量化检索
- ✅ **自动记录** - Claude 在每次对话后自动保存到长期记忆

## Prerequisites

### 1. 创建 Python 虚拟环境

**为什么需要虚拟环境？**
- ✅ 隔离依赖，避免与系统 Python 包冲突
- ✅ 确保依赖版本一致性
- ✅ 不同项目可以使用不同版本的依赖

**创建虚拟环境：**

```bash
# 在项目目录创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r ~/.claude/skills/ai-partner-chat/scripts/requirements.txt
```

**注意事项:**
- 首次运行会自动下载嵌入模型 BAAI/bge-m3 (~4.3GB)
  - macOS/Linux: 模型缓存到 `~/.cache/huggingface/hub/`
  - Windows: 模型缓存到 `%USERPROFILE%\.cache\huggingface\hub\`
  - 系统会自动检测是否已缓存，避免重复下载
- 后续运行会直接使用缓存，加载速度很快（几秒钟）
- 每次使用前需要激活虚拟环境：
  - macOS/Linux: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`

**关于 torch.load 安全警告:**
- 依赖中使用 `transformers<4.50` 来避免 torch 2.6 依赖（macOS torch 2.6 尚未发布）
- transformers 4.50+ 强制要求 torch>=2.6 解决 CVE-2025-32434 安全漏洞
- 当前方案使用 `transformers==4.49.1` + `torch==2.5.1` 是安全的
- BAAI/bge-m3 模型使用 safetensors 格式，不受此漏洞影响
- 如果你使用的是 Linux/Windows 且需要最新版本，可以升级：
  ```bash
  pip install torch>=2.6 transformers>=4.50
  ```

### 2. 配置双画像系统（首次使用必须）

系统需要双画像文件来理解你和定义 AI 的行为：

**步骤 1: 复制模版文件到项目配置目录**

从 `~/.claude/skills/ai-partner-chat/assets/` 复制到项目的 `config/` 目录：

**macOS/Linux:**
```bash
# 创建配置目录
mkdir -p config

# 复制用户画像模版
cp ~/.claude/skills/ai-partner-chat/assets/user-persona-template.md config/user-persona.md

# 复制 AI 画像模版
cp ~/.claude/skills/ai-partner-chat/assets/ai-persona-template.md config/ai-persona.md
```

**Windows:**
```powershell
# 创建配置目录
mkdir config

# 复制用户画像模版
copy %USERPROFILE%\.claude\skills\ai-partner-chat\assets\user-persona-template.md config\user-persona.md

# 复制 AI 画像模版
copy %USERPROFILE%\.claude\skills\ai-partner-chat\assets\ai-persona-template.md config\ai-persona.md
```

**步骤 2: 自定义你的画像**

编辑项目 `config/` 目录中的文件：

- **`config/user-persona.md`** - 描述你的背景、学习风格、沟通偏好
- **`config/ai-persona.md`** - 定义 AI 的角色、回复风格、个性

**为什么需要复制？**
- ✅ `assets/` 中的模版保持不变，供参考
- ✅ `config/` 中的文件是你的自定义版本
- ✅ 每个项目可以有不同的画像配置
- ✅ Python 代码会读取项目 `config/` 目录中的画像

### 3. 目录结构说明

**重要改进：长期记忆设计**

系统采用集中存储设计，所有运行时数据存放在 skill 目录，实现真正的长期学习伙伴：

```
~/.claude/skills/ai-partner-chat/
├── scripts/                   # Python 模块
│   ├── orchestrator.py
│   ├── note_processor.py
│   └── ... (其他模块)
├── assets/                    # 模版文件
│   ├── user-persona-template.md
│   └── ai-persona-template.md
├── notes-examples/            # 笔记示例（仅供参考）
│   └── example-learning.md
└── data/                      # 运行时数据（自动创建）
    ├── vector_db/             # 统一向量库（长期记忆）
    │   └── chroma.sqlite3     # ⚡ 所有笔记/对话/代码的向量都在这里
    ├── conversations/         # 对话历史
    │   ├── raw/
    │   │   └── YYYY-MM/
    │   │       └── YYYY-MM-DD.md  # 按日期组织的对话
    │   ├── summary/
    │   └── metadata.json
    ├── indexes/               # 索引文件
    │   ├── tags_index.json
    │   ├── emotion_timeline.json
    │   └── processed_notes.json   # 已处理笔记跟踪
    └── analysis/              # 分析报告
        └── weekly_*.md

your-project/                  # 用户项目（干净）
├── config/                    # 画像配置（可选）
│   ├── user-persona.md
│   └── ai-persona.md
├── notes/                     # ⚡ 你的笔记（项目本地，原文保留）
│   └── *.md                   #    被处理后向量进入 skill/data/vector_db
└── venv/                      # 虚拟环境
```

**核心特性：**
- ✅ **长期记忆** - 所有学习历史累积在 skill 目录，永不丢失
- ✅ **跨项目复用** - 项目 A 学的知识，项目 B 也能用
- ✅ **项目干净** - 用户项目只有 config 和 notes
- ✅ **自动恢复** - 每次启动自动加载历史数据

**数据流说明：**
```
项目 notes/ 中的笔记
    ↓ (检测到新笔记)
note_processor.py 处理
    ↓ (提取内容、标签、代码)
orchestrator.process_new_note()
    ↓ (生成 chunks)
vector_indexer.append_chunks()
    ↓ (向量化)
skill/data/vector_db/  ← 向量存储（长期记忆）
    ↓
跨项目可检索！

原笔记文件 → 保留在项目 notes/ 中
```

**重要：**
- 📝 **原文件保留** - 你的笔记永远在项目 `notes/` 目录，不会被移动或删除
- 🔍 **向量入库** - 笔记内容被向量化后存入 `skill/data/vector_db/`
- 🌐 **跨项目共享** - 向量库是全局的，所有项目共享同一个知识库
- 📊 **状态跟踪** - `processed_notes.json` 记录哪些笔记已处理，避免重复

**手动创建目录：**
```bash
# 项目目录只需创建 notes
mkdir -p notes

# config 从模版复制（已在步骤2完成）
# data 目录会自动创建在 skill 目录，无需手动操作
```

### 4. 首次运行检查清单

在开始使用系统前，请确认以下步骤：

- [ ] **虚拟环境已创建并激活**
  ```bash
  # 检查虚拟环境
  which python  # macOS/Linux，应显示 venv/bin/python
  where python  # Windows，应包含 venv\Scripts\python
  ```

- [ ] **依赖已安装**
  ```bash
  python -c "import chromadb; print('✅ chromadb')"
  python -c "import sentence_transformers; print('✅ sentence-transformers')"
  ```

- [ ] **双画像已配置**
  ```bash
  # 检查画像文件是否存在
  ls config/user-persona.md config/ai-persona.md  # macOS/Linux
  dir config\user-persona.md config\ai-persona.md  # Windows
  ```

- [ ] **笔记目录已创建**
  ```bash
  mkdir -p notes  # 创建笔记目录（如果不存在）
  ```

- [ ] **测试运行**
  ```python
  import sys
  from pathlib import Path
  sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))

  from orchestrator import AIPartnerOrchestrator
  orch = AIPartnerOrchestrator()  # 应该看到 "✅ AI Partner 协调器已初始化"
  ```

### 5. 长期记忆工作原理

**首次使用（新用户）:**
```python
>>> orch = AIPartnerOrchestrator()
✅ AI Partner 协调器已初始化
   项目: ai-partner-chat
   数据: ~/.claude/skills/ai-partner-chat/data/
   向量库: 0 chunks
```

**3 天后使用（自动恢复记忆）:**
```python
>>> orch = AIPartnerOrchestrator()
✅ AI Partner 协调器已初始化
   项目: ai-partner-chat
   数据: ~/.claude/skills/ai-partner-chat/data/
   向量库: 25 chunks  ← 自动加载历史！
   💭 长期记忆已加载
```

**3 个月后使用（长期记忆）:**
```python
>>> orch = AIPartnerOrchestrator()
✅ AI Partner 协调器已初始化
   向量库: 1,250 chunks  ← 3 个月的学习积累！
   💭 长期记忆已加载

>>> context = orch.handle_conversation("useCallback 怎么用?")
🔍 检索结果:
   📝 相关笔记 (3条) - 包含 90 天前的笔记
   💬 相关对话 (2条) - AI 记得你之前问过
```

**AI 回复示例:**
```
你好！看到你又回来学习 React 了 😊

根据你 3 个月前的笔记，你已经掌握了 useCallback 的基础。
那时候你在性能优化项目中成功应用了它...
```

现在可以开始使用系统 →

## 完整工作流程

### 流程 1: 添加新笔记

```python
import sys
from pathlib import Path

# 添加 skill 脚本路径
sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))
from orchestrator import AIPartnerOrchestrator

orch = AIPartnerOrchestrator()

result = orch.process_new_note(
    note_path="./notes/学习笔记.md",
    content=open("./notes/学习笔记.md").read()
)
```

**返回结果:**
```python
{
    'chunks_created': 5,
    'chunks_indexed': 5,
    'tags': ['React', 'Hooks', 'JavaScript'],
    'emotion': {'state': 'breakthrough', 'excitement': 8},
    'thinking_level': 3,
    'code_blocks': 4
}
```

### 流程 2: 处理对话

```python
# 获取上下文
result = orch.handle_conversation(
    user_message="React Hooks 的 useState 为什么要用数组解构?",
    save_conversation=False
)

context = result['context']
user_message = context['user_message']
ai_response = your_ai_generate_response(context)

# 保存对话
orch.handle_conversation(
    user_message=user_message,
    ai_response=ai_response,
    save_conversation=True
)
```

### 流程 3: 生成报告

```python
report_path = orch.generate_weekly_report()
```

### 流程 4: 查看统计

```python
stats = orch.get_system_stats()
```

## 核心模块说明

### 1. 双画像系统

画像配置已在 Prerequisites 中说明，这里简述其工作原理：

**工作流程:**
1. Python 代码启动时读取项目 `config/` 目录中的画像文件
2. 将画像内容传递给 LLM 作为系统提示词
3. LLM 根据画像调整回复风格和策略

**关键点:**
- 用户画像（user-persona.md）让 AI 了解你的背景和学习风格
- AI 画像（ai-persona.md）定义 AI 的角色和回应策略
- 每个项目可以有不同的画像配置，实现项目级隔离

**示例场景:**
```markdown
# config/user-persona.md
## 学习风格
- 喜欢从原理出发,理解底层机制
- 偏好实践驱动,通过代码加深理解

# config/ai-persona.md
## 沟通风格
- 语气友好但专业
- 先给出核心原理,再展开细节
- 使用具体代码示例说明抽象概念
- 适时鼓励,认可学习进步

## 上下文使用
- 自然引用用户的笔记: "根据你之前学习的 useState..."
- 建立知识关联: "这和你上周学的 useEffect 闭包问题类似"
- 追踪学习状态: 根据情绪和思维层次调整回应
- 避免重复: 不重复用户已经理解的内容
```

**画像在系统中的作用:**

1. **个性化检索**: 系统会根据用户画像调整检索策略
2. **状态感知回应**: 结合情绪分析,AI 画像指导回应风格
3. **知识关联**: AI 画像定义如何引用历史笔记和对话
4. **持续改进**: 可随时更新画像,反映学习进展

### 1. 统一数据模型 (chunk_schema.py)

所有内容(笔记/对话/代码)都统一为 **Chunk** 格式:

```python
{
    'content': '内容文本',
    'metadata': {
        # === 基础字段 ===
        'filename': 'note.md',
        'filepath': '/path/to/file',
        'chunk_id': 0,
        'chunk_type': 'note' | 'conversation' | 'code',

        # === 标签系统 ===
        'tags': ['React', 'Hooks', 'JavaScript'],
        'tag_layers': {
            'topic': ['学习笔记', 'Web开发'],
            'tech': ['React', 'JavaScript'],
            'custom': []
        },

        # === 对话记忆 ===
        'conversation_id': 'conv_20251115_143022',
        'importance': 4,  # 1-5 分

        # === 代码管理 ===
        'language': 'javascript',
        'function_name': 'useState',
        'purpose': 'React状态管理Hook',

        # === 状态追踪 ===
        'emotion': {
            'state': 'breakthrough',
            'excitement': 8,
            'confusion': 2
        },

        # === 思维分析 ===
        'thinking_level': 3,  # 1-4 级

        'date': '2025-11-15',
        'created_at': '2025-11-15T14:30:22'
    }
}
```

### 2. 核心协调器 (orchestrator.py)

**AIPartnerOrchestrator** 是整个系统的大脑,串联所有功能:

**主要方法:**
- `process_new_note(note_path, content)` - 处理新笔记全流程
- `handle_conversation(user_msg, ai_msg)` - 处理对话全流程
- `generate_weekly_report()` - 生成周报
- `get_system_stats()` - 获取系统统计

### 3. 标签系统

**TagGenerator** - 自动生成分层标签
- 提取主题标签(学习笔记、技术文档等)
- 提取技术标签(React、Python等)
- 支持自定义标签

**TagIndexer** - 标签索引管理
- 快速按标签检索文件
- 标签统计分析
- 标签关系网络

### 4. 对话记忆 (conversation_logger.py)

**功能:**
- 所有对话保存为 Markdown (按日期组织)
- 自动评估对话重要性 (1-5 分)
- 重要对话向量化 (≥3 分)
- 生成每周对话摘要

**存储结构:**
```
conversations/
├── raw/
│   └── 2025-11/
│       ├── 2025-11-15.md
│       └── 2025-11-16.md
├── summary/
│   └── weekly-2025-W46.md
└── metadata.json
```

### 5. 代码管理 (code_parser.py)

**功能:**
- 自动识别 Markdown 中的代码块
- 提取函数名、参数、依赖
- 分析代码复杂度
- 独立向量化索引

**支持语言:**
- Python - 函数、类、导入识别
- JavaScript/TypeScript - 函数、导入识别
- 其他语言 - 基础识别

### 6. 状态追踪 (emotion_analyzer.py)

**追踪的学习状态:**
- `exploration` - 探索期
- `confusion` - 困惑期
- `breakthrough` - 突破期
- `consolidation` - 巩固期
- `burnout` - 倦怠期

**情绪时间线:**
```json
[
  {
    "date": "2025-11-15",
    "state": "breakthrough",
    "excitement": 8,
    "confidence": 7,
    "confusion": 2,
    "notes_count": 3
  }
]
```

### 7. 思维分析 (thinking_analyzer.py)

**思维层次 (1-4 级):**
- Level 1: 记录事实 - "今天学了 useState"
- Level 2: 理解原理 - "useState 通过闭包保存状态"
- Level 3: 形成洞察 - "原来 Hooks 解决了类组件的复杂性"
- Level 4: 创新应用 - "设计了一个自定义 Hook 解决..."

**学习报告内容:**
- 整体统计 (笔记/对话/代码数量)
- 主题分布分析
- 思维层次分布
- 个性化建议

## 快速开始

**⚠️ 重要**: 使用前请确保已激活虚拟环境

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 方案 A: 使用协调器（推荐）

最简单的方式 - 所有功能一行搞定:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))
from orchestrator import AIPartnerOrchestrator

# 初始化
orch = AIPartnerOrchestrator()

# 添加笔记
result = orch.process_new_note(
    note_path="./notes/my_note.md",
    content=open("./notes/my_note.md").read()
)
print(f"✅ 已处理: {result['chunks_created']} chunks")

# 对话交互
context = orch.handle_conversation(
    user_message="React Hooks 怎么用?",
    generate_response=True
)

# 基于上下文生成 AI 回复
ai_response = your_ai_function(context)

# 记录对话
orch.handle_conversation(
    user_message="React Hooks 怎么用?",
    ai_response=ai_response
)

# 生成报告
orch.generate_weekly_report()
```

### 方案 B: 使用独立模块

如果需要更细粒度的控制:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))
from tag_generator import TagGenerator
from emotion_analyzer import EmotionAnalyzer
from vector_indexer import VectorIndexer

# 标签分析
tag_gen = TagGenerator()
tags = tag_gen.generate_tag_layers(content)

# 情绪分析
emotion = EmotionAnalyzer()
state = emotion.analyze_emotion(content)

# 向量化
indexer = VectorIndexer()
indexer.append_chunks(chunks)
```

## 数据流图解

```
┌─────────────────┐
│  新笔记 note.md │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│     Orchestrator.process_new_note()       │
│                                            │
│  ┌──────────────┐  ┌─────────────────┐    │
│  │ TagGenerator │  │ EmotionAnalyzer │    │
│  │ 提取标签      │  │ 分析情绪状态     │    │
│  └──────────────┘  └─────────────────┘    │
│                                            │
│  ┌──────────────┐  ┌─────────────────┐    │
│  │ CodeParser   │  │ ThinkingAnalyz  │    │
│  │ 提取代码      │  │ 判断思维层次     │    │
│  └──────────────┘  └─────────────────┘    │
│                                            │
│         ▼                                  │
│  生成 Chunks (笔记主体 + 代码块)             │
│         │                                  │
└─────────┼──────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  VectorIndexer      │
│  增量向量化 (append) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  ChromaDB           │
│  向量数据库           │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐       ┌──────────────┐
│  MultiSource        │◄──────│ 用户查询      │
│  Retriever          │       └──────────────┘
│  多源检索            │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────────┐
│  检索结果:                       │
│  - 相关笔记 (top 3)              │
│  - 相关对话 (top 2)              │
│  - 相关代码 (top 2)              │
│  + 当前学习状态                  │
└─────────┬───────────────────────┘
          │
          ▼
┌─────────────────────┐
│  生成 AI 回复        │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────────────┐
│  ConversationLogger              │
│  - 保存 Markdown                 │
│  - 评估重要性                     │
│  - 向量化 (if 重要性 ≥ 3)         │
└──────────────────────────────────┘
```

## 项目结构

```
<project_root>/
├── notes/                        # 📝 用户笔记 (Markdown)
│   └── *.md
│
├── assets/                       # 🎨 双画像模版（不要修改，供复制参考）
│   ├── user-persona-template.md # 用户画像模版
│   └── ai-persona-template.md   # AI 画像模版
│
├── config/                       # ⚙️  配置文件（首次使用必须创建）
│   ├── user-persona.md          # 你的用户画像（从 assets 复制后自定义）
│   ├── ai-persona.md            # 你的 AI 画像（从 assets 复制后自定义）
│   └── tags_taxonomy.json       # 标签分类规则（可选）
│
├── conversations/                # 💬 对话历史（运行时自动生成）
│   ├── raw/                      # 原始对话 (按月份/日期)
│   │   └── 2025-11/
│   │       └── 2025-11-15.md
│   ├── summary/                  # 对话摘要
│   │   └── weekly-2025-W46.md
│   └── metadata.json             # 对话元数据
│
├── analysis/                     # 📊 分析数据（运行时自动生成）
│   ├── emotion_timeline.json    # 情绪时间线
│   └── reports/                  # 学习报告
│       └── learning_report_本周.md
│
├── indexes/                      # 🗂️  索引数据（运行时自动生成）
│   └── tags_index.json           # 标签索引
│
├── vector_db/                    # 💾 ChromaDB 向量数据库（运行时自动生成）
│   └── chroma.sqlite3
│
├── venv/                         # 🐍 Python 虚拟环境
│   ├── bin/                      # 可执行文件
│   ├── lib/                      # 依赖包
│   └── pyvenv.cfg
│
├── scripts/                      # 🔧 核心脚本
│   ├── orchestrator.py          # ⭐ 核心协调器（主入口）
│   ├── chunk_schema.py          # 数据模型定义
│   ├── vector_indexer.py        # 向量化索引
│   ├── vector_utils.py          # 多源检索
│   ├── tag_generator.py         # 标签生成器
│   ├── tag_indexer.py           # 标签索引
│   ├── conversation_logger.py   # 对话记录器
│   ├── code_parser.py           # 代码解析器
│   ├── emotion_analyzer.py      # 情绪分析器
│   ├── thinking_analyzer.py     # 思维分析器
│   ├── example_usage.py         # 使用示例
│   └── requirements.txt         # Python 依赖
```

**依赖安装**: 在虚拟环境中安装
```bash
# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r ~/.claude/skills/ai-partner-chat/scripts/requirements.txt
```

## 技术细节

### 向量数据库

- **存储引擎**: ChromaDB (本地持久化)
- **嵌入模型**: BAAI/bge-m3 (1024维, ~4.3GB)
  - 优化中文语义理解
  - 多语言支持
  - 高质量向量表示
- **相似度算法**: Cosine Similarity
- **更新模式**: 增量追加 (append) - 无需重建整个数据库

### 性能优化

**关键突破 - 增量更新:**

```python
# ✅ 新方案: 增量追加,秒级完成
indexer.append_chunks(new_chunks)  # 仅几秒钟
```

**多源检索优化:**
- 并行查询笔记/对话/代码
- 按 chunk_type 过滤
- 自动聚合结果

### 数据模型

**统一 Chunk 格式** - 所有内容类型共享相同结构:
- 笔记 chunks: 包含标签、情绪、思维层次
- 对话 chunks: 包含重要性评分、主题
- 代码 chunks: 包含语言、函数名、复杂度

**元数据扁平化** - ChromaDB 限制:
- 复杂类型 (dict/list) 自动转换为 JSON 字符串
- 检索时自动解析回原始类型

## 最佳实践

### 笔记组织

**推荐格式:**
- Markdown 格式,支持任意结构
- 包含代码块时使用三个反引号标注语言
- 添加清晰的标题和段落

**示例:**
```markdown
# React Hooks 学习

今天深入学习了 useState,终于理解了状态更新的原理!

## 基础用法

`​``javascript
const [count, setCount] = useState(0);
`​``

原来每次调用 setCount 都会触发重新渲染,这太好了!

## 注意事项

- 不要在循环/条件中调用 Hooks
- state 更新是异步的
```

### 对话策略

**如何让 AI 回复更个性化:**

1. **充分利用状态感知**
   ```python
   # AI 会根据你的学习状态调整回应
   # 困惑期: 更详细的解释,更多示例
   # 突破期: 鼓励深入思考,提供进阶内容
   # 巩固期: 实践项目建议,知识关联
   ```

2. **利用多源检索**
   - 系统会自动查找相关笔记、对话、代码
   - 无需重复提供背景信息
   - AI 能记住你之前的学习轨迹

3. **重要对话会被记住**
   - 重要性 ≥ 3 分的对话会向量化
   - 未来对话可以引用之前的讨论
   - 形成连贯的学习上下文

### 标签管理

**标签会自动生成,但你可以优化:**

创建 `config/tags_taxonomy.json`:
```json
{
  "topic_tags": ["学习笔记", "技术文档", "项目规划", "问题解决"],
  "tech_tags": ["React", "Python", "JavaScript", "TypeScript", "SQL"],
  "custom_tags": []
}
```

### 定期维护

**每周操作:**
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.claude/skills/ai-partner-chat/scripts'))
from orchestrator import AIPartnerOrchestrator
orch = AIPartnerOrchestrator()

# 生成周报
report = orch.generate_weekly_report()

# 查看系统状态
stats = orch.get_system_stats()
```

**每月操作:**
- 审阅学习报告,调整学习方向
- 清理过期的临时笔记
- 更新 user-persona.md 反映成长

## 常见问题

### Q: 为什么要用增量更新而不是重建数据库?

**A:** 性能差异巨大:
- 重建: 1000 chunks ≈ 5-10 分钟
- 增量: 10 chunks ≈ 5 秒

随着内容增长,重建会越来越慢,增量更新始终快速。

### Q: 对话重要性是如何评估的?

**A:** 简单规则 + 长度判断:
- 包含"突破"、"理解"等关键词 → 高分
- 长对话(>500字符)→ 可能重要
- 寒暄、简单确认 → 低分

生产环境可用 LLM 替换规则。

### Q: 代码块能识别哪些信息?

**A:** 当前支持:
- 语言识别 (Python, JS, TS 等)
- 函数名和参数 (Python/JS)
- import/from 依赖
- 代码复杂度估算

可扩展为使用 AST 进行深度分析。

### Q: 如何自定义情绪分析?

**A:** 编辑 `emotion_analyzer.py`:
```python
# 修改关键词列表
excitement_keywords = ['太好了', '明白了', '成功', ...]
confusion_keywords = ['不懂', '困惑', '难', ...]
```

或使用 LLM:
```python
# 使用提供的 EMOTION_ANALYSIS_PROMPT 提示词
# 调用你的 LLM API 进行情绪分析
```

### Q: 向量数据库占用多少空间?

**A:** 估算:
- 嵌入模型: ~4.3GB (一次性)
- 每个 chunk: ~5KB (1024维向量 + 元数据)
- 1000 chunks ≈ 5MB
- 10000 chunks ≈ 50MB

空间占用很小,主要是嵌入模型。

### Q: 可以用其他嵌入模型吗?

**A:** 可以,修改 `vector_indexer.py`:
```python
from sentence_transformers import SentenceTransformer

# 替换模型
self.model = SentenceTransformer('your-model-name')
```

推荐中文模型:
- BAAI/bge-m3 (当前使用)
- BAAI/bge-large-zh-v1.5
- moka-ai/m3e-base

## 故障排查

### 问题 1: ValueError: Due to torch.load CVE-2025-32434

**症状:**
```
ValueError: Due to a serious vulnerability issue in `torch.load`, even with
`weights_only=True`, we now require users to upgrade torch to at least v2.6
```

**原因**: transformers 4.50+ 强制要求 torch>=2.6，但 macOS 的 torch 2.6 尚未发布

**解决方案:**

**macOS 用户（推荐）:**
```bash
# 使用当前配置（transformers 4.49.1 + torch 2.5.1）
# 这是安全的，因为 BAAI/bge-m3 使用 safetensors 格式
pip install -r ~/.claude/skills/ai-partner-chat/scripts/requirements.txt
```

**Linux/Windows 用户（可选升级）:**
```bash
# 如果需要最新版本
pip install torch>=2.6 transformers>=4.50
```

**补充说明:**
- BAAI/bge-m3 模型文件使用 safetensors 格式（不受 torch.load 漏洞影响）
- transformers<4.50 的配置是安全的，专门为 macOS 兼容性设计
- 等 macOS torch 2.6 发布后可以升级到最新版本

### 问题 2: ModuleNotFoundError: No module named 'chromadb'

**原因**: Python 环境不一致，依赖安装到了不同的 Python

**解决方案**:
```bash
# 1. 确保虚拟环境已激活
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 2. 确认当前 Python
which python  # macOS/Linux，应显示 venv/bin/python
where python  # Windows，应包含 venv\Scripts\python

# 3. 重新安装依赖到当前环境
pip install -r ~/.claude/skills/ai-partner-chat/scripts/requirements.txt

# 4. 验证安装
python -c "import chromadb; print('✅ chromadb 已安装')"
```

### 问题 3: 对话没有保存

**原因**: 调用 `handle_conversation` 时未正确设置参数

**解决方案**:
```python
# 方式 1 - 两步调用（推荐）
result = orch.handle_conversation(
    user_message=user_msg,
    save_conversation=False
)
orch.handle_conversation(
    user_message=user_msg,
    ai_response=ai_response,
    save_conversation=True
)

# 方式 2 - 一步调用（默认保存）
orch.handle_conversation(
    user_message=user_msg,
    ai_response=ai_response
)
```

### 问题 4: 模型重复下载

**原因**: 模型缓存路径不对或被清理

**检查缓存**:
```bash
# macOS/Linux
ls ~/.cache/huggingface/hub/models--BAAI--bge-m3

# Windows
dir %USERPROFILE%\.cache\huggingface\hub\models--BAAI--bge-m3
```

**如果缓存存在但仍然下载**: 环境变量可能不对
```bash
# 设置缓存目录
export HF_HOME=~/.cache/huggingface  # macOS/Linux
set HF_HOME=%USERPROFILE%\.cache\huggingface  # Windows
```

### 问题 5: 虚拟环境激活失败

**Windows PowerShell 权限问题**:
```powershell
# 如果报错: 无法加载文件，因为在此系统上禁止运行脚本
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后再激活
venv\Scripts\activate
```

**macOS/Linux 权限问题**:
```bash
# 如果 venv/bin/activate 没有执行权限
chmod +x venv/bin/activate
source venv/bin/activate
```

### 问题 6: FileNotFoundError: config/user-persona.md 不存在

**症状**: 初始化时报错找不到画像文件

**原因**: 没有从 assets 复制画像模版到项目 config 目录

**解决方案**:
```bash
# macOS/Linux
mkdir -p config
cp ~/.claude/skills/ai-partner-chat/assets/user-persona-template.md config/user-persona.md
cp ~/.claude/skills/ai-partner-chat/assets/ai-persona-template.md config/ai-persona.md

# Windows
mkdir config
copy %USERPROFILE%\.claude\skills\ai-partner-chat\assets\user-persona-template.md config\user-persona.md
copy %USERPROFILE%\.claude\skills\ai-partner-chat\assets\ai-persona-template.md config\ai-persona.md
```

然后编辑 `config/user-persona.md` 和 `config/ai-persona.md` 自定义你的画像。

### 问题 7: 导入路径错误

**症状**: `ModuleNotFoundError: No module named 'orchestrator'`

**原因**: sys.path 没有正确设置

**解决方案**:
```python
import sys
from pathlib import Path

# 获取用户home目录
skills_path = Path.home() / '.claude' / 'skills' / 'ai-partner-chat' / 'scripts'
sys.path.insert(0, str(skills_path))

# 现在可以导入
from orchestrator import AIPartnerOrchestrator
```

## 进阶功能

### 使用 LLM 增强分析

系统预留了 LLM 提示词模板,可用于更精确的分析:

**1. 情绪分析** (emotion_analyzer.py)
```python
from emotion_analyzer import EMOTION_ANALYSIS_PROMPT

# 使用 LLM 替换简单规则
prompt = EMOTION_ANALYSIS_PROMPT.format(content=note_content)
emotion_result = your_llm_api(prompt)
```

**2. 代码分析** (code_parser.py)
```python
from code_parser import CODE_ANALYSIS_PROMPT

prompt = CODE_ANALYSIS_PROMPT.format(
    language='python',
    code=code_snippet
)
code_analysis = your_llm_api(prompt)
```

**3. 对话重要性评估** (conversation_logger.py)
```python
from conversation_logger import IMPORTANCE_EVALUATION_PROMPT

prompt = IMPORTANCE_EVALUATION_PROMPT.format(
    user_message=user_msg,
    ai_response=ai_msg
)
importance_score = your_llm_api(prompt)
```

### 自定义工作流

基于 Orchestrator 构建自己的工作流:

```python
from scripts.orchestrator import AIPartnerOrchestrator

class MyCustomWorkflow(AIPartnerOrchestrator):
    def process_daily_notes(self):
        """每日笔记批量处理"""
        today = datetime.now().strftime('%Y-%m-%d')
        daily_notes = Path('./notes').glob(f'*{today}*.md')

        for note in daily_notes:
            result = self.process_new_note(
                str(note),
                note.read_text()
            )
            print(f"✅ {note.name}: {result['chunks_created']} chunks")

    def generate_monthly_insights(self):
        """月度深度分析"""
        # 获取最近 30 天的所有内容
        chunks = self.retriever.get_recent(days=30, top_k=500)

        # 生成深度报告
        report = self.thinking_analyzer.generate_learning_report(
            chunks,
            period="本月"
        )

        # 生成知识图谱
        # ... 自定义分析逻辑
```

## 版本历史

### v2.0 (当前版本)

**新增功能:**
- ✅ 智能标签系统 (分层标签)
- ✅ 对话历史记忆 (重要性评分)
- ✅ 代码片段管理 (独立索引)
- ✅ 状态感知对话 (情绪追踪)
- ✅ 思维模式分析 (学习报告)

**核心突破:**
- ✅ 增量更新 - 10x+ 性能提升
- ✅ 多源检索 - 统一检索笔记/对话/代码
- ✅ 统一数据模型 - 所有内容类型共享架构

**技术改进:**
- ✅ 重构 chunk_schema - 完整元数据支持
- ✅ 重构 vector_indexer - append 模式
- ✅ 重构 vector_utils - MultiSourceRetriever
- ✅ 新增 orchestrator - 核心协调器


## 总结

AI Partner Chat 2.0 是一个**完整的个性化学习伙伴系统**,通过整合 5 大核心功能:

1. **标签系统** - 自动组织和分类
2. **对话记忆** - 记住重要讨论
3. **代码管理** - 独立索引代码片段
4. **状态追踪** - 感知学习状态
5. **思维分析** - 生成学习洞察

实现了:
- 📝 **智能笔记管理** - 自动标签、代码提取、情绪分析
- 💬 **连贯对话体验** - 多源检索、状态感知、历史记忆
- 📊 **学习洞察报告** - 思维层次分析、主题分布、个性化建议
- ⚡ **高性能更新** - 增量追加,秒级完成

**使用起来很简单:**
```python
from scripts.orchestrator import AIPartnerOrchestrator
orch = AIPartnerOrchestrator()

# 一行代码处理笔记
orch.process_new_note(note_path, content)

# 一行代码处理对话
context = orch.handle_conversation(user_msg)

# 一行代码生成报告
orch.generate_weekly_report()
```

享受你的 AI 私人长期伙伴学习伙伴! 🚀