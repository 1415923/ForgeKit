param(
    [switch]$SkipSkillValidation
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$projectTemplate = Join-Path $repoRoot "project-template"
$errors = New-Object System.Collections.Generic.List[string]

function Add-Error {
    param([string]$Message)
    $errors.Add($Message) | Out-Null
}

function Test-RequiredPath {
    param([string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        Add-Error "Missing required path: $RelativePath"
    }
}

function Test-NoPattern {
    param(
        [string]$RelativePath,
        [string]$Pattern,
        [string]$Label
    )
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return
    }
    $matches = Select-String -Path $path -Pattern $Pattern -SimpleMatch
    foreach ($match in $matches) {
        Add-Error "$Label in ${RelativePath}:$($match.LineNumber)"
    }
}

function Test-RequiredPattern {
    param(
        [string]$RelativePath,
        [string]$Pattern,
        [string]$Label
    )
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path)) {
        return
    }
    $found = Select-String -Path $path -Pattern $Pattern -SimpleMatch -Quiet
    if (-not $found) {
        Add-Error "$Label missing in $RelativePath"
    }
}

function Test-SkillAscii {
    $skillFiles = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Recurse -Filter "SKILL.md"
    foreach ($file in $skillFiles) {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        foreach ($byte in $bytes) {
            if ($byte -gt 127) {
                Add-Error "Non-ASCII byte found in skill: $($file.FullName)"
                break
            }
        }
    }
}

function Test-SkillFrontmatter {
    $skillFiles = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Recurse -Filter "SKILL.md"
    foreach ($file in $skillFiles) {
        $lines = Get-Content -LiteralPath $file.FullName
        if ($lines.Count -lt 5 -or $lines[0] -ne "---") {
            Add-Error "Missing frontmatter start in skill: $($file.FullName)"
            continue
        }
        if (-not ($lines | Select-String -Pattern "^name: " -Quiet)) {
            Add-Error "Missing name in skill: $($file.FullName)"
        }
        if (-not ($lines | Select-String -Pattern "^description: " -Quiet)) {
            Add-Error "Missing description in skill: $($file.FullName)"
        }
    }
}

function Test-GovernanceFiles {
    $required = @(
        "project-template\governance\sdlc.md",
        "project-template\governance\architecture-governance.md",
        "project-template\governance\adr-process.md",
        "project-template\governance\rfc-process.md",
        "project-template\governance\traceability.md",
        "project-template\governance\definition-of-ready.md",
        "project-template\governance\definition-of-done.md",
        "project-template\governance\risk-management.md",
        "project-template\governance\technical-debt-management.md",
        "project-template\governance\quality-metrics.md",
        "project-template\governance\change-management.md",
        "project-template\governance\incident-process.md",
        "project-template\governance\security-governance.md",
        "project-template\governance\cicd-environment-governance.md",
        "project-template\governance\code-ownership-review-governance.md",
        "project-template\governance\project-management-task-model.md",
        "project-template\governance\agent-harness.md",
        "project-template\governance\large-change-execution.md",
        "project-template\governance\team-agent-rollout.md",
        "project-template\governance\agent-suitability.md",
        "project-template\governance\v0.3-agent-harness-roadmap.md"
    )
    foreach ($item in $required) {
        Test-RequiredPath $item
    }
}

function Get-CodebaseMapPath {
    $name = ([char]0x4EE3).ToString() + ([char]0x7801).ToString() + ([char]0x5E93).ToString() + ([char]0x5730).ToString() + ([char]0x56FE).ToString()
    return "project-template\docs\$name.md"
}

function Get-CodebaseMapRef {
    $name = ([char]0x4EE3).ToString() + ([char]0x7801).ToString() + ([char]0x5E93).ToString() + ([char]0x5730).ToString() + ([char]0x56FE).ToString()
    return "docs/$name.md"
}

function Get-LocalToolchainPath {
    $name = ([char]0x672C).ToString() + ([char]0x5730).ToString() + ([char]0x5DE5).ToString() + ([char]0x5177).ToString() + ([char]0x94FE).ToString() + ([char]0x68C0).ToString() + ([char]0x67E5).ToString()
    return "project-template\docs\$name.md"
}

function Get-LocalToolchainRef {
    $name = ([char]0x672C).ToString() + ([char]0x5730).ToString() + ([char]0x5DE5).ToString() + ([char]0x5177).ToString() + ([char]0x94FE).ToString() + ([char]0x68C0).ToString() + ([char]0x67E5).ToString()
    return "docs/$name.md"
}

