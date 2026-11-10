#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'

const usage = `Usage:
  node <skill-root>/scripts/cli/review/feedback-gate.mjs --run-dir <dir> [options]

Check whether Feedback Mode was requested and whether skill-feedback.md exists
before the final response.

Options:
  --run-dir <dir>          Required current pptx-nova run directory.
  --prompt <text>          Original user prompt or task text.
  --prompt-file <path>     File containing the original user prompt or task text.
  --workflow <name>        create|refurbish|translation|other. Inferred when omitted.
  --require-feedback       Force feedback to be required even if no trigger is detected.
  --output <path>          Write gate JSON. Defaults to <run-dir>/feedback-gate.json.
  --write-template         Create a TODO skill-feedback.md template when required and missing.
  --overwrite              Replace an existing gate JSON or generated template.
  --strict                 Exit 2 when feedback is required but missing or still a template.
  --json                   Print the gate JSON to stdout.
  --help                   Show this help.
`

const TRIGGERS = [
  { id: 'need-feedback', pattern: /\bneeds?\s+feedback\b/i },
  { id: 'give-feedback', pattern: /\bgive\s+(?:me\s+)?feedback\b/i },
  { id: 'provide-feedback', pattern: /\bprovide\s+(?:me\s+)?feedback\b/i },
  { id: 'skill-feedback', pattern: /\bskill\s+feedback\b/i },
  {
    id: 'feedback-requested',
    pattern: /\bfeedback\s+(requested|required|needed|wanted|expected)\b/i,
  },
  { id: 'cn-gei-fankui', pattern: /给反馈/ },
  { id: 'cn-xuyao-fankui', pattern: /需要反馈/ },
  { id: 'cn-shiyong-fankui', pattern: /使用反馈/ },
  { id: 'cn-you-shenme-fankui', pattern: /有什么.{0,8}反馈/ },
]

const TEMPLATE_MARKER = '<!-- pptx-nova-feedback-template -->'

const SCORECARD_RUBRICS = {
  create: [
    { dimension: '需求与内容准确性', weight: 20 },
    { dimension: '最终文件可靠性', weight: 18 },
    { dimension: '验证闭环', weight: 17 },
    { dimension: '视觉设计质量', weight: 15 },
    { dimension: 'DeckKit 与 op 使用正确性', weight: 12 },
    { dimension: '异常恢复与状态管理', weight: 10 },
    { dimension: '流程效率', weight: 8 },
  ],
  refurbish: [
    { dimension: '内容保真', weight: 20 },
    { dimension: '最终文件可靠性', weight: 18 },
    { dimension: '验证闭环', weight: 17 },
    { dimension: '视觉翻新质量', weight: 15 },
    { dimension: 'op 使用正确性', weight: 12 },
    { dimension: '异常恢复与状态管理', weight: 10 },
    { dimension: '流程效率', weight: 8 },
  ],
  translation: [
    { dimension: '翻译完整性与准确性', weight: 20 },
    { dimension: '布局与格式保真', weight: 18 },
    { dimension: '最终文件可靠性', weight: 17 },
    { dimension: '验证闭环', weight: 15 },
    { dimension: '文本替换与布局修复 op 正确性', weight: 12 },
    { dimension: '异常恢复与状态管理', weight: 10 },
    { dimension: '流程效率', weight: 8 },
  ],
}

const WORKFLOWS = new Set([...Object.keys(SCORECARD_RUBRICS), 'other'])

function valueAfter(argv, index, flag) {
  const value = argv[index + 1]
  if (!value || value.startsWith('--')) throw new Error(`${flag} requires a value`)
  return value
}

function parseArgs(argv) {
  const args = {
    runDir: '',
    prompts: [],
    promptFiles: [],
    workflow: '',
    requireFeedback: false,
    output: '',
    writeTemplate: false,
    overwrite: false,
    strict: false,
    json: false,
  }

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--help' || arg === '-h') {
      process.stdout.write(usage)
      process.exit(0)
    } else if (arg === '--run-dir') {
      args.runDir = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--prompt') {
      args.prompts.push(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--prompt-file') {
      args.promptFiles.push(valueAfter(argv, i, arg))
      i += 1
    } else if (arg === '--workflow') {
      args.workflow = valueAfter(argv, i, arg)
      if (!WORKFLOWS.has(args.workflow)) {
        throw new Error(`--workflow must be one of: ${[...WORKFLOWS].join(', ')}`)
      }
      i += 1
    } else if (arg === '--require-feedback') {
      args.requireFeedback = true
    } else if (arg === '--output' || arg === '-o') {
      args.output = valueAfter(argv, i, arg)
      i += 1
    } else if (arg === '--write-template') {
      args.writeTemplate = true
    } else if (arg === '--overwrite') {
      args.overwrite = true
    } else if (arg === '--strict') {
      args.strict = true
    } else if (arg === '--json') {
      args.json = true
    } else {
      throw new Error(`Unknown option: ${arg}\n\n${usage}`)
    }
  }

  if (!args.runDir) throw new Error(`--run-dir is required\n\n${usage}`)
  return args
}

