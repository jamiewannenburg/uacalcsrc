use uacalc::resource::{alloc_i32_table, clear_cancel, set_memory_limit, UaError};

#[test]
fn huge_table_returns_memory_error_not_panic() {
    clear_cancel();
    set_memory_limit(Some(1024));
    let err = alloc_i32_table(10000, 3).unwrap_err();
    assert!(matches!(err, UaError::Memory { .. }));
}

#[test]
fn checked_pow_overflow_is_memory_error() {
    clear_cancel();
    set_memory_limit(None);
    let err = alloc_i32_table(usize::MAX, 32).unwrap_err();
    assert!(matches!(err, UaError::Memory { .. }));
}