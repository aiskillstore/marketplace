# 知乎（Zhihu）链式调用模式库

## 模式1：关键词搜索 → 内容详情

**触发场景**：用户想查找特定主题的内容

**步骤**：
1. 调用 `GET /api/v1/zhihu/web/fetch_article_search_v3` 搜索关键词 → 获取内容ID
2. 用内容ID调用 `GET /api/v1/zhihu/web/fetch_column_articles` → 获取完整详情

**示例**：
```
用户: "搜索知乎上关于旅行的视频"
→ Step1: GET /api/v1/zhihu/web/fetch_article_search_v3?keyword=旅行
→ Step2: GET /api/v1/zhihu/web/fetch_column_articles?id=<从Step1获取的ID>
```

## 模式2：用户信息 → 用户作品 → 数据分析

**触发场景**：用户想了解某个博主/创作者

## 模式4：多维度交叉分析

**触发场景**：用户需要综合分析，单个API无法满足

**步骤**：
1. 搜索API获取基础数据集
2. 逐条调用详情API补充完整字段
3. 创作者API获取作者维度数据
4. 分析API获取趋势维度数据
5. 综合所有数据输出分析报告

## 模式5：批量数据采集

**触发场景**：用户需要批量获取数据

**步骤**：
1. 确定采集范围（关键词/用户/时间）
2. 分页调用搜索/列表API获取ID集合
3. 批量调用详情API（注意限流）
4. 去重、清洗、结构化输出
