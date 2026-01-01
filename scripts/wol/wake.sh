#!/usr/bin/env bash
set -euo pipefail

MAC="${1:-}"

if [[ -z "$MAC" ]]; then
    echo "Usage: $0 <MAC_ADDRESS>"
    echo "Example: $0 00:11:22:33:44:55"
    exit 1
fi

MAC_CLEAN=$(echo "$MAC" | tr -d ':' | tr -d '-')

if [[ ${#MAC_CLEAN} -ne 12 ]]; then
    echo "Error: Invalid MAC address"
    exit 1
fi

MAGIC_PACKET=$(printf '\xff%.0s' {1..6})
for i in {1..16}; do
    MAGIC_PACKET+=$(echo "$MAC_CLEAN" | sed 's/../\\x&/g')
done

echo -ne "$MAGIC_PACKET" | socat - UDP-DATAGRAM:255.255.255.255:9,broadcast

echo "WoL packet sent to $MAC"
