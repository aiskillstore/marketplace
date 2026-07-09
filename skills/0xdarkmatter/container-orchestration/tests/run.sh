#!/usr/bin/env bash
# Self-test for container-orchestration — fully offline: never runs a real
# `docker build`/`docker push` and never calls a real registry.
#
# build-push.sh ships real side effects, so this suite exercises ONLY its safe
# surfaces: the protocol contract (--help / EXAMPLES / exit codes), arg parsing
# through the no-docker `--dry-run` path, stream separation (data on stdout,
# chatter on stderr), and a pre/post proof that the happy-path DATA output is
# unchanged by the protocol backfill (only the chatter banners and --help were
# added/moved). A sentinel `docker` on PATH proves the help/parse/dry-run paths
# never invoke docker at all.
#
# Usage:   bash tests/run.sh
# Exit:    0 all pass, 1 one or more failures

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL="$(dirname "$HERE")"
V="$SKILL/scripts/build-push.sh"

# Pre-backfill git blob of build-push.sh — used for a live pre/post data diff
# when the object is still reachable in the repo's history.
OLD_BLOB="0d6b10cdef2901784b3360a2c61ba2ea144b6bc2"

SB="$(mktemp -d)"; trap 'rm -rf "$SB"' EXIT
PASS=0; FAIL=0
ok() { PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
no() { FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
expect_exit() { [[ "$2" == "$3" ]] && ok "$1 (exit $3)" || no "$1 (want $2 got $3)"; }
expect_has()  { case "$3" in *"$2"*) ok "$1";; *) no "$1 (missing '$2')";; esac; }

# Sentinel `docker`: records any invocation into $DOCKER_SENTINEL_LOG, then
# exits nonzero WITHOUT performing a real build/push. Prepended to PATH so we
# can prove the safe paths never touch docker (and the baseline run of the old
# script likewise performs no real build).
mkdir -p "$SB/bin"
cat > "$SB/bin/docker" <<'EOF'
#!/usr/bin/env bash
# Test sentinel — never builds/pushes; just records the call.
printf 'docker %s\n' "$*" >> "${DOCKER_SENTINEL_LOG:-/dev/null}"
exit 1
EOF
chmod +x "$SB/bin/docker"
NO_DOCKER_PATH="$SB/bin:$PATH"
no_docker_calls() { [[ ! -s "$SB/docker.log" ]]; }   # true == nothing was logged

echo "=== container-orchestration self-test ==="

# ── syntax + contract header ─────────────────────────────────────────────────
echo "-- contract --"
bash -n "$V" 2>/dev/null && ok "bash -n build-push.sh" || no "bash -n build-push.sh"
hdr="$(head -25 "$V")"
expect_has "header has Usage"     "Usage:"   "$hdr"
expect_has "header has Output"    "Output:"  "$hdr"
expect_has "header has Stderr"    "Stderr:"  "$hdr"
expect_has "header has Exit"      "Exit:"    "$hdr"
expect_has "header has Examples"  "xamples"  "$hdr"

# ── --help / -h ──────────────────────────────────────────────────────────────
echo "-- help --"
PATH="$NO_DOCKER_PATH" bash "$V" --help >/dev/null 2>&1; expect_exit "--help exits 0" 0 $?
PATH="$NO_DOCKER_PATH" bash "$V" -h     >/dev/null 2>&1; expect_exit "-h exits 0"     0 $?
out="$(PATH="$NO_DOCKER_PATH" bash "$V" --help 2>/dev/null)"
expect_has "--help lists --tag"      "--tag"      "$out"
expect_has "--help lists --registry" "--registry" "$out"
expect_has "--help lists --push"     "--push"     "$out"
expect_has "--help lists --dry-run"  "--dry-run"  "$out"
expect_has "--help documents exit 2" "2"          "$out"
expect_has "--help documents exit 5" "5"          "$out"
rm -f "$SB/docker.log"
PATH="$NO_DOCKER_PATH" DOCKER_SENTINEL_LOG="$SB/docker.log" bash "$V" --help >/dev/null 2>&1
no_docker_calls && ok "--help invokes no docker" || no "--help invoked docker"

# ── usage errors (exit 2) ────────────────────────────────────────────────────
echo "-- usage errors --"
PATH="$NO_DOCKER_PATH" bash "$V" --bogus >/dev/null 2>&1; expect_exit "unknown flag -> 2" 2 $?
PATH="$NO_DOCKER_PATH" bash "$V" --tag   >/dev/null 2>&1; expect_exit "missing --tag value -> 2" 2 $?
PATH="$NO_DOCKER_PATH" bash "$V" --registry >/dev/null 2>&1; expect_exit "missing --registry value -> 2" 2 $?
rm -f "$SB/docker.log"
PATH="$NO_DOCKER_PATH" DOCKER_SENTINEL_LOG="$SB/docker.log" bash "$V" --bogus >/dev/null 2>&1
no_docker_calls && ok "arg-parse error invokes no docker" || no "arg-parse error invoked docker"

