"""Build sys.modules['dmm'] from Jamie's dmm.py with Jython/Java preamble stripped."""
from __future__ import annotations

import re
import sys
import types
from pathlib import Path

_PHD_ROOT = Path(__file__).resolve().parents[1] / "phd_runtime"
_LOADED = False


def _jython2_patches(source: str) -> str:
    out_lines = []
    for line in source.splitlines():
        m = re.match(r"^(\s*)print\s+(.+)$", line)
        if m and "print(" not in line.lstrip()[:6]:
            line = f"{m.group(1)}print({m.group(2)})"
        out_lines.append(line)
    source = "\n".join(out_lines)
    if source and not source.endswith("\n"):
        source += "\n"
    source = source.replace(".iteritems()", ".items()")
    source = source.replace(".iterkeys()", ".keys()")
    source = source.replace(".itervalues()", ".values()")
    source = re.sub(
        r"^(\s*)except\s+(\w+)\s*,\s*(\w+)\s*:",
        r"\1except \2 as \3:",
        source,
        flags=re.MULTILINE,
    )
    source = re.sub(r"=\s*map\(([^)\n]+)\)", r"= list(map(\1))", source)
    source = re.sub(r"\+\s*map\(([^)\n]+)\)", r"+ list(map(\1))", source)
    return source


def _strip_jython_preamble(source: str) -> str:
    drop_substrings = (
        'sys.path.append("uacalc.jar")',
        'sys.path.append("LatDraw.jar")',
        "from java.lang import",
        "from java.io import",
        "class NoOutputStream",
        "def write(self, b, off, len)",
        "oldOut = System.out",
        "System.setOut",
        "sys.stdout = oldOut",
    )
    out: list[str] = []
    for line in source.splitlines(keepends=True):
        if any(s in line for s in drop_substrings):
            continue
        out.append(line)
    return "".join(out)


def ensure_dmm_loaded() -> None:
    global _LOADED
    if _LOADED and "dmm" in sys.modules:
        return
  # org.uacalc and pyparsing must resolve before dmm body runs
    import org.uacalc.alg  # noqa: F401
    import org.uacalc.io  # noqa: F401

    vendor = _PHD_ROOT.parent / "_vendor"
    repo_python = _PHD_ROOT.parents[2] / "python"
    for p in (str(vendor), str(repo_python), str(repo_python / "uacalc_lib")):
        if p not in sys.path:
            sys.path.insert(0, p)

    raw = (_PHD_ROOT / "dmm.py").read_text(encoding="utf-8", errors="replace")
    src = _jython2_patches(_strip_jython_preamble(raw))
    mod = types.ModuleType("dmm")
    mod.__file__ = str(_PHD_ROOT / "dmm.py")
    mod.__package__ = ""
    exec(compile(src, str(_PHD_ROOT / "dmm.py"), "exec"), mod.__dict__)  # noqa: S102
    sys.modules["dmm"] = mod
    _LOADED = True