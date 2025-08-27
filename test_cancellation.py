#!/usr/bin/env python3

import uacalc_rust
import time
import threading

def test_cancellation():
    """Test that cancellation works properly in congruence lattice construction."""
    
    # Create a much larger algebra that will take more time to process
    algebra = uacalc_rust.create_algebra("test", list(range(16)))  # 16-element algebra
    
    # Add a binary operation that will create more complex congruences
    # This creates a more complex operation table
    op_table = []
    for i in range(16):
        for j in range(16):
            op_table.append([i, j, (i + j) % 16])
    
    operation = uacalc_rust.create_operation("f", 2, op_table)
    algebra.add_operation("f", operation)
    
    # Create congruence lattice
    lattice = uacalc_rust.create_congruence_lattice(algebra)
    
    # Test the cancellation flag
    print(f"Initial cancellation state: {lattice.is_cancelled()}")
    
    # Set cancellation flag BEFORE starting construction
    print("Setting cancellation flag before construction...")
    lattice.set_cancelled()
    print(f"Cancellation state after setting: {lattice.is_cancelled()}")
    
    # Create a progress callback that will be cancelled
    progress_calls = []
    
    def progress_callback(progress, message):
        progress_calls.append(progress)
        print(f"Progress: {progress:.2f} - {message}")
        # Check cancellation state in callback
        print(f"Cancellation state in callback: {lattice.is_cancelled()}")
        time.sleep(0.01)  # Simulate some work
    
    # Set up the progress callback - this should fail due to cancellation
    try:
        lattice.with_progress_callback(progress_callback)
        print("ERROR: Progress callback setup should have failed due to cancellation")
        return False
    except uacalc_rust.CancellationError as e:
        print(f"✓ Progress callback setup correctly cancelled: {e}")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        return False

if __name__ == "__main__":
    success = test_cancellation()
    if success:
        print("✓ Cancellation test passed")
    else:
        print("✗ Cancellation test failed")
