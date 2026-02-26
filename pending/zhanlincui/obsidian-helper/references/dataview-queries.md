# Dataview 查询模板

## 产品库看板

```dataview
TABLE company, stage, pricing, language, url
FROM "30_Resources/Products"
WHERE type = "product"
SORT stage ASC, file.ctime DESC
```

## 按标签分组的产品

```dataview
TABLE WITHOUT ID
  file.link as "产品",
  company as "公司",
  stage as "阶段"
FROM "30_Resources/Products"
WHERE type = "product"
GROUP BY tags[0]
```

## 活跃项目

```dataview
TABLE status, priority, deadline
FROM "10_Projects"
WHERE type = "project" AND status = "active"
SORT priority DESC, deadline ASC
```

## 最近创建的笔记

```dataview
TABLE type, tags, created
FROM ""
WHERE created
SORT created DESC
LIMIT 20
```

## 今日修改

```dataview
LIST
FROM ""
WHERE file.mday = date(today)
SORT file.mtime DESC
```

## AI 待处理（Inbox 内容）

```dataview
TABLE type, created
FROM "00_Inbox/AI"
SORT file.ctime DESC
```

## 永久笔记索引

```dataview
TABLE source, tags
FROM "40_Zettels"
WHERE type = "zettel"
SORT file.ctime DESC
```

## Tasks 查询示例

### 未完成且即将到期

```tasks
not done
due before in two weeks
sort by due
```

### 今日任务

```tasks
not done
due today
```

### 按项目分组

```tasks
not done
group by folder
```
