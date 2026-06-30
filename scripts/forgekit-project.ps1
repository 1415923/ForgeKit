$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "forgekit-project.py"
& python $scriptPath @args
exit $LASTEXITCODE
