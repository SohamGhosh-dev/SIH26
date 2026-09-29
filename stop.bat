@echo off
title Stop 3D Cadastre Server
echo [*] Terminating 3D Cadastre Server on port 8000...

:: Kill by designated window title
taskkill /FI "WINDOWTITLE eq CadastreServer*" /F /T >nul 2>&1

:: Kill any remaining process holding port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [✓] Server stopped and port 8000 released.
timeout /t 2 >nul
exit