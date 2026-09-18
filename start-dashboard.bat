@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where python >nul 2>nul || goto :missing_python
where npm.cmd >nul 2>nul || goto :missing_node

if not exist "backend\.venv\Scripts\python.exe" (
  echo Preparing the Python environment. This is only needed once...
  python -m venv backend\.venv || goto :failed
  call backend\.venv\Scripts\activate.bat
  python -m pip install -r backend\requirements.txt || goto :failed
)

if not exist "frontend\node_modules" (
  echo Preparing the frontend dependencies. This is only needed once...
  call npm.cmd --prefix frontend install || goto :failed
)

for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object {$_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown'} ^| Select-Object -First 1 -ExpandProperty IPAddress)"`) do set "DASHBOARD_IP=%%I"
if not defined DASHBOARD_IP set "DASHBOARD_IP=127.0.0.1"

netstat -ano | findstr /C:":8000 " | findstr LISTENING >nul && goto :backend_running
netstat -ano | findstr /C:":5173 " | findstr LISTENING >nul && goto :frontend_running

set "CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://%DASHBOARD_IP%:5173"
set "ALLOWED_HOSTS=localhost,127.0.0.1,%DASHBOARD_IP%"
start "Request Dashboard API" /D "%CD%\backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
start "Request Dashboard UI" /D "%CD%\frontend" cmd /k "npm.cmd run dev -- --host 0.0.0.0"

echo.
echo Dashboard is starting. Open one of these addresses:
echo   This computer: http://127.0.0.1:5173
echo   Phone on the same trusted Wi-Fi: http://%DASHBOARD_IP%:5173
echo.
echo Allow Python and Node.js on Private networks if Windows Firewall asks.
pause
exit /b 0

:backend_running
echo Port 8000 is already in use. Stop the existing backend before starting the dashboard.
pause
exit /b 1

:frontend_running
echo Port 5173 is already in use. Stop the existing frontend before starting the dashboard.
pause
exit /b 1

:missing_python
echo Python 3.11 or newer was not found. Install it, then run this file again.
pause
exit /b 1

:missing_node
echo Node.js 18 or newer was not found. Install it, then run this file again.
pause
exit /b 1

:failed
echo Setup did not finish. Review the message above and run this file again.
pause
exit /b 1
