param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$ProjectName = "",

    [ValidateSet("Lite", "Standard", "Enterprise")]
    [string]$Mode = "Standard",

    [string[]]$Stacks = @(),

    [switch]$Upgrade,

    [switch]$ExportUpgradeTemplates,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[init] $Message"
}

function Copy-DirectoryContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceDir,

        [Parameter(Mandatory = $true)]
        [string]$DestinationDir,

        [switch]$Overwrite
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        throw "Source directory not found: $SourceDir"
    }

    New-Item -ItemType Directory -Force -Path $DestinationDir | Out-Null

    Get-ChildItem -LiteralPath $SourceDir -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($SourceDir.Length).TrimStart('\', '/')
        $destinationFile = Join-Path $DestinationDir $relativePath
        $destinationParent = Split-Path -Parent $destinationFile

        if (-not (Test-Path -LiteralPath $destinationParent)) {
            New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
        }

        if ((Test-Path -LiteralPath $destinationFile) -and -not $Overwrite) {
            Write-Host "[skip] $relativePath already exists"
            return
        }

        Copy-Item -LiteralPath $_.FullName -Destination $destinationFile -Force:$Overwrite
        Write-Host "[copy] $relativePath"
    }
}

function New-UpgradeState {
    return [PSCustomObject]@{
        Copied = New-Object System.Collections.Generic.List[string]
        SkippedSame = New-Object System.Collections.Generic.List[string]
        SkippedDifferent = New-Object System.Collections.Generic.List[string]
        ExportedTemplates = New-Object System.Collections.Generic.List[string]
    }
}

function Test-FileSame {
    param(
        [string]$LeftPath,
        [string]$RightPath
    )
    if (-not (Test-Path -LiteralPath $LeftPath) -or -not (Test-Path -LiteralPath $RightPath)) {
        return $false
    }
    $leftHash = Get-FileHash -LiteralPath $LeftPath -Algorithm SHA256
    $rightHash = Get-FileHash -LiteralPath $RightPath -Algorithm SHA256
    return $leftHash.Hash -eq $rightHash.Hash
}

function Copy-DirectoryContentForUpgrade {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceDir,

        [Parameter(Mandatory = $true)]
        [string]$DestinationDir,

        [Parameter(Mandatory = $true)]
        [string]$ExportDir,

        [Parameter(Mandatory = $true)]
        $State,

        [switch]$ExportTemplates
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        throw "Source directory not found: $SourceDir"
    }

    New-Item -ItemType Directory -Force -Path $DestinationDir | Out-Null

    Get-ChildItem -LiteralPath $SourceDir -Recurse -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($SourceDir.Length).TrimStart('\', '/')
        $destinationFile = Join-Path $DestinationDir $relativePath
        $destinationParent = Split-Path -Parent $destinationFile

        if (-not (Test-Path -LiteralPath $destinationParent)) {
            New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
        }

        if (-not (Test-Path -LiteralPath $destinationFile)) {
            Copy-Item -LiteralPath $_.FullName -Destination $destinationFile
            $State.Copied.Add($relativePath) | Out-Null
            Write-Host "[copy] $relativePath"
            return
        }

        if (Test-FileSame -LeftPath $_.FullName -RightPath $destinationFile) {
            $State.SkippedSame.Add($relativePath) | Out-Null
            Write-Host "[same] $relativePath"
            return
        }

        $State.SkippedDifferent.Add($relativePath) | Out-Null
        Write-Host "[review] $relativePath differs; existing file preserved"

        if ($ExportTemplates) {
            $exportFile = Join-Path $ExportDir $relativePath
            $exportParent = Split-Path -Parent $exportFile
            if (-not (Test-Path -LiteralPath $exportParent)) {
                New-Item -ItemType Directory -Force -Path $exportParent | Out-Null
            }
            Copy-Item -LiteralPath $_.FullName -Destination $exportFile -Force
            $State.ExportedTemplates.Add($relativePath) | Out-Null
        }
    }
}

function New-Text {
    param([int[]]$CodePoints)
    $builder = New-Object System.Text.StringBuilder
    foreach ($codePoint in $CodePoints) {
        [void]$builder.Append([char]$codePoint)
    }
    return $builder.ToString()
}

