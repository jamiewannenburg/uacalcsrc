# Parity task template (copy into a GitHub issue or PR description)

**Title:** Parity slice: `<slice id from parity_slices.yaml>`

## Goal

Bring `<java_package_prefixes>` to **shim_complete** or **parity_golden** per `jython_comparison/AGENTS_PARITY.md`.

## Scope

- Slice id:
- Java packages (from parity_slices):
- Out of scope:

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