function readPromptText(args) {
  const parts = [...args.prompts]
  for (const file of args.promptFiles) {
    parts.push(readFileSync(file, 'utf8'))
  }
  return parts.join('\n\n')
}

function matchedTriggers(text) {
  return TRIGGERS.filter((trigger) => trigger.pattern.test(text)).map((trigger) => trigger.id)
}

function inferWorkflowFromArtifacts(runDir) {
  const artifactGroups = [
    ['translation', ['translation-compare.json', 'i18n-plan.json', 'i18n-text-plan.json']],
    ['refurbish', ['refurbish-plan.json', 'refurbish-run-summary.json', 'refurbish-compare.json']],
    ['create', ['create-run-summary.json']],
  ]
  for (const [workflow, artifacts] of artifactGroups) {
    if (artifacts.some((name) => existsSync(resolve(runDir, name)))) return workflow
  }
  return ''
}

function inferWorkflowFromPrompt(promptText) {
  const patterns = [
    ['translation', /\btranslat(?:e|ed|ing|ion)\b|翻译|本地化/i],
    ['refurbish', /\brefurbish|\bpolish|\bredesign|\brebrand|翻新|美化|换肤|改版/i],
    [
      'create',
      /\bcreate|\bgenerate|\bbuild|\bmake\b|\bnew\s+(?:deck|presentation)|创建|生成|新建|做一份|做\s*PPT/i,
    ],
  ]
  return patterns.find(([, pattern]) => pattern.test(promptText))?.[0] || ''
}

function detectWorkflow(args, promptText, runDir) {
  if (args.workflow) return { id: args.workflow, source: 'explicit-flag' }
  const artifactWorkflow = inferWorkflowFromArtifacts(runDir)
  if (artifactWorkflow) return { id: artifactWorkflow, source: 'run-artifacts' }
  const promptWorkflow = inferWorkflowFromPrompt(promptText)
  if (promptWorkflow) return { id: promptWorkflow, source: 'prompt-inference' }
  return { id: 'other', source: 'undetermined' }
}

function scorecardTemplate(workflow) {
  const rubric = SCORECARD_RUBRICS[workflow]
  if (!rubric) return ''
  const rows = rubric
    .map(({ dimension, weight }) => `| ${dimension}（${weight}%） | TODO / 10 | TODO |`)
    .join('\n')
  return `
## 执行过程评分

| 维度 | 分数 | 评价 |
| --- | ---: | --- |
${rows}

加权综合评分：TODO / 10
`
}

function templateText(workflow) {
  return `${TEMPLATE_MARKER}
# pptx-nova SKILL 使用反馈

任务：TODO
时间：${new Date().toISOString()}

## 总体评价

TODO: 记录本次 pptx-nova 工作流的总体反馈。

## 具体反馈

### 1. TODO

- 现象：
- 影响：
- 建议：
- 状态分类：文档引导不足 / 工具缺口 / 已有能力未使用 / 历史 run 过期 / 流程门禁缺口

## 建议优先级

1. TODO
${scorecardTemplate(workflow)}
`
}

function inspectFeedback(path) {
  if (!existsSync(path)) {
    return {
      path,
      exists: false,
      byteLength: 0,
      lineCount: 0,
      template: false,
      state: 'missing',
    }
  }
  const content = readFileSync(path, 'utf8')
  const template = isTemplateDraft(content)
  return {
    path,
    exists: true,
    byteLength: statSync(path).size,
    lineCount: content.split(/\r?\n/).length,
    template,
    state: content.trim() && !template ? 'complete' : 'draft',
  }
}

function isTemplateDraft(content) {
  if (content.includes(TEMPLATE_MARKER)) return true
  const placeholderPatterns = [
    /^任务：\s*TODO\s*$/m,
    /^TODO:\s*记录本次 pptx-nova 工作流的总体反馈。\s*$/m,
    /^###\s+1\.\s+TODO\s*$/m,
    /^1\.\s+TODO\s*$/m,
  ]
  const placeholderHits = placeholderPatterns.filter((pattern) => pattern.test(content)).length
  return placeholderHits >= 2
}

