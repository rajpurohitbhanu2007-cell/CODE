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
set "LAUNCH_BAT=%~dp0..\Launch_GITwifi.bat"
set "ICON_FILE=%~dp0..\app_icon.ico"

if exist "%STARTUP_LNK%" (
    echo Status: GITwifi IS currently set to start automatically on Windows boot.
    echo.
    echo 1. Disable / Remove from Startup
    echo 2. Update / Re-create shortcut
    echo 3. Exit
    echo.
    goto :PromptEnabled
) else (
    echo Status: GITwifi is NOT currently set to start on Windows boot.
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
:: WindowStyle = 7 (Minimized) prevents the CMD window flash on boot
powershell -NoProfile -Command ^
  "$target = (Resolve-Path '%LAUNCH_BAT%').Path; $workDir = (Resolve-Path '%~dp0..').Path; $startup = [Environment]::GetFolderPath('Startup'); $lnkPath = Join-Path $startup 'GITwifi.lnk'; $ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut($lnkPath); $s.TargetPath = $target; $s.WorkingDirectory = $workDir; $s.WindowStyle = 7; if (Test-Path '%ICON_FILE%') { $s.IconLocation = (Resolve-Path '%ICON_FILE%').Path + ',0' }; $s.Save()"

if exist "%STARTUP_LNK%" (
    echo [OK] Successfully enabled! GITwifi will now run automatically on system boot.
) else (
    echo [!] Shortcut created in startup apps.
)
goto :End

:RemoveStartup
echo.
echo [*] Removing GITwifi from Windows Startup...
if exist "%STARTUP_LNK%" del /f /q "%STARTUP_LNK%" >nul 2>&1
powershell -NoProfile -Command "$p = Join-Path ([Environment]::GetFolderPath('Startup')) 'GITwifi.lnk'; if (Test-Path $p) { Remove-Item $p -Force }"
echo [OK] Removed from Windows Startup.
goto :End

:Exit
goto :End

:End
echo.
pause
