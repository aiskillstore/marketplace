#!/bin/bash

# Source 1: Camel Spring Boot BOM (versions < 4.15.0)
SB_URL="https://repo.maven.apache.org/maven2/org/apache/camel/springboot/spring-boot"
# Source 2: Camel Parent POM (versions >= 4.15.0) — also used for CXF version for all 4.x
PARENT_URL="https://repo.maven.apache.org/maven2/org/apache/camel/camel-parent"
# Spring Boot starter directory (for SB release dates)
SB_STARTER_URL="https://repo.maven.apache.org/maven2/org/springframework/boot/spring-boot-starter"

# Cutover version: from 4.15.0 onwards use camel-parent for spring-boot-version
CUTOVER="4.15.0"

RELEASES_URL="https://camel.apache.org/releases/"

MIN_VERSION="${1:-3.0.0}"
MAX_VERSION="${2:-99.99.99}"
OUTPUT_MD="target/camel-springboot-matrix.md"

ver_to_int() {
	echo "$1" | awk -F. '{ printf "%d%03d%03d", $1, $2, $3 }'
}

# Extract a single property value from POM XML
extract_property() {
	local pom="$1" tag="$2"
	echo "$pom" | grep -o "<${tag}>[^<]*</${tag}>" | grep -o '>[^<]*<' | tr -d '><'
}

# Parse "version date" pairs from a Maven directory listing HTML
# Each line looks like:  <a href="3.0.0/">3.0.0/</a>   2019-11-24 23:00  -
parse_dates_from_listing() {
	grep -E 'href="[0-9]+\.[0-9]+\.[0-9]+/"' |
		sed -n 's/.*href="\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)\/".* \([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\).*/\1 \2/p'
}

MIN_INT=$(ver_to_int "$MIN_VERSION")
MAX_INT=$(ver_to_int "$MAX_VERSION")
CUTOVER_INT=$(ver_to_int "$CUTOVER")

# ── Fetch metadata pages (each fetched only once) ──────────────────────────

echo "Fetching release metadata from $RELEASES_URL ..."
RELEASES_PAGE=$(curl -sf "$RELEASES_URL")
[ -z "$RELEASES_PAGE" ] && echo "WARNING: Could not fetch $RELEASES_URL — LTS/type columns will be empty"

echo "Fetching Camel date index (< $CUTOVER) ..."
CAMEL_DATES_OLD=$(curl -sf "$SB_URL/" | parse_dates_from_listing)

echo "Fetching Camel date index (>= $CUTOVER) ..."
CAMEL_DATES_NEW=$(curl -sf "$PARENT_URL/" | parse_dates_from_listing)

CAMEL_DATES=$(printf "%s\n%s" "$CAMEL_DATES_OLD" "$CAMEL_DATES_NEW" | grep -v '^$')

echo "Fetching Spring Boot date index from $SB_STARTER_URL ..."
SPRINGBOOT_DATES=$(curl -sf "$SB_STARTER_URL/" | parse_dates_from_listing)

# ── Lookup helpers ─────────────────────────────────────────────────────────

# Map each release version to LTS / non-LTS from the release description.
# The releases page marks LTS releases explicitly ("... LTS release X.Y.Z");
# every other release is not LTS.
RELEASE_TYPES=$(echo "$RELEASES_PAGE" |
	grep -oiE 'releases-desc">[^<]*' |
	sed -E 's/.*releases-desc">//' |
	awk 'match($0, /[0-9]+\.[0-9]+\.[0-9]+/) {
		v = substr($0, RSTART, RLENGTH)
		print v, ($0 ~ /LTS/ ? "LTS" : "non-LTS")
	}')

get_release_type() {
	echo "$RELEASE_TYPES" | awk -v v="$1" '$1 == v { print $2; exit }'
}

get_camel_date() {
	echo "$CAMEL_DATES" | awk -v v="$1" '$1 == v { print $2; exit }'
}

get_sb_date() {
	echo "$SPRINGBOOT_DATES" | awk -v v="$1" '$1 == v { print $2; exit }'
}

# ── Fetch version lists ────────────────────────────────────────────────────

fetch_versions() {
	local url="$1"
	curl -sf "$url/" |
		grep -oE 'href="[0-9]+\.[0-9]+\.[0-9]+/"' |
		grep -oE '[0-9]+\.[0-9]+\.[0-9]+' |
		sort -V |
		while read -r v; do
			v_int=$(ver_to_int "$v")
			if [ "$v_int" -ge "$MIN_INT" ] && [ "$v_int" -le "$MAX_INT" ]; then
				echo "$v"
			fi
		done
}

echo "Fetching Camel version lists..."

VERSIONS_OLD=$(fetch_versions "$SB_URL" | while read -r v; do
	[ "$(ver_to_int "$v")" -lt "$CUTOVER_INT" ] && echo "$v"
done)

VERSIONS_NEW=$(fetch_versions "$PARENT_URL" | while read -r v; do
	[ "$(ver_to_int "$v")" -ge "$CUTOVER_INT" ] && echo "$v"
done)

