import paramiko, socket

HOST, USER, PWD = "43.136.175.219", "root", "2Vbrm5ah"
KEY = r"C:\Users\win\Documents\2026世界杯体彩竞猜\deploy\keys\id_ed25519"

# Test socket
try:
    s = socket.create_connection((HOST, 22), timeout=8)
    s.close()
    print("socket OK")
except Exception as e:
    print(f"socket {type(e).__name__}")
    raise SystemExit(1)

# Try key
cli = paramiko.SSHClient()
cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for label, kw in [
    ("key_only", dict(key_filename=KEY, password=None, allow_agent=False, look_for_keys=False)),
    ("pwd_only", dict(key_filename=None, password=PWD, allow_agent=False, look_for_keys=False)),
    ("both",     dict(key_filename=KEY, password=PWD, allow_agent=False, look_for_keys=False)),
]:
    cli2 = paramiko.SSHClient()
    cli2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        cli2.connect(HOST, username=USER, timeout=15, **kw)
        print(f"AUTH OK [{label}]")
        sin, sout, serr = cli2.exec_command("uname -a; which docker; docker compose version 2>/dev/null; docker --version 2>/dev/null", timeout=15)
        print(sout.read().decode())
        cli2.close()
        raise SystemExit(0)
    except Exception as e:
        print(f"[{label}] FAIL: {type(e).__name__}: {e}")
        try: cli2.close()
        except: pass
