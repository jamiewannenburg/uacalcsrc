"""Ensure CPython tests import the maturin-built ``uacalc_lib``, not the Rust crate dir."""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: import/structure checks")
    config.addinivalue_line("markers", "surface: public API surface checks")
    config.addinivalue_line("markers", "behavioral: exact functional parity with Java")


_REPO_ROOT = Path(__file__).resolve().parents[2]
_PYTHON_DIR = _REPO_ROOT / "python"

# Prefer python/ over the repo root so `uacalc_lib` is the extension module.
_python = str(_PYTHON_DIR)
if sys.path[:1] != [_python]:
    if _python in sys.path:
        sys.path.remove(_python)
    sys.path.insert(0, _python)

# Drop a previously imported namespace package that shadows the extension.
_mod = sys.modules.get("uacalc_lib")
if _mod is not None and getattr(_mod, "__file__", None) is None:
    to_drop = [name for name in list(sys.modules) if name == "uacalc_lib" or name.startswith("uacalc_lib.")]
    for name in to_drop:
        sys.modules.pop(name, None)
