# iPhone Setup: a-Shell

a-Shell is a local Unix terminal for iOS that also supports SSH. It's free and integrates well with Apple Shortcuts.

## Installation

1. Download [a-Shell](https://apps.apple.com/us/app/a-shell/id1473805438) from the App Store (free, ~2GB)
2. Download [Tailscale](https://apps.apple.com/us/app/tailscale/id1470499037) from the App Store (free)

## Initial Setup

### 1. Connect to Tailscale

1. Open Tailscale app
2. Sign in with your account
3. Toggle VPN on

### 2. Generate SSH Keys (First Time)

Open a-Shell and run:

```bash
ssh-keygen -t ed25519
```

Press Enter for default location and optionally set a passphrase.

### 3. Copy Public Key to Your Macs

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy this output. On each Mac, add it to `~/.ssh/authorized_keys`:

```bash
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
```

Or use Tailscale SSH (no keys needed):

```bash
tailscale ssh user@hostname
```

## Connecting to Your Macs

### Basic SSH

```bash
ssh filip@mac-mini
```

### With Tailscale SSH (Recommended)

If your Macs have Tailscale SSH enabled:

```bash
ssh mac-mini
```

### Using tmux

Always use tmux to preserve your session:

```bash
ssh mac-mini -t 'tmux new -A -s ai'
```

## Using Tailcode from a-Shell

Once connected:

```bash
tc status
tc ai
tc connect macbook1
```

## Shortcuts Integration

a-Shell's killer feature is Shortcuts integration. Create automations that:

1. Run SSH commands
2. Capture output
3. Send notifications

### Example: Wake Mac Shortcut

Create a Shortcut with:

1. **Run Command in a-Shell**:
   ```
   ssh mac-mini 'tc wake macbook2'
   ```
2. **Show Notification**: "Mac waking up..."

### Example: Quick Status Check

1. **Run Command in a-Shell**:
   ```
   ssh mac-mini 'tc status --json'
   ```
2. **Get Dictionary Value** (parse JSON)
3. **Show Result**

## Pro Tips

### Create Shell Aliases

Add to `~/.profile` in a-Shell:

```bash
alias mm='ssh mac-mini -t "tmux new -A -s ai"'
alias mb='ssh macbook-pro-1 -t "tmux new -A -s ai"'
alias ai='ssh mac-mini -t "tc ai"'
```

Then just type `mm` to connect!

### Use Screen Instead of tmux

a-Shell has limited terminal capabilities. Screen may work better:

```bash
ssh mac-mini -t 'screen -dR ai'
```

### File Transfer with scp

```bash
scp localfile.txt mac-mini:~/Documents/
scp mac-mini:~/code/file.py ./
```

## Limitations

- Terminal emulation is basic compared to Termius
- No Mosh support
- Large app size (~2GB)
- Some escape sequences don't render correctly

## When to Use a-Shell vs Termius

| Use a-Shell | Use Termius |
|-------------|-------------|
| Shortcuts automation | Day-to-day SSH |
| Local scripting | Mosh connections |
| File processing | Multiple tabs |
| Quick commands | Long coding sessions |
