param(
    [switch]$SkipSkillValidation
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$projectTemplate = Join-Path $repoRoot "project-template"
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

function Test-NoPattern {
    param(
        [string]$RelativePath,
        [string]$Pattern,
        [string]$Label
    )
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return
    }
    $matches = Select-String -Path $path -Pattern $Pattern -SimpleMatch
    foreach ($match in $matches) {
        Add-Error "$Label in ${RelativePath}:$($match.LineNumber)"
    }
}

function Test-SkillAscii {
    $skillFiles = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Recurse -Filter "SKILL.md"
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

function Test-SkillFrontmatter {
    $skillFiles = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Recurse -Filter "SKILL.md"
    foreach ($file in $skillFiles) {
        $lines = Get-Content -LiteralPath $file.FullName
        if ($lines.Count -lt 5 -or $lines[0] -ne "---") {
            Add-Error "Missing frontmatter start in skill: $($file.FullName)"
            continue
        }
        if (-not ($lines | Select-String -Pattern "^name: " -Quiet)) {
            Add-Error "Missing name in skill: $($file.FullName)"
        }
        if (-not ($lines | Select-String -Pattern "^description: " -Quiet)) {
            Add-Error "Missing description in skill: $($file.FullName)"
        }
    }
}

function Test-GovernanceFiles {
    $required = @(
        "project-template\governance\sdlc.md",
        "project-template\governance\architecture-governance.md",
        "project-template\governance\adr-process.md",
        "project-template\governance\rfc-process.md",
        "project-template\governance\traceability.md",
        "project-template\governance\definition-of-ready.md",
        "project-template\governance\definition-of-done.md",
        "project-template\governance\risk-management.md",
        "project-template\governance\technical-debt-management.md",
        "project-template\governance\quality-metrics.md",
        "project-template\governance\change-management.md",
        "project-template\governance\incident-process.md",
        "project-template\governance\security-governance.md",
        "project-template\governance\cicd-environment-governance.md",
        "project-template\governance\code-ownership-review-governance.md",
        "project-template\governance\project-management-task-model.md"
    )
    foreach ($item in $required) {
        Test-RequiredPath $item
    }
}

function Test-StackTemplates {
    $requiredStacks = @(
        "java-springboot",
        "vue",
        "react",
        "python-fastapi",
        "node-express",
        "fpga-vivado-vitis"
    )
    foreach ($stack in $requiredStacks) {
        Test-RequiredPath "templates\$stack\README.md"
        Test-RequiredPath "templates\$stack\commands.md"
        Test-RequiredPath "templates\$stack\codex-addons.md"
        Test-RequiredPath "templates\$stack\checklist.md"
        Test-RequiredPath "templates\$stack\docs-notes.md"
    }
}

function Test-StaleText {
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/project development plan" "Stale document path"
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/version roadmap" "Stale document path"
    Test-NoPattern "scripts\init-project-template.ps1" "docs/technology selection document" "Stale init text"
}

Test-RequiredPath "README.md"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "project-template\README.md"
Test-RequiredPath "project-template\.codex\rules.md"
Test-RequiredPath "project-template\.agents\skills\project-init\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\handover-review\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\code-review\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\release-check\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\security-review\SKILL.md"

Test-GovernanceFiles
Test-StackTemplates
Test-SkillAscii
Test-SkillFrontmatter
Test-StaleText

if (-not $SkipSkillValidation) {
    $validator = Join-Path $env:USERPROFILE ".codex-b\skills\.system\skill-creator\scripts\quick_validate.py"
    if (Test-Path -LiteralPath $validator) {
        $skillDirs = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Directory
        foreach ($dir in $skillDirs) {
            $result = & python $validator $dir.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                Add-Error "Skill validation failed: $($dir.Name) $result"
            }
        }
    } else {
        Write-Host "[warn] Skill validator not found; skipped quick_validate.py"
    }
}

if ($errors.Count -gt 0) {
    Write-Host "[fail] Template validation failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Template validation passed"