function Get-ExplorationReportPath {
    $name = ([char]0x63A2).ToString() + ([char]0x7D22).ToString() + ([char]0x62A5).ToString() + ([char]0x544A).ToString()
    return "project-template\docs\$name.md"
}

function Get-ImplementationPlanPath {
    $name = ([char]0x5B9E).ToString() + ([char]0x65BD).ToString() + ([char]0x8BA1).ToString() + ([char]0x5212).ToString()
    return "project-template\docs\$name.md"
}

function Get-ExplorationReportRef {
    $name = ([char]0x63A2).ToString() + ([char]0x7D22).ToString() + ([char]0x62A5).ToString() + ([char]0x544A).ToString()
    return "docs/$name.md"
}

function Get-ImplementationPlanRef {
    $name = ([char]0x5B9E).ToString() + ([char]0x65BD).ToString() + ([char]0x8BA1).ToString() + ([char]0x5212).ToString()
    return "docs/$name.md"
}

function Get-SuitabilityPath {
    $name = ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x9002).ToString() + ([char]0x7528).ToString() + ([char]0x6027).ToString() + ([char]0x8BC4).ToString() + ([char]0x4F30).ToString()
    return "project-template\docs\$name.md"
}

function Get-SuitabilityRef {
    $name = ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x9002).ToString() + ([char]0x7528).ToString() + ([char]0x6027).ToString() + ([char]0x8BC4).ToString() + ([char]0x4F30).ToString()
    return "docs/$name.md"
}

function Get-TrialRecordPath {
    $name = ([char]0x771F).ToString() + ([char]0x5B9E).ToString() + ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x8BD5).ToString() + ([char]0x7528).ToString() + ([char]0x8BB0).ToString() + ([char]0x5F55).ToString()
    return "project-template\docs\$name.md"
}

function Get-TrialRecordRef {
    $name = ([char]0x771F).ToString() + ([char]0x5B9E).ToString() + ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x8BD5).ToString() + ([char]0x7528).ToString() + ([char]0x8BB0).ToString() + ([char]0x5F55).ToString()
    return "docs/$name.md"
}

function Test-AgentsHarness {
    $agentsFiles = @(
        "AGENTS.md",
        "project-template\AGENTS.md"
    )
    foreach ($relativePath in $agentsFiles) {
        Test-RequiredPath $relativePath
        $path = Join-Path $repoRoot $relativePath
        if (-not (Test-Path -LiteralPath $path)) {
            continue
        }
        $lines = Get-Content -LiteralPath $path
        if ($lines.Count -gt 200) {
            Add-Error "AGENTS file is too long: $relativePath has $($lines.Count) lines"
        }
    }

    Test-RequiredPath (Get-CodebaseMapPath)
    Test-RequiredPath (Get-LocalToolchainPath)
    Test-RequiredPath (Get-ExplorationReportPath)
    Test-RequiredPath (Get-ImplementationPlanPath)
    Test-RequiredPath (Get-SuitabilityPath)
    Test-RequiredPath (Get-TrialRecordPath)
    Test-RequiredPath "project-template\governance\agent-harness.md"
    Test-RequiredPath "project-template\governance\large-change-execution.md"
    Test-RequiredPath "project-template\governance\team-agent-rollout.md"
    Test-RequiredPath "project-template\.codex\commands-catalog.md"
    Test-RequiredPath "project-template\.codex\hooks.md"
    Test-RequiredPattern "project-template\AGENTS.md" "Do not read every file" "Governance context guard"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-CodebaseMapRef) "Codebase map routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-LocalToolchainRef) "Local toolchain routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/agent-harness.md" "Agent harness routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/large-change-execution.md" "Large-change routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/team-agent-rollout.md" "Team rollout routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/agent-suitability.md" "Agent suitability routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-SuitabilityRef) "Suitability document routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ExplorationReportRef) "Exploration report routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ImplementationPlanRef) "Implementation plan routing"
}

