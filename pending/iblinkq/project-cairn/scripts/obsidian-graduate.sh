#!/usr/bin/env bash
# obsidian-graduate.sh — Project Cairn graduation adapter for the Obsidian provider.
#
# Encodes the verified adapter constraints (see references/graduation/obsidian.md,
# references/provider-interface.md, and scripts/obsidian-preflight.sh):
#   - The `obsidian` CLI is used only to RESOLVE the vault (read dependency,
#     same "create_note is not a pure write" principle as Lark/Notion) and to
#     read the file back for verification. The note body itself is written
#     DIRECTLY to the vault's filesystem, not through `obsidian create` --
#     that command takes content as a shell argument, which hits the same
#     length/quoting fragility the other adapters route around (Lark pipes
#     via stdin; here we just write the file).
#   - Frontmatter is YAML embedded in the note itself (Obsidian's native
#     format), not external properties (Notion) and not left for the caller
#     to hand-embed (Lark). This script owns frontmatter construction from
#     flags, the same way notion-graduate.sh owns DB properties -- `--content`
#     here is BODY ONLY, no frontmatter inside it.
#   - `graduated_from` is a STRUCTURED LIST of {project, path} entries, not a
#     scalar. Verified against real notes already in this vault's knowledge
#     base (30_工程知识库/*.md) -- every one uses this shape, several with
#     multiple entries. references/frontmatter.md did not document this
#     internal structure; only describes the field as "required".
#   - `[[wikilinks]]` in `--content` pass through unchanged: Obsidian is the
#     one provider with native WikiLink support (config.yaml's
#     `link_format: wikilink`), so no rewrite step is needed here the way
#     Notion needs a two-pass title->page-mention conversion.
#   - Overwrite protection: writing straight to a vault path can silently
#     clobber an existing file with the same title. Create mode refuses to
#     overwrite; explicit re-graduation uses --force to atomically replace the
#     same path with caller-supplied current truth.
#   - INDEX append is idempotent: skips the append if `[[Title]]` already
#     appears in the INDEX file, so a --force re-run (the only way to reach
#     this code path twice for the same title -- overwrite protection blocks
#     a plain re-run before it gets here) doesn't accumulate duplicate lines.
#
# macOS Bash 3.2 compatible: no mapfile/readarray, no associative arrays
# (ordinary indexed arrays are fine in 3.2 and used here for repeatable
# --graduated-from entries). No `timeout` (not on stock macOS) -- same
# retry-with-sleep tradeoff as obsidian-preflight.sh.
#
# Requires: jq; obsidian (only for vault resolution + read-back verify).
#
# Usage:
#   obsidian-graduate.sh --vault "<vault name>" --title TITLE --target "<folder>"
#       [--content FILE] [--index "<folder>/INDEX.md"]
#       [--type knowledge_note] [--summary TEXT] [--contains a,b,c] [--tags a,b,c]
#       --graduated-from "<project>|<source path>" [--graduated-from "..." ...]
#       [--contributor NAME ...] [--graduated-by NAME ...]
#       [--authoring-mode ai_generated] [--force] [--dry-run]
#
# Output (stdout): JSON { path, obsidian_url }
# obsidian_url follows Obsidian's documented obsidian://open URI scheme.
# Confirmed the generated URL dispatches cleanly via `open` on macOS (no
# handler error); did not independently confirm the target note becomes the
# focused file on the other end (no screenshot tooling in this pass).
set -uo pipefail

CLI="${OBSIDIAN_CLI:-obsidian}"
VAULT=""; TITLE=""; TARGET=""; CONTENT_FILE=""; INDEX=""
TYPE="knowledge_note"; SUMMARY=""; CONTAINS=""; TAGS=""; AMODE="ai_generated"
FORCE=0; DRY_RUN=0
GFROM_ENTRIES=()
CONTRIBUTOR_ENTRIES=()
GRADUATED_BY_ENTRIES=()
RETRIES=4

