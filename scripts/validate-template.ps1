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

function Get-CodexNextWorkOrderPath {
    $name = "Codex" + ([char]0x4E0B).ToString() + ([char]0x4E00).ToString() + ([char]0x6B65).ToString() + ([char]0x5DE5).ToString() + ([char]0x4F5C).ToString() + ([char]0x5355).ToString()
    return "project-template\docs\$name.md"
}

function Get-CodexNextWorkOrderRef {
    $name = "Codex" + ([char]0x4E0B).ToString() + ([char]0x4E00).ToString() + ([char]0x6B65).ToString() + ([char]0x5DE5).ToString() + ([char]0x4F5C).ToString() + ([char]0x5355).ToString()
    return "docs/$name.md"
}

function Get-VersionRoadmapPath {
    $name = ([char]0x7248).ToString() + ([char]0x672C).ToString() + ([char]0x8DEF).ToString() + ([char]0x7EBF).ToString() + ([char]0x56FE).ToString()
    return "project-template\docs\$name.md"
}

function Get-ProjectTaskBoardPath {
    $name = ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x4EFB).ToString() + ([char]0x52A1).ToString() + ([char]0x770B).ToString() + ([char]0x677F).ToString()
    return "project-template\docs\$name.md"
}

function Get-ProjectPlanPath {
    $name = ([char]0x9879).ToString() + ([char]0x76EE).ToString() + ([char]0x5F00).ToString() + ([char]0x53D1).ToString() + ([char]0x65B9).ToString() + ([char]0x6848).ToString()
    return "project-template\docs\$name.md"
}

function Get-RequiredStacks {
    return @(
        "java-springboot",
        "vue",
        "react",
        "python-fastapi",
        "node-express",
        "csharp-dotnet",
        "go-service",
        "php-laravel",
        "rust-cli-service",
        "flutter-dart",
        "cpp-cmake",
        "kotlin-spring",
        "swift-ios",
        "ruby-rails",
        "r-data-analysis",
        "fpga-vivado-vitis"
    )
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
    Test-RequiredPath (Get-CodexNextWorkOrderPath)
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
    Test-RequiredPattern "project-template\AGENTS.md" (Get-CodexNextWorkOrderRef) "Codex next work order routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ExplorationReportRef) "Exploration report routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ImplementationPlanRef) "Implementation plan routing"
}

