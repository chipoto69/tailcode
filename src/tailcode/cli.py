import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="tc", help="Connect to any device, anywhere")
console = Console()


def get_config():
    from tailcode.config import load_config
    return load_config()


@app.command()
def status():
    """Show all devices and their online status."""
    from tailcode.tailscale import is_peer_online

    config = get_config()
    table = Table(title="Devices")
    table.add_column("Name", style="cyan")
    table.add_column("Host", style="dim")
    table.add_column("Role")
    table.add_column("Status")
    table.add_column("WoL")

    for name, device in config.devices.items():
        online = is_peer_online(device.hostname)
        status_str = "[green]online[/green]" if online else "[dim]offline[/dim]"
        wol_str = "[green]yes[/green]" if device.can_wake else "[dim]no[/dim]"
        table.add_row(name, device.hostname, device.role, status_str, wol_str)

    console.print(table)


@app.command()
def connect(
    device_name: str = typer.Argument(None, help="Device to connect to"),
    no_session: bool = typer.Option(False, "--no-session", "-n", help="Don't attach tmux"),
    wake: bool = typer.Option(True, "--wake/--no-wake", "-w/-W", help="Auto-wake if offline"),
):
    """Connect to a device. Auto-wakes if needed."""
    from tailcode.ssh import is_reachable, ssh_connect
    from tailcode.tailscale import is_peer_online

    config = get_config()

    if device_name is None:
        device = config.get_default_device()
        if not device:
            console.print("[red]No default device configured[/red]")
            raise typer.Exit(1)
        device_name = device.name
    else:
        device = config.get_device(device_name)

    if not device:
        console.print(f"[red]Device '{device_name}' not found[/red]")
        raise typer.Exit(1)

    if not device.can_connect:
        console.print(f"[red]{device_name} is a client device, can't connect to it[/red]")
        raise typer.Exit(1)

    if not is_peer_online(device.hostname):
        if wake and device.can_wake:
            console.print(f"[yellow]{device_name} offline, waking...[/yellow]")
            _do_wake(device, config)
            _wait_for_device(device, config, timeout=60)
        else:
            console.print(f"[red]{device_name} is offline[/red]")
            raise typer.Exit(1)

    console.print(f"Connecting to [cyan]{device_name}[/cyan]...")
    exit_code = ssh_connect(device, config, with_session=not no_session)
    raise typer.Exit(exit_code)


@app.command()
def wake(device_name: str = typer.Argument(..., help="Device to wake")):
    """Send Wake-on-LAN to a device."""
    config = get_config()
    device = config.get_device(device_name)

    if not device:
        console.print(f"[red]Device '{device_name}' not found[/red]")
        raise typer.Exit(1)

    _do_wake(device, config)


@app.command()
def run(
    device_name: str = typer.Argument(..., help="Device to run command on"),
    command: str = typer.Argument(..., help="Command to execute"),
):
    """Run a command on a device."""
    from tailcode.ssh import ssh_exec

    config = get_config()
    device = config.get_device(device_name)

    if not device:
        console.print(f"[red]Device '{device_name}' not found[/red]")
        raise typer.Exit(1)

    result = ssh_exec(device, config, command)
    if result.stdout:
        console.print(result.stdout, end="")
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]", end="")
    raise typer.Exit(result.returncode)


@app.command()
def notify(
    message: str = typer.Argument(..., help="Message to send"),
    title: str = typer.Option("Tailcode", "--title", "-t"),
):
    """Send a push notification."""
    from tailcode.notify import notify as send_notify

    config = get_config()
    success = send_notify(message, title=title, config=config)
    if success:
        console.print("[green]Sent[/green]")
    else:
        console.print("[red]Failed[/red]")
        raise typer.Exit(1)


@app.command()
def serve(
    port: int = typer.Option(8765, "--port", "-p"),
):
    """Start webhook server for Shortcuts."""
    from tailcode.webhook import run_server

    console.print(f"Webhook server on [cyan]:{port}[/cyan]")
    console.print("POST /wake   {\"device\": \"name\"}")
    console.print("POST /status")
    console.print("GET  /health")
    run_server("0.0.0.0", port)


