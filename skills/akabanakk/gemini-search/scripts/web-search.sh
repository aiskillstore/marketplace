#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <search-query>"
    echo "Example: $0 \"Next.js 15の新機能について教えて\""
    exit 1
fi

SEARCH_QUERY="$1"

gemini -p "
## タスク
「依頼内容」を達成するために、ウェブ検索を行い、できるだけ詳細に回答してください。

## 依頼内容
${SEARCH_QUERY}

## 結果のフォーマット
- 回答はMarkdown形式で記述すること
- 検索結果はファイルなどに書き出さず、レスポンスとして返すこと
- 回答には参考にしたURLを全て一覧として含めること
" --yolo --output-format json
