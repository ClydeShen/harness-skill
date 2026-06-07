# Links all skills in this collection into $HOME\.claude\skills\ as junctions.
# Junctions work without admin rights on Windows.
# Usage: pwsh scripts/link-skills.ps1

$RepoRoot = Split-Path -Parent $PSScriptRoot
$TargetDir = Join-Path $HOME ".claude\skills"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════╗"
Write-Host "  ║   ━━━━━━━━━  Harness Engineering Skills  ━━━━━━━━  ║"
Write-Host "  ╚══════════════════════════════════════════════════╝"
Write-Host ""

$count = 0
Get-ChildItem "$RepoRoot\skills" -Recurse -Filter "SKILL.md" | ForEach-Object {
    $skillDir = $_.DirectoryName
    $skillName = Split-Path $skillDir -Leaf
    $link = Join-Path $TargetDir $skillName

    # Remove existing junction or symlink; warn and skip plain directories
    if (Test-Path $link) {
        $item = Get-Item $link -Force
        if ($item.LinkType -in @("Junction", "SymbolicLink")) {
            Remove-Item $link -Force
        } else {
            Write-Host "  ⚠ Skipped: $skillName — plain directory exists at $link (remove manually)"
            return
        }
    }

    New-Item -ItemType Junction -Path $link -Target $skillDir | Out-Null
    Write-Host "  ✓ Linked: $skillName → $link"
    $count++
}

Write-Host ""
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "  Done. $count skill(s) linked. Run 'claude skills' to verify."
Write-Host "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