def _ai_connect(
    device_name: str | None,
    project: str | None,
    wake: bool,
    tool: str,
):
    from tailcode.ssh import ssh_connect_with_command
    from tailcode.tailscale import is_peer_online

    config = get_config()

    if device_name is None:
        device = config.get_default_device()
        if not device:
            console.print("[red]No default device configured[/red]")
            raise typer.Exit(1)
        device_name = device.name
    else:
        device = config.get_device(device_name)

    if not device:
        console.print(f"[red]Device '{device_name}' not found[/red]")
        raise typer.Exit(1)

    if not device.can_connect:
        console.print(f"[red]{device_name} is a client device, can't connect to it[/red]")
        raise typer.Exit(1)

    if not is_peer_online(device.hostname):
        if wake and device.can_wake:
            console.print(f"[yellow]{device_name} offline, waking...[/yellow]")
            _do_wake(device, config)
            _wait_for_device(device, config, timeout=60)
        else:
            console.print(f"[red]{device_name} is offline[/red]")
            raise typer.Exit(1)

    tool_cmd = tool if tool else config.preferences.default_tool
    tool_display = "Claude Code" if tool_cmd == "claude" else "OpenCode"
    
    console.print(f"Connecting to [cyan]{device_name}[/cyan] + {tool_display}...")
    
    cmd = f"cd {project} && {tool_cmd}" if project else tool_cmd
    
    exit_code = ssh_connect_with_command(device, config, cmd)
    raise typer.Exit(exit_code)


@app.command()
def ai(
    device_name: str = typer.Argument(None, help="Device to connect to"),
    project: str = typer.Option(None, "--project", "-p", help="Project directory to cd into"),
    wake: bool = typer.Option(True, "--wake/--no-wake", "-w/-W", help="Auto-wake if offline"),
    tool: str = typer.Option(None, "--tool", "-t", help="AI tool to launch: opencode (default) or claude"),
):
    """Connect to a device and launch AI coding assistant (OpenCode or Claude Code)."""
    _ai_connect(device_name, project, wake, tool or "opencode")


@app.command()
def opencode(
    device_name: str = typer.Argument(None, help="Device to connect to"),
    project: str = typer.Option(None, "--project", "-p", help="Project directory to cd into"),
    wake: bool = typer.Option(True, "--wake/--no-wake", "-w/-W", help="Auto-wake if offline"),
    tool: str = typer.Option(None, "--tool", "-t", help="AI tool to launch: opencode (default) or claude"),
):
    """Connect to a device and launch OpenCode (alias for 'tc ai')."""
    _ai_connect(device_name, project, wake, tool or "opencode")


@app.command()
def install(
    port: int = typer.Option(8765, "--port", "-p", help="Webhook server port"),
    uninstall: bool = typer.Option(False, "--uninstall", "-u", help="Remove the service"),
    show_status: bool = typer.Option(False, "--status", "-s", help="Show service status"),
):
    """Install webhook server as a launchd service (auto-starts on boot)."""
    from tailcode.install import install_service, service_status, uninstall_service

    if show_status:
        status = service_status()
        table = Table(title="Webhook Service")
        table.add_column("Property")
        table.add_column("Value")
        
        table.add_row("Installed", "[green]yes[/green]" if status["installed"] else "[dim]no[/dim]")
        table.add_row("Running", "[green]yes[/green]" if status["running"] else "[dim]no[/dim]")
        if status["pid"]:
            table.add_row("PID", str(status["pid"]))
        table.add_row("Plist", status["plist_path"])
        table.add_row("Logs", status["log_path"])
        
        console.print(table)
        return

    if uninstall:
        success, message = uninstall_service()
        if success:
            console.print(f"[green]{message}[/green]")
        else:
            console.print(f"[red]{message}[/red]")
            raise typer.Exit(1)
        return

    success, message = install_service(port=port)
    if success:
        console.print(f"[green]{message}[/green]")
        console.print(f"\nWebhook server will auto-start on boot (port {port})")
        console.print("Check status: [cyan]tc install --status[/cyan]")
        console.print("View logs: [cyan]tail -f ~/Library/Logs/tailcode/tailcode.log[/cyan]")
    else:
        console.print(f"[red]{message}[/red]")
        raise typer.Exit(1)


