#!/usr/bin/env python3
"""
Advanced UACalc Usage Examples

This file demonstrates advanced usage patterns for the UACalc Python API,
including large-scale computations, custom algebra construction, research
workflows, and performance optimization techniques.
"""

import uacalc
import time
import psutil
import os
import json
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
import glob
from pathlib import Path

def monitor_memory():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def benchmark_operation(operation_name: str, operation_func, *args, **kwargs):
    """Benchmark an operation and return timing and memory usage"""
    start_memory = monitor_memory()
    start_time = time.time()
    
    result = operation_func(*args, **kwargs)
    
    end_time = time.time()
    end_memory = monitor_memory()
    
    duration_ms = (end_time - start_time) * 1000
    memory_used = end_memory - start_memory
    
    print(f"{operation_name}: {duration_ms:.2f}ms, Memory: {memory_used:.1f}MB")
    return result, duration_ms, memory_used

# ============================================================================
# 1. Large-Scale Computations
# ============================================================================

def large_scale_congruence_analysis():
    """Demonstrate large-scale congruence analysis with progress reporting"""
    print("=== Large-Scale Congruence Analysis ===")
    
    # Create a larger algebra for demonstration
    # In practice, you would load this from a file
    algebra = uacalc.create_cyclic_group(8)
    print(f"Analyzing algebra: {algebra.name} (size: {algebra.cardinality})")
    
    # Progress callback for long-running operations
    def progress_callback(progress, message):
        print(f"Progress: {progress:.1%} - {message}")
    
    # Compute congruence lattice with progress reporting
    print("Computing congruence lattice...")
    lattice, duration, memory = benchmark_operation(
        "Lattice construction",
        uacalc.create_congruence_lattice_with_progress,
        algebra,
        progress_callback
    )
    
    print(f"Lattice computed: {lattice.size()} congruences")
    print(f"Atoms: {len(lattice.atoms())}")
    print(f"Coatoms: {len(lattice.coatoms())}")
    
    # Analyze lattice properties
    print("\nLattice analysis:")
    congruences = lattice.congruences()
    block_counts = [congruence.num_blocks for congruence in congruences]
    print(f"Block count distribution: {sorted(set(block_counts))}")
    
    # Find congruences with specific properties
    minimal_congruences = [c for c in congruences if c.num_blocks == algebra.cardinality - 1]
    print(f"Minimal congruences: {len(minimal_congruences)}")
    
    return lattice

def memory_optimized_computation():
    """Demonstrate memory optimization techniques for large computations"""
    print("\n=== Memory-Optimized Computation ===")
    
    # Monitor memory usage during computation
    initial_memory = monitor_memory()
    print(f"Initial memory: {initial_memory:.1f}MB")
    
    # Process algebras in batches to control memory usage
    algebra_files = glob.glob("resources/algebras/*.ua")[:5]  # Limit for demo
    
    results = []
    for i, file_path in enumerate(algebra_files):
        print(f"\nProcessing {file_path} ({i+1}/{len(algebra_files)})")
        
        # Load algebra
        algebra = uacalc.load_algebra(file_path)
        load_memory = monitor_memory()
        print(f"After loading: {load_memory:.1f}MB (+{load_memory - initial_memory:.1f}MB)")
        
        # Compute basic properties (memory-efficient)
        properties = {
            'name': algebra.name,
            'cardinality': algebra.cardinality,
            'operation_count': len(algebra.operations)
        }
        
        # Only compute lattice for smaller algebras
        if algebra.cardinality <= 6:
            try:
                lattice = uacalc.create_congruence_lattice(algebra)
                properties.update({
                    'lattice_size': lattice.size(),
                    'atoms': len(lattice.atoms())
                })
            except Exception as e:
                print(f"Lattice computation failed: {e}")
        
        results.append(properties)
        
        # Force garbage collection to free memory
        import gc
        gc.collect()
        
        current_memory = monitor_memory()
        print(f"After processing: {current_memory:.1f}MB")
    
    print(f"\nFinal memory: {monitor_memory():.1f}MB")
    return results

# ============================================================================
# 2. Custom Algebra Construction
# ============================================================================