function Test-HarnessEntryConsistency {
    $codebaseMapRef = Get-CodebaseMapRef
    Test-RequiredPattern "README.md" "Agent Harness" "Root README harness section"
    Test-RequiredPattern "README.md" $codebaseMapRef "Root README codebase map reference"
    Test-RequiredPattern "README.md" (Get-LocalToolchainRef) "Root README local toolchain reference"
    Test-RequiredPattern "project-template\README.md" "governance/agent-harness.md" "Template README harness reference"
    Test-RequiredPattern "project-template\README.md" "governance/large-change-execution.md" "Template README large-change reference"
    Test-RequiredPattern "project-template\README.md" "governance/team-agent-rollout.md" "Template README team rollout reference"
    Test-RequiredPattern "project-template\README.md" "governance/agent-suitability.md" "Template README suitability reference"
    Test-RequiredPattern "project-template\README.md" $codebaseMapRef "Template README codebase map reference"
    Test-RequiredPattern "project-template\README.md" (Get-LocalToolchainRef) "Template README local toolchain reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "governance/agent-harness.md" "Skills harness reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "governance/team-agent-rollout.md" "Skills team rollout reference"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "AGENTS.md" "Skill README AGENTS reference"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Start Codex from AGENTS.md" "Init script startup guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "codebase map" "Init script codebase map guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "large-change-execution.md" "Init script large-change guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "team-agent-rollout.md" "Init script team rollout guidance"
    Test-RequiredPattern "使用说明.html" "startupOutput" "HTML startup output"
    Test-RequiredPattern "使用说明.html" "governance/agent-harness.md" "HTML harness prompt reference"
    Test-RequiredPattern "使用说明.html" "governance/large-change-execution.md" "HTML large-change prompt reference"
    Test-RequiredPattern "使用说明.html" "governance/agent-suitability.md" "HTML suitability prompt reference"
    Test-RequiredPattern "使用说明.html" "不要默认读取全部" "HTML context guard"
}

function Test-AgentSuitability {
    Test-RequiredPath "project-template\governance\agent-suitability.md"
    Test-RequiredPath (Get-SuitabilityPath)
    Test-RequiredPath (Get-TrialRecordPath)
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Suitable" "Suitability outcomes"
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Conditional" "Conditional suitability outcome"
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Custom" "Custom suitability outcome"
    Test-RequiredPattern "使用说明.html" "suitabilityList" "HTML suitability checklist"
    Test-RequiredPattern "使用说明.html" "适用性已确认" "HTML suitability brief"
}

function Test-TeamToolingProtocol {
    Test-RequiredPath "project-template\governance\team-agent-rollout.md"
    Test-RequiredPath "project-template\.codex\commands-catalog.md"
    Test-RequiredPath "project-template\.codex\hooks.md"
    Test-RequiredPattern "project-template\governance\team-agent-rollout.md" "AGENTS -> skills -> commands -> hooks -> plugin -> MCP" "Team rollout order"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "GitHub" "GitHub integration catalog"
    Test-RequiredPattern "project-template\.codex\hooks.md" "Opt-in only" "Hooks opt-in guard"
    Test-RequiredPattern "project-template\.codex\config.example.toml" "team-agent-rollout.md" "MCP rollout reference"
    Test-RequiredPattern "project-template\AGENTS.md" "commands-catalog.md" "Commands catalog routing"
    Test-RequiredPattern "project-template\AGENTS.md" "hooks.md" "Hooks routing"
    Test-RequiredPattern "project-template\.codex\security.md" "config.example.toml" "Security MCP config guard"
    Test-RequiredPattern "project-template\.codex\rules.md" "team-agent-rollout.md" "Rules team rollout guard"

    $configPath = Join-Path $repoRoot "project-template\.codex\config.example.toml"
    if (Test-Path -LiteralPath $configPath) {
        $activeMcp = Select-String -Path $configPath -Pattern "^\s*\[mcp_servers\."
        foreach ($match in $activeMcp) {
            Add-Error "MCP example must stay commented in project-template\.codex\config.example.toml:$($match.LineNumber)"
        }
    }
}

function Test-LargeChangeProtocol {
    Test-RequiredPath "project-template\governance\large-change-execution.md"
    Test-RequiredPath (Get-ExplorationReportPath)
    Test-RequiredPath (Get-ImplementationPlanPath)
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "large-change protocol" "Project init large-change gate"
    Test-RequiredPattern "project-template\.agents\skills\code-review\SKILL.md" "large-change protocol" "Code review large-change gate"
    Test-RequiredPattern "project-template\.agents\skills\release-check\SKILL.md" "large-change protocol" "Release check large-change gate"
    Test-RequiredPattern "使用说明.html" "data-prompt=""large""" "HTML large-change tab"

    $largeChangeFiles = @(
        "project-template\governance\large-change-execution.md",
        (Get-ExplorationReportPath),
        (Get-ImplementationPlanPath)
    )
    foreach ($relativePath in $largeChangeFiles) {
        $path = Join-Path $repoRoot $relativePath
        if (-not (Test-Path -LiteralPath $path)) {
            continue
        }
        $lineCount = (Get-Content -LiteralPath $path).Count
        if ($lineCount -gt 100) {
            Add-Error "Large-change document is too long: $relativePath has $lineCount lines"
        }
    }
}