ALL_VERSIONS=$(printf "%s\n%s" "$VERSIONS_OLD" "$VERSIONS_NEW" | grep -v '^$' | sort -V)

if [ -z "$ALL_VERSIONS" ]; then
	echo "ERROR: No versions found in range $MIN_VERSION - $MAX_VERSION"
	exit 1
fi

VERSION_COUNT=$(echo "$ALL_VERSIONS" | wc -l | tr -d ' ')
echo "Found $VERSION_COUNT versions. Fetching POM files..."
echo ""

# ── Write Markdown header ──────────────────────────────────────────────────

mkdir -p "$(dirname "$OUTPUT_MD")"

SOURCE_URL="https://stackoverflow.com/questions/68087511/compatibility-of-camel-springboot-and-spring-boot"

{
	echo "# Camel Spring Boot Compatibility Matrix"
	echo ""
	echo "- Generated: $(date '+%Y-%m-%d %H:%M:%S')"
	echo "- Cutover: $CUTOVER"
	echo ""
	echo "## Sources"
	echo ""
	echo "- Spring Boot compatibility rules: $SOURCE_URL"
	echo "- LTS and release type info: $RELEASES_URL"
	echo "- Camel release dates (versions < $CUTOVER): $SB_URL"
	echo "- Camel release dates (versions >= $CUTOVER): $PARENT_URL"
	echo "- Spring Boot release dates: $SB_STARTER_URL"
	echo "- Apache CXF version: $PARENT_URL (camel-parent POM, property \`<cxf-version>\`)"
	echo ""
	echo "## POM Sources"
	echo ""
	echo "- Spring Boot version, versions < $CUTOVER: $SB_URL"
	echo "- Spring Boot version + CXF version, versions >= $CUTOVER: $PARENT_URL"
	echo "- CXF version, versions < $CUTOVER: $PARENT_URL (fetched additionally)"
	echo ""
	echo "## Matrix"
	echo ""
	echo "| Camel Version | Type | Camel Release Date | Spring Boot Version | Spring Boot Release Date | CXF Version | CXF POM | Spring Boot POM |"
	echo "| --- | --- | --- | --- | --- | --- | --- | --- |"
} >"$OUTPUT_MD"

printf "%-18s | %-6s | %-12s | %-20s | %-12s | %-12s | %s\n" \
	"Camel Version" "Type" "Camel Date" "Spring Boot Version" "SB Date" "CXF Version" "POM URL"
printf "%s\n" "$(printf '%0.s-' {1..130})"

# ── Main loop ─────────────────────────────────────────────────────────────

i=0
while IFS= read -r VERSION; do
	[ -z "$VERSION" ] && continue
	i=$((i + 1))
	printf "[%d/%d] %-15s\r" "$i" "$VERSION_COUNT" "$VERSION" >&2

	v_int=$(ver_to_int "$VERSION")
	if [ "$v_int" -lt "$CUTOVER_INT" ]; then
		SB_POM_URL="$SB_URL/$VERSION/spring-boot-$VERSION.pom"
		SB_POM=$(curl -sf "$SB_POM_URL" 2>/dev/null)
		# CXF version always comes from camel-parent
		CXF_POM_URL="$PARENT_URL/$VERSION/camel-parent-$VERSION.pom"
		CXF_POM=$(curl -sf "$CXF_POM_URL" 2>/dev/null)
	else
		SB_POM_URL="$PARENT_URL/$VERSION/camel-parent-$VERSION.pom"
		SB_POM=$(curl -sf "$SB_POM_URL" 2>/dev/null)
		# Same POM contains both spring-boot-version and cxf-version
		CXF_POM_URL="$SB_POM_URL"
		CXF_POM="$SB_POM"
	fi

	SB_VERSION=$(extract_property "$SB_POM" "spring-boot-version")
	[ -z "$SB_VERSION" ] && SB_VERSION="N/A"

	CXF_VERSION=$(extract_property "$CXF_POM" "cxf-version")
	[ -z "$CXF_VERSION" ] && CXF_VERSION="N/A"

	REL_TYPE=$(get_release_type "$VERSION")
	[ -z "$REL_TYPE" ] && REL_TYPE="non-LTS"

	CAMEL_DATE=$(get_camel_date "$VERSION")
	[ -z "$CAMEL_DATE" ] && CAMEL_DATE="?"

	SB_DATE=$(get_sb_date "$SB_VERSION")
	[ -z "$SB_DATE" ] && SB_DATE="?"

	echo "| $VERSION | $REL_TYPE | $CAMEL_DATE | $SB_VERSION | $SB_DATE | $CXF_VERSION | [POM]($CXF_POM_URL) | [POM]($SB_POM_URL) |" >>"$OUTPUT_MD"
	printf "%-18s | %-6s | %-12s | %-20s | %-12s | %-12s | %s\n" \
		"$VERSION" "$REL_TYPE" "$CAMEL_DATE" "$SB_VERSION" "$SB_DATE" "$CXF_VERSION" "$SB_POM_URL"

	sleep 0.05
done <<<"$ALL_VERSIONS"

echo ""
echo "Matrix saved to: $OUTPUT_MD"
