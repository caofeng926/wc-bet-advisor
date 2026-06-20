@echo off
cd /D C:\Users\win\Documents\2026世界杯体彩竞猜\backend
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a
timeout /t 2 >nul
start "" .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
echo Backend restarted on port 8000