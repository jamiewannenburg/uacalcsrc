#!/usr/bin/env python3
"""Copy selected PhD scripts into tests/jython_scripts/phd (read-only source)."""
from __future__ import annotations

import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\u28409265\Documents\uacalc")
DST = REPO / "tests" / "jython_scripts" / "phd"
INPUT = DST / "input"

HEADER = """# CPython harness: copied from Jamie's PhD tree (read-only); path roots are relative to this file.
# Changes: none to logic; inputs live under tests/jython_scripts/phd/input/.
"""

BUNDLE: dict[str, list[str]] = {
    "rigorous_extension.py": [],
    "sugihara.py": [],
    "associativity_of_iff.py": ["dmm.py", "sugihara.py"],
    "check_crl.py": ["dmm.py"],
    "mace4.py": [],
    "twist.py": [],
    "isomorphism.py": [],
    "dmm.py": [],
}

INPUT_FILES = [
    "b2.ua",
    "s3.ua",
    "c4.ua",
    "c4_weaved.ua",
    "KR-1gen.model",
    "t3.model",
]


def main() -> int:
    INPUT.mkdir(parents=True, exist_ok=True)
    for name, deps in BUNDLE.items():
        src = SRC / name
        if not src.is_file():
            raise SystemExit(f"missing {src}")
        text = src.read_text(encoding="utf-8", errors="replace")
        if "CPython harness:" not in text:
            text = HEADER + text
        (DST / name).write_text(text, encoding="utf-8")
        for dep in deps:
            dep_src = SRC / dep
            if dep_src.is_file():
                dep_text = dep_src.read_text(encoding="utf-8", errors="replace")
                if "CPython harness:" not in dep_text:
                    dep_text = HEADER + dep_text
                (DST / dep).write_text(dep_text, encoding="utf-8")
    for fn in INPUT_FILES:
        for base in (SRC / "input", SRC):
            p = base / fn
            if p.is_file() and p.stat().st_size < 1024 * 1024:
                if fn.endswith(".model"):
                    shutil.copy2(p, DST / fn)
                else:
                    shutil.copy2(p, INPUT / fn)
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())