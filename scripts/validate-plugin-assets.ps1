param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$forgekitVersion = (Get-Content (Join-Path $repoRoot "VERSION") -Raw).Trim()

# v0.47 validates capabilities and behavior; historical gates are version-pinned.
if ($forgekitVersion -eq "0.47.0") {
    & python -B (Join-Path $repoRoot "scripts/gate-v047.py") --repo-root $repoRoot --static-only
    exit $LASTEXITCODE
}

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

function Test-VersionField {
    param(
        [string]$Label,
        [string]$RelativePath,
        [string]$Field,
        [AllowNull()]
        [object]$Actual
    )
    $actualText = if ($null -eq $Actual) { "<missing>" } else { [string]$Actual }
    if ($actualText -ne $forgekitVersion) {
        Add-Error "$Label mismatch at $($RelativePath) [$Field]: expected '$forgekitVersion' from VERSION, actual '$actualText'"
    }
}

function Test-ReleaseVersionConsistency {
    $codexManifestPath = Join-Path $repoRoot ".codex-plugin\plugin.json"
    $claudeManifestPath = Join-Path $repoRoot ".claude-plugin\plugin.json"
    $agentsMarketplacePath = Join-Path $repoRoot ".agents\plugins\marketplace.json"
    $claudeMarketplacePath = Join-Path $repoRoot ".claude-plugin\marketplace.json"
    $statePath = Join-Path $repoRoot "project-template\.forgekit\state.json"
    $templateManifestPath = Join-Path $repoRoot "project-template\.forgekit\template-manifest.json"

    $codexManifest = Get-Content -LiteralPath $codexManifestPath -Raw | ConvertFrom-Json
    Test-VersionField "Codex plugin version" ".codex-plugin\plugin.json" "version" $codexManifest.version

    $claudeManifest = Get-Content -LiteralPath $claudeManifestPath -Raw | ConvertFrom-Json
    Test-VersionField "Claude plugin version" ".claude-plugin\plugin.json" "version" $claudeManifest.version

    $agentsMarketplace = Get-Content -LiteralPath $agentsMarketplacePath -Raw | ConvertFrom-Json
    $agentsPlugins = @($agentsMarketplace.plugins | Where-Object { $_.name -eq "forgekit" })
    if ($agentsPlugins.Count -ne 1) {
        Add-Error "Expected exactly one forgekit plugin at .agents\plugins\marketplace.json [plugins], actual count '$($agentsPlugins.Count)'"
    } else {
        Test-VersionField "Agents marketplace plugin version" ".agents\plugins\marketplace.json" "plugins[forgekit].version" $agentsPlugins[0].version
    }

    $claudeMarketplace = Get-Content -LiteralPath $claudeMarketplacePath -Raw | ConvertFrom-Json
    Test-VersionField "Claude marketplace version" ".claude-plugin\marketplace.json" "version" $claudeMarketplace.version
    $claudePlugins = @($claudeMarketplace.plugins | Where-Object { $_.name -eq "forgekit" })
    if ($claudePlugins.Count -ne 1) {
        Add-Error "Expected exactly one forgekit plugin at .claude-plugin\marketplace.json [plugins], actual count '$($claudePlugins.Count)'"
    } else {
        Test-VersionField "Claude marketplace plugin version" ".claude-plugin\marketplace.json" "plugins[forgekit].version" $claudePlugins[0].version
    }

    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    Test-VersionField "Template state ForgeKit version" "project-template\.forgekit\state.json" "forgekit_version" $state.forgekit_version

    $templateManifest = Get-Content -LiteralPath $templateManifestPath -Raw | ConvertFrom-Json
    Test-VersionField "Template manifest version" "project-template\.forgekit\template-manifest.json" "template_version" $templateManifest.template_version
}

