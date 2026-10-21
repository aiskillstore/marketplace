import path from 'node:path';
import {
  walk,
  rootIdentifier,
  isLiteralish,
  literalValue,
  assertionMachineryNodes
} from './ast_utils.mjs';
import { parseExpectation } from './expect_parser.mjs';
import { detectMockEcho } from './mock_echo.mjs';
import { classifyExpect } from './classifier.mjs';
import { subjectLaunders } from './laundering.mjs';

export const ASSERTION_ROOTS = new Set(['expect', 'assert', 'chai', 'sinon', 'expectTypeOf', 'assertType']);
export const NEUTRAL_EXPECT_STATIC = new Set(['assertions', 'hasAssertions']);

export const isAssertionRoot = (root) =>
  ASSERTION_ROOTS.has(root) || /^(expect|assert|verify|check|should)/i.test(root);

export function isOutermostAssertCall(ts, n) {
  let p = n.parent;
  while (p && (ts.isPropertyAccessExpression(p) || ts.isCallExpression(p) ||
               ts.isAwaitExpression(p) || ts.isParenthesizedExpression(p) ||
               ts.isNonNullExpression(p))) {
    if (ts.isCallExpression(p)) {
      const r = rootIdentifier(ts, p.expression);
      if (r && isAssertionRoot(r)) return false;
    }
    p = p.parent;
  }
  return true;
}

export function isNoiseCall(ts, expr) {
  let curr = expr;
  while (curr) {
    if (ts.isCallExpression(curr) || ts.isNewExpression(curr)) {
      curr = curr.expression;
    } else if (ts.isPropertyAccessExpression(curr)) {
      const name = curr.name.text;
      if (name === 'console' || name === 'log' || name === 'logger' || name === 'logging') return true;
      curr = curr.expression;
    } else if (ts.isElementAccessExpression(curr) || ts.isNonNullExpression(curr) ||
               ts.isAwaitExpression(curr) || ts.isParenthesizedExpression(curr)) {
      curr = curr.expression;
    } else if (ts.isIdentifier(curr)) {
      const text = curr.text;
      return text === 'console' || text === 'log' || text === 'logger' || text === 'logging';
    } else if (curr.kind === ts.SyntaxKind.ThisKeyword) {
      return false;
    } else {
      break;
    }
  }
  return false;
}

export function isTestBlock(ts, stmt) {
  if (!ts.isExpressionStatement(stmt) || !ts.isCallExpression(stmt.expression)) return null;
  const c = stmt.expression;
  let name = null, modifier = null;
  if (ts.isIdentifier(c.expression)) name = c.expression.text;
  else if (ts.isPropertyAccessExpression(c.expression) && ts.isIdentifier(c.expression.expression) &&
           ['only', 'skip', 'fails', 'concurrent', 'sequential'].includes(c.expression.name.text)) {
    name = c.expression.expression.text;
    modifier = c.expression.name.text;
  }
  if (!name || !['it', 'test', 'xit', 'fit'].includes(name)) return null;
  const fn = c.arguments.find(a => ts.isArrowFunction(a) || ts.isFunctionExpression(a));
  if (!fn) return null;
  const title = c.arguments[0] && ts.isStringLiteralLike(c.arguments[0]) ? c.arguments[0].text : '<dynamic>';
  const skipped = name === 'xit' || modifier === 'skip';
  return { stmt, title, fn, skipped };
}

export function enclosingDescribeKey(ts, node, sf) {
  let n = node.parent;
  while (n) {
    if (ts.isCallExpression(n) && rootIdentifier(ts, n.expression) === 'describe') return `${sf.fileName}#${n.pos}`;
    n = n.parent;
  }
  return `${sf.fileName}#top`;
}

export function toReportFinding(projectDir, rec, f) {
  return {
    file: path.relative(projectDir, rec.sf.fileName),
    line: f.stmtRef ? rec.sf.getLineAndCharacterOfPosition(f.stmtRef.getStart(rec.sf)).line + 1 : (f.covLine ?? rec.line),
    test: rec.title,
    category: f.category, level: f.level, deletable: f.deletable,
    snippet: f.stmtRef ? f.stmtRef.getText(rec.sf).slice(0, 160) : undefined,
    reason: f.reason,
  };
}

