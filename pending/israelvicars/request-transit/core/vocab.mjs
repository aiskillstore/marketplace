// User-visible vocabulary for each Transit skill. Packs may be partial: the
// request pack is the compatibility fallback for every missing string.
export const vocab = {
  request: {
    lineNoun: 'service', stationNoun: 'hop', hopNoun: 'hop', hopNounPlural: 'hops',
    play: 'Play', pause: 'Pause',
    helpTitle: 'Keyboard shortcuts', space: 'play / pause', nextHop: 'next hop', previousHop: 'previous hop',
    seek: 'seek 0.5 s', frame: 'step one frame', startEnd: 'start / end', speed: 'speed 0.5x / 1x / 2x',
    click: 'click', clickHelp: 'station, train or line: select that hop', inspectClick: 'click a station, train or line', pauseHelp: 'selects the hop in progress',
    escape: 'deselect / close', help: 'this help',
    of: 'of', video: '1 s of video', trace: 'trace', infrastructure: 'infrastructure',
    delay: 'DELAY', serviceAlert: 'SERVICE ALERT', request: 'request', response: 'response',
    legendDelay: 'delay: self time ≥', legendAlert: 'service alert: error starts here',
    legendInfra: 'dotted: infrastructure (no spans of its own)',
    synthetic: 'SYNTHETIC sample data', renderedLocally: 'rendered locally by Transit',
    unmatched: 'unmatched', matched: 'matched', contracts: 'contracts', noContractIndex: 'no contract index',
    contractFooter: true,   // footer counts hops without a contract; only request traces have contracts
    scrubbedValues: 'value(s) scrubbed from names, messages and URLs', scrubOff: 'Value scrubbing was OFF for this page: do not share it.',
    error: 'error', slow: 'slow', ok: 'ok',
    tableTitle: 'Hops', tableStart: 'start', tableFrom: 'from', tableTo: 'to', tableSpan: 'span',
    tableStatus: 'status', tableContract: 'contract', infrastructureHop: 'infrastructure hop', infrastructureHopTitle: 'Infrastructure hop',
    unmatchedContracts: 'unmatched (contracts not indexed)', unmatchedShort: 'unmatched',
    noHopSelected: 'no hop selected', inspectHop: 'Pause, press', or: 'or',
    inspectTail: 'to inspect a hop.', shortcuts: 'Shortcuts', transit: 'Transit',
    hop: 'HOP', span: 'SPAN', from: 'from', client: 'client', server: 'server',
    noServerSpan: 'no server span', notInstrumented: 'is not instrumented',
    status: 'status', unset: 'unset', resource: 'resource', attributes: 'Attributes',
    serverSpan: 'server span', children: 'Children', none: 'none',
    sensitiveRedacted: 'Sensitive-looking keys are redacted at build time.',
    redactedAcross: 'attribute(s) redacted across this trace before rendering.',
    expectedRequestResponse: 'Expected request / response', contractsNotIndexed: 'Contracts not indexed. The contract layer is optional: build an index with',
    thenBuildWith: 'then build the page with', noHopContract: 'No hop contract for this span',
    internalWorkInside: 'internal work inside', noContractExpected: 'No contract expected',
    fallback: 'FALLBACK', matchedTag: 'MATCHED', message: 'Message',
    noRequestSchema: 'No request schema found', noResponseType: 'No response type found',
    responseBody: 'no body (void)', unknown: 'unknown', unresolved: 'unresolved',
    deeperFields: '… deeper fields not shown', optional: 'optional', required: 'required',
    sharedPackage: 'shared package', declared: 'declared',
    clientCallFrom: 'client call from', in: 'in', wholeTrace: 'of the whole trace',
    spanInsideClient: 'server span inside the client call', spanInsideParent: 'span inside its parent',
    deselect: 'Deselect (Esc)', more: 'more',
    confidenceHigh: 'high confidence', confidenceMedium: 'medium confidence', confidenceLow: 'low confidence',
    validator: 'validator', type: 'type', spec: 'spec', schema: 'schema',
    kind: 'kind', start: 'start', duration: 'duration', self: 'self',
    groups: { http: 'HTTP', db: 'DB', messaging: 'Messaging', rpc: 'RPC', other: 'Other' },
  },
  ci: {
    lineNoun: 'job', stationNoun: 'step', hopNoun: 'dependency', hopNounPlural: 'dependencies',
    request: 'workflow run', response: 'completion', delay: 'DELAY', serviceAlert: 'SERVICE ALERT',
    legendDelay: 'delay: self time ≥', legendAlert: 'service alert: error starts here',
    tableTitle: 'Steps', tableSpan: 'step', infrastructure: 'workflow infrastructure',
    hop: 'STEP', span: 'JOB', trace: 'run', error: 'failed', slow: 'slow step', skipped: 'skipped', contractFooter: false,
  },
  agent: {
    lineNoun: 'tool family', stationNoun: 'call', hopNoun: 'call', hopNounPlural: 'calls',
    trace: 'session', request: 'session', response: 'completion', tableTitle: 'Tool calls', tableSpan: 'call',
    delay: 'DELAY', serviceAlert: 'SERVICE ALERT', legendDelay: 'delay: self time ≥',
    legendAlert: 'service alert: error starts here', infrastructure: 'agent infrastructure',
    hop: 'CALL', span: 'TOOL', error: 'error', slow: 'slow call', contractFooter: false,
  },
};

export const VOCAB_PACKS = vocab;
export const DEFAULT_VOCAB = 'request';

export function resolveVocab(value = DEFAULT_VOCAB) {
  const pack = typeof value === 'string' ? vocab[value] : value;
  if (typeof value === 'string' && !pack) throw new Error(`unknown vocab pack: ${value}`);
  return { ...vocab.request, ...(pack || {}) };
}