function Test-SharedSkillDistribution {
    $checker = Join-Path $repoRoot "scripts\sync-skill-projections.py"
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & python $checker check --repo-root $repoRoot 2>&1
        $projectionExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($projectionExitCode -ne 0) {
        Add-Error "Skill projection check failed: $($output -join [Environment]::NewLine)"
    }
    $stageCValidator = Join-Path $repoRoot "scripts\validate-stage-c-skills.py"
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $stageCOutput = & python -B $stageCValidator --repo-root $repoRoot 2>&1
        $stageCExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($stageCExitCode -ne 0) {
        Add-Error "Stage C Skill contract check failed: $($stageCOutput -join [Environment]::NewLine)"
    }
    $stageDValidator = Join-Path $repoRoot "scripts\validate-stage-d-skills.py"
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $stageDOutput = & python -B $stageDValidator --repo-root $repoRoot 2>&1
        $stageDExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($stageDExitCode -ne 0) {
        Add-Error "Stage D Skill contract check failed: $($stageDOutput -join [Environment]::NewLine)"
    }
    $stageEValidator = Join-Path $repoRoot "scripts\validate-stage-e-release.py"
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $stageEOutput = & python -B $stageEValidator --repo-root $repoRoot 2>&1
        $stageEExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($stageEExitCode -ne 0) {
        Add-Error "Stage E release structure check failed: $($stageEOutput -join [Environment]::NewLine)"
    }
}

function Test-ReleaseGateWiring {
    $wiringValidator = Join-Path $repoRoot "scripts\validate-release-gate-wiring.py"
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $wiringOutput = & python -B $wiringValidator --repo-root $repoRoot 2>&1
        $wiringExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    if ($wiringExitCode -ne 0) {
        Add-Error "Stage E gate wiring check failed: $($wiringOutput -join [Environment]::NewLine)"
    }
}

function Test-PluginManifest {
    $codexManifestPath = Join-Path $repoRoot ".codex-plugin\plugin.json"
    $claudeManifestPath = Join-Path $repoRoot ".claude-plugin\plugin.json"

    $codexManifest = Get-Content -LiteralPath $codexManifestPath -Raw | ConvertFrom-Json
    if ($codexManifest.name -ne "forgekit") {
        Add-Error "Unexpected Codex plugin name: $($codexManifest.name)"
    }
    if ($codexManifest.skills -ne "./skills/") {
        Add-Error "Codex plugin skills must point to ./skills/"
    }

    $claudeManifest = Get-Content -LiteralPath $claudeManifestPath -Raw | ConvertFrom-Json
    if ($claudeManifest.name -ne "forgekit") {
        Add-Error "Unexpected Claude plugin name: $($claudeManifest.name)"
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
Test-RequiredPath "config\skill-projections.json"
Test-RequiredPath "scripts\sync-skill-projections.py"
Test-RequiredPath "scripts\validate-stage-c-skills.py"
Test-RequiredPath "scripts\validate-stage-d-skills.py"
Test-RequiredPath "scripts\validate-stage-e-release.py"
Test-RequiredPath "scripts\validate-release-gate-wiring.py"
Test-RequiredPath "scripts\test-fresh-clone-crlf.py"
Test-RequiredPath "project-template\AGENTS.md"
Test-RequiredPath "project-template\CLAUDE.md"
Test-RequiredPath "project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
Test-RequiredPath "project-template\.codex\stacks\README.md"
Test-RequiredPath "project-template\scripts\detect-local-toolchain.ps1"
Test-RequiredPath "project-template\scripts\run-harness-check.ps1"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "scripts\init-project-template.sh"
Test-RequiredPath "scripts\test-release-consistency.ps1"

Test-RequiredPattern "README.md" "可选原生 agent 配置" "Current native adapter entry"
Test-RequiredPattern "scripts\init-project-template.ps1" "CLAUDE.md" "Unified initializer Claude guidance"
Test-RequiredPattern "skills\project-init\SKILL.md" "## Trigger Boundary" "Project init trigger boundary"
Test-RequiredPattern "skills\project-suitability\SKILL.md" "suitable-with-constraints" "Project suitability constrained outcome"
Test-RequiredPattern "skills\project-suitability\SKILL.md" "not-recommended" "Project suitability negative outcome"
Test-RequiredPattern "skills\project-suitability\SKILL.md" "insufficient-evidence" "Project suitability evidence outcome"
Test-RequiredPattern "skills\large-change-planning\SKILL.md" "## Impact Branch" "Large change impact branch"

Test-ForbiddenPath "plugins\forgekit-codex-workflow"
Test-ForbiddenPath "plugins\forgekit-claude-workflow"

Test-PluginManifest
Test-ReleaseVersionConsistency
Test-ReleaseGateWiring
Test-SharedSkillDistribution
Test-SkillAscii

if ($errors.Count -gt 0) {
    Write-Host "[fail] Unified plugin asset validation failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Unified plugin asset validation passed"
