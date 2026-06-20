import subprocess, time, os, sys

# Detach Vite via Python subprocess so it survives the shell
ws = r"C:\Users\win\Documents\2026世界杯体彩竞猜"
preview = os.path.join(ws, "preview")
log_out = os.path.join(preview, "dev.log")
log_err = os.path.join(preview, "dev.err.log")

# Kill any existing vite processes
subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True)
time.sleep(1)

node_exe = r"C:\Program Files\nodejs\node.exe"
vite_js = os.path.join(preview, "node_modules", "vite", "bin", "vite.js")

# Open log files
fout = open(log_out, "w", encoding="utf-8")
ferr = open(log_err, "w", encoding="utf-8")

# Use DETACHED_PROCESS to truly detach from parent
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
proc = subprocess.Popen(
    [node_exe, vite_js],
    cwd=preview,
    stdout=fout,
    stderr=ferr,
    stdin=subprocess.DEVNULL,
    creationflags=flags,
    close_fds=True,
)
print(f"Started Vite PID={proc.pid}")
time.sleep(6)

# Check if still alive
if proc.poll() is None:
    print("Process is running")
else:
    print(f"Process exited with code {proc.returncode}")
