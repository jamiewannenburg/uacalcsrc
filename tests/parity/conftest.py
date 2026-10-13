"""Import ``org.uacalc`` shims without shadowing the installed ``uacalc_lib`` wheel.

Pytest puts the repo root on ``sys.path``. That makes ``import uacalc_lib`` hit the
Rust crate directory (a PEP 420 namespace) instead of the extension module.
``python/`` must be on the path for ``org.uacalc``. ``python/uacalc_lib`` is the
real module only when a maturin ``.so``/``.pyd`` is present. On CI the wheel in
site-packages is the source of truth; tests must not require Jython.
"""

from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: import/structure checks")
    config.addinivalue_line("markers", "surface: public API surface checks")
    config.addinivalue_line("markers", "behavioral: exact functional parity with Java")


_REPO_ROOT = Path(__file__).resolve().parents[2]
_PYTHON_DIR = _REPO_ROOT / "python"
_LIB_DIR = _PYTHON_DIR / "uacalc_lib"
_python = str(_PYTHON_DIR)
_root = str(_REPO_ROOT)


def _has_native_extension(lib_dir: Path) -> bool:
    if not lib_dir.is_dir():
        return False
    return any(
        p.name.startswith("uacalc_lib") and p.suffix in {".so", ".pyd", ".dylib"}
        for p in lib_dir.iterdir()
    )


def _drop_unbound_uacalc_lib() -> None:
    """Drop a namespace-package or stub ``uacalc_lib`` so the next import can bind."""
    mod = sys.modules.get("uacalc_lib")
    if mod is None:
        return
    path = getattr(mod, "__file__", None)
    has_bindings = hasattr(mod, "alg") or hasattr(mod, "io") or hasattr(mod, "terms")
    if path is None or not has_bindings:
        to_drop = [
            name
            for name in list(sys.modules)
            if name == "uacalc_lib" or name.startswith("uacalc_lib.")
        ]
        for name in to_drop:
            sys.modules.pop(name, None)


if _python in sys.path:
    sys.path.remove(_python)

if _has_native_extension(_LIB_DIR):
    sys.path.insert(0, _python)
    _drop_unbound_uacalc_lib()
else:
    # Hide the crate dir and the stub python/uacalc_lib, import the wheel, then
    # put python/ first so org.uacalc resolves. The cached uacalc_lib stays the wheel.
    for p in (_root, "", "."):
        while p in sys.path:
            sys.path.remove(p)
    _drop_unbound_uacalc_lib()
    try:
        import uacalc_lib  # noqa: F401
    except ImportError:
        pass
    sys.path.insert(0, _python)
    if _root not in sys.path:
        sys.path.append(_root)
