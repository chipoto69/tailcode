# Apple Shortcuts Integration

Control your tailnet devices from iPhone/iPad with one tap.

## Architecture

```
iPhone Shortcut
    |
    | HTTP POST (over Tailscale)
    v
Raspberry Pi (webhook server)
    |
    | Wake-on-LAN / SSH
    v
Target Server
```

The webhook server runs on your always-on device (Pi) and handles commands.

## Setup

### 1. Start the Webhook Server on Your Bridge Device

```bash
# On Pi or always-on device
cd /path/to/tailcode
source .venv/bin/activate

# Set auth token (optional but recommended)
export TAILCODE_WEBHOOK_TOKEN="your-secret-token"

# Start server
tailcode serve --port 8765
```

### 2. Run as Systemd Service (Recommended)

Create `/etc/systemd/system/tailcode-webhook.service`:

```ini
[Unit]
Description=Tailcode Webhook Server
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tailcode
Environment="TAILCODE_WEBHOOK_TOKEN=your-secret-token"
ExecStart=/home/pi/tailcode/.venv/bin/tailcode serve --port 8765
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now tailcode-webhook
```

## Apple Shortcuts

### Shortcut 1: Wake Server

1. Open Shortcuts app
2. Create new shortcut
3. Add actions:

```
Get Contents of URL
  URL: http://pi.tailnet-name.ts.net:8765/wake
  Method: POST
  Headers:
    Authorization: Bearer your-secret-token
    Content-Type: application/json
  Request Body: JSON
    device: homeserver

Show Notification
  Title: Tailcode
  Body: Server waking up...
```

### Shortcut 2: Connect to Server (Blink Shell)

1. Create new shortcut
2. Add actions:

```
Open URLs
  URL: blinkshell://run?key=homeserver
```

Note: Configure "homeserver" host in Blink Shell first with:
- Host: homeserver.tailnet-name.ts.net
- User: ubuntu
- Use Mosh: ON

### Shortcut 3: Boot & Connect (Full Workflow)

1. Create new shortcut
2. Add actions:

```
Get Contents of URL
  URL: http://pi.tailnet-name.ts.net:8765/wake
  Method: POST
  Headers:
    Authorization: Bearer your-secret-token
    Content-Type: application/json
  Request Body: JSON
    device: homeserver

Wait 30 seconds

Repeat 6 times
  Get Contents of URL
    URL: http://pi.tailnet-name.ts.net:8765/ping
    Method: POST
    Headers:
      Authorization: Bearer your-secret-token
      Content-Type: application/json
    Request Body: JSON
      device: homeserver
  
  Get Dictionary Value (reachable) from Contents of URL
  
  If reachable = true
    Open URLs
      URL: blinkshell://run?key=homeserver&cmd=tmux%20new%20-A%20-s%20ai-coding
    Stop Repeat
  Otherwise
    Wait 10 seconds
  End If
End Repeat
```

### Shortcut 4: Quick Notify

1. Create new shortcut
2. Add actions:

```
Ask for Input
  Prompt: Message
  Input Type: Text

Get Contents of URL
  URL: http://pi.tailnet-name.ts.net:8765/notify
  Method: POST
  Headers:
    Authorization: Bearer your-secret-token
    Content-Type: application/json
  Request Body: JSON
    message: [Provided Input]
    title: Phone
```

## Blink Shell URL Schemes

| Action | URL |
|--------|-----|
| Open host | `blinkshell://run?key=hostname` |
| Run command | `blinkshell://run?key=hostname&cmd=command` |
| Mosh connect | `blinkshell://run?key=hostname` (if Mosh enabled) |
| Open tmux | `blinkshell://run?key=hostname&cmd=tmux%20new%20-A%20-s%20session` |

URL encode commands: space = `%20`, `&` = `%26`

## Termius URL Schemes (Alternative)

| Action | URL |
|--------|-----|
| Open host | `termius://host/hostname` |
| SSH connect | `termius://ssh/user@host` |

## Widget Setup

1. Long press home screen
2. Add Shortcuts widget
3. Select your tailcode shortcuts
4. One-tap access to wake/connect

## Siri Integration

Each shortcut can be triggered by voice:
- "Hey Siri, wake my server"
- "Hey Siri, connect to homeserver"
- "Hey Siri, boot and connect"

## Troubleshooting

### Can't Connect to Webhook
1. Verify Tailscale is connected on phone
2. Check Pi hostname: `tailscale status`
3. Test in browser: `http://pi.tailnet-name.ts.net:8765/health`

### Shortcut Timeout
- Increase wait times between ping attempts
- Check if server takes longer to boot

### Blink Not Opening
- Ensure Blink Shell is installed
- Check host is configured in Blink
- Try URL in Safari first to test
