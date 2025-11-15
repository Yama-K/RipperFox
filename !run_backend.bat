@echo off
setlocal
title RipperFox Backend

eho "Installing python via winget"
winget install Python.Python.3.13

set BASEDIR=%~dp0
set PYTHON_EXE=%BASEDIR%python\python.exe
set PYTHON_INSTALL=%BASEDIR%python_install.bat
set SITE_PACKAGES=%BASEDIR%python\Lib\site-packages
set REQ_FILE=%BASEDIR%requirements.txt
set FFMPEG_EXE=%BASEDIR%ffmpeg\ffmpeg.exe
set FFMPEG_INSTALL=%BASEDIR%ffmpeg_install.bat

echo ================================================
echo   RipperFox Backend Launcher
echo ================================================
echo.

REM ---- Verify Python exists ----
if not exist "%PYTHON_EXE%" (
    echo [!] python.exe not found in "python" folder.
    pause
    exit /b
)

REM ---- Verify local site-packages ----
if not exist "%SITE_PACKAGES%" (
    echo [!] Python dependencies not installed.
    call "%PYTHON_INSTALL%"
)

REM ---- Use local python path for this session ----
set PYTHONPATH=%SITE_PACKAGES%

REM ---- Verify dependencies ----
echo [*] Checking Python dependencies...
"%PYTHON_EXE%" -c "import sys; sys.path.insert(0, r'%SITE_PACKAGES%'); import flask, flask_cors, colorama" >nul 2>&1
if errorlevel 1 (
    echo [!] Missing dependencies detected.
    call "%PYTHON_INSTALL%"
)

REM ---- Verify FFmpeg ----
if not exist "%FFMPEG_EXE%" (
    echo [!] FFmpeg not found.
    choice /M "Download and install FFmpeg automatically?"
    if errorlevel 2 (
        echo Skipping FFmpeg installation.
    ) else (
        call "%FFMPEG_INSTALL%"
    )
)

REM ---- Verify yt-dlp ----
if not exist "%BASEDIR%yt-dlp\yt-dlp.exe" (
    echo [!] yt-dlp not found.
    choice /M "Download yt-dlp automatically?"
    if errorlevel 2 (
        echo Skipping yt-dlp installation.
    ) else (
        call "%BASEDIR%yt_dlp_install.bat"
    )
)

REM ---- Launch backend using local site-packages ----
echo.
echo Starting RipperFox backend using local Python environment...
"%PYTHON_EXE%" "%BASEDIR%yt_backend.py"
pause
