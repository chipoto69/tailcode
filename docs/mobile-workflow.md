# Mobile Workflow for Claude Code / OpenCode

Run AI coding assistants from your phone, anywhere.

## Prerequisites

- Tailscale account with devices configured
- Server with Claude Code or OpenCode installed
- Mobile device with Tailscale app

## Mobile SSH Client Setup

### iOS: Blink Shell (Recommended)
- Native Mosh support (survives network changes)
- Tailscale integration built-in
- Excellent keyboard support

### Android: Termux + Mosh
```bash
pkg install mosh openssh
```

### Cross-Platform: Termius
- Cloud-synced connections
- Snippet library for common commands

## Connection Flow

### Option 1: Direct SSH (Simple)
```bash
# From mobile terminal
tailscale ssh user@hostname
tmux new -A -s ai-coding
claude  # or opencode
```

### Option 2: Mosh (Better for Mobile)
```bash
# On server: install mosh
sudo apt install mosh

# From mobile (Blink Shell)
mosh user@hostname.tailnet-name.ts.net -- tmux new -A -s ai-coding
```

### Option 3: Full Boot Cycle (Best)
```bash
# Using tailcode CLI
tailcode boot homeserver
# Wakes machine -> waits for boot -> connects to tmux session
```

## Why tmux is Mandatory

Mobile connections drop. Tunnels, elevators, network switches. Without tmux:
- Connection drops = process dies = lost work

With tmux:
- Connection drops = reconnect and continue
- AI keeps working while you're disconnected

## Recommended tmux Config

Add to `~/.tmux.conf` on your server:

```bash
# Visible status bar
set -g status on
set -g status-interval 5
set -g status-left '[#S] '
set -g status-right '%H:%M'

# Mouse support (helps on mobile)
set -g mouse on

# Larger history
set -g history-limit 50000

# Easy window switching
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
```

## Workflow Tips

### 1. Use Snippets
Store common commands in your SSH client's snippet library:
- `tmux new -A -s ai-coding`
- `opencode --model claude-3-5-sonnet`

### 2. Prefer Faster Models for Mobile
Less back-and-forth = better mobile experience:
- Use Claude 3.5 Sonnet for complex tasks
- Use Haiku for quick fixes

### 3. Set Up Notifications
Get notified when long tasks complete:
```bash
# After a long build
tailcode notify "Build complete"
```

### 4. Use OpenCode's Session Persistence
OpenCode maintains sessions. If you disconnect and reconnect:
```bash
opencode  # Resumes your session
```

## Quick Reference

| Task | Command |
|------|---------|
| Wake + Connect | `tailcode boot server` |
| Just Connect | `tailcode ssh server -s` |
| Check Status | `tailcode ping server` |
| Notify Phone | `tailcode notify "Done"` |
| List Devices | `tailcode devices` |

## Troubleshooting

### Connection Drops Constantly
Use Mosh instead of SSH. It's designed for unreliable networks.

### Can't Wake Machine
1. Check WoL enabled in BIOS
2. Check `ethtool eth0 | grep Wake-on` shows `g`
3. Ensure bridge device (Pi) is on same LAN as target

### Tailscale Not Connecting
1. Check Tailscale app is running on phone
2. Try `tailscale status` on server
3. Check ACLs in Tailscale admin console
