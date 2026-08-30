# Jython Compatibility Contracts

Declarative contracts describing the Java/Jython API surface that the
`python/org/` compatibility shim must provide so existing Jython scripts can
run against the Rust/`uacalc_lib` bindings.

## Hierarchy

Contracts are **hierarchical**: package and/or file (one Java public type).

Resolution is **most general → most refined**; the more refined contract wins
on conflicts (status, notes, surface fields).

Examples:

| File | Level | Role |
|------|-------|------|
| `org.uacalc.io.yaml` | package | Whole small package (`AlgebraIO` facade) |
| `org.uacalc.alg.yaml` | package | Thin index only — `.alg` is too large for one surface |
| `org.uacalc.alg.BasicAlgebra.yaml` | file | Per-class aliases / parity |
| `org.uacalc.alg.SmallAlgebra.yaml` | file | Per-class aliases / parity |

Lookup for `org.uacalc.alg.BasicAlgebra`:

1. Load package contract `org.uacalc.alg` (if present)
2. Load file contract `org.uacalc.alg.BasicAlgebra` (if present)
3. Merge; file wins

A package marked `ignored` covers all types under it unless a more refined
contract overrides.

**Large packages** (especially `org.uacalc.alg`) should use **file-level**
contracts. Package-level contracts there should stay thin (re-export notes /
shared policy), not hold the full alias map. Coarse package contracts may be
split or rewritten as the hierarchy settles.

## Schema

```yaml
target: org.uacalc.alg.BasicAlgebra   # FQCN or package
level: file                           # package | file
status: pending                       # pending | implemented | ignored
java_source: org/uacalc/alg/BasicAlgebra.java
notes: ""
ignore_reason: null                   # required when status=ignored
surface:
  package_export: true
  aliases:
    getUniverseList: get_universe_list
  static_methods: []                  # e.g. AlgebraIO.readAlgebraFile
  str_parity: false                   # __str__/__repr__ vs Java toString
testing:
  notes: |
    Free-form recipe: how to exercise this surface and what to observe.
  task_refs: []                       # optional tasks/*.md Testing Strategy links
  scripts:
    - path: jython_comparison/scripts/load_cyclic2.py
      covers:                         # symbols this script is meant to exercise
        - getName
        - getUniverseList
      ignore_lines:                   # stdout prefixes skipped in dual-runtime diff
        - "Universe:"
```

Implementation remains hand-written under `python/org/`. Contracts are the
source of truth for **tracking**, **`validate`**, and **parity script coverage**.

### Testing / parity scripts

Goal: a growing set of dual-runtime `.py` files under
`jython_comparison/scripts/` that:

1. Import only the Jython-style `org.uacalc.*` API
2. Print deterministic, comparable stdout
3. Together cover all **declared** public-facing symbols on contracts
   (`surface.aliases`, `surface.static_methods`, and `__str__` when
   `str_parity: true`)

Run them with:

```bash
python3 jython_comparison/run_comparison.py
```

That runner loads every `testing.scripts` entry from contracts and diffs
Jython vs CPython output (honoring `ignore_lines`).

**Note on existing docs:** `tasks/*.md` contain Rust/Python/Java **port**
testing strategies, not Jython dual-runtime recipes. `jython_comparison/*.md`
described the high-level approach and had a single shared script. Put
Jython-specific how-to-test text in `testing.notes` (and optional
`task_refs` when a task's strategy is still useful).

## CLI

From the repo root (requires PyYAML):

```bash
python3 tools/jython_contracts_cli.py status
python3 tools/jython_contracts_cli.py status --packages --status pending
python3 tools/jython_contracts_cli.py init org.uacalc.lat
python3 tools/jython_contracts_cli.py init org.uacalc.alg.FreeAlgebra
python3 tools/jython_contracts_cli.py set-status org.uacalc.ui ignored --reason "GUI not in scope"
python3 tools/jython_contracts_cli.py inspect org.uacalc.alg.BasicAlgebra
python3 tools/jython_contracts_cli.py show org.uacalc.alg.BasicAlgebra
python3 tools/jython_contracts_cli.py validate
python3 tools/jython_contracts_cli.py coverage -v
```

Or: `python3 -m jython_contracts …` with `PYTHONPATH=tools`.

| Command | Purpose |
|---------|---------|
| `status` | List Java public types (excludes `ui`/`nbui` by default) with effective status |
| `init` | Scaffold a contract YAML |
| `set-status` | Update status (`--reason` required for `ignored`) |
| `inspect` | Location, Javadoc, public API, usage examples, binding hint |
| `show` | Print effective merged contract |
| `validate` | Check contracts against `python/org/` shims and script paths |
| `coverage` | Which declared surface symbols are listed in `testing.scripts.covers` |

## Migration notes

The previous de-facto contracts were the ad-hoc shims in `python/org/`:

- `org.uacalc.io` — package-level `AlgebraIO.readAlgebraFile` (kept as package contract)
- `org.uacalc.alg` — package-wide monkey-patch of `SmallAlgebra` / `BasicAlgebra` aliases

That **`.alg` package surface was too coarse** and has been remade as
**file-level** contracts for `BasicAlgebra` and `SmallAlgebra`, with a thin
`org.uacalc.alg.yaml` package index. The shim
`python/org/uacalc/alg/__init__.py` now applies aliases via a per-class map
aligned with those file contracts.

Expect further contract splits as more classes gain aliases or `__str__`
parity requirements. Expand `jython_comparison/scripts/` until `coverage`
reports full surface coverage for every implemented contract.