function Write-UpgradeReport {
    param(
        [string]$DestinationDir,
        [string]$ExportDir,
        $State,
        [switch]$ExportTemplates
    )

    $reportPath = Join-Path $DestinationDir ".codex\upgrade-report.md"
    $reportParent = Split-Path -Parent $reportPath
    if (-not (Test-Path -LiteralPath $reportParent)) {
        New-Item -ItemType Directory -Force -Path $reportParent | Out-Null
    }

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# ForgeKit Upgrade Report") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("Generated by scripts/init-project-template.ps1 -Upgrade.") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("Existing project files were preserved. Files listed under review differ from the newer ForgeKit template and should be merged manually or with AI assistance.") | Out-Null
    $lines.Add("") | Out-Null
    $lines.Add("## Copied Missing Files") | Out-Null
    if ($State.Copied.Count -eq 0) { $lines.Add("- None") | Out-Null } else { $State.Copied | ForEach-Object { $lines.Add("- $_") | Out-Null } }
    $lines.Add("") | Out-Null
    $lines.Add("## Review Existing Files") | Out-Null
    if ($State.SkippedDifferent.Count -eq 0) { $lines.Add("- None") | Out-Null } else { $State.SkippedDifferent | ForEach-Object { $lines.Add("- $_") | Out-Null } }
    $lines.Add("") | Out-Null
    $lines.Add("## Same Files") | Out-Null
    if ($State.SkippedSame.Count -eq 0) { $lines.Add("- None") | Out-Null } else { $State.SkippedSame | ForEach-Object { $lines.Add("- $_") | Out-Null } }
    $lines.Add("") | Out-Null
    $lines.Add("## Merge Guidance") | Out-Null
    $lines.Add("- Do not overwrite project facts with template text.") | Out-Null
    $lines.Add("- Prefer merging new sections, safety rules, scripts, and routing hints into existing files.") | Out-Null
    $lines.Add("- Ask the AI assistant to compare this report with current project files before applying changes.") | Out-Null
    if ($ExportTemplates) {
        $lines.Add("- New template copies were exported under: $ExportDir") | Out-Null
    } else {
        $lines.Add("- Re-run with -ExportUpgradeTemplates to export newer template copies for side-by-side diff.") | Out-Null
    }
    $lines.Add("") | Out-Null
    $lines.Add("Legacy filename migration:") | Out-Null
    $lines.Add("- Upgrade mode does not automatically rename existing Chinese document names or `#Uxxxx` escaped file names.") | Out-Null
    $lines.Add("- Review the detected list below and migrate paths manually after checking project-specific references.") | Out-Null
    $legacyPatterns = @(
        "#U",
        (New-Text @(0x4EE3,0x7801,0x5E93,0x5730,0x56FE)),
        (New-Text @(0x672C,0x5730,0x5DE5,0x5177,0x94FE,0x68C0,0x67E5)),
        (New-Text @(0x7248,0x672C,0x8DEF,0x7EBF,0x56FE)),
        (New-Text @(0x7248,0x672C,0x66F4,0x65B0,0x8BB0,0x5F55)),
        (New-Text @(0x9879,0x76EE,0x5F00,0x53D1,0x65B9,0x6848)),
        (New-Text @(0x9879,0x76EE,0x4EFB,0x52A1,0x770B,0x677F)),
        (New-Text @(0x6280,0x672F,0x9009,0x578B)),
        (New-Text @(0x4F7F,0x7528,0x8BF4,0x660E))
    )
    $legacyMatches = New-Object System.Collections.Generic.List[string]
    Get-ChildItem -LiteralPath $DestinationDir -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($DestinationDir.Length + 1)
        foreach ($pattern in $legacyPatterns) {
            if ($relative -like "*$pattern*") {
                $legacyMatches.Add($relative) | Out-Null
                break
            }
        }
    }
    if ($legacyMatches.Count -eq 0) {
        $lines.Add("- Detected: none.") | Out-Null
    } else {
        $lines.Add("- Detected legacy paths:") | Out-Null
        foreach ($item in $legacyMatches) {
            $lines.Add("  - $item") | Out-Null
        }
    }
    $lines.Add("") | Out-Null
    $lines.Add("Suggested prompt:") | Out-Null
    $lines.Add("Review .codex/upgrade-report.md and merge useful new ForgeKit template sections into the existing project files without overwriting project facts.") | Out-Null

    Set-Content -LiteralPath $reportPath -Value $lines -Encoding UTF8
    Write-Host "[copy] .codex\upgrade-report.md"
}

