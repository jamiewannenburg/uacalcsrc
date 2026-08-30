"""Allow `python -m jython_contracts` from tools/."""

from .cli import main

raise SystemExit(main())
