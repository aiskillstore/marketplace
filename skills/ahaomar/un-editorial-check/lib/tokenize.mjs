// A deliberately small, dependency-free JS/TS tokenizer. It does not build an
// AST — it answers one question: "is this character inside a string/template
// literal, inside a comment, or inside live code?"
//
// That distinction is what the previous line-regex implementation got wrong:
// it ran prose checks over raw source lines, so `color:` object keys, `//`
// comments and modulo operators were reported as editorial errors.
//
// Known limitation (documented, not hidden): regex literals (/abc/g) are not
// distinguished from the division operator, and JSX text nodes are not
// extracted. See README "Known limitations".

export function tokenizeJS(source) {
  const tokens = [];
  const n = source.length;
  let i = 0;
  let typeStart = 0;
  let curType = 'code';
  let curGroup = null;
  let templateGroupCounter = 0;

  const stack = [{ mode: 'code', fromTemplate: false, braceDepth: 0 }];
  const top = () => stack[stack.length - 1];
  // Groups (backtick literals) that contained at least one ${...} hole.
  const interpolated = new Set();

  function emit(end, type) {
    if (end > typeStart) {
      const token = { type, start: typeStart, end, text: source.slice(typeStart, end) };
      if (type === 'template') {
        token.group = curGroup;
        token.interp = curGroup !== null && interpolated.has(curGroup);
      }
      tokens.push(token);
    }
    typeStart = end;
  }

  while (i < n) {
    const c = source[i];
    const c2 = i + 1 < n ? source[i + 1] : '';
    const frame = top();

    if (frame.mode === 'code') {
      if (c === '/' && c2 === '/') {
        emit(i, 'code');
        stack.push({ mode: 'line-comment' });
        curType = 'comment';
        i += 2;
        continue;
      }
      if (c === '/' && c2 === '*') {
        emit(i, 'code');
        stack.push({ mode: 'block-comment' });
        curType = 'comment';
        i += 2;
        continue;
      }
      if (c === '"' || c === "'" || c === '`') {
        emit(i, 'code');
        if (c === '`') {
          stack.push({ mode: 'template' });
          curType = 'template';
          curGroup = ++templateGroupCounter;
        } else {
          stack.push({ mode: c === '"' ? 'str-double' : 'str-single' });
          curType = c === '"' ? 'string-double' : 'string-single';
        }
        i += 1;
        continue;
      }
      if (frame.fromTemplate) {
        if (c === '{') { frame.braceDepth++; i++; continue; }
        if (c === '}') {
          if (frame.braceDepth === 0) {
            emit(i, 'code');
            stack.pop();
            curType = 'template';
            i += 1;
            typeStart = i; // the '}' closes the interpolation, not a segment
            continue;
          }
          frame.braceDepth--; i++; continue;
        }
      }
      i++; continue;
    }

    if (frame.mode === 'line-comment') {
      if (c === '\n') {
        emit(i, 'comment');
        stack.pop();
        curType = 'code';
        continue; // leave the newline for code mode
      }
      i++; continue;
    }

    if (frame.mode === 'block-comment') {
      if (c === '*' && c2 === '/') {
        i += 2;
        emit(i, 'comment');
        stack.pop();
        curType = 'code';
        continue;
      }
      i++; continue;
    }

    if (frame.mode === 'str-double' || frame.mode === 'str-single') {
      const quote = frame.mode === 'str-double' ? '"' : "'";
      if (c === '\\') { i += 2; continue; }
      if (c === quote || c === '\n') {
        i += c === quote ? 1 : 0;
        emit(i, curType); // an unterminated literal ends defensively at the newline
        stack.pop();
        curType = 'code';
        continue;
      }
      i++; continue;
    }

    if (frame.mode === 'template') {
      if (c === '\\') { i += 2; continue; }
      if (c === '`') {
        i += 1;
        emit(i, 'template');
        stack.pop();
        curType = 'code';
        continue;
      }
      if (c === '$' && c2 === '{') {
        if (curGroup !== null) interpolated.add(curGroup);
        emit(i, 'template');
        stack.push({ mode: 'code', fromTemplate: true, braceDepth: 0 });
        curType = 'code';
        i += 2;
        continue;
      }
      i++; continue;
    }

    i++; // unreachable
  }
  emit(n, curType);
  return tokens;
}
