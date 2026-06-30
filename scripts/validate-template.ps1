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
        "project-template\governance\ai-engineering-loop.md"
    )
    foreach ($item in $required) {
        Test-RequiredPath $item
    }
}

function Get-CodebaseMapPath {
    return "project-template\docs\codebase-map.md"
}

function Get-CodebaseMapRef {
    return ".forgekit/docs/codebase-map.md"
}

function Get-LocalToolchainPath {
    return "project-template\docs\local-toolchain.md"
}

function Get-LocalToolchainRef {
    return ".forgekit/docs/local-toolchain.md"
}

function Get-ExplorationReportPath {
    return "project-template\docs\exploration-report.md"
}

function Get-ImplementationPlanPath {
    return "project-template\docs\implementation-plan.md"
}

function Get-ExplorationReportRef {
    return ".forgekit/docs/exploration-report.md"
}

function Get-ImplementationPlanRef {
    return ".forgekit/docs/implementation-plan.md"
}

function Get-SuitabilityPath {
    return "project-template\docs\project-suitability.md"
}

function Get-SuitabilityRef {
    return ".forgekit/docs/project-suitability.md"
}

function Get-TrialRecordPath {
    return "project-template\docs\project-trial-record.md"
}

function Get-TrialRecordRef {
    return ".forgekit/docs/project-trial-record.md"
}

function Get-CodexNextWorkOrderPath {
    return "project-template\docs\codex-next-work-order.md"
}

function Get-CodexNextWorkOrderRef {
    return ".forgekit/docs/codex-next-work-order.md"
}

function Get-VersionRoadmapPath {
    return "project-template\docs\version-roadmap.md"
}

function Get-ProjectTaskBoardPath {
    return "project-template\docs\task-board.md"
}

function Get-ProjectPlanPath {
    return "project-template\docs\project-plan.md"
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
    Test-RequiredPath "project-template\.forgekit\project-boundary.yml"
    Test-RequiredPath "project-template\.forgekit\docs\document-responsibility.md"
    Test-RequiredPath "project-template\.forgekit\docs\document-lifecycle.md"
    Test-RequiredPath "project-template\docs\work-log.md"
    Test-RequiredPath "project-template\docs\task-intake.md"
    Test-RequiredPath "project-template\docs\workflow-router.md"
    Test-RequiredPath "project-template\.forgekit\archive\README.md"
    Test-RequiredPath "project-template\.forgekit\archive\changes\README.md"
    Test-RequiredPath "project-template\.forgekit\archive\releases\README.md"
    Test-RequiredPath "project-template\governance\agent-harness.md"
    Test-RequiredPath "project-template\governance\ai-engineering-loop.md"
    Test-RequiredPath "project-template\governance\large-change-execution.md"
    Test-RequiredPath "project-template\governance\team-agent-rollout.md"
    Test-RequiredPath "project-template\.codex\commands-catalog.md"
    Test-RequiredPath "project-template\.codex\hooks.md"
    Test-RequiredPattern "project-template\AGENTS.md" "Do not read every file" "Governance context guard"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-CodebaseMapRef) "Codebase map routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-LocalToolchainRef) "Local toolchain routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/agent-harness.md" "Agent harness routing"
    Test-RequiredPattern "project-template\AGENTS.md" ".forgekit/project-boundary.yml" "Boundary routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/ai-engineering-loop.md" "AI engineering loop routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/large-change-execution.md" "Large-change routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/team-agent-rollout.md" "Team rollout routing"
    Test-RequiredPattern "project-template\AGENTS.md" "governance/agent-suitability.md" "Agent suitability routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-SuitabilityRef) "Suitability document routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-CodexNextWorkOrderRef) "Codex next work order routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ExplorationReportRef) "Exploration report routing"
    Test-RequiredPattern "project-template\AGENTS.md" (Get-ImplementationPlanRef) "Implementation plan routing"
    Test-RequiredPattern "project-template\AGENTS.md" ".agents/skills/<skill>/SKILL.md" "AGENTS project-local skill resolution"
}

