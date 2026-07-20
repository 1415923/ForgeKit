param()

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$validator = Join-Path $scriptRoot "validate-plugin-assets.ps1"
$expectedVersion = (Get-Content -LiteralPath (Join-Path $repoRoot "VERSION") -Raw).Trim()
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Invoke-ReleaseValidator {
    $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $validator 2>&1
    return [PSCustomObject]@{
        ExitCode = $LASTEXITCODE
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
        [string[]]$ExpectedMessages
    )

    $path = Join-Path $repoRoot $RelativePath
    $originalBytes = [System.IO.File]::ReadAllBytes($path)
    try {
        & $Mutate $path
        $result = Invoke-ReleaseValidator
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

$skillTest = @{
    Label = "code-review shared skill mutation"
    RelativePath = "skills\code-review\SKILL.md"
    Mutate = {
        param($Path)
        $bytes = [System.IO.File]::ReadAllBytes($Path)
        $suffix = [System.Text.Encoding]::ASCII.GetBytes([Environment]::NewLine + "# release-consistency-mutation" + [Environment]::NewLine)
        $mutated = New-Object byte[] ($bytes.Length + $suffix.Length)
        [System.Array]::Copy($bytes, 0, $mutated, 0, $bytes.Length)
        [System.Array]::Copy($suffix, 0, $mutated, $bytes.Length, $suffix.Length)
        [System.IO.File]::WriteAllBytes($Path, $mutated)
    }
    ExpectedMessages = @("skills\code-review\SKILL.md", "project-template\.agents\skills\code-review\SKILL.md", "expected SHA256", "actual SHA256")
}
Invoke-RestoringMutation @skillTest

Assert-ValidationPassed "post-mutation restored baseline"
Write-Host "[ok] Release consistency mutation tests passed"
