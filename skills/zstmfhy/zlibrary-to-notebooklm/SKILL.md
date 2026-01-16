---
name: zlibrary-to-notebooklm
description: 自动从 Z-Library 下载书籍并上传到 Google NotebookLM。支持 PDF/EPUB 格式，自动转换，一键创建知识库。
---

# Z-Library to NotebookLM Skill

让 Claude 帮你自动下载书籍并上传到 NotebookLM，实现"零幻觉"的 AI 对话式阅读。

## 🎯 核心功能

- 一键下载书籍（优先 PDF，自动降级 EPUB）
- 自动创建 NotebookLM 笔记本
- 上传文件并返回笔记本 ID
- 支持与 AI 进行基于书籍内容的对话

## 📋 激活条件（Triggers）

当用户提到以下需求时，使用此 Skill：

- 用户提供 Z-Library 书籍链接（包含 `zlib.li`、`z-lib.org`、`zh.zlib.li` 等域名）
- 用户说"帮我把这本书上传到 NotebookLM"
- 用户说"自动下载并读这本书"
- 用户说"用 Z-Library 链接创建 NotebookLM 知识库"
- 用户要求从特定 URL 下载书籍并分析

## 🔧 核心指令

当用户提供 Z-Library 链接时，按以下流程执行：

### Step 1: 提取信息

从用户提供的 URL 中提取：
- 书名
- 作者（如果有）
- 完整 URL
- 格式选项（PDF/EPUB/MOBI 等）

### Step 2: 自动下载

使用已保存的会话（`~/.zlibrary/storage_state.json`）自动登录 Z-Library：

1. **优先下载 PDF**（保留排版，AI 分析效果更好）
2. **自动降级**：如果没有 PDF，下载 EPUB
3. **格式转换**：如果下载 EPUB，使用 ebooklib 转换为纯文本

### Step 3: 创建 NotebookLM 笔记本

```bash
notebooklm create "书名"
```

### Step 4: 上传文件

```bash
notebooklm source add "文件路径"
```

### Step 5: 返回结果

向用户返回：
- ✅ 下载成功确认
- 📚 笔记本 ID
- 💡 建议的后续问题示例

### Step 6: 错误处理

如果遇到错误：
- 尝试重试最多 3 次
- 如果登录失败，提示用户运行 `python3 ~/.claude/skills/zlibrary-to-notebooklm/scripts/login.py`
- 如果下载失败，提供故障排查建议

## ⚠️ 重要限制

**仅限合法资源！**

- ✅ 用户拥有合法访问权限的资源
- ✅ 公共领域或开源许可的文档
- ✅ 个人拥有版权或已获授权的内容
- ❌ 不要鼓励或协助版权侵权行为

**如果 URL 明显涉及受版权保护的商业作品，提醒用户：**
> "请确保你有合法访问权限。本项目仅用于学习研究目的，请支持正版阅读。"

## 🛠️ 依赖工具

### 必需工具

1. **Playwright** - 浏览器自动化
   - 用于自动登录和下载
   - 需要预先运行 `playwright install chromium`

2. **ebooklib** - EPUB 处理
   - 用于将 EPUB 转换为纯文本

3. **NotebookLM CLI** - 上传工具
   - `notebooklm create` - 创建笔记本
   - `notebooklm source add` - 上传文件

### 配置文件

- `~/.zlibrary/storage_state.json` - 保存的登录会话
- `~/.zlibrary/browser_profile/` - 浏览器数据

## 📝 使用示例

### 用户请求

```
帮我把这本书上传到 NotebookLM：
https://zh.zlib.li/book/25314781/aa05a1/钱的第四维
```

### 执行流程

1. **确认并提取信息**
   ```
   书名：钱的第四维
   URL：https://zh.zlib.li/book/25314781/aa05a1/钱的第四维
   ```

2. **执行下载脚本**
   ```bash
   cd ~/.claude/skills/zlibrary-to-notebooklm
   python3 scripts/upload.py "https://zh.zlib.li/book/25314781/aa05a1/钱的第四维"
   ```

3. **返回结果**
   ```
   ✅ 下载成功！
   📚 笔记本 ID: 22916611-c68c-4065-a657-99339e126fb4

   现在你可以问我：
   - "这本书的核心观点是什么？"
   - "总结第3章的内容"
   - "作者有哪些独特的见解？"
   ```

## 🔄 备选流程

### 如果用户只提供书名

```
用户："帮我下载《认知觉醒》这本书"
```

**操作：**
1. 询问："请问有 Z-Library 的链接吗？"
2. 如果有链接，执行标准流程
3. 如果没有链接，提示："请提供 Z-Library 书籍页面链接，我可以帮你自动下载并上传到 NotebookLM"

### 如果用户提供其他来源

```
用户："这个 PDF 能上传到 NotebookLM 吗？[本地文件路径]"
```

**操作：**
1. 告知用户："本 Skill 主要用于 Z-Library 链接"
2. 建议："对于本地文件，你可以直接使用 notebooklm source add 命令上传"

## 📊 技术细节

### 下载优先级

1. **PDF** - 保留排版，AI 分析效果最佳
2. **EPUB** - 转换为纯文本（使用 ebooklib）
3. **其他格式** - 尝试转换或提示用户

### 会话管理

- **一次登录，永久使用**
- 会话保存在 `~/.zlibrary/storage_state.json`
- 如果会话失效，提示用户重新登录

### 错误重试

- 下载失败：自动重试 3 次
- 登录失败：提示用户手动登录
- 上传失败：检查文件大小和格式

## 💡 最佳实践

### 首次使用

第一次使用前，确保用户已完成登录：

```bash
cd ~/.claude/skills/zlibrary-to-notebooklm
python3 scripts/login.py
```

### 批量处理

如果用户有多个链接：

```
用户："帮我下载这3本书：[链接1] [链接2] [链接3]"
```

**操作：**
1. 逐个处理（每次一个链接）
2. 每个完成后，再处理下一个
3. 避免并发导致会话冲突

### 内容分析

上传完成后，主动建议：

```
✅ 书籍已上传！你可以：

• 立即开始阅读："这本书的核心观点是什么？"
• 深入探讨："解释第5章的案例"
• 生成笔记："创建详细的读书笔记"
• 对比分析："这与书中的观点有什么不同？"
```

## 🚨 故障排查

### 常见问题

**Q: 提示"未找到登录会话"**
A: 需要先运行 `python3 scripts/login.py` 登录一次

**Q: 下载失败，超时**
A: 可能是网络问题，建议重试或检查网络连接

**Q: 找不到下载按钮**
A: Z-Library 页面结构可能变化，使用备用方案手动下载

**Q: NotebookLM 上传失败**
A: 检查文件大小（NotebookLM 有上传限制）

### 详细帮助

查看 `docs/TROUBLESHOOTING.md` 获取完整故障排查指南。

## 📚 相关资源

- [NotebookLM 官方文档](https://notebooklm.google.com/)
- [Z-Library 网站](https://zh.zlib.li/)
- [Playwright 文档](https://playwright.dev/)
- [项目 GitHub](https://github.com/zstmfhy/zlibrary-to-notebooklm)

## 🎓 学习资源

如果你想了解更多：

- **如何高效使用 NotebookLM**：询问"NotebookLM 有哪些使用技巧？"
- **如何创建个人知识库**：询问"如何用 NotebookLM 构建知识管理系统？"
- **AI 对话式阅读**：询问"怎样让 AI 帮我深度阅读一本书？"

---

**Skill Version:** 1.0.0
**Last Updated:** 2025-01-14
**Author:** zstmfhy
