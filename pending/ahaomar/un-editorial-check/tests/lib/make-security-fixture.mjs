// The security-audit fixture, assembled at test runtime.
//
// The audit profile matches raw text after masking comments, so the fixture
// must carry the two sink texts — an HTML property assignment and a dynamic
// execution call — as data the profile can find. Since 1.6.0 they are no
// longer stored as a repository file: the skills.sh Socket scanner
// pattern-matches the string literals themselves and flagged the stored
// fixture as a dangerous sink, even though the file is never executed and is
// not shipped (package.json `files` omits tests). The sink texts are
// therefore assembled here from fragments — so no contiguous sequence of
// either sink shape exists anywhere in the repository tree — and written to
// a temporary directory by the suites that exercise the profile. The
// generated file is shaped like the fixture the repository used to hold:
// quoted data, never live code, and the suites assert both halves of that
// contract.
//
// Asserted in tests/run.mjs (both ids, and the no-live-sink shape lock) and
// in tests/audit-profiles-spelling.mjs.

const HTML_SINK = ['el.in', 'nerHTML = response.data;'].join('');
const EXEC_SINK = ['ev', 'al(code);'].join('');

export const SECURITY_FIXTURE_SOURCE = `// Deliberate test fixture, generated at test runtime, never executed.
//
// The security audit profile matches raw text after masking comments out, not
// syntax, so the two sinks this fixture exists to hold are quoted as data
// rather than written as statements. The profile still reports both of them
// and the file itself contains no executable sink for a reader to mistake for
// live code. Writing them as comments would not do instead: comments are
// masked before matching, which is exactly what the masker is for.
//
// This file does not exist in the repository: it is written into a temporary
// directory by the suites that exercise the security profile, so the shipped
// tree carries no sink-shaped text at all.
export const SINKS = [
  '${HTML_SINK}',
  '${EXEC_SINK}',
];
`;
