#!/bin/bash
# Multi-skill processing script for process-submission workflow
# This script discovers and processes ALL skills in a repository

set -euo pipefail

# Required environment variables
WORK_DIR="${WORK_DIR:?WORK_DIR is required}"
SKILL_PATH="${SKILL_PATH:-}"
AI_API_BASE="${AI_API_BASE:?AI_API_BASE is required}"
AI_MODEL="${AI_MODEL:?AI_MODEL is required}"
SOURCE_URL="${SOURCE_URL:?SOURCE_URL is required}"
GITHUB_OUTPUT="${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}"

# Determine search directory
if [ -n "$SKILL_PATH" ]; then
  SEARCH_DIR="$WORK_DIR/source-repo/$SKILL_PATH"
else
  SEARCH_DIR="$WORK_DIR/source-repo"
fi

echo "============================================"
echo "Multi-Skill Discovery & Processing"
echo "============================================"
echo "Search directory: $SEARCH_DIR"
echo "Source URL: $SOURCE_URL"

# Discover ALL SKILL.md files (NO head -1!)
find "$SEARCH_DIR" -maxdepth 10 -name "SKILL.md" -type f | sort > "$WORK_DIR/all-skills.txt"
SKILL_COUNT=$(wc -l < "$WORK_DIR/all-skills.txt" | tr -d ' ')

if [ "$SKILL_COUNT" -eq 0 ]; then
  echo "::error::No SKILL.md found in repository"
  exit 1
fi

echo "Found $SKILL_COUNT skill(s):"
cat "$WORK_DIR/all-skills.txt"

# Initialize manifest
echo "[]" > "$WORK_DIR/skills-manifest.json"

