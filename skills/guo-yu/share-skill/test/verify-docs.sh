#!/bin/bash
#
# share-skill Documentation Verification Script
# 验证生成的文档系统是否符合 SKILL.md 定义
#
# Usage:
#   ./share-skill/test/verify-docs.sh [repo-path]
#
# Example:
#   ./share-skill/test/verify-docs.sh ~/Codes/skills
#   ./share-skill/test/verify-docs.sh .
#

# Don't use set -e as arithmetic operations can return non-zero

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Repository path (default to current directory)
REPO_PATH="${1:-.}"

# Resolve to absolute path
REPO_PATH=$(cd "$REPO_PATH" && pwd)

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     share-skill Documentation Verification Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Repository: ${YELLOW}$REPO_PATH${NC}"
echo ""

# Helper functions
pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    PASS=$((PASS + 1))
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    FAIL=$((FAIL + 1))
}

warn() {
    echo -e "  ${YELLOW}⚠${NC} $1"
    WARN=$((WARN + 1))
}

section() {
    echo ""
    echo -e "${BLUE}── $1 ──${NC}"
}

check_file_exists() {
    local file="$1"
    local desc="$2"
    if [ -f "$file" ]; then
        pass "$desc exists"
        return 0
    else
        fail "$desc missing: $file"
        return 1
    fi
}

check_contains() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        pass "$desc"
        return 0
    else
        fail "$desc"
        return 1
    fi
}

check_contains_regex() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    if grep -E "$pattern" "$file" >/dev/null 2>&1; then
        pass "$desc"
        return 0
    else
        fail "$desc"
        return 1
    fi
}

# ============================================================
# 1. Check Directory Structure
# ============================================================
section "1. Directory Structure"

check_file_exists "$REPO_PATH/docs/index.html" "docs/index.html"
check_file_exists "$REPO_PATH/docs/js/main.js" "docs/js/main.js"
check_file_exists "$REPO_PATH/docs/css/custom.css" "docs/css/custom.css"

if [ -f "$REPO_PATH/docs/CNAME" ]; then
    pass "docs/CNAME exists (custom domain configured)"
else
    warn "docs/CNAME not found (no custom domain)"
fi

# ============================================================
# 2. Check index.html Structure
# ============================================================
section "2. index.html Structure"

INDEX_FILE="$REPO_PATH/docs/index.html"

if [ -f "$INDEX_FILE" ]; then
    # 2.1 Favicon
    check_contains "$INDEX_FILE" 'id="favicon"' "Favicon element with id='favicon'"

    # 2.2 Navbar brand with repo link
    check_contains "$INDEX_FILE" 'id="repoLink"' "Navbar brand with id='repoLink'"
    check_contains "$INDEX_FILE" 'target="_blank"' "Repo link opens in new tab"
    check_contains "$INDEX_FILE" 'id="userAvatar"' "User avatar element"
    check_contains "$INDEX_FILE" 'id="brandTitle"' "Brand title element"

    # 2.3 Three-column layout
    check_contains "$INDEX_FILE" 'three-column' "Three-column layout class"
    check_contains "$INDEX_FILE" 'sidebar-right' "Right sidebar element"
    check_contains "$INDEX_FILE" 'class="sidebar' "Left sidebar element"

    # 2.4 Language switcher
    check_contains "$INDEX_FILE" 'data-lang="en"' "English language button"
    check_contains "$INDEX_FILE" 'data-lang="zh-CN"' "Chinese language button"
    check_contains "$INDEX_FILE" 'data-lang="ja"' "Japanese language button"

    # 2.5 Installation section
    check_contains "$INDEX_FILE" 'data-i18n="installation"' "Installation section with i18n"
    check_contains "$INDEX_FILE" '/plugin marketplace add' "Plugin marketplace command"
    check_contains "$INDEX_FILE" '/plugin install' "Plugin install command"

    # 2.6 Table of Contents
    check_contains "$INDEX_FILE" 'js-toc' "Tocbot container (js-toc)"
    check_contains "$INDEX_FILE" 'js-toc-content' "Tocbot content container"
    check_contains "$INDEX_FILE" 'tocbot' "Tocbot library included"

    # 2.7 Code highlighting
    check_contains "$INDEX_FILE" 'highlight.js' "Highlight.js library included"

    # 2.8 Footer
    check_contains "$INDEX_FILE" 'class="footer"' "Footer element"
    check_contains "$INDEX_FILE" 'skill.guoyu.me' "Footer link to skill.guoyu.me"

    # 2.9 Version numbers on assets
    check_contains_regex "$INDEX_FILE" 'custom\.css\?v=[0-9]+' "CSS has version number"
    check_contains_regex "$INDEX_FILE" 'main\.js\?v=[0-9]+' "JS has version number"
