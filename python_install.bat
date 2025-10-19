@echo off
setlocal
title RipperFox Python Environment Setup

set BASEDIR=%~dp0
set PYTHON_EXE=%BASEDIR%python\python.exe
set REQ_FILE=%BASEDIR%requirements.txt
set SITE_PACKAGES=%BASEDIR%python\Lib\site-packages

echo ================================================
echo   Setting up RipperFox local Python environment
echo ================================================
echo.

if not exist "%PYTHON_EXE%" (
    echo [!] python.exe not found in "%BASEDIR%python"
    echo Please place a standalone python.exe there first.
    pause
    exit /b
)

if not exist "%SITE_PACKAGES%" mkdir "%SITE_PACKAGES%"

echo [*] Ensuring pip is available...
"%PYTHON_EXE%" -m ensurepip
"%PYTHON_EXE%" -m pip install --upgrade pip

echo [*] Installing local dependencies...
"%PYTHON_EXE%" -m pip install --target "%SITE_PACKAGES%" -r "%REQ_FILE%"
pause
