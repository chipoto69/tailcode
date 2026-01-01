# Apple Shortcuts for Tailcode

One-tap access to your Macs from iPhone/iPad.

## Prerequisites

1. Tailscale installed and connected on iPhone/iPad
2. Webhook server running on at least one Mac: `tc serve` or `tc install`
3. SSH app installed (Termius recommended)

## Quick Setup

### 1. Start webhook server on your always-on Mac

```bash
tc install  # Installs as launchd service, auto-starts on boot
```

### 2. Find your webhook URL

Your webhook URL is: `http://YOUR-MAC-HOSTNAME:8765`

Example: `http://mac-mini:8765`

### 3. Create shortcuts below

---

## Shortcuts

### 1. Wake Device

Sends Wake-on-LAN to wake a sleeping Mac.

**Actions:**
1. **URL**: `http://mac-mini:8765/wake`
2. **Get Contents of URL**
   - Method: POST
   - Headers: `Content-Type: application/json`
   - Request Body: `{"device": "macbook1"}`
3. **Show Notification**
   - Title: "Tailcode"
   - Body: "Waking macbook1..."

### 2. Device Status

Check which devices are online.

**Actions:**
1. **URL**: `http://mac-mini:8765/status`
2. **Get Contents of URL** (Method: POST)
3. **Get Dictionary Value**: Key = `devices`
4. **Repeat with Each** item in Devices:
   - Get Dictionary Value: `name`
   - Get Dictionary Value: `online`
   - **If** online = true:
     - Add to Text: "[name]: Online"
   - Otherwise:
     - Add to Text: "[name]: Offline"
5. **Show Result**

### 3. Connect to Mac (Termius)

Opens Termius and connects to a specific host.

**Actions:**
1. **Open URL**: `termius://host/macmini`

Note: Replace `macmini` with the host name configured in Termius.

### 4. Wake + Connect

Wake a device, wait, then connect.

**Actions:**
1. **URL**: `http://mac-mini:8765/wake`
2. **Get Contents of URL** (POST, body: `{"device": "macbook1"}`)
3. **Wait**: 20 seconds
4. **Open URL**: `termius://host/macbook1`

### 5. AI Coding Session

Wake device, wait, connect with AI assistant (OpenCode/Claude) ready.

**Actions:**
1. **Get Contents of URL**: `http://mac-mini:8765/wake` (POST, device: macmini)
2. **Wait**: 15 seconds
3. **Open URL**: `termius://host/macmini`
4. **Show Notification**: "Run 'tc ai' to start coding"

### 6. Smart Wake + Connect (Poll Until Ready)

More reliable than fixed wait time.

**Actions:**
1. **Get Contents of URL**: Wake endpoint
2. **Repeat 12 times**:
   - **Wait** 5 seconds
   - **Get Contents of URL**: Status endpoint
   - **Get Dictionary Value** from devices for your target
   - **If** online = true:
     - **Open URL**: Termius
     - **Stop Repeat**
3. **If** not connected after 60s:
   - **Show Notification**: "Device didn't wake up"

---

## Termius URL Schemes

| Action | URL |
|--------|-----|
| Open app | `termius://` |
| Connect to host | `termius://host/HOSTNAME` |
| Connect with command | `termius://host/HOSTNAME?cmd=COMMAND` |

URL-encode special characters in commands (space = `%20`).

---

## Webhook API Reference

| Endpoint | Method | Body | Response |
|----------|--------|------|----------|
| `/health` | GET | - | `{"ok": true}` |
| `/wake` | POST | `{"device": "name"}` | `{"ok": true, "method": "relay:macmini"}` |
| `/status` | POST | - | `{"devices": [...]}` |
| `/notify` | POST | `{"message": "text", "title": "optional"}` | `{"ok": true}` |
| `/discover` | POST | - | `{"ok": true, "hostname": "...", "webhook_port": 8765}` |

---

## Dynamic Webhook Discovery

If you have multiple Macs that might run the webhook, use discovery:

**Shortcut: Find Active Webhook**

1. Create a list of potential hosts: `["mac-mini", "macbook-pro-1", "macbook-pro-2"]`
2. **Repeat with Each** host:
   - **Get Contents of URL**: `http://[host]:8765/health`
   - **If** response contains "ok":
     - **Set Variable** `ActiveHost` to current host
     - **Stop Repeat**
3. Use `ActiveHost` for subsequent API calls

---

## Tips

### Add to Home Screen

1. Create your shortcut
2. Tap ••• (three dots)
3. Tap "Add to Home Screen"
4. Choose an icon and name

### Use Siri

Name your shortcuts naturally:
- "Wake Mac Mini"
- "Connect to MacBook"
- "Start Coding"

Then say: "Hey Siri, wake Mac Mini"

### Lock Screen Widget

Add Shortcuts widget to Lock Screen for fastest access.

### Focus Mode Integration

Different shortcuts for different contexts:
- Work Focus: Show coding shortcuts
- Home Focus: Show all devices
