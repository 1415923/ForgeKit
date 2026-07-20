#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


ENTRY_FILES = {
    "AGENTS.md": {
        "required": (
            "# Codex Project Guide",
            ".agents/skills/<skill>/SKILL.md",
            ".codex/stacks/<stack>/",
        ),
    },
    "CLAUDE.md": {
        "required": (
            "# Claude Code Project Guide",
            ".claude/skills/",
            ".agents/skills/<skill>/SKILL.md",
            "forgekit-project-workflow",
            "forgekit-request-code-review",
            "forgekit-code-review",
        ),
    },
}

CONTRACT_ANCHORS = {
    "project-and-write-boundary": "## Project and Write Boundary",
    "evidence-and-no-fabrication": "## Evidence and No Fabrication",
    "audit-default": "## Audit Default",
    "bounded-local-authorization": "## Bounded Local Authorization",
    "external-and-irreversible-actions": "## External and Irreversible Actions",
    "minimum-evidence-based-writeback": "## Minimum Evidence-Based Writeback",
    "skill-routing": "## Skill Routing",
}

COMMON_REQUIRED = (
    "governance/agent-entry-contract.md",
    ".forgekit/project-boundary.yml",
    ".forgekit/docs/codebase-map.md",
    ".forgekit/docs/workflow-router.md",
    ".forgekit/docs/context-continuity.md",
    ".forgekit/docs/local-toolchain.md",
    "governance/ai-engineering-loop.md",
    "Critical conclusions must not live only in chat",
    "scripts/forgekit-project.py",
    "scripts/forgekit-upgrade.py",
    "File count alone does not determine risk",
    "updated disk files do not prove the current session reloaded them",
)

FORBIDDEN_PATTERNS = {
    "expanded archive protocol": r"archive\s*/\s*maintenance before and after|current state restoration pass",
    "expanded checkpoint protocol": r"pre-compact checkpoint|post-compact recovery check|micro update|checkpoint update|ship update",
    "expanded worktree protocol": r"before creating a worktree|worktree results must be written",
    "expanded loop protocol": r"a loop must have a state file|loop continue must not run continuously|bounded-auto must stop",
    "maker-checker state machine": r"maker phase|checker phase|checkerstatus:|makerstatus:",
    "code-review convergence copy": r"blocker-recheck|initial review blocks|re-review defaults|reviewdecision:",
    "fixed file threshold": r"more than\s+5\s+files|>\s*5\s+files",
    "fixed module threshold": r"more than\s+2\s+modules|>\s*2\s+modules",
    "fixed question count": r"\b3\s*[-–]\s*5\s+questions\b|fixed\s+question\s+count",
    "fixed eight-section output": r"exactly\s+(?:8|eight)\s+sections|fixed\s+eight\s+sections",
    "universal independent review": r"all\s+code\s+changes.*independent\s+review|code\s+changes\s+require\s+independent\s+review\s+by\s+default",
    "repeated local-write confirmation": r"before\s+business\s+code.*wait\s+for\s+explicit\s+user\s+confirmation",
    "legacy prompt entry": r"(?:^|[\s`/])prompts/",
}

