#!/bin/bash
# claude_wrapper.sh - Wrapper CLI pour l'API Anthropic
# PRD-008 Story 8.3: Exemple de CLI wrapper
#
# Usage: ./claude_wrapper.sh "Votre prompt ici"
#
# Prérequis:
#   - curl installé
#   - ANTHROPIC_API_KEY défini
#
# Configuration optionnelle:
#   - CLAUDE_MODEL: Modèle à utiliser (défaut: claude-3-5-sonnet-20241022)
#   - CLAUDE_MAX_TOKENS: Tokens max (défaut: 4096)

set -e

# Configuration
MODEL="${CLAUDE_MODEL:-claude-3-5-sonnet-20241022}"
MAX_TOKENS="${CLAUDE_MAX_TOKENS:-4096}"
API_URL="https://api.anthropic.com/v1/messages"

# Vérification de la clé API
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Erreur: ANTHROPIC_API_KEY non défini" >&2
    exit 1
fi

# Récupérer le prompt
PROMPT="$1"
if [ -z "$PROMPT" ]; then
    echo "Erreur: Prompt requis" >&2
    echo "Usage: $0 \"Votre prompt\"" >&2
    exit 1
fi

# Échapper le prompt pour JSON
ESCAPED_PROMPT=$(echo "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')

# Appel API
RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d "{
        \"model\": \"$MODEL\",
        \"max_tokens\": $MAX_TOKENS,
        \"messages\": [
            {\"role\": \"user\", \"content\": $ESCAPED_PROMPT}
        ]
    }")

# Extraire le contenu de la réponse
echo "$RESPONSE" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    if "content" in data and len(data["content"]) > 0:
        print(data["content"][0]["text"])
    elif "error" in data:
        print(f"Erreur API: {data[\"error\"][\"message\"]}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Réponse inattendue", file=sys.stderr)
        sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Erreur JSON: {e}", file=sys.stderr)
    sys.exit(1)
'
