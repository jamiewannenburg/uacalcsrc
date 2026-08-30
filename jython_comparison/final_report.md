# Final report: Python–Jython compatibility (UACalc)

This file is a **snapshot** of progress, not a claim that every `org.uacalc.*` surface matches legacy Jython behavior.

## What exists today

1. **`python/org/uacalc/`** mirrors Java package names so scripts can use `import org.uacalc...` on CPython (via `uacalc_lib`) and on Jython (classpath) where packages exist.
2. **Shims** delegate to `uacalc_lib` on CPython and re-export public names; some submodules are still empty stubs until Rust bindings grow.
3. **`jython_comparison/run_comparison.py`** runs a chosen script under Jython and under CPython and compares normalized stdout (default script: `jython_comparison/test_script.py`).
4. **Parity tooling:** `parity_slices.yaml` (human), `parity_inventory.yaml` (generated), `validate_parity_slices.py`, and `generate_parity_inventory.py` coordinate multi-agent work. Status values and owners live in `parity_slices.yaml`.
5. **Tests:** `tests/parity/*` golden and shim smoke tests; `python/uacalc/tests/test_jython_examples_parity.py` locks example APIs and runs inventory validation helpers.

## Not done / in flight

- **`uacalc_lib.types`** is a placeholder Rust module; `org.uacalc.types` tracks it under the `core-util` workstream but may export nothing until stubs are implemented.
- **Swing / NetBeans UI** packages are **out of scope** for the parity slice manifest (not listed in `parity_slices.yaml`).
- **String-level parity** (`repr` / `toString`) and **full alias coverage** across all types are ongoing where tests do not yet enforce them; some slices still have richer behavior on Jython than on CPython until Rust exposes matching types.

## How to verify locally

```text
python jython_comparison/scripts/validate_parity_slices.py
python jython_comparison/scripts/generate_parity_inventory.py --verify
pytest python/uacalc/tests/test_jython_examples_parity.py -q
```

Rebuild `uacalc_lib` (wheel) before pytest if you changed Rust bindings.
