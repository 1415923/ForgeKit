---
name: project-init
description: Initialize or repair a project's Codex workflow, discover product requirements, inspect existing projects before asking stack questions, and fill first-version `.codex/` and `docs/` files from confirmed facts. Use when Codex is asked to set up a project, clarify a vague idea, process initialization answers, discuss architecture before implementation, or decide whether coding may start.
---

# Project Init

## Workflow

1. Read `AGENTS.md` first if present, then read the governance overview, `.codex/init.generated.md`, `.codex/questionnaires/`, existing `.codex/`, existing `docs/`, and project root files.
2. Identify whether this is a new project idea, an existing project handover, or a feature/change request inside an existing project.
3. Inspect local evidence before asking stack questions:
   - For existing projects, scan README files, build files, dependency manifests, scripts, tests, source roots, and config files to infer the current stack and constraints.
   - For new empty projects, treat missing `.codex/stacks/` or empty stacks as a normal planning state, not an error.
   - Read `.codex/stacks/<stack>/` only when the stack is already present, selected in metadata, or clearly inferred from local evidence.
4. If questionnaire answers exist, use `governance/project-bootstrap-fill.md` to convert them into first-version `.codex/` rules and `docs/`.
5. Interview the user before large-scale coding when key facts are unclear. Do not start with a fixed list of technical questions. Choose the next question from the current uncertainty:
   - product goal and target users
   - current workflow or pain point
   - success criteria and acceptance evidence
   - product shape options and non-goals
   - existing system constraints, if any
   - research needed before deciding
   - v0.1.0 minimum closed loop
   - risks and blockers
   - Epic / Feature / Task / Bug model
   - version roadmap
6. Classify the discovery state before asking the next question:
   - `unclear`: The user has an idea, complaint, or goal, but the target users, problem, product shape, or success criteria are not coherent yet. Ask product-level questions only.
   - `options-needed`: The problem is understandable, but there are multiple viable product shapes or scope paths. Present 2 to 4 options with tradeoffs, recommend one default, and ask the user to choose or reject.
   - `research-needed`: A decision depends on external facts, official docs, public examples, compatibility, policy, market behavior, or unfamiliar technology. Propose concrete references to inspect, search queries to run, GitHub examples to compare, or a throwaway prototype.
   - `existing-project-scan`: The user is handing over a repo, adding a feature, fixing a bug, or refactoring existing code. Scan local files first, infer stack and constraints, then ask only targeted questions about contradictions or missing evidence.
   - `ready-for-plan`: The problem, users, product shape, v0.1.0 closed loop, constraints, validation evidence, and major risks are coherent enough to write a plan. Produce the plan and execution summary instead of continuing broad discovery.
7. Apply the discovery state rules:
   - In `unclear`, ask at most 3 high-leverage questions about WHAT, WHY, WHO, success, and non-goals. Do not ask framework, database, auth, hosting, or directory questions.
   - In `options-needed`, provide a comparison table: option, scope, cost, risk, validation path, and why it may fit. Include a recommended default and a conservative fallback.
   - In `research-needed`, do not pretend to know. State the unknown, the decision it blocks, the sources or repositories to check, and what evidence would change the recommendation.
   - In `existing-project-scan`, report the files inspected, inferred stack, commands, test strategy, integration points, and contradictions before asking the user.
   - In `ready-for-plan`, stop asking exploratory questions and write the structured project plan, roadmap, task model, risks, and execution confirmation.
8. Use iterative solution shaping, not a one-shot questionnaire:
   - Ask only the next 3 to 5 highest-leverage questions.
   - If the user cannot answer, provide 2 to 4 realistic options with tradeoffs and a recommended default.
   - If current knowledge is insufficient, propose a research path: local docs to inspect, official docs to search, example projects to compare, or small throwaway prototypes to run.
   - For new product ideas, treat product discovery and architecture discussion as a dedicated phase. Do not collapse it into engineering parameter questions such as framework, database, login, or directory structure.
   - Clearly mark each item as Confirmed, Assumption, Research needed, or Deferred.
   - Keep interviewing and revising the plan until the problem, product shape, v0.1.0 scope, validation evidence, and safety boundary are coherent. Technical stack may remain undecided until product constraints justify it.
   - Do not treat "unknown" as a reason to stop; turn unknowns into decision options, research tasks, or deferred non-goals.
9. When the user describes a product idea in natural language, translate it into:
   - problem and target users
   - MVP workflow
   - explicit non-goals
   - data and state boundaries
   - technical constraints and research options, without forcing a stack decision too early
   - validation strategy
   - risks and open decisions
   - first implementation slice, only when coding is allowed
