param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,

    [string]$ProjectName = "",

    [ValidateSet("Lite", "Standard", "Enterprise")]
    [string]$Mode = "Standard",

    [string[]]$Stacks = @(),

    [ValidateSet("none", "claude-code", "codex", "all")]
    [string]$NativeAgentAdapter = "none",

    [switch]$Upgrade,

    [switch]$ExportUpgradeTemplates,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "[init] $Message"
}

function Get-MappedTemplatePath {
    param([string]$RelativePath)
    if ($RelativePath -like "docs\*" -or $RelativePath -like "docs/*") {
        return Join-Path ".forgekit\docs" ($RelativePath.Substring(5))
    }
    if ($RelativePath -like "changes\*" -or $RelativePath -like "changes/*") {
        return Join-Path ".forgekit\changes" ($RelativePath.Substring(8))
    }
    return $RelativePath
}

function Test-SkipTemplatePath {
    param([string]$RelativePath)
    $normalized = $RelativePath.Replace('\', '/')
    if ($normalized -eq ".forgekit/template-manifest.json") { return $true }
    if ($normalized -eq ".forgekit/template-lock.json") { return $true }
    if ($normalized -eq ".forgekit/upgrade-report.md") { return $true }
    if ($normalized -eq ".forgekit/archive-plan.md") { return $true }
    if ($normalized -eq ".forgekit/archive-apply-report.md") { return $true }
    if ($normalized -eq ".forgekit/archive-reference-report.md") { return $true }
    if ($normalized -eq ".forgekit/current-docs-sync-report.md") { return $true }
    if ($normalized -eq ".forgekit/smart-archive-report.md") { return $true }
    if ($normalized -eq ".forgekit/smart-archive-apply-report.md") { return $true }
    if ($normalized -like ".forgekit/upgrade-export/*") { return $true }
    if ($normalized -like ".forgekit/upgrade/*") { return $true }
    return $false
}

function Get-RelativePathCompat {
    param(
        [string]$FromPath,
        [string]$ToPath
    )

    try {
        if ([System.IO.Path].GetMethod("GetRelativePath", [type[]]@([string], [string]))) {
            return [System.IO.Path]::GetRelativePath($FromPath, $ToPath)
        }
    } catch {
        # Windows PowerShell 5.1 does not expose Path.GetRelativePath.
    }

    try {
        $fromFull = [System.IO.Path]::GetFullPath($FromPath)
        $toFull = [System.IO.Path]::GetFullPath($ToPath)
        if (-not $fromFull.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
            $fromFull = $fromFull + [System.IO.Path]::DirectorySeparatorChar
        }
        $fromUri = New-Object System.Uri($fromFull)
        $toUri = New-Object System.Uri($toFull)
        if ($fromUri.Scheme -ne $toUri.Scheme) {
            return "<path-to-forgekit>"
        }
        $relativeUri = $fromUri.MakeRelativeUri($toUri)
        $relative = [System.Uri]::UnescapeDataString($relativeUri.ToString())
        return $relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
    } catch {
        return "<path-to-forgekit>"
    }
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
        if (Test-SkipTemplatePath $relativePath) {
            return
        }
        $destinationRelativePath = Get-MappedTemplatePath $relativePath
        $destinationFile = Join-Path $DestinationDir $destinationRelativePath
        $destinationParent = Split-Path -Parent $destinationFile

        if (-not (Test-Path -LiteralPath $destinationParent)) {
            New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
        }

        if ((Test-Path -LiteralPath $destinationFile) -and -not $Overwrite) {
            Write-Host "[skip] $relativePath already exists"
            return
        }

        Copy-Item -LiteralPath $_.FullName -Destination $destinationFile -Force:$Overwrite
        Write-Host "[copy] $destinationRelativePath"
    }
}

