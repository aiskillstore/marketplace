import path from 'node:path';
import { walk } from './ast_utils.mjs';

export function decideRemovals(ts, testRecords, doFix, report, fs, projectDir) {
  const removableTests = [];
  const removableStmts = [];

  for (const rec of testRecords) {
    // never plan a removal in a symlinked test file — the write would follow
    // the link out of the scanned tree. Excluding it here (not just at the
    // write) keeps report.fixed counts and report.plan honest about what --fix
    // will actually touch.
    if (fs.lstatSync(rec.sf.fileName).isSymbolicLink()) {
      console.error(`captain-obvious: skipping ${rec.sf.fileName} — symlinked test files are never rewritten (the write would follow the link)`);
      continue;
    }
    const wants = (f) => f.deletable === 'safe';

    if (rec.isDuplicate && wants(rec.findings.find(f => f.category === 'duplicate-test'))) {
      removableTests.push(rec);
      continue;
    }
    const never = rec.findings.find(f => ['never-asserts', 'silent-smoke'].includes(f.category));
    if (never) {
      if (wants(never)) removableTests.push(rec);
      continue;
    }
    // no-assert / skipped-test are never deletable:'safe' — whole-test
    // removal for them is the agent's call, not the fixer's
    if (rec.findings.some(f => ['no-assert', 'skipped-test'].includes(f.category))) continue;

    const stmtFindings = rec.findings.filter(f => f.stmtRef);
    const deadStmts = stmtFindings.filter(f => f.category === 'dead-assert');
    const liveDeletable = stmtFindings.filter(f => f.category !== 'dead-assert').filter(wants);
    const allRedundant =
      rec.expectCount > 0 &&
      liveDeletable.length === rec.expectCount &&
      rec.nonRedundantExpects === 0 &&
      rec.nestedAssertions === 0;

    let remainingCall = false;
    if (allRedundant && ts.isBlock(rec.fn.body)) {
      const del = new Set(liveDeletable.map(f => f.stmtRef));
      for (const st of rec.fn.body.statements) {
        if (del.has(st)) continue;
        if (ts.isExpressionStatement(st) && ts.isStringLiteral(st.expression)) continue;
        walk(ts, st, n => {
          if (ts.isCallExpression(n) || ts.isNewExpression(n)) remainingCall = true;
        });
        if (remainingCall) break;
      }
    }
    const wholeTest = allRedundant && !remainingCall;

    if (wholeTest) removableTests.push(rec);
    else {
      const remainingAsserts = rec.nonRedundantExpects + rec.nestedAssertions +
        stmtFindings.filter(f => f.deletable === 'report-only').length;
      if (liveDeletable.length > 0 && remainingAsserts > 0 && !rec.hasAssertionCtl) {
        removableStmts.push(...liveDeletable.map(f => ({ rec, stmt: f.stmtRef })));
      }
      removableStmts.push(...deadStmts.map(f => ({ rec, stmt: f.stmtRef })));
    }
  }

  report.plan = {
    testsToRemove: removableTests.map(r => ({ file: path.relative(projectDir, r.sf.fileName), line: r.line, test: r.title })),
    assertionsToRemove: removableStmts.length,
  };

  if (doFix) {
    const editsByFile = new Map();
    const removedTestPos = new Set();
    for (const rec of removableTests) {
      const arr = editsByFile.get(rec.sf.fileName) ?? [];
      arr.push({ start: rec.stmt.getFullStart(), end: rec.stmt.getEnd() });
      removedTestPos.add(rec.stmt);
      editsByFile.set(rec.sf.fileName, arr);
    }
    for (const { rec, stmt } of removableStmts) {
      if (removedTestPos.has(rec.stmt)) continue;
      const arr = editsByFile.get(rec.sf.fileName) ?? [];
      arr.push({ start: stmt.getFullStart(), end: stmt.getEnd() });
      editsByFile.set(rec.sf.fileName, arr);
    }
    let filesChanged = 0;
    for (const [file, edits] of editsByFile) {
      let text = fs.readFileSync(file, 'utf8');
      edits.sort((a, b) => b.start - a.start);
      for (const e of edits) text = text.slice(0, e.start) + text.slice(e.end);
      fs.writeFileSync(file, text);
      filesChanged++;
    }
    report.fixed = { testsRemoved: removableTests.length, assertionsRemoved: removableStmts.length, filesChanged };
  }
}
