@echo off
setlocal
title RipperFox FFMPEG Installer

set BASEDIR=%~dp0
set FFMPEG_DIR=%BASEDIR%ffmpeg
set ZIP_PATH=%BASEDIR%ffmpeg.zip
set TMP_DIR=%BASEDIR%ffmpeg_tmp

echo ================================================
echo   RipperFox FFmpeg Downloader
echo ================================================
echo.

REM ---- Create ffmpeg folder if missing ----
if not exist "%FFMPEG_DIR%" mkdir "%FFMPEG_DIR%"

REM ---- Download the latest build (from gyan.dev) ----
echo [*] Downloading latest FFmpeg Windows build...
powershell -Command ^
  "(New-Object Net.WebClient).DownloadFile('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', '%ZIP_PATH%')" || (
    echo [!] Failed to download FFmpeg archive.
    echo Please check your internet connection or try manually:
    echo   https://www.gyan.dev/ffmpeg/builds/
    pause
    exit /b
)

REM ---- Extract ffmpeg and ffprobe ----
echo [*] Extracting executables...
powershell -Command ^
  "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%TMP_DIR%' -Force" || (
    echo [!] Extraction failed.
    pause
    exit /b
)

REM ---- Move binaries to /ffmpeg ----
for /r "%TMP_DIR%" %%F in (ffmpeg.exe ffprobe.exe) do (
    echo Copying %%~nxF to %FFMPEG_DIR% ...
    copy /Y "%%F" "%FFMPEG_DIR%" >nul
)

REM ---- Cleanup ----
echo [*] Cleaning up temporary files...
rmdir /S /Q "%TMP_DIR%" >nul 2>&1
del "%ZIP_PATH%" >nul 2>&1

echo.
echo [✓] FFmpeg installed successfully into: %FFMPEG_DIR%
echo.
pause
