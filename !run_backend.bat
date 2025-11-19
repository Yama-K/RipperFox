@echo off
setlocal
title RipperFox Backend

where python >nul 2>&1
if errorlevel 1 (
    echo Installing Python via winget...
    winget install -e --id Python.Python.3.13
)

set BASEDIR=%~dp0
set PYTHON_INSTALL=%BASEDIR%python_install.bat
set SITE_PACKAGES=%BASEDIR%python\Lib\site-packages
set REQ_FILE=%BASEDIR%requirements.txt

echo ================================================
echo   RipperFox Backend Launcher
echo ================================================
echo.

REM ---- Verify local site-packages ----
if not exist "%SITE_PACKAGES%" (
    echo [!] Python dependencies not installed.
    call "%PYTHON_INSTALL%"
)

REM ---- Use local python path for this session ----
set PYTHONPATH=%SITE_PACKAGES%

REM ---- Verify dependencies ----
echo [*] Checking Python dependencies...
python -c "import sys; sys.path.insert(0, r'%SITE_PACKAGES%'); import flask, flask_cors, colorama, yt_dlp, ffmpeg, pystray, PIL" >nul 2>&1
if errorlevel 1 (
    echo [!] Missing dependencies detected.
    call "%PYTHON_INSTALL%"
)

REM ---- Launch backend using system tray ----
echo.
echo Starting RipperFox backend in system tray...
python "%BASEDIR%tray_icon.py"