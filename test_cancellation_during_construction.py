#!/usr/bin/env python3

import uacalc_rust
import time
import threading

def test_cancellation_during_construction():
    """Test that cancellation works during actual lattice construction."""
    
    # Create a large algebra that will take time to process
    algebra = uacalc_rust.create_algebra("test", list(range(12)))  # 12-element algebra
    
    # Add a binary operation that will create complex congruences
    op_table = []
    for i in range(12):
        for j in range(12):
            op_table.append([i, j, (i * j) % 12])  # Multiplication mod 12
    
    operation = uacalc_rust.create_operation("f", 2, op_table)
    algebra.add_operation("f", operation)
    
    # Create congruence lattice
    lattice = uacalc_rust.create_congruence_lattice(algebra)
    
    # Create a progress callback
    progress_calls = []
    
    def progress_callback(progress, message):
        progress_calls.append(progress)
        print(f"Progress: {progress:.2f} - {message}")
        time.sleep(0.01)  # Simulate some work
    
    # Set up the progress callback
    lattice.with_progress_callback(progress_callback)
    
    # Start the lattice construction in a separate thread
    construction_complete = threading.Event()
    construction_error = None
    
    def build_lattice():
        nonlocal construction_error
        try:
            # This should trigger the progress callback during construction
            congruences = lattice.congruences()
            print(f"Number of congruences: {len(congruences)}")
        except Exception as e:
            construction_error = e
        finally:
            construction_complete.set()
    
    # Start construction
    thread = threading.Thread(target=build_lattice)
    thread.start()
    
    # Wait a bit and then cancel
    time.sleep(0.2)
    print("Cancelling operation during construction...")
    lattice.set_cancelled()
    
    # Wait for construction to complete
    thread.join(timeout=5.0)
    
    if construction_error:
        if isinstance(construction_error, uacalc_rust.CancellationError):
            print(f"✓ Construction was cancelled as expected: {construction_error}")
            return True
        else:
            print(f"✗ Unexpected error: {construction_error}")
            return False
    else:
        print("✗ Construction completed without cancellation")
        return False

if __name__ == "__main__":
    success = test_cancellation_during_construction()
    if success:
        print("✓ Cancellation during construction test passed")
    else:
        print("✗ Cancellation during construction test failed")
