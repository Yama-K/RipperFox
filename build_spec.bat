@echo off
setlocal
title Building RipperFox Executable

echo ========================================
echo    Building RipperFox Executable
echo ========================================
echo.

echo [*] Installing required packages...
pip install pyinstaller pillow pystray appdirs requests packaging

echo [*] Building using spec file...
pyinstaller ripperfox.spec

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