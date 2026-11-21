"""
uacalc_lib - Rust extension module for UACalc.

This package contains the native Rust extension module and type stubs.
The actual implementation is provided by the Rust extension built by maturin.

During development (maturin develop), the native extension (.so/.pyd) will be
copied to this directory. The type stubs in __init__.pyi provide type information
for IDEs and type checkers.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

# For maturin's mixed rust/python pattern with PyO3:
# When we have an __init__.py, Python imports this file instead of the native extension.
# We need to explicitly load the native extension and expose its contents.

_package_dir = pathlib.Path(__file__).resolve().parent
_native_loaded = False


def _abi_tag() -> str:
    vi = sys.version_info
    return f"cp{vi.major}{vi.minor}"


def _find_repo_root(start: pathlib.Path) -> pathlib.Path | None:
    for directory in (start, *start.parents):
        if (directory / "pyproject.toml").is_file() and (directory / "uacalc_lib" / "Cargo.toml").is_file():
            return directory
    return None


def _extension_candidates() -> list[pathlib.Path]:
    """Return native modules to try, newest first.

  - Always consider extensions co-located with this ``__init__.py`` (wheel / editable install).
  - Also consider ``python/uacalc_lib`` under a repo root only when this package lives inside
    that checkout (local ``maturin develop``). Installed site-packages trees do not walk up to
    an unrelated checkout, so CI and normal ``pip install`` never load a stray repo ``.pyd``.
    Set ``UACALC_LIB_DEVELOP=1`` to force the repo ``python/uacalc_lib`` directory when needed.
    """
    import os

    tag = _abi_tag()
    patterns = (
        f"uacalc_lib.{tag}-*.pyd",
        f"uacalc_lib.{tag}-*.so",
        f"uacalc_lib.{tag}-*.dylib",
        "uacalc_lib.*.pyd",
        "uacalc_lib.*.so",
        "uacalc_lib.*.dylib",
    )
    roots = [_package_dir]
    repo = _find_repo_root(_package_dir)
    if repo is not None:
        dev_native = repo / "python" / "uacalc_lib"
        if dev_native.is_dir() and dev_native.resolve() != _package_dir.resolve():
            roots.append(dev_native)
    elif os.environ.get("UACALC_LIB_DEVELOP") == "1":
        forced = pathlib.Path(os.environ.get("UACALC_LIB_REPO", ".")).resolve() / "python" / "uacalc_lib"
        if forced.is_dir():
            roots.append(forced)

    seen: set[pathlib.Path] = set()
    matches: list[pathlib.Path] = []
    for root in roots:
        for pattern in patterns:
            for path in root.glob(pattern):
                key = path.resolve()
                if key in seen:
                    continue
                seen.add(key)
                matches.append(path)
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches


_stdlib_modules = frozenset({"importlib", "sys"})

for ext_file in _extension_candidates():
    try:
        spec = importlib.util.spec_from_file_location("uacalc_lib", ext_file)
        if not (spec and spec.loader):
            continue
        _package = sys.modules[__name__]
        _held = sys.modules.pop(__name__, None)
        try:
            _native = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_native)
            for name in dir(_native):
                if name in _stdlib_modules:
                    continue
                if not name.startswith("_") or name in (
                    "__file__",
                    "__name__",
                    "__package__",
                    "__doc__",
                ):
                    setattr(_package, name, getattr(_native, name))
            _native_loaded = True
            break
        finally:
            sys.modules[__name__] = _package
            if _held is not None and _held is not _package:
                pass  # keep the live package in sys.modules
    except Exception:
        continue

if _native_loaded:
    _pkg = sys.modules[__name__]
    for _leak in (
        "_native",
        "_temp_module",
        "_held",
        "_package",
        "_stdlib_modules",
        "importlib",
        "sys",
        "pathlib",
        "importlib.util",
    ):
        _pkg.__dict__.pop(_leak, None)

if not _native_loaded:
    try:
        _temp_module = sys.modules.pop(__name__, None)
        try:
            import importlib

            _native = importlib.import_module("uacalc_lib")
            if getattr(_native, "__file__", None) != __file__:
                sys.modules[__name__] = _native
                _native_loaded = True
        finally:
            if not _native_loaded and _temp_module is not None:
                sys.modules[__name__] = _temp_module
    except Exception:
        pass