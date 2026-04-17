# Agent guide: Jython–Python 3 API parity

This document tells **what to build**, **where it lives**, and **how multiple agents coordinate** while the Rust code and `uacalc_lib` evolve.

## What you are implementing

1. **Behavioral source of truth:** Jython 2.7 calling the real Java classes under `org.uacalc.*` (classpath with the UACalc jars), as users’ legacy scripts did.
2. **Python 3 target:** The same *import paths and call shapes* (`org.uacalc...`), implemented by thin shims that delegate to `uacalc_lib` (Rust), plus camelCase aliases where Java had them.
3. **Proof:** Tests that compare outputs between **Jython+Java** and **CPython+`uacalc_lib`**, not only java_wrapper JSON subprocess tests.

## Canonical files

| File / directory | Role |
|------------------|------|
| `jython_comparison/parity_inventory.yaml` | **Auto-generated.** Inventory of Java types under `org/uacalc`, public-method heuristics, java_wrapper coverage, `python/org` shim flags. **Regenerate** after Java or wrapper changes. |
| `jython_comparison/parity_slices.yaml` | **Human-edited.** Work slices, owners, status, notes. **Claim a slice** here before large work. |
| `jython_comparison/scripts/generate_parity_inventory.py` | Script that rebuilds `parity_inventory.yaml`. |
| `python/org/uacalc/` | Compatibility package mirroring Java package names. Branch on Jython vs CPython as in `python/org/uacalc/alg/__init__.py`. |
| `python/uacalc/tests/` (and future `tests/parity/…`) | Pytest tests; add **golden** or **normalized** comparisons as described below. |

Legacy context: `jython_comparison/api_diff.md` and `jython_comparison/compatibility_plan.md`.

## Before you start (every agent)

1. Read **your slice** in `parity_slices.yaml` (`id`, `java_package_prefixes`, `depends_on`, `parity_tests_dir`).
2. Run `python jython_comparison/scripts/generate_parity_inventory.py` so `parity_inventory.yaml` matches current Java.
3. Set your slice to `in_progress`, set `owner`, and add a short `notes` line (branch name or PR). **Commit this update** with your work or in a tiny “claim” PR to avoid duplicate effort.

## Workflow per slice

1. **Shim surface:** Add or extend `python/org/uacalc/<…>/__init__.py` so that `import org.uacalc....` resolves on **CPython** and forwards to `uacalc_lib` with **camelCase** aliases on types that need them (see existing `monkey_patch_classes` in `alg`).
2. **Behavior:** Match Java/Jython semantics: method results, `str`/`repr` where scripts depend on `toString()`-style output, and exception behavior where tests assert it.
3. **Tests:**
   - **Unit / JSON parity:** Same idea as `python/uacalc/tests/test_*.py` + java_wrapper (good for coverage).
   - **Integration:** Add small scripts checked in under the slice’s `parity_tests_dir` (create the directory if missing) that run under **both** Jython and CPython, writing **normalized** output; compare to checked-in goldens or to a live Jython run in CI.
   - **Jython example alignment:** `python/uacalc/tests/test_jython_examples_parity.py` locks `jython_comparison/test_script.py` / `subreducts_mace4_stream.py` APIs against `uacalc_lib` and runs the parity manifest scripts (`validate_parity_slices`, `generate_parity_inventory`).
4. **Finish:** Update the slice status to `parity_golden` or `done` in `parity_slices.yaml`.

## Multi-agent rules (avoid merge pain)

- **One owner per slice** at a time (`parity_slices.yaml`). If a slice is too big, add a `workstreams:` entry with two ids and split responsibilities in **notes** (still one slice row, two named workstreams).
- **Merge boundaries:** Prefer separate packages under `python/org/uacalc/` and separate test files per slice. Touch **one slice** per PR when possible.
- **Large shared types:** If you must change a type used by another slice (e.g. `SmallAlgebra`), coordinate in **notes** and land the shared layer first; dependents update second.
- **Regenerate inventory** in the same PR when you add or rename Java classes or wrappers relevant to your slice.

## Commands

```text
# Regenerate machine-readable inventory (required after org/uacalc or java_wrapper edits)
python jython_comparison/scripts/generate_parity_inventory.py

# Optional: fail CI if inventory is missing or older than Java / wrappers / generator script
python jython_comparison/scripts/generate_parity_inventory.py --verify

# Confirm parity_slices.yaml java_package_prefixes match packages in the inventory
python jython_comparison/scripts/validate_parity_slices.py
```

## Normalization for cross-Python tests

Jython 2.7 and CPython 3 differ in `print`, `long`/`int`, and sometimes ordering. Put **cosmetic** fixes in test helpers (e.g. normalize line endings, sort lines when order is not specified by Java, stable formatting of integers). Keep normalization **small and documented** next to the tests.

## What “done” means

- Shims for the slice’s **documented** entry points import cleanly on CPython.
- Tests cover those entry points with parity vs Jython or vs java_wrapper where Jython is not in CI.
- `parity_slices.yaml` updated: `status`, `notes`, and `last_updated` if you add that field.

## Questions

Prefer extending this file with a short “Decisions” subsection in your PR when something is ambiguous (e.g. UI packages excluded from parity).
