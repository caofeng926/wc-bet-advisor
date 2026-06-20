@echo off
setlocal
set "WS=%~dp0.."
set "PYIO=utf-8"
set "PYUTF8=1"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
  taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
cd /D "%~dp0"
start "" .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo Backend started on http://127.0.0.1:8000
