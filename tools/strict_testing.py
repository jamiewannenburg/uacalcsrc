"""Strict CI policy for guard skips vs allowed environment/slow/platform skips."""

from __future__ import annotations

from typing import Optional

import pytest

from strict_skip_policy import (  # noqa: E402
    ALLOWED_SKIP_PREFIXES,
    is_allowed_skip_reason,
    is_guard_skip_reason,
    is_strict,
)

__all__ = [
    "ALLOWED_SKIP_PREFIXES",
    "is_strict",
    "is_allowed_skip_reason",
    "is_guard_skip_reason",
    "guard_skip",
    "guard_import_skip",
    "pytest_configure",
]


def guard_skip(reason: str) -> None:
    if is_strict() and is_guard_skip_reason(reason):
        pytest.fail(f"Strict CI (UACALC_STRICT_TESTS): disallowed skip: {reason}")
    pytest.skip(reason)


def guard_import_skip(module_name: str, exc: Optional[BaseException] = None) -> None:
    msg = f"{module_name} not available"
    if exc is not None:
        msg = f"{msg}: {exc}"
    if is_strict():
        raise ImportError(msg) from exc
    pytest.skip(msg, allow_module_level=True)


class StrictSkipPlugin:
    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if not is_strict() or call.when != "call":
            return
        if report.skipped:
            reason = _skip_reason(report)
            if reason and is_guard_skip_reason(reason):
                report.outcome = "failed"
                report.longrepr = f"Strict CI: guard skip at runtime: {reason}"


def _skip_reason(report) -> str:
    longrepr = report.longrepr
    if isinstance(longrepr, tuple) and len(longrepr) >= 3:
        return str(longrepr[2])
    return str(longrepr or "")


def pytest_configure(config) -> None:
    if is_strict():
        config.pluginmanager.register(StrictSkipPlugin(), "uacalc_strict_skip")