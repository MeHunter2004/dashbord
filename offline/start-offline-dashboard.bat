@echo off
setlocal EnableExtensions
cd /d "%~dp0"

for /f "tokens=4" %%I in ('route print -4 ^| findstr /R /C:"^[ ]*0.0.0.0[ ]*0.0.0.0"') do set "DASHBOARD_IP=%%I"
if not defined DASHBOARD_IP set "DASHBOARD_IP=127.0.0.1"
set "CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://%DASHBOARD_IP%:8000"
set "ALLOWED_HOSTS=localhost,127.0.0.1,%DASHBOARD_IP%"

netstat -ano | findstr /C:":8000 " | findstr LISTENING >nul && goto :already_running
start "Request Dashboard" /D "%CD%\backend" cmd /k "..\runtime\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo.
echo Dashboard is starting. Open one of these addresses:
echo   This computer: http://127.0.0.1:8000
echo   Phone on the same trusted Wi-Fi: http://%DASHBOARD_IP%:8000
echo.
echo Allow Python on Private networks if Windows Firewall asks.
pause
exit /b 0

:already_running
echo Port 8000 is already in use. Stop the existing dashboard first.
pause
exit /b 1