function Test-StackHarnessDetails {
    $requiredStacks = @(
        "java-springboot",
        "vue",
        "react",
        "python-fastapi",
        "node-express",
        "fpga-vivado-vitis"
    )
    foreach ($stack in $requiredStacks) {
        $readme = "templates\$stack\README.md"
        $commands = "templates\$stack\commands.md"
        Test-RequiredPattern $readme "Codex" "Stack Codex startup guidance"
        Test-RequiredPattern $readme "LSP" "Stack LSP or symbol guidance"
        Test-RequiredPattern $readme "Ignore guidance" "Stack ignore guidance"
        Test-RequiredPattern $commands "Local validation" "Stack local validation commands"

        $readmePath = Join-Path $repoRoot $readme
        $commandsPath = Join-Path $repoRoot $commands
        $readmeLines = (Get-Content -LiteralPath $readmePath).Count
        $commandsLines = (Get-Content -LiteralPath $commandsPath).Count
        if ($readmeLines -gt 80) {
            Add-Error "Stack README is too long: $readme has $readmeLines lines"
        }
        if ($commandsLines -gt 80) {
            Add-Error "Stack commands file is too long: $commands has $commandsLines lines"
        }
    }
}

function Test-StackTemplates {
    $requiredStacks = @(
        "java-springboot",
        "vue",
        "react",
        "python-fastapi",
        "node-express",
        "fpga-vivado-vitis"
    )
    foreach ($stack in $requiredStacks) {
        Test-RequiredPath "templates\$stack\README.md"
        Test-RequiredPath "templates\$stack\commands.md"
        Test-RequiredPath "templates\$stack\codex-addons.md"
        Test-RequiredPath "templates\$stack\checklist.md"
        Test-RequiredPath "templates\$stack\docs-notes.md"
    }
}

function Test-PromptTemplates {
    $promptDir = Join-Path $repoRoot "prompts"
    if (-not (Test-Path -LiteralPath $promptDir)) {
        Add-Error "Missing prompt directory: prompts"
        return
    }
    $promptCount = (Get-ChildItem -LiteralPath $promptDir -Filter "*.prompt.md" -File).Count
    if ($promptCount -lt 7) {
        Add-Error "Expected at least 7 prompt templates, found $promptCount"
    }
}

function Test-StaleText {
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/project development plan" "Stale document path"
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/version roadmap" "Stale document path"
    Test-NoPattern "scripts\init-project-template.ps1" "docs/technology selection document" "Stale init text"
}

Test-RequiredPath "README.md"
Test-RequiredPath "AGENTS.md"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "project-template\README.md"
Test-RequiredPath "project-template\AGENTS.md"
Test-RequiredPath "project-template\.codex\rules.md"
Test-RequiredPath "project-template\.agents\skills\project-init\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\project-bootstrap-fill\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\handover-review\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\code-review\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\release-check\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\security-review\SKILL.md"
Test-RequiredPath "project-template\governance\project-bootstrap-fill.md"

Test-GovernanceFiles
Test-StackTemplates
Test-PromptTemplates
Test-AgentsHarness
Test-HarnessEntryConsistency
Test-StackHarnessDetails
Test-LargeChangeProtocol
Test-TeamToolingProtocol
Test-AgentSuitability
Test-SkillAscii
Test-SkillFrontmatter
Test-StaleText

if (-not $SkipSkillValidation) {
    $validator = Join-Path $env:USERPROFILE ".codex-b\skills\.system\skill-creator\scripts\quick_validate.py"
    if (Test-Path -LiteralPath $validator) {
        $skillDirs = Get-ChildItem -LiteralPath (Join-Path $projectTemplate ".agents\skills") -Directory
        foreach ($dir in $skillDirs) {
            $result = & python $validator $dir.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                Add-Error "Skill validation failed: $($dir.Name) $result"
            }
        }
    } else {
        Write-Host "[warn] Skill validator not found; skipped quick_validate.py"
    }
}

if ($errors.Count -gt 0) {
    Write-Host "[fail] Template validation failed"
    foreach ($errorItem in $errors) {
        Write-Host " - $errorItem"
    }
    exit 1
}

Write-Host "[ok] Template validation passed"
