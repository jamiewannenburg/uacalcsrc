"""
uacalc_lib - Rust extension module for UACalc.

This package contains the native Rust extension module and type stubs.
The actual implementation is provided by the Rust extension built by maturin.

During development (maturin develop), the native extension (.so/.pyd) will be
copied to this directory. The type stubs in __init__.pyi provide type information
for IDEs and type checkers.
"""

# For maturin's mixed rust/python pattern with PyO3:
# When we have an __init__.py, Python imports this file instead of the native extension.
# We need to explicitly load the native extension and expose its contents.

import sys
import importlib.util
from pathlib import Path

# Get the directory containing this __init__.py
_package_dir = Path(__file__).parent

# Try to find and load the native extension
# Maturin installs it with a platform-specific name (e.g., uacalc_lib.cp310-win_amd64.pyd)
_native_loaded = False

# Search for native extension files in the package directory
_extensions = list(_package_dir.glob('uacalc_lib.*.pyd')) + list(_package_dir.glob('uacalc_lib.*.so')) + list(_package_dir.glob('uacalc_lib.*.dylib'))

for ext_file in sorted(_extensions):
    try:
        # Load the native extension module directly
        spec = importlib.util.spec_from_file_location('uacalc_lib', ext_file)
        if spec and spec.loader:
            _native = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_native)
            # Replace this module's contents with the native extension's contents
            # This makes all submodules (alg, lat, terms, etc.) available
            for name in dir(_native):
                if not name.startswith('_') or name in ('__file__', '__name__', '__package__', '__doc__'):
                    setattr(sys.modules[__name__], name, getattr(_native, name))
            _native_loaded = True
            break
    except Exception:
        # Continue trying other files
        continue

# If native extension wasn't found locally, try importing it as if it were installed
# This handles the case where the package is installed via pip/maturin
if not _native_loaded:
    try:
        # Remove this module from sys.modules temporarily to allow importing the native extension
        _temp_module = sys.modules.pop(__name__, None)
        try:
            # Try to import the native extension directly
            # Python's import system should find it if it's installed
            import importlib
            _native = importlib.import_module('uacalc_lib')
            # If we got a different module (not this __init__.py), use it
            if _native.__file__ != __file__:
                sys.modules[__name__] = _native
                _native_loaded = True
        finally:
            # Restore this module if import failed
            if not _native_loaded and _temp_module is not None:
                sys.modules[__name__] = _temp_module
    except Exception:
        pass

# If native extension still wasn't found, the package will exist but won't have submodules
# This allows type checkers to work even if the extension isn't built yet

