#!/usr/bin/env python3
"""Preflight checks before pytest (java wrappers built, extension importable)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = _repo_root()
    errors: list[str] = []

    wrapper_classes = root / "java_wrapper" / "build" / "classes"
    if not wrapper_classes.is_dir():
        errors.append(
            "java_wrapper not built: run `ant compile-wrappers` "
            f"(missing {wrapper_classes})"
        )

    dist_classes = root / "build" / "classes"
    if not dist_classes.is_dir():
        errors.append(
            "Java main classes missing: run `ant compile-wrappers` "
            f"(missing {dist_classes})"
        )

    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        errors.append("JAVA_HOME is not set (JDK 8+ required for wrapper tests)")

    try:
        import uacalc_lib  # noqa: F401
    except ImportError as exc:
        errors.append(
            f"uacalc_lib not importable ({exc}): run "
            "`pip install -e '.[test,drawing]'` and `maturin develop --release`"
        )

    if errors:
        print("Test environment check FAILED:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print("Test environment OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())