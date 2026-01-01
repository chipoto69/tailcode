# iPhone Setup: Termius

Termius is the recommended SSH client for iPhone. It's free, supports Mosh, and has an excellent mobile keyboard.

## Installation

1. Download [Termius](https://apps.apple.com/us/app/termius-modern-ssh-client/id549039908) from the App Store (free)
2. Download [Tailscale](https://apps.apple.com/us/app/tailscale/id1470499037) from the App Store (free)

## Initial Setup

### 1. Connect to Tailscale

1. Open Tailscale app
2. Sign in with your account
3. Toggle VPN on
4. Verify your devices appear in the device list

### 2. Configure Hosts in Termius

For each Mac you want to connect to:

1. Open Termius
2. Tap **+** → **New Host**
3. Configure:
   - **Alias**: `macmini` (or descriptive name)
   - **Hostname**: Your Mac's Tailscale hostname (e.g., `mac-mini`)
   - **Username**: Your macOS username
   - **Use SSH**: ON

4. Tap **Save**

Repeat for each device (macbook1, macbook2, etc.)

### 3. Test Connection

1. Tap on the host you created
2. If prompted about host key, tap **Continue**
3. You should see a terminal connected to your Mac

## Using Tailcode from iPhone

Once connected via Termius:

```bash
# Check device status
tc status

# Connect to another device with tmux
tc connect macmini

# Launch OpenCode
tc ai

# Launch Claude Code
tc ai --tool claude

# Wake a sleeping Mac (from an awake Mac)
tc wake macbook2
```

## Pro Tips

### Use Mosh for Better Mobile Experience

Mosh handles network switching (WiFi → cellular) without dropping your session.

1. On your Mac, install mosh: `brew install mosh`
2. In Termius host settings, enable **Mosh**

### Create Snippets for Common Commands

1. Go to **Snippets** in Termius
2. Add frequently used commands:
   - `tc ai` - Start AI coding
   - `tc status` - Check devices
   - `tmux attach -t ai` - Reattach to session

### Use the Extra Keyboard Row

Termius provides an extra keyboard row with:
- Tab, Ctrl, Esc, arrow keys
- Swipe left/right on the bar for more keys

### Quick Connect Widget

Add Termius widget to your home screen for one-tap access to favorite hosts.

## Troubleshooting

### Connection Refused

- Ensure Tailscale is connected on both devices
- Check Remote Login is enabled on Mac: **System Settings → General → Sharing → Remote Login**

### Session Drops Frequently

- Enable Mosh in host settings
- Keep Tailscale VPN always-on

### Can't Find Host

- Use Tailscale hostname, not IP
- Run `tailscale status` on Mac to verify hostname

## Limitations

- Free tier doesn't sync hosts across devices
- Background connections limited to ~30 seconds (iOS limitation)
- Use tmux to preserve work when switching apps
