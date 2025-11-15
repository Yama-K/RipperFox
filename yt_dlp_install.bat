@echo off
setlocal
title RipperFox yt-dlp Installer

set BASEDIR=%~dp0
set YTDLP_DIR=%BASEDIR%yt-dlp
set YTDLP_EXE=%YTDLP_DIR%\yt-dlp.exe
set YTDLP_URL=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe

echo ================================================
echo     RipperFox yt-dlp Downloader
echo ================================================
echo.

REM Create folder if missing
if not exist "%YTDLP_DIR%" mkdir "%YTDLP_DIR%"

REM Skip if already there
if exist "%YTDLP_EXE%" (
    echo [OK] yt-dlp.exe already exists at "%YTDLP_EXE%"
    echo Skipping download.
    pause
    exit /b
)

echo [*] Downloading yt-dlp.exe from official GitHub release...
powershell -Command ^
    "Invoke-WebRequest -Uri '%YTDLP_URL%' -OutFile '%YTDLP_EXE%'"
 
    if errorlevel 1 (
    echo [!] Download failed.
    exit /b
)

if exist "%YTDLP_EXE%" (
    echo.
    echo [OK] yt-dlp installed successfully.
    echo Location: "%YTDLP_EXE%"
) else (
    echo [ERROR] yt-dlp.exe was not downloaded correctly.
)

echo.
