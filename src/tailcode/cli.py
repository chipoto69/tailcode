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