# These patterns intentionally cover only direct, explicit reversals of the shared
# entry contract. The contract remains the policy owner; this table is a narrow
# deterministic rejection gate, not a second natural-language specification.
AUDIT_DEFAULT_CONTRADICTION = {
    "id": "audit-auto-write",
    "category": "audit-default",
    "subjects": (
        r"\b(?:audit|audits|auditing)\b",
        r"\b(?:review|reviews|reviewing)\b",
        r"\b(?:assessment|assessments|assessing)\b",
        r"\b(?:diagnosis|diagnoses|diagnostic|diagnosing)\b",
        r"\b(?:planning|plan|plans)\b",
        r"(?:审计|审查|评估|诊断|规划)",
    ),
    "automatic_write_actions": (
        r"\bautomatically\s+(?:\w+\s+){0,2}(?:modify|edit|write|change|fix)(?:es|ed|ing|s)?\b",
        r"\b(?:modify|edit|write|change|fix)(?:es|ed|ing|s)?(?:\s+files?)?\s+automatically\b",
        r"\bauto[- ](?:modify|edit|write|fix)(?:es|ed|ing|s)?\b",
        r"\bdirectly\s+(?:apply\s+fix(?:es)?|fix(?:es|ed|ing)?(?:\s+files?)?)\b",
        r"\b(?:modify|edit|write|change)(?:es|ed|ing|s)?(?:\s+files?)?\s+by\s+default\b",
        r"\bapply\s+fix(?:es)?\s+by\s+default\b",
        r"(?:自动|直接).{0,8}(?:修改|编辑|写入|改变|修复)",
        r"(?:修改|编辑|写入|改变|修复).{0,8}(?:自动|默认)",
    ),
    "write_actions": (
        r"\b(?:modify|modifies|modified|modifying)\b",
        r"\b(?:edit|edits|edited|editing)\b",
        r"\b(?:write|writes|written|writing)\b",
        r"\b(?:change|changes|changed|changing)\b",
        r"\b(?:apply|applies|applied|applying)\s+fix(?:es)?\b",
        r"(?:修改|编辑|写入|改变|修复)",
    ),
    "no_repair_request": (
        r"\bwithout\s+(?:an?\s+)?(?:explicit\s+)?repair\s+request\b",
        r"\beven\s+when\s+no\s+repair\s+request\s+was\s+made\b",
        r"\bno\s+repair\s+request\s+is\s+required\b",
        r"\brepair\s+authorization\s+is\s+not\s+required\b",
        r"(?:无需|不需要).{0,6}(?:修复请求|修复授权|明确修复授权)",
    ),
    "explicit_negations": (
        r"\bmust\s+not\b",
        r"\bnever\b",
        r"\bcannot\b",
        r"\bcan['’]?t\b",
        r"\bmay\s+not\b",
        r"\b(?:do|does)\s+not\b",
        r"\bnot\b(?!\s+required\b)",
        r"\bno\s+(?:audit|audits|review|reviews|assessment|assessments|diagnosis|diagnoses|planning|plan|plans)\b",
        r"(?:不得|不能|不可|不会|从不)",
    ),
    "message": "read-only work cannot default to automatic writes or write without repair authorization",
}

CONTRADICTION_RULES = (
    {
        "id": "bounded-auth-repeat",
        "category": "bounded-local-authorization",
        "patterns": (
            r"\b(?:every|any)\s+local\s+(?:write|edit).*(?:must|requires?).*(?:ask|confirm).*(?:again|repeated)",
            r"\beven\s+after.*\b(?:authorized|approved).*(?:must|shall)\s+(?:ask|request|confirm).*(?:again|another\s+time)",
            r"(?:已经|已).*(?:授权|明确要求).*(?:本地修复|本地写入).*(?:仍须|仍需|必须再次).*(?:确认|授权)",
            r"(?:任何|每次)本地写入.*(?:都|均)?必须(?:再次|重复)(?:确认|授权)",
        ),
        "message": "bounded local authorization cannot require synonymous reconfirmation",
    },
    {
        "id": "external-no-auth",
        "category": "external-and-irreversible-actions",
        "patterns": (
            r"\b(?:push|publish|release|deploy|irreversible\s+(?:delete|deletion|migration)).*\b(?:does|do)\s+not\s+require\s+(?:explicit|specific)\s+authorization\b",
            r"\b(?:push|publish|release|deploy|irreversible\s+(?:delete|deletion|migration)).*\bmay\s+proceed\s+without\s+(?:explicit|specific)\s+authorization\b",
            r"\blocal\s+(?:fix|write)\s+authorization.*\b(?:extends?|includes?|covers?)\b.*\b(?:push|publish|release|deploy)\b",
            r"(?:推送|发布|部署|不可逆删除|不可逆迁移).*(?:无需|不需要).*(?:明确|单独|具体)?授权",
            r"本地(?:修复|写入)授权.*(?:自动扩展|同时授权).*(?:推送|发布|部署|外部动作)",
        ),
        "message": "external or irreversible actions still require specific authorization",
    },
    {
        "id": "evidence-fabrication",
        "category": "evidence-and-no-fabrication",
        "patterns": (
            r"\b(?:assumptions?|speculation|unverified\s+(?:claims?|content))\s+(?:may|can)\s+be\s+(?:recorded|written|reported)\s+as\s+(?:confirmed\s+)?facts?\b",
            r"\binsufficient\s+evidence.*\b(?:may|can)\s+(?:still\s+)?(?:claim|assert|report)\s+(?:completion|success|done)\b",
            r"(?:推测|猜测|未经验证(?:的)?内容).*(?:可以|可).*(?:写成|记录为|报告为).*(?:已确认)?事实",
            r"证据不足.*(?:仍可|可以|可).*(?:断言|声称).*(?:完成|成功)",
        ),
        "message": "unverified claims cannot be written as confirmed facts",
    },
    {
        "id": "boundary-expansion",
        "category": "project-and-write-boundary",
        "patterns": (
            r"\btask\s+authorization.*\b(?:automatically\s+)?(?:includes?|covers?|extends?\s+to)\b.*\b(?:adjacent|neighboring)\s+(?:repositories?|projects?)\b",
            r"\b(?:may|can)\s+modify\s+(?:files?\s+)?outside\s+(?:the\s+)?(?:task\s+)?scope\b",
            r"当前任务授权.*(?:自动覆盖|自动包含|扩展到).*(?:相邻仓库|其他项目|范围外文件)",
            r"(?:可以|可)修改(?:任务|当前)?范围外文件",
        ),
        "message": "task authorization cannot expand beyond the named project and scope",
    },
    {
        "id": "writeback-overreach",
        "category": "minimum-evidence-based-writeback",
        "patterns": (
            r"\bevery\s+task\s+(?:must|shall)\s+(?:create|generate|write).*(?:complete|full)\s+governance\s+(?:documents?|documentation|artifact\s+chain)\b",
            r"\buncertain\s+(?:project\s+)?business\s+(?:facts?|claims?).*\b(?:may|can|should)\s+be\s+written\s+(?:in|into|to)\s+governance\b",
            r"每个任务.*必须.*(?:完整|全套)治理(?:文档|工件)",
            r"不确定(?:的)?(?:项目|业务)事实.*(?:可以|可|应).*(?:写入|记录到)governance",
        ),
        "message": "writeback must remain minimum, confirmed, and owned by the right document",
    },
)


