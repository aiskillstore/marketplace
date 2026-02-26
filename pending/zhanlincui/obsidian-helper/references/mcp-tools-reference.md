# Obsidian MCP 工具参考

本文档为 obsidian-helper skill 提供 MCP 工具使用参考。

## 常用工具速查

### 获取周期笔记

```javascript
// 获取今日日记
obsidian_get_periodic_note(period: "daily")

// 获取最近5篇日记（含内容）
obsidian_get_recent_periodic_notes(
  period: "daily",
  limit: 5,
  include_content: true
)
```

### 搜索笔记

```javascript
// 简单文本搜索
obsidian_simple_search(
  query: "API设计",
  context_length: 100
)

// 复杂搜索 - 按文件夹
obsidian_complex_search({
  "glob": ["Resources/*.md", {"var": "path"}]
})

// 复杂搜索 - 按标签（在内容中搜索）
obsidian_simple_search(query: "#project")
```

### 读取内容

```javascript
// 单文件读取
obsidian_get_file_contents(filepath: "Daily Notes/2026-01-19.md")

// 批量读取
obsidian_batch_get_file_contents(filepaths: [
  "Daily Notes/2026-01-19.md",
  "Daily Notes/2026-01-18.md"
])
```

### 写入内容

```javascript
// 追加内容（或创建新文件）
obsidian_append_content(
  filepath: "Resources/新笔记.md",
  content: "# 标题\n\n内容..."
)

// 精确位置编辑 - 在标题下追加
obsidian_patch_content(
  filepath: "Daily Notes/2026-01-19.md",
  operation: "append",
  target_type: "heading",
  target: "待办事项",
  content: "- [ ] 新任务"
)

// 精确位置编辑 - 替换 frontmatter
obsidian_patch_content(
  filepath: "Projects/项目A.md",
  operation: "replace",
  target_type: "frontmatter",
  target: "status",
  content: "completed"
)
```

### 文件管理

```javascript
// 列出目录内容
obsidian_list_files_in_dir(dirpath: "Daily Notes")

// 列出库根目录
obsidian_list_files_in_vault()

// 获取最近修改的文件
obsidian_get_recent_changes(limit: 10, days: 7)
```

## 典型工作流

### /daily 工作流

1. `obsidian_get_periodic_note(period: "daily")` - 获取今日日记
2. `obsidian_get_recent_periodic_notes(period: "daily", limit: 2, include_content: true)` - 获取昨日日记
3. 解析昨日未完成任务（查找 `- [ ]` 模式）
4. `obsidian_append_content` 或 `obsidian_patch_content` - 创建/更新今日日记

### /capture 工作流

1. `obsidian_simple_search(query: "<主题>")` - 搜索相关笔记
2. 如果找到：`obsidian_patch_content` - 追加到现有笔记
3. 如果未找到：`obsidian_append_content` - 创建新笔记

### /review 工作流

1. `obsidian_get_recent_periodic_notes(period: "daily", limit: 7, include_content: true)` - 获取一周日记
2. `obsidian_get_recent_changes(days: 7)` - 获取最近修改
3. 分析内容，生成报告
4. `obsidian_append_content` - 保存回顾报告

## 错误处理

| 错误 | 可能原因 | 解决方案 |
|------|----------|----------|
| 文件不存在 | 路径错误或文件未创建 | 使用 append_content 创建 |
| MCP 连接失败 | Obsidian 未运行或插件未启用 | 检查 Local REST API 插件 |
| 搜索无结果 | 关键词不匹配 | 尝试更宽泛的搜索词 |