function Test-HarnessEntryConsistency {
    $codebaseMapRef = Get-CodebaseMapRef
    Test-RequiredPattern "README.md" "Agent Harness" "Root README harness section"
    Test-RequiredPattern "README.md" "agent runtime" "Root README ECC boundary"
    Test-RequiredPattern "README.md" "ECC" "Root README ECC reference"
    Test-RequiredPattern "README.md" $codebaseMapRef "Root README codebase map reference"
    Test-RequiredPattern "README.md" (Get-LocalToolchainRef) "Root README local toolchain reference"
    Test-RequiredPattern "README.md" "plugins/forgekit-codex-workflow/" "Root README plugin distribution reference"
    Test-RequiredPattern "project-template\README.md" "governance/agent-harness.md" "Template README harness reference"
    Test-RequiredPattern "project-template\README.md" "governance/large-change-execution.md" "Template README large-change reference"
    Test-RequiredPattern "project-template\README.md" "governance/team-agent-rollout.md" "Template README team rollout reference"
    Test-RequiredPattern "project-template\README.md" "governance/agent-suitability.md" "Template README suitability reference"
    Test-RequiredPattern "project-template\README.md" "forgekit-codex-workflow" "Template README plugin reference"
    Test-RequiredPattern "project-template\README.md" $codebaseMapRef "Template README codebase map reference"
    Test-RequiredPattern "project-template\README.md" (Get-LocalToolchainRef) "Template README local toolchain reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "governance/agent-harness.md" "Skills harness reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "governance/team-agent-rollout.md" "Skills team rollout reference"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "AGENTS.md" "Skill README AGENTS reference"
    Test-RequiredPattern "project-template\.codex\skills.md" (Get-CodexNextWorkOrderRef) "Skills next work order reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "forgekit-codex-workflow" "Skills plugin distribution reference"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "detect-local-toolchain.ps1" "Skill README toolchain detector reference"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "run-harness-check.ps1" "Skill README harness check reference"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "forgekit-codex-workflow" "Skill README plugin distribution reference"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Start Codex from AGENTS.md" "Init script startup guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "[ValidateSet(""Lite"", ""Standard"", ""Enterprise"")]" "Init script mode parameter"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\scripts\init-project-template.ps1" "[ValidateSet(""Lite"", ""Standard"", ""Enterprise"")]" "Plugin init script mode parameter"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.zh-CN.md" "-Mode Standard" "Plugin Chinese README mode quickstart"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.md" "-Mode Standard" "Plugin English README mode quickstart"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.zh-CN.md" "Discovery Interview" "Plugin Chinese README discovery interview"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.md" "Discovery Interview" "Plugin English README discovery interview"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.zh-CN.md" "agent runtime" "Codex plugin ECC boundary"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.md" "Boundary With ECC" "Codex plugin English ECC boundary"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.zh-CN.md" "ECC" "Codex plugin ECC reference"
    Test-RequiredPattern "plugins\forgekit-codex-workflow\README.md" "Do not replicate ECC" "Codex plugin English no ECC clone boundary"
    Test-NoPattern "plugins\forgekit-codex-workflow\README.zh-CN.md" "## 常用技术栈" "Plugin README must not front-load stack selection"
    Test-NoPattern "plugins\forgekit-codex-workflow\README.md" "## Common Stacks" "Plugin README must not front-load stack selection"
    Test-RequiredPattern "scripts\init-project-template.ps1" "codebase map" "Init script codebase map guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "StackSelection: deferred" "Init script deferred stack guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "large-change-execution.md" "Init script large-change guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "team-agent-rollout.md" "Init script team rollout guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "detect-local-toolchain.ps1" "Init script toolchain detection guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "run-harness-check.ps1" "Init script harness check guidance"
    Test-RequiredPattern "使用说明.html" "startupOutput" "HTML startup output"
    Test-RequiredPattern "使用说明.html" "governance/agent-harness.md" "HTML harness prompt reference"
    Test-RequiredPattern "使用说明.html" "governance/large-change-execution.md" "HTML large-change prompt reference"
    Test-RequiredPattern "使用说明.html" "governance/agent-suitability.md" "HTML suitability prompt reference"
    Test-RequiredPattern "使用说明.html" "不要默认读取全部" "HTML context guard"
    Test-RequiredPattern "使用说明.html" "detect-local-toolchain.ps1" "HTML executable harness prompt"
    Test-RequiredPattern "使用说明.html" "run-harness-check.ps1" "HTML harness check prompt"
    Test-RequiredPattern "使用说明.html" "plugins/forgekit-codex-workflow/" "HTML plugin distribution reference"
    Test-RequiredPattern "使用说明.html" "Execution Confirmation" "HTML execution confirmation prompt"
    Test-RequiredPattern "使用说明.html" "产品方案商讨" "HTML product planning prompt"
}

function Test-ExecutableHarness {
    Test-RequiredPath "project-template\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "project-template\scripts\run-harness-check.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.sh"
    Test-RequiredPath "project-template\scripts\install-hooks.ps1"
    Test-RequiredPath "project-template\scripts\install-hooks.sh"
    Test-RequiredPath "project-template\.codex\automation-decision.md"
    Test-RequiredPath "project-template\.codex\automation-decision.md"
    Test-RequiredPath (Get-CodexNextWorkOrderPath)
    Test-RequiredPattern "project-template\scripts\detect-local-toolchain.ps1" "Do not install missing tools" "Toolchain detector safety guard"
    Test-RequiredPattern "project-template\scripts\run-harness-check.ps1" "Harness check passed" "Harness check success output"
    Test-RequiredPattern "project-template\.codex\commands.md" "detect-local-toolchain.ps1" "Commands toolchain detector"
    Test-RequiredPattern "project-template\.codex\commands.md" "run-harness-check.ps1" "Commands harness check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.ps1" "Commands document sync check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.sh" "Commands document sync check bash"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.ps1" "Commands hook installer"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.sh" "Commands hook installer bash"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "detect-local-toolchain" "Commands catalog toolchain detector"
    Test-RequiredPattern "project-template\.codex\hooks.md" "run-harness-check.ps1" "Hooks harness check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.ps1" "Hooks document sync check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.sh" "Hooks document sync check bash"
    Test-RequiredPattern "project-template\.codex\hooks.md" "install-hooks.sh" "Hooks installer bash"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "push" "Automation decision hook rejection section"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "docs-warn" "Automation decision hook profile"
    Test-RequiredPattern (Get-LocalToolchainPath) "detect-local-toolchain.ps1" "Local toolchain executable detector reference"
}

