@echo off
REM VulnoraIQ browser GUI double-click launcher for Windows.
cd /d "%~dp0"
echo Starting VulnoraIQ browser GUI on http://127.0.0.1:8787 ...
echo This launcher creates or reuses .venv, installs VulnoraIQ locally, and opens the WebUI.
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py scripts\bootstrap_launch.py %*
) else (
  python scripts\bootstrap_launch.py %*
)
echo VulnoraIQ WebUI launcher has stopped.
pause
