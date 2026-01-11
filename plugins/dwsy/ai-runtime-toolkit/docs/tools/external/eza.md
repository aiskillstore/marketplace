---
name: eza
description: 现代化的ls替代品，带彩色输出和图标
category: essential
tool_id: EXT-EZA-001
---

# eza (Modern ls) ⭐⭐⭐⭐⭐

## 用途
现代化文件列表，替代传统ls命令

## 安装

### macOS
```bash
brew install eza
```

### Ubuntu/Debian
```bash
sudo apt-get install -y gpg wget
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/gierens.gpg
echo "deb http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
sudo apt-get update
sudo apt-get install -y eza
```

## 配置 (添加到 ~/.bashrc)

```bash
alias ll='eza -lah'
alias ls='eza'
alias tree='eza --tree --level=2'
```

## 使用

```bash
# 详细列表
ll

# Git状态
ll --git

# 树形结构
tree

# 显示图标
eza --icons
```

## 常用选项

- `-l` -- 长格式
- `-a` -- 显示隐藏文件
- `-h` -- 人性化大小
- `-g` -- 显示Git状态
- `--tree` -- 树形视图
- `--icons` -- 显示文件图标
