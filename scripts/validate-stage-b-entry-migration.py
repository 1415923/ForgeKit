#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


APPROVED_STAGE_A_COMMIT = "506cecf8d377a17a2616bf3b9eeea483ee4039a4"
APPROVED_STAGE_B_COMMIT = "d02b496971db3773ac0c1435a423198189d6d8d8"
APPROVED_STAGE_C_COMMIT = "868846da54634899141047951b0f4275ad378966"
DRAFT_RELATIVE = Path(
    ".forgekit/changes/v045-rule-ownership-skill-convergence/"
    "stage-b-migration-draft/0.45.0"
)
ENTRY_NAMES = ("AGENTS.md", "CLAUDE.md")
REPORT_JSON = Path(".forgekit/reports/upgrade-review-needed.json")
REPORT_MD = Path(".forgekit/reports/upgrade-review-needed.md")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(path.read_bytes())


def make_temp_root(prefix, repo_root, temp_parent=None):
    # Default beside the candidate repository so the formal gate works under a
    # workspace-only sandbox. Callers may supply a shorter isolated parent.
    parent = Path(temp_parent) if temp_parent else Path(repo_root)
    parent.mkdir(parents=True, exist_ok=True)
    for _ in range(20):
        candidate = parent / f"{prefix}{uuid.uuid4().hex[:8]}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError(f"cannot allocate isolated Stage B validator directory under {parent}")


