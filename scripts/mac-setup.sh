#!/usr/bin/env bash
set -euo pipefail

echo "=== Tailcode Mac Setup ==="

echo ""
echo "1. Checking Tailscale..."
if command -v tailscale &> /dev/null; then
    echo "   Tailscale installed"
    tailscale version
else
    echo "   Installing Tailscale..."
    brew install tailscale
fi

echo ""
echo "2. Enabling Remote Login (SSH)..."
sudo systemsetup -setremotelogin on 2>/dev/null || echo "   Already enabled or requires System Settings"

echo ""
echo "3. Wake-on-LAN Setup"
echo "   Open System Settings > Energy Saver (or Battery)"
echo "   Enable: 'Wake for network access'"
echo ""
echo "   To get your MAC address:"
echo "   networksetup -getmacaddress en0"
MAC=$(networksetup -getmacaddress en0 2>/dev/null | awk '{print $3}' || echo "unknown")
echo "   Your MAC: $MAC"

echo ""
echo "4. Tailscale SSH"
echo "   Run: tailscale up --ssh"
echo "   This enables Tailscale SSH (no key management needed)"

echo ""
echo "5. Configuration"
echo "   Add this device to ~/.config/tailcode/config.yaml:"
echo ""
HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]')
echo "   $HOSTNAME:"
echo "     hostname: \"$HOSTNAME\""
echo "     mac: \"$MAC\""
echo "     user: \"$USER\""
echo "     role: server"

echo ""
echo "=== Done ==="
