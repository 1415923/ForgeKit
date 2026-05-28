param(
    [ValidateSet("docs-warn", "docs-strict")]
    [string]$Profile = "docs-warn",

    [ValidateSet("git", "claude", "codex")]
    [string]$Target = "git",

    [switch]$DryRun,
    [switch]$Status,
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$hookName = "ForgeKit document sync"
$hookStart = "# BEGIN FORGEKIT DOC SYNC HOOK"
$hookEnd = "# END FORGEKIT DOC SYNC HOOK"

function Get-HookBody {
    $strictArgSh = ""
    $strictArgPs = ""
    if ($Profile -eq "docs-strict") {
        $strictArgSh = " --strict"
        $strictArgPs = " -Strict"
    }
    return @"
$hookStart
if [ -f "./scripts/check-doc-sync.sh" ]; then
  sh ./scripts/check-doc-sync.sh$strictArgSh
  status=`$?
  if [ "`$status" -ne 0 ]; then
    exit "`$status"
  fi
elif [ -f "./scripts/check-doc-sync.ps1" ]; then
  powershell -ExecutionPolicy Bypass -File "./scripts/check-doc-sync.ps1"$strictArgPs
  status=`$?
  if [ "`$status" -ne 0 ]; then
    exit "`$status"
  fi
fi
$hookEnd
"@
}

function Assert-GitRepo {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git"))) {
        throw "Git hooks require a Git repository. Run git init first, or use the manual command from .codex/hooks.md."
    }
}

function Get-GitHookPath {
    return Join-Path $repoRoot ".git\hooks\pre-commit"
}

function Test-Installed {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }
    return Select-String -LiteralPath $Path -Pattern $hookStart -SimpleMatch -Quiet
}

function Remove-ManagedBlock {
    param([string]$Text)
    $pattern = "(?ms)^$([regex]::Escape($hookStart)).*?$([regex]::Escape($hookEnd))\r?\n?"
    return [regex]::Replace($Text, $pattern, "")
}

function Install-GitHook {
    $hookPath = Get-GitHookPath

    if ($Status) {
        if (-not (Test-Path -LiteralPath (Join-Path $repoRoot ".git"))) {
            Write-Host "[info] current project is not a Git repository; Git hook is not installed"
            return
        }
        if (Test-Installed $hookPath) {
            Write-Host "[ok] $hookName is installed in .git/hooks/pre-commit"
        } else {
            Write-Host "[info] $hookName is not installed in .git/hooks/pre-commit"
        }
        return
    }

    Assert-GitRepo

    if ($Uninstall) {
        if (-not (Test-Path -LiteralPath $hookPath)) {
            Write-Host "[ok] no git pre-commit hook to uninstall"
            return
        }
        $content = Get-Content -LiteralPath $hookPath -Raw
        $updated = Remove-ManagedBlock $content
        if ($DryRun) {
            Write-Host "[dry-run] would remove $hookName from .git/hooks/pre-commit"
            return
        }
        Set-Content -LiteralPath $hookPath -Value $updated -Encoding ASCII
        Write-Host "[ok] removed $hookName from .git/hooks/pre-commit"
        return
    }

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $hookPath) | Out-Null
    $existing = ""
    if (Test-Path -LiteralPath $hookPath) {
        $existing = Get-Content -LiteralPath $hookPath -Raw
    }
    $clean = Remove-ManagedBlock $existing
    $body = Get-HookBody
    $prefix = $clean.TrimEnd()
    if ([string]::IsNullOrWhiteSpace($prefix)) {
        $prefix = "#!/usr/bin/env sh"
    }
    $newContent = $prefix + "`n" + $body + "`n"

    if ($DryRun) {
        Write-Host "[dry-run] would install $hookName into .git/hooks/pre-commit"
        Write-Host "[dry-run] profile: $Profile"
        return
    }

    Set-Content -LiteralPath $hookPath -Value $newContent -Encoding ASCII
    Write-Host "[ok] installed $hookName into .git/hooks/pre-commit"
    Write-Host "[ok] profile: $Profile"
}

switch ($Target) {
    "git" {
        Install-GitHook
    }
    "claude" {
        Write-Host "[info] Claude Code lifecycle hook installer is not enabled yet."
        Write-Host "[info] Use Git hook target now: powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Target git -Profile docs-warn"
        Write-Host "[info] See .codex/hooks.md for Claude Code project-hook guidance."
    }
    "codex" {
        Write-Host "[info] Codex lifecycle hook installer is not enabled yet."
        Write-Host "[info] Use Git hook target now: powershell -ExecutionPolicy Bypass -File .\scripts\install-hooks.ps1 -Target git -Profile docs-warn"
        Write-Host "[info] Codex hook loading differs by version; keep this explicit until plugin-local hooks are stable."
    }
}
