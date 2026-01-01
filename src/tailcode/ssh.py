import subprocess

from tailcode.config import Config, Device


def build_ssh_command(
    device: Device,
    config: Config,
    command: str | None = None,
    with_session: bool = False,
) -> list[str]:
    if config.ssh.use_tailscale_ssh:
        cmd = ["tailscale", "ssh"]
    else:
        cmd = ["ssh"]

    target = f"{device.user}@{device.hostname}" if device.user else device.hostname
    cmd.append(target)

    if with_session:
        session = config.ssh.session_name
        remote_cmd = f"tmux new-session -A -s {session}"
        if command:
            remote_cmd = f"tmux new-session -A -s {session} '{command}'"
        cmd.append(remote_cmd)
    elif command:
        cmd.append(command)

    return cmd


def ssh_exec(device: Device, config: Config, command: str, timeout: int = 30) -> subprocess.CompletedProcess:
    cmd = build_ssh_command(device, config, command=command)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ssh_connect(device: Device, config: Config, with_session: bool = True) -> int:
    cmd = build_ssh_command(device, config, with_session=with_session)
    result = subprocess.run(cmd)
    return result.returncode


def is_reachable(device: Device, config: Config, timeout: int = 5) -> bool:
    try:
        result = ssh_exec(device, config, "echo ok", timeout=timeout)
        return result.returncode == 0 and "ok" in result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False
