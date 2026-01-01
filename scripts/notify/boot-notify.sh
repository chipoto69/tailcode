#!/usr/bin/env bash
set -euo pipefail

HOSTNAME=$(hostname)
IP=$(tailscale ip -4 2>/dev/null || hostname -I | awk '{print $1}')
UPTIME=$(uptime -p 2>/dev/null || uptime)

MESSAGE="Host: $HOSTNAME
IP: $IP
$UPTIME"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/notify.sh" "$MESSAGE" "Boot Complete"
