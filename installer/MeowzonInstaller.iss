; Meowzon Inno Setup installer script
; Save as installer\MeowzonInstaller.iss
; The PowerShell/Batch scripts call ISCC with defines:
;   /DMyAppVersion="3.0.0" /DMyAppName="Meowzon"
; so the script supports overriding the version/name from the command line.

#ifndef MyAppName
#define MyAppName "Meowzon"
#endif

#ifndef MyAppVersion
#define MyAppVersion "3.0.0"
#endif

#define MyAppExeName MyAppName + ".exe"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=installer
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Include the built dist folder contents (packaging\Meowzon)
Source: "..\packaging\{#MyAppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Optional Tesseract installer (if provided)
Source: "..\packaging\{#MyAppName}\extras\Tesseract-Setup.exe"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
; Launch Meowzon after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  ResultCode: Integer;

function ExecAndReturnCode(const Cmd, Params, WorkingDir: string): Integer;
begin
  if Exec(Cmd, Params, WorkingDir, SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    Result := ResultCode
  else
    Result := -1;
end;

function IsTesseractAvailable(): Boolean;
var
  rc: Integer;
begin
  rc := ExecAndReturnCode('cmd.exe', '/C where tesseract', '');
  Result := (rc = 0);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  TesseractInstallerPath: string;
begin
  if CurStep = ssInstall then
  begin
    if not IsTesseractAvailable() then
    begin
      TesseractInstallerPath := ExpandConstant('{tmp}\Tesseract-Setup.exe');
      if FileExists(TesseractInstallerPath) then
      begin
        if ExecAndReturnCode(TesseractInstallerPath, '/S', '') = 0 then
          MsgBox('Tesseract installed silently.', mbInformation, MB_OK)
        else
          MsgBox('Tesseract installer ran but returned non-zero. You may need to install Tesseract manually.', mbInformation, MB_OK);
      end
      else
      begin
        MsgBox('Tesseract OCR was not detected on this machine.'#13#10 +
               'For full functionality, install Tesseract: https://github.com/tesseract-ocr/tesseract', mbInformation, MB_OK);
      end;
    end;
  end;
end;
