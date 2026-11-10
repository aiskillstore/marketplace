import { createHash } from 'node:crypto'
import { canonicalJsonV1 } from '../runtime/canonical-json.mjs'
import { reviewFindingIdentity } from './policy.mjs'

export const LAYOUT_SNAPSHOT_SCHEMA_VERSION = 'pptx-nova-layout-snapshot/v1'
const EMU_PER_INCH = 914400
const DEFAULT_PROMPT_TEXT_RE =
  /^(click to add|click to add title|click to add subtitle|title goes here|subtitle goes here|name goes here|单击此处|单击添加|添加标题|添加副标题)$/i
const STRUCTURAL_PLACEHOLDER_TEXT_RE = /^(date|footer|slide number|页脚|日期|幻灯片编号)$/i
const INFORMATIONAL_RISK_CODES = new Set([
  'bbox-missing',
  'font-family-missing',
  'font-size-missing',
])
const MAX_SUMMARY_SLIDES = 8

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function isPlainObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value)
}

function numberOrNull(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

function compact(values) {
  return values.filter((value) => value !== null && value !== undefined && value !== '')
}

function unique(values) {
  return [...new Set(values)]
}

function pushRisk(list, severity, code, message, details = {}) {
  const classification = INFORMATIONAL_RISK_CODES.has(code) ? 'informational' : 'actionable'
  list.push({
    severity: classification === 'informational' ? 'info' : severity,
    classification,
    code,
    message,
    ...details,
  })
}

function slideCountOf(inspect) {
  const count = numberOrNull(inspect?.presentation?.slideCount)
  if (Number.isInteger(count) && count >= 0) return count
  return asArray(inspect?.slides).length
}

function parseDimensionToEmu(value) {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'number' && Number.isFinite(value)) return value
  const text = String(value).trim()
  const match = text.match(/^(-?\d+(?:\.\d+)?)(in|inch|cm|mm|pt|px|emu)?$/i)
  if (!match) return null
  const amount = Number(match[1])
  if (!Number.isFinite(amount)) return null
  const unit = (match[2] ?? 'emu').toLowerCase()
  if (unit === 'in' || unit === 'inch') return amount * EMU_PER_INCH
  if (unit === 'cm') return (amount / 2.54) * EMU_PER_INCH
  if (unit === 'mm') return (amount / 25.4) * EMU_PER_INCH
  if (unit === 'pt') return (amount / 72) * EMU_PER_INCH
  if (unit === 'px') return (amount / 96) * EMU_PER_INCH
  return amount
}

function presentationSize(inspect) {
  const size = inspect?.presentation?.size ?? inspect?.presentation?.slideSize ?? inspect?.slideSize
  const widthEmu =
    numberOrNull(size?.wEmu ?? size?.cxEmu ?? size?.widthEmu) ??
    parseDimensionToEmu(size?.width ?? size?.w ?? size?.cx)
  const heightEmu =
    numberOrNull(size?.hEmu ?? size?.cyEmu ?? size?.heightEmu) ??
    parseDimensionToEmu(size?.height ?? size?.h ?? size?.cy)
  return {
    width: size?.width ?? size?.w ?? null,
    height: size?.height ?? size?.h ?? null,
    widthEmu,
    heightEmu,
  }
}

function slideSize(slide, fallback) {
  const size = slide?.size ?? slide?.slideSize
  const widthEmu =
    numberOrNull(size?.wEmu ?? size?.cxEmu ?? size?.widthEmu) ??
    parseDimensionToEmu(size?.width ?? size?.w ?? size?.cx) ??
    fallback.widthEmu
  const heightEmu =
    numberOrNull(size?.hEmu ?? size?.cyEmu ?? size?.heightEmu) ??
    parseDimensionToEmu(size?.height ?? size?.h ?? size?.cy) ??
    fallback.heightEmu
  return {
    width: size?.width ?? size?.w ?? fallback.width,
    height: size?.height ?? size?.h ?? fallback.height,
    widthEmu,
    heightEmu,
  }
}

