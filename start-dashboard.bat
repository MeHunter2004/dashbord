@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where python >nul 2>nul || goto :missing_python
python -c "import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)" >nul 2>nul || goto :invalid_python
where npm.cmd >nul 2>nul || goto :missing_node

if not exist "backend\.venv\Scripts\python.exe" (
  echo Preparing the Python environment. This is only needed once...
  echo Creating the virtual environment...
  python -m venv backend\.venv
  if errorlevel 1 goto :venv_failed
  echo Installing backend dependencies. This can take a few minutes...
  backend\.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r backend\requirements.txt
  if errorlevel 1 goto :pip_failed
)

if not exist "frontend\node_modules" (
  echo Preparing the frontend dependencies. This is only needed once...
  call npm.cmd --prefix frontend install || goto :failed
)

for /f "tokens=4" %%I in ('route print -4 ^| findstr /R /C:"^[ ]*0.0.0.0[ ]*0.0.0.0"') do set "DASHBOARD_IP=%%I"
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
echo Python 3.11, 3.12, or 3.13 was not found.
echo Install it from https://www.python.org/downloads/windows/
echo During installation, select "Add Python to PATH", then run this file again.
pause
exit /b 1

:invalid_python
echo Python 3.11, 3.12, or 3.13 is required. Python 3.14 is not yet supported.
echo Run "python --version" to check the installed version, then run this file again.
pause
exit /b 1

:missing_node
echo Node.js 18 or newer was not found. Install it, then run this file again.
pause
exit /b 1

:venv_failed
echo Creating the Python environment failed.
echo Verify that Python 3.11, 3.12, or 3.13 is fully installed, then run this file again.
pause
exit /b 1

:pip_failed
echo Installing Python packages failed.
echo The installer could not download packages from PyPI.
echo Check the internet connection and ask IT to allow pypi.org and files.pythonhosted.org over HTTPS.
echo If your organization uses a proxy, configure it before running this file again.
pause
exit /b 1
