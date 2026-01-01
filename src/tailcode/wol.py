import socket
import struct
import subprocess

from tailcode.config import Config, Device


def create_magic_packet(mac: str) -> bytes:
    mac_clean = mac.replace(":", "").replace("-", "").replace(".", "")
    if len(mac_clean) != 12:
        raise ValueError(f"Invalid MAC address: {mac}")
    mac_bytes = bytes.fromhex(mac_clean)
    return b"\xff" * 6 + mac_bytes * 16


def send_wol_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> bool:
    try:
        packet = create_magic_packet(mac)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, (broadcast, port))
        return True
    except Exception:
        return False


def send_wol_via_ssh(
    mac: str,
    relay_host: str,
    relay_user: str,
    use_tailscale_ssh: bool = True,
) -> dict:
    wol_cmd = f"python3 -c \"import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1); s.sendto(b'\\\\xff'*6+bytes.fromhex('{mac.replace(':','')}')*16,('255.255.255.255',9)); print('sent')\""
    
    if use_tailscale_ssh:
        cmd = ["tailscale", "ssh", f"{relay_user}@{relay_host}", wol_cmd]
    else:
        cmd = ["ssh", f"{relay_user}@{relay_host}", wol_cmd]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def wake_device(device: Device, config: Config, relay: Device | None = None) -> dict:
    if not device.mac:
        return {"success": False, "error": "No MAC address configured", "method": None}

    if relay:
        result = send_wol_via_ssh(
            mac=device.mac,
            relay_host=relay.hostname,
            relay_user=relay.user,
            use_tailscale_ssh=config.ssh.use_tailscale_ssh,
        )
        result["method"] = f"relay:{relay.name}"
        return result

    success = send_wol_packet(device.mac)
    return {
        "success": success,
        "method": "local" if success else None,
        "error": None if success else "Failed to send WoL packet",
    }


def find_wake_relay(target: Device, config: Config) -> Device | None:
    from tailcode.tailscale import is_peer_online
    
    for device in config.get_servers():
        if device.name == target.name:
            continue
        if device.location == target.location and is_peer_online(device.hostname):
            return device
    return None
