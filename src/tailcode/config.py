from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

Role = Literal["server", "client"]


@dataclass
class Device:
    name: str
    hostname: str
    user: str = ""
    mac: str | None = None
    role: Role = "server"
    location: str = ""
    always_on: bool = False

    @property
    def can_wake(self) -> bool:
        return self.mac is not None and self.role == "server"

    @property
    def can_connect(self) -> bool:
        return self.role == "server"
    
    @property
    def is_wake_relay(self) -> bool:
        return self.always_on and self.role == "server"


@dataclass
class TailscaleConfig:
    api_key: str = ""
    tailnet: str = "-"


@dataclass
class NtfyConfig:
    server: str = "https://ntfy.sh"
    topic: str = "tailcode-alerts"


@dataclass
class NotificationConfig:
    provider: str = "ntfy"
    ntfy: NtfyConfig = field(default_factory=NtfyConfig)


@dataclass
class SSHConfig:
    use_tailscale_ssh: bool = True
    session_name: str = "ai"


@dataclass
class Location:
    name: str
    wake_relay: str | None = None


@dataclass
class Preferences:
    default_device: str = ""
    default_tool: str = "opencode"
    auto_wake: bool = True


@dataclass
class Config:
    tailscale: TailscaleConfig = field(default_factory=TailscaleConfig)
    devices: dict[str, Device] = field(default_factory=dict)
    locations: dict[str, Location] = field(default_factory=dict)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    ssh: SSHConfig = field(default_factory=SSHConfig)
    preferences: Preferences = field(default_factory=Preferences)

    def get_device(self, name: str) -> Device | None:
        return self.devices.get(name)

    def get_servers(self) -> list[Device]:
        return [d for d in self.devices.values() if d.role == "server"]

    def get_default_device(self) -> Device | None:
        if self.preferences.default_device:
            return self.get_device(self.preferences.default_device)
        servers = self.get_servers()
        return servers[0] if servers else None
    
    def get_location(self, name: str) -> Location | None:
        return self.locations.get(name)
    
    def get_wake_relay_for_location(self, location: str) -> Device | None:
        loc = self.get_location(location)
        if loc and loc.wake_relay:
            return self.get_device(loc.wake_relay)
        for device in self.devices.values():
            if device.location == location and device.is_wake_relay:
                return device
        return None


def _parse_device(name: str, data: dict[str, Any]) -> Device:
    return Device(
        name=name,
        hostname=data.get("hostname", name),
        user=data.get("user", ""),
        mac=data.get("mac"),
        role=data.get("role", "server"),
        location=data.get("location", ""),
        always_on=data.get("always_on", False),
    )


def _parse_location(name: str, data: dict[str, Any]) -> Location:
    return Location(
        name=data.get("name", name),
        wake_relay=data.get("wake_relay"),
    )


def _parse_config(data: dict[str, Any]) -> Config:
    ts_data = data.get("tailscale", {})
    tailscale = TailscaleConfig(
        api_key=ts_data.get("api_key", ""),
        tailnet=ts_data.get("tailnet", "-"),
    )

    devices = {}
    for name, dev_data in data.get("devices", {}).items():
        devices[name] = _parse_device(name, dev_data)

    locations = {}
    for name, loc_data in data.get("locations", {}).items():
        locations[name] = _parse_location(name, loc_data)

    notif_data = data.get("notifications", {})
    ntfy_data = notif_data.get("ntfy", {})
    notifications = NotificationConfig(
        provider=notif_data.get("provider", "ntfy"),
        ntfy=NtfyConfig(
            server=ntfy_data.get("server", "https://ntfy.sh"),
            topic=ntfy_data.get("topic", "tailcode-alerts"),
        ),
    )

    ssh_data = data.get("ssh", {})
    ssh = SSHConfig(
        use_tailscale_ssh=ssh_data.get("use_tailscale_ssh", True),
        session_name=ssh_data.get("session_name", "ai"),
    )

    pref_data = data.get("preferences", {})
    preferences = Preferences(
        default_device=pref_data.get("default_device", ""),
        default_tool=pref_data.get("default_tool", "opencode"),
        auto_wake=pref_data.get("auto_wake", True),
    )

    return Config(
        tailscale=tailscale,
        devices=devices,
        locations=locations,
        notifications=notifications,
        ssh=ssh,
        preferences=preferences,
    )


def load_config(path: Path | str | None = None) -> Config:
    if path is None:
        search_paths = [
            Path.cwd() / "config" / "config.yaml",
            Path.cwd() / "config.yaml",
            Path.home() / ".config" / "tailcode" / "config.yaml",
        ]
        for p in search_paths:
            if p.exists():
                path = p
                break

    if path is None:
        return Config()

    path = Path(path)
    if not path.exists():
        return Config()

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return _parse_config(data)