def strip_fenced_code_blocks(text):
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            token = match.group(1)
            if fence is None:
                fence = token[0]
            elif token[0] == fence:
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)


ATX_HEADING = re.compile(r"^\s{0,3}#{1,6}(?:\s+|$)")
SETEXT_HEADING = re.compile(r"^\s{0,3}(?:=+|-+)\s*$")
REFERENCE_DEFINITION = re.compile(r"^\s{0,3}\[[^\]\n]+\]:")
URL_TOKEN = re.compile(r"(?:https?://|mailto:)[^\s<>()]+", re.IGNORECASE)
PATH_TOKEN = re.compile(
    r"(?<![\w])(?:[A-Za-z]:[\\/]|\.{1,2}[\\/]|[A-Za-z0-9_.-]+[\\/])"
    r"(?:[A-Za-z0-9_.@%+~:-]+[\\/])*[A-Za-z0-9_.@%+~:-]+"
)
FILE_TOKEN = re.compile(
    r"(?<![\w-])[A-Za-z0-9_.-]+\.(?:md|py|ps1|json|ya?ml|toml|html?|txt)(?![\w-])",
    re.IGNORECASE,
)
INLINE_IMAGE = re.compile(r"!\[[^\]\n]*\]\([^\n)]*\)")
REFERENCE_IMAGE = re.compile(r"!\[[^\]\n]*\]\[[^\]\n]*\]")
INLINE_LINK = re.compile(r"(?<!!)\[([^\]\n]*)\]\([^\n)]*\)")
REFERENCE_LINK = re.compile(r"(?<!!)\[([^\]\n]*)\]\[[^\]\n]*\]")
AUTOLINK = re.compile(r"<(?:https?://|mailto:)[^>\n]+>", re.IGNORECASE)
NEUTRAL_NAVIGATION = " NAVIGATION "


def load_navigation_tokens(repo_root, skill_names):
    """Load navigation identifiers without creating another maintained Skill list."""
    tokens = set(skill_names)
    claude_skills = Path(repo_root) / "project-template" / ".claude" / "skills"
    if claude_skills.is_dir():
        tokens.update(path.name for path in claude_skills.iterdir() if path.is_dir())
    return tuple(sorted(tokens, key=lambda value: (-len(value), value)))


def neutralize_inline_code(text):
    output = []
    index = 0
    while index < len(text):
        if text[index] != "`":
            output.append(text[index])
            index += 1
            continue
        run_end = index
        while run_end < len(text) and text[run_end] == "`":
            run_end += 1
        delimiter = text[index:run_end]
        closing = run_end
        while True:
            closing = text.find(delimiter, closing)
            if closing < 0:
                output.append(delimiter)
                index = run_end
                break
            before_is_tick = closing > 0 and text[closing - 1] == "`"
            after = closing + len(delimiter)
            after_is_tick = after < len(text) and text[after] == "`"
            if not before_is_tick and not after_is_tick:
                output.append(NEUTRAL_NAVIGATION)
                index = after
                break
            closing = after
    return "".join(output)


