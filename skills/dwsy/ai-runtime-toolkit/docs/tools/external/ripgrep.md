---
name: ripgrep
description: 极速代码搜索工具（rg）- grep的现代化替代品
category: essential
tool_id: EXT-RG-001
---

# ripgrep (rg) ⭐⭐⭐⭐⭐

## 用途
极速代码搜索，默认递归搜索且遵守.gitignore

## 安装

### macOS
```bash
brew install ripgrep
```

### Ubuntu/Debian
```bash
sudo apt-get install ripgrep
```

## 配置
```bash
# 添加到 ~/.bashrc
alias grep='rg'
```

## 使用

```bash
# 搜索Python文件中的TODO
rg "TODO" -g "*.py"

# 显示上下文（3行）
rg -A 3 -B 3 "def function_name" app.py

# 统计匹配数
rg --count "import"

# 搜索并打开文件
rg "TODO" --files-with-matches | fzf | xargs bat
```

## 常用选项

- `-i` -- 忽略大小写
- `-g` -- 文件模式匹配（glob）
- `-A NUM` -- 显示匹配后NUM行
- `-B NUM` -- 显示匹配前NUM行
- `-C NUM` -- 显示匹配前后各NUM行
- `--count` -- 统计匹配数
- `--files-with-matches` -- 只显示包含匹配的文件名

## 技巧

```bash
# 搜索并替换（预览）
rg "old_function" -S | fzf

# 指定编码
rg --encoding utf8 "pattern"

# 与fzf集成
rg "" --files-with-matches | fzf --preview 'rg --color=always "" {}'
```
