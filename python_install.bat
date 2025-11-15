@echo off
setlocal
title RipperFox Python Environment Setup

set BASEDIR=%~dp0
set REQ_FILE=%BASEDIR%requirements.txt
set SITE_PACKAGES=%BASEDIR%python\Lib\site-packages

echo ================================================
echo   Setting up RipperFox local Python environment
echo ================================================
echo.

if not exist "%SITE_PACKAGES%" mkdir "%SITE_PACKAGES%"

echo [*] Ensuring pip is available...
python -m ensurepip
python -m pip install --upgrade pip

echo [*] Installing local dependencies...
python -m pip install --no-warn-script-location --upgrade --target "%SITE_PACKAGES%" -r "%REQ_FILE%"
echo.