def build_custom_algebra():
    """Demonstrate building algebras programmatically"""
    print("\n=== Custom Algebra Construction ===")
    
    # Example 1: Build a Boolean algebra from scratch
    print("Building Boolean algebra...")
    bool_algebra = uacalc.create_boolean_algebra()
    print(f"Boolean algebra: {bool_algebra.name}, size: {bool_algebra.cardinality}")
    
    # Example 2: Build a lattice from its Hasse diagram
    print("\nBuilding lattice from Hasse diagram...")
    # Define the lattice structure (example: M3 lattice)
    hasse_edges = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 4), (3, 4)]  # 0=bottom, 4=top
    lattice_algebra = uacalc.create_lattice_from_hasse(5, hasse_edges, "M3")
    print(f"Lattice algebra: {lattice_algebra.name}, size: {lattice_algebra.cardinality}")
    
    # Example 3: Build algebra from operation tables
    print("\nBuilding algebra from operation tables...")
    # Define a simple group operation table (cyclic group of order 3)
    operation_table = [
        [0, 1, 2],  # 0 * x
        [1, 2, 0],  # 1 * x
        [2, 0, 1]   # 2 * x
    ]
    
    custom_algebra = uacalc.create_algebra_from_table(
        "CustomGroup",
        ["*"],
        [operation_table]
    )
    print(f"Custom algebra: {custom_algebra.name}, size: {custom_algebra.cardinality}")
    
    # Verify the algebra properties
    print(f"Operations: {[op.symbol for op in custom_algebra.operations]}")
    
    return bool_algebra, lattice_algebra, custom_algebra

def validate_algebra_properties():
    """Demonstrate algebra property validation"""
    print("\n=== Algebra Property Validation ===")
    
    # Test various algebra types
    algebras = [
        ("Boolean", uacalc.create_boolean_algebra()),
        ("Cyclic3", uacalc.create_cyclic_group(3)),
        ("Cyclic4", uacalc.create_cyclic_group(4)),
    ]
    
    for name, algebra in algebras:
        print(f"\n{name} algebra properties:")
        
        # Check basic properties
        print(f"  Cardinality: {algebra.cardinality}")
        print(f"  Operations: {len(algebra.operations)}")
        
        # Check operation properties
        for op in algebra.operations:
            print(f"  {op.symbol}: arity {op.arity}")
            
            # Test some basic properties
            if op.arity == 2:
                # Check commutativity
                is_commutative = True
                for a in range(algebra.cardinality):
                    for b in range(algebra.cardinality):
                        if op.value([a, b]) != op.value([b, a]):
                            is_commutative = False
                            break
                    if not is_commutative:
                        break
                print(f"    Commutative: {is_commutative}")
                
                # Check associativity
                is_associative = True
                for a in range(algebra.cardinality):
                    for b in range(algebra.cardinality):
                        for c in range(algebra.cardinality):
                            left = op.value([op.value([a, b]), c])
                            right = op.value([a, op.value([b, c])])
                            if left != right:
                                is_associative = False
                                break
                        if not is_associative:
                            break
                    if not is_associative:
                        break
                print(f"    Associative: {is_associative}")

# ============================================================================
# 3. Research Workflow Examples
# ============================================================================

