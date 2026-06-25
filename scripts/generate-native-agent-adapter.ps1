param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("claude-code", "codex", "all")]
    [string]$Target,

    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [switch]$DryRun,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $scriptRoot "generate-native-agent-adapter.py"

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
    "--project-root", $ProjectRoot
)
if ($DryRun) {
    $argsList += "--dry-run"
}
if ($Force) {
    $argsList += "--force"
}

& $python.Source @argsList
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
