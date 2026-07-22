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

function Invoke-StageCSkillValidator {
    $stageCValidator = Join-Path $scriptRoot "validate-stage-c-skills.py"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python -B $stageCValidator --repo-root $repoRoot 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Invoke-StageDSkillValidator {
    $stageDValidator = Join-Path $scriptRoot "validate-stage-d-skills.py"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python -B $stageDValidator --repo-root $repoRoot 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Output = ($output -join [Environment]::NewLine)
    }
}

function Invoke-FreshCloneValidator {
    $freshCloneValidator = Join-Path $scriptRoot "test-fresh-clone-crlf.py"
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python -B $freshCloneValidator --repo-root $repoRoot 2>&1
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

function Invoke-RestoringMultiPassGuard {
    param(
        [string]$Label,
        [string[]]$RelativePaths,
        [scriptblock]$Mutate,
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
        if ($result.ExitCode -ne 0) {
            throw "$Label expected validation success, actual exit code $($result.ExitCode): $($result.Output)"
        }
        Write-Host "[ok] $Label passed as expected"
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

$stageCDirectoryThresholdTest = @{
    Label = "Stage C directory threshold semantic mutation"
    RelativePaths = @(
        "skills\large-change-planning\agents\openai.yaml",
        "project-template\.agents\skills\large-change-planning\agents\openai.yaml"
    )
    Mutate = {
        param($Paths)
        foreach ($path in $Paths) {
            $text = [System.IO.File]::ReadAllText($path)
            $needle = "Plan this change only when impact warrants staged planning."
            $sentence = "A 42-directory change requires independent planning."
            $mutated = $text.Replace($needle, "$needle $sentence")
            if ($mutated -eq $text) {
                throw "Stage C directory threshold mutation marker was not found"
            }
            [System.IO.File]::WriteAllText($path, $mutated, $utf8NoBom)
        }
    }
    ExpectedMessages = @(
        "large-change-planning [package-prompt/fixed-quantity-risk-threshold]",
        "A 42-directory change requires independent planning.",
        "quantity='42'",
        "unit='directory'"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCDirectoryThresholdTest

$stageCSetupAgainTest = @{
    Label = "Stage C setup-again semantic mutation"
    RelativePaths = @(
        "skills\project-init\SKILL.md",
        "project-template\.agents\skills\project-init\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $sentence = "An initialized project is required to go through project setup again before review."
        foreach ($path in $Paths) {
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $mutated)
        }
    }
    ExpectedMessages = @(
        "project-init [existing-project-reinitialize]",
        "An initialized project is required to go through project setup again before review.",
        "features=existing_subject,init_action,repeat_action,positive_requirement"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCSetupAgainTest

$stageCBootstrappedSymmetryPaths = @(
    (Join-Path $repoRoot "skills\project-init\SKILL.md"),
    (Join-Path $repoRoot "project-template\.agents\skills\project-init\SKILL.md"),
    (Join-Path $repoRoot "project-template\.forgekit\template-manifest.json")
)
$stageCBootstrappedSymmetryOriginals = @(
    [System.IO.File]::ReadAllBytes($stageCBootstrappedSymmetryPaths[0]),
    [System.IO.File]::ReadAllBytes($stageCBootstrappedSymmetryPaths[1]),
    [System.IO.File]::ReadAllBytes($stageCBootstrappedSymmetryPaths[2])
)
$writeStageCBootstrappedSentence = {
    param([string]$Sentence)
    foreach ($index in 0, 1) {
        $bytes = [System.IO.File]::ReadAllBytes($stageCBootstrappedSymmetryPaths[$index])
        $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$Sentence`n")
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($stageCBootstrappedSymmetryPaths[$index], $mutated)
    }
    $manifest = Get-Content -LiteralPath $stageCBootstrappedSymmetryPaths[2] -Raw | ConvertFrom-Json
    $entry = $manifest.files | Where-Object { $_.source_path -eq ".agents/skills/project-init/SKILL.md" }
    if (@($entry).Count -ne 1) {
        throw "Stage C bootstrapped symmetry guard expected one project-init manifest entry"
    }
    $entry.checksum = "sha256:$((Get-FileHash -LiteralPath $stageCBootstrappedSymmetryPaths[1] -Algorithm SHA256).Hash.ToLowerInvariant())"
    $rendered = (($manifest | ConvertTo-Json -Depth 20) + "`n").Replace("`r`n", "`n")
    [System.IO.File]::WriteAllText($stageCBootstrappedSymmetryPaths[2], $rendered, $utf8NoBom)
}
try {
    $safeSentence = "An already initialized project must not be bootstrapped again."
    & $writeStageCBootstrappedSentence $safeSentence
    $safeResult = Invoke-StageCSkillValidator
    if ($safeResult.ExitCode -ne 0) {
        throw "Stage C negated bootstrapped expected-pass guard returned $($safeResult.ExitCode): $($safeResult.Output)"
    }
    Write-Host "[ok] Stage C negated bootstrapped expected-pass guard passed"

    for ($index = 0; $index -lt $stageCBootstrappedSymmetryPaths.Count; $index++) {
        [System.IO.File]::WriteAllBytes($stageCBootstrappedSymmetryPaths[$index], $stageCBootstrappedSymmetryOriginals[$index])
    }
    $positiveSentence = "An already initialized project must be bootstrapped again."
    & $writeStageCBootstrappedSentence $positiveSentence
    $positiveResult = Invoke-StageCSkillValidator
    if ($positiveResult.ExitCode -eq 0) {
        throw "Stage C positive bootstrapped symmetry guard expected failure, actual exit code 0"
    }
    foreach ($message in @(
        "project-init [existing-project-reinitialize]",
        $positiveSentence,
        "features=existing_subject,init_action,repeat_action,positive_requirement"
    )) {
        if (-not $positiveResult.Output.Contains($message)) {
            throw "Stage C positive bootstrapped symmetry output missing '$message': $($positiveResult.Output)"
        }
    }
    Write-Host "[ok] Stage C positive bootstrapped symmetry guard failed as expected"
} finally {
    for ($index = 0; $index -lt $stageCBootstrappedSymmetryPaths.Count; $index++) {
        [System.IO.File]::WriteAllBytes($stageCBootstrappedSymmetryPaths[$index], $stageCBootstrappedSymmetryOriginals[$index])
    }
}
for ($index = 0; $index -lt $stageCBootstrappedSymmetryPaths.Count; $index++) {
    $restored = [System.IO.File]::ReadAllBytes($stageCBootstrappedSymmetryPaths[$index])
    if ([System.Convert]::ToBase64String($restored) -ne [System.Convert]::ToBase64String($stageCBootstrappedSymmetryOriginals[$index])) {
        throw "Stage C bootstrapped symmetry guard did not restore $($stageCBootstrappedSymmetryPaths[$index]) byte-for-byte"
    }
}
if ((Invoke-StageCSkillValidator).ExitCode -ne 0) {
    throw "Stage C bootstrapped symmetry guard did not restore the validator baseline"
}
Write-Host "[ok] Stage C bootstrapped symmetry guard restored baseline"

$stageCActionFirstBootstrapTest = @{
    Label = "Stage C imperative bootstrap-again semantic mutation"
    RelativePaths = @(
        "skills\project-init\SKILL.md",
        "project-template\.agents\skills\project-init\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $sentence = "Bootstrap an already initialized repository again."
        foreach ($path in $Paths) {
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $mutated)
        }
    }
    ExpectedMessages = @(
        "project-init [existing-project-reinitialize]",
        "Bootstrap an already initialized repository again.",
        "features=existing_subject,init_action,repeat_action,positive_requirement"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCActionFirstBootstrapTest

$stageCPhrasalSetUpTest = @{
    Label = "Stage C imperative phrasal-set-up semantic mutation"
    RelativePaths = @(
        "skills\project-init\SKILL.md",
        "project-template\.agents\skills\project-init\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $sentence = "Set up each existing workspace from scratch."
        foreach ($path in $Paths) {
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $mutated)
        }
    }
    ExpectedMessages = @(
        "project-init [existing-project-reinitialize]",
        "Set up each existing workspace from scratch.",
        "features=existing_subject,init_action,repeat_action,positive_requirement"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCPhrasalSetUpTest

$stageCOneByOnePipelineTest = @{
    Label = "Stage C one-by-one pipeline semantic mutation"
    RelativePaths = @(
        "skills\project-init\SKILL.md",
        "project-template\.agents\skills\project-init\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $sentence = "All Stage C Skills form a mandatory one-by-one workflow for each project."
        foreach ($path in $Paths) {
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $mutated)
        }
    }
    ExpectedMessages = @(
        "project-init [mandatory-five-skill-pipeline]",
        "All Stage C Skills form a mandatory one-by-one workflow for each project.",
        "features=full_skill_set,universal_scope,mandatory,sequence"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCOneByOnePipelineTest

$stageCFullSetMandatoryTest = @{
    Label = "Stage C full-set mandatory without sequence semantic mutation"
    RelativePaths = @(
        "skills\project-init\SKILL.md",
        "project-template\.agents\skills\project-init\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $sentence = "Every Stage C Skill is compulsory for every project request."
        foreach ($path in $Paths) {
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes("`n$sentence`n")
            $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $mutated)
        }
    }
    ExpectedMessages = @(
        "project-init [mandatory-five-skill-pipeline]",
        "Every Stage C Skill is compulsory for every project request.",
        "features=full_skill_set,universal_scope,mandatory"
    )
    ValidationCommand = { Invoke-StageCSkillValidator }
}
Invoke-RestoringMultiMutation @stageCFullSetMandatoryTest

$stageDMutations = @(
    @{ Label = "Stage D code-review automatic maker mutation"; Skill = "code-review"; Sentence = "Automatically fix every finding after review."; Expected = "code-review [review-auto-maker]" },
    @{ Label = "Stage D security always-on mutation"; Skill = "security-review"; Sentence = "Security review is mandatory for every change."; Expected = "security-review [security-review-always-on]" },
    @{ Label = "Stage D release ordinary-commit mutation"; Skill = "release-check"; Sentence = "Every ordinary commit must use a release check."; Expected = "release-check [release-check-always-on]" },
    @{ Label = "Stage D suitability auto-init mutation"; Skill = "project-suitability"; Sentence = "Automatically initialize ForgeKit after the assessment."; Expected = "project-suitability [suitability-auto-initialize]" },
    @{ Label = "Stage D mandatory four-Skill pipeline mutation"; Skill = "code-review"; Sentence = "All four Stage D Skills are mandatory for every task."; Expected = "code-review [mandatory-stage-d-pipeline]" },
    @{ Label = "Stage D fixed-count checker mutation"; Skill = "code-review"; Sentence = "A 7-file change requires an independent checker."; Expected = "code-review [fixed-quantity-risk-threshold]" },
    @{ Label = "Stage D finding auto-authorizes repair mutation"; Skill = "code-review"; Sentence = "Finding a defect directly authorizes repair."; Expected = "code-review [finding-auto-authorizes-repair]" },
    @{ Label = "Stage D ordinary backend mandatory security mutation"; Skill = "security-review"; Sentence = "Every ordinary backend change must run security review."; Expected = "security-review [ordinary-change-requires-security-review]" },
    @{ Label = "Stage D ordinary commit treated as release mutation"; Skill = "release-check"; Sentence = "Treat every ordinary commit as a release and run release-check."; Expected = "release-check [ordinary-commit-is-release]" },
    @{ Label = "Stage D suitability creates ForgeKit mutation"; Skill = "project-suitability"; Sentence = "After every suitability assessment, automatically create .forgekit."; Expected = "project-suitability [suitability-auto-initialization]" },
    @{ Label = "Stage D internal authorization external action mutation"; Skill = "code-review"; Sentence = "Internal stage authorization automatically permits push and release."; Expected = "code-review [internal-authorization-external-action]" }
)
foreach ($mutation in $stageDMutations) {
    $stageDTest = @{
        Label = $mutation.Label
        RelativePaths = @(
            "skills\$($mutation.Skill)\SKILL.md",
            "project-template\.agents\skills\$($mutation.Skill)\SKILL.md"
        )
        Mutate = {
            param($Paths)
            foreach ($path in $Paths) {
                $bytes = [System.IO.File]::ReadAllBytes($path)
                $suffix = [System.Text.Encoding]::ASCII.GetBytes(([char]10) + $mutation.Sentence + ([char]10))
                $updated = New-Object byte[] ($bytes.Length + $suffix.Length)
                [System.Array]::Copy($bytes, 0, $updated, 0, $bytes.Length)
                [System.Array]::Copy($suffix, 0, $updated, $bytes.Length, $suffix.Length)
                [System.IO.File]::WriteAllBytes($path, $updated)
            }
        }
        ExpectedMessages = @($mutation.Expected)
        ValidationCommand = { Invoke-StageDSkillValidator }
    }
    Invoke-RestoringMultiMutation @stageDTest
}

$stageDEvidenceMutations = @(
    @{ Label = "Stage D security missing validation evidence mutation"; Skill = "security-review"; Old = "changed-path evidence and validation evidence"; New = "changed-path evidence"; Expected = "security-review [missing-validation-evidence]" },
    @{ Label = "Stage D release missing changed-path evidence mutation"; Skill = "release-check"; Old = "changed-path evidence and validation evidence"; New = "validation evidence"; Expected = "release-check [missing-changed-path-evidence]" },
    @{ Label = "Stage D generic evidence mutation"; Skill = "code-review"; Old = "changed-path evidence and validation evidence"; New = "evidence"; Expected = "code-review [missing-changed-path-evidence]" }
)
foreach ($mutation in $stageDEvidenceMutations) {
    $stageDEvidenceTest = @{
        Label = $mutation.Label
        RelativePaths = @(
            "skills\$($mutation.Skill)\SKILL.md",
            "project-template\.agents\skills\$($mutation.Skill)\SKILL.md"
        )
        Mutate = {
            param($Paths)
            foreach ($path in $Paths) {
                $text = [System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($path))
                $updated = $text.Replace($mutation.Old, $mutation.New)
                if ($updated -eq $text) {
                    throw "$($mutation.Label) target phrase was not found in $path"
                }
                [System.IO.File]::WriteAllBytes($path, [System.Text.Encoding]::ASCII.GetBytes($updated))
            }
        }
        ExpectedMessages = @($mutation.Expected, "skills/$($mutation.Skill)/SKILL.md")
        ValidationCommand = { Invoke-StageDSkillValidator }
    }
    Invoke-RestoringMultiMutation @stageDEvidenceTest
}

$stageDSafeGuard = @{
    Label = "Stage D finite-policy safe-negation guard"
    RelativePaths = @(
        "skills\code-review\SKILL.md",
        "project-template\.agents\skills\code-review\SKILL.md",
        "skills\security-review\SKILL.md",
        "project-template\.agents\skills\security-review\SKILL.md",
        "skills\release-check\SKILL.md",
        "project-template\.agents\skills\release-check\SKILL.md",
        "skills\project-suitability\SKILL.md",
        "project-template\.agents\skills\project-suitability\SKILL.md"
    )
    Mutate = {
        param($Paths)
        $safeBySkill = @{
            "code-review" = @(
                "A finding requires separate repair authorization; the reviewer remains read-only.",
                "Internal authorization does not authorize external actions; push and release require explicit user authorization."
            )
            "security-review" = @("An ordinary backend change alone does not require security-review.")
            "release-check" = @("An ordinary commit is not a release; release-check requires explicit release intent.")
            "project-suitability" = @("A suitable result does not initialize the project; initialization requires a separate explicit request.")
        }
        foreach ($path in $Paths) {
            $skill = Split-Path (Split-Path $path -Parent) -Leaf
            $bytes = [System.IO.File]::ReadAllBytes($path)
            $suffix = [System.Text.Encoding]::ASCII.GetBytes(([char]10) + ($safeBySkill[$skill] -join ([char]10)) + ([char]10))
            $updated = New-Object byte[] ($bytes.Length + $suffix.Length)
            [System.Array]::Copy($bytes, 0, $updated, 0, $bytes.Length)
            [System.Array]::Copy($suffix, 0, $updated, $bytes.Length, $suffix.Length)
            [System.IO.File]::WriteAllBytes($path, $updated)
        }
    }
    ValidationCommand = { Invoke-StageDSkillValidator }
}
Invoke-RestoringMultiPassGuard @stageDSafeGuard

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
$freshCloneBaseline = Invoke-FreshCloneValidator
if ($freshCloneBaseline.ExitCode -ne 0) {
    throw "fresh-clone LF/CRLF gate expected validation success: $($freshCloneBaseline.Output)"
}
Write-Host "[ok] fresh-clone LF/CRLF checkout baseline"
Write-Host "[ok] Release consistency mutation tests passed"
