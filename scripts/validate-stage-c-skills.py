#!/usr/bin/env python3
"""Validate Stage C Skill packages, semantics, projections, and template coverage."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import NamedTuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("[fail] Stage C Skills require PyYAML") from exc


CHANGE = Path(".forgekit/changes/v045-rule-ownership-skill-convergence")
DESIGN = CHANGE / "design.md"
TASKS = CHANGE / "tasks.md"
EXPECTED_TASK_IDS = tuple(f"SC-{number:02d}" for number in range(1, 6))
STAGE_C_ACTION = re.compile(r"(?:阶段\s*C|Stage\s*C)", re.IGNORECASE)
STAGE_D_ACTION = re.compile(r"(?:阶段\s*D|Stage\s*D)", re.IGNORECASE)
NEGATION = re.compile(
    r"\b(?:must\s+not|never|cannot|can't|may\s+not|do(?:es)?\s+not|not|no)\b",
    re.IGNORECASE,
)


class StageCSkillError(ValueError):
    pass


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise StageCSkillError(f"cannot load validator dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_task_mapping(repo: Path) -> list[dict[str, str]]:
    """Source A: parse approved SC-01..SC-05 rows without a Skill-name list."""
    text = (repo / TASKS).read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"SC-0[1-5](?:\s+.*)?", cells[0]):
            continue
        if len(cells) < 3:
            raise StageCSkillError(f"task mapping row is incomplete: {cells[0]}")
        task_id = cells[0].split()[0]
        owner_match = re.fullmatch(r"`?(skills/([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md)`?", cells[1])
        if not owner_match:
            raise StageCSkillError(f"{task_id} has an invalid Skill owner path: {cells[1]}")
        rows.append({
            "task_id": task_id,
            "owner": owner_match.group(1),
            "skill": owner_match.group(2),
            "invocation_policy": cells[2].casefold(),
        })
    ids = [row["task_id"] for row in rows]
    if tuple(sorted(ids)) != EXPECTED_TASK_IDS or len(ids) != len(set(ids)):
        raise StageCSkillError(
            f"tasks Source A must contain exactly {', '.join(EXPECTED_TASK_IDS)} once; found {ids}"
        )
    skills = [row["skill"] for row in rows]
    if len(set(skills)) != 5:
        raise StageCSkillError(f"tasks Source A must contain exactly five distinct Skills; found {skills}")
    return sorted(rows, key=lambda row: row["task_id"])


def parse_matrix_sources(repo: Path) -> tuple[list[dict[str, str]], set[str]]:
    """Source B: parse Stage C normative owners and identify Stage D owners."""
    ownership = load_module("stage_c_rule_ownership", repo / "scripts/validate-rule-ownership.py")
    rows = ownership.parse_matrix(repo / DESIGN)
    selected = [
        dict(row) for row in rows
        if row["rule_id"].startswith("ROUTE-") and STAGE_C_ACTION.search(row["migration_action"])
    ]
    stage_d: set[str] = set()
    for row in rows:
        owner = PurePosixPath(row["owner"])
        if row["rule_id"].startswith("ROUTE-") and STAGE_D_ACTION.search(row["migration_action"]):
            if len(owner.parts) == 3 and owner.parts[0] == "skills" and owner.parts[2] == "SKILL.md":
                stage_d.add(owner.parts[1])
    for row in selected:
        owner = PurePosixPath(row["owner"])
        if len(owner.parts) != 3 or owner.parts[0] != "skills" or owner.parts[2] != "SKILL.md":
            raise StageCSkillError(f"{row['rule_id']} has an invalid Stage C owner: {row['owner']}")
        row["skill"] = owner.parts[1]
    skills = [row["skill"] for row in selected]
    if len(selected) != 5 or len(set(skills)) != 5:
        raise StageCSkillError(
            f"ownership matrix Source B must contain exactly five distinct Stage C Skills; found {skills}"
        )
    return selected, stage_d


def stage_c_rows(repo: Path) -> list[dict[str, str]]:
    tasks = parse_task_mapping(repo)
    matrix, stage_d = parse_matrix_sources(repo)
    task_skills = {row["skill"] for row in tasks}
    matrix_skills = {row["skill"] for row in matrix}
    if task_skills != matrix_skills:
        raise StageCSkillError(
            "Stage C Skill-set sources disagree: "
            f"tasks-only={sorted(task_skills - matrix_skills)}; "
            f"matrix-only={sorted(matrix_skills - task_skills)}"
        )
    overlap = task_skills & stage_d
    if overlap:
        raise StageCSkillError(f"Stage C mapping includes Stage D Skill owner(s): {sorted(overlap)}")
    projection = json.loads((repo / "config/skill-projections.json").read_text(encoding="utf-8"))
    projected = [entry.get("skill") for entry in projection.get("entries", []) if isinstance(entry, dict)]
    duplicates = sorted(skill for skill, count in Counter(projected).items() if count > 1)
    if duplicates:
        raise StageCSkillError(f"Skill projection manifest contains duplicate Skill(s): {duplicates}")
    missing = task_skills - set(projected)
    if missing:
        raise StageCSkillError(f"Stage C Skill(s) missing from projection manifest: {sorted(missing)}")
    return tasks


def parse_frontmatter(text: str, skill: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise StageCSkillError(f"{skill} [frontmatter]: missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise StageCSkillError(f"{skill} [frontmatter]: unterminated frontmatter") from exc
    try:
        metadata = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        raise StageCSkillError(f"{skill} [frontmatter]: invalid YAML: {exc}") from exc
    if not isinstance(metadata, dict):
        raise StageCSkillError(f"{skill} [frontmatter]: must be a mapping")
    return metadata, "\n".join(lines[end + 1 :]) + "\n"


def contains_key(value, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


def parse_package_yaml(path: Path, skill: str) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise StageCSkillError(f"{skill} [package-yaml]: cannot parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StageCSkillError(f"{skill} [package-yaml]: agents/openai.yaml must be a mapping")
    return value


def require(skill: str, rule: str, prose: str, patterns: list[str], errors: list[str]) -> None:
    for pattern in patterns:
        if not re.search(pattern, prose, re.IGNORECASE | re.MULTILINE):
            errors.append(f"{skill} [{rule}]: missing prose contract /{pattern}/")


def forbid(skill: str, rule: str, prose: str, patterns: list[str], errors: list[str]) -> None:
    for pattern in patterns:
        match = re.search(pattern, prose, re.IGNORECASE | re.MULTILINE)
        if match:
            errors.append(f"{skill} [{rule}]: forbidden regression: {' '.join(match.group(0).split())}")


def negated(segment: str, action_start: int, action_end: int | None = None) -> bool:
    before = segment[max(0, action_start - 120) : action_start]
    if NEGATION.search(before):
        return True
    after = segment[action_end if action_end is not None else action_start :][:100]
    return bool(re.search(r"\b(?:is|are|was|were)?\s*not\s+(?:required|mandatory|needed|a prerequisite)\b", after, re.IGNORECASE))


# C-M03 is enforced as sentence-level feature invariants. These are small word
# families, not complete forbidden sentences and not order-dependent rules.
PROJECT_NOUN = r"(?:projects?|repositor(?:y|ies)|workspaces?)"
EXISTING_PROJECT_SUBJECTS = (
    rf"\b(?:for (?:each|every|any) |an? |the |each |every |any )?existing (?:ForgeKit )?{PROJECT_NOUN}\b",
    rf"\b(?:for (?:each|every|any) |an? |the |each |every |any )?(?:already|previously) initialized (?:ForgeKit )?{PROJECT_NOUN}\b",
    rf"\b(?:for (?:each|every|any) |an? |the |each |every |any )?initialized (?:ForgeKit )?{PROJECT_NOUN}\b",
    rf"\b{PROJECT_NOUN} that (?:is|are|was|were)(?: already| previously)? initialized\b",
    rf"\b{PROJECT_NOUN} that (?:has|have)(?: already)? been initialized\b",
)
INIT_ACTION_SPECS = (
    (
        "repeat-init",
        r"\b(?:repeat(?:s|ed|ing)?|rerun(?:s|ning)?|restart(?:s|ed|ing)?)\s+"
        r"(?:the\s+)?(?:project\s+)?(?:setup(?: process)?|bootstrap(?: process)?|initialization)\b",
    ),
    ("set-up", r"\bset(?:s|ting)?\s+up\b"),
    (
        "set-up",
        rf"\bset(?:s|ting)?\s+(?:(?:the|an?|each|every|any)\s+)?"
        rf"(?:(?:existing|initialized|already initialized|previously initialized)\s+)?"
        rf"(?:{PROJECT_NOUN}|it)\s+up\b",
    ),
    ("reinitialize", r"\bre-?initializ(?:e|ed|es|ing|ation)\b"),
    ("initialize", r"\b(?:project )?initializ(?:e|ed|es|ing|ation)\b"),
    ("bootstrap", r"(?<![\w-])bootstrap(?:s|ped|ping)?(?![\w-])"),
    ("setup", r"(?<![\w-])(?:project )?setup(?: process)?(?![\w-])"),
)
REPEAT_ACTION_PATTERNS = (
    r"\bagain\b",
    r"\bonce more\b",
    r"\banew\b",
    r"\bfrom scratch\b",
    r"\brepeat(?:ed|s|ing)?\b",
    r"\brerun(?:s|ning)?\b",
    r"\brestart(?:ed|s|ing)?\b",
    r"\bre-?initializ(?:e|ed|es|ing|ation)\b",
    r"\balso applies to\b",
)
POSITIVE_REQUIREMENT_PATTERNS = (
    r"\b(?:must|should|requires?|required|has to|have to|need(?:s)? to|prerequisite)\b",
    r"\bbefore (?:review|audit|handover|continuing)\b",
    r"\balso applies to\b",
)
ALTERNATIVE_ROUTE_PATTERNS = (
    r"\bcontinue to handover-review without\b",
    r"\b(?:route|go(?:es)?) to handover-review instead of\b",
    r"\buse project-bootstrap-fill rather than\b",
    r"\bskip (?:project )?(?:initialization|setup|bootstrap) and continue\b",
)

FULL_SKILL_SET_PATTERNS = (
    r"\ball (?:of )?(?:the )?(?:five|5)(?: Stage C)? Skills\b",
    r"\b(?:every one|each) of the (?:five|5) Skills\b",
    r"\b(?:every|each|all) Stage C Skills?\b",
    r"\bthe (?:complete|full) Stage C Skill set\b",
    r"\bthe (?:complete|full) set of (?:Stage C Skills|(?:five|5))\b",
    r"\bevery Skill in Stage C\b",
    r"\bevery Skill\b",
    r"\b(?:these|the) (?:five|5) Skills\b",
    r"\b(?:five|5)-Skill\b",
)
UNIVERSAL_SCOPE_PATTERNS = (
    r"\b(?:for )?(?:every|each|any) (?:project )?(?:tasks?|requests?|changes?|projects?)\b",
    r"\ball work\b",
    r"\balways\b",
)
MANDATORY_EXECUTION_PATTERNS = (
    r"\b(?:mandatory|required|compulsory|must|has to|have to|prerequisite)\b",
    r"\b(?:cannot|can not|may not) be skipped\b",
    r"\bcomplete every\b",
    r"\bmust (?:pass|run) through\b",
    r"\btake every (?:project )?(?:task|request|change) through\b",
)
SEQUENTIAL_EXECUTION_PATTERNS = (
    r"\bsequential(?:ly)?\b",
    r"\bsequence\b",
    r"\b(?:in|fixed) order\b",
    r"\bone[- ]by[- ]one\b",
    r"\bone after another\b",
    r"\bone at a time\b",
    r"\b(?:pipeline|workflow|chain)\b",
    r"\b(?:pass|run|process(?:ed)?) through\b",
    r"\bbefore finishing\b",
    r"\bcomplete the (?:complete|full) set\b",
)
NON_SKIPPABLE_PATTERNS = (
    r"\bno Stage C Skill may be skipped\b",
    r"\b(?:every|each) Stage C Skill (?:cannot|can not|must not|may not) be skipped\b",
    r"\bno Skill may be skipped\b",
)
NEGATED_PIPELINE_PATTERNS = (
    r"\bnot every\b",
    r"\bdo(?:es)? not\b",
    r"\bno (?:fixed )?(?:order|pipeline|workflow|chain)\b",
    r"\bnot mandatory\b",
    r"\bneed not\b",
    r"\bmay use\b",
    r"\boptional\b",
    r"\b(?:are|remain) alternatives\b",
    r"\brather than (?:processing |running |using )?all\b",
    r"\bonly when applicable\b",
    r"\bonly the matching (?:one|Skill)\b",
    r"\bno (?:project )?(?:task|request|change) is required to\b",
)


def first_match(patterns: tuple[str, ...], text: str):
    return next((match for pattern in patterns if (match := re.search(pattern, text, re.IGNORECASE))), None)


def has_safe_context(patterns: tuple[str, ...], text: str) -> bool:
    """Preserve the closed C-M01 safe-context predicate used by threshold checks."""
    return first_match(patterns, text) is not None


IMPERATIVE_INIT_PREFIX = (
    r"(?:before (?:review|audit|handover|continuing)|"
    r"for (?:each|every|any) [^,]{1,160})"
)


class InitActionMatch(NamedTuple):
    start: int
    end: int
    family: str
    text: str


def find_init_action_matches(sentence: str) -> list[InitActionMatch]:
    """Return non-overlapping init actions from the single lexical source."""
    found: list[InitActionMatch] = []
    for family, pattern in INIT_ACTION_SPECS:
        for match in re.finditer(pattern, sentence, re.IGNORECASE):
            if any(match.start() < item.end and item.start < match.end() for item in found):
                continue
            found.append(InitActionMatch(match.start(), match.end(), family, match.group(0)))
    return sorted(found, key=lambda item: (item.start, item.end))


def existing_subject_spans(sentence: str) -> list[tuple[int, int]]:
    return [
        match.span()
        for pattern in EXISTING_PROJECT_SUBJECTS
        for match in re.finditer(pattern, sentence, re.IGNORECASE)
    ]


def directive_init_action_matches(sentence: str) -> list[InitActionMatch]:
    subject_spans = existing_subject_spans(sentence)
    return [
        action
        for action in find_init_action_matches(sentence)
        if not any(start <= action.start and action.end <= end for start, end in subject_spans)
    ]


def detect_imperative_init_action(sentence: str, actions: list[InitActionMatch]) -> bool:
    """Recognize commands by locating a shared init-action match after an allowed lead."""
    allowed_lead = re.compile(
        rf"^\s*(?:{IMPERATIVE_INIT_PREFIX}\s*,\s*)?"
        r"(?:(?:run)\s+(?:the\s+)?(?:project\s+)?)?$",
        re.IGNORECASE,
    )
    return any(allowed_lead.fullmatch(sentence[: action.start]) for action in actions)


NEGATION_BEFORE_INIT_ACTION = (
    r"\b(?:must|should|may)\s+(?:not|never)\s+(?:(?:be|go through)\s+)?$",
    r"\b(?:cannot|can't|can not)\s+(?:(?:be|go through)\s+)?$",
    r"\bdo(?:es)? not\s+$",
    r"\bnever\s+$",
    r"\bwithout\s+$",
    r"\binstead of\s+$",
    r"\b(?:is|are|was|were) not\s+$",
)
NEGATION_AFTER_INIT_ACTION = (
    r"^.{0,80}\b(?:is|are|was|were) (?:not|never) (?:required|needed|mandatory)\b",
    r"^.{0,80}\b(?:should|must) never be used\b",
)


def init_action_is_negated(sentence: str, action: InitActionMatch) -> bool:
    before = sentence[max(0, action.start - 100) : action.start]
    after = sentence[action.end : action.end + 100]
    return (
        first_match(NEGATION_BEFORE_INIT_ACTION, before) is not None
        or first_match(NEGATION_AFTER_INIT_ACTION, after) is not None
    )


def init_actions_are_negated(sentence: str, actions: list[InitActionMatch]) -> bool:
    """A directive is negated only when every recognized directive action is locally negated."""
    return bool(actions) and all(init_action_is_negated(sentence, action) for action in actions)


def sentence_features(segment: str, stage_skills: set[str]) -> dict[str, bool]:
    init_actions = directive_init_action_matches(segment)
    mentioned = {
        skill for skill in stage_skills
        if re.search(rf"(?<![a-z0-9-])\$?{re.escape(skill)}(?![a-z0-9-])", segment, re.IGNORECASE)
    }
    navigation_completes_set = (
        "NAVIGATION" in segment and len(mentioned) == len(stage_skills) - 1
    )
    non_skippable = first_match(NON_SKIPPABLE_PATTERNS, segment) is not None
    return {
        "existing_subject": first_match(EXISTING_PROJECT_SUBJECTS, segment) is not None,
        "init_action": bool(init_actions),
        "repeat_action": first_match(REPEAT_ACTION_PATTERNS, segment) is not None,
        "positive_requirement": (
            first_match(POSITIVE_REQUIREMENT_PATTERNS, segment) is not None
            or detect_imperative_init_action(segment, init_actions)
        ),
        "negated_init": init_actions_are_negated(segment, init_actions),
        "alternative_route": first_match(ALTERNATIVE_ROUTE_PATTERNS, segment) is not None,
        "full_skill_set": (
            first_match(FULL_SKILL_SET_PATTERNS, segment) is not None
            or mentioned == stage_skills
            or navigation_completes_set
            or non_skippable
        ),
        "universal_scope": first_match(UNIVERSAL_SCOPE_PATTERNS, segment) is not None,
        "mandatory": first_match(MANDATORY_EXECUTION_PATTERNS, segment) is not None,
        "sequence": first_match(SEQUENTIAL_EXECUTION_PATTERNS, segment) is not None,
        "non_skippable": non_skippable,
        "negated_pipeline": first_match(NEGATED_PIPELINE_PATTERNS, segment) is not None,
    }


def enabled_feature_names(features: dict[str, bool], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(name for name in names if features[name])


def semantic_reversals(prose: str, policy, stage_skills: set[str]) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    for segment in policy.policy_segments(prose):
        features = sentence_features(segment, stage_skills)
        reinitialize_names = (
            "existing_subject", "init_action", "repeat_action", "positive_requirement"
        )
        if (
            all(features[name] for name in reinitialize_names)
            and not features["negated_init"]
            and not features["alternative_route"]
        ):
            found.append({
                "category": "existing-project-reinitialize",
                "segment": segment,
                "features": enabled_feature_names(features, reinitialize_names),
            })

        full_mandatory = (
            features["full_skill_set"]
            and features["universal_scope"]
            and features["mandatory"]
        )
        full_sequence = (
            features["full_skill_set"]
            and features["universal_scope"]
            and features["sequence"]
        )
        full_non_skippable = features["non_skippable"] and features["universal_scope"]
        if (full_mandatory or full_sequence or full_non_skippable) and not features["negated_pipeline"]:
            pipeline_names = (
                "full_skill_set", "universal_scope", "mandatory", "sequence", "non_skippable"
            )
            found.append({
                "category": "mandatory-five-skill-pipeline",
                "segment": segment,
                "features": enabled_feature_names(features, pipeline_names),
            })
    return found


NUMBER_TOKEN = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|dozens?)"
QUANTITY_PREFIX = r"(?:(?:more than|over|at least|fewer than|touching|affecting|changing)\s+)?"
WORKLOAD_UNITS = (
    r"files?", r"director(?:y|ies)", r"folders?", r"modules?", r"lines?",
    r"components?", r"packages?", r"services?", r"endpoints?", r"documents?",
    r"class(?:es)?", r"repositor(?:y|ies)", r"projects?",
)
QUANTITY_UNIT = rf"(?:{'|'.join(WORKLOAD_UNITS)})"
THRESHOLD_TRIGGERS = (
    r"\brequires?\b",
    r"\b(?:must|should|always) (?:use|trigger)\b",
    r"\bautomatically becomes?\b",
    r"\bis the threshold\b",
    r"\bqualif(?:y|ies) as\b",
    r"\bcounts? as\b",
    r"\btreat(?:ed)?\b.{0,120}\bas\b",
    r"\btriggers?\b",
    r"\bmandates?\b",
    r"\bneeds?\b",
    r"\buse\b.{0,100}\b(?:whenever|when)\b",
)
RISK_PROCESS_TARGETS = (
    r"\blarge changes?\b",
    r"\blarge-change planning\b",
    r"\bindependent planning\b",
    r"\bheavy planning\b",
    r"\b(?:an? )?independent checker\b",
    r"\bchecker\b",
    r"\bstaged workflow\b",
    r"\bformal review\b",
    r"\bhigh[- ]risk\b",
    r"\bescalation\b",
    r"\blarge-change workflow\b",
    r"\bthis Skill\b",
    r"\buse\b.{0,100}\b(?:whenever|when)\b",
)
QUANTITY_SAFE_CONTEXTS = (
    r"\bdo(?:es)? not\b",
    r"\bmust not\b",
    r"\bnever\b",
    r"\bcannot\b",
    r"\bmay (?:still )?remain\b",
    r"\bcan (?:still )?remain\b",
    r"\b(?:for |only as an )?example\b",
    r"\bcount alone (?:does not|is not)\b",
    r"\bdeterministic projection can remain\b",
)


def fixed_quantity_thresholds(prose: str, policy) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    quantity_pattern = rf"\b(?P<quantity>{QUANTITY_PREFIX}{NUMBER_TOKEN})(?:\s+of)?\s*(?:-|\s)\s*(?P<unit>{QUANTITY_UNIT})\b"
    for segment in policy.policy_segments(prose):
        quantity = re.search(quantity_pattern, segment, re.IGNORECASE)
        trigger = first_match(THRESHOLD_TRIGGERS, segment)
        target = first_match(RISK_PROCESS_TARGETS, segment)
        if (
            quantity and trigger and target
            and not has_safe_context(QUANTITY_SAFE_CONTEXTS, segment)
            and not negated(segment, trigger.start(), trigger.end())
        ):
            found.append({
                "segment": segment,
                "quantity": quantity.group("quantity"),
                "unit": quantity.group("unit"),
                "trigger": trigger.group(0),
                "target": target.group(0),
            })
    return found


def prompt_without_fences(prompt: str) -> str:
    visible: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in prompt.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_char is None and marker:
            fence_char = marker.group(1)[0]
            fence_length = len(marker.group(1))
            continue
        if fence_char is not None:
            if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_length},}}\s*$", line):
                fence_char = None
                fence_length = 0
            continue
        visible.append(line)
    return "\n".join(visible)


def prompt_invocations(prompt: str) -> tuple[list[str], list[str]]:
    visible = prompt_without_fences(prompt)
    formal = []
    for line in visible.splitlines():
        match = re.fullmatch(r"\s*\$([a-z0-9][a-z0-9-]*)\s*", line, re.IGNORECASE)
        if match:
            formal.append(match.group(1))
    tokens = re.findall(r"(?<![a-z0-9-])\$([a-z0-9][a-z0-9-]*)", visible, re.IGNORECASE)
    return formal, tokens


COMMON_REQUIRED = [
    r"(?:do not ask again|without asking again) for equivalent authorization",
    r"(?:commit|push).*(?:release|deploy)",
    r"(?:confirmed|verifiable).*(?:fact|evidence)|(?:fact|evidence).*(?:confirmed|verifiable)",
]
COMMON_FORBIDDEN = [
    r"(?:ask|question)\D{0,24}(?:exactly|at most|at least)\s+\d+",
    r"(?:exactly|must have)\s+(?:eight|8)\s+sections?",
]


def validate_skill(
    row: dict[str, str], text: str, package: dict, policy, repo: Path, stage_skills: set[str]
) -> list[str]:
    skill, task_id = row["skill"], row["task_id"]
    errors: list[str] = []
    meta, body = parse_frontmatter(text, skill)
    if meta.get("name") != skill:
        errors.append(f"{skill} [{task_id}]: public frontmatter name changed")
    if not isinstance(meta.get("description"), str) or not meta["description"].strip():
        errors.append(f"{skill} [{task_id}]: description is missing")
    if contains_key(meta, "allow_implicit_invocation"):
        errors.append(f"{skill} [package-policy]: allow_implicit_invocation is unsupported in SKILL.md frontmatter")

    navigation = policy.load_navigation_tokens(repo, [skill])
    prose = policy.extract_policy_prose(body, navigation)
    if not re.search(r"^##\s+Trigger Boundary\s*$", policy.strip_fenced_code_blocks(body), re.MULTILINE):
        errors.append(f"{skill} [{task_id}]: missing Trigger Boundary heading")
    require(skill, task_id, prose, COMMON_REQUIRED, errors)
    forbid(skill, task_id, prose, COMMON_FORBIDDEN, errors)
    for match in semantic_reversals(prose, policy, stage_skills):
        errors.append(
            f"{skill} [{match['category']}]: direct policy reversal: "
            f"{' '.join(str(match['segment']).split())}; "
            f"features={','.join(match['features'])}"
        )
    for match in fixed_quantity_thresholds(prose, policy):
        errors.append(
            f"{skill} [fixed-quantity-risk-threshold]: {' '.join(match['segment'].split())}; "
            f"quantity={match['quantity']!r}; unit={match['unit']!r}; "
            f"trigger={match['trigger']!r}; target={match['target']!r}"
        )

    interface = package.get("interface")
    prompt = interface.get("default_prompt") if isinstance(interface, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append(f"{skill} [package-prompt]: interface.default_prompt must be non-empty text")
        prompt = ""
    formal_invocations, invocation_tokens = prompt_invocations(prompt)
    if formal_invocations != [skill]:
        if not formal_invocations:
            errors.append(f"{skill} [package-prompt/invocation]: missing standalone ${skill} invocation")
        elif len(formal_invocations) > 1:
            errors.append(f"{skill} [package-prompt/invocation]: duplicate standalone invocation markers: {formal_invocations}")
        else:
            errors.append(f"{skill} [package-prompt/invocation]: wrong standalone Skill invocation: ${formal_invocations[0]}")
    wrong_tokens = sorted(set(invocation_tokens) - {skill})
    if wrong_tokens:
        errors.append(f"{skill} [package-prompt/invocation]: invokes other Skill ID(s): {wrong_tokens}")
    if invocation_tokens.count(skill) != 1:
        errors.append(
            f"{skill} [package-prompt/invocation]: ${skill} must appear exactly once; "
            f"found {invocation_tokens.count(skill)}"
        )
    invocation = row["invocation_policy"]
    yaml_policy = package.get("policy")
    if invocation == "explicit-only":
        if not isinstance(yaml_policy, dict) or "allow_implicit_invocation" not in yaml_policy:
            errors.append(f"{skill} [package-policy]: explicit-only Skill is missing policy.allow_implicit_invocation")
        elif type(yaml_policy["allow_implicit_invocation"]) is not bool:
            errors.append(f"{skill} [package-policy]: policy.allow_implicit_invocation must be boolean")
        elif yaml_policy["allow_implicit_invocation"] is not False:
            errors.append(f"{skill} [package-policy]: explicit-only Skill must set policy.allow_implicit_invocation: false")
    elif isinstance(yaml_policy, dict) and yaml_policy.get("allow_implicit_invocation") is False:
        errors.append(f"{skill} [package-policy]: tasks mapping does not designate this Skill explicit-only")

    prompt_prose = policy.extract_policy_prose(prompt, navigation)
    for match in semantic_reversals(prompt_prose, policy, stage_skills):
        errors.append(
            f"{skill} [package-prompt/{match['category']}]: "
            f"{' '.join(str(match['segment']).split())}; "
            f"features={','.join(match['features'])}"
        )
    for match in fixed_quantity_thresholds(prompt_prose, policy):
        errors.append(
            f"{skill} [package-prompt/fixed-quantity-risk-threshold]: "
            f"{' '.join(match['segment'].split())}; quantity={match['quantity']!r}; "
            f"unit={match['unit']!r}; trigger={match['trigger']!r}; target={match['target']!r}"
        )
    task_required = {
        "SC-01": [r"has not completed ForgeKit project initialization", r"TODO_REVIEW|UNKNOWN", r"does not authorize business implementation"],
        "SC-02": [r"already initialized", r"Preserve existing customization", r"do not require every section"],
        "SC-03": [r"read-only by default", r"Current code, configuration, and files", r"Historical plans describe intent", r"must not automatically invoke repair"],
        "SC-04": [r"implementation already exists", r"fixed document count", r"Preserve the target's structure and user customization", r"Do not write future behavior"],
        "SC-05": [r"merely because many files or modules", r"trust boundary", r"stage authorization", r"acceptance IDs", r"not mandatory for every low-risk code edit"],
    }
    require(skill, task_id, prose, task_required[task_id], errors)
    body_forbidden = {
        "SC-01": [],
        "SC-02": [r"(?:overwrite|replace) existing (?:customization|confirmed content)"],
        "SC-03": [r"(?:automatically|immediately|by default)\s+(?:fix|repair|apply fixes)"],
        "SC-04": [
            r"evidence (?:is|remains) insufficient.{0,50}(?:infer|guess|assume|plausible completion)",
            r"(?:infer|guess|assume).{0,50}when evidence (?:is|remains) insufficient",
        ],
        "SC-05": [
            r"all (?:code )?(?:changes|edits).{0,50}(?:must|require).{0,30}(?:checker|independent review)",
            r"(?:checker|independent review).{0,30}(?:required|mandatory) for all (?:code )?(?:changes|edits)",
        ],
    }
    forbid(skill, f"{task_id}/body", prose, body_forbidden[task_id], errors)

    structural = policy.strip_fenced_code_blocks(body)
    if task_id == "SC-01":
        route = re.search(
            r"Route those intents to\s+`handover-review`,\s*`project-bootstrap-fill`",
            structural,
            re.IGNORECASE,
        )
        if not route:
            errors.append(f"{skill} [{task_id}]: missing existing-project handover/bootstrap route")
    for segment in policy.policy_segments(structural):
        forward = re.search(r"route from\s+`?project-init`?\s+to\s+`?project-bootstrap-fill`?", segment, re.IGNORECASE)
        backward = re.search(r"route from\s+`?project-bootstrap-fill`?\s+to\s+`?project-init`?", segment, re.IGNORECASE)
        if forward and backward and not NEGATION.search(segment[: forward.start()]):
            errors.append(f"{skill} [routing-cycle]: obvious project-init/bootstrap routing cycle")
    prompt_forbidden = {
        "SC-01": [r"questionnaire", r"selected[- ]stack templates?", r"complete stack template", r"fixed interview"],
        "SC-02": [r"fill (?:all|every) sections?", r"reinitializ(?:e|ation)", r"questionnaire"],
        "SC-03": [r"(?:automatically|by default)\s+(?:fix|repair|apply fixes)"],
        "SC-04": [r"one source document at a time", r"one document at a time", r"exactly \d+ documents?", r"fixed batch"],
        "SC-05": [r"all code (?:changes|edits).{0,40}(?:checker|independent review)", r"exactly (?:eight|8) sections?"],
    }
    forbid(skill, f"{task_id}/package-prompt", prompt_prose, prompt_forbidden[task_id], errors)
    return errors


def canonical_checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def projection_managed_paths(repo: Path) -> list[tuple[Path, Path, str]]:
    config = json.loads((repo / "config/skill-projections.json").read_bytes().decode("utf-8"))
    target_root = config.get("target_root")
    if target_root != "project-template/.agents/skills":
        raise StageCSkillError(f"projection target_root is unexpected: {target_root!r}")
    paths: list[tuple[Path, Path, str]] = []
    seen: set[str] = set()
    for entry in config.get("entries", []):
        if not isinstance(entry, dict) or not isinstance(entry.get("skill"), str):
            raise StageCSkillError("projection entry must identify one Skill")
        for managed in entry.get("managed_files", []):
            source = Path("skills") / entry["skill"] / Path(managed)
            target = Path(target_root) / entry["skill"] / Path(managed)
            manifest_source = target.relative_to("project-template").as_posix()
            if manifest_source in seen:
                raise StageCSkillError(f"projection contains duplicate target: {manifest_source}")
            seen.add(manifest_source)
            paths.append((source, target, manifest_source))
    if len(paths) != 18:
        raise StageCSkillError(f"projection contract must contain exactly 18 managed files; found {len(paths)}")
    return paths


def validate_template_manifest(repo: Path, rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    manifest = json.loads((repo / "project-template/.forgekit/template-manifest.json").read_text(encoding="utf-8"))
    version = (repo / "VERSION").read_text(encoding="ascii").strip()
    if manifest.get("template_version") != version or version != "0.44.1":
        errors.append(f"template-manifest [version]: expected current 0.44.1, got {manifest.get('template_version')!r}/{version!r}")
    files = manifest.get("files")
    if not isinstance(files, list):
        return errors + ["template-manifest [files]: must be a list"]
    sources = [item.get("source_path") for item in files if isinstance(item, dict)]
    counts = Counter(sources)
    duplicates = sorted(source for source, count in counts.items() if count > 1)
    if duplicates:
        errors.append(f"template-manifest [duplicate]: {duplicates}")
    required = {manifest_source for _, _, manifest_source in projection_managed_paths(repo)}
    required.add(".gitattributes")
    for source in sorted(required):
        if counts[source] != 1:
            errors.append(f"template-manifest [Stage C completeness]: {source} must appear exactly once")
            continue
        item = next(item for item in files if item.get("source_path") == source)
        actual = canonical_checksum(repo / "project-template" / source)
        if item.get("checksum") != actual:
            errors.append(f"template-manifest [checksum]: {source}: manifest={item.get('checksum')} actual={actual}")
    forbidden_prefixes = (
        "scripts/validate-stage-c-skills.py",
        "tests/test_stage_c_skills.py",
        ".forgekit/changes/v045-rule-ownership-skill-convergence/stage-b-migration-draft/",
    )
    for source in sources:
        if isinstance(source, str) and source.startswith(forbidden_prefixes):
            errors.append(f"template-manifest [scope]: development-only Stage C path included: {source}")
    for row in rows:
        claude_path = f".claude/skills/{row['skill']}/SKILL.md"
        if claude_path in counts:
            errors.append(f"template-manifest [scope]: Stage C common Skill must not create Claude adapter: {claude_path}")
    return errors


def validate_lf_contract(repo: Path) -> list[str]:
    errors: list[str] = []
    required = (
        ".gitattributes", "*.md", "*.json", "*.yaml", "*.yml",
        "*.toml", "*.py", "*.ps1", "*.sh",
    )
    for relative in (Path(".gitattributes"), Path("project-template/.gitattributes")):
        path = repo / relative
        if not path.is_file():
            errors.append(f"checkout-contract: missing {relative.as_posix()}")
            continue
        active: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            active[parts[0]] = " ".join(parts[1:])
        for pattern in required:
            if active.get(pattern) != "text eol=lf":
                errors.append(f"checkout-contract: {relative.as_posix()} must set {pattern} text eol=lf")
    byte_paths = {
        Path(".gitattributes"),
        Path("project-template/.gitattributes"),
        Path("config/skill-projections.json"),
        Path("project-template/.forgekit/template-manifest.json"),
    }
    for source, target, _ in projection_managed_paths(repo):
        byte_paths.add(source)
        byte_paths.add(target)
    draft = repo / CHANGE / "stage-b-migration-draft/0.45.0"
    if draft.is_dir():
        byte_paths.add(draft.relative_to(repo) / "migration.json")
        for branch in ("baseline", "files"):
            root = draft / branch
            if root.is_dir():
                for path in root.rglob("*"):
                    if path.is_file() and path.suffix.casefold() in {".md", ".json", ".yaml", ".yml"}:
                        byte_paths.add(path.relative_to(repo))
    for relative in sorted(byte_paths, key=lambda path: path.as_posix()):
        path = repo / relative
        if not path.is_file():
            errors.append(f"checkout-contract [LF content]: missing {relative.as_posix()}")
            continue
        raw = path.read_bytes()
        if b"\r" in raw:
            kind = "CRLF" if b"\r\n" in raw else "lone CR"
            errors.append(f"checkout-contract [LF content]: {relative.as_posix()} contains {kind}")
    return errors


def validate(repo: Path) -> tuple[list[dict[str, str]], list[str]]:
    repo = repo.resolve()
    rows = stage_c_rows(repo)
    stage_skills = {row["skill"] for row in rows}
    errors: list[str] = []
    markdown_policy = load_module("stage_c_markdown_policy", repo / "scripts/validate-agent-entries.py")
    for row in rows:
        skill = row["skill"]
        owner = repo / row["owner"]
        root_yaml = owner.parent / "agents/openai.yaml"
        targets = (
            (owner, repo / "project-template/.agents/skills" / skill / "SKILL.md"),
            (root_yaml, repo / "project-template/.agents/skills" / skill / "agents/openai.yaml"),
        )
        missing = False
        for source, target in targets:
            if not source.is_file():
                errors.append(f"{skill} [package]: owner file is missing: {source.relative_to(repo)}")
                missing = True
            elif not target.is_file():
                errors.append(f"{skill} [projection]: projected file is missing: {target.relative_to(repo)}")
                missing = True
            elif source.read_bytes() != target.read_bytes():
                errors.append(f"{skill} [projection]: root and .agents bytes differ: {source.relative_to(repo)}")
        if missing or not owner.is_file() or not root_yaml.is_file():
            continue
        try:
            text = owner.read_bytes().decode("ascii")
        except UnicodeDecodeError:
            errors.append(f"{skill} [{row['task_id']}]: SKILL.md must remain ASCII-only")
            continue
        try:
            package = parse_package_yaml(root_yaml, skill)
            errors.extend(validate_skill(row, text, package, markdown_policy, repo, stage_skills))
        except StageCSkillError as exc:
            errors.append(str(exc))
    errors.extend(validate_template_manifest(repo, rows))
    errors.extend(validate_lf_contract(repo))
    return rows, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    try:
        rows, errors = validate(Path(args.repo_root))
    except (OSError, UnicodeError, json.JSONDecodeError, StageCSkillError) as exc:
        print(f"[fail] Stage C Skills: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"[fail] {error}", file=sys.stderr)
        return 1
    print(f"[ok] Stage C Skill contracts passed: {len(rows)} Skills locked by tasks and ownership matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
