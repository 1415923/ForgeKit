param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $errors.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param([string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Error "Missing required path: $RelativePath"
    }
}

function Test-ForbiddenPath {
    param([string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (Test-Path -LiteralPath $path) {
        Add-Error "Forbidden root plugin path: $RelativePath"
    }
}

function Test-RequiredPattern {
    param(
        [string]$RelativePath,
        [string]$Pattern,
        [string]$Label
    )
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return
    }
    if (-not (Select-String -Path $path -Pattern $Pattern -SimpleMatch -Quiet)) {
        Add-Error "$Label missing in $RelativePath"
    }
}

function Test-SkillAscii {
    $skillRoot = Join-Path $repoRoot "skills"
    $skillFiles = Get-ChildItem -LiteralPath $skillRoot -Recurse -Filter "SKILL.md"
    foreach ($file in $skillFiles) {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        foreach ($byte in $bytes) {
            if ($byte -gt 127) {
                Add-Error "Non-ASCII byte found in skill: $($file.FullName)"
                break
            }
        }
    }
}

function Test-PluginManifest {
    $codexManifestPath = Join-Path $repoRoot ".codex-plugin\plugin.json"
    $claudeManifestPath = Join-Path $repoRoot ".claude-plugin\plugin.json"

    $codexManifest = Get-Content -LiteralPath $codexManifestPath -Raw | ConvertFrom-Json
    if ($codexManifest.name -ne "forgekit") {
        Add-Error "Unexpected Codex plugin name: $($codexManifest.name)"
    }
    if ($codexManifest.version -ne "0.12.0") {
        Add-Error "Unexpected Codex plugin version: $($codexManifest.version)"
    }
    if ($codexManifest.skills -ne "./skills/") {
        Add-Error "Codex plugin skills must point to ./skills/"
    }

    $claudeManifest = Get-Content -LiteralPath $claudeManifestPath -Raw | ConvertFrom-Json
    if ($claudeManifest.name -ne "forgekit") {
        Add-Error "Unexpected Claude plugin name: $($claudeManifest.name)"
    }
    if ($claudeManifest.version -ne "0.12.0") {
        Add-Error "Unexpected Claude plugin version: $($claudeManifest.version)"
    }
    $claudeSkills = @($claudeManifest.skills)
    if ($claudeSkills.Count -ne 1 -or $claudeSkills[0] -ne "./skills/") {
        Add-Error "Claude plugin skills must point to ./skills/"
    }
    if ($claudeManifest.PSObject.Properties.Name -contains "hooks") {
        Add-Error "Claude plugin must not enable hooks by default"
    }
    if ($claudeManifest.PSObject.Properties.Name -contains "mcpServers") {
        Add-Error "Claude plugin must not enable MCP by default"
    }
}

Test-RequiredPath ".codex-plugin\plugin.json"
Test-RequiredPath ".claude-plugin\plugin.json"
Test-RequiredPath ".agents\plugins\marketplace.json"
Test-RequiredPath ".claude-plugin\marketplace.json"
Test-RequiredPath "skills\project-init\SKILL.md"
Test-RequiredPath "skills\project-bootstrap-fill\SKILL.md"
Test-RequiredPath "skills\document-backfill\SKILL.md"
Test-RequiredPath "skills\handover-review\SKILL.md"
Test-RequiredPath "skills\code-review\SKILL.md"
Test-RequiredPath "skills\release-check\SKILL.md"
Test-RequiredPath "skills\security-review\SKILL.md"
Test-RequiredPath "project-template\AGENTS.md"
Test-RequiredPath "project-template\CLAUDE.md"
Test-RequiredPath "project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
Test-RequiredPath "project-template\.codex\stacks\README.md"
Test-RequiredPath "project-template\scripts\detect-local-toolchain.ps1"
Test-RequiredPath "project-template\scripts\run-harness-check.ps1"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "scripts\init-project-template.sh"

Test-RequiredPattern "README.md" "Root-level plugin surface" "Unified root plugin section"
Test-RequiredPattern "scripts\init-project-template.ps1" "CLAUDE.md" "Unified initializer Claude guidance"
Test-RequiredPattern "skills\project-init\SKILL.md" "Classify the discovery state" "Project init discovery state"

Test-ForbiddenPath "plugins\forgekit-codex-workflow"
Test-ForbiddenPath "plugins\forgekit-claude-workflow"

Test-PluginManifest
Test-SkillAscii

if ($errors.Count -gt 0) {
    Write-Host "[fail] Unified plugin asset validation failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Unified plugin asset validation passed"
