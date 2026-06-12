# Windows 用户指南

`zach-feature-demand-validator` 的脚本统一用 Python CLI，Windows 和 macOS 的功能一致。

## 基本约定

- 推荐命令：`py -3`
- 原始文件和输出文件尽量使用 UTF-8
- 路径里有空格时请加引号

## 1. 解析 Sorftime Review JSON

```powershell
py -3 skills\zach-feature-demand-validator\scripts\parse_reviews.py `
  --input ".\reviews.json" `
  --asin "B0XXXXXXX" `
  --keywords "steam,steamer,steaming" `
  --source-url "sorftime://product_reviews/B0XXXXXXX" `
  --output ".\01_review_信号_原始数据.csv"
```

## 2. 解析本地 Review fallback 包

```powershell
py -3 skills\zach-feature-demand-validator\scripts\parse_review_source_pack.py `
  --pack ".\review_source_pack" `
  --keywords "steam,steamer,steaming" `
  --output ".\01_review_信号_原始数据.csv"
```

## 3. 导出关键词 CSV

```powershell
py -3 skills\zach-feature-demand-validator\scripts\generate_keyword_csv.py `
  --type detail `
  --data ".\keyword_detail.json" `
  --source-ref "keyword_detail:steam air fryer" `
  --output ".\02_keyword_信号_搜索量数据.csv"
```

## 4. 导出社区 CSV

```powershell
py -3 skills\zach-feature-demand-validator\scripts\generate_community_csv.py `
  --data ".\community.json" `
  --source-ref 'site:reddit.com "air fryer steam"' `
  --output ".\05_社区_信号_讨论摘要.csv"
```

## 5. 校验交付物

```powershell
py -3 skills\zach-feature-demand-validator\scripts\validate_deliverables.py `
  --dir ".\outputs\feature-validation\2026-03-19_air-fryer_steam"
```

## 常见问题

### 中文乱码

PowerShell 先执行：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 找不到文件

- 检查当前工作目录
- 检查路径是否写成了相对路径
- 有空格时加引号

### 模块导入报错

优先从仓库根目录运行命令，不要把脚本单独复制到别处执行。