function Write-InitMetadata {
    param(
        [string]$DestinationDir,
        [string]$Name,
        [string]$SelectedMode,
        [string[]]$SelectedStacks,
        [switch]$Overwrite
    )

    $metadataFile = Join-Path $DestinationDir ".codex\init.generated.md"
    if ((Test-Path -LiteralPath $metadataFile) -and -not $Overwrite) {
        Write-Host "[skip] .codex\init.generated.md already exists"
        return
    }

    $stackText = if ($SelectedStacks.Count -gt 0) { $SelectedStacks -join ", " } else { "deferred" }
    $projectText = if ([string]::IsNullOrWhiteSpace($Name)) { "" } else { $Name }

    $lines = @(
        "# Init Metadata",
        "",
        "Generated by scripts/init-project-template.ps1.",
        "",
        "- ProjectName: $projectText",
        "- Mode: $SelectedMode",
        "- Stacks: $stackText",
        "- StackSelection: deferred means no stack was chosen during initialization. This is normal.",
        "",
        "Use this file as initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, the docs codebase map, the local toolchain check document, and docs/tech-decisions.md manually or with Codex.",
        "",
        "Stack guidance:",
        "- New projects: confirm product shape, users, constraints, risks, and the v0.1.0 closed loop before choosing a stack.",
        "- Existing projects: infer the stack from project files before asking the user technical-stack questions.",
        "- Feature, fix, and refactor work defaults to the existing stack unless the user explicitly asks for migration or architecture change.",
        "",
        "Mode guidance:",
        "- Lite: metadata hint for lightweight AI filling and governance discussion.",
        "- Standard: metadata hint for normal AI filling and governance discussion.",
        "- Enterprise: metadata hint for stricter AI filling and governance discussion.",
        "- The initializer copies the same template files for every mode; mode does not crop files in v0.14.0.",
        "",
        "Recommended Codex startup order:",
        "1. AGENTS.md",
        "2. project suitability assessment under docs",
        "3. docs codebase map",
        "4. local toolchain check document under docs",
        "5. Codex next-step work order under docs",
        "6. .codex/project.md, .codex/scope.md, .codex/commands.md",
        "7. .codex/stacks/README.md, then related .codex/stacks/<stack>/ only when a stack is confirmed",
        "8. Task-specific governance files",
        "9. For large changes, use governance/large-change-execution.md first",
        "10. For commands, hooks, plugins, or MCP, use governance/team-agent-rollout.md first"
    )

    Set-Content -LiteralPath $metadataFile -Value $lines -Encoding UTF8
    Write-Host "[copy] .codex\init.generated.md"
}

