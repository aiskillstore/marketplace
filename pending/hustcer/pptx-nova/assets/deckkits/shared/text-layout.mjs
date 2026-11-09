import { textUnits } from './design-contract.mjs'
import { wrapCjkText } from './design-text.mjs'

export function fitTextPlan(value, frame, style, path) {
  if (typeof value !== 'string' || !value.trim()) throw Error(`${path}: nonblank text required`)
  const cap = ((frame[2] - 0.04) * 72) / style.sizePt / (style.bold ? 1.08 : 1)
  const text = wrapCjkText(value, cap * 0.91)
  let lines = 0
  for (const line of text.split(/\r\n|\r|\n/)) {
    lines++
    let used = 0
    for (const token of line.split(/(\s+)/u)) {
      const n = textUnits(token)
      if (n > cap) throw Error(`${path}: unbroken token exceeds width`)
      if (used && used + n > cap) {
        lines++
        used = 0
      }
      used += n
    }
  }
  const requiredHeight = (lines * style.sizePt * (style.sizePt >= 23 ? 1.18 : 1.5)) / 72 + 0.025
  if (requiredHeight > frame[3] + 0.002)
    throw Error(
      `${path}: ${lines} lines exceed ${frame[3].toFixed(2)}in; select a legal layout, reorganize or split`,
    )
  return {
    kind: 'text',
    text,
    frame: [...frame],
    allocatedFrame: [...frame],
    style: { ...style },
    path,
    paths: [path],
    estimatedLines: lines,
    requiredHeight,
  }
}
