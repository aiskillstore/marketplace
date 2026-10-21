import { hasUnsafeCast } from './ast_utils.mjs';

export const TYPEOF_CHECKS = (ts) => {
  const TF = ts.TypeFlags;
  return {
    string:  t => !!(t.flags & TF.StringLike),
    number:  t => !!(t.flags & TF.NumberLike),
    boolean: t => !!(t.flags & TF.BooleanLike),
    bigint:  t => !!(t.flags & TF.BigIntLike),
    symbol:  t => !!(t.flags & TF.ESSymbolLike),
    undefined: t => !!(t.flags & TF.Undefined),
    function: t => !!(t.flags & TF.Object) &&
      (t.getCallSignatures().length > 0 || t.getConstructSignatures().length > 0),
  };
};

export const parts = (t) => (t.isUnion?.() ? t.types : [t]);

export function isBadType(ts, t) {
  const TF = ts.TypeFlags;
  const BAD_MASK = TF.Any | TF.Unknown | (TF.TypeVariable ?? 0) | (TF.Index ?? 0) |
                   (TF.Conditional ?? 0) | (TF.Substitution ?? 0);
  return t.isIntersection?.() || parts(t).some(p => p.isIntersection?.() || (p.flags & BAD_MASK));
}

export function typeExcludes(type, flags) {
  return !parts(type).some(p => p.flags & flags);
}

export function isAlwaysTruthy(ts, checker, type) {
  const TF = ts.TypeFlags;
  return parts(type).every(p => {
    if (p.flags & (TF.Null | TF.Undefined | TF.Void)) return false;
    if (p.isStringLiteral?.()) return p.value !== '';
    if (p.isNumberLiteral?.()) return p.value !== 0 && !Number.isNaN(p.value);
    if (p.flags & TF.BooleanLiteral) return checker.typeToString(p) === 'true';
    if (p.flags & TF.Object) return true;
    return false;
  });
}

export function resolveSymbol(ts, checker, sym) {
  if (sym && (sym.flags & ts.SymbolFlags.Alias)) {
    try { return checker.getAliasedSymbol(sym); } catch { return sym; }
  }
  return sym;
}

export function classDeclOf(ts, sym) {
  if (!sym) return null;
  if (sym.valueDeclaration && ts.isClassLike(sym.valueDeclaration)) return sym.valueDeclaration;
  return (sym.declarations ?? []).find(d => ts.isClassLike(d)) ?? null;
}

export function classChainIncludes(ts, checker, startSym, targetSym) {
  let sym = resolveSymbol(ts, checker, startSym), guard = 0;
  while (sym && guard++ < 50) {
    if (sym === targetSym) return true;
    const decl = classDeclOf(ts, sym);
    if (!decl) return false;
    const ext = (decl.heritageClauses ?? []).find(h => h.token === ts.SyntaxKind.ExtendsKeyword);
    if (!ext || !ext.types[0]) return false;
    sym = resolveSymbol(ts, checker, checker.getTypeAtLocation(ext.types[0].expression)?.getSymbol());
  }
  return false;
}

export function chainHasPrivateMember(ts, checker, startSym) {
  let sym = resolveSymbol(ts, checker, startSym), guard = 0;
  while (sym && guard++ < 50) {
    const decl = classDeclOf(ts, sym);
    if (!decl) return false;
    for (const m of decl.members ?? []) {
      if (m.name && ts.isPrivateIdentifier(m.name)) return true;
      const mods = ts.canHaveModifiers?.(m) ? ts.getModifiers(m) ?? [] : (m.modifiers ?? []);
      if (mods.some(x => x.kind === ts.SyntaxKind.PrivateKeyword || x.kind === ts.SyntaxKind.ProtectedKeyword)) return true;
    }
    const ext = (decl.heritageClauses ?? []).find(h => h.token === ts.SyntaxKind.ExtendsKeyword);
    if (!ext || !ext.types[0]) return false;
    sym = resolveSymbol(ts, checker, checker.getTypeAtLocation(ext.types[0].expression)?.getSymbol());
  }
  return false;
}

export function isDeclaredPropertyAccess(checker, subject) {
  if (!subject || !subject.expression || !subject.name) return true;
  const objType = checker.getTypeAtLocation(subject.expression);
  return parts(objType).every(p => checker.getPropertyOfType(p, subject.name.text));
}

export function instanceOfVerdict(ts, checker, subject, classArg) {
  const t = checker.getTypeAtLocation(subject);
  if (isBadType(ts, t) || hasUnsafeCast(ts, subject)) return null;
  const classSym = resolveSymbol(ts, checker, checker.getSymbolAtLocation(classArg));
  if (!classDeclOf(ts, classSym)) return null;
  for (const p of parts(t)) {
    if (p.flags & (ts.TypeFlags.Null | ts.TypeFlags.Undefined)) return null;
    if (!classChainIncludes(ts, checker, p.getSymbol?.(), classSym)) return null;
  }
  const nominal = parts(t).every(p => chainHasPrivateMember(ts, checker, p.getSymbol?.()));
  return nominal
    ? { level: 'proven', reason: `type is ${checker.typeToString(t)} (nominal — has private members), instanceof cannot fail` }
    : { level: 'advisory', reason: `declared type is ${checker.typeToString(t)}, but TS is structural — a shaped non-instance could sneak in` };
}

export function isArrayType(checker, t) {
  if (typeof checker.isArrayLikeType === 'function') return checker.isArrayLikeType(t);
  const s = checker.typeToString(t);
  return /\[\]$/.test(s) || /^(Readonly)?Array</.test(s) || /^readonly .*\[\]$/.test(s);
}
