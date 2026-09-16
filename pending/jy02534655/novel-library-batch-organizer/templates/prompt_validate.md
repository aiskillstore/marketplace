【任务】校验小说处理结果并标记异常

【输入数据】
---
文件名：{{file_name}}
原字符数：{{original_chars}}
新字符数：{{new_chars}}
章节数：{{chapter_count}}
章节列表：{{chapter_list}}
检测到的异常：{{detected_issues}}
---

【校验规则】
1. 章节编号必须从1开始，连续无断无重
2. 字符数变化率 = |新-原|/原，必须 < 5%
3. 所有章节标题必须严格匹配 第\d+章 格式
4. 检查是否存在明显的广告残留

【输出要求】
输出JSON格式校验报告：
{
  "file_name": "{{file_name}}",
  "passed": true/false,
  "checks": {
    "chapter_continuity": true/false,
    "chars_diff_ok": true/false,
    "title_format_ok": true/false,
    "no_ad_residue": true/false
  },
  "issues": ["问题描述1", "问题描述2"],
  "suggestion": "通过/人工复核/重新处理"
}