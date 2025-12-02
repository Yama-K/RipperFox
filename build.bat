@echo off
setlocal
title Building RipperFox Executable

echo ========================================
echo    Building RipperFox Executable
echo ========================================
echo.

echo [*] Installing required packages...
pip install pyinstaller pillow pystray appdirs requests packaging

echo [*] Downloading FFmpeg binaries...
if not exist "ffmpeg.exe" (
    echo Downloading ffmpeg.exe...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/Yama-K/FFmpeg/releases/download/Release/ffmpeg.exe' -OutFile 'ffmpeg.exe'"
) else (
    echo ffmpeg.exe already exists, skipping download.
)

if not exist "ffprobe.exe" (
    echo Downloading ffprobe.exe...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/Yama-K/FFmpeg/releases/download/Release/ffprobe.exe' -OutFile 'ffprobe.exe'"
) else (
    echo ffprobe.exe already exists, skipping download.
)

echo [*] Downloading yt-dlp binary...
if not exist "yt-dlp.exe" (
    echo Downloading yt-dlp.exe...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe' -OutFile 'yt-dlp.exe'"
) else (
    echo yt-dlp.exe already exists, skipping download.
)

echo [*] Verifying downloads...
if not exist "ffmpeg.exe" (
    echo [!] Failed to download ffmpeg.exe
    pause
    exit /b 1
)
if not exist "ffprobe.exe" (
    echo [!] Failed to download ffprobe.exe
    pause
    exit /b 1
)
if not exist "yt-dlp.exe" (
    echo [!] Failed to download yt-dlp.exe
    pause
    exit /b 1
)

echo [*] Building executable...
pyinstaller --onefile --console --icon=icon.ico --name "RipperFox" --add-data "icon.ico;." --add-data "settings.json;." --add-data "yt_backend.py;." --add-data "ffmpeg.exe;." --add-data "ffprobe.exe;." --add-data "yt-dlp.exe;." --hidden-import=flask --hidden-import=flask_cors --hidden-import=colorama --hidden-import=yt_dlp --hidden-import=ffmpeg --hidden-import=pystray --hidden-import=PIL --hidden-import=PIL._imaging --hidden-import=PIL._imagingft --hidden-import=yt_dlp.extractor --hidden-import=yt_dlp.postprocessor --hidden-import=appdirs ripperfox_launcher.py

if errorlevel 1 (
    echo [!] Build failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed!
echo Executable: dist\RipperFox.exe
echo.
pause