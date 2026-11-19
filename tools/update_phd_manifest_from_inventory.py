#!/usr/bin/env python3
"""Write phd/manifest.json from tools/phd_inventory.json."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INV = REPO / "tools" / "phd_inventory.json"
OUT = REPO / "tests" / "jython_scripts" / "phd" / "manifest.json"
PROBE = "probes/nullary_string_to_term.py"


def main() -> int:
    rows = json.loads(INV.read_text(encoding="utf-8"))
    entries: list[dict] = []
    # probe always included
    entries.append(
        {
            "path": PROBE,
            "argv": [],
            "xfail_cpython": {
                "reason": "Rust string_to_term accepts e(); Java/Jython golden rejects e()",
            },
        }
    )
    for row in rows:
        name = row["script"]
        argv = row.get("argv_default") or []
        st = row["status"]
        if name == Path(PROBE).name:
            continue
        if st == "not-applicable":
            entries.append(
                {
                    "path": name,
                    "argv": argv,
                    "skip_cpython": "not-applicable",
                    "skip_jython_golden": "not-applicable",
                }
            )
            continue
        if st == "syntax-jython2":
            entries.append(
                {
                    "path": name,
                    "argv": argv,
                    "skip_cpython": "syntax-jython2-vs-py3",
                    "skip_jython_golden": "syntax-jython2-vs-py3",
                }
            )
            continue
        if st == "slow":
            entries.append(
                {
                    "path": name,
                    "argv": argv,
                    "slow": True,
                    "skip_cpython": "jython probe exceeded 30s",
                    "skip_jython_golden": "jython probe exceeded 30s",
                }
            )
            continue
        if st == "fast-ok":
            ent = {"path": name, "argv": argv, "slow": False}
            if name in ("mace4.py", "filter2sa_mace4.py") or any(
                a.endswith(".model") for a in argv
            ):
                ent["cwd_model"] = True
            entries.append(ent)
            continue
        cat = row.get("error_category") or "jython-error"
        entries.append(
            {
                "path": name,
                "argv": argv,
                "skip_cpython": f"jython-error: {cat}",
                "skip_jython_golden": f"jython-error: {cat}",
            }
        )
    OUT.write_text(json.dumps({"scripts": entries}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())