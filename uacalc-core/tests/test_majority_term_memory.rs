// Test file for memory limit functionality


#[test]
fn test_memory_limit_functionality() -> Result<(), Box<dyn std::error::Error>> {
    use uacalc_core::memory::{set_memory_limit, would_exceed_limit, reset_memory_limit};
    
    println!("Testing memory limit functionality...");
    
    // Test that we can set a memory limit
    set_memory_limit(1024 * 1024).unwrap(); // 1MB limit
    
    // Test that would_exceed_limit works
    assert!(!would_exceed_limit(512 * 1024), "512KB should not exceed 1MB limit");
    assert!(would_exceed_limit(2 * 1024 * 1024), "2MB should exceed 1MB limit");
    
    println!("✓ Memory limit functionality is working correctly");
    
    // Reset memory limit to default to avoid affecting other tests
    reset_memory_limit().unwrap();
    
    Ok(())
}
