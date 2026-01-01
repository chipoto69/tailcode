#!/usr/bin/env bash
set -euo pipefail

IFACE="${1:-eth0}"

echo "=== Wake-on-LAN Setup for $IFACE ==="

echo "Current WoL status:"
sudo ethtool "$IFACE" | grep -i wake || echo "Could not get WoL status"

echo ""
echo "Creating systemd service to enable WoL on boot..."

sudo tee /etc/systemd/system/wol.service > /dev/null << EOF
[Unit]
Description=Enable Wake-on-LAN
After=network-online.target

[Service]
Type=oneshot
ExecStart=/sbin/ethtool -s $IFACE wol g

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now wol.service

echo ""
echo "WoL enabled. Verifying..."
sudo ethtool "$IFACE" | grep -i wake

echo ""
echo "Done. Make sure WoL is also enabled in BIOS/UEFI."