10. For new projects, discuss product shape before implementation:
   - Provide 2 to 4 possible product shapes when the user's goal is broad or ambiguous.
   - Compare scope, complexity, deployment cost, long-term evolution, and non-goals.
   - Propose a long-term version roadmap with concrete v0.1.0, v0.2.0, v0.3.0, and v1.0.0 outcomes.
   - If public references would help, ask whether to search official docs, public projects, or product examples before finalizing the plan.
   - Summarize what was learned from local files or external research, and say when research has not been done.
   - Do not ask the user to choose a stack at the beginning. Present stack options only after product shape, runtime constraints, integration points, team skills, and validation needs are known.
11. For existing projects, use repository evidence first:
   - Infer stack, commands, architecture, and test strategy from files before asking the user.
   - New features and fixes should default to the existing stack and architecture.
   - Ask about stack migration, database replacement, framework changes, or major refactors only when the user explicitly requests them or local evidence shows a blocking conflict.
   - If local evidence is missing or contradictory, summarize what was found and ask targeted questions about the contradiction.
12. For large, cross-module, migration, refactor, or high-risk work, require the large-change protocol before implementation:
   - read `governance/large-change-execution.md`
   - create or update the exploration report in `docs/`
   - create or update the implementation plan in `docs/`
   - do not start broad coding until the implementation plan says coding is allowed
13. Fill or update:
   - `.codex/project.md`
   - `.codex/scope.md`
   - `.codex/commands.md`
   - `.codex/style.md`
   - `.codex/testing.md`
   - `.codex/security.md`
   - `.codex/git.md`
   - `.codex/version-gates.md`
   - `docs/project plan`
   - version roadmap document in `docs/`
   - `docs/requirements`
   - `docs/architecture`
   - `docs/technology selection`
   - `docs/environment matrix`
   - `docs/release pipeline`
   - `docs/project task board`
14. Preserve existing project-specific facts. Do not overwrite real information with template text.
15. Remove or replace template history that belongs to ForgeKit itself. Generated projects must not keep ForgeKit Agent Harness roadmap tasks as if they were project tasks.
16. Do not modify business code unless the user explicitly asks.

## Gate Before Coding

If the development plan, version roadmap, landing conditions, or first implementation slice are unclear, ask follow-up questions instead of starting implementation.

If the user cannot answer a gate question, do not repeat the same question. Provide a decision table, a recommended default, and a concrete way to verify the choice.

If the requested work is large or cross-module, require exploration and implementation planning before coding.

Before creating business code, installing dependencies, initializing Git, committing, pushing, or performing any external write, output an "Execution Confirmation" summary and wait for explicit user confirmation. The summary must include:

- one-sentence final project goal
- product shape chosen and alternatives rejected
- v0.1.0, v0.2.0, v0.3.0, and v1.0.0 roadmap
- what this implementation will do and explicitly not do
- product constraints, technology stack status, storage/auth/deployment status, and validation choices
- reference or research status, including whether web research was skipped
- major risks and safety boundaries
- files to create or modify
- commands to run
- external actions such as Git init, commit, push, issue/PR updates, deployment, or service start

User replies such as "allow generating the project", "use MySQL", or "go ahead with dependencies" are not enough by themselves. Treat them as partial decisions unless they explicitly confirm the full execution summary.

Do not recommend large-scale coding until there is at least a first version of:

- project plan
- version roadmap
- technical stack status: confirmed, inferred from existing project, assumption, research needed, or deferred
- software/hardware conditions
- architecture governance and ADR needs
- RFC needs, traceability IDs, readiness, and risks
- v0.1.0 scope and v0.1.1 review/refactor gate
- first-pass environment matrix and release pipeline assumptions
- first-pass Epic / Feature / Task / Bug model
- exploration report and implementation plan for large changes

## Selection Rules

- Do not make stack selection the first user task.
- Use `templates/README.md` only after a stack is confirmed or inferred from local evidence.
- For existing projects, infer stack from repository files before asking the user.
- For Java projects, read `java-springboot` only when Java/Spring Boot is present or selected after planning.
- For FPGA projects, read `fpga-vivado-vitis` only when Vivado/Vitis/HLS is present or selected after planning.
- For full-stack projects, read only the backend and frontend stacks actually present or selected after planning.

## Output

End with:

- Project classification.
- Discovery state: unclear, options-needed, research-needed, existing-project-scan, or ready-for-plan.
- Stack status: none yet, selected by metadata, inferred from files, or deferred pending planning.
- Files created or updated.
- Plan status: confirmed, partial, or blocked.
- Confirmed decisions, assumptions, research-needed items, and deferred non-goals.
- The next 3-5 questions or decision options to continue the project planning discussion.
- Reference or research suggestions when the user cannot decide from current context.
- Suggested first implementation slice only if coding is allowed.
- Validation commands that are safe to run.
