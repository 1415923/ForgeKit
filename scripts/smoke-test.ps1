param(
    [switch]$KeepTemp
)

$ErrorActionPreference = "Stop"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$argsList = @("--repo-root", $repoRoot)
if ($KeepTemp) {
    $argsList += "--keep-temp"
}
python (Join-Path $scriptRoot "smoke-test.py") @argsList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
