#!/usr/bin/env python3
"""
Enhanced Test Runner for Comprehensive Java Compatibility Testing

This script provides a unified interface for running both pytest and the
comprehensive test suite with advanced features like parallel execution,
resource monitoring, and enhanced reporting.
"""

import argparse
import sys
import os
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_pytest_tests(
    test_paths: List[str] = None,
    parallel: bool = False,
    max_workers: int = 4,
    timeout: int = 300,
    markers: List[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run tests using pytest with enhanced reporting"""
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--html=reports/pytest_report.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=reports/pytest_report.json",
        f"--timeout={timeout}",
        "--durations=10",
        "--maxfail=5"
    ]
    
    if verbose:
        cmd.append("-v")
    
    if parallel:
        cmd.extend(["-n", str(max_workers)])
    
    if markers:
        for marker in markers:
            cmd.extend(["-m", marker])
    
    if test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append("tests/python/")
    
    print(f"Running pytest command: {' '.join(cmd)}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    # Parse JSON report if available
    json_report = {}
    json_path = Path("reports/pytest_report.json")
    if json_path.exists():
        try:
            with open(json_path) as f:
                json_report = json.load(f)
        except Exception as e:
            print(f"Warning: Could not parse JSON report: {e}")
    
    return {
        "success": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "execution_time": end_time - start_time,
        "json_report": json_report
    }

def run_comprehensive_suite(
    config_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Run the comprehensive test suite"""
    
    from tests.python.comprehensive_test_suite import ComprehensiveTestSuite, TestSuiteConfiguration
    
    # Default configuration
    default_config = {
        "include_algebra_tests": True,
        "include_congruence_tests": True,
        "include_operation_tests": True,
        "include_term_tests": True,
        "include_lattice_tests": True,
        "include_equation_tests": True,
        "include_group_tests": True,
        "include_io_tests": True,
        "include_utility_tests": True,
        "timeout_per_test": 300,
        "parallel_execution": False,
        "max_parallel_tests": 4,
        "resource_management": True,
        "memory_limit_mb": 2048,
        "cpu_limit_percent": 80,
        "save_results_to_file": True,
        "output_file": "reports/comprehensive_test_results.json"
    }
    
    if config_options:
        default_config.update(config_options)
    
    config = TestSuiteConfiguration(**default_config)
    test_suite = ComprehensiveTestSuite(config)
    
    start_time = time.time()
    report = test_suite.run_comprehensive_tests()
    end_time = time.time()
    
    return {
        "success": report.failed_tests == 0,
        "report": report,
        "execution_time": end_time - start_time
    }

def generate_combined_report(
    pytest_results: Dict[str, Any],
    comprehensive_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a combined report from both test runners"""
    
    combined_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pytest_results": {
            "success": pytest_results["success"],
            "execution_time": pytest_results["execution_time"],
            "returncode": pytest_results["returncode"]
        },
        "comprehensive_results": {
            "success": comprehensive_results["success"],
            "execution_time": comprehensive_results["execution_time"]
        }
    }
    
    # Add comprehensive test details if available
    if "report" in comprehensive_results:
        report = comprehensive_results["report"]
        combined_report["comprehensive_results"].update({
            "total_tests": report.total_tests,
            "passed_tests": report.passed_tests,
            "failed_tests": report.failed_tests,
            "skipped_tests": report.skipped_tests,
            "compatibility_percentage": report.compatibility_percentage,
            "feature_coverage": report.feature_coverage,
            "resource_statistics": report.resource_statistics
        })
    
    # Add pytest JSON report details if available
    if "json_report" in pytest_results and pytest_results["json_report"]:
        json_report = pytest_results["json_report"]
        combined_report["pytest_results"].update({
            "summary": json_report.get("summary", {}),
            "duration": json_report.get("duration", 0)
        })
    
    return combined_report

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Test Runner for Comprehensive Java Compatibility Testing"
    )
    
    # Test runner selection
    parser.add_argument(
        "--runner", 
        choices=["pytest", "comprehensive", "both"], 
        default="both",
        help="Which test runner to use"
    )
    
    # Pytest options
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest")
    parser.add_argument("--comprehensive-only", action="store_true", help="Run only comprehensive suite")
    
    # Parallel execution
    parser.add_argument("--parallel", action="store_true", help="Enable parallel execution")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum parallel workers")
    
    # Timeout options
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per test in seconds")
    
    # Test filtering
    parser.add_argument("--markers", nargs="+", help="Pytest markers to filter tests")
    parser.add_argument("--test-paths", nargs="+", help="Specific test paths to run")
    
    # Resource management
    parser.add_argument("--memory-limit", type=int, default=2048, help="Memory limit in MB")
    parser.add_argument("--cpu-limit", type=int, default=80, help="CPU limit percentage")
    parser.add_argument("--no-resource-monitoring", action="store_true", help="Disable resource monitoring")
    
    # Output options
    parser.add_argument("--output-file", default="reports/combined_test_results.json", help="Output file for combined results")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure reports directory exists
    Path("reports").mkdir(exist_ok=True)
    
    print("🧪 Enhanced Test Runner for Java Compatibility Testing")
    print("=" * 60)
    
    pytest_results = None
    comprehensive_results = None
    
    # Run pytest if requested
    if args.runner in ["pytest", "both"] or args.pytest_only:
        print("\n📋 Running pytest tests...")
        pytest_results = run_pytest_tests(
            test_paths=args.test_paths,
            parallel=args.parallel,
            max_workers=args.max_workers,
            timeout=args.timeout,
            markers=args.markers,
            verbose=args.verbose
        )
        
        if pytest_results["success"]:
            print("✅ Pytest tests completed successfully")
        else:
            print("❌ Pytest tests failed")
            if args.verbose:
                print("STDOUT:", pytest_results["stdout"])
                print("STDERR:", pytest_results["stderr"])
    
    # Run comprehensive suite if requested
    if args.runner in ["comprehensive", "both"] or args.comprehensive_only:
        print("\n🔬 Running comprehensive test suite...")
        
        config_options = {
            "parallel_execution": args.parallel,
            "max_parallel_tests": args.max_workers,
            "timeout_per_test": args.timeout,
            "resource_management": not args.no_resource_monitoring,
            "memory_limit_mb": args.memory_limit,
            "cpu_limit_percent": args.cpu_limit,
            "output_file": "reports/comprehensive_test_results.json"
        }
        
        comprehensive_results = run_comprehensive_suite(config_options)
        
        if comprehensive_results["success"]:
            print("✅ Comprehensive test suite completed successfully")
        else:
            print("❌ Comprehensive test suite failed")
    
    # Generate combined report
    if pytest_results and comprehensive_results:
        print("\n📊 Generating combined report...")
        combined_report = generate_combined_report(pytest_results, comprehensive_results)
        
        with open(args.output_file, 'w') as f:
            json.dump(combined_report, f, indent=2, default=str)
        
        print(f"📄 Combined report saved to {args.output_file}")
        
        # Print summary
        print("\n📈 Test Summary:")
        print(f"  Pytest: {'✅ Passed' if pytest_results['success'] else '❌ Failed'}")
        print(f"  Comprehensive: {'✅ Passed' if comprehensive_results['success'] else '❌ Failed'}")
        
        if "report" in comprehensive_results:
            report = comprehensive_results["report"]
            print(f"  Total Tests: {report.total_tests}")
            print(f"  Compatibility: {report.compatibility_percentage:.1f}%")
            print(f"  Execution Time: {comprehensive_results['execution_time']:.2f}s")
    
    # Determine exit code
    exit_code = 0
    if pytest_results and not pytest_results["success"]:
        exit_code = 1
    if comprehensive_results and not comprehensive_results["success"]:
        exit_code = 1
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