# ── arg parsing + resolution via --dry-run (no docker) ───────────────────────
echo "-- dry-run resolution --"
rm -f "$SB/docker.log"
out="$(PATH="$NO_DOCKER_PATH" DOCKER_SENTINEL_LOG="$SB/docker.log" \
       IMAGE_NAME=myapp bash "$V" --dry-run --tag v1 --registry ghcr.io/acme 2>/dev/null)"; rc=$?
expect_exit "dry-run exits 0" 0 "$rc"
expect_has "resolves full image"    "Image: ghcr.io/acme/myapp:v1" "$out"
expect_has "default dockerfile"     "Dockerfile: Dockerfile"      "$out"
expect_has "default context"        "Context: ."                  "$out"
expect_has "push flag shown false"  "Push: false"                 "$out"
no_docker_calls && ok "dry-run invokes no docker" || no "dry-run invoked docker"

out="$(PATH="$NO_DOCKER_PATH" IMAGE_NAME=svc bash "$V" --dry-run --push --tag dev 2>/dev/null)"
expect_has "no registry -> bare image" "Image: svc:dev"      "$out"
expect_has "push flag shown true"      "Push: true"          "$out"
expect_has "plan includes build"       "docker build -t svc:dev -f Dockerfile ." "$out"
expect_has "plan includes push"        "docker push svc:dev" "$out"

out="$(PATH="$NO_DOCKER_PATH" IMAGE_NAME=app bash "$V" --dry-run \
       --dockerfile Dockerfile.prod --context ./builds/app 2>/dev/null)"
expect_has "--dockerfile honoured" "Dockerfile: Dockerfile.prod" "$out"
expect_has "--context honoured"    "Context: ./builds/app"       "$out"

# ── stream separation: banners on stderr, data on stdout ─────────────────────
echo "-- stream separation --"
err="$(PATH="$NO_DOCKER_PATH" IMAGE_NAME=x bash "$V" --dry-run 2>&1 1>/dev/null)"
expect_has "banner on stderr" "===" "$err"
dat="$(PATH="$NO_DOCKER_PATH" IMAGE_NAME=x bash "$V" --dry-run 2>/dev/null)"
case "$dat" in
    *"==="*) no "stdout leaked a banner";;
    *)       ok "stdout carries only data lines";;
esac

# ── happy-path DATA preserved pre/post (only chatter/help moved) ─────────────
echo "-- data preservation (pre/post) --"
# Captured baseline = the pre-backfill happy-path stdout data lines. These must
# stay byte-identical so downstream parsers are unaffected.
BASELINE=$'Image: ghcr.io/acme/myapp:v1\nDockerfile: Dockerfile\nContext: .'
new_data="$(PATH="$NO_DOCKER_PATH" IMAGE_NAME=myapp bash "$V" --dry-run \
            --tag v1 --registry ghcr.io/acme 2>/dev/null \
            | grep -E '^(Image|Dockerfile|Context): ')"
[[ "$new_data" == "$BASELINE" ]] \
    && ok "data lines match captured baseline" \
    || { no "data lines match captured baseline"; printf '  got:\n%s\n' "$new_data" >&2; }

# Live pre/post diff against the actual pre-backfill blob, when reachable.
if OLD_SRC="$(git -C "$SKILL/../../.." cat-file -p "$OLD_BLOB" 2>/dev/null)"; then
    printf '%s' "$OLD_SRC" > "$SB/old-build-push.sh"
    old_data="$(cd "$SB" && PATH="$NO_DOCKER_PATH" DOCKER_SENTINEL_LOG="$SB/old-docker.log" \
                IMAGE_NAME=myapp bash "$SB/old-build-push.sh" --tag v1 --registry ghcr.io/acme 2>/dev/null \
                | grep -E '^(Image|Dockerfile|Context): ')"
    if [[ -n "$old_data" && "$old_data" == "$new_data" ]]; then
        ok "pre/post data identical (live diff vs old blob)"
    else
        no "pre/post data identical (live diff vs old blob)"
    fi
else
    echo "  SKIP  live pre/post diff (old blob $OLD_BLOB not reachable)"
fi

echo ""
echo "=== $PASS passed, $FAIL failed ==="
[[ "$FAIL" -eq 0 ]] || exit 1
exit 0