fi

# ============================================================
# 3. Check main.js Configuration
# ============================================================
section "3. main.js Configuration"

MAIN_JS="$REPO_PATH/docs/js/main.js"

if [ -f "$MAIN_JS" ]; then
    # 3.1 Repository configuration
    check_contains "$MAIN_JS" 'REPO_OWNER' "REPO_OWNER constant defined"
    check_contains "$MAIN_JS" 'REPO_NAME' "REPO_NAME constant defined"
    check_contains "$MAIN_JS" 'BRANCH' "BRANCH constant defined"

    # 3.2 Cache busting
    check_contains "$MAIN_JS" 'CACHE_VERSION' "CACHE_VERSION constant defined"
    check_contains "$MAIN_JS" 'Date.now()' "Cache version uses Date.now()"

    # 3.3 i18n translations
    check_contains "$MAIN_JS" 'I18N' "I18N translations object"
    check_contains "$MAIN_JS" "'zh-CN'" "Chinese translations included"
    check_contains "$MAIN_JS" "installation:" "Installation i18n key"
    check_contains "$MAIN_JS" "installDesc:" "Install description i18n key"
    check_contains "$MAIN_JS" "addMarketplace:" "Add marketplace i18n key"

    # 3.4 Dynamic features
    check_contains "$MAIN_JS" "getElementById('favicon')" "Favicon dynamic setting"
    check_contains "$MAIN_JS" "getElementById('repoLink')" "Repo link dynamic setting"
    check_contains "$MAIN_JS" 'avatar_url' "Avatar URL usage"

    # 3.5 getBasePath with cache busting
    check_contains "$MAIN_JS" 'getBasePath' "getBasePath function defined"
    check_contains "$MAIN_JS" '?v=' "Cache busting in URL"

    # 3.6 Tocbot initialization
    check_contains "$MAIN_JS" 'tocbot.init' "Tocbot initialization"
    check_contains "$MAIN_JS" 'tocSelector' "Tocbot tocSelector config"

    # 3.7 Highlight.js
    check_contains "$MAIN_JS" 'hljs.highlightElement' "Highlight.js usage"
fi

# ============================================================
# 4. Check README Files
# ============================================================
section "4. README Files"

# 4.1 Check all language versions exist
check_file_exists "$REPO_PATH/README.md" "README.md (English)"
check_file_exists "$REPO_PATH/README.zh-CN.md" "README.zh-CN.md (Chinese)"
check_file_exists "$REPO_PATH/README.ja.md" "README.ja.md (Japanese)"

# 4.2 Check language navigation in each README
for readme in "$REPO_PATH/README.md" "$REPO_PATH/README.zh-CN.md" "$REPO_PATH/README.ja.md"; do
    if [ -f "$readme" ]; then
        filename=$(basename "$readme")
        check_contains "$readme" 'href="README.md"' "$filename has English link"
        check_contains "$readme" 'href="README.zh-CN.md"' "$filename has Chinese link"
        check_contains "$readme" 'href="README.ja.md"' "$filename has Japanese link"
    fi
done

# 4.3 Check footer attribution
for readme in "$REPO_PATH/README.md" "$REPO_PATH/README.zh-CN.md" "$REPO_PATH/README.ja.md"; do
    if [ -f "$readme" ]; then
        filename=$(basename "$readme")
        check_contains "$readme" 'skill.guoyu.me' "$filename has footer link"
    fi
