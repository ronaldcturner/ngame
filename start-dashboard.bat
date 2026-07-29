@echo off
REM NGAME dashboard auto-start — place at repository root (ships with the repo).
REM Double-click to test; Task Scheduler should run this file at logon.
cd /d "%~dp0"
if not exist "logs" mkdir logs
cd /d "%~dp0ngame_ui"
"%~dp0.venv\Scripts\pythonw.exe" app-simple.py >> "%~dp0logs\dashboard.log" 2>> "%~dp0logs\dashboard.err.log"
