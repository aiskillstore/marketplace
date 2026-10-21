import { rootIdentifier, canon } from './ast_utils.mjs';
import { EQ_MATCHERS } from './expect_parser.mjs';

export function detectMockEcho(ts, statements, expectStmts) {
  const stubs = new Map();
  const directCalls = new Map();
  const bindings = new Map();
  const findings = new Map();

  for (const stmt of statements) {
    let e = ts.isExpressionStatement(stmt) ? stmt.expression : null;
    if (ts.isVariableStatement(stmt)) {
      for (const d of stmt.declarationList.declarations) {
        if (d.initializer && ts.isIdentifier(d.name)) {
          let init = d.initializer;
          if (ts.isAwaitExpression(init)) init = init.expression;
          if (ts.isCallExpression(init) && ts.isIdentifier(init.expression)) {
            bindings.set(d.name.text, { mock: init.expression.text });
          }
        }
      }
      continue;
    }
    if (!e) continue;
    if (ts.isAwaitExpression(e)) e = e.expression;

    if (ts.isCallExpression(e) && ts.isPropertyAccessExpression(e.expression) &&
        /^mock(Return|Resolved)Value(Once)?$/.test(e.expression.name.text) &&
        e.arguments.length === 1) {
      const root = rootIdentifier(ts, e.expression.expression);
      if (root) stubs.set(root, canon(ts, e.arguments[0].getText()));
      continue;
    }

    if (ts.isCallExpression(e) && ts.isIdentifier(e.expression)) {
      directCalls.set(e.expression.text, canon(ts, e.arguments.map(a => a.getText()).join(',')));
      continue;
    }

    const exp = expectStmts.get(stmt);
    if (!exp || exp.unsupported) continue;
    const { subject, matcher, args, negated } = exp;
    if (negated) continue;

    if (/^toHaveBeenCalled(Times|With)?$/.test(matcher)) {
      const root = rootIdentifier(ts, subject);
      if (root && directCalls.has(root)) {
        let ok = matcher !== 'toHaveBeenCalledWith' ||
                 canon(ts, args.map(a => a.getText()).join(',')) === directCalls.get(root);
        if (matcher === 'toHaveBeenCalledTimes') ok = args[0]?.getText() === '1';
        if (ok) {
          findings.set(stmt, { category: 'mock-echo', level: 'proven', deletable: 'safe',
            reason: `test calls ${root}() itself, then asserts it was called — asserts the test's own action` });
          continue;
        }
      }
    }

    if (EQ_MATCHERS.has(matcher) && args[0]) {
      let root = null;
      let s = subject;
      if (ts.isAwaitExpression(s)) s = s.expression;
      if (ts.isCallExpression(s) && ts.isIdentifier(s.expression)) root = s.expression.text;
      else if (ts.isIdentifier(s) && bindings.get(s.text)) root = bindings.get(s.text).mock;
      if (root && stubs.has(root) && stubs.get(root) === canon(ts, args[0].getText())) {
        findings.set(stmt, { category: 'mock-echo', level: 'proven', deletable: 'safe',
          reason: `asserts ${root}() returns the exact value it was stubbed with — tests the mocking library` });
      }
    }
  }
  return findings;
}
