#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-}"
TITLE="${2:-Tailcode}"
TOPIC="${NTFY_TOPIC:-tailcode-alerts}"
SERVER="${NTFY_SERVER:-https://ntfy.sh}"

if [[ -z "$MESSAGE" ]]; then
    echo "Usage: $0 <message> [title]"
    echo "Environment variables:"
    echo "  NTFY_TOPIC  - ntfy topic (default: tailcode-alerts)"
    echo "  NTFY_SERVER - ntfy server (default: https://ntfy.sh)"
    exit 1
fi

curl -s \
    -H "Title: $TITLE" \
    -d "$MESSAGE" \
    "$SERVER/$TOPIC"

echo "Notification sent: $MESSAGE"
