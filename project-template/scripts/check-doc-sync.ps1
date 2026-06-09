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
    return Join-Path ".forgekit\docs" "$FileName.md"
}

function Get-VersionRecordName {
    return "changelog"
}

function Get-VersionRoadmapName {
    return "version-roadmap"
}

function Get-TaskBoardName {
    return "task-board"
}

function Get-TestDocName {
    return "testing"
}

function Get-RiskRegisterName {
    return "risk-register"
}

function Get-ChangeImpactName {
    return "change-impact"
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
    $paths += & git -C $repoRoot diff --name-only HEAD -- .forgekit .codex governance 2>$null
    $paths += & git -C $repoRoot diff --cached --name-only -- .forgekit .codex governance 2>$null
    return @($paths | Where-Object { $_ } | Sort-Object -Unique)
}

function Test-StalePhrases {
    $docsRoot = Join-Path $repoRoot ".forgekit\docs"
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
        if ($insideChanged -and $line -match "^\s*-\s+" -and $line -notmatch "Reason:|Because:|because:") {
            Add-Warning "Changed entry should include a reason in version update record:$($i + 1)"
        }
    }
}

function Test-ChangedDocsNeedVersionRecord {
    $changedPaths = Get-ChangedPaths
    if ($changedPaths.Count -eq 0) {
        return
    }

    $changedPaths = @($changedPaths | Where-Object {
        $_ -notlike ".forgekit/upgrade-export/*" -and
        $_ -notlike ".forgekit\upgrade-export\*" -and
        $_ -notlike ".forgekit/archive/*" -and
        $_ -notlike ".forgekit\archive\*"
    })
    if ($changedPaths.Count -eq 0) {
        return
    }

    $docChanged = @($changedPaths | Where-Object { $_ -like ".forgekit/*" -or $_ -like "governance/*" -or $_ -like ".codex/*" })
    if ($docChanged.Count -eq 0) {
        return
    }

    $versionRecordPath = ".forgekit/docs/" + (Get-VersionRecordName) + ".md"
    $versionChanged = $changedPaths -contains $versionRecordPath
    if (-not $versionChanged) {
        Add-Warning "Docs or governance changed, but the version update record is not changed. Confirm whether it needs an entry with reason."
    }

    $riskTerms = @(
        "defect",
        "risk",
        "incident",
        "security",
        "dependency",
        "deployment",
        "environment",
        "api",
        "database",
        "implementation-plan",
        "exploration-report",
        "change-impact"
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

function Test-ChangeArtifacts {
    $changesRoot = Join-Path $repoRoot ".forgekit\changes"
    if (-not (Test-Path -LiteralPath $changesRoot)) {
        return
    }

    $changeDirs = Get-ChildItem -LiteralPath $changesRoot -Directory | Where-Object { $_.Name -ne "_template" }
    foreach ($dir in $changeDirs) {
        $relativeDir = [System.IO.Path]::GetRelativePath($repoRoot, $dir.FullName)
        $proposal = Join-Path $dir.FullName "proposal.md"
        if (-not (Test-Path -LiteralPath $proposal)) {
            Add-Warning "Change is missing proposal.md: $relativeDir"
            continue
        }

        $statusLine = Get-Content -LiteralPath $proposal | Where-Object { $_ -match "^Status:\s*(\S+)" } | Select-Object -First 1
        if (-not $statusLine) {
            Add-Warning "Change proposal is missing Status: metadata: $relativeDir/proposal.md"
        } else {
            $status = ([regex]::Match($statusLine, "^Status:\s*(\S+)").Groups[1].Value).ToLowerInvariant()
            if ($status -eq "archived") {
                continue
            }
            if ($status -eq "done") {
                Add-Warning "Change is done and may be archived: $relativeDir"
                continue
            }
            if ($status -notin @("draft", "active")) {
                Add-Warning "Change proposal has unknown Status value '$status': $relativeDir/proposal.md"
            }
        }

        $riskLine = Get-Content -LiteralPath $proposal | Where-Object { $_ -match "^Risk:\s*(\S+)" } | Select-Object -First 1
        if (-not $riskLine) {
            Add-Warning "Change proposal is missing Risk: metadata: $relativeDir/proposal.md"
            continue
        }

        $risk = ([regex]::Match($riskLine, "^Risk:\s*(\S+)").Groups[1].Value).ToLowerInvariant()
        $required = @()
        if ($risk -eq "medium") {
            $required = @("proposal.md", "tasks.md", "verification.md", "review.md")
        } elseif ($risk -eq "high") {
            $required = @("proposal.md", "design.md", "tasks.md", "verification.md", "review.md", "ship.md")
        } elseif ($risk -ne "low") {
            Add-Warning "Change proposal has unknown Risk value '$risk': $relativeDir/proposal.md"
            continue
        }

        foreach ($name in $required) {
            if (-not (Test-Path -LiteralPath (Join-Path $dir.FullName $name))) {
                Add-Warning "Change with Risk: $risk is missing required artifact: $relativeDir/$name"
            }
        }
    }
}

function Test-UpgradeExportIgnored {
    $exportRoot = Join-Path $repoRoot ".forgekit\upgrade-export"
    if (Test-Path -LiteralPath $exportRoot) {
        return
    }
}

function Test-CurrentDocsLength {
    $docsRoot = Join-Path $repoRoot ".forgekit\docs"
    if (-not (Test-Path -LiteralPath $docsRoot)) {
        return
    }

    $files = Get-ChildItem -LiteralPath $docsRoot -Recurse -File -Include *.md
    foreach ($file in $files) {
        $lineCount = (Get-Content -LiteralPath $file.FullName).Count
        if ($lineCount -gt 600) {
            $relative = [System.IO.Path]::GetRelativePath($repoRoot, $file.FullName)
            Add-Warning "Current state doc is long ($lineCount lines). Consider moving historical process details to a change or archive: $relative"
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
Test-UpgradeExportIgnored
Test-ChangeArtifacts
Test-CurrentDocsLength

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
