#!/usr/bin/env python3
"""Entry point for the Jython compatibility contracts CLI."""

import sys
from pathlib import Path

# Allow running as a script without installing the package
_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from jython_contracts.cli import main

if __name__ == "__main__":
    sys.exit(main())
