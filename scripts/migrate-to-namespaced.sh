#!/bin/bash
set -e

OFFICIAL_OWNERS="anthropics openai aiskillstore"

for dir in plugins/*/; do
  if [ -f "${dir}marketplace-entry.json" ]; then
    slug=$(basename "$dir")
    repo=$(jq -r '.repository // empty' "${dir}marketplace-entry.json")
    owner=$(echo "$repo" | sed -E 's|.*github\.com/([^/]+)/.*|\1|')
    
    is_official=false
    for official in $OFFICIAL_OWNERS; do
      if [ "$owner" = "$official" ]; then
        is_official=true
        break
      fi
    done
    
    if [ "$is_official" = false ]; then
      echo "Migrating $slug -> $owner/$slug"
      
      mkdir -p "plugins/$owner"
      mv "plugins/$slug" "plugins/$owner/$slug"
      
      jq --arg slug "$owner/$slug" --arg path "plugins/$owner/$slug" \
        '.name = $slug | .slug = $slug | .path = $path' \
        "plugins/$owner/$slug/marketplace-entry.json" > /tmp/entry.json
      mv /tmp/entry.json "plugins/$owner/$slug/marketplace-entry.json"
      
      if [ -f "plugins/$owner/$slug/.claude-plugin/plugin.json" ]; then
        jq --arg name "$owner/$slug" --arg homepage "https://skillstore.io/skills/$owner/$slug" \
          '.name = $name | .homepage = $homepage' \
          "plugins/$owner/$slug/.claude-plugin/plugin.json" > /tmp/plugin.json
        mv /tmp/plugin.json "plugins/$owner/$slug/.claude-plugin/plugin.json"
      fi
    else
      echo "Keeping $slug (official: $owner)"
    fi
  fi
done

echo "Migration complete!"
