# ME Event Skill API

Base URL: `https://api.me.news/skill/events`

所有时间按 `Asia/Shanghai`（UTC+8）处理。成功响应的顶层 `code` 为 `200`。

请求失败、HTTP 非 2xx、JSON 无法解析或顶层 `code` 非 `200` 时，不更新任何本地游标。

## 筛选选项

```http
GET /options
```

返回 `types` 和 `regions`。请求其他接口时只使用这里返回的 `value`。

当前类型：

- `ai`：标题符合 ME News 现有 AI 分类规则。
- `web3`：其他活动。

## 未来活动

```http
GET /upcoming?type_ids=ai,web3&region_ids=hong-kong,singapore&hours=168&limit=20
```

参数均可省略：

- `type_ids`：逗号分隔，多选为 OR。
- `region_ids`：逗号分隔，多选为 OR。
- `hours`：从当前时间开始向后查询的小时数，1～8784；默认 168（7 天）。
- `start_date`、`end_date`：明确日期范围，格式均为 `YYYY-MM-DD`，必须同时传入，包含起止两天。
- `limit`：1～100，默认 20。返回达到 100 条时，应缩小时间范围或增加类型、地区筛选，不继续放大单次结果。

`hours` 不能与 `start_date`、`end_date` 同时使用。单次日期范围最多 366 天，更长范围应拆分请求。

自然语言映射示例：

- “近期活动”或未指定时间：不传时间参数，使用默认未来 7 天。
- “未来 30 天”：`hours=720`。
- “2026 年 8 月份”：`start_date=2026-08-01&end_date=2026-08-31`。
- “8 月 10 日到 20 日”：解析年份后传 `start_date`、`end_date`；年份不明确时先询问用户。

类型与地区之间为 AND。结果按开始时间升序使用。

## 新增活动

```http
GET /changes?cursor=CURSOR&type_ids=ai&region_ids=hong-kong&limit=100
```

- 首次不传 `cursor` 时，服务端返回当前最新游标和空 `items`。
- 后续必须传入本地保存的游标。
- 只有一批消息全部处理成功后才保存 `next_cursor`。
- `has_more=true` 时继续请求。

## 活动字段

```json
{
  "id": "activity:681",
  "source": "activity",
  "source_id": 681,
  "activity_id": 681,
  "collection_id": null,
  "title": "活动名称",
  "description": "活动原始介绍",
  "start_time": "2026-08-13 13:00:00",
  "end_time": "2026-08-13 17:00:00",
  "timezone": "Asia/Shanghai",
  "type": {"value": "ai", "label": "AI"},
  "region": {"value": "hong-kong", "label": "香港"},
  "city": "",
  "address": "香港",
  "url": "https://www.me.news/events/681"
}
```

`url` 的来源规则：

- `activity`：ME 活动详情页 `https://www.me.news/events/{activity_id}`，不返回活动记录中的外部来源链接。
- `activity_other`：所属合集的 ME 活动详情页 `https://www.me.news/events/{collection_id}`。
- `activity_import`：表格导入时提供的链接；表格没有链接时为 `null`。

`source` 说明：

- `activity`：ME News 活动表中的独立活动，包括合集内自有活动。
- `activity_other`：活动合集下批量录入的外部边会活动。

合集容器本身不返回，两类独立活动都参与固定提醒和新增提醒。

## 时间展示与异常处理

- 同日活动显示完整开始时间和结束时刻；跨日活动同时显示结束日期。
- `timezone` 为 `Asia/Shanghai` 时向用户显示 `UTC+8`。
- `end_time` 为空表示结束时间未提供。
- `end_time` 无法解析、早于或等于 `start_time` 时属于可疑数据。客户端不得自动修正或推断跨天，应保留开始时间并给出异常提示。