def is_navigation_label(label, navigation_tokens):
    candidate = re.sub(r"\s+", " ", label).strip()
    if not candidate or candidate == NEUTRAL_NAVIGATION.strip():
        return True
    folded = candidate.casefold()
    if folded in {token.casefold() for token in navigation_tokens}:
        return True
    return bool(
        URL_TOKEN.fullmatch(candidate)
        or PATH_TOKEN.fullmatch(candidate)
        or FILE_TOKEN.fullmatch(candidate)
    )


def neutralize_markdown_links(text, navigation_tokens):
    text = INLINE_IMAGE.sub(NEUTRAL_NAVIGATION, text)
    text = REFERENCE_IMAGE.sub(NEUTRAL_NAVIGATION, text)
    text = AUTOLINK.sub(NEUTRAL_NAVIGATION, text)

    def visible_label(match):
        label = neutralize_inline_code(match.group(1))
        return NEUTRAL_NAVIGATION if is_navigation_label(label, navigation_tokens) else label

    text = INLINE_LINK.sub(visible_label, text)
    return REFERENCE_LINK.sub(visible_label, text)


def neutralize_navigation_tokens(text, navigation_tokens):
    text = URL_TOKEN.sub(NEUTRAL_NAVIGATION, text)
    text = PATH_TOKEN.sub(NEUTRAL_NAVIGATION, text)
    text = FILE_TOKEN.sub(NEUTRAL_NAVIGATION, text)
    for token in navigation_tokens:
        text = re.sub(
            rf"(?<![\w-]){re.escape(token)}(?![\w-])",
            NEUTRAL_NAVIGATION,
            text,
            flags=re.IGNORECASE,
        )
    return text


def extract_policy_prose(text, navigation_tokens=()):
    """Remove Markdown/navigation structure while preserving ordinary policy prose."""
    lines = strip_fenced_code_blocks(text).splitlines()
    excluded = set()
    for index, line in enumerate(lines):
        if ATX_HEADING.match(line) or REFERENCE_DEFINITION.match(line):
            excluded.add(index)
        if index + 1 < len(lines) and line.strip() and SETEXT_HEADING.match(lines[index + 1]):
            excluded.update((index, index + 1))

    prose_lines = []
    for index, line in enumerate(lines):
        if index in excluded:
            continue
        prose = neutralize_inline_code(line)
        prose = neutralize_markdown_links(prose, navigation_tokens)
        prose = neutralize_navigation_tokens(prose, navigation_tokens)
        prose_lines.append(prose)
    return "\n".join(prose_lines)


def policy_segments(text):
    for line in text.splitlines():
        normalized = re.sub(r"\s+", " ", line).strip()
        if not normalized:
            continue
        for segment in re.split(r"(?<=[.!?。！？])\s+|[;；]\s*", normalized):
            segment = segment.strip()
            if segment:
                yield segment


def first_pattern_match(patterns, text):
    return next((pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)), None)


def find_audit_default_contradictions(prose):
    rule = AUDIT_DEFAULT_CONTRADICTION
    matches = []
    for segment in policy_segments(prose):
        if first_pattern_match(rule["explicit_negations"], segment):
            continue
        subject = first_pattern_match(rule["subjects"], segment)
        automatic_action = first_pattern_match(rule["automatic_write_actions"], segment)
        no_repair = first_pattern_match(rule["no_repair_request"], segment)
        write_action = first_pattern_match(rule["write_actions"], segment)
        if (subject and automatic_action) or (no_repair and write_action):
            matches.append(segment)
    return matches


def detect_policy_contradictions(prose):
    """Detect direct policy reversals in already-extracted prose."""
    detections = [
        (AUDIT_DEFAULT_CONTRADICTION, matched)
        for matched in find_audit_default_contradictions(prose)
    ]
    for rule in CONTRADICTION_RULES:
        matched = next(
            (
                match.group(0)
                for pattern in rule["patterns"]
                if (match := re.search(pattern, prose, re.IGNORECASE | re.MULTILINE))
            ),
            None,
        )
        if matched:
            detections.append((rule, matched))
    return detections


