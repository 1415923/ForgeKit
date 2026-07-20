"""Atomic review/rollback packet support for the existing ForgeKit upgrader."""

from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import stat
import sys
import unicodedata
import uuid
from pathlib import Path, PurePosixPath
from typing import Callable


REPORTS_ROOT = Path(".forgekit/reports")
PACKET_ROOT = Path(".forgekit/reports/review-needed")
CLASSIFICATIONS = {"stock", "custom", "missing", "unknown-baseline"}
FORGEKIT_VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
WINDOWS_UNSAFE = re.compile(r"[<>:\"|?*\x00-\x1f]")
WINDOWS_DEVICES = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
CANONICAL_PACKET_NAME = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+--[0-9a-f]{16}$")


class PacketError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_target_version(value: str) -> str:
    if not isinstance(value, str) or not FORGEKIT_VERSION.fullmatch(value):
        raise PacketError(f"unsafe target version: {value!r}; expected ForgeKit major.minor.patch")
    return value


def _validate_component(component: str, label: str) -> None:
    if not component or component in {".", ".."}:
        raise PacketError(f"{label} contains an empty or traversal component: {component!r}")
    if WINDOWS_UNSAFE.search(component) or component.endswith((".", " ")):
        raise PacketError(f"{label} contains a non-portable component: {component!r}")
    if component.split(".", 1)[0].upper() in WINDOWS_DEVICES:
        raise PacketError(f"{label} contains a Windows reserved device name: {component!r}")


def normalize_managed_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise PacketError(f"managed path must be a normalized POSIX relative path: {value!r}")
    if value.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", value):
        raise PacketError(f"managed path must not be absolute, drive-qualified, UNC, or device-qualified: {value!r}")
    raw_parts = value.split("/")
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith("./"):
        raise PacketError(f"unsafe managed path: {value!r}")
    for component in raw_parts:
        _validate_component(component, "managed path")
    return path.as_posix()


def packet_id(target_version: str, managed_path: str) -> str:
    target_version = validate_target_version(target_version)
    managed_path = normalize_managed_path(managed_path)
    path_hash = hashlib.sha256(managed_path.encode("utf-8")).hexdigest()[:16]
    return f"{target_version}--{path_hash}"


