// Registered roles describe component responsibilities, independent of slide type names.
export const BIENNALE_REGIONS = {
  cover: ['date', 'title', 'subline', 'credits'],
  manifesto: ['quote', 'attribution'],
  programme: ['kicker', 'word', 'description', 'heading', 'strands'],
  chapter: ['rail', 'number', 'title', 'lede'],
  data: ['title', 'label', 'stats', 'chart', 'source'],
  quote: ['kicker', 'quote', 'author', 'role'],
  calendar: ['title', 'label', 'table'],
  colophon: ['kicker', 'title', 'credits'],
}

// Static input fields project to these regions. Repeating/combined fields are checked
// against actual resolved component frames, rather than independent string budgets.
export const BIENNALE_FIELDS = {
  cover: { dateRange: ['date', 'date'], title: ['title', '$title'], subline: ['subline', 'label'] },
  manifesto: { quote: ['quote', '$title'], attribution: ['attribution', 'label'] },
  programme: {
    kicker: ['kicker', 'label'],
    word: ['word', '$title'],
    description: ['description', 'body'],
    headLabel: ['heading', 'label'],
  },
  chapter: {
    rail: ['rail', 'label'],
    number: ['number', 'number'],
    title: ['title', '$title'],
    lede: ['lede', 'body'],
  },
  data: { title: ['title', '$title'], label: ['label', 'label'], source: ['source', 'source'] },
  quote: {
    kicker: ['kicker', 'label'],
    quote: ['quote', '$title'],
    author: ['author', 'label'],
    role: ['role', 'body'],
  },
  calendar: { title: ['title', '$title'], label: ['label', 'label'] },
  colophon: { kicker: ['kicker', 'label'], title: ['title', '$title'] },
}
