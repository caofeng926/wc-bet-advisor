"""Probe remote server using ed25519 key."""
import paramiko, sys

HOST = "43.136.175.219"
USER = "root"
KEY = r"C:\Users\win\.ssh\wc-bet-deploy\id_ed25519"

cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cli.connect(HOST, username=USER, key_filename=KEY, timeout=20, allow_agent=False, look_for_keys=False)
print("AUTH OK")

cmds = [
    ("uname -a; cat /etc/os-release 2>/dev/null | head -8", "OS"),
    ("which docker; docker --version 2>/dev/null; docker compose version 2>/dev/null", "Docker"),
    ("ip -4 addr show 2>/dev/null | grep inet | head -5", "IPs"),
    ("ss -tlnp 2>/dev/null | head -25 || netstat -tlnp 2>/dev/null | head -25", "Listening"),
    ("systemctl is-active docker 2>/dev/null; echo ---; systemctl list-unit-files docker* 2>/dev/null | head", "docker service"),
    ("free -h | head -3; echo ---; df -h / /opt 2>/dev/null | head", "Resources"),
    ("cat /etc/ssh/sshd_config 2>/dev/null | grep -E '^[#]*(Password|Pubkey|AuthorizedKeys)' | grep -v '^#'", "sshd_config"),
    ("ls -la /root/.ssh/ 2>/dev/null", "ssh dir"),
]
for cmd, label in cmds:
    print(f"\n=== {label} ===")
    sin, sout, serr = cli.exec_command(cmd, timeout=15)
    out = sout.read().decode("utf-8", errors="replace").strip()
    err = serr.read().decode("utf-8", errors="replace").strip()
    print(out or err or "(empty)")
cli.close()
