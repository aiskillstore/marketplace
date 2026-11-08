// Native, editable atmosphere. Clip sampled ellipse outlines to the actual canvas
// before authoring, so edge cropping never leaves out-of-bounds slide objects.
export function clippedPulseEllipse(ellipse, canvas) {
  const { cx, cy, rx, ry, rotation } = ellipse,
    angle = (rotation * Math.PI) / 180
  let points = Array.from({ length: 128 }, (_, i) => {
    const t = (i * Math.PI * 2) / 128,
      x = rx * Math.cos(t),
      y = ry * Math.sin(t)
    return [
      cx + x * Math.cos(angle) - y * Math.sin(angle),
      cy + x * Math.sin(angle) + y * Math.cos(angle),
    ]
  })
  for (const [axis, bound, keepGreater] of [
    [0, 0, true],
    [0, canvas.widthIn, false],
    [1, 0, true],
    [1, canvas.heightIn, false],
  ]) {
    const next = [],
      inside = (p) => (keepGreater ? p[axis] >= bound : p[axis] <= bound)
    for (let i = 0; i < points.length; i++) {
      const a = points[i],
        b = points[(i + 1) % points.length],
        ai = inside(a),
        bi = inside(b)
      if (ai) next.push(a)
      if (ai !== bi) {
        const t = (bound - a[axis]) / (b[axis] - a[axis])
        next.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])])
      }
    }
    points = next
  }
  if (points.length < 3) throw Error('Atmosphere ellipse must intersect the canvas')
  points = points.map(([x, y]) => [
    Math.max(0, Math.min(canvas.widthIn, x)),
    Math.max(0, Math.min(canvas.heightIn, y)),
  ])
  const x = Math.min(...points.map((p) => p[0])),
    y = Math.min(...points.map((p) => p[1])),
    w = Math.max(...points.map((p) => p[0])) - x,
    h = Math.max(...points.map((p) => p[1])) - y
  if (w <= 0 || h <= 0) throw Error('Atmosphere requires visible area')
  return { frame: [x, y, w, h], points: points.map(([a, b]) => [(a - x) / w, (b - y) / h]) }
}

export function pulseAtmosphere(design, role) {
  return design.pulse.atmosphere[role].map((ellipse, i) => ({
    kind: 'atmosphere',
    name: `Atmosphere${i}`,
    ...clippedPulseEllipse(ellipse, design.canvas),
    color: ellipse.color,
    alpha: ellipse.alpha,
    gradientAngle: ellipse.gradientAngle,
  }))
}
