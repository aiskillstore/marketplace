# Resolving conflicts between stacked PRs

**Textual conflicts.** Read each hunk and combine intent: prose takes the
richer superset, code keeps both sides' additions (two PRs that each add a
function at the same anchor: keep both). For a generated or lock file
(`Cargo.lock`, `package-lock.json`, `poetry.lock`), take the base version and
regenerate from the resolved manifest, then confirm consistency (`npm ci` fails
if a lockfile and manifest disagree).

**Semantic conflicts** (invisible to Git):

- **Shared version or sequence constants.** Two layers must not both claim the
  same bump. Relabel by stack order: if a lower layer took `3 -> 4`, the upper
  one becomes `4 -> 5`. Regenerate whatever the change feeds and re-run the
  affected tests.
- **Migration or numbered-file collisions.** The same numeric prefix on
  different filenames is a clash Git cannot see. Renumber by stack order.
- **Combined-tree build or test breaks.** Two layers that touch the same
  module in different files can still fail together. The top branch is where
  you catch that.
- **Mutually dependent PRs.** A library bump and its call-site fix only build
  together. Stacking them is the fix: the atomic merge never exposes the
  broken intermediate state. Folding one PR into another and closing it
  changes the contributor-visible outcome; obtain approval before doing that.
