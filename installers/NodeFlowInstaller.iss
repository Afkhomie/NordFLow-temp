; Inno Setup script for NodeFlow
; Replace {#AppExe} and {#AppIcon} as needed

#define AppName "NodeFlow"
#define AppVersion "1.0.0"
#define AppPublisher "NodeFlow Team"
#define AppExe "NodeFlow.exe"
#define AppIcon "assets\\nodeflow.ico"

[Setup]
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={pf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=NodeFlow-Setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Copy single bundled executable and assets from staging
Source: "staging\NodeFlow.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "staging\assets\nodeflow.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"; IconFilename: "{app}\assets\nodeflow.ico"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
