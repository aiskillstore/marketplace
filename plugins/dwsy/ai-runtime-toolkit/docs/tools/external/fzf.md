---
name: fzf
description: 命令行模糊查找工具 - 用于交互式搜索和选择
category: essential
tool_id: EXT-FZF-001
---

# fzf (Fuzzy Finder) ⭐⭐⭐⭐⭐

## 用途
命令行模糊查找，革命性交互体验

## 安装

### macOS
```bash
brew install fzf
$(brew --prefix)/opt/fzf/install  # 安装键盘快捷键
```

### Ubuntu/Debian
```bash
sudo apt-get install fzf
```

## 基础使用

```bash
# 文件名查找
find . -type f | fzf

# 历史命令
history | fzf

# Git分支
git branch | fzf

# 进程kill
ps aux | fzf | awk '{print $2}' | xargs kill
```

## 进阶配置 (添加到 ~/.bashrc)

```bash
# 使用Ctrl-R搜索历史
export FZF_CTRL_R_OPTS="--preview 'echo {}' --preview-window down:3:wrap"

# 使用Ctrl-T搜索文件
export FZF_CTRL_T_COMMAND="fd --type f --hidden --follow --exclude .git"
export FZF_CTRL_T_OPTS="--preview 'bat -n --color=always {}'"
```

## 在ai-runtime中的建议

```bash
# 集成到discover-toolkit.py
# 当选择工具时，使用fzf进行交互式选择
python3 discover-toolkit.py list | fzf --height 40%
```

## 为什么我们不应重新实现

- 7000+ stars on GitHub，社区验证
- 性能优化到极致
- 支持多种Shell和OS
- 生态丰富（vim插件、tmux集成等）

**类比**：就像人类不会自己打造锤子，而是从五金店购买。

## 快速验证

```bash
# 检查是否安装
which fzf

# 验证版本
fzf --version

# 测试基本功能
ls | fzf
```