@app.command()
def discover(
    user: str = typer.Option("", "--user", "-u", help="Default SSH user for servers"),
    output: Path = typer.Option(None, "--output", "-o", help="Output config file path"),
    show: bool = typer.Option(False, "--show", "-s", help="Just show discovered devices"),
):
    """Discover devices from Tailscale and generate config."""
    from tailcode.discover import discover_devices, generate_config_yaml, save_discovered_config

    devices = discover_devices()
    
    if not devices:
        console.print("[red]No devices discovered. Is Tailscale running?[/red]")
        raise typer.Exit(1)
    
    if show:
        table = Table(title="Discovered Devices")
        table.add_column("Hostname", style="cyan")
        table.add_column("Name")
        table.add_column("OS")
        table.add_column("Status")
        table.add_column("Self")
        
        for d in devices:
            status = "[green]online[/green]" if d["online"] else "[dim]offline[/dim]"
            is_self = "[yellow]<- you[/yellow]" if d.get("is_self") else ""
            table.add_row(d["hostname"], d["name"], d["os"], status, is_self)
        
        console.print(table)
        return
    
    if output is None:
        output = Path.home() / ".config" / "tailcode" / "config.yaml"
    
    yaml_content = generate_config_yaml(devices, user=user)
    
    if output.exists():
        console.print(f"[yellow]Config exists: {output}[/yellow]")
        if not typer.confirm("Overwrite?"):
            console.print("Aborted")
            raise typer.Exit(0)
    
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml_content)
    
    console.print(f"[green]Config written: {output}[/green]")
    console.print(f"\nDiscovered {len(devices)} devices")
    console.print("\n[yellow]TODO:[/yellow] Edit config to add MAC addresses for Wake-on-LAN")


@app.command()
def location(
    set_location: str = typer.Argument(None, help="Location to set (e.g., east_front, west_front)"),
):
    """Show or set current location context."""
    config = get_config()
    
    if set_location:
        if set_location not in config.locations and set_location != "auto":
            available = ", ".join(config.locations.keys()) if config.locations else "none configured"
            console.print(f"[red]Unknown location: {set_location}[/red]")
            console.print(f"Available: {available}")
            raise typer.Exit(1)
        console.print(f"[green]Location set to: {set_location}[/green]")
        console.print("[dim]Note: This is informational only. Auto-detection is used for wake relay.[/dim]")
        return
    
    table = Table(title="Locations")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name")
    table.add_column("Wake Relay")
    table.add_column("Relay Status")
    
    from tailcode.tailscale import is_peer_online
    
    for name, loc in config.locations.items():
        relay_device = config.get_device(loc.wake_relay) if loc.wake_relay else None
        if relay_device:
            online = is_peer_online(relay_device.hostname)
            relay_status = "[green]online[/green]" if online else "[dim]offline[/dim]"
            relay_name = loc.wake_relay
        else:
            relay_status = "[dim]none[/dim]"
            relay_name = "-"
        table.add_row(name, loc.name, relay_name, relay_status)
    
    console.print(table)


