param()

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pluginRoot = Split-Path -Parent $scriptRoot
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $errors.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param([string]$RelativePath)
    $path = Join-Path $pluginRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Error "Missing required path: $RelativePath"
    }
}

function Test-ForbiddenPath {
    param([string]$RelativePath)
    $path = Join-Path $pluginRoot $RelativePath
    if (Test-Path -LiteralPath $path) {
        Add-Error "Forbidden path in plugin package: $RelativePath"
    }
}

function Test-SkillAscii {
    $skillRoot = Join-Path $pluginRoot "skills"
    if (-not (Test-Path -LiteralPath $skillRoot)) {
        return
    }

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

function Test-SkillFrontmatter {
    $skillRoot = Join-Path $pluginRoot "skills"
    if (-not (Test-Path -LiteralPath $skillRoot)) {
        return
    }

    $skillFiles = Get-ChildItem -LiteralPath $skillRoot -Recurse -Filter "SKILL.md"
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

function Test-PluginManifest {
    $manifestPath = Join-Path $pluginRoot ".codex-plugin\plugin.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Add-Error "Missing plugin manifest: .codex-plugin\plugin.json"
        return
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.name -ne "forgekit-codex-workflow") {
        Add-Error "Unexpected plugin name: $($manifest.name)"
    }
    if ($manifest.version -ne "0.10.1") {
        Add-Error "Unexpected plugin version: $($manifest.version)"
    }
    if ($manifest.skills -ne "./skills/") {
        Add-Error "Plugin manifest must point skills to ./skills/"
    }
    if ($manifest.PSObject.Properties.Name -contains "mcpServers") {
        Add-Error "Plugin must not enable MCP by default"
    }
    if ($manifest.PSObject.Properties.Name -contains "hooks") {
        Add-Error "Plugin must not enable hooks in manifest"
    }
}

Test-RequiredPath ".codex-plugin\plugin.json"
Test-RequiredPath "README.md"
Test-RequiredPath "README.zh-CN.md"
Test-RequiredPath "skills\project-init\SKILL.md"
Test-RequiredPath "skills\project-bootstrap-fill\SKILL.md"
Test-RequiredPath "skills\handover-review\SKILL.md"
Test-RequiredPath "skills\code-review\SKILL.md"
Test-RequiredPath "skills\release-check\SKILL.md"
Test-RequiredPath "skills\security-review\SKILL.md"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "scripts\detect-local-toolchain.ps1"
Test-RequiredPath "scripts\run-harness-check.ps1"
Test-RequiredPath "assets\project-template\AGENTS.md"
Test-RequiredPath "assets\project-template\.codex\commands.md"
Test-RequiredPath "assets\project-template\.codex\hooks.md"
Test-RequiredPath "assets\project-template\.codex\config.example.toml"
Test-RequiredPath "assets\project-template\.codex\stacks\README.md"
Test-RequiredPath "assets\templates\java-springboot\README.md"
Test-RequiredPath "assets\templates\vue\README.md"
Test-RequiredPath "assets\templates\csharp-dotnet\README.md"
Test-RequiredPath "assets\templates\go-service\README.md"
Test-RequiredPath "assets\templates\php-laravel\README.md"
Test-RequiredPath "assets\templates\rust-cli-service\README.md"
Test-RequiredPath "assets\templates\flutter-dart\README.md"
Test-RequiredPath "assets\templates\cpp-cmake\README.md"
Test-RequiredPath "assets\templates\kotlin-spring\README.md"
Test-RequiredPath "assets\templates\swift-ios\README.md"
Test-RequiredPath "assets\templates\ruby-rails\README.md"
Test-RequiredPath "assets\templates\r-data-analysis\README.md"
Test-RequiredPath "assets\questionnaires\README.md"
Test-RequiredPath "assets\docs\install.md"
Test-RequiredPath "assets\docs\upgrade.md"
Test-RequiredPath "assets\docs\safety.md"
Test-RequiredPath "assets\docs\feedback.md"

if (-not (Select-String -Path (Join-Path $pluginRoot 'scripts\init-project-template.ps1') -Pattern '[ValidateSet("Lite", "Standard", "Enterprise")]' -SimpleMatch -Quiet)) {
    Add-Error "Plugin initializer must expose -Mode Lite/Standard/Enterprise"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.md') -Pattern '-Mode Standard' -SimpleMatch -Quiet)) {
    Add-Error "English README must show -Mode in Quick Start"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.md') -Pattern 'Discovery Interview' -SimpleMatch -Quiet)) {
    Add-Error "English README must explain discovery interview"
}
if (Select-String -Path (Join-Path $pluginRoot 'README.md') -Pattern '## Common Stacks' -SimpleMatch -Quiet) {
    Add-Error "English README must not front-load stack selection"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.md') -Pattern 'cd D:\projects\my-app' -SimpleMatch -Quiet)) {
    Add-Error "English README must show how to enter the generated project"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.md') -Pattern 'Read AGENTS.md and help me initialize this project with ForgeKit.' -SimpleMatch -Quiet)) {
    Add-Error "English README must include the Codex startup message"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.zh-CN.md') -Pattern '-Mode Standard' -SimpleMatch -Quiet)) {
    Add-Error "Chinese README must show -Mode in Quick Start"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.zh-CN.md') -Pattern 'Discovery Interview' -SimpleMatch -Quiet)) {
    Add-Error "Chinese README must explain discovery interview"
}
if (Select-String -Path (Join-Path $pluginRoot 'README.zh-CN.md') -Pattern '## 常用技术栈' -SimpleMatch -Quiet) {
    Add-Error "Chinese README must not front-load stack selection"
}

$projectInitSkill = Join-Path $pluginRoot 'skills\project-init\SKILL.md'
if (-not (Select-String -Path $projectInitSkill -Pattern 'Classify the discovery state' -SimpleMatch -Quiet)) {
    Add-Error "Project init skill must classify discovery state"
}
if (-not (Select-String -Path $projectInitSkill -Pattern 'options-needed' -SimpleMatch -Quiet)) {
    Add-Error "Project init skill must include options-needed state"
}
if (-not (Select-String -Path $projectInitSkill -Pattern 'research-needed' -SimpleMatch -Quiet)) {
    Add-Error "Project init skill must include research-needed state"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.zh-CN.md') -Pattern 'cd D:\projects\my-app' -SimpleMatch -Quiet)) {
    Add-Error "Chinese README must show how to enter the generated project"
}
if (-not (Select-String -Path (Join-Path $pluginRoot 'README.zh-CN.md') -Pattern 'AGENTS.md' -SimpleMatch -Quiet)) {
    Add-Error "Chinese README must include the Codex startup message"
}

Test-ForbiddenPath "user-rules"
Test-ForbiddenPath "document"
Test-ForbiddenPath ".git"

Test-PluginManifest
Test-SkillAscii
Test-SkillFrontmatter

if ($errors.Count -gt 0) {
    Write-Host "[fail] Plugin asset validation failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Plugin asset validation passed"
