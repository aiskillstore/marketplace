---
name: Novel Library Batch Organizer
description: 批量整理本地小说库。先统一转码所有文件到 UTF-8 临时目录，再扫描分析、分层处理，最终输出到 NovelLibrary_Processed/ 保持原目录结构。
triggers:
  - 整理小说库
  - 批量整理小说
  - 排版小说
  - 统一章节
  - NovelLibrary 整理
---

# Novel Library Batch Organizer Skill

## 概述

本 Skill 采用三阶段流程：
1. 预处理：遍历 NovelLibrary/ 下所有文件，检测编码，统一转为 UTF-8 输出到 NovelLibrary_Temp/
2. 处理：所有后续操作（扫描、分层、排版、章节规范化）均基于 NovelLibrary_Temp/
3. 输出：最终结果输出到 NovelLibrary_Processed/，保持原目录结构

核心原则：
- 源文件只读，永不修改
- 统一编码后再处理，逻辑简洁可靠
- 经济优先：规整层零AI调用，半规整层优先自动映射，仅对杂糅候选使用 AI 识别，混乱层才全文 AI 处理
- 可恢复：支持断点续传（全局进度文件统一管理）

## AI 角色边界说明

本 Skill 是「指导型 Skill」，AI 的角色是：
1. 指导用户执行本地 Python 脚本
2. 在需要 AI 辅助识别时（半规整层/混乱层），处理用户粘贴的内容并返回结果
3. 解读脚本输出报告，给出下一步建议

AI 无法直接执行本地脚本或访问用户文件系统，所有脚本需要用户在本地终端中手动运行。

## 目录约定

./NovelLibrary/ 源目录（只读）
./NovelLibrary_Temp/ 临时目录（统一 UTF-8 编码）
./NovelLibrary_Processed/ 输出目录（最终结果）
./.organizer_progress/ 进度文件目录（包含全局进度和各阶段日志）

## ⚠️ 预处理安全警告

执行 Step 0 前请务必注意：
- `--temp` 指定的临时目录会被完全清空（递归删除所有内容）
- 请确保 `--temp` 目录不包含任何重要文件
- 不要将 `--temp` 设为源目录 `./NovelLibrary` 或当前工作目录 `.`
- 脚本包含安全检查，会阻止以下危险操作：
  - temp == source（临时目录等于源目录）
  - temp 是 source 的子目录或父目录
  - temp == 当前目录 (.)
  - temp == 用户主目录
- 清空已有临时目录前会有 5 秒倒计时，可随时按 Ctrl+C 取消

## 全局进度文件

位置：.organizer_progress/task_progress.json

格式：
{
  "task_id": "20260807_143022",
  "start_time": "2026-08-07T14:30:22",
  "last_update": "2026-08-07T15:45:10",
  "status": "in_progress",
  "phases": {
    "preprocess": {
      "status": "completed",
      "completed_at": "2026-08-07T14:35:00",
      "total_files": 150,
      "processed_files": 150,
      "failed_files": 0
    },
    "scan": {
      "status": "completed",
      "completed_at": "2026-08-07T14:50:00",
      "total_files": 150,
      "by_layer": {"regular": 120, "semi_regular": 20, "chaotic": 8, "error": 2}
    },
    "regular_layer": {
      "status": "completed",
      "completed_at": "2026-08-07T15:10:00",
      "total": 120,
      "processed": 120,
      "failed": 0
    },
    "semi_regular_layer": {
      "status": "in_progress",
      "current_file": "武侠/射雕英雄传.txt",
      "total": 20,
      "processed": 15,
      "failed": 0,
      "ai_calls": 3
    },
    "chaotic_layer": {
      "status": "pending",
      "total": 8,
      "processed": 0
    },
    "validate": {
      "status": "pending"
    }
  }
}

## 恢复机制

当用户说"继续整理小说库"时：
1. AI 读取 .organizer_progress/task_progress.json
2. 检查各阶段 status：
   - "completed"：跳过
   - "in_progress"：从该阶段断点继续
   - "pending"：开始执行
   - "failed"：提示用户检查错误
3. 每个阶段内部支持细粒度断点续传
4. 全部完成后将 status 更新为 "completed"

## 分层判断标准

扫描阶段对每个文件计算以下指标：

文件大小：< 500KB = 轻量，500KB-5MB = 中等，>5MB = 超大
章节匹配率：>80% = 规整，50%-80% = 半规整，<50% = 混乱
文本污染度：<1% = 清洁，1%-5% = 轻度，>5% = 重度

最终层级判定（注意边界情况）：
- 规整层：章节匹配率 >80% 且 污染度 <1%，或 章节匹配率 = 0 且 污染度 <1%（无章节短篇）
- 半规整层：章节匹配率 50%-80% 或（污染度 1%-5% 且 章节匹配率 >0）
- 混乱层：章节匹配率 <50% 或 污染度 >5%

## 工作流（用户执行）

### Step 0: 预处理（统一编码）

⚠️ 安全警告：临时目录会被完全清空，请确认不含重要文件！

