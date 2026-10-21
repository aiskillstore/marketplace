export const norm = (s) => s.replace(/\s+/g, '');

export function canon(ts, text) {
  const sc = ts.createScanner(ts.ScriptTarget.Latest, /*skipTrivia*/ true,
    ts.LanguageVariant.Standard, text);
  const toks = [];
  let k;
  try {
    while ((k = sc.scan()) !== ts.SyntaxKind.EndOfFileToken) {
      if (k === ts.SyntaxKind.Unknown) return norm(text);
      toks.push(sc.getTokenText());
    }
  } catch {
    return norm(text);
  }
  return toks.join(' ');
}

export function nameTokens(title) {
  const words = (title || '').match(/[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])/g) || [];
  return new Set(words.map(w => w.toLowerCase()).filter(w => w && !/^\d+$/.test(w)));
}

export function namesDiverge(a, b) {
  const ta = nameTokens(a), tb = nameTokens(b);
  if (!ta.size || !tb.size) return false;
  let inter = 0;
  for (const w of ta) if (tb.has(w)) inter++;
  const union = ta.size + tb.size - inter;
  return inter / union < 0.6;
}

export function walk(ts, node, fn) {
  fn(node);
  ts.forEachChild(node, c => walk(ts, c, fn));
}

export function hasUnsafeCast(ts, node) {
  let found = false;
  walk(ts, node, n => {
    if (found) return;
    if (ts.isAsExpression(n)) {
      const asConst = ts.isTypeReferenceNode(n.type) && n.type.typeName.getText() === 'const';
      if (!asConst) found = true;
    } else if (n.kind === ts.SyntaxKind.TypeAssertionExpression || ts.isNonNullExpression(n)) {
      found = true;
    }
  });
  return found;
}

export function isSilentCatch(ts, catchClause) {
  return catchClause.block.statements.every(s =>
    ts.isExpressionStatement(s) && ts.isCallExpression(s.expression) &&
    rootIdentifier(ts, s.expression.expression) === 'console');
}

// The call nodes that make up the assertion itself — for `expect(x).toBe(1)`
// that is the `.toBe(1)` call, the `expect(...)` call, and the property access
// between them, but NOT the argument expressions. Callers use this to tell
// assertion machinery apart from code the test genuinely exercises.
export function assertionMachineryNodes(ts, assertCalls) {
  const nodes = new Set();
  for (const c of assertCalls) {
    let n = c;
    while (n) {
      nodes.add(n);
      if (ts.isCallExpression(n) || ts.isPropertyAccessExpression(n)) n = n.expression;
      else break;
    }
  }
  return nodes;
}

export function hasElementAccess(ts, node) {
  let found = false;
  walk(ts, node, n => { if (ts.isElementAccessExpression(n)) found = true; });
  return found;
}

export function rootIdentifier(ts, expr) {
  let n = expr;
  while (true) {
    if (ts.isCallExpression(n) || ts.isPropertyAccessExpression(n) ||
        ts.isElementAccessExpression(n) || ts.isNonNullExpression(n)) { n = n.expression; continue; }
    if (ts.isAwaitExpression(n) || ts.isParenthesizedExpression(n)) { n = n.expression; continue; }
    return ts.isIdentifier(n) ? n.text : null;
  }
}

export const isLiteralish = (ts, n) =>
  ts.isStringLiteralLike(n) || ts.isNumericLiteral(n) ||
  n.kind === ts.SyntaxKind.TrueKeyword || n.kind === ts.SyntaxKind.FalseKeyword ||
  n.kind === ts.SyntaxKind.NullKeyword ||
  (ts.isPrefixUnaryExpression(n) && n.operator === ts.SyntaxKind.MinusToken && ts.isNumericLiteral(n.operand)) ||
  (ts.isIdentifier(n) && n.text === 'undefined');

export const NO_VALUE = Symbol('no');

export function literalValue(ts, n) {
  if (ts.isStringLiteralLike(n)) return n.text;
  if (ts.isNumericLiteral(n)) return Number(n.text);
  if (n.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (n.kind === ts.SyntaxKind.FalseKeyword) return false;
  if (n.kind === ts.SyntaxKind.NullKeyword) return null;
  if (ts.isIdentifier(n) && n.text === 'undefined') return undefined;
  if (ts.isPrefixUnaryExpression(n) && n.operator === ts.SyntaxKind.MinusToken && ts.isNumericLiteral(n.operand)) {
    return -Number(n.operand.text);
  }
  return NO_VALUE;
}

export function isSimpleChain(ts, n) {
  if (ts.isIdentifier(n) || n.kind === ts.SyntaxKind.ThisKeyword) return true;
  if (ts.isPropertyAccessExpression(n)) return isSimpleChain(ts, n.expression);
  return false;
}
