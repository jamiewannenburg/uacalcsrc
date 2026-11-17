# Rust gaps

Parity tests that fail because `uacalc` / `uacalc_lib` is missing logic
(stubs, unbound parallel workers, incomplete searches) are marked
`pytest.mark.xfail(..., strict=True)` with a reason that **starts with**
`Rust gap:`. They are kept separate from Java-bug / Java-limitation xfails.

This file lists each such gap: Rust location, what is missing, and the
test(s) that surface it.

## Current gaps from leftover wraps

None. Newly wrapped methods in this round either match Java on the
fixtures we have, or are left unbound on purpose (GUI `ProgressReport` /
latdraw, Groovy `makeOperationFromScript`, `Terms.testFlatten`,
`BasicPartition` SubProduct/Term overloads).

`Closer.doOneStagePartialClosure` is wrapped for Java's early exits
(empty `rawList` → `IndexOutOfBoundsException`, `numOfOps == 0` no-op,
null `termMap` → `NullPointerException`). The parallel worker body is
not bound in Rust (`src/alg/closer.rs` / `uacalc_lib` `Closer`); there
is no success-path fixture that reaches it without hitting those Java
exceptions first, so there is no `Rust gap:` xfail yet.

## Platform notes (not Rust-gap xfails)

On Windows, `malcev_term_rand_bin` and `hagemann_mitschke_rand_bin`
(size-3 magma seed 11, F(2)=409) exceed the 120s search timeout that
Linux CI meets. They are Windows-only xfails, not `Rust gap:` entries.