def contradiction_error(label, rule, matched_text):
    excerpt = re.sub(r"\s+", " ", matched_text).strip()
    if len(excerpt) > 240:
        excerpt = excerpt[:237] + "..."
    return (
        f"{label}: contradiction {rule['id']} [{rule['category']}]: {rule['message']}; "
        f"matched text: {excerpt}"
    )


def load_skill_names(repo_root):
    manifest_path = Path(repo_root) / "config" / "skill-projections.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read Skill projection manifest {manifest_path}: {exc}") from exc
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"Skill projection manifest has no entries: {manifest_path}")
    skills = []
    for index, entry in enumerate(entries):
        skill = entry.get("skill") if isinstance(entry, dict) else None
        if not isinstance(skill, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill):
            raise ValueError(f"Skill projection manifest entry {index} has an invalid skill name")
        if skill in skills:
            raise ValueError(f"Skill projection manifest contains duplicate skill: {skill}")
        skills.append(skill)
    return tuple(skills)


def markdown_routing_sections(text):
    sections = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        heading = re.match(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$", lines[index])
        if not heading or "routing" not in heading.group(2).casefold():
            index += 1
            continue
        level = len(heading.group(1))
        body = []
        index += 1
        while index < len(lines):
            next_heading = re.match(r"^\s*(#{1,6})\s+", lines[index])
            if next_heading and len(next_heading.group(1)) <= level:
                break
            body.append(lines[index])
            index += 1
        sections.append("\n".join(body))
    return sections


def route_counts(text, skill_names):
    routing_text = "\n".join(markdown_routing_sections(strip_fenced_code_blocks(text)))
    return {
        skill: len(re.findall(rf"`{re.escape(skill)}`", routing_text))
        for skill in skill_names
    }


def validate_entry_text(label, text, skill_names=None, navigation_tokens=None):
    errors = []
    if skill_names is None:
        try:
            skill_names = load_skill_names(Path(__file__).resolve().parents[1])
        except ValueError as exc:
            return [str(exc)]
    if navigation_tokens is None:
        navigation_tokens = tuple(skill_names)
    structural_text = strip_fenced_code_blocks(text)
    policy_prose = extract_policy_prose(text, navigation_tokens)
    spec = ENTRY_FILES[label]
    for marker in COMMON_REQUIRED + spec["required"]:
        if marker not in structural_text:
            errors.append(f"{label}: missing required marker: {marker}")
    for anchor in CONTRACT_ANCHORS:
        marker = f"governance/agent-entry-contract.md#{anchor}"
        if marker not in structural_text:
            errors.append(f"{label}: missing shared-contract anchor: {anchor}")
    counts = route_counts(structural_text, skill_names)
    for skill, count in counts.items():
        if count == 0:
            errors.append(f"{label}: missing manifest Skill route: {skill}")
    for description, pattern in FORBIDDEN_PATTERNS.items():
        if re.search(pattern, structural_text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            errors.append(f"{label}: forbidden {description}")
    for rule, matched in detect_policy_contradictions(policy_prose):
        errors.append(contradiction_error(label, rule, matched))
    return errors


def validate_repo(repo_root):
    repo_root = Path(repo_root).resolve()
    template = repo_root / "project-template"
    contract = template / "governance" / "agent-entry-contract.md"
    errors = []
    try:
        skill_names = load_skill_names(repo_root)
    except ValueError as exc:
        return [str(exc)]
    navigation_tokens = load_navigation_tokens(repo_root, skill_names)
    if not contract.is_file():
        return [f"missing shared contract: {contract}"]
    contract_text = contract.read_text(encoding="utf-8")
    for anchor, heading in CONTRACT_ANCHORS.items():
        if heading not in contract_text:
            errors.append(f"agent-entry-contract.md: missing anchor heading: {anchor}")
    for label in ENTRY_FILES:
        path = template / label
        if not path.is_file():
            errors.append(f"missing entry: {path}")
            continue
        errors.extend(
            validate_entry_text(
                label,
                path.read_text(encoding="utf-8"),
                skill_names,
                navigation_tokens,
            )
        )
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate lightweight generated-project agent entries.")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_repo(Path(args.repo_root).resolve())
    if errors:
        for error in errors:
            print(f"[fail] {error}")
        raise SystemExit(1)
    print("[ok] Agent entry contracts passed")


if __name__ == "__main__":
    main()
