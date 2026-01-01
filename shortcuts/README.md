# iPad Shortcuts for Tailcode

These shortcuts integrate with the Tailcode webhook server running on your Mac.

## Prerequisites

1. Tailcode webhook server running on a Mac in your Tailscale network
2. Blink Shell installed on iPad (for SSH connections)
3. Tailscale installed on iPad

## Quick Setup

### 1. Start the webhook server on your Mac

```bash
# Option A: Run in foreground
tc serve

# Option B: Install as service (auto-starts on boot)
tc install
```

### 2. Get your Mac's Tailscale hostname

```bash
tailscale status
# Note your Mac's hostname (e.g., "macbook-pro")
```

### 3. Create shortcuts on iPad

See below for each shortcut.

---

## Shortcuts

### Wake Mac Mini

Sends Wake-on-LAN to your Mac Mini via the webhook server.

**Actions:**
1. **Get Contents of URL**
   - URL: `http://YOUR-MAC-HOSTNAME:8765/wake`
   - Method: POST
   - Headers: `Content-Type: application/json`
   - Request Body: `{"device": "macmini"}`

2. **Show Notification**
   - Title: "Wake Sent"
   - Body: "Mac Mini waking up..."

### Device Status

Shows which devices are online.

**Actions:**
1. **Get Contents of URL**
   - URL: `http://YOUR-MAC-HOSTNAME:8765/status`
   - Method: POST

2. **Get Dictionary Value** (key: "devices")

3. **Show Result**

### Connect to Mac Mini

Opens Blink Shell and connects to your Mac Mini.

**Actions:**
1. **Open URL**
   - URL: `blinkshell://run?key=macmini`

*Note: Set up a Blink host named "macmini" first: `tailscale ssh` to your Mac Mini's Tailscale hostname.*

### Connect to MacBook

**Actions:**
1. **Open URL**
   - URL: `blinkshell://run?key=macbook`

### Wake + Connect (Smart)

Wakes a device if needed, waits, then connects.

**Actions:**
1. **Get Contents of URL**
   - URL: `http://YOUR-MAC-HOSTNAME:8765/wake`
   - Method: POST
   - Request Body: `{"device": "macmini"}`

2. **Wait** (15 seconds)

3. **Open URL**
   - URL: `blinkshell://run?key=macmini`

### AI Session

Wake device, wait, connect directly to Claude Code.

**Actions:**
1. **Get Contents of URL**
   - URL: `http://YOUR-MAC-HOSTNAME:8765/wake`
   - Method: POST
   - Request Body: `{"device": "macmini"}`

2. **Wait** (20 seconds)

3. **Open URL**
   - URL: `blinkshell://run?key=macmini&cmd=claude`

---

## Blink Shell Setup

Configure Blink hosts for each device:

1. Open Blink Shell
2. Go to Settings → Hosts
3. Add new host:
   - **Key**: `macmini`
   - **Host**: Your Mac Mini's Tailscale hostname
   - **User**: Your username
   - **SSH**: Use Tailscale SSH (mosh disabled)

Repeat for each device.

---

## Webhook API Reference

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/wake` | POST | `{"device": "name"}` | `{"success": true}` |
| `/status` | POST | - | `{"devices": [...]}` |
| `/health` | GET | - | `{"status": "ok"}` |

---

## Tips

- Add shortcuts to Home Screen for one-tap access
- Create a "Wake All" shortcut that wakes multiple devices
- Use Focus modes to show different shortcuts at home vs. work
- Add shortcuts to Lock Screen widgets (iOS 16+)
