@echo off
cd /d "%~dp0"
title 3D Cadastre Enterprise Launcher

echo [*] Starting 3D Cadastre HTTP Server on port 8000...

:: Kill existing process on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start background server
start "CadastreServer" /min python -m http.server 8000
timeout /t 2 /nobreak >nul

echo [*] Opening Cadastre Role Access Portal...
start http://localhost:8000/index.html

echo [✓] System live at http://localhost:8000/index.html
exit