#!/usr/bin/env bash
# lark-wiki-graduate.sh — Project Cairn graduation adapter for the Lark/Feishu wiki provider.
#
# Encodes the verified adapter constraints (see references/graduation/lark-wiki.md
# and references/provider-interface.md):
#   - user identity + the coarse `wiki:wiki` scope. Granular read scopes
#     (wiki:space:retrieve / wiki:space:read / wiki:node:read) may never enter
#     the user token on CLI-style apps; the write-capable wiki:wiki does.
#   - NATIVE wiki resource API only (wiki spaces get / wiki nodes create /
#     wiki spaces get_node). NOT the +space-list / +node-create shortcuts —
#     they do strict literal scope prechecks that reject wiki:wiki coverage.
#   - create_note has a read dependency: the target space is resolved (read)
#     before the node is created (write).
#   - Frontmatter is owned by this script, built from CLI flags, and prepended
#     as a YAML-formatted text block ahead of the body -- Feishu docs have no
#     native structured-properties concept (unlike Notion), so this is an
#     embedded-text mechanism. Confirmed NOT to survive as parseable YAML
#     through Feishu's markdown conversion: the `---` markers survive as
#     literal text, but nested list entries (graduated_from's `- project: ...
#     / path: ...`) lose their indentation on round-trip, so a YAML parser
#     either errors or silently misassigns `path` as a top-level sibling key
#     instead of a field of the list entry. Treat it as a human-readable text
#     expression of structured intent, not a machine-re-parseable structure
#     (see references/provider-interface.md and cairn/LOG.md 2026-07-02 for
#     what was actually observed). Passing no frontmatter flags at all
#     preserves the old exact behavior (content written as-is) for backward
#     compatibility.
#   - Create mode makes a new wiki node and appends its initial document body.
#     Update mode (`--update-node-token` + `--update-obj-token` + `--update-url`)
#     targets that exact existing object and uses the installed lark-cli's
#     supported `docs +update --command overwrite` contract to replace the
#     document body. The caller resolves merged current truth (including the
#     `graduated_by` union) before invoking this low-level adapter.
#   - `--index-doc` append is idempotent: the index doc is fetched and checked
#     for an existing `[$TITLE](` entry before appending, so re-running
#     graduate for the same title does not duplicate the INDEX line (it does
#     not prevent a duplicate wiki NODE from being created -- Lark's API has
#     no object-level create-if-not-exists).
#
# Writes one graduated note into a Feishu wiki space and optionally links it
# into an INDEX node. Content is piped via stdin to dodge the CLI's
# cwd-relative @file path restriction.
#
# macOS Bash 3.2 compatible: no mapfile/readarray, no associative arrays.
# Iterating GFROM_ENTRIES uses "${GFROM_ENTRIES[@]:-}", not the bare form --
# confirmed on real bash 3.2.57 that the bare form throws "unbound variable"
# under `set -u` when the array has zero elements.
#
# Usage:
#   lark-wiki-graduate.sh --title TITLE [--content FILE]
#       [--space-id ID|my_library] [--parent-node-token TOKEN]
#       [--update-node-token TOKEN --update-obj-token TOKEN --update-url URL]
#       [--index-doc OBJ_TOKEN] [--identity user|bot]
#       [--type knowledge_note] [--summary TEXT] [--contains a,b,c] [--tags a,b,c]
#       [--graduated-from "<project>|<source path>" ...] [--authoring-mode ai_generated]
#       [--contributor NAME ...] [--graduated-by NAME ...]
#       [--dry-run]
#
# Output (stdout): JSON { space_id, node_token, obj_token, url }
# Requires: lark-cli (authorized; user identity with wiki:wiki), jq.

set -euo pipefail

CLI="${LARK_CLI:-lark-cli}"
IDENTITY="user"
SPACE_ID="my_library"
TITLE=""
CONTENT_FILE=""
PARENT=""
INDEX_DOC=""
UPDATE_NODE_TOKEN=""
UPDATE_OBJ_TOKEN=""
UPDATE_URL=""
DRY_RUN=0
TYPE=""; SUMMARY=""; CONTAINS=""; TAGS=""; AMODE=""
FRONTMATTER_FLAGS_GIVEN=0
GFROM_ENTRIES=()
CONTRIBUTOR_ENTRIES=()
GRADUATED_BY_ENTRIES=()

die() { echo "error: $*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --title) TITLE="${2:-}"; shift 2;;
    --content) CONTENT_FILE="${2:-}"; shift 2;;
    --space-id) SPACE_ID="${2:-}"; shift 2;;
    --parent-node-token) PARENT="${2:-}"; shift 2;;
    --index-doc) INDEX_DOC="${2:-}"; shift 2;;
    --update-node-token) UPDATE_NODE_TOKEN="${2:-}"; shift 2;;
    --update-obj-token) UPDATE_OBJ_TOKEN="${2:-}"; shift 2;;
    --update-url) UPDATE_URL="${2:-}"; shift 2;;
    --identity) IDENTITY="${2:-}"; shift 2;;
    --type) TYPE="${2:-}"; FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --summary) SUMMARY="${2:-}"; FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --contains) CONTAINS="${2:-}"; FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --tags) TAGS="${2:-}"; FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --graduated-from) GFROM_ENTRIES+=("${2:-}"); FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --contributor)
      [ -n "${2:-}" ] || die "--contributor requires a non-empty display name"
      CONTRIBUTOR_ENTRIES+=("$2"); FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --graduated-by)
      [ -n "${2:-}" ] || die "--graduated-by requires a non-empty display name"
      GRADUATED_BY_ENTRIES+=("$2"); FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --authoring-mode) AMODE="${2:-}"; FRONTMATTER_FLAGS_GIVEN=1; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) sed -n '2,53p' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$TITLE" ] || die "--title is required"
