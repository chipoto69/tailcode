# Tailcode

Connect to any Mac, from anywhere. One command.

```bash
tc connect        # Connect to default device (auto-wakes if needed)
tc connect macbook   # Connect to specific device
tc status         # See what's online
```

## Your Setup

```
iPad Pro ──── Tailscale ──── MacBook Pro
                  │               │
                  │          Wake-on-LAN
                  │               │
                  └──────── Mac Mini
```

- **Mac Mini**: Home server, always reachable via Tailscale
- **MacBook Pro**: Mobile workhorse, can wake Mac Mini when home
- **iPad Pro**: Your mobile terminal via Blink Shell

## Quick Start

```bash
# Install
cd tailcode
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Auto-discover devices from Tailscale
tc discover --user filip

# Or manually configure
cp config/config.example.yaml ~/.config/tailcode/config.yaml

# Setup each Mac (enables Remote Login, WoL)
./scripts/mac-setup.sh

# Use
tc status           # See devices
tc connect          # Connect to default
tc ai               # Connect + Claude Code
```

## Commands

| Command | Description |
|---------|-------------|
| `tc status` | Show all devices and online status |
| `tc connect [device]` | SSH + tmux to device (auto-wake) |
| `tc ai [device]` | Connect + launch Claude Code |
| `tc wake <device>` | Send Wake-on-LAN |
| `tc run <device> <cmd>` | Run command remotely |
| `tc discover` | Auto-discover devices from Tailscale |
| `tc install` | Install webhook as launchd service |
| `tc serve` | Start webhook for iPad Shortcuts |
| `tc notify <msg>` | Push notification to phone |

## Config

`~/.config/tailcode/config.yaml`:

```yaml
devices:
  macmini:
    hostname: "mac-mini"
    mac: "AA:BB:CC:DD:EE:FF"
    user: "filip"
    role: server
    location: home

  macbook:
    hostname: "macbook-pro"  
    mac: "11:22:33:44:55:66"
    user: "filip"
    role: server
    location: mobile

  ipad:
    hostname: "ipad-pro"
    role: client

notifications:
  provider: ntfy
  ntfy:
    topic: "your-secret-topic"

preferences:
  default_device: macmini
```

## iPad Workflow

1. Install webhook server on your Mac:
   ```bash
   tc install  # Auto-starts on boot
   ```

2. Create Shortcuts on iPad (see `shortcuts/README.md`):
   - **Wake**: POST to `http://macbook-pro:8765/wake`
   - **Connect**: Open `blinkshell://run?key=macmini`
   - **AI Session**: Wake + Connect + Claude Code

3. Add to home screen widget for one-tap access

## Wake-on-LAN Logic

When you `tc connect macmini` and it's offline:

1. Finds another device at same location that's online
2. SSHes to that device to send WoL packet
3. Waits for target to come online
4. Connects

This means: if your MacBook is home and online, it can wake your Mac Mini for you, even when you're remote on iPad.

## Requirements

- macOS with Remote Login enabled
- Tailscale on all devices
- Wake for network access enabled (System Settings → Battery)
- Blink Shell on iPad (recommended)
