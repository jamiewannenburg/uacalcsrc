#!/usr/bin/env python3
"""
Manual Dependency Analyzer

This tool manually analyzes the key operation classes to determine the correct
dependency chain based on the actual Java source code.
"""

def analyze_operation_dependencies():
    """Manually analyze the dependency chain for operation classes."""
    
    print("Manual Analysis of Operation Class Dependencies")
    print("=" * 60)
    
    # Based on manual inspection of the Java source files
    dependencies = {
        'org.uacalc.util.SequenceGenerator': {
            'dependencies': [],
            'description': 'Utility class for generating sequences. No UACalc dependencies.',
            'level': 0
        },
        'org.uacalc.alg.op.Operation': {
            'dependencies': [],
            'description': 'Interface defining operation contract. No UACalc dependencies.',
            'level': 0
        },
        'org.uacalc.alg.op.Operations': {
            'dependencies': ['org.uacalc.alg.op.Operation', 'org.uacalc.util.SequenceGenerator'],
            'description': 'Factory class with static methods. Depends on Operation interface and SequenceGenerator.',
            'level': 1
        },
        'org.uacalc.alg.op.AbstractOperation': {
            'dependencies': ['org.uacalc.alg.op.Operation', 'org.uacalc.alg.op.Operations'],
            'description': 'Abstract implementation of Operation. Implements Operation interface and calls Operations static methods.',
            'level': 2
        }
    }
    
    # Print analysis
    for class_name, info in dependencies.items():
        print(f"\n{class_name}:")
        print(f"  Level: {info['level']}")
        print(f"  Dependencies: {len(info['dependencies'])}")
        for dep in info['dependencies']:
            print(f"    - {dep}")
        print(f"  Description: {info['description']}")
    
    # Determine implementation order
    print("\n" + "=" * 60)
    print("CORRECT IMPLEMENTATION ORDER")
    print("=" * 60)
    
    # Sort by dependency level
    sorted_classes = sorted(dependencies.items(), key=lambda x: x[1]['level'])
    
    print("\nRecommended Implementation Order:")
    for i, (class_name, info) in enumerate(sorted_classes, 1):
        print(f"{i}. {class_name}")
        print(f"   Level: {info['level']} (no dependencies on other UACalc classes)")
        if info['dependencies']:
            print(f"   Depends on: {', '.join(info['dependencies'])}")
        print(f"   {info['description']}")
        print()
    
    # Show the dependency chain
    print("DEPENDENCY CHAIN:")
    print("SequenceGenerator (0) → Operations (1) → AbstractOperation (2)")
    print("Operation (0) → AbstractOperation (2)")
    print()
    print("Therefore, implement in this order:")
    print("1. SequenceGenerator (has no UACalc dependencies)")
    print("2. Operation (interface, no UACalc dependencies)")  
    print("3. Operations (depends on SequenceGenerator and Operation)")
    print("4. AbstractOperation (depends on Operation and Operations)")

if __name__ == "__main__":
    analyze_operation_dependencies()

