#define MyAppName "CRMRunner"
#define MyAppExeName "CRMRunner.exe"
#define ApplicationVersion GetVersionNumbersString('CRMRunner.exe')

[Setup]
AppId = "78902D197-8DDF-49RR-X98X-59F0866129ZX"
AppName={#MyAppName}
AppVerName={#MyAppName} {#ApplicationVersion}
VersionInfoVersion={#ApplicationVersion}
SetupIconFile=icons\icon.ico
DefaultDirName={commonpf64}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename={#MyAppName}
Compression=lzma
SolidCompression=yes
AppPublisher = "Εβγενθι ΐαδώψεβ"
AppCopyright = "Copyright © 2023 iam@eabdyushev@ru Eugene Abdyushev"

[Files]
Source: "build\*.*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName}"; Flags: nowait postinstall shellexec

[UninstallDelete]
Type: files; Name: "!{app}\settings.json"; 
Type: files; Name: "!{app}\auth.json";   