function bboxOf(shape) {
  const box = shape?.bbox ?? shape?.bounds ?? shape?.frame ?? shape?.position
  if (!isPlainObject(box)) return null
  return {
    xEmu: numberOrNull(box.xEmu ?? box.x ?? box.left),
    yEmu: numberOrNull(box.yEmu ?? box.y ?? box.top),
    wEmu: numberOrNull(box.wEmu ?? box.w ?? box.width ?? box.cx),
    hEmu: numberOrNull(box.hEmu ?? box.h ?? box.height ?? box.cy),
  }
}

function textPreviewOf(shape) {
  return String(shape?.textPreview ?? shape?.text ?? shape?.plainText ?? '').trim()
}

function hasText(shape, textPreview) {
  if (shape?.hasText === true) return true
  if (shape?.hasText === false && !textPreview) return false
  return Boolean(textPreview || asArray(shape?.runs).length || asArray(shape?.textRuns).length)
}

function shapeKind(shape, textPreview) {
  const raw = String(shape?.shapeType ?? shape?.type ?? shape?.kind ?? '').trim()
  const lower = raw.toLowerCase()
  if (shape?.chart || shape?.hasChart || lower.includes('chart')) return 'chart'
  if (shape?.table || shape?.hasTable || lower.includes('table')) return 'table'
  if (shape?.image || shape?.picture || lower.includes('picture') || lower.includes('image')) {
    return 'image'
  }
  if (hasText(shape, textPreview)) return 'text'
  return raw || 'shape'
}

function placeholderOf(shape) {
  const placeholder = shape?.placeholder ?? shape?.ph ?? null
  if (!placeholder) return null
  if (typeof placeholder === 'string') {
    return { type: placeholder, status: null, provenance: 'unknown' }
  }
  if (!isPlainObject(placeholder)) {
    return { type: String(placeholder), status: null, provenance: 'unknown' }
  }
  return {
    type: placeholder.type ?? placeholder.kind ?? null,
    idx: placeholder.idx ?? placeholder.index ?? null,
    status: placeholder.status ?? null,
    provenance: placeholder.provenance ?? shape?.placeholderProvenance ?? 'unknown',
  }
}

function detectorPlaceholderEvidence(placeholder) {
  const evidence = { ...placeholder }
  delete evidence.provenance
  return evidence
}

function collectRuns(shape) {
  const directRuns = asArray(shape?.runs).concat(asArray(shape?.textRuns))
  const textRuns = asArray(shape?.text?.runs)
  const paragraphs = asArray(shape?.paragraphs ?? shape?.text?.paragraphs)
  const paragraphRuns = paragraphs.flatMap((paragraph) =>
    asArray(paragraph?.runs ?? paragraph?.textRuns),
  )
  return [...directRuns, ...textRuns, ...paragraphRuns]
}

function fontOf(shape) {
  const runs = collectRuns(shape)
  const families = unique(
    compact([
      shape?.fontFamily,
      shape?.fontName,
      shape?.font?.name,
      ...runs.map((run) => run?.fontFamily ?? run?.fontName ?? run?.font?.name),
    ]).map(String),
  )
  const sizesPt = unique(
    compact([
      numberOrNull(shape?.fontSizePt ?? shape?.fontPt),
      fontSizeToPt(shape?.fontSize ?? shape?.font?.size),
      ...runs.map(
        (run) => numberOrNull(run?.fontSizePt ?? run?.fontPt) ?? fontSizeToPt(run?.fontSize),
      ),
    ]),
  )
  const colors = unique(
    compact([
      normalizeColor(shape?.fontColor ?? shape?.color ?? shape?.font?.color),
      ...runs.map((run) => normalizeColor(run?.fontColor ?? run?.color ?? run?.font?.color)),
    ]),
  )
  return { families, sizesPt, colors }
}

function fontSizeToPt(value) {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'number' && Number.isFinite(value)) return value
  const text = String(value).trim()
  const match = text.match(/^(-?\d+(?:\.\d+)?)(pt|px)?$/i)
  if (!match) return null
  const amount = Number(match[1])
  if (!Number.isFinite(amount)) return null
  return (match[2] ?? 'pt').toLowerCase() === 'px' ? amount * 0.75 : amount
}