用户执行：
python scripts/preprocess_encoding.py --source ./NovelLibrary --temp ./NovelLibrary_Temp --force

脚本自动：
- 遍历 NovelLibrary/ 下所有 .txt 文件，检测编码，统一转为 UTF-8
- 输出到 NovelLibrary_Temp/，保持目录结构
- 生成转码报告

### Step 1: 扫描与分类

用户执行：
python scripts/scan_and_classify.py --source ./NovelLibrary_Temp --output ./NovelLibrary_Processed

脚本自动计算章节匹配率和文本污染度，分层归类。

### Step 2: 分层处理

A. 规整层（零AI调用）：python scripts/clean_basic.py --batch
B. 半规整层：auto_chapter_map.py + chapter_replace.py 自动映射
C. 混乱层：split_chunks.py → AI逐块清洗 → merge_progress.py → renumber.py

⚠️ 混乱层和半规整层必须走完整的 AI 处理流程，不可使用批量跳过脚本，
    否则会导致标题格式混乱、元数据残留、首行非章节等质量问题。

### Step 3: 校验

python scripts/validate.py --source ./NovelLibrary_Temp --output ./NovelLibrary_Processed

报告三类问题：
1. 硬失败：未规范化标题残留、字符变化>10%、广告残留>5处
2. 连续性告警：章节编号不连续（原文固有结构，不影响 pass/fail）
3. 质量告警：首行非章节、元数据残留、裸标题（不影响 pass/fail）

## 章节标题规范化规则

脚本自动识别并转换以下所有格式的章节标题（所有单位统一转为 `章`）：

| 原始格式 | 转换后 | 示例 |
|---------|--------|------|
| 第X章/回/节 标题 | 保留 | 第3章 初次相遇 |
| 第一章/回/节 | 中文数字转阿拉伯 | 第一章 → 第1章 |
| Chapter X / CHAPTER X | 第X章 | Chapter 5 → 第5章 |
| （N）/ (N) | 第N章 | （3）→ 第3章 |
| （一）（二）（三）... | 第1章 第2章 第3章 | （一）→ 第1章 |
| 【N、标题】/ 【N，标题】 | 第N章 标题 | 【1、初次相遇】→ 第1章 初次相遇 |
| 一、标题 / 1、标题 | 第1章 标题 | 一、初次相遇 → 第1章 初次相遇 |
| 第一集/卷/部：标题 | 第1章 标题 | 第一集：初遇 → 第1章 初遇 |
| 正文 第一章... | 剥离前缀后转换 | 正文 第一章芙蓉出水 → 第1章 芙蓉出水 |
| 书名（N） | 保留为章节标题 | 楠楠的暴露（五）→ 第5章 |

### 特殊章节（不参与编号，保留原名）

- 序章 / 楔子 / 第零章 / 引子 / 前言 / 引言
- 尾声 / 后记 / 番外 / 外传 / 跋

### 转换规则

1. 只做格式转换，不重新编号（保留原文的章节数字）
2. 中文数字一律转为阿拉伯数字（一→1，十→10）
3. 装饰前缀（☆、※、正文 等）自动剥离
4. 章节单位（集/卷/部/回）统一转为 "章"
5. 每章标题独占一行，正文段落间用 1 个空行分隔

## 可用资源

### 脚本清单

scripts/preprocess_encoding.py : 统一转码所有文件到 UTF-8
scripts/scan_and_classify.py : 扫描、分层分析、生成报告
scripts/clean_basic.py : 规整层排版清洗 + 章节标题标准化（支持全部 10 种格式）
scripts/chapter_replace.py : 提取候选章节 / 根据映射表执行替换
scripts/auto_chapter_map.py : 半规整层自动映射（零AI处理）
scripts/split_chunks.py : 按章节边界自动分块
scripts/renumber.py : 合并后统一重新编号（1-N连续）
scripts/merge_progress.py : 合并分块结果，恢复断点
scripts/progress_manager.py : 全局进度管理
scripts/validate.py : 校验最终输出（标题格式、连续性、质量、广告）
scripts/chapter_patterns.py : 公共正则模块，所有脚本依赖。支持 第X章/回/节/集/卷/部、Chapter X、括号（N）（一）、【N、标题】、一、标题、正文前缀剥离

### AI 提示词模板

templates/prompt_chapter.md : 章节识别，输入候选行，输出映射表
templates/prompt_clean.md : 全文清洗，输入片段，输出排版文本

## 异常处理

编码检测失败：依次尝试 UTF-8 → GBK → GB18030 → Big5
分块时切断章节：回溯到最近的章节标题再切分
AI 返回格式错误：重试3次，仍失败则标记异常并跳过
输出字符数变化大于5%：标记异常，保留原样不输出
进度文件损坏：扫描已处理的输出目录重建进度
脚本执行失败：记录错误日志，继续处理下一个文件

## AI 处理最大重试次数

半规整层和混乱层调用 AI 时：
- 单个文件最多重试 3 次
- 连续 3 次失败后，标记该文件为 "failed" 并跳过
- 错误记录到 .organizer_progress/ai_errors.log
- 继续处理下一个文件，不阻塞整体流程