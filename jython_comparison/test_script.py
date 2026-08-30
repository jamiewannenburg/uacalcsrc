# Backward-compatible entry point; prefer scripts/load_cyclic2.py.
import os
import runpy

_here = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(
    os.path.join(_here, "scripts", "load_cyclic2.py"),
    run_name="__main__",
)
