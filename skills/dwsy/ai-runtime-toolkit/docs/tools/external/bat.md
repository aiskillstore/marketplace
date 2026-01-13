---
name: bat
description: 带语法高亮的cat替代品
category: essential
tool_id: EXT-BAT-001
---

# bat (cat with syntax) ⭐⭐⭐⭐⭐

## 用途
语法高亮的文件查看

## 安装

### macOS
```bash
brew install bat
```

### Ubuntu/Debian
```bash
sudo apt-get install bat
```

## 配置 (添加到 ~/.bashrc)

```bash
alias cat='bat -p'
alias catn='bat'
```

## 使用

```bash
# 查看文件（有语法高亮）
bat app.py

# 分页查看（保留高亮）
bat -p app.py | less -R

# 查看Git修改
bat -d app.py

# 查看行号
bat -n app.py
```

## 常用选项

- `-p` -- 纯文本模式（无分页）
- `-n` -- 显示行号
- `-d` -- 显示Git diff
- `-l` -- 指定语言
- `--theme` -- 选择主题

## 与其他工具集成

```bash
# 与fzf集成
fd .py | fzf --preview 'bat --color=always {}'

# 查看日志
bat /var/log/system.log
```
