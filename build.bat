@echo off
setlocal
title Building RipperFox Executable

echo ========================================
echo    Building RipperFox Executable
echo ========================================
echo.

echo [*] Installing required packages...
pip install pyinstaller pillow pystray appdirs

echo [*] Building executable with explicit includes...
pyinstaller --onefile ^
            --console ^
            --icon=icon.ico ^
            --name "RipperFox" ^
            --add-data "icon.ico;." ^
            --add-data "settings.json;." ^
            --add-data "yt_backend.py;." ^
            --hidden-import=flask ^
            --hidden-import=flask_cors ^
            --hidden-import=colorama ^
            --hidden-import=yt_dlp ^
            --hidden-import=ffmpeg ^
            --hidden-import=pystray ^
            --hidden-import=PIL ^
            --hidden-import=PIL._imaging ^
            --hidden-import=PIL._imagingft ^
            --hidden-import=yt_dlp.extractor ^
            --hidden-import=yt_dlp.postprocessor ^
            --hidden-import=appdirs ^
            ripperfox_launcher.py

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