[ -z "$UPDATE_NODE_TOKEN$UPDATE_OBJ_TOKEN$UPDATE_URL" ] || {
  [ -n "$UPDATE_NODE_TOKEN" ] && [ -n "$UPDATE_OBJ_TOKEN" ] && [ -n "$UPDATE_URL" ] ||
    die "update mode requires --update-node-token, --update-obj-token, and --update-url together"
}
[ -z "$CONTENT_FILE" ] || [ -f "$CONTENT_FILE" ] || die "content file not found: $CONTENT_FILE"
command -v "$CLI" >/dev/null 2>&1 || die "$CLI not found"
command -v jq  >/dev/null 2>&1 || die "jq not found"

for e in "${GFROM_ENTRIES[@]:-}"; do
  [ -z "$e" ] && continue
  case "$e" in *"|"*) : ;; *) die "--graduated-from entries must be \"<project>|<source path>\", got: $e";; esac
done

# --- yaml helpers (reimplemented locally; see provider-interface.md on why
#     adapter scripts don't share code) ---
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

# --- detection guard: warn (never fail) if the caller still hand-embeds
#     frontmatter into --content instead of using the flags above ---
if [ "$FRONTMATTER_FLAGS_GIVEN" -eq 0 ] && [ -n "$CONTENT_FILE" ]; then
  FIRST_LINE="$(head -n1 "$CONTENT_FILE" 2>/dev/null || true)"
  [ "$FIRST_LINE" = "---" ] && echo "warn: content appears to pre-embed frontmatter; prefer --type/--summary/--contains/--tags/--graduated-from/--contributor/--graduated-by/--authoring-mode instead" >&2
fi

# --- assemble frontmatter (only if at least one flag was given); local-only
#     scratch file, allowed in dry-run per provider-interface.md ---
WRITE_CONTENT="$CONTENT_FILE"
if [ "$FRONTMATTER_FLAGS_GIVEN" -eq 1 ]; then
  CONTAINS_YAML="$(yaml_flow_list "$CONTAINS")"
  TAGS_YAML="$(yaml_flow_list "$TAGS")"
  CONTRIBUTORS_YAML="$(yaml_block_list contributors "${CONTRIBUTOR_ENTRIES[@]:-}")"
  GRADUATED_BY_YAML="$(yaml_block_list graduated_by "${GRADUATED_BY_ENTRIES[@]:-}")"
  GFROM_YAML=""
  for e in "${GFROM_ENTRIES[@]:-}"; do
    [ -z "$e" ] && continue
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
type: ${TYPE:-knowledge_note}
summary: $(yaml_scalar "$SUMMARY")
contains: $CONTAINS_YAML
tags: $TAGS_YAML
graduated_from:$GFROM_YAML$PROVENANCE_YAML
authoring_mode: ${AMODE:-ai_generated}
---"
  TMP_CONTENT="$(mktemp -t lark-grad.XXXXXX)"
  trap 'rm -f "$TMP_CONTENT"' EXIT
  { printf '%s\n' "$FRONTMATTER"; [ -n "$CONTENT_FILE" ] && cat "$CONTENT_FILE"; } > "$TMP_CONTENT"
  WRITE_CONTENT="$TMP_CONTENT"
fi

# lark() — wrap a JSON-returning native call with the shared identity flags.
lark() { "$CLI" "$@" --as "$IDENTITY" --json; }

# 0) Preflight: warn (don't fail) if the user token lacks wiki:wiki.
if [ "$DRY_RUN" -eq 0 ] && [ "$IDENTITY" = "user" ] && [ -z "$UPDATE_NODE_TOKEN" ]; then
  scopes="$("$CLI" auth status --json 2>/dev/null | jq -r '.identities.user.scope // ""' 2>/dev/null || true)"
  case " $scopes " in
    *" wiki:wiki "*) : ;;
    *) echo "warn: user token has no wiki:wiki scope; run: $CLI auth login --scope wiki:wiki" >&2;;
  esac
fi

# 1) Resolve target space (read dependency before create).
if [ -n "$UPDATE_NODE_TOKEN" ]; then
  RESOLVED_SPACE="$SPACE_ID"
