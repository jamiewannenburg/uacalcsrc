# Parity task template (copy into a GitHub issue or PR description)

**Title:** Parity slice: `<slice id from parity_slices.yaml>`

## Goal

Bring `<java_package_prefixes>` to **shim_complete** or **parity_golden** per `jython_comparison/AGENTS_PARITY.md`.

## Scope

- Slice id:
- Java packages (from parity_slices):
- Out of scope:

## Workstreams (optional, matches `merge_rules` in `parity_slices.yaml`)

The `merge_rules` block in `parity_slices.yaml` is the contract—for example:

```yaml
merge_rules:
  - One active owner per slice (set owner to GitHub handle or initials).
  - Touch only this file and your slice directory under python/org/uacalc/... and tests.
  - After changing Java under org.uacalc or java_wrapper wrappers, regenerate parity_inventory.yaml.
  - Conflicts: if two agents need the same slice, split work by "workstream" notes or sub-slice id.
```

When two people share one slice without splitting the YAML row, use one slice id and name workstreams in **notes** (the `workstreams:` list is for short ids only):

- **Slice:** `core-alg-base`
- **workstreams:** e.g. `agent-a-bindings`, `agent-b-goldens` (both optional labels in YAML)
- **notes:** e.g. `agent-a: BasicAlgebra camelCase aliases; agent-b: tests/parity/alg goldens — branch xyz`

YAML shape (illustrative; keep `owner` singular per `merge_rules`):

```yaml
  - id: core-alg-base
    owner: agent-a
    status: in_progress
    workstreams:
      - agent-a-bindings
      - agent-b-goldens
    notes: >-
      agent-a: bindings + camelCase on SmallAlgebra; agent-b: tests/parity/alg goldens —
      coordinate on shared types before merge.
```

Follow **merge_rules**: one active **owner** field, separate test dirs where possible, and coordinate if you touch shared types (e.g. `SmallAlgebra`).

## Deliverables

- [ ] `python/org/uacalc/...` updates (CPython path + Jython branch if needed)
- [ ] camelCase aliases on bound types where the Java API uses them
- [ ] Tests under `parity_tests_dir` (or `python/uacalc/tests/…`) — Jython+CPython or java_wrapper JSON as appropriate
- [ ] `parity_inventory.yaml` regenerated if Java or `java_wrapper` changed
- [ ] `parity_slices.yaml`: `owner`, `status`, `notes` updated

## Verification

- [ ] `python jython_comparison/scripts/generate_parity_inventory.py --verify` passes after merge (if CI runs it)
- [ ] pytest target: `...`

## Links

- Branch:
- Related PRs:
