# JSON Schemas

本文件定义 skill-creator 用到的 JSON 结构（schema）。JSON 字段名和示例值保持英文不改——因为代码会直接消费这些字段。

---

## evals.json

定义一个 skill 的测试用例。位置：skill 目录下的 `evals/evals.json`。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**字段说明：**
- `skill_name`：和 skill frontmatter 里的 name 对应
- `evals[].id`：唯一的整数标识符
- `evals[].prompt`：要执行的任务文本
- `evals[].expected_output`：人类可读的成功描述
- `evals[].files`：可选的输入文件路径列表（相对 skill 根目录）
- `evals[].expectations`：可验证的断言文本列表

---

## history.json

追踪 Improve 模式下版本演进。位置：workspace 根目录。

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**字段说明：**
- `started_at`：迭代开始的 ISO 时间戳
- `skill_name`：被迭代的 skill 名
- `current_best`：当前最优版本的标识符
- `iterations[].version`：版本标识符（v0、v1…）
- `iterations[].parent`：从哪个版本派生而来
- `iterations[].expectation_pass_rate`：评分后的通过率
- `iterations[].grading_result`：`"baseline"`、`"won"`、`"lost"` 或 `"tie"`
- `iterations[].is_current_best`：是否为当前最优版本

---

## grading.json

grader agent 的输出。位置：`<run-dir>/grading.json`。

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**字段说明：**
- `expectations[]`：逐条评过的期望，含证据
- `summary`：总体通过/失败统计
- `execution_metrics`：工具使用和输出大小（来自执行方的 metrics.json）
- `timing`：实际耗时（来自 timing.json）
- `claims`：从输出里提取并验证过的声明
- `user_notes_summary`：执行方标记的问题
- `eval_feedback`：**可选**——只有当 grader 发现 eval 本身有值得反馈的问题时才出现

---

## metrics.json

executor agent 的输出。位置：`<run-dir>/outputs/metrics.json`。

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**字段说明：**
- `tool_calls`：每种工具的调用次数
- `total_tool_calls`：所有工具调用的总和
- `total_steps`：主要执行步骤数量
- `files_created`：创建的输出文件列表
- `errors_encountered`：执行中遇到的错误数量
- `output_chars`：输出文件的总字符数
- `transcript_chars`：transcript 的字符数

---

## timing.json

单次 run 的实际耗时。位置：`<run-dir>/timing.json`。

**怎么捕获：** 子 agent 任务结束时，task notification 里带 `total_tokens` 和 `duration_ms`。**立刻保存**——这些数据不会在别的地方留存，错过就拿不回来。

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

Benchmark 模式的输出。位置：`benchmarks/<timestamp>/benchmark.json`。

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Used 2023 data, may be stale",
        "Fell back to text overlay for non-fillable fields"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
    "Eval 3 shows high variance (50% ± 40%) - may be flaky or model-dependent",
    "Without-skill runs consistently fail on table extraction expectations",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**字段说明：**
- `metadata`：benchmark run 的元信息
  - `skill_name`：skill 名
  - `timestamp`：benchmark 运行时间
  - `evals_run`：eval 的 name 或 id 列表
  - `runs_per_configuration`：每个配置跑的次数（比如 3）
- `runs[]`：单次 run 的结果
  - `eval_id`：数字化的 eval 标识
  - `eval_name`:人类可读的 eval 名称（viewer 里用作分区标题）
  - `configuration`：必须是 `"with_skill"` 或 `"without_skill"`（viewer 用这个精确字符串分组+配色）
  - `run_number`：整数 run 编号（1、2、3…）
  - `result`：嵌套对象，含 `pass_rate`、`passed`、`total`、`time_seconds`、`tokens`、`errors`
- `run_summary`：每个配置的统计聚合
  - `with_skill` / `without_skill`：各含 `pass_rate`、`time_seconds`、`tokens` 对象，带 `mean` 和 `stddev` 字段
  - `delta`：差值字符串，比如 `"+0.50"`、`"+13.0"`、`"+1700"`
- `notes`：分析师给的自由观察

**重要：** viewer **严格**按这些字段名读数据。如果把 `config` 写成 `configuration` 之外的拼写，或者把 `pass_rate` 放在 run 的顶层而不是嵌在 `result` 下，viewer 会显示空或 0。手动生成 benchmark.json 时务必对照本 schema。

---

## comparison.json

盲比对（blind comparator）的输出。位置：`<grading-dir>/comparison-N.json`。

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting inconsistencies", "Partial data extraction"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    }
  }
}
```

**字段说明：**
- `winner`：赢家标识，`"A"` 或 `"B"`
- `reasoning`：盲比对时的判断理由（评审方不知道 A/B 是哪个版本）
- `rubric`：每个版本按"内容"和"结构"两个维度打分（1-5），加权得出 `overall_score`
- `output_quality`：两个版本的优缺点
- `expectation_results`：两个版本分别对 expectations 的通过情况

---

## analysis.json

事后分析（post-hoc analyzer）的输出。位置：`<grading-dir>/analysis.json`。

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Minor: skipped optional logging step"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods"
  }
}
```

**字段说明：**
- `comparison_summary`：解盲后的对比总结
- `winner_strengths`：赢家 skill 的优点清单
- `loser_weaknesses`：输家 skill 的缺点清单
- `instruction_following`：两者对 skill 指令的遵循度打分（1-10）及问题
- `improvement_suggestions`：可落地的改进建议，含优先级、类别、具体建议、预期影响
- `transcript_insights`：从 transcript 看到的执行模式差异