function maybeWriteTemplate(args, feedbackPath, required, feedback, workflow) {
  if (!required || feedback.exists || !args.writeTemplate) return null
  if (existsSync(feedbackPath) && !args.overwrite) {
    throw new Error(`feedback template target already exists: ${feedbackPath}`)
  }
  mkdirSync(dirname(feedbackPath), { recursive: true })
  writeFileSync(feedbackPath, templateText(workflow))
  return feedbackPath
}

function scorecardSection(content) {
  const match = content.match(/(?:^|\n)##\s+执行过程评分\s*\n([\s\S]*?)(?=\n##\s+|$)/)
  return match?.[1] || ''
}

function dimensionParts(value) {
  const weightMatch = value.match(/[（(]\s*(\d+(?:\.\d+)?)\s*%\s*[）)]/)
  return {
    dimension: value.replace(/[（(]\s*\d+(?:\.\d+)?\s*%\s*[）)]/g, '').trim(),
    weight: weightMatch ? Number(weightMatch[1]) : null,
  }
}

function parseScorecardRows(section) {
  const rows = []
  for (const line of section.split(/\r?\n/)) {
    const cells = line
      .trim()
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((cell) => cell.trim())
    if (cells.length !== 3) continue
    const scoreMatch = cells[1].match(/^(\d+(?:\.\d+)?)\s*(?:\/\s*10)?$/)
    if (!scoreMatch) continue
    const { dimension, weight } = dimensionParts(cells[0])
    rows.push({
      displayDimension: cells[0],
      dimension,
      weight,
      score: Number(scoreMatch[1]),
      evaluation: cells[2],
    })
  }
  return rows
}

function roundOne(value) {
  return Math.round((value + Number.EPSILON) * 10) / 10
}

function validateScorecard(content, workflow) {
  const rubric = SCORECARD_RUBRICS[workflow]
  if (!rubric) {
    return {
      required: false,
      status: 'not-required',
      passed: true,
      rows: [],
      reportedWeightedScore: null,
      computedWeightedScore: null,
      errors: [],
    }
  }

  const section = scorecardSection(content)
  const parsedRows = parseScorecardRows(section)
  const errors = []
  if (!section) errors.push('missing section: ## 执行过程评分')
  if (parsedRows.length !== 7)
    errors.push(`expected 7 numeric score rows, found ${parsedRows.length}`)

  const rows = rubric.map((expected) => {
    const matches = parsedRows.filter((row) => row.dimension === expected.dimension)
    if (matches.length === 0) {
      errors.push(`missing score dimension: ${expected.dimension}`)
      return { ...expected, score: null, evaluation: '' }
    }
    if (matches.length > 1) errors.push(`duplicate score dimension: ${expected.dimension}`)
    const row = matches[0]
    if (row.weight !== expected.weight) {
      errors.push(
        `score dimension weight mismatch: ${expected.dimension}; expected ${expected.weight}%, found ${row.weight ?? 'missing'}`,
      )
    }
    if (!Number.isFinite(row.score) || row.score < 0 || row.score > 10) {
      errors.push(`score out of range for ${expected.dimension}: ${row.score}`)
    }
    if (!row.evaluation || /\bTODO\b/i.test(row.evaluation)) {
      errors.push(`missing evaluation for score dimension: ${expected.dimension}`)
    }
    return { ...expected, score: row.score, evaluation: row.evaluation }
  })

  const unexpected = parsedRows.filter(
    (row) => !rubric.some((expected) => expected.dimension === row.dimension),
  )
  for (const row of unexpected) errors.push(`unexpected score dimension: ${row.dimension}`)

  const overallMatch = section.match(/加权综合评分\s*[：:]\s*(\d+(?:\.\d+)?)\s*\/\s*10/)
  const reportedWeightedScore = overallMatch ? Number(overallMatch[1]) : null
  if (reportedWeightedScore === null)
    errors.push('missing weighted overall score: 加权综合评分：<score> / 10')
  if (reportedWeightedScore !== null && (reportedWeightedScore < 0 || reportedWeightedScore > 10)) {
    errors.push(`weighted overall score out of range: ${reportedWeightedScore}`)
  }

  const computable = rows.every((row) => Number.isFinite(row.score))
  const computedWeightedScore = computable
    ? roundOne(rows.reduce((sum, row) => sum + row.score * row.weight, 0) / 100)
    : null
  if (
    reportedWeightedScore !== null &&
    computedWeightedScore !== null &&
    Math.abs(reportedWeightedScore - computedWeightedScore) > 0.05
  ) {
    errors.push(
      `weighted overall score mismatch: reported ${reportedWeightedScore}, computed ${computedWeightedScore}`,
    )
  }

  return {
    required: true,
    status: errors.length === 0 ? 'pass' : 'fail',
    passed: errors.length === 0,
    rows,
    reportedWeightedScore,
    computedWeightedScore,
    errors,
  }
}

function buildReport(args) {
  const runDir = resolve(args.runDir)
  const promptText = readPromptText(args)
  const workflow = detectWorkflow(args, promptText, runDir)
  const triggers = matchedTriggers(promptText)
  const required = args.requireFeedback || triggers.length > 0
  const source = args.requireFeedback
    ? 'explicit-flag'
    : triggers.length > 0
      ? 'prompt-trigger'
      : 'not-requested'
  const feedbackPath = resolve(runDir, 'skill-feedback.md')
  let feedback = inspectFeedback(feedbackPath)
  const createdTemplate = maybeWriteTemplate(args, feedbackPath, required, feedback, workflow.id)
  if (createdTemplate) feedback = inspectFeedback(feedbackPath)

  const feedbackContent = feedback.exists ? readFileSync(feedbackPath, 'utf8') : ''
  const processScorecard = validateScorecard(feedbackContent, workflow.id)

  const missing = required && feedback.state !== 'complete'
  const scorecardInvalid = required && processScorecard.required && !processScorecard.passed
  const status = missing || scorecardInvalid ? 'fail' : required ? 'pass' : 'not-required'
  const message = missing
    ? `Feedback Mode was requested but ${feedback.state === 'draft' ? 'skill-feedback.md is still a TODO template' : 'skill-feedback.md is missing'}.`
    : scorecardInvalid
      ? `Feedback Mode for ${workflow.id} requires a valid seven-dimension process scorecard and weighted overall score.`
      : required
        ? `Feedback Mode was requested and skill-feedback.md is present${processScorecard.required ? ' with a valid process scorecard' : ''}.`
        : 'Feedback Mode was not requested by the supplied prompt.'

  return {
    schemaVersion: 'pptx-nova-feedback-gate/v1',
    observedAt: new Date().toISOString(),
    status,
    runDir,
    requirement: {
      required,
      source,
      matchedTriggers: triggers,
    },
    workflow,
    feedback,
    processScorecard,
    createdTemplate,
    strict: args.strict,
    agentSummary: {
      status,
      required,
      feedbackPath,
      workflow: workflow.id,
      weightedOverallScore: processScorecard.reportedWeightedScore,
      message,
    },
  }
}

function writeReport(args, report) {
  const output = resolve(args.output || resolve(args.runDir, 'feedback-gate.json'))
  const text = `${JSON.stringify(report, null, 2)}\n`
  if (existsSync(output) && !args.overwrite) {
    throw new Error(
      `output already exists: ${output}; use --overwrite for a current-run gate artifact`,
    )
  }
  mkdirSync(dirname(output), { recursive: true })
  writeFileSync(output, text)

  if (args.json) {
    process.stdout.write(text)
  } else {
    process.stdout.write(`feedback gate: ${report.status}\n`)
    process.stdout.write(`${report.agentSummary.message}\n`)
    if (report.processScorecard.required && report.processScorecard.rows.length > 0) {
      process.stdout.write('\n| 维度 | 分数 | 评价 |\n')
      process.stdout.write('| --- | ---: | --- |\n')
      for (const row of report.processScorecard.rows) {
        process.stdout.write(
          `| ${row.dimension}（${row.weight}%） | ${row.score ?? '-'} / 10 | ${row.evaluation || '-'} |\n`,
        )
      }
      process.stdout.write(
        `\n加权综合评分：${report.processScorecard.reportedWeightedScore ?? '-'} / 10\n`,
      )
    }
    process.stdout.write(`report: ${output}\n`)
  }
}

try {
  const args = parseArgs(process.argv.slice(2))
  const report = buildReport(args)
  writeReport(args, report)
  if (args.strict && report.status === 'fail') process.exit(2)
} catch (error) {
  process.stderr.write(`[error] ${error.message}\n`)
  process.exit(1)
}
