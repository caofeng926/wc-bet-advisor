import subprocess, time, os
ws = r"C:\Users\win\Documents\2026世界杯体彩竞猜"
DETACHED = 0x00000008
p = subprocess.Popen(
    [r"C:\Program Files\nodejs\node.exe", os.path.join(ws, "tools/serve.js")],
    cwd=ws,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=DETACHED,
    close_fds=True,
)
print(f"server PID={p.pid}")
time.sleep(3)
print("poll:", p.poll())