export function analyzeTest(ts, checker, typesAvailable, strictNull, uncheckedIndex, sf, tBlock, allFindings, testRecords, projectDir) {
  const { stmt, title, fn, skipped } = tBlock;
  const body = fn.body;
  const statements = ts.isBlock(body) ? [...body.statements] : [];
  const line = sf.getLineAndCharacterOfPosition(stmt.getStart(sf)).line + 1;
  const rec = { sf, stmt, title, fn, line, findings: [], expectCount: 0,
                nonRedundantExpects: 0, nestedAssertions: 0, hasAssertionCtl: false };

  if (skipped) {
    rec.findings.push({ category: 'skipped-test', level: 'advisory', deletable: 'aggressive',
      reason: 'test is unconditionally skipped (xit / .skip) — it never runs and can never fail', stmtRef: null });
    allFindings.push(toReportFinding(projectDir, rec, rec.findings[0]));
    testRecords.push(rec);
    return;
  }

  const allAssertCalls = [];
  walk(ts, fn, n => {
    if (ts.isCallExpression(n)) {
      const root = rootIdentifier(ts, n.expression);
      if (root && isAssertionRoot(root) && isOutermostAssertCall(ts, n)) allAssertCalls.push(n);
    }
  });

  const unreachableStmts = new Set();
  {
    let dead = false;
    for (const s of statements) {
      if (dead) unreachableStmts.add(s);
      if (ts.isReturnStatement(s) || ts.isThrowStatement(s)) dead = true;
    }
  }

  for (const s of statements) {
    if (unreachableStmts.has(s)) {
      let isFail = false;
      if (ts.isThrowStatement(s)) isFail = true;
      else if (ts.isExpressionStatement(s) && ts.isCallExpression(s.expression)) {
        const root = rootIdentifier(ts, s.expression.expression);
        if (root === 'fail') isFail = true;
      }
      if (isFail) {
        rec.findings.push({ category: 'missed-fail', level: 'proven', deletable: 'report-only', stmtRef: s,
          reason: 'fail marker sits after an unconditional return/throw — it can never fire' });
      }
    }
  }
  const topStatementOf = (node) => {
    let n = node;
    while (n && n.parent !== body) n = n.parent;
    return n;
  };

  const swallowed = new Set();
  // Everything lexically inside a try{} whose catch is silent: if it throws,
  // the catch absorbs it, so it can never fail the test and therefore never
  // counts as coverage worth preserving.
  const silentlyGuarded = new Set();
  walk(ts, fn, n => {
    if (ts.isTryStatement(n) && n.catchClause && isSilentCatch(ts, n.catchClause)) {
      walk(ts, n, m => silentlyGuarded.add(m));
      walk(ts, n.tryBlock, m => {
        if (ts.isCallExpression(m)) {
          const root = rootIdentifier(ts, m.expression);
          if (root && isAssertionRoot(root) && isOutermostAssertCall(ts, m)) swallowed.add(m);
        }
      });
    }
  });

  // helper to check if try statement's catch block is silent
  function isSilentCatch(ts, catchClause) {
    return catchClause.block.statements.every(s =>
      ts.isExpressionStatement(s) && ts.isCallExpression(s.expression) &&
      rootIdentifier(ts, s.expression.expression) === 'console');
  }

  for (const s of statements) {
    if (ts.isExpressionStatement(s) && ts.isCallExpression(s.expression) &&
        ts.isPropertyAccessExpression(s.expression.expression) &&
        ts.isIdentifier(s.expression.expression.expression) &&
        s.expression.expression.expression.text === 'expect' &&
        NEUTRAL_EXPECT_STATIC.has(s.expression.expression.name.text)) {
      rec.hasAssertionCtl = true;
    }
  }

  const realAsserts = allAssertCalls.filter(c => {
    if (ts.isPropertyAccessExpression(c.expression) &&
        ts.isIdentifier(c.expression.expression) && c.expression.expression.text === 'expect' &&
        NEUTRAL_EXPECT_STATIC.has(c.expression.name.text)) return false;
    return true;
  });
  const liveAsserts = realAsserts.filter(c =>
    !swallowed.has(c) && !unreachableStmts.has(topStatementOf(c)));

  for (const c of swallowed) {
    if (!realAsserts.includes(c)) continue;
    const cline = sf.getLineAndCharacterOfPosition(c.getStart(sf)).line + 1;
    rec.findings.push({ category: 'swallowed-assert', level: 'proven', deletable: 'report-only',
      reason: `assertion at line ${cline} sits in a try{} with a silent catch — a failure is swallowed, it can never fail the test`, stmtRef: null });
  }

  if (realAsserts.length === 0) {

    let hasCalls = false;
    let allCallsGuarded = true;
    walk(ts, body, n => {
      if (ts.isCallExpression(n) || ts.isNewExpression(n)) {
        if (!isNoiseCall(ts, n)) {
          hasCalls = true;
          if (!silentlyGuarded.has(n)) {
            allCallsGuarded = false;
          }
        }
      }
    });

    if (hasCalls && allCallsGuarded) {
      rec.findings.push({ category: 'silent-smoke', level: 'proven', deletable: 'safe',
        reason: 'assertion-free test where every call is wrapped in a try{} with a silent catch — the test can never fail', stmtRef: null });
    } else if (!hasCalls) {
      rec.findings.push({ category: 'silent-smoke', level: 'proven', deletable: 'safe',
        reason: 'assertion-free test containing no calls — the test does nothing and can never fail', stmtRef: null });
    } else {
      rec.findings.push({ category: 'no-assert', level: 'advisory', deletable: 'report-only',
        reason: 'assertion-free smoke test — legitimate by design (it checks the code runs ' +
          "without throwing). ICSE'19 distinguishes smoke tests from rotten tests; only worth a " +
          'look if an assertion was clearly intended here', stmtRef: null });
    }
    for (const f of rec.findings) allFindings.push(toReportFinding(projectDir, rec, f));
    testRecords.push(rec);
    return;
  }
  if (liveAsserts.length === 0) {
    // Every assertion is dead or swallowed, so the assertions can't fail the
    // test — but an UNGUARDED call still can, by throwing. Deleting the test
    // would drop that signal. A call inside a silently-caught try{} is not
    // such a signal (the catch absorbs the throw), so it doesn't count; nor
    // does the assertion machinery itself, nor console logging.
    const machinery = assertionMachineryNodes(ts, realAsserts);
    let remnant = false;
    walk(ts, body, n => {
      if (remnant) return;
      if (!ts.isCallExpression(n) && !ts.isNewExpression(n)) return;
      if (machinery.has(n) || silentlyGuarded.has(n)) return;
      if (isNoiseCall(ts, n.expression)) return;
      const top = topStatementOf(n);
      if (top && unreachableStmts.has(top)) return;
      remnant = true;
    });
    rec.findings.push(remnant
      ? { category: 'never-asserts', level: 'advisory', deletable: 'report-only', stmtRef: null,
          reason: 'every assertion is dead or swallowed, but an unguarded call remains that can ' +
            'still fail this test by throwing — deleting it would drop that signal. Repair the ' +
            'assertion, or delete by hand once you have confirmed the call cannot fail' }
      : { category: 'never-asserts', level: 'proven', deletable: 'safe', stmtRef: null,
          reason: 'every assertion in this test is unreachable or swallowed — the test can never fail' });
    for (const f of rec.findings) allFindings.push(toReportFinding(projectDir, rec, f));
    testRecords.push(rec);
    return;
  }

  const constMap = new Map();
  for (const s of statements) {
    if (ts.isVariableStatement(s) && (s.declarationList.flags & ts.NodeFlags.Const)) {
      for (const d of s.declarationList.declarations) {
        if (ts.isIdentifier(d.name) && d.initializer && isLiteralish(ts, d.initializer)) {
          constMap.set(d.name.text, literalValue(ts, d.initializer));
        }
      }
    }
  }

  const expectStmts = new Map();
  const topLevelExpectCalls = new Set();
  for (const s of statements) {
    if (!ts.isExpressionStatement(s)) continue;
    if (!ts.isAwaitExpression(s.expression)) {
      let probe = s.expression;
      let sawResolves = false;
      while (ts.isCallExpression(probe) || ts.isPropertyAccessExpression(probe)) {
        if (ts.isPropertyAccessExpression(probe) &&
            ['resolves', 'rejects'].includes(probe.name.text)) sawResolves = true;
        probe = probe.expression;
      }
      if (sawResolves && ts.isIdentifier(probe) && probe.text === 'expect') {
        const cline = sf.getLineAndCharacterOfPosition(s.getStart(sf)).line + 1;
        rec.findings.push({ category: 'floating-async-assert', level: 'advisory', deletable: 'report-only',
          reason: `async assertion at line ${cline} is not awaited — under Jest it silently never fails the test; ` +
                  `bun:test and modern Vitest do catch it at settle time. Add await either way`, stmtRef: null });
        rec.nonRedundantExpects++;
        continue;
      }
    }
    const exp = parseExpectation(ts, s.expression);
    if (!exp) continue;
    if (unreachableStmts.has(s)) {
      rec.findings.push({ category: 'dead-assert', level: 'proven', deletable: 'safe', stmtRef: s,
        reason: 'sits after an unconditional return/throw — this assertion never executes' });
      continue;
    }
    expectStmts.set(s, exp);
    let e = s.expression;
    if (ts.isAwaitExpression(e)) e = e.expression;
    walk(ts, e, n => {
      if (ts.isCallExpression(n) && rootIdentifier(ts, n.expression) === 'expect') topLevelExpectCalls.add(n);
    });
  }

  for (const c of liveAsserts) {
    if (topLevelExpectCalls.has(c)) continue;
    let n = c.parent, crossed = null;
    while (n && n !== fn) {
      if (ts.isIfStatement(n) || ts.isIterationStatement?.(n, false) ||
          ts.isTryStatement(n) || ts.isCatchClause(n) ||
          ts.isArrowFunction(n) || ts.isFunctionExpression(n)) { crossed = n; break; }
      n = n.parent;
    }
    if (crossed) {
      rec.nestedAssertions++;
      if (ts.isIfStatement(crossed)) {
        const cline = sf.getLineAndCharacterOfPosition(c.getStart(sf)).line + 1;
        rec.findings.push({ category: 'conditional-assert', level: 'advisory', deletable: 'report-only',
          reason: `assertion at line ${cline} is gated behind an if — it may never execute (rotten green)`,
          covLine: cline, stmtRef: null });
      }
    }
  }

  const mockFindings = detectMockEcho(ts, statements, expectStmts);

  for (const [s, exp] of expectStmts) {
    rec.expectCount++;
    if (mockFindings.has(s)) {
      const f = { ...mockFindings.get(s), stmtRef: s };
      rec.findings.push(f);
      continue;
    }
    if (exp.unsupported) { rec.nonRedundantExpects++; continue; }
    exp.testTitle = rec.title;
    let verdict = classifyExpect(ts, checker, typesAvailable, strictNull, uncheckedIndex, exp, constMap);
    if (verdict && verdict.category === 'type-guaranteed' &&
        subjectLaunders(ts, checker, exp.subject, statements)) {
      verdict = null;
    }
    if (verdict) rec.findings.push({ ...verdict, stmtRef: s });
    else rec.nonRedundantExpects++;
  }

  // -- try-catch without fail (missed-fail)
  walk(ts, fn, n => {
    if (ts.isTryStatement(n) && n.catchClause) {
      let catchHasAssert = false;
      walk(ts, n.catchClause, m => {
        if (ts.isCallExpression(m)) {
          const root = rootIdentifier(ts, m.expression);
          if (root && isAssertionRoot(root) && isOutermostAssertCall(ts, m)) catchHasAssert = true;
        }
      });
      if (catchHasAssert) {
        let tryHasFail = false;
        walk(ts, n.tryBlock, m => {
          if (ts.isCallExpression(m)) {
            const root = rootIdentifier(ts, m.expression);
            if (root === 'fail') tryHasFail = true;
          } else if (ts.isThrowStatement(m)) {
            tryHasFail = true;
          }
        });
        if (!tryHasFail) {
          const cline = sf.getLineAndCharacterOfPosition(n.getStart(sf)).line + 1;
          rec.findings.push({ category: 'missed-fail', level: 'advisory', deletable: 'report-only',
            reason: `try block at line ${cline} catches an exception and asserts on it, but lacks a forced fail (e.g. fail()) at the end of the try block — if no exception is thrown, the test will pass silently`, stmtRef: null });
        }
      }
    }
  });

  // -- missed-skip (conditional early return/skip preceding assertions)
  const paramNames = new Set();
  for (const p of fn.parameters) {
    if (ts.isIdentifier(p.name)) paramNames.add(p.name.text);
  }
  for (let i = 0; i < statements.length; i++) {
    const s = statements[i];
    if (ts.isIfStatement(s)) {
      let hasEarlyExit = false;
      walk(ts, s, x => {
        if (ts.isReturnStatement(x)) hasEarlyExit = true;
        else if (ts.isCallExpression(x)) {
          const root = rootIdentifier(ts, x.expression);
          if (root === 'skip') hasEarlyExit = true;
        }
      });
      if (hasEarlyExit) {
        let assertionsAfter = false;
        for (let j = i + 1; j < statements.length; j++) {
          walk(ts, statements[j], x => {
            if (ts.isCallExpression(x)) {
              const root = rootIdentifier(ts, x.expression);
              if (root && isAssertionRoot(root) && isOutermostAssertCall(ts, x)) assertionsAfter = true;
            }
          });
          if (assertionsAfter) break;
        }
        if (assertionsAfter) {
          const condNames = new Set();
          walk(ts, s.expression, x => {
            if (ts.isIdentifier(x)) condNames.add(x.text);
          });
          let overlaps = false;
          for (const name of condNames) {
            if (paramNames.has(name)) overlaps = true;
          }
          if (!overlaps) {
            const cline = sf.getLineAndCharacterOfPosition(s.getStart(sf)).line + 1;
            rec.findings.push({ category: 'missed-skip', level: 'advisory', deletable: 'report-only',
              reason: `conditional early return/skip at line ${cline} precedes assertions — if the condition is met, the remaining assertions never run (a bare return passes silently; this.skip() at least reports a skip)`, stmtRef: null });
          }
        }
      }
    }
  }

  for (const f of rec.findings) allFindings.push(toReportFinding(projectDir, rec, f));
  testRecords.push(rec);
}
