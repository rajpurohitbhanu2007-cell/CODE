@echo off
setlocal
title GITwifi Setup Wizard

set "INSTALL_DIR=%LOCALAPPDATA%\GITwifi"
echo ========================================================
echo           GITwifi Windows Desktop Setup Wizard
echo ========================================================
echo.
echo Installing GITwifi to:
echo   %INSTALL_DIR%
echo.

:: 1. Close any running instances so files aren't locked during upgrade
echo [*] Checking for running instances of GITwifi...
taskkill /F /IM GITwifi.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: 2. Create install directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: 3. Copy binary and icon (cleanly overwrites older versions)
echo [*] Copying application files...
copy /y "%~dp0GITwifi.exe" "%INSTALL_DIR%\GITwifi.exe" >nul
copy /y "%~dp0app_icon.ico" "%INSTALL_DIR%\app_icon.ico" >nul

:: 3. Create Desktop & Start Menu Shortcuts via PowerShell
echo [*] Creating Desktop and Start Menu shortcuts...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$deskPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'GITwifi.lnk'); " ^
  "$s1 = $ws.CreateShortcut($deskPath); " ^
  "$s1.TargetPath = '%INSTALL_DIR%\GITwifi.exe'; " ^
  "$s1.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s1.IconLocation = '%INSTALL_DIR%\app_icon.ico,0'; " ^
  "$s1.Description = 'GITwifi Suite - Campus Wi-Fi Authentication'; " ^
  "$s1.Save(); " ^
  "$programs = [System.IO.Path]::Combine([Environment]::GetFolderPath('Programs'), 'GITwifi'); " ^
  "if (!(Test-Path -Path $programs)) { New-Item -ItemType Directory -Path $programs -Force | Out-Null }; " ^
  "$menuPath = [System.IO.Path]::Combine($programs, 'GITwifi.lnk'); " ^
  "$s2 = $ws.CreateShortcut($menuPath); " ^
  "$s2.TargetPath = '%INSTALL_DIR%\GITwifi.exe'; " ^
  "$s2.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s2.IconLocation = '%INSTALL_DIR%\app_icon.ico,0'; " ^
  "$s2.Description = 'GITwifi Suite - Campus Wi-Fi Authentication'; " ^
  "$s2.Save();"

:: 4. Create clean Uninstaller script
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo title Uninstall GITwifi >> "%INSTALL_DIR%\uninstall.bat"
echo echo [*] Closing running GITwifi processes... >> "%INSTALL_DIR%\uninstall.bat"
echo taskkill /F /IM GITwifi.exe ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo echo [*] Removing Desktop and Start Menu shortcuts... >> "%INSTALL_DIR%\uninstall.bat"
echo del /f /q "%USERPROFILE%\Desktop\GITwifi.lnk" ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\GITwifi" ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo echo [*] Removing Registry entries... >> "%INSTALL_DIR%\uninstall.bat"
echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\GITwifi" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "GITwifi" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\uninstall.bat"
echo echo [*] Removing application files... >> "%INSTALL_DIR%\uninstall.bat"
echo start "" /b cmd.exe /c "timeout /t 1 ^>nul ^& rmdir /s /q """%INSTALL_DIR%"""" >> "%INSTALL_DIR%\uninstall.bat"
echo echo [OK] GITwifi has been uninstalled successfully. >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"
echo exit >> "%INSTALL_DIR%\uninstall.bat"

:: 5. Register in Windows Settings (Add or Remove Programs)
echo [*] Registering uninstaller in Windows Settings...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$regPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\GITwifi'; " ^
  "New-Item -Path $regPath -Force | Out-Null; " ^
  "Set-ItemProperty -Path $regPath -Name 'DisplayName' -Value 'GITwifi Suite' -Force; " ^
  "Set-ItemProperty -Path $regPath -Name 'DisplayVersion' -Value '1.0.0' -Force; " ^
  "Set-ItemProperty -Path $regPath -Name 'Publisher' -Value 'StormDucky' -Force; " ^
  "Set-ItemProperty -Path $regPath -Name 'DisplayIcon' -Value '%INSTALL_DIR%\app_icon.ico' -Force; " ^
  "Set-ItemProperty -Path $regPath -Name 'InstallLocation' -Value '%INSTALL_DIR%' -Force; " ^
  "Set-ItemProperty -Path $regPath -Name 'UninstallString' -Value 'cmd.exe /c `\"%INSTALL_DIR%\uninstall.bat`\"' -Force;"

echo.
echo ========================================================
echo        [SUCCESS] GITwifi installed successfully!
echo ========================================================
echo.
echo Desktop shortcut created: GITwifi
echo Start Menu shortcut created: GITwifi
echo.

set /p AUTOSTART="Do you want GITwifi to automatically start on Windows boot? (Y/N) [Y]: "
if /i "%AUTOSTART%"=="" set "AUTOSTART=Y"
if /i "%AUTOSTART%"=="Y" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
      "$runKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'; " ^
      "Set-ItemProperty -Path $runKey -Name 'GITwifi' -Value '`\"%INSTALL_DIR%\GITwifi.exe`\" --minimized' -Force;"
    echo [OK] Automatic startup enabled (starts silently in tray on boot).
    echo.
)

set /p LAUNCH="Do you want to launch GITwifi now? (Y/N) [Y]: "
if /i "%LAUNCH%"=="" set "LAUNCH=Y"
if /i "%LAUNCH%"=="Y" (
    start "" "%INSTALL_DIR%\GITwifi.exe"
)
exit /b 0
