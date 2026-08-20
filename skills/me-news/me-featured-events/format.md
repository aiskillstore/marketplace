# ME Featured Events Output Format

## Fixed reminder

```text
今日开始

1. {Event name}
{First 50 characters of the cleaned event description}
{M月D日 HH:mm–HH:mm（UTC+8）}｜{Address or region}
{Event URL}
```

Use `明日开始` for tomorrow and an explicit date heading for later dates in the requested window. Omit empty groups.

## New event

```text
新增会议

{Event name}
{First 50 characters of the cleaned event description}
{M月D日 HH:mm–HH:mm（UTC+8）}｜{Address or region}
{Event URL}
```

Rules:

- Preserve the API order by `start_time`.
- Do not invent facts, addresses, or URLs.
- Strip HTML and collapse whitespace in `description`, then show its first 50 characters. Add an ellipsis only when content was truncated; do not describe this excerpt as a generated summary.
- When `description` is empty, use the event title and address as a factual fallback.
- Print only the API `url`: ME detail URLs for regular/collection events, and the imported spreadsheet URL for `activity_import` events. Never substitute a source, WeChat, official-site, or registration URL found elsewhere in the event data.
- Use the region when the address is empty.
- Show both `start_time` and `end_time`. For a same-day event, shorten the end to `HH:mm`; for a cross-day event, show its month and day again.
- Use the API `timezone`; render `Asia/Shanghai` as `UTC+8`.
- When `end_time` is empty, add `结束时间未提供` on the next line.
- When `end_time` is invalid or not later than `start_time`, do not infer a corrected date. Omit the end from the range and add `⚠️ 结束时间格式异常` or `⚠️ 结束时间疑似异常` on the next line.
- Omit the URL line when the URL is empty.
- Produce no message when there are no matching events.