@app.command()
def setup():
    """Interactive setup wizard for first-time configuration."""
    from pathlib import Path
    
    console.print("\n[bold cyan]Tailcode Setup Wizard[/bold cyan]\n")
    
    config_path = Path.home() / ".config" / "tailcode" / "config.yaml"
    
    if config_path.exists():
        console.print(f"[yellow]Config already exists: {config_path}[/yellow]")
        if not typer.confirm("Run setup anyway?"):
            raise typer.Exit(0)
    
    console.print("\n[bold]Step 1: Discover Tailscale devices[/bold]")
    console.print("This will find all devices on your Tailscale network.\n")
    
    from tailcode.discover import discover_devices
    
    devices = discover_devices()
    if not devices:
        console.print("[red]No devices found. Is Tailscale running?[/red]")
        console.print("Run: tailscale status")
        raise typer.Exit(1)
    
    console.print(f"[green]Found {len(devices)} devices[/green]\n")
    
    for i, d in enumerate(devices, 1):
        status = "[green]online[/green]" if d["online"] else "[dim]offline[/dim]"
        self_marker = " [yellow](this device)[/yellow]" if d.get("is_self") else ""
        console.print(f"  {i}. {d['hostname']} ({d['os']}) {status}{self_marker}")
    
    console.print("\n[bold]Step 2: Configure default user[/bold]")
    default_user = typer.prompt("SSH username for your Macs", default="")
    
    console.print("\n[bold]Step 3: Set default device[/bold]")
    console.print("Which device should be the default for 'tc connect'?")
    
    server_devices = [d for d in devices if d["os"] in ("macOS", "linux", "Linux")]
    if server_devices:
        for i, d in enumerate(server_devices, 1):
            console.print(f"  {i}. {d['hostname']}")
        
        choice = typer.prompt("Enter number", default="1")
        try:
            default_device = server_devices[int(choice) - 1]["hostname"]
        except (ValueError, IndexError):
            default_device = server_devices[0]["hostname"] if server_devices else ""
    else:
        default_device = ""
    
    console.print("\n[bold]Step 4: Notification setup (optional)[/bold]")
    console.print("Tailcode can send push notifications via ntfy.sh")
    setup_ntfy = typer.confirm("Set up notifications?", default=False)
    
    ntfy_topic = ""
    if setup_ntfy:
        ntfy_topic = typer.prompt("ntfy topic name", default=f"tailcode-{default_user or 'alerts'}")
    
    console.print("\n[bold]Step 5: Generate config[/bold]")
    
    from tailcode.discover import generate_config_yaml
    
    yaml_content = generate_config_yaml(devices, user=default_user)
    
    if ntfy_topic:
        yaml_content = yaml_content.replace('topic: "tailcode-alerts"', f'topic: "{ntfy_topic}"')
    
    if default_device:
        yaml_content = yaml_content.replace('default_device: ""', f'default_device: "{default_device}"')
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml_content)
    
    console.print(f"\n[green]Config saved: {config_path}[/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit config to add MAC addresses for Wake-on-LAN")
    console.print("  2. Run [cyan]tc status[/cyan] to verify devices")
    console.print("  3. Run [cyan]tc connect[/cyan] to test connection")
    console.print("  4. Run [cyan]tc install[/cyan] to set up webhook server")


def _do_wake(device, config):
    from tailcode.notify import notify
    from tailcode.wol import find_wake_relay, wake_device

    if not device.can_wake:
        console.print(f"[red]{device.name} has no MAC address configured[/red]")
        raise typer.Exit(1)

    relay = find_wake_relay(device, config)
    if relay:
        console.print(f"Waking [cyan]{device.name}[/cyan] via [dim]{relay.name}[/dim]...")
    else:
        console.print(f"Waking [cyan]{device.name}[/cyan] (local broadcast)...")

    result = wake_device(device, config, relay=relay)

    if result["success"]:
        console.print(f"[green]WoL sent[/green] ({result['method']})")
        if config.preferences.auto_wake:
            notify(f"Waking {device.name}", config=config)
    else:
        console.print(f"[red]Failed: {result.get('error')}[/red]")
        raise typer.Exit(1)


def _wait_for_device(device, config, timeout: int = 60):
    from tailcode.ssh import is_reachable

    console.print(f"Waiting for [cyan]{device.name}[/cyan]...", end="")
    start = time.time()
    while time.time() - start < timeout:
        if is_reachable(device, config):
            console.print(" [green]ready[/green]")
            return
        console.print(".", end="")
        time.sleep(3)
    console.print(" [red]timeout[/red]")
    raise typer.Exit(1)


if __name__ == "__main__":
    app()
