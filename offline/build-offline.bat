@echo off
setlocal EnableExtensions
cd /d "%~dp0\.."

if not exist "backend\.venv\Scripts\python.exe" goto :missing_environment
call npm.cmd --prefix frontend run build || goto :failed

if exist offline\package rmdir /s /q offline\package
mkdir offline\package\EDR-Dashboard-Offline\backend
mkdir offline\package\EDR-Dashboard-Offline\frontend
mkdir offline\package\EDR-Dashboard-Offline\backend\data
mkdir offline\package\EDR-Dashboard-Offline\runtime

for /f "usebackq delims=" %%I in (`backend\.venv\Scripts\python.exe -c "import sys; print(sys.base_prefix)"`) do set "BASE_PYTHON=%%I"
if not defined BASE_PYTHON goto :failed

robocopy "%BASE_PYTHON%" "offline\package\EDR-Dashboard-Offline\runtime" *.exe *.dll /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
robocopy "%BASE_PYTHON%\DLLs" "offline\package\EDR-Dashboard-Offline\runtime\DLLs" /e /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
robocopy "%BASE_PYTHON%\Lib" "offline\package\EDR-Dashboard-Offline\runtime\Lib" /e /xd site-packages /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
robocopy "backend\.venv\Lib\site-packages" "offline\package\EDR-Dashboard-Offline\runtime\Lib\site-packages" /e /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
robocopy "backend\app" "offline\package\EDR-Dashboard-Offline\backend\app" /e /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
robocopy "frontend\dist" "offline\package\EDR-Dashboard-Offline\frontend\dist" /e /nfl /ndl /njh /njs
if errorlevel 8 goto :failed
copy /y offline\start-offline-dashboard.bat offline\package\EDR-Dashboard-Offline\start-dashboard.bat >nul
copy /y offline\PACKAGE-README.md offline\package\EDR-Dashboard-Offline\README.md >nul

echo.
echo Offline package created at offline\package\EDR-Dashboard-Offline
echo Copy the customer's Excel file into backend\data before delivery.
pause
exit /b 0

:missing_environment
echo The development Python environment is missing. Run the normal project setup first.
pause
exit /b 1

:failed
echo Offline package build failed. Review the message above.
pause
exit /b 1
