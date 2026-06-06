#!/usr/bin/env bash
# find.sh — professional cross-registry agent-skill finder.
#
# Searches skills.sh + clawhub.ai + GitHub, then presents EACH board on its own
# NATIVE metric (skills.sh: installs · clawhub: installs/stars · GitHub: stars),
# shows the top of each board, security-scans the top installable candidates,
# flags already-installed skills, and reports per-source health/latency.
#
# Deliberately uses no invented composite "score": ranking within each board is
# that board's own popularity metric. The only computed signal shown is
# `match %` = the share of your query words a skill's name/summary mentions —
# a transparent relevance hint, not a quality verdict.
#
# Usage:
#   scripts/find.sh "<query>" [--limit N] [--scan K] [--no-scan] [--json]
#
# Requires: jq, curl. Optional: gh (GitHub + skills.sh body fetch), unzip
# (clawhub body fetch). Missing optional tools degrade gracefully. No API keys.

set -uo pipefail

usage() { cat <<'U'
find.sh — cross-registry agent-skill finder (skills.sh + clawhub.ai + GitHub)

  find.sh "<query>" [--limit N] [--scan K] [--no-scan] [--json]

  --limit N    results per source (default 10)
  --scan K     security-scan the top K installable candidates per registry (default 2, max 5)
  --no-scan    skip the security scan (faster)
  --json       emit machine-readable JSON instead of the formatted report
  -h, --help   show this help
U
}

QUERY="" ; LIMIT=10 ; SCAN_K=2 ; JSON_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --limit) LIMIT="${2:-10}"; shift 2 ;;
    --scan)  SCAN_K="${2:-2}"; shift 2 ;;
    --no-scan) SCAN_K=0; shift ;;
    --json)  JSON_ONLY=1; shift ;;
    *)       QUERY="${QUERY:+$QUERY }$1"; shift ;;
  esac
done
# numeric guards: fall back to defaults on non-numeric input
case "$LIMIT"  in ''|*[!0-9]*) LIMIT=10 ;; esac
case "$SCAN_K" in ''|*[!0-9]*) SCAN_K=2 ;; esac
[ "$SCAN_K" -gt 5 ] && SCAN_K=5
if [ -z "${QUERY// /}" ]; then usage >&2; exit 2; fi
command -v jq   >/dev/null 2>&1 || { echo "error: jq is required (brew install jq)" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "error: curl is required" >&2; exit 1; }

ENC_QUERY=$(jq -rn --arg q "$QUERY" '$q|@uri')
QTOKENS=$(jq -cn --arg q "$QUERY" '$q|ascii_downcase|[scan("[a-z0-9]+")]')
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
now_ms() { echo $(( $(date +%s%N)/1000000 )); }

