// Bounded compositions; names here describe renderer geometry, never business content.
export const ANNUAL_LAYOUTS = {
  cover: { standard: ['title', 'abstract', 'metrics'] },
  summary: { standard: ['main', 'side'] },
  evidence: {
    rail: ['chart0', 'detail'],
    wide: ['chart0', 'detail'],
    paired: ['chart0', 'chart1', 'detail'],
    lead: ['chart0', 'chart1', 'chart2', 'detail'],
    quad: ['chart0', 'chart1', 'chart2', 'chart3', 'detail'],
  },
  matrix: { full: ['main', 'detail'], compact: ['main', 'detail'] },
  composite: { standard: ['chart0', 'main', 'detail'] },
  timeline: { standard: ['phases', 'main', 'detail'] },
  decision: { standard: ['main', 'side'] },
  argument: { column: ['main'], split: ['main', 'side'] },
}