done

# ============================================================
# 5. Check Skill SKILL.md Files (if in skills repo)
# ============================================================
section "5. Skill Documentation Files"

# Find all skill directories
SKILL_DIRS=$(find "$REPO_PATH" -maxdepth 1 -type d ! -name "docs" ! -name ".*" ! -name "node_modules" ! -path "$REPO_PATH" 2>/dev/null)

for skill_dir in $SKILL_DIRS; do
    skill_name=$(basename "$skill_dir")

    # Skip if not a skill directory (no SKILL.md)
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        continue
    fi

    echo -e "  ${YELLOW}Skill: $skill_name${NC}"

    # Check SKILL.md exists
    check_file_exists "$skill_dir/SKILL.md" "  $skill_name/SKILL.md"

    # Check translated versions
    if [ -f "$skill_dir/SKILL.zh-CN.md" ]; then
        pass "  $skill_name/SKILL.zh-CN.md exists"
    else
        warn "  $skill_name/SKILL.zh-CN.md missing (optional)"
    fi

    if [ -f "$skill_dir/SKILL.ja.md" ]; then
        pass "  $skill_name/SKILL.ja.md exists"
    else
        warn "  $skill_name/SKILL.ja.md missing (optional)"
    fi
done

# ============================================================
# 6. Check Skills Configuration in main.js
# ============================================================
section "6. Skills Configuration"

if [ -f "$MAIN_JS" ]; then
    # Check if SKILLS object contains entries for each skill
    for skill_dir in $SKILL_DIRS; do
        skill_name=$(basename "$skill_dir")

        if [ ! -f "$skill_dir/SKILL.md" ]; then
            continue
        fi

        if grep -q "'$skill_name'" "$MAIN_JS" 2>/dev/null; then
            pass "Skill '$skill_name' configured in main.js"
        else
            fail "Skill '$skill_name' missing from SKILLS config in main.js"
        fi
    done
fi

# ============================================================
# 7. Check share-skill Config File
# ============================================================
section "7. share-skill Config File"

CONFIG_FILE="$HOME/.claude/share-skill-config.json"

if [ -f "$CONFIG_FILE" ]; then
    pass "Config file exists: ~/.claude/share-skill-config.json"

    # 7.1 Check required config fields
    check_contains "$CONFIG_FILE" '"code_root"' "Config has code_root field"
    check_contains "$CONFIG_FILE" '"skills_repo"' "Config has skills_repo field"
    check_contains "$CONFIG_FILE" '"github_username"' "Config has github_username field"
    check_contains "$CONFIG_FILE" '"remotes"' "Config has remotes field"
    check_contains "$CONFIG_FILE" '"default_remote"' "Config has default_remote field"

    # 7.2 Check docs config
    check_contains "$CONFIG_FILE" '"docs"' "Config has docs section"
    check_contains "$CONFIG_FILE" '"style"' "Config has docs.style field"
    check_contains "$CONFIG_FILE" '"custom_domain"' "Config has docs.custom_domain field"
else
    warn "Config file not found: ~/.claude/share-skill-config.json (will be auto-created on first run)"
fi

# ============================================================
# 8. Check Dynamic Footer URL Logic
# ============================================================
section "8. Dynamic Footer URL"

if [ -f "$MAIN_JS" ]; then
    # Check for getDocsUrl function
    check_contains "$MAIN_JS" 'getDocsUrl' "getDocsUrl function defined"

    # Check for CUSTOM_DOMAIN usage or github.io fallback
    if grep -q 'CUSTOM_DOMAIN' "$MAIN_JS" 2>/dev/null || grep -q 'github.io' "$MAIN_JS" 2>/dev/null; then
        pass "Dynamic URL logic (CUSTOM_DOMAIN or github.io)"
    else
        warn "Dynamic URL logic not found (may use static URL)"
    fi
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                        Summary                              ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASS"
echo -e "  ${RED}Failed:${NC}  $FAIL"
echo -e "  ${YELLOW}Warnings:${NC} $WARN"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All required checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review the output above.${NC}"
    exit 1
fi
