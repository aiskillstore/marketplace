import { rootIdentifier } from './ast_utils.mjs';

export function parseExpectation(ts, expr) {
  let call = expr;
  if (ts.isAwaitExpression(call)) call = call.expression;
  if (!ts.isCallExpression(call) || !ts.isPropertyAccessExpression(call.expression)) return null;
  const matcher = call.expression.name.text;
  let base = call.expression.expression;
  let negated = false;
  if (ts.isPropertyAccessExpression(base) && base.name.text === 'not') { negated = true; base = base.expression; }
  if (ts.isPropertyAccessExpression(base) && ['resolves', 'rejects'].includes(base.name.text)) return { unsupported: true };
  if (!ts.isCallExpression(base)) return null;
  const be = base.expression;
  const isExpect = (ts.isIdentifier(be) && be.text === 'expect') ||
    (ts.isPropertyAccessExpression(be) && ts.isIdentifier(be.expression) &&
     be.expression.text === 'expect' && be.name.text === 'soft');
  if (!isExpect || base.arguments.length !== 1) return null;
  return { subject: base.arguments[0], matcher, args: [...call.arguments], negated };
}

export function parseExpectHelper(ts, arg) {
  if (!ts.isCallExpression(arg) || !ts.isPropertyAccessExpression(arg.expression)) return null;
  const pa = arg.expression;
  if (!ts.isIdentifier(pa.expression) || pa.expression.text !== 'expect') return null;
  if (pa.name.text === 'anything') return { kind: 'anything' };
  if (pa.name.text === 'any' && arg.arguments.length === 1) return { kind: 'any', ctor: arg.arguments[0] };
  return null;
}
export const EQ_MATCHERS = new Set(['toBe', 'toEqual', 'toStrictEqual']);
