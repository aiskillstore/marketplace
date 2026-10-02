# Short post for X or Bluesky

Facts to keep intact: version 1.1.0, zero npm dependencies, MIT licence. The body is 249 characters including surrounding whitespace, so it fits Bluesky at 300 and Mastodon at 500 as written. Under the X rule the 45-character link counts as 23, giving 227 against a 280 budget. Measured with `sed '1,/^---$/d' templates/social/x-short.md | wc -m`; `--preview` counts this file's instruction block too, so it is not the right tool here.

Recommended placement: X, Bluesky, Mastodon, or the top of a release thread that the longer post follows.

---

`un-editorial-check` 1.1.0: a zero-dependency Node.js CLI and Agent Skill that pre-screens prose against 43 documented rules. Five review lanes, PDF/JSON/SARIF output, nothing rewritten unless you ask. https://github.com/ahaomar/un-editorial-check
