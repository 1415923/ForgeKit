"""Shared ForgeKit version reader.

Reads the canonical ForgeKit version from the VERSION file located in
the ForgeKit root (the repository that contains this script).  Every
Python tool that needs the current ForgeKit version should import
`get_version()` from here rather than hardcoding a literal string.

Usage:
    from forgekit_version import get_version
    version = get_version()   # "0.43.2"
"""

from pathlib import Path


def _forgekit_root():
    """Return the ForgeKit repository root."""
    return Path(__file__).resolve().parents[1]


def get_version():
    """Return the current ForgeKit version string."""
    version_path = _forgekit_root() / "VERSION"
    if not version_path.is_file():
        raise RuntimeError(
            "VERSION file not found at ForgeKit root. "
            "Run from a ForgeKit repository and ensure VERSION exists."
        )
    return version_path.read_text(encoding="utf-8").strip()
