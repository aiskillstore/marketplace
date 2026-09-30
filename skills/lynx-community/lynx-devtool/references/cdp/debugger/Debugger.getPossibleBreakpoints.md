# Debugger.getPossibleBreakpoints

- `Debugger.getPossibleBreakpoints` - Returns locations where a breakpoint can be set within a script range.
- Input:
  - `start` (object, required): `{scriptId: string, lineNumber: integer, columnNumber?: integer}`. Line and column numbers are zero-based.
  - `end` (object, optional): Exclusive end of the search range, with the same shape as `start`. It must use the same `scriptId` as `start`; omit it to search through the end of the script.
  - `restrictToFunction` (boolean, optional): Restrict results to the non-nested function containing `start`.
- Output: `{locations: Array<{scriptId: string, lineNumber: integer, columnNumber?: integer, type?: "debuggerStatement" | "call" | "return"}>}`.

## Notes

- `scriptId` values are scoped to the selected VM thread. Obtain them from `Debugger.scriptParsed` or `get-sources` on that same thread.
- The method is part of the PrimJS inspector command map. V8-backed sessions follow Lynx's adopted [CDP 1.3 Debugger reference](https://chromedevtools.github.io/devtools-protocol/1-3/Debugger/#method-getPossibleBreakpoints).