function Test-AIEngineeringLoop {
    $changeTemplates = @(
        "project-template\changes\README.md",
        "project-template\changes\_template\proposal.md",
        "project-template\changes\_template\design.md",
        "project-template\changes\_template\tasks.md",
        "project-template\changes\_template\verification.md",
        "project-template\changes\_template\review.md",
        "project-template\changes\_template\ship.md",
        "project-template\changes\_template\retro.md"
    )
    foreach ($item in $changeTemplates) {
        Test-RequiredPath $item
    }

    Test-RequiredPattern "project-template\changes\_template\proposal.md" "Status:" "Change proposal status metadata"
    Test-RequiredPattern "project-template\changes\_template\proposal.md" "Risk:" "Change proposal risk metadata"
    Test-RequiredPattern "project-template\changes\_template\proposal.md" "Created:" "Change proposal created metadata"
    Test-RequiredPattern "project-template\changes\_template\proposal.md" "Owner:" "Change proposal owner metadata"
    Test-RequiredPattern "project-template\changes\_template\proposal.md" "Reason:" "Change proposal reason metadata"
    Test-RequiredPattern "project-template\governance\ai-engineering-loop.md" "AI Engineering Loop" "AI engineering loop title"
    Test-RequiredPattern "project-template\governance\ai-engineering-loop.md" "low" "AI engineering loop low risk"
    Test-RequiredPattern "project-template\governance\ai-engineering-loop.md" "medium" "AI engineering loop medium risk"
    Test-RequiredPattern "project-template\governance\ai-engineering-loop.md" "high" "AI engineering loop high risk"
    Test-RequiredPattern "project-template\CLAUDE.md" "governance/ai-engineering-loop.md" "CLAUDE AI engineering loop routing"
    Test-RequiredPattern "project-template\.codex\rules.md" "governance/ai-engineering-loop.md" "Codex risk workflow rule"
    Test-RequiredPattern "project-template\.forgekit\project-boundary.yml" 'managed_docs_root: ".forgekit/docs"' "Boundary managed docs root"
    Test-RequiredPattern "project-template\.forgekit\project-boundary.yml" 'change_root: ".forgekit/changes"' "Boundary change root"
    Test-RequiredPattern "project-template\.forgekit\project-boundary.yml" "business_docs_roots:" "Boundary business docs roots"
    Test-RequiredPattern "project-template\.forgekit\project-boundary.yml" "task_scoped:" "Boundary task-scoped policy"
    Test-RequiredPattern "project-template\.forgekit\project-boundary.yml" "read_mostly:" "Boundary read-mostly policy"
    Test-RequiredPattern "project-template\.codex\rules.md" "Boundary First" "Codex boundary-first rule"
    Test-RequiredPattern "project-template\.forgekit\docs\document-lifecycle.md" "current docs say what is true now" "Document lifecycle core rule"
    Test-RequiredPattern "project-template\.forgekit\docs\document-lifecycle.md" "current docs say what is true now" "Document lifecycle current docs"
    Test-RequiredPattern "project-template\.forgekit\docs\document-lifecycle.md" "changes explain why and how one change happened" "Document lifecycle change docs"
    Test-RequiredPattern "project-template\.forgekit\docs\document-lifecycle.md" "archive preserves history without becoming current truth" "Document lifecycle archive docs"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "v2" "Document responsibility v2 title"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "core" "Document responsibility class value"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "current" "Document responsibility class value"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "as-needed" "Document responsibility default read value"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "triggered" "Document responsibility triggered value"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "work-log.md" "Document responsibility work log entry"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "task-intake.md" "Document responsibility task intake entry"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "workflow-router.md" "Document responsibility workflow router entry"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "用户意图" "Document responsibility workflow router purpose"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/" "Codebase map search-entry boundary"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/" "Codebase map no full docs read rule"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/work-log.md" "Codebase map work log index"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/task-intake.md" "Codebase map task intake index"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/workflow-router.md" "Codebase map workflow router index"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "Intent Routing Table" "Workflow router routing table"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "Read Targets" "Workflow router read targets"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "Write Targets" "Workflow router write targets"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "Do Not Write" "Workflow router do-not-write"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "Required Output" "Workflow router required output"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "task-intake.md" "Workflow router task intake coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "task-board.md" "Workflow router task board coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "requirements.md" "Workflow router requirements coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "work-log.md" "Workflow router work log coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "testing.md" "Workflow router testing coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "changelog.md" "Workflow router changelog coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "risk-register.md" "Workflow router risk coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "bounded-auto-loop-policy.md" "Workflow router loop coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "maker-checker-protocol.md" "Workflow router maker-checker coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "worktree-playbook.md" "Workflow router worktree coverage"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "handoff" "Workflow router handoff coverage"
    Test-RequiredPattern "project-template\AGENTS.md" "workflow-router.md" "AGENTS workflow router routing"
    Test-RequiredPattern "project-template\AGENTS.md" "intent routing" "AGENTS intent routing rule"
    Test-RequiredPattern "project-template\AGENTS.md" "doc-health-report.py" "AGENTS doc health report rule"
    Test-RequiredPattern "project-template\AGENTS.md" ".forgekit/doc-health-report.md" "AGENTS doc health generated report rule"
    Test-RequiredPattern "project-template\AGENTS.md" "source-trace-report.py" "AGENTS source trace report rule"
    Test-RequiredPattern "project-template\AGENTS.md" ".forgekit/source-trace-report.md" "AGENTS source trace generated report rule"
    Test-RequiredPattern "project-template\AGENTS.md" "handoff-package.py" "AGENTS handoff package rule"
    Test-RequiredPattern "project-template\AGENTS.md" ".forgekit/handoff-package.md" "AGENTS handoff generated report rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "workflow-router.md" "CLAUDE workflow router routing"
    Test-RequiredPattern "project-template\CLAUDE.md" "intent routing" "CLAUDE intent routing rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "doc-health-report.py" "CLAUDE doc health report rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "source-trace-report.py" "CLAUDE source trace report rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "handoff-package.py" "CLAUDE handoff package rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "workflow-router.md" "Rules workflow router routing"
    Test-RequiredPattern "project-template\.codex\rules.md" "intent routing" "Rules intent routing rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "doc-health-report.py" "Rules doc health report rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "source-trace-report.py" "Rules source trace report rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "handoff-package.py" "Rules handoff package rule"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" ".forgekit/doc-health-report.md" "Document responsibility doc health generated report"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" ".forgekit/source-trace-report.md" "Document responsibility source trace generated report"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" ".forgekit/handoff-package.md" "Document responsibility handoff generated report"
    Test-RequiredPattern "project-template\docs\codebase-map.md" "doc-health-report.py" "Codebase map doc health entry"
    Test-RequiredPattern "project-template\docs\codebase-map.md" "source-trace-report.py" "Codebase map source trace entry"
    Test-RequiredPattern "project-template\docs\codebase-map.md" "handoff-package.py" "Codebase map handoff entry"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "检查文档健康" "Workflow router doc health intent"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "检查任务来源追溯" "Workflow router source trace intent"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" ".forgekit/doc-health-report.md" "Bounded auto doc health stop boundary"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" ".forgekit/source-trace-report.md" "Bounded auto source trace stop boundary"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" ".forgekit/handoff-package.md" "Bounded auto handoff stop boundary"
    Test-RequiredPattern "project-template\docs\work-log.md" "Status:" "Work log recent window purpose"
    Test-RequiredPattern "project-template\docs\work-log.md" "Commit" "Work log commit status"
    Test-RequiredPattern "project-template\docs\work-log.md" "Push" "Work log push status"
    Test-RequiredPattern "project-template\docs\work-log.md" "handed-off" "Work log handoff status"
    Test-RequiredPattern "project-template\docs\work-log.md" "Not run" "Work log boundary"
    Test-RequiredPattern "project-template\docs\work-log.md" "Task ID" "Work log task backlink"
    Test-RequiredPattern "project-template\docs\work-log.md" "Source ID" "Work log source backlink"
    Test-RequiredPattern "project-template\docs\work-log.md" "needs-task-decision" "Work log no automatic task creation"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Source ID" "Task intake source record template"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Source Type" "Task intake source type"
    Test-RequiredPattern "project-template\docs\task-intake.md" "self-planned" "Task intake self planned source"
    Test-RequiredPattern "project-template\docs\task-intake.md" "user-feedback" "Task intake user feedback source"
    Test-RequiredPattern "project-template\docs\task-intake.md" "bug-found" "Task intake bug source"
    Test-RequiredPattern "project-template\docs\task-intake.md" "tech-debt" "Task intake technical debt source"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Received At" "Task intake received at"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Human Review" "Task intake human review field"
    Test-RequiredPattern "project-template\docs\task-intake.md" "AI" "Task intake AI interpretation"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Task ID" "Task intake derived tasks"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Update Notes" "Task intake update notes"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Task Decision" "Task intake decision gate"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Task Gate" "Task intake gate"
    Test-RequiredPattern "project-template\docs\task-intake.md" "update-existing-task" "Task intake update existing task"
    Test-RequiredPattern "project-template\docs\task-intake.md" "note-only" "Task intake note only"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Human Review" "Task intake human review"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Confidentiality:" "Task intake confidentiality"
    Test-RequiredPattern "project-template\docs\task-board.md" "Source ID" "Task board source ID backlink"
    Test-RequiredPattern "project-template\docs\task-intake.md" "Task Gate" "Task board intake gate"
    Test-RequiredPattern "project-template\docs\task-board.md" "Closed / Dropped / Superseded" "Task board closed table"
    Test-RequiredPattern "project-template\docs\task-board.md" "Superseded" "Task board alignment check"
    Test-RequiredPattern "project-template\docs\requirements.md" "task-intake.md" "Requirements task-intake boundary"
    Test-RequiredPattern "project-template\docs\changelog.md" "task-intake.md" "Changelog task-intake boundary"
    Test-RequiredPattern "project-template\changes\_template\review.md" "CurrentDocsSync: confirmed `| not-needed `| missing `| unknown" "Review current docs sync metadata"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ChangelogUpdated: yes `| no `| not-needed `| unknown" "Review changelog sync metadata"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ArchitectureUpdated: yes `| no `| not-needed `| unknown" "Review architecture sync metadata"
    Test-RequiredPattern "project-template\changes\_template\review.md" "TestingUpdated: yes `| no `| not-needed `| unknown" "Review testing sync metadata"
    Test-RequiredPattern "project-template\changes\_template\review.md" "RequirementsUpdated: yes `| no `| not-needed `| unknown" "Review requirements sync metadata"
    Test-RequiredPattern "project-template\changes\README.md" "Status" "Change README status lifecycle"
    Test-RequiredPattern "project-template\changes\README.md" "done" "Change README done status"
    Test-RequiredPattern "project-template\changes\README.md" "archived" "Change README archived status"
    Test-RequiredPattern "project-template\AGENTS.md" ".forgekit/archive/**" "AGENTS archive default-read rule"
    Test-RequiredPattern "project-template\CLAUDE.md" ".forgekit/archive/**" "CLAUDE archive default-read rule"
    Test-RequiredPattern "project-template\.codex\rules.md" ".forgekit/archive/**" "Rules archive default-read rule"
    Test-RequiredPath "project-template\docs\loop-readiness.md"
    Test-RequiredPath "project-template\docs\loop-blueprint.md"
    Test-RequiredPath "project-template\docs\loop-operations.md"
    Test-RequiredPath "project-template\docs\bounded-auto-loop-policy.md"
    Test-RequiredPath "project-template\docs\maker-checker-protocol.md"
    Test-RequiredPath "project-template\docs\native-agent-adapter.md"
    Test-RequiredPath "project-template\docs\worktree-playbook.md"
    Test-RequiredPattern "project-template\docs\loop-readiness.md" "Readiness Status: not-ready `| partial `| ready" "Loop readiness status"
    Test-RequiredPattern "project-template\docs\loop-readiness.md" "Loop suitability: not-ready `| partial `| ready" "Loop readiness suitability"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "Loop Name:" "Loop blueprint name"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "Default: manual only." "Loop blueprint manual trigger"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "State File" "Loop blueprint trigger"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Allowed Paths" "Loop blueprint input sources"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "State File" "Loop blueprint state file"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Allowed Paths" "Loop blueprint allowed paths"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Forbidden Paths" "Loop blueprint forbidden paths"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Validation Command" "Loop blueprint validation command"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Stop Condition" "Loop blueprint stop condition"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Human Escalation" "Loop blueprint human escalation"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Token / Scope Budget" "Loop blueprint token budget"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "RequiresUserConfirmation: yes" "Loop blueprint comprehension check"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WritebackTarget:" "Loop blueprint output writeback"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "agent_mode:" "Loop blueprint agent mode"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "native_agent_status:" "Loop blueprint native status"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "native_agent_lifecycle:" "Loop blueprint native lifecycle"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "agent_invocation_observed:" "Loop blueprint agent invocation"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "fallback_reason:" "Loop blueprint fallback reason"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "OperationMode: dry-run `| one-step `| continue `| stop-handoff" "Loop blueprint operation mode"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "LoopMode: one-step `| bounded-auto `| review-only" "Loop blueprint loop mode"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "AuthorizationScope:" "Loop blueprint authorization scope"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "AgentModeRequired: native `| fallback-allowed `| any" "Loop blueprint agent mode required"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "AllowedStages:" "Loop blueprint allowed stages"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxRounds:" "Loop blueprint max rounds"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxStageCount:" "Loop blueprint max stage count"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxFixAttempts:" "Loop blueprint max fix attempts"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxFilesRead:" "Loop blueprint max files read"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxFilesChanged:" "Loop blueprint max files changed"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "MaxCommands:" "Loop blueprint max commands"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "ForbiddenActions:" "Loop blueprint forbidden actions"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "StopConditions:" "Loop blueprint stop conditions"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "CheckpointWriteback:" "Loop blueprint checkpoint writeback"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "FinalHandoffRequired: yes" "Loop blueprint final handoff"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "RequiresUserConfirmation: yes" "Loop blueprint user confirmation"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WritebackTarget:" "Loop blueprint writeback target"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "StopOnUnclearScope: yes" "Loop blueprint unclear scope stop"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "StopOnValidationFailure: yes" "Loop blueprint validation stop"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "OperationMode:" "Loop blueprint operation fields boundary"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WorktreeStrategy:" "Loop blueprint worktree strategy section"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WorktreeStrategy: none `| optional `| required" "Loop blueprint worktree strategy"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WorktreePath:" "Loop blueprint worktree path"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WorktreeBranch:" "Loop blueprint worktree branch"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "IsolationReason:" "Loop blueprint isolation reason"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "CleanupRule:" "Loop blueprint cleanup rule"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "WorktreePath:" "Loop blueprint worktree no automation boundary"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Loop Dry Run" "Loop operations default off"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "loop runner" "Loop operations no runner boundary"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop Dry Run" "Loop operations dry run"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop One Step" "Loop operations one step"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop Bounded Auto" "Loop operations bounded auto"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop Review Only" "Loop operations review only"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop Continue" "Loop operations continue"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "## Loop Stop / Handoff" "Loop operations stop handoff"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Loop Dry Run" "Loop dry-run no modification"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Loop One Step" "Loop one-step one round"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "Loop Continue" "Loop continue one round"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "State File" "Loop operations writeback"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "agent_mode:" "Loop operations agent mode"
    Test-RequiredPattern "project-template\docs\loop-operations.md" "native-only" "Loop operations native-only stop"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "LoopMode" "Bounded auto policy loop mode"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "AgentModeRequired" "Bounded auto policy agent mode"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Stop Conditions" "Bounded auto policy stop conditions"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Checkpoint Writeback" "Bounded auto policy checkpoint"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Final Handoff" "Bounded auto policy handoff"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "ManagedDocsWriteback: off `| minimal `| full-review" "Managed docs writeback modes"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Implementation Scope" "Implementation scope boundary"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Governance Writeback Scope" "Governance writeback scope boundary"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "只改这些业务文件" "Business file scope does not disable writeback"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "``review-only`` 绝不写文件" "Review-only no writeback"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "report-only 脚本仍然只生成报告" "Report-only no automatic fixes"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "实现完成 / 阶段收口 / 版本推进" "Workflow router completion writeback"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "ManagedDocsWriteback: minimal" "Responsibility matrix minimal writeback"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "不是 runner、daemon、cron、scheduler、多 agent dispatcher、自动 PR 或 worktree orchestration" "Bounded auto no runner boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" 'native_agent_lifecycle: generated | installed | registered | invoked' "Native adapter runtime lifecycle boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" 'native_agent_status` 合法值只允许 `available | unavailable | unverified`' "Native adapter status value boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "只有 ``invoked`` 才能写成 native 真正可用" "Native adapter invoked-only boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "子 agent 可以报告" "Native adapter child agent boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "容量阻塞" "Native adapter capacity blocked boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "Native Agent Verification Checklist" "Native adapter verification checklist"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "check-codex-native-agents.py" "Native adapter Codex doctor"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "FallbackPolicy: fallback is downgrade mode, not native success" "Native adapter fallback boundary"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "native-only verification 默认只读" "Native adapter native-only read-only"
    Test-RequiredPattern "project-template\docs\native-agent-adapter.md" "不得把 fallback 或 simulated 结果描述为 native agent 成功" "Native adapter no false native claim"
    Test-RequiredPattern "native-adapters\claude-code\skills\forgekit-loop\SKILL.md" "agent_mode=fallback" "Native adapter skill fallback record"
    Test-RequiredPattern "native-adapters\claude-code\skills\forgekit-loop\SKILL.md" "Only invoked can be called native available." "Native adapter skill invoked-only boundary"
    Test-RequiredPattern "native-adapters\claude-code\skills\forgekit-loop\SKILL.md" "Keep native_agent_status limited to available, unavailable, or unverified." "Native adapter skill status boundary"
    Test-RequiredPattern "native-adapters\claude-code\skills\forgekit-loop\SKILL.md" "capacity blocked rather than native unavailable" "Native adapter skill capacity boundary"
    Test-RequiredPattern "native-adapters\claude-code\skills\forgekit-loop\SKILL.md" "native-only" "Native adapter skill native-only rule"
    Test-RequiredPattern "project-template\docs\loop-blueprint.md" "Maker / Checker" "Loop blueprint maker checker strategy"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "ready-for-check" "Maker checker protocol boundary"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "manual-review" "Maker checker no scheduler boundary"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "ready-for-check" "Maker phase section"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "manual-review" "Checker phase section"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "agent" "Single agent maker checker rule"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "sub-agent" "Maker checker no automation boundary"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "Worktree" "Maker checker worktree isolation"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "worktree" "Maker checker no automatic worktree"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git worktree" "Worktree playbook title"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "work/<topic>" "Worktree playbook when to use"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git status --short" "Worktree playbook when not to use"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "../<repo-name>-wt/<topic>" "Worktree playbook naming"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git status --short" "Worktree playbook checklist"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git worktree add" "Worktree playbook commands"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "Maker" "Worktree playbook maker checker"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git worktree remove" "Worktree playbook cleanup"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" ".forgekit/docs/" "Worktree playbook safety"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "worktree runner" "Worktree playbook no runner"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "worktree" "Worktree explicit user request"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "git status --short" "Worktree clean status command"
    Test-RequiredPattern "project-template\docs\worktree-playbook.md" "merge" "Worktree no automation"
    Test-RequiredPattern "project-template\changes\_template\review.md" "MakerStatus:" "Review maker summary section"
    Test-RequiredPattern "project-template\changes\_template\review.md" "MakerStatus: ready-for-check `| blocked `| partial" "Review maker status"
    Test-RequiredPattern "project-template\changes\_template\review.md" "FilesChanged:" "Review maker files changed"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ImplementationSummary:" "Review maker implementation summary"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ValidationRun:" "Review maker validation run"
    Test-RequiredPattern "project-template\changes\_template\review.md" "KnownRisks:" "Review maker known risks"
    Test-RequiredPattern "project-template\changes\_template\review.md" "NotVerified:" "Review maker not verified"
    Test-RequiredPattern "project-template\changes\_template\review.md" "CheckerStatus:" "Review checker section"
    Test-RequiredPattern "project-template\changes\_template\review.md" "CheckerStatus: pass `| needs-fix `| manual-review `| not-run" "Review checker status"
    Test-RequiredPattern "project-template\changes\_template\review.md" "DiffReviewed: yes `| no" "Review diff reviewed"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ValidationReviewed: yes `| no" "Review validation reviewed"
    Test-RequiredPattern "project-template\changes\_template\review.md" "DocsReviewed: yes `| no" "Review docs reviewed"
    Test-RequiredPattern "project-template\changes\_template\review.md" "RisksReviewed: yes `| no" "Review risks reviewed"
    Test-RequiredPattern "project-template\changes\_template\review.md" "FinalRecommendation:" "Review final recommendation"
    Test-RequiredPattern "project-template\AGENTS.md" "A loop must have a state file, validation command, stop condition, and human escalation path" "AGENTS loop short rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "A loop must have a state file, validation command, stop condition, and human escalation path" "CLAUDE loop short rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "loop" "Rules loop short rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Do not enter loop mode unless the user explicitly asks for loop dry-run, one-step, bounded-auto, review-only, continue, or stop/handoff." "AGENTS loop operation trigger rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Do not enter loop mode unless the user explicitly asks for loop dry-run, one-step, bounded-auto, review-only, continue, or stop/handoff." "CLAUDE loop operation trigger rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Bounded-auto must stop" "AGENTS bounded auto stop rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Bounded-auto must stop" "CLAUDE bounded auto stop rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "bounded-auto 遇到范围不清" "Rules bounded auto stop rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "loop mode" "Rules loop operation trigger rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Loop continue must not run continuously" "AGENTS loop continue rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Loop continue must not run continuously" "CLAUDE loop continue rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "loop continue" "Rules loop continue rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Loop output must write back" "AGENTS loop writeback rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Loop output must write back" "CLAUDE loop writeback rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "work-log.md" "Rules loop writeback rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Implementation Scope from Governance Writeback Scope" "AGENTS writeback scope separation"
    Test-RequiredPattern "project-template\CLAUDE.md" "Implementation Scope from Governance Writeback Scope" "CLAUDE writeback scope separation"
    Test-RequiredPattern "project-template\.codex\rules.md" "ManagedDocsWriteback: minimal" "Rules minimal writeback"
    Test-RequiredPattern "project-template\AGENTS.md" "Generated native agent config is not proof of runtime registration" "AGENTS native adapter runtime boundary"
    Test-RequiredPattern "project-template\CLAUDE.md" "Generated native agent config is not proof of runtime registration" "CLAUDE native adapter runtime boundary"
    Test-RequiredPattern "project-template\.codex\rules.md" "生成 native agent 配置不等于 runtime 已注册" "Rules native adapter runtime boundary"
    Test-RequiredPattern "project-template\.codex\rules.md" "agent_mode" "Rules loop agent mode record"
    Test-RequiredPattern "project-template\AGENTS.md" "Medium or high risk code changes should separate Maker phase and Checker phase" "AGENTS maker checker short rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Medium or high risk code changes should separate Maker phase and Checker phase" "CLAUDE maker checker short rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "Maker phase" "Rules maker checker short rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Checker should not expand scope or implement new features unless the user explicitly asks" "AGENTS checker scope rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Checker should not expand scope or implement new features unless the user explicitly asks" "CLAUDE checker scope rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "Checker" "Rules checker scope rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Do not create a worktree unless the user explicitly asks." "AGENTS worktree explicit rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Do not create a worktree unless the user explicitly asks." "CLAUDE worktree explicit rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "worktree" "Rules worktree explicit rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Before creating a worktree, confirm ``git status --short`` is clean" "AGENTS worktree clean status rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Before creating a worktree, confirm ``git status --short`` is clean" "CLAUDE worktree clean status rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "git status --short" "Rules worktree clean status rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Do not automatically merge, push, delete branches, remove worktrees, create PRs, start agents, or schedule worktree tasks." "AGENTS worktree no automation rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Do not automatically merge, push, delete branches, remove worktrees, create PRs, start agents, or schedule worktree tasks." "CLAUDE worktree no automation rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "push" "Rules worktree no automation rule"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "maker-checker-protocol.md" "Document responsibility maker checker"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "loop-operations.md" "Document responsibility loop operations"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "native-agent-adapter.md" "Document responsibility native agent adapter"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "worktree-playbook.md" "Document responsibility worktree playbook"
    Test-RequiredPattern "project-template\docs\codebase-map.md" "ForgeKit" "Codebase map managed docs entry"
    Test-RequiredPattern "project-template\docs\codebase-map.md" ".forgekit/docs/" "Codebase map avoids full docs loading"
    Test-RequiredPattern "README.md" "Independent Code Review Protocol" "Root README current review capability"
    Test-RequiredPattern "README.en.md" "Independent Code Review Protocol" "English README current review capability"
    Test-RequiredPattern "usage.html" "maker-checker-protocol.md" "Usage maker checker docs"
    Test-RequiredPattern "usage.html" "loop-operations.md" "Usage loop operations docs"
    Test-RequiredPattern "usage.html" "worktree-playbook.md" "Usage worktree playbook docs"
    if (Test-Path -LiteralPath (Join-Path $repoRoot "scripts\maker-checker-runner.py")) {
        Add-Error "v0.26 must not add automatic maker/checker runner"
    }
    if (Test-Path -LiteralPath (Join-Path $repoRoot "project-template\scripts\maker-checker-runner.py")) {
        Add-Error "v0.26 must not add generated automatic maker/checker runner"
    }
    if (Test-Path -LiteralPath (Join-Path $repoRoot "project-template\.codex\agents\maker.md")) {
        Add-Error "v0.26 must not add maker sub-agent config"
    }
    if (Test-Path -LiteralPath (Join-Path $repoRoot "project-template\.codex\agents\checker.md")) {
        Add-Error "v0.26 must not add checker sub-agent config"
    }
    foreach ($forbiddenLoopPath in @(
        "scripts\loop-runner.py",
        "project-template\scripts\loop-runner.py",
        "scripts\loop-daemon.py",
        "project-template\scripts\loop-daemon.py",
        "scripts\loop-scheduler.py",
        "project-template\scripts\loop-scheduler.py",
        "project-template\.codex\agents\loop-runner.md",
        "scripts\worktree-runner.py",
        "project-template\scripts\worktree-runner.py",
        "scripts\worktree-scheduler.py",
        "project-template\scripts\worktree-scheduler.py",
        "scripts\worktree-agent.py",
        "project-template\scripts\worktree-agent.py",
        "project-template\.codex\agents\worktree-runner.md"
    )) {
        if (Test-Path -LiteralPath (Join-Path $repoRoot $forbiddenLoopPath)) {
            Add-Error "v0.28 must not add loop/worktree runner, daemon, scheduler, or sub-agent config: $forbiddenLoopPath"
        }
    }
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" "Status: metadata" "PowerShell change status check"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" "Change is done and may be archived" "PowerShell done archive warning"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" "Change is done and may be archived" "Bash done archive warning"
}

