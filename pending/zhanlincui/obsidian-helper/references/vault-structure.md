# Obsidian Vault 推荐结构

## PARA + Zettelkasten 混合结构

```
Vault/
├── 00_Inbox/                 # 随手记、AI 进来的草稿
│   └── AI/                   # 【重要】AI 专用落地区
├── 10_Projects/              # 有截止时间的项目
├── 20_Areas/                 # 长期维持的领域（学习/健康/职业）
├── 30_Resources/             # 资料与外部信息
│   ├── Products/             # 产品库
│   ├── Articles/             # 文章收藏
│   └── References/           # 参考资料
├── 40_Zettels/               # 永久笔记（结论/洞见）
├── 90_Archive/               # 结束项目与废弃内容
├── 99_System/                # 模板、脚本、附件、配置
│   ├── Templates/
│   └── Attachments/
└── Daily Notes/              # 日记（可放顶层或 20_Areas 下）
```

## AI 写入三条硬规矩

1. **AI 专用落地区**: `00_Inbox/AI/`
   - AI 新建/抓取/生成的内容先落这里
   - 人工确认后再移动到其他位置

2. **追加式写入**:
   - 用 `append` / `patch_content` 往指定标题下追加
   - 不要重写整篇，降低误伤

3. **Properties 白名单**:
   - 只允许写预定义字段
   - AI 不能随意发明字段名

## 核心 Properties Schema（8-12 个字段）

### 通用笔记
```yaml
---
type: note          # note / project / product / article / zettel
title: ""
tags: []
created: {{date}}
modified: {{date}}
status: active      # active / done / archived
---
```

### 产品卡片
```yaml
---
type: product
name: ""
company: ""
url: ""
stage: discovery    # discovery / beta / launched / mature
pricing: free       # free / freemium / paid / unknown
language: en        # en / zh / multi
tags: [ai, tool]
created: {{date}}
---
```

### 项目
```yaml
---
type: project
title: ""
status: active      # active / paused / done / archived
priority: medium    # high / medium / low
deadline: ""
tags: []
created: {{date}}
---
```

### Zettel（永久笔记）
```yaml
---
type: zettel
title: ""
source: "[[]]"      # 来源笔记链接
tags: []
created: {{date}}
---
```
