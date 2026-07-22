---
name: project-suitability
description: Assess whether a new or existing project is suitable for the ForgeKit AI workflow. Use during initialization, inherited project handover, or when Git, validation, docs, project structure, or ownership may be weak.
---

# Project Suitability

## Trigger

Use this skill when:

- initializing a new project with unknown engineering conditions
- taking over an existing project
- the project may lack Git, tests, build commands, docs, or standard structure
- the user is unsure whether Lite, Standard, Enterprise, or Custom flow fits
- broad AI-assisted coding would be risky without a readiness assessment

## Workflow

1. Gather evidence before asking broad questions:
   - check whether the project is a Git repository
   - inspect top-level files and directories
   - read README, setup, usage, testing, deployment, API, architecture, and release docs when present
   - inspect dependency, build, test, and startup files
   - identify binary-heavy areas and generated artifacts
2. Assess core dimensions:
   - version control and history
   - source layout and ownership clarity
   - text-code ratio versus binary or generated assets
   - local validation commands
   - documentation quality
   - deployment and environment reproducibility
   - safety, compliance, credential, and production-risk boundaries
   - maintainer or reviewer availability
3. Classify the project:
   - Suitable: ForgeKit can be used directly
   - Conditional: ForgeKit can be used after missing conditions are handled
   - Custom: use a tailored workflow with reduced automation and extra human review
4. Fill or update the suitability document:
   - conclusion
   - supporting evidence
   - missing conditions
   - safe minimum next step
   - questions that cannot be answered from local evidence
   - accepted risks if the user chooses to proceed
5. Recommend mode:
   - Lite for small low-risk tools
   - Standard for normal applications and internal systems
   - Enterprise for production, inherited, team, regulated, or high-risk projects
   - Custom when standard workflow assumptions do not hold

## Ask Only Targeted Questions

Ask the user only when local evidence cannot answer the point, for example:

- validation commands are absent or contradictory
- ownership and deployment responsibility are unclear
- docs conflict with source files
- external systems or production data are involved
- the user wants to accept a Conditional or Custom risk

## Output

End with:

- Suitability: Suitable, Conditional, or Custom.
- Recommended mode.
- Evidence read.
- Missing conditions.
- Safe next step.
- Questions for the user, if any.

## Rules

- Do not ask the user to restate facts already present in docs or source files.
- Do not treat absence of tests as permission to code broadly.
- Do not force Standard or Enterprise when a Custom workflow is safer.
- Do not install tools, initialize Git, run migrations, push, tag, or deploy during assessment.
- Record uncertainty explicitly instead of inventing readiness.
