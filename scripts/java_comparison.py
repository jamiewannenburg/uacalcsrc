#!/usr/bin/env python3
"""
Java-Rust UACalc Comparison Harness

This script provides comprehensive comparison between Java UACalc and Rust implementation
for correctness verification and performance benchmarking.
"""

import json
import subprocess
import sys
import time
import os
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import hashlib
from dataclasses import dataclass, asdict
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ComparisonResult:
    """Result of comparing Java vs Rust operations"""
    operation: str
    algebra_file: str
    java_time_ms: float
    rust_time_ms: float
    speedup: float
    memory_java_mb: Optional[float] = None
    memory_rust_mb: Optional[float] = None
    memory_improvement: Optional[float] = None
    correctness_match: bool = True
    error_message: Optional[str] = None

@dataclass
class AlgebraProperties:
    """Basic properties of an algebra for comparison"""
    name: str
    cardinality: int
    operation_count: int
    operation_symbols: List[str]
    operation_arities: List[int]
    java_memory_mb: Optional[float] = None

class JavaUACalcRunner:
    """Handles execution of Java UACalc operations"""
    
    def __init__(self, java_jar_path: str = "jars/uacalc.jar"):
        self.java_jar_path = java_jar_path
        self.java_wrapper_path = "scripts/JavaWrapper.java"
        
    def _compile_wrapper(self) -> bool:
        """Compile the Java wrapper if needed"""
        if not os.path.exists(self.java_wrapper_path):
            logger.error(f"Java wrapper not found: {self.java_wrapper_path}")
            return False
            
        try:
            # Compile the wrapper
            result = subprocess.run([
                "javac", "-cp", self.java_jar_path, 
                "-d", "scripts", self.java_wrapper_path
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to compile Java wrapper: {result.stderr}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error compiling Java wrapper: {e}")
            return False
    
    def get_algebra_properties(self, ua_file: str) -> Optional[AlgebraProperties]:
        """Get basic properties of an algebra using Java UACalc"""
        if not self._compile_wrapper():
            return None
            
        try:
            result = subprocess.run([
                "java", "-cp", f"{self.java_jar_path};scripts/scripts",
                "scripts.JavaWrapper", "properties", ua_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Java properties failed: {result.stderr}")
                return None
                
            data = json.loads(result.stdout)
            return AlgebraProperties(**data)
            
        except Exception as e:
            logger.error(f"Error getting Java properties: {e}")
            return None
    
    def compute_cg(self, ua_file: str, a: int, b: int) -> Optional[Tuple[List[List[int]], float]]:
        """Compute Cg(a,b) using Java UACalc"""
        if not self._compile_wrapper():
            return None
            
        try:
            result = subprocess.run([
                "java", "-cp", f"{self.java_jar_path};scripts/scripts",
                "scripts.JavaWrapper", "cg", ua_file, str(a), str(b)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                logger.error(f"Java Cg failed: {result.stderr}")
                return None
                
            data = json.loads(result.stdout)
            partition = data.get("partition")
            memory_mb = data.get("java_memory_mb", 0.0)
            return (partition, memory_mb) if partition else None
            
        except Exception as e:
            logger.error(f"Error computing Java Cg: {e}")
            return None
    
    def compute_congruence_lattice(self, ua_file: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Compute full congruence lattice using Java UACalc"""
        if not self._compile_wrapper():
            return None
            
        try:
            result = subprocess.run([
                "java", "-cp", f"{self.java_jar_path};scripts/scripts",
                "scripts.JavaWrapper", "lattice", ua_file
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Java lattice failed: {result.stderr}")
                return None
                
            data = json.loads(result.stdout)
            memory_mb = data.pop("java_memory_mb", 0.0)
            return (data, memory_mb)
            
        except Exception as e:
            logger.error(f"Error computing Java lattice: {e}")
            return None

class RustUACalcRunner:
    """Handles execution of Rust UACalc operations"""
    
    def __init__(self):
        self.python_module = "uacalc"
        
    def get_algebra_properties(self, ua_file: str) -> Optional[AlgebraProperties]:
        """Get basic properties of an algebra using Rust implementation"""
        try:
            import uacalc
            algebra = uacalc.load_algebra(ua_file)
            
            return AlgebraProperties(
                name=algebra.name,
                cardinality=algebra.cardinality,
                operation_count=len(list(algebra.operations())),
                operation_symbols=[op.symbol for op in algebra.operations()],
                operation_arities=[op.arity for op in algebra.operations()]
            )
            
        except Exception as e:
            logger.error(f"Error getting Rust properties: {e}")
            return None
    
    def compute_cg(self, ua_file: str, a: int, b: int) -> Optional[List[List[int]]]:
        """Compute Cg(a,b) using Rust implementation"""
        try:
            import uacalc
            algebra = uacalc.load_algebra(ua_file)
            lattice = uacalc.create_congruence_lattice(algebra)
            partition = lattice.principal_congruence(a, b)
            
            # Convert partition to list of blocks
            blocks = []
            for block in partition.blocks():
                blocks.append(list(block))
            return blocks
            
        except Exception as e:
            logger.error(f"Error computing Rust Cg: {e}")
            return None
    
    def compute_congruence_lattice(self, ua_file: str) -> Optional[Dict[str, Any]]:
        """Compute full congruence lattice using Rust implementation"""
        try:
            import uacalc
            algebra = uacalc.load_algebra(ua_file)
            lattice = uacalc.create_congruence_lattice(algebra)
            
            return {
                "size": lattice.size(),
                "join_irreducibles": len(lattice.join_irreducibles()),
                "height": lattice.height(),
                "width": lattice.width()
            }
            
        except Exception as e:
            logger.error(f"Error computing Rust lattice: {e}")
            return None

def partition_equality(part1: List[List[int]], part2: List[List[int]]) -> bool:
    """Check if two partitions are equal (same block structure)"""
    if len(part1) != len(part2):
        return False
    
    # Normalize partitions by sorting blocks and elements within blocks
    def normalize_partition(partition):
        return sorted([sorted(block) for block in partition])
    
    return normalize_partition(part1) == normalize_partition(part2)

def measure_memory_usage() -> Optional[float]:
    """Measure current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    except ImportError:
        return None

def time_operation(operation_func, *args, **kwargs) -> Tuple[float, Optional[float]]:
    """Time an operation and optionally measure memory usage"""
    start_memory = measure_memory_usage()
    start_time = time.time()
    
    try:
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        end_memory = measure_memory_usage()
        
        duration_ms = (end_time - start_time) * 1000
        memory_usage = None
        if start_memory is not None and end_memory is not None:
            memory_usage = end_memory - start_memory
            
        return duration_ms, memory_usage, result
        
    except Exception as e:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        return duration_ms, None, None

def compare_cg_operations(ua_file: str, java_runner: JavaUACalcRunner, 
                         rust_runner: RustUACalcRunner) -> List[ComparisonResult]:
    """Compare Cg(a,b) operations between Java and Rust"""
    results = []
    
    # Get algebra properties to determine universe size
    props = rust_runner.get_algebra_properties(ua_file)
    if not props:
        return results
    
    # Test Cg for all pairs (a,b) where a < b
    for a in range(props.cardinality):
        for b in range(a + 1, props.cardinality):
            logger.info(f"Comparing Cg({a},{b}) for {ua_file}")
            
            # Time Java operation
            java_time, _, java_result = time_operation(
                java_runner.compute_cg, ua_file, a, b
            )
            
            # Extract memory usage from Java result
            java_memory = None
            if java_result is not None:
                java_result, java_memory = java_result
            
            # Time Rust operation
            rust_time, rust_memory, rust_result = time_operation(
                rust_runner.compute_cg, ua_file, a, b
            )
            
            # Compare results
            correctness_match = True
            error_msg = None
            
            if java_result is None or rust_result is None:
                correctness_match = False
                error_msg = "One or both operations failed"
            elif not partition_equality(java_result, rust_result):
                correctness_match = False
                error_msg = "Partition results don't match"
            
            # Calculate speedup and memory improvement
            speedup = java_time / rust_time if rust_time > 0 else float('inf')
            memory_improvement = None
            if java_memory is not None and rust_memory is not None and java_memory > 0:
                memory_improvement = (java_memory - rust_memory) / java_memory * 100
            
            result = ComparisonResult(
                operation=f"Cg({a},{b})",
                algebra_file=ua_file,
                java_time_ms=java_time,
                rust_time_ms=rust_time,
                speedup=speedup,
                memory_java_mb=java_memory,
                memory_rust_mb=rust_memory,
                memory_improvement=memory_improvement,
                correctness_match=correctness_match,
                error_message=error_msg
            )
            
            results.append(result)
            
            # Log results
            if correctness_match:
                logger.info(f"✓ Cg({a},{b}) - Java: {java_time:.2f}ms, Rust: {rust_time:.2f}ms, "
                           f"Speedup: {speedup:.2f}x")
            else:
                logger.error(f"✗ Cg({a},{b}) - {error_msg}")
    
    return results

def compare_lattice_operations(ua_file: str, java_runner: JavaUACalcRunner,
                              rust_runner: RustUACalcRunner) -> List[ComparisonResult]:
    """Compare congruence lattice operations between Java and Rust"""
    results = []
    
    logger.info(f"Comparing congruence lattice for {ua_file}")
    
    # Time Java operation
    java_time, _, java_result = time_operation(
        java_runner.compute_congruence_lattice, ua_file
    )
    
    # Extract memory usage from Java result
    java_memory = None
    if java_result is not None:
        java_result, java_memory = java_result
    
    # Time Rust operation
    rust_time, rust_memory, rust_result = time_operation(
        rust_runner.compute_congruence_lattice, ua_file
    )
    
    # Compare results
    correctness_match = True
    error_msg = None
    
    if java_result is None or rust_result is None:
        correctness_match = False
        error_msg = "One or both operations failed"
    elif java_result != rust_result:
        correctness_match = False
        error_msg = f"Lattice results don't match: Java={java_result}, Rust={rust_result}"
    
    # Calculate speedup and memory improvement
    speedup = java_time / rust_time if rust_time > 0 else float('inf')
    memory_improvement = None
    if java_memory is not None and rust_memory is not None:
        memory_improvement = (java_memory - rust_memory) / java_memory * 100
    
    result = ComparisonResult(
        operation="congruence_lattice",
        algebra_file=ua_file,
        java_time_ms=java_time,
        rust_time_ms=rust_time,
        speedup=speedup,
        memory_java_mb=java_memory,
        memory_rust_mb=rust_memory,
        memory_improvement=memory_improvement,
        correctness_match=correctness_match,
        error_message=error_msg
    )
    
    results.append(result)
    
    # Log results
    if correctness_match:
        logger.info(f"✓ Lattice - Java: {java_time:.2f}ms, Rust: {rust_time:.2f}ms, "
                   f"Speedup: {speedup:.2f}x")
    else:
        logger.error(f"✗ Lattice - {error_msg}")
    
    return results

def generate_report(results: List[ComparisonResult], output_file: str = "comparison_report.json"):
    """Generate comprehensive comparison report"""
    # Calculate summary statistics
    successful_results = [r for r in results if r.correctness_match]
    failed_results = [r for r in results if not r.correctness_match]
    
    if successful_results:
        avg_speedup = sum(r.speedup for r in successful_results) / len(successful_results)
        max_speedup = max(r.speedup for r in successful_results)
        min_speedup = min(r.speedup for r in successful_results)
        
        memory_improvements = [r.memory_improvement for r in successful_results 
                             if r.memory_improvement is not None]
        avg_memory_improvement = (sum(memory_improvements) / len(memory_improvements) 
                                if memory_improvements else None)
    else:
        avg_speedup = max_speedup = min_speedup = avg_memory_improvement = None
    
    report = {
        "summary": {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(failed_results),
            "success_rate": len(successful_results) / len(results) if results else 0,
            "average_speedup": avg_speedup,
            "max_speedup": max_speedup,
            "min_speedup": min_speedup,
            "average_memory_improvement_percent": avg_memory_improvement
        },
        "results": [asdict(r) for r in results],
        "failed_tests": [asdict(r) for r in failed_results]
    }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to {output_file}")
    
    # Print summary
    print(f"\n=== COMPARISON SUMMARY ===")
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_results)}")
    print(f"Failed: {len(failed_results)}")
    print(f"Success rate: {report['summary']['success_rate']:.2%}")
    
    if avg_speedup:
        print(f"Average speedup: {avg_speedup:.2f}x")
        print(f"Speedup range: {min_speedup:.2f}x - {max_speedup:.2f}x")
    
    if avg_memory_improvement:
        print(f"Average memory improvement: {avg_memory_improvement:.1f}%")
    
    if failed_results:
        print(f"\n=== FAILED TESTS ===")
        for result in failed_results:
            print(f"{result.algebra_file} - {result.operation}: {result.error_message}")

def main():
    """Main comparison function"""
    # Check if Java UACalc is available
    java_jar_path = "jars/uacalc.jar"
    if not os.path.exists(java_jar_path):
        logger.error(f"Java UACalc JAR not found: {java_jar_path}")
        logger.error("Please ensure Java UACalc is available for comparison")
        return 1
    
    # Initialize runners
    java_runner = JavaUACalcRunner(java_jar_path)
    rust_runner = RustUACalcRunner()
    
    # Find all .ua files
    ua_files = glob.glob("resources/algebras/**/*.ua", recursive=True)
    if not ua_files:
        logger.error("No .ua files found in resources/algebras/")
        return 1
    
    logger.info(f"Found {len(ua_files)} algebra files for comparison")
    
    all_results = []
    
    # Compare each algebra file
    for ua_file in ua_files:
        logger.info(f"\n=== Comparing {ua_file} ===")
        
        # Compare basic properties
        java_props = java_runner.get_algebra_properties(ua_file)
        rust_props = rust_runner.get_algebra_properties(ua_file)
        
        if java_props and rust_props:
            if java_props == rust_props:
                logger.info(f"✓ Properties match: {rust_props.name} (|A|={rust_props.cardinality})")
            else:
                logger.error(f"✗ Properties don't match: Java={java_props}, Rust={rust_props}")
        
        # Compare Cg operations
        cg_results = compare_cg_operations(ua_file, java_runner, rust_runner)
        all_results.extend(cg_results)
        
        # Compare lattice operations (only for smaller algebras to avoid timeouts)
        if java_props and java_props.cardinality <= 8:
            lattice_results = compare_lattice_operations(ua_file, java_runner, rust_runner)
            all_results.extend(lattice_results)
    
    # Generate report
    generate_report(all_results)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
