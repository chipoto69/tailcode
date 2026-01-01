# Server Setup Guide

Complete setup for a remote development server accessible via Tailscale.

## 1. Tailscale Installation

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start with SSH and exit node enabled
sudo tailscale up --ssh --advertise-exit-node

# Follow the auth URL that appears
```

### Enable Exit Node (Admin Console)
1. Go to https://login.tailscale.com/admin/machines
2. Find your server
3. Click "..." -> "Edit route settings"
4. Enable "Use as exit node"

## 2. IP Forwarding (Required for Exit Node)

```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

## 3. Wake-on-LAN Setup

### BIOS/UEFI Settings
- Wake on LAN: **Enabled**
- Wake on PCIe: **Enabled**
- ERP Ready / Deep Sleep: **Disabled**

### Linux Configuration
```bash
# Check current status
sudo ethtool eth0 | grep Wake-on
# Should show: Wake-on: g

# If it shows 'd', enable WoL:
sudo ethtool -s eth0 wol g

# Make persistent (systemd)
sudo tee /etc/systemd/system/wol.service << 'EOF'
[Unit]
Description=Enable Wake-on-LAN
After=network-online.target

[Service]
Type=oneshot
ExecStart=/sbin/ethtool -s eth0 wol g

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now wol.service
```

## 4. Mosh Installation (Optional but Recommended)

```bash
sudo apt install mosh
# Firewall: allow UDP 60000-61000
sudo ufw allow 60000:61000/udp
```

## 5. tmux Setup

```bash
sudo apt install tmux

# Create config
cat > ~/.tmux.conf << 'EOF'
set -g status on
set -g mouse on
set -g history-limit 50000
set -g default-terminal "screen-256color"
EOF
```

## 6. Boot Notification (Optional)

Send a notification when the server boots:

```bash
# Copy the notify script
sudo cp scripts/notify/boot-notify.sh /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/boot-notify.service << 'EOF'
[Unit]
Description=Boot Notification
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/boot-notify.sh
Environment="NTFY_TOPIC=your-topic"

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable boot-notify.service
```

## 7. Claude Code / OpenCode Installation

```bash
# Claude Code
npm install -g @anthropic/claude-code

# Or OpenCode
go install github.com/opencode-ai/opencode@latest
```

## Verification Checklist

- [ ] `tailscale status` shows connected
- [ ] `tailscale ssh user@localhost` works
- [ ] `ethtool eth0 | grep Wake-on` shows `g`
- [ ] `tmux` starts correctly
- [ ] `mosh localhost` works (if installed)
- [ ] Boot notification received (if configured)

## Security Notes

### Tailscale ACLs
Configure ACLs in the admin console to restrict access:
```json
{
  "acls": [
    {"action": "accept", "src": ["autogroup:member"], "dst": ["*:*"]}
  ],
  "ssh": [
    {"action": "check", "src": ["autogroup:member"], "dst": ["tag:server"], "users": ["autogroup:nonroot"]}
  ]
}
```

### No Open Ports
With Tailscale SSH, you don't need port 22 open to the internet. Your server is only accessible via Tailscale.
