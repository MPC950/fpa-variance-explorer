@echo off
setlocal
cd /d "%~dp0"
set "fpa_python=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%fpa_python%" (
  "%fpa_python%" analyze.py --open
  if errorlevel 1 pause
  exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 analyze.py --open
  if errorlevel 1 (
    echo See README.md to install the required Python packages.
    pause
  )
  exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
  python analyze.py --open
  if errorlevel 1 (
    echo See README.md to install the required Python packages.
    pause
  )
  exit /b
)
echo Python was not found. See README.md for setup, or open report\variance_report.html to view the completed analysis.
pause
