#!/usr/bin/env bash
set -euo pipefail

echo "=== Tailscale Server Setup ==="

if command -v tailscale &> /dev/null; then
    echo "Tailscale already installed"
    tailscale version
else
    echo "Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi

echo ""
echo "=== Enabling IP Forwarding (for exit node) ==="
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf

echo ""
echo "=== Starting Tailscale ==="
echo "Run the following command to authenticate and enable features:"
echo ""
echo "  sudo tailscale up --ssh --advertise-exit-node"
echo ""
echo "Then approve the exit node in the Tailscale admin console:"
echo "  https://login.tailscale.com/admin/machines"
