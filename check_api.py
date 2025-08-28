#!/usr/bin/env python3
import uacalc

print("Available functions in uacalc module:")
functions = [f for f in dir(uacalc) if not f.startswith('_') and callable(getattr(uacalc, f))]
for f in sorted(functions):
    print(f"  {f}")

print("\nAvailable classes in uacalc module:")
classes = [c for c in dir(uacalc) if not c.startswith('_') and isinstance(getattr(uacalc, c), type)]
for c in sorted(classes):
    print(f"  {c}")

print("\nTrying to load an algebra...")
try:
    algebra = uacalc.load_algebra('resources/algebras/ba2.ua')
    print(f"Successfully loaded algebra: {algebra.name}")
    print(f"Cardinality: {algebra.cardinality}")
    
    print("\nAvailable methods on algebra object:")
    methods = [m for m in dir(algebra) if not m.startswith('_') and callable(getattr(algebra, m))]
    for m in sorted(methods):
        print(f"  {m}")
        
    print("\nAvailable attributes on algebra object:")
    attrs = [a for a in dir(algebra) if not a.startswith('_') and not callable(getattr(algebra, a))]
    for a in sorted(attrs):
        print(f"  {a}")
        
except Exception as e:
    print(f"Error loading algebra: {e}")