die() { echo "error: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --vault) VAULT="${2:-}"; shift 2;;
    --title) TITLE="${2:-}"; shift 2;;
    --target) TARGET="${2:-}"; shift 2;;
    --content) CONTENT_FILE="${2:-}"; shift 2;;
    --index) INDEX="${2:-}"; shift 2;;
    --type) TYPE="${2:-}"; shift 2;;
    --summary) SUMMARY="${2:-}"; shift 2;;
    --contains) CONTAINS="${2:-}"; shift 2;;
    --tags) TAGS="${2:-}"; shift 2;;
    --graduated-from) GFROM_ENTRIES+=("${2:-}"); shift 2;;
    --contributor)
      [ -n "${2:-}" ] || die "--contributor requires a non-empty display name"
      CONTRIBUTOR_ENTRIES+=("$2"); shift 2;;
    --graduated-by)
      [ -n "${2:-}" ] || die "--graduated-by requires a non-empty display name"
      GRADUATED_BY_ENTRIES+=("$2"); shift 2;;
    --authoring-mode) AMODE="${2:-}"; shift 2;;
    --force) FORCE=1; shift;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) sed -n '2,55p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$VAULT" ] || die '--vault "<vault name>" is required'
[ -n "$TITLE" ] || die "--title is required"
[ -n "$TARGET" ] || die '--target "<folder>" is required'
[ "${#GFROM_ENTRIES[@]}" -gt 0 ] || die '--graduated-from "<project>|<source path>" is required (at least one; repeatable)'
[ -z "$CONTENT_FILE" ] || [ -f "$CONTENT_FILE" ] || die "content file not found: $CONTENT_FILE"
command -v "$CLI" >/dev/null 2>&1 || die "$CLI not found — run scripts/obsidian-preflight.sh first"
command -v jq >/dev/null 2>&1 || die "jq not found"

for e in "${GFROM_ENTRIES[@]}"; do
  case "$e" in *"|"*) : ;; *) die "--graduated-from entries must be \"<project>|<source path>\", got: $e";; esac
done

# --- yaml helpers ---
yaml_scalar() { jq -Rn --arg s "$1" '$s'; }   # YAML double-quoted scalars are JSON-compatible, so jq's JSON string escaping produces a valid one -- handles embedded newlines/tabs/control chars that the previous hand-rolled sed (backslash+quote only) missed
yaml_flow_list() { # comma-separated -> [a, b, c] (empty -> [])
  s="$1"; out=""
  IFS=','; for item in $s; do
    item="$(printf '%s' "$item" | sed -e 's/^ *//' -e 's/ *$//')"
    [ -z "$item" ] && continue
    if [ -z "$out" ]; then out="$item"; else out="$out, $item"; fi
  done
  unset IFS
  printf '[%s]' "$out"
}
yaml_block_list() { # field, repeatable values; empty -> no output
  field="$1"; shift; body=""
  seen_entries=()
  for item in "$@"; do
    [ -z "$item" ] && continue
    duplicate=0
    for seen in "${seen_entries[@]:-}"; do
      [ -z "$seen" ] && continue
      [ "$seen" = "$item" ] && duplicate=1 && break
    done
    [ "$duplicate" -eq 1 ] && continue
    seen_entries+=("$item")
    body="$body
  - $(yaml_scalar "$item")"
  done
  [ -n "$body" ] && printf '%s:%s\n' "$field" "$body"
  return 0
}

# --- resolve vault path (read dependency before any write) ---
VAULT_PATH=""
attempt=0
while [ "$attempt" -lt "$RETRIES" ]; do
  attempt=$((attempt + 1))
  VAULT_PATH="$("$CLI" vault="$VAULT" vault info=path 2>/dev/null | tail -1 || true)"
  [ -n "$VAULT_PATH" ] && [ -d "$VAULT_PATH" ] && break
  VAULT_PATH=""
  sleep "$attempt"
done
[ -n "$VAULT_PATH" ] || die "could not resolve vault '$VAULT' after $RETRIES tries — run scripts/obsidian-preflight.sh --vault \"$VAULT\" to diagnose"

# --- build target path ---
SAFE_TITLE="$(printf '%s' "$TITLE" | tr '/\\:*?"<>|' '-')"
REL_PATH="$TARGET/$SAFE_TITLE.md"
FULL_PATH="$VAULT_PATH/$REL_PATH"

if [ -e "$FULL_PATH" ] && [ "$FORCE" -ne 1 ]; then
  die "note already exists at '$REL_PATH' — pass --force to overwrite"
fi

