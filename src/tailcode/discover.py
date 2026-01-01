"""Auto-discovery of Tailscale devices."""
import json
from pathlib import Path

from tailcode.config import Config, Device, load_config
from tailcode.tailscale import get_tailscale_status


def discover_devices() -> list[dict]:
    """Discover all devices from Tailscale network."""
    status = get_tailscale_status()
    if not status:
        return []
    
    devices = []
    
    # Add self
    self_info = status.get("Self", {})
    if self_info:
        devices.append({
            "hostname": self_info.get("HostName", ""),
            "name": self_info.get("DNSName", "").split(".")[0],
            "ip": self_info.get("TailscaleIPs", [""])[0],
            "os": self_info.get("OS", ""),
            "online": True,
            "is_self": True,
        })
    
    # Add peers
    peers = status.get("Peer", {})
    for peer_id, peer in peers.items():
        devices.append({
            "hostname": peer.get("HostName", ""),
            "name": peer.get("DNSName", "").split(".")[0],
            "ip": peer.get("TailscaleIPs", [""])[0] if peer.get("TailscaleIPs") else "",
            "os": peer.get("OS", ""),
            "online": peer.get("Online", False),
            "is_self": False,
        })
    
    return devices


def guess_role(device: dict) -> str:
    """Guess device role based on OS."""
    os_name = device.get("os", "").lower()
    hostname = device.get("hostname", "").lower()
    
    # iOS/iPadOS devices are clients
    if "ios" in os_name or "ipad" in hostname or "iphone" in hostname:
        return "client"
    
    # macOS devices are servers (can SSH to them)
    if "darwin" in os_name or "macos" in os_name or "mac" in hostname:
        return "server"
    
    # Linux is usually a server
    if "linux" in os_name:
        return "server"
    
    # Windows could be either, default to client
    if "windows" in os_name:
        return "client"
    
    return "server"


def generate_config_yaml(devices: list[dict], user: str = "") -> str:
    """Generate YAML config from discovered devices."""
    lines = [
        "# Auto-generated Tailcode config",
        "# Review and customize as needed",
        "",
        "devices:",
    ]
    
    server_devices = []
    
    for device in devices:
        hostname = device.get("hostname", "")
        name = device.get("name", hostname).replace("-", "").replace("_", "").lower()
        
        # Skip empty hostnames
        if not hostname:
            continue
        
        role = guess_role(device)
        
        lines.append(f"  {name}:")
        lines.append(f'    hostname: "{hostname}"')
        
        if role == "server" and user:
            lines.append(f'    user: "{user}"')
        
        lines.append(f"    role: {role}")
        
        if role == "server":
            lines.append('    mac: ""  # Fill in for Wake-on-LAN')
            server_devices.append(name)
        
        # Add location hint for macOS
        if "darwin" in device.get("os", "").lower():
            lines.append('    location: ""  # home, office, mobile, etc.')
        
        lines.append("")
    
    lines.extend([
        "preferences:",
        f"  default_device: {server_devices[0] if server_devices else ''}",
        "  auto_wake: true",
        "",
        "ssh:",
        "  use_tailscale_ssh: true",
        '  session_name: "ai"',
        "",
        "notifications:",
        "  provider: ntfy",
        "  ntfy:",
        '    server: "https://ntfy.sh"',
        '    topic: "tailcode-alerts"  # Change this!',
    ])
    
    return "\n".join(lines)


def merge_discovered_devices(config: Config, discovered: list[dict]) -> dict[str, Device]:
    """Merge discovered devices with existing config, preserving user customizations."""
    merged = dict(config.devices)
    
    for device in discovered:
        hostname = device.get("hostname", "")
        name = device.get("name", hostname).replace("-", "").replace("_", "").lower()
        
        if not hostname:
            continue
        
        # Check if already exists by hostname
        existing = None
        for existing_name, existing_device in merged.items():
            if existing_device.hostname == hostname:
                existing = existing_device
                break
        
        if existing:
            # Keep existing config, device already known
            continue
        
        # Add new device
        role = guess_role(device)
        merged[name] = Device(
            name=name,
            hostname=hostname,
            user="",
            mac=None,
            role=role,
            location="",
        )
    
    return merged


def save_discovered_config(output_path: Path, user: str = "") -> tuple[bool, str, int]:
    """Discover devices and save to config file."""
    devices = discover_devices()
    
    if not devices:
        return False, "No devices discovered. Is Tailscale running?", 0
    
    yaml_content = generate_config_yaml(devices, user=user)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_content)
    
    return True, str(output_path), len(devices)
