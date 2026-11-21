"""Repo-level pytest hooks (strict skip policy, shared with parity runs)."""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from strict_testing import pytest_configure  # noqa: E402