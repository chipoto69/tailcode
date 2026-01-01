# iPad Pro Shortcuts

One-tap access to your Macs from iPad.

## Prerequisites

1. Tailscale running on iPad
2. Blink Shell installed
3. Webhook server running on one Mac (the one that stays on most)

## Start Webhook Server

On your MacBook (or whichever Mac is usually on):

```bash
tc serve
```

Or run as background service:
```bash
nohup tc serve > /dev/null 2>&1 &
```

## Shortcut 1: Wake Mac Mini

**Actions:**
1. URL: `http://macbook-pro:8765/wake`
2. Method: POST
3. Headers: Content-Type: application/json
4. Body: `{"device": "macmini"}`
5. Get Contents of URL
6. Show Notification: "Mac Mini waking up"

## Shortcut 2: Connect to Mac Mini

**Actions:**
1. Open URL: `blinkshell://run?key=macmini&cmd=tmux%20new%20-A%20-s%20ai`

Configure `macmini` host in Blink Shell first:
- Host: mac-mini (Tailscale name)
- User: filip
- Mosh: ON

## Shortcut 3: Wake & Connect

**Actions:**
1. Get Contents of URL (wake endpoint)
2. Wait 30 seconds
3. Repeat 6 times:
   - Get Contents of `http://macbook-pro:8765/status`
   - Get dictionary value for macmini.online
   - If true: Open Blink URL, Stop Repeat
   - Else: Wait 10 seconds

## Shortcut 4: Quick Status Check

**Actions:**
1. Get Contents of `http://macbook-pro:8765/status`
2. Get dictionary value "devices"
3. Show Result

## Blink Shell URL Reference

| Action | URL |
|--------|-----|
| Connect | `blinkshell://run?key=hostname` |
| With tmux | `blinkshell://run?key=hostname&cmd=tmux%20new%20-A%20-s%20ai` |
| Run command | `blinkshell://run?key=hostname&cmd=your%20command` |

URL-encode spaces as `%20`

## Widget Setup

1. Long press home screen
2. Add Shortcuts widget (medium size)
3. Select your tailcode shortcuts
4. One-tap wake + connect from home screen

## Siri

Each shortcut can be voice-activated:
- "Hey Siri, wake Mac Mini"
- "Hey Siri, connect to Mac"

## Tips

1. **Keep MacBook awake** when at home - it's your relay for WoL
2. **Use Mosh** in Blink - survives network changes
3. **tmux always** - never lose your session
4. **ntfy app** - get notifications when devices wake
