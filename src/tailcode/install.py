"""Launchd service management for webhook server."""
import os
import subprocess
import sys
from pathlib import Path

PLIST_NAME = "com.tailcode.webhook.plist"
PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tailcode.webhook</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>-m</string>
        <string>tailcode.cli</string>
        <string>serve</string>
        <string>--port</string>
        <string>{port}</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>{log_dir}/tailcode.log</string>
    
    <key>StandardErrorPath</key>
    <string>{log_dir}/tailcode.error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
"""


def get_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / PLIST_NAME


def get_log_dir() -> Path:
    log_dir = Path.home() / "Library" / "Logs" / "tailcode"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def generate_plist(port: int = 8765) -> str:
    python_path = sys.executable
    log_dir = get_log_dir()
    return PLIST_TEMPLATE.format(
        python_path=python_path,
        port=port,
        log_dir=log_dir,
    )


def install_service(port: int = 8765) -> tuple[bool, str]:
    """Install launchd service for webhook server."""
    plist_path = get_plist_path()
    
    # Unload existing if present
    if plist_path.exists():
        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True,
        )
    
    # Write new plist
    plist_content = generate_plist(port)
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(plist_content)
    
    # Load service
    result = subprocess.run(
        ["launchctl", "load", str(plist_path)],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        return False, f"Failed to load: {result.stderr}"
    
    return True, f"Installed and started: {plist_path}"


def uninstall_service() -> tuple[bool, str]:
    """Uninstall launchd service."""
    plist_path = get_plist_path()
    
    if not plist_path.exists():
        return False, "Service not installed"
    
    # Unload
    result = subprocess.run(
        ["launchctl", "unload", str(plist_path)],
        capture_output=True,
        text=True,
    )
    
    # Remove plist
    plist_path.unlink()
    
    return True, "Service uninstalled"


def service_status() -> dict:
    """Check if service is running."""
    plist_path = get_plist_path()
    log_dir = get_log_dir()
    
    status = {
        "installed": plist_path.exists(),
        "plist_path": str(plist_path),
        "log_path": str(log_dir / "tailcode.log"),
        "running": False,
        "pid": None,
    }
    
    if not status["installed"]:
        return status
    
    # Check if running
    result = subprocess.run(
        ["launchctl", "list", "com.tailcode.webhook"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        status["running"] = True
        # Parse PID from output
        lines = result.stdout.strip().split("\n")
        for line in lines:
            parts = line.split("\t")
            if len(parts) >= 1 and parts[0].isdigit():
                status["pid"] = int(parts[0])
    
    return status
