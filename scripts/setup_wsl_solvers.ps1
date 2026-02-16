param(
  [string]$Distro = "Ubuntu"
)

Write-Host "== Step 1: Ensure WSL is installed (Admin required) =="
Write-Host "Run this in an ADMIN PowerShell if WSL is missing:"
Write-Host "  wsl --install -d $Distro"
Write-Host "Then REBOOT and open $Distro once to create your Linux user."

$wsl = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wsl) {
  Write-Host "WSL command not found. Install manually first."
  exit 1
}

Write-Host "== Step 2: Copy and run Linux setup script =="
$repo = Split-Path -Parent $PSScriptRoot
$linuxScriptWin = Join-Path $repo "scripts\setup_wsl_solvers.sh"
$linuxScriptWsl = "/tmp/setup_wsl_solvers.sh"

$linuxScriptWinEsc = $linuxScriptWin -replace '\\','/'
if ($linuxScriptWinEsc -match '^([A-Za-z]):/(.*)$') {
  $drive = $matches[1].ToLower()
  $tail = $matches[2]
  $wslPath = "/mnt/$drive/$tail"
} else {
  $wslPath = $linuxScriptWinEsc
}

wsl -d $Distro bash -lc "cp '$wslPath' '$linuxScriptWsl' && chmod +x '$linuxScriptWsl' && '$linuxScriptWsl'"

Write-Host "== Step 3: Validate installs =="
wsl -d $Distro bash -lc "which simpleFoam || true; which lmp || true; which pw.x || true"

Write-Host "Done."