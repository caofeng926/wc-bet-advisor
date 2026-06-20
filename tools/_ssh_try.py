import paramiko, socket

# Try via different transport
HOST = "43.136.175.219"
USER = "root"
KEY = r"C:\Users\win\Documents\2026世界杯体彩竞猜\deploy\keys\id_ed25519"

# First check connectivity
try:
    s = socket.create_connection((HOST, 22), timeout=10)
    s.close()
    print("socket OK")
except Exception as e:
    print(f"socket {type(e).__name__}: {e}")
    raise SystemExit(1)

# Try a longer SSH handshake
cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print("connecting...")
    cli.connect(HOST, username=USER, key_filename=KEY, timeout=30, allow_agent=False, look_for_keys=False, banner_timeout=30, auth_timeout=30)
    print("AUTH OK")
    sin, sout, serr = cli.exec_command("uname -a; which docker; docker compose version 2>/dev/null; docker --version 2>/dev/null")
    print(sout.read().decode())
    cli.close()
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
