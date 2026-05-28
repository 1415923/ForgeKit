param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$warnings = New-Object System.Collections.Generic.List[string]
$errors = New-Object System.Collections.Generic.List[string]

function Add-Warning {
    param([string]$Message)
    $warnings.Add($Message) | Out-Null
}

function New-Text {
    param([int[]]$CodePoints)
    $builder = New-Object System.Text.StringBuilder
    foreach ($codePoint in $CodePoints) {
        [void]$builder.Append([char]$codePoint)
    }
    return $builder.ToString()
}

function Join-DocPath {
    param([string]$FileName)
    return Join-Path "docs" "$FileName.md"
}

function Get-VersionRecordName {
    return New-Text @(0x7248,0x672C,0x66F4,0x65B0,0x8BB0,0x5F55)
}

function Get-VersionRoadmapName {
    return New-Text @(0x7248,0x672C,0x8DEF,0x7EBF,0x56FE)
}

function Get-TaskBoardName {
    return New-Text @(0x9879,0x76EE,0x4EFB,0x52A1,0x770B,0x677F)
}

function Get-TestDocName {
    return New-Text @(0x6D4B,0x8BD5,0x6587,0x6863)
}

function Get-RiskRegisterName {
    return New-Text @(0x98CE,0x9669,0x767B,0x8BB0,0x518C)
}

function Get-ChangeImpactName {
    return New-Text @(0x53D8,0x66F4,0x5F71,0x54CD,0x8BC4,0x4F30)
}

function Test-PathRequired {
    param([string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Warning "Missing document commonly needed for sync checks: $RelativePath"
    }
}

function Get-ChangedPaths {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        return @()
    }
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git"))) {
        return @()
    }

    $inside = & git -C $repoRoot rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0 -or $inside -ne "true") {
        return @()
    }

    $paths = @()
    $paths += & git -C $repoRoot diff --name-only HEAD -- docs .codex governance 2>$null
    $paths += & git -C $repoRoot diff --cached --name-only -- docs .codex governance 2>$null
    return @($paths | Where-Object { $_ } | Sort-Object -Unique)
}

function Test-StalePhrases {
    $docsRoot = Join-Path $repoRoot "docs"
    if (-not (Test-Path -LiteralPath $docsRoot)) {
        return
    }

    $patterns = @(
        "still under workaround",
        "temporary workaround",
        "known stale",
        "stale description",
        "workaround still active",
        (New-Text @(0x4ECD,0x5728,0x89C4,0x907F)),
        (New-Text @(0x4ECD,0x9700,0x89C4,0x907F)),
        (New-Text @(0x4E34,0x65F6,0x89C4,0x907F)),
        (New-Text @(0x8FC7,0x671F,0x63CF,0x8FF0)),
        (New-Text @(0x63CF,0x8FF0,0x8FC7,0x671F))
    )

    $files = Get-ChildItem -LiteralPath $docsRoot -Recurse -File -Include *.md
    foreach ($file in $files) {
        foreach ($pattern in $patterns) {
            $matches = Select-String -LiteralPath $file.FullName -Pattern $pattern -SimpleMatch
            foreach ($match in $matches) {
                $relative = [System.IO.Path]::GetRelativePath($repoRoot, $file.FullName)
                Add-Warning "Possible stale doc phrase in ${relative}:$($match.LineNumber): $pattern"
            }
        }
    }
}

function Test-VersionChangedReasons {
    $versionDoc = Join-Path $repoRoot (Join-DocPath (Get-VersionRecordName))
    if (-not (Test-Path -LiteralPath $versionDoc)) {
        return
    }

    $reasonText = New-Text @(0x539F,0x56E0)
    $lines = Get-Content -LiteralPath $versionDoc
    $insideChanged = $false
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match "^###\s+Changed\s*$") {
            $insideChanged = $true
            continue
        }
        if ($line -match "^###\s+" -and $insideChanged) {
            $insideChanged = $false
        }
        if ($insideChanged -and $line -match "^\s*-\s+" -and $line -notmatch "$reasonText|Reason|Because|because") {
            Add-Warning "Changed entry should include a reason in version update record:$($i + 1)"
        }
    }
}

function Test-ChangedDocsNeedVersionRecord {
    $changedPaths = Get-ChangedPaths
    if ($changedPaths.Count -eq 0) {
        return
    }

    $docChanged = @($changedPaths | Where-Object { $_ -like "docs/*" -or $_ -like "governance/*" -or $_ -like ".codex/*" })
    if ($docChanged.Count -eq 0) {
        return
    }

    $versionRecordPath = "docs/" + (Get-VersionRecordName) + ".md"
    $versionChanged = $changedPaths -contains $versionRecordPath
    if (-not $versionChanged) {
        Add-Warning "Docs or governance changed, but the version update record is not changed. Confirm whether it needs an entry with reason."
    }

    $riskTerms = @(
        (New-Text @(0x7F3A,0x9677)),
        (New-Text @(0x98CE,0x9669)),
        (New-Text @(0x4E8B,0x6545)),
        (New-Text @(0x5B89,0x5168)),
        (New-Text @(0x4F9D,0x8D56)),
        (New-Text @(0x90E8,0x7F72)),
        (New-Text @(0x73AF,0x5883)),
        (New-Text @(0x63A5,0x53E3)),
        (New-Text @(0x6570,0x636E,0x5E93)),
        (New-Text @(0x5B9E,0x65BD,0x8BA1,0x5212)),
        (New-Text @(0x63A2,0x7D22,0x62A5,0x544A))
    )

    foreach ($path in $changedPaths) {
        foreach ($term in $riskTerms) {
            if ($path -match [regex]::Escape($term)) {
                Add-Warning "Risk-sensitive docs changed. Check related docs such as risk register, change impact, testing, release pipeline, and version update record."
                return
            }
        }
    }
}

Test-PathRequired (Join-DocPath (Get-VersionRecordName))
Test-PathRequired (Join-DocPath (Get-VersionRoadmapName))
Test-PathRequired (Join-DocPath (Get-TaskBoardName))
Test-PathRequired (Join-DocPath (Get-TestDocName))
Test-PathRequired (Join-DocPath (Get-RiskRegisterName))
Test-PathRequired (Join-DocPath (Get-ChangeImpactName))

Test-StalePhrases
Test-VersionChangedReasons
Test-ChangedDocsNeedVersionRecord

if ($warnings.Count -eq 0 -and $errors.Count -eq 0) {
    Write-Host "[ok] Document sync check passed"
    exit 0
}

Write-Host "[warn] Document sync check found items to review"
foreach ($warning in $warnings) {
    Write-Host " - $warning"
}
foreach ($errorItem in $errors) {
    Write-Host " - $errorItem"
}

Write-Host ""
Write-Host "Recommended prompt:"
Write-Host "Check whether other docs need synchronized updates. If the version update record has Changed entries, add the reason for each change."

if ($Strict -and ($warnings.Count -gt 0 -or $errors.Count -gt 0)) {
    exit 1
}

exit 0
