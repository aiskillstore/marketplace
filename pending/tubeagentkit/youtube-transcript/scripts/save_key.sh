#!/bin/bash
# Step 2 of API key setup: gets the API key and saves it without ever printing
# it. Two ways in:
#   - with <email> <code>: exchanges the 6-digit code that request_code.sh had
#     emailed for an API key (creates the account if it is new);
#   - with no email/code: reads a key the user created at
#     https://getyoutubetranscript.com/dashboard and pasted, from standard input
#     (so it is not a command-line argument).
# The key is checked against the free /credits endpoint, then written to
# ~/.config/getyoutubetranscript/api_key (mode 600), which every script in
# scripts/ reads.
#
# Only with --profile (pass it only after the user has explicitly agreed), one
# line is appended to the shell profile (~/.zshrc, ~/.bashrc or ~/.profile):
#   [ -r "<key file>" ] && export YOUTUBE_TRANSCRIPT_API_KEY="$(cat "<key file>")"  # getyoutubetranscript.com
# That line reads the key file; the key itself is not copied into the profile.
#
# --name "<name>" (optional, only if the user offered one) is stored as the
# account's display name when the account has none yet.
#
# Usage:
#   ./save_key.sh <email> <6-digit-code> [--name "<name>"] [--profile]
#   printf '%s' "<api key>" | ./save_key.sh [--profile]
#   ./save_key.sh --profile     (adds the profile line for the key already saved)
set -euo pipefail

UPDATE_PROFILE=0
NAME=""
ARGS=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        --profile) UPDATE_PROFILE=1 ;;
        --name) NAME="${2:-}"; shift ;;
        --name=*) NAME="${1#--name=}" ;;
        *) ARGS+=("$1") ;;
    esac
    shift
done

# JSON string escaping for values we didn't choose (the email and the optional name).
json_escape() {
    printf '%s' "$1" | tr '\000-\037' ' ' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

API_BASE="https://getyoutubetranscript.com/api/v1"
KEY_FILE="$HOME/.config/getyoutubetranscript/api_key"
USER_AGENT="User-Agent: youtube-transcript-skill/1.2"

if [ "${#ARGS[@]}" -ge 2 ]; then
    RESPONSE="$(curl -s -X POST "${API_BASE}/signup/verify" \
        -H "Content-Type: application/json" -H "$USER_AGENT" \
        --data "$(printf '{"email": "%s", "otp": "%s", "name": "%s"}' "$(json_escape "${ARGS[0]}")" "$(json_escape "${ARGS[1]}")" "$(json_escape "$NAME")")")"
    KEY="$(printf '%s' "$RESPONSE" | sed -n 's/.*"api_key" *: *"\(sk_live_[A-Za-z0-9_-]*\)".*/\1/p')"
    if [ -z "$KEY" ]; then
        # No key in the response, so it is safe to show: it is the server's error.
        echo "Error: could not verify the code. Server response: ${RESPONSE}" >&2
        exit 1
    fi
else
    KEY=""
    [ -t 0 ] || KEY="$(tr -d '[:space:]')"
    if [ -z "$KEY" ] && [ "$UPDATE_PROFILE" = 1 ] && [ -r "$KEY_FILE" ]; then
        # --profile on its own: add the profile line for the key that is already saved.
        KEY="$(tr -d '[:space:]' < "$KEY_FILE")"
    fi
    case "$KEY" in
        sk_live_*) ;;
        *)
            echo "Error: expected <email> <code>, or an API key starting with sk_live_ on standard input." >&2
            exit 1
            ;;
    esac
fi

# Check the key before saving it (the credits call is free and prints the balance, not the key).
BALANCE="$(curl -s "${API_BASE}/credits" -H "Authorization: Bearer ${KEY}" -H "$USER_AGENT")"
case "$BALANCE" in
    *'"success":true'*) ;;
    *)
        echo "Error: the key was not accepted, nothing was saved. Server response: ${BALANCE}" >&2
        exit 1
        ;;
esac

mkdir -p "$(dirname "$KEY_FILE")"
chmod 700 "$(dirname "$KEY_FILE")"
(umask 077 && printf '%s\n' "$KEY" > "$KEY_FILE")
echo "Saved the API key to ${KEY_FILE} (readable only by you)."

if [ "$UPDATE_PROFILE" = 1 ]; then
    case "$(basename "${SHELL:-}")" in
        zsh) PROFILE="$HOME/.zshrc" ;;
        bash) PROFILE="$HOME/.bashrc" ;;
        *) PROFILE="$HOME/.profile" ;;
    esac
    LINE="[ -r \"${KEY_FILE}\" ] && export YOUTUBE_TRANSCRIPT_API_KEY=\"\$(cat \"${KEY_FILE}\")\"  # getyoutubetranscript.com"
    if grep -qF "# getyoutubetranscript.com" "$PROFILE" 2>/dev/null; then
        echo "${PROFILE} already loads the key file; left it unchanged."
    else
        printf '\n%s\n' "$LINE" >> "$PROFILE"
        echo "Added one line to ${PROFILE} so new terminals load YOUTUBE_TRANSCRIPT_API_KEY from that file."
    fi
fi

echo "$BALANCE"
