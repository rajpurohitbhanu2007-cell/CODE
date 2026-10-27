@echo off
setlocal
title GITwifi - Dependency Installer and Setup
color 0B

echo =======================================================
echo          GITwifi Windows Setup and Installer           
echo =======================================================
echo.

:: 1. Check for Python
echo [*] Checking for Python installation...
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

if not defined PY_CMD goto :InstallPython

echo [OK] Python found:
%PY_CMD% --version
echo.

:: 2. Upgrade pip
echo [*] Ensuring pip is up to date...
%PY_CMD% -m pip install --upgrade pip --quiet

:: 3. Install required libraries
echo [*] Installing required dependencies (requests, pillow, pystray, urllib3)...
set "REQ_FILE=%~dp0..\requirements.txt"
if not exist "%REQ_FILE%" set "REQ_FILE=%~dp0requirements.txt"
%PY_CMD% -m pip install -r "%REQ_FILE%"

if %errorlevel% NEQ 0 (
    echo.
    echo [!] An error occurred while installing dependencies.
    echo Please make sure you are connected to the Internet and try again.
    goto :End
)

echo.
echo =======================================================
echo   [SUCCESS] All dependencies installed successfully!
echo =======================================================
echo.

:: 4. Ask to add to Windows Startup
set /p "AUTOSTART=Do you want GITwifi to automatically start on Windows boot? (Y/N): "
if /i "%AUTOSTART%"=="Y" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$root = (Resolve-Path '%~dp0..').Path; " ^
      "$installedExe = [System.IO.Path]::Combine($env:LOCALAPPDATA, 'GITwifi\GITwifi.exe'); " ^
      "$distExe = Join-Path $root 'dist\GITwifi.exe'; " ^
      "$launchBat = Join-Path $root 'Launch_GITwifi.bat'; " ^
      "if (Test-Path $installedExe) { $target = $installedExe; $work = [System.IO.Path]::GetDirectoryName($installedExe); $args = '--minimized' } " ^
      "elseif (Test-Path $distExe) { $target = $distExe; $work = (Join-Path $root 'dist'); $args = '--minimized' } " ^
      "else { $target = $launchBat; $work = $root; $args = '' }; " ^
      "$startup = [Environment]::GetFolderPath('Startup'); " ^
      "$lnkPath = Join-Path $startup 'GITwifi.lnk'; " ^
      "$ws = New-Object -ComObject WScript.Shell; " ^
      "$s = $ws.CreateShortcut($lnkPath); " ^
      "$s.TargetPath = $target; " ^
      "$s.Arguments = $args; " ^
      "$s.WorkingDirectory = $work; " ^
      "$s.WindowStyle = 7; " ^
      "$ico = Join-Path $root 'app_icon.ico'; if (Test-Path $ico) { $s.IconLocation = $ico + ',0' }; " ^
      "$s.Save(); " ^
      "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder' -Name 'GITwifi.lnk' -ErrorAction SilentlyContinue; " ^
      "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder' -Name 'Launch_GITwifi.bat.lnk' -ErrorAction SilentlyContinue; " ^
      "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'GITwifi' -ErrorAction SilentlyContinue; " ^
      "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run' -Name 'GITwifi' -ErrorAction SilentlyContinue; " ^
      "$staleBat = Join-Path $startup 'Launch_GITwifi.bat.lnk'; if (Test-Path $staleBat) { Remove-Item $staleBat -Force };"
    echo [OK] Added to Windows Startup (runs minimized on boot)!
    echo.
)

:: 5. Launch Option
echo You can run GITwifi anytime using Launch_GITwifi.bat
echo.
set /p "LAUNCH=Would you like to launch GITwifi now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    cd /d "%~dp0.."
    start "" Launch_GITwifi.bat
)
goto :End

:InstallPython
echo.
echo [!] Python is not installed or not added to your system PATH.
echo.
echo Choose an option:
echo   1. Automatically download and install Python (Recommended)
echo   2. Open official python.org download page in browser
echo   3. Exit
echo.
set /p "OPT=Enter choice (1/2/3): "

if "%OPT%"=="1" (
    echo.
    echo [*] Attempting automated Python install via Windows Package Manager...
    winget install --id Python.Python.3.12 --exact --source winget --accept-source-agreements --accept-package-agreements
    if %errorlevel% NEQ 0 (
        echo [*] winget not available or failed. Downloading official installer...
        set "PY_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
        set "PY_TEMP=%TEMP%\python_setup.exe"
        powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_TEMP%'"
        if exist "%TEMP%\python_setup.exe" (
            echo [*] Installing Python with 'Add to PATH' option enabled...
            start /wait "" "%TEMP%\python_setup.exe" /passive InstallAllUsers=0 PrependPath=1 Include_pip=1
            del "%TEMP%\python_setup.exe" >nul 2>&1
        ) else (
            echo [!] Download failed. Please install Python manually from https://www.python.org/downloads/
        )
    )
    echo.
    echo [i] Python installation completed. Please re-run this script to finish setup!
    pause
    exit /b 0
)

if "%OPT%"=="2" (
    echo Opening Python downloads page...
    start https://www.python.org/downloads/
    pause
    exit /b 0
)

:End
echo.
pause
