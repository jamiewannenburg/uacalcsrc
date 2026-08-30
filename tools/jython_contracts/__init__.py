"""Jython compatibility contracts CLI package."""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = TOOLS_DIR.parent
CONTRACTS_DIR = PROJECT_ROOT / "jython_contracts"
JAVA_ROOT = PROJECT_ROOT / "org" / "uacalc"
ORG_SHIM_ROOT = PROJECT_ROOT / "python" / "org" / "uacalc"

DEFAULT_EXCLUDE_PACKAGES = frozenset({"ui", "nbui"})
VALID_STATUSES = frozenset({"pending", "implemented", "ignored"})
VALID_LEVELS = frozenset({"package", "file"})

__all__ = [
    "PROJECT_ROOT",
    "CONTRACTS_DIR",
    "JAVA_ROOT",
    "ORG_SHIM_ROOT",
    "DEFAULT_EXCLUDE_PACKAGES",
    "VALID_STATUSES",
    "VALID_LEVELS",
]