function Test-PluginDistribution {
    $pluginRoot = Join-Path $repoRoot "plugins\forgekit-codex-workflow"
    Test-RequiredPath ".agents\plugins\marketplace.json"
    Test-RequiredPath "plugins\forgekit-codex-workflow\.codex-plugin\plugin.json"
    Test-RequiredPath "plugins\forgekit-codex-workflow\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\README.zh-CN.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\project-init\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\project-bootstrap-fill\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\handover-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\code-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\release-check\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\security-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\init-project-template.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\validate-plugin-assets.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\run-harness-check.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\AGENTS.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\CLAUDE.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\.codex\stacks\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\.codex\stacks\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\java-springboot\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\csharp-dotnet\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\go-service\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\php-laravel\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\rust-cli-service\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\flutter-dart\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\cpp-cmake\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\kotlin-spring\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\swift-ios\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\ruby-rails\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\r-data-analysis\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\questionnaires\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\install.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\upgrade.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\safety.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\feedback.md"

    if (Test-Path -LiteralPath $pluginRoot) {
        $forbidden = @("user-rules", "document", ".git")
        foreach ($item in $forbidden) {
            if (Test-Path -LiteralPath (Join-Path $pluginRoot $item)) {
                Add-Error "Forbidden path in plugin package: plugins\forgekit-codex-workflow\$item"
            }
        }
    }

    $pluginJsonPath = Join-Path $repoRoot "plugins\forgekit-codex-workflow\.codex-plugin\plugin.json"
    if (Test-Path -LiteralPath $pluginJsonPath) {
        $pluginJson = Get-Content -LiteralPath $pluginJsonPath -Raw | ConvertFrom-Json
        if ($pluginJson.name -ne "forgekit-codex-workflow") {
            Add-Error "Unexpected plugin name in plugin.json: $($pluginJson.name)"
        }
        if ($pluginJson.version -ne "0.10.1") {
            Add-Error "Unexpected plugin version in plugin.json: $($pluginJson.version)"
        }
        $pluginSkillsPath = $pluginJson.PSObject.Properties["skills"].Value
        if ($pluginSkillsPath -ne "./skills/") {
            Add-Error "Plugin skills path must be ./skills/"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "mcpServers") {
            Add-Error "Plugin must not enable MCP by default"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "hooks") {
            Add-Error "Plugin must not enable hooks by default"
        }
    }

    $marketplacePath = Join-Path $repoRoot ".agents\plugins\marketplace.json"
    if (Test-Path -LiteralPath $marketplacePath) {
        $marketplace = Get-Content -LiteralPath $marketplacePath -Raw | ConvertFrom-Json
        $entry = @($marketplace.plugins | Where-Object { $_.name -eq "forgekit-codex-workflow" })
        if ($entry.Count -ne 1) {
            Add-Error "Marketplace must include exactly one forgekit-codex-workflow entry"
        } else {
            if ($entry[0].source.path -ne "./plugins/forgekit-codex-workflow") {
                Add-Error "Marketplace source path must be ./plugins/forgekit-codex-workflow"
            }
            if ($entry[0].policy.installation -ne "AVAILABLE") {
                Add-Error "Marketplace install policy must be AVAILABLE"
            }
            if ($entry[0].policy.authentication -ne "ON_INSTALL") {
                Add-Error "Marketplace auth policy must be ON_INSTALL"
            }
        }
    }
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
    Test-RequiredPath "project-template\.codex\automation-decision.md"
    Test-RequiredPattern "project-template\governance\team-agent-rollout.md" "AGENTS -> skills -> commands -> hooks -> plugin -> MCP" "Team rollout order"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "GitHub" "GitHub integration catalog"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" ".codex/automation-decision.md" "Commands catalog automation decision reference"
    Test-RequiredPattern "project-template\.codex\hooks.md" "Opt-in only" "Hooks opt-in guard"
    Test-RequiredPattern "project-template\.codex\hooks.md" ".codex/automation-decision.md" "Hooks automation decision reference"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "docs-warn" "Automation decision hook profile"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "project-init" "Automation decision skill section"
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
    Test-RequiredPath "project-template\.agents\skills\large-change-planning\SKILL.md"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "large-change protocol" "Project init large-change gate"
    Test-RequiredPattern "project-template\.agents\skills\code-review\SKILL.md" "large-change protocol" "Code review large-change gate"
    Test-RequiredPattern "project-template\.agents\skills\release-check\SKILL.md" "large-change protocol" "Release check large-change gate"
    Test-RequiredPattern "project-template\.agents\skills\large-change-planning\SKILL.md" "staged implementation plan" "Large-change planning output"
    Test-RequiredPattern "project-template\AGENTS.md" "large-change-planning" "AGENTS large-change skill routing"
    Test-RequiredPattern "project-template\CLAUDE.md" "large-change-planning" "CLAUDE large-change skill routing"
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
    $requiredStacks = Get-RequiredStacks
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
    $requiredStacks = Get-RequiredStacks
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

function Test-ClaudePluginDistribution {
    $pluginRoot = Join-Path $repoRoot "plugins\forgekit-claude-workflow"
    Test-RequiredPath ".claude-plugin\marketplace.json"
    Test-RequiredPath "plugins\forgekit-claude-workflow\.claude-plugin\plugin.json"
    Test-RequiredPath "plugins\forgekit-claude-workflow\README.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\README.zh-CN.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\project-init\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\project-bootstrap-fill\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\handover-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\code-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\release-check\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\skills\security-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\scripts\init-project-template.ps1"
    Test-RequiredPath "plugins\forgekit-claude-workflow\scripts\validate-plugin-assets.ps1"
    Test-RequiredPath "plugins\forgekit-claude-workflow\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "plugins\forgekit-claude-workflow\scripts\run-harness-check.ps1"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\project-template\AGENTS.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\project-template\CLAUDE.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\project-template\.codex\stacks\README.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\templates\java-springboot\README.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\questionnaires\README.md"
    Test-RequiredPath "plugins\forgekit-claude-workflow\assets\docs\install.md"
    Test-RequiredPattern "README.md" "plugins/forgekit-claude-workflow/" "Root README Claude plugin distribution reference"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.zh-CN.md" ".claude-plugin/plugin.json" "Claude Chinese README manifest path"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.md" ".claude-plugin/plugin.json" "Claude English README manifest path"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.zh-CN.md" "Claude Code runtime" "Claude plugin ECC boundary"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.md" "Boundary With ECC" "Claude plugin English ECC boundary"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.zh-CN.md" "ECC" "Claude plugin ECC reference"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\README.md" "Do not replicate ECC" "Claude plugin English no ECC clone boundary"
    Test-RequiredPattern "plugins\forgekit-claude-workflow\skills\project-init\SKILL.md" "existing-project-scan" "Claude project-init discovery state"

    if (Test-Path -LiteralPath $pluginRoot) {
        $forbidden = @("user-rules", "document", ".git", ".codex-plugin")
        foreach ($item in $forbidden) {
            if (Test-Path -LiteralPath (Join-Path $pluginRoot $item)) {
                Add-Error "Forbidden path in Claude plugin package: plugins\forgekit-claude-workflow\$item"
            }
        }
    }

    $pluginJsonPath = Join-Path $repoRoot "plugins\forgekit-claude-workflow\.claude-plugin\plugin.json"
    if (Test-Path -LiteralPath $pluginJsonPath) {
        $pluginJson = Get-Content -LiteralPath $pluginJsonPath -Raw | ConvertFrom-Json
        if ($pluginJson.name -ne "forgekit-claude-workflow") {
            Add-Error "Unexpected Claude plugin name in plugin.json: $($pluginJson.name)"
        }
        if ($pluginJson.version -ne "0.11.1") {
            Add-Error "Unexpected Claude plugin version in plugin.json: $($pluginJson.version)"
        }
        if (-not ($pluginJson.PSObject.Properties.Name -contains "skills")) {
            Add-Error "Claude plugin manifest must expose skills"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "mcpServers") {
            Add-Error "Claude plugin must not enable MCP by default"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "hooks") {
            Add-Error "Claude plugin must not enable hooks by default"
        }
    }

    $marketplacePath = Join-Path $repoRoot ".claude-plugin\marketplace.json"
    if (Test-Path -LiteralPath $marketplacePath) {
        $marketplaceJson = Get-Content -LiteralPath $marketplacePath -Raw | ConvertFrom-Json
        $pluginEntry = $marketplaceJson.plugins | Where-Object { $_.name -eq "forgekit-claude-workflow" } | Select-Object -First 1
        if (-not $pluginEntry) {
            Add-Error "Claude marketplace must list forgekit-claude-workflow"
        } elseif ($pluginEntry.source -ne "./plugins/forgekit-claude-workflow") {
            Add-Error "Claude marketplace source must point to ./plugins/forgekit-claude-workflow"
        }
    }
}

function Test-StaleText {
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/project development plan" "Stale document path"
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/version roadmap" "Stale document path"
    Test-NoPattern "scripts\init-project-template.ps1" "docs/technology selection document" "Stale init text"
    Test-NoPattern (Get-VersionRoadmapPath) "TASK-HARNESS" "ForgeKit harness task leaked into generated roadmap"
    Test-NoPattern (Get-VersionRoadmapPath) "FEAT-HARNESS" "ForgeKit harness feature leaked into generated roadmap"
    Test-NoPattern (Get-ProjectTaskBoardPath) "TASK-HARNESS" "ForgeKit harness task leaked into generated task board"
    Test-NoPattern (Get-ProjectTaskBoardPath) "FEAT-HARNESS" "ForgeKit harness feature leaked into generated task board"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Execution Confirmation" "Project init execution confirmation gate"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Do not make stack selection the first user task" "Project init deferred stack rule"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Infer stack" "Project init existing-project stack inference"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Classify the discovery state" "Project init discovery state gate"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "evidence extracted" "Project init existing-project evidence summary"
    Test-RequiredPattern "project-template\.agents\skills\handover-review\SKILL.md" "Evidence-first gate" "Handover evidence-first gate"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "document backfill pass" "Project init document backfill pass"
    Test-RequiredPattern "project-template\.agents\skills\handover-review\SKILL.md" "Document backfill pass" "Handover document backfill pass"
    Test-RequiredPattern "project-template\.agents\skills\document-backfill\SKILL.md" "Process exactly one source document at a time" "Document backfill one-source rule"
    Test-RequiredPattern "project-template\AGENTS.md" "one source document at a time" "AGENTS doc backfill routing"
    Test-RequiredPattern "project-template\CLAUDE.md" "one source document at a time" "CLAUDE doc backfill routing"
    Test-RequiredPattern "project-template\AGENTS.md" "existing README/usage/setup/test/deploy docs first" "AGENTS existing project docs-first routing"
    Test-RequiredPattern "project-template\CLAUDE.md" "existing README/usage/setup/test/deploy docs first" "CLAUDE existing project docs-first routing"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "options-needed" "Project init options state"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "research-needed" "Project init research state"
    Test-RequiredPath "project-template\.codex\stacks\README.md"
    Test-RequiredPattern "project-template\AGENTS.md" "execution summary" "AGENTS execution summary gate"
    Test-RequiredPattern (Get-CodexNextWorkOrderPath) "Execution Confirmation" "Next work order execution confirmation gate"
    Test-RequiredPattern (Get-ProjectPlanPath) "Product Shape Options" "Project plan product-shape section"
    Test-RequiredPattern "project-template\.codex\scope.md" "Execution Confirmation" "Scope execution confirmation gate"
}

function Test-StackTemplates {
    $requiredStacks = Get-RequiredStacks
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

function Test-StackHarnessDetails {
    $requiredStacks = Get-RequiredStacks
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

function Test-TeamToolingProtocol {
    Test-RequiredPath "project-template\governance\team-agent-rollout.md"
    Test-RequiredPath "project-template\.codex\commands-catalog.md"
    Test-RequiredPath "project-template\.codex\hooks.md"
    Test-RequiredPath "project-template\.codex\automation-decision.md"
    Test-RequiredPattern "project-template\governance\team-agent-rollout.md" "AGENTS -> skills -> commands -> hooks -> plugin -> MCP" "Team rollout order"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "GitHub" "GitHub integration catalog"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" ".codex/automation-decision.md" "Commands catalog automation decision reference"
    Test-RequiredPattern "project-template\.codex\hooks.md" "Opt-in only" "Hooks opt-in guard"
    Test-RequiredPattern "project-template\.codex\hooks.md" ".codex/automation-decision.md" "Hooks automation decision reference"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "docs-warn" "Automation decision hook profile"
    Test-RequiredPattern "project-template\.codex\automation-decision.md" "project-init" "Automation decision skill section"
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

function Test-AgentSuitability {
    Test-RequiredPath "project-template\governance\agent-suitability.md"
    Test-RequiredPath (Get-SuitabilityPath)
    Test-RequiredPath (Get-TrialRecordPath)
    Test-RequiredPath "project-template\.agents\skills\project-suitability\SKILL.md"
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Suitable" "Suitability outcomes"
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Conditional" "Conditional suitability outcome"
    Test-RequiredPattern "project-template\governance\agent-suitability.md" "Custom" "Custom suitability outcome"
    Test-RequiredPattern "project-template\.agents\skills\project-suitability\SKILL.md" "Suitable, Conditional, or Custom" "Project suitability skill outcome"
    Test-RequiredPattern "project-template\AGENTS.md" "project-suitability" "AGENTS suitability skill routing"
    Test-RequiredPattern "project-template\CLAUDE.md" "project-suitability" "CLAUDE suitability skill routing"
    Test-RequiredPattern "使用说明.html" "suitabilityList" "HTML suitability checklist"
    Test-RequiredPattern "使用说明.html" "适用性已确认" "HTML suitability brief"
}

function Test-ExecutableHarness {
    Test-RequiredPath "project-template\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "project-template\scripts\run-harness-check.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.sh"
    Test-RequiredPath "project-template\scripts\install-hooks.ps1"
    Test-RequiredPath "project-template\scripts\install-hooks.sh"
    Test-RequiredPath (Get-CodexNextWorkOrderPath)
    Test-RequiredPattern "project-template\scripts\detect-local-toolchain.ps1" "Do not install missing tools" "Toolchain detector safety guard"
    Test-RequiredPattern "project-template\scripts\run-harness-check.ps1" "Harness check passed" "Harness check success output"
    Test-RequiredPattern "project-template\.codex\commands.md" "detect-local-toolchain.ps1" "Commands toolchain detector"
    Test-RequiredPattern "project-template\.codex\commands.md" "run-harness-check.ps1" "Commands harness check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.ps1" "Commands document sync check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.sh" "Commands document sync check bash"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.ps1" "Commands hook installer"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.sh" "Commands hook installer bash"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "detect-local-toolchain" "Commands catalog toolchain detector"
    Test-RequiredPattern "project-template\.codex\hooks.md" "run-harness-check.ps1" "Hooks harness check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.ps1" "Hooks document sync check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.sh" "Hooks document sync check bash"
    Test-RequiredPattern "project-template\.codex\hooks.md" "install-hooks.sh" "Hooks installer bash"
    Test-RequiredPattern (Get-LocalToolchainPath) "detect-local-toolchain.ps1" "Local toolchain executable detector reference"
}

function Test-PluginDistribution {
    $pluginRoot = Join-Path $repoRoot "plugins\forgekit-codex-workflow"
    Test-RequiredPath ".agents\plugins\marketplace.json"
    Test-RequiredPath "plugins\forgekit-codex-workflow\.codex-plugin\plugin.json"
    Test-RequiredPath "plugins\forgekit-codex-workflow\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\README.zh-CN.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\project-init\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\project-bootstrap-fill\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\handover-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\code-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\release-check\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\skills\security-review\SKILL.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\init-project-template.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\validate-plugin-assets.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\scripts\run-harness-check.ps1"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\project-template\AGENTS.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\java-springboot\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\csharp-dotnet\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\go-service\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\php-laravel\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\rust-cli-service\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\flutter-dart\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\cpp-cmake\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\kotlin-spring\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\swift-ios\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\ruby-rails\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\templates\r-data-analysis\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\questionnaires\README.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\install.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\upgrade.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\safety.md"
    Test-RequiredPath "plugins\forgekit-codex-workflow\assets\docs\feedback.md"

    if (Test-Path -LiteralPath $pluginRoot) {
        $forbidden = @("user-rules", "document", ".git")
        foreach ($item in $forbidden) {
            if (Test-Path -LiteralPath (Join-Path $pluginRoot $item)) {
                Add-Error "Forbidden path in plugin package: plugins\forgekit-codex-workflow\$item"
            }
        }
    }

    $pluginJsonPath = Join-Path $repoRoot "plugins\forgekit-codex-workflow\.codex-plugin\plugin.json"
    if (Test-Path -LiteralPath $pluginJsonPath) {
        $pluginJson = Get-Content -LiteralPath $pluginJsonPath -Raw | ConvertFrom-Json
        if ($pluginJson.name -ne "forgekit-codex-workflow") {
            Add-Error "Unexpected plugin name in plugin.json: $($pluginJson.name)"
        }
        if ($pluginJson.version -ne "0.10.1") {
            Add-Error "Unexpected plugin version in plugin.json: $($pluginJson.version)"
        }
        $pluginSkillsPath = $pluginJson.PSObject.Properties["skills"].Value
        if ($pluginSkillsPath -ne "./skills/") {
            Add-Error "Plugin skills path must be ./skills/"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "mcpServers") {
            Add-Error "Plugin must not enable MCP by default"
        }
        if ($pluginJson.PSObject.Properties.Name -contains "hooks") {
            Add-Error "Plugin must not enable hooks by default"
        }
    }
}

function Test-StaleText {
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/project development plan" "Stale document path"
    Test-NoPattern "project-template\.agents\skills\project-init\SKILL.md" "docs/version roadmap" "Stale document path"
    Test-NoPattern "scripts\init-project-template.ps1" "docs/technology selection document" "Stale init text"
    Test-NoPattern (Get-VersionRoadmapPath) "TASK-HARNESS" "ForgeKit harness task leaked into generated roadmap"
    Test-NoPattern (Get-VersionRoadmapPath) "FEAT-HARNESS" "ForgeKit harness feature leaked into generated roadmap"
    Test-NoPattern (Get-ProjectTaskBoardPath) "TASK-HARNESS" "ForgeKit harness task leaked into generated task board"
    Test-NoPattern (Get-ProjectTaskBoardPath) "FEAT-HARNESS" "ForgeKit harness feature leaked into generated task board"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Execution Confirmation" "Project init execution confirmation gate"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Do not make stack selection the first user task" "Project init deferred stack rule"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Infer stack" "Project init existing-project stack inference"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "Classify the discovery state" "Project init discovery state gate"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "options-needed" "Project init options state"
    Test-RequiredPattern "project-template\.agents\skills\project-init\SKILL.md" "research-needed" "Project init research state"
    Test-RequiredPath "project-template\.codex\stacks\README.md"
    Test-RequiredPattern "project-template\AGENTS.md" "execution summary" "AGENTS execution summary gate"
    Test-RequiredPattern (Get-CodexNextWorkOrderPath) "Execution Confirmation" "Next work order execution confirmation gate"
    Test-RequiredPattern (Get-ProjectPlanPath) "Product Shape Options" "Project plan product-shape section"
    Test-RequiredPattern "project-template\.codex\scope.md" "Execution Confirmation" "Scope execution confirmation gate"
}

function Test-HarnessEntryConsistency {
    $codebaseMapRef = Get-CodebaseMapRef
    Test-RequiredPattern "README.md" "Plugin Distribution" "Root README unified plugin surface"
    Test-RequiredPattern "README.md" ".codex-plugin/plugin.json" "Root README Codex root manifest"
    Test-RequiredPattern "README.md" ".claude-plugin/plugin.json" "Root README Claude root manifest"
    Test-RequiredPattern "README.md" "./skills/" "Root README shared skills reference"
    Test-RequiredPattern "README.md" $codebaseMapRef "Root README codebase map reference"
    Test-RequiredPattern "project-template\README.md" "v0.12.0" "Template README unified plugin note"
    Test-RequiredPattern "project-template\README.md" "CLAUDE.md" "Template README Claude entry"
    Test-RequiredPattern "project-template\README.md" $codebaseMapRef "Template README codebase map reference"
    Test-RequiredPattern "project-template\.codex\skills.md" "v0.12.0" "Skills unified plugin note"
    Test-RequiredPattern "project-template\.agents\skills\README.md" "v0.12.0" "Skill README unified plugin note"
    Test-RequiredPattern "scripts\init-project-template.ps1" "CLAUDE.md" "Init script Claude startup guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "[ValidateSet(""Lite"", ""Standard"", ""Enterprise"")]" "Init script mode parameter"
    Test-RequiredPattern "scripts\init-project-template.ps1" "StackSelection: deferred" "Init script deferred stack guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Upgrade" "Init script upgrade mode"
    Test-RequiredPattern "scripts\init-project-template.ps1" "upgrade-report.md" "Init script upgrade report"
    Test-RequiredPattern "scripts\init-project-template.ps1" "ExportUpgradeTemplates" "Init script export upgrade templates"
    Test-RequiredPattern "scripts\init-project-template.sh" "--upgrade" "Bash init upgrade mode"
    Test-RequiredPattern "scripts\init-project-template.sh" "upgrade-report.md" "Bash init upgrade report"
    Test-RequiredPattern "scripts\init-project-template.sh" "--export-upgrade-templates" "Bash init export upgrade templates"
    Test-RequiredPattern "README.md" "-Upgrade" "Root README upgrade guidance"
    Test-RequiredPattern "README.md" "upgrade-report.md" "Root README upgrade report guidance"
    Test-RequiredPattern "README.en.md" "-Upgrade" "English README upgrade guidance"
    Test-RequiredPattern "README.en.md" "upgrade-report.md" "English README upgrade report guidance"
    Test-RequiredPattern "使用说明.html" "startupOutput" "HTML startup output"
    Test-RequiredPattern "使用说明.html" "governance/agent-harness.md" "HTML harness prompt reference"
}

function Test-PluginDistribution {
    Test-RequiredPath ".agents\plugins\marketplace.json"
    Test-RequiredPath ".claude-plugin\marketplace.json"
    Test-RequiredPath ".codex-plugin\plugin.json"
    Test-RequiredPath ".claude-plugin\plugin.json"
    Test-RequiredPath "skills\project-init\SKILL.md"
    Test-RequiredPath "skills\project-bootstrap-fill\SKILL.md"
    Test-RequiredPath "skills\project-suitability\SKILL.md"
    Test-RequiredPath "skills\document-backfill\SKILL.md"
    Test-RequiredPath "skills\handover-review\SKILL.md"
    Test-RequiredPath "skills\large-change-planning\SKILL.md"
    Test-RequiredPath "skills\code-review\SKILL.md"
    Test-RequiredPath "skills\release-check\SKILL.md"
    Test-RequiredPath "skills\security-review\SKILL.md"
    Test-RequiredPath "scripts\validate-plugin-assets.ps1"
    Test-RequiredPattern "skills\project-init\SKILL.md" "existing-project-scan" "Root project-init discovery state"
    Test-RequiredPattern "skills\project-init\SKILL.md" "evidence extracted" "Root project-init evidence summary"
    Test-RequiredPattern "skills\handover-review\SKILL.md" "Evidence-first gate" "Root handover evidence-first gate"
    Test-RequiredPattern "skills\project-init\SKILL.md" "document backfill pass" "Root project-init document backfill pass"
    Test-RequiredPattern "skills\handover-review\SKILL.md" "Document backfill pass" "Root handover document backfill pass"
    Test-RequiredPattern "skills\document-backfill\SKILL.md" "Process exactly one source document at a time" "Root document backfill one-source rule"
    Test-RequiredPattern "skills\project-suitability\SKILL.md" "Suitable, Conditional, or Custom" "Root project suitability outcome"
    Test-RequiredPattern "skills\large-change-planning\SKILL.md" "staged implementation plan" "Root large-change planning output"
    if (Test-Path -LiteralPath (Join-Path $repoRoot "plugins\forgekit-codex-workflow")) {
        Add-Error "Codex plugin subdirectory must not exist in unified 0.12.0 surface"
    }
    if (Test-Path -LiteralPath (Join-Path $repoRoot "plugins\forgekit-claude-workflow")) {
        Add-Error "Claude plugin subdirectory must not exist in unified 0.12.0 surface"
    }

    $codexPluginJson = Get-Content -LiteralPath (Join-Path $repoRoot ".codex-plugin\plugin.json") -Raw | ConvertFrom-Json
    if ($codexPluginJson.name -ne "forgekit") {
        Add-Error "Unexpected Codex plugin name in root plugin.json: $($codexPluginJson.name)"
    }
    if ($codexPluginJson.version -ne "0.13.0") {
        Add-Error "Unexpected Codex plugin version in root plugin.json: $($codexPluginJson.version)"
    }
    if ($codexPluginJson.skills -ne "./skills/") {
        Add-Error "Root Codex plugin skills must be ./skills/"
    }

    $claudePluginJson = Get-Content -LiteralPath (Join-Path $repoRoot ".claude-plugin\plugin.json") -Raw | ConvertFrom-Json
    if ($claudePluginJson.name -ne "forgekit") {
        Add-Error "Unexpected Claude plugin name in root plugin.json: $($claudePluginJson.name)"
    }
    if ($claudePluginJson.version -ne "0.13.0") {
        Add-Error "Unexpected Claude plugin version in root plugin.json: $($claudePluginJson.version)"
    }
    $claudeSkills = @($claudePluginJson.skills)
    if ($claudeSkills.Count -ne 1 -or $claudeSkills[0] -ne "./skills/") {
        Add-Error "Root Claude plugin skills must be ./skills/"
    }
}

function Test-ClaudePluginDistribution {
    Test-RequiredPath ".claude-plugin\plugin.json"
    Test-RequiredPath ".claude-plugin\marketplace.json"
    Test-RequiredPath "project-template\CLAUDE.md"
    Test-RequiredPath "project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
    Test-RequiredPattern "project-template\CLAUDE.md" "Claude Code Project Guide" "Claude project guide"
    Test-RequiredPattern "project-template\.claude\skills\forgekit-project-workflow\SKILL.md" "Discovery State" "Claude thin entry skill"
}

Test-RequiredPath "README.md"
Test-RequiredPath "AGENTS.md"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "scripts\init-project-template.sh"
Test-RequiredPath "scripts\validate-plugin-assets.ps1"
Test-RequiredPath "project-template\README.md"
Test-RequiredPath "project-template\AGENTS.md"
Test-RequiredPath "project-template\CLAUDE.md"
Test-RequiredPath "project-template\.codex\rules.md"
Test-RequiredPath "project-template\.claude\skills\forgekit-project-workflow\SKILL.md"
    Test-RequiredPath "project-template\.agents\skills\project-init\SKILL.md"
    Test-RequiredPath "project-template\.agents\skills\project-bootstrap-fill\SKILL.md"
    Test-RequiredPath "project-template\.agents\skills\project-suitability\SKILL.md"
    Test-RequiredPath "project-template\.agents\skills\document-backfill\SKILL.md"
    Test-RequiredPath "project-template\.agents\skills\handover-review\SKILL.md"
Test-RequiredPath "project-template\.agents\skills\large-change-planning\SKILL.md"
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
Test-ExecutableHarness
Test-PluginDistribution
Test-ClaudePluginDistribution
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
