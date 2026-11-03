$ErrorActionPreference = "Stop"

$Dest = "$env:USERPROFILE\.claude\skills\academic-tikz"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== academic-tikz installer ==="
Write-Host "Destination: $Dest"

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

# Root docs and metadata
Copy-Item "$ScriptDir\*.md" $Dest -Force
Copy-Item "$ScriptDir\LICENSE" $Dest -Force
Copy-Item "$ScriptDir\INSTALLATION.json" $Dest -Force

# Every asset directory is required: templates/ is the starting canvas,
# assets/ holds the publication preamble and the Method Draw editor.
foreach ($dir in "references", "scripts", "templates", "assets", "agents", "tests") {
    New-Item -ItemType Directory -Force -Path "$Dest\$dir" | Out-Null
    Copy-Item "$ScriptDir\$dir\*" "$Dest\$dir" -Recurse -Force
}

$count = (Get-ChildItem $Dest -Recurse -File | Measure-Object).Count
Write-Host "Files installed: $count"
Write-Host ""

# Run env check if Python available
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "=== Environment check ==="
    & python "$Dest\scripts\check-env.py"
} else {
    Write-Host "Python not found — skipping environment check"
}

Write-Host ""
Write-Host "Done. Restart Claude Code to use /academic-tikz"
