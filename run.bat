@echo off
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 pause
