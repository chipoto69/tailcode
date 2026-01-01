# Setup Guide

## Your Devices

| Device | Role | Notes |
|--------|------|-------|
| Mac Mini | Server | Home base, wake via WoL |
| MacBook Pro | Server | Mobile, wake when on home network |
| iPad Pro | Client | Use Blink Shell to connect |

## 1. Install Tailscale on All Devices

**Mac:**
```bash
brew install tailscale
tailscale up --ssh
```

**iPad:** Download from App Store

## 2. Enable Remote Login (SSH) on Macs

System Settings → General → Sharing → Remote Login → ON

Or via terminal:
```bash
sudo systemsetup -setremotelogin on
```

## 3. Enable Wake-on-LAN on Macs

System Settings → Battery → Options → Wake for network access → ON

Get your MAC address:
```bash
networksetup -getmacaddress en0
```

## 4. Install Tailcode

```bash
cd ~/projects/tailcode
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 5. Configure

Create `~/.config/tailcode/config.yaml`:

```yaml
tailscale:
  api_key: "tskey-api-xxx"  # Optional, for API features
  tailnet: "-"

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
  auto_wake: true
```

## 6. iPad Setup (Blink Shell)

1. Install Blink Shell from App Store
2. Add hosts:
   - Name: `macmini`
   - Host: `mac-mini` (Tailscale hostname)
   - User: `filip`
   - Use Mosh: ON (recommended)

3. Connect: `mosh macmini`

## Usage

```bash
# Show all devices
tc status

# Connect to default (mac mini)
tc connect

# Connect to specific device
tc connect macbook

# Wake a device
tc wake macmini

# Run command
tc run macmini "uptime"

# Send notification
tc notify "Build done"
```

## Wake-on-LAN Flow

When you `tc connect macmini` and it's offline:

1. Tool detects Mac Mini is offline
2. Looks for another device on same network (location: home)
3. If MacBook is home and online → sends WoL via MacBook
4. If nothing online at home → sends local broadcast (only works if you're home)
5. Waits for device to come online
6. Connects

## iPad Shortcuts

Create these in Apple Shortcuts app:

**Wake Mac Mini:**
```
POST http://macbook:8765/wake
Body: {"device": "macmini"}
```

**Check Status:**
```
POST http://macbook:8765/status
```

Then tap shortcut → Mac wakes → open Blink → connect
