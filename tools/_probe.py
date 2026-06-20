"""Probe remote server: OS, Docker availability, ports, existing services."""
import paramiko, sys, re

HOST, USER, PWD = "43.136.175.219", "root", "2Vbrm5ah"

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, password=PWD, timeout=20, allow_agent=False, look_for_keys=False)

cmds = [
    ("uname -a", "OS / kernel"),
    ("cat /etc/os-release 2>/dev/null | head -10", "OS release"),
    ("which docker; docker --version 2>/dev/null", "docker"),
    ("which docker-compose; docker-compose --version 2>/dev/null; docker compose version 2>/dev/null", "compose"),
    ("ip addr show 2>/dev/null | grep -E 'inet |state UP' | head -10", "network"),
    ("ss -tlnp 2>/dev/null | head -20 || netstat -tlnp 2>/dev/null | head -20", "ports"),
    ("systemctl is-active docker 2>/dev/null", "docker service"),
    ("free -h; df -h /", "resources"),
]
for cmd, label in cmds:
    print(f"\n=== {label} ===")
    sin, sout, serr = cli.exec_command(cmd, timeout=10)
    out = sout.read().decode("utf-8", errors="replace").strip()
    err = serr.read().decode("utf-8", errors="replace").strip()
    print(out or err or "(empty)")
cli.close()
