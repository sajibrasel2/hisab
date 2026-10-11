@echo off
title Amar Hisab Billing Software
cd /d "%~dp0"
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Software closed with an error. Press any key to exit.
    pause
)
