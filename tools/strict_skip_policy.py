"""Skip classification helpers (no pytest dependency)."""

from __future__ import annotations

import os
import re

STRICT_ENV = "UACALC_STRICT_TESTS"

ALLOWED_SKIP_PREFIXES = (
    "Environment:",
    "slow:",
    "platform:",
    "optional:",
)

_GUARD_PATTERNS = re.compile(
    r"|".join(
        re.escape(s)
        for s in (
            "uacalc_lib",
            "not available",
            "missing",
            "not found",
            "not on path",
            "not checked in",
            "fixture missing",
            "could not load",
            "no test algebra",
            "type stub file",
            "cyclic2.ua",
            "cyclic3.ua",
            ".ua not found",
            "algebra file",
            "java wrapper",
            "native extension",
            "not bound",
            "not in this build",
            "golden_io",
            "mace4",
            "resources/special",
            "invalid_parity",
            "multi-algebra",
            "compare_stdout",
            "skip_cpython",
            "skip_jython_golden",
            "JAVA_HOME not set",
        )
    ),
    re.IGNORECASE,
)


def is_strict() -> bool:
    return os.environ.get(STRICT_ENV) == "1"


def is_allowed_skip_reason(reason: str) -> bool:
    reason = (reason or "").strip()
    return any(reason.startswith(p) for p in ALLOWED_SKIP_PREFIXES)


def is_guard_skip_reason(reason: str) -> bool:
    reason = (reason or "").strip()
    if not reason:
        return True
    if is_allowed_skip_reason(reason):
        return False
    return bool(_GUARD_PATTERNS.search(reason))