#!/usr/bin/env bash
set -euo pipefail

# Web Search Script using Gemini CLI
# Usage: bash web-search.sh "<search query>"
# Description: Execute web search using Gemini API and return comprehensive results

# Validate input
if [[ -z "${1:-}" ]]; then
  cat <<EOF
Usage: bash web-search.sh "<search query>"

Example:
  bash web-search.sh "Next.js 15の新機能について教えて"
  bash web-search.sh "What are the latest features in TypeScript 5.5?"

Description:
  Execute web search using Gemini API and return comprehensive, cited results.
EOF
  exit 1
fi

readonly SEARCH_QUERY="$1"

# Execute Gemini search with structured prompt
gemini -p "Execute a web search to answer the following query comprehensively:

${SEARCH_QUERY}

Requirements:
- Search the web for current, relevant information
- Provide a detailed response in Markdown format
- Include all source URLs in your response
- Synthesize information from multiple sources when applicable
- Format code examples properly if applicable
- Do not write results to files, return them directly

Please provide a comprehensive answer with proper citations." \
  --yolo \
  --output-format json