# --- assemble frontmatter ---
CONTAINS_YAML="$(yaml_flow_list "$CONTAINS")"
TAGS_YAML="$(yaml_flow_list "$TAGS")"
CONTRIBUTORS_YAML="$(yaml_block_list contributors "${CONTRIBUTOR_ENTRIES[@]:-}")"
GRADUATED_BY_YAML="$(yaml_block_list graduated_by "${GRADUATED_BY_ENTRIES[@]:-}")"
GFROM_YAML=""
for e in "${GFROM_ENTRIES[@]}"; do
  proj="${e%%|*}"; path="${e#*|}"
  GFROM_YAML="$GFROM_YAML
  - project: $(yaml_scalar "$proj")
    path: $(yaml_scalar "$path")"
done
PROVENANCE_YAML=""
[ -n "$CONTRIBUTORS_YAML" ] && PROVENANCE_YAML="$PROVENANCE_YAML
$CONTRIBUTORS_YAML"
[ -n "$GRADUATED_BY_YAML" ] && PROVENANCE_YAML="$PROVENANCE_YAML
$GRADUATED_BY_YAML"

FRONTMATTER="---
type: $TYPE
summary: $(yaml_scalar "$SUMMARY")
contains: $CONTAINS_YAML
tags: $TAGS_YAML
graduated_from:$GFROM_YAML$PROVENANCE_YAML
authoring_mode: $AMODE
---"

BODY=""
[ -n "$CONTENT_FILE" ] && BODY="$(cat "$CONTENT_FILE")"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY-RUN: would write $(printf '%s' "$BODY" | wc -l | tr -d ' ') body lines to:" >&2
  echo "  $FULL_PATH" >&2
  echo "DRY-RUN: frontmatter:" >&2
  printf '%s\n' "$FRONTMATTER" | sed 's/^/  /' >&2
  [ -n "$INDEX" ] && echo "DRY-RUN: would append a WikiLink line to $VAULT_PATH/$INDEX" >&2
  jq -nc --arg p "$REL_PATH" '{path:$p, obsidian_url:"<dry-run>"}'
  exit 0
fi

# --- write atomically: temp file in the same dir, then mv into place ---
mkdir -p "$(dirname "$FULL_PATH")" || die "could not create target folder"
TMP_FILE="$(mktemp "${FULL_PATH}.XXXXXX")" || die "mktemp failed"
trap 'rm -f "$TMP_FILE"' EXIT
{
  printf '%s\n' "$FRONTMATTER"
  printf '# %s\n' "$TITLE"
  [ -n "$BODY" ] && printf '\n%s\n' "$BODY"
} > "$TMP_FILE"
mv "$TMP_FILE" "$FULL_PATH" || die "could not move note into place"
trap - EXIT

# --- read-back verify (direct filesystem, no need to round-trip the flaky CLI) ---
[ -f "$FULL_PATH" ] && grep -q "^type: $TYPE\$" "$FULL_PATH" || echo "warn: read-back did not find the expected frontmatter; verify manually" >&2

# --- optional INDEX append (WikiLink — this provider's native format),
#     idempotent: skip if an entry for this title already exists.
#     Known TOCTOU: grep-then-append is not atomic; two concurrent --force
#     re-runs for the same title could both pass the check before either
#     appends. Accepted for this codebase's serial single-invocation usage
#     pattern, not fixed here. ---
if [ -n "$INDEX" ]; then
  INDEX_FULL="$VAULT_PATH/$INDEX"
  mkdir -p "$(dirname "$INDEX_FULL")" || die "could not create INDEX folder"
  [ -f "$INDEX_FULL" ] || : > "$INDEX_FULL"
  if grep -qF "[[$SAFE_TITLE]]" "$INDEX_FULL" 2>/dev/null; then
    echo "note: '$SAFE_TITLE' already has an INDEX entry; not appending a duplicate" >&2
  else
    LINK_LINE="- [[$SAFE_TITLE]]"
    [ -n "$SUMMARY" ] && LINK_LINE="$LINK_LINE — $SUMMARY"
    [ -s "$INDEX_FULL" ] && [ "$(tail -c1 "$INDEX_FULL")" != "" ] && printf '\n' >> "$INDEX_FULL"
    printf '%s\n' "$LINK_LINE" >> "$INDEX_FULL"
  fi
fi

# --- emit result ---
ENC_VAULT="$(jq -rn --arg v "$VAULT" '$v|@uri')"
ENC_PATH="$(jq -rn --arg p "$REL_PATH" '$p|@uri')"
jq -nc --arg p "$REL_PATH" --arg url "obsidian://open?vault=$ENC_VAULT&file=$ENC_PATH" \
  '{path:$p, obsidian_url:$url}'
