# Scripts Directory

Utility scripts for managing the Picture Book Wizard skill documentation.

## Available Scripts

### doc-stats.sh
文档统计脚本 - 显示文档数量、行数分布、最大文件等信息。

```bash
./doc-stats.sh
```

**输出**:
- 总文件数和行数
- 按目录统计
- 最大的 10 个文件
- 中英文重复文件检测

### cleanup-duplicates.sh
清理重复文档脚本 - 删除中英文重复版本和冗余文件。

```bash
# 预览模式 (不实际删除)
./cleanup-duplicates.sh --dry-run

# 执行删除
./cleanup-duplicates.sh
```

**删除内容**:
- 中文版本文档 (保留英文版)
- 冗余的 usage-guide (SKILL.md 已包含核心内容)

## Usage

```bash
cd .claude/skills/picture-book-wizard/scripts
./doc-stats.sh
```

## Notes

- 所有脚本需要在 scripts 目录下运行
- 使用 `--dry-run` 参数可以预览操作而不实际执行
