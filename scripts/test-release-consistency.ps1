param()

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$validator = Join-Path $scriptRoot "validate-plugin-assets.ps1"
$expectedVersion = (Get-Content -LiteralPath (Join-Path $repoRoot "VERSION") -Raw).Trim()
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Invoke-ReleaseValidator {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $validator 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Invoke-TemplateValidator {
    $templateValidator = Join-Path $scriptRoot "validate-template.ps1"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $templateValidator -SkipSkillValidation 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Invoke-AgentEntryValidator {
    $entryValidator = Join-Path $scriptRoot "validate-agent-entries.py"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python -B $entryValidator --repo-root $repoRoot 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Invoke-StageBMigrationValidator {
    $migrationValidator = Join-Path $scriptRoot "validate-stage-b-entry-migration.py"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python -B $migrationValidator --repo-root $repoRoot 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Assert-ValidationPassed {
    param([string]$Label)
    $result = Invoke-ReleaseValidator
    if ($result.ExitCode -ne 0) {
        throw "$Label expected validation success, actual exit code $($result.ExitCode): $($result.Output)"
    }
    Write-Host "[ok] $Label"
}

function Invoke-RestoringMutation {
    param(
        [string]$Label,
        [string]$RelativePath,
        [scriptblock]$Mutate,
        [string[]]$ExpectedMessages,
        [scriptblock]$ValidationCommand = { Invoke-ReleaseValidator }
    )

    $path = Join-Path $repoRoot $RelativePath
    $originalBytes = [System.IO.File]::ReadAllBytes($path)
    try {
        & $Mutate $path
        $result = & $ValidationCommand
        if ($result.ExitCode -eq 0) {
            throw "$Label expected validation failure, actual exit code 0"
        }
        foreach ($message in $ExpectedMessages) {
            if (-not $result.Output.Contains($message)) {
                throw "$Label failure output missing '$message': $($result.Output)"
            }
        }
        Write-Host "[ok] $Label failed as expected"
    } finally {
        [System.IO.File]::WriteAllBytes($path, $originalBytes)
    }

    $restoredBytes = [System.IO.File]::ReadAllBytes($path)
    if ([System.Convert]::ToBase64String($restoredBytes) -ne [System.Convert]::ToBase64String($originalBytes)) {
        throw "$Label did not restore $RelativePath byte-for-byte"
    }
    Write-Host "[ok] $Label restored $RelativePath"
}

function Invoke-RestoringMultiMutation {
    param(
        [string]$Label,
        [string[]]$RelativePaths,
        [scriptblock]$Mutate,
        [string[]]$ExpectedMessages,
        [scriptblock]$ValidationCommand
    )

    $paths = @($RelativePaths | ForEach-Object { Join-Path $repoRoot $_ })
    $originals = @{}
    foreach ($path in $paths) {
        $originals[$path] = [System.IO.File]::ReadAllBytes($path)
    }
    try {
        & $Mutate $paths
        $result = & $ValidationCommand
        if ($result.ExitCode -eq 0) {
            throw "$Label expected validation failure, actual exit code 0"
        }
        foreach ($message in $ExpectedMessages) {
            if (-not $result.Output.Contains($message)) {
                throw "$Label failure output missing '$message': $($result.Output)"
            }
        }
        Write-Host "[ok] $Label failed as expected"
    } finally {
        foreach ($path in $paths) {
            [System.IO.File]::WriteAllBytes($path, $originals[$path])
        }
    }
    foreach ($path in $paths) {
        $restoredBytes = [System.IO.File]::ReadAllBytes($path)
        if ([System.Convert]::ToBase64String($restoredBytes) -ne [System.Convert]::ToBase64String($originals[$path])) {
            throw "$Label did not restore $path byte-for-byte"
        }
        Write-Host "[ok] $Label restored $path"
    }
}

Assert-ValidationPassed "v$expectedVersion release consistency baseline"

$marketplaceTest = @{
    Label = "marketplace version mutation"
    RelativePath = ".agents\plugins\marketplace.json"
    Mutate = {
        param($Path)
        $text = [System.IO.File]::ReadAllText($Path)
        $needle = '"version": "' + $expectedVersion + '"'
        $replacement = '"version": "0.0.0-mutation"'
        $mutated = $text.Replace($needle, $replacement)
        if ($mutated -eq $text) {
            throw "Marketplace mutation target version '$expectedVersion' was not found"
        }
        [System.IO.File]::WriteAllText($Path, $mutated, $utf8NoBom)
    }
    ExpectedMessages = @(".agents\plugins\marketplace.json", "expected '$expectedVersion'", "actual '0.0.0-mutation'")
}
Invoke-RestoringMutation @marketplaceTest

$packetHelperTest = @{
    Label = "shared upgrade packet helper mutation"
    RelativePath = "scripts\upgrade_review_packets.py"
    Mutate = {
        param($Path)
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n# helper-drift-mutation`n")
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($Path, $mutated)
    }
    ExpectedMessages = @(
        "scripts/upgrade_review_packets.py",
        "project-template/scripts/upgrade_review_packets.py",
        "SHA-256="
    )
    ValidationCommand = { Invoke-TemplateValidator }
}
Invoke-RestoringMutation @packetHelperTest

$agentsAnchorTest = @{
    Label = "AGENTS shared-contract marker mutation"
    RelativePath = "project-template\AGENTS.md"
    Mutate = {
        param($Path)
        $text = [System.IO.File]::ReadAllText($Path)
        $mutated = $text.Replace("governance/agent-entry-contract.md#audit-default", "governance/agent-entry-contract.md#audit-marker-removed")
        if ($mutated -eq $text) {
            throw "AGENTS audit-default mutation marker was not found"
        }
        [System.IO.File]::WriteAllText($Path, $mutated, $utf8NoBom)
    }
    ExpectedMessages = @("AGENTS.md: missing shared-contract anchor: audit-default")
    ValidationCommand = { Invoke-AgentEntryValidator }
}
Invoke-RestoringMutation @agentsAnchorTest

$claudeAnchorTest = @{
    Label = "CLAUDE shared-contract marker mutation"
    RelativePath = "project-template\CLAUDE.md"
    Mutate = {
        param($Path)
        $text = [System.IO.File]::ReadAllText($Path)
        $mutated = $text.Replace("governance/agent-entry-contract.md#bounded-local-authorization", "governance/agent-entry-contract.md#authorization-marker-removed")
        if ($mutated -eq $text) {
            throw "CLAUDE bounded-local-authorization mutation marker was not found"
        }
        [System.IO.File]::WriteAllText($Path, $mutated, $utf8NoBom)
    }
    ExpectedMessages = @("CLAUDE.md: missing shared-contract anchor: bounded-local-authorization")
    ValidationCommand = { Invoke-AgentEntryValidator }
}
Invoke-RestoringMutation @claudeAnchorTest

$reviewConvergenceTest = @{
    Label = "entry code-review convergence mutation"
    RelativePath = "project-template\AGENTS.md"
    Mutate = {
        param($Path)
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $suffix = [System.Text.Encoding]::ASCII.GetBytes("`nInitial review blocks must use blocker-recheck before approval.`n")
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($Path, $mutated)
    }
    ExpectedMessages = @("AGENTS.md: forbidden code-review convergence copy")
    ValidationCommand = { Invoke-AgentEntryValidator }
}
Invoke-RestoringMutation @reviewConvergenceTest

$auditContradictionTest = @{
    Label = "entry audit contradiction mutation"
    RelativePath = "project-template\AGENTS.md"
    Mutate = {
        param($Path)
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $suffix = [System.Text.Encoding]::ASCII.GetBytes("`nAudits may automatically modify files without a repair request.`n")
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($Path, $mutated)
    }
    ExpectedMessages = @("AGENTS.md: contradiction audit-auto-write")
    ValidationCommand = { Invoke-AgentEntryValidator }
}
Invoke-RestoringMutation @auditContradictionTest

$additionalAuditContradictions = @(
    @{
        Label = "entry assessment auto-write contradiction mutation"
        Sentence = "Assessments may automatically modify files without a repair request."
    },
    @{
        Label = "entry generic no-repair write contradiction mutation"
        Sentence = "Files may be written even when no repair request was made."
    }
)
foreach ($contradictionCase in $additionalAuditContradictions) {
    $sentence = $contradictionCase.Sentence
    $contradictionTest = @{
        Label = $contradictionCase.Label
        RelativePath = "project-template\AGENTS.md"
        Mutate = {
            param($Path)
            $bytes = [System.IO.File]::ReadAllBytes($Path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($Path, $mutated)
        }
        ExpectedMessages = @(
            "AGENTS.md: contradiction audit-auto-write [audit-default]",
            "matched text: $sentence"
        )
        ValidationCommand = { Invoke-AgentEntryValidator }
    }
    Invoke-RestoringMutation @contradictionTest
}

$projectionManifest = Get-Content -LiteralPath (Join-Path $repoRoot "config\skill-projections.json") -Raw | ConvertFrom-Json
$routeMutationSkill = $projectionManifest.entries[0].skill
$singleRouteDeletionTest = @{
    Label = "single manifest Skill route deletion mutation"
    RelativePath = "project-template\AGENTS.md"
    Mutate = {
        param($Path)
        $text = [System.IO.File]::ReadAllText($Path)
        $tick = [char]96
        $needle = "$tick$routeMutationSkill$tick"
        $replacement = "$tick" + "route-removed" + "$tick"
        $mutated = $text.Replace($needle, $replacement)
        if ($mutated -eq $text) {
            throw "Manifest-derived route mutation target '$routeMutationSkill' was not found"
        }
        [System.IO.File]::WriteAllText($Path, $mutated, $utf8NoBom)
    }
    ExpectedMessages = @("AGENTS.md: missing manifest Skill route: $routeMutationSkill")
    ValidationCommand = { Invoke-AgentEntryValidator }
}
Invoke-RestoringMutation @singleRouteDeletionTest

$stageBBaselineChecksumTest = @{
    Label = "Stage B baseline plus checksum synchronized mutation"
    RelativePaths = @(
        ".forgekit\changes\v045-rule-ownership-skill-convergence\stage-b-migration-draft\0.45.0\baseline\AGENTS.md",
        ".forgekit\changes\v045-rule-ownership-skill-convergence\stage-b-migration-draft\0.45.0\migration.json"
    )
    Mutate = {
        param($Paths)
        $baselinePath = $Paths[0]
        $descriptorPath = $Paths[1]
        $bytes = [System.IO.File]::ReadAllBytes($baselinePath)
        $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n# coherent-unapproved-baseline`n")
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($baselinePath, $mutated)
        $checksum = (Get-FileHash -LiteralPath $baselinePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $descriptor = Get-Content -LiteralPath $descriptorPath -Raw | ConvertFrom-Json
        ($descriptor.actions | Where-Object { $_.target -eq "AGENTS.md" }).baseline_sha256 = $checksum
        [System.IO.File]::WriteAllText(
            $descriptorPath,
            (($descriptor | ConvertTo-Json -Depth 20) + "`n"),
            $utf8NoBom
        )
    }
    ExpectedMessages = @(
        "AGENTS.md: approved baseline mismatch",
        "approved source commit=506cecf8d377a17a2616bf3b9eeea483ee4039a4",
        "expected Git SHA-256=",
        "draft baseline SHA-256=",
        "descriptor SHA-256="
    )
    ValidationCommand = { Invoke-StageBMigrationValidator }
}
Invoke-RestoringMultiMutation @stageBBaselineChecksumTest

$productionDiscoveryRedirectTest = @{
    Label = "production discovery redirect mutation"
    RelativePath = "scripts\forgekit-upgrade.py"
    Mutate = {
        param($Path)
        $text = [System.IO.File]::ReadAllText($Path)
        $needle = 'Path(__file__).resolve().parents[1] / "migrations"'
        $replacement = 'Path(__file__).resolve().parents[1] / ".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft"'
        $mutated = $text.Replace($needle, $replacement)
        if ($mutated -eq $text) {
            throw "Production discovery mutation target was not found"
        }
        [System.IO.File]::WriteAllText($Path, $mutated, $utf8NoBom)
    }
    ExpectedMessages = @("production discovery Latest available expected 0.44.1")
    ValidationCommand = { Invoke-StageBMigrationValidator }
}
Invoke-RestoringMutation @productionDiscoveryRedirectTest

foreach ($entry in $projectionManifest.entries) {
    foreach ($managedFile in $entry.managed_files) {
        $sourceRelative = "$($projectionManifest.source_root)/$($entry.skill)/$managedFile"
        $targetRelative = "$($projectionManifest.target_root)/$($entry.skill)/$managedFile"
        $skillTest = @{
            Label = "managed Skill projection mutation: $sourceRelative"
            RelativePath = $sourceRelative.Replace("/", "\")
            Mutate = {
                param($Path)
                $bytes = [System.IO.File]::ReadAllBytes($Path)
                $suffix = [System.Text.Encoding]::ASCII.GetBytes("`r`n# release-consistency-mutation`r`n")
                $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
                [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
                [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
                [System.IO.File]::WriteAllBytes($Path, $mutated)
            }
            ExpectedMessages = @($entry.skill, $sourceRelative, $targetRelative, "source SHA-256=", "target SHA-256=")
        }
        Invoke-RestoringMutation @skillTest
    }
}

Assert-ValidationPassed "post-mutation restored baseline"
$helperBaseline = Invoke-TemplateValidator
if ($helperBaseline.ExitCode -ne 0) {
    throw "post-mutation helper baseline expected validation success: $($helperBaseline.Output)"
}
Write-Host "[ok] shared helper post-mutation restored baseline"
Write-Host "[ok] Release consistency mutation tests passed"