def git_blob_at(repo_root, commit, relative):
    command = [
        "git",
        "-C",
        str(repo_root),
        "show",
        f"{commit}:{relative.as_posix()}",
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git show failed for {relative}: {message}")
    return result.stdout


def git_blob(repo_root, relative):
    return git_blob_at(repo_root, APPROVED_STAGE_A_COMMIT, relative)


def stage_c_skill_targets(repo_root):
    import importlib.util

    path = Path(repo_root) / "scripts/validate-stage-c-skills.py"
    spec = importlib.util.spec_from_file_location("stage_b_stage_c_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Stage C validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    targets = []
    for row in module.stage_c_rows(Path(repo_root)):
        prefix = f".agents/skills/{row['skill']}"
        targets.append(f"{prefix}/SKILL.md")
        targets.append(f"{prefix}/agents/openai.yaml")
    return tuple(targets)


def stage_d_skill_targets(repo_root):
    import importlib.util

    path = Path(repo_root) / "scripts/validate-stage-d-skills.py"
    spec = importlib.util.spec_from_file_location("stage_b_stage_d_contract", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Stage D validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    targets = []
    for row in module.stage_d_rows(Path(repo_root)):
        prefix = f".agents/skills/{row['skill']}"
        targets.append(f"{prefix}/SKILL.md")
        targets.append(f"{prefix}/agents/openai.yaml")
    return tuple(targets)


def managed_targets(repo_root):
    return ENTRY_NAMES + stage_c_skill_targets(repo_root) + stage_d_skill_targets(repo_root)


def validate_draft(repo_root, package_root=None):
    repo_root = Path(repo_root).resolve()
    package = Path(package_root).resolve() if package_root else repo_root / DRAFT_RELATIVE
    errors = []
    descriptor_path = package / "migration.json"
    if not descriptor_path.is_file():
        return [f"missing Stage B migration draft: {descriptor_path}"]
    if b"\r" in descriptor_path.read_bytes():
        errors.append("migration.json violates the LF checkout contract")
    try:
        descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"invalid Stage B migration draft JSON: {exc}"]

    if descriptor.get("from") != "0.44.1" or descriptor.get("to") != "0.45.0":
        errors.append("Stage B migration draft must describe 0.44.1 -> 0.45.0")
    if descriptor.get("development_status") != "fixture-only-not-released":
        errors.append("Stage B migration draft must be marked fixture-only-not-released")
    if descriptor.get("source_commit") != APPROVED_STAGE_A_COMMIT:
        errors.append(
            "Stage B migration draft source_commit must equal approved Stage A commit "
            f"{APPROVED_STAGE_A_COMMIT}; descriptor={descriptor.get('source_commit')!r}"
        )
    errors.extend(validate_release_lifecycle(repo_root, descriptor))

    actions = descriptor.get("actions")
    expected_targets = managed_targets(repo_root)
    if not isinstance(actions, list) or len(actions) != len(expected_targets):
        errors.append(f"Stage B/C/D migration draft must contain exactly {len(expected_targets)} managed actions")
        return errors
    by_target = {action.get("target"): action for action in actions if isinstance(action, dict)}
    if set(by_target) != set(expected_targets):
        errors.append("Stage B/C/D migration draft targets must equal entries plus dual-source-derived Stage C and Stage D package files")
        return errors

    for target, action in by_target.items():
        expected_source = f"files/{target}"
        expected_baseline = f"baseline/{target}"
        if action.get("type") != "replace_file_if_baseline_matches" or action.get("safety") != "safe":
            errors.append(f"{target}: migration action must use safe baseline-guarded replacement")
        if action.get("source") != expected_source or action.get("baseline") != expected_baseline:
            errors.append(f"{target}: unexpected source/baseline path")
            continue
        source = package / expected_source
        baseline = package / expected_baseline
        template_entry = repo_root / "project-template" / target
        if not source.is_file() or not baseline.is_file():
            errors.append(f"{target}: source or baseline fixture is missing")
            continue
        if target in ENTRY_NAMES:
            baseline_commit = APPROVED_STAGE_A_COMMIT
        elif target in stage_c_skill_targets(repo_root):
            baseline_commit = APPROVED_STAGE_B_COMMIT
        else:
            baseline_commit = APPROVED_STAGE_C_COMMIT
        if target not in ENTRY_NAMES and action.get("baseline_commit") != baseline_commit:
            stage_label = "Stage B" if baseline_commit == APPROVED_STAGE_B_COMMIT else "Stage C"
            errors.append(f"{target}: baseline_commit must equal approved {stage_label} commit {baseline_commit}")
        try:
            git_bytes = git_blob_at(repo_root, baseline_commit, Path("project-template") / target)
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        baseline_bytes = baseline.read_bytes()
        if b"\r" in baseline_bytes:
            errors.append(f"{target}: baseline fixture violates the LF checkout contract")
        descriptor_baseline = action.get("baseline_sha256")
        git_sha = sha256_bytes(git_bytes)
        draft_sha = sha256_bytes(baseline_bytes)
        if baseline_bytes != git_bytes or descriptor_baseline != git_sha:
            errors.append(
                f"{target}: approved baseline mismatch; managed path={target}; "
                f"approved source commit={baseline_commit}; expected Git SHA-256={git_sha}; "
                f"draft baseline SHA-256={draft_sha}; descriptor SHA-256={descriptor_baseline}"
            )

        if not template_entry.is_file():
            errors.append(f"{target}: current project-template entry is missing")
            continue
        incoming_bytes = source.read_bytes()
        if b"\r" in incoming_bytes:
            errors.append(f"{target}: incoming fixture violates the LF checkout contract")
        template_bytes = template_entry.read_bytes()
        descriptor_incoming = action.get("incoming_sha256")
        template_sha = sha256_bytes(template_bytes)
        draft_incoming_sha = sha256_bytes(incoming_bytes)
        if incoming_bytes != template_bytes or descriptor_incoming != template_sha:
            errors.append(
                f"{target}: current incoming mismatch; managed path={target}; "
                f"current template SHA-256={template_sha}; draft incoming SHA-256={draft_incoming_sha}; "
                f"descriptor SHA-256={descriptor_incoming}"
            )
        if incoming_bytes == baseline_bytes:
            errors.append(f"{target}: baseline and incoming fixture must differ")
    return errors


def version_tuple(value):
    try:
        parts = tuple(int(part) for part in value.split("."))
    except (AttributeError, ValueError):
        return None
    return parts if len(parts) == 3 else None


def validate_release_lifecycle(repo_root, draft_descriptor=None):
    """Validate only pre-release/released package presence and version identity."""
    repo_root = Path(repo_root).resolve()
    errors = []
    if draft_descriptor is None:
        draft_path = repo_root / DRAFT_RELATIVE / "migration.json"
        if not draft_path.is_file():
            return [f"release lifecycle: missing development draft descriptor: {draft_path}"]
        draft_descriptor = json.loads(draft_path.read_text(encoding="utf-8"))
    version_path = repo_root / "VERSION"
    if not version_path.is_file():
        return ["release lifecycle: missing root VERSION"]
    current = version_path.read_text(encoding="utf-8").strip()
    target = draft_descriptor.get("to")
    current_key = version_tuple(current)
    target_key = version_tuple(target)
    if current_key is None or target_key is None:
        return [f"release lifecycle: invalid semantic version current={current!r}, target={target!r}"]

    formal_paths = (repo_root / f"migrations/{target}", repo_root / f"project-template/migrations/{target}")
    if current_key < target_key:
        for formal in formal_paths:
            if formal.exists():
                errors.append(f"release lifecycle [premature-formal-migration]: {formal}")
        return errors

    descriptors = []
    for formal in formal_paths:
        descriptor_path = formal / "migration.json"
        if not descriptor_path.is_file():
            errors.append(f"release lifecycle [missing-formal-migration]: {descriptor_path}")
            continue
        formal_descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        descriptors.append((descriptor_path, formal_descriptor))
        if formal.name != formal_descriptor.get("to"):
            errors.append(
                f"release lifecycle [directory-version-mismatch]: directory={formal.name!r}, "
                f"descriptor.to={formal_descriptor.get('to')!r}: {descriptor_path}"
            )
        if formal_descriptor.get("from") != draft_descriptor.get("from"):
            errors.append(
                f"release lifecycle [from-version-mismatch]: expected {draft_descriptor.get('from')!r}, "
                f"got {formal_descriptor.get('from')!r}: {descriptor_path}"
            )
        if formal_descriptor.get("to") != target:
            errors.append(
                f"release lifecycle [to-version-mismatch]: expected {target!r}, "
                f"got {formal_descriptor.get('to')!r}: {descriptor_path}"
            )
    if len(descriptors) == 2 and descriptors[0][0].read_bytes() != descriptors[1][0].read_bytes():
        errors.append("release lifecycle [formal-mirror-mismatch]: root/template migration descriptors differ")

    production_matches = []
    for descriptor_path in sorted((repo_root / "migrations").glob("*/migration.json")):
        production = json.loads(descriptor_path.read_text(encoding="utf-8"))
        if production.get("to") == target:
            production_matches.append(descriptor_path)
    if len(production_matches) != 1:
        errors.append(
            f"release lifecycle [duplicate-production-version]: expected one production {target}, "
            f"found {len(production_matches)}: {[str(path) for path in production_matches]}"
        )
    return errors


def write_state(project):
    state = {
        "schema_version": 1,
        "forgekit_version": "0.44.1",
        "managed_docs_root": ".forgekit/docs",
        "change_root": ".forgekit/changes",
        "mode": "standard",
        "features": {},
        "last_upgrade": None,
    }
    state_path = project / ".forgekit/state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return state_path.read_bytes()


def file_snapshot(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def run_cli(script, arguments, cwd):
    command = [sys.executable, "-B", str(script), *map(str, arguments)]
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=60)


def validate_production_discovery(repo_root, temp_parent=None):
    repo_root = Path(repo_root).resolve()
    errors = []
    evidence = {}
    temp_root = make_temp_root(".fb45d-", repo_root, temp_parent)
    evidence["temp_root"] = str(temp_root)
    try:
        isolated = temp_root / "repo"
        (isolated / "scripts").mkdir(parents=True)
        for name in ("forgekit-upgrade.py", "upgrade_review_packets.py"):
            shutil.copy2(repo_root / "scripts" / name, isolated / "scripts" / name)
        upgrade_source = (isolated / "scripts/forgekit-upgrade.py").read_text(encoding="utf-8")
        if "stage-b-migration-draft" in upgrade_source or DRAFT_RELATIVE.parent.as_posix() in upgrade_source.replace("\\", "/"):
            errors.append("production discovery implementation references the change-local Stage B draft path")
        shutil.copytree(repo_root / "migrations", isolated / "migrations")
        draft_source = repo_root / DRAFT_RELATIVE.parent
        draft_target = isolated / DRAFT_RELATIVE.parent
        draft_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(draft_source, draft_target)

        project = temp_root / "project"
        state_before = write_state(project)
        before = file_snapshot(project)
        result = run_cli(
            isolated / "scripts/forgekit-upgrade.py",
            ["check", "--repo-root", project],
            isolated,
        )
        after = file_snapshot(project)
        evidence.update({
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "state_before": state_before,
            "state_after": (project / ".forgekit/state.json").read_bytes(),
            "project_unchanged": before == after,
        })
        if result.returncode != 0:
            errors.append(f"production discovery check returned {result.returncode}: {result.stdout}{result.stderr}")
            return errors, evidence
        fields = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
        current_version = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
        draft_descriptor = json.loads((repo_root / DRAFT_RELATIVE / "migration.json").read_text(encoding="utf-8"))
        released = version_tuple(current_version) >= version_tuple(draft_descriptor["to"])
        expected_latest = current_version if released else draft_descriptor["from"]
        expected = {
            "Current version": "0.44.1",
            "Latest available": expected_latest,
            "Planned target": expected_latest,
            "Pending migrations": "1" if released else "0",
        }
        evidence["fields"] = fields
        for key, value in expected.items():
            if fields.get(key) != value:
                errors.append(f"production discovery {key} expected {value}, got {fields.get(key)!r}")
        lowered = (result.stdout + result.stderr).casefold()
        if "stage-b-migration-draft" in lowered or str(DRAFT_RELATIVE.parent).casefold() in lowered:
            errors.append("production discovery exposed the change-local Stage B draft path")
        if not released and "0.45.0" in lowered:
            errors.append("production discovery incorrectly exposed Stage B target 0.45.0")
        if released and draft_descriptor["to"] not in lowered:
            errors.append(f"production discovery did not expose formal target {draft_descriptor['to']}")
        if before != after:
            errors.append("production check modified project state, files, or reports")
        if (project / ".forgekit/reports").exists():
            errors.append("production check created reports")
        if evidence["state_after"] != state_before:
            errors.append("production check modified state.json")
    except Exception as exc:
        errors.append(f"production discovery gate failed: {type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(temp_root, ignore_errors=False)
        evidence["cleaned"] = not temp_root.exists()
    return errors, evidence


def create_scenario(temp_root, name, package_root, entries, remove_baseline=None):
    scenario = temp_root / name
    migrations = scenario / "migrations"
    package = migrations / "0.45.0"
    shutil.copytree(package_root, package)
    if remove_baseline:
        (package / "baseline" / remove_baseline).unlink()
    project = scenario / "project"
    state_before = write_state(project)
    for target, content in entries.items():
        if content is not None:
            path = project / target
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return project, migrations, package, state_before, file_snapshot(project)


def read_behavior_evidence(project, result, before_entries, state_before, before_snapshot, targets):
    report_path = project / REPORT_JSON
    report_text = report_path.read_text(encoding="utf-8")
    report = json.loads(report_text)
    reports_root = project / ".forgekit/reports"
    packets = {}
    for item in report.get("items", []):
        packet_path = reports_root / item["packet_artifacts"]["packet"]
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        artifacts = {}
        for key, relative in packet["artifacts"].items():
            artifacts[key] = None if relative is None else (reports_root / relative).read_bytes()
        packets[item["target_path"]] = {"metadata": packet, "artifacts": artifacts}
    return {
        "project_root": str(project),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "before_entries": before_entries,
        "after_entries": {
            target: (project / target).read_bytes() if (project / target).is_file() else None
            for target in targets
        },
        "state_before": state_before,
        "state_after": (project / ".forgekit/state.json").read_bytes(),
        "state": json.loads((project / ".forgekit/state.json").read_text(encoding="utf-8")),
        "before_snapshot": before_snapshot,
        "report": report,
        "report_text": report_text,
        "report_markdown": (project / REPORT_MD).read_text(encoding="utf-8"),
        "packets": packets,
    }


def validate_scenario(name, evidence, incoming, expected_classifications, targets):
    errors = []
    if evidence["returncode"] != 0:
        return [f"{name}: upgrader returned {evidence['returncode']}: {evidence['stdout']}{evidence['stderr']}"]
    items = evidence["report"].get("items", [])
    by_target = {item.get("target_path"): item for item in items}
    if set(by_target) != set(targets):
        errors.append(f"{name}: report targets differ from the managed Stage B/C target set")
        return errors
    for target, expected_classification in expected_classifications.items():
        item = by_target[target]
        packet_record = evidence["packets"].get(target)
        if item.get("classification") != expected_classification:
            errors.append(
                f"{name}/{target}: expected classification {expected_classification}, got {item.get('classification')}"
            )
        if not packet_record:
            errors.append(f"{name}/{target}: packet is missing")
            continue
        packet = packet_record["metadata"]
        artifacts = packet_record["artifacts"]
        if packet.get("classification") != item.get("classification"):
            errors.append(f"{name}/{target}: packet/report classification mismatch")
        if packet.get("packet_id") != item.get("packet_id"):
            errors.append(f"{name}/{target}: packet/report identity mismatch")
        if packet.get("managed_path") != target:
            errors.append(f"{name}/{target}: packet managed path mismatch")
        if artifacts.get("incoming") != incoming[target]:
            errors.append(f"{name}/{target}: packet incoming bytes mismatch")
        if packet.get("incoming_sha256") != sha256_bytes(incoming[target]):
            errors.append(f"{name}/{target}: packet incoming checksum mismatch")
        for artifact_name, checksum_name in (
            ("local", "local_sha256"),
            ("incoming", "incoming_sha256"),
            ("diff", "diff_sha256"),
            ("rollback", "rollback_sha256"),
        ):
            artifact_bytes = artifacts.get(artifact_name)
            expected_checksum = None if artifact_bytes is None else sha256_bytes(artifact_bytes)
            if packet.get(checksum_name) != expected_checksum:
                errors.append(f"{name}/{target}: {artifact_name} artifact checksum mismatch")
        if expected_classification == "missing":
            if evidence["after_entries"][target] != incoming[target]:
                errors.append(f"{name}/{target}: missing target was not installed")
            if artifacts.get("local") is not None or artifacts.get("rollback") is not None:
                errors.append(f"{name}/{target}: missing classification fabricated local/rollback bytes")
            if packet.get("rollback_action") != "delete_upgrade_created_file":
                errors.append(f"{name}/{target}: missing rollback action is not delete_upgrade_created_file")
        else:
            original = evidence["before_entries"][target]
            if artifacts.get("local") != original or artifacts.get("rollback") != original:
                errors.append(f"{name}/{target}: packet local/rollback bytes differ from upgrade origin")
            if expected_classification == "stock":
                if evidence["after_entries"][target] != incoming[target]:
                    errors.append(f"{name}/{target}: stock target was not updated")
            elif evidence["after_entries"][target] != original:
                errors.append(f"{name}/{target}: {expected_classification} target was overwritten")
            if packet.get("rollback_sha256") != sha256_bytes(original):
                errors.append(f"{name}/{target}: rollback checksum differs from upgrade origin")
        if expected_classification in {"custom", "unknown-baseline"}:
            if not artifacts.get("diff"):
                errors.append(f"{name}/{target}: manual-merge diff is missing or empty")
        if target not in evidence["report_markdown"] or expected_classification not in evidence["report_markdown"]:
            errors.append(f"{name}/{target}: Markdown summary lacks target/classification")
    if evidence["state"].get("forgekit_version") != "0.45.0":
        errors.append(f"{name}: state target version is not 0.45.0")
    if evidence["project_root"].casefold() in evidence["report_text"].casefold():
        errors.append(f"{name}: report leaked an absolute project path")
    for item in items:
        for relative in item.get("packet_artifacts", {}).values():
            if relative is not None and (Path(relative).is_absolute() or not relative.startswith("review-needed/")):
                errors.append(f"{name}/{item.get('target_path')}: non-portable packet artifact path: {relative}")
    return errors


def rollback_from_packets(project, evidence):
    for target, packet_record in evidence["packets"].items():
        packet = packet_record["metadata"]
        path = project / target
        if packet["rollback_action"] == "restore_original_bytes":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packet_record["artifacts"]["rollback"])
        elif packet["rollback_action"] == "delete_upgrade_created_file":
            if path.exists():
                path.unlink()
        else:
            raise RuntimeError(f"unsupported rollback action: {packet['rollback_action']}")
    (project / ".forgekit/state.json").write_bytes(evidence["state_before"])
    shutil.rmtree(project / ".forgekit/reports")


def run_chain_gate(temp_root, repo_root):
    root = temp_root / "chain"
    migrations = root / "migrations"
    project = root / "project"
    state_before = write_state(project)
    original = b"stage-a-origin\r\n"
    intermediate = b"stage-b-intermediate\n"
    final = b"stage-b-final\n"
    (project / "AGENTS.md").write_bytes(original)
    before = file_snapshot(project)
    for folder, from_version, to_version, baseline, incoming in (
        ("0.44.2", "0.44.1", "0.44.2", original, intermediate),
        ("0.45.0", "0.44.2", "0.45.0", intermediate, final),
    ):
        package = migrations / folder
        (package / "baseline").mkdir(parents=True)
        (package / "files").mkdir()
        (package / "baseline/AGENTS.md").write_bytes(baseline)
        (package / "files/AGENTS.md").write_bytes(incoming)
        descriptor = {
            "id": f"stage-b-chain-{folder}",
            "title": "Stage B same-path origin rollback gate",
            "from": from_version,
            "to": to_version,
            "risk": "high",
            "actions": [{
                "id": f"agents-{folder}",
                "type": "replace_file_if_baseline_matches",
                "safety": "safe",
                "source": "files/AGENTS.md",
                "baseline": "baseline/AGENTS.md",
                "target": "AGENTS.md",
            }],
            "manual_review": [],
            "non_goals": [],
        }
        (package / "migration.json").write_text(json.dumps(descriptor), encoding="utf-8")
    result = run_cli(
        repo_root / "scripts/forgekit-upgrade.py",
        ["apply", "--safe", "--repo-root", project, "--migration-root", migrations,
         "--review-needed-policy", "manual-merge"],
        repo_root,
    )
    if result.returncode != 0:
        return [f"chain: upgrader returned {result.returncode}: {result.stdout}{result.stderr}"], {}
    report = json.loads((project / REPORT_JSON).read_text(encoding="utf-8"))
    item = next(item for item in report["items"] if item["target_path"] == "AGENTS.md")
    reports_root = project / ".forgekit/reports"
    packet_path = reports_root / item["packet_artifacts"]["packet"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    rollback = (reports_root / packet["artifacts"]["rollback"]).read_bytes()
    errors = []
    if (project / "AGENTS.md").read_bytes() != final:
        errors.append("chain: final AGENTS bytes are incorrect")
    if rollback != original or packet.get("rollback_sha256") != sha256_bytes(original):
        errors.append("chain: packet did not retain complete upgrade-start origin bytes")
    chain_evidence = {
        "state_before": state_before,
        "before_snapshot": before,
        "final": (project / "AGENTS.md").read_bytes(),
        "rollback": rollback,
        "packet": packet,
    }
    (project / "AGENTS.md").write_bytes(rollback)
    (project / ".forgekit/state.json").write_bytes(state_before)
    shutil.rmtree(project / ".forgekit/reports")
    chain_evidence["rollback_restored"] = file_snapshot(project) == before
    if not chain_evidence["rollback_restored"]:
        errors.append("chain: rollback did not restore complete upgrade-start state")
    return errors, chain_evidence


def validate_migration_behavior(repo_root, package_root=None, temp_parent=None):
    repo_root = Path(repo_root).resolve()
    package_root = Path(package_root).resolve() if package_root else repo_root / DRAFT_RELATIVE
    errors = []
    evidence = {"scenarios": {}}
    temp_root = make_temp_root(".fb45m-", repo_root, temp_parent)
    evidence["temp_root"] = str(temp_root)
    try:
        targets = managed_targets(repo_root)
        baseline = {name: (package_root / "baseline" / name).read_bytes() for name in targets}
        incoming = {name: (package_root / "files" / name).read_bytes() for name in targets}
        # Keep the long-standing entry unknown-baseline scenario stable while
        # the stock/custom/missing/mixed scenarios exercise every Stage C Skill.
        unknown_target = "CLAUDE.md"
        mixed_entries = {
            target: baseline[target] if index % 2 == 0 else f"mixed custom {index}\r\n".encode("ascii")
            for index, target in enumerate(targets)
        }
        mixed_expected = {
            target: "stock" if index % 2 == 0 else "custom"
            for index, target in enumerate(targets)
        }
        scenarios = {
            "stock": ({name: baseline[name] for name in targets}, None,
                      {name: "stock" for name in targets}),
            "custom": ({name: f"custom {index}\r\n".encode("ascii") for index, name in enumerate(targets)}, None,
                       {name: "custom" for name in targets}),
            "unknown": ({name: baseline[name] if name != unknown_target else b"unknown skill\n" for name in targets},
                        unknown_target, {name: "stock" if name != unknown_target else "unknown-baseline" for name in targets}),
            "missing": ({name: None for name in targets}, None,
                        {name: "missing" for name in targets}),
            "mixed": (mixed_entries, None, mixed_expected),
        }
        for name, (entries, removed_baseline, expected) in scenarios.items():
            project, migrations, _package, state_before, before = create_scenario(
                temp_root, name, package_root, entries, removed_baseline
            )
            result = run_cli(
                repo_root / "scripts/forgekit-upgrade.py",
                ["apply", "--safe", "--repo-root", project, "--migration-root", migrations,
                 "--review-needed-policy", "manual-merge"],
                repo_root,
            )
            if result.returncode != 0 or not (project / REPORT_JSON).is_file():
                errors.append(f"{name}: upgrader/report failure: {result.stdout}{result.stderr}")
                continue
            evidence_item = read_behavior_evidence(project, result, entries, state_before, before, targets)
            evidence["scenarios"][name] = evidence_item
            errors.extend(validate_scenario(name, evidence_item, incoming, expected, targets))
            if name == "stock" and evidence_item["state"].get("last_upgrade", {}).get("review_needed_actions"):
                errors.append("stock: unresolved REVIEW-NEEDED actions were produced")
            if name in {"missing", "mixed"}:
                rollback_from_packets(project, evidence_item)
                evidence_item["rollback_restored"] = file_snapshot(project) == before
                if not evidence_item["rollback_restored"]:
                    errors.append("mixed: rollback did not restore complete upgrade-start state")
        chain_errors, chain_evidence = run_chain_gate(temp_root, repo_root)
        errors.extend(chain_errors)
        evidence["chain"] = chain_evidence
    except Exception as exc:
        errors.append(f"migration behavior gate failed: {type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(temp_root, ignore_errors=False)
        evidence["cleaned"] = not temp_root.exists()
    return errors, evidence


def validate_repo(repo_root):
    repo_root = Path(repo_root).resolve()
    errors = validate_draft(repo_root)
    discovery_errors, _ = validate_production_discovery(repo_root)
    behavior_errors, _ = validate_migration_behavior(repo_root)
    errors.extend(discovery_errors)
    errors.extend(behavior_errors)
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate Stage B entry draft identity, production isolation, and real migration behavior."
    )
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_repo(Path(args.repo_root))
    if errors:
        for error in errors:
            print(f"[fail] {error}")
        raise SystemExit(1)
    print(
        "[ok] Stage B entry migration draft passed: Git/current anchors, production discovery, "
        "stock/custom/unknown/missing/mixed/rollback, and same-path origin rollback"
    )


if __name__ == "__main__":
    main()
