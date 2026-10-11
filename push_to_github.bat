@echo off
title Push Amar Hisab to GitHub
cd /d "%~dp0"
echo ==============================================
echo Pushing Amar Hisab to https://github.com/sajibrasel2/hisab
echo ==============================================
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ==============================================
    echo [SUCCESS] Code successfully pushed to GitHub!
    echo Repository: https://github.com/sajibrasel2/hisab
    echo ==============================================
) else (
    echo [NOTICE] If prompted, please sign in with GitHub in your browser.
)
echo.
pause