def _is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(info, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def ensure_portable_path(root: Path, relative: str) -> None:
    """Reject reparse/root escape and existing Unicode-normalization aliases."""
    relative = normalize_managed_path(relative)
    root = root.resolve()
    current = root
    for component in PurePosixPath(relative).parts:
        if current.exists():
            if _is_reparse(current) or not current.is_dir():
                raise PacketError(f"managed path parent is not a safe directory: {current}")
            normalized = unicodedata.normalize("NFC", component)
            aliases = [child.name for child in current.iterdir() if unicodedata.normalize("NFC", child.name) == normalized]
            if aliases and component not in aliases:
                raise PacketError(
                    f"managed path has a Unicode normalization conflict at {component!r}: existing {aliases!r}"
                )
        current = current / component
        if current.exists() and _is_reparse(current):
            raise PacketError(f"managed path crosses a symlink, junction, or reparse point: {relative}")
    try:
        current.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise PacketError(f"managed path escapes the allowed root: {relative}") from exc


def _safe_packet_root(project_root: Path) -> Path:
    project_root = project_root.resolve()
    current = project_root
    for part in PACKET_ROOT.parts:
        current = current / part
        if current.exists():
            if _is_reparse(current):
                raise PacketError("packet root crosses a symlink, junction, or reparse point")
            if not current.is_dir():
                raise PacketError(f"packet root parent is not a directory: {current}")
    current.mkdir(parents=True, exist_ok=True)
    return current


def _artifact_relative(packet: str, section: str, managed_path: str | None = None) -> str:
    relative = PurePosixPath("review-needed") / packet / section
    if managed_path:
        relative = relative / PurePosixPath(managed_path)
    return relative.as_posix()


def canonical_packet_directories(packet_root: Path) -> list[Path]:
    """Enumerate only fixed canonical packet directories, never staging/old siblings."""
    if not packet_root.is_dir() or _is_reparse(packet_root):
        return []
    canonical = []
    for child in sorted(packet_root.iterdir()):
        if not child.is_dir() or _is_reparse(child) or not CANONICAL_PACKET_NAME.fullmatch(child.name):
            continue
        try:
            validate_complete_packet(child)
        except PacketError:
            continue
        canonical.append(child)
    return canonical


def _summary_references_name(project_root: Path, directory_name: str) -> bool:
    reports_root = project_root / REPORTS_ROOT
    for name in ("upgrade-review-needed.json", "upgrade-review-needed.md"):
        path = reports_root / name
        if path.is_file() and directory_name in path.read_text(encoding="utf-8-sig", errors="replace"):
            return True
    return False


def _cleanup_stale_old(
    project_root: Path,
    packet_root: Path,
    identity_value: str,
    cleanup: Callable[[Path], None],
    warn: Callable[[str], None],
) -> None:
    prefix = f".old-{identity_value}-"
    for candidate in sorted(packet_root.iterdir()):
        if not candidate.name.startswith(prefix):
            continue
        if candidate.parent != packet_root or not candidate.is_dir() or _is_reparse(candidate):
            warn(f"packet cleanup pending: unsafe stale old directory ignored: {candidate.name}")
            continue
        if _summary_references_name(project_root, candidate.name):
            warn(f"packet cleanup pending: referenced stale old directory ignored: {candidate.name}")
            continue
        try:
            cleanup(candidate)
        except OSError as exc:
            warn(f"packet cleanup pending: could not remove stale {candidate.name}: {exc}")


def _diff_bytes(local_bytes: bytes | None, incoming_bytes: bytes, managed_path: str) -> bytes:
    old = (local_bytes or b"").decode("utf-8", errors="replace").splitlines(keepends=True)
    new = incoming_bytes.decode("utf-8", errors="replace").splitlines(keepends=True)
    rendered = "".join(difflib.unified_diff(old, new, fromfile=managed_path, tofile=f"incoming/{managed_path}"))
    return rendered.encode("utf-8")


def _identity(packet: dict) -> dict:
    return {
        "packet_id": packet.get("packet_id"),
        "managed_path": packet.get("managed_path"),
        "target_version": packet.get("target_version"),
        "source_version": packet.get("source_version"),
        "existed_before_upgrade": packet.get("existed_before_upgrade", packet.get("local_existed")),
        "rollback_sha256": packet.get("rollback_sha256"),
    }


def validate_complete_packet(packet_dir: Path, expected_identity: dict | None = None) -> dict:
    metadata = packet_dir / "packet.json"
    try:
        packet = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PacketError(f"packet is incomplete or unreadable: {packet_dir}") from exc
    if packet.get("publication_status") != "complete":
        raise PacketError(f"packet is not complete: {packet_dir}")
    managed_path = normalize_managed_path(packet.get("managed_path"))
    identity = _identity(packet)
    if packet_id(packet.get("target_version"), managed_path) != packet.get("packet_id"):
        raise PacketError(f"packet identity conflict: invalid packet ID in {packet_dir}")
    if expected_identity is not None and identity != expected_identity:
        raise PacketError(
            "packet identity conflict: existing="
            + json.dumps(identity, ensure_ascii=False, sort_keys=True)
            + " expected="
            + json.dumps(expected_identity, ensure_ascii=False, sort_keys=True)
        )
    nested = Path(*PurePosixPath(managed_path).parts)
    expected_paths = {
        "incoming": packet_dir / "incoming" / nested,
        "diff": packet_dir / "diff.patch",
    }
    existed = bool(identity["existed_before_upgrade"])
    if existed:
        expected_paths["local"] = packet_dir / "local" / nested
        expected_paths["rollback"] = packet_dir / "rollback" / nested
    checksums = {
        "incoming": packet.get("incoming_sha256"),
        "diff": packet.get("diff_sha256"),
        "local": packet.get("local_sha256"),
        "rollback": packet.get("rollback_sha256"),
    }
    for name, path in expected_paths.items():
        if not path.is_file() or sha256_bytes(path.read_bytes()) != checksums[name]:
            raise PacketError(f"packet artifact checksum mismatch: {name} in {packet_dir}")
    if not existed:
        for name in ("local", "rollback"):
            if (packet_dir / name / nested).exists() or checksums[name] is not None:
                raise PacketError(f"missing-origin packet fabricates {name}: {packet_dir}")
    return packet


def prepare_packet(
    project_root: Path,
    *,
    target_version: str,
    managed_path: str,
    source_version: str | None,
    classification: str,
    baseline_sha256: str | None,
    local_bytes: bytes | None,
    incoming_bytes: bytes,
    resolution_status: str,
    user_action: str,
    origin_snapshot: dict | None = None,
    on_publish: Callable[[dict], None] | None = None,
    fault_injector: Callable[[str], None] | None = None,
    old_cleanup: Callable[[Path], None] | None = None,
    warning_callback: Callable[[str], None] | None = None,
) -> dict:
    if classification not in CLASSIFICATIONS:
        raise PacketError(f"invalid classification: {classification}")
    target_version = validate_target_version(target_version)
    source_version = validate_target_version(source_version)
    managed_path = normalize_managed_path(managed_path)
    project_root = project_root.resolve()
    ensure_portable_path(project_root, managed_path)
    identity_value = packet_id(target_version, managed_path)
    if origin_snapshot is None:
        origin_snapshot = {
            "managed_path": managed_path,
            "source_version": source_version,
            "existed_before_upgrade": local_bytes is not None,
            "original_bytes": local_bytes,
            "original_sha256": sha256_bytes(local_bytes) if local_bytes is not None else None,
        }
    if origin_snapshot.get("managed_path") != managed_path or origin_snapshot.get("source_version") != source_version:
        raise PacketError("packet identity conflict: origin snapshot path/source version mismatch")
    existed = bool(origin_snapshot.get("existed_before_upgrade"))
    rollback_bytes = origin_snapshot.get("original_bytes")
    rollback_sha = origin_snapshot.get("original_sha256")
    if existed:
        if not isinstance(rollback_bytes, bytes) or sha256_bytes(rollback_bytes) != rollback_sha:
            raise PacketError("packet identity conflict: origin rollback bytes/checksum mismatch")
    elif rollback_bytes is not None or rollback_sha is not None:
        raise PacketError("packet identity conflict: missing origin has rollback bytes")
    expected_identity = {
        "packet_id": identity_value,
        "managed_path": managed_path,
        "target_version": target_version,
        "source_version": source_version,
        "existed_before_upgrade": existed,
        "rollback_sha256": rollback_sha,
    }
    packet_root = _safe_packet_root(project_root)
    cleanup = old_cleanup or shutil.rmtree
    warn = warning_callback or (lambda message: print(f"[warning] {message}", file=sys.stderr))
    final_dir = packet_root / identity_value
    if final_dir.exists():
        if not final_dir.is_dir() or _is_reparse(final_dir):
            raise PacketError(f"packet identity conflict: fixed packet target is unsafe: {final_dir}")
        validate_complete_packet(final_dir, expected_identity)
    _cleanup_stale_old(project_root, packet_root, identity_value, cleanup, warn)

    nonce = uuid.uuid4().hex
    staging = packet_root / f".tmp-{identity_value}-{nonce}"
    old = packet_root / f".old-{identity_value}-{nonce}"
    fault = fault_injector or (lambda _stage: None)
    published = False
    old_moved = False
    committed = False
    try:
        staging.mkdir()
        nested = Path(*PurePosixPath(managed_path).parts)
        local_path = staging / "local" / nested
        incoming_path = staging / "incoming" / nested
        rollback_path = staging / "rollback" / nested
        diff_path = staging / "diff.patch"
        if existed:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(rollback_bytes)
            if sha256_bytes(local_path.read_bytes()) != rollback_sha:
                raise PacketError("local artifact verification failed")
        fault("after_local")
        incoming_path.parent.mkdir(parents=True, exist_ok=True)
        incoming_path.write_bytes(incoming_bytes)
        incoming_sha = sha256_bytes(incoming_bytes)
        if sha256_bytes(incoming_path.read_bytes()) != incoming_sha:
            raise PacketError("incoming artifact verification failed")
        fault("after_incoming")
        if existed:
            rollback_path.parent.mkdir(parents=True, exist_ok=True)
            rollback_path.write_bytes(rollback_bytes)
            if sha256_bytes(rollback_path.read_bytes()) != rollback_sha:
                raise PacketError("rollback artifact verification failed")
        fault("after_rollback")
        diff_bytes = _diff_bytes(rollback_bytes if existed else None, incoming_bytes, managed_path)
        diff_path.write_bytes(diff_bytes)
        diff_sha = sha256_bytes(diff_bytes)
        if sha256_bytes(diff_path.read_bytes()) != diff_sha:
            raise PacketError("diff artifact verification failed")
        fault("after_diff")
        artifacts = {
            "packet": _artifact_relative(identity_value, "packet.json"),
            "local": _artifact_relative(identity_value, "local", managed_path) if existed else None,
            "incoming": _artifact_relative(identity_value, "incoming", managed_path),
            "rollback": _artifact_relative(identity_value, "rollback", managed_path) if existed else None,
            "diff": _artifact_relative(identity_value, "diff.patch"),
        }
        packet = {
            "schema_version": 1,
            "publication_status": "complete",
            "packet_id": identity_value,
            "managed_path": managed_path,
            "source_version": source_version,
            "target_version": target_version,
            "classification": classification,
            "baseline_sha256": baseline_sha256,
            "local_sha256": rollback_sha if existed else None,
            "incoming_sha256": incoming_sha,
            "diff_sha256": diff_sha,
            "rollback_sha256": rollback_sha,
            "local_existed": existed,
            "existed_before_upgrade": existed,
            "rollback_action": "restore_original_bytes" if existed else "delete_upgrade_created_file",
            "artifacts": artifacts,
            "resolution_status": resolution_status,
            "user_action": user_action,
        }
        fault("before_packet_json")
        (staging / "packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        validate_complete_packet(staging, expected_identity)
        fault("after_packet_json")

        if final_dir.exists():
            final_dir.rename(old)
            old_moved = True
        fault("after_old_rename")
        staging.rename(final_dir)
        published = True
        fault("after_publish")
        validate_complete_packet(final_dir, expected_identity)
        if on_publish is not None:
            on_publish(packet)
        # Commit point: canonical packet and both summaries have been published and
        # cross-validated by the callback. No later cleanup failure may roll them back.
        committed = True
    except Exception as exc:
        if committed:
            raise PacketError(f"packet post-commit failure: {exc}") from exc
        try:
            if published and final_dir.exists():
                shutil.rmtree(final_dir)
            if old_moved and old.exists():
                old.rename(final_dir)
                old_moved = False
        finally:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            if old.exists() and final_dir.exists():
                shutil.rmtree(old, ignore_errors=True)
        if isinstance(exc, PacketError):
            raise
        raise PacketError(f"packet publication failed at fixed root: {exc}") from exc
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
    if old_moved:
        try:
            cleanup(old)
            old_moved = False
        except OSError as exc:
            warn(
                f"packet committed; cleanup pending for non-canonical {old.name}: {exc}"
            )
    return packet
