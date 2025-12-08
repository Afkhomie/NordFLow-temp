; NodeFlow Windows Installer Script
; Built with Inno Setup 6.2.2+
; This installer includes OBS Virtual Camera and VB-Audio Cable

#define MyAppName "NodeFlow"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "NodeFlow"
#define MyAppURL "https://github.com/yourusername/nodeflow"
#define MyAppExeName "NodeFlow.exe"

[Setup]
; Installer metadata
AppId={{8A3C6E9F-5D7B-4C2A-9E1F-3B8D5A2C7E9F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases

; Installation directory
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no

; Files and licensing
LicenseFile=LICENSE
OutputDir=release
OutputBaseFilename=NodeFlow-Setup-v{#MyAppVersion}
OutputBaseFilename=NodeFlow-Setup-v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Permissions
PrivilegesRequired=admin
AllowNoIcons=yes
AllowUNCPaths=no

; Architecture
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

; Windows versions
MinVersion=10.0.17763

; UI
WizardSizePercent=100
ShowComponentSizes=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunch"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Launch NodeFlow on startup"; GroupDescription: "Startup Options"

[Files]
; Main application
Source: "dist\NodeFlow\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "QUICK_REFERENCE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "VIRTUAL_DEVICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "GETTING_STARTED_VIRTUAL.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
; Virtual device drivers (if included)
Source: "installers\OBS-VirtualCam-Installer.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: FileExists(ExpandConstant('{src}\installers\OBS-VirtualCam-Installer.exe'))
Source: "installers\VB-CABLE_Driver_Pack.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: FileExists(ExpandConstant('{src}\installers\VB-CABLE_Driver_Pack.exe'))

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunch
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: startup

[Run]
; Install OBS Virtual Camera (optional)
Filename: "{tmp}\OBS-VirtualCam-Installer.exe"; \
    Parameters: "/S"; \
    StatusMsg: "Installing OBS Virtual Camera (required for video)..."; \
    Flags: runhidden waituntilterminated; \
    Check: FileExists(ExpandConstant('{tmp}\OBS-VirtualCam-Installer.exe'))

; Install VB-Audio Cable (optional)
Filename: "{tmp}\VB-CABLE_Driver_Pack.exe"; \
    Parameters: "/VERYSILENT"; \
    StatusMsg: "Installing VB-Audio Cable (required for audio)..."; \
    Flags: runhidden waituntilterminated; \
    Check: FileExists(ExpandConstant('{tmp}\VB-CABLE_Driver_Pack.exe'))

; Launch NodeFlow
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent; \
    WorkingDir: "{app}"

[UninstallDelete]
Type: files; Name: "{userappdata}\NodeFlow\*"
Type: dirsifempty; Name: "{userappdata}\NodeFlow"

[Code]
// Helper function to check if file exists
function FileExists(const FileName: String): Boolean;
begin
  Result := FileOrDirectoryExists(FileName);
end;

// Pre-installation checks
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin10OrLater then
  begin
    MsgBox('NodeFlow requires Windows 10 or later.' + #13#10 + 'Your system: ' + GetWindowsVersionString, mbCriticalError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Show welcome message
  MsgBox('Welcome to NodeFlow Setup!' + #13#10#13#10 + \
         'This installer will install:' + #13#10 + \
         '• NodeFlow Desktop Application' + #13#10 + \
         '• OBS Virtual Camera Driver (for video)' + #13#10 + \
         '• VB-Audio Virtual Cable Driver (for audio)' + #13#10#13#10 + \
         'Installation requires Administrator privileges.' + #13#10 + \
         'This may take 5-10 minutes.' + #13#10#13#10 + \
         'Click OK to continue.', \
         mbInformation, MB_OK);
end;

// Post-installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('NodeFlow installation complete!' + #13#10#13#10 + \
           'Virtual device drivers may require a system restart.' + #13#10 + \
           'Please restart Windows for full functionality.' + #13#10#13#10 + \
           'After restart:' + #13#10 + \
           '1. Launch NodeFlow from desktop or Start Menu' + #13#10 + \
           '2. Open https://YOUR_IP:5000 on your phone' + #13#10 + \
           '3. Click "Start Camera" and "Start Microphone"' + #13#10 + \
           '4. Use "OBS Virtual Camera" in Discord/Zoom/OBS' + #13#10#13#10 + \
           'For help, see QUICK_REFERENCE.md', \
           mbInformation, MB_OK);
  end;
end;

// Helper function - is Windows 10 or later
function IsWin10OrLater: Boolean;
begin
  Result := CompareStr(GetWindowsVersionString, '10') >= 0;
end;
