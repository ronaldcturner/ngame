@echo off
REM NGAME dashboard auto-start — place at repository root (ships with the repo).
REM Double-click to test; for login auto-start prefer start-dashboard-silent.vbs in shell:startup.
cd /d "%~dp0"
if not exist "logs" mkdir logs
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0ngame_ui"
"%~dp0.venv\Scripts\pythonw.exe" app-simple.py >> "%~dp0logs\dashboard.log" 2>> "%~dp0logs\dashboard.err.log"
