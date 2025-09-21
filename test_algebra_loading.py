#!/usr/bin/env python3
"""
Test script to debug algebra loading issues
"""

import sys
import os
sys.path.insert(0, 'python')

import uacalc

def test_algebra_loading():
    print("Testing algebra loading...")
    
    # Test loading the baker2.ua algebra
    algebra_file = "resources/algebras/baker2.ua"
    
    try:
        print(f"Loading algebra from {algebra_file}...")
        algebra = uacalc.load_algebra(algebra_file)
        print(f"Successfully loaded algebra: {algebra.name}")
        print(f"Cardinality: {algebra.cardinality}")
        print(f"Operations: {len(algebra.operations)}")
        
        # Test Malcev analysis
        print("Testing Malcev analysis...")
        analyzer = uacalc.MalcevAnalyzer()
        analysis = analyzer.analyze_malcev_conditions(algebra)
        print(f"Analysis completed: {analysis.analysis_completed}")
        print(f"Has Malcev term: {analysis.has_malcev_term}")
        print(f"Has join term: {analysis.has_join_term}")
        print(f"Semilattice term: {analysis.semilattice_term}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_algebra_loading()
