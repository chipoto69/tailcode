# iPhone Setup: iSH

iSH provides a full Alpine Linux environment on iOS. It's free, lightweight, and gives you access to the `apk` package manager.

## Installation

1. Download [iSH Shell](https://apps.apple.com/us/app/ish-shell/id1436902243) from the App Store (free, ~6MB)
2. Download [Tailscale](https://apps.apple.com/us/app/tailscale/id1470499037) from the App Store (free)

## Initial Setup

### 1. Connect to Tailscale

1. Open Tailscale app
2. Sign in with your account
3. Toggle VPN on

### 2. Install SSH Client in iSH

Open iSH and run:

```bash
apk update
apk add openssh-client
```

### 3. Optional: Install Additional Tools

```bash
apk add tmux vim git curl
```

### 4. Generate SSH Keys

```bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```

Add this public key to `~/.ssh/authorized_keys` on your Macs.

## Connecting to Your Macs

### Basic SSH

```bash
ssh filip@mac-mini
```

### With tmux

```bash
ssh mac-mini -t 'tmux new -A -s ai'
```

## Using Tailcode from iSH

Once connected to your Mac:

```bash
tc status
tc ai
tc connect macbook1
```

## Pro Tips

### Install Mosh for Better Connections

```bash
apk add mosh-client
mosh filip@mac-mini -- tmux new -A -s ai
```

Note: Mosh in iSH may have compatibility issues due to the x86 emulation.

### Configure SSH

Create `~/.ssh/config`:

```bash
cat > ~/.ssh/config << 'EOF'
Host macmini
    HostName mac-mini
    User filip
    
Host macbook1
    HostName macbook-pro-1
    User filip
    
Host macbook2
    HostName macbook-pro-2
    User filip
EOF
chmod 600 ~/.ssh/config
```

Now connect with just:

```bash
ssh macmini
```

### Create Aliases

Add to `~/.profile`:

```bash
echo 'alias mm="ssh macmini -t tmux new -A -s ai"' >> ~/.profile
echo 'alias ai="ssh macmini -t tc ai"' >> ~/.profile
source ~/.profile
```

### Persist Your Setup

iSH data persists between sessions, but you can also:

1. Export your home directory via Files app
2. Sync dotfiles with git

## Performance Notes

iSH uses x86 emulation on ARM, so:

- Commands run slower than native apps
- Some complex programs may not work
- SSH/network operations are unaffected (native)

## Limitations

- Slower than native apps due to emulation
- No background execution (iOS limitation)
- Some packages may not compile/run
- Limited window support

## When to Use iSH

| Use iSH | Use Termius |
|---------|-------------|
| You want a full Linux environment | Just need SSH |
| You need `apk` packages | Best mobile UX |
| You prefer Linux CLI | Mosh support |
| Local file processing | Multiple tabs |

## Troubleshooting

### SSH Connection Slow

This is normal due to x86 emulation. The connection itself is fast, but key exchange is slower.

### Package Not Found

```bash
apk update
apk search PACKAGE_NAME
```

### Terminal Rendering Issues

Some apps render incorrectly. Try:

```bash
export TERM=xterm
```
