#!/usr/bin/env python3
"""Validate the finite Stage D review/release Skill contracts."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("[fail] Stage D Skills require PyYAML") from exc


CHANGE = Path(".forgekit/changes/v045-rule-ownership-skill-convergence")
TASKS = CHANGE / "tasks.md"
DESIGN = CHANGE / "design.md"
EXPECTED_TASK_IDS = tuple(f"SD-{number:02d}" for number in range(1, 5))
STAGE_D_ACTION = re.compile(r"(?:阶段\s*D|Stage\s*D)", re.IGNORECASE)


class StageDSkillError(ValueError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise StageDSkillError(f"cannot load validator dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_task_mapping(repo: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in (repo / TASKS).read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"SD-0[1-4](?:\s+.*)?", cells[0]):
            continue
        task_id = cells[0].split()[0]
        if len(cells) < 3:
            raise StageDSkillError(f"task mapping row is incomplete: {task_id}")
        owner = re.fullmatch(r"`?(skills/([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md)`?", cells[1])
        if not owner:
            raise StageDSkillError(f"{task_id} has an invalid Skill owner path: {cells[1]}")
        rows.append({"task_id": task_id, "owner": owner.group(1), "skill": owner.group(2)})
    ids = [row["task_id"] for row in rows]
    if tuple(sorted(ids)) != EXPECTED_TASK_IDS or len(ids) != len(set(ids)):
        raise StageDSkillError(f"tasks Source A must contain exactly {', '.join(EXPECTED_TASK_IDS)} once; found {ids}")
    if len({row["skill"] for row in rows}) != 4:
        raise StageDSkillError("tasks Source A must contain exactly four distinct Stage D Skills")
    return sorted(rows, key=lambda row: row["task_id"])


def parse_matrix_mapping(repo: Path) -> list[dict[str, str]]:
    ownership = load_module("stage_d_rule_ownership", repo / "scripts/validate-rule-ownership.py")
    selected = []
    for source in ownership.parse_matrix(repo / DESIGN):
        if not source["rule_id"].startswith("ROUTE-") or not STAGE_D_ACTION.search(source["migration_action"]):
            continue
        owner = PurePosixPath(source["owner"])
        if len(owner.parts) != 3 or owner.parts[0] != "skills" or owner.parts[2] != "SKILL.md":
            continue
        row = dict(source)
        row["skill"] = owner.parts[1]
        selected.append(row)
    skills = [row["skill"] for row in selected]
    if len(selected) != 4 or len(set(skills)) != 4:
        raise StageDSkillError(f"ownership matrix Source B must contain exactly four distinct Stage D Skills; found {skills}")
    return selected


def stage_d_rows(repo: Path) -> list[dict[str, str]]:
    tasks = parse_task_mapping(repo)
    matrix = parse_matrix_mapping(repo)
    task_skills = {row["skill"] for row in tasks}
    matrix_skills = {row["skill"] for row in matrix}
    if task_skills != matrix_skills:
        raise StageDSkillError(
            f"Stage D Skill-set sources disagree: tasks-only={sorted(task_skills-matrix_skills)}; matrix-only={sorted(matrix_skills-task_skills)}"
        )
    projection = json.loads((repo / "config/skill-projections.json").read_bytes().decode("utf-8"))
    projected = [item.get("skill") for item in projection.get("entries", []) if isinstance(item, dict)]
    duplicates = [name for name, count in Counter(projected).items() if count > 1]
    if duplicates:
        raise StageDSkillError(f"projection contains duplicate Skills: {sorted(duplicates)}")
    missing = task_skills - set(projected)
    if missing:
        raise StageDSkillError(f"Stage D Skill(s) missing from projection: {sorted(missing)}")
    return tasks


def check_patterns(skill: str, prose: str, required: list[str], forbidden: list[tuple[str, str]]) -> list[str]:
    errors = []
    for pattern in required:
        if not re.search(pattern, prose, re.IGNORECASE | re.MULTILINE):
            errors.append(f"{skill} [required-contract]: missing /{pattern}/")
    for category, pattern in forbidden:
        match = re.search(pattern, prose, re.IGNORECASE | re.MULTILINE)
        if match:
            errors.append(f"{skill} [{category}]: {' '.join(match.group(0).split())}")
    return errors


BOUNDED_WRITE_PATTERNS = {
    "authorization": (r"separately.{0,30}explicitly authoriz",),
    "writable_paths": (r"non-empty explicit writable paths",),
    "changed_path_evidence": (r"changed-path evidence",),
    "validation_evidence": (r"validation evidence",),
    "no_expansion": (r"must not expand to another finding, path, project, or external action",),
}


FINITE_POLICY_CATEGORIES = (
    {
        "category": "finding-auto-authorizes-repair",
        "features": {
            "finding": (r"\b(?:finding|defect|issue|review result)s?\b",),
            "permission": (r"\b(?:authoriz(?:e|es)|grants?|allows?|permits?)\b",),
            "repair": (r"\b(?:repair|fix|modify|write|implement)(?:s|ed|ing)?\b",),
        },
        "safe": (
            r"\b(?:does|do) not authoriz",
            r"\brequires? (?:a )?separate (?:repair )?authorization\b",
            r"\bseparately(?: and explicitly)? authoriz",
            r"\bremains? read-only\b",
        ),
    },
    {
        "category": "ordinary-change-requires-security-review",
        "features": {
            "ordinary_change": (
                r"\b(?:ordinary|all|every|any)\s+(?:backend|config(?:uration)?|code)\s+changes?\b",
            ),
            "mandatory": (r"\b(?:must|requires?|always)\b",),
            "security_review": (r"\bsecurity(?:-| )review\b|\bsecurity checker\b",),
        },
        "safe": (
            r"\balone (?:does|do) not require\b",
            r"\bonly when\b",
            r"\bremain(?:s)? normal code review\b",
            r"\b(?:does|do) not require\b",
        ),
    },
    {
        "category": "ordinary-commit-is-release",
        "features": {
            "ordinary_commit": (
                r"\b(?:(?:every|any)(?:\s+ordinary)?|ordinary)\s+(?:code\s+)?commits?\b",
            ),
            "automatic_release": (
                r"\bautomatically\b",
                r"\balways requires?\b",
                r"\bis treated as\b",
                r"\btreat\b.{0,60}\bas\b",
            ),
            "release": (r"\brelease(?:-check| readiness)?\b",),
        },
        "safe": (
            r"\bis not a release\b",
            r"\balone (?:does|do) not trigger\b",
            r"\brequires? explicit release intent\b",
            r"\b(?:does|do) not (?:trigger|require)\b",
        ),
    },
    {
        "category": "suitability-auto-initialization",
        "features": {
            "suitability": (
                r"\bsuitability (?:assessment|result)\b",
                r"\bsuitable result\b",
            ),
            "automatic": (r"\b(?:automatically|then|must)\b",),
            "initialization": (
                r"\bcreate\s+\.forgekit\b",
                r"\binitializ(?:e|es|ed|ing|ation)\b",
                r"\bmodify\s+(?:AGENTS|CLAUDE)\b",
                r"\bmigrate\s+rules\b",
            ),
        },
        "safe": (
            r"\badvisory and read-only\b",
            r"\b(?:does|do) not initializ",
            r"\brequires? a separate explicit request\b",
        ),
    },
    {
        "category": "internal-authorization-external-action",
        "features": {
            "internal_authorization": (
                r"\b(?:stage|internal|local|review|repair) authorization\b",
                r"\blocal repair permission\b",
            ),
            "permission": (
                r"\b(?:permits?|allows?|includes?)\b",
                r"\bis sufficient for\b",
                r"\bautomatically\b",
            ),
            "external_action": (r"\b(?:push|tag|publish|release|deploy)\b",),
        },
        "safe": (
            r"\b(?:does|do) not authoriz",
            r"\brequires? explicit user authorization\b",
            r"\bis separate from (?:publication|external action) permission\b",
            r"\bnever implied\b",
        ),
    },
)


def first_match(patterns, text):
    return next((match for pattern in patterns if (match := re.search(pattern, text, re.IGNORECASE))), None)


def validate_bounded_write_contract(skill: str, prose: str, policy, location: str) -> list[str]:
    errors = []
    segments = list(policy.policy_segments(prose))
    contract_segments = [
        segment for segment in segments
        if first_match(BOUNDED_WRITE_PATTERNS["writable_paths"], segment)
        and not re.match(r"^(?:for example\b|example\s*:)", segment, re.IGNORECASE)
    ]
    authorization = next(
        (segment for segment in segments if first_match(BOUNDED_WRITE_PATTERNS["authorization"], segment)),
        None,
    )
    if authorization is None:
        errors.append(f"{skill} [missing-explicit-repair-authorization] {location}: no separate explicit authorization contract")
    if not contract_segments:
        return errors + [f"{skill} [missing-writable-path-contract] {location}: no non-empty explicit writable-path contract"]
    contract = contract_segments[0]
    for feature, category in (
        ("changed_path_evidence", "missing-changed-path-evidence"),
        ("validation_evidence", "missing-validation-evidence"),
        ("no_expansion", "missing-write-boundary"),
    ):
        if not first_match(BOUNDED_WRITE_PATTERNS[feature], contract):
            errors.append(f"{skill} [{category}] {location}: {contract}")
    return errors


def finite_policy_violations(skill: str, prose: str, policy, location: str, display_prose: str | None = None) -> list[str]:
    errors = []
    segments = list(policy.policy_segments(prose))
    display_segments = list(policy.policy_segments(display_prose if display_prose is not None else prose))
    for index, segment in enumerate(segments):
        displayed = display_segments[index] if len(display_segments) == len(segments) else segment
        for rule in FINITE_POLICY_CATEGORIES:
            if first_match(rule["safe"], segment):
                continue
            matched = {
                feature: first_match(patterns, segment)
                for feature, patterns in rule["features"].items()
            }
            if all(matched.values()):
                features = ",".join(matched)
                errors.append(f"{skill} [{rule['category']}] {location}: {displayed} features={features}")
    return errors


COMMON_REQUIRED = [
    r"read-only by default|read-only gate by default|read-only advisory assessment",
    r"(?:separately|explicitly) authoriz|explicit user authorization",
    r"(?:writable paths|authorized paths|explicit writable paths)",
    r"(?:Do not|Never).{0,80}commit, push, tag|Do not commit, push",
]

COMMON_FORBIDDEN = [
    ("review-auto-maker", r"(?:automatically|by default|immediately)\s+(?:fix|repair|modify|apply fixes)"),
    ("mandatory-stage-d-pipeline", r"(?:all|every|each)\s+(?:four\s+)?Stage D Skills?.{0,80}(?:mandatory|required|must|pipeline|in sequence|in order)"),
    ("universal-checker", r"(?:all|every)\s+(?:code\s+)?(?:change|edit)s?.{0,50}(?:require|must).{0,30}(?:checker|independent review)"),
]

SPECIFIC = {
    "SD-01": {
        "required": [r"Initial review", r"Independent checker", r"Findings recheck", r"impact_severity", r"blocking", r"primary_consequence", r"failure_path", r"MAJOR", r"NOTE", r"NEEDS_TEST", r"Discovering a defect does not authorize repair", r"objective impact"],
        "forbidden": [],
    },
    "SD-02": {
        "required": [r"actual security boundary", r"Code, backend, or configuration changes.{0,80}not enough", r"Finding a security issue does not make the reviewer a maker", r"Verified", r"Supported", r"Unverified", r"human review"],
        "forbidden": [("security-review-always-on", r"security review.{0,40}(?:required|mandatory|must run).{0,40}(?:every|all)\s+(?:task|change)s?")],
    },
    "SD-03": {
        "required": [r"Use this Skill only when", r"ordinary commit.{0,50}not a release", r"Progressive Evidence", r"`ready`", r"`blocked`", r"`not-verified`", r"does not permit a version bump"],
        "forbidden": [("release-check-always-on", r"(?:every|ordinary|daily)\s+(?:commit|change).{0,50}(?:run|requires?|must use)\s+(?:a\s+)?release")],
    },
    "SD-04": {
        "required": [r"read-only advisory assessment", r"`suitable`", r"`suitable-with-constraints`", r"`not-recommended`", r"`insufficient-evidence`", r"Do not initialize ForgeKit or create `.forgekit`", r"Do not automatically invoke initialization"],
        "forbidden": [("suitability-auto-initialize", r"(?:automatically|by default|immediately)\s+(?:initialize|bootstrap|create\s+`?\.forgekit)")],
    },
}


def validate_skill(repo: Path, row: dict[str, str], policy, stage_c) -> list[str]:
    skill = row["skill"]
    owner = repo / row["owner"]
    package_path = owner.parent / "agents/openai.yaml"
    target = repo / "project-template/.agents/skills" / skill
    errors: list[str] = []
    for source, projected in ((owner, target / "SKILL.md"), (package_path, target / "agents/openai.yaml")):
        if not source.is_file() or not projected.is_file():
            errors.append(f"{skill} [package/projection]: missing {source.relative_to(repo)} or {projected.relative_to(repo)}")
        elif source.read_bytes() != projected.read_bytes():
            errors.append(f"{skill} [projection]: root/template raw bytes differ for {source.relative_to(repo)}")
    if errors:
        return errors
    raw = owner.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        return [f"{skill} [package]: SKILL.md must remain ASCII-only"]
    meta, body = stage_c.parse_frontmatter(text, skill)
    if set(meta) != {"name", "description"} or meta.get("name") != skill or not isinstance(meta.get("description"), str):
        errors.append(f"{skill} [frontmatter]: only unchanged name and non-empty description are allowed")
    navigation = policy.load_navigation_tokens(repo, [skill])
    prose = policy.extract_policy_prose(body, navigation)
    display_prose = policy.extract_policy_prose(body, ())
    contract_text = policy.strip_fenced_code_blocks(body)
    errors.extend(check_patterns(skill, contract_text, COMMON_REQUIRED + SPECIFIC[row["task_id"]]["required"], []))
    errors.extend(validate_bounded_write_contract(skill, prose, policy, row["owner"]))
    errors.extend(finite_policy_violations(skill, prose, policy, row["owner"], display_prose))
    errors.extend(check_patterns(skill, prose, [], COMMON_FORBIDDEN + SPECIFIC[row["task_id"]]["forbidden"]))
    for match in stage_c.fixed_quantity_thresholds(prose, policy):
        errors.append(f"{skill} [fixed-quantity-risk-threshold]: {' '.join(match['segment'].split())}")
    try:
        package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return errors + [f"{skill} [package-yaml]: {exc}"]
    interface = package.get("interface") if isinstance(package, dict) else None
    prompt = interface.get("default_prompt") if isinstance(interface, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append(f"{skill} [package-prompt]: missing interface.default_prompt")
        prompt = ""
    formal, tokens = stage_c.prompt_invocations(prompt)
    if formal != [skill] or tokens.count(skill) != 1 or set(tokens) != {skill}:
        errors.append(f"{skill} [package-prompt/invocation]: expected exactly one standalone ${skill}; formal={formal}; tokens={tokens}")
    yaml_policy = package.get("policy") if isinstance(package, dict) else None
    if yaml_policy is not None:
        value = yaml_policy.get("allow_implicit_invocation") if isinstance(yaml_policy, dict) else None
        if type(value) is not bool:
            errors.append(f"{skill} [package-policy]: allow_implicit_invocation must be boolean at policy.allow_implicit_invocation")
    prompt_prose = policy.extract_policy_prose(prompt, navigation)
    prompt_display_prose = policy.extract_policy_prose(prompt, ())
    errors.extend(
        finite_policy_violations(
            skill,
            prompt_prose,
            policy,
            str(package_path.relative_to(repo)).replace("\\", "/"),
            prompt_display_prose,
        )
    )
    errors.extend(check_patterns(skill, prompt_prose, [], COMMON_FORBIDDEN + SPECIFIC[row["task_id"]]["forbidden"]))
    for match in stage_c.fixed_quantity_thresholds(prompt_prose, policy):
        errors.append(f"{skill} [package-prompt/fixed-quantity-risk-threshold]: {' '.join(match['segment'].split())}")
    return errors


def validate(repo: Path):
    repo = repo.resolve()
    rows = stage_d_rows(repo)
    policy = load_module("stage_d_policy", repo / "scripts/validate-agent-entries.py")
    stage_c = load_module("stage_d_stage_c_helpers", repo / "scripts/validate-stage-c-skills.py")
    errors = []
    for row in rows:
        errors.extend(validate_skill(repo, row, policy, stage_c))
    return rows, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    try:
        rows, errors = validate(Path(args.repo_root))
    except (OSError, UnicodeError, json.JSONDecodeError, StageDSkillError) as exc:
        print(f"[fail] Stage D Skills: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"[fail] {error}", file=sys.stderr)
        return 1
    print(f"[ok] Stage D Skill contracts passed: {len(rows)} Skills locked by tasks and ownership matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