# Build skills manifest
while IFS= read -r skill_md_path; do
  [ -z "$skill_md_path" ] && continue
  
  SKILL_DIR=$(dirname "$skill_md_path")
  
  # Extract name from frontmatter
  FRONTMATTER_NAME=$(sed -n '/^---$/,/^---$/p' "$skill_md_path" 2>/dev/null | grep -E '^name:' | head -1 | sed 's/^name:[[:space:]]*//' | tr -d '"'"'" | xargs || true)
  
  if [ -n "$FRONTMATTER_NAME" ]; then
    SLUG=$(echo "$FRONTMATTER_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//')
  else
    SLUG=$(basename "$SKILL_DIR" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
  fi
  
  echo "  - $SLUG: $SKILL_DIR"
  
  jq --arg slug "$SLUG" --arg dir "$SKILL_DIR" '. + [{"slug": $slug, "dir": $dir}]' \
    "$WORK_DIR/skills-manifest.json" > "$WORK_DIR/tmp.json" && mv "$WORK_DIR/tmp.json" "$WORK_DIR/skills-manifest.json"
done < "$WORK_DIR/all-skills.txt"

echo ""
echo "Skills manifest:"
cat "$WORK_DIR/skills-manifest.json"

# Output skill count
echo "skill_count=$SKILL_COUNT" >> "$GITHUB_OUTPUT"

# Determine trust level
IS_OFFICIAL="false"
TRUST_LEVEL="COMMUNITY"
if [[ "$SOURCE_URL" == *"github.com/anthropics/skills"* ]]; then
  IS_OFFICIAL="true"
  TRUST_LEVEL="OFFICIAL"
fi

echo ""
echo "Trust level: $TRUST_LEVEL"

# Initialize tracking files
touch "$WORK_DIR/processed-skills.txt"
touch "$WORK_DIR/blocked-skills.txt"
touch "$WORK_DIR/risk-levels.txt"

# Build response schema and write to file (avoids jq --argjson escaping issues)
cat > "$WORK_DIR/response-schema.json" << 'SCHEMA_EOF'
{"type":"json_schema","json_schema":{"name":"audit","strict":true,"schema":{"type":"object","required":["security_audit","content"],"additionalProperties":false,"properties":{"security_audit":{"type":"object","required":["risk_level","should_block","safe_to_publish","summary"],"additionalProperties":false,"properties":{"risk_level":{"type":"string","enum":["safe","low","medium","high","critical"]},"should_block":{"type":"boolean"},"safe_to_publish":{"type":"boolean"},"summary":{"type":"string"},"critical_findings":{"type":"array","items":{"type":"object","properties":{"locations":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line_start":{"type":"integer"},"line_end":{"type":"integer"}},"required":["file","line_start","line_end"],"additionalProperties":false}},"title":{"type":"string"},"description":{"type":"string"}},"required":["locations","title","description"],"additionalProperties":false}},"high_findings":{"type":"array","items":{"type":"object","properties":{"locations":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line_start":{"type":"integer"},"line_end":{"type":"integer"}},"required":["file","line_start","line_end"],"additionalProperties":false}},"title":{"type":"string"},"description":{"type":"string"}},"required":["locations","title","description"],"additionalProperties":false}},"medium_findings":{"type":"array","items":{"type":"object","properties":{"locations":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line_start":{"type":"integer"},"line_end":{"type":"integer"}},"required":["file","line_start","line_end"],"additionalProperties":false}},"title":{"type":"string"},"description":{"type":"string"}},"required":["locations","title","description"],"additionalProperties":false}},"low_findings":{"type":"array","items":{"type":"object","properties":{"locations":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line_start":{"type":"integer"},"line_end":{"type":"integer"}},"required":["file","line_start","line_end"],"additionalProperties":false}},"title":{"type":"string"},"description":{"type":"string"}},"required":["locations","title","description"],"additionalProperties":false}},"files_analyzed":{"type":"integer"},"dangerous_patterns_found":{"type":"array","items":{"type":"string"}}}},"content":{"type":"object","additionalProperties":false,"properties":{"user_title":{"type":"string"},"value_statement":{"type":"string"},"seo_keywords":{"type":"array","items":{"type":"string"}},"actual_capabilities":{"type":"array","items":{"type":"string"}},"limitations":{"type":"array","items":{"type":"string"}},"use_cases":{"type":"array","items":{"type":"object","properties":{"target_user":{"type":"string"},"title":{"type":"string"},"description":{"type":"string"}},"required":["target_user","title","description"],"additionalProperties":false}},"prompt_templates":{"type":"array","items":{"type":"object","properties":{"title":{"type":"string"},"scenario":{"type":"string"},"prompt":{"type":"string"}},"required":["title","scenario","prompt"],"additionalProperties":false}},"output_examples":{"type":"array","items":{"type":"object","properties":{"input":{"type":"string"},"output":{"type":"array","items":{"type":"string"}}},"required":["input","output"],"additionalProperties":false}},"best_practices":{"type":"array","items":{"type":"string"}},"anti_patterns":{"type":"array","items":{"type":"string"}},"faq":{"type":"array","items":{"type":"object","properties":{"question":{"type":"string"},"answer":{"type":"string"}},"required":["question","answer"],"additionalProperties":false}},"technical_requirements":{"type":"object","additionalProperties":false,"properties":{"dependencies":{"type":"array","items":{"type":"string"}},"permissions_needed":{"type":"array","items":{"type":"string"}},"estimated_complexity":{"type":"string","enum":["low","medium","high"]},"setup_time_minutes":{"type":"integer"}},"required":["dependencies","permissions_needed","estimated_complexity","setup_time_minutes"]}},"required":["user_title","value_statement","seo_keywords","actual_capabilities","limitations","use_cases","prompt_templates","output_examples","best_practices","anti_patterns","faq","technical_requirements"]}}}}}
SCHEMA_EOF

# Process each skill
jq -c '.[]' "$WORK_DIR/skills-manifest.json" | while read -r skill_entry; do
  SLUG=$(echo "$skill_entry" | jq -r '.slug')
  SKILL_DIR=$(echo "$skill_entry" | jq -r '.dir')
  
  echo ""
  echo "=========================================="
  echo "Processing: $SLUG"
  echo "Directory: $SKILL_DIR"
  echo "=========================================="
  
  # Collect files
  FILE_CONTENTS=""
  TOTAL_LINES=0
  FILE_COUNT=0
  
  while IFS= read -r file; do
    if [ -f "$file" ]; then
      REL_PATH="${file#$SKILL_DIR/}"
      EXT="${file##*.}"
      LINES=$(wc -l < "$file" 2>/dev/null || echo "0")
      TOTAL_LINES=$((TOTAL_LINES + LINES))
      FILE_COUNT=$((FILE_COUNT + 1))
      CONTENT=$(head -c 30000 "$file")
      FILE_CONTENTS="${FILE_CONTENTS}

