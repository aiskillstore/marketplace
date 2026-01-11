---
name: external-tools-reference
description: 完整的外部CLI工具参考指南 - 包含所有工具的安装、配置和使用示例
---

# 外部工具完整参考指南

**核心理念**: **整合 > 创造**

外部CLI工具是**成熟的、社区验证的**工具，我们**不应重新实现**，而应直接集成到ai-runtime工具装备系统中。

## 工具分类

### 基础必备（所有用户都应安装）

这些工具提供**日常开发**的核心功能，建议**优先安装**。

| 工具 | ID | 用途 | 安装难度 | 推荐度 |
|-----|-----|-----|---------|-------|
| [fzf](../tools/external/fzf.md) | EXT-FZF-001 | 模糊查找和交互 | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| [eza](../tools/external/eza.md) | EXT-EZA-001 | 文件列表（替代ls） | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| [zoxide](../tools/external/zoxide.md) | EXT-ZOXIDE-001 | 智能目录跳转 | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| [fd](../tools/external/fd.md) | EXT-FD-001 | 文件搜索（替代find） | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| [bat](../tools/external/bat.md) | EXT-BAT-001 | 文件查看（替代cat） | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| [ripgrep](../tools/external/ripgrep.md) | EXT-RG-001 | 代码搜索（替代grep） | ⭐ 简单 | ⭐⭐⭐⭐⭐ |
| starship | EXT-STEAMSHIP-001 | Shell提示符 | ⭐ 简单 | ⭐⭐⭐⭐ |

### 进阶推荐（提升效率）

| 工具 | ID | 用途 | 推荐度 |
|-----|-----|-----|-------|
| [jq](../tools/external/jq.md) | EXT-JQ-001 | JSON查询和处理 | ⭐⭐⭐⭐⭐ |
| zellij | EXT-ZELLIJ-001 | 终端复用（替代tmux） | ⭐⭐⭐⭐ |
| procs | EXT-PROCS-001 | 进程查看（替代ps） | ⭐⭐⭐⭐ |

### 专家级（特定场景）

| 工具 | ID | 用途 | 推荐度 |
|-----|-----|-----|-------|
| just | EXT-JUST-001 | 任务运行器（替代make） | ⭐⭐⭐⭐ |
| hyperfine | EXT-HYPERFINE-001 | 性能基准测试 | ⭐⭐⭐⭐ |
| delta | EXT-DELTA-001 | Git diff美化 | ⭐⭐⭐⭐ |
| xh | EXT-XH-001 | HTTP客户端（替代curl） | ⭐⭐⭐⭐ |

## 一键安装脚本

### macOS (使用Homebrew)
```bash
brew install fzf eza zoxide fd bat ripgrep jq just hyperfine git-delta xh
```

### Ubuntu/Debian
```bash
# 基础工具
sudo apt-get install fzf ripgrep jq

# eza（需要添加源）
sudo apt-get install -y gpg wget
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/gierens.gpg
echo "deb http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
sudo apt-get update
sudo apt-get install -y eza

# zoxide
curl -sSfL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | sh

# fd
sudo apt-get install fd-find
ln -s $(which fdfind) ~/.local/bin/fd

# bat
sudo apt-get install bat

# just
cargo install just

# hyperfine
cargo install hyperfine
```

## 个人工具箱建议

### 最小工具箱（4个）⭐
适合新手，提供基础文件和导航功能：
```bash
fzf + eza + zoxide + fd
```

### 完整工具箱（10个）⭐⭐
适合日常开发，覆盖90%场景：
```bash
fzf + eza + zoxide + fd + bat + ripgrep + starship + jq + xh + delta
```

### 终极工具箱（15+个）⭐⭐⭐
适合高级用户和工具链爱好者：
```bash
所有上面工具 + zellij + just + hyperfine + procs + ...
```

## 整合到ai-runtime

### 1. 在discover-toolkit.py中添加检测

扩展discover-toolkit.py，使其能够检测系统已安装的CLI工具：

```python
# 在discover-toolkit.py中添加
EXTERNAL_TOOLS = {
    'fzf': {'category': 'search', 'priority': 'essential'},
    'eza': {'category': 'file-listing', 'priority': 'essential'},
    'zoxide': {'category': 'navigation', 'priority': 'essential'},
    # ...
}

def detect_external_tools():
    """检测已安装的外部工具"""
    installed = []
    for tool, meta in EXTERNAL_TOOLS.items():
        if shutil.which(tool):
            installed.append({
                'name': tool,
                'category': meta['category'],
                'priority': meta['priority'],
                'installed': True
            })
    return installed
```

### 2. 在脚本中使用

示例：在runtime-explore.sh中
```bash
# 使用fzf选择文件
FILE=$(fd .py | fzf --preview 'bat -n --color=always {}')
read_file_content "$FILE"
```

### 3. 配置检查

在系统初始化时检查关键工具是否安装：

```bash
# check-tools.sh
for tool in fzf eza zoxide fd bat rg jq; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool 未安装 - 运行: brew install $tool"
    else
        echo "✅ $tool 已安装 ($(which $tool))"
    fi
done
```

## 维护策略

### 定期检查
建议**每月**检查一次：
- 工具是否有新版本发布
- 安全漏洞通告
- 社区推荐变化

### 更新策略

- **基础工具**（fzf, eza, zoxide, fd）: 建议**始终使用最新版**
- **进阶工具**（jq, bat, ripgrep）: 根据**需求更新**
- **专家工具**（zellij, just）: 有**新功能**时再更新

### 废弃管理

- 记录工具替代关系（如ripgrep → grep）
- 在元数据中标记"replaced_by"
- 保持向后兼容

## 参考资源

- [fzf文档](https://github.com/junegunn/fzf)
- [eza文档](https://github.com/eza-community/eza)
- [zoxide文档](https://github.com/ajeetdsouza/zoxide)
- [bat文档](https://github.com/sharkdp/bat)
- [ripgrep文档](https://github.com/BurntSushi/ripgrep)
- [jq文档](https://github.com/jqlang/jq)

## 相关文档

- 查看工具详情: `@docs/tools/external/fzf.md`
- 查看创建工具指南: `@docs/guides/creating-tools.md`
- 查看工具分类说明: `@docs/references/tool-categories.md`

---

**最后更新**: 2025-11-14
**下次审查**: 2025-12-14
**维护者**: CodeConscious
**状态**: Active