function Write-BoundaryConfig {
    param(
        [string]$DestinationDir,
        [string]$ForgeKitRoot,
        [string]$ProjectRoot,
        [string]$SelectedMode,
        [switch]$Overwrite
    )

    $boundaryFile = Join-Path $DestinationDir ".forgekit\project-boundary.yml"
    if ((Test-Path -LiteralPath $boundaryFile) -and -not $Overwrite) {
        Write-Host "[skip] .forgekit\project-boundary.yml already exists"
        return
    }

    $relativeForgeKitRoot = Get-RelativePathCompat -FromPath $DestinationDir -ToPath $ForgeKitRoot
    if ([string]::IsNullOrWhiteSpace($relativeForgeKitRoot)) {
        $relativeForgeKitRoot = "<path-to-forgekit>"
    }

    $lines = @(
        'forgekit:',
        '  version: "0.33.0"',
        "  mode: `"$SelectedMode`"",
        '',
        'roots:',
        "  forgekit_root: `"$relativeForgeKitRoot`"",
        "  project_root: `"$ProjectRoot`"",
        '  managed_docs_root: ".forgekit/docs"',
        '  change_root: ".forgekit/changes"',
        '  business_docs_roots:',
        '    - "docs"',
        '',
        'write_policy:',
        '  allow:',
        '    - ".codex/**"',
        '    - ".agents/**"',
        '    - ".claude/**"',
        '    - ".forgekit/docs/**"',
        '    - ".forgekit/changes/**"',
        '  task_scoped:',
        '    - "src/**"',
        '    - "tests/**"',
        '    - "scripts/**"',
        '  read_mostly:',
        '    - "docs/**"',
        '  ask:',
        '    - "README.md"',
        '    - "AGENTS.md"',
        '    - "CLAUDE.md"',
        '    - ".github/**"',
        '    - "package.json"',
        '    - "pom.xml"',
        '    - "build.gradle"',
        '  readonly:',
        "    - `"$relativeForgeKitRoot/**`"",
        '    - ".git/**"',
        '    - "node_modules/**"',
        '    - "target/**"',
        '    - "dist/**"',
        '    - "build/**"'
    )
    Set-Content -LiteralPath $boundaryFile -Value $lines -Encoding UTF8
    Write-Host "[copy] .forgekit\project-boundary.yml"
}

function Invoke-TemplateVersioning {
    param(
        [string]$Command,
        [string]$DestinationDir
    )

    $script = Join-Path $templateRoot "scripts\update-template-manifest.py"
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command py -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw "Python is required for ForgeKit template versioning. Install Python or run scripts/update-template-manifest.py manually."
    }

    if ($Command -eq "install-lock") {
        & $python.Source $script install-lock --repo-root $templateRoot --project-root $DestinationDir
    } elseif ($Command -eq "upgrade-report") {
        & $python.Source $script upgrade-report --repo-root $templateRoot --project-root $DestinationDir
    } else {
        throw "Unknown template versioning command: $Command"
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Template versioning command failed: $Command"
    }
}

function Initialize-CodeRoot {
    param(
        [string]$DestinationDir,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Name)) {
        return "."
    }

    $safeName = $Name.Trim()
    if ($safeName -match '[\\/:*?"<>|]') {
        throw "ProjectName contains characters that cannot be used as a folder name: $Name"
    }

    $codeRoot = Join-Path $DestinationDir $safeName
    if (-not (Test-Path -LiteralPath $codeRoot)) {
        New-Item -ItemType Directory -Force -Path $codeRoot | Out-Null
        Write-Host "[copy] $safeName\"
    } else {
        Write-Host "[skip] $safeName\ already exists"
    }
    return "./$safeName"
}

function Invoke-NativeAgentAdapterGeneration {
    param(
        [string]$DestinationDir,
        [string]$Target,
        [switch]$Overwrite
    )

    if ($Target -eq "none") {
        return
    }

    $script = Join-Path $templateRoot "scripts\generate-native-agent-adapter.py"
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw "Python is required to generate ForgeKit native agent adapter files."
    }

    $argsList = @(
        $script,
        "--target", $Target,
        "--project-root", $DestinationDir
    )
    if ($Overwrite) {
        $argsList += "--force"
    }

    & $python.Source @argsList
    if ($LASTEXITCODE -ne 0) {
        throw "Native agent adapter generation failed."
    }
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
        "Use this file as initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, .forgekit/docs/codebase-map.md, .forgekit/docs/local-toolchain.md, and .forgekit/docs/tech-decisions.md manually or with Codex.",
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
        "- The initializer copies the same template files for every mode; mode does not crop files in the current version.",
        "",
        "Recommended Codex startup order:",
        "1. AGENTS.md",
        "2. .forgekit/project-boundary.yml",
        "3. project suitability assessment under .forgekit/docs",
        "4. .forgekit/docs/codebase-map.md",
        "5. .forgekit/docs/local-toolchain.md",
        "6. .forgekit/docs/codex-next-work-order.md",
        "7. .codex/project.md, .codex/scope.md, .codex/commands.md",
        "8. .codex/stacks/README.md, then related .codex/stacks/<stack> only when a stack is confirmed",
        "9. Task-specific governance files",
        "10. For large changes, use governance/large-change-execution.md first",
        "11. For commands, hooks, plugins, or MCP, use governance/team-agent-rollout.md first"
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
        "Use this file as Claude Code initialization metadata. Merge real project facts into .codex/project.md, .codex/scope.md, .forgekit/docs/codebase-map.md, .forgekit/docs/local-toolchain.md, and .forgekit/docs/tech-decisions.md manually or with Claude Code.",
        "",
        "Recommended Claude Code startup order:",
        "1. CLAUDE.md",
        "2. .claude/skills/forgekit-project-workflow/SKILL.md",
        "3. .forgekit/project-boundary.yml",
        "4. .forgekit/docs/codebase-map.md",
        "5. .forgekit/docs/local-toolchain.md",
        "6. .forgekit/docs/codex-next-work-order.md",
        "7. .codex/project.md, .codex/scope.md, .codex/commands.md",
        "8. .codex/stacks/README.md, then related .codex/stacks/<stack> only when a stack is confirmed",
        "9. Task-specific governance files"
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
    Write-Step "mode: report-only upgrade; existing files, lock, and business docs are preserved"
    if ($ExportUpgradeTemplates) {
        Write-Step "export newer templates for review under .forgekit\upgrade-export"
    }
}