def batch_algebra_analysis():
    """Demonstrate batch analysis of multiple algebras"""
    print("\n=== Batch Algebra Analysis ===")
    
    # Find all algebra files
    algebra_files = glob.glob("resources/algebras/*.ua")
    print(f"Found {len(algebra_files)} algebra files")
    
    def analyze_single_algebra(file_path: str) -> Dict[str, Any]:
        """Analyze a single algebra file"""
        try:
            algebra = uacalc.load_algebra(file_path)
            
            # Basic properties
            result = {
                'file': file_path,
                'name': algebra.name,
                'cardinality': algebra.cardinality,
                'operation_count': len(algebra.operations),
                'success': True
            }
            
            # Try to compute congruence lattice for smaller algebras
            if algebra.cardinality <= 8:
                try:
                    lattice = uacalc.create_congruence_lattice(algebra)
                    result.update({
                        'lattice_size': lattice.size(),
                        'atoms': len(lattice.atoms()),
                        'coatoms': len(lattice.coatoms())
                    })
                except Exception as e:
                    result['lattice_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'file': file_path,
                'success': False,
                'error': str(e)
            }
    
    # Process algebras in parallel
    print("Processing algebras...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyze_single_algebra, algebra_files))
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Successfully analyzed: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("Failed files:")
        for result in failed:
            print(f"  {result['file']}: {result['error']}")
    
    # Generate statistics
    if successful:
        cardinalities = [r['cardinality'] for r in successful]
        print(f"\nCardinality statistics:")
        print(f"  Min: {min(cardinalities)}")
        print(f"  Max: {max(cardinalities)}")
        print(f"  Mean: {sum(cardinalities) / len(cardinalities):.1f}")
        
        # Lattice statistics
        lattice_results = [r for r in successful if 'lattice_size' in r]
        if lattice_results:
            lattice_sizes = [r['lattice_size'] for r in lattice_results]
            print(f"\nLattice size statistics:")
            print(f"  Min: {min(lattice_sizes)}")
            print(f"  Max: {max(lattice_sizes)}")
            print(f"  Mean: {sum(lattice_sizes) / len(lattice_sizes):.1f}")
    
    # Save results
    with open("batch_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def statistical_analysis():
    """Demonstrate statistical analysis of algebra properties"""
    print("\n=== Statistical Analysis ===")
    
    # Load analysis results
    try:
        with open("batch_analysis_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("No batch analysis results found. Run batch_algebra_analysis() first.")
        return
    
    # Filter successful results with lattice data
    lattice_results = [r for r in results if r['success'] and 'lattice_size' in r]
    
    if not lattice_results:
        print("No lattice data available for statistical analysis.")
        return
    
    # Create DataFrame for analysis
    df = pd.DataFrame(lattice_results)
    
    # Basic statistics
    print("Statistical summary:")
    print(df[['cardinality', 'lattice_size', 'height', 'width']].describe())
    
    # Correlation analysis
    print("\nCorrelations:")
    correlations = df[['cardinality', 'lattice_size', 'height', 'width']].corr()
    print(correlations)
    
    # Visualizations
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Cardinality vs Lattice Size
    axes[0, 0].scatter(df['cardinality'], df['lattice_size'])
    axes[0, 0].set_xlabel('Cardinality')
    axes[0, 0].set_ylabel('Lattice Size')
    axes[0, 0].set_title('Cardinality vs Lattice Size')
    
    # Height vs Width
    axes[0, 1].scatter(df['height'], df['width'])
    axes[0, 1].set_xlabel('Height')
    axes[0, 1].set_ylabel('Width')
    axes[0, 1].set_title('Height vs Width')
    
    # Lattice Size Distribution
    axes[1, 0].hist(df['lattice_size'], bins=10)
    axes[1, 0].set_xlabel('Lattice Size')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Lattice Size Distribution')
    
    # Cardinality Distribution
    axes[1, 1].hist(df['cardinality'], bins=10)
    axes[1, 1].set_xlabel('Cardinality')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Cardinality Distribution')
    
    plt.tight_layout()
    plt.savefig("algebra_statistics.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    return df

# ============================================================================
# 4. Performance Optimization Examples
# ============================================================================

def performance_profiling():
    """Demonstrate performance profiling and optimization"""
    print("\n=== Performance Profiling ===")
    
    # Test different algebra sizes
    sizes = [3, 5, 7, 10]
    results = []
    
    for size in sizes:
        print(f"\nTesting algebra size {size}")
        
        # Create test algebra
        algebra = uacalc.create_cyclic_group(size)
        
        # Profile Cg computation for all pairs
        def cg_all_pairs():
            for a in range(size):
                for b in range(a + 1, size):
                    algebra.cg(a, b)
        
        _, duration, memory = benchmark_operation(
            f"Cg all pairs (size {size})",
            cg_all_pairs
        )
        
        results.append({
            'size': size,
            'duration_ms': duration,
            'memory_mb': memory,
            'pairs': size * (size - 1) // 2
        })
    
    # Analyze performance scaling
    print("\nPerformance scaling analysis:")
    for i, result in enumerate(results):
        if i > 0:
            prev = results[i-1]
            size_ratio = result['size'] / prev['size']
            time_ratio = result['duration_ms'] / prev['duration_ms']
            print(f"Size {prev['size']} -> {result['size']}: "
                  f"time ratio = {time_ratio:.2f}x (theoretical: {size_ratio**3:.2f}x)")
    
    return results

def memory_profiling():
    """Demonstrate memory profiling techniques"""
    print("\n=== Memory Profiling ===")
    
    # Monitor memory during different operations
    initial_memory = monitor_memory()
    print(f"Initial memory: {initial_memory:.1f}MB")
    
    # Test memory usage for different algebra sizes
    for size in [3, 5, 7]:
        print(f"\nTesting memory usage for size {size}")
        
        # Create algebra
        algebra = uacalc.create_cyclic_group(size)
        after_create = monitor_memory()
        print(f"  After creating algebra: {after_create:.1f}MB (+{after_create - initial_memory:.1f}MB)")
        
        # Compute congruence lattice
        lattice = algebra.congruence_lattice()
        after_lattice = monitor_memory()
        print(f"  After lattice computation: {after_lattice:.1f}MB (+{after_lattice - after_create:.1f}MB)")
        
        # Compute all Cg pairs
        for a in range(size):
            for b in range(a + 1, size):
                algebra.cg(a, b)
        
        after_cg = monitor_memory()
        print(f"  After Cg computation: {after_cg:.1f}MB (+{after_cg - after_lattice:.1f}MB)")
        
        # Force garbage collection
        import gc
        gc.collect()
        after_gc = monitor_memory()
        print(f"  After garbage collection: {after_gc:.1f}MB")
        
        # Clean up
        del algebra, lattice
        gc.collect()
    
    final_memory = monitor_memory()
    print(f"\nFinal memory: {final_memory:.1f}MB")

def optimization_comparison():
    """Compare different optimization strategies"""
    print("\n=== Optimization Comparison ===")
    
    # Test algebra
    algebra = uacalc.create_cyclic_group(6)
    
    # Test 1: Standard computation
    print("Standard computation:")
    _, std_time, std_memory = benchmark_operation(
        "Standard Cg computation",
        lambda: algebra.cg(0, 1)
    )
    
    # Test 2: Batch computation
    print("\nBatch computation:")
    def batch_cg():
        results = []
        for a in range(algebra.cardinality):
            for b in range(a + 1, algebra.cardinality):
                results.append(algebra.cg(a, b))
        return results
    
    _, batch_time, batch_memory = benchmark_operation(
        "Batch Cg computation",
        batch_cg
    )
    
    # Test 3: Parallel computation (if available)
    print("\nParallel computation:")
    try:
        def parallel_cg():
            pairs = [(a, b) for a in range(algebra.cardinality) 
                    for b in range(a + 1, algebra.cardinality)]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(algebra.cg, a, b) for a, b in pairs]
                results = [future.result() for future in futures]
            return results
        
        _, parallel_time, parallel_memory = benchmark_operation(
            "Parallel Cg computation",
            parallel_cg
        )
        
        print(f"\nPerformance comparison:")
        print(f"Standard: {std_time:.2f}ms, {std_memory:.1f}MB")
        print(f"Batch: {batch_time:.2f}ms, {batch_memory:.1f}MB")
        print(f"Parallel: {parallel_time:.2f}ms, {parallel_memory:.1f}MB")
        
        if parallel_time > 0:
            print(f"Parallel speedup: {batch_time / parallel_time:.2f}x")
    
    except Exception as e:
        print(f"Parallel computation not available: {e}")

# ============================================================================
# 5. Integration Examples
# ============================================================================

def jupyter_integration_example():
    """Example of Jupyter notebook integration"""
    print("\n=== Jupyter Integration Example ===")
    
    # This would be used in a Jupyter notebook
    algebra = uacalc.load_algebra("resources/algebras/ba2.ua")
    
    # Create interactive visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Algebra properties
    axes[0, 0].text(0.1, 0.5, 
                   f"Name: {algebra.name}\n"
                   f"Cardinality: {algebra.cardinality}\n"
                   f"Operations: {len(algebra.operations)}",
                   fontsize=12, transform=axes[0, 0].transAxes,
                   verticalalignment='center')
    axes[0, 0].set_title("Algebra Properties")
    axes[0, 0].axis('off')
    
    # Operation table visualization
    if algebra.operations:
        op = algebra.operations[0]
        if op.arity == 2:
            table = np.zeros((algebra.cardinality, algebra.cardinality), dtype=int)
            for i in range(algebra.cardinality):
                for j in range(algebra.cardinality):
                    table[i, j] = op.value([i, j])
            
            im = axes[0, 1].imshow(table, cmap='viridis')
            axes[0, 1].set_title(f"Operation Table: {op.symbol}")
            plt.colorbar(im, ax=axes[0, 1])
    
    # Congruence lattice visualization
    try:
        lattice = algebra.congruence_lattice()
        block_counts = [congruence.num_blocks for congruence in lattice]
        
        axes[1, 0].hist(block_counts, bins=range(min(block_counts), max(block_counts) + 2))
        axes[1, 0].set_xlabel("Number of Blocks")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].set_title("Congruence Block Distribution")
        
        # Lattice properties
        axes[1, 1].text(0.1, 0.5,
                       f"Lattice Size: {len(lattice)}\n"
                       f"Join-Irreducibles: {len(lattice.join_irreducibles)}\n"
                       f"Height: {lattice.height}\n"
                       f"Width: {lattice.width}",
                       fontsize=12, transform=axes[1, 1].transAxes,
                       verticalalignment='center')
        axes[1, 1].set_title("Lattice Properties")
        axes[1, 1].axis('off')
        
    except Exception as e:
        axes[1, 0].text(0.5, 0.5, f"Lattice computation failed:\n{e}",
                       transform=axes[1, 0].transAxes,
                       horizontalalignment='center',
                       verticalalignment='center')
        axes[1, 0].set_title("Lattice Analysis")
    
    plt.tight_layout()
    plt.savefig("algebra_analysis.png", dpi=300, bbox_inches='tight')
    plt.show()

def pandas_integration():
    """Demonstrate pandas integration for data analysis"""
    print("\n=== Pandas Integration ===")
    
    # Create sample data
    data = []
    for size in [3, 4, 5, 6]:
        algebra = uacalc.create_cyclic_group(size)
        try:
            lattice = uacalc.create_congruence_lattice(algebra)
            data.append({
                'size': size,
                'lattice_size': lattice.size(),
                'atoms': len(lattice.atoms()),
                'coatoms': len(lattice.coatoms())
            })
        except Exception as e:
            data.append({
                'size': size,
                'error': str(e)
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print("Algebra analysis DataFrame:")
    print(df)
    
    # Statistical analysis
    if 'lattice_size' in df.columns:
        print("\nStatistical summary:")
        print(df.describe())
        
        # Correlation matrix
        numeric_cols = ['size', 'lattice_size', 'join_irreducibles', 'height', 'width']
        print("\nCorrelation matrix:")
        print(df[numeric_cols].corr())
    
    return df

# ============================================================================
# Main execution
# ============================================================================

def main():
    """Run all advanced usage examples"""
    print("UACalc Advanced Usage Examples")
    print("=" * 50)
    
    # Check if UACalc is available
    try:
        print(f"UACalc version: {uacalc.__version__}")
    except AttributeError:
        print("UACalc version not available")
    
    # Run examples
    try:
        # 1. Large-scale computations
        lattice = large_scale_congruence_analysis()
        memory_results = memory_optimized_computation()
        
        # 2. Custom algebra construction
        bool_algebra, lattice_algebra, custom_algebra = build_custom_algebra()
        validate_algebra_properties()
        
        # 3. Research workflows
        batch_results = batch_algebra_analysis()
        stats_df = statistical_analysis()
        
        # 4. Performance optimization
        perf_results = performance_profiling()
        memory_profiling()
        optimization_comparison()
        
        # 5. Integration examples
        jupyter_integration_example()
        pandas_df = pandas_integration()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
