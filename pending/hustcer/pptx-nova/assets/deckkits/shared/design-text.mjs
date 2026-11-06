// Insert layout breaks only. Preserve every input character and keep closing punctuation
// attached to a preceding word; the PPTX renderer still owns final font measurement.
export function wrapCjkText(value, capacity) {
  if (!/[\u2e80-\u9fff]/u.test(value)) return value
  const segmenter = new Intl.Segmenter('zh', { granularity: 'word' })
  return value
    .split('\n')
    .map((paragraph) => {
      const lines = []
      let words = [],
        width = 0
      const units = (s) => [...s].reduce((n, c) => n + (c.codePointAt(0) > 255 ? 1 : 0.52), 0)
      for (const { segment } of segmenter.segment(paragraph)) {
        const w = units(segment)
        if (width + w > capacity && words.length) {
          if (/^[，。！？、；：）》】」』,.!?;:]+$/u.test(segment)) {
            const last = words.pop()
            if (words.length) lines.push(words.join(''))
            words = [last, segment]
            width = units(last) + w
          } else {
            lines.push(words.join(''))
            words = [segment]
            width = w
          }
        } else {
          words.push(segment)
          width += w
        }
      }
      if (words.length) lines.push(words.join(''))
      return lines.join('\n')
    })
    .join('\n')
}