if (-not (Test-Path -LiteralPath $resolvedTarget)) {
    New-Item -ItemType Directory -Force -Path $resolvedTarget | Out-Null
}

if ($Upgrade -and -not $Force) {
    Invoke-TemplateVersioning -Command "upgrade-report" -DestinationDir $resolvedTarget
} else {
    Copy-DirectoryContent -SourceDir $projectTemplateDir -DestinationDir $resolvedTarget -Overwrite:$Force

    if (Test-Path -LiteralPath $questionnairesDir) {
        $targetQuestionnaireDir = Join-Path $resolvedTarget ".codex\questionnaires"
        Copy-DirectoryContent -SourceDir $questionnairesDir -DestinationDir $targetQuestionnaireDir -Overwrite:$Force
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
        Copy-DirectoryContent -SourceDir $stackDir -DestinationDir $destinationStackDir -Overwrite:$Force
    }

    $projectRootRelative = Initialize-CodeRoot -DestinationDir $resolvedTarget -Name $ProjectName
    Write-InitMetadata -DestinationDir $resolvedTarget -Name $ProjectName -SelectedMode $Mode -SelectedStacks $normalizedStacks -Overwrite:$Force
    Write-ClaudeInitMetadata -DestinationDir $resolvedTarget -Name $ProjectName -SelectedMode $Mode -SelectedStacks $normalizedStacks -Overwrite:$Force
    Write-BoundaryConfig -DestinationDir $resolvedTarget -ForgeKitRoot $templateRoot -ProjectRoot $projectRootRelative -SelectedMode $Mode -Overwrite
    Invoke-TemplateVersioning -Command "install-lock" -DestinationDir $resolvedTarget
    Invoke-NativeAgentAdapterGeneration -DestinationDir $resolvedTarget -Target $NativeAgentAdapter -Overwrite:$Force
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
Write-Host "Boundary:"
Write-Host "- ForgeKitRoot is the toolkit/template source: $templateRoot"
if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    Write-Host "- ProjectRoot is the business repository and Git commit location: $resolvedTarget"
} else {
    Write-Host "- Outer workspace is ForgeKit governance: $resolvedTarget"
    Write-Host "- ProjectRoot is the business code folder and Git commit location: $(Join-Path $resolvedTarget $ProjectName)"
}
Write-Host "- Managed ForgeKit docs default to .forgekit/docs; change artifacts default to .forgekit/changes."
Write-Host "- Existing business docs/ is read-mostly by default; do not write ForgeKit governance templates there unless the user confirms."
Write-Host "- Do not copy ForgeKit itself into ProjectRoot or commit ForgeKitRoot as part of the business repository."
if ($NativeAgentAdapter -ne "none" -and -not $Upgrade) {
    Write-Host "- Native Agent Adapter was generated for target: $NativeAgentAdapter. Generated config still needs runtime verification before it can be called native success."
    Write-Host "- Codex schema check: python scripts\check-codex-native-agents.py --repo-root ."
}
Write-Host ""
Write-Host "Do not choose a tech stack here. ForgeKit will confirm or infer it during the discovery interview."
if ($Upgrade) {
    Write-Host "Upgrade note: report-only mode preserved existing files and lock. Review .forgekit/upgrade-report.md and candidate templates under .forgekit/upgrade-export manually."
}
