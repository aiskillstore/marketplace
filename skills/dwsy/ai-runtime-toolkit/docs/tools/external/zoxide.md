---
name: zoxide
description: 智能目录跳转工具（z）- cd的AI驱动替代品
category: essential
tool_id: EXT-ZOXIDE-001
---

# zoxide (Smart cd) ⭐⭐⭐⭐⭐

## 用途
智能目录跳转，学习访问习惯，基于频率和最近访问时间

## 安装

### 所有平台（推荐）
```bash
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh
```

或者使用包管理器：

### macOS
```bash
brew install zoxide
```

### Ubuntu/Debian
```bash
sudo apt-get install zoxide
```

## 配置

添加到 `~/.bashrc`:
```bash
eval "$(zoxide init bash)"
alias cd='z'
alias cdi='zi'
```

## 使用

```bash
# 第一次需要完整路径
cd ~/projects/ai-runtime

# 之后只需（zoxide会学习）
z ai-runtime

# 查看访问频率
z --list | head

# 交互式选择
zi

# 跳转到包含'proj'的目录
z proj

# 跳转到包含'ai'和'time'的目录
z ai time
```

## 常用命令

- `z --list` -- 显示访问目录列表
- `z --list | head` -- 显示最近访问的目录
- `z -i` -- 交互式跳转（同`zi`）
- `z -e` -- 显示最高匹配目录

## 特性

- **智能学习**：基于访问频率和最近访问时间
- **模糊匹配**：支持部分匹配
- **跨Shell**：支持bash, zsh, fish等
- **快速跳转**：通常比手动输入路径更快
