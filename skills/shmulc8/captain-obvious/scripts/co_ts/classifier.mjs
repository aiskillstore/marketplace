import {
  isLiteralish,
  literalValue,
  isSimpleChain,
  canon,
  hasUnsafeCast,
  hasElementAccess,
  walk,
  NO_VALUE
} from './ast_utils.mjs';

import {
  isBadType,
  typeExcludes,
  isAlwaysTruthy,
  isDeclaredPropertyAccess,
  instanceOfVerdict,
  isArrayType,
  TYPEOF_CHECKS,
  parts
} from './type_predicates.mjs';

import { parseExpectHelper, EQ_MATCHERS } from './expect_parser.mjs';

export function classifyExpect(ts, checker, typesAvailable, strictNull, uncheckedIndex, exp, constMap = new Map()) {
  const { subject, matcher, args, negated } = exp;
  const arg0 = args[0];

  // ---- boundary-tautology: a .length/.size can never be negative
  if (!negated && ts.isPropertyAccessExpression(subject) &&
      ['length', 'size'].includes(subject.name.text) && arg0 && isLiteralish(ts, arg0)) {
    const v = literalValue(ts, arg0);
    if ((matcher === 'toBeGreaterThanOrEqual' && v === 0) ||
        (matcher === 'toBeGreaterThan' && v === -1)) {
      return { category: 'boundary-tautology', level: 'proven', deletable: 'safe',
               reason: `${subject.getText()} can never be negative — the comparison always holds` };
    }
  }

  // ---- local-const-echo: const x = LIT; ... expect(x).toBe(LIT)
  if (!negated && EQ_MATCHERS.has(matcher) && arg0 &&
      ts.isIdentifier(subject) && constMap.has(subject.text) && isLiteralish(ts, arg0)) {
    const bound = constMap.get(subject.text), asserted = literalValue(ts, arg0);
    if (bound !== NO_VALUE && asserted !== NO_VALUE && bound === asserted) {
      return { category: 'local-const-echo', level: 'proven', deletable: 'safe',
               reason: `${subject.text} is a const bound to ${JSON.stringify(bound)} two lines up — the test asserts its own arrangement` };
    }
  }

  // ---- self-compare-call: expect(f(a)).toEqual(f(a))
  // (literal subjects fall through to constant-assert below: expect(true)
  // .toBe(true) is a proven tautology, not a maybe-nondeterministic compare)
  if (!negated && EQ_MATCHERS.has(matcher) && arg0 && !isSimpleChain(ts, subject) &&
      !isLiteralish(ts, subject) &&
      canon(ts, subject.getText()) === canon(ts, arg0.getText()) &&
      !/stable|determin|consistent|idempotent|same|pure/i.test(exp.testTitle ?? '')) {
    return { category: 'self-compare-call', level: 'advisory', deletable: 'report-only',
             reason: `compares ${subject.getText().slice(0, 60)} to an identical expression — equal by construction unless nondeterministic` };
  }

  // ---- smoke-only: not.toThrow()
  if (negated && (matcher === 'toThrow' || matcher === 'toThrowError')) {
    return { category: 'smoke-only', level: 'advisory', deletable: 'report-only',
             reason: 'not.toThrow() adds nothing — calling the function directly fails the test on throw anyway; assert on the return value instead' };
  }

  // ---- constant-assert
  if (!negated && EQ_MATCHERS.has(matcher) && arg0) {
    if (isLiteralish(ts, subject) && isLiteralish(ts, arg0)) {
      const a = literalValue(ts, subject), b = literalValue(ts, arg0);
      if (a !== NO_VALUE && b !== NO_VALUE && a === b) {
        return { category: 'constant-assert', level: 'proven', deletable: 'safe',
                 reason: `compares constant ${JSON.stringify(a)} to itself` };
      }
      return null;
    }
    if (isSimpleChain(ts, subject) && canon(ts, subject.getText()) === canon(ts, arg0.getText())) {
      return { category: 'constant-assert', level: 'proven', deletable: 'safe',
               reason: `compares ${subject.getText()} to itself` };
    }
  }
  if (!negated && matcher === 'toBeTruthy' && args.length === 0 && isLiteralish(ts, subject)) {
    const v = literalValue(ts, subject);
    if (v !== NO_VALUE && !!v) {
      return { category: 'constant-assert', level: 'proven', deletable: 'safe',
               reason: `literal ${JSON.stringify(v)} is always truthy` };
    }
  }

  if (!typesAvailable) return null;

  // ---- type-guaranteed family
  let subjectHasCall = false;
  if (subject) walk(ts, subject, (n) => {
    if (ts.isCallExpression(n) || ts.isNewExpression(n)) subjectHasCall = true;
  });
  const proven = (reason) => subjectHasCall
    ? { category: 'type-guaranteed', level: 'advisory', deletable: 'report-only',
        reason: reason + ' — subject inlines a call, kept advisory to preserve smoke coverage' }
    : { category: 'type-guaranteed', level: 'proven', deletable: 'safe', reason };
  const advisory = (reason) => ({ category: 'type-guaranteed', level: 'advisory', deletable: 'aggressive', reason });

  // negated typeof
  if (negated && ts.isTypeOfExpression(subject) && EQ_MATCHERS.has(matcher) &&
      arg0 && ts.isStringLiteralLike(arg0) && arg0.text === 'undefined' && strictNull) {
    const operand = subject.expression;
    if (!hasUnsafeCast(ts, operand)) {
      const t = checker.getTypeAtLocation(operand);
      if (!isBadType(ts, t) && typeExcludes(t, ts.TypeFlags.Undefined | ts.TypeFlags.Void) &&
          !(hasElementAccess(ts, operand) && !uncheckedIndex) && isDeclaredPropertyAccess(checker, operand)) {
        return proven(`type ${checker.typeToString(t)} already excludes undefined — typeof can never be "undefined"`);
      }
    }
    return null;
  }

  // typeof x / toBeTypeOf
  const typeofTarget =
    (!negated && ts.isTypeOfExpression(subject) && EQ_MATCHERS.has(matcher) &&
     arg0 && ts.isStringLiteralLike(arg0)) ? { operand: subject.expression, name: arg0.text }
    : (!negated && matcher === 'toBeTypeOf' && arg0 && ts.isStringLiteralLike(arg0))
      ? { operand: subject, name: arg0.text } : null;
  if (typeofTarget) {
    const check = TYPEOF_CHECKS(ts)[typeofTarget.name];
    if (!check || hasUnsafeCast(ts, typeofTarget.operand)) return null;
    const t = checker.getTypeAtLocation(typeofTarget.operand);
    if (!isBadType(ts, t) && parts(t).every(check)) {
      return proven(`compiler already guarantees typeof is "${typeofTarget.name}" (type: ${checker.typeToString(t)})`);
    }
    return null;
  }

  if (hasUnsafeCast(ts, subject)) return null;
  const t = () => checker.getTypeAtLocation(subject);

  // toBeDefined / not.toBeUndefined / not.toBeNull / toBeNull / toBeUndefined
  if ((matcher === 'toBeDefined' && !negated) || (matcher === 'toBeUndefined' && negated)) {
    if (!strictNull) return null;
    const ty = t();
    if (!isBadType(ts, ty) && typeExcludes(ty, ts.TypeFlags.Undefined | ts.TypeFlags.Void)) {
      if (hasElementAccess(ts, subject) && !uncheckedIndex) {
        return advisory(`type ${checker.typeToString(ty)} excludes undefined, but indexed access without noUncheckedIndexedAccess can lie`);
      }
      if (!isDeclaredPropertyAccess(checker, subject)) {
        return advisory(`type ${checker.typeToString(ty)} excludes undefined, but the property comes from an index signature — the type is a promise, not a check`);
      }
      return proven(`type ${checker.typeToString(ty)} already excludes undefined`);
    }
    return null;
  }
  if (matcher === 'toBeNull' && negated) {
    if (!strictNull) return null;
    const ty = t();
    if (!isBadType(ts, ty) && typeExcludes(ty, ts.TypeFlags.Null)) {
      return proven(`type ${checker.typeToString(ty)} already excludes null`);
    }
    return null;
  }

  // toBeTruthy / not.toBeFalsy
  if ((matcher === 'toBeTruthy' && !negated) || (matcher === 'toBeFalsy' && negated)) {
    if (!strictNull) return null;
    const ty = t();
    if (!isBadType(ts, ty) && isAlwaysTruthy(ts, checker, ty)) {
      if ((hasElementAccess(ts, subject) && !uncheckedIndex) || !isDeclaredPropertyAccess(checker, subject)) {
        return advisory(`type ${checker.typeToString(ty)} is always truthy, but the value comes through an index signature or unchecked indexed access — the type may lie`);
      }
      return proven(`type ${checker.typeToString(ty)} is always truthy`);
    }
    return null;
  }

  // toBeInstanceOf
  if (matcher === 'toBeInstanceOf' && !negated && arg0) {
    const v = instanceOfVerdict(ts, checker, subject, arg0);
    return v ? { category: 'type-guaranteed', level: v.level,
                 deletable: v.level === 'proven' ? 'safe' : 'aggressive', reason: v.reason } : null;
  }

  // expect(Array.isArray(x)).toBe(true) / toBeTruthy
  if (!negated && ts.isCallExpression(subject) && ts.isPropertyAccessExpression(subject.expression) &&
      subject.expression.name.text === 'isArray' &&
      ts.isIdentifier(subject.expression.expression) && subject.expression.expression.text === 'Array' &&
      subject.arguments.length === 1 &&
      ((EQ_MATCHERS.has(matcher) && arg0?.kind === ts.SyntaxKind.TrueKeyword) ||
       (matcher === 'toBeTruthy' && args.length === 0))) {
    const inner = subject.arguments[0];
    if (hasUnsafeCast(ts, inner)) return null;
    const ty = checker.getTypeAtLocation(inner);
    if (!isBadType(ts, ty) && parts(ty).every(p => isArrayType(checker, p))) {
      return proven(`type ${checker.typeToString(ty)} is already an array`);
    }
    return null;
  }

  // toEqual(expect.anything()) / toEqual(expect.any(Ctor))
  if (!negated && EQ_MATCHERS.has(matcher) && arg0) {
    const helper = parseExpectHelper(ts, arg0);
    if (helper?.kind === 'anything') {
      if (!strictNull) return null;
      const ty = t();
      if (!isBadType(ts, ty) && typeExcludes(ty, ts.TypeFlags.Null | ts.TypeFlags.Undefined | ts.TypeFlags.Void)) {
        return proven(`expect.anything() matches everything non-null; type ${checker.typeToString(ty)} is never null/undefined`);
      }
      return null;
    }
    if (helper?.kind === 'any' && ts.isIdentifier(helper.ctor)) {
      const ctorName = helper.ctor.text;
      const prim = { Number: 'number', String: 'string', Boolean: 'boolean', Function: 'function', BigInt: 'bigint', Symbol: 'symbol' }[ctorName];
      const ty = t();
      if (prim) {
        if (!isBadType(ts, ty) && parts(ty).every(TYPEOF_CHECKS(ts)[prim])) {
          return proven(`expect.any(${ctorName}) matches any ${prim}; type is ${checker.typeToString(ty)}`);
        }
        return null;
      }
      if (ctorName === 'Object') {
        if (!isBadType(ts, ty) && parts(ty).every(p => p.flags & ts.TypeFlags.Object)) {
          return proven(`expect.any(Object) matches any object; type is ${checker.typeToString(ty)}`);
        }
        return null;
      }
      const v = instanceOfVerdict(ts, checker, subject, helper.ctor);
      return v ? { category: 'type-guaranteed', level: v.level,
                   deletable: v.level === 'proven' ? 'safe' : 'aggressive',
                   reason: `expect.any = instanceof check; ${v.reason}` } : null;
    }
  }

  // toHaveProperty('name')
  if (!negated && matcher === 'toHaveProperty' && args.length === 1 && arg0 && ts.isStringLiteralLike(arg0) &&
      !arg0.text.includes('.')) {
    const ty = t();
    if (isBadType(ts, ty)) return null;
    const ok = parts(ty).every(p => {
      if (p.flags & (ts.TypeFlags.Null | ts.TypeFlags.Undefined)) return false;
      const prop = checker.getPropertyOfType(p, arg0.text);
      return prop && !(prop.flags & ts.SymbolFlags.Optional);
    });
    if (ok) return proven(`property "${arg0.text}" is required on type ${checker.typeToString(t())}`);
    return null;
  }

  return null;
}