function normalizeColor(value) {
  if (value === null || value === undefined || value === '') return null
  const text = String(value).trim().replace(/^#/, '')
  return /^[0-9a-f]{6}$/i.test(text) ? `#${text.toUpperCase()}` : String(value)
}

function fillOf(shape) {
  return normalizeColor(shape?.fillColor ?? shape?.fill?.color ?? shape?.fill)
}

function lineOf(shape) {
  if (shape?.lineNoFill === true) return { color: null, width: null, noFill: true }
  const color = normalizeColor(shape?.lineColor ?? shape?.line?.color ?? shape?.strokeColor)
  const width = shape?.lineWidth ?? shape?.line?.width ?? shape?.strokeWidth ?? null
  return color || width ? { color, width, noFill: false } : null
}

function zOrderOf(shape, fallbackIndex) {
  return numberOrNull(shape?.zOrder ?? shape?.z ?? shape?.order ?? shape?.zIndex) ?? fallbackIndex
}

function normalizeShape(shape, slideIndex, shapeIndex, size) {
  const textPreview = textPreviewOf(shape)
  const type = shapeKind(shape, textPreview)
  const bbox = bboxOf(shape)
  const font = fontOf(shape)
  const placeholder = placeholderOf(shape)
  const risks = []
  validateObject({
    risks,
    bbox,
    size,
    type,
    textPreview,
    font,
    placeholder,
    slideIndex,
    shapeIndex,
  })
  return {
    id: shape?.id ?? shape?.shapeId ?? null,
    name: shape?.name ?? shape?.shapeName ?? null,
    type,
    rawType: shape?.shapeType ?? shape?.type ?? shape?.kind ?? null,
    zOrder: zOrderOf(shape, shapeIndex),
    bbox,
    textPreview,
    font,
    fill: fillOf(shape),
    line: lineOf(shape),
    placeholder,
    risks,
  }
}

function validateObject({ risks, bbox, size, type, textPreview, font, placeholder, slideIndex }) {
  const invalidSize = bbox
    ? type === 'connector'
      ? bbox.wEmu < 0 || bbox.hEmu < 0 || (bbox.wEmu === 0 && bbox.hEmu === 0)
      : bbox.wEmu <= 0 || bbox.hEmu <= 0
    : false
  if (!bbox) {
    pushRisk(risks, 'warning', 'bbox-missing', 'Object is missing bbox in final inspect', {
      slide: slideIndex,
    })
  } else if (
    bbox.xEmu === null ||
    bbox.yEmu === null ||
    bbox.wEmu === null ||
    bbox.hEmu === null ||
    invalidSize
  ) {
    pushRisk(
      risks,
      'warning',
      'bbox-invalid',
      'Object bbox is missing values or has non-positive size',
      {
        slide: slideIndex,
        bbox,
      },
    )
  } else if (
    Number.isFinite(size.widthEmu) &&
    Number.isFinite(size.heightEmu) &&
    (bbox.xEmu + bbox.wEmu <= 0 ||
      bbox.yEmu + bbox.hEmu <= 0 ||
      bbox.xEmu >= size.widthEmu ||
      bbox.yEmu >= size.heightEmu)
  ) {
    pushRisk(
      risks,
      'warning',
      'bbox-off-canvas',
      'Object bbox is completely outside the slide canvas',
      {
        slide: slideIndex,
        bbox,
      },
    )
  }

  if (placeholder && !textPreview) {
    pushRisk(risks, 'warning', 'empty-placeholder', 'Placeholder object is empty in final layout', {
      slide: slideIndex,
      placeholder: detectorPlaceholderEvidence(placeholder),
      observed: { textEmpty: true },
    })
  }
  if (
    textPreview &&
    (DEFAULT_PROMPT_TEXT_RE.test(textPreview) ||
      (placeholder && STRUCTURAL_PLACEHOLDER_TEXT_RE.test(textPreview)))
  ) {
    pushRisk(
      risks,
      'warning',
      'default-placeholder-text',
      'Object still contains default placeholder text',
      {
        slide: slideIndex,
        textPreview,
      },
    )
  }
  if (type === 'text' && font.families.length === 0) {
    pushRisk(risks, 'warning', 'font-family-missing', 'Text object has no disclosed font family', {
      slide: slideIndex,
    })
  }
  if (type === 'text' && font.sizesPt.length === 0) {
    pushRisk(risks, 'warning', 'font-size-missing', 'Text object has no disclosed font size', {
      slide: slideIndex,
    })
  }
  for (const sizePt of font.sizesPt) {
    if (sizePt > 0 && sizePt < 6) {
      pushRisk(
        risks,
        'warning',
        'font-size-too-small',
        'Text object discloses a font size below 6pt',
        {
          slide: slideIndex,
          sizePt,
        },
      )
    }
  }
}

function normalizeSlide(slide, fallbackSize) {
  const index = numberOrNull(slide?.index ?? slide?.slide) ?? 0
  const partName = String(slide?.partName ?? slide?.part_name ?? slide?.part ?? '')
    .replaceAll('\\', '/')
    .replace(/^\/+/, '')
  const size = slideSize(slide, fallbackSize)
  const rawObjects = asArray(slide?.shapes ?? slide?.objects ?? slide?.elements)
  const objects = rawObjects.map((shape, shapeIndex) =>
    normalizeShape(shape, index, shapeIndex, size),
  )
  const risks = []
  const seenIds = new Set()
  const seenNames = new Set()
  const reportedIds = new Set()
  const reportedNames = new Set()
  for (const object of objects) {
    if (object.id !== null && object.id !== undefined) {
      const key = String(object.id)
      if (seenIds.has(key) && !reportedIds.has(key)) {
        pushRisk(risks, 'warning', 'duplicate-object-id', 'Slide has duplicate object ids', {
          slide: index,
          id: object.id,
        })
        reportedIds.add(key)
      }
      seenIds.add(key)
    }
    if (object.name) {
      const key = String(object.name)
      if (seenNames.has(key) && !reportedNames.has(key)) {
        pushRisk(risks, 'warning', 'duplicate-object-name', 'Slide has duplicate object names', {
          slide: index,
          name: object.name,
        })
        reportedNames.add(key)
      }
      seenNames.add(key)
    }
  }
  return {
    index,
    partName,
    size,
    objectCount: objects.length,
    objects: objects.sort((a, b) => Number(a.zOrder ?? 0) - Number(b.zOrder ?? 0)),
    risks,
  }
}

function flattenRisks(slides) {
  const risks = []
  for (const slide of slides) {
    for (const risk of slide.risks) {
      const finding = withSlideReference({ ...risk, slidePart: slide.partName }, slide.index)
      risks.push(
        finding.classification === 'actionable'
          ? { ...finding, reviewIdentity: reviewFindingIdentity(finding) }
          : finding,
      )
    }
    for (const object of slide.objects) {
      for (const risk of object.risks) {
        const finding = withSlideReference(
          {
            ...risk,
            slidePart: slide.partName,
            objectId: object.id,
            objectName: object.name,
            objectType: object.type,
          },
          slide.index,
        )
        risks.push(
          finding.classification === 'actionable'
            ? { ...finding, reviewIdentity: reviewFindingIdentity(finding) }
            : finding,
        )
      }
    }
  }
  return risks
}

function withSlideReference(risk, fallbackIndex) {
  const slideIndex = numberOrNull(risk.slideIndex ?? risk.slide ?? fallbackIndex)
  if (!Number.isInteger(slideIndex) || slideIndex < 0) return risk
  const reference = slideReference(slideIndex)
  return {
    ...risk,
    slide: reference.slideIndex,
    ...reference,
  }
}

function slideReference(slideIndex) {
  const slideNumber = slideIndex + 1
  return {
    slideIndex,
    slideNumber,
    previewFile: `slide-${String(slideNumber).padStart(3, '0')}.png`,
  }
}

function countBySeverity(risks) {
  const counts = { error: 0, warning: 0, info: 0 }
  for (const risk of risks) {
    const severity = risk.severity in counts ? risk.severity : 'warning'
    counts[severity] += 1
  }
  return counts
}

function countByClassification(risks) {
  const counts = { actionable: 0, informational: 0 }
  for (const risk of risks) {
    const classification = risk.classification === 'informational' ? 'informational' : 'actionable'
    counts[classification] += 1
  }
  return counts
}

function slideIndexes(risks) {
  return unique(
    risks
      .map((risk) => numberOrNull(risk.slide))
      .filter((slide) => Number.isInteger(slide) && slide >= 0),
  ).sort((a, b) => a - b)
}

function slideReferences(risks) {
  const indexes = slideIndexes(risks)
  const references = indexes.map((index) => slideReference(index))
  return {
    slides: indexes,
    slideIndexes: indexes,
    slideNumbers: references.map((reference) => reference.slideNumber),
    previewFiles: references.map((reference) => reference.previewFile),
  }
}

function summarizeByCode(risks) {
  const groups = new Map()
  for (const risk of risks) {
    const code = risk.code || 'unknown'
    const classification = risk.classification === 'informational' ? 'informational' : 'actionable'
    const group = groups.get(code) ?? {
      code,
      classification,
      severity: risk.severity ?? 'warning',
      count: 0,
      risks: [],
    }
    group.count += 1
    group.risks.push(risk)
    groups.set(code, group)
  }
  return [...groups.values()]
    .map((group) => {
      const references = slideReferences(group.risks)
      return {
        code: group.code,
        classification: group.classification,
        severity: group.severity,
        count: group.count,
        affectedSlideCount: references.slideIndexes.length,
        slides: references.slides.slice(0, MAX_SUMMARY_SLIDES),
        slideIndexes: references.slideIndexes.slice(0, MAX_SUMMARY_SLIDES),
        slideNumbers: references.slideNumbers.slice(0, MAX_SUMMARY_SLIDES),
        previewFiles: references.previewFiles.slice(0, MAX_SUMMARY_SLIDES),
        slidesTruncated: references.slideIndexes.length > MAX_SUMMARY_SLIDES,
      }
    })
    .sort((a, b) => b.count - a.count || a.code.localeCompare(b.code, 'en'))
}

function summarizeRisks(risks) {
  const byCode = summarizeByCode(risks)
  const actionableRisks = risks.filter((risk) => risk.classification !== 'informational')
  const informationalRisks = risks.filter((risk) => risk.classification === 'informational')
  const affectedSlides = slideReferences(risks)
  const actionableSlides = slideReferences(actionableRisks)
  return {
    riskCount: risks.length,
    actionableRiskCount: actionableRisks.length,
    informationalRiskCount: informationalRisks.length,
    affectedSlideCount: affectedSlides.slideIndexes.length,
    actionableSlideCount: actionableSlides.slideIndexes.length,
    slideIndexBase: 0,
    slideNumberBase: 1,
    affectedSlides: affectedSlides.slides.slice(0, MAX_SUMMARY_SLIDES),
    affectedSlideIndexes: affectedSlides.slideIndexes.slice(0, MAX_SUMMARY_SLIDES),
    affectedSlideNumbers: affectedSlides.slideNumbers.slice(0, MAX_SUMMARY_SLIDES),
    affectedPreviewFiles: affectedSlides.previewFiles.slice(0, MAX_SUMMARY_SLIDES),
    affectedSlidesTruncated: affectedSlides.slideIndexes.length > MAX_SUMMARY_SLIDES,
    actionableSlideIndexes: actionableSlides.slideIndexes.slice(0, MAX_SUMMARY_SLIDES),
    actionableSlideNumbers: actionableSlides.slideNumbers.slice(0, MAX_SUMMARY_SLIDES),
    actionablePreviewFiles: actionableSlides.previewFiles.slice(0, MAX_SUMMARY_SLIDES),
    actionableSlidesTruncated: actionableSlides.slideIndexes.length > MAX_SUMMARY_SLIDES,
    bySeverity: countBySeverity(risks),
    byClassification: countByClassification(risks),
    byCode,
    topActionable: byCode.filter((group) => group.classification === 'actionable').slice(0, 5),
  }
}

export function buildLayoutSnapshot(inspect, options = {}) {
  const sourceLabel = typeof options === 'string' ? options : (options.sourceLabel ?? '')
  const size = presentationSize(inspect)
  const slides = asArray(inspect?.slides).map((slide) => normalizeSlide(slide, size))
  const objects = slides.flatMap((slide) => slide.objects)
  const risks = flattenRisks(slides)
  const riskSummary = summarizeRisks(risks)
  return {
    schemaVersion: LAYOUT_SNAPSHOT_SCHEMA_VERSION,
    status: riskSummary.actionableRiskCount > 0 ? 'warn' : 'pass',
    source: sourceLabel,
    summary: {
      slideCount: slideCountOf(inspect),
      objectCount: objects.length,
      textObjectCount: objects.filter((object) => object.type === 'text').length,
      placeholderCount: objects.filter((object) => object.placeholder).length,
      chartCount: objects.filter((object) => object.type === 'chart').length,
      tableCount: objects.filter((object) => object.type === 'table').length,
      imageCount: objects.filter((object) => object.type === 'image').length,
      ...riskSummary,
    },
    slides,
    risks,
  }
}

function projectRisk(risk) {
  const evidence = { ...(risk ?? {}) }
  delete evidence.message
  delete evidence.previewFile
  delete evidence.slideNumber
  return evidence
}

function compareCanonical(left, right) {
  const leftJson = canonicalJsonV1(left)
  const rightJson = canonicalJsonV1(right)
  if (leftJson === rightJson) return 0
  return leftJson < rightJson ? -1 : 1
}

export function layoutSemanticProjectionV1(snapshot) {
  return {
    schemaVersion: snapshot?.schemaVersion ?? null,
    status: snapshot?.status ?? null,
    slides: asArray(snapshot?.slides)
      .map((slide) => ({
        index: slide?.index ?? null,
        partName: slide?.partName ?? '',
        size: slide?.size ?? null,
        objects: asArray(slide?.objects)
          .map((object) => ({
            id: object?.id ?? null,
            name: object?.name ?? null,
            type: object?.type ?? null,
            rawType: object?.rawType ?? null,
            zOrder: object?.zOrder ?? null,
            bbox: object?.bbox ?? null,
            textPreview: object?.textPreview ?? '',
            font: object?.font ?? null,
            fill: object?.fill ?? null,
            line: object?.line ?? null,
            placeholder: object?.placeholder ?? null,
          }))
          .sort(
            (left, right) =>
              Number(left.zOrder ?? 0) - Number(right.zOrder ?? 0) || compareCanonical(left, right),
          ),
      }))
      .sort(
        (left, right) =>
          Number(left.index ?? 0) - Number(right.index ?? 0) || compareCanonical(left, right),
      ),
    risks: asArray(snapshot?.risks).map(projectRisk).sort(compareCanonical),
  }
}

export function layoutSemanticSha256(snapshot) {
  return createHash('sha256')
    .update(canonicalJsonV1(layoutSemanticProjectionV1(snapshot)), 'utf8')
    .digest('hex')
}

export function buildLayoutSnapshotFailure(sourceLabel, error) {
  return {
    schemaVersion: LAYOUT_SNAPSHOT_SCHEMA_VERSION,
    status: 'fail',
    source: sourceLabel ?? '',
    summary: {
      slideCount: 0,
      objectCount: 0,
      textObjectCount: 0,
      placeholderCount: 0,
      chartCount: 0,
      tableCount: 0,
      imageCount: 0,
      riskCount: 1,
      bySeverity: { error: 1, warning: 0, info: 0 },
    },
    slides: [],
    risks: [
      {
        severity: 'error',
        code: 'layout-snapshot-error',
        message: error instanceof Error ? error.message : String(error),
      },
    ],
  }
}
