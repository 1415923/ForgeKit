$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $errors.Add($Message) | Out-Null
}

function Test-PathRequired {
    param([string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Error "Missing required path: $RelativePath"
    }
}

function Test-FileContains {
    param(
        [string]$RelativePath,
        [string]$Text
    )
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return
    }
    if (-not (Select-String -LiteralPath $path -Pattern $Text -SimpleMatch -Quiet)) {
        Add-Error "Missing expected text in ${RelativePath}: $Text"
    }
}

Test-PathRequired "AGENTS.md"
Test-PathRequired ".codex\commands.md"
Test-PathRequired ".codex\commands-catalog.md"
Test-PathRequired ".codex\hooks.md"
Test-PathRequired ".codex\automation-decision.md"
Test-PathRequired "docs"
Test-PathRequired "governance\agent-harness.md"
Test-PathRequired "governance\large-change-execution.md"
Test-PathRequired "governance\team-agent-rollout.md"
Test-PathRequired "governance\agent-suitability.md"
Test-PathRequired "scripts\check-doc-sync.ps1"
Test-PathRequired "scripts\check-doc-sync.sh"
Test-PathRequired "scripts\install-hooks.ps1"
Test-PathRequired "scripts\install-hooks.sh"

$agentsPath = Join-Path $repoRoot "AGENTS.md"
if (Test-Path -LiteralPath $agentsPath) {
    $lineCount = (Get-Content -LiteralPath $agentsPath).Count
    if ($lineCount -gt 200) {
        Add-Error "AGENTS.md is too long: $lineCount lines"
    }
}

Test-FileContains "AGENTS.md" "Do not read every file"
Test-FileContains "AGENTS.md" "large-change-execution.md"
Test-FileContains "AGENTS.md" "team-agent-rollout.md"
Test-FileContains ".codex\hooks.md" "Opt-in only"
Test-FileContains ".codex\hooks.md" "check-doc-sync.ps1"
Test-FileContains ".codex\hooks.md" "install-hooks.sh"
Test-FileContains ".codex\automation-decision.md" "docs-warn"
Test-FileContains ".codex\automation-decision.md" "project-init"

if ($errors.Count -gt 0) {
    Write-Host "[fail] Harness check failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Harness check passed"
