import { canon, namesDiverge } from './ast_utils.mjs';
import { toReportFinding, enclosingDescribeKey } from './analyzer.mjs';

export function markDuplicates(ts, printer, testRecords, allFindings, projectDir) {
  const seen = new Map();
  const seenGlobal = new Map();
  for (const rec of testRecords) {
    const bodyText = ts.isBlock(rec.fn.body)
      ? printer.printNode(ts.EmitHint.Unspecified, rec.fn.body, rec.sf)
      : rec.fn.body.getText(rec.sf);
    // snapshot/baseline tests have identical bodies by design — each is keyed
    // to a distinct stored baseline by test name, so deleting one orphans it
    if (/Match\w*Snapshot/.test(bodyText)) continue;
    const bodyKey = canon(ts, bodyText);
    if (bodyKey.length < 8) continue;
    const key = enclosingDescribeKey(ts, rec.stmt, rec.sf) + '::' + bodyKey;
    if (seen.has(key)) {
      const first = seen.get(key);
      let reason = `body is identical to "${first.title}" (line ${first.line}) in the same suite`;
      if (namesDiverge(rec.title, first.title)) {
        reason += " — names differ, so this is likely a copy-paste that leaves this test's " +
          'named behaviour untested; deleting is coverage-safe but consider fixing the body instead';
      }
      const f = { category: 'duplicate-test', level: 'proven', deletable: 'safe',
        reason, stmtRef: null };
      rec.findings.push(f);
      rec.isDuplicate = true;
      allFindings.push(toReportFinding(projectDir, rec, f));
    } else {
      seen.set(key, rec);
    }

    const gkey = bodyKey;
    if (seenGlobal.has(gkey)) {
      const first = seenGlobal.get(gkey);
      const sameScope = first.sf.fileName === rec.sf.fileName &&
        enclosingDescribeKey(ts, first.stmt, first.sf) === enclosingDescribeKey(ts, rec.stmt, rec.sf);
      if (!rec.isDuplicate && !sameScope) {
        const where = `${first.sf.fileName.split('/').pop()}:${first.line}`;
        const f = { category: 'duplicate-test', level: 'advisory', deletable: 'report-only',
          reason: `body is identical to "${first.title}" (${where}) in a different suite — ` +
            'likely redundant, but beforeEach/setup may differ, so review before removing', stmtRef: null };
        rec.findings.push(f);
        allFindings.push(toReportFinding(projectDir, rec, f));
      }
    } else {
      seenGlobal.set(gkey, rec);
    }
  }
}
