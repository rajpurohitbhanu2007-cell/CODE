[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallProgram
ShowInstallProgramWindow=0
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AdminQuietInstCmd%
UserQuietInstCmd=%UserQuietInstCmd%
SourceFiles=SourceFiles
[Strings]
InstallPrompt=Do you want to install GITwifi Suite on your computer?
DisplayLicense=
FinishMessage=GITwifi setup has completed.
TargetName=C:\CODES\GITwifi\dist\GITwifi_Setup.exe
FriendlyName=GITwifi Suite Setup
AppLaunched=cmd.exe /c setup.bat
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
FILE0="GITwifi.exe"
FILE1="app_icon.ico"
FILE2="setup.bat"
[SourceFiles]
SourceFiles0=C:\CODES\GITwifi\installer_build\
[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=
