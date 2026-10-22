@echo off
title Build GITwifi Standalone Executable
cd /d "%~dp0.."

echo =======================================================
echo           GITwifi Windows Executable Builder
echo =======================================================
echo.

:: 1. Ensure Python is available
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [!] Python is not installed or not in PATH.
    echo Please install Python 3.10+ first.
    pause
    exit /b
)

:: 2. Ensure PyInstaller is installed
echo [*] Checking PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% NEQ 0 (
    echo [*] Installing PyInstaller...
    python -m pip install --upgrade pyinstaller
)

:: 3. Build standalone executable
echo [*] Compiling GITwifi into standalone executable...
pyinstaller --clean --noconfirm GITwifi.spec

:: 4. Build single setup installer package
echo [*] Packing single standalone installer package (GITwifi_Setup.exe)...
pyinstaller --clean --noconfirm GITwifi_Setup.spec

if %errorlevel% EQU 0 (
    echo.
    echo =======================================================
    echo   [SUCCESS] All packages built successfully!
    echo.
    echo   1. Single Installation Setup Wizard:
    echo      dist\GITwifi_Setup.exe
    echo.
    echo   2. Standalone Portable Executable:
    echo      dist\GITwifi.exe
    echo =======================================================
) else (
    echo.
    echo [!] Build encountered errors.
)
echo.
pause
