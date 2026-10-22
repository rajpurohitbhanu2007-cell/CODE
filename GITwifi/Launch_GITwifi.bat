@echo off
title GITwifi Windows Suite
cd /d "%~dp0"

:: 0. Check for compiled standalone executable first
if exist "%~dp0dist\GITwifi.exe" (
    start "" "%~dp0dist\GITwifi.exe" %*
    exit /b
)
if exist "%~dp0GITwifi.exe" (
    start "" "%~dp0GITwifi.exe" %*
    exit /b
)

:: 1. Check if Python is installed
set "PY_CMD="
python --version >nul 2>&1
if %errorlevel% EQU 0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>&1
    if %errorlevel% EQU 0 (
        set "PY_CMD=py -3"
    )
)

if not defined PY_CMD (
    echo [!] Python was not found on this computer.
    echo Starting dependency installer...
    echo.
    if exist "%~dp0tools\Install_Dependencies.bat" (
        call "%~dp0tools\Install_Dependencies.bat"
    ) else (
        call "%~dp0Install_Dependencies.bat"
    )
    exit /b
)

:: 2. Check if required dependencies are installed
%PY_CMD% -c "import requests, PIL, pystray" >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [!] Missing required dependencies. Running installer first...
    echo.
    if exist "%~dp0tools\Install_Dependencies.bat" (
        call "%~dp0tools\Install_Dependencies.bat"
    ) else (
        call "%~dp0Install_Dependencies.bat"
    )
    exit /b
)

:: 3. Launch: prefer pythonw (no console window) if available, else fall back to python
where pythonw >nul 2>&1
if %errorlevel% EQU 0 (
    start "" pythonw "%~dp0git_wifi_suite.py" %*
) else (
    echo [i] pythonw not found, launching with console window.
    start "" %PY_CMD% "%~dp0git_wifi_suite.py" %*
)
exit