function Test-TemplateManifest {
    Test-RequiredPath "project-template\.forgekit\template-manifest.json"
    Test-RequiredPath "scripts\update-template-manifest.py"
    $manifestPath = Join-Path $repoRoot "project-template\.forgekit\template-manifest.json"
    if (Test-Path -LiteralPath $manifestPath) {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ($manifest.template_version -ne "0.40.1") {
            Add-Error "Unexpected template manifest version: $($manifest.template_version)"
        }
        $sources = @($manifest.files | ForEach-Object { $_.source_path })
        if ($sources -contains ".forgekit/template-manifest.json") {
            Add-Error "template-manifest.json must not list itself"
        }
        if ($sources -contains ".forgekit/archive-plan.md") {
            Add-Error "archive-plan.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/archive-capsule-plan.md") {
            Add-Error "archive-capsule-plan.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/archive-apply-report.md") {
            Add-Error "archive-apply-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/archive-reference-report.md") {
            Add-Error "archive-reference-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/current-docs-sync-report.md") {
            Add-Error "current-docs-sync-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/smart-archive-report.md") {
            Add-Error "smart-archive-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/smart-archive-apply-report.md") {
            Add-Error "smart-archive-apply-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/state.json") {
            Add-Error "state.json is runtime migration state and must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/codex-native-agent-report.md") {
            Add-Error "codex-native-agent-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/doc-health-report.md") {
            Add-Error "doc-health-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/source-trace-report.md") {
            Add-Error "source-trace-report.md must not be listed in template manifest"
        }
        if ($sources -contains ".forgekit/handoff-package.md") {
            Add-Error "handoff-package.md must not be listed in template manifest"
        }
        foreach ($item in $manifest.files) {
            if ($item.source_path -like "*handoff-package.md" -or $item.target_path -like "*handoff-package.md" -or $item.target_path -like "*handoff.md") {
                Add-Error "generated handoff reports must not be listed in template manifest"
            }
        }
        if ($sources -notcontains "scripts/doc-health-report.py") {
            Add-Error "doc-health-report.py script must be listed in template manifest"
        }
        if ($sources -notcontains "scripts/source-trace-report.py") {
            Add-Error "source-trace-report.py script must be listed in template manifest"
        }
        if ($sources -notcontains "scripts/handoff-package.py") {
            Add-Error "handoff-package.py script must be listed in template manifest"
        }
        if ($sources -notcontains "scripts/forgekit-upgrade.py") {
            Add-Error "forgekit-upgrade.py script must be listed in template manifest"
        }
        if ($sources -notcontains "scripts/archive-capsule.py") {
            Add-Error "archive-capsule.py script must be listed in template manifest"
        }
        foreach ($source in @("docs/project-maintenance.md", "docs/archive-capsule.md", ".claude/skills/forgekit-maintenance/SKILL.md", "migrations/0.39.0/migration.json")) {
            if ($sources -notcontains $source) { Add-Error "Project maintenance template missing from manifest: $source" }
        }
        if ($sources -notcontains "migrations/0.36.0/migration.json") {
            Add-Error "v0.36.0 migration descriptor must be listed in template manifest"
        }
        $dollarSign = [string][char]36
        $managedDocsRootPattern = $dollarSign + "{managed_docs_root}/*"
        $changeRootPattern = $dollarSign + "{change_root}/*"
        foreach ($item in $manifest.files) {
            if ($item.update_policy -notin @("replace", "merge", "ask", "readonly")) {
                Add-Error "Invalid update_policy in template manifest: $($item.source_path)"
            }
            if ($item.render_mode -notin @("copy", "render")) {
                Add-Error "Invalid render_mode in template manifest: $($item.source_path)"
            }
            if ($item.source_path -like "docs/*" -and $item.target_path -notlike $managedDocsRootPattern) {
                Add-Error "docs source must target managed_docs_root in manifest: $($item.source_path)"
            }
            if ($item.source_path -like "changes/*" -and $item.target_path -notlike $changeRootPattern) {
                Add-Error "changes source must target change_root in manifest: $($item.source_path)"
            }
            if ($item.source_path -like ".forgekit/archive/changes/*/*" -or $item.source_path -like ".forgekit/archive/releases/*/*") {
                Add-Error "User archive history must not be listed in template manifest: $($item.source_path)"
            }
        }
    }

    $result = & python (Join-Path $repoRoot "scripts\update-template-manifest.py") --check 2>&1
    if ($LASTEXITCODE -ne 0) {
        Add-Error "Template manifest checksum check failed: $result"
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
    Test-RequiredPattern "usage.html" "data-prompt=""large""" "HTML large-change tab"

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
    Test-RequiredPattern "project-template\.codex\config.example.toml" "[forgekit.native_agents]" "Codex native agent config example"
    Test-RequiredPattern "project-template\.codex\config.example.toml" 'implementer = "not-generated"' "Codex native adapter no implementer"
    Test-RequiredPath "project-template\.codex\config.toml"
    Test-RequiredPattern "project-template\.codex\config.toml" "[agents]" "Codex project agents config"
    Test-RequiredPattern "project-template\.codex\config.toml" "max_threads" "Codex project agents max_threads"
    Test-RequiredPattern "project-template\.codex\config.toml" "max_depth" "Codex project agents max_depth"
    Test-RequiredPath "project-template\.codex\agents\forgekit-planner.toml"
    Test-RequiredPath "project-template\.codex\agents\forgekit-reviewer.toml"
    Test-RequiredPath "project-template\.codex\agents\forgekit-verifier.toml"
    foreach ($agentName in @("forgekit-planner", "forgekit-reviewer", "forgekit-verifier")) {
        $agentPath = "project-template\.codex\agents\$agentName.toml"
        Test-RequiredPattern $agentPath "name = `"$agentName`"" "$agentName name"
        Test-RequiredPattern $agentPath "description =" "$agentName description"
        Test-RequiredPattern $agentPath 'developer_instructions = """' "$agentName developer instructions string"
        Test-NoPattern $agentPath "[developer_instructions]" "$agentName developer_instructions table"
        Test-NoPattern $agentPath "developer_instructions = {" "$agentName developer_instructions inline map"
        $nativeAdapterPath = "native-adapters\codex\agents\$agentName.toml"
        Test-RequiredPath $nativeAdapterPath
        Test-RequiredPattern $nativeAdapterPath "name = `"$agentName`"" "$agentName native adapter name"
        Test-RequiredPattern $nativeAdapterPath "description =" "$agentName native adapter description"
        Test-RequiredPattern $nativeAdapterPath 'developer_instructions = """' "$agentName native adapter developer instructions string"
        Test-NoPattern $nativeAdapterPath "[developer_instructions]" "$agentName native adapter developer_instructions table"
        Test-NoPattern $nativeAdapterPath "developer_instructions = {" "$agentName native adapter developer_instructions inline map"
    }
    Test-RequiredPath "scripts\check-codex-native-agents.py"
    Test-RequiredPath "project-template\scripts\check-codex-native-agents.py"
    Test-RequiredPattern "scripts\check-codex-native-agents.py" "Schema pass does not mean runtime registered." "Codex native doctor runtime boundary"
    Test-RequiredPattern "project-template\scripts\check-codex-native-agents.py" "NativeAgentStatus: {native_status}" "Codex native doctor status output"
    Test-RequiredPattern "project-template\scripts\check-codex-native-agents.py" "NativeAgentLifecycle: {native_lifecycle}" "Codex native doctor lifecycle output"
    Test-RequiredPattern "project-template\scripts\check-codex-native-agents.py" "NativeAgentStatusAllowed: available | unavailable | unverified" "Codex native doctor status values"
    Test-RequiredPattern "project-template\scripts\check-codex-native-agents.py" "must be string" "Codex native doctor type validation"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/codex-native-agent-report.md" "PowerShell Codex native report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/codex-native-agent-report.md" "Bash Codex native report exclusion"
    Test-RequiredPattern "scripts\generate-native-agent-adapter.py" "present" "Native adapter generator present status"
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
    Test-RequiredPattern "usage.html" "suitabilityList" "HTML suitability checklist"
    Test-RequiredPattern "usage.html" "selectedSuitability()" "HTML suitability brief"
}

function Test-ExecutableHarness {
    Test-RequiredPath "project-template\scripts\detect-local-toolchain.ps1"
    Test-RequiredPath "project-template\scripts\run-harness-check.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.ps1"
    Test-RequiredPath "project-template\scripts\check-doc-sync.sh"
    Test-RequiredPath "project-template\scripts\archive-changes.py"
    Test-RequiredPath "project-template\scripts\doc-health-report.py"
    Test-RequiredPath "scripts\doc-health-report.py"
    Test-RequiredPath "project-template\scripts\source-trace-report.py"
    Test-RequiredPath "scripts\source-trace-report.py"
    Test-RequiredPath "project-template\scripts\handoff-package.py"
    Test-RequiredPath "scripts\handoff-package.py"
    Test-RequiredPath "project-template\scripts\install-hooks.ps1"
    Test-RequiredPath "project-template\scripts\install-hooks.sh"
    Test-RequiredPath (Get-CodexNextWorkOrderPath)
    Test-RequiredPattern "project-template\scripts\detect-local-toolchain.ps1" "Do not install missing tools" "Toolchain detector safety guard"
    Test-RequiredPattern "project-template\scripts\run-harness-check.ps1" "Harness check passed" "Harness check success output"
    Test-RequiredPattern "project-template\.codex\commands.md" "detect-local-toolchain.ps1" "Commands toolchain detector"
    Test-RequiredPattern "project-template\.codex\commands.md" "run-harness-check.ps1" "Commands harness check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.ps1" "Commands document sync check"
    Test-RequiredPattern "project-template\.codex\commands.md" "check-doc-sync.sh" "Commands document sync check bash"
    Test-RequiredPattern "project-template\.codex\commands.md" "archive-changes.py --dry-run" "Commands archive dry-run"
    Test-RequiredPattern "project-template\.codex\commands.md" "archive-changes.py --reference-check" "Commands archive reference check"
    Test-RequiredPattern "project-template\.codex\commands.md" "archive-changes.py --sync-check" "Commands current docs sync check"
    Test-RequiredPattern "project-template\.codex\commands.md" "archive-changes.py --smart-check" "Commands smart archive check"
    Test-RequiredPattern "project-template\.codex\commands.md" "archive-changes.py --smart-apply" "Commands smart archive apply"
    Test-RequiredPattern "project-template\.codex\commands.md" "doc-health-report.py" "Commands doc health report"
    Test-RequiredPattern "project-template\.codex\commands.md" ".forgekit/doc-health-report.md" "Commands doc health output"
    Test-RequiredPattern "project-template\.codex\commands.md" "source-trace-report.py" "Commands source trace report"
    Test-RequiredPattern "project-template\.codex\commands.md" ".forgekit/source-trace-report.md" "Commands source trace output"
    Test-RequiredPattern "project-template\.codex\commands.md" "handoff-package.py" "Commands handoff package"
    Test-RequiredPattern "project-template\.codex\commands.md" ".forgekit/handoff-package.md" "Commands handoff output"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.ps1" "Commands hook installer"
    Test-RequiredPattern "project-template\.codex\commands.md" "install-hooks.sh" "Commands hook installer bash"
    Test-RequiredPattern "project-template\.codex\commands-catalog.md" "detect-local-toolchain" "Commands catalog toolchain detector"
    Test-RequiredPattern "project-template\.codex\hooks.md" "run-harness-check.ps1" "Hooks harness check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.ps1" "Hooks document sync check"
    Test-RequiredPattern "project-template\.codex\hooks.md" "check-doc-sync.sh" "Hooks document sync check bash"
    Test-RequiredPattern "project-template\.codex\hooks.md" "install-hooks.sh" "Hooks installer bash"
    Test-RequiredPattern (Get-LocalToolchainPath) "detect-local-toolchain.ps1" "Local toolchain executable detector reference"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "--confirm" "Archive script apply confirmation"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "Git working tree must be clean except the selected" "Archive script clean git guard"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "Archive-Status" "Archive script machine-readable plan"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "archive-apply-report.md" "Archive script apply report"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "--reference-check" "Archive script reference check"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "--sync-check" "Archive script sync check"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "--smart-check" "Archive script smart check"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "--smart-apply" "Archive script smart apply"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "smart-archive-apply-report.md" "Smart archive apply report"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "Reference-Status" "Archive reference report machine-readable field"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "Sync-Status" "Current docs sync report machine-readable field"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "current-docs-sync-report.md" "Current docs sync report output"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "smart-archive-report.md" "Smart archive report output"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "Smart-Status" "Smart archive report machine-readable field"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "string-match only" "Archive reference report string-match disclaimer"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "archive-plan.md" "Archive script plan output"
    Test-RequiredPattern "project-template\scripts\archive-changes.py" "change_root:" "Archive script boundary change_root"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "Status: report-only" "Doc health report-only status"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "Mode: doc-health" "Doc health mode"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "Findings by Severity" "Doc health severity section"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "Findings by Document" "Doc health document section"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "Suggested Manual Fixes" "Doc health manual fixes"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "No automatic doc slimming" "Doc health no auto slimming"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "workflow-router.md" "Doc health router boundary"
    Test-RequiredPattern "project-template\scripts\doc-health-report.py" "doc-health-report.md is listed in template manifest" "Doc health manifest guard"
    Test-RequiredPattern "scripts\doc-health-report.py" "Status: report-only" "Root doc health report-only status"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Status: report-only" "Source trace report-only status"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Mode: source-trace" "Source trace mode"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Trace Chain Overview" "Source trace chain overview"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Findings by Trace Stage" "Source trace stage findings"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Orphan Records" "Source trace orphan records"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "Status Consistency" "Source trace status consistency"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "No automatic Source ID creation" "Source trace no auto source ID"
    Test-RequiredPattern "project-template\scripts\source-trace-report.py" "source-trace-report.md is listed in template manifest" "Source trace manifest guard"
    Test-RequiredPattern "scripts\source-trace-report.py" "Status: report-only" "Root source trace report-only status"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Status: report-only" "Handoff package report-only status"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Mode: handoff-package" "Handoff package mode"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Source / Requirement Trace" "Handoff package trace section"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "What Changed" "Handoff package changed section"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Verification Evidence" "Handoff package verification section"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Doc Health / Source Trace Status" "Handoff package report reuse"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "Human Review Checklist" "Handoff package review checklist"
    Test-RequiredPattern "project-template\scripts\handoff-package.py" "must not trigger automatic fixes" "Handoff package report-only notice"
    Test-RequiredPattern "scripts\handoff-package.py" "Status: report-only" "Root handoff package report-only status"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/archive-plan.md" "PowerShell archive plan exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/archive-apply-report.md" "PowerShell archive apply report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/archive-reference-report.md" "PowerShell archive reference report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/current-docs-sync-report.md" "PowerShell current docs sync report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/smart-archive-report.md" "PowerShell smart archive report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/smart-archive-apply-report.md" "PowerShell smart archive apply report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/doc-health-report.md" "PowerShell doc health report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/source-trace-report.md" "PowerShell source trace report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/handoff-package.md" "PowerShell handoff package exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.ps1" ".forgekit/upgrade/*" "PowerShell guided upgrade exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/archive-plan.md" "Bash archive plan exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/archive-apply-report.md" "Bash archive apply report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/archive-reference-report.md" "Bash archive reference report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/current-docs-sync-report.md" "Bash current docs sync report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/smart-archive-report.md" "Bash smart archive report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/smart-archive-apply-report.md" "Bash smart archive apply report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/doc-health-report.md" "Bash doc health report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/source-trace-report.md" "Bash source trace report exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/handoff-package.md" "Bash handoff package exclusion"
    Test-RequiredPattern "project-template\scripts\check-doc-sync.sh" ".forgekit/upgrade/" "Bash guided upgrade exclusion"

    $rootDocHealth = Get-Content -LiteralPath (Join-Path $repoRoot "scripts\doc-health-report.py") -Raw
    $templateDocHealth = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\scripts\doc-health-report.py") -Raw
    if ($rootDocHealth -ne $templateDocHealth) {
        Add-Error "Root and project-template doc-health-report.py must stay identical"
    }
    $rootSourceTrace = Get-Content -LiteralPath (Join-Path $repoRoot "scripts\source-trace-report.py") -Raw
    $templateSourceTrace = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\scripts\source-trace-report.py") -Raw
    if ($rootSourceTrace -ne $templateSourceTrace) {
        Add-Error "Root and project-template source-trace-report.py must stay identical"
    }
    $rootHandoff = Get-Content -LiteralPath (Join-Path $repoRoot "scripts\handoff-package.py") -Raw
    $templateHandoff = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\scripts\handoff-package.py") -Raw
    if ($rootHandoff -ne $templateHandoff) {
        Add-Error "Root and project-template handoff-package.py must stay identical"
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

function Test-NoForgeKitHistoryInTemplate {
    $templateMaturity = ([char]0x6A21).ToString() + ([char]0x677F).ToString() + ([char]0x6210).ToString() + ([char]0x719F).ToString() + ([char]0x5EA6).ToString() + ([char]0x6539).ToString() + ([char]0x8FDB).ToString() + ([char]0x6E05).ToString() + ([char]0x5355).ToString()
    $governanceRoadmap = ([char]0x6CBB).ToString() + ([char]0x7406).ToString() + ([char]0x6539).ToString() + ([char]0x8FDB).ToString() + ([char]0x8DEF).ToString() + ([char]0x7EBF).ToString() + ([char]0x56FE).ToString()
    $usageHtml = ([char]0x4F7F).ToString() + ([char]0x7528).ToString() + ([char]0x8BF4).ToString() + ([char]0x660E).ToString() + ".html"
    $patterns = @(
        "FEAT-HARNESS",
        "TASK-HARNESS",
        "DEBT-HARNESS",
        "MAT-",
        "v0.3-agent-harness-roadmap",
        $templateMaturity,
        $governanceRoadmap,
        $usageHtml
    )
    $files = Get-ChildItem -LiteralPath $projectTemplate -Recurse -File -Include *.md,*.ps1,*.sh
    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
        foreach ($pattern in $patterns) {
            $matches = Select-String -Path $file.FullName -Pattern $pattern -SimpleMatch
            foreach ($match in $matches) {
                Add-Error "ForgeKit internal history leaked into generated template: ${relativePath}:$($match.LineNumber) contains $pattern"
            }
        }
    }
}

function Test-HarnessEntryConsistency {
    $codebaseMapRef = Get-CodebaseMapRef
    Test-RequiredPattern "README.md" "## 快速开始" "Root README quick start"
    Test-RequiredPattern "README.md" "## 核心能力" "Root README current capabilities"
    Test-RequiredPattern "README.md" "CHANGELOG.md" "Root README changelog link"
    Test-RequiredPattern "README.en.md" "CHANGELOG.md" "English README changelog link"
    Test-RequiredPattern "project-template\README.md" ".codex-plugin" "Template README unified plugin note"
    Test-RequiredPattern "project-template\README.md" "CLAUDE.md" "Template README Claude entry"
    Test-RequiredPattern "project-template\README.md" ".agents/skills/<skill>/SKILL.md" "Template README project-local skill resolution"
    Test-RequiredPattern "project-template\README.md" $codebaseMapRef "Template README codebase map reference"
    Test-RequiredPattern "project-template\.codex\skills.md" ".codex-plugin" "Skills unified plugin note"
    Test-RequiredPattern "project-template\.agents\skills\README.md" ".codex-plugin" "Skill README unified plugin note"
    Test-RequiredPattern "scripts\init-project-template.ps1" "CLAUDE.md" "Init script Claude startup guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" ".agents/skills/project-init/SKILL.md" "PowerShell init project-local startup skill"
    Test-RequiredPattern "scripts\init-project-template.ps1" "[ValidateSet(""Lite"", ""Standard"", ""Enterprise"")]" "Init script mode parameter"
    Test-RequiredPattern "scripts\init-project-template.ps1" "NativeAgentAdapter" "Init script native adapter parameter"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Invoke-NativeAgentAdapterGeneration" "Init script native adapter generation"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Write-ForgeKitState" "PowerShell init versioned migration state"
    Test-RequiredPattern "scripts\init-project-template.ps1" "StackSelection: deferred" "Init script deferred stack guidance"
    Test-RequiredPattern "scripts\init-project-template.ps1" "Upgrade" "Init script upgrade mode"
    Test-RequiredPattern "scripts\init-project-template.ps1" "upgrade-report.md" "Init script upgrade report"
    Test-RequiredPattern "scripts\init-project-template.ps1" "ExportUpgradeTemplates" "Init script export upgrade templates"
    Test-RequiredPattern "scripts\init-project-template.sh" "--upgrade" "Bash init upgrade mode"
    Test-RequiredPattern "scripts\init-project-template.sh" "--native-agent-adapter" "Bash init native adapter parameter"
    Test-RequiredPattern "scripts\init-project-template.sh" "generate_native_agent_adapter" "Bash init native adapter generation"
    Test-RequiredPattern "scripts\init-project-template.sh" "write_forgekit_state" "Bash init versioned migration state"
    Test-RequiredPattern "scripts\init-project-template.sh" ".agents/skills/project-init/SKILL.md" "Bash init project-local startup skill"
    Test-RequiredPattern "scripts\init-project-template.sh" "upgrade-report.md" "Bash init upgrade report"
    Test-RequiredPattern "scripts\init-project-template.sh" "--export-upgrade-templates" "Bash init export upgrade templates"
    Test-RequiredPath "scripts\upgrade-forgekit.py"
    Test-RequiredPath "scripts\upgrade-forgekit.ps1"
    Test-RequiredPath "scripts\upgrade-forgekit.sh"
    Test-RequiredPattern "scripts\upgrade-forgekit.py" "guided-upgrade" "Guided upgrade mode"
    Test-RequiredPattern "scripts\upgrade-forgekit.py" "upgrade-plan.md" "Guided upgrade plan"
    Test-RequiredPattern "scripts\upgrade-forgekit.py" "upgrade-actions.md" "Guided upgrade actions"
    Test-RequiredPattern "scripts\upgrade-forgekit.py" "legacy-inventory.md" "Guided upgrade legacy inventory"
    Test-RequiredPattern "scripts\upgrade-forgekit.py" "[legacy]" "Guided upgrade legacy warning"
    Test-RequiredPath "scripts\forgekit-upgrade.py"
    Test-RequiredPath "project-template\scripts\forgekit-upgrade.py"
    Test-RequiredPath "migrations\0.36.0\migration.json"
    Test-RequiredPath "project-template\migrations\0.36.0\migration.json"
    Test-RequiredPath "project-template\.forgekit\state.json"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"schema_version": 1' "State schema version"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"forgekit_version": "0.40.1"' "State ForgeKit version"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"managed_docs_root": ".forgekit/docs"' "State managed docs root"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"change_root": ".forgekit/changes"' "State change root"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"last_upgrade": null' "State last upgrade"
    Test-RequiredPattern "migrations\0.36.0\migration.json" '"actions": []' "Migration actions"
    Test-RequiredPattern "scripts\forgekit-upgrade.py" "Status: adoption-required" "Upgrade adoption guidance"
    Test-RequiredPattern "scripts\forgekit-upgrade.py" "apply requires --safe" "Upgrade safe apply gate"
    Test-RequiredPattern "scripts\forgekit-upgrade.py" "Status: report-only" "Upgrade plan report-only status"
    Test-NoPattern "scripts\forgekit-upgrade.py" "candidates" "New upgrade model must not export candidates"
    Test-NoPattern "scripts\forgekit-upgrade.py" "upgrade-export" "New upgrade model must not use upgrade-export"
    Test-RequiredPattern "README.md" "forgekit-upgrade.py check" "Root README versioned upgrade check"
    Test-RequiredPattern "README.md" "v0.35.x" "Root README pre-v0.36 adoption"
    Test-RequiredPattern "README.md" ".agents/skills/project-init/SKILL.md" "Root README project-local startup skill"
    Test-RequiredPattern "README.md" "-NativeAgentAdapter all" "Root README init native adapter example"
    Test-RequiredPattern "README.en.md" "forgekit-upgrade.py check" "English README versioned upgrade check"
    Test-RequiredPattern "README.en.md" "v0.35.x" "English README pre-v0.36 adoption"
    Test-RequiredPattern "README.en.md" ".agents/skills/project-init/SKILL.md" "English README project-local startup skill"
    Test-RequiredPattern "README.en.md" "-NativeAgentAdapter all" "English README init native adapter example"
    Test-RequiredPattern "usage.html" "startupOutput" "HTML startup output"
    Test-RequiredPattern "usage.html" ".agents/skills/project-init/SKILL.md" "HTML project-local startup skill"
    Test-RequiredPattern "usage.html" "governance/agent-harness.md" "HTML harness prompt reference"
    Test-RequiredPattern "usage.html" "apply --safe" "HTML versioned upgrade entry"

    $rootUpgrade = Get-Content -LiteralPath (Join-Path $repoRoot "scripts\forgekit-upgrade.py") -Raw
    $templateUpgrade = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\scripts\forgekit-upgrade.py") -Raw
    if ($rootUpgrade -ne $templateUpgrade) {
        Add-Error "Root and project-template forgekit-upgrade.py must stay identical"
    }
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
    if ($codexPluginJson.version -ne "0.40.1") {
        Add-Error "Unexpected Codex plugin version in root plugin.json: $($codexPluginJson.version)"
    }
    if ($codexPluginJson.skills -ne "./skills/") {
        Add-Error "Root Codex plugin skills must be ./skills/"
    }

    $claudePluginJson = Get-Content -LiteralPath (Join-Path $repoRoot ".claude-plugin\plugin.json") -Raw | ConvertFrom-Json
    if ($claudePluginJson.name -ne "forgekit") {
        Add-Error "Unexpected Claude plugin name in root plugin.json: $($claudePluginJson.name)"
    }
    if ($claudePluginJson.version -ne "0.40.1") {
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
    Test-RequiredPattern "project-template\CLAUDE.md" ".agents/skills/<skill>/SKILL.md" "CLAUDE project-local skill resolution"
    Test-RequiredPattern "project-template\.claude\skills\forgekit-project-workflow\SKILL.md" "Discovery State" "Claude thin entry skill"
}

function Test-IndependentCodeReviewProtocol {
    $paths = @(
        "project-template\.claude\agents\forgekit-code-reviewer.md",
        "project-template\.codex\agents\forgekit-code-reviewer.toml",
        "project-template\.claude\skills\forgekit-request-code-review\SKILL.md",
        "project-template\.claude\skills\forgekit-code-review\SKILL.md",
        "project-template\.claude\skills\forgekit-code-review\references\universal-review.md",
        "project-template\.claude\skills\forgekit-code-review\references\security-review.md",
        "project-template\.claude\skills\forgekit-code-review\references\testing-review.md",
        "migrations\0.37.0\migration.json",
        "project-template\migrations\0.37.0\migration.json"
    )
    foreach ($item in $paths) { Test-RequiredPath $item }

    Test-RequiredPattern "project-template\.claude\agents\forgekit-code-reviewer.md" "permissionMode: plan" "Claude code reviewer read-only permission"
    Test-RequiredPattern "project-template\.claude\agents\forgekit-code-reviewer.md" "ReviewDecision" "Claude code reviewer output"
    Test-RequiredPattern "project-template\.codex\agents\forgekit-code-reviewer.toml" 'name = "forgekit-code-reviewer"' "Codex code reviewer name"
    Test-RequiredPattern "project-template\.codex\agents\forgekit-code-reviewer.toml" 'description = "' "Codex code reviewer description string"
    Test-RequiredPattern "project-template\.codex\agents\forgekit-code-reviewer.toml" 'developer_instructions = """' "Codex code reviewer instructions string"
    Test-NoPattern "project-template\.codex\agents\forgekit-code-reviewer.toml" "[developer_instructions]" "Codex code reviewer instructions table"
    Test-RequiredPattern "project-template\.claude\skills\forgekit-request-code-review\SKILL.md" "Do not provide the maker's full conversation history" "Request review context isolation"
    Test-RequiredPattern "project-template\.claude\skills\forgekit-code-review\SKILL.md" "Read-only" "Code review skill read-only"
    Test-RequiredPattern "project-template\.claude\skills\forgekit-code-review\SKILL.md" "needs-fix" "Code review blocking decision"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "self-review" "Self-review distinction"
    Test-RequiredPattern "project-template\docs\maker-checker-protocol.md" "mandatory independent review" "Independent review trigger"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Independent Review Gate" "Bounded-auto independent review gate"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ReviewType: independent | self-review" "Review type field"
    Test-RequiredPattern "project-template\changes\_template\review.md" "ReviewerAgent:" "Reviewer agent field"
    Test-RequiredPattern "scripts\handoff-package.py" "Independent Code Review" "Handoff review evidence"
    Test-RequiredPattern "scripts\check-codex-native-agents.py" "forgekit-code-reviewer" "Codex doctor reviewer coverage"
    Test-RequiredPattern "migrations\0.37.0\migration.json" '"from": "0.36.0"' "v0.37 migration source"
    Test-RequiredPattern "migrations\0.37.0\migration.json" '"to": "0.37.0"' "v0.37 migration target"

    $skillFiles = @(
        "project-template\.claude\skills\forgekit-request-code-review\SKILL.md",
        "project-template\.claude\skills\forgekit-code-review\SKILL.md",
        "project-template\.claude\skills\forgekit-code-review\references\universal-review.md",
        "project-template\.claude\skills\forgekit-code-review\references\security-review.md",
        "project-template\.claude\skills\forgekit-code-review\references\testing-review.md"
    )
    foreach ($relative in $skillFiles) {
        $full = Join-Path $repoRoot $relative
        $bytes = [System.IO.File]::ReadAllBytes($full)
        if ($bytes | Where-Object { $_ -gt 127 }) { Add-Error "Independent review skill must be ASCII-only: $relative" }
        if ((Get-Content -LiteralPath $full).Count -gt 180) { Add-Error "Independent review skill/reference is too large: $relative" }
    }

    $manifest = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\.forgekit\template-manifest.json") -Raw | ConvertFrom-Json
    $sources = @($manifest.files | ForEach-Object { $_.source_path })
    foreach ($source in @(
        ".claude/agents/forgekit-code-reviewer.md",
        ".codex/agents/forgekit-code-reviewer.toml",
        ".claude/skills/forgekit-request-code-review/SKILL.md",
        ".claude/skills/forgekit-code-review/SKILL.md",
        "migrations/0.37.0/migration.json"
    )) {
        if ($sources -notcontains $source) { Add-Error "Independent review template missing from manifest: $source" }
    }
}
function Test-ContextContinuityProtocol {
    Test-RequiredPath "project-template\docs\context-continuity.md"
    Test-RequiredPath "migrations\0.38.0\migration.json"
    Test-RequiredPath "project-template\migrations\0.38.0\migration.json"
    foreach ($heading in @(
        "Critical Facts",
        "Context Checkpoint Triggers",
        "Context Survival Map",
        "Compact / Clear Readiness",
        "Post-Upgrade Session Refresh",
        "Subagent Output Handling",
        "Large Output Handling",
        "Writeback Boundaries"
    )) {
        Test-RequiredPattern "project-template\docs\context-continuity.md" $heading "Context continuity $heading"
    }
    Test-RequiredPattern "project-template\docs\context-continuity.md" "upgrade 后旧会话只用于收口" "Post-upgrade old-session closure rule"
    Test-RequiredPattern "project-template\docs\context-continuity.md" "新任务应新开会话" "Post-upgrade new-session rule"
    Test-RequiredPattern "project-template\docs\context-continuity.md" "不假设当前会话自动加载新规则" "Post-upgrade reload boundary"
    Test-RequiredPattern "project-template\AGENTS.md" "Critical conclusions must not live only in chat" "AGENTS context checkpoint rule"
    Test-RequiredPattern "project-template\AGENTS.md" "After a ForgeKit upgrade" "AGENTS post-upgrade refresh rule"
    Test-RequiredPattern "project-template\AGENTS.md" "Summarize large outputs" "AGENTS large output rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Critical conclusions must not live only in chat" "CLAUDE context checkpoint rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "After a ForgeKit upgrade" "CLAUDE post-upgrade refresh rule"
    Test-RequiredPattern "project-template\CLAUDE.md" "Summarize large outputs" "CLAUDE large output rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "关键结论不能只留在聊天里" "Rules context checkpoint rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "新任务应新开会话" "Rules post-upgrade refresh rule"
    Test-RequiredPattern "project-template\.codex\rules.md" "长工具输出只保留摘要" "Rules large output rule"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "保存关键结论" "Workflow router context intent"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "ForgeKit 升级后继续工作" "Workflow router post-upgrade intent"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "compact" "Workflow router compact route"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "clear" "Workflow router clear route"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "Context Checkpoint" "Bounded-auto context checkpoint"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "不得跨过版本边界" "Bounded-auto post-upgrade stop"
    Test-RequiredPattern "project-template\.forgekit\docs\document-responsibility.md" "context-continuity.md" "Document responsibility context entry"
    Test-RequiredPattern "project-template\docs\codebase-map.md" "context-continuity.md" "Codebase map context entry"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"context_continuity": true' "State context continuity feature"
    Test-RequiredPattern "README.md" "Context Continuity Protocol" "README context continuity entry"
    Test-RequiredPattern "README.en.md" "Context Continuity Protocol" "English README context continuity entry"
    Test-RequiredPattern "project-template\README.md" "context-continuity.md" "Template README context continuity entry"
    Test-RequiredPattern "usage.html" "context-continuity.md" "Usage context continuity entry"
    Test-RequiredPattern "scripts\handoff-package.py" "Context Continuity Check" "Handoff continuity check"
    Test-RequiredPattern "migrations\0.38.0\migration.json" '"from": "0.37.0"' "v0.38 migration source"
    Test-RequiredPattern "migrations\0.38.0\migration.json" '"to": "0.38.0"' "v0.38 migration target"
    foreach ($forbidden in @(
        "scripts\context-continuity-runner.py",
        "project-template\scripts\context-continuity-runner.py",
        "scripts\token-monitor.py",
        "project-template\scripts\token-monitor.py",
        "scripts\auto-compact.py",
        "project-template\scripts\auto-compact.py"
    )) {
        if (Test-Path -LiteralPath (Join-Path $repoRoot $forbidden)) { Add-Error "v0.38 must not add automatic context execution: $forbidden" }
    }
    $manifest = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\.forgekit\template-manifest.json") -Raw | ConvertFrom-Json
    $sources = @($manifest.files | ForEach-Object { $_.source_path })
    foreach ($source in @("docs/context-continuity.md", "migrations/0.38.0/migration.json")) {
        if ($sources -notcontains $source) { Add-Error "Context continuity template missing from manifest: $source" }
    }
}
function Test-ProjectMaintenanceOperations {
    foreach ($path in @(
        "project-template\docs\project-maintenance.md",
        "project-template\docs\archive-capsule.md",
        "project-template\.claude\skills\forgekit-maintenance\SKILL.md",
        "scripts\forgekit-project.py",
        "scripts\forgekit-project.ps1",
        "scripts\forgekit-project.sh",
        "scripts\archive-capsule.py",
        "project-template\scripts\archive-capsule.py",
        "migrations\0.39.0\migration.json",
        "project-template\migrations\0.39.0\migration.json"
    )) { Test-RequiredPath $path }
    foreach ($heading in @("Maintenance Intents", "Unified Project Bootstrap / Install-or-Upgrade Entry", "Upgrade Sync", "Archive Capsule", "Plan before Apply", "Confirmation Rules", "Post-Operation Summary")) {
        Test-RequiredPattern "project-template\docs\project-maintenance.md" $heading "Project maintenance $heading"
    }
    foreach ($heading in @("Archive is not deletion", "Capsule structure", "Archive index", "Archived items log", "Legacy archive handling", "Plan / apply boundary")) {
        Test-RequiredPattern "project-template\docs\archive-capsule.md" $heading "Archive capsule $heading"
    }
    foreach ($intent in @("project-bootstrap", "upgrade-sync", "archive-capsule", "context-checkpoint", "handoff", "doc-health", "source-trace")) {
        Test-RequiredPattern "project-template\.claude\skills\forgekit-maintenance\SKILL.md" $intent "Maintenance skill intent $intent"
    }
    Test-RequiredPattern "scripts\archive-capsule.py" "Status: report-only" "Archive capsule report-only plan"
    Test-RequiredPattern "scripts\archive-capsule.py" "requires --confirm" "Archive capsule confirmation gate"
    Test-RequiredPattern "scripts\archive-capsule.py" "archive-summary.md" "Archive capsule summary"
    Test-RequiredPattern "scripts\archive-capsule.py" "archived-items.md" "Archive capsule items log"
    Test-RequiredPattern "scripts\archive-capsule.py" "archive/index.md" "Archive capsule index output"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "MaintenanceIntent: upgrade-sync" "Workflow router upgrade sync intent"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "MaintenanceIntent: archive-capsule" "Workflow router archive capsule intent"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "MaintenanceIntent: project-bootstrap" "Workflow router unified bootstrap intent"
    Test-RequiredPattern "scripts\forgekit-project.py" "Continue with safe apply? [y/N]:" "Unified upgrade default-No confirmation"
    Test-RequiredPattern "scripts\forgekit-project.py" '"apply", "--safe"' "Unified entry delegates safe apply"
    Test-RequiredPattern "scripts\forgekit-project.py" "Non-interactive session detected" "Unified non-interactive plan-only rule"
    Test-RequiredPattern "scripts\forgekit-project.py" "legacy-adoption" "Unified legacy adoption route"
    Test-RequiredPattern "scripts\forgekit-project.py" "stop-toolkit-too-old" "Unified newer-project stop"
    Test-RequiredPattern "README.md" 'python .\scripts\forgekit-project.py' "Windows unified entry command"
    Test-RequiredPattern "README.md" 'python3 ./scripts/forgekit-project.py' "macOS/Linux unified entry command"
    Test-RequiredPattern "README.md" "forgekit-project.ps1" "PowerShell unified wrapper entry"
    Test-RequiredPattern "README.md" "forgekit-project.sh" "Bash unified wrapper entry"
    Test-RequiredPattern "scripts\forgekit-upgrade.py" "already-present" "Idempotent same-content migration result"
    Test-RequiredPattern "scripts\forgekit-upgrade.py" "skipped-existing-review-needed" "Idempotent different-content migration result"
    Test-NoPattern "project-template\.forgekit\template-manifest.json" '"source_path": "scripts/forgekit-project.py"' "ForgeKitRoot unified entry must not enter project manifest"
    foreach ($entry in @("project-template\AGENTS.md", "project-template\CLAUDE.md", "project-template\.codex\rules.md")) {
        Test-RequiredPattern $entry "MaintenanceIntent" "Maintenance intent entry rule"
        Test-RequiredPattern $entry "归档不是删除" "Archive is not deletion entry rule"
    }
    Test-RequiredPattern "project-template\.forgekit\state.json" '"project_maintenance_operations": true' "State project maintenance feature"
    Test-RequiredPattern "migrations\0.39.0\migration.json" '"from": "0.38.0"' "v0.39 migration source"
    Test-RequiredPattern "migrations\0.39.0\migration.json" '"to": "0.39.0"' "v0.39 migration target"
    $rootCapsule = Get-Content -LiteralPath (Join-Path $repoRoot "scripts\archive-capsule.py") -Raw
    $templateCapsule = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\scripts\archive-capsule.py") -Raw
    if ($rootCapsule -ne $templateCapsule) { Add-Error "Root and project-template archive-capsule.py must stay identical" }
    foreach ($forbidden in @("scripts\maintenance-runner.py", "project-template\scripts\maintenance-runner.py", "scripts\archive-daemon.py", "project-template\scripts\archive-daemon.py")) {
        if (Test-Path -LiteralPath (Join-Path $repoRoot $forbidden)) { Add-Error "v0.39 must not add maintenance runner/daemon/scheduler: $forbidden" }
    }
}
function Test-ReasoningReviewProtocol {
    foreach ($path in @(
        "project-template\docs\reasoning-review.md",
        "project-template\.claude\skills\forgekit-first-principles\SKILL.md",
        "project-template\.claude\skills\forgekit-adversarial-review\SKILL.md",
        "migrations\0.40.0\migration.json",
        "project-template\migrations\0.40.0\migration.json"
    )) { Test-RequiredPath $path }
    foreach ($marker in @(
        "First-Principles Pass", "Adversarial Review Pass", "Problem / Goal", "Known Facts",
        "Assumptions", "Constraints", "Surface Fix vs Root Fix", "Minimal Verifiable Outcome",
        "Failure Scenario", "Trigger Condition", "Expected Failure", "Evidence / Reproduction",
        "Verification Needed", "Relationship to Independent Code Review", "Critical Facts"
    )) { Test-RequiredPattern "project-template\docs\reasoning-review.md" $marker "Reasoning/review marker $marker" }
    foreach ($entry in @("project-template\AGENTS.md", "project-template\CLAUDE.md", "project-template\.codex\rules.md")) {
        Test-RequiredPattern $entry "First-Principles Pass" "First-principles entry rule"
        Test-RequiredPattern $entry "Adversarial Review Pass" "Adversarial-review entry rule"
    }
    Test-RequiredPattern "project-template\docs\workflow-router.md" "first-principles" "Workflow router first-principles route"
    Test-RequiredPattern "project-template\docs\workflow-router.md" "adversarial-review" "Workflow router adversarial-review route"
    Test-RequiredPattern "project-template\docs\bounded-auto-loop-policy.md" "blocking finding" "Bounded-auto adversarial stop gate"
    Test-RequiredPattern "project-template\docs\context-continuity.md" "blocking finding" "Context Critical Facts finding"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"first_principles_adversarial_review": true' "State reasoning/review feature"
    Test-RequiredPattern "migrations\0.40.0\migration.json" '"from": "0.39.0"' "v0.40 migration source"
    Test-RequiredPattern "migrations\0.40.0\migration.json" '"to": "0.40.0"' "v0.40 migration target"
    Test-RequiredPath "migrations\0.40.1\migration.json"
    Test-RequiredPath "project-template\migrations\0.40.1\migration.json"
    Test-RequiredPattern "migrations\0.40.1\migration.json" '"from": "0.40.0"' "v0.40.1 migration source"
    Test-RequiredPattern "migrations\0.40.1\migration.json" '"to": "0.40.1"' "v0.40.1 migration target"
    Test-RequiredPattern "project-template\.forgekit\state.json" '"idempotent_safe_migrations": true' "State idempotent migration feature"
    $manifest = Get-Content -LiteralPath (Join-Path $repoRoot "project-template\.forgekit\template-manifest.json") -Raw | ConvertFrom-Json
    $sources = @($manifest.files | ForEach-Object { $_.source_path })
    foreach ($source in @("docs/reasoning-review.md", ".claude/skills/forgekit-first-principles/SKILL.md", ".claude/skills/forgekit-adversarial-review/SKILL.md", "migrations/0.40.0/migration.json")) {
        if ($sources -notcontains $source) { Add-Error "Reasoning/review template missing from manifest: $source" }
    }
    foreach ($forbidden in @("scripts/reasoning-runner.py", "scripts/adversarial-review-runner.py", "project-template\scripts\reasoning-runner.py", "project-template\scripts\adversarial-review-runner.py")) {
        if (Test-Path -LiteralPath (Join-Path $repoRoot $forbidden)) { Add-Error "v0.40 must not add reasoning/review runner or daemon: $forbidden" }
    }
}
Test-RequiredPath "README.md"
Test-RequiredPath "AGENTS.md"
Test-RequiredPath "scripts\init-project-template.ps1"
Test-RequiredPath "scripts\init-project-template.sh"
Test-RequiredPath "scripts\archive-changes.py"
Test-RequiredPath "scripts\validate-plugin-assets.ps1"
Test-RequiredPath "project-template\README.md"
Test-RequiredPath "project-template\AGENTS.md"
Test-RequiredPath "project-template\CLAUDE.md"
Test-RequiredPath "project-template\.codex\rules.md"
Test-RequiredPattern "project-template\.codex\rules.md" "Think Before Coding" "AI coding rule: think before coding"
Test-RequiredPattern "project-template\.codex\rules.md" "Simplicity First" "AI coding rule: simplicity first"
Test-RequiredPattern "project-template\.codex\rules.md" "Surgical Changes" "AI coding rule: surgical changes"
Test-RequiredPattern "project-template\.codex\rules.md" "Goal-Driven Execution" "AI coding rule: goal-driven execution"
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

$rootArchiveScript = Join-Path $repoRoot "scripts\archive-changes.py"
$templateArchiveScript = Join-Path $repoRoot "project-template\scripts\archive-changes.py"
if ((Test-Path -LiteralPath $rootArchiveScript) -and (Test-Path -LiteralPath $templateArchiveScript)) {
    $rootArchiveText = Get-Content -LiteralPath $rootArchiveScript -Raw
    $templateArchiveText = Get-Content -LiteralPath $templateArchiveScript -Raw
    if ($rootArchiveText -ne $templateArchiveText) {
        Add-Error "Root and project-template archive-changes.py must stay identical"
    }
}

Test-GovernanceFiles
Test-AIEngineeringLoop
Test-TemplateManifest
Test-StackTemplates
Test-PromptTemplates
Test-AgentsHarness
Test-HarnessEntryConsistency
Test-StackHarnessDetails
Test-LargeChangeProtocol
Test-TeamToolingProtocol
Test-IndependentCodeReviewProtocol
Test-ContextContinuityProtocol
Test-ProjectMaintenanceOperations
Test-ReasoningReviewProtocol
Test-AgentSuitability
Test-ExecutableHarness
Test-PluginDistribution
Test-ClaudePluginDistribution
Test-SkillAscii
Test-SkillFrontmatter
Test-StaleText
Test-NoForgeKitHistoryInTemplate

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
