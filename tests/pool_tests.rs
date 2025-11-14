//! Tests for the Pool implementation

use uacalc::alg::parallel::Pool;
use std::sync::Arc;
use std::thread;
use uacalc::common::*;

#[test]
fn test_pool_initialization() {
    // Test that the pool can be initialized
    let runtime = Pool::fj_pool();
    assert!(Arc::strong_count(&runtime) >= 1);
}

#[test]
fn test_pool_singleton() {
    // Test that accessing the pool multiple times returns the same instance
    let runtime1 = Pool::fj_pool();
    let runtime2 = Pool::fj_pool();
    
    // Both should reference the same Arc
    assert!(Arc::ptr_eq(&runtime1, &runtime2));
}

#[test]
fn test_pool_thread_safety() {
    // Test that the pool can be accessed from multiple threads
    let handles: Vec<_> = (0..10)
        .map(|_| {
            thread::spawn(move || {
                let runtime = Pool::fj_pool();
                // Verify we got a valid runtime
                assert!(Arc::strong_count(&runtime) >= 1);
                runtime
            })
        })
        .collect();
    
    let runtimes: Vec<_> = handles
        .into_iter()
        .map(|h| h.join().unwrap())
        .collect();
    
    // All runtimes should be the same instance
    let first = &runtimes[0];
    for runtime in &runtimes[1..] {
        assert!(Arc::ptr_eq(first, runtime));
    }
}

#[test]
fn test_pool_java_comparison() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.PoolWrapper",
        ["get_pool"],
        || {
            let runtime = Pool::fj_pool();
            let initialized = Arc::strong_count(&runtime) > 0;
            // Java returns just the boolean value in the data field
            serde_json::json!(initialized)
        }
    );
}

#[test]
fn test_pool_is_initialized() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.PoolWrapper",
        ["is_initialized"],
        || {
            let _runtime = Pool::fj_pool();
            let initialized = true;
            // Java returns just the boolean value in the data field
            serde_json::json!(initialized)
        }
    );
}

#[test]
fn test_pool_comprehensive() {
    let config = TestConfig::default();
    
    compare_with_java!(
        config,
        "java_wrapper.src.alg.parallel.PoolWrapper",
        ["test"],
        || {
            let runtime1 = Pool::fj_pool();
            let runtime2 = Pool::fj_pool();
            let same_instance = Arc::ptr_eq(&runtime1, &runtime2);
            // Java returns JSON string in data field, so we need to match that structure
            // Java output: {"success": true, "data": "{\"initialized\":true,\"same_instance\":true}"}
            serde_json::json!({
                "initialized": true,
                "same_instance": same_instance
            })
        }
    );
}

