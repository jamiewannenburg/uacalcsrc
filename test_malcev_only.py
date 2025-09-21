#!/usr/bin/env python3
"""
Test script to debug Malcev analysis issues
"""

import sys
import os
sys.path.insert(0, 'python')

def test_malcev_analysis():
    print("Testing Malcev analysis...")
    
    try:
        import uacalc
        print("Successfully imported uacalc")
        
        # Load algebra
        algebra_file = "resources/algebras/baker2.ua"
        print(f"Loading algebra from {algebra_file}...")
        algebra = uacalc.load_algebra(algebra_file)
        print(f"Successfully loaded algebra: {algebra.name}")
        print(f"Cardinality: {algebra.cardinality}")
        
        # Test Malcev analysis
        print("Creating MalcevAnalyzer...")
        analyzer = uacalc.MalcevAnalyzer()
        print("MalcevAnalyzer created successfully")
        
        print("Starting analyze_malcev_conditions...")
        analysis = analyzer.analyze_malcev_conditions(algebra)
        print("Analysis completed successfully!")
        
        print(f"Analysis results:")
        print(f"  - Analysis completed: {analysis.analysis_completed}")
        print(f"  - Has Malcev term: {analysis.has_malcev_term}")
        print(f"  - Has join term: {analysis.has_join_term}")
        print(f"  - Semilattice term: {analysis.semilattice_term}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_malcev_analysis()
