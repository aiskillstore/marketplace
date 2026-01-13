#!/bin/bash
# ollama_wrapper.sh - Wrapper CLI pour Ollama (LLM local)
# PRD-008 Story 8.3: Exemple de CLI wrapper
#
# Usage: ./ollama_wrapper.sh "Votre prompt ici"
#
# Prérequis:
#   - Ollama installé et en cours d'exécution
#   - Au moins un modèle téléchargé (ex: ollama pull llama2)
#
# Configuration optionnelle:
#   - OLLAMA_MODEL: Modèle à utiliser (défaut: llama2)
#   - OLLAMA_HOST: URL du serveur (défaut: http://localhost:11434)

set -e

# Configuration
MODEL="${OLLAMA_MODEL:-llama2}"
HOST="${OLLAMA_HOST:-http://localhost:11434}"

# Récupérer le prompt
PROMPT="$1"
if [ -z "$PROMPT" ]; then
    echo "Erreur: Prompt requis" >&2
    echo "Usage: $0 \"Votre prompt\"" >&2
    exit 1
fi

# Vérifier qu'Ollama est accessible
if ! curl -s --connect-timeout 2 "$HOST/api/tags" > /dev/null 2>&1; then
    echo "Erreur: Ollama non accessible sur $HOST" >&2
    echo "Lancez: ollama serve" >&2
    exit 1
fi

# Échapper le prompt pour JSON
ESCAPED_PROMPT=$(echo "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')

# Appel API Ollama
RESPONSE=$(curl -s -X POST "$HOST/api/generate" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"$MODEL\",
        \"prompt\": $ESCAPED_PROMPT,
        \"stream\": false
    }")

# Extraire la réponse
echo "$RESPONSE" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
    if "response" in data:
        print(data["response"])
    elif "error" in data:
        print(f"Erreur Ollama: {data[\"error\"]}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Réponse inattendue", file=sys.stderr)
        sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Erreur JSON: {e}", file=sys.stderr)
    sys.exit(1)
'