function Write-ClaudeInitMetadata {
    param(
        [string]$DestinationDir,
        [string]$Name,
        [string]$SelectedMode,
        [string[]]$SelectedStacks,
        [switch]$Overwrite
    )

    $metadataFile = Join-Path $DestinationDir ".claude\init.generated.md"
    if ((Test-Path -LiteralPath $metadataFile) -and -not $Overwrite) {
        Write-Host "[skip] .claude\init.generated.md already exists"
        return
    }

    $stackText = if ($SelectedStacks.Count -gt 0) { $SelectedStacks -join ", " } else { "deferred" }
    $projectText = if ([string]::IsNullOrWhiteSpace($Name)) { "" } else { $Name }

    $lines = @(
        "# Claude Init Metadata",
        "",
        "Generated by scripts/init-project-template.ps1.",
        "",
        "- ProjectName: $projectText",
        "- Mode: $SelectedMode",
        "- Stacks: $stackText",
        "- StackSelection: deferred means no stack was chosen during initialization. This is normal.",
        "",
        "Use this file as Claude Code initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, the docs codebase map, the local toolchain check document, and docs/tech-decisions.md manually or with Claude Code.",
        "",
        "Recommended Claude Code startup order:",
        "1. CLAUDE.md",
        "2. .claude/skills/forgekit-project-workflow/SKILL.md",
        "3. docs codebase map",
        "4. local toolchain check document under docs",
        "5. Codex next-step work order under docs",
        "6. .codex/project.md, .codex/scope.md, .codex/commands.md",
        "7. .codex/stacks/README.md, then related .codex/stacks/<stack>/ only when a stack is confirmed",
        "8. Task-specific governance files"
    )

    $metadataParent = Split-Path -Parent $metadataFile
    if (-not (Test-Path -LiteralPath $metadataParent)) {
        New-Item -ItemType Directory -Force -Path $metadataParent | Out-Null
    }
    Set-Content -LiteralPath $metadataFile -Value $lines -Encoding UTF8
    Write-Host "[copy] .claude\init.generated.md"
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateRoot = Split-Path -Parent $scriptRoot
$projectTemplateDir = Join-Path $templateRoot "project-template"
$templatesDir = Join-Path $templateRoot "templates"
$questionnairesDir = Join-Path $templateRoot "questionnaires"
$normalizedStacks = @()
foreach ($stackValue in $Stacks) {
    if ([string]::IsNullOrWhiteSpace($stackValue)) {
        continue
    }
    $stackValue.Split(',') | ForEach-Object {
        $trimmed = $_.Trim()
        if (-not [string]::IsNullOrWhiteSpace($trimmed)) {
            $normalizedStacks += $trimmed
        }
    }
}

$resolvedTarget = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($TargetPath)

Write-Step "target: $resolvedTarget"
Write-Step "base template: $projectTemplateDir"
if ($Upgrade) {
    if ($Force) {
        throw "-Upgrade cannot be combined with -Force. Upgrade mode must preserve existing project facts; run a non-upgrade initialization separately if you intentionally want overwrites."
    }
    Write-Step "mode: upgrade existing project; existing files are preserved"
    if ($ExportUpgradeTemplates) {
        Write-Step "export newer templates for review under .codex\upgrade-templates"
    }
}

if (-not (Test-Path -LiteralPath $resolvedTarget)) {
    New-Item -ItemType Directory -Force -Path $resolvedTarget | Out-Null
}

$upgradeState = $null
$upgradeExportDir = Join-Path $resolvedTarget ".codex\upgrade-templates"
if ($Upgrade -and -not $Force) {
    $upgradeState = New-UpgradeState
    Copy-DirectoryContentForUpgrade -SourceDir $projectTemplateDir -DestinationDir $resolvedTarget -ExportDir $upgradeExportDir -State $upgradeState -ExportTemplates:$ExportUpgradeTemplates
} else {
    Copy-DirectoryContent -SourceDir $projectTemplateDir -DestinationDir $resolvedTarget -Overwrite:$Force
}

if (Test-Path -LiteralPath $questionnairesDir) {
    $targetQuestionnaireDir = Join-Path $resolvedTarget ".codex\questionnaires"
    if ($Upgrade -and -not $Force) {
        Copy-DirectoryContentForUpgrade -SourceDir $questionnairesDir -DestinationDir $targetQuestionnaireDir -ExportDir (Join-Path $upgradeExportDir ".codex\questionnaires") -State $upgradeState -ExportTemplates:$ExportUpgradeTemplates
    } else {
        Copy-DirectoryContent -SourceDir $questionnairesDir -DestinationDir $targetQuestionnaireDir -Overwrite:$Force
    }
}

foreach ($stack in $normalizedStacks) {
    if ([string]::IsNullOrWhiteSpace($stack)) {
        continue
    }

    $stackDir = Join-Path $templatesDir $stack
    if (-not (Test-Path -LiteralPath $stackDir)) {
        throw "Unknown stack template: $stack"
    }

    $destinationStackDir = Join-Path $resolvedTarget ".codex\stacks\$stack"
    Write-Step "stack template: $stack"
    if ($Upgrade -and -not $Force) {
        Copy-DirectoryContentForUpgrade -SourceDir $stackDir -DestinationDir $destinationStackDir -ExportDir (Join-Path $upgradeExportDir ".codex\stacks\$stack") -State $upgradeState -ExportTemplates:$ExportUpgradeTemplates
    } else {
        Copy-DirectoryContent -SourceDir $stackDir -DestinationDir $destinationStackDir -Overwrite:$Force
    }
}

Write-InitMetadata -DestinationDir $resolvedTarget -Name $ProjectName -SelectedMode $Mode -SelectedStacks $normalizedStacks -Overwrite:$Force
Write-ClaudeInitMetadata -DestinationDir $resolvedTarget -Name $ProjectName -SelectedMode $Mode -SelectedStacks $normalizedStacks -Overwrite:$Force

if ($Upgrade -and -not $Force) {
    Write-UpgradeReport -DestinationDir $resolvedTarget -ExportDir $upgradeExportDir -State $upgradeState -ExportTemplates:$ExportUpgradeTemplates
}

Write-Step "done"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Enter the generated project:"
Write-Host "   cd $resolvedTarget"
Write-Host "2. Start your AI coding tool from that project:"
Write-Host "   Codex: codex"
Write-Host "   Claude Code: claude"
Write-Host "3. Send the startup message:"
Write-Host "   Codex: Read AGENTS.md, prefer .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path."
Write-Host "   Claude Code: Read CLAUDE.md, prefer .agents/skills/project-init/SKILL.md, and help me initialize this project with ForgeKit. Do not read a user-level or system-level project-init path."
Write-Host ""
Write-Host "Do not choose a tech stack here. ForgeKit will confirm or infer it during the discovery interview."
if ($Upgrade) {
    Write-Host "Upgrade note: existing files were preserved. Review .codex/upgrade-report.md and merge useful template updates manually."
}