elif [ "$SPACE_ID" = "my_library" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: $CLI wiki spaces get --params '{\"space_id\":\"my_library\"}' --as $IDENTITY --json" >&2
    RESOLVED_SPACE="<resolved-my_library-id>"
  else
    RESOLVED_SPACE="$(lark wiki spaces get --params '{"space_id":"my_library"}' | jq -r '.data.space.space_id')"
    [ -n "$RESOLVED_SPACE" ] && [ "$RESOLVED_SPACE" != "null" ] || die "failed to resolve my_library (need wiki:wiki + user identity)"
  fi
else
  RESOLVED_SPACE="$SPACE_ID"
fi

# 2) Create a node, or bind update mode to the caller-supplied existing object.
if [ -n "$UPDATE_NODE_TOKEN" ]; then
  NODE_TOKEN="$UPDATE_NODE_TOKEN"
  OBJ_TOKEN="$UPDATE_OBJ_TOKEN"
  NODE_URL="$UPDATE_URL"
else
  data="$(jq -nc --arg t "$TITLE" --arg p "$PARENT" \
    '{node_type:"origin",obj_type:"docx",title:$t} + (if $p=="" then {} else {parent_node_token:$p} end)')"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: $CLI wiki nodes create --params '{\"space_id\":\"$RESOLVED_SPACE\"}' --data '$data' --as $IDENTITY --json" >&2
    NODE_TOKEN="<node_token>"; OBJ_TOKEN="<obj_token>"; NODE_URL="<url>"
  else
    created="$(lark wiki nodes create --params "{\"space_id\":\"$RESOLVED_SPACE\"}" --data "$data")"
    NODE_TOKEN="$(printf '%s' "$created" | jq -r '.data.node.node_token')"
    OBJ_TOKEN="$(printf '%s' "$created" | jq -r '.data.node.obj_token')"
    NODE_URL="$(printf '%s' "$created" | jq -r '.data.node.url')"
    [ -n "$NODE_TOKEN" ] && [ "$NODE_TOKEN" != "null" ] || die "node create failed: $created"
  fi
fi

# 3) Write body + frontmatter (stdin avoids the @file cwd restriction). Create
# mode appends into the fresh empty document; update mode replaces current truth.
if [ -n "$WRITE_CONTENT" ]; then
  WRITE_COMMAND="append"
  [ -n "$UPDATE_NODE_TOKEN" ] && WRITE_COMMAND="overwrite"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: cat '$WRITE_CONTENT' | $CLI docs +update --doc $OBJ_TOKEN --command $WRITE_COMMAND --doc-format markdown --content - --as $IDENTITY --json" >&2
    if [ "$FRONTMATTER_FLAGS_GIVEN" -eq 1 ]; then
      echo "DRY-RUN: frontmatter:" >&2
      printf '%s\n' "$FRONTMATTER" | sed 's/^/  /' >&2
    fi
  else
    "$CLI" docs +update --doc "$OBJ_TOKEN" --command "$WRITE_COMMAND" --doc-format markdown \
      --content - --as "$IDENTITY" --json < "$WRITE_CONTENT" >/dev/null
  fi
fi

# 4) Read-back verify (title must round-trip).
if [ "$DRY_RUN" -eq 0 ]; then
  back="$("$CLI" docs +fetch --doc "$OBJ_TOKEN" --doc-format markdown --as "$IDENTITY" 2>/dev/null || true)"
  case "$back" in
    *"$TITLE"*) : ;;
    *) echo "warn: read-back did not contain the title; verify the node manually" >&2;;
  esac
fi

# 5) Optionally append a link into the INDEX/container node (update_index),
#    idempotent: skip if an entry for this title already exists.
#    Known TOCTOU: fetch-then-append is not atomic; two concurrent calls for
#    the same title could both pass the check before either appends. Accepted
#    for this codebase's serial single-invocation usage pattern (an agent
#    calling this script one graduation at a time), not fixed here.
if [ -n "$INDEX_DOC" ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY-RUN: $CLI docs +fetch --doc $INDEX_DOC --doc-format markdown --as $IDENTITY  (check for existing [$TITLE]( entry first)" >&2
    echo "DRY-RUN: printf -- '- [%s](%s)\\n' \"$TITLE\" \"$NODE_URL\" | $CLI docs +update --doc $INDEX_DOC --command append --doc-format markdown --content - --as $IDENTITY --json" >&2
  else
    index_back="$("$CLI" docs +fetch --doc "$INDEX_DOC" --doc-format markdown --as "$IDENTITY" 2>/dev/null || true)"
    case "$index_back" in
      *"[$TITLE]("*) echo "note: '$TITLE' already has an INDEX entry; not appending a duplicate" >&2;;
      *)
        printf -- '- [%s](%s)\n' "$TITLE" "$NODE_URL" \
          | "$CLI" docs +update --doc "$INDEX_DOC" --command append --doc-format markdown \
              --content - --as "$IDENTITY" --json >/dev/null
        ;;
    esac
  fi
fi

# 6) Emit result.
jq -nc --arg sp "$RESOLVED_SPACE" --arg nt "$NODE_TOKEN" --arg ot "$OBJ_TOKEN" --arg url "$NODE_URL" \
  '{space_id:$sp, node_token:$nt, obj_token:$ot, url:$url}'