=== File: ${REL_PATH} (${LINES} lines) ===
${CONTENT}
"
    fi
  done < <(find "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.sh" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) -size -50k 2>/dev/null | head -20)
  
  echo "Collected $FILE_COUNT files ($TOTAL_LINES lines)"
  
  # Build audit prompt
  if [ "$IS_OFFICIAL" = "true" ]; then
    TRUST_SECTION="OFFICIAL SKILL - TRUSTED SOURCE. Set risk_level=safe, should_block=false."
  else
    TRUST_SECTION="COMMUNITY SKILL - FULL SECURITY AUDIT REQUIRED."
  fi
  
  AUDIT_PROMPT="Audit skill: $SLUG | Repo: $SOURCE_URL | Trust: $TRUST_LEVEL | Files: $FILE_COUNT

SOURCE CODE:
$FILE_CONTENTS

Return JSON with security_audit (risk_level, should_block, safe_to_publish, summary, findings arrays) and content (user_title, value_statement, seo_keywords with Claude, capabilities, limitations, use_cases, prompt_templates, output_examples, best_practices, anti_patterns, faq, technical_requirements).
$TRUST_SECTION"
  
  # Build request using --slurpfile to safely read the schema JSON
  REQUEST_BODY=$(jq -n \
    --arg model "$AI_MODEL" \
    --arg content "$AUDIT_PROMPT" \
    --slurpfile response_format "$WORK_DIR/response-schema.json" \
    '{model: $model, messages: [{role: "user", content: $content}], temperature: 0.3, max_tokens: 100000, response_format: $response_format[0]}')
  
  echo "Calling AI API..."
  RESPONSE=$(curl -s --max-time 300 "$AI_API_BASE/chat/completions" -H "Content-Type: application/json" -d "$REQUEST_BODY" || echo '{}')
  
  AI_CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')
  
  if [ -z "$AI_CONTENT" ]; then
    echo "AI unavailable, using fallback"
    AI_CONTENT='{"security_audit":{"risk_level":"medium","should_block":false,"safe_to_publish":true,"summary":"AI unavailable","critical_findings":[],"high_findings":[],"medium_findings":[],"low_findings":[],"files_analyzed":0,"dangerous_patterns_found":[]},"content":{"user_title":"Skill","value_statement":"A Claude skill.","seo_keywords":["Claude"],"actual_capabilities":[],"limitations":[],"use_cases":[],"prompt_templates":[],"output_examples":[],"best_practices":[],"anti_patterns":[],"faq":[],"technical_requirements":{"dependencies":[],"permissions_needed":[],"estimated_complexity":"medium","setup_time_minutes":5}}}'
  fi
  
  CLEAN_JSON=$(echo "$AI_CONTENT" | sed 's/^```json//g' | sed 's/^```//g' | sed 's/```$//g')
  RISK_LEVEL=$(echo "$CLEAN_JSON" | jq -r '.security_audit.risk_level // "unknown"')
  SHOULD_BLOCK=$(echo "$CLEAN_JSON" | jq -r '.security_audit.should_block // false')
  
  echo "Result: risk=$RISK_LEVEL, block=$SHOULD_BLOCK"
  echo "$RISK_LEVEL" >> "$WORK_DIR/risk-levels.txt"
  
  # Build skill report
  jq -n \
    --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg model "$AI_MODEL" \
    --arg source_url "$SOURCE_URL" \
    --arg source_ref "$(cd "$WORK_DIR/source-repo" && git rev-parse HEAD)" \
    --argjson ai_result "$CLEAN_JSON" \
    --argjson total_lines "$TOTAL_LINES" \
    --argjson file_count "$FILE_COUNT" \
    '{meta:{generated_at:$generated_at,model:$model,source_url:$source_url,source_ref:$source_ref,analysis_version:"2.0.0"},security_audit:($ai_result.security_audit+{files_scanned:$file_count,total_lines:$total_lines}),content:$ai_result.content}' \
    > "$WORK_DIR/skill-report-$SLUG.json"
  
  # Package if not blocked
  if [ "$SHOULD_BLOCK" != "true" ]; then
    PENDING_DIR="pending/$SLUG"
    mkdir -p "$PENDING_DIR/.claude-plugin" "$PENDING_DIR/skills/$SLUG"
    cp -r "$SKILL_DIR"/* "$PENDING_DIR/skills/$SLUG/"
    cp "$WORK_DIR/skill-report-$SLUG.json" "$PENDING_DIR/skill-report.json"
    
    DESC=$(jq -r '.content.value_statement // "A Claude skill"' "$WORK_DIR/skill-report-$SLUG.json")
    jq -n --arg name "$SLUG" --arg desc "$DESC" --arg repo "$SOURCE_URL" \
      '{name:$name,version:"1.0.0",description:$desc,author:{name:"Community"},homepage:("https://skillstore.io/skills/"+$name),repository:$repo,license:"MIT",keywords:[]}' \
      > "$PENDING_DIR/.claude-plugin/plugin.json"
    jq -n --arg name "$SLUG" --arg desc "$DESC" --arg path "pending/$SLUG" \
      '{name:$name,version:"1.0.0",description:$desc,author:{name:"Community"},homepage:("https://skillstore.io/skills/"+$name),path:$path}' \
      > "$PENDING_DIR/marketplace-entry.json"
    
    echo "$SLUG" >> "$WORK_DIR/processed-skills.txt"
    echo "Packaged: $SLUG -> $PENDING_DIR"
  else
    echo "$SLUG:$RISK_LEVEL" >> "$WORK_DIR/blocked-skills.txt"
    echo "Blocked: $SLUG (risk: $RISK_LEVEL)"
  fi
done

# Calculate final stats
PROCESSED_COUNT=$(wc -l < "$WORK_DIR/processed-skills.txt" 2>/dev/null | tr -d ' ' || echo "0")
BLOCKED_COUNT=$(wc -l < "$WORK_DIR/blocked-skills.txt" 2>/dev/null | tr -d ' ' || echo "0")

# Determine highest risk
if grep -q "critical" "$WORK_DIR/risk-levels.txt" 2>/dev/null; then
  HIGHEST_RISK="critical"
elif grep -q "high" "$WORK_DIR/risk-levels.txt" 2>/dev/null; then
  HIGHEST_RISK="high"
elif grep -q "medium" "$WORK_DIR/risk-levels.txt" 2>/dev/null; then
  HIGHEST_RISK="medium"
elif grep -q "low" "$WORK_DIR/risk-levels.txt" 2>/dev/null; then
  HIGHEST_RISK="low"
else
  HIGHEST_RISK="safe"
fi

echo ""
echo "============================================"
echo "Processing Complete"
echo "============================================"
echo "Total skills: $SKILL_COUNT"
echo "Processed: $PROCESSED_COUNT"
echo "Blocked: $BLOCKED_COUNT"
echo "Highest risk: $HIGHEST_RISK"

# Output results
echo "processed_count=$PROCESSED_COUNT" >> "$GITHUB_OUTPUT"
echo "blocked_count=$BLOCKED_COUNT" >> "$GITHUB_OUTPUT"
echo "highest_risk=$HIGHEST_RISK" >> "$GITHUB_OUTPUT"
SHOULD_BLOCK_ALL=$( [ "$PROCESSED_COUNT" -eq "0" ] && echo 'true' || echo 'false' )
echo "should_block_all=$SHOULD_BLOCK_ALL" >> "$GITHUB_OUTPUT"
SKILLS_LIST=$(cat "$WORK_DIR/processed-skills.txt" 2>/dev/null | tr '\n' ',' | sed 's/,$//' || echo "")
echo "skills_list=$SKILLS_LIST" >> "$GITHUB_OUTPUT"

echo ""
echo "Processed skills: $SKILLS_LIST"
