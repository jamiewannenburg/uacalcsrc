"""
UACalc Python Package

This package provides Python bindings for the Universal Algebra Calculator (UACalc).
"""

try:
    import uacalc_lib
except ImportError:
    raise ImportError(
        "uacalc_lib module not found. Please ensure the Rust extension module is built and installed."
    )

# Re-export all modules from uacalc_lib
from uacalc_lib import *

__version__ = "0.0.2"
__author__ = "UACalc Contributors"
__license__ = "MIT"
