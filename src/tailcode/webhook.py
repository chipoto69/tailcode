import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from tailcode.config import load_config
from tailcode.notify import notify
from tailcode.ssh import is_reachable
from tailcode.tailscale import is_peer_online
from tailcode.wol import find_wake_relay, wake_device

CONFIG = load_config()
AUTH_TOKEN = os.environ.get("TAILCODE_TOKEN", "")


class Handler(BaseHTTPRequestHandler):
    def _auth(self) -> bool:
        if not AUTH_TOKEN:
            return True
        token = self.headers.get("Authorization", "").replace("Bearer ", "")
        return token == AUTH_TOKEN

    def _json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        if self.path == "/health":
            self._json({"ok": True})
            return
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        if not self._auth():
            self._json({"error": "unauthorized"}, 401)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else "{}"
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._json({"error": "invalid json"}, 400)
            return

        if self.path == "/wake":
            name = data.get("device")
            if not name:
                self._json({"error": "device required"}, 400)
                return
            device = CONFIG.get_device(name)
            if not device:
                self._json({"error": f"unknown device: {name}"}, 404)
                return
            relay = find_wake_relay(device, CONFIG)
            result = wake_device(device, CONFIG, relay=relay)
            if result["success"]:
                notify(f"Waking {name}", config=CONFIG)
            self._json({"ok": result["success"], "method": result.get("method")})
            return

        if self.path == "/status":
            devices = []
            for name, device in CONFIG.devices.items():
                online = is_peer_online(device.hostname)
                devices.append({
                    "name": name,
                    "hostname": device.hostname,
                    "online": online,
                    "role": device.role,
                })
            self._json({"devices": devices})
            return

        if self.path == "/notify":
            msg = data.get("message")
            if not msg:
                self._json({"error": "message required"}, 400)
                return
            ok = notify(msg, title=data.get("title", "Tailcode"), config=CONFIG)
            self._json({"ok": ok})
            return

        self._json({"error": "not found"}, 404)

    def log_message(self, *args):
        pass


def run_server(host: str = "0.0.0.0", port: int = 8765):
    server = HTTPServer((host, port), Handler)
    server.serve_forever()
