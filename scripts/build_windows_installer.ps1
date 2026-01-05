<#
Build and package Meowzon for Windows (PyInstaller + Inno Setup)

Usage (PowerShell):
  # 1) Open PowerShell (recommended: run as normal user, not admin)
  # 2) Activate your environment where PyInstaller & deps are installed:
  #       conda activate meowzon   OR   .venv\Scripts\Activate.ps1
  # 3) From repo root run:
  #       .\scripts\build_windows_installer.ps1 -Version "3.0.0" -OneFile:$false
  #
  Notes:
    - Requires PyInstaller installed in the active Python env.
    - Requires Inno Setup Compiler (ISCC.exe) installed; either add ISCC.exe to PATH or set $env:ISCC_PATH to the full path of ISCC.exe.
    - If OneDrive causes locks, this script uses TEMP build dirs (C:\Windows\Temp or %TEMP%).
    - If you want to bundle Tesseract installer, place it at extras\Tesseract-Setup.exe.
#>

param(
    [string] $Version = "3.0.0",
    [switch] $OneFile = $false,
    [string] $AppName = "Meowzon",
    [string] $EntryScript = "main.py"
)

set -e

# repo root = current directory
$RepoRoot = (Get-Location).Path

Write-Host "Repo root: $RepoRoot"
Write-Host "Requested Version: $Version"
Write-Host "OneFile: $OneFile"

# Ensure python and pyinstaller are available in current env
$py = "python"
try {
    & $py -V > $null
} catch {
    throw "Python not found in PATH. Activate the environment or use full path to python.exe."
}

# Prepare isolated temp build directories (avoid OneDrive)
$TempRoot = Join-Path -Path $env:TEMP -ChildPath "meowzon_pyi_build_$([System.Guid]::NewGuid().ToString('N'))"
$WorkPath = Join-Path $TempRoot "work"
$DistPath = Join-Path $TempRoot "dist"
$SpecPath = Join-Path $TempRoot "spec"
New-Item -ItemType Directory -Path $WorkPath, $DistPath, $SpecPath -Force | Out-Null

Write-Host "Using temporary build folders:"
Write-Host "  WorkPath: $WorkPath"
Write-Host "  DistPath: $DistPath"
Write-Host "  SpecPath: $SpecPath"

# Build command
$pyinstallerArgs = @("--clean", "--noconfirm", "--name", $AppName, $EntryScript, "--workpath", $WorkPath, "--distpath", $DistPath, "--specpath", $SpecPath)
if ($OneFile) {
    $pyinstallerArgs += "--onefile"
} else {
    $pyinstallerArgs += "--onedir"
}

# Run PyInstaller
Write-Host "`n==> Running PyInstaller..."
$piCmd = "$py -m PyInstaller " + ($pyinstallerArgs -join " ")
Write-Host $piCmd
$rc = & $py -m PyInstaller @pyinstallerArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

# Locate built output
if ($OneFile) {
    # onefile -> single exe in $DistPath
    $builtFolder = $DistPath
    $builtExe = Get-ChildItem -Path $builtFolder -Filter "$AppName.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $builtExe) {
        # try root dist
        $builtExe = Get-ChildItem -Path $DistPath -Filter "*.exe" -Recurse | Where-Object { $_.Name -like "$AppName*.exe" } | Select-Object -First 1
    }
} else {
    $builtFolder = Join-Path $DistPath $AppName
    if (-not (Test-Path $builtFolder)) {
        # fallback: if PyInstaller put dist in dist\$AppName or dist\Meowzon
        $builtFolder = Get-ChildItem -Path $DistPath -Directory | Select-Object -First 1
        if ($builtFolder) { $builtFolder = $builtFolder.FullName } else { throw "Could not find PyInstaller output in $DistPath" }
    }
}

Write-Host "`nBuilt output located at: $builtFolder"

# Prepare packaging folder
$PackageRoot = Join-Path $RepoRoot "packaging"
$AppPackageDir = Join-Path $PackageRoot $AppName

if (Test-Path $AppPackageDir) {
    Write-Host "Removing existing packaging folder: $AppPackageDir"
    Remove-Item -Recurse -Force -LiteralPath $AppPackageDir
}

Write-Host "Creating packaging folder: $AppPackageDir"
New-Item -ItemType Directory -Path $AppPackageDir -Force | Out-Null

# Copy built files into packaging folder
Write-Host "Copying built app into packaging folder..."
if ($OneFile) {
    Get-ChildItem -Path $DistPath -Filter "*.exe" -Recurse | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $AppPackageDir -Force
    }
} else {
    Copy-Item -Path (Join-Path $builtFolder "*") -Destination $AppPackageDir -Recurse -Force
}

# Copy runtime extras (config, readme, license, sample config)
$extras = @("meowzon_config.yaml", "README.md", "LICENSE")
foreach ($f in $extras) {
    $src = Join-Path $RepoRoot $f
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $AppPackageDir -Force
    }
}

# Copy optional extras\Tesseract-Setup.exe if present
$extraInstaller = Join-Path $RepoRoot "extras\Tesseract-Setup.exe"
if (Test-Path $extraInstaller) {
    $extrasDest = Join-Path $AppPackageDir "extras"
    New-Item -ItemType Directory -Path $extrasDest -Force | Out-Null
    Copy-Item -Path $extraInstaller -Destination $extrasDest -Force
    Write-Host "Bundled Tesseract installer found and copied."
} else {
    Write-Host "No bundled Tesseract installer (extras\Tesseract-Setup.exe) found — installer will prompt users."
}

# Prepare Inno Setup call
$issPath = Join-Path $RepoRoot "installer\MeowzonInstaller.iss"
if (-not (Test-Path $issPath)) {
    throw "Inno Setup script not found at: $issPath"
}

# Find ISCC (Inno Setup Compiler)
$ISCC = $env:ISCC_PATH
if (-not $ISCC) {
    # common install path
    $commonISCC = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
    if (Test-Path $commonISCC) { $ISCC = $commonISCC }
    else {
        # fallback to PATH
        $ISCC = "ISCC.exe"
    }
}

Write-Host "`n==> Running Inno Setup to build installer..."
# Pass defines: MyAppVersion and MyAppName
$defineArgs = "/DMyAppVersion=`"$Version`" /DMyAppName=`"$AppName`""

# Run ISCC with working dir = installer folder
Push-Location (Split-Path $issPath)
try {
    $isccCmd = "$ISCC $defineArgs `"$issPath`""
    Write-Host $isccCmd
    & $ISCC $defineArgs $issPath
    if ($LASTEXITCODE -ne 0) {
        throw "ISCC failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
}

# Find resulting installer in installer\ (OutputDir configured in .iss)
$installerDir = Join-Path $RepoRoot "installer"
$installerExe = Get-ChildItem -Path $installerDir -Filter "*.exe" -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($installerExe) {
    Write-Host "`n✅ Installer created: $($installerExe.FullName)"
    Write-Host "Packaged app folder: $AppPackageDir"
} else {
    Write-Warning "Installer build completed but installer file not found in $installerDir."
}

# Cleanup temporary build folder (optional)
Write-Host "`nCleaning up temporary build folders..."
try {
    Remove-Item -Recurse -Force -LiteralPath $TempRoot
    Write-Host "Temporary build folder removed."
} catch {
    Write-Warning "Could not remove temporary folder $TempRoot. You can delete it manually."
}

Write-Host "`nAll done."
