param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$script = Join-Path $scriptDir "upgrade-forgekit.py"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "Python is required for ForgeKit guided upgrade."
}

& $python.Source $script --repo-root $repoRoot --project-path $ProjectPath
if ($LASTEXITCODE -ne 0) {
    throw "ForgeKit guided upgrade failed."
}
