"""Launch xray detached with config."""
import subprocess, time, os, sys
deploy = r"C:\Users\win\Documents\2026世界杯体彩竞猜\deploy"
xray = r"D:\v2rayN-windows-64-desktop\v2rayN-windows-64\bin\xray\xray.exe"
cfg = os.path.join(deploy, "xray-proxy.json")
log_out = os.path.join(deploy, "xray-out.log")
log_err = os.path.join(deploy, "xray-err.log")

# Kill old
subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq xray-proxy*"], capture_output=True)
time.sleep(1)

DETACHED_PROCESS = 0x00000008
CREATE_NO_WINDOW = 0x08000000

fout = open(log_out, "wb")
ferr = open(log_err, "wb")
proc = subprocess.Popen(
    [xray, "run", "-c", cfg],
    cwd=deploy,
    stdin=subprocess.DEVNULL,
    stdout=fout,
    stderr=ferr,
    creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
    close_fds=True,
)
print(f"started PID {proc.pid}")
time.sleep(3)
print("poll:", proc.poll())
