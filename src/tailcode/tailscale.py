import subprocess
from dataclasses import dataclass

import httpx

from tailcode.config import Config


@dataclass
class TailscaleDevice:
    id: str
    hostname: str
    name: str
    addresses: list[str]
    os: str
    online: bool
    last_seen: str
    tags: list[str]

    @property
    def ip(self) -> str | None:
        return self.addresses[0] if self.addresses else None

    @property
    def is_mac(self) -> bool:
        return "darwin" in self.os.lower() or "macos" in self.os.lower()


class TailscaleAPI:
    def __init__(self, config: Config):
        self.api_key = config.tailscale.api_key
        self.tailnet = config.tailscale.tailnet
        self.base_url = "https://api.tailscale.com/api/v2"

    def _request(self, method: str, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        with httpx.Client() as client:
            response = client.request(
                method,
                url,
                auth=(self.api_key, ""),
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    def list_devices(self) -> list[TailscaleDevice]:
        data = self._request("GET", f"/tailnet/{self.tailnet}/devices")
        devices = []
        for d in data.get("devices", []):
            devices.append(
                TailscaleDevice(
                    id=d.get("id", ""),
                    hostname=d.get("hostname", ""),
                    name=d.get("name", ""),
                    addresses=d.get("addresses", []),
                    os=d.get("os", ""),
                    online=d.get("online", False),
                    last_seen=d.get("lastSeen", ""),
                    tags=d.get("tags", []),
                )
            )
        return devices

    def find_device(self, hostname: str) -> TailscaleDevice | None:
        devices = self.list_devices()
        for device in devices:
            if device.hostname == hostname or device.name.startswith(hostname):
                return device
        return None

    def get_online_devices(self) -> list[TailscaleDevice]:
        return [d for d in self.list_devices() if d.online]


def get_local_tailscale_ip() -> str | None:
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def get_tailscale_status() -> dict | None:
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def is_peer_online(hostname: str) -> bool:
    status = get_tailscale_status()
    if not status:
        return False
    
    peers = status.get("Peer", {})
    for peer_info in peers.values():
        peer_hostname = peer_info.get("HostName", "")
        if hostname in peer_hostname or peer_hostname in hostname:
            return peer_info.get("Online", False)
    return False