# ---- already-installed awareness ----------------------------------------
INSTALLED_JSON="[]"
for d in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
  [ -d "$d" ] || continue
  for s in "$d"/*; do [ -e "$s" ] && basename "$s"; done
done | sort -u > "$TMP/installed.txt" 2>/dev/null
[ -s "$TMP/installed.txt" ] && INSTALLED_JSON=$(jq -R . "$TMP/installed.txt" | jq -s .)

# ---- source fetchers (each records health: status + latency + count) -----
mkdir -p "$TMP/health"
record_health() { jq -cn --arg n "$1" --arg s "$2" --argjson ms "$3" --argjson c "$4" \
  '{source:$n, status:$s, ms:$ms, count:$c}' > "$TMP/health/$1.json"; }

fetch_skillssh() {
  local t0 t1 out n; t0=$(now_ms)
  out=$(curl -sS --max-time 25 "https://skills.sh/api/search?q=${ENC_QUERY}&limit=${LIMIT}" 2>/dev/null)
  t1=$(now_ms)
  [ -z "$out" ] && { record_health skills.sh failed $((t1-t0)) 0; return 0; }
  echo "$out" | jq -c '(.skills // [])[] |
      { board:"skills.sh", name:.skillId, summary:null, installs:(.installs//0),
        stars:null, version:null, updatedAt:null,
        url:("https://www.skills.sh/"+.source+"/"+.skillId), repo:.source, slug:null }' \
      2>/dev/null > "$TMP/skillssh.ndjson"
  n=$(wc -l < "$TMP/skillssh.ndjson" | tr -d ' '); record_health skills.sh ok $((t1-t0)) "${n:-0}"
}

fetch_clawhub() {
  local t0 t1 search; t0=$(now_ms)
  search=$(curl -sS --max-time 15 "https://clawhub.ai/api/search?q=${ENC_QUERY}" 2>/dev/null)
  [ -z "$search" ] && { t1=$(now_ms); record_health clawhub failed $((t1-t0)) 0; return 0; }
  echo "$search" | jq -r --argjson n "$LIMIT" '(.results // [])[:$n][].slug' 2>/dev/null > "$TMP/claw_slugs.txt"
  : > "$TMP/clawhub.ndjson"
  while read -r slug; do
    [ -z "$slug" ] && continue
    { curl -sS --max-time 10 "https://clawhub.ai/api/skill?slug=${slug}" 2>/dev/null \
      | jq -c '(.skill // {}) as $s | {
          board:"clawhub", name:($s.slug//""), summary:($s.summary//null),
          installs:($s.stats.installsAllTime//0),
          stars:($s.stats.stars//0), version:(.latestVersion.version//null),
          updatedAt:($s.updatedAt//null), url:("https://clawhub.ai/skill/"+($s.slug//"")),
          repo:null, slug:($s.slug//"") } | select(.name!="")' 2>/dev/null >> "$TMP/clawhub.ndjson"; } &
  done < "$TMP/claw_slugs.txt"
  wait; t1=$(now_ms)
  record_health clawhub ok $((t1-t0)) "$(wc -l < "$TMP/clawhub.ndjson" | tr -d ' ')"
}

fetch_github() {
  local t0 t1 kw; t0=$(now_ms)
  command -v gh >/dev/null 2>&1 || { record_health github skipped 0 0; return 0; }
  kw="${QUERY%% *}"   # the claude-skills topic is small; multi-word AND empties it
  # Union across the common skill topics. Each --topic call is its own AND query
  # (GitHub has no OR), so query each in PARALLEL to temp files, then merge+dedupe.
  mkdir -p "$TMP/gh"
  for topic in claude-skills agent-skills claude-code-skills; do
    gh search repos "$kw" --topic "$topic" --limit "$LIMIT" \
       --json fullName,stargazersCount,description,url 2>/dev/null \
    | jq -c '.[] | { board:"github", name:.fullName, summary:(.description//null),
          stars:(.stargazersCount//0), url:.url, repo:.fullName }' 2>/dev/null \
    > "$TMP/gh/$topic.ndjson" &
  done
  wait
  cat "$TMP/gh"/*.ndjson 2>/dev/null | jq -s -c 'unique_by(.name) | .[]' 2>/dev/null > "$TMP/github.ndjson"
  t1=$(now_ms); record_health github ok $((t1-t0)) "$(wc -l < "$TMP/github.ndjson" 2>/dev/null | tr -d ' ')"
}

: > "$TMP/skillssh.ndjson"; : > "$TMP/clawhub.ndjson"; : > "$TMP/github.ndjson"
fetch_skillssh & fetch_clawhub & fetch_github & wait

# ---- enrich + rank each board on its OWN native metric -------------------
# match%  = query-token coverage in name+summary (transparent relevance hint).
# installed = normalized-name match against a local skills dir (same heuristic
#             as the cross-board flag, so face-swap ↔ faceswap line up).
enrich='
  def nrm: ascii_downcase | gsub("[^a-z0-9]+";"");
  def matchpct(name; summary):
    ((name+" "+(summary//""))|ascii_downcase) as $hay
    | (if ($qt|length)==0 then 0
       else ([ $qt[] | select(. as $t | $hay|contains($t)) ]|length) / ($qt|length) * 100 end)
    | round;
  ($inst|map(nrm)) as $instn
  | map(. + { match: matchpct(.name; .summary),
              installed: ((.name|nrm) as $x | $instn|index($x))!=null })'

SK=$(jq -s --argjson qt "$QTOKENS" --argjson inst "$INSTALLED_JSON" \
      "$enrich | sort_by(-.installs)" "$TMP/skillssh.ndjson" 2>/dev/null); [ -z "$SK" ] && SK="[]"
CL=$(jq -s --argjson qt "$QTOKENS" --argjson inst "$INSTALLED_JSON" \
      "$enrich | sort_by(-.installs, -.stars)" "$TMP/clawhub.ndjson" 2>/dev/null); [ -z "$CL" ] && CL="[]"
GH=$(jq -s --argjson qt "$QTOKENS" --argjson inst "$INSTALLED_JSON" \
      "$enrich | sort_by(-.match, -.stars)" "$TMP/github.ndjson" 2>/dev/null); [ -z "$GH" ] && GH="[]"

# cross-board note (heuristic): match on the normalized name (lowercased,
# non-alphanumerics stripped) so "face-swap" ↔ "faceswap" line up, in BOTH
# directions. Still a name heuristic — a true cross-post with a renamed slug
# can be missed.
CL_NORMS=$(jq -c '[.[].name | ascii_downcase | gsub("[^a-z0-9]+";"")]' <<<"$CL")
SK_NORMS=$(jq -c '[.[].name | ascii_downcase | gsub("[^a-z0-9]+";"")]' <<<"$SK")
SK=$(jq -c --argjson o "$CL_NORMS" 'map(. + {also_other: ((.name|ascii_downcase|gsub("[^a-z0-9]+";"")) as $n | $o|index($n))!=null})' <<<"$SK")
CL=$(jq -c --argjson o "$SK_NORMS" 'map(. + {also_other: ((.name|ascii_downcase|gsub("[^a-z0-9]+";"")) as $n | $o|index($n))!=null})' <<<"$CL")

# ---- security scan: top installable candidates on each registry ----------
scan_body() { local f="$1" flags="" level="clean"
  grep -Eiq '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba)?sh' "$f" && { flags+="curl-pipe-install;"; level="risky"; }
  grep -Eiq '\b(eval|source)[[:space:]]+["'\''$(]*\b(curl|wget)' "$f" && { flags+="eval-remote;"; level="risky"; }
  grep -Eiq 'base64[[:space:]]+(-d|--decode)[^|]*\|[[:space:]]*(ba)?sh' "$f" && { flags+="base64-pipe-exec;"; level="risky"; }
  grep -Eiq 'allowed-tools:.*(Bash\(\*|Bash\([^)]*\*[^)]*:\*)' "$f" && { flags+="broad-tool-grant;"; [ "$level" = clean ] && level="caution"; }
  grep -Eiq '(~/\.ssh|~/\.aws|/\.env\b|id_rsa|AWS_SECRET|PRIVATE_KEY)' "$f" && { flags+="reads-secrets;"; [ "$level" = clean ] && level="caution"; }
  grep -Eiq '(paste|enter|provide).{0,20}(api[ _-]?key|token|password)' "$f" && { flags+="solicits-credentials;"; [ "$level" = clean ] && level="caution"; }
  echo "${level}|${flags%;}"; }

get_body() { local rec="$1" out="$2" repo slug name br path
  repo=$(jq -r '.repo // empty' <<<"$rec"); slug=$(jq -r '.slug // empty' <<<"$rec"); name=$(jq -r '.name' <<<"$rec")
  if [ -n "$repo" ] && command -v gh >/dev/null 2>&1; then
    br=$(gh api "repos/$repo" --jq '.default_branch' 2>/dev/null)
    if [ -n "$br" ]; then
      path=$(gh api "repos/$repo/git/trees/$br?recursive=1" --jq \
        "[.tree[].path | select(endswith(\"SKILL.md\")) | select(test(\"(^|/)$name/SKILL.md$\";\"i\"))][0]" 2>/dev/null)
      [ -z "$path" ] && path=$(gh api "repos/$repo/git/trees/$br?recursive=1" --jq \
        '[.tree[].path | select(endswith("SKILL.md"))][0]' 2>/dev/null)
      [ -n "$path" ] && curl -sS --max-time 12 "https://raw.githubusercontent.com/$repo/$br/$path" -o "$out" 2>/dev/null && [ -s "$out" ] && return 0
    fi
  fi
  if [ -n "$slug" ] && command -v unzip >/dev/null 2>&1; then
    curl -sS --max-time 12 "https://clawhub.ai/api/download?slug=$slug" -o "$TMP/dl.zip" 2>/dev/null && [ -s "$TMP/dl.zip" ] \
      && unzip -p "$TMP/dl.zip" SKILL.md > "$out" 2>/dev/null && [ -s "$out" ] && return 0
  fi
  return 1; }

scan_board() { # $1=array json -> echoes array json with .risk on top SCAN_K
  local arr="$1" out="[]" k=0 rec res lvl fl
  [ "$SCAN_K" -eq 0 ] && { echo "$arr"; return; }
  while [ "$k" -lt "$SCAN_K" ]; do
    rec=$(jq -c ".[$k] // empty" <<<"$arr"); [ -z "$rec" ] && break
    if get_body "$rec" "$TMP/body.md"; then
      res=$(scan_body "$TMP/body.md"); lvl="${res%%|*}"; fl="${res#*|}"
      rec=$(jq -c --arg l "$lvl" --arg f "$fl" '.risk={level:$l, flags:($f|split(";")|map(select(.!="")))}' <<<"$rec")
    else rec=$(jq -c '.risk={level:"unknown", flags:[]}' <<<"$rec"); fi
    out=$(jq -c --argjson r "$rec" '. + [$r]' <<<"$out"); k=$((k+1))
  done
  jq -c --argjson s "$out" '$s + .[($s|length):]' <<<"$arr"; }

SK=$(scan_board "$SK"); CL=$(scan_board "$CL")

HEALTH=$(cat "$TMP/health"/*.json 2>/dev/null | jq -s 'sort_by(.source)'); [ -z "$HEALTH" ] && HEALTH="[]"
OUT="$TMP/result.json"
jq -n --arg q "$QUERY" --argjson health "$HEALTH" --argjson inst "$INSTALLED_JSON" \
      --argjson sk "$SK" --argjson cl "$CL" --argjson gh "$GH" \
  '{query:$q, health:$health, installed_count:($inst|length), skills_sh:$sk, clawhub:$cl, github:$gh}' > "$OUT"
RESULT_FILE="${TMPDIR:-/tmp}/find-skills-$(date +%s).json"; cp "$OUT" "$RESULT_FILE"

if [ "$JSON_ONLY" -eq 1 ]; then cat "$OUT"; echo "# full JSON: $RESULT_FILE" >&2; exit 0; fi

# ---- output --------------------------------------------------------------
rule_w=$(( ${#QUERY} + 22 )); [ "$rule_w" -lt 66 ] && rule_w=66
RULE=$(printf '─%.0s' $(seq 1 "$rule_w"))

printf '\n┏%s┓\n  find-skills   ·   "%s"\n┗%s┛\n' "$RULE" "$QUERY" "$RULE"
printf '  sources   '
jq -r '.[] | "\(.source) " + (if .status=="ok" then "✓ \(.count)·\((.ms/1000*10|round)/10)s" elif .status=="skipped" then "– skipped" else "✗ failed" end)' <<<"$HEALTH" | paste -sd '   ' -
printf '  local     %s skills installed on this machine\n' "$(jq 'length' <<<"$INSTALLED_JSON")"

# ---- top of each board (native metric — NOT a vetted pick) ---------------
printf '\n▶ TOP OF EACH BOARD  (by that board'\''s own metric — keyword/popularity, not vetted; read before trusting)\n'
sk0=$(jq -c '.[0] // empty' <<<"$SK"); cl0=$(jq -c '.[0] // empty' <<<"$CL"); gh0=$(jq -c '.[0] // empty' <<<"$GH")
if [ -n "$sk0" ]; then
  jq -r '"  skills.sh   \(.name)   (\(.repo))  —  ⬇ \(.installs) installs · match \(.match)%" + (if .installed then "  ✓ INSTALLED" else "" end) + "\n              \(.url)"' <<<"$sk0"
else printf '  skills.sh   (no match for this query)\n'; fi
if [ -n "$cl0" ]; then
  jq -r '"  clawhub     \(.name)  —  ⬇ \(.installs) installs · ★ \(.stars)  · match \(.match)%" + (if .installed then "  ✓ INSTALLED" else "" end) + "\n              \(.url)"' <<<"$cl0"
else printf '  clawhub     (no match for this query)\n'; fi
if [ -n "$gh0" ]; then
  jq -r '"  github      \(.name)  —  ★ \(.stars)  · match \(.match)%\n              \(.url)"' <<<"$gh0"
else printf '  github      (no match / gh unavailable)\n'; fi

# ---- already installed & relevant (positive nudge) -----------------------
inst_hits=$(jq -c '[(.skills_sh[],.clawhub[]) | select(.installed)] | unique_by(.name)' "$OUT")
if [ "$(jq 'length' <<<"$inst_hits")" -gt 0 ]; then
  printf '\n%s\n✓ ALREADY ON YOUR MACHINE (relevant — no install needed)\n' "$RULE"
  jq -r '.[] | "  • \(.name)  — already installed, ⬇ \(.installs) installs, match \(.match)%. A solid match you already have."' <<<"$inst_hits"
fi

board_list() { # $1=array $2=metric-fmt
  local arr="$1" fmt="$2"
  if [ "$(jq 'length' <<<"$arr")" -eq 0 ]; then echo "  (no matches for this query)"; return; fi
  jq -r --argjson lim "$LIMIT" --arg fmt "$fmt" '
    to_entries | .[:$lim][] | (.key+1) as $i | .value |
    " [\($i)] \(.name)" +
      (if .installed then "  ✓ INSTALLED" else "" end) +
      (if (.also_other // false) then (if $fmt=="claw" then "  (also on skills.sh)" else "  (also on clawhub)" end) else "" end) +
      (if .risk and .risk.level!="unknown" then
         (if .risk.level=="risky" then "  ⛔ RISKY" elif .risk.level=="caution" then "  ⚠ caution" else "  ✓ clean" end) +
         (if (.risk.flags|length)>0 then " ["+(.risk.flags|join(", "))+"]" else "" end) else "" end) + "\n" +
    "     " + (if $fmt=="claw" then "⬇ \(.installs) installs · ★ \(.stars)" else "⬇ \(.installs) installs · \(.repo)" end) +
      "   ·   match \(.match)%" + "\n" +
    (if .summary then "     " + (.summary[0:150]) + "\n" else "" end) +
    "     \(.url)"' <<<"$arr"
}

printf '\n%s\n📦 skills.sh   (ranked by installs · 1-click installable)\n\n' "$RULE"
board_list "$SK" plain
printf '\n%s\n🪝 clawhub   (ranked by installs · stars · 1-click installable)\n\n' "$RULE"
board_list "$CL" claw

printf '\n%s\n🐙 github   (ranked by match%%, then stars · review before use)\n\n' "$RULE"
if [ "$(jq 'length' <<<"$GH")" -eq 0 ]; then echo "  (gh unavailable or no matches)"; else
  jq -r '.[] | "  ★ \(.stars|tostring|(" "*(7-length))+.)  · match \(.match)%   \(.name)\n          \(.summary // "—")\n          \(.url)"' <<<"$GH"
fi

printf '\n%s\n📚 curated lists   (human-vetted, worth a scan)\n' "$RULE"
printf '  ComposioHQ/awesome-claude-skills · microsoft/skills · bergside/awesome-design-skills\n'
printf '\n# full JSON: %s\n' "$RESULT_FILE"
