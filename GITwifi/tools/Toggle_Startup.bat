@echo off
setlocal
title GITwifi - Windows Startup Configurator
color 0A

echo =======================================================
echo          GITwifi Windows Startup Configurator          
echo =======================================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_LNK=%STARTUP_FOLDER%\GITwifi.lnk"
set "STALE_BAT_LNK=%STARTUP_FOLDER%\Launch_GITwifi.bat.lnk"
set "INSTALLED_EXE=%LOCALAPPDATA%\GITwifi\GITwifi.exe"
set "DIST_EXE=%~dp0..\dist\GITwifi.exe"
set "LAUNCH_BAT=%~dp0..\Launch_GITwifi.bat"
set "ICON_FILE=%~dp0..\app_icon.ico"

:: Determine best target executable/script
if exist "%INSTALLED_EXE%" (
    set "TARGET_PATH=%INSTALLED_EXE%"
    set "TARGET_DIR=%LOCALAPPDATA%\GITwifi"
    set "TARGET_ARGS=--minimized"
    set "TARGET_DESC=GITwifi Suite Autostart"
    set "TARGET_TYPE=Installed Executable (%LOCALAPPDATA%\GITwifi\GITwifi.exe)"
) else if exist "%DIST_EXE%" (
    set "TARGET_PATH=%DIST_EXE%"
    set "TARGET_DIR=%~dp0..\dist"
    set "TARGET_ARGS=--minimized"
    set "TARGET_DESC=GITwifi Suite Autostart"
    set "TARGET_TYPE=Compiled Portable Executable (dist\GITwifi.exe)"
) else (
    set "TARGET_PATH=%LAUNCH_BAT%"
    set "TARGET_DIR=%~dp0.."
    set "TARGET_ARGS="
    set "TARGET_DESC=GITwifi Suite Launcher"
    set "TARGET_TYPE=Launcher Script (Launch_GITwifi.bat)"
)

if exist "%STARTUP_LNK%" (
    echo Status: GITwifi IS currently set to start automatically on Windows boot.
    echo Target: %TARGET_TYPE%
    echo.
    echo 1. Disable / Remove from Startup
    echo 2. Update / Re-create shortcut pointing to current target
    echo 3. Exit
    echo.
    goto :PromptEnabled
) else (
    echo Status: GITwifi is NOT currently set to start on Windows boot.
    echo Target: %TARGET_TYPE%
    echo.
    echo 1. Enable Start with Windows
    echo 2. Exit
    echo.
    goto :PromptDisabled
)

:PromptEnabled
set /p "CHOICE=Enter choice (1/2/3): "
if "%CHOICE%"=="1" goto :RemoveStartup
if "%CHOICE%"=="2" goto :EnableStartup
goto :Exit

:PromptDisabled
set /p "CHOICE=Enter choice (1/2): "
if "%CHOICE%"=="1" goto :EnableStartup
goto :Exit

:EnableStartup
echo.
echo [*] Adding GITwifi to Windows Startup folder...
echo [*] Target: %TARGET_PATH% %TARGET_ARGS%
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%STARTUP_LNK%'); " ^
  "$s.TargetPath = '%TARGET_PATH%'; " ^
  "$s.Arguments = '%TARGET_ARGS%'; " ^
  "$s.WorkingDirectory = '%TARGET_DIR%'; " ^
  "$s.WindowStyle = 7; " ^
  "$s.Description = '%TARGET_DESC%'; " ^
  "if (Test-Path '%ICON_FILE%') { $s.IconLocation = (Resolve-Path '%ICON_FILE%').Path + ',0' }; " ^
  "$s.Save(); " ^
  "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder' -Name 'GITwifi.lnk' -ErrorAction SilentlyContinue; " ^
  "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder' -Name 'Launch_GITwifi.bat.lnk' -ErrorAction SilentlyContinue; " ^
  "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'GITwifi' -ErrorAction SilentlyContinue; " ^
  "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run' -Name 'GITwifi' -ErrorAction SilentlyContinue; " ^
  "if (Test-Path '%STALE_BAT_LNK%') { Remove-Item '%STALE_BAT_LNK%' -Force };"

if exist "%STARTUP_LNK%" (
    echo [OK] Successfully enabled! GITwifi will now run automatically on system boot.
) else (
    echo [!] Failed to create shortcut in startup apps.
)
goto :End

:RemoveStartup
echo.
echo [*] Removing GITwifi from Windows Startup...
if exist "%STARTUP_LNK%" del /f /q "%STARTUP_LNK%" >nul 2>&1
if exist "%STALE_BAT_LNK%" del /f /q "%STALE_BAT_LNK%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'GITwifi' -ErrorAction SilentlyContinue; " ^
  "$s1 = Join-Path ([Environment]::GetFolderPath('Startup')) 'GITwifi.lnk'; if (Test-Path $s1) { Remove-Item $s1 -Force }; " ^
  "$s2 = Join-Path ([Environment]::GetFolderPath('Startup')) 'Launch_GITwifi.bat.lnk'; if (Test-Path $s2) { Remove-Item $s2 -Force };"
echo [OK] Removed from Windows Startup.
goto :End

:Exit
goto :End

:End
echo.
